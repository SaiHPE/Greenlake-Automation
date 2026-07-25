# Architecture — current state (HLD + LLD baseline)

> **Purpose.** A snapshot of the system *as built today* (v0.12.0), written as the baseline for a
> planned HLD/LLD-driven refactor. It records what exists, how the layers fit, the runtime flows, and —
> most usefully for a refactor — the **seams and pain points**. It is descriptive, not aspirational:
> the north-star scope lives in [SCOPE.md](SCOPE.md), the domain language in [CONTEXT.md](../CONTEXT.md),
> and the *why* of individual decisions in [docs/adr/](adr/). This doc ties them to the real modules.

---

## 1. What it is

A **local, single-operator desktop tool** that automates deploying an HPE Alletra Storage MP B10000:
initialize into GreenLake/DSCC → discover → verify zoning → provision (host/volume/LUN) → verify → and
now **document (as-built)**. Primary user = an HPE deployment/PS engineer, not a customer day-2 admin.
Today's app is the top-left of the [SCOPE.md](SCOPE.md) matrix (Alletra MP **block**); the file column
and the DSCC **cloud** control plane are the big unbuilt gaps.

**Released increments:** v0.3–0.9 (onboarding A→B→C→D, modes, discovery, zoning-verify, proxy, fabric),
v0.10 (zoning plan), **v0.11.0** (provisioning tiers + Stage-2 dropdown builder + tier-2 path verify),
**v0.12.0** (as-built document generation).

## 2. Runtime & deployment

| Aspect | Detail |
|---|---|
| Shape | FastAPI backend + React 18/Vite/HPE-Grommet SPA, one process, **localhost 127.0.0.1:8765** |
| Packaging | PyInstaller **onedir `.exe`** (Windows); the SPA `frontend/dist` + resources + Discovery Tool are bundled (`alletra_onboard.spec`, `sys._MEIPASS` at runtime) |
| Build profiles | `ALLETRA_PROFILE` = `full` \| `init-only` (the "Initialization accelerator" — same codebase, baked flag; ADR 0007) |
| Prod serving | API serves `frontend/dist` at `/` (same origin); vite dev talks to `:8765` with CORS |
| Persistence | **SQLite** (`adapters/persistence/sqlite.py`) for runs/work-items/pending-sheets/provisioning-intent; gitignored `.env` for GreenLake creds/proxy |
| Concurrency | async FastAPI; blocking device I/O (paramiko SSH, python-3parclient, pyvmomi) runs via `asyncio.to_thread`; eventlet is pulled in by the SDK but **never monkey-patched (dormant)** |
| Live updates | per-run event bus → **SSE** (`/runs/{id}/stream`); the UI renders from the event stream, not step return values |

## 3. Architecture style — ports & adapters (hexagonal-ish)

Four layers, dependencies point inward (`api → application → domain`; `adapters` implement `domain/ports`):

```
 frontend/ (React SPA)  ──HTTP/SSE──►  api/ (FastAPI routes + schemas)
                                           │
                                           ▼
                                    application/  (services: orchestration + use-cases)
                                       │              │
                                       ▼              ▼
                                    domain/        adapters/  (device/cloud/persistence I/O)
                                 (models, ports,   (array WSAPI+CLI, vCenter, brocade,
                                  workflow, errors) greenlake, browser, persistence, system)
```

- **`domain/`** — pure models + contracts, no I/O. `models.py` (onboarding: `ArrayWorkItem`, `RunRecord`,
  `WorkflowPhase`, `RunMode`), `storage.py` (provisioning subdomain: `ProvisioningIntent`/`VolumeRequest`/
  `HostSetRequest`/`ExportRequest`, discovery `DiscoveryReport`, zoning, `PathVerification`),
  `workflow.py` (the **step registry** + mode→steps), `ports.py` (`RunStore` interface),
  `policies.py`, `errors.py`.
- **`application/`** — services orchestrating domain + adapters. Split: onboarding/init + a `storage/`
  subpackage (the provisioning bounded context) + as-built modules + cross-cutting (proxy, prereqs,
  health, init_sheet).
- **`adapters/`** — one subpackage per external system, each built from `EndpointCreds`/config via
  factory functions (`storage/clients.py`, injectable so services unit-test with fakes).
