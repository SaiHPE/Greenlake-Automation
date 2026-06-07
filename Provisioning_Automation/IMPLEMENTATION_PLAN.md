# Alletra MP B10000 Onboarding Automation - Implementation Blueprint

_Updated 2026-06-07. This is the implementation-ready architecture for the onboarding automation described in `FEASIBILITY.md` and `AUTOMATION_PLAN.md`._

---

## 1. Executive Summary

Build a local operator application that runs from the jump box and automates B10000 onboarding through a hybrid workflow:

1. GreenLake control-plane setup by REST.
2. Array `cloudinit` connectivity wizard by browser automation.
3. DSCC Setup System wizard by browser automation.
4. Optional Storage Fleet verification/settings by regional REST APIs after initialization.

The architecture is intentionally provider-agnostic at the core. The state machine, run model, UI, errors, artifacts, retries, and persistence do not know about HPE-specific APIs. HPE GreenLake, DSCC, Storage Fleet, and browser automation are adapters plugged into stable domain ports.

---

## 2. Goals and Non-Goals

### Goals

- Provide a clean local web UI for operators to run onboarding safely.
- Provide a CLI for scripted/lab execution.
- Use one local API shared by UI and CLI.
- Make every workflow phase idempotent and resumable.
- Capture structured logs, screenshots, Playwright traces, async operation IDs, and run summaries.
- Keep secrets out of files, logs, browser storage, and exports.
- Make endpoint contracts testable before lab runs.
- Keep provider-specific logic isolated in adapters.

### Non-Goals

- Automating rack/cable/power work.
- Automating the HPE Discovery Tool.
- Creating a primary GreenLake workspace.
- Automating SSO/MFA credentials.
- Replacing DSCC Setup System before HPE exposes a B10000 first-time setup API.

---

## 3. Architecture Principles

1. **API-first**: UI and CLI both call the same application services/local API.
2. **Ports and adapters**: domain workflow depends on interfaces, not GreenLake/DSCC implementations.
3. **Durable state machine**: every phase persists start, progress, external IDs, result, artifacts, and errors.
4. **Idempotent writes**: every write is guarded by a read and followed by verification.
5. **Explicit GUI islands**: unsupported API steps are modelled as browser automation phases, not hidden inside REST logic.
6. **Operator-aware automation**: when the system needs manual login, physical correction, or lab confirmation, the UI shows it as a first-class state.
7. **Secure by default**: localhost binding, no browser-side secrets, redaction everywhere.
8. **Contract-driven**: request bodies and response parsing are covered by contract tests derived from the scraped docs.

---

## 4. System Overview

```
Operator Browser
    |
    v
Local Web UI (React + TypeScript)
    |
    v
Local API (FastAPI) <---- CLI (Typer)
    |
    v
Application Services
    |-- RunService
    |-- PreflightService
    |-- WorkflowOrchestrator
    |-- EventBus
    |-- ArtifactService
    |
    v
Domain Core
    |-- WorkItem
    |-- Run
    |-- PhaseExecution
    |-- WorkflowStateMachine
    |-- ErrorCatalog
    |-- Port Interfaces
    |
    +--> GreenLake Adapter       -> global.api.greenlake.hpe.com
    +--> Cloudinit Browser       -> https://169.254.x/cloudinit
    +--> DSCC Browser            -> console-{dscc_region_code}.data.cloud.hpe.com
    +--> Storage Fleet Adapter   -> {gl-region}.api.greenlake.hpe.com
    +--> SQLite State Store
    +--> Artifact Store
    +--> Secret Provider
```

Runtime location: the jump box. It must have internet access, link-local array access, and a browser available for Playwright/CDP attachment.

---

## 5. Recommended Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Matches automation stack; good local API and UI hosting |
| HTTP | httpx | Explicit async/sync REST control |
| Models | pydantic v2 + pydantic-settings | Strong validation for work items and config |
| CLI | Typer + Rich | Good operator CLI and tables |
| Browser | Playwright | Reliable browser automation, traces, screenshots |
| UI | React + TypeScript + Vite | Rich run dashboard and real-time state display |
| State | SQLite + Alembic | Local, reliable, easy backup/export |
| Tests | pytest + respx + Playwright | Unit, contract, API mock, browser tests |
| Logs | structlog JSONL | Machine-readable run history |

---

## 6. Repository Layout

