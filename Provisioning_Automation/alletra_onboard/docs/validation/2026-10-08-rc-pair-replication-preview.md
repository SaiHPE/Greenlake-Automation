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
