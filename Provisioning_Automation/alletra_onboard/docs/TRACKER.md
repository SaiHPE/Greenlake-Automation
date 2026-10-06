# Pending work tracker

The ONE list of open items. `SCOPE.md` says where each of the nine areas stands; this file says what is
left, who has it, and what blocks it. The status workbook (`alletra mp init and prov status-updated.xlsx`)
is the management view — its row is in the **Sheet** column.

Rules:
- Every open item has an ID here. New work gets a new ID before it starts.
- Close an item in the same commit that finishes it: move it to *Closed* with the date and the evidence
  (commit, validation file, report). Never delete a row.
- "Done" means run live, not only tests passing (LESSONS). Built-but-not-run stays under *Test live*.

Status: `todo` · `doing` · `blocked` · `done`

## Next up (in order)

| ID | Item | Owner | Status | Sheet | Next step / notes |
|---|---|---|---|---|---|
| BL-06 | Status workbook refresh | dev | todo | — | After each closed item. |
| BL-07 | Dependabot: 4 alerts on github.com/SaiHPE/Greenlake-Automation | dev | todo | — | Bump, full test run, push both remotes. |
| BL-31 | Discovery's fabric probe is slow on a large fabric: D22U27 (CRV) took ~42 s per ready FC port (`showportdev fcfabric`), 4½ min for 6 ports, although `_FCFABRIC_TIMEOUT` is 30 s | dev | todo | B.5 | Seen 2026-10-05. Check why the per-probe timeout is not honoured; consider probing once per switch, or in parallel. |
| BL-32 | Provisioning gate table lists FC hosts only: an iSCSI host that passes (ESX1-iscsi, 2026-10-05) appears only in Check notes | dev | todo | B.6 | Add a row *iSCSI — no zoning needed* per logged-in iSCSI host. |
| BL-35 | `session.ps1` cleanup: the array reset the ssh connection after the password, before the CLI prompt (`ssh_dispatch_run_fatal … Unknown error`) — 2026-10-06 and very likely 09-28, which left `zz_s6_*` behind | dev | doing | B.9 | Evidence 10-06: the saved transcript is that one line — no *Permission denied*, no `cli%`, so nothing ran. Not reproducible by hand (`< file`, `type |`, `| Out-String`, `> file` all worked with `showversion`). Runner now: ssh output to a file, one retry when the connection drops before `cli%`, loud failure otherwise. Built — pending the next `session.cmd` run. |

## Test live (built, not yet run on hardware)

| ID | Item | Owner | Status | Sheet | Blocked by |
|---|---|---|---|---|---|

## Build (not started or partial)

| ID | Item | Area | Status | Sheet | Notes |
|---|---|---|---|---|---|
| BL-20 | Replication (Remote Copy) | 5 | todo | Replication B.1 | Research done: `docs/research/2026-09-19-replication-two-arrays.md` — decisions listed there are needed before a spec. Lab pair offered 2026-10-05: AlletraMP_D22U27 (10.64.122.99; RCIP 0:4:3/1:4:3 on 10.54.122.92/.93) and AlletraMP_E18U31 (10.64.154.190, CZ2D3209YV, OS 10.5.0; RCIP 10.54.154.192/.193; existing group `rcopy_async_test` with failed reverse tasks, no quorum witness). Both reachable from labrat; ESX1/ESX2 are zoned to both. |
| BL-21 | Snapshots + schedules | 5 | todo | — | DSCC protection policies, or `createsv` / `createsched`. |
| BL-22 | HLD document | 9 | todo | — | |
| BL-23 | LLD document | 9 | todo | — | |
| BL-24 | Health / performance reporting (DSCC, Data Ops Manager, InfoSight) | 8 | todo | — | |
| BL-25 | VLAN configuration (read-only today) | 3 | todo | — | |
| BL-26 | Peer-port configuration (read-only today) | 3 | todo | — | |
| BL-27 | Migration: source-array discovery, peer setup and zoning | 2, 3 | todo | — | |
| BL-28 | Alletra MP Unified File | 6 | todo | — | Research first. |
| BL-29 | GreenLake for File (GL4F) | 7 | todo | — | Research first; gated on file API entitlements. |
| BL-30 | Tool approved as tenets | — | todo | B.11 | Management. |

