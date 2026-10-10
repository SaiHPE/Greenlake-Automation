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

**Removal set pasted 2026-10-09 (B first, as the page then said) — the order was wrong, the lines right.**
E18U31 refused `removevvset -f zz_rc_vvs_rc` while the group existed: *"Set zz_rc_vvs_rc is currently
admitted to Remote Copy Group and may not be directly removed."* On D22U27 `stoprcopygroup -f`,
`dismissrcopyvv -f -removevv zz_rc_vol01 zz_rc_vvs_rcg` (*"Volume zz_rc_vol01 has been dismissed"*;
the secondary on E18U31 was gone with it — `showvv zz_rc_vol01` there: *no vv listed*),
`removercopygroup -f` (*"Group zz_rc_vvs_rcg has been deleted"*), `removevvset -f zz_rc_test`,
`removevv -f zz_rc_test_v01` all succeeded; `zz_rc_vvs` on D22U27 still holds `zz_rc_vol01`. The page
now says **A first, then B**, with the array's sentence as the reason.

## 2026-10-09 22:07 — third apply, `jumpbox-test` 47084d7, **sync: configured and verified**

Sheet rebuilt with `mode: sync` (RTT 1 ms). Read → 6 to create, 0 findings, every group line
`…:sync`; the tool's own test group followed. Approved → *Configure replication*: **12 writes in two
seconds, all Done** — test volume and set; `zz_rc_vvs_rcg` created (sync → AlletraMP_E18U31,
localUserCPG SSD_r6), policies set, `zz_rc_vol01` admitted with its secondary auto-created on
E18U31, peer set `zz_rc_vvs_rc` created on E18U31, group started; the same five for
`zz_rc_test_rcg`. Header: *Complete · replication configured*. Removal set: 8 lines on A, 2 on B.

*Verify replication* (screenshot kept): links *2/2 Up* each way; **both groups Replicating** —
*Started · Primary here, Secondary on the peer · Sync · 1 volume(s) Synced*; peer names
`zz_rc_vvs_rcg.r188150`, `zz_rc_test_rcg.r188150`.

Read-only capture minutes later (`tests/fixtures/rc_pair/after_apply/`): `showrcopy` on both arrays
shows the two new groups beside the six old ones (8 each side), `auto_recover,auto_synchronize`,
`Synced`, `LastSyncTime NA`; WSAPI records `role 1`/`mode 1`/`state 3`/`syncStatus 3`,
`volumeLastSyncTime 2026-10-09T22:07:07+05:30`, `localVolumeSetName zz_rc_vvs`; `showvvset` on
E18U31 lists `zz_rc_vvs_rc` and `zz_rc_test_rc` with the secondaries. **No `RCP_<group>` set was
created** — that is CLI `creatercopygroup` behaviour, not WSAPI's. Pinned by
`test_verify_on_the_live_after_apply_capture_says_replicating_for_both_groups`.

**SPEC-016 R1–R8 are live-verified for sync.** Three live lessons on the way, each now a test:
two PUTs for period and policies (code 44); one mode per target is a finding, not a failed start
(code 236); the removal set pastes A before B. Owed: the periodic path end to end (needs a target
without sync groups), the *Provision, then replicate* preset with a real host, runner scenario 7.

**Cleanup 22:40 — the tool's removal set, A then B, plus the two hand-made objects:** every A line
accepted (*"Volume … has been dismissed"*, *"Group … has been deleted"*, *"Removing vv …"*); on B
both `removevvset` lines answered *"vv set … does not exist"* — **the array removes the peer set
itself when a started group is removed** (it did not on the never-started group of the second
attempt). `showrcopy groups zz_rc*` / `showvvset zz_rc*` / `showvv zz_rc*` empty on both arrays;
the six original groups untouched. Both arrays are as they were on 2026-10-07.

## Where a periodic target could come from — 2026-10-09 22:50–23:10, read-only plus one refused write

