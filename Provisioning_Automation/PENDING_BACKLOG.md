# Pending Backlog

This backlog captures what remains before `alletra_onboard` is a complete end-to-end HPE Alletra MP B10000 onboarding automation tool. It is based on the current repository state, `IMPLEMENTATION_PLAN.md`, and the latest audit.

## Current Status

The project is currently at the foundation stage:

- Python package, domain models, workflow phase enum, FastAPI shell, Typer CLI shell, SQLite run/event store, GreenLake read-only preflight, and GreenLake payload helpers are implemented.
- Backend tests pass for the implemented slice.
- The actual multi-phase execution engine is not yet implemented.
- Browser adapters for cloudinit and DSCC Setup are placeholders until real UI pages are captured and locator behavior is verified.
- The React dashboard is a static starter shell and does not yet call the local API.

## Priority 0 - Lab UI Capture Inputs

These are needed before reliable Playwright automation can be completed.

- Capture the cloudinit wizard screens from the jump host:
  - Welcome / Get Started
  - EULA / acceptance
  - Network management IPv4 / mask / gateway / DNS
  - Proxy / no proxy / proxy auth if used
  - Time / NTP / timezone
  - Review summary
  - Progress success
  - Progress failures, especially `fail-prov-no-device` and `fail-prov-no-rule`
- Capture the DSCC Setup Service screens from an authenticated browser session:
  - DSCC application shell after login
  - Setup Service entry point / navigation
  - System list with serial search/filter
  - Row states: Connected, not connected, Initialized, not initialized
  - Missing subscription banner or warning
  - Apply Blueprint flow
  - Manual Set Up System wizard screens
  - Initialization progress and warning states
  - Final Initialized verification
- For each captured screen, collect:
  - Screenshot
  - HTML snapshot
  - Visible text snapshot
  - Candidate buttons/inputs/labels/headings for locator design
- Avoid capturing real passwords, MFA codes, real subscription keys, or customer-sensitive values. Use dummy data in form fields where possible.

## Priority 1 - Run Engine And Persistence

- Implement a durable workflow runner that executes phases in order:
  - `PREFLIGHT`
  - `GL_DISCOVER_SERVICE`
  - `GL_ADD_SUBSCRIPTION`
  - `GL_REGISTER_DEVICE`
  - `GL_ASSIGN_APPLICATION`
  - `GL_APPLY_SUBSCRIPTION`
  - `GL_VERIFY_DEVICE`
  - `CLOUDINIT_CONNECT`
  - `DSCC_SETUP_SYSTEM`
  - optional `STORAGE_FLEET_VERIFY`
  - `COMPLETE`
- Add phase execution records:
  - phase name
  - attempt number
  - started/ended timestamps
  - status
  - idempotency decision
  - active async operation ID
  - error code/remediation
  - artifact IDs
- Add persistent tables or equivalent models for:
  - arrays / imported work items
  - phase executions
  - external resources
  - artifacts
  - operator notes
- Implement resume logic:
  - Re-read external GreenLake state before retrying writes.
  - Start from the first incomplete phase.
  - Verify completed phases instead of blindly repeating them.
- Implement retry logic:
  - Retry only safe/idempotent phases.
  - Surface terminal failures with actionable remediation.
- Implement pause/cancel safe points:
  - Do not abandon an active GreenLake async operation without reconciling it.
  - Mark local runs `CANCEL_REQUESTED` when cancellation is requested during an external operation.

## Priority 2 - GreenLake REST Write Path

- Create an application service for the full GreenLake onboarding pipeline.
- Service Catalog discovery:
  - Read provisioned Data Services service manager by GreenLake region.
  - Persist `serviceManager.id` as `service_manager_id`.
- Subscription phase:
  - Read by subscription key first.
  - Add subscription only if missing.
  - Poll returned `Location` to terminal state.
  - Re-read and persist `subscription_id`.
- Device registration phase:
  - Read by serial first.
  - Add storage device only if missing using serial number and part number.
  - Poll returned `Location` to terminal state.
  - Re-read and persist `device_id`.
