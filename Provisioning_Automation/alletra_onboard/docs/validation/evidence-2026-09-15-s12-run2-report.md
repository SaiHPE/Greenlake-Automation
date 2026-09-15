# SPEC-006 session - 20260915-142128

- App version: 0.16.0rc16
- Array: 10.132.30.121 (3paradm)  ; CPG: SSD_r6  ; host: 10.132.30.136
- Run 1: 16b021ce-5dd3-4342-bd2e-2ab456989c77
- Result: **38 PASS, 1 FAIL**


| Section | Verdict | Check | Detail |
|---|---|---|---|
| Preflight | PASS | array has no zz_s6_ objects | hosts=11 hostsets=5 volumes=54 volumesets=9 vluns=17 |
| 1 Create | PASS | discovery reports >= 1 host on both fabrics | 10.132.30.136 [vcenter] |
| 1 Create | PASS | zoning check puts 10.132.30.136 in zoned_hosts | zoned: 10.132.30.136 |
| 1 Create | PASS | plan: every zz_s6_ row and the export are 'create' | hostset zz_s6_hs=create; volume zz_s6_vol01=create; volume zz_s6_vol02=create; vvset zz_s6_vvs=create; vlun zz_s6_vvs=create |
| 1 Create | PASS | plan: host row 10.132.30.136 is 'create' (array lacks it) | create  |
| 1 Create | PASS | plan: 0 blockers |  |
| 1 Create | PASS | apply: no outcome failed |  |
| 1 Create | PASS | apply: created == planned create (6) | created=6 |
| 1 Create | PASS | apply: exists == planned exists (0) | exists=0 |
| 1 Create | PASS | apply: export read-back names two LUNs, no duplicate | LUN 0, LUN 1 → set:zz_s6_hs |
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
| 3 Conflict | PASS | POST /storage/apply refused (HTTP 4xx) | HTTP 409:  |
| 3 Conflict | PASS | WSAPI unchanged | templates=19 volumes=56 |
| 4 Blank members | PASS | plan: a blocker names zz_s6_hs | Host set zz_s6_hs has no members — choose them in the Compose card (or fill Members on the Host sets tab). Blank no longer means every host.; hostset zz_s6_hs: no members — choose them in Compose or on the Host sets tab |
| 4 Blank members | PASS | plan: no host rows |  |
| 4 Blank members | PASS | plan: no vlun rows (SPEC-005) |  |
| 5 Documents | PASS | verify: reachable, no mismatch | passed=10 mismatches=0 health=19 |
| 5 Documents | PASS | as-built generated | As-built ready for rack13arcus — 781 KB. |
| 5 Documents | PASS | docx names 'zz_s6_vol01' |  |
| 5 Documents | PASS | docx names 'zz_s6_vvs' |  |
| 5 Documents | PASS | docx names 'host set zz_s6_hs' |  |
| 5 Documents | PASS | docx names 'To remove what this run created' |  |
| 5 Documents | PASS | docx carries 'removevlun -f zz_s6_vol02 1 set:zz_s6_hs' |  |
| 5 Documents | PASS | docx carries 'removevlun -f zz_s6_vol01 0 set:zz_s6_hs' |  |
| 5 Documents | PASS | docx does NOT say 'did not include the SAN zoning step' (A-3) |  |
| 6 Cleanup | PASS | the removal lines were accepted (no CLI error text) |  |
| 6 Cleanup | FAIL | cleanup failed: The underlying connection was closed: An unexpected error occurred on a send. | paste C:\Users\Administrator\Downloads\alletra-onboard-win64\AlletraOnboard\session-20260915-142128\run1-removal-set.txt by hand |

Evidence: every API response as NN-<step>.json, WSAPI reads as NN-wsapi-<what>-<when>.json, asbuilt.docx, cleanup.txt.
