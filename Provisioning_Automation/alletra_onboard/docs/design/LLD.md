# Low-Level Design: Alletra Onboard

Companion to [HLD.md](HLD.md) and [docs/STANDARD.md](../STANDARD.md). This document holds the
low-level invariants that are not obvious from skimming the code. Where this document and the code
disagree, the code is right.

All relative paths below start from `Provisioning_Automation/alletra_onboard/`.

---

## 1. Boundaries beyond the import contracts

Python layer order, workflow order, writer protections and acyclic-sibling rules are defined and
enforced in `pyproject.toml` (`[tool.importlinter]`) and `quality/imports-type-only.toml` (the
`deps` gate step). See [HLD.md](HLD.md) §5 for the component diagram. Per STANDARD C2, no hand-copied
module table is kept here.

Structural rules that the Python import contracts cannot express:

- `application/unified_file/` imports only `domain/`; its callers (`provisioning/discovery.py` and
  `documents/steps.py`) pass in the read clients.
- `api/app.py` (`create_app`) and `application/service.py` (`OnboardingService`) wire the backend
  services; `api/app.py` is the only entrypoint permitted to open `SqliteRunStore`.
- In `frontend/src/`, ESLint confines `fetch` to `api.ts` and `EventSource` to `useRunEvents.ts`
  (STANDARD F1), and prevents step pages in `steps/` from importing each other (F2).
- Generated OpenAPI TypeScript types live in `frontend/generated/api.ts`, outside `frontend/src/`.

---

## 2. Run and step state machine

### 2.1 Step registry and modes

`domain/workflow.py` is the single definition of steps (`STEP_REGISTRY`), preset modes
(`_MODE_STEPS`), replication-gated steps (`REPLICATION_STEP_KEYS`) and unbuilt steps
(`NOT_BUILT_STEPS`). `GET /app/profile` serves them — plus `capabilities.wsapi_sdk` — to the UI.

- Every `StepDef` must name either its `lab_script` or a `no_lab_script` reason (STANDARD X4).
- `create_run` sets `status = READY` and `current_phase = initial_phase(mode, selected_steps)`. It
  refuses any step in `NOT_BUILT_STEPS`, any step missing its required workbook tab, and an empty
  Volumes tab when `provision` is selected.
- `next_enabled_phase` auto-advances only `kind == "init"` steps. Every other step starts on an
  explicit operator request.
- In the `init-only` build profile (`ALLETRA_PROFILE`), `/app/profile` locks the UI to
  `FULL_ONBOARDING` (it reports `init_only`; the sheets route serves the matching workbook template).

### 2.2 RunStatus and transitions

`RunStatus` lives in `domain/models.py`. Legacy rows carrying a retired status
(`_RETIRED_RUN_STATUSES`) still deserialize as `ready`.

| Step group | On start | On success | On failure |
|---|---|---|---|
| `greenlake` | `RUNNING`, `GL_DISCOVER_SERVICE` (walks `GL_*`) | `READY`, next init phase (or `PREFLIGHT` on dry run) | `RETRYABLE_FAILURE` |
| `cloudinit`, `dscc` | `RUNNING`, step phase | `READY` (next init phase) or `WAITING_FOR_OPERATOR` | `RETRYABLE_FAILURE` or `TERMINAL_FAILURE` |
| Read-only discovery, zoning plan, applies, replication/snapshot verify, failover test | `RUNNING`, step phase | `READY` | `RETRYABLE_FAILURE` |
| Plan previews, link check, zoning check (when unzoned), path verify | `RUNNING`, step phase | `WAITING_FOR_OPERATOR` (or `READY` when no action needed) | `RETRYABLE_FAILURE` |
| `verify`, `asbuilt` | Unchanged | Unchanged (events only) | Unchanged (events only) |
| `POST /runs/{id}/complete` | — | `SUCCEEDED`, `COMPLETE` | — |

Any unhandled exception escaping a spawned task is caught by `RunCoordinator._guarded`, setting
`RETRYABLE_FAILURE` and emitting `step.crashed` so a run is never left in `RUNNING`.

---

## 3. Typed run events, OpenAPI schema and SSE

The event registry lives in `domain/events.py` (`EVENT_TYPES`, `EventType[D]`, `NoData`). Stored
event compatibility and evolution rules live in
[ADR 0032](../adr/0032-typed-run-events-and-generated-frontend-types.md).

