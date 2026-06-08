# Project Context: HPE Alletra MP B10000 Onboarding Automation

This workspace automates the end-to-end onboarding of HPE Alletra MP B10000 storage arrays into HPE GreenLake and DSCC (Data Services Cloud Console). It runs from a Windows jump box and combines three automation tracks under one local application.

---

## What We Are Building

A local Python operator application (`alletra_onboard`) that drives a strict 11-phase workflow per array:

```
NOT_STARTED → PREFLIGHT → GL_DISCOVER_SERVICE → GL_ADD_SUBSCRIPTION
→ GL_REGISTER_DEVICE → GL_ASSIGN_APPLICATION → GL_APPLY_SUBSCRIPTION
→ GL_VERIFY_DEVICE → CLOUDINIT_CONNECT → DSCC_SETUP_SYSTEM
→ STORAGE_FLEET_VERIFY (optional) → COMPLETE
```

Every phase is idempotent, resumable, and persisted to SQLite. The application exposes a local FastAPI REST API (127.0.0.1:8765), a Typer/Rich CLI, and a React/Vite dashboard. UI and CLI both call the same API.

---

## The Three Automation Tracks

### Track 1 — GreenLake REST API

Global host: `https://global.api.greenlake.hpe.com`
OAuth token endpoint: `https://sso.common.cloud.hpe.com/as/token.oauth2` (client_credentials flow)

**Service sequence:**

1. **Service Catalog discovery** — find the provisioned Data Services service manager for the target region.
   - `GET /service-catalog/v1/service-manager-provisions?filter=status eq 'PROVISIONED' and region eq '<region>'`
   - Critical: the response field is `serviceManager.id`, NOT `application_id`. `provisionStatus` is the status field.

2. **Subscription add** (idempotency read first)
   - Read: `GET /subscriptions/v1/subscriptions?filter=key eq '<key>'`
   - Write: `POST /subscriptions/v1/subscriptions` → body: `{"subscriptions": [{"key": "..."}]}`
   - Rate limit: ~4 adds/min/workspace. Poll returned `Location` header.

3. **Device registration** (idempotency read first)
   - Read: `GET /devices/v1/devices?filter=serialNumber eq '<serial>'`
   - Write: `POST /devices/v1/devices` → body: `{"storage": [{"serialNumber": "...", "partNumber": "...", "tags": {}}]}`
   - Rate limit: 25 adds/min/workspace. Poll `Location`.