```
alletra_onboard/
├── pyproject.toml
├── README.md
├── config/
│   ├── settings.example.toml
│   └── arrays.example.csv
├── src/alletra_onboard/
│   ├── __main__.py
│   ├── api/
│   │   ├── app.py
│   │   ├── routes_runs.py
│   │   ├── routes_inventory.py
│   │   ├── routes_config.py
│   │   └── schemas.py
│   ├── cli/
│   │   └── main.py
│   ├── domain/
│   │   ├── models.py
│   │   ├── workflow.py
│   │   ├── ports.py
│   │   ├── errors.py
│   │   └── policies.py
│   ├── application/
│   │   ├── orchestrator.py
│   │   ├── run_service.py
│   │   ├── validation_service.py
│   │   ├── dry_run_service.py
│   │   └── event_bus.py
│   ├── adapters/
│   │   ├── greenlake/
│   │   │   ├── auth.py
│   │   │   ├── http_client.py
│   │   │   ├── devices.py
│   │   │   ├── subscriptions.py
│   │   │   ├── service_catalog.py
│   │   │   └── storage_fleet.py
│   │   ├── browser/
│   │   │   ├── session.py
│   │   │   ├── cloudinit_wizard.py
│   │   │   ├── dscc_setup.py
│   │   │   └── locators.py
│   │   ├── persistence/
│   │   │   ├── sqlite.py
│   │   │   ├── migrations/
│   │   │   └── artifacts.py
│   │   └── secrets/
│   │       ├── env_provider.py
│   │       └── keyring_provider.py
│   └── observability/
│       ├── logging.py
│       └── redaction.py
├── frontend/
│   ├── src/
│   └── package.json
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    └── e2e/
```

---

## 7. Operator UI

The UI is a local web app served by the FastAPI backend. It is not a marketing page; it is the actual operational surface.

### Views

| View | Purpose |
|---|---|
| Dashboard | Batch health, arrays by phase, blocked items, recent failures |
| Array Intake | Upload CSV/JSON, add/edit array work items, validate required fields |
| Preflight | Credentials, permissions, region mapping, subscription key, duplicate device, browser status, network reachability |
| Run Detail | Timeline, phase progress, async operation IDs, logs, retries, screenshots, traces |
| Batch Monitor | Dense table for many arrays; filter by status, phase, region, error class |
| Browser Session | CDP connection status, DSCC login status, manual login guidance |
| Artifacts | Download run summary, JSONL logs, screenshots, Playwright traces |
| Settings | Region maps, timeout profiles, rate-limit budgets, secret provider status |

### UI Rules

- No secrets in browser local storage.
- No subscription keys or passwords displayed after input/import unless explicitly unmasked by local operator policy.
- Every write action has a dry-run or preflight step where the API supports it.
- Every failure shows: cause, phase, endpoint/UI screen, retry safety, and next action.
- Browser failures show a screenshot and trace link.
- Batch tables are compact and scannable for repeated operator use.

---

## 8. Domain Model

### ArrayWorkItem

Required:

| Field | Meaning |
|---|---|
| `serial_number` | Array serial number |
| `part_number` | Product/part number for GreenLake device add |
| `subscription_key` | Key from box/activation receipt |
| `service_catalog_region_id` | GreenLake region id, e.g. `ap-northeast` |
| `dscc_region_code` | DSCC code, e.g. `jp1` |
| `cloudinit_url` | Link-local setup URL from Discovery Tool |
| `network_config` | Management IP, mask, gateway, DNS, NTP, timezone, proxy |
| `dscc_setup_config` | System name, country, credentials reference, blueprint options |

Optional:

- `tags`
- `support_contact`
- `location`
- `blueprint_name`
- `storage_fleet_enabled`
- `notes`

### Run

Stores:

- `run_id`, `batch_id`, `array_id`, `serial_number`
- overall status and current phase
- external IDs: `device_id`, `subscription_id`, `service_manager_id`, async operation IDs
- start/end timestamps
- warnings and final result

### PhaseExecution

Stores:

- phase name and attempt number
- status
- started/ended timestamps
- external operation ID
- idempotency decision
- error code and remediation hint
- artifact links

---

## 9. Workflow State Machine