- **Static and runtime checking:** `EventType[D]` uses `D` in both `data: type[D]` and
  `dump(payload: D)` so pyright treats `D` as invariant. `RunCoordinator.emit` overloads
  `EventType[NoData]` and `EventType[D]`, catching mismatched payloads at every call site.
  `tests/conftest.py` (`_validate_emitted_events`) also validates every emitted payload during tests.
- **Generated frontend types:** `api/schemas.py` (`run_event_list`) attaches a discriminated union
  to `GET /runs/{run_id}/events` for OpenAPI documentation while runtime keeps
  `response_model=EventListResponse`. `scripts/api_types.py` generates `frontend/generated/api.ts`,
  verified by the `api-types` gate step. `frontend/src/api.ts` wraps schemas in `Wire<T>` while
  pages retain nullish guards for legacy stored events.
- **Worker binding and SSE streaming:** `RunCoordinator.spawn` copies `contextvars` with
  `command_log.bind(command_sink)` and `device_trust.bind(RunTrustBook)`. Worker threads push
  command records back to the event loop via `loop.call_soon_threadsafe(record_command)`.
  `api/routes/events.py` (`/runs/{run_id}/stream`) and `api/routes/console.py`
  (`/runs/{run_id}/console/stream`) share `sse_stream` in `api/routes/common.py`
  (`SSE_HEARTBEAT_S = 15.0`). Buses keep no backlog; `frontend/src/useRunEvents.ts` fetches
  `GET /runs/{run_id}/events`, opens SSE, deduplicates by `event_id` and refreshes the run record.

---

## 4. Approvals and durable in-progress apply records

Implemented under [ADR 0031](../adr/0031-least-privilege-in-three-stages.md) (STANDARD S2, S3, S5):

- **Plan hold and approval check:** Previewed plans live in memory in their step service under a
  fresh `plan_id` (`new_plan_id()`). Re-discovery, builder edits, re-preview or restart withdraws
  the hold. Every apply calls `check_approval(approved_plan, held_plan_id)` and rejects conflicts
  before requesting an `Approval`. Failover requires `authorised: true` on `FailoverTestRequest`
  (HTTP 409 otherwise).
- **Single-use `Approval` (`domain/approval.py`):** Identity-only (`eq=False`), never serialized,
  issued only by `RunCoordinator.issue_approval`. `is_busy(run_id)` remains true while a step task
  runs or an unspent approval exists.
- **Writer consumption:** `make_wsapi_writer`, `make_rc_writer` and `make_snap_writer` pull
  credentials strictly through `Approval.creds_for(purpose, side)`. Every write calls
  `approval.require_live()`. `RunCoordinator.run_approved(approval, fn)` binds `apply_record` onto
  `approval.save_record` and sets `approval.spent = True` in the worker thread's own `finally`.
- **Pre-write undo checkpointing (`application/runs/apply_record.py`):** `recorded_write` appends an
  inspect-first note (`maybe_made`) and saves the current result (including pre-recorded SSH removal
  lines per ADR 0025) to `run_artifacts` (`kind = 'apply_in_progress'`) before each write, then drops
  the note and saves the confirmed removal set on clean return. Terminal apply events
  (`TERMINAL_APPLY_EVENTS`) call `close_apply_record(run_id)`. On startup
  (`recover_interrupted_applies`) and `get_run`, `recover_interrupted_apply` promotes any unclosed
  record with no live task or terminal event to `*.apply.failed` or `failover.failed` +
  `RETRYABLE_FAILURE` via private `_append`.
- **Failover checkpointing (`application/replication/failover.py`):** `try_save_record` saves
  observed sides and recovery guidance before each DR send. A save error before step 1 aborts with
  nothing sent; a save error after step 1 is noted while the sequence continues to restore.
  `run_failover_test` returns a `FailoverRecord` and never raises on device errors.

---

## 5. Persistence schema, migrations and encryption

Implemented in `adapters/persistence/sqlite.py` and `adapters/persistence/secrets.py`:

- **SQLite settings:** WAL mode (`PRAGMA journal_mode=WAL`), `busy_timeout=5000`, `timeout=5`.
- **Migrations:** `MIGRATIONS` tuple indexed by `PRAGMA user_version`
  (`SCHEMA_VERSION = len(MIGRATIONS)`). `_migrate` applies pending entries in one `BEGIN IMMEDIATE`
  transaction and raises `StateDatabaseTooNewError` if the file's `user_version` exceeds
  `SCHEMA_VERSION`. Shipped entries are never edited; schema changes append a new entry.

