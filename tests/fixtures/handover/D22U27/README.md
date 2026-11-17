# AlletraMP_D22U27, OS 10.5.0, 2026-11-17

`lab/handover_capture.py`, read-only, 0 FAIL, every command answered. HPE Alletra Storage MP, two
nodes, serial CZ2D320BT1, management address 10.64.122.99 (lab). Captured 2026-11-17 00:03 IST
(`showdate`: `IST (Asia/Calcutta)`) by the owner from labrat. One half of the lab Remote Copy pair
with E18U31 (`../../rc_pair/`).

## What it shows

- **Alerts: the long list.** 525, all `New`. `showalert` is 4201 lines (145 KB), `showalert -d`
  5255 lines (176 KB), each closed by `525 alerts`. Both are under 1 MB, so both are kept whole.
  - Minor 521, all `Task failed`: the scheduled tasks `Compact-Task` (237) and `Compact-Task1` (284).
  - Major 4: Remote Copy target 5 to `AlletraMP_E18U31` failed (all links down) and two of its links
    down for more than four hours (alerts 135, 136, 573, repeating since 2026-06-15 and 2026-10-12);
    and alert 10, "disconnected from Data Services Cloud Console for more than 19202 minutes".
  - Latest times from 2026-09-30 20:00:00 IST to 2026-11-17 00:00:01 IST. The array prints the
    alerts by that time, oldest first, not by Id (444 first, 966 last, alert 10 near the end).
  - Alert 10's `Time` is 2026-11-16 23:50:26 IST, 13 minutes before the capture. Only `-d` adds
    `Repeat Count: Occurred 2285 times, first at 2025-12-26 21:11:20 IST`. It is the oldest alert
    by first occurrence and would look new without `-d`. Four alerts carry a repeat line, placed
    before `Time` as on OS 10.6.0.
- **checkhealth -svc -detail:** 13 summary rows, 565 issues: the 525 alerts again (component and
  message equal `showalert -d`), sysvars.init 4, a host seen by one node only, packet errors on
  both RCIP ports, 3 ports listed as host paths that are free or file ports, Remote Copy (2
  transports missing, 1 failed target, 2 links down, 6 groups not started), remote root access, 11
  failed tasks, 7 hosts not connected. Took 27.7 s.
- **Capacity (`showsys -space`):** raw 29278208 MiB, allocated 947899, free 24457541 (equal to the
  `showsys` columns); usable 19890325, used 1381934, free 18508391; reduction 1.05, total 22.90.
  OS 10.5.x prints three more lines than 10.6.0 under Raw > Usable > Free: `VV Preallocated`,
  `CPG Preallocated`, `Unallocated`.
- **System Reporter:** all ten forms answered, the corrected ones included.
  - **Host I/O on FC.** Five FC host ports (0:3:1, 0:3:4, 1:3:1, 1:3:2, 1:3:4) averaged 44.2 IO/s
    together; the busiest, 1:3:1, peaked at 23.2 IO/s. The `host,iscsi` form prints the same five
    rows: the array has no iSCSI port (its slot 4 ports are file and RCIP ports).
  - Volumes together averaged 96.0 IO/s (max 680.5).
  - CPU (`min,avg,5%,95%,max`): busy on average 3.5 % (node 0) and 4.2 % (node 1); 95 % busy 3.5 and
    4.3; busiest sample 6.0 and 5.8 (100 minus the minimum Idle%).
  - `srstatrcvv`: the summary has no row and `End Time` is epoch 0. Its six groups are not started.
- **Help:** same text as on E18U31 and VZ; differences from OS 10.6.0 are in SPEC-026 §2a.

## Scrubbing

Checked every file for user names, passwords, e-mail addresses, IP addresses and customer names.
- `console.txt`: the Windows user name in the zip path is replaced by `<user>`, and the carriage
  returns are removed (the screen log had `\r\r\n` line ends). Nothing else changed.
- Every other file is byte-for-byte the capture. No alert or checkhealth line names a user. The only
  address is the array's lab management address in `report.txt` and `console.txt`. Names in the
  alerts and checkhealth are lab objects: scheduled tasks (`Compact-Task*`), Remote Copy groups and
  targets (`300gb`, `APP_Test`, `Intern_Automation*`, `Test-RCG*`, `AlletraMP_E18U31`), lab hosts
  (`DL380G10*`, `DL380G11*`, `winhost_CDS`, `Host1-zerto`) and their WWNs.
