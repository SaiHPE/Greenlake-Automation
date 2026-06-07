# HPE Alletra MP B10000 → GreenLake / DSCC Onboarding Automation — Feasibility Report

_Researched 2026-06-05. Updated 2026-06-07 against the full local GreenLake API scrape. Confidence noted per item._

---

## 1. Verdict

| Phase | Automatable? | How |
|---|---|---|
| **Add subscription to workspace** | ✅ Yes | REST — `POST /subscriptions/v1/subscriptions` (async) |
| **Register storage array to inventory** (fixes `fail-prov-no-device`) | ✅ Yes | REST — `POST /devices/v1/devices` (async) |
| **Assign device → Data Services application instance + region** (fixes `fail-prov-no-rule`) | ✅ Yes | REST — `PATCH /devices/v1/devices?id={id}` |
| **Apply subscription to the device** | ✅ Yes | REST — same `PATCH` endpoint, separate call |
| **Verify state at each gate** | ✅ Yes | `GET` (or read-only GreenLake MCP) |
| **Post-initialization storage settings / verification** | ✅ Yes | REST — Storage Fleet regional APIs after the system exists |
| **Create the primary workspace** | ❌ No API | Console UI / prerequisite input (only MSP *tenant* workspaces have a POST) |
| **On-array first boot** (Discovery Tool + Cloud Connectivity Wizard / `cloudinit`) | ⚠️ No REST API found | GUI / browser automation from the jump box (not separately verified — see §7) |
| **DSCC "Setup system" initialization of the B10000** | ❌ No REST API (verified) | GUI / browser automation |

**Bottom line:** the *GreenLake control-plane registration + subscription + application binding* is a clean, scriptable async REST pipeline. The *first-boot array connectivity wizard* and the *DSCC "Setup system" wizard* are **not exposed via REST** and must be driven through the UI (browser automation). Storage Fleet adds useful REST automation **after** the system exists, but it does not replace first-time setup. So a "fully automated" solution is necessarily **hybrid: REST for the cloud control plane + post-init checks/settings, browser automation for two GUI islands.**

---

## 2. The automatable cloud core (HIGH confidence)

Base host for Devices, Subscriptions, and Service Catalog: `https://global.api.greenlake.hpe.com`. Device and Subscription writes require **`ccs.device-management.edit`**; reads require **`ccs.device-management.view`**. Service Catalog discovery requires **`ccs.app-catalog.view`** and **`ccs.app-provision.view`**. Optional Storage Fleet calls use regional GreenLake API hosts and Storage Fleet permissions.

### Step 1 — Add the subscription key
```
POST https://global.api.greenlake.hpe.com/subscriptions/v1/subscriptions
Authorization: Bearer <greenlake-token>
Body: { "subscriptions": [ { "key": "<SUBSCRIPTION_KEY>" } ] }   # array, max 5
```
- Async: returns **202 Accepted**, `Location` header to poll. Rate limit ~4 req/min/workspace (429 on exceed).
- GA path is **v1** (`v1beta1` deprecated, removal dated 2025-05-05).

### Step 2 — Register the storage array (fix `fail-prov-no-device`)
```
POST https://global.api.greenlake.hpe.com/devices/v1/devices
Authorization: Bearer <greenlake-token>
Body: {
  "storage": [
    { "serialNumber": "<SERIAL>", "partNumber": "<PART_NUMBER>", "tags": { ... } }
  ]
}                                                   # network[]/compute[]/storage[]; max 5 total
```
- Async: **202** + `Location: /devices/v1/async-operations/{id}`.
- Poll `GET /devices/v1/async-operations/{id}` → terminal `SUCCEEDED | FAILED | TIMEOUT`; resource expires 24h; multi-device responses give a per-serial succeeded/failed breakdown.
- ✅ **Field ambiguity RESOLVED by the source docx screenshots (§8c):** the GreenLake "Add devices" Storage form uses **Serial number + Product (part) number** (e.g. `SGHD44LQLS` / `S0B84A`) — **not** the subscription key. The subscription key is added to the workspace **separately** (`POST /subscriptions`) and then **applied to the device** via the `PATCH` (see Step 3). So the storage `POST /devices/v1/devices` body should send **`serialNumber` + `partNumber`** (the OpenAPI-example form), not subscriptionKey.

### Step 3 — Bind device to application instance + region, then apply subscription (fix `fail-prov-no-rule`)

