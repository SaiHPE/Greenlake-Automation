# Live validation: discovery + zoning, rack13arcus (BGL training lab), 2026-09-12

Second run of the storage steps **driven by the operator in the shipped application UI**
(v0.16.0-rc.5, `f404ece`) against real hardware. Purpose: retest discovery, zoning and provisioning
after the 2026-08-31 fixes, on an array that has since been rebuilt by the training team.

**Outcome so far: discovery and the zoning *read/design* side are correct on every check against
raw output. One design defect (the zoning host list) and seven UX findings. Provisioning, verify
and as-built were not reached in this session.** The defect is closed in code (this commit) and the
UI redesigned — both **pending a live run**.

## Environment

| | |
|---|---|
| Array | Alletra MP B10000 `rack13arcus`, `10.132.30.121`, serial CZ2D2K014S, OS **10.5.55**, user `3paradm` |
| CPG | `SSD_r6`, 302 400 MiB free |
| Fabric F1 | `10.132.30.111` `SAN6700R13U38`, fabric `Training_Lab_Rack12` (2 switches; ISL to `SN6000B-SANB-ZR07U40` 10.132.30.11), active cfg `mycfg`, **no aliases**, zones written in raw WWPNs |
| Fabric F2 | `10.132.30.112` `SAN6700R13U40`, fabric `Training_Lab_Rack11` (2 switches; ISL to `SAN1624ZR12U40` 10.132.30.62), active cfg `jul2prabhu`, 13 zones, shared with a Primera |
| vCenter | `10.132.26.124` — hosts `.136`, `.47`, `.86` |
| Windows host | `10.132.30.137`, QLogic `51:40:2e:c0:20:89:cc:1c` (F2, zoned) + `…cc:1e` (F1, **unzoned**) |
| Mode | Provision storage only; sheet `Initialisation_sheet_rack13arcus_2026-09-12.xlsx` (Hosts tab: `zz_t2_declared` fake WWPN, `arcus-win137` both WWPNs) |
| Baselines | `script-logs/rack13_precheck_20260912_152028.utf8.txt`, `script-logs/rack13_nscam_20260912_172824.txt` (fixtures cut into `tests/fixtures/rack13_fabric/`) |

**Cross-cabled again**: F1 carries `0:3:4` + `1:3:3`, F2 carries `0:3:3` + `1:3:4`. Array ports now
also register **NPIV FC-NVMe shadow targets** (`20:34:01:02:ad:f2:d4:95`…). `showport -rcip`
returns "There is no specified port information".

**Cleanup from 2026-08-31**: nothing left. `zz_test_vol01`, `zz_test_hs`, host `10.132.30.136` and
the zone `zz_test_h86_zz_test_a0303` are all gone (array rebuilt; switch config reset by the
training team). The disclosure to the SAN team remains a conversation, not a config change.

## What was driven, and what the hardware said

### Discovery — correct on every line

| Item | Ground truth | Discovery |
|---|---|---|
| Ready ports + fabric | F1 `0:3:4`,`1:3:3`; F2 `0:3:3`,`1:3:4` | ✅ identical, switch named per port |
| loss_sync ports | `0:3:1/2`, `1:3:1/2` | ✅ listed, "require a cable or switch-port check", not zoning candidates |
| NPIV shadows | present in both NS | ✅ none leaked as hosts |
| `showport -rcip` no-info | — | ✅ handled; 4 peer ports shown unconfigured |
| `.136` | `…12A8`→F2, `…12A9`→F1 | ✅ both fabrics, vCenter-joined, OS read |
| `.47`, `.86` | none of 4 WWPNs in either fabric-wide NS | ✅ "Not logged in" |
| Unclaimed logins | 6 in `showhost -d` | ✅ all 6 kept, incl. `…12A9` on F1 ports |
| `vmenode` | existing FC host | ✅ existing |
| iSCSI hosts | 11 | ✅ 11, IPs from `showhost -d`, three "Not logged in" |
| Names free | 3 vols + vvset + hostset | ✅ 5 |

Not visible in the UI: the three parity/cabling notes the code computes (both switches at the same
card-port parity; `0:3:4` and `0:3:3` mismatches). Not yet confirmed whether they render anywhere.

### Zoning — read and design correct; host list wrong