`scripts/rc_options.py` (jumpbox-test branch) read all three lab arrays and pinged across the
replication networks; `scripts/rc_target2.py` tried the cheapest idea, a second target over the
existing ports. Captures in `tests/fixtures/rc_pair/second_target/`.

- **VZ** (`MPB10K-D24U21-VZ`, 10.64.122.140, OS 10.5.51) is up on management but its RCIP ports
  10.222.1.5–.8/24 have no gateway and no carrier (`loss_sync`); its one target `MPB10K-E24U21-LZ`
  is `failed`, four links `Down`. Pings D22U27→VZ and E18U31→VZ: 100 % loss; VZ→either:
  *Destination Host Unreachable* from itself. The VZ/LZ pair is physically down today — relevant to
  the owed CRV VZ/LZ run too. Not a candidate without recabling the CRV pair's ports.
- **Spare ports** 0:4:4 / 1:4:4 on D22U27 and E18U31: `offline`, no cable.
- **Second target over the same links — refused on both arrays**, nothing created:
  `creatercopytarget AlletraMP_E18U31_async IP 0:4:3:10.54.154.192 1:4:3:10.54.154.193` →
  *"Link 0:4:3:10.54.154.192 appears to exist on another target."* A link (local port, peer address)
  belongs to one target. Targets and links after are identical to before (captured).

**So the periodic run needs new links:** cable the spare x:4:4 ports and give them routed
addresses (lab-team ticket; the two arrays' RCIP subnets 10.54.120.0/21 and 10.54.152.0/21 are
routed, not flat). Since a link is unique per *local port + peer address*, cabling one array's two
spare ports is enough in principle: the other array's second target uses its existing ports toward
the two new addresses, and the cabled array's second target uses its new ports toward the existing
addresses — the shared-port layout HPE describes for 1-to-N. To be proven once ports have carrier.
The other way is the group owners' agreement to re-home the six Sync groups, which is not ours to ask
for lightly. **Decision owed by the operator (BL-20).**

## The periodic run — 2026-10-09 23:30–23:55, the six Sync groups paused for the window

The operator chose the pause. Baseline captured (`rc_option1.py baseline`: `showrcopy`, `showrcopy
-d groups`, `showvvset`, `showvlun`, `showvv` both arrays), `zz_rc_vol01` + `zz_rc_vvs` recreated,
then `stoprcopygroup -f` on each of the six from its Primary side — read at run time, because
**APP_Test had swapped sides since 10-07** (Primary on D22U27 now; the first draft of the script
had it hard-coded on E18U31, the kind of overfit this session was asked to avoid).

**The UI refused, as designed:** the R2 finding counts stopped groups too (*already carries 6 sync
group(s)*), because a periodic group started beside stopped Sync groups puts their restart at risk.
So the run went through the product's own modules from a harness (`scripts/rc_async_lab.py` on the
lab branch): same `read_array` / `check` / `build_plan` / `apply_plan` / `verify`, with exactly that
one finding dropped. Sheet composed by `rc_sheet.py async` (one row, `zz_rc_vvs` → `SSD_r6`, async,
RPO 10 → period 5 min).

**Apply: 12 writes, all `created`, no error** — test volume, test set, `creatercopygroup …:periodic`
(with `localUserCPG`), the two PUTs (period 300 s, then policies), admit with `volumeAutoCreation`,
peer set on B, **start accepted** — the same start that was code 236 at 21:41 with the Sync groups
started. **The array's one-mode rule counts started groups only.** Verify, twice: both groups
*Replicating · Started · Primary here, Secondary on the peer · Periodic · 1 volume(s) Synced · last
sync 2026-10-09 23:39:23 IST*, links 2/2 each way. Captures in
`tests/fixtures/rc_pair/after_apply_periodic/` with the harness's plan / result / verify JSON.

**What the capture taught the code:** the periodic primary's `showrcopy` row has spaces inside its
Options column (`Last-Sync <ts>, Period 5m,<policies>`); the parser split on whitespace and would
have shown "Last-Sync" as the only policy. Fixed the same night: `period` and `last_sync` are fields,
the Replication page shows *Periodic · every 5m* and the last sync. The array adds
`over_per_alert` to a periodic group by itself.