| Table | Primary key | Purpose | Retention |
|---|---|---|---|
| `runs` | `run_id` | `RunRecord` JSON and indexed status, phase, timestamp | Kept |
| `run_events` | `event_id` | Ordered `RunEvent` timeline (unvalidated dicts on read) | Kept |
| `work_items` | `run_id` | `ArrayWorkItem` JSON with sealed secret fields | Kept |
| `provisioning_intents` | `run_id` | `ProvisioningIntent` JSON with sealed secret fields | Kept |
| `pending_sheets` | `token` | Uploaded workbook awaiting mode choice (single-use pop) | Purged after `PENDING_SHEET_TTL` (24 h) |
| `run_artifacts` | `(run_id, kind)` | Step caches, as-built `.docx`, `apply_in_progress` | Newest `ARTIFACT_RETENTION_RUNS` (20) runs; `apply_in_progress` exempt |
| `run_commands` | `(run_id, seq)` | Redacted device/cloud command log (64 KB output cap) | Newest `ARTIFACT_RETENTION_RUNS` (20) runs |
| `run_device_pins` | `(run_id, kind, host, port)` | Per-run SSH host key or TLS certificate pins (ADR 0026) | Kept with run |

- **Encryption at rest ([ADR 0027](../adr/0027-stored-credentials-encrypted-at-rest.md)):**
  `SecretBox` creates a Fernet key in `secrets.key` beside `state.db` on first save (`0o600` on
  POSIX, `O_CREAT | O_EXCL`). Only the paths listed in `_WORK_ITEM_SECRETS`, `_INTENT_SECRETS` and
  `pending_sheets` (`workbook_b64`) in `adapters/persistence/sqlite.py` are sealed as
  `{"fernet": "<token>"}`, leaving the rest readable for support. Older plaintext rows still open
  unchanged; a missing or wrong key raises `StoredCredentialsUnreadableError` (HTTP 409).

---

## 6. Rate limiting and GreenLake HTTP mechanics

See [AGENTS.md](../../../../AGENTS.md) (*Domain facts*) for GreenLake API quirks (two-PATCH
assignment, region code mapping, 202 polling). Code-level mechanics:

- **Token bucket (`domain/policies.py`):** `TokenBucket.acquire()` refills under `asyncio.Lock` and
  sleeps outside the lock.
- **Rate budgets and retries (`adapters/greenlake/http_client.py`):** Per-endpoint budgets live in
  `default_rate_buckets()`; unknown names fall back to `default`. Status codes in `RETRYABLE_STATUS`
  retry up to `max_retries` times (honouring `Retry-After`, capped at 30 s). Any other non-2xx
  raises `GreenLakeHttpError`.
- **Async polling:** `poll_async` polls a 202 `Location` until `TERMINAL_OK` or `TERMINAL_FAIL`,
  honouring `suggestedPollingIntervalSeconds`. An optional `settled()` inventory check escapes
  operation resources that stall after the resource already exists.
- **Service catalog read (`adapters/greenlake/service_catalog.py`):** `all_provisions()` reads
  `/service-catalog/v1/service-manager-provisions` unfiltered because the live API rejects
  `provisionStatus eq ...` and combined `and` filters with HTTP 400. `service_manager_provisions()`
  filters in Python on `provisionStatus`, `region` and `serviceManager.id`.
- **Console redaction:** GreenLake command records store method and path only (plus `?dry-run=true`);
  query strings, bodies and error text are omitted because subscription keys appear in all three.

---

## 7. Array SSH allowlists, write clients and WSAPI planes

### 7.1 Read-only SSH and diagnostics (`adapters/array/cli_client.py`)

- `refusal()` rejects any character in `_FORBIDDEN_CHARS` (shell metacharacters plus Tcl quoting and
  substitution characters), any first word outside `ALLOWED_COMMANDS`, and any acting flag in
  `_ACTION_OPTIONS` (such as `showtarget -rescan`). Both `ArrayCliClient.run()` and the operator
  console prompt ([SPEC-019](../specs/SPEC-019-console.md)) pass through `refusal()`.
- `run_diagnostic()` enforces whole-line regexes in `_DIAGNOSTIC_FORMS` (bounded `checkrclink` time
  and ping count) and is called only by `application/replication/link_check.py`.

