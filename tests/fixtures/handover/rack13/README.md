# rack13-ARCUS, OS 10.6.0, 2026-11-16

`lab/handover_capture.py`, read-only, 0 FAIL. HPE Alletra Storage MP B10230, two nodes, serial
CZ2D2K014S, management address 10.132.30.121 (lab). Captured 2026-11-16 23:27 IST by the owner from
the lab jump box, before the script took the corrected forms (no `_24h_v2` files here).

## What it shows

- **Alerts:** nine, all `New`: Major 3 (two iLO ssh-key alerts, one "disconnected from Data
  Services Cloud Console for more than 7200 minutes"), Critical 2 (switch running/startup config
  mismatch), Degraded 2 (unqualified SFPs on 0:4:2 and 1:4:2), Informational 2 (cage I/O module
  firmware). Times from 2026-11-11 23:22:51 IST to 2026-11-16 23:25:20 IST. Alert 40's `Time` is its
  latest occurrence; only `showalert -d` adds `Repeat Count: Occurred 240 times, first at
  2026-11-11 23:54:31 IST`.
- **checkhealth -svc -detail:** 10 summary rows, 40 issues (the nine alerts again, a degraded cage,
  12 drives on old firmware, the SFPs, remote root access enabled, switch firmware and config, nine
  iSCSI hosts not connected). Took 65 s.
- **Capacity (`showsys -space`):** usable 15174810 MiB, used 90039 MiB, free 15084771 MiB; reduction
  8.46, total efficiency printed as `>25`.
- **System Reporter:** all eight forms answered. Host ports (`-port_type host`, four FC ports) carried
  no I/O in the 24 hours; the volumes together averaged 27.6 IO/s (the array's own I/O). CPU 7.5 to
  7.8 % busy on average per node. No Remote Copy group: `srstatrcvv` prints its header only, and the 24-hour
  form prints `End Time: 1970-01-01 05:30:00 IST (0)`.
- **Help:** `help showalert`, `help showsys` and `help srstat{cpu,port,vv,rcvv}` on OS 10.6.0.

## Scrubbing

Checked every file for user names, passwords, e-mail addresses, IP addresses and customer names.
None needed removing: no alert or checkhealth line names a user, and the only address is the lab
array's own management address in `report.txt`. Host names in `checkhealth` (`HPE_VM_*`,
`iqn.2024-12.com.hpe:vmenode*`) are HPE lab virtual machines. The files are byte-for-byte the
capture.