Device Management v1 PATCH supports both capabilities, but **only one operation is allowed per PATCH call**. The implementation must use two sequential async PATCH calls.

#### Step 3a — assign device → application instance + region
```
PATCH https://global.api.greenlake.hpe.com/devices/v1/devices?id={device_id}
Authorization: Bearer <greenlake-token>
Content-Type: application/merge-patch+json
Body: {
  "application":  { "id": "<service_manager_id>" },
  "region": "<service_catalog_region_id>"
}                                                   # max 5 devices/req; dry-run query param supported
```
- Async: **202** + `Location: /devices/v1/async-operations/{id}`. Rate limit **20 req/min/workspace**.

#### Step 3b — apply subscription to the already-assigned device
```
PATCH https://global.api.greenlake.hpe.com/devices/v1/devices?id={device_id}
Authorization: Bearer <greenlake-token>
Content-Type: application/merge-patch+json
Body: {
  "subscription": [ { "id": "<subscription_id>" } ]
}
```
- Async: **202** + `Location: /devices/v1/async-operations/{id}`. Poll both PATCH operations to terminal state.
- Documented capabilities of this endpoint: assign/remove device→application, apply/remove subscription, and dry-run. The operations cannot be combined in one call.
- `region` = "the region of the application the device is provisioned in." For Service Catalog this is the region id such as `ap-northeast`, not the DSCC host code `jp1`.

> **Resolved (2nd pass, corrected against the full scrape):** discover `application.id` + `region` via the GreenLake **Service Catalog API**. `GET /service-catalog/v1/per-region-service-managers` maps "Data Services" to a GreenLake region id and service-manager id. `GET /service-catalog/v1/service-manager-provisions` returns provision entries with **`serviceManager.id`**, `region`, and **`provisionStatus`**. Filter by `status eq 'PROVISIONED'` / `region eq '<region>'`, then feed `serviceManager.id` into Device PATCH as `application.id`.
>
> **Field-level confirmations:** storage add requires `serialNumber` + `partNumber` (v2beta1 also requires `deviceType:"STORAGE"`); the v1 guide's `subscriptionKey` storage example is a doc artifact (subscription applied separately). The device's `application.resourceUri` points to `/service-catalog/.../service-managers/…` — cross-confirms the Service Catalog relationship. Verify success via the device's `assignedState` (`UNASSIGNED → ASSIGNED_TO_SERVICE`), `application.id`, `region`, and `subscription[].id`. Rate limits: add-devices **25/min**, update-devices/PATCH **20/min**, subscriptions **4/min** per workspace. Service Catalog read permissions are exact: `ccs.app-catalog.view` and `ccs.app-provision.view`.
>
> **Preclaim caveat:** `GET /subscriptions/v2beta1/{key}/preclaim` appears in the scraped **internal** Subscription OpenAPI bundle. Keep it as a useful optional pre-flight, but do not make it the only path; fall back to `POST /subscriptions/v1/subscriptions` + `GET /subscriptions/v1/subscriptions?filter=key eq ...` if preclaim is unavailable.

### Step 4 — Optional post-initialization Storage Fleet REST
After the system is connected/initialized, the richer GreenLake scrape exposes regional Storage Fleet APIs for B10000 (`devtype4`) inventory and settings:
```
GET https://{gl-region}.api.greenlake.hpe.com/storage-fleet/v1alpha1/devtype4-storage-systems
GET/PUT .../devtype4-storage-systems/{systemId}/system-settings
GET/POST .../devtype4-storage-systems/{systemId}/network-settings
GET/POST/PUT .../devtype4-storage-systems/{systemId}/support-settings
GET/POST .../devtype4-storage-systems/{systemId}/licenses
```
- Regional hosts use GreenLake region ids such as `ap-northeast.api.greenlake.hpe.com`.
- Useful for post-setup verification, settings drift correction, NTP/timezone/name, support/contact metadata, network/proxy settings, and license visibility.
- Not a first-boot or DSCC "Setup system" substitute: all routes require an existing `systemId`; the only `initialize` found is port-level (`.../ports/{id}/initialize`), not system initialization.

---

## 3. The hard blocker — DSCC "Setup system" is NOT in the REST API (HIGH confidence)

This is the decisive finding. A verifier downloaded the **live DSCC Data Services storage spec** (`storage-api.yaml`, v1.8.0, ~3.9 MB) and exhaustively grepped it:

- The B10000 maps to **`device-type4`** (appears 469× in the spec).
- The base `/api/v1/storage-systems/device-type4` collection is **GET-only** (`DeviceType4SystemsList`); `/{id}` is GET-only.
- Searching the operationIds `CreateStorageSystem | OnboardStorageSystem | SetupSystem | InitializeStorageSystem | RegisterStorageSystem | CreateDeviceType4 | AddStorageSystem` → **zero matches.**
- Every `device-type4` "Create" op builds *sub-resources* on an already-existing system; the only `initialize` is on **ports** (`.../ports/{id}/initialize`), not the system.
- **Asymmetry that proves it:** the sibling `device-type2` *does* have `DeviceType2CreateArray` and `GetDeviceType2UninitializedArrays` — and there is **no `device-type4` equivalent.**

➡️ Therefore the **"Setup system" wizard for the B10000 must be driven through the GUI** (or browser automation). The on-array **B10000 Web Services API v3** likewise manages an *already-initialized* array — it is not a first-boot path.

⏳ _Caveat:_ spec verified at **v1.8.0** — re-check the version before each campaign, since a future release could in principle add device-type4 onboarding.

---

## 4. Authentication model (HIGH confidence) — one identity provider, several API hosts

| | GreenLake global APIs | Storage Fleet regional APIs | DSCC regional APIs |
|---|---|---|---|
| Host | `https://global.api.greenlake.hpe.com` | `https://{gl-region}.api.greenlake.hpe.com` | `https://{dscc-region}.data.cloud.hpe.com` (`/api/v1/...`) |
| Used for | Devices, Subscriptions, Service Catalog | B10000 post-init inventory/settings | DSCC storage verification/management |
| Token endpoint | `POST https://sso.common.cloud.hpe.com/as/token.oauth2` (`grant_type=client_credentials`) | same identity layer | same identity layer |
| Token | OAuth2/JWT bearer from GreenLake API client | same bearer model | JWT bearer (`aud: external_api`, RS256, issuer `sso.common.cloud.hpe.com`) |
| Lifetime | GreenLake tokens documented as short-lived; refresh on expiry/401 | same | ~7200s (~2h); refresh on expiry/401 |

All authenticate against the **same common-cloud identity layer** with the client-credentials grant; they differ by host and required permissions. DSCC region codes are `{region}.data.cloud.hpe.com`: **us1** (US West), **eu1** (EU Central), **jp1** (AP Northeast — *not* "ap1"), **uk1** (EU West, added later). GreenLake/Storage Fleet region ids use values such as `us-west`, `eu-west`, `eu-central`, and `ap-northeast`. Keep both region vocabularies in config.

---

## 5. Recommended automated architecture (hybrid)