## Closed

| ID | Item | Closed | Evidence |
|---|---|---|---|
| BL-02 | Docs catch-up: SCOPE (init, zoning, as-built live), SPEC-010 §5 and SPEC-014 addenda, LESSONS 41–42, validation record, project instructions | 2026-09-29 | [validation/2026-09-29-rack13arcus-live-test-3.md](validation/2026-09-29-rack13arcus-live-test-3.md). |
| BL-03 | Initialization run recorded | 2026-09-29 | Operator-confirmed run from scratch on a factory-fresh array; SCOPE area 1 marked live-verified. |
| BL-10 | Linux host read over SSH, through the app's Discovery (SPEC-014 R4) | 2026-10-05 | labrat RDP (GBGSAIROOP), app from `jumpbox-test`, sheet `D22U27_linux_discovery.xlsx` (array 10.64.122.99): *Hosts in this run — Linux (1)*: `linux-test` 10.54.159.49, *sheet host read from the server over SSH*, RHEL 8.9 (Ootpa), IQN `iqn.1994-05.com.redhat:6e35c4a016a0` (not logged in — D22U27 has no iSCSI target ports), serial *not reported* (login `sai`, not root). Root password login refused; serial + multipath need root or passwordless sudo — optional follow-up. |
| BL-05 | Canned demo: discovery → SAN zoning → provisioning → as-built | 2026-10-06 | Recorded on rack13 from the packaged **v0.16.1** `AlletraOnboard.exe` (Training RDP), sheet `Demo_rack13_canned.xlsx` (ESXi `.136` from vCenter + Windows `ELJR0NB1UV` over WinRM): discovery, zoning check, zoning plan (missing F1 zone for ELJR0NB1UV designed, name check, command set), plan → create `zz_demo_*` → removal set, Verify paths *Live* + ESXi *Rescan needed → Visible* after a vSphere rescan, verify, as-built. Edited 6:02 cut (credentials, vCenter URL/inventory/user blurred; loading cut). Objects removed with the removal set. |
| — | Release v0.16.1 (exe) | 2026-10-06 | Tag `v0.16.1` (5c9385a1): github.com Actions built and smoke-tested slim, offline and init-only exe zips; same assets + `session.ps1/.cmd` on github.hpe.com (SHA256 verified). |
| BL-33 | rack13 regression run + as-built page review (S-8) | 2026-10-06 | Training RDP, `session-20261006-111739`: **57 PASS** — every app assertion (create, rerun P-21, conflict refused, blank members, verify, as-built, credential masking, zoning render, paths *Live · 4 paths/LUN · both fabrics*, ESXi *absent* before rescan); 3 FAIL all from the runner's SSH cleanup (BL-35), cleaned by hand. Leftover `zz_s6_*` from 09-28 removed first. As-built reviewed: hosts, volumes (vol01 tpvv / vol02 tdvv), presentations *4 on 10.132.30.136*, zoning, run, removal set and path verification all match; one defect — table label *NVMe SSD Disks (15.36 TB)* over *12 x 1.92 TB* — fixed (label drops the template's sample size). |
| BL-34 | Verify paths counts iSCSI paths | 2026-10-05 | labrat, E18U31 run `3d413ddc` (3a82d87a): `ESX1-iscsi` **Live** *1 LUN(s) · 1 initiator(s) · 4 path(s) per LUN · iSCSI on 0:4:1, 0:4:2, 1:4:1, 1:4:2 · both nodes*; ESXi view n/a (host not in the LZ vCenter). Removal set pasted: `showvv zz_is*` / `showhostset zz_is*` empty, ESX1-iscsi intact. |
| BL-11 | iSCSI export (S-9) | 2026-10-05 | labrat, AlletraMP_E18U31, run `68149459` (`E18U31_iscsi_test.xlsx`): zoning check *ESX1-iscsi: iSCSI, logged in on 0:4:1, 0:4:2, 1:4:1, 1:4:2 — no zoning needed; exports allowed*; plan 3 create / 1 exists (ESX1-iscsi, untouched) / 0 conflicts; created `zz_is_hs`, `zz_is_vol01` (id 1750, 10 GiB tpvv SSD_r6), export LUN 0 → set:zz_is_hs; `showvlun -a -host ESX1-iscsi`: `zz_is_vol01` active/nonopt on 0:4:x and 1:4:x; removal set pasted, objects gone, ESX1-iscsi intact. Verify paths read *No path* (IQN rows were dropped) — fixed: iSCSI paths counted, redundancy judged by controller node; to re-see live. |
| BL-13 | Vault Zone end to end (T-0006); Landing Zone dropped | 2026-10-05 | From the labrat RDP: VZ read-only (discovery, zoning plan: 12 pairs already zoned, verify, as-built) and VZ writes, run `be21f8f0`: plan 6 create / 1 exists / 0 conflicts; created `zz_vz_vol01/02` (ids 9088/9089), `zz_vz_vvs`, `zz_vz_hs` [CRV_VZ_DL360G11D24U25], exports at LUN 0/2; Verify paths *Live, 2 LUNs · 2 HBAs · 4 paths/LUN · both fabrics*; removal set pasted, objects gone. The ESXi view wrongly read *not an ESXi host* with vCenter unreachable — fixed to *not read*. LZ: array unreachable, environment considered dead by the operator. |
| BL-12 | ESXi shows the volume *Visible* after a rescan (SPEC-013) | 2026-10-05 | rack13 run `0443e340` (`Demo_rack13_ready.xlsx`): 2 × 10 GiB exported to `zz_demo_hs` (.136) at LUN 2/3; Verify paths → Array *Live, 2 LUNs · 2 HBAs · 4 paths/LUN · both fabrics*, ESXi *Rescan needed — sees 0 of 2*; vSphere Rescan Storage on .136; Verify paths → ESXi **Visible** *2 volume(s) · 2 active of 4 path(s) per LUN · vmhba3, vmhba4* (ALUA: active-optimised on the owning node). |
| BL-09 | Names panel flags clashing alias/zone names before *Generate* | 2026-09-29 | 11ff0e1; rack13 screenshots: `CZ2D2K014S_N1S3P3` on a host port → red "Already on the switch for another device", Generate disabled; `host_cc1e_hba1` on two ports → both red "Same name as …", Generate disabled; corrected name → Valid, enabled. Zone-name cases live 2026-10-05 (T-0019): `rack13` + `F1_cfg` → red "zone rack13_F1_cfg already exists on the switch" (the F1 cfg name); a 50-character host alias → alias Valid, red "… is 68 characters — FOS allows 64"; Generate disabled both times. |
| BL-08 | Installer-default host names (`localhost…`, `smartstart`, `ubuntu[-server]`) are not identities | 2026-09-29 | c199a29; rack13 rebuilt plan: `10:00:5c:ed:8c:53:12:a3/a2` shown by WWPN, alias `host_12a3_hba1`. |
| BL-04 | Zoning name checks live: alias already on the switch for another device; same new alias for two ports | 2026-09-29 | a0cbb04; rack13 screenshots: `CZ2D2K014S_N1S3P3` on a host port → Not included, no zonecreate; `host_cc1e_hba1` twice → first pair rendered, second Not included. (Zone-name cases seen live before the click — see BL-09.) |
| BL-01 | Zoning starts with nothing ticked; the operator ticks every pair (decision 2026-09-29) | 2026-09-29 | 0a71a96; rack13 screenshots 12:50 — new panel text, operator's own two ticks, "Generate command set (2 new zones)". |
| — | Discovery (ESXi via vCenter, array, Windows over WinRM, sheet lookups), provisioning FC, verify, as-built | 2026-09-28 | rack13: session.ps1 60/60 (09-19), 59/1 with the 1 an ssh typo (09-28, fixed dde5ed5); spec014.ps1 40/0/2. |
| — | Tool-designed zone logs a host in (G-1) | 2026-09-17 | rack13. |
| — | Host-join / zoning bug sweeps (persona, OS, iSCSI host on array, alias and zone-name clashes, zone length, volume size) | 2026-09-28 | e083406, 486dfa8, ffdf900, a0cbb04. |
