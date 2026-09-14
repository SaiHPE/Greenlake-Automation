# Live validation: discovery + zoning, rack13arcus (BGL training lab), 2026-09-12

Second run of the storage steps **driven by the operator in the shipped application UI**
(v0.16.0-rc.5, `f404ece`) against real hardware. Purpose: retest discovery, zoning and provisioning
after the 2026-08-31 fixes, on an array that has since been rebuilt by the training team.

**Outcome: discovery and the zoning *read/design* side are correct on every check against raw
output. Provisioning was driven end to end through the UI (v0.16.0-rc.7) twice; the array's own
event log confirms every object and every command. One zoning design defect (the host list) and
seven UX findings, closed in rc.6/rc.7 and confirmed live. Open: the plan's export rows carry no
existence check (defect 4), the provisioning host list is vCenter-only (defect 5), and the UX
register in `docs/ux/FINDINGS-2026-09-13.md`. Verify and as-built reached; documents not yet
reviewed.**

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

### Provisioning — driven through the UI on v0.16.0-rc.7 (2026-09-13 00:01)

Operator composed: host set `zz_t2_hs` = `10.132.30.136` only; exports `zz_t2_vvs` → `zz_t2_hs`
and `zz_t2_vol03` → `10.132.30.136`, LUN auto. Plan showed 8 creates (host persona VMware, three
volumes on `SSD_r6` with `vol03` taking the sheet defaults, no held-back note, no rows for `.47`,
`.86` or `vmenode`). Apply: 8 × "Created" in 3 s. Path verify: `.136` Live, 2 HBAs on both fabrics;
nothing said about hosts not exported to. Array afterwards
(`script-logs/rack13_postprov_20260913_000725.utf8.txt`):

| Object | Array says | Verdict |
|---|---|---|
| host `10.132.30.136` | id 11, persona VMware, `…12A8` on `0:3:3`/`1:3:4`, `…12A9` on `0:3:4`/`1:3:3`; both WWPNs **gone from the unclaimed block** | ✅ |
| `zz_t2_vol01/02/03` | tpvv / **tdvv** (reduce) / tpvv, all `SSD_r6`, normal, 1/1/2 GiB | ✅ |
| host set `zz_t2_hs` | id 30, member `10.132.30.136` | ✅ |
| VLUNs | LUN 0 `vol01`, LUN 1 `vol02` (type *host set*), LUN 2 `vol03` (type *host*); each on all four ports, 12 rows, active/nonopt split by owning node | ✅ |
| **VV-set `zz_t2_vvs`** | run 1 post-check: absent — **hand-deleted by the operator before the check** (see defect 4). Run 2, polled live: `33 zz_t2_vvs` with `vol01`, `vol02`, present for the whole window; event log shows `createvvset` and `createvlun set:zz_t2_vvs 0 set:zz_t2_hs` | ✅ |
| `vmenode`, `SSD_r6`, both switches | unchanged; `cfgtransshow` clean, `mycfg` / `jul2prabhu` effective, no `zz_` alias or zone | ✅ |

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

**4. Export rows in the plan never carry an existence check (open) — and a withdrawn claim.**
First written here as "the VV-set was reported Created and does not exist". **Withdrawn**: the
operator had run the manual cleanup (including `removevvset -f zz_t2_vvs`) before the post-check
script ran, so the script photographed a hand-deleted set. The run was repeated at 00:41 with the
array polled every 2 s from before the click and its event log read afterwards
(`script-logs/rack13_applywatch_20260913_004156.utf8.txt`, `rack13_events_20260913_004647.utf8.txt`):

```
createhost -persona 11 10.132.30.136 10005CED8C5312A8 10005CED8C5312A9
createhostset zz_t2_hs 10.132.30.136
createtpvv -usrboundary SSD_r6 zz_t2_vol01 1024
createtpvv -reduce -usrboundary SSD_r6 zz_t2_vol02 1024
createtpvv -usrboundary SSD_r6 zz_t2_vol03 2048
createvvset zz_t2_vvs zz_t2_vol01 zz_t2_vol02          -> Object Set 33 added
createvlun set:zz_t2_vvs 0 set:zz_t2_hs                 -> VLUNs 574-581 added
```

