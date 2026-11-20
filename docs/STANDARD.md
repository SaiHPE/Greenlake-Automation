# The engineering standard

This is the reference the code is measured against. It exists so that "good" means the same thing
to every person and every agent who works here, and so that a change can be judged by a check
rather than by taste.

Four rules govern the standard itself:

1. **Every rule has a source:** a published reference (section 2), an ADR, or a failure this project
   lived through (`docs/LESSONS.md`). A rule nobody can trace is deleted.
2. **Every rule has a check, or says plainly that it is judgement.** A check fails `scripts/check.py`
   and its message says what to do. When a judgement rule is broken twice, it gets a check, or the
   design changes so the mistake cannot be written.
3. **Known violations are listed one by one and only go down.** Each tool keeps its own list (section
   4). An entry names the file and the function or import, never a line number. The gate fails on a
   new violation, on a listed function that got worse, and on an entry whose violation is gone. It
   also fails when a branch adds an entry to a list or raises its number. Listed code that moves or
   is renamed takes its entry along (`scripts/fitness.py --move`); that is not a new violation.
4. **Changing a rule here needs an ADR.** Fixing a violation does not. Changing what a check
   measures is changing a rule: the gate fails when a branch changes the gate's scripts or a tool's
   settings.

The standard was reviewed before adoption by three independent models; their critiques and what was
taken from each are in ADR 0028. An audit of the first refactor steps found ways to pass the gate
without meeting a rule; ADR 0030 records what changed to close them.

## 1. What the code must be good at, in order

When two goals conflict, the higher one wins.

| # | Quality goal | What it means here |
|---|---|---|
| Q1 | **Safe on customer equipment** | The tool changes an array only through a plan the operator approved, only on the objects that plan names, never writes to a SAN switch, and can always say how to undo what it did. |
| Q2 | **Truthful** | Screens and documents report what the devices said when asked. A failure shows as a failure, an unknown as unknown, never as empty or done. |
| Q3 | **Operable by a consultant on a jump box** | One download, both build profiles (full and initialisation-only) work, plain words on screen. |
| Q4 | **Changeable without drift** | A person or an agent can add a step, a device read or a check without breaking the others and without copying a bad example. |

## 2. The references

| Key | Source | What we take from it |
|---|---|---|
| **SALTZER** | Jerome Saltzer and Michael Schroeder, *The Protection of Information in Computer Systems* (1975) | Least privilege, fail-safe defaults, complete mediation: a module holds only the power its job needs, and every write is checked against an approval. |
| **HEX** | Alistair Cockburn, *Hexagonal Architecture* (2005) | Dependencies point inward; the core is testable without the outside world. |
| **APP** | Harry Percival and Bob Gregory, *Architecture Patterns with Python* (2020), chapters on the service layer and dependency injection | Services orchestrate, adapters do I/O, clients come from injectable factories, tests use fakes. Not taken: a Protocol for every adapter, or a separate bootstrap module (chapter 13 presents bootstrap as one option for a wiring problem this app does not have). |
| **DDD** | Eric Evans, *Domain-Driven Design* (2003), the ubiquitous language | One vocabulary for the domain (`CONTEXT.md`), used in code, screens and documents. Not taken: separate bounded contexts with their own models; this is one context with several workflows. |
| **APOSD** | John Ousterhout, *A Philosophy of Software Design* (2nd ed., 2021) | Deep modules with small interfaces; information hiding; "define errors out of existence"; comments for what the code cannot say. Also its warning: splitting code to meet a length limit makes it shallower, not better. |
| **PARSE** | Alexis King, *Parse, don't validate* (2019) | Outside data becomes a typed value once, where it enters; inside code never re-checks it. |
| **MCCABE** | Thomas McCabe, *A Complexity Measure* (1976); NIST SP 500-235 (1996) | Cyclomatic complexity above 10 is where defects and untestable paths concentrate. |
| **EVO** | Neal Ford, Rebecca Parsons, Patrick Kua, Pramod Sadalage, *Building Evolutionary Architectures* (2nd ed., 2023) | Fitness functions: an architectural rule is a test that runs on every change. |
| **TRUST** | Lauren Tan, *All Code Is Slop (Except Mine)*, AI Engineer CODE 2026; her pstack principles | The code is the next agent's memory; a repeated correction becomes a check or a better API, not more prose; a comment that justifies a workaround spreads the workaround. |
| **DOCS** | arc42 (Starke, Hruschka) for the HLD's headings; the C4 model (Simon Brown) for its diagrams; Michael Nygard, *Documenting Architecture Decisions* (2011) for ADRs | One place for each kind of document. |
| **REACT** | react.dev, *Rules of Hooks* and *You Might Not Need an Effect* | How the UI holds state. |

