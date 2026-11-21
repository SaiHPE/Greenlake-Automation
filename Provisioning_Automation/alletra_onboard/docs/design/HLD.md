# High-Level Design: Alletra Onboard

Headings follow [arc42](https://arc42.org) and diagrams follow the [C4 model](https://c4model.com).
Companion document: [LLD.md](LLD.md). Where this document and the code disagree, the code is right.

---

## 1. Introduction and goals

Alletra Onboard is a local web app for HPE field engineers. It deploys one **HPE Alletra Storage MP
B10000** array per run from a single uploaded workbook:

1. registers the array in HPE GreenLake and assigns Data Services and a subscription;
2. connects the array to GreenLake through its link-local setup wizard;
3. fills the DSCC *Set Up System* wizard in the operator's signed-in browser;
4. discovers the array (block and Unified File), vCenter ESXi hosts, Windows/Linux hosts and Brocade
   SAN fabrics;
5. builds array-port command sets (iSCSI VLAN and migration peer ports) and Brocade SAN zoning
   command sets;
6. provisions block storage (hosts, host sets, volumes, volume sets, exports) and verifies paths;
7. creates snapshots and snapshot schedules;
8. sets up Remote Copy partnerships and groups, checks links and runs a planned failover test;
9. verifies the array against the workbook and writes the Word as-built document.

Feature scope and live-run status live in [docs/SCOPE.md](../SCOPE.md).

### Quality goals

Priority order — the higher goal wins when two conflict ([docs/STANDARD.md](../STANDARD.md) §1):

| # | Goal | Meaning |
|---|---|---|
| Q1 | Safe on customer equipment | Every outside write goes through its gate (section 4), SAN switches are never written to, and array applies keep an undo record. |
| Q2 | Truthful | Screens and documents report what devices answered. Failures and unknowns never render as empty or done. |
| Q3 | Operable on a jump box | One download, both build profiles (`full` and `init-only`), plain words on screen. |
| Q4 | Changeable without drift | Import contracts, type checks and fitness gates keep the structure intact. |

### Stakeholders

| Stakeholder | Role |
|---|---|
| HPE field engineer | Runs the app on a jump box, reviews each plan, approves array writes and delivers the as-built. |
| Customer SAN team | Applies the copy-paste Brocade zoning command set on their schedule. |
| Customer admin | Fills the workbook and receives the as-built document. |
| Maintainers and reviewers | Change the code under [docs/STANDARD.md](../STANDARD.md) and `scripts/check.py`. |

---

## 2. Constraints

All nine engineering and safety rules live in [AGENTS.md](../../../../AGENTS.md) (*Hard rules*) and
apply verbatim here. Operational constraints:

- Runs as one local process on a Windows jump box bound to `127.0.0.1:8765`, with no server
  infrastructure or app login.
- The jump box needs link-local access to the array, management-network access to on-site devices
  and outbound HTTPS (direct or via proxy) to HPE GreenLake and DSCC.
- The operator signs in to DSCC in their own Chrome; the app attaches over CDP on `localhost:9222`
  and never sees DSCC credentials or MFA.
- SAN zoning supports Brocade Fabric OS only ([ADR 0004](../adr/0004-auto-remediate-san-zoning.md)).
- Shipped `.ps1` scripts must stay pure ASCII for Windows PowerShell.

---

## 3. Context and scope

### C4 Level 1 — System context

```mermaid
flowchart LR
    OP(["Operator<br/>HPE field engineer"])
    SAN(["Customer SAN team"])

    SYS["Alletra Onboard<br/>Local web app and CLI<br/>on Windows jump box"]

    GL["HPE GreenLake<br/>SSO and Global REST API"]
    DSCC["HPE DSCC<br/>Cloud console in<br/>operator's Chrome"]
    TIME["HTTPS time sources<br/>(Date header)"]
    ARR["Primary Alletra MP B10000<br/>WSAPI v1/v3 :443, SSH :22,<br/>link-local wizard"]
    PEER["Peer array<br/>Remote Copy WSAPI :443,<br/>SSH :22"]
    VC["VMware vCenter<br/>HTTPS :443"]
    SW["Brocade FOS switches<br/>F1 and F2, SSH :22"]
    HST["Customer hosts<br/>Linux SSH :22,<br/>Windows WinRM 5985/5986"]

    OP -- "Browser UI (HTTP + SSE)<br/>and CLI" --> SYS
    SYS -- "OAuth + REST<br/>(via proxy)" --> GL
    SYS -- "Playwright CDP<br/>(fills forms only)" --> DSCC
    OP -- "Signs in and submits" --> DSCC
    SYS -- "HTTPS GET (clock skew)" --> TIME
    SYS -- "WSAPI v1/v3, SSH allowlist,<br/>Playwright link-local wizard" --> ARR
    SYS -- "WSAPI v1, SSH read,<br/>RC write-scoped SSH" --> PEER
    SYS -- "Read-only pyVmomi" --> VC
    SYS -- "Read-only SSH allowlist" --> SW
    SYS -- "Fixed read-only queries" --> HST
    SYS -. "Brocade command set<br/>(copy-paste text)" .-> SAN
    SAN -. "Applies zoning" .-> SW
```

### External interfaces

| External system | Transport | Access | Adapter |
|---|---|---|---|
| GreenLake SSO and Global API | HTTPS OAuth + REST (via proxy) | Read + write (subscription, device, assignment) | `adapters/greenlake/` |
| Array setup wizard | Playwright (`https://169.254.*` or `fe80::`) | Write (network, proxy, time; after Review check) | `adapters/browser/cloudinit_wizard.py` |
| DSCC console | Playwright CDP (`localhost:9222`) | Fills *Set Up System* forms; operator submits | `adapters/browser/dscc_setup.py` |
| Primary and peer array WSAPI v1 | HTTPS `/api/v1` (`python-3parclient`) | Read (`WsapiReader`); write (`WsapiWriter`) | `adapters/array/wsapi_client.py`, `adapters/array/wsapi_writer.py` |
| Array WSAPI v3 (Unified File) | HTTPS `/api/v3` (`httpx`) | Read-only (`GET` + credential login/logout) | `adapters/array/wsapi_v3_client.py` |
| Primary and peer array SSH | SSH :22 (`paramiko`) | Read allowlist, link diagnostics, RC and snapshot SSH writers | `adapters/array/cli_client.py`, `adapters/array/rc_cli_client.py`, `adapters/array/snap_cli_client.py` |
| VMware vCenter | HTTPS :443 (`pyVmomi`) | Read-only HBA/WWPN/IQN and ESXi LUN paths | `adapters/vcenter/vcenter_client.py` |
| Brocade FOS switches | SSH :22 (`paramiko`) | Read-only allowlist | `adapters/fabric/brocade_client.py` |
| Linux and Windows hosts | SSH :22 / WinRM 5985, 5986 | Fixed read-only identity, initiator and multipath/MPIO reads | `adapters/hosts/linux_ssh.py`, `adapters/hosts/windows_winrm.py` |
| Jump-box OS and tools | Local process / HTTPS GET | Clock skew check/sync, TCP/proxy probes, Discovery Tool, terminal | `adapters/system/` |

### Out of scope

| Excluded item | Status / reference |
|---|---|
| Writing to SAN switches; Cisco MDS fabrics | Never ([ADR 0012](../adr/0012-no-switch-writes-the-tool-emits-a-command-set.md), [ADR 0004](../adr/0004-auto-remediate-san-zoning.md)) |
| Two arrays provisioned from one workbook (paired runs) | Deferred ([ADR 0014](../adr/0014-paired-runs-from-one-workbook.md)); peer lives on the Replication tab |
| Peer Persistence, Active Sync, 3DC, RCIP VLANs; RCFC port setup | Refused at intake or deferred ([ADR 0024](../adr/0024-rcfc-ports-and-targets.md) part B) |
| Array iSCSI VLAN and migration peer-port writes | Emitted as command sets only; write clients deferred ([ADR 0017](../adr/0017-iscsi-vlan-write-plane.md), [ADR 0018](../adr/0018-peer-ports-over-a-port-scoped-ssh-client.md)) |
| Migration step execution | Tab and mode exist; step not built ([ADR 0020](../adr/0020-migration-tool-prepares-hpe-imports.md)) |
| Unified File writes; GreenLake for File (X10000) | Reads built; writes wait on lab probe ([ADR 0021](../adr/0021-unified-file-over-wsapi-v3.md)); GL4F deferred ([ADR 0022](../adr/0022-greenlake-for-file-system-type.md)) |
| ESXi datastore creation, host rescan, DSCC login/MFA, general SSH shell, day-2 admin | Out of scope ([docs/SCOPE.md](../SCOPE.md)) |

---

## 4. Solution strategy

- **One local process and one codebase.** FastAPI serves the REST API, SSE streams and built React UI
  on `127.0.0.1:8765`. Blocking device calls run in worker threads. A baked build profile
  (`ALLETRA_PROFILE`) produces both the `full` and `init-only` deliverables
  ([ADR 0007](../adr/0007-init-only-build-profile.md)).
- **Layered backend with enforced import contracts.** Dependencies point inward (`api`/`cli` →
  `application` → `adapters` → `domain`) and downward across workflow packages. Import-linter checks
  these rules on every run of `scripts/check.py` ([ADR 0028](../adr/0028-one-engineering-standard-enforced-by-the-gate.md)).
- **Four write paths, each with its own gate.** Read-only steps hold readers with no write methods.
  Every outside write uses one of four gated paths:

| Write path | What it changes | Gate and undo |
|---|---|---|
| GreenLake API (`application/onboarding/steps.py`) | Subscription, device registration, application and subscription assignment | Operator starts the step; reads before every write so reruns are safe. No `Approval` token or removal set. |
| Browser wizards (`adapters/browser/`) | Array network setup via link-local wizard; DSCC form fields only | Cloud Connectivity checks the Review page back before submitting (no `Approval` or removal set). DSCC never submits. |
| Array WSAPI (`WsapiWriter`) | Hosts, sets, volumes, exports, snapshots, Remote Copy groups and DR actions | Previewed plan with no conflicts, operator tick, single-use `Approval` and durable removal set. Failover is authorised (`authorised: true` + `Approval`), not planned, and records HPE recovery commands instead of a removal set. |
| Array SSH write-scoped (`ArrayRcCliClient`, `ArraySnapCliClient`) | RCIP addresses/targets/links (ADR 0015); snapshot schedules (ADR 0016) | ADR 0025: exact tested forms, built only inside an approved apply, plan-scoped objects, undo recorded before write, read-back after, no prompts. |

- **Discovery-driven planning.** The workbook states intent and reach; live environment facts are
  discovered at run time ([ADR 0002](../adr/0002-provisioning-driven-by-discovery.md)).
- **Typed run events and generated frontend types.** Backend events are checked statically against
  `domain/events.py`, and OpenAPI generates `frontend/generated/api.ts`
  ([ADR 0032](../adr/0032-typed-run-events-and-generated-frontend-types.md)).
- **Fakes and captures for tests; hardware for done.** Pytest blocks network I/O (`tests/conftest.py`)
  and pins parsers to scrubbed lab captures under `tests/fixtures/`.

---

## 5. Building block view

### C4 Level 2 — Containers

```mermaid
flowchart TB
    OP(["Operator"])
    UI["Web UI (SPA)<br/>React + Grommet<br/>frontend/src/"]
    CLI["CLI<br/>Typer: onboard ui / api / check<br/>src/alletra_onboard/cli/main.py"]
    API["Backend server<br/>FastAPI + Uvicorn<br/>127.0.0.1:8765"]
    DB[("Local SQLite store<br/>state.db + secrets.key + .env")]
    PW["Playwright browsers<br/>Automated Chromium (cloudinit)<br/>Chrome via CDP :9222 (DSCC)"]
    DT["HPE Discovery Tool<br/>Bundled .exe (SHA256 checked)"]
    GL["HPE GreenLake API"]

    OP --> UI
    OP --> CLI
    CLI -- "Starts server (ui / api)" --> API
    CLI -- "Direct check (onboard check)" --> GL
    UI -- "HTTP JSON + SSE<br/>(api.ts, useRunEvents.ts)" --> API
    API -- "OAuth + REST" --> GL
    API -- "SQLite WAL + Fernet" --> DB
    API -- "Playwright driver" --> PW
    API -- "Launches process" --> DT
```

### C4 Level 3 — Backend components

Every box is a real package or module under `src/alletra_onboard/`, and every arrow is an actual
import verified in the code.

```mermaid
flowchart TB
    subgraph ENTRY["Entrypoints"]
        APIAPP["api/app.py"]
        ROUTES["api/routes/"]
        CLI["cli/main.py"]
    end

    SVC["application/service.py<br/>OnboardingService"]

    subgraph APP["application/"]
        DOC["documents/"]
        ONB["onboarding/"]
        PROV["provisioning/"]
        SNAP["snapshots/"]
        REP["replication/"]
        UFILE["unified_file/"]
        RUNS["runs/<br/>coordinator, console, writer_clients,<br/>event_bus, apply_record, trust"]
        PLAT["platform/<br/>init_sheet, init_sheet_tabs, intake,<br/>proxy, prereqs, configuring, clients"]
    end

    CFG["config.py"]

    subgraph ADP["adapters/"]
        ARR["array/"]
        GL["greenlake/"]
        BR["browser/"]
        VC["vcenter/"]
        FAB["fabric/"]
        HST["hosts/"]
        PERS["persistence/"]
        SYS["system/"]
        PLUMB["tls.py, device_trust.py,<br/>command_log.py"]
    end

    DOM["domain/<br/>(no I/O)"]

    APIAPP --> ROUTES & SVC & PLAT & PROV & RUNS & CFG & DOM
    APIAPP -. "opens store" .-> PERS
    ROUTES --> SVC & PLAT & ONB & PROV & RUNS & CFG & DOM
    CLI --> ONB & CFG

    SVC --> DOC & ONB & PROV & SNAP & REP & RUNS & PLAT & CFG & DOM
    DOC --> PROV & REP & SNAP & UFILE & RUNS
    PROV --> UFILE & RUNS
    REP --> PROV & RUNS
    SNAP --> PROV & REP & RUNS
    ONB --> RUNS & CFG
    RUNS --> CFG

    DOC & ONB & PROV & SNAP & REP & PLAT & RUNS & UFILE --> DOM
    ONB & PROV & SNAP & REP & PLAT -- "via */clients.py" --> ADP
    RUNS -- "via coordinator, console,<br/>writer_clients" --> ADP
    ADP --> DOM
```

`application/unified_file/` imports only `domain/`; its callers (`provisioning/discovery.py` and
`documents/steps.py`) pass in the clients.

### Frontend (`frontend/src/`)

- `App.tsx` and `ui/AppChrome.tsx` render the wizard from `/app/profile` (`modes.ts`).
- `steps/` holds one component per step screen; no step imports another step.
- `ui/` holds shared blocks (`StepShell.tsx`, `ConsolePane.tsx`, `TrustedDevices.tsx`, `RemovalSets.tsx`).
- `api.ts` and `useRunEvents.ts` are the only modules that call `fetch` or `EventSource`, using types
  generated in `frontend/generated/api.ts`.

---

## 6. Runtime view

### 6.1 Initialization run (GreenLake → Cloud Connectivity → DSCC)

```mermaid
sequenceDiagram
    participant O as Operator / UI
    participant S as OnboardingSteps
    participant G as GreenLake API
    participant W as Array wizard (link-local)
    participant D as DSCC (Chrome CDP :9222)

    O->>S: POST /runs/{id}/provision (GreenLake)
    S->>G: OAuth token, read service catalog and inventory
    S->>G: POST subscription (if absent) and poll 202 Location
    S->>G: POST device (if absent) and poll 202 Location
    S->>G: PATCH 1: application and region (poll 202 Location)
    S->>G: PATCH 2: subscription (poll 202 Location)
    S-->>O: READY, advance to CLOUDINIT_CONNECT

    O->>S: POST /runs/{id}/cloudinit (with link-local URL)
    S->>W: Fill Network, Proxy, Time
    S->>W: Read Review page back (verify values, refill once on mismatch)
    S->>W: Submit (if auto_submit and Review matches)
    W-->>S: Connected (fail-prov-* stops as GreenLake state error)
    S-->>O: READY, advance to DSCC_SETUP_SYSTEM

    O->>D: Sign in by hand, open Set Up System
    O->>S: POST /runs/{id}/dscc
    S->>D: Attach over CDP, fill wizard, stop at Review
    S-->>O: WAITING_FOR_OPERATOR (operator.credentials_ready)
    O->>D: Enter array credential and Submit
    O->>S: POST /runs/{id}/complete
    S-->>O: SUCCEEDED (run.completed)
```

### 6.2 Plan → approve → apply with undo-before-write and read-back

Used by block provisioning, Remote Copy partnership, Remote Copy groups and snapshots
([ADR 0025](../adr/0025-one-rule-for-ssh-writes.md), [ADR 0031](../adr/0031-least-privilege-in-three-stages.md)).

```mermaid
sequenceDiagram
    participant O as Operator / UI
    participant Step as Step service
    participant C as RunCoordinator
    participant DB as SQLite store
    participant W as Writer client
    participant A as Array (WSAPI / SSH)

    O->>Step: Preview plan
    Step->>A: Read live state via reader client
    Step->>Step: Hold plan and fresh plan_id in memory
    Step-->>O: WAITING_FOR_OPERATOR (plan and plan_id)

    O->>Step: Apply with ticked plan_id
    Step->>Step: Verify plan_id matches held plan and no conflicts
    Step->>C: Request single-use Approval for this run and side(s)
    Step->>W: Open writer from Approval (and plan objects for SSH)

    loop Each planned write
        Step->>DB: Save inspect-first note and removal line before write
        W->>A: Send write (checks Approval live and scope)
        W->>A: Read back object to verify result
        Step->>DB: Save confirmed removal set
    end

    C->>C: Spend Approval when worker thread finishes
    Step->>C: Record terminal apply event
    C->>DB: Append event and clear in-progress record
```

If the process crashes mid-apply, the unclosed record stays in SQLite. Reopening the run or starting
the app promotes it to a failed apply event so the UI and as-built show the removal set and notes
([LLD.md](LLD.md) §4).

### 6.3 Failover test (`application/replication/failover.py`)

```mermaid
sequenceDiagram
    participant O as Operator / UI
    participant R as ReplicationSteps and failover
    participant DB as SQLite store
    participant P as Primary array (A)
    participant S as Peer array (B)

    O->>R: POST /runs/{id}/replication/failover-test (authorised: true)
    R->>R: Issue Approval for failover on A and B
    R->>P: Full read-only array read (read_array)
    R->>S: Full read-only array read (read_array)
    Note over R: Require Primary/Started on P, Secondary/Started on S, all Synced
    R->>P: Open WsapiWriter on A
    R->>S: Open WsapiWriter on B

    R->>DB: Checkpoint step 1 (abort if pre-step-1 save fails)
    R->>P: 1. Stop group -> poll Stopped on P and S
    R->>DB: Checkpoint step 2
    R->>S: 2. Failover (DR action 7) -> poll Primary-Rev on S
    Note over R: 3. Record peer read/write state (no host write)
    R->>DB: Checkpoint step 4 (unless array auto-started)
    R->>S: 4. Recover (DR action 9, if needed) -> poll Secondary-Rev and Started
    R->>S: 5. Poll group until every volume Synced
    R->>DB: Checkpoint step 6
    R->>S: 6. Restore (DR action 10), or fail back S to P if natural primary flipped
    R->>P: Poll Primary/Started on P, Secondary/Started on S, Synced
    R-->>O: FailoverRecord (passed, or failed with recovery commands)
```

`run_failover_test` always returns a `FailoverRecord` and never raises on device errors. On failure
it reports both observed sides and HPE's documented CLI way back.

### 6.4 Event emission and streaming to the UI

```mermaid
sequenceDiagram
    participant UI as Browser (useRunEvents.ts)
    participant API as Events and console routes
    participant C as RunCoordinator
    participant DB as SQLite store
    participant BUS as Event and console buses
    participant D as Device adapter (worker thread)

    UI->>API: GET /runs/{id}/events (initial history)
    UI->>API: GET /runs/{id}/stream (SSE with heartbeat)
    C->>DB: Append typed RunEvent
    C->>BUS: Push RunEvent to live subscribers
    API-->>UI: Stream RunEvent JSON (dedup by event_id, refresh run)

    D->>C: Record redacted device command
    C->>DB: Append command row
    C->>BUS: Push command record
    API-->>UI: Stream live line to ConsolePane
```

---

## 7. Deployment view

```mermaid
flowchart LR
    subgraph JB["Windows jump box (customer management network)"]
        EXE["AlletraOnboard.exe<br/>(or Python .venv)"]
        DATA["%LOCALAPPDATA%\AlletraOnboard\<br/>state.db + secrets.key<br/>(or .alletra_onboard/ in dev)"]
        ENV[".env (GreenLake creds,<br/>proxy override)"]
        BR["Edge / Chrome /<br/>bundled Chromium"]
        DT["HPE Discovery Tool"]
        EXE --> DATA
        EXE --> ENV
        EXE --> BR
        EXE --> DT
    end
    JB -- "Link-local 169.254/16 or fe80::" --> WIZ["Array setup wizard"]
    JB -- "Management VLAN (bypass proxy)" --> SITE["Arrays, vCenter,<br/>Brocade switches, Hosts"]
    JB -- "Outbound TCP 443 (via corporate proxy)" --> CLOUD["HPE GreenLake and DSCC"]
```

- Uvicorn listens on `127.0.0.1:8765` only. CORS permits only the Vite dev server on port 5173. Run
  as Administrator when using *Sync system clock*.
- In the `.exe`, `packaging/app_main.py` stores `state.db` and `secrets.key` under
  `%LOCALAPPDATA%\AlletraOnboard` unless a `state.db` already exists beside the executable.

### Build deliverables

| Artifact | Profile | Contents |
|---|---|---|
| `alletra-onboard-win64.zip` | `full` | Slim PyInstaller `.exe`, built UI, as-built template, HPE Discovery Tool; uses installed Chrome/Edge. |
| `alletra-onboard-offline-win64.zip` | `full` | Same as slim, with Chromium bundled for offline jump boxes. |
| `alletra-mp-initialization-win64.zip` | `init-only` | Initialization steps and workbook only ([ADR 0007](../adr/0007-init-only-build-profile.md)). |
| `alletra-onboard-latest.zip` | `full` | Source zip (`src/`, built UI, `start.cmd`, `start.ps1`). |

Packaging files: `alletra_onboard.spec`, `packaging/app_main.py`, `packaging/rthook_playwright.py`,
`scripts/build_exe.ps1`, `scripts/smoke_serve.ps1`. `/app/profile` exposes `capabilities.wsapi_sdk`
so a missing SDK bundle shows up without an array.

---

## 8. Crosscutting concepts

**Least privilege and console safety.** Read clients have no write methods; writer factories sit
behind import-linter `protected` contracts and require a live `Approval`
([ADR 0031](../adr/0031-least-privilege-in-three-stages.md)). The operator console prompt is held
to the read allowlist in `adapters/array/cli_client.py` ([SPEC-019](../specs/SPEC-019-console.md)).

**Secrets and redaction.** Secret fields in `state.db` are Fernet-encrypted with `secrets.key` next
to the database ([ADR 0027](../adr/0027-stored-credentials-encrypted-at-rest.md)). `redact()`
(`domain/policies.py`) and per-client scrubbing strip passwords, bearer tokens and session keys from
logs and console output.

**Transport trust ([ADR 0026](../adr/0026-certificates-and-host-keys.md)).** Cloud calls always
verify TLS against the OS trust store, `certifi` and any `ALLETRA_CA_BUNDLE` (`adapters/tls.py`).
On-site SSH and TLS clients (arrays, vCenter, switches, Linux hosts) use first-contact trust pinned
per run in `run_device_pins` (`adapters/device_trust.py`); a changed key blocks before credentials
are sent until explicitly re-trusted. Setting `ALLETRA_DEVICE_CA_BUNDLE` replaces first-contact
trust with full CA verification for WSAPI, vCenter and WinRM over HTTPS only; SSH stays on
first-contact trust (`config.py`). Two links are neither pinned nor verified, with documented
reasons enforced by `tests/unit/test_trust_checks_off.py`: the link-local setup wizard
(`adapters/browser/cloudinit_wizard.py`) and WinRM without a device CA bundle
(`adapters/hosts/windows_winrm.py`).

**Persistence, proxy and errors.** One SQLite WAL file (`adapters/persistence/sqlite.py`) stores
runs, events, artifacts, commands and pins. Outbound calls auto-detect the system proxy with
`ALLETRA_PROXY` override while on-site addresses bypass it ([ADR 0008](../adr/0008-proxy-auto-detect-with-override.md)).
Adapters raise subclasses of `DeviceError` (`domain/errors.py`); `except Exception` is restricted to
`application/runs/coordinator.py`, `api/app.py` and the listed ceilings in `quality/ceilings.toml`.
Event compatibility follows [ADR 0032](../adr/0032-typed-run-events-and-generated-frontend-types.md).

**Workbook intake and auditability.** One Excel workbook (`application/platform/init_sheet.py`)
feeds every mode; upload keeps passwords server-side under a single-use token. Every device or cloud
call goes to `run_commands` (`adapters/command_log.py`) and feeds the console pane and the as-built
change appendix.

---

## 9. Architecture decisions

| ADR | Status | Decision |
|---|---|---|
| [0001](../adr/0001-post-init-verification-via-ssh-cli.md) | Accepted (amended by 0013, 0015, 0019, 0025) | Post-init verification reads running array config via read-only SSH allowlist. |
| [0002](../adr/0002-provisioning-driven-by-discovery.md) | Accepted | Workbook carries intent and reach; environment facts are discovered at run time. |
| [0003](../adr/0003-transport-wsapi-with-readiness-gate.md) | Accepted | Block provisioning uses WSAPI `/api/v1` behind a readiness gate; SSH covers gaps. |
| [0004](../adr/0004-auto-remediate-san-zoning.md) | Accepted (reaffirmed by 0012) | Verify SAN zoning and emit a read-only Brocade FOS zoning plan; Cisco MDS out of scope. |
| [0005](../adr/0005-decouple-onboarding-into-modes.md) | Accepted (revised) | Complete workbook upload precedes mode selection; modes select registry steps. |
| [0006](../adr/0006-hybrid-control-plane.md) | Accepted (corrected by 0019) | Target hybrid plane (DSCC cloud + direct WSAPI); direct WSAPI is built today. |
| [0007](../adr/0007-init-only-build-profile.md) | Accepted | Initialization accelerator is a build profile (`init-only`) of one codebase, not a fork. |
| [0008](../adr/0008-proxy-auto-detect-with-override.md) | Accepted | Auto-detect system proxy like the browser, allow override, bypass on-site devices. |
| [0009](../adr/0009-fabric-from-switch-with-parity-fallback.md) | Accepted | Derive FC fabric from attached switch; report port-number parity when used as fallback. |
| [0010](../adr/0010-provisioning-builder-consumes-zoning.md) | Accepted | Interactive provisioning builder over discovered objects; consumes zoning, verifies paths. |
| [0011](../adr/0011-bounded-context-refactor-decoupled-ux.md) | Accepted | Organize backend by workflow context behind frozen API; serve step registry to UI. |
| [0012](../adr/0012-no-switch-writes-the-tool-emits-a-command-set.md) | Accepted | Never write to a SAN switch; emit copy-paste Brocade commands; zoning gates exports per host. |
| [0013](../adr/0013-one-array-credential-per-run.md) | Accepted | Hold one array admin credential per run from the workbook for all steps. |
| [0014](../adr/0014-paired-runs-from-one-workbook.md) | Deferred | Paired two-array runs from one workbook deferred; peer lives on the Replication tab. |
| [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md) | Accepted | Configure Remote Copy: groups/DR over WSAPI, RCIP ports/targets over `ArrayRcCliClient`. |
| [0016](../adr/0016-snapshot-schedules-write-scoped-ssh.md) | Accepted | Snapshots via WSAPI; snapshot schedules via `ArraySnapCliClient` (one `createsched -f` form). |
| [0017](../adr/0017-iscsi-vlan-write-plane.md) | Accepted (write deferred) | iSCSI VLANs planned and emitted as command sets; never offline a port; write client deferred. |
| [0018](../adr/0018-peer-ports-over-a-port-scoped-ssh-client.md) | Accepted (write deferred) | Migration peer ports planned and emitted as command sets; port-mode write client deferred. |
| [0019](../adr/0019-handover-report-from-the-array.md) | Accepted | Handover status read from the array (`showalert` + capacity); DSCC telemetry deferred. |
| [0020](../adr/0020-migration-tool-prepares-hpe-imports.md) | Accepted (step not built) | Tool prepares and verifies migration prerequisites; HPE Peer Motion imports data. |
| [0021](../adr/0021-unified-file-over-wsapi-v3.md) | Accepted (reads only) | Read Unified File over array WSAPI `/api/v3` GET-only client; writes wait on lab probe. |
| [0022](../adr/0022-greenlake-for-file-system-type.md) | Deferred | GreenLake for File (X10000) deferred until lab hardware and GreenLake file APIs exist. |
| [0023](../adr/0023-one-question-per-step-screen.md) | Accepted | Each step screen asks one operator question; detail and tools stay one click away. |
| [0024](../adr/0024-rcfc-ports-and-targets.md) | Part A accepted, B deferred | Use existing RCFC partnerships for groups/verify (part A); RCFC port setup deferred (B). |
| [0025](../adr/0025-one-rule-for-ssh-writes.md) | Accepted | One rule for array SSH writes: exact forms, approved apply, plan-scoped, undo-first, read-back. |
| [0026](../adr/0026-certificates-and-host-keys.md) | Accepted | Verify cloud TLS; trust on-site devices on first contact with per-run pins or device CA. |
| [0027](../adr/0027-stored-credentials-encrypted-at-rest.md) | Proposed and built | Encrypt secret fields in `state.db` with a Fernet key in `secrets.key` beside the database. |
| [0028](../adr/0028-one-engineering-standard-enforced-by-the-gate.md) | Accepted | Adopt [docs/STANDARD.md](../STANDARD.md) with cited sources and enforce it via `scripts/check.py`. |
| [0029](../adr/0029-where-device-text-parsers-live.md) | Accepted | Shared device-text parsers live in `domain/array_parse.py`; single-context parsers stay in their read module. |
| [0030](../adr/0030-the-gate-fails-where-it-only-warned.md) | Accepted | Gate fails on list growth, gate config edits, new suppressions, dead doc paths and unchecked lessons. |
| [0031](../adr/0031-least-privilege-in-three-stages.md) | Implemented | Split `WsapiReader`/`WsapiWriter`, gate writes behind `Approval`, persist `apply_in_progress`. |
| [0032](../adr/0032-typed-run-events-and-generated-frontend-types.md) | Accepted | Register run events in `domain/events.py`; generate `frontend/generated/api.ts` from OpenAPI. |

---

## 10. Quality requirements

Quality goals, rules and references live in [docs/STANDARD.md](../STANDARD.md). Every branch must
pass `scripts/check.py` before a pull request (there is no remote CI). A feature is done only after
live lab verification using `lab/` scripts, recorded in [docs/validation/](../validation/) and
[docs/SCOPE.md](../SCOPE.md).

---

## 11. Risks and technical debt

Known code violations are listed in `quality/ceilings.toml` and `frontend/eslint-suppressions.json`
and may only shrink (`scripts/fitness.py --tighten`). Open work lives in github.hpe.com issues
(`BL-NN`), and built features still awaiting live lab runs are tracked in
[docs/SCOPE.md](../SCOPE.md).

Architectural risks currently accepted:

| Risk | Mitigation / status |
|---|---|
| `secrets.key` sits beside `state.db` without OS user-key binding on Windows | Protects standalone DB copies; Windows DPAPI waits for Windows lab testing ([ADR 0027](../adr/0027-stored-credentials-encrypted-at-rest.md)). |
| Unsigned Windows `.exe` triggers SmartScreen warning | Documented in `README.md`; SHA256 ships with each release zip. |
| `paramiko` pinned below major 4 for legacy Brocade switch SSH algorithms | Accepted as tolerable for read-only switch SSH (`pyproject.toml`). |
| Historical `run_events` rows are stored as raw dicts | Kept readable without migration; evolution rules live in [ADR 0032](../adr/0032-typed-run-events-and-generated-frontend-types.md). |

---

## 12. Glossary

Domain terms — including **Approval**, **Mode**, **Step**, **Command set**, **Fabric**, **Export
(VLUN)** and **As-built** — are defined in [CONTEXT.md](../../CONTEXT.md). Three architecture terms
used here:

- **Run:** one deployment record for one array, holding its work item, intent, events, artifacts,
  command log and device pins.
- **Removal set:** copy-paste array CLI commands that undo only what an apply created; never run by
  the tool ([SPEC-007](../specs/SPEC-007-removal-set.md)).
- **Gate:** `scripts/check.py`, the pre-pull-request suite enforcing [docs/STANDARD.md](../STANDARD.md).