### 7.2 Write-scoped SSH clients (ADR 0025)

`ArrayRcCliClient` (`adapters/array/rc_cli_client.py`, `RC_WRITE_FORMS`, `RcPlanObjects`,
[ADR 0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md)) and `ArraySnapCliClient`
(`adapters/array/snap_cli_client.py`, `SNAP_WRITE_FORMS`, `SnapPlanObjects`,
[ADR 0016](../adr/0016-snapshot-schedules-write-scoped-ssh.md)) both subclass `ArrayCliClient`:

- `run()` keeps the read allowlist so each apply reads back through the same session.
- `write()` requires a live `Approval` and plan-bound objects; an unbound client refuses every write.
- Commands match whole-line regexes (including IPv4/mask validation for RC, and inner `createsv`,
  cron, reserved-name and no-lock validation for snapshots), log with `write=True` and treat lines
  starting with `Error` (`domain/array_parse.answered_error`) as failures.

### 7.3 WSAPI v1, WSAPI v3 and Brocade switches

- **WSAPI v1 (`adapters/array/wsapi_client.py`, `adapters/array/wsapi_writer.py`):** `WsapiReader`
  wraps `python-3parclient` (minimum version pinned in `pyproject.toml` so login posts to
  `/api/v1/credentials`). `connect()` acts as the readiness gate (HTTP 503 → `WsapiNotReady`,
  [ADR 0003](../adr/0003-transport-wsapi-with-readiness-gate.md)). `WsapiWriter` subclasses
  `WsapiReader` with the mutating calls, each gated by `approval.require_live()`. Hardware quirks
  encoded in `WsapiWriter`: reduced volumes send `{"reduce": True}` only; `set_remote_copy_group`
  sends `syncPeriod` and `policies` in two separate PUTs; `EXISTENT_PATH` is never swallowed; HTTP
  400 code 28 translates oversized volume sizes into plain wording.
- **WSAPI v3 (`adapters/array/wsapi_v3_client.py`, [ADR 0021](../adr/0021-unified-file-over-wsapi-v3.md)):**
  GET-only plus `/api/v3/credentials` login and logout. Sends the JSON Content-Type header on GETs
  and forwards both `X-HP3PAR-WSAPI-SessionKey` and login cookies. `get()` returns
  `V3Answer` for any HTTP status; a refused login raises `WsapiV3LoginRefused`, and a transport or TLS
  failure raises `WsapiV3Error` / `WsapiV3TrustError`.
- **Brocade switches (`adapters/fabric/brocade_client.py`, `adapters/fabric/brocade_writer.py`):**
  `BrocadeClient` stays strictly read-only through `ALLOWED_READ` with zero write verbs
  ([ADR 0012](../adr/0012-no-switch-writes-the-tool-emits-a-command-set.md)). Opt-in Brocade FOS
  zoning apply uses `BrocadeZoneWriter` ([ADR 0033](../adr/0033-opt-in-brocade-zoning-apply.md)),
  built only via `application/provisioning/brocade_writer_factory.py` inside
  `application/provisioning/zoning_apply.py`, requiring a live `"zoning"` `Approval` and
  `ZoningPlanObjects`, accepting only five exact prompt-free forms (`alicreate`, `zonecreate`,
  `cfgadd`, `cfgenable "<cfg>" -f`, `cfgtransabort`) with pre-flight `cfgtransshow`/`cfgshow`
  guards, pre-write undo persistence and post-apply `cfgshow` read-back. `paramiko` is pinned below
  major 4 in `pyproject.toml` for older FOS switch SSH algorithms.

---

## 8. Error-handling contracts (STANDARD E1–E3) and API mapping

- **E1 (`DeviceError`):** All device and cloud adapter errors live in `domain/errors.py` under
  `DeviceError`. Non-`DeviceError` exceptions are `ApplyRecordError` (`domain/errors.py`),
  `ApprovalError` (`domain/approval.py`), `StoredCredentialsUnreadableError` (`domain/ports.py`),
  `DeviceTrustError` (`adapters/device_trust.py`, translated by adapters into their `DeviceError`
  subclass) and `StateDatabaseTooNewError` (`adapters/persistence/sqlite.py`). Ruff `BLE001` allows
  `except Exception` only in `application/runs/coordinator.py`, `api/app.py` and the ceilings in
  `quality/ceilings.toml`.
