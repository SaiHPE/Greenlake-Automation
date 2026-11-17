# VZ snapshot and schedule captures — 2026-11-17 00:08 IST (BL-21)

Read-only capture from MPB10K-D24U21-VZ, the lab's CRV Vault Zone array (10.64.122.140, SGHD44LQLS,
OS 10.5.51, `systemVersion` 10.5.51.1), by `lab/snap_capture.py`, run through
`lab/labrat_captures.py` from the BGL LabRAT workspace. Show commands and the CLI's own help over
SSH; GETs over WSAPI (one session, closed at the end). Nothing was changed on the array. The first
line of each `.txt` file is the command, as the script wrote it; `report.txt` is the script's own
summary (0 FAIL). The console log is not kept: it repeats `report.txt` and names the workspace's
Windows user.

Scrubbed before commit: `wsapi_system.json` `contact` (a person's name, phone and e-mail) is
`lab-user`. There was no other user name: the one schedule was made by `3paradm`, and WSAPI volume
records carry no creating user. The `CRV_LZ_*` volume names and the group `LZ_RcopyGroup1` are the
lab's own and already appear in the docs and tests.

## What the array held

- **One schedule, suspended** (`showsched.txt`): `SynRcopy_Schedule` runs
  `syncrcopy LZ_RcopyGroup1.r194089` at `5 3,7,11,15,19,23 * * *`; Status `suspended`, NextRunTime
  `--`. The script's summary says `schedules: 0` because it counts only lines that name `createsv`
  or `compactcpg`; the file has the row.
- **93 volumes, 66 snapshots**, 60 with an expiry and 57 with a lock. `showvv_snapcols.txt` and
  `wsapi_volumes.json` agree on every one.
- 57 of them were made by Remote Copy, not by a schedule on VZ: their comment is *Remote Copy
  snapshot created for target 'MPB10K-E24U21-LZ' of group 'LZ_RcopyGroup1.r194089'.* All 57 are
  read-only, `copyOf` a member of `VZ_VVSet`, kept 48 hours and locked about 24. Most are
  `sv_CRV_LZ_<volume>_MM.DD.HH.MM.SS`, every four hours; the time in each name is about a minute
  after VZ's own creation time.
- A snapshot of a snapshot: `snap_profile_auto_test_040926` is `copyOf`
  `sv_CRV_LZ_ESXi_Backup_09.04.15.05.53`, its parent, not the base volume.
- `showcpg.txt`: one CPG, `SSD_r6`. `showvvset.txt`: two sets. Nothing named `zz_sn_*`.
- `showdate.txt`: both nodes `IST (Asia/Kolkata)`; `wsapi_system.json`: `timeZone` `Asia/Kolkata`,
  `VVRetentionTimeMax` 1209600 s (14 days, the default), `virtualLock` licensed.

## What it settled

- **A suspended schedule's row**: Status `suspended`, NextRunTime `--` (one token), every other column
  as for an active one. `parse_showsched` keeps `--` as printed.
- **The WSAPI lock field** is `retentionTime8601` / `retentionTimeSec` here too (OS 10.5.51).
- **Snapshots with `copyOf` a member are not all made by a schedule on the array**: on a Remote Copy
  array, Remote Copy makes them too (SPEC-023 §2.2).
- **The time zone has two names**: VZ prints `Asia/Kolkata`, D22U27 and E18U31 `Asia/Calcutta`; both
  are IST.
- `GET /api/v1/schedules`: HTTP 501, code 9. The help is the same as on D22U27 (OS 10.5.0).

Pinned by `tests/unit/test_snapshots_read.py`.