```
NOT_STARTED
  -> PREFLIGHT
  -> GL_DISCOVER_SERVICE
  -> GL_ADD_SUBSCRIPTION
  -> GL_REGISTER_DEVICE
  -> GL_ASSIGN_APPLICATION
  -> GL_APPLY_SUBSCRIPTION
  -> GL_VERIFY_DEVICE
  -> CLOUDINIT_CONNECT
  -> DSCC_SETUP_SYSTEM
  -> STORAGE_FLEET_VERIFY   [optional]
  -> COMPLETE
```

Special states:

- `WAITING_FOR_OPERATOR`: manual browser login, missing secret, physical prerequisite.
- `RETRYABLE_FAILURE`: 429, transient 5xx, propagation delay, async still running.
- `TERMINAL_FAILURE`: wrong serial/part, key claimed elsewhere, missing Data Services provision, unsupported UI state.
- `CANCELLED`: stopped by operator at a safe boundary.

Resume rule: start from the first incomplete phase. Completed phases are verified but not repeated unless the operator uses a force option.

---

## 10. GreenLake REST Adapter

Global host: `https://global.api.greenlake.hpe.com`.

Required permissions:

- `ccs.device-management.view`
- `ccs.device-management.edit`
- `ccs.app-catalog.view`
- `ccs.app-provision.view`

### Service Catalog Discovery

1. `GET /service-catalog/v1/per-region-service-managers`.
2. Match `serviceManagers.name == "Data Services"` in `service_catalog_region_id`.
3. Store `serviceManagers.id` as candidate service manager id.
4. `GET /service-catalog/v1/service-manager-provisions?filter=status eq 'PROVISIONED' and region eq '<region>'`.
5. Match `items.serviceManager.id` and require `items.provisionStatus == "PROVISIONED"`.
6. Use `items.serviceManager.id` as Device PATCH `application.id`.

Important: public v1 service-manager-provision returns `serviceManager.id`, `region`, and `provisionStatus`; it does not return top-level `application_id`.

### Subscription Flow

1. Optional: `GET /subscriptions/v2beta1/{key}/preclaim` if the tenant allows it.
2. Idempotency read: `GET /subscriptions/v1/subscriptions?filter=key eq '<key>'`.
3. If missing: `POST /subscriptions/v1/subscriptions` with `{ "subscriptions": [{ "key": "..." }] }`.
4. Poll returned `Location` until terminal state.
5. Read subscription again and store `subscription_id`.

Rate limit: about 4 add-subscription requests/min/workspace.

### Proactive Rate Limiting

Do not rely only on reactive `tenacity` retries after `429`. The GreenLake docs expose rate-limit headers (`ratelimit-limit`, `ratelimit-remaining`, `rateLimit-reset`) and endpoint-specific limits, so the adapter should throttle before sending requests when the local budget is exhausted.

Implementation requirements:

- Maintain a token-bucket or leaky-bucket limiter per endpoint family and workspace/API client.
- Seed default budgets from the known endpoint limits:
  - subscription add: about 4/min/workspace
  - device add: 25/min/workspace
  - device update/PATCH: 20/min/workspace
  - device async polling: 90/min/workspace
  - subscription async polling: 30/min/workspace
- Adjust runtime budgets from returned `ratelimit-*` headers when present.
- Add jitter to retries after 429/5xx.
- In batch mode, queue REST writes rather than launching all array writes concurrently.
- Expose current budget and wait reason in the UI timeline, so an operator can distinguish throttling from a stuck run.

### Device Registration Flow

1. Idempotency read: `GET /devices/v1/devices?filter=serialNumber eq '<serial>'`.
2. If missing: `POST /devices/v1/devices`.
3. Storage payload must use `serialNumber + partNumber`:

```json
{
  "storage": [
    {
      "serialNumber": "<SERIAL>",
      "partNumber": "<PART_NUMBER>",
      "tags": {}
    }
  ]
}
```

4. Poll `/devices/v1/async-operations/{id}`.
5. Read device again and store `device_id`.

Rate limit: 25 add-device requests/min/workspace.

### Assignment and Entitlement Flow

Device PATCH supports only one operation per call.

Assign application:

```json
PATCH /devices/v1/devices?id=<device_id>
Content-Type: application/merge-patch+json

{
  "application": { "id": "<service_manager_id>" },
  "region": "<service_catalog_region_id>"
}
```

Apply subscription:

```json
PATCH /devices/v1/devices?id=<device_id>
Content-Type: application/merge-patch+json

{
  "subscription": [ { "id": "<subscription_id>" } ]
}
```

Each PATCH returns `202 + Location`; poll unconditionally.

Rate limit: 20 device update requests/min/workspace.

### Verification Gate

`GET /devices/v1/devices/{device_id}` must show:

- `assignedState == "ASSIGNED_TO_SERVICE"`
- `application.id == service_manager_id`
- `region == service_catalog_region_id`
- `subscription[].id` contains `subscription_id`

Only then proceed to browser phases.

---

## 11. Playwright Browser Automation Adapters

The implementation has two required Playwright adapters: one for the on-array Cloud Connectivity Wizard and one for DSCC Setup Service. They are isolated behind domain ports so selector churn and browser details do not leak into the workflow engine.

### Shared Browser Rules

- Use Playwright locators by role, label, and visible text wherever possible.
- Keep all selectors in `adapters/browser/locators.py` grouped by screen.
- Never use generated CSS classes, React IDs, or fragile absolute XPath unless there is no alternative.
- Every browser phase writes a Playwright trace and final screenshot on failure.
- Every long-running screen is polled by visible state/progress text, not fixed sleeps.
- The browser adapters return typed results: `ALREADY_DONE`, `SUCCEEDED`, `FAILED_RETRYABLE`, `FAILED_TERMINAL`, or `WAITING_FOR_OPERATOR`.
- The workflow engine owns retries; browser adapters do not recursively retry whole workflows.

### Browser Session Strategy

Cloudinit and DSCC use different browser contexts:

| Adapter | Browser mode | Auth model |
|---|---|---|
| Cloudinit wizard | fresh Playwright Chromium context with `ignore_https_errors=True` | no auth; link-local/self-signed |
| DSCC Setup | attach to already logged-in Chrome/Edge over CDP, e.g. `http://localhost:9222` | inherited SSO/MFA session |

The tool never collects SSO passwords, MFA codes, or DSCC credentials through the automation API. DSCC setup credentials entered into the wizard must be provided through a secret reference or a secure operator prompt outside model/chat logs.

### Cloud Connectivity Wizard Adapter

Module: `adapters/browser/cloudinit_wizard.py`

Input:

- `cloudinit_url`
- management IPv4, mask, gateway
- DNS servers
- NTP server
- timezone
- optional proxy host/port/user/password reference

Implementation flow:

1. Start a fresh context:

```python
browser = await chromium.launch(headless=False)
context = await browser.new_context(ignore_https_errors=True)
page = await context.new_page()
```

2. Navigate to `cloudinit_url` and classify current state:
  - `already configured` / `already connected` -> return `ALREADY_DONE`.
  - welcome page -> continue.
  - unreachable/certificate/network timeout -> `WAITING_FOR_OPERATOR` with link-local remediation.

3. Welcome screen:
  - Click `Get Started`, `Start`, or equivalent role button.

4. EULA screen:
  - Scroll EULA container if needed.
  - Check acceptance checkbox by label.
  - Click `Next`.

5. Network screen:
  - Fill management IPv4.
  - Fill subnet mask/prefix.
  - Fill gateway.
  - Add one or more DNS servers.
  - Validate that entered values are reflected before moving on.

6. Proxy screen:
  - If proxy is configured, fill host and port.
  - If proxy auth is configured, fill username and password from secret provider.
  - If proxy is not configured, choose `No proxy` / skip where present.

7. Time/NTP screen:
  - Fill NTP server.
  - Select timezone/region/city.
  - Validate summary values.

8. Review screen:
  - Read visible summary.
  - Compare against input model.
  - Stop with `FAILED_TERMINAL` if the UI summary does not match requested config.
  - Click submit/connect.

9. Progress screen:
  - Poll for success text such as `connected`, `100%`, or `Launch Data Services Cloud Console`.
  - Detect failure text such as `fail-prov-no-device`, `fail-prov-no-rule`, or generic `Failed`.
  - Map `fail-prov-*` to a GreenLake verification failure and stop rather than blind retrying.

10. Return result:
   - `connected=True`
   - any subscription key text shown by the wizard, masked in logs
   - warning/error text
   - screenshot/trace artifact IDs

Required tests:

- Static-page locator tests for each wizard screen.
- Failure classification tests for `fail-prov-no-device` and `fail-prov-no-rule`.
- Trace/screenshot generation test on synthetic failure.

