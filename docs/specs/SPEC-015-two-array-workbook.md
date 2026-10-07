# SPEC-015 — Two arrays in one workbook, and the paired run

**Status:** APPROVED 2026-10-07 (operator decisions: paired runs; sync and async first; defaults
below) — not implemented
**ADR:** [0014 — paired runs from one workbook](../adr/0014-paired-runs-from-one-workbook.md)
**Research:** [2026-09-19](../research/2026-09-19-replication-two-arrays.md) §6,
[2026-10-07](../research/2026-10-07-replication-document-review.md) §3, §6
**Owner:** `application/platform/init_sheet.py` (template, parser, compose), `domain/models.py`
(`RunRecord`, `RunMode`, `WorkflowPhase`), `domain/workflow.py` (registry), `api/app.py`
(`/runs/from-sheet`, `/runs`), `frontend` (pair header, run list)

## 1. Problem

Replication needs two arrays. The workbook names one and refuses two; a run is one array. The field
engineer must be able to describe both arrays and the replication between them in **one** workbook,
upload it once, and work through each array with the steps that already exist.

## 2. Requirements

**R1 — Array B in the key/value tabs.** The *Initialisation* and *Provisioning* tabs gain a column
**"Array B"** between *Value* and *Notes*; the existing *Value* column is headed **"Array A"**. The
parser locates columns by their header text (row 3), not by position, so every workbook written
before this spec (Field | Value | Notes) parses exactly as today. Array B is optional field by field:
a blank Array B column means a single-array workbook.

**R2 — Array B in the row tabs.** *Volumes*, *Host sets* and *Hosts* gain a first column **"Array"**
(`A` / `B`, blank = `A`). Each array's provisioning intent is built only from its own rows.

**R3 — The Replication tab.** A new tab, parsed only when Array B is present:

| Section | Fields | Default / rule |
|---|---|---|
| *Replication network (RCIP)* — one row per port | Array (A/B) · Port (N:S:P) · IP · Netmask · Gateway (optional) · VLAN (optional) | Rows may be left blank: the Replicate step then uses what `showport -rcip` already shows. At least 2 ports per array, on 2 different nodes, when filled. |
| *Partnership* | Name of B as seen from A · Name of A as seen from B | the other array's system name (`showsys`) |
| *Measured round-trip time (ms)* | one number | required for any `sync` row; optional otherwise |
| *Protection* — one row per Remote Copy group | Volume set · Direction (`A→B` / `B→A`) · Mode (`async` / `sync`) · RPO (minutes, async only) · Secondary CPG · Secondary volume set name · Auto synchronize · Auto recover | Mode `async`; RPO **10**; Auto synchronize **yes**; Auto recover **yes**; secondary set name `<set>_rc` |
| *Failover test* | yes / no · Group (blank = the tool's own test group) | **yes**, own test group |

**R4 — Validation at upload (blocking, one sentence each).** A row is refused with the reason when:
- Mode is not `async`/`sync`, or any other type (APP, Active Sync, SLD, 3DC) is named — *not
  supported in this version*.
- Async RPO < 1 minute or not a whole number of minutes (the array's minimum period is 15 s and
  RPO ≈ 2 × period; the DSCC minimum is 30 s — whole minutes keeps both simple). Period sent to the
  array = RPO / 2.
- Sync with measured RTT missing or > 10 ms; async with RTT > 200 ms (Support Matrix, RCIP).
- Two RCIP rows share an IP; an RCIP IP is in the same subnet as that array's management IP; an RCIP
  port is also an iSCSI port in the same workbook.
- The volume set is neither named on the primary array's *Volumes* tab nor (checked later, at
  Replicate time) present on the array.
- Secondary CPG blank.
- The group name the tool will derive (§R6) exceeds 22 characters.

**R5 — One upload, two runs.** `POST /runs/from-sheet` on a workbook with Array B creates **two**
runs atomically: run A (`role: primary`) and run B (`role: secondary`), with the same `pair_id` and
each other's id as `peer_run_id`. Each run's credential, intent and steps come only from its own
column (ADR 0013 unchanged). The response carries both run ids; a single-array workbook returns one
run exactly as today. If either run cannot be created, neither is.

**R6 — Names the tool derives.** Remote Copy group: `<volume set>_rcg` (shortened with a stable
suffix when needed to stay ≤ 22). Test group for the failover test: `zz_rc_test_rcg` over a 1 GiB
volume `zz_rc_test_v01` in VV set `zz_rc_test` on the primary, created by the Replicate step through
WSAPI — the same write path and removal lines provisioning uses (SPEC-007); no new write capability.

**R7 — Modes and steps.** `WorkflowPhase` gains `STORAGE_REPLICATE` and `STORAGE_FAILOVER_TEST`;
the step registry gains `replicate` ("Replication") and `failover_test` ("Failover test"), kind
`pair`, served to the UI through `/app/profile` like every step. A new preset `RunMode.REPLICATE`
= discover → zoning → provision → replicate → failover_test → verify → asbuilt. Pair-kind steps are
only enabled on a run with a `pair_id`; requesting one on a single run is refused with a sentence.

**R8 — The UI shows one pair.** When a run has a pair: a header *"Array A · <name> ⇄ Array B ·
<name>"* with an A / B switch above the per-array steps; switching changes which run the step pages
read and act on. Pair-kind steps show once, under the header, and say they act on both arrays. The
run list (*Open another run*) shows a pair as one entry with both serials.

**R9 — The template.** The downloadable template (`build_template_bytes`) and `compose_workbook_bytes`
(SPEC-006) include the Array B column, the Array column on row tabs and the Replication tab, with the
defaults of R3 pre-filled and a notes column explaining each field.

## 3. Non-goals

Replication types other than 1-to-1 `sync` and `async` (Active Peer Persistence, Active Sync, SLD,
3DC, MxN beyond one partner) — refused at upload until sync and async are proven live. RCFC
transport. Snapshot schedules (BL-21). More than two arrays.

## 4. Verification

Unit: every lab workbook in the repo's fixtures and on the operator's desktop list parses identically
before and after (single-array back-compat); a two-array workbook mints two runs with one `pair_id`;
each R4 rule refuses with its sentence; R6 names stay ≤ 22 characters; the registry serves the two
new steps and refuses them on an unpaired run. Live: upload a D22U27 ↔ E18U31 workbook, see the pair
header, switch A / B, run Discovery on each.

## 5. Size

Parser and template (~250 lines), pairing in the store and API (~120), registry and modes (~30), UI
pair header and run list (~200), ~25 unit tests. One release.
