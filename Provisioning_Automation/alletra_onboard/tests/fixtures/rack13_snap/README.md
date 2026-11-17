# rack13-ARCUS snapshot and schedule captures — 2026-11-16 23:18 IST (BL-21)

Read-only capture from rack13-ARCUS (10.132.30.121, HPE Alletra Storage MP B10230, serial
CZ2D2K014S, OS 10.6.0, `systemVersion` 10.6.0.74) by `lab/snap_capture.py` with
`SNAP_HOST=10.132.30.121`, run from the lab jump box. Show commands and the CLI's own help over SSH;
GETs over WSAPI (one session, closed at the end). Nothing was changed on the array. The first line of
each `.txt` file is the command, as the script wrote it; `report.txt` is the script's own summary
(0 FAIL).

Scrubbed before commit: `wsapi_system.json` `contact` (a person's name, phone and e-mail) is
`lab-user`. There was no other user name: `showsched` lists no schedule, so there is no CreatedBy
column, and WSAPI volume records carry no creating user. The volume and volume-set comments name lab
VMs made by Morpheus, as in `../rack13_wsapi/volumesets.json`; no password, token or customer data.

## What the array held

- **No schedule.** `showsched.txt` is `No scheduled tasks listed` (the empty case of the parser).
- **No snapshot.** `showvv_snapcols.txt`: 35 volumes, every one `Type base`, `CopyOf ---`,
  `ExpirationTime --`, `RetentionEndTime --`. `wsapi_volumes.json`: the same 35 names, every
  `copyType` 1, no `copyOf`, no `expirationTime8601`. So the WSAPI name of a snapshot's retention
  field is still not seen (SPEC-023 section 2).
- **Nothing named `zz_sn_*`** (`showvv_zz_sn.txt`: `no vv listed`; `showvvset_zz_sn.txt`:
  `No vv set listed`).
- `showcpg.txt`: one CPG, `SSD_r6`, 324975 MiB free. `showvvset.txt`: 7 sets, multi-line members.
- `showdate.txt`: both nodes `2026-11-16 23:18:05 IST (Asia/Kolkata)`; `wsapi_system.json`
  `timeZone` is `Asia/Kolkata`.

## What it settled

- **WSAPI has no schedule resource.** `wsapi_schedules_probe.json`: `GET /api/v1/schedules` answered
  HTTP 501, `{"code": 9, "desc": "unsupported operation for the resource"}`. Schedules are read with
  `showsched` and written only through the CLI.
- **`createsched`** (`help_createsched.txt`): `createsched [options] <cmd> <taskschedule> <schedname>`.
  `createsv` is on the list of commands a schedule may run. Cron fields: minute 0-59, hour, day of
  month, month and day of week (`0-6`, 0 is Sunday), each `*`, a number, a list (`1,2,5`) or a range
  (`8-17`); no step syntax (`*/4`) is documented. `@hourly`, `@daily` and the like, and
  `-interval <15-1440 minutes>`, also exist. The name may have 127 characters; `all` and `upgrade`
  are reserved. Without `-f`, `createsched` asks for confirmation when it predicts too many schedule
  starts in one minute. `-immutable` makes a schedule with `-retain` impossible to change or remove.
- **`createsv`** (`help_createsv.txt`): `-exp` and `-retain` take 1 minute to 1825 days (43800 hours);
  the retention cannot be longer than the expiry; the retention cannot exceed the system's
  `VVRetentionTimeMax`, 14 days by default (`wsapi_system.json`: `VVRetentionTimeMax` 1209600 s, the
  default, and `virtualLock` licensed); `-f` skips the confirmation that `-retain` asks for. A snapshot
  of `set:<set>` is one consistent point in time for every member. At most 2048 virtual copies per
  volume (the help's wording of which snapshots count is loose). Snapshot names up to 255 characters.
- **`removesched`** (`help_removesched.txt`): `removesched [options] {<schedname>|<pattern>}...`
  with `-f` (no confirmation) and `-pat`; a name of at most 31 characters.
- **`removevv`** (`help_removevv.txt`): a volume that still has snapshots cannot be removed.
- **`showsched`** (`help_showsched.txt`): without `-all` it hides the system's own schedules.
- `help_setsched.txt` is kept for the record: changing, suspending or renaming a schedule is out of
  scope (SPEC-023 section 5).

Not settled here (no schedule and no snapshot on the array): the WSAPI snapshot body, the quoted
`createsched` over the tool's own SSH session, whether the cron hour is the array's local time, a
suspended schedule's row in `showsched`, and the WSAPI retention field.

Settled since on OS 10.5 by the captures of 2026-11-17 (`../d22u27_snap/`, `../vz_snap/`,
SPEC-023 §2.2): the cron hour is the array's local time, a suspended schedule prints `suspended` and
NextRunTime `--`, and the WSAPI retention field is `retentionTime8601`.

## showsched_one.txt — one schedule on OS 10.6.0, 2026-11-17 about 18:02 IST

`showsched` read right after BL-21's live check 1 sent
`createsched -f "createsv -f -ro -exp 1h @vvname@.@y@@m@@d@@H@@M@@S@ set:zz_snap_vvs" "0 3 * * *" zz_snap_probe`
through the tool's `ArraySnapCliClient` (`docs/validation/2026-11-17-rack13-live-w2.md`). The
schedule was removed with `removesched -f zz_snap_probe` straight after. CreatedBy is `3paradm`, the
array's own account. On OS 10.6.0 the table starts each row with an `Id` column and has a `Rebal`
column before NextRunTime, which the OS 10.5 captures do not have. The parser takes the columns by
header word, so both layouts read.

Pinned by `tests/unit/test_snapshots_read.py`; `tests/unit/test_snap_cli_client.py` reads the help
files once the write client exists.