### DSCC Setup Service Adapter

Module: `adapters/browser/dscc_setup.py`

Input:

- `dscc_region_code`, e.g. `jp1`
- array serial number
- system name
- country/site attributes
- DNS/NTP/timezone values used by setup
- management network values used by setup
- setup credential secret reference
- blueprint name and `apply_blueprint` flag

Implementation flow:

1. Attach to existing authenticated browser:

```python
browser = await chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]
page = context.pages[0] if context.pages else await context.new_page()
```

2. Validate browser session:
  - Navigate to DSCC console host `https://console-{dscc_region_code}.data.cloud.hpe.com`.
  - If redirected to login, return `WAITING_FOR_OPERATOR` with UI guidance to log in and retry.
  - If DSCC application shell loads, continue.

3. Open Setup Service:
  - Prefer direct URL if known from lab capture.
  - Otherwise navigate via app launcher/search using role/text locators.

4. Locate the target system:
  - Search/filter by serial number.
  - Read row fields: connection status, setup status, service/subscription indicators.
  - If not found, return `FAILED_RETRYABLE` if Cloudinit just completed, otherwise `FAILED_TERMINAL` with remediation.

5. Idempotency checks:
  - If setup status is `Initialized`, return `ALREADY_DONE`.
  - If connection status is not `Connected`, return `FAILED_RETRYABLE` pointing to Cloudinit/GreenLake verification.
  - If visible UI says no subscription attached, return `FAILED_TERMINAL` pointing to GreenLake apply-subscription phase.

6. Blueprint path:
  - If `apply_blueprint == true` and blueprint exists, select row -> `Apply Blueprint` -> choose blueprint -> review -> submit.
  - Record which blueprint was used.
  - Poll initialization progress.

7. Manual setup wizard path:
  - Select system row.
  - Click `Set Up System`.
  - Complete wizard screens:
    - Welcome.
    - Network Domain / DNS.
    - Time / NTP / timezone.
    - Attributes/site metadata.
    - System details: system name, country, management IP/mask/gateway.
    - Create/select credential secret for administrative setup credentials.
    - Review and finalize.
  - Optionally select `Save as a new blueprint` for the first system.
  - Submit initialization.

8. Initialization progress:
  - Poll progress text/percent until completed.
  - Capture warnings such as cabling warnings as structured warnings.
  - Treat hard failures as `FAILED_TERMINAL` with screenshot/trace.
  - Treat UI/session timeouts as `FAILED_RETRYABLE` if backend indicates setup continues.

9. Final verification:
  - Re-open/refresh systems view.
  - Verify setup status is `Initialized`.
  - Optionally call DSCC/Storage Fleet verification adapter after UI completion.

Required tests:

- Session-not-logged-in classification test.
- Static-page locator tests for Setup Service list and wizard screens.
- Missing-subscription banner detection test.
- Initialized idempotency test.
- Blueprint path test.
- Warning capture test.

### Browser Artifacts

Each browser phase writes artifacts under the run directory:

```text
artifacts/<run_id>/browser/
├── cloudinit-trace.zip
├── cloudinit-failure.png
├── dscc-setup-trace.zip
├── dscc-setup-failure.png
└── dom-snapshots/
```

Artifacts are referenced in the UI timeline and are downloadable from `/artifacts/{artifact_id}`. If traces are disabled by security policy, screenshots and structured step logs remain mandatory.

---

## 12. Storage Fleet Adapter

Storage Fleet is post-initialization only.

Regional hosts:

- `https://us-west.api.greenlake.hpe.com`
- `https://eu-west.api.greenlake.hpe.com`
- `https://eu-central.api.greenlake.hpe.com`
- `https://ap-northeast.api.greenlake.hpe.com`

Useful calls:

- `GET /storage-fleet/v1alpha1/devtype4-storage-systems`
- `GET /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}`
- `GET|PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/system-settings`
- `GET|POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/network-settings`
- `GET|POST|PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/support-settings`
- `GET|POST /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/licenses`

Do not use it as first-boot setup. The found `initialize` endpoint is port-level only: `.../ports/{id}/initialize`.

---

