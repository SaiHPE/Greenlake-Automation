# E18U31 snapshot and schedule captures — 2026-11-17 00:04 IST (BL-21)

Read-only capture from the lab's E18U31 array (10.64.154.190, CZ2D3209YV, OS 10.5.60,
`systemVersion` 10.5.60.36) by `lab/snap_capture.py`, run through `lab/labrat_captures.py` from the
BGL LabRAT workspace. Show commands and the CLI's own help over SSH; GETs over WSAPI (one session,
closed at the end). Nothing was changed on the array. The first line of each `.txt` file is the
command, as the script wrote it; `report.txt` is the script's own summary (0 FAIL). The console log
is not kept: it repeats `report.txt` and names the workspace's Windows user.

The array is not the one in `../rc_pair/E18U31/` (2026-10-07) any more: it was set up again on
2026-10-22 (`.mgmtdata` was created then) and is now named `DHCI_B10K`, with OS 10.5.60 instead of
10.5.0. The schedule `patchisched` and the Remote Copy groups of that time are gone.

Scrubbed before commit: `wsapi_system.json` `contact` (a person's name, phone and e-mail) is
`lab-user`. There was no other user name: `showsched` lists no schedule, and WSAPI volume records
carry no creating user. The volume and set comments name lab VMs made by Morpheus, as in
`../rack13_snap/`; the `TPIPoc-*` volume names already appear in `../rc_pair/`.

## What the array held

- **No schedule.** `showsched.txt` is `No scheduled tasks listed`.
- **35 volumes, 3 snapshots**: `preRecover_LK04_20261116`, `preRecover_LK05_20261116` and
  `preRecover_LK06_20261116`, read-only snapshots of `TPIPoc-NEW-RH-LK-04` to `-06`, made on
  2026-11-16. **No expiry and no lock**: `showvv` prints `--` in both columns, and the WSAPI records
  have neither `expirationTime8601` nor any `retention*` key.
- `showcpg.txt`: one CPG, `SSD_r6`. `showvvset.txt`: three sets. Nothing named `zz_sn_*`.
- `showdate.txt`: both nodes `IST (Asia/Calcutta)`; `wsapi_system.json`: `timeZone`
  `Asia/Calcutta`, `VVRetentionTimeMax` 1209600 s (14 days, the default), `virtualLock` licensed.

## What it settled

- A snapshot without an expiry or a lock reads the same in both views: `--` in `showvv`, keys absent
  in WSAPI (so `parse_volumes` gives `expires` "").
- `GET /api/v1/schedules`: HTTP 501, code 9, as on the other arrays.
- The help on OS 10.5.60 is the same as on 10.5.0 and 10.5.51 (`help_*.txt`), except that
  `help_setsched.txt` adds one note: `-rebalance`, `-resume_all` and `-suspend_all` need the Super
  or Service role. SPEC-023 §2.2 lists how 10.5 differs from 10.6.0.

Pinned by `tests/unit/test_snapshots_read.py`.