```
                ┌─────────────────────────── PRE-STAGE (cloud, REST, headless) ───────────────────────────┐
 inputs:        │  token = client_credentials(GreenLake API client)                                        │
  serial,       │  1. POST /subscriptions/v1/subscriptions      → 202 → poll async-op → SUCCEEDED          │
  partNumber,   │  2. POST /devices/v1/devices (serial+partNumber) → 202 → poll /async-operations/{id}     │  ← fixes fail-prov-no-device
  workspaceId,  │  3. GET /service-catalog/v1/... → serviceManager.id + region + provisionStatus           │
  glRegion      │  4a. PATCH /devices/v1/devices?id= {application, region} → poll                           │
                │  4b. PATCH /devices/v1/devices?id= {subscription} → poll                                  │  ← fixes fail-prov-no-rule
                └──────────────────────────────────────────────────────────────────────────────────────────┘
                                                   │  (array is now pre-registered, so it won't hit the two errors)
                ┌─────────────────────── ON-ARRAY FIRST BOOT (jump box, GUI/browser) ──────────────────────┐
                │  5. Discovery Tool: enter serial → connect to link-local IP                               │
                │  6. Cloud Connectivity Wizard / cloudinit: enter network info + subscription key          │
                └──────────────────────────────────────────────────────────────────────────────────────────┘
                ┌─────────────────────────── DSCC "SETUP SYSTEM" (GUI/browser) ───────────────────────────┐
                │  7. DSCC Setup Service wizard (blueprints can pre-fill many systems) — NO REST           │
                └──────────────────────────────────────────────────────────────────────────────────────────┘
                ┌─────────────────────────────── VERIFY (REST / MCP) ─────────────────────────────────────┐
                │  GET /devices/v1/devices, Storage Fleet devtype4 systems, DSCC /api/v1/storage-systems   │
                └──────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key insight (MEDIUM confidence — synthesized, not quoted from a single HPE runbook):** doing the cloud trio (1‑4) **before** the array phones home pre-empts both `fail-prov-no-device` and `fail-prov-no-rule`, turning the docx's trial-and-error loop into a clean linear pipeline. The precise dependency (must the subscription exist before the device POST that references its key, vs. applying the key later via PATCH) is inferred, not explicitly verified — confirm against an HPE onboarding runbook / live workspace.

---

## 6. Reusable HPE automation assets

These official repos are useful, but none replace the control-plane onboarding flow for a B10000. Use direct REST for the GreenLake cloud trio; use SDKs/toolkits mainly for verification or later management.

- **`github.com/HewlettPackard/gl-mcp`** — useful for read-only GreenLake verification gates.
- **`github.com/HewlettPackard/HPEDSCC-PowerShell-Toolkit`** — useful for already-onboarded DSCC/storage management, not B10000 onboarding.
- **`github.com/HewlettPackard/greenlake-data-services-ansible`** — useful for already-onboarded Data Services resources, not B10000 onboarding.
- **`github.com/HewlettPackard/greenlake-data-services-python`** — useful as an HTTP/client reference for Data Services verification and later management.

Implementation decision: build the GreenLake registration/subscription/assignment path with `httpx` direct REST calls so endpoint contracts, async polling, idempotency, and rate limits stay explicit.

---

## 7. Confidence, caveats & open questions

**Source-retrieval note:** the original 2026-06-05 pass had weaker GreenLake-platform capture because the developer portal is a client-rendered SPA. That caveat is now mostly superseded for Devices, Subscriptions, Service Catalog, and Storage Fleet because the 2026-06-07 local scrape includes rendered markdown and raw OpenAPI YAML. The remaining weaker areas are external HPE support pages for the official onboarding sequence and some first-boot hardware/network details.

**URL/version note:** use GA GreenLake paths where available: `/devices/v1/...`, `/subscriptions/v1/...`, `/service-catalog/v1/...`. Some scraped folders include historical names such as `service-catalog-v1beta1`, but the contained endpoint paths are `v1`.

**Status of the original open gaps (updated after the 2nd pass — see §7b):**
1. ✅ **Service-catalog discovery** of `application.id` + `region` — **RESOLVED with correction**: use `service-manager-provisions.items.serviceManager.id`, `items.region`, and `items.provisionStatus`.
2. ⚠️ **On-array first boot (Section C)** — **partly resolved:** connection model + "no on-array init API" confirmed; Discovery-Tool headless mode and a `cloudinit` REST API remain **undocumented → treat as GUI/browser-only.** Storage Fleet can manage settings after a system exists, but it does not expose first-boot/system setup.
3. ❌ HPE's officially-named **onboarding sequence** + the subscription-before-device dependency — **still open** (authoritative support docs are JS-rendered and weren't captured).
4. ⚠️ **Reusable assets** — validated enough to know the **PowerShell toolkit / Ansible collection do _not_ onboard** a B10000 (manage-only) → the cloud trio needs **direct REST**.

---

## 7b. Updated gap-closing findings

These are the current working conclusions after the 2026-06-07 local GreenLake scrape and the earlier DSCC/API research pass.

**GAP 1 — Discover `application.id` + `region` → RESOLVED (HIGH, corrected against full scrape).** Use the GreenLake **Service Catalog API** (base `https://global.api.greenlake.hpe.com`):
- `GET /service-catalog/v1/per-region-service-managers` — lists region ids and service managers available in each region. Match `serviceManagers.name` to **Data Services** and keep `serviceManagers.id`.
- `GET /service-catalog/v1/service-manager-provisions` (+ `/{id}`) — lists the workspace's provisioned service-manager entries; response fields are **`serviceManager.id`**, `region`, and **`provisionStatus`**. The filter parameter uses `status eq 'PROVISIONED'`, but the response field is `provisionStatus`.
- The Device PATCH `application.id` should use the Service Catalog **`serviceManager.id`**, and `region` should use the Service Catalog region id such as `ap-northeast`. The public v1 service-manager-provision endpoint does **not** return `application_id`; older/private UI endpoints may expose that name, but do not build the main flow on it.

