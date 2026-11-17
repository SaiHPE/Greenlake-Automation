# D22U27 snapshot and schedule captures — 2026-11-17 00:02 IST (BL-21)

Read-only capture from AlletraMP_D22U27 (10.64.122.99, CZ2D320BT1, OS 10.5.0, `systemVersion`
10.5.0.43) by `lab/snap_capture.py`, run through `lab/labrat_captures.py` from the BGL LabRAT
workspace. Show commands and the CLI's own help over SSH; GETs over WSAPI (one session, closed at the
end). Nothing was changed on the array. The first line of each `.txt` file is the command, as the
script wrote it; `report.txt` is the script's own summary (0 FAIL). The console log is not kept: it
repeats `report.txt` and names the workspace's Windows user.

Scrubbed before commit:

- `showsched.txt`: the CreatedBy of `Pol-999`, a colleague's login, is `lab-user`, padded to the
  original width (as in `../rc_pair/D22U27/showsched.txt`).
- `wsapi_system.json` `contact` (a person's name, phone and e-mail) is `lab-user`.
- Two volume names that carried a person's first name read `lab-user1_885564_553150` and
  `lab-user_HOC`; two that carried what looks like a customer's name read `LAB-VOLUME-001` and
  `LAB-VOLUME-002`. The same names are replaced in every file (`showvv_snapcols.txt`,
  `showvvset.txt`, `wsapi_volumes.json`, `wsapi_volumesets.json`); in the fixed-width files the
  longer replacement takes spaces from the padding after the name, so no column moves.

Other volume and set names are the lab's own and already appear in `../rc_pair/`.

## What the array held

- **Seven schedules**, all `active` (`showsched.txt`). Three run `createsv`:
  - `test_CRV_snapschedule`: `createsv -f -ro -exp 56h -retain 48h snp-@vvname@@m@@d@@H@@M@ set:test_CRV_set`,
    cron `00 0,4,8,12,16,20 * * *`;
  - `Pol-999`: `createsv -f -ro -exp 1440m -addtoset set-test9991784524165764448212 @vvname@.@y@@m@@d@@H@@M@@S@ set:set-test999`,
    every 15 minutes from 08:00 to 20:45, every day;
  - `Test` (new since 2026-10-07): `createsv -f -addtoset Test.Snapset -exp 5d -retain 2d @vvname@.@y@@m@@d@@H@@M@@S@ set:300gb`,
    cron `0 7 9 * *` (07:00 on the 9th of each month): read-write snapshots, times in days.

  The other four run `compactcpg`; `compactcpg_SSD_r6_sun` has day of week `0`.
- **217 volumes, 105 snapshots** (`copyType` 3, `provisioningType` 3; `showvv` `Prov snp`,
  `Type vcopy`), 67 with an expiry and 23 with a lock (`-retain`). `showvv_snapcols.txt` and
  `wsapi_volumes.json` list the same names and agree on every snapshot's parent, RO or RW, creation
  time, expiry and lock.
- Remote Copy's own snapshots are among them: `rcpy.41.269.5` is `copyOf` `300gb` (a member of the
  set the `Test` schedule snapshots), with the comment *Remote Copy snapshot created for target
  'AlletraMP_E18U31' of group '300gb'.*
- `showcpg.txt`: four CPGs (`3sc`, `SSD_r6`, `test`, `test_1`). `wsapi_volumesets.json`: 21 sets.
  Nothing named `zz_sn_*`.
- `showdate.txt`: both nodes `IST (Asia/Calcutta)`; `wsapi_system.json`: `timeZone`
  `Asia/Calcutta`, `VVRetentionTimeMax` 1209600 s (14 days, the default), `virtualLock` licensed.

## What it settled

- **The WSAPI name of a snapshot's lock**: `retentionTime8601` and `retentionTimeSec`, absent when
  the snapshot has none (as `expirationTime8601` is). `showvv`'s `RetentionEndTime` prints the same
  time.
- **A schedule runs in the array's local time.** On 2026-11-16 `Pol-999` made 52 snapshots of
  `test999`, created at minutes 0, 15, 30 and 45 of hours 08 to 20 IST; `test_CRV_snapschedule`'s
  are created at 00:00, 04:00 … 20:00 IST. Each expires exactly `-exp` after it was created, and its
  lock ends `-retain` after it, within a second.
- **The time suffix**: `@vvname@.@y@@m@@d@@H@@M@@S@` makes the volume name, a dot and twelve digits
  with a two-digit year (`test999.261116080000`), 13 characters after the volume name. The seconds
  in the name can be one past the creation time (`test999.261116170001` was created at 17:00:00).
- **`-addtoset`** puts every snapshot in the set it names: `set-test9991784524165764448212` holds
  `Pol-999`'s 52 and one older snapshot.
- **No schedule resource in WSAPI** on OS 10.5.0 either: `GET /api/v1/schedules` answered HTTP 501,
  `{"code": 9, "desc": "unsupported operation for the resource"}`.
- **The help on OS 10.5.0** (`help_*.txt`): the same forms and limits as on 10.6.0, except that
  `createsched` names take at most 31 characters (10.6.0: 127) and a few options 10.6.0 added are
  missing. SPEC-023 §2.2 lists every difference.

Pinned by `tests/unit/test_snapshots_read.py`.