## 13. Local API Surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | API and dependency health |
| `GET` | `/config` | Non-secret effective config |
| `POST` | `/inventory/import` | Import CSV/JSON work items |
| `GET` | `/inventory/arrays` | List known arrays |
| `POST` | `/preflight` | Validate without writes |
| `POST` | `/runs` | Create run or batch run |
| `GET` | `/runs` | List runs |
| `GET` | `/runs/{run_id}` | Run detail |
| `GET` | `/runs/{run_id}/events` | Server-sent event stream |
| `POST` | `/runs/{run_id}/pause` | Pause after current safe point |
| `POST` | `/runs/{run_id}/resume` | Resume run |
| `POST` | `/runs/{run_id}/cancel` | Cancel run |
| `POST` | `/runs/{run_id}/retry-phase` | Retry failed/idempotent phase |
| `GET` | `/browser/status` | CDP/browser login readiness |
| `GET` | `/artifacts/{artifact_id}` | Download logs/traces/screenshots |

### Pause and Cancel Semantics

GreenLake Devices and Subscriptions async operation docs expose status polling (`GET /devices/v1/async-operations/{id}`, `GET /subscriptions/v1/async-operations/{id}`), but the relevant onboarding docs do not expose a cancel endpoint for an in-flight device add/update or subscription add operation.

Therefore pause/cancel must be safe-point based:

- If no external async operation is active, pause/cancel immediately after persisting state.
- If an async operation is active, the API returns `409 active_external_operation` unless the operator confirms `cancel_after_cloud_operation`.
- The UI should show: "GreenLake is already processing operation `<id>`. Local cancellation cannot stop the cloud task. Wait for completion or cancel locally after it reaches a terminal state."
- If the operator confirms local cancel while the cloud operation is active, mark the run `CANCEL_REQUESTED`, keep polling the cloud operation, then reconcile final state before marking the phase cancelled/failed/succeeded.
- Resume always starts by re-reading GreenLake state rather than trusting local phase state.

---

## 14. CLI Surface

```bash
onboard ui start
onboard preflight --array SERIAL
onboard run --array SERIAL
onboard run --batch config/arrays.csv
onboard status --run RUN_ID
onboard resume --run RUN_ID
onboard retry-phase --run RUN_ID --phase GL_APPLY_SUBSCRIPTION
onboard verify --array SERIAL
onboard export --run RUN_ID --format markdown
```

---

## 15. Persistence and Artifacts

SQLite tables:

- `arrays`
- `runs`
- `phase_executions`
- `run_events`
- `external_resources`
- `artifacts`
- `operator_notes`

Artifact layout:

```text
.alletra_onboard/
├── state.db
├── artifacts/
│   └── <run_id>/
│       ├── run.log.jsonl
│       ├── summary.md
│       ├── screenshots/
│       └── traces/
└── exports/
```

Do not store secrets in SQLite. Store only references such as `env:GL_CLIENT_SECRET` or `keyring:greenlake/client-secret`.

### SQLite Concurrency

SQLite is acceptable for a local jump-box controller, but the UI, event stream, and orchestrator can read/write at the same time. Configure SQLite intentionally:

- Enable WAL mode on startup: `PRAGMA journal_mode=WAL;`.
- Set a busy timeout, e.g. `PRAGMA busy_timeout=5000;`.
- Use short transactions; never hold a write transaction while waiting on network, browser, or async polling.
- Route run mutations through one application service/write queue where practical.
- UI polling and event streaming should be read-only and tolerant of brief retryable database contention.

### Automated Migrations

This is a local operator tool, so do not require operators to run database migrations manually.

- On API startup and CLI entry, acquire a migration lock.
- Run `alembic upgrade head` before accepting traffic or starting a run.
- Refuse to start if migration fails, and show a clear remediation message with the database path.
- Back up `state.db` before non-trivial migrations once real runs exist.

---

## 16. Error Model

| Category | Examples | Retry |
|---|---|---|
| `CONFIG` | missing serial, invalid region map, missing proxy | after edit |
| `AUTH` | token failure, missing permission, browser not logged in | after fix |
| `GREENLAKE_CONTRACT` | unexpected field, bad PATCH body, schema mismatch | no |
| `GREENLAKE_STATE` | device claimed elsewhere, subscription unavailable, no Data Services provision | after workspace fix |
| `RATE_LIMIT` | 429 from devices/subscriptions | automatic |
| `BROWSER_SELECTOR` | UI changed, locator missing | fix selector |
| `PHYSICAL` | cabling warning, array unreachable, link-local unavailable | manual |
| `PROPAGATION` | expected state not visible yet | bounded retry |