- Application assignment phase:
  - Verify current device application/region first.
  - PATCH application and region only.
  - Poll returned `Location` to terminal state.
- Subscription application phase:
  - Verify current device subscriptions first.
  - PATCH subscription only.
  - Poll returned `Location` to terminal state.
- Verification phase:
  - Require `assignedState == "ASSIGNED_TO_SERVICE"`.
  - Require expected `application.id`.
  - Require expected GreenLake region.
  - Require expected `subscription[].id`.
- Implement async polling behavior:
  - Recognize `SUCCEEDED`, `FAILED`, `TIMEOUT`, `TIMEDOUT`, and `PAUSED`.
  - Honor suggested polling interval when present.
  - Persist operation IDs and progress events.
- Improve HTTP behavior:
  - Endpoint-specific rate buckets.
  - Runtime adjustment from GreenLake rate-limit headers when available.
  - 429 and transient 5xx retry/backoff.
  - Redacted error reporting.

## Priority 3 - Cloudinit Browser Automation

- Replace the placeholder cloudinit adapter with real Playwright automation.
- Use a fresh Chromium context with `ignore_https_errors=True`.
- Validate URL starts with `https://169.254.`.
- Implement screen handling:
  - Already connected/configured detection.
  - Welcome start button.
  - EULA scroll/check/next.
  - Network input and validation.
  - Proxy/no-proxy/auth input.
  - NTP/timezone input.
  - Review summary validation against the work item.
  - Submit/connect.
  - Progress success/failure polling.
- Classify failures:
  - `fail-prov-no-device` -> GreenLake device registration issue.
  - `fail-prov-no-rule` -> GreenLake assignment/subscription issue.
  - generic failed states -> retryable or terminal based on text.
  - unreachable link-local URL -> `WAITING_FOR_OPERATOR`.
- Write artifacts:
  - trace zip
  - failure screenshot
  - DOM snapshot on failure
  - structured step log
- Add tests:
  - static HTML locator tests for every screen
  - already-done detection
  - fail-prov classification
  - summary mismatch terminal failure
  - artifact creation on failure

## Priority 4 - DSCC Setup Browser Automation

- Replace the placeholder DSCC adapter with real Playwright/CDP automation.
- Attach to a browser already logged in to DSCC using `http://localhost:9222`.
- Validate remote debugging is localhost only.
- Navigate to `https://console-{dscc_region_code}.data.cloud.hpe.com`.
- Detect login redirect and return `WAITING_FOR_OPERATOR`.
- Open Setup Service using direct URL or role/text navigation.
- Locate target array by serial number.
- Implement idempotency checks:
  - Already `Initialized` -> `ALREADY_DONE`.
  - Not `Connected` -> `FAILED_RETRYABLE`.
  - Missing subscription banner -> `FAILED_TERMINAL`.
- Implement blueprint path:
  - Select row.
  - Apply Blueprint.
  - Choose requested blueprint.
  - Review and submit.
  - Poll progress.
- Implement manual setup path:
  - Set Up System.
  - Network Domain/DNS.
  - Time/NTP/timezone.
  - Attributes/site metadata.
  - System details.
  - Credential selection/creation using secret reference.
  - Review and submit.
- Poll initialization progress and capture structured warnings.
- Verify final Initialized status in the list view.
- Write artifacts:
  - trace zip
  - failure screenshot
  - DOM snapshot on failure
  - structured step log
- Add tests:
  - not logged in classification
  - list row status parsing
  - missing subscription detection
  - initialized idempotency
  - blueprint path
  - manual setup path
  - warning capture
  - CDP disconnect handling

## Priority 5 - API Surface

Implement the planned local API endpoints:

- `GET /config` for non-secret effective config.
- `POST /inventory/import` for CSV/JSON work item import.
- `GET /inventory/arrays` for known arrays.
- `POST /runs` for single and batch run creation.
- `POST /runs/{run_id}/resume`.
- `POST /runs/{run_id}/pause`.
- `POST /runs/{run_id}/cancel`.
- `POST /runs/{run_id}/retry-phase`.
- `GET /runs/{run_id}/events` as an event stream or polling-compatible feed.
- `GET /browser/status` for DSCC CDP/login readiness.
- `GET /artifacts/{artifact_id}` for logs, screenshots, traces, and summaries.

