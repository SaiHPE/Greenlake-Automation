# SPEC-006 session - 20260916-112647

- App version: 0.16.0rc24
- Runner: PowerShell 5.1.20348.5499; TLS callback: compiled
- Array: 10.132.30.121 (3paradm)  ; CPG: SSD_r6  ; host: 10.132.30.136
- Run 1: 58e4dad7-3e17-4759-a532-dc121a1588c3
- Result: **57 PASS, 1 FAIL**


| Section | Verdict | Check | Detail |
|---|---|---|---|
| Preflight | PASS | array has no zz_s6_ objects | hosts=11 hostsets=5 volumes=57 volumesets=9 vluns=17 |
| 1 Create | PASS | discovery reports >= 1 host on both fabrics | 10.132.30.136 [vcenter] |
| 1 Create | PASS | zoning check puts 10.132.30.136 in zoned_hosts | zoned: 10.132.30.136 |
| 1 Create | PASS | discovery: every host carries identified + in_run (SPEC-009) | hosts=20 |
| 1 Create | PASS | discovery: 10.132.30.136 is in this run and identified | in_run=True identified=True sources=vcenter,array |
| 1 Create | PASS | discovery: 10.132.30.136 initiators carry their array ports | 10005CED8C5312A8 -> 0:3:3,1:3:4 |
| 1 Create | PASS | discovery: unidentified only when the name is the initiator id itself (D-2) |  |
| 1 Create | PASS | preflight: names check counts objects by kind (D-4) | pass: 4 object name(s) free: 2 volumes, 1 VV set, 1 host set. Hosts named in the sheet: 2 (0 already on the array). |
| 1 Create | PASS | zoning render: cfgtransshow first, cfgsave + cfgenable last (Z-4) | cfgtransshow ... cfgsave; cfgenable mycfg / cfgtransshow ... cfgsave; cfgenable jul2prabhu |
| 1 Create | PASS | zoning render: a rejected alias offers a corrected one (Z-3) | host arcus-win137 × array port 0:3:4 — alias 'bad name.1' for host arcus-win137 contains ' ', '.' — FOS names allow letters, digits and _ (- $ ^ on FOS 8.1+) — try 'bad_name_1' |
| 1 Create | PASS | plan: every zz_s6_ row and the export are 'create' | hostset zz_s6_hs=create; volume zz_s6_vol01=create; volume zz_s6_vol02=create; vvset zz_s6_vvs=create; vlun zz_s6_vvs=create |
| 1 Create | PASS | plan: host row 10.132.30.136 is 'create' (array lacks it) | create  |
| 1 Create | PASS | plan: 0 blockers |  |
| 1 Create | PASS | apply: no outcome failed |  |
| 1 Create | PASS | apply: created == planned create (6) | created=6 |
| 1 Create | PASS | apply: exists == planned exists (0) | exists=0 |
| 1 Create | PASS | apply: export read-back names two LUNs, no duplicate | LUN 0, LUN 1 → set:zz_s6_hs |
| 1 Create | PASS | result: host row names id, persona, WWN count (P-8) | id 11 · persona VMware · 2 WWNs |
| 1 Create | PASS | result: zz_s6_vol01 row names id, WWN, size, type, CPG | id 121 · WWN 60002AC000000000000000790002D495 · 1024 MiB tpvv on SSD_r6 |
| 1 Create | PASS | result: host set row lists its member | 1 member: 10.132.30.136 |
| 1 Create | PASS | result: VV set row lists its volumes | 2 volumes: zz_s6_vol01, zz_s6_vol02 |
| 1 Create | PASS | WSAPI: exactly two new VLUN templates | zz_s6_vol01/0/set:zz_s6_hs; zz_s6_vol02/1/set:zz_s6_hs |
| 1 Create | PASS | WSAPI: both new templates target set:zz_s6_hs | zz_s6_vol01/0/set:zz_s6_hs; zz_s6_vol02/1/set:zz_s6_hs |
| 1 Create | PASS | paths: 10.132.30.136 is 'live' | 2 LUN(s) · 2 HBA(s) · 4 path(s) per LUN · both fabrics (SAN6700R13U40, SAN6700R13U38) |
| 1 Create | PASS | paths: lun_count == 2 | lun_count=2 |
| 1 Create | PASS | paths: paths_per_lun >= 2 | paths_per_lun=4 |
| 1 Create | PASS | removal set: 7 lines in dependency order | removevlun -f zz_s6_vol01 0 set:zz_s6_hs ; removevlun -f zz_s6_vol02 1 set:zz_s6_hs ; removevvset -f zz_s6_vvs ; removevv -f zz_s6_vol01 ; removevv -f zz_s6_vol02 ; removehostset -f zz_s6_hs ; removehost 10.132.30.136 |
| 2 Rerun | PASS | plan: every row 'exists', 0 to create | host 10.132.30.136=exists; hostset zz_s6_hs=exists; volume zz_s6_vol01=exists; volume zz_s6_vol02=exists; vvset zz_s6_vvs=exists; vlun zz_s6_vvs=exists |
| 2 Rerun | PASS | plan: 0 blockers |  |
| 2 Rerun | PASS | apply: every outcome 'exists' | host 10.132.30.136=exists; hostset zz_s6_hs=exists; volume zz_s6_vol01=exists; volume zz_s6_vol02=exists; vvset zz_s6_vvs=exists; vlun zz_s6_vvs=exists |
| 2 Rerun | PASS | WSAPI: template count unchanged (P-21) | before=19 after=19 |
| 2 Rerun | PASS | removal set empty |  |
| 3 Conflict | PASS | plan: zz_s6_vol01 is 'conflict' | on the array: 1 GiB tpvv on SSD_r6 · intent: 2 GiB tpvv on SSD_r6 |
| 3 Conflict | PASS | plan: blockers non-empty | volume zz_s6_vol01: on the array: 1 GiB tpvv on SSD_r6 · intent: 2 GiB tpvv on SSD_r6 |
| 3 Conflict | PASS | plan: names the volume no export presents, zz_s6_vol03 (P-19) | Host 'win-10-132-30-137' names only initiators that already belong to another host (arcus-win137) — not planned. / 2 initiator(s) logged in with no host name — name them on the sheet's Hosts tab to provision them. / 1 volume is not presented by this plan: zz_s6_vol03 |
| 3 Conflict | PASS | POST /storage/apply refused (HTTP 4xx) | HTTP 409:  |
| 3 Conflict | PASS | WSAPI unchanged | templates=19 volumes=59 |
| 4 Blank members | PASS | plan: a blocker names zz_s6_hs | Host set zz_s6_hs has no members — choose them in the Compose card (or fill Members on the Host sets tab). Blank no longer means every host.; hostset zz_s6_hs: no members — choose them in Compose or on the Host sets tab |
| 4 Blank members | PASS | plan: no host rows |  |
| 4 Blank members | PASS | plan: no vlun rows (SPEC-005) |  |
| 5 Documents | PASS | run holds the sheet's array credential (3paradm) | source=provisioning user=3paradm host=10.132.30.121 |
| 5 Documents | FAIL | GET /runs/{id} carries no password |  |
| 5 Documents | PASS | verify: reachable, no mismatch | passed=10 mismatches=0 health=35 |
| 5 Documents | PASS | verify: every check states its match rule (V-4) |  |
| 5 Documents | PASS | verify: DNS servers is 'includes', Support contact is 'contains' (V-4) | dns=includes contact=contains |
| 5 Documents | PASS | verify: every status row carries its detail rows (V-1) | status rows=8 detail rows=39 |
| 5 Documents | PASS | as-built generated | As-built ready for rack13arcus — 783 KB. |
| 5 Documents | PASS | docx names 'zz_s6_vol01' |  |
| 5 Documents | PASS | docx names 'zz_s6_vvs' |  |
| 5 Documents | PASS | docx names 'host set zz_s6_hs' |  |
| 5 Documents | PASS | docx names 'To remove what this run created' |  |
| 5 Documents | PASS | docx carries 'removevlun -f zz_s6_vol02 1 set:zz_s6_hs' |  |
| 5 Documents | PASS | docx carries 'removevlun -f zz_s6_vol01 0 set:zz_s6_hs' |  |
| 5 Documents | PASS | docx does NOT say 'did not include the SAN zoning step' (A-3) |  |
| 5 Documents | PASS | docx: the provisioning run section flows on from the zoning one (A-4) | zoning heading breaks=True provisioning heading breaks=False |
| 6 Cleanup | PASS | the removal lines were accepted (no CLI error text) |  |
| 6 Cleanup | PASS | no zz_s6_ object left |  |
| 6 Cleanup | PASS | counts equal the baseline | hosts=11/11 hostsets=5/5 volumes=57/57 volumesets=9/9 vluns=17/17 |

Evidence: every API response as NN-<step>.json, WSAPI reads as NN-wsapi-<what>-<when>.json, asbuilt.docx, cleanup.txt.

## Still needs eyes - UI-only changes, one screenshot each (open run 1 in the browser)
1. Verify step: the line 'Using the array credential from the sheet: ...' and the 'Use a different credential' button (SPEC-008 R4).
2. Provision step, Compose card: pick two members - the box shows the names, not 'multiple' (SPEC-008 R6).
3. Discovery step: 'Hosts in this run' above 'Other hosts on this array', one legend line, RCIP state column (SPEC-009).
4. Zoning step after Build plan: designer legend, an alias with a space typed -> 'Use ...' button, blocks 1/2/3 (SPEC-010).
5. Verify step: one Array status row expanded to its detail rows; a Match row with 'contains the expected value' (SPEC-011).
6. Provision step: Result card Detail column with ids/WWNs; Continue label; 'To remove what this run created' (SPEC-012, SPEC-007).