**Cleanup and restore:** the removal set (A then B) run by `rc_async_lab.py cleanup`, every line
accepted; `rc_option1.py start` restarted the six (delta resync from the stop snapshots, all volume
rows Synced within minutes); `rc_option1.py compare` — **IDENTICAL to the baseline** on `showrcopy
groups`, `showrcopy -d groups`, `showvvset`, `showvlun` on both arrays; `unprep` removed the test
volume and set. The pair is as it was on 10-07 plus APP_Test's side swap, which predates us.

**Not learned, on purpose:** whether the Sync groups restart beside a *started* periodic group (the
periodic groups were removed first). The tool's finding for stopped groups therefore stays, with the
honest sentence (*the array would start … but … the tool will not put their restart at risk*).

**SPEC-016 R1–R8 are live for sync and periodic.** Through the UI for sync; through the same
modules for periodic. Owed: periodic through the UI itself (a target of its own, BL-20), the preset
with a real host, runner scenario 7.

## Periodic through the UI — 2026-10-10 15:29–17:05, the six Sync groups removed and rebuilt

The operator's decision (2026-10-10): the six lab groups may be removed and rebuilt; no data at
stake. `scripts/rc_rebuild.py` (lab branch) first **saved** every group's definition from
`showrcopy -d groups` (Primary side, target, mode, CPGs, policies, volume pairs, local/remote sets)
plus `showvvset`, `showvlun -t`, `showhost` on both arrays, then stopped and removed them from
their Primary side with `removercopygroup -f` — **without `-removevv`, so every volume stayed on
both arrays**.

