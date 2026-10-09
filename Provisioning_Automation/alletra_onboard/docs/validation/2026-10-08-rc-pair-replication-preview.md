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

## 2026-10-09 21:22 — first apply (R4), `jumpbox-test` 2ab24f34: stopped at write 4, as designed

Same sheet and mode. `zz_rc_vol01` / `zz_rc_vvs` created by hand on D22U27 first (the sheet's host
set has no real member, so the Provision step would have blocked — a different test). Read both
arrays again → **6 to create · 0 conflicts**, no finding (the clean-plan path owed above: seen).
Approved → *Configure replication*:

| # | Write | Result |
|---|---|---|
| 1 | `createvv -tpvv SSD_r6 zz_rc_test_v01 1g` (WSAPI) | Done |
| 2 | `createvvset zz_rc_test zz_rc_test_v01` (WSAPI) | Done |
| 3 | `POST /remotecopygroups zz_rc_vvs_rcg` (mode 2, userCPG SSD_r6, localUserCPG SSD_r6) | Done — the group exists on the array |
| 4 | `PUT /remotecopygroups/zz_rc_vvs_rcg {syncPeriod: 300, policies: {…}}` | **HTTP 400 code 44** — *invalid input: parameters cannot be present at the same time - policies, syncPeriod* |

The step stopped there (*Stopped after 3 write(s)*), nothing after write 4 ran, and the removal set
listed exactly the three objects: `stoprcopygroup -f zz_rc_vvs_rcg` · `removercopygroup -f
zz_rc_vvs_rcg` · `removevvset -f zz_rc_test` · `removevv -f zz_rc_test_v01` (B block empty — the
peer was never written). R4's stop-at-first-failure and R7's bounded removal set are live-verified
by this.

**The defect:** one `modifyRemoteCopyGroup` body may carry the period *or* the policies, not both —
a WSAPI rule absent from the client docs and from the 2026-10-07 capture (no periodic group
existed to read). Fixed the same evening: two PUTs, period first, then policies
(`WsapiClient.set_remote_copy_group`), pinned by `test_period_and_policies_go_in_two_puts_period_first`
with a stub that raises the array's exact error on a combined body. Also: the step header read
*Failed · awaiting approval* after the stop; it now reads *stopped after N write(s)*.

Also noticed: `APP_Test` is now **Primary** on D22U27 (Secondary on 10-08) — someone switched the
Peer Persistence group between the two sessions; not ours, listed and untouched.

Still owed: the retry on the fixed build after the removal set is pasted, then Verify, then the
first periodic group's `showrcopy` as a fixture.

## 2026-10-09 21:41 — second apply, `jumpbox-test` ab8059e: stopped at write 7, the start

Removal set pasted, read again → 6 to create, approved. The two-PUT fix held: period and policies
both *Done*. Then:

| # | Write | Result |
|---|---|---|
| 1–2 | test volume, test set | Done |
| 3 | `creatercopygroup zz_rc_vvs_rcg … periodic` | Done |
| 4 | period 300 s, then policies (two PUTs) | Done |
| 5 | `admitrcopyvv -createvv zz_rc_vol01` — the secondary was created on E18U31 | Done |
| 6 | `createvvset zz_rc_vvs_rc` on E18U31 | Done |
| 7 | `startrcopygroup zz_rc_vvs_rcg` | **HTTP 400 code 236** — *Group with different modes on a single target is not supported* |

Removal set: A `stoprcopygroup -f` · `dismissrcopyvv -f -removevv zz_rc_vol01 zz_rc_vvs_rcg` ·
`removercopygroup -f` · `removevvset -f zz_rc_test` · `removevv -f zz_rc_test_v01`; B `removevvset -f
zz_rc_vvs_rc`. Exactly what was created.

**The rule:** one mode per target. The lab target already carries six **Sync** groups; a Periodic
group can be created, configured and populated on it, but not started. HPE says so in two places
we had read and not turned into a check — Support Matrix note 1 (*"RC Groups using the same
RC-Target must replicate in the same mode"*) and the Getting-started guide (*"create a separate
target for each mode"*). Fixed the same evening: R2 gains the finding (names the target, the
groups and their mode, the way out), the Replication tab may not mix modes, and the tool's own test
group follows the rows' mode. Pinned by `test_an_async_row_on_a_target_that_carries_sync_groups_is_a_finding`
with the exact sentence. The removal set's paste order is now B first (the peer set must go before
`-removevv` takes the secondaries).

Consequence for this pair: the live test runs in **sync** (RTT 1 ms). The first periodic group's
`showrcopy` fixture waits for a target that carries no sync groups.

Still owed: paste this removal set (B, then A), retry with `mode: sync` on the tab, Verify.
