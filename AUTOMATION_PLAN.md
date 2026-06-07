# Alletra MP B10000 Onboarding Automation — Implementation Plan (Python)

_Companion to `FEASIBILITY.md`. Stack: **Python**. Scope: end-to-end onboarding of a newly-shipped HPE Alletra Storage MP B10000 into HPE GreenLake + DSCC. The HPE Discovery Tool is **out of scope** (the array's link-local URL is supplied as input). Browser automation may **always attach to an already-logged-in session** (SSO/MFA is solved by session reuse)._

---

## 1. Architecture overview

Three components + an orchestrator, run as one Python package **from the jump box** (it has internet, link-local reachability to the array, and a browser):

```
                          ┌──────────────────────────── orchestrator ────────────────────────────┐
 inputs (per array) ─────▶│  per-array state machine · idempotent · resumable · batch · logging    │
  serial, partNumber,     └───────┬───────────────────────┬────────────────────────┬──────────────┘
  subscriptionKey,                │ 1                      │ 2                       │ 3
  cloudinit URL,                  ▼                        ▼                         ▼
  net cfg, dscc cfg     ┌──────────────────┐    ┌──────────────────────┐   ┌────────────────────┐
                        │ A) GreenLake REST │    │ B) Connectivity      │   │ C) DSCC Setup      │
                        │    (headless)     │    │    Wizard (Playwright)│   │   (Playwright)     │
                        │ register+subscribe│    │  on-array cloudinit   │   │  Setup/Blueprint   │
                        │ +assign+verify    │    │  (link-local, no auth)│   │ (logged-in session)│
                        └──────────────────┘    └──────────────────────┘   └────────────────────┘
                          internet                jump-box ↔ 169.254.x        internet + browser
```

**Execution order per array (the reorder that kills the docx error loop):**
**A (REST) → B (Connectivity Wizard) → C (DSCC Setup).**
Doing A first means the array is already in inventory + subscribed + assigned, so B connects on the first try and C's "no subscription" gate never fires.

### Repo / module layout
```
alletra_onboard/
├── pyproject.toml
├── config/
│   ├── settings.toml            # non-secret defaults (base URLs, timeouts, regions)
│   └── arrays.csv|json          # per-array work items (batch input)
├── alletra_onboard/
│   ├── __main__.py              # CLI entry (typer)
│   ├── config.py                # pydantic-settings loader; secrets via env/.env
│   ├── models.py                # pydantic models (work item, results, API DTOs)
│   ├── logging.py               # structured logging + run summary
│   ├── state.py                 # per-array state store (JSON/SQLite) for resume
│   ├── orchestrator.py          # runs A→B→C per array; batch; partial-failure
│   ├── greenlake/               # COMPONENT A (REST, headless)
│   │   ├── auth.py              # OAuth2 client-credentials + token cache
│   │   ├── client.py           # httpx wrapper: base URL, bearer, retry, async-poll
│   │   ├── service_catalog.py  # discover application.id + region
│   │   ├── subscriptions.py    # preclaim + add subscription
│   │   ├── devices.py          # add device + assign/subscribe + get
│   │   └── verify.py           # assignedState == ASSIGNED_TO_SERVICE
│   ├── browser/                 # shared Playwright plumbing
│   │   ├── session.py          # attach to logged-in session (CDP) or storage_state
│   │   └── helpers.py          # resilient locators, wait-for-progress, screenshots
│   ├── connectivity_wizard/     # COMPONENT B (Playwright)
│   │   └── wizard.py
│   └── dscc/                    # COMPONENT C (Playwright)
│       └── setup.py
└── tests/                       # pytest + respx (REST) + Playwright traces
```

### Tech stack
`httpx` (REST) · `tenacity` (retry/backoff) · `pydantic` + `pydantic-settings` (config/models) · `playwright` (browser) · `typer` (CLI) · `rich` (console tables) · `structlog` or stdlib `logging` · `pytest` + `respx` (tests). Reference code: **`gl-mcp`** (Python; exact GreenLake-platform auth + GET patterns) and **`greenlake-data-services-python`** (DSCC mgmt, for verification later).

---

## 2. Configuration & inputs

**Secrets (env / `.env`, never committed):**
`GL_CLIENT_ID`, `GL_CLIENT_SECRET`, `GL_MEMBER_WORKSPACE_ID`, optional `GL_TOKEN_URL` (default `https://sso.common.cloud.hpe.com/as/token.oauth2`), `GL_BASE_URL` (default `https://global.api.greenlake.hpe.com`).

**Per-array work item (`models.ArrayWorkItem`):**
| Field | Used by | Source |
|---|---|---|
| `serial_number`, `part_number` | A (register) | box / label |
| `subscription_key` | A (subscribe) | box / Activation Receipt |
| `target_region` | A (assign), C (host) | site plan (e.g. `AP NorthEast`/`jp1`) |
| `cloudinit_url` (e.g. `https://169.254.239.27/cloudinit`) | B | supplied (Discovery Tool done manually) |
| `mgmt_ipv4`, `mask`, `gateway`, `dns[]`, `ntp`, `timezone`, `proxy{host,port,user,pass}` | B, C | site network plan |
| `dscc_system_name`, `dscc_country`, `dscc_credentials{name,user,pass}` | C | site plan |
| `blueprint_name`, `apply_blueprint` (bool) | C | fleet template |
| `tags`, `support_contact` | A, C | optional |

**Defaults (`settings.toml`):** API version pins (`devices=v1`, `preclaim=v2beta1`), poll/timeout values, rate-limit budgets (devices 25/min, subs 4/min), DSCC region→host map (`us1/eu1/jp1/uk1`).

---

## 3. Component A — GreenLake REST (headless)

Base `https://global.api.greenlake.hpe.com`; bearer from OAuth2 client-credentials (member-workspace-scoped client); scope `ccs.device-management.edit` (+`.view`, + service-catalog view). **Every write is GET-guarded for idempotency; every POST is async (202 → poll).**

### Auth (`auth.py`)
`get_token()` → POST token URL (`grant_type=client_credentials`), cache JWT + expiry, refresh on 401/expiry. Single shared token for all GreenLake calls.

### Client (`client.py`)
Thin httpx wrapper: injects bearer, `tenacity` retry (429 honoring rate budgets + 5xx backoff), and a `poll_async(location)` helper that follows `Location → GET /devices/v1/async-operations/{id}` until `SUCCEEDED|FAILED|TIMEOUT` (surfacing the per-serial breakdown).

### Pipeline (per array)
```
0. token = auth.get_token()
1. DISCOVER
   app = service_catalog.find_application(service="Data Services", region=target_region)
        → GET /service-catalog/v1/service-manager-provisions  → {application_id, region, resourceUri}
   pre = subscriptions.preclaim(subscription_key)         # v2beta1, read-only pre-flight
        → GET /subscriptions/v2beta1/{key}/preclaim        → {claimStatus, aaSType, devices[]}
        → assert claimStatus == NOT_CLAIMED (or already-ours); abort early on wrong key
   state snapshot: devices.get_by_serial(serial), subscriptions.get_by_key(key)
2. ADD SUBSCRIPTION (idempotent)
   if key not present: POST /subscriptions/v1/subscriptions {subscriptions:[{key}]} → 202 → poll
   subscription_id = subscriptions.get_by_key(key).id
3. REGISTER DEVICE (idempotent)
   if serial not in inventory:
     POST /devices/v1/devices {storage:[{serialNumber, partNumber, tags}]} → 202 (+transactionId) → poll
   device_id = devices.get_by_serial(serial).id
4. ASSIGN + SUBSCRIBE (idempotent)   ← isolate behind devices.assign() (see lab-check)
     PATCH /devices/v1/devices?id={device_id}  (application/merge-patch+json)
       { application:{id: app.application_id}, region: app.region, subscription:[{id: subscription_id}] }
     → poll if async
5. VERIFY
   d = devices.get(device_id)
   assert d.assignedState == "ASSIGNED_TO_SERVICE" and d.application.id and d.subscription[0].id
   return ArrayResult(...)
```

### Notes / decisions
- **Device add body:** `serialNumber` + `partNumber` (the v1 guide's `subscriptionKey` example is a doc artifact). Subscription is added & applied **separately**. (v2beta1 alt: flat `{serialNumber, partNumber, deviceType:"STORAGE"}`.)
- **`devices.assign()` is an abstraction seam.** Default = the verified `PATCH`. If the lab shows assignment is actually bundled into the v2beta1 POST or driven by subscription-claim, we swap the function body only — pipeline shape unchanged. (This is open-item #1.)
- **Verification signal** = device `assignedState` flipping to `ASSIGNED_TO_SERVICE` (+ `application.id`, `subscription[].id`). Cross-confirmed: `application.resourceUri` → `/service-catalog/.../service-managers/…`.
- **Dry-run:** the device PATCH supports a dry-run query param → expose `--dry-run` for safe rehearsal.

---

## 4. Component B — Connectivity Wizard (Playwright, on the jump box)

Drives the array's on-array `cloudinit` web UI. **No auth** (local link-local, self-signed cert). **Must run on the jump box** (only it can reach `169.254.x`). Steps mirror the screenshots (img6–13).

### Setup
- `browser/session.py → new_local_context()`: `chromium.launch()` → `new_context(ignore_https_errors=True)` (self-signed). Fresh context is fine (no auth).
- Resilient locators only: `get_by_role`, `get_by_label`, `get_by_text` (never brittle CSS/auto-IDs). Centralize all selectors in `connectivity_wizard/wizard.py` for one-place maintenance.

### Flow (`run_wizard(work_item)`)
```
goto(cloudinit_url)
if "already configured / connected" detected: return ALREADY_DONE        # idempotent (first-boot only)
Welcome      → click "Get Started"
EULA         → scroll EULA container to end → check "I have read and accept" → Next
Network      → fill IPv4 address/mask/gateway → add DNS server(s) → Next
Proxy        → if proxy: fill server/port (+NTLM creds) ; else skip → Next
Time         → fill NTP server, select Region + Country/City (timezone) → Next
Review       → assert summary matches inputs → Submit/Connect
PROGRESS     → poll the running screen:
                 success: text "Your system is now connected" / 100% / "Launch Data Services Cloud Console"
                 failure: "Failed" + capture error text (fail-prov-*)
return WizardResult(connected: bool, subscription_key_shown, error_text)
```

### Robustness
- **Expect success on first pass** (Component A ran first). If it fails with `fail-prov-*`, do **not** blind-retry — surface the error (means A didn't propagate); the orchestrator decides.
- Generous waits on the progress screen (network apply + DSCC check take time); poll text, don't fixed-sleep.
- Screenshot + Playwright trace on any failure.
- **Optional fast-path (stretch):** the progress screen polls a backend, implying a JSON endpoint under `/cloudinit`. A one-time network capture could let us `POST` the config directly and skip the browser for B entirely. Plan keeps Playwright as default; flag the capture as a cheap optimization experiment.

---

## 5. Component C — DSCC Setup (Playwright, logged-in session)

Drives DSCC **Setup Service → Set Up System** (first array) or **Apply Blueprint** (subsequent arrays). Host = `https://console-{region}.data.cloud.hpe.com`. **Auth assumption: always attach to an already-logged-in session.**

### Session (`browser/session.py`)
- `attach_logged_in()` — primary: `chromium.connect_over_cdp("http://localhost:9222")` to attach to the human's Chrome already authenticated to GreenLake/DSCC (start that Chrome once with `--remote-debugging-port=9222`). Reuse its context/page.
- Fallback: `chromium.launch_persistent_context(user_data_dir=…)` or `storage_state=auth.json` captured after a manual login.
- Either way, the script never handles SSO/MFA — it inherits the session.

### Flow (`run_setup(work_item)`)
```
page = session.attach_logged_in()
goto DSCC Setup Service (region host) → System Setup
find system row by serial
  precondition: Connection Status == "Connected"  (else B/A incomplete → abort with clear msg)
  if Setup Status == "Initialized": return ALREADY_DONE          # idempotent
if work_item.apply_blueprint and blueprint exists:
    select system → "Apply Blueprint" → choose blueprint_name → confirm
else:
    select system → "Set Up System" wizard:
      Welcome
      Network Domain  → add DNS server(s)
      Time            → NTP server + timezone
      Attributes      → (site attributes)
      System          → system name, country, mgmt IPv4/mask/gateway,
                        Create Secret (credentials name/user/pass)
      Review&Finalize → assert NO "device has no subscription" banner   # A guarantees this
                        optional: check "Save as a new blueprint" + name (first array only)
                        Submit → start initialization
POLL initialization modal until "100% Completed"
   (device setup→system manager→hw check→commit network→init storage→support→restart→sw update)
   capture non-fatal warnings (e.g. CDM cabling) → surface, don't fail
verify Systems tab: Setup Status == "Initialized"
return DsccResult(initialized: bool, blueprint_name, warnings[])
```

### Robustness
- React SPA → role/text locators; centralize selectors; long async → poll progress text with generous timeout (minutes), close-and-reopen-safe (the UI says setup continues if dialog closed).
- **Blueprint = the batch lever:** first array creates/saves the blueprint; subsequent arrays use Apply Blueprint (few fields, far less to break).
- Screenshot + trace on failure; surface the "no subscription" banner as a hard error pointing back to Component A.

---

## 6. Orchestrator, state & batch

`orchestrator.run(work_item)` executes **A → B → C**, each step:
1. checks persisted state (`state.py`) — skip already-completed steps (resume),
2. runs the component,
3. records result + timestamp,
4. on failure: stop that array, mark step failed, continue with next array (batch isolation).

- **State store:** per-array JSON (or SQLite) keyed by serial → `{phaseA, phaseB, phaseC, ids, status, errors}`. Makes the whole flow **idempotent & resumable** (re-run continues where it stopped — matches the docx's retry reality).
- **Batch:** `arrays.csv|json` → process sequentially (browser steps are inherently serial per machine; the REST Phase A can optionally run with limited concurrency).
- **CLI (typer):**
  `onboard run --array SERIAL` · `onboard run --batch arrays.csv` · `--only A|B|C` · `--dry-run` · `--from-step` · `onboard status` · `onboard verify`.
- **Output:** `rich` summary table (per array: A/B/C status, device_id, region, initialized?, warnings) + structured logs + exit codes; Playwright traces/screenshots saved per failed step.

### Where each runs (single host = jump box)
| Component | Network need | Auth |
|---|---|---|
| A GreenLake REST | internet → global.api | OAuth2 token (headless) |
| B Connectivity Wizard | link-local → 169.254.x | none (local) |
| C DSCC Setup | internet → console-{region} | attach logged-in session |

Running the orchestrator on the jump box satisfies all three.

---

## 7. Cross-cutting: errors, retries, logging, security
- **Retries:** `tenacity` — REST 429 (respect 25/min devices, 4/min subs) + 5xx exponential; token refresh on 401; browser steps retry idempotently or fail with trace.
- **Error mapping:** translate to actionable messages — *no available subscription seats*, *serial/part mismatch*, *no Data Services provision in region X*, *device claimed in another workspace*, *DSCC "no subscription" banner → Phase A incomplete*, *array unreachable on link-local*.
- **Logging:** structured, per-array correlation id (serial); secrets redacted; run summary table; Playwright trace on failure.
- **Security:** secrets only via env/`.env`/secret store; never commit; token in memory only; least-privilege API client (edit on Devices & Subscription + view on Service Catalog).

---

## 8. Build milestones
1. **Skeleton + auth + smoke test** — `config`, `auth`, `client`, `GET /devices`. Proves member-workspace creds + scope. *(validates the org/member assumption)*
2. **Discovery** — `service_catalog.find_application` + `subscriptions.preclaim`. *(validates GAP 1 live; confirms application.id + region)*
3. **Register + subscribe** — add subscription + add device with async polling + idempotency.
4. **Assign + verify** — `devices.assign()` + verify `assignedState`. *(resolves open-item #1: PATCH vs bundled)*
5. **Connectivity Wizard (B)** — Playwright on jump box, end-to-end to "connected".
6. **DSCC Setup (C)** — Playwright on logged-in session: Set Up System + Save Blueprint; then Apply Blueprint path.
7. **Orchestrator + state + batch + CLI + reporting.**

Each milestone is independently testable; 1–4 need only API creds, 5 needs a lab array, 6 needs a connected system + logged-in DSCC.

---

## 9. Open items to confirm in the lab (cheap, early)
1. **Assignment-call form** (open-item #1): PATCH `/devices?id=` vs v2beta1 bundled POST vs subscription-claim. Isolated behind `devices.assign()`. *(Milestone 4)*
2. **Member-scoped creds** cover device + subscription writes + service-catalog reads. *(Milestone 1)*
3. **PATCH sync vs async** + exact response field names (`application.id`, `subscription[].id` confirmed; check `region` placement — may be implied by the per-region service-manager). *(Milestone 4)*
4. **Wizard selectors** (B and C) — need one live capture each to finalize locators (the only thing that can't be written blind). *(Milestones 5–6)*
5. **Region/timezone field formats** in both wizards. *(Milestones 5–6)*

## 10. Out of scope (handled elsewhere / manual)
HPE Discovery Tool (manual; link-local URL supplied as input) · physical rack/cable/power · primary/org & member workspace creation (prerequisite) · firewall/proxy allowlist for the DSCC tunnel (one-time IT change; FQDNs in HPE docs sd00002403/2385/2429) · obtaining the subscription key (from box/Activation Receipt).