**Five went at once; the Peer Persistence group did not.** `APP_Test` (`active_active`) answered
`setrcopygroup pol no_active_active` with *"Cannot remove active_active policy … Remote group
APP_Test.r188150 contains an exported Peer Persistence volume (Id=531). Please unexport
geoclustered volumes"* and `removercopygroup -f` with *"Volume APP.test.vv of group
APP_Test.r188150 is an Active-Active Peer Persistence volume. Please unexport the secondary volume
so the host only has access to the primary volume and retry."* After `removevlun -f APP.test.vv 16
set:ESX1` on E18U31 (answer: *"Issuing removevlun …"*) the removal was accepted (*"Group APP_Test
has been deleted."*). The UI read in between showed the honest finding for one stopped sync group
(*… already carries 1 sync group(s) (APP_Test), all stopped …*).

**The UI run, no override anywhere (run `a9476922`):** `D22U27_replication_async.xlsx`, Custom,
Replication only. *Read both arrays* → no findings, 0 groups each side, plan 6 to create, every
group line `…:periodic`. *Configure replication* → **12 writes Done** at 15:37:44–45.
*Verify* at 15:38: both *Replicating · Started · Primary here, Secondary on the peer · Periodic ·
1 volume(s) Synced*; *Verify* again at 15:45: **last sync 2026-10-10 15:42:48 IST** — the
5-minute resync cycle ran on its own between the two reads. Removal set shown by the page, A then
B; run by `rc_rebuild.py ui-cleanup` straight from the app's event (every A line accepted, both B
lines *does not exist* — the array removes the peer set with a started group, as on the 9th).
Capture of the live state in `ui_before_cleanup/`.

**Rebuild, from the saved definitions:** `creatercopygroup [-usr_cpg …] <g> <target>:sync`,
volumes admitted to the EXISTING secondaries, policies set, `startrcopygroup`. Two things the array
taught on the way: (1) the CLI `admitrcopyvv <vv> <group> <target>:<existing secondary>` for a
single volume **never answered** (set-based `admitrcopyvv set:300gb …` did) — switched to the
product's WSAPI `addVolumeToRemoteCopyGroup` without `volumeAutoCreation`, which admitted every
volume at once; (2) `creatercopygroup` from the CLI did **not** create the `RCP_<group>` set its
help promises (`showvvset` identical before and after). All six Started, every volume **Synced**
on both sides within minutes, `active_active` accepted on `APP_Test`.

**Peer Persistence host proximity — one wrong guess, corrected:** `createvlun APP.test.vv 16
set:ESX1` on E18U31 was refused (*"Cannot export to host which is not admitted to the group"*);
the host set has to be admitted with `admitrcopyhost -proximity {primary|secondary|all}`. The
save had not captured `showhostset -summary` (its `RC_host` column holds the value), and I
inferred `secondary` from the host set living on E18U31 — the array's first summary showed the
original was **`Pri`**, so the inference was wrong and changed it. Put back with the same command
and `primary` (allowed on the secondary *"to correct inconsistencies"*; the export was accepted in
between and is in place). Each `admitrcopyhost` leaves an array-made host set `RH<n>_<group>`
(`RH0_APP_Test` on D22U27, `RH0_APP_Test.r188150` on E18U31, both `Pri`) — the array's own
bookkeeping, the only visible difference from before. The script now captures
`showhostset -summary` in every save.

**Compare against the save:** `showrcopy groups` identical, `showvlun -t` identical, `showvvset`
differs only in `test999.2610…` snapshots — a pre-existing 15-minute snapshot schedule on D22U27
that ages old ones out and adds new ones (`showsched`, captured 10-07). Lab restored.

**SPEC-016 R1–R8 are live for sync and periodic, both through the UI.** Owed: the preset with a
real host, runner scenario 7, and (still) whether a stopped Sync group restarts beside a started
periodic group — not taken today either, the periodic groups were removed before the rebuild.

## Failover test (SPEC-017) — 2026-10-10 18:18 to 19:01, sync, the tool's test group

Three runs on `zz_rc_test_rcg` (1 GiB, sync, D22U27 → E18U31), each run from the Failover test
page, the terminal side done by `scripts/rc_failover_lab.py` (lab branch).

1. **18:18, stopped at step 4.** Stop (P) and failover (action 7 on S) worked. With both arrays up
   the array mirrored the failover at once (P Secondary-Rev) and started the group from S by itself,
   so the recover the tool sent was refused: HTTP 403 code 284 *Remote copy group not stopped*. The
   test stopped and showed the state and the way back, as designed. Also seen: `Syncing (100%)` in
   the SyncStatus column (parser fixed).
2. Between runs the group was found as **Secondary on P, Primary on S** (no -Rev): the array had made
   S the natural primary once the sync back finished. The lab script put it back with stop on S,
   `setrcopygroup reverse -f` on S, `startrcopygroup` on P; every command accepted.
3. **18:45, stopped at step 6.** Steps 0 to 5 passed and step 4 correctly sent no recover. As the
   sync finished the array again turned the -Rev roles into plain Primary (S) / Secondary (P), and
   `restore` (action 10) was refused: HTTP 400 code 29 *the role of group … was not previously
   switched*. Step 6 changed to follow the array: restore while the roles carry -Rev, otherwise
   fail back the way it failed over (stop on S, failover on P).
4. **18:55, PASSED.** All 7 steps OK; failover 1.6 s; synced back at once; fail back 16 s; the
   group ended Primary/Started on D22U27 and Secondary/Started on E18U31, every volume Synced.

**As-built generated live** after the pass: the replication section (partner array, links, the two
groups with roles and sync state, the six lab groups listed as already present) and the Failover
test section (result, timings, the 7-step table with both arrays' state after each step). Two
wording faults in the replication section for a run that found the groups already in place were
fixed the same evening (it said both *built but not applied* and *Configured over WSAPI*; the peer
volume set showed —).

**What this teaches about the arrays (OS 10.5.0, mirror_config, both arrays up):** a failover is
mirrored to the old primary straight away, the array starts replication back by itself, and once
that sync is complete it makes the peer the natural primary. So in a planned test the way home is
the same move from the other side, not recover + restore. Recover and restore remain the path when
the old primary was unreachable at failover (a real disaster); the tool picks by what the arrays show.