## 3. The rules

### 3.1 Least privilege on customer equipment (Q1; SALTZER; ADR 0012, 0015, 0016, 0025)

| Rule | Statement | Check |
|---|---|---|
| S1 | Every SSH command the tool can send matches an allowlist; each exact form has a test. | existing allowlist tests |
| S2 | A module gets only the power its job needs. Array access comes in two classes: a **reader** with no method that changes anything, and a **writer** that extends it. Discovery, verify, the as-built, the hand-over and every plan get readers. | import-linter `protected` on each writer module and on the factory that builds it (once write factories live in their own module), naming the modules allowed to use it |
| S3 | A writer can only be built from an **approval**: the value the coordinator returns when the operator approved this run's current plan (or confirmed the failover test). No approval, a stale one or one from before a restart: no writer, so no write. | type of the writer factories' parameter; tests that a fake device receives zero writes without a valid approval |
| S4 | A write-scoped SSH client acts only on the objects its plan names, writes each object's removal line before the command, and reads the object back before the next object. | existing per-client tests; a fake-device test per writer |
| S5 | The undo of anything written is stored in the run before the write returns, so a crash leaves the removal set on record. A result says "possibly created, inspect first" when it cannot confirm. | test with a fake device that fails mid-apply, then reads the run's stored removal set |
| S6 | The switch client has no method that changes the switch. | existing Brocade allowlist test |

### 3.2 Layers (HEX, APP)

```
api/, cli/  ──►  application/  ──►  adapters/  ──►  domain/
     (entrypoints)      │                              ▲
                        └──────────────────────────────┘
```

| Rule | Statement | Check |
|---|---|---|
| L1 | `domain` imports nothing outside `domain`, and does no I/O. | import-linter `layers` |
| L2 | `adapters` never import `application` or `api`. Shared adapter plumbing (`tls`, `command_log`, `device_trust`) lives in `adapters/`. | import-linter `forbidden` |
| L3 | `application` builds clients only in its context's `clients.py` (one constructor per kind) and receives them as injectable factories. Errors and plan-object types that application code names are defined in `domain`. | import-linter `forbidden` with the `clients` modules listed as the allowed importers |
| L4 | `application` and `domain` import no network, SSH, browser or process library (`httpx`, `requests`, `paramiko`, `socket`, `ssl`, `subprocess`, `playwright`, `pyVmomi`, `winrm`). That I/O lives in an adapter. | import-linter `forbidden` on external packages |
| L5 | `api/app.py`'s `create_app` with `application/service.py` is the composition root: the only place services are wired. Entrypoints never import an adapter except the store they open. | import-linter `forbidden` |
| L6 | No import cycles, and no import inside a production function to hide one. | import-linter `acyclic_siblings`; ruff `PLC0415` on `src/` |
| L7 | A Protocol is added for a port only when there is a second production implementation or a fake that a test needs and a factory cannot give. `RunStore` is one. | judgement (APP, APOSD) |

### 3.3 Workflow packages (DDD, HEX)

| Rule | Statement | Check |
|---|---|---|
| B1 | The application packages form a declared order, and imports only go down it: `documents` → the step contexts (`onboarding`, `provisioning`, `snapshots`, `replication`, `unified_file`) → `runs` → `platform`. Step contexts do not import each other's `plan` or `apply`. Shared reads move down, to an adapter or `domain`. | import-linter `layers` on `application` |
| B2 | Verify and the as-built read the devices now, through readers (SPEC-018 R3, SPEC-023 R8); "what this run did" comes from the run's stored results. | covered by S2 and B1 |
| B3 | Words in code match `CONTEXT.md`. | judgement |

### 3.4 Functions and modules (APOSD, MCCABE)