Every command is the one a consultant would type. `showvlun -t` lists a set-source export as one
template per member volume with the host set as target — the training team's own `Vol1.x →
set:grp3_alletra` rows look identical — so the "two per-volume templates" reading was a
misreading of the array's display, not evidence of a wrong request. **LESSONS: the array's event
log (`showeventlog -oneline`) is the authority on what was requested; `show*` tables are the
authority on what exists now; neither is a substitute for the other.**

What *is* wrong: `build_plan` sets `exists` on host / hostset / volume / vvset rows but never on
`vlun` rows, and the WSAPI client has no VLUN read. On Rebuild plan after a successful apply the two
export rows read *Create* while LUNs 0/1/2 existed on the array, and the summary said "to create".
Apply is safe only because the array answers a duplicate with a conflict that `ensure_vlun` maps to
"exists". The plan is the operator's approval document and must be true. Fix: a VLUN read, `exists`
on export rows, and a read-back after create. Full register: `docs/ux/FINDINGS-2026-09-13.md`.

**5. Provisioning host list is vCenter-only (design, same shape as defect 1).** `_hosts_by_name`
and `_persona_by_host` read `discovery.host_hbas`; the Compose dropdown therefore offered `.136`,
`.47`, `.86` and not `arcus-win137` (sheet) or `localhost.localdomain` (fabric NS), both of which
the zoning step now lists. The union rule applied to zoning in rc.6 has to reach provisioning too.

**6. Compose card resets to "Load objects" after apply (UX).** The saved membership and export
rows were used (the Result table proves it) but are no longer displayed; an operator clicking
Rebuild plan sees an empty card and cannot tell whether the composition survived.

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

- **Defect 4**: VLUN read + `exists` on export rows + read-back after create; re-run Rebuild plan
  and see every row *Exists*.
- **Defect 5**: provisioning host list = the zoning union.
- **Verify + As-built documents** reviewed (as-built shows the set export?), then the array cleanup
  (`removevlun` × 3 → `removevvset -f zz_t2_vvs` → `removevv` × 3 → `removehostset zz_t2_hs` →
  `removehost 10.132.30.136`).
- **Apply one tool-generated command set and watch the login appear** — the single most important
  untested link. Candidate: `localhost.localdomain` on F1 (`mycfg`, the training team's own switch,
  no aliases to collide with). Needs the training team's nod for `cfgenable mycfg`.
- Confirm the parity notes render somewhere in Discovery (finding D-1).
- Optional, for the record: `showeventlog -min 90 -oneline -msg zz_t2` to show run 1's
  `createvvset` at 00:01 and the manual `removevvset` after it.

## Second session — S-1 and S-2 setup (2026-09-13 evening, v0.16.0-rc.9)

Operator ran from the rc.9 `.exe`; same sheet as run 2, unchanged (blank *Members* on `zz_t2_hs`,
no composed exports). Provision only.

**S-1 — Build plan with `zz_t2_*` present.** Screenshot kept. What SPEC-001 promised held on every
row it could judge: `zz_t2_vol01/02/03` *Exists · 1 GiB tpvv on SSD_r6 — matches* (and `2 GiB` for
vol03, `reduce` for vol02); `zz_t2_vvs` *Exists · has all 2 volume(s)*; the two set exports *Exists ·
already exported at LUN 0 / LUN 1*; host `.136` *Exists · carries all 2 WWN(s)*. Summary line
*5 to create · 1 to update · 18 already exist · 0 conflicts*.

The five creates and the one update were the blank-members default meeting the SPEC-003 union:
`.47`, `.86`, `arcus-win137`, `zz_t2_declared` to be created; `zz_t2_hs` to gain **15 members** —
those four plus `vmenode`, `grp3_vmenode1-3` and seven `HPE_VM_*` (all other teams' iSCSI hosts).
`zz_t2_vol03 → set:zz_t2_hs` was planned *Create* although run 2 had presented it directly to `.136`
at LUN 2. Not applied. Findings P-13, P-14, P-16 → SPEC-005, rc.10. LESSONS 36.

**S-2 setup.** `createvv -tpvv SSD_r6 zz_t3_vol01 10g` → id 101; `showvv -showcols
Id,Name,Prov,Type,CPG,VSize_MB zz_t3_vol01` printed the table with a `CPG` column — the corrected
C-1 command works on OS 10.5.55 (fixture `showvv_showcols_cpg.txt`). S-2 plan itself: next, on rc.10.

Array state at the end of this sitting: run-2 objects present; **plus `zz_t3_vol01` (10 GiB, id
101, unexported)**. Cleanup list now includes `removevv -f zz_t3_vol01`.

## S-1 passed — 2026-09-14 11:29, v0.16.0-rc.10

Second attempt. The sheet's *Members* cell had been filled (`10.132.30.136`) but rc.10 dropped the
column (P-17: header matched on the full hint text, which rc.10 had reworded) — the Compose card
showed *choose members* and the plan blocked on *zz_t2_hs has no members*, exactly as SPEC-005 R1
says it must. The operator picked the member in the dropdown, composed the two run-2 exports
(`zz_t2_vvs → zz_t2_hs` auto; `zz_t2_vol03 → host 10.132.30.136` LUN 2; a first try typed `z` for
the LUN and the plan read it as auto — P-18) and rebuilt:

**0 to create · 0 to update · 8 already exist · 0 conflicts.** Every row *Exists* with its reason
— host *carries all 2 WWN(s)*, set *has all 1 host(s)*, volumes *matches* (1 GiB tpvv / 1 GiB reduce /
2 GiB tpvv on SSD_r6), VV-set *has all 2 volume(s)*, exports *already exported at LUN 0, LUN 1* and
*at LUN 2*. SPEC-001 R1–R5 confirmed on hardware. Both live findings fixed in rc.11.

## S-2 passed — 2026-09-14 12:04, v0.16.0-rc.10

`zz_t3_vol01` exists on the array at 10 GiB (created by hand for this test). Sheet row at **20 GiB**
→ the row is red *Conflict · on the array: 10 GiB tpvv on SSD_r6 · intent: 20 GiB tpvv on SSD_r6*,
the banner reads *1 conflict — the plan cannot be applied*, the authorisation checkbox is disabled.
Sheet row changed to **10 GiB** → *Exists · 10 GiB tpvv on SSD_r6 — matches*, 0 conflicts. Every
other row unchanged and *Exists*. SPEC-001 R2 (attributes, not names) and R6 (conflicts block
apply) confirmed on hardware. Also observed: with one export composed, `zz_t2_vol03` has no export
row at all and nothing says so — P-19 (UX).

## S-4 — 2026-09-14 12:35–12:47, v0.16.0-rc.10: passed, and found P-21

Sheet: `zz_t3_vol01` (10 GiB, VV-set `zz_t3_vvs`), `zz_t3_vol02` (2 GiB, same set), host sets `zz_t3_hs`
(`.136`, `.86`) and `zz_t3_win` (`arcus-win137`), plus the run-2 objects. Members picked in Compose
(rc.10 dropped the sheet column — P-17). Exports composed: `zz_t2_vvs → zz_t2_hs`, `zz_t3_vvs → zz_t3_hs`.

**Dropdown** listed every host with its source — `.47/.136/.86 … from vCenter`, `arcus-win137 … from
the sheet`, `vmenode — 1 HBAs - one fabric (even) · on the array`, then the eleven iSCSI-only hosts
labelled *iSCSI only · on the array · not zoned or path-verified by this tool*. SPEC-003 live.

**Plan**: 7 to create · 0 to update · 8 already exist · 0 conflicts. `.86` and `arcus-win137` *Create*
(VMware / WindowsServer); the plan also said *Host 'win-10-132-30-137' names only initiators that
already belong to another host (arcus-win137) — not planned* — a second Hosts-tab row with the same
WWPNs, dropped with its owner named (SPEC-003 R1).

**Apply**: 8 created · 7 existed. Seven creates exactly as planned; `zz_t3_vvs → zz_t3_hs` at
LUN 5, 6. **The eighth was wrong**: `zz_t2_vvs → zz_t2_hs`, which the plan had called *Exists · LUN 0,
LUN 1*, came back *Created · LUN 3, LUN 4*. `showvlun -t` at 12:47 showed 24 templates with
`zz_t2_vol01` at LUN 0 and 3, `zz_t2_vol02` at LUN 1 and 4; the event log showed two `createvlun`
commands from the tool at 12:39:57. Cause: apply never read the exports before creating them and
`createvlun … auto` never conflicts. Removed by hand (`removevlun -f zz_t2_vol01 3 set:zz_t2_hs`,
`… zz_t2_vol02 4 …`); 22 templates after, each volume once. Fixture `showvlun_t_duplicate.txt`.
P-21 → SPEC-001 R11, rc.12. LESSONS 37.

**Path verification**: `.136` *Live · 6 LUN(s) · 2 HBA(s) · 4 path(s) per LUN · both fabrics
(SAN6700R13U40, SAN6700R13U38)* — the 6 (for 4 volumes) is the duplicate showing through; `.86` *No
path · 0 live paths for 2 exported volume(s) — the host is off or not zoned*; `arcus-win137` *No path ·
nothing is exported to this host*. SPEC-004 R5 live.

Array state now: run-2 objects; `zz_t3_vol01`, `zz_t3_vol02`, `zz_t3_vvs`, `zz_t3_hs` (`.136`, `.86`),
`zz_t3_win` (`arcus-win137`), hosts `10.132.30.86` and `arcus-win137`; `zz_t3_vvs → set:zz_t3_hs` at
LUN 5/6. All to be removed at the end of the session.

## S-8 passed — 2026-09-14 12:59, v0.16.0-rc.10

Verify: configuration matches. As-built generated (782 KB, 28 pages) and checked against `showhost -d`,
`showhostset`, `showvv`, `showvv -showcols …CPG…`, `showvvset`, `showvlun -t`, `showvlun -a` captured
at 13:02. Every array section agrees with the array: the three run hosts with personas, initiators,
ports and set membership; unclaimed logins now 3 WWPNs + 2 IQNs (`51402EC02089CC1C` moved into
`arcus-win137`); five `zz_*` volumes with CPG `SSD_r6` (the corrected C-1 read works in the document);
22 templates, the five `zz_*` ones each *4 on 10.132.30.136*. The run sections record the apply as it
happened — including `zz_t2_vvs Created · LUN 3, LUN 4`, which is P-21 written down by the tool itself.

Three findings from the document: **Z-B** — `arcus-win137` is in the Hosts table, logged in on F2, but
was absent from the zoning gate table on screen: the check's expected list was vCenter-only, so a
sheet or fabric host could never pass the gate (fixed rc.13 — the check uses the provisioning union).
**A-3** — the zoning section said *This run did not include the SAN zoning step* when the check had
run and only the plan had not (fixed rc.13). **A-5** — compression column showed `v2` (fixed).

## Cleanup — 2026-09-14 13:11 — array as found

Fourteen removals by pasted script (`removevlun` × 5, `removevvset` × 2, `removevv` × 5 in one line,
`removehostset` × 3, `removehost` × 3), all accepted, no complaint. Proof lines: `showvlun -t` **17
total** (the count on 2026-09-12 before anything was created), `showhost -d` 35 rows, `showvv` 51,
`showvvset` 9, `showhostset` 5 — and no `zz_*`, `arcus-win137`, `10.132.30.86` or `10.132.30.136` in
any table. Two sessions' worth of objects gone; the training team's objects untouched throughout.

## Second session — summary

| Test | Result | Proved | Found |
|---|---|---|---|
| S-1 | passed (rc.10, 2nd attempt) | SPEC-001 R1–R5 | P-13, P-14, P-16 (rc.9); P-17, P-18 (rc.10) |
| S-2 | passed | SPEC-001 R2, R6 | P-19 |
| S-4 | passed with one defect | SPEC-003; SPEC-004 R4, R5; SPEC-005 wording | **P-21**, P-20 |
| S-8 | passed | SPEC-002 all five sections | Z-B, A-3, A-5 |
| S-11 | passed | SPEC-004 R1–R3 | — |
| S-10 | done by hand | — | G-5 stays open |
| S-12 | 27 PASS / 4 FAIL (rc.14 exe, rc.15 runner) | SPEC-001 R1–R6, R11; SPEC-005; SPEC-004 R4/R5 — by machine | **SPEC-007 R3** (unsorted list); three runner faults → rc.16 |

Not run: S-3 (failure paths), S-5 (reload/resume), S-6 (same sheet twice), S-7 (G-1 zoning apply),
S-9 (iSCSI). Releases during the session: rc.10 (SPEC-005), rc.11 (P-17/P-18), rc.12 (P-21 / R11),
rc.13 (Z-B / A-3 / A-5). Every fix carries a test pinned to the evidence the session produced.

## S-12 — 2026-09-14 14:16–14:24, v0.16.0-rc.14 exe + rc.15 `session.ps1`: the runner's first run

`.\session.ps1 -BaseSheet Initialisation_sheet_rack13arcus_2026-09-12-rc10-test.xlsx` — the whole
provisioning session, no clicks, 8 minutes. **27 PASS, 4 FAIL** (`script-logs/report.md`; the
evidence folder is owed). Baseline: 11 hosts, 5 host sets, 51 volumes, 9 VV sets, 79 VLUN rows
(19 templates). Host picked: `10.132.30.136` (vCenter, both fabrics, in `zoned_hosts`).

What passed, and therefore is now **live-proven by machine**: SPEC-001 R1–R6 and R11 (rerun: every
row `exists`, template count 19 → 19, removal set empty); SPEC-005 (blank members → blocker naming
the set, no host / VLUN rows); the size conflict → `conflict` + blocker + `POST /storage/apply`
refused with 409 and the array untouched; apply created 6 == planned 6, read-back `LUN 0, LUN 1 →
set:zz_s6_hs`, WSAPI showed exactly the two new templates; path verification `live`, 2 LUNs, 4 paths
per LUN on both switches (SPEC-004 R4/R5).

The four FAILs, sorted by whose they were:

| # | FAIL | Whose | Fix |
|---|---|---|---|
| 1 | *plan: host row 10.132.30.136 is 'exists'* — it was `create` | **runner assumption.** S-10's cleanup had removed the host; the plan was right. | rc.16: expectation comes from the WSAPI baseline (`exists` if the host is there, else `create`); removal count 6 or 7 accordingly. |
| 2 | *removal set: 6 lines in dependency order* — 7 lines, and the order was vlun, vlun, **host, hostset, vv, vv, vvset** | **app defect (SPEC-007 R3).** `removal_set()` returned outcome order; only the UI and the as-built sorted. The runner pasted the raw list — host before its set, volumes before their VV set. | rc.16: the list is sorted at the source (`test_a_created_host_is_removed_after_its_set_in_the_raw_list`); the runner also sorts before pasting. |
| 3 | *5 Documents: waited for verify.completed … run status 'waiting_for_operator'* after 5 s | **runner bug.** Verify and as-built never change the run status by design; the runner treated "not running and no event" as settled. | rc.16: wait by event only, up to the ceiling; a timeout names the last event. |
| 4 | *cleanup failed: The underlying connection was closed* on the WSAPI read after SSH | **runner robustness.** A pooled TLS connection went stale over the 8 minutes; 5.1 does not retry. | rc.16: `DisableKeepAlive`, one retry, re-login on 401/403. |

Consequence of #2 and #4: the cleanup's effect on the array is **unverified**. The SSH transcript
(`cleanup.txt`) is owed; if `removevv` was refused for a VV still in its set (the order pasted), the
array holds `zz_s6_vol01`/`zz_s6_vol02` (the VV set itself was removed last, so they are now loose)
and possibly host `10.132.30.136`. The rc.16 runner's preflight names the leftovers and prints the
lines to paste. Also seen in the report: `→` and `·` rendered as `â` / `Â·` — 5.1 decoded the JSON
body as Latin-1; rc.16 decodes the bytes as UTF-8.
