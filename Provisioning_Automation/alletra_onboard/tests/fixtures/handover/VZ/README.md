# MPB10K-D24U21-VZ (the lab's CRV Vault Zone), OS 10.5.51, 2026-11-17

`lab/handover_capture.py`, read-only, 0 FAIL, every command answered. HPE Alletra Storage MP, two
nodes, serial SGHD44LQLS, management address 10.64.122.140 (lab). OS 10.5.51 (its kernel line says
10.5.0). Captured 2026-11-17 00:08 IST (`showdate`: `IST (Asia/Kolkata)`) by the owner from labrat.
The lab's LZ array (10.64.154.225) did not answer on SSH that night, so it has no capture.

## What it shows

- **Alerts:** 31, all `New`, latest times from 2026-06-24 16:00:00 IST to 2026-11-17 00:06:30 IST,
  printed by that time (oldest first), not by Id.
  - Minor 18: the scheduled task `LZ_RcopyGroup1.r194089` failing every four hours.
  - Major 8: ports 0:3:4 and 1:3:3 failed (unsupported 64G SFP); four Remote Copy links and the
    target `MPB10K-E24U21-LZ` down; "disconnected from Data Services Cloud Console", 3012 times since
    2026-06-24.
  - Degraded 4: unqualified SFPs on 0:3:3, 0:3:4, 1:3:3, 1:3:4 (`-d` adds a `Spare_PN` line to four
    hardware alerts).
  - Informational 1: an OS update is available, `OS-10.5.60.36` (a version, not an address).
  - 12 alerts carry a repeat line; the Remote Copy link alerts have repeated about 880 times since
    2026-06-24.
- **checkhealth -svc -detail:** 14 summary rows, 96 issues: the 31 alerts again (component and
  message equal `showalert -d`), CDM not connected to the network switch, sysvars.init 6, SFPs
  degraded, disabled and of mixed speed, Remote Copy (4 ports and 4 transports not ready, 1 failed
  target, 4 links down, 2 groups not started), remote root access, 24 failed tasks, 8 expired
  volumes. Took 27.5 s.
- **Capacity (`showsys -space`):** raw 43929600 MiB, allocated 696198, free 37244026 (equal to the
  `showsys` columns); usable 29547910, used 599314, free 28948596. Efficiency prints `Dedup : -`
  (no figure) and `>25` for compression, reduction and total.
- **System Reporter:** all ten forms answered, the corrected ones included.
  - **Remote Copy group rows.** The 24-hour summary has two groups. `LZ_RcopyGroup1.r194089`:
    local 7.2 IO/s on average, 185.3 at most, service time 0.08 and 0.87 ms, nothing remote; RPO
    printed `-` on the Avg row and `0` on the Max row. `Recover_back`: all zeros, RPO printed as a date
    and time, `2026-07-20 13:11:32`, with a space in it. Both groups are not started and their target
    has failed (checkhealth), so a row means System Reporter has samples, not that the group
    replicates. The plain `srstatrcvv` shows the samples come only around the four-hourly task (33 in
    its 12 hours, a burst of about 57 IO/s each time).
  - Host ports idle: four FC host ports, 0.9 IO/s together. `-port_type host,iscsi` adds the four
    iSCSI ports 0:4:1, 0:4:2, 1:4:1, 1:4:2 with all-zero rows. In `showport` on the same night they
    are offline with connection type `free`: the `iscsi` type lists every iSCSI port, configured or not.
  - Volumes together averaged 35.7 IO/s (max 217.7): the array's own I/O, as on rack13.
  - CPU (`min,avg,5%,95%,max`): busy on average 7.2 % (node 0) and 6.7 % (node 1); 95 % busy 7.2 and
    6.7; busiest sample 10.2 and 11.0.
- **Help:** same text as on D22U27 and E18U31.

## Scrubbing

Checked every file for user names, passwords, e-mail addresses, IP addresses and customer names.
- `console.txt`: the Windows user name in the zip path is replaced by `<user>`, and the carriage
  returns are removed (the screen log had `\r\r\n` line ends). Nothing else changed.
- Every other file is byte-for-byte the capture. Nothing names a user; the only address is the
  array's lab management address in `report.txt` and `console.txt`. Names are lab objects: the partner
  array `MPB10K-E24U21-LZ`, the groups `LZ_RcopyGroup1.r194089` and `Recover_back`, and the lab's
  CRV snapshot volumes (`sv_CRV_LZ_*`, `snap_*_auto_test_*`, `new_snap`).