| Rule | Statement | Check |
|---|---|---|
| M1 | Function complexity at most 10; at most 5 parameters; at most 12 branches and 50 statements (ruff's defaults, unchanged). A function on the list may not get worse. A change to what a listed function does brings it within the limits in the same change; an edit that leaves its behaviour alone (types, a rename, an import) need not. The hot spots in section 5 are fixed now. | ruff `C901`, `PLR0913`, `PLR0912`, `PLR0915`, listed per function with its current value as a ceiling (may not get worse); judgement (fixing it when its behaviour changes) |
| M2 | No limit on file length. A source file under `src/` or `frontend/src/` over 18,000 non-blank characters (about 500 lines) may not grow. Its non-blank characters are counted, not its lines, so joining lines changes nothing. Splitting a file or function only to get under a number is not a fix; a split must hide a decision, remove duplication or make behaviour testable on its own. | `scripts/fitness.py` (growth); judgement (the split) |
| M3 | No dead code: unused functions, classes, exports, dependencies. Tool findings are leads; a deletion needs proof that nothing reaches the code (LESSONS 18). | vulture (Python), knip (TypeScript) |
| M4 | A wrapper with one caller and no second implementation is inlined. | judgement |
| M5 | A rule that grows by one `if` per case becomes a table or a registry. | judgement; M1 catches the symptom |

### 3.5 Data at the edges and types (PARSE)

| Rule | Statement | Check |
|---|---|---|
| T1 | Device output, workbook cells, HTTP bodies, SSE events, environment variables and database rows are parsed into typed models where they enter; inner code trusts the types. A pure parser of device text that more than one context uses lives in `domain/array_parse.py`; one that a single context uses stays in that context's read module (ADR 0029). | judgement; T2 catches most slips |
| T2 | The backend type-checks: pyright `standard` on `src`, `strict` on `domain`. Brought in one package at a time. | pyright, per-file error counts listed |
| T3 | No `type: ignore` or `noqa` without its rule code; no `@ts-ignore`, and no `@ts-expect-error` without a reason. A file may not gain a suppression comment of any kind (`type: ignore`, `noqa`, `pyright:`, `eslint-disable`, `@ts-expect-error`). | ruff `PGH003`, `RUF100`; eslint `ban-ts-comment`, and its report of a disable comment that suppresses nothing; `scripts/fitness.py` (suppression comments counted per file) |
| T4 | Run events carry typed data: `RunEvent.data` is a union of models in the OpenAPI schema. The TypeScript types of the API and of the events are generated from it, not written by hand. The frontend has no `any` and no `as unknown as`. | a check that the generated file is current; eslint `no-explicit-any`, `no-restricted-syntax` |

### 3.6 Errors (APOSD, Q2)

| Rule | Statement | Check |
|---|---|---|
| E1 | Adapters raise subclasses of one `DeviceError` in `domain`. Application code catches `DeviceError` or something narrower. `except Exception` appears only at the coordinator's step boundary and the API's error mapping. | ruff `BLE001` with those two modules as the only per-file allowance |
| E2 | No silent swallowing: no `except: pass`, no `contextlib.suppress(Exception)`. | ruff `S110`, `S112` on; `scripts/fitness.py` for `suppress(Exception)` |
| E3 | A device that cannot be read gives "unknown" or "failed", never an empty list that reads as "none". | tests per reader |
| E4 | A failure the operator sees says what happened, what it means and what to do. | frozen words test; judgement |

### 3.7 Comments and documents (APOSD, TRUST, DOCS)

| Rule | Statement | Check |
|---|---|---|
| C1 | A comment says only what the code cannot: an outside fact (a device quirk, with the capture that shows it), a constraint someone must not break, or a marked exception (`TRUST-OFF:`). It never argues that a workaround is acceptable; fix the cause or open an issue. | ruff `ERA001`, `FIX`, `TD`; judgement |
| C2 | The structure is described once: the import contracts (enforced) and the HLD (`docs/design/HLD.md`, arc42 headings, C4 diagrams). Module tables are generated from the code or not written. The separate architecture document is gone. | `scripts/fitness.py`: every code path a document names exists, and so does a name it gives inside a file (`domain/workflow.enabled_steps`). Checked in `AGENTS.md`, the READMEs, `CONTEXT.md`, this file, `docs/design` and the ADRs from 0028 on. |
| C3 | Markdown lives in the folders that exist today; adding a folder is the owner's call. | `scripts/fitness.py` (folder list) |
| C4 | A new lesson about a code defect lands with the test or lint rule that now catches it, named by id; the gate resolves the id. A non-defect lesson states `No check:` and why. Old lessons are left as they are. | `scripts/fitness.py` (lessons after 49: the test id exists, or the rule is one the configuration selects, or the lesson says `No check:` and why) |
| C5 | `AGENTS.md` holds the judgement rules and points to the checks; it does not restate a rule a check enforces. | judgement |

### 3.8 Tests and verification (APP, TRUST, EVO)

| Rule | Statement | Check |
|---|---|---|
| X1 | Tests use fakes and real captured device output; no test opens a network connection. | socket guard in `tests/conftest.py` |
| X2 | A test asserts behaviour seen through a public interface and survives a change of internals. | judgement |
| X3 | Both build profiles start and serve the step registry, and the workbook-to-run path works in each, before and after any change. | API tests for `full` and `init-only`; a check that every module the PyInstaller spec names exists |
| X4 | Each step in the registry names the lab script that drives it live, or `None` with a reason. | `lab_script` on `StepDef`; the registry test checks the file exists |
| X5 | "Done" means run live on lab hardware with a validation record. | judgement; pull request template |

### 3.9 Frontend (REACT, SALTZER)

| Rule | Statement | Check |
|---|---|---|
| F1 | Only `api.ts` (HTTP) and `useRunEvents.ts` (SSE) talk to the backend. | eslint `no-restricted-globals` (`fetch`, `EventSource`) |
| F2 | A step page does not import another step page; shared pieces live in `ui/`. | eslint `no-restricted-imports` |
| F3 | Hooks follow the Rules of Hooks; an effect only syncs with something outside React. | eslint `react-hooks`; judgement |
| F4 | The step list and modes come from `/app/profile`. | existing test |

## 4. The gate

`scripts/check.py` runs every check above. Import rules keep their list in `pyproject.toml` and
`quality/imports-type-only.toml` (`ignore_imports`, with stale entries reported as errors), and
eslint keeps its own in `frontend/eslint-suppressions.json`. `scripts/fitness.py` checks everything
else against `quality/ceilings.toml`: ruff complexity and lint ceilings per function, pyright
per-file error counts, vulture and knip leads, file growth, suppression comments per file, document
paths, lesson ids and stale entries.

The lists are compared with the branch point as well (`lists`): an entry a branch adds, or a number
it raises, fails. `ALLOW_LISTS=1` lets it through as a warning; that is the owner's call, for a new
check that brings its list, and the pull request says why.

What the gate measures is compared with the branch point too (`config`): `scripts/check.py`,
`scripts/fitness.py`, `[tool.ruff]`, `pyrightconfig.json`, `frontend/eslint.config.js`,
`frontend/tsconfig.json`, the npm scripts and the knip block of `frontend/package.json`, and the
import contracts apart from their `ignore_imports` lists. A change to any of them fails;
`ALLOW_CONFIG=1` lets it through as a warning, for a change that comes with its ADR.

## 5. Order of work

Risk first, size last. Each step is behaviour-preserving, ships alone, and passes the gate, the tests
and the live checks for what it touches.

1. Safety net: the build-profile and spec checks (X3), the socket guard (X1), the gate with today's
   lists. No source change.
2. Subtract: proven dead code, the separate architecture document, stale module tables.
3. Mechanical moves: `tls`, `proxy`, `prereqs` and other raw I/O into adapters; shared error and plan
   types into `domain`; the cycles cut one per change.
4. Least privilege: reader/writer split, write factories behind approvals, undo stored before the
   write returns. One lab session covers provisioning, Remote Copy and snapshots.
5. Errors: `DeviceError`, package by package, onboarding last.
6. Types: pyright package by package, `domain` first; typed run events, then generated TypeScript types
   and eslint.
7. Complexity hot spots, each with characterisation tests from captured output first (ruff C901
   today): `create_app` (115), `assemble_hosts` (57), `_parse_snapshots_tab` (26), `apply_plan`
   (22), `build_report` (17).

Not done, on purpose: a Protocol per device client; a bootstrap module; splitting `init_sheet.py`,
`asbuilt.py` or a component only by length; rewriting the GreenLake and browser adapters beyond import
paths; retro-fitting old lessons.