## Priority 6 - CLI Surface

Expand the CLI so it calls the same services/API behavior:

- `onboard ui start`
- `onboard preflight --array SERIAL`
- `onboard run --array SERIAL`
- `onboard run --batch config/arrays.csv`
- `onboard status --run RUN_ID`
- `onboard resume --run RUN_ID`
- `onboard retry-phase --run RUN_ID --phase GL_APPLY_SUBSCRIPTION`
- `onboard verify --array SERIAL`
- `onboard export --run RUN_ID --format markdown`

## Priority 7 - React Dashboard

- Replace static starter content with API-driven views.
- Required views:
  - dashboard summary
  - inventory import
  - preflight result view
  - run list
  - run detail timeline
  - phase logs/events
  - retry/resume/pause/cancel controls
  - browser readiness status
  - artifacts download view
- Display operator states clearly:
  - waiting for DSCC login
  - link-local unreachable
  - missing secret reference
  - GreenLake async operation active
  - retryable failure
  - terminal failure
- Add frontend tests or component-level checks once UI behavior exists.
- Keep UI localhost-only and avoid storing secrets in browser state.

## Priority 8 - Configuration And Intake

- Decide whether `settings.example.toml` is loaded directly or remains documentation only.
- If TOML is intended, implement TOML loading and environment override behavior.
- Add config validation for:
  - API bind host must default to `127.0.0.1`.
  - DSCC CDP URL must be localhost.
  - known GreenLake/DSCC region mapping.
  - artifact directory.
- Extend CSV intake for:
  - `dscc_setup.password_ref`
  - proxy username
  - proxy password reference
  - tags if needed
  - support contact if needed
  - storage fleet enable flag
- Ensure subscription keys remain redacted in logs, events, reports, and API responses.

## Priority 9 - Storage Fleet Module

- Implement regional host mapping by GreenLake region.
- Discover B10000 systems after DSCC initialization.
- Match systems by serial/name/known IDs.
- Verify expected post-init state.
- Add read smoke for settings:
  - system settings
  - network settings
  - support settings
  - licenses
- Add optional write/update support only after lab confirmation.
- Add tests with mocked regional API responses.

## Priority 10 - Testing And Hardening

- Add unit tests for every phase decision.
- Add contract tests for async poller terminal states.
- Add mocked GreenLake integration tests with `respx`.
- Add SQLite concurrency tests for UI reads plus orchestrator writes.
- Add migration/startup schema tests.
- Add browser tests using captured/static HTML.
- Add trace/screenshot artifact assertions.
- Add export redaction tests.
- Add dry-run mode where GreenLake supports it.
- Add operator documentation for jump host prerequisites.

## Suggested Implementation Order

1. Capture real cloudinit and DSCC UI artifacts.
2. Add tests around captured UI snapshots and locator constants.
3. Implement GreenLake REST write service and async poller.
4. Implement durable phase execution and run/resume engine.
5. Implement Cloudinit adapter using captured pages.
6. Implement DSCC adapter using captured pages.
7. Add API/CLI controls for run lifecycle.
8. Make dashboard API-driven.
9. Add Storage Fleet post-init verification.
10. Run lab dry-runs, then controlled real onboarding runs.
# Pending Backlog

Updated: 2026-06-08

This backlog tracks what is still required to move the current `alletra_onboard` implementation from the first foundation slice to a complete end-to-end HPE Alletra MP B10000 onboarding automation.

## Current Status

The repository currently contains a working foundation:

- Python package layout, domain models, workflow phase enum, and phase ordering.
- FastAPI health, run create/list/get, and preflight endpoints.
- Typer CLI for API startup, run creation, status, and preflight.
- SQLite run and run event persistence with WAL and busy timeout.
- GreenLake OAuth, read-only preflight, and low-level clients for Devices, Subscriptions, and Service Catalog.
- Correct GreenLake payload helpers for storage device add, application assignment, and subscription apply.
- Placeholder/shell Playwright adapters for Cloudinit and DSCC.
- Static React/Vite dashboard starter.
- Backend tests and Ruff lint pass for the existing slice.

The automation is not yet complete end to end. The main missing piece is the actual phase execution engine that runs the 11-phase workflow, plus real browser automation for the Cloudinit and DSCC UI islands.

## External UI Inputs Needed

The Cloudinit and DSCC browser phases cannot be implemented reliably without seeing the real UI screens from the jump host. Use the capture scripts in `alletra_onboard/scripts/` to collect screenshots, sanitized DOM HTML, visible text, and control metadata.

### Cloudinit Screens Needed

Capture these screens from `https://169.254.x.x/cloudinit`:

1. Welcome or already-configured screen.
2. EULA acceptance screen.
3. Network management IP/mask/gateway/DNS screen.
4. Proxy configuration or no-proxy screen.
5. Time/NTP/timezone screen.
6. Review/summary screen before submit.
7. Progress screen while connecting.
8. Success screen.
9. Any failure screen, especially `fail-prov-no-device`, `fail-prov-no-rule`, or generic failed state.

### DSCC Screens Needed

Capture these screens from an already-authenticated browser session:

1. DSCC console landing/application shell.
2. Setup Service entry point/navigation.
3. Setup Service system list with target serial visible.
4. Row state for `Connected` but not initialized.
5. Row state for already `Initialized`, if available.
6. Missing subscription banner/message, if seen.
7. Blueprint selection flow.
8. Manual `Set Up System` wizard screens.
9. Network Domain/DNS screen.
10. Time/NTP/timezone screen.
11. Attributes/site metadata screen.
12. System details screen.
13. Credential selection/creation screen, without exposing passwords.
14. Review/submit screen.
15. Initialization progress screen.
16. Final initialized verification screen.
17. Any warning or failure screen.

Do not capture passwords, MFA codes, API secrets, or subscription keys in screenshots. The scripts avoid reading browser cookies/local storage and blank form field values in saved HTML/control metadata, but screenshots can still show sensitive data if it is visible on screen.

## Milestone 1: Project Foundation

Status: mostly done.

Pending:

- Add automated schema migrations or a lightweight migration runner.
- Add structured JSONL logging per run.
- Add non-secret effective config endpoint.
- Make `config/settings.example.toml` match actual settings loading, or implement TOML loading.
- Expand CSV intake to include `dscc_setup.password_ref`, proxy username, and proxy password reference.
- Add tests for config loading and CSV secret-reference mapping.

Acceptance criteria:

- `onboard status`, `onboard preflight`, and `onboard api` work from a clean editable install.
- Settings can be provided consistently by environment variables and/or the documented local config file.
- No secret values are persisted to SQLite, logs, artifacts, or exported reports.

## Milestone 2: GreenLake Read-Only Foundation

Status: mostly done.

Pending:

- Add permission-specific diagnostics where GreenLake returns 401/403.
- Add tests for HTTP error formatting across Devices, Subscriptions, and Service Catalog.
- Add optional preclaim support only when available, with fallback to existing read/add flow.

Acceptance criteria:

- Live preflight can confirm OAuth, Service Catalog provision, device serial state, and subscription key state.
- All live preflight failures produce actionable remediation text with redacted sensitive values.

## Milestone 3: Cloud REST Write Path

Status: pending.

Tasks:

- Create a GreenLake phase service used by the workflow orchestrator.
- Implement `GL_DISCOVER_SERVICE`:
  - Read per-region service managers where needed.
  - Read service-manager provisions filtered by `status eq 'PROVISIONED' and region eq '<region>'`.
  - Persist `service_manager_id` and `service_catalog_region_id`.
- Implement `GL_ADD_SUBSCRIPTION`:
  - Read by key first.
  - Add subscription if missing.
  - Poll returned `Location` to terminal state.
  - Re-read and persist `subscription_id`.