Every error includes a stable code, retryability, and remediation hint.

---

## 17. Security Model

- Bind local API to `127.0.0.1` by default.
- Optional LAN mode requires explicit config and an operator token.
- Store credentials in environment variables or OS keychain.
- Redact tokens, secrets, subscription keys, passwords, proxy credentials, and DSCC secret values.
- Never store secrets in browser local storage.
- Keep Playwright traces configurable because traces may capture page content.
- Exported reports must redact sensitive fields.
- Treat Chrome DevTools Protocol as sensitive. Bind Chrome remote debugging to localhost only, use a dedicated browser profile where possible, and never expose `localhost:9222` over the network.

---

## 18. Observability

Emit structured events:

- `phase.started`
- `phase.skipped`
- `phase.async_operation.created`
- `phase.async_operation.progress`
- `phase.verification.passed`
- `phase.warning`
- `phase.failed`
- `phase.completed`

The UI renders these as a timeline. Logs are JSONL and can be exported to Markdown/CSV.

---

## 19. Testing Strategy

### Unit Tests

- State transitions.
- Config validation.
- Region mapping.
- Redaction.
- Idempotency guards.
- SQLite WAL/busy-timeout initialization.
- Pause/cancel safe-point policy with active async operation IDs.
- Token-bucket limiter behavior.

### Contract Tests

- Device add payload uses `serialNumber + partNumber`.
- Device assignment PATCH contains only `application + region`.
- Device subscription PATCH contains only `subscription`.
- Service Catalog parser uses `serviceManager.id`, `region`, `provisionStatus`.
- Poller handles `SUCCEEDED`, `FAILED`, `TIMEOUT`, `TIMEDOUT`, `PAUSED`.

### Integration Tests

- Mock GreenLake with respx.
- Dry-run against real tenant where permitted.
- Storage Fleet read-only smoke test after DSCC setup.
- Concurrent UI read + orchestrator write against SQLite.
- Startup migration from an older test schema.

### Browser Tests

- Playwright tests against captured/static pages for locator stability.
- Lab-only end-to-end tests for cloudinit and DSCC setup.
- Trace and screenshot assertions.
- CDP disconnect handling: simulate `TargetClosedError`/connection reset and verify transition to `WAITING_FOR_OPERATOR`.

---

## 20. Build Milestones

1. **Project skeleton**: package layout, config, SQLite with WAL/migrations, logging, CLI, FastAPI health.
2. **GreenLake read-only foundation**: OAuth, devices, subscriptions, service catalog, permission diagnostics.
3. **Cloud REST write path**: proactive rate limiter, add subscription, add device, split PATCH assignment/subscription, polling, verification.
4. **UI shell and run engine**: dashboard, import, preflight, timeline, events, artifacts.
5. **Cloudinit browser automation**: link-local reachability, wizard automation, trace capture.
6. **DSCC setup automation**: CDP attach, setup wizard, blueprint path, progress polling.
7. **Storage Fleet module**: regional host map, B10000 discovery, settings read/write smoke.
8. **Batch hardening**: pause/resume/cancel safe-points, active async operation reconciliation, concurrency limits, exports, operator docs.

---

## 21. Lab Confirmations

1. Confirm `service-manager-provisions.items.serviceManager.id` is accepted as Device PATCH `application.id`.
2. Confirm Device PATCH `region` uses GreenLake region id (`ap-northeast`), not DSCC host code (`jp1`).
3. Confirm whether internal `GET /subscriptions/v2beta1/{key}/preclaim` is reachable with customer credentials.
4. Capture one cloudinit wizard and one DSCC setup run for selectors.
5. Confirm when the initialized system appears in Storage Fleet after DSCC setup.
6. Decide UI packaging mode: local-only app by default, or Windows service/LAN mode for a team.

---

## 22. First Implementation Slice

Start with a narrow but production-shaped vertical slice:

1. SQLite state + config + API health.
2. UI import page + preflight page.
3. GreenLake read-only discovery.
4. Add subscription and register device with dry-run support.
5. Split PATCH assignment/subscription flow.
6. Run timeline and logs.

This proves the architecture before investing heavily in browser automation, where selector drift is the highest-change surface.
