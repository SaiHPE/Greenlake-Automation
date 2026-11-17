# DHCI_B10K (formerly AlletraMP_E18U31), OS 10.5.60, 2026-11-17

`lab/handover_capture.py`, read-only, 0 FAIL, every command answered. HPE Alletra Storage MP, two
nodes, serial CZ2D3209YV, management address 10.64.154.190 (lab). Captured 2026-11-17 00:04 IST
(`showdate`: `IST (Asia/Calcutta)`) by the owner from labrat. The same array as `../../rc_pair/E18U31/`
(2026-10-07, OS 10.5.0, named `AlletraMP_E18U31`): since then it was upgraded to 10.5.60 and renamed.

## What it shows

- **Alerts: none.** `showalert` and `showalert -d` each print one line, `no alerts`. These are the
  array's words for an alert-free system that SPEC-026 needed; the parser reads them as an empty
  list and anything else as an error. `checkhealth` has no Alert row either.
- **checkhealth -svc -detail:** 5 summary rows, 9 issues: sysvars.init 4, no admin network link on
  node 0, packet errors on `Node1:NVMe:1:1:2`, degraded SFPs on 0:4:1 and 1:4:1, remote root access.
  Took 35.2 s.
- **Capacity (`showsys -space`):** raw 29278208 MiB, allocated 106859, free 25006741 (equal to the
  `showsys` columns); usable 19517890, used 89049, free 19428841; reduction 1.69; thin and total
  printed as `>25`. Same 10.5.x layout as D22U27.
- **System Reporter:** all ten forms answered, the corrected ones included.
  - **Host I/O on iSCSI: the case the corrected port form is for.** `-port_type host` prints four FC
    host ports (0:3:1, 0:3:4, 1:3:1, 1:3:4), 2.7 IO/s together: below the idle threshold of 10.
    `-port_type host,iscsi` adds the four ready iSCSI host ports 0:4:1, 0:4:2, 1:4:1, 1:4:2 (10.7,
    10.7, 1.1 and 1.1 IO/s): 26.3 IO/s together, not idle. The FC rows are the same in both forms.
  - Volumes together averaged 77.7 IO/s (max 771.1).
  - CPU (`min,avg,5%,95%,max`): busy on average 3.9 % (node 0) and 3.7 % (node 1); 95 % busy 3.9 and
    3.8; busiest sample 5.5 and 6.3.
  - `srstatrcvv`: the summary has no row and `End Time` is epoch 0.
- **Help:** same text as on D22U27 and VZ.

## Scrubbing

Checked every file for user names, passwords, e-mail addresses, IP addresses and customer names.
- `console.txt`: the Windows user name in the zip path is replaced by `<user>`, and the carriage
  returns are removed (the screen log had `\r\r\n` line ends). Nothing else changed.
- Every other file is byte-for-byte the capture. Nothing names a user; the only address is the
  array's lab management address in `report.txt` and `console.txt`.
