# Live validation: replication preview (SPEC-016 R1–R3), lab pair, 2026-10-08

First live record for the replication context. Run from labrat (GBGSAIROOP), `jumpbox-test` at
6d508256 from source (`.venv\Scripts\onboard.exe ui`). **Read-only: nothing was written to either
array.**

**Outcome: the Replication step read both arrays in 6 seconds and reported exactly what the
2026-10-07 fixtures predicted — the partnership found by link address despite the peer's misnamed
target, 2/2 links Up each way, `mirror_config`, the six existing Sync groups listed as untouched,
and the one finding this run was built to produce. SPEC-016 R1–R3 are live-verified; R4–R8 (apply,
verify, removal set) are next.**

## Environment

| | Array A (this run) | Array B (the peer) |
|---|---|---|
| System | AlletraMP_D22U27 · CZ2D320BT1 · 10.64.122.99 | AlletraMP_E18U31 · CZ2D3209YV · 10.64.154.190 |
| OS | 10.5.0 | 10.5.0 |
| RCIP | 0:4:3 10.54.122.92 · 1:4:3 10.54.122.93 | 0:4:3 10.54.154.192 · 1:4:3 10.54.154.193 |
| Remote Copy | Started, Normal · 6 groups · 18 VV sets | Started, Normal · 6 groups · 10 VV sets |

Sheet `D22U27_replication.xlsx`, composed from the blank template through `POST /init-sheet/compose`
(placeholders in the GreenLake/DSCC fields; Volumes `zz_rc_vol01` 1 GiB in set `zz_rc_vvs`;
Replication tab: peer 10.64.154.190, RTT 1 ms, one row `zz_rc_vvs` → peer CPG `SSD_r6`). Mode
**Custom**, only *Replication* ticked — provisioning deliberately skipped, so the plan has to block.

## 10:47 — Read both arrays

| Time | Event |
|---|---|
| 10:47:28 | Run created for CZ2D320BT1 (CUSTOM) |
| 10:47:33 | Reading 10.64.122.99: system, RCIP ports, Remote Copy… |
| 10:47:36 | Reading 10.64.154.190: system, RCIP ports, Remote Copy… |
| 10:47:39 | Read AlletraMP_D22U27 and AlletraMP_E18U31 — 1 blocking finding(s) |

Seen on the page, each as the spec words it:

- *Partnered — AlletraMP_D22U27 → AlletraMP_E18U31 2/2 links Up · AlletraMP_E18U31 → AlletraMP_D22U27
  2/2 links Up. Target on D22U27 "AlletraMP_E18U31" · target on E18U31 "AlletraMP_E18U31" · policy
  mirror_config.* — R2, matched by address (the peer's target carries the peer's own name).
- The finding: *Volume set 'zz_rc_vvs' does not exist on AlletraMP_D22U27. Run Provision storage
  first, or correct the name.* — correct: this run skipped provisioning.
- Plan: 6 to create (test volume + set, group `zz_rc_vvs_rcg` async RPO 10 / period 5 → E18U31,
  peer set `zz_rc_vvs_rc`, group `zz_rc_test_rcg`, peer set `zz_rc_test_rc`), 0 exist, 0 conflicts;
  *Show 12 commands* in apply order; note *On AlletraMP_E18U31 each new group will be named
  '<group>.r188150'*.
- *Replication already present*: `300gb` Sync Primary 2/2 synced (auto_recover, auto_synchronize);
  `APP_Test` Sync **Secondary** 1/1 (… active_active); `Intern_Automation` 4/4; `Intern_Automation2`
  4/4; `Test-RCG` 2/2; `Test-RCG2` 2/2 — all Started. Matches `tests/fixtures/rc_pair/README.md`.

## Owed

- The clean-plan path (0 findings) once *Provision, then replicate* can run end to end — needs R4
  (apply). The first periodic group on this pair will also pin the `LastSyncTime` / period output.
- The runner scenario 7 (SPEC-006 §4b).

Two operational notes from the session, not defects: an earlier app instance (`python`, PID 2152)
still held port 8765 and had to be stopped before the new build could start; labrat has no copy of
a D22U27 workbook, so the sheet was composed from the template.
