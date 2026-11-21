# Live validation: BL-65 engineering-standard refactor (PRs #50–#68), rack13-ARCUS & PRIMERA630R11U22, 2026-11-19 to 2026-11-21

End-to-end live verification of the BL-65 engineering-standard refactor across PRs #50–#68 on
`rack13-ARCUS` (Alletra MP B10000, OS 10.6.0) and `PRIMERA630R11U22` (Primera 630, OS 4.6.20), run
from `2026-11-20` through `2026-11-21` (PRs #53–#55 ran on `2026-11-20`; PRs #56–#68 ran on
`2026-11-21`, with the final full-suite run on PR #68 branch head `c8fc5d41`, merged to `main` as
`dcc9aa34`). PR #49 (`3cea7b03`, encrypted credentials and schema versions) is recorded separately in
[2026-11-19-bl65-credentials-and-schema.md](2026-11-19-bl65-credentials-and-schema.md). Driven from
source against a fresh state database per script under the lab lock; credentials came from the lab
initialisation workbooks via the app's own parser (`fl.sheet_targets`), with no password, token or
subscription key printed or saved.

**Outcome: every lab script passed with 0 failures. `failed_apply_lab.py`, `iscsi_lun_lab.py` and
`rcip_tool_lab.py` wrote `zz_*` objects to the lab arrays and removed everything they created via
their removal sets; `init_walk_lab.py` and `ui_live_lab.py` made no writes to any device. The demo
pair checks (`demo_prep.py check`, `demo_objects.py check`) were all READY before and after.**

## Scope verified (PRs #50–#68)

| PRs (merge SHA) | What changed |
|---|---|
| #50 (`de58d0cd`), #51 (`a6994bb9`), #52 (`e4310aa5`) | **Standard, gate and cleanup (ADR 0028, ADR 0030):** engineering standard, `scripts/check.py` / `scripts/fitness.py` gate, `lab/init_walk_lab.py`, dead code/docs subtracted, import boundaries/cycles/knip/eslint burned to zero, audit findings fixed. |
| #53 (`fd6741b9`), #54 (`f5881394`), #55 (`f980c868`), #57 (`12ef6ae5`) | **Least privilege (ADR 0031):** `WsapiReader`/`WsapiWriter` split, single-use `Approval` required for every array writer and failover test, pre-write undo checkpointing (`apply_in_progress`) and crash recovery, every write site tested for its record. |
| #56 (`c5afcaad`) | **Error contracts (STANDARD E1–E3):** unified `DeviceError` hierarchy, narrow catches, zero silent swallowing (`except: pass` / `suppress(Exception)`). |
| #58 (`566770c9`), #63 (`e21578f6`) | **Typed run events and generated API types (ADR 0032):** `domain/events.py` registry, OpenAPI-generated `frontend/generated/api.ts`, last hand-written frontend API types removed. |
| #59 (`d5cfc991`) | **Per-area API routers:** `create_app` split into routers under `api/routes/` (complexity 114 → 3). |
| #64 (`60955928`), #66 (`2741d0e6`) | **Zero pyright errors and zero suppressions** across Python and TypeScript. |
| #60 (`7ae17e1a`), #61 (`b906e325`), #65 (`b9c0e422`), #66 (`2741d0e6`), #68 (`dcc9aa34`, tested at `c8fc5d41`) | **Complexity hot spots cleared (STANDARD M1):** provisioning planning, zoning, replication, `showrcopy`, iSCSI network, `asbuilt`, `init_sheet` parser/composer, handover, verification, `path_verify` and `peer_ports` — all remaining non-cloudinit/failover production `C901` entries cleared (leaving only `cloudinit_wizard.py` 15, `onboarding/steps.py::_run_cloudinit` 13, and `replication/failover.py::run_failover_test` 11). |
| #62 (`ca5c99d0`), #67 (`7038c9e6`) | **Living docs refreshed:** arc42 + C4 `HLD.md` / `LLD.md` and `DEVELOPER-HANDBOOK.html`. |

## Lab results

| Script / check | Profile / mode | Result | Notes |
|---|---|---|---|
| `lab/init_walk_lab.py` | `full` build profile (with restart) | **112 PASS, 0 FAIL** | Read-only against devices; runs, stored credentials and held workbook survived app restart |
| `lab/init_walk_lab.py` | `init-only` build profile (with restart) | **62 PASS, 0 FAIL** | Read-only against devices; locked init-only registry, upload, pages and restart persistence |
| `lab/ui_live_lab.py` | read-only | **23 PASS, 0 FAIL** | Discovery, zoning check/plan, provisioning plan, Array ports, Verify, as-built at 1366 and 1080 wide |
| `lab/failed_apply_lab.py` | provisioning failure + undo | **27 PASS, 0 FAIL** | Sheet refusals (1 PiB, illegal volume/VV-set names), mid-apply failure keeps removal set across UI/rebuild/as-built, Console refuses `showtarget -rescan`; `zz_bl45_*` removed |
| `lab/iscsi_lun_lab.py` | iSCSI host + LUN export | **17 PASS, 0 FAIL** | Host created from IQN, 1 GiB LUN presented, paths verified, as-built generated; `zz_is_*` removed |
| `lab/rcip_tool_lab.py` | `sync` (OS 10.6.0 → 4.6.20) | **12 PASS, 0 FAIL** | Sync blocked at preview 1 before any write (BL-62), apply refused HTTP 409; zero writes sent by the run |
| `lab/rcip_tool_lab.py` | `async` (full RCIP flow) | **38 PASS, 0 FAIL** | Partnership setup, link check, groups, `showrcopy -d` verify, failover test and back, as-built without performance, merged removal set restored pair |
| Demo pair health | `demo_prep.py check` & `demo_objects.py check` | **All READY** | Verified before and after the runs; demo volumes and sets untouched |

## Not covered in this session

Hardware-gated items that require lab equipment outside rack13 + Primera remain open as tracked in
[SCOPE.md](../SCOPE.md): D22U27 (BL-21 checks 3–4 and BL-28 Unified File), a cabled FC peer port
(BL-26), the 3PAR 20850 R2 (BL-27), a Linux host with multipath + an Alletra LUN (BL-36), and a
cabled FC array pair (BL-50).