| Check | Result |
|---|---|
| `.136` pre-ticked `0:3:4`,`1:3:3` (F1) and `0:3:3`,`1:3:4` (F2) | ✅ matches `kiranzone1` and the array logins |
| `.86 cc:38` offered `0:3:3`,`1:3:4` on F2 only | ✅ — `nscamshow` confirms it on remote switch `SAN1624ZR12U40` port 0 (`Physical Initiator`, SN1610Q) |
| `.47` ×2, `.86 cc:3a` Offline | ✅ in neither fabric-wide NS |
| Command set for `.86` (operator aliases `arcus_esx86-hba1`, `rack13arcus_N0S3P3`, `rack13arcus_N1S3P4`) | ✅ 3 `alicreate`, 2 SIST `zonecreate`, `cfgadd "jul2prabhu",…`, `cfgenable` separate, nothing for F1 |
| Switch state after the step | not yet snapshotted — **owed** |

The command set was **not applied**: `.86` sits on the training team's remote switch and `cfgenable
jul2prabhu` touches their zones.

## Defects found

**1. Hosts not in vCenter never reach the zoning plan (design).** `build_zoning_plan` used
`discovery.host_hbas` (vCenter) and fell back to the switches' local NS only when that was empty;
declared (Hosts-tab) hosts were never read. Live consequence: `cc:1e` (Windows `.137`, F1, unzoned),
`10:00:5c:ed:8c:53:12:a3` / `…12:a2` (Linux `localhost.localdomain`, one HBA per fabric, unzoned on
both) were absent from the step. The customer-shaped test — zone an unzoned Windows/Linux host — was
blocked. **Closed in code**: the host list is the union of vCenter, sheet, array logins and local NS,
each row tagged with its source (LESSONS 33). Pinned to the captures by
`test_rack13_zoning_candidates_are_the_union_of_every_source`. **Pending live run.**

**2. Alias names not validated.** `arcus_esx86-hba1` accepted; `-` is FOS 8.1.0+-only. Closed:
`render_commands` skips names FOS rejects (with the character named); `/zoning/render` returns
portability warnings; the UI validates inline.

**3. A globally incomplete zoning report hid Continue even when one host passed the per-host gate.**
The backend correctly returned one `zoned_hosts` entry and the activity log said that host could be
provisioned, but `ZoningStep.tsx` rendered Continue only when `report.proper` (every host) was true.
This contradicted ADR 0012 and the footer's per-host rule, trapping the operator on this screen.
**Closed in v0.16.0-rc.7:** the frontend consumes `zoned_hosts`, shows exactly which hosts can
proceed, and renders **Continue with N zoned hosts** whenever `N > 0`; other hosts remain excluded
by name. Frontend type-check/build passed; pending live run.

## UX findings (all closed in the redesign, pending live run)

Z1 nothing labelled (switch read as a host; IP not marked as host; WWPN not marked as HBA port) ·
Z2 "(zoned)" without *to whom* or *by which zone* · Z3 alias boxes for hosts needing nothing ·
Z4 no legend · Z6 current zoning and design mixed in one view · Z7 no visible re-check loop ·
Z9 no hint that `.86` sits on a remote switch · Z10 WWPNs without decode. Plan and rationale:
[docs/ux/ZONING-REDESIGN.md](../ux/ZONING-REDESIGN.md). LESSONS 34.

## Findings from the switches worth keeping

- F2's `arcus__windows137_zone1` contains `cc:1e`, which lives on F1 — a dead member. The plan
  correctly derives "zoned" from array logins, so it did not mislead.
- The Linux host `localhost.localdomain` (Emulex SN1720E2P, `12:a2` on F2 port 11, `12:a3` on F1
  port 11, both unzoned) is the ideal greenfield candidate for the next run: two fabrics, no zones,
  named by the NS, no vCenter.
- F1 holds `rcfc1`/`rcfc2` zones pairing this array's `0:3:4`/`1:3:3` with a Primera's RCFC ports.

## Owed

- **Post-step switch snapshot** (`cfgshow`, `cfgtransshow` on both) to close the "never writes"
  check for this run.
- **Apply one tool-generated command set and watch the login appear** — the single most important
  untested link. Candidate: `localhost.localdomain` on F1 (`mycfg`, the training team's own switch,
  no aliases to collide with), or `cc:1e` for `.137`. Needs the fixed build.
- **Provisioning, path verify, verify, as-built** on this array (Phases 5–6 of the plan).
- Confirm the parity notes render somewhere in Discovery.
- Re-test the partial-host Continue gate in v0.16.0-rc.7, then complete provisioning.