- **`api/`** — `app.py` (all routes as inline closures in `create_app(service)`), `schemas.py` (Pydantic
  request/response models).

## 4. HLD — control planes & lifecycle coverage

**Control planes (ADR 0006, hybrid — only the direct plane is built):**
- **Direct (built):** a single array's **WSAPI** (`:443`, python-3parclient) for provisioning writes +
  structured reads; **SSH CLI** (`ArrayCliClient`, read-only allowlist) for config/health/inventory reads
  and zoning-verify.
- **Cloud (NOT built):** the DSCC/GreenLake multi-array REST plane — the intended *primary*. Onboarding
  Component A touches the GreenLake *global* API (`adapters/greenlake/*`) and DSCC is driven via a
  **browser wizard** (Component C, Playwright/CDP), but there is **no DSCC provisioning cloud client**.
- **Switch (read-only/deferred):** Brocade FOS (`adapters/fabric/brocade_client.py`) — verify + a
  read-only zoning *plan*; zone *creation* is deferred (ADR 0004).

**Lifecycle coverage (block column of SCOPE.md):** Initialize ✅ · Discover ✅(array)/🟡(vCenter) ·
Connect-zoning 🟡(verify+plan; create deferred) · Provision 🟢(tiered, tier-1 live-proven) ·
Replicate/DR ⚪ · Report ⚪ · **Document ✅(as-built, v0.12.0)**. File column = ⚪ entirely.

## 5. LLD — module map (by layer)