- **E2 (no silent swallowing):** Ruff `S110`/`S112` and `fitness[suppress]` forbid `except: pass`,
  `except: continue` and `contextlib.suppress(Exception)`.
- **E3 (truthful reads):** Unreadable devices report unknown or failed, never empty — e.g.
  `UnexpectedAnswer` (`application/unified_file/read.py`), `None` counts in `HandoverStatus`, and
  *not read* when vCenter is down during ESXi path checks.
- **E4 (plain wording):** `WsapiReader._translate` strips SDK method names and produces plain
  sentences (`Could not <action>. The array said: ...`).

### HTTP status mapping (`api/app.py` and `api/routes/`)

| Exception | HTTP | Where mapped |
|---|---|---|
| `RunNotFoundError`, `DevicePinNotFoundError`, missing artifact/intent | `404` | `api/routes/common.py`, `discovery.py`, `documents.py`, `snapshots.py`, `trust.py`, `zoning.py` |
| `RunBusyError`, `StepPreconditionError`, `StoredCredentialsUnreadableError` | `409` | `api/routes/common.py`, `api/app.py` (`_credentials_unreadable`), `console.py`, `provisioning.py`, `trust.py` |
| `PendingSheetNotFoundError` | `410` | `api/routes/runs.py` (`/runs/from-sheet`) |
| `ValueError`, `ValidationError`, workbook/CSV parse errors | `422` | `api/routes/runs.py`, `api/routes/sheets.py` |
| `PermissionError` (non-admin clock sync) | `403` | `api/routes/system.py` |
| `RuntimeError`, `OSError` (browser launch or clock sync failure) | `500` | `api/routes/system.py` |

---

## 9. Transport trust, process-wide hooks and test guards

### 9.1 Device trust and outbound TLS

- **Cloud (`adapters/tls.py`):** `ssl_context()` builds the union of the OS trust store, `certifi`
  and any `ALLETRA_CA_BUNDLE` / `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` file. Verification never turns
  off.
- **On-site devices (`adapters/device_trust.py`):** `open_ssh`, `check_tls` and `pinned_context`
  enforce per-run first-contact pins in `run_device_pins`. Setting `ALLETRA_DEVICE_CA_BUNDLE`
  switches WSAPI, vCenter and WinRM over HTTPS to full CA verification with no fallback; SSH stays on
  first-contact trust. Mismatches fail before sending credentials; re-trusting requires
  `POST /runs/{run_id}/trust/retrust` matching the offered fingerprint and emits `device.retrusted`.
- **Unchecked links:** The link-local setup wizard (`adapters/browser/cloudinit_wizard.py`) and
  WinRM without a device CA bundle (`adapters/hosts/windows_winrm.py`) are neither pinned nor
  verified. Every `# TRUST-OFF:` site must be listed in `tests/unit/test_trust_checks_off.py`.

### 9.2 Process-wide hooks

1. **Pinned WSAPI transport (`adapters/array/wsapi_client.py`):** On import, `_install_pinned_transport`
   replaces `hpe3parclient.http.requests` once with `_PinnedRequests`. For each client, `_pin_calls`
   wraps `client.http.request` to bind the `_PINNED_FINGERPRINT` `ContextVar`, so every SDK request
   goes through an adapter enforcing `urllib3`'s `assert_fingerprint`.
2. **Proxy environment variables:** `apply_proxy_env` (`application/platform/proxy.py`),
   `POST /prereqs/proxy` (`api/routes/prereqs.py`), `bypass_proxy_for` (`adapters/device_trust.py`)
   and `ensure_localhost_no_proxy` (`adapters/browser/debug_browser.py`, called by
   `cloudinit_wizard.py` and `dscc_setup.py`) keep `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` aligned
   with ADR 0008. Packaged `.exe` defaults use `setdefault` in `packaging/app_main.py` and
   `packaging/rthook_playwright.py`.

### 9.3 Test guards (`tests/conftest.py`)

Four `autouse` fixtures enforce STANDARD X1 and T4 across pytest: `_no_network` (blocks non-loopback
sockets and DNS lookups), `_run_in_a_scratch_folder` (`chdir(tmp_path)`),
`_isolate_settings_from_dotenv`, and `_validate_emitted_events`. Parsers are pinned to scrubbed lab
captures under `tests/fixtures/`.