- Implement `GL_REGISTER_DEVICE`:
  - Read by serial first.
  - Add storage device if missing using serial number and part number.
  - Poll returned `Location` to terminal state.
  - Re-read and persist `device_id`.
- Implement `GL_ASSIGN_APPLICATION`:
  - Read current device state first.
  - PATCH only `{application, region}` when needed.
  - Poll returned `Location`.
  - Verify assigned state/application/region.
- Implement `GL_APPLY_SUBSCRIPTION`:
  - Read current device subscription state first.
  - PATCH only `{subscription}` when needed.
  - Poll returned `Location`.
  - Verify subscription assignment.
- Implement `GL_VERIFY_DEVICE`:
  - Require `assignedState == ASSIGNED_TO_SERVICE`.
  - Require expected `application.id`.
  - Require expected `region`.
  - Require expected `subscription[].id`.
- Implement terminal async polling:
  - Handle `SUCCEEDED`, `FAILED`, `TIMEDOUT`, `TIMEOUT`, and `PAUSED`.
  - Honor suggested polling intervals where present.
  - Persist operation IDs and progress events.
- Implement endpoint-family token buckets:
  - `subscription_add`, `subscription_read`, `subscription_poll`.
  - `device_add`, `device_patch`, `device_read`, `device_poll`.
  - `service_catalog_read`.
- Update budgets from `ratelimit-*` headers when available.
- Map GreenLake errors to retryable/terminal/operator states.

TDD targets:

- Idempotent existing subscription does not POST.
- Missing subscription POSTs and polls before re-read.
- Existing device does not POST.
- Missing device POSTs and polls before re-read.
- Assignment and subscription are two separate PATCH calls.
- Combined assignment+subscription payload is never emitted.
- Poller handles every terminal status.
- Verification fails with clear remediation when any expected field is wrong.

Acceptance criteria:

- A dry/mock run can execute every GreenLake phase using fakes/respx without hitting live HPE APIs.
- A live run can stop before browser phases with the device registered, assigned, subscribed, and verified.

## Milestone 4: Workflow Engine, Resume, Events, and Artifacts

Status: pending.

Tasks:

- Replace the current preflight-only orchestrator with a full phase runner.
- Add `PhaseExecution` model/table.
- Persist phase start/end, attempt number, idempotency decision, status, external operation ID, error code, remediation, and artifact links.
- Resume from first incomplete phase.
- Re-read external GreenLake state before resuming any completed GreenLake phase.
- Add retry phase support for retryable failures.
- Add pause-after-safe-point support.
- Add cancel semantics for active external GreenLake operations.
- Emit structured events:
  - `phase.started`
  - `phase.skipped`
  - `phase.async_operation.created`
  - `phase.async_operation.progress`
  - `phase.verification.passed`
  - `phase.warning`
  - `phase.failed`
  - `phase.completed`
- Add artifact metadata table and artifact download service.
- Add run summary export.

TDD targets:

- New run starts at `PREFLIGHT`.
- Successful local preflight advances to `GL_DISCOVER_SERVICE`.
- Each successful phase advances exactly one phase.
- Storage Fleet phase is skipped when disabled.
- Resume starts from the first incomplete phase.
- Retry only permits failed/idempotent phases.
- Cancel with active async operation returns or records safe-point behavior.

Acceptance criteria:

- A run record shows accurate status, current phase, resources, warnings, and events.
- Operator can pause/resume/retry/cancel safely without corrupting state.

## Milestone 5: Cloudinit Browser Automation

Status: blocked on real UI captures.

Tasks:

- Use fresh Chromium context with `ignore_https_errors=True`.
- Validate URL starts with `https://169.254.`.
- Implement screen classification:
  - already configured/connected -> `ALREADY_DONE`.
  - welcome page -> continue.
  - unreachable/certificate/network timeout -> `WAITING_FOR_OPERATOR`.
- Implement wizard screens:
  - Welcome.
  - EULA.
  - Network.
  - Proxy.
  - Time/NTP.
  - Review validation.
  - Submit/connect.
  - Progress polling.
