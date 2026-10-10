# Lab replication pair captures — 2026-10-07 18:19 (BL-38)

Read-only output from both arrays of the lab Remote Copy pair, captured from labrat with
`ui-smoke/rc_capture.ps1` (SSH `show*`/`help` via paramiko, one `exec_command` per file so each file
starts with `# <command>`; WSAPI `GET`s via the `hpe3parclient` the tool provisions with). Nothing was
written.

| Array | Dir | System | Serial | ID (hex / dec) | OS | WSAPI | RCIP (slot 4 port 3, both nodes) | Gateway |
|---|---|---|---|---|---|---|---|---|
| D22U27 | `D22U27/` | `AlletraMP_D22U27` | CZ2D320BT1 | 0x2DEF6 / 188150 | 10.5.0 | 1.15 (build 100500043) | 0:4:3 10.54.122.92 · 1:4:3 10.54.122.93 /21 | 10.54.127.254 |
| E18U31 | `E18U31/` | `AlletraMP_E18U31` | CZ2D3209YV | 0x2DEF2 / 188146 | 10.5.0 | 1.15 (build 100500043) | 0:4:3 10.54.154.192 · 1:4:3 10.54.154.193 /21 | 10.54.159.254 |

## What the pair looks like (the facts the parsers are pinned to)

