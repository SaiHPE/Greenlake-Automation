# Handover report captures (BL-24, SPEC-026 R2)

Read-only output of `lab/handover_capture.py`: alerts, capacity and System Reporter reports, the
reads the as-built's *Array status and performance at handover* section is built from. One folder
per array, each with its own README: what the array showed and what was scrubbed. Each file starts
with `# <command>`, then the array's output exactly as the SSH client returned it (tests drop the
first line). `_index.txt` lists every command with its line count and time; `report.txt` is the
script's own PASS/FAIL summary; `console.txt` (2026-11-17 captures only) is the script's screen
output. Nothing was written to any array: the script sends only `show*`, `srstat*`, `checkhealth`
and `help` commands.

| Array | Folder | Model | Serial | OS | Captured | By |
|---|---|---|---|---|---|---|
| rack13-ARCUS (10.132.30.121, lab) | [`rack13/`](rack13/README.md) | HPE Alletra Storage MP B10230, 2 nodes | CZ2D2K014S | 10.6.0 (Standard Support Release) | 2026-11-16 23:27 IST | owner, from the lab jump box |
| AlletraMP_D22U27 (10.64.122.99, lab) | [`D22U27/`](D22U27/README.md) | HPE Alletra Storage MP, 2 nodes | CZ2D320BT1 | 10.5.0 (Standard Support Release) | 2026-11-17 00:03 IST | owner, from labrat |
| DHCI_B10K, formerly AlletraMP_E18U31 (10.64.154.190, lab) | [`E18U31/`](E18U31/README.md) | HPE Alletra Storage MP, 2 nodes | CZ2D3209YV | 10.5.60 (Standard Support Release) | 2026-11-17 00:04 IST | owner, from labrat |
| MPB10K-D24U21-VZ, the lab's CRV Vault Zone (10.64.122.140, lab) | [`VZ/`](VZ/README.md) | HPE Alletra Storage MP, 2 nodes | SGHD44LQLS | 10.5.51 (Standard Support Release) | 2026-11-17 00:08 IST | owner, from labrat |

What each capture is for:

| Folder | Alerts | Host I/O (24 h average, host ports summed) | Remote Copy rows | Corrected forms (`*_24h_v2.txt`) |
|---|---|---|---|---|
| `rack13/` | 9, all New | none: 0.0 IO/s on FC | none (no group) | not taken: the script did not have them yet |
| `D22U27/` | 525, all New: the long list | 44.2 IO/s on FC | none (six groups, none started) | answered; no iSCSI port, so both port forms agree |
| `E18U31/` | none: the array prints `no alerts` | 2.7 IO/s on FC, 26.3 with its four iSCSI ports | none | answered; `host,iscsi` adds the iSCSI ports |
| `VZ/` | 31, all New | 0.9 IO/s: idle | two groups; one RPO printed as a date and time | answered; four offline iSCSI ports print zeros |

A quirk of the script, not of the arrays: the `array clock:` line in every `report.txt` (and
`console.txt`) prints `Node Date`, the heading of `showdate`, not the clock. `showdate.txt` has the
time and the zone.

Pinned by `tests/unit/test_handover_parse.py` (the reports), `tests/unit/test_asbuilt_handover.py`
(the as-built section built from them) and `tests/unit/test_cli_allowlist.py` (every option in the
`help_*.txt` of `showalert` and the four `srstat*` reports is reviewed read-only, LESSONS 46). What the captures confirmed and contradicted is in SPEC-026 §2a.