- Centralize selectors in `adapters/browser/locators.py`.
- Use role, label, and visible-text locators.
- Resolve proxy password from secret provider when configured.
- Save trace and failure screenshot under run artifacts.
- Classify failure text:
  - `fail-prov-no-device` -> terminal GreenLake registration problem.
  - `fail-prov-no-rule` -> terminal GreenLake assignment/subscription problem.
  - generic failed -> retryable or terminal based on message.

TDD targets:

- Static HTML page tests for each screen.
- Selector tests use role/label/text, not generated classes.
- Review mismatch returns `FAILED_TERMINAL`.
- `fail-prov-*` messages are not retried blindly.
- Synthetic failure writes screenshot/artifact metadata.

Acceptance criteria:

- Lab run can complete Cloudinit from a clean array, or classify the exact blocking state with artifacts.

## Milestone 6: DSCC Setup Browser Automation

Status: blocked on real UI captures.

Tasks:

- Attach to existing Chrome/Edge session over CDP at `http://localhost:9222`.
- Require localhost CDP binding only.
- Navigate to `https://console-{dscc_region_code}.data.cloud.hpe.com`.
- Detect login redirect and return `WAITING_FOR_OPERATOR`.
- Open Setup Service.
- Locate target system by serial number.
- Implement idempotency checks:
  - `Initialized` -> `ALREADY_DONE`.
  - not `Connected` -> `FAILED_RETRYABLE`.
  - no subscription banner -> `FAILED_TERMINAL`.
- Implement blueprint flow when `apply_blueprint == true`.
- Implement manual setup wizard path:
  - Network Domain/DNS.
  - Time/NTP/timezone.
  - Attributes/site metadata.
  - System details.
  - Credentials.
  - Review/submit.
- Resolve setup admin password from `dscc_setup.password_ref`; never accept inline password in CSV/config.
- Poll initialization progress.
- Capture warnings as structured warnings.
- Verify final `Initialized` status.
- Save trace and failure screenshot under run artifacts.

TDD targets:

- Not-logged-in session returns `WAITING_FOR_OPERATOR`.
- Missing serial row is retryable shortly after Cloudinit, terminal after configured timeout/attempts.
- Missing subscription banner returns `FAILED_TERMINAL`.
- Already initialized returns `ALREADY_DONE`.
- Blueprint path selects requested blueprint.
- Manual path fills required screens using labels/roles.
- CDP disconnect returns `WAITING_FOR_OPERATOR`.

Acceptance criteria:

- Lab run can initialize a B10000 through DSCC Setup Service, or stop with a precise operator action and artifacts.

## Milestone 7: Storage Fleet Module

Status: pending.

Tasks:

- Add regional GreenLake host selection by GreenLake region ID.
- List B10000 `devtype4` systems.
- Match system by serial number/name after DSCC initialization.
- Persist `storage_fleet_system_id`.
- Add read-only verification smoke.
- Add optional settings verification/update for system, network, support, and licensing where safe.
- Add tests using fake regional HTTP client.

Acceptance criteria:

- Post-init verification can prove the initialized array appears in Storage Fleet.
- Optional settings checks never run before DSCC setup is complete.

## Milestone 8: API, CLI, and UI Completion

Status: pending.

API tasks:

- `GET /config` for non-secret effective config.
- `POST /inventory/import` for CSV/JSON work items.
- `GET /inventory/arrays`.
- `GET /runs/{run_id}/events` as event stream or pollable event list.
- `POST /runs/{run_id}/pause`.
- `POST /runs/{run_id}/resume`.
- `POST /runs/{run_id}/cancel`.
- `POST /runs/{run_id}/retry-phase`.
- `GET /browser/status`.
- `GET /artifacts/{artifact_id}`.

CLI tasks:

- `onboard ui start`.
- `onboard preflight --array SERIAL`.
- `onboard run --batch config/arrays.csv`.
- `onboard status --run RUN_ID`.
- `onboard resume --run RUN_ID`.
- `onboard retry-phase --run RUN_ID --phase PHASE`.
- `onboard verify --array SERIAL`.
- `onboard export --run RUN_ID --format markdown`.