**GAP 2 — On-array first boot → PARTLY RESOLVED.**
- ✅ The array→DSCC connection is a **secure tunnel (mTLS) over outbound TCP 443** (confirmed).
- ✅ The **B10000 Web Services API v3 manages an already-initialized array only** — no first-boot init (re-confirms §3).
- ❌ **Refuted (0-3):** the minimal "only 443 + SMTP 25, no NTP/DNS/websocket" claim was killed → the real allowlist is **larger** (expect NTP, DNS, and specific HPE FQDNs). Authoritative docs to consult directly (all JS-rendered, so read in a browser): **sd00002403** "Websites / Cloud Enablement Quick Start", **sd00002385** "Network requirement details", **sd00002429** "Configuring ports".
- ⚠️ **No documented CLI/headless mode for the Discovery Tool, and no documented REST API behind the `cloudinit` / Cloud Connectivity Wizard** were found. Absence of any documented interface ⇒ plan for **GUI/browser automation** on the jump box. No public subscription-key "activation API" surfaced (key still comes from the box / Activation Receipt email).

**GAP 3 — Official named sequence & ordering → STILL OPEN.** No officially-named, verbatim end-to-end onboarding sequence or `fail-prov-*` remediation text was captured (the candidate HPE support pages returned no extractable content). The **register-in-cloud-before-the-array-connects** ordering is *indirectly* supported (DSCC console access "presupposes a storage system already added"), but the precise **subscription-before-device-POST** dependency remains unconfirmed — validate against a live lab workspace.

**Reusable assets — clarified:** the **HPEDSCC PowerShell Toolkit** and **greenlake-data-services Ansible** collection have **no device-onboarding / assign-application capability** for the B10000 (they manage already-onboarded arrays; the toolkit centers on device-type1 / Alletra-9000-class). ⇒ implement the cloud registration trio with **direct REST calls** (or the Python SDK at the HTTP layer); use the toolkits/MCP for **verification** only.

---

## 8b. Appendix — the source docx, step by step: automatable vs not

Legend: ✅ REST (headless API) · 🟡 GUI-only (scriptable via browser/desktop automation, no API) · 🔴 not automatable (physical / human / one-time prerequisite).