4. **Assign application** (PATCH #1 — application only, no subscription in this call)
   - `PATCH /devices/v1/devices?id=<device_id>` with `Content-Type: application/merge-patch+json`
   - Body: `{"application": {"id": "<service_manager_id>"}, "region": "<service_catalog_region_id>"}`
   - Rate limit: 20 PATCHes/min/workspace. Returns `202 + Location`.

5. **Apply subscription** (PATCH #2 — subscription only, no application in this call)
   - Same PATCH endpoint, different body: `{"subscription": [{"id": "<subscription_id>"}]}`
   - **Device PATCH cannot combine application + subscription in one call.**

6. **Verification gate**
   - `GET /devices/v1/devices/{device_id}` must show `assignedState == "ASSIGNED_TO_SERVICE"`, correct `application.id`, correct `region`, and `subscription[].id`.

**Rate limiting:** Token-bucket limiter per endpoint family, seeded from known limits. Budget keys: `device_add`, `device_patch`, `device_read`, `subscription_add`, `subscription_read`, `service_catalog_read`. Sleep is always *outside* the lock to avoid deadlock.

**Secrets:** `GL_CLIENT_ID`, `GL_CLIENT_SECRET`, `GL_MEMBER_WORKSPACE_ID` — never in files, only environment variables.

**Async operations:** GreenLake device and subscription writes return `202 + Location`. Poll with `GET <location>` until `SUCCEEDED` / `FAILED` / `TIMEDOUT`. Operations expire 24h after reaching terminal state.

---

### Track 2 — Playwright: Cloud Connectivity Wizard (cloudinit)

Module: `src/alletra_onboard/adapters/browser/cloudinit_wizard.py`

The B10000 exposes a setup wizard at a link-local HTTPS URL discovered by the HPE Discovery Tool. This wizard cannot be driven by REST — it is a browser UI only.

**Browser context:** Fresh Playwright Chromium context with `ignore_https_errors=True` (self-signed cert on link-local address). Never reuse browser sessions between arrays.

**URL format:** `https://169.254.x.x/cloudinit` — must start with `https://169.254.` or preflight fails.

**Wizard screens (in order):**
1. Welcome → click `Get Started`/`Start`
2. EULA → scroll, check acceptance checkbox, click `Next`
3. Network → fill management IPv4, mask, gateway, DNS servers (can be multiple)
4. Proxy → fill host/port/credentials from secret provider, or select `No proxy`
5. Time/NTP → fill NTP server, select timezone
6. Review → validate UI summary matches input model before submitting
7. Progress → poll for success or failure text

**Success text patterns:** `connected`, `100%`, `Launch Data Services Cloud Console`
**Failure text patterns:** `fail-prov-no-device`, `fail-prov-no-rule`, generic `Failed`
- `fail-prov-*` means GreenLake state is wrong (device not registered or subscription not applied); do not retry blindly — fix GreenLake state first.

**Return values (typed):** `ALREADY_DONE`, `SUCCEEDED`, `FAILED_RETRYABLE`, `FAILED_TERMINAL`, `WAITING_FOR_OPERATOR`

**Artifacts written:** `artifacts/<run_id>/browser/cloudinit-trace.zip`, `cloudinit-failure.png`

**Locator rule:** Use role/label/visible-text locators. All selector constants live in `adapters/browser/locators.py` — never hardcode selectors in the wizard module. No fragile CSS class selectors.

---

### Track 3 — Playwright: DSCC Setup Service

Module: `src/alletra_onboard/adapters/browser/dscc_setup.py`

After GreenLake registration and cloudinit connectivity are complete, the array appears in DSCC Setup Service. This wizard must also be driven via browser — no first-boot REST API is exposed by HPE for B10000.

**Browser context:** Attach over CDP to an already-authenticated Chrome/Edge session (`http://localhost:9222` by default). The operator must be logged in to DSCC SSO/MFA manually — the automation never handles passwords or MFA.

**DSCC console URL format:** `https://console-{dscc_region_code}.data.cloud.hpe.com`
- Region code is different from GreenLake region ID:

| GreenLake region ID | DSCC region code |
|---|---|
| `ap-northeast` | `jp1` |
| `us-west` | `us1` |
| `eu-central` | `eu1` |
| `eu-west` | `uk1` |

**Setup flow:**
1. Attach to CDP → validate DSCC console is loaded (if redirected to login → `WAITING_FOR_OPERATOR`)
2. Open Setup Service → locate target array by serial number
3. Idempotency checks:
   - Already `Initialized` → `ALREADY_DONE`
   - Not `Connected` → `FAILED_RETRYABLE` (cloudinit/GreenLake issue)
   - No subscription banner → `FAILED_TERMINAL` (apply-subscription phase failed)
4. Blueprint path (if `apply_blueprint == true`): select row → `Apply Blueprint` → choose → review → submit
5. Manual wizard path: Set Up System → Network Domain/DNS → Time/NTP → Attributes → System details → credentials → review → submit
6. Poll initialization progress, capture warnings as structured warnings
7. Final verification: confirm `Initialized` status in list view

**Credential handling:** Setup admin password must be provided via `dscc_setup.password_ref` (e.g. `env:DSCC_SETUP_PASSWORD`), never inline in CSV/config.

**Artifacts written:** `artifacts/<run_id>/browser/dscc-setup-trace.zip`, `dscc-setup-failure.png`

---

## Domain Architecture

### Provider-agnostic core

The domain (models, workflow state machine, error catalog, ports) has zero knowledge of HPE APIs or browser specifics. All GreenLake, DSCC, browser, and SQLite details live in adapters. The domain depends only on Port interfaces (Protocol classes).

Key files:
- `src/alletra_onboard/domain/models.py` — `ArrayWorkItem`, `RunRecord`, `PreflightReport`, `WorkflowPhase`, `RunStatus`, `CheckStatus`, etc.
- `src/alletra_onboard/domain/workflow.py` — `next_phase()` state machine, `WORKFLOW_ORDER`
- `src/alletra_onboard/domain/policies.py` — `TokenBucket`, `RateBudget`, `redact()`
- `src/alletra_onboard/domain/ports.py` — `EventSink`, `RunStore`, `CloudinitWizard`, `DsccSetupWizard` Protocols

### Array work item (CSV columns)

```
serial_number, part_number, subscription_key, service_catalog_region_id,
dscc_region_code, cloudinit_url, mgmt_ipv4, mask, gateway, dns (semicolon-sep),
ntp, timezone, proxy_host, proxy_port, dscc_system_name, dscc_country,
blueprint_name, apply_blueprint
```

CSV example: `config/arrays.example.csv`

---

## Project File Layout

```
storage automation/                          ← workspace root
├── .github/
│   └── copilot-instructions.md             ← THIS FILE
├── Provisioning_Automation/
│   ├── IMPLEMENTATION_PLAN.md              ← full blueprint with all API contracts + Playwright flows
│   ├── AUTOMATION_PLAN.md                  ← high-level plan, pointers
│   ├── FEASIBILITY.md                      ← feasibility research
│   └── alletra_onboard/                    ← Python project (editable install: pip install -e .[dev])
│       ├── pyproject.toml                  ← hatchling build, entry: onboard = alletra_onboard.cli.main:app
│       ├── config/
│       │   ├── arrays.example.csv
│       │   └── settings.example.toml
│       ├── src/alletra_onboard/
│       │   ├── config.py                   ← pydantic-settings; reads from env or .env
│       │   ├── api/
│       │   │   ├── app.py                  ← FastAPI factory, all routes
│       │   │   └── schemas.py              ← request/response models incl. PreflightRequest.live_greenlake
│       │   ├── cli/main.py                 ← typer: api, run, status, preflight [--live-greenlake]
│       │   ├── domain/
│       │   │   ├── models.py
│       │   │   ├── workflow.py
│       │   │   ├── policies.py             ← TokenBucket (sleep outside lock), redact()
│       │   │   ├── ports.py
│       │   │   └── errors.py
│       │   ├── application/
│       │   │   ├── preflight_service.py    ← run_local() sync + run() async (local + optional live)
│       │   │   ├── greenlake_preflight.py  ← live read-only GreenLake checks (opt-in)
│       │   │   ├── orchestrator.py
│       │   │   ├── run_service.py
│       │   │   ├── intake.py               ← CSV loader, _split_semicolon() for DNS
│       │   │   ├── event_bus.py
│       │   │   └── validation_service.py
│       │   └── adapters/
│       │       ├── greenlake/
│       │       │   ├── auth.py             ← OAuthClientCredentials (client_credentials, 30s buffer)
│       │       │   ├── http_client.py      ← GreenLakeHttpClient + poll_location()
│       │       │   ├── devices.py          ← DevicesClient; payload helpers use TYPE_CHECKING guard
│       │       │   ├── subscriptions.py    ← SubscriptionsClient
│       │       │   ├── service_catalog.py  ← ServiceCatalogClient + parse_service_manager_provision()
│       │       │   └── storage_fleet.py    ← post-init only; regional hosts
│       │       ├── browser/
│       │       │   ├── cloudinit_wizard.py ← Track 2: fresh context, ignore_https_errors=True
│       │       │   ├── dscc_setup.py       ← Track 3: CDP attach to localhost:9222
│       │       │   ├── locators.py         ← all selector constants (CLOUDINIT_TEXT, DSCC_TEXT)
│       │       │   └── session.py
│       │       ├── persistence/
│       │       │   ├── sqlite.py           ← WAL + busy_timeout=5000; runs + run_events tables
│       │       │   └── artifacts.py
│       │       └── secrets/
│       │           └── env_provider.py
│       ├── frontend/                       ← React + TypeScript + Vite dashboard (starter shell)
│       └── tests/
│           ├── unit/                       ← workflow, policies, preflight, intake, GL preflight (17 tests)
│           └── contract/                   ← payload shapes, service catalog parser, read filter params
├── docs and plans/
│   └── greenlake_api_docs/                 ← LOCAL COPY of all HPE GreenLake developer docs
│       ├── llms.txt                        ← AI agent index: remote URLs → local file paths (2500 files)
│       ├── _llms.txt                       ← Table of contents with remote https:// URLs only
│       ├── .md                             ← root developer portal page
│       ├── assets/                         ← PNG diagrams, visual assets
│       └── greenlake/
│           ├── guides/                     ← authentication, rate-limiting, versioning, support
│           ├── services/                   ← per-service docs (see below)
│           └── services.md, guides.md, ...
└── webscraper/
    ├── scrape_greenlake_docs.py
    ├── generate_local_llms_txt.py
    └── scraped_docs/                       ← alternate scraped copy (same content, different layout)
```

---

## GreenLake API Documentation — Local Copies

The full HPE GreenLake developer portal is mirrored locally. **Always read local files rather than fetching from the internet.**

### Primary reference: `docs and plans/greenlake_api_docs/`

- `llms.txt` — AI agent index: maps document titles to `file://` local paths. Use this to find any specific doc. 2500 files indexed.
- `_llms.txt` — Table of contents with remote `https://` URLs; use for link references or when comparing with live docs.
- Individual markdown files mirror the structure of `https://developer.greenlake.hpe.com/docs/greenlake/`

### Service docs relevant to this project

| Service | Local path | Key for this project |
|---|---|---|
| Device Management | `greenlake/services/device-management/` | POST device, PATCH assign/subscribe, GET by serial |
| Subscription Management | `greenlake/services/subscription-management/` | POST add, GET by key, async polling |
| Service Catalog | `greenlake/services/service-catalog/` | service-manager-provisions, per-region-service-managers |
| Storage Fleet | `greenlake/services/storage-fleet/` | devtype4-storage-systems; post-init only |
| IAM / Auth | `greenlake/services/iam/`, `greenlake/guides/public/authentication/` | OAuth2, rate limits, permissions |

### Alternate scraped copy: `webscraper/scraped_docs/`

Same content, kept in sync by `webscraper/scrape_greenlake_docs.py`. Use if the primary copy is missing a specific path.

### Finding a specific API endpoint

1. Open `docs and plans/greenlake_api_docs/llms.txt` and search for the endpoint name or service.
2. Follow the local `file://` link to the markdown or OpenAPI spec file.
3. OpenAPI YAML specs are at `**/openapi/*.yaml` paths within each service folder.

---

## Configuration and Secrets

**Environment variables (never in files):**
- `GL_CLIENT_ID` — GreenLake API client ID
- `GL_CLIENT_SECRET` — GreenLake API client secret
- `GL_MEMBER_WORKSPACE_ID` — target workspace ID
- `DSCC_SETUP_PASSWORD` (or any name referenced in `dscc_setup.password_ref`) — DSCC admin setup credential

**Non-secret config:** `config/settings.example.toml` — copy to `config/settings.toml` locally.

**State store:** `.alletra_onboard/state.db` (SQLite WAL; excluded from git via `.gitignore`)

**API default:** `http://127.0.0.1:8765`

---

## CLI Quick Reference

```powershell
# Local offline preflight for a CSV batch
onboard preflight --file config\arrays.example.csv

# Local + live GreenLake read-only preflight (needs GL_CLIENT_* env vars)
onboard preflight --file config\arrays.example.csv --live-greenlake

# Start the local API server
onboard api

# Show all run states
onboard status

# Create a run for one array
onboard run --array SGHD44LQLS
```

---

## Critical Implementation Nuances

1. **Two-PATCH rule:** Device assignment (`application + region`) and subscription (`subscription`) must be two separate PATCH calls. Combining them in one call is rejected by the API.

2. **Service Catalog field name:** The response field is `serviceManager.id` (nested object), not `application_id`. The filter uses `status` but the response field is `provisionStatus`.

3. **Async operation polling:** Every write returns `202 + Location`. Always poll; do not assume immediate completion. Operations expire 24h after terminal state.

4. **Token-bucket lock discipline:** Release the asyncio lock *before* sleeping. Holding the lock during `asyncio.sleep()` blocks all other coroutines.

5. **TYPE_CHECKING guard on adapters:** Payload helper functions in `devices.py`, `subscriptions.py`, `storage_fleet.py` import `GreenLakeHttpClient` under `TYPE_CHECKING` only, so contract tests can import payload helpers without needing `httpx` installed.

6. **Browser CDP binding:** Chrome remote debugging must be bound to `localhost` only. Never expose port 9222 over the network.

7. **DSCC region codes differ from GreenLake region IDs:** `ap-northeast` (GL) ↔ `jp1` (DSCC). The mapping lives in `settings.example.toml` under `[regions.dscc]`.

8. **Cloudinit URL validation:** Must start exactly with `https://169.254.` — any other prefix fails the PREFLIGHT phase.

9. **`fail-prov-*` errors in cloudinit wizard are GreenLake state problems**, not network problems. The remediation is to fix GreenLake device registration or subscription assignment, not to retry the wizard.

10. **Preflight is two-tier:** `run_local()` is synchronous and offline. `run(item, live_greenlake=True)` appends live GreenLake read checks. The API accepts `"live_greenlake": true` in the POST body.

---

## Testing

```powershell
Set-Location Provisioning_Automation\alletra_onboard
python -m pytest -q        # 17 tests, all passing
python -m ruff check .     # zero lint issues
```

Test layout:
- `tests/unit/` — workflow state machine, token-bucket policy, preflight logic, CSV intake, live GL preflight (with fakes)
- `tests/contract/` — payload shape validation, service catalog parser, read-client filter params

All tests use fakes/stubs. No live GreenLake calls in the test suite.

---

## GitHub Repository

`https://github.com/SaiHPE/Greenlake-Automation` — branch `main`

Latest commits:
- `e89cec7` Add live GreenLake preflight checks
- `b4c4890` Add alletra_onboard implementation + scraped GreenLake API docs