- **Partnership:** one IP target on each array, two links, all `Up`, policy `mirror_config`.
  **The target on E18U31 is named `AlletraMP_E18U31` too** (it points at D22U27's RCIP addresses) —
  so the tool matches the partnership by **link addresses** (`showrctransport -rcip` `PeerIPAddress` ↔
  the other array's `showport -rcip` `IPAddr`), never by target name.
- **Groups:** six, all **Sync**, all `Started`/`Synced`, `LastSyncTime NA`: `300gb` (auto_recover,
  auto_synchronize), `APP_Test` (+ `active_active` — a Peer Persistence group whose Primary is E18U31),
  `Intern_Automation`, `Intern_Automation2`, `Test-RCG`, `Test-RCG2`. **No periodic group exists**, so
  the periodic `LastSyncTime` / period output is pinned by the first live async run, not here.
  `rcopy_async_test` (named in earlier notes) does not exist: `showrcopy_groups_rcopy_async_test.txt`
  holds the CLI error (`Error: group matching … does not exist on the system`) and
  `wsapi/remotecopygroups_rcopy_async_test.json` the WSAPI one (404, code 187).
- **Peer-side group name** = `<group>.r<creating system's decimal ID>` (`300gb` ↔ `300gb.r188150`),
  carried in WSAPI as `remoteGroupName`. The suffix stays after a role change (`APP_Test.r188150` is
  the Primary on E18U31).
- **WSAPI `/remotecopygroups` record:** `role` 1 Primary / 2 Secondary; `targets[].mode` 1 Sync
  (2 periodic, 4 async streaming per the client docs); `targets[].state` 3 (observed on Started groups);
  `targets[].policies` = `activeActive`, `autoFailover`, `autoRecover`, `autoSynchronize`,
  `multiTargetPeerPersistence`, `overPeriodAlert`, `pathManagement`; `targets[].syncPeriod` absent on
  Sync groups; `localUserCPG` / `targets[].remoteUserCPG` (`SSD_r6` ↔ `SSD_r6`, absent on two groups);
  `volumes[].remoteVolumes[]` = `remoteVolumeName`, `remoteVolumeID`, `syncStatus` 3 (Synced),
  `volumeLastSyncTime` (ISO, +05:30) / `volumeLastSyncTimeSec`, `localVolumeSetName` /
  `remoteVolumeSetName` (`300gb` ↔ `300gb`).
- **A second target between the same two arrays needs links of its own** (`second_target/`, live
  2026-10-09 23:10): `creatercopytarget AlletraMP_E18U31_async IP 0:4:3:10.54.154.192 1:4:3:10.54.154.193`
  is refused on both arrays with *"Link 0:4:3:10.54.154.192 appears to exist on another target."* —
  a link is (local port, peer address) and belongs to one target. So the HPE way out of "one mode
  per target" (a separate target per mode) needs spare RCIP ports with addresses: on this pair
  0:4:4 / 1:4:4 are `offline`, no cable, on both arrays. Nothing was created; targets and links after
  are identical to before.
- **The third lab array** `MPB10K-D24U21-VZ` (10.64.122.140, SGHD44LQLS, OS **10.5.51**) cannot
  stand in: its four RCIP ports (10.222.1.5–.8/24, no gateway) are `loss_sync`, its only target
  `MPB10K-E24U21-LZ` is `failed` with all four links `Down` (`second_target/VZ_*`); `controlport rcip
  ping` fails both ways (10.222.1.0/24 is not routed from 10.54.0.0/16).
- **`/remotecopy`:** `mode 2`, `status 1`, `asyncEnabled false`; links to `/remotecopygroups`,
  `/remotecopytargets` (not captured), `/remotecopylinks` (captured: one member per link, named
  `<target>_<N>_<S>_<P>`).
- **WSAPI write rules (live, 2026-10-09):** `PUT /remotecopygroups/<g>` refuses `syncPeriod` and
  `policies` in the same `targets[]` entry — HTTP 400 code 44 *"parameters cannot be present at the
  same time - policies, syncPeriod"*. Two PUTs. `POST /remotecopygroups` with `localUserCPG` in the
  body was accepted. **One mode per target:** a Periodic group on this target (six Sync groups) is
  created, configured and populated without complaint and then refused at **start** — HTTP 400 code
  236 *"Group with different modes on a single target is not supported"* (Support Matrix note 1).
  **Removal order:** the peer refuses `removevvset` on a set holding secondaries while the group
  exists (*"Set … is currently admitted to Remote Copy Group and may not be directly removed"*);
  `dismissrcopyvv -removevv` on the primary removes the secondary volume on the peer. Removing a
  **started** group removes its peer volume set too (`removevvset` on B then says *does not exist*);
  a never-started group leaves the set behind.
- **CPGs:** D22U27 `3sc`, `SSD_r6`, `test`; E18U31 `SSD_r6` only.
- **`help/`** — the array's own `-h` for every Remote Copy command (D22U27; identical OS on E18U31).
  Confirms: `creatercopygroup -usr_cpg <cpg> <target>:<cpg> <group> <target>:<mode>`;
  `admitrcopyvv -createvv [-nowwn] set:<set> <group> <target>:<sec_set>`; `setrcopygroup pol
  auto_recover|auto_synchronize`; `setrcopygroup period <n>{s|m|h|d} <target> <group>`;
  `setrcopygroup failover|recover|restore -f`; `dismissrcopyvv -removevv`; `stoprcopygroup -f`.

Pinned by `tests/unit/test_replication_read.py` (SPEC-016 R1/R2/R6) — to be written with SPEC-016.

## `after_apply/` — 2026-10-09 22:07, minutes after the first successful live apply

`showrcopy`, `showrcopy groups`, `showrcopy -d`, `showvvset` and WSAPI `/remotecopygroups` on both
arrays with the tool's two **sync** groups live beside the six old ones: `zz_rc_vvs_rcg` /
`zz_rc_test_rcg` on D22U27 (Primary, Started, Synced, `auto_recover,auto_synchronize`), their
`.r188150` copies on E18U31 (Secondary); WSAPI `role 1`, `mode 1`, `state 3`, `syncStatus 3`,
`volumeLastSyncTime` set, `localVolumeSetName` = the primary set; peer sets `zz_rc_vvs_rc` /
`zz_rc_test_rc` hold the secondaries. No `RCP_<group>` set exists — the WSAPI path does not create
one. Pinned by `test_verify_on_the_live_after_apply_capture_says_replicating_for_both_groups`.

## `after_apply_periodic/` — 2026-10-09 23:39, the first live periodic apply

The same reads on both arrays, plus the harness's `plan.json` / `result.json` / `verify.json`, with
the tool's two **periodic** groups live (`zz_rc_vvs_rcg`, `zz_rc_test_rcg`; period 5m, RPO 10) and
the six Sync groups **Stopped** for the window (`scripts/rc_option1.py stop` on the lab branch; the
six were restarted afterwards and `showrcopy groups` / `showrcopy -d groups` / `showvvset` /
`showvlun` diffed **identical** to the baseline). Facts:

- **The array's one-mode rule counts STARTED groups only:** the periodic start was accepted beside
  six stopped Sync groups (the same start was code 236 with them started, 21:41). The tool still
  refuses to plan that — the stopped groups' restart would be at risk — and says so in its own
  sentence (pinned by `test_stopped_groups_of_the_other_mode_are_still_a_finding_with_the_honest_sentence`).
  Not learned: whether the Sync groups restart beside a started periodic group (they were restarted
  after the periodic groups were removed).
- **The periodic PRIMARY's `showrcopy` row carries spaces in Options:** `Last-Sync 2026-10-09
  23:39:23 IST, Period 5m,auto_recover,over_per_alert,auto_synchronize`; the secondary's row reads
  `Period 5m,auto_recover,over_per_alert,auto_synchronize`. `over_per_alert` is the array's own
  default. Volume rows carry `LastSyncTime 2026-10-09 23:39:23 IST`; `showrcopy -d` adds the resync
  snapshot `Resync_ss rcpy.27.12373.5` and `VV_iter`/`R_iter` `188150/1`. Parsed into `RcGroup.period`
  / `.last_sync` (pinned by `test_a_periodic_group_row_parses_last_sync_and_period_out_of_its_options`).
- Verify: *Replicating · last sync <ts>* for both, links 2/2 each way (pinned by
  `test_verify_on_the_live_periodic_capture_says_replicating_with_the_last_sync_time`). The removal
  set (A then B) was the same shape as for sync and every line was accepted.

## 2026-10-10 — the six groups removed and rebuilt; periodic through the UI (validation record)

Not captured here yet (zip owed: `rc_rebuild/`), facts from the session:

- **Peer Persistence (`active_active`) group removal:** `setrcopygroup pol no_active_active` and
  `removercopygroup -f` are both refused while the secondary volume is exported — *"Please unexport
  the secondary volume so the host only has access to the primary volume and retry."* After
  `removevlun -f <vv> <lun> set:<hostset>` on the peer (answer *"Issuing removevlun …"*) the
  removal goes through. Re-exporting the secondary afterwards needs the host (set) admitted to the
  group first: `admitrcopyhost -proximity {primary|secondary|all} <group> set:<hostset>` (*"Cannot
  export to host which is not admitted to the group"*). The value shows in `showhostset -summary`
  column `RC_host` (`Pri`/`Sec`/`All`); the array keeps a host set `RH<n>_<group>` per admission.
  Proximity should be set on the primary; the secondary accepts it *"to correct inconsistencies"*.
- **`removercopygroup -f` without `-removevv`** on a stopped group: accepted, primary and secondary
  volumes stay; re-admitting them later is a full initial copy (all Synced within minutes here).
- **Single-volume CLI `admitrcopyvv <vv> <group> <target>:<existing secondary>` never answered**
  over `exec_command` (the set form `admitrcopyvv set:<s> <g> <t>:<s>` did); WSAPI
  `addVolumeToRemoteCopyGroup` with the existing `secVolumeName` and no `volumeAutoCreation`
  admitted the same volumes at once.
- **CLI `creatercopygroup` created no `RCP_<group>` set** on OS 10.5.0, although its help says it
  will — `showvvset` was identical before and after the rebuild.
- A 15-minute snapshot schedule on D22U27 (`test999.*` into `set-test999…`) ages snapshots out and
  adds new ones; it shows up in any `showvvset` diff and is not ours.