| # | Action in the docx | Category | How / why |
|---|---|---|---|
| 0 | _(implied)_ rack, cable, power on the uninitialized array | 🔴 | physical hardware |
| 0 | _(implied)_ jump-box remote access + proxy/firewall allowlist for the DSCC tunnel | 🔴 | one-time IT/network change (FQDN list in HPE docs sd00002403/2385/2429) |
| 1 | "Input the SN of the Array" → "Click search" (Discovery Tool) | 🟡 | native Windows GUI tool, no CLI/headless mode found |
| 2 | Open the array `cloudinit` page (`https://169.254.x/cloudinit`) | 🟡 | web UI on link-local IP; no REST behind it |
| 3 | "Your subscription key is …" (obtain key) | 🔴 | key comes from shipping box / Activation Receipt email — no API |
| 4 | Enter network info in Cloud Connectivity Wizard | 🟡 | same `cloudinit` UI → browser automation |
| 5 | Array "Checking DSCC connection" → `fail-prov-no-device` | — | symptom, not a step — eliminated by registering first |
| 6 | "Create new workspace" | 🔴 | no REST for primary workspace (UI-only) → `workspaceId` is an input |
| 7 | Register/add storage system to inventory _(fixes `fail-prov-no-device`)_ | ✅ | `POST /devices/v1/devices` (serial + partNumber), async |
| 8 | Add subscription key to workspace | ✅ | `POST /subscriptions/v1/subscriptions` |
| 9 | Find Data Services application instance + region | ✅ | `GET /service-catalog/v1/service-manager-provisions` (+ `/service-managers`) |
| 10 | Assign device → application instance + region, then apply subscription _(fixes `fail-prov-no-rule`)_ | ✅ | two sequential `PATCH /devices/v1/devices?id=` calls; one operation per call |
| 11 | "Retry" connection | ✅ | no manual retry if #7–10 ran first; array connects first try |
| 12 | "Launch DSCC from the Array" | 🟡 | navigation — or open the DSCC console URL directly |
| 13 | "Setup service needs to be clicked" | 🟡 | DSCC Setup Service wizard — no REST for B10000 |
| 14 | "Select the storage and click Setup system" | 🟡 | **hard blocker** — DSCC has no setup/init REST op for `device-type4` |
| 15 | "Apply the subscription" (in DSCC) | ✅/🟡 | binding is REST (#10); inside the wizard it's a GUI field |
| 16 | _(implied)_ verify registered + subscribed | ✅ | `GET /devices`, DSCC `GET /storage-systems`, or read-only MCP |

**Buckets.** ✅ REST: add subscription → register device → discover app instance/region → assign → apply subscription → verify (the entire `fail-prov-*` fix), plus post-initialization Storage Fleet settings/verification. 🟡 GUI-only: Discovery Tool, on-array `cloudinit` wizard, DSCC "Setup service → Setup system". 🔴 not automatable: physical install, subscription-key acquisition, primary-workspace creation, jump-box connectivity + firewall allowlist, valid API-client credentials.

**Reorder insight:** running the ✅ REST bucket (#7–10) before the array phones home eliminates both `fail-prov-no-device` and `fail-prov-no-rule`, collapsing the docx's fail→fix→retry loop.

---

## 8c. Screenshot-by-screenshot map (41 images in the source docx)

Each embedded screenshot (`imageN.jpeg`, document order = file order) mapped to the §8b step. Categories: ✅ REST · 🟡 GUI-only · 🔴 not automatable.

| Img | What it shows | §8b row | Cat |
|---|---|---|---|
| 1 | File Explorer: HPE Discovery Tool .exe (native Windows app) | obtain tool | 🔴/🟡 |
| 2 | Discovery Tool — enter serial, Search | 1 | 🟡 |
| 3–4 | Discovery Tool "Searching for array" | 1 | 🟡 |
| 5 | "Array found" → https://169.254.239.27, Launch | 1→2 | 🟡 |
| 6 | Cloud Connectivity Wizard Welcome (needs IPv4 + Time/DNS + Proxy) | 2/4 | 🟡 |
| 7 | Wizard EULA | 4 | 🟡 |
| 8 | Wizard Proxy step (Proxy.bgl1…:8080) | 4 | 🟡 |
| 9 | Wizard Time/NTP (NTP1.bgl1…, Asia/Kolkata) | 4 | 🟡 |
| 10 | Wizard Review (IP/DNS/NTP/proxy) | 4 | 🟡 |
| 11 | Connecting — applying network settings | 4→5 | 🟡 |
| 12 | Connecting 85% — subscription key shown (YHHD7UUA5T2TY9TP80EZ) | 3 | 🔴 |
| 13 | FAILED — `fail-prov-no-device` (SGHD44LQLS / S0B84A) | 5 | — |
| 14 | GreenLake login + workspace list, Create new workspace | login+6 | 🔴 |
| 15 | Create workspace form (Enterprise, India) | 6 | 🔴 |
| 16 | Asset explorer Devices — No devices — Add devices | 7 | ✅ |
| 17 | Add devices: Storage; fields **Serial number + Product number** | 7 | ✅ |
| 18 | Device added: SGHD44LQLS / S0B84A | 7 | ✅ |
| 19 | Review add devices → Finish | 7 | ✅ |
| 20 | Devices list: model B10100, Service blank / no subscription | 7 done (= `fail-prov-no-rule` cause) | — |
| 21 | Subscriptions → Add device subscription | 8 | ✅ |
| 22 | Add subscription key YHHD7UUA5T2TY9TP80EZ | 8 | ✅ |
| 23 | Review subscription → Finish | 8 | ✅ |
| 24–25 | Subscription listed — tier "HPE Data Services Res Svc E-LTU", exp 2031 | 8 done | ✅ |
| 26 | Wizard retry — still `fail-prov-no-device` (propagation) | 5/11 | — |
| 27 | Wizard retry running | 11 | 🟡 |
| 28 | Devices: **Service = "Data Services / AP NorthEast"** set | 9/10 (app+region bound) | ✅ |
| 29 | Wizard 100% "now connected" → Launch DSCC | 11 success | 🟡 |
| 30 | DSCC Data Ops Manager dashboard (console-jp1), 1 system | 12 | 🟡 |
| 31 | DSCC apps incl. Setup Service | 13 | 🟡 |
| 32 | Setup Service — Set Up System; "Not initialized"; Blueprints tab | 14 | 🟡 |
| 33 | Setup Wizard — Network Domain (DNS) | 14 | 🟡 |
| 34 | Setup Wizard — System step + Create Secret (3paradm creds) | 14 | 🟡 |
| 35 | Setup Wizard — Review — RED "no subscription, attach first" | 14→15 | 🟡 |
| 36 | **Apply subscription** to device (Data Services tier + key) | 15 | ✅ |
| 37 | Finalize — "Save as a new blueprint"; init 2% | 14 | 🟡 |
| 38 | Init 6% + CDM cabling warning (physical) | 14 (+🔴) | 🟡 |
| 39 | Init 100% Completed | 14 | 🟡 |
| 40 | Setup Service: Setup Status "Initialized", blueprint set | 14 done | 🟡 |
| 41 | Array mgmt UI https://10.64.122.140/system/overview — Normal, OS 10.5.51 | 16 verify | 🟡/✅ |

**Screenshot-derived refinements:** (1) storage device-add = **serial + part number**, subscription added & applied **separately**; (2) the application instance = **"Data Services"**; map display region **"AP NorthEast"** to GreenLake region id `ap-northeast` and DSCC host code `jp1`; (3) DSCC **"Setup system" enforces an attached subscription before finalizing** (confirms ordering); (4) the Setup wizard **creates a reusable Blueprint** (batch lever); (5) the array genuinely needs **DNS + NTP + Proxy** outbound (confirms ">443" allowlist); (6) physical gotcha: a **CDM cabling warning** can fail initialization regardless of automation.

---

## 8. Primary sources

- GreenLake Device Management — [API reference](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/openapi/nbapi-inventory-latest/devices-v1) · [developer guide](https://developer.greenlake.hpe.com/docs/greenlake/services/device-management/public/guide/)
- GreenLake Subscription Management — [Add subscriptions](https://developer.greenlake.hpe.com/docs/greenlake/services/subscription-management/public/openapi/nbapi-subscription-latest/operation/postSubscriptions/)
- GreenLake Workspace Management — [API](https://developer.greenlake.hpe.com/docs/greenlake/services/workspace/public/openapi/workspace-management-v1/nb-api-workspaces)
- GreenLake Service Catalog (app instance + region) — [developer guide](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/guide) · [Service Manager API](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/openapi/service-catalog-v1beta1/v1/service-manager) · [glossary](https://developer.greenlake.hpe.com/docs/greenlake/services/service-catalog/public/glossary)
- GreenLake Storage Fleet (post-init B10000 settings/verification) — [developer guide](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public) · [API reference](https://developer.greenlake.hpe.com/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1)
- Alletra MP B10000 connectivity — [Network requirement details (sd00002385)](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00002385en_us&page=GUID-24BE868B-C227-4A87-8727-93A11831E38A.html&docLocale=en_US) · [Cloud Enablement Quick Start / Websites (sd00002403)](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00002403en_us&page=GUID-A1201D1E-6CB8-4647-AA3D-EBCB405C51FC.html&docLocale=en_US) · [Configuring ports (sd00002429)](https://support.hpe.com/hpesc/public/docDisplay?docId=sd00002429en_us&page=GUID-29E578B3-4CED-4A92-BF88-04ECCC8166E7.html&docLocale=en_US)
- GreenLake [Authentication guide](https://developer.greenlake.hpe.com/docs/greenlake/guides/public/authentication/authentication) · [API client credentials guide](https://developer.greenlake.hpe.com/docs/greenlake/services/credentials/public/guide)
- DSCC — [live storage API spec (storage-api.yaml)](https://console-us1.data.cloud.hpe.com/doc/api/v1/storage-api.yaml) · [OAuth2 for DSCC](https://developer.hpe.com/blog/oauth2-for-hpe-greenlake-data-services-cloud-console/) · [Getting started with the DSCC public REST API](https://developer.hpe.com/blog/getting-started-with-the-hpe-data-services-cloud-console-public-rest-api/)
- Alletra MP B10000 — [Power Up & Initialization (Discovery Tool / Cloud Connectivity)](https://support.hpe.com/hpesc/public/docDisplay?docId=psg000248aen_us&page=GUID-17F9016E-C729-483B-B75F-A90BD2D345A7.html&docLocale=en_US) · [Web Services API home](https://developer.hpe.com/platform/hpe-alletra/home/)
- Reusable assets — [gl-mcp](https://github.com/HewlettPackard/gl-mcp) · [DSCC PowerShell Toolkit](https://github.com/HewlettPackard/HPEDSCC-PowerShell-Toolkit) · [Data Services Ansible](https://github.com/HewlettPackard/greenlake-data-services-ansible) · [Data Services Python](https://github.com/HewlettPackard/greenlake-data-services-python)