### 5.1 domain/
| Module | Responsibility |
|---|---|
| `models.py` | Onboarding models + enums: `ArrayWorkItem` (per-array intake, now incl. `customer_name`/`site`), `RunRecord`/`RunStatus`, `WorkflowPhase`, `RunMode`, `NetworkConfig`, `DsccSetupConfig`, `VerificationReport` |
| `storage.py` | Provisioning subdomain: `EndpointCreds`; **plural intent** (`ProvisioningIntent` = `volumes[]`+`host_sets[]`+`exports[]`, `from_simple`); `persona_for_os`→name; discovery (`ArrayPort`/`HostHba`/`ArrayHost`/`DiscoveryReport`); zoning (`ZoningReport`/`ZoningPlan`); builder palette (`ProvisioningObjects`/`ProvisioningBuilder`); plan+result; tier-2 (`PathVerification`). (As-built's `AsBuiltData` is a dataclass in `application/asbuilt.py`, not here) |
| `workflow.py` | **`STEP_REGISTRY`** (ordered `StepDef`s: greenlake, cloudinit, dscc, discover, zoning, provision, verify, **asbuilt**) + `_MODE_STEPS` (preset mode→steps) + `enabled_steps`/`initial_phase`/`next_enabled_phase` |
| `ports.py` | `RunStore` interface (persistence contract) |
| `policies.py`, `errors.py` | Domain rules + typed errors |

### 5.2 application/ (onboarding + cross-cutting)
| Module | Responsibility |
|---|---|
| **`onboarding_service.py`** | **The orchestrator** (see §8). Holds the event bus + store + all per-run transient state; every `start_*`/`_run_*` step lives here |
| `init_sheet.py` | The workbook: `build_template_bytes` (Initialisation + Provisioning + Volumes + Host sets + Prerequisites tabs) and `parse_workbook_bytes` → `ParsedInitSheet` (work item, GL creds, `ProvisioningIntent`, customer/site) |
| `provisioning.py` | Component A — GreenLake onboarding provisioning (register/assign/subscribe) orchestration |
| `verification.py` | Post-init read-only config+health verify (`verify(item, user, pw)` → `VerificationReport`) |
| `proxy.py` | `ProxyResolver` — effective proxy (manual > auto-detected system/PAC > direct), `apply_proxy_env` (ADR 0008) |
| `prereqs.py`, `preflight_service.py`, `greenlake_preflight.py` | Firewall rules, connectivity pre-check, GreenLake readiness |
| `health.py`, `configuring.py`, `intake.py` | GreenLake health check, config I/O, CSV intake |
| `event_bus.py` | `InMemoryEventBus` — per-run pub/sub feeding SSE |
| **`asbuilt.py`** | `AsBuiltData` + `generate_asbuilt` — fills the bundled HPE Block-Storage `.docx` (cover/customer, Table 01, inventory + checkhealth tables); `default_template()` resolution |
| **`asbuilt_parse.py`** | `parse_asbuilt` (dump→`AsBuiltData`), `parse_inventory` (**CSV**, `showinventory -csvtable`), `parse_checkhealth` (Summary/Details) |
| **`asbuilt_docx.py`** | `hpe_table` — HPE house-style Word tables (green header/zebra/borders), ported from the operator's `sapdoc.py` |

### 5.3 application/storage/ (provisioning bounded context)
| Module | Responsibility |
|---|---|
| `clients.py` | Adapter **factories** (`make_wsapi`/`make_array_cli`/`make_vcenter`/`make_brocade`) — the injection seam for tests |
| `discovery.py` | Read array ports + `showhost -d` + fabric resolution + vCenter HBAs → `DiscoveryReport` |
| `zoning.py`, `zoning_plan.py` | Array-side zoning **verify** (report) + read-only zoning **plan** builder (ADR 0004) |
| `storage_provision.py` | Tier-1 `build_plan`/`apply_plan` (plural/heterogeneous create; exports w/ default fallback) + builder palette reads (`read_array_objects`, `host_briefs`) |
| `path_verify.py` | Tier-2 read-only path verification (`showvlun -a` → per-host live/partial/no_path) |

### 5.4 adapters/
| Subpackage | Responsibility |
|---|---|
| `array/wsapi_client.py` | WSAPI writes/reads via python-3parclient; persona-by-name→WSAPI enum (VMware=8); readiness gate; idempotent creates |
| `array/cli_client.py` | Read-only SSH CLI, **command allowlist** (structurally read-only) — verify + as-built + discovery |
| `vcenter/vcenter_client.py` | Read-only ESXi HBA/WWPN discovery (pyvmomi) |
| `fabric/brocade_client.py` | Brocade FOS reads (nsshow/cfgshow/…); read-only (write path removed) |
| `greenlake/*` | GreenLake global API: `auth`, `devices`, `subscriptions`, `service_catalog`, `http_client` (Component A) |
| `browser/*` | Playwright/CDP browser automation: `cloudinit_wizard` (B), `dscc_setup` (C), `debug_browser`, `locators` |
| `persistence/sqlite.py` | `SqliteRunStore` (implements `RunStore`) |
| `system/clock.py`, `system/discovery_tool.py` | HTTPS-based clock sync (ADR 0008 note), bundled Discovery Tool launcher |

### 5.5 api/ & frontend/
- `api/app.py` — `create_app(service)` wires every route as an inline closure; helpers `_get_run_or_404`,
  `_start_step` (maps `StepPreconditionError`→409, `RunNotFound`→404). Routes: config, prereqs/proxy,
  init-sheet upload/template, runs CRUD, per-step `POST`s (`/greenlake`…/`verify`/**`/asbuilt`** +
  `/asbuilt/download`), storage (`/discover`,`/zoning/*`,`/storage/{objects,builder,preview,apply,verify-paths}`),
  events + SSE.
- `frontend/src/` — `App.tsx` (wizard shell + step render switch), `modes.ts` (mirror of the step registry —
  **kept in lockstep with `workflow.py` by hand**), `api.ts` (fetch client + all TS interfaces), `useRunEvents.ts`
  (SSE hook), `steps/*` (one component per step: GreenLake/Cloudinit/Dscc/Discovery/Zoning(+ZoningPlanView)/
  Provision(+ProvisioningBuilderView)/Verify/**AsBuilt**/Done/Mode/Prereq/InitSheet).

## 6. Runtime flows (key sequences)

1. **Intake → run:** download template → operator fills the workbook → `POST /init-sheet/upload` parses +
   validates the *complete* superset, saves GL creds, and **holds the parsed sheet under a token** (device
   passwords never round-trip to the browser). Picking a **mode** → `POST /runs/from-sheet` mints the run
   from the token (ADR 0005). Mode → `enabled_steps` → the wizard's step list.
2. **A step:** `POST /runs/{id}/<step>` → `service.start_*` spawns a background `asyncio` task → device I/O
   on a thread → **emits events** → SSE streams them → the step component renders from events. Init steps
   auto-advance the phase; provision/verify/asbuilt are operator-triggered and (verify/asbuilt) never change
   run status.
3. **Provisioning:** discover → (compose in the dropdown builder: `GET /storage/objects` palette +
   `POST /storage/builder`) → `preview` (`build_plan`) → confirm → `apply` (`apply_plan`, idempotent WSAPI
   writes) → `verify-paths` (tier-2, report-only).
4. **As-built (last):** `POST /runs/{id}/asbuilt` → SSH read-only (`show*`/`checkhealth`/`showinventory
   -csvtable`) → `parse_asbuilt` → `generate_asbuilt` → **.docx bytes in memory** → `GET /asbuilt/download`.

## 7. State & persistence
- **Durable (SQLite):** runs, work items, pending sheets (single-use token), provisioning intent.
- **Transient (in-memory dicts on the service, lost on restart):** `_discovery`, `_zoning`, `_plan`,
  **`_asbuilt`** (docx bytes), `_tasks` (running asyncio tasks). Also emitted in event data so the UI has them.
- **Secrets:** GreenLake creds + proxy in gitignored `.env`; device passwords supplied per-run or held in the
  pending-sheet/intent, never echoed to the browser.

## 8. Refactoring seams & known pain points (read this first)

- **`onboarding_service.py` is a god-object.** It owns the event bus, the store, *all* per-run transient
  state, and *every* step's `start_*`/`_run_*` (onboarding A–C, discovery, zoning, provisioning tiers,
  verify, as-built). It is the prime decomposition target — e.g. split into per-bounded-context services
  (onboarding / provisioning / verify / document) behind a thin run coordinator, and move transient state
  into a store or the event log.
