# SPEC-015 — The Replication tab

**Status:** APPROVED 2026-10-07; **re-cut the same day** — the two-array workbook and paired runs
(ADR 0014) are deferred; replication is a step on the existing one-array run — not implemented
**ADRs:** [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md) (sequenced: groups
first over WSAPI; links and targets later) · [0014](../adr/0014-paired-runs-from-one-workbook.md)
deferred · [0013](../adr/0013-one-array-credential-per-run.md) unchanged
**Research:** [2026-10-07](../research/2026-10-07-replication-document-review.md) §3, §6.1
**Owner:** `application/platform/init_sheet.py` (template, parser, compose), `domain/workflow.py`
(registry, phases, preset), `domain/replication.py` (new intent model), `frontend` (step pages)

## 1. Problem

Replication needs the peer array's address and credential, and a list of what to protect. The
workbook names one array and that stays (ADR 0013). The engineer adds one tab to the workbook they
already have, and the run gains two steps.

## 2. Requirements

**R1 — A new, optional tab "Replication".** Parsed only when present and non-blank; every workbook
written before this spec parses exactly as today.

| Section | Fields | Default / rule |
|---|---|---|
| *Peer array* | Management address · User · Password | Required. Held by the run for the replication steps only, like the switch and vCenter credentials. The peer's system name is **read** (`showsys`), never asked. |
| *Measured round-trip time (ms)* | one number | Required for any `sync` row; optional otherwise. |
| *Protection* — one row per Remote Copy group | Volume set · Mode (`async` / `sync`) · RPO (minutes, async only) · Peer CPG · Peer volume set name · Auto synchronize · Auto recover | Mode **async**; RPO **10**; Peer volume set `<set>_rc`; both policies **yes**. |
| *Failover test* | yes / no · Group (blank = the tool's own test group) | **yes**, own test group. |

Direction is always **this run's array → the peer**. To replicate the other way, run the tool on the
other array with its own workbook.

**R2 — Validation at upload (blocking, one sentence each).**
- Mode is not `async` / `sync`, or any other type is named (Peer Persistence, Active Sync, SLD, 3DC)
  — *not supported in this version*.
- Async RPO missing, under 1 minute or not a whole number of minutes. Period sent to the array =
  RPO / 2 (the array's minimum period is 15 s; whole minutes keep RPO ≥ 2 × period simple).
- Sync with RTT missing or > 10 ms; async with RTT > 200 ms (Support Matrix, RCIP).
- Peer CPG blank. Peer array address, user or password blank.
- The volume set is not on the *Volumes* tab (its presence on the array is checked at step time).
- The derived group name (R3) exceeds 22 characters.

**R3 — Names the tool derives.** Group `<volume set>_rcg` (shortened with a stable suffix to stay
≤ 22). The failover test's own objects: volume `zz_rc_test_v01` (1 GiB) in VV set `zz_rc_test` on
this run's array, group `zz_rc_test_rcg`, peer set `zz_rc_test_rc` — created and removed by the
Replication step through the same WSAPI calls and removal lines provisioning uses (SPEC-007).

**R4 — Steps and modes.** `WorkflowPhase` gains `STORAGE_REPLICATE` and `STORAGE_FAILOVER_TEST`;
the step registry gains `replicate` ("Replication") and `failover_test` ("Failover test"), served
through `/app/profile` like every step. `_STEP_REQUIRES` for both = the Replication tab; a run
whose sheet has none refuses them with one sentence. New preset `RunMode.REPLICATE` = discover →
zoning → provision → replicate → failover_test → verify → asbuilt; *Custom* can pick them.

**R5 — UI.** Two step pages in the existing `StepShell` / `useStepState` pattern. The Configure page
lists the peer array (address, and the system name once read). No pair header, no A/B switch.

**R6 — Template and compose.** `build_template_bytes` and `compose_workbook_bytes` (SPEC-006 R3)
include the tab with R1's defaults and a notes column; `POST /init-sheet/compose` accepts a
`replication` block so the runner can compose scenario 7 sheets.

## 3. Non-goals

Array B columns and paired runs (ADR 0014, deferred until engineers ask for the DR site's hosts in
the same workbook — today that is a normal run on the peer). Replication types beyond 1-to-1 async
and sync. RCFC. Snapshot schedules (BL-21). Replicating in both directions from one run.

## 4. Verification

Unit: every workbook fixture in the repo parses identically before and after; a workbook with the
tab yields a `ReplicationIntent`; each R2 rule refuses with its sentence; R3 names stay ≤ 22; the
registry serves the two steps and refuses them without the tab. Live: upload a D22U27 workbook with
peer E18U31; the Replication step reads both arrays (SPEC-016 R1).

## 5. Size

Parser, model and template (~180 lines), registry and modes (~30), compose (~20), ~15 unit tests.
Ships with SPEC-016 as v0.17.