UI tasks:

- Replace static starter dashboard with API-backed UI.
- Add inventory import.
- Add batch monitor table.
- Add run detail timeline.
- Show current phase, status, resource IDs, async operation IDs, warnings, and errors.
- Show browser/CDP readiness and DSCC login status.
- Show artifacts with download links.
- Add controls for pause, resume, cancel, and retry.
- Add operator-action states with clear next action.

TDD targets:

- API route tests with FastAPI test client.
- CLI tests through Typer runner.
- Frontend build/type check.
- UI component tests or smoke tests where practical.

Acceptance criteria:

- CLI and UI both call the same local API/application services.
- Operator can run and monitor a batch without manually editing SQLite.

## Milestone 9: Security, Redaction, and Operator Safety

Status: partially done.

Tasks:

- Extend redaction for subscription keys, password refs, bearer tokens, client secrets, and common HPE error payloads.
- Ensure screenshot/trace capture can be disabled or scoped if page content is sensitive.
- Never collect SSO passwords or MFA codes.
- Never store setup admin passwords inline.
- Validate CDP URL is localhost only.
- Add exported report redaction.
- Add security tests for persisted run payloads and artifacts.

Acceptance criteria:

- Secret values do not appear in tests, logs, events, SQLite, or exports.
- Browser capture scripts and automation clearly warn before saving screenshots.

## Milestone 10: Lab Validation

Status: pending.

Tasks:

- Run offline tests.
- Run mocked GreenLake end-to-end tests.
- Run live read-only GreenLake preflight.
- Run live GreenLake write path in a safe tenant/window.
- Capture Cloudinit UI screens.
- Implement and test Cloudinit automation against captured pages.
- Run Cloudinit lab test.
- Capture DSCC Setup UI screens.
- Implement and test DSCC automation against captured pages.
- Run DSCC lab test.
- Run post-init Storage Fleet verification.
- Export run summary and confirm artifacts are useful.

Acceptance criteria:

- A single array can progress from `NOT_STARTED` to `COMPLETE` with persisted state, artifacts, and verified external IDs.
- A second run against the same already-onboarded array is idempotent and does not repeat unsafe writes.

## Suggested TDD Order

1. Add tests for config/intake gaps.
2. Add tests for SQLite phase execution persistence.
3. Add tests for GreenLake async poller.
4. Add tests for each GreenLake phase using fake clients.
5. Implement GreenLake phase service.
6. Add orchestrator phase progression tests.
7. Implement orchestrator resume/retry/cancel basics.
8. Capture Cloudinit UI artifacts from jump host.
9. Add static HTML browser tests for Cloudinit screens.
10. Implement Cloudinit adapter.
11. Capture DSCC UI artifacts from jump host.
12. Add static HTML browser tests for DSCC screens.
13. Implement DSCC adapter.
14. Add Storage Fleet tests and implementation.
15. Expand API and CLI tests.
16. Implement UI API integration.
17. Run full backend, frontend, and lab validation.

## Files To Watch

- `src/alletra_onboard/application/orchestrator.py`
- `src/alletra_onboard/application/run_service.py`
- `src/alletra_onboard/application/greenlake_preflight.py`
- `src/alletra_onboard/adapters/greenlake/http_client.py`
- `src/alletra_onboard/adapters/greenlake/devices.py`
- `src/alletra_onboard/adapters/greenlake/subscriptions.py`
- `src/alletra_onboard/adapters/greenlake/service_catalog.py`
- `src/alletra_onboard/adapters/browser/cloudinit_wizard.py`
- `src/alletra_onboard/adapters/browser/dscc_setup.py`
- `src/alletra_onboard/adapters/browser/locators.py`
- `src/alletra_onboard/adapters/persistence/sqlite.py`
- `src/alletra_onboard/api/app.py`
- `src/alletra_onboard/cli/main.py`
- `frontend/src/main.tsx`