- **The step registry is duplicated** across `domain/workflow.py` and `frontend/src/modes.ts`, kept "in
  lockstep" by hand (a comment says so). A single source (generated or served) would remove a class of bugs.
- **Transient per-run state is in-memory only** (`_discovery`/`_zoning`/`_plan`/`_asbuilt`) — a server
  restart loses it and the step must re-run. Fine for a single-operator desktop app; a refactor toward
  durability/multi-run would need to persist these.
- **The hybrid control plane is half-built** (ADR 0006): everything is direct-WSAPI/SSH/browser; the DSCC
  *cloud* client (the intended primary, multi-array plane) does not exist. A refactor that adds it should
  introduce a control-plane-client abstraction with **capability routing** (cloud-preferred vs direct-only).
- **Bounded contexts are already legible** and worth hardening: **provisioning** (`application/storage/*` +
  `domain/storage.py`'s provisioning half), **as-built/document** (`asbuilt*.py` — cleanly self-contained,
  parse→generate→docx), **onboarding** (A–D), **discovery/zoning** (shared foundation). `domain/storage.py`
  is doing double duty (provisioning **and** discovery **and** zoning **and** as-built models) — a candidate
  to split per context.
- **Async/sync boundary:** FastAPI async + `asyncio.to_thread` around blocking SDK clients; eventlet dormant.
  Keep the "no monkey-patch" invariant if touching the SDK import path (a past heap-corruption class of bug
  lived near packaging — see ADR 0008 pitfall).
- **CLI text parsing** was the fragile spot; the as-built now uses **deterministic CSV** (`-csvtable`) and
  `key:value` detail output, not fixed-width slicing. Prefer that pattern for any new device reads.

## 9. Pointers
- **Scope / north-star:** [SCOPE.md](SCOPE.md) — the 7-stage × block/file matrix.
- **Glossary:** [CONTEXT.md](../CONTEXT.md) — canonical domain terms (incl. As-built, Provisioning intent,
  Path verification, Ideal subset, control plane).
- **Decisions:** [docs/adr/0001–0010](adr/) — post-init verify (0001), discovery-driven (0002), WSAPI
  transport (0003), zoning verify+plan (0004), modes (0005), hybrid control plane (0006), init-only profile
  (0007), proxy auto-detect (0008), fabric-from-switch (0009), provisioning builder consumes zoning (0010).
- **Runbook:** [docs/runbooks/provisioning-esxi-fc.md](runbooks/provisioning-esxi-fc.md).
