# Live check: the owner's demo feedback (BL-64), rack13-ARCUS → PRIMERA630R11U22, 2026-11-19

After the customer demo of replication over RCIP the owner asked for three changes. All three are built
on branch `feat/bl-64-demo-feedback` (one commit each) and ran live on the lab pair the same afternoon.
Run from the developer's Mac on the VPN, the app from the branch's source on 127.0.0.1:8765
(`STATE_DATABASE_PATH=~/Documents/alletra-demo/bl64-live.db`), driven over its API by
`lab/rcip_tool_lab.py` with `RCIP_MODE=async`. The password came from the owner's rack13 workbook
through the app's own parser (`sheet_targets`) and went only to the local app and the SSH sessions.
Async only: the array refuses sync for this pair.

## What changed

| # | The owner's words | What the tool does now |
|---|---|---|
| 1 | "Change button check link -> check rc link" | The Replication page says *Check RC link* and *Check RC link again* (button, parts bar, panel and section titles, the sentences that tell the operator to press it); the apply's 409 reads *Check RC link first: …*. Behaviour unchanged |
| 2 | "Remove performance from asbuilt" | The as-built section is *Array status at handover*: alerts and capacity, no performance. No `srstat*` read is sent; `srstatcpu`, `srstatport` and `srstatvv` left the read allowlist. The array's UTC offset for *Before this run* now comes from `showdate`. The As-built page's block and the `handover` event lost the performance fields |
| 3 | "To show all volumes in rcgroup including config, showrcopy -d" | Verify reads `showrcopy -d groups <group>` on this array for each group the run configured; the `replication.verified` event, a folded section per group on the Replication page and a table per group in the as-built show the group's settings and every volume |

## Before

- 16:13 IST: the morning's demo run (`8356cf30`) was still configured on the pair, so
  `demo_prep.py check` said NOT READY on four lines. The read-only captures in
  `tests/fixtures/rcip_pair/showrcopy_d/` were taken from it then.
- About 16:25: `after-demo.sh` pasted that run's own removal set (A block, then B block) and the demo app was
  stopped (the run sheet's after-demo steps). Then `demo_prep.py check`: all six lines READY (the
  Primera's RCIP gateway left cleared, as the demo needs); `demo_objects.py check`: READY,
  `demo_rc_vol01` in `demo_rc_vvs` on rack13.

## The run

Run `5ee6d1b9-4523-4a9e-9864-41a79d74aca7`, **37 PASS, 0 FAIL** (it was 27/0 on 2026-11-18; the ten new
lines are this change's checks). Evidence in `~/Documents/alletra-demo/bl64/rcip_tool_async/`.

- Partnership: 4 addresses, 2 pings, Remote Copy started, 2 targets, links Up (8 steps).
- *Check RC link*: the apply before the check answered HTTP 409 *Check RC link first: the latency
  between the arrays has not been measured in this run.*; the check measured 0.022 ms on 2 links.
- Groups `zz_rc_vvs_rcg` and `zz_rc_test_rcg` created and started (12 writes); Verify: 2 replicating.
- Failover test passed on `zz_rc_test_rcg`: failover in 6.7 s, synced back in 6.6 s.
- As-built 793 KB, 6 items to check (5 alerts of the lab array, the unfilled cover placeholders).

The three extra checks:

| Check | Result | From |
|---|---|---|
| The as-built has no performance | PASS. Heading *Array status at handover*; subsections *Alerts* and *Capacity*; no *System Reporter*, window, CPU, port or volume table. *Before this run*: Yes on all five Major-or-worse alerts, from `showdate` (*read at 2026-11-19 11:12 UTC (16:42 on the array's clock, UTC+05:30)*). The `handover` event: `read_at, alerts_new 10, alerts_major 5, oldest_alert, cloud_alert 40, read_errors {}`, no performance field | `11-asbuilt-text.txt`, `asbuilt.docx`, `10-asbuilt.json` |
| No `srstat*` command sent | PASS. 203 commands in the run's command log, none starting `srstat` | `12-commands.txt` |
| Every volume and the group's settings from `showrcopy -d` | PASS. One `showrcopy -d groups <group>` per group, on rack13-ARCUS. The Verify event's `config` for each group: target PRIMERA630R11U22, Periodic, period 5m, RPO 10, Primary, Started, CPG SSD_r6 both sides, policies `auto_recover, over_per_alert, auto_synchronize`, and its volume (`zz_rc_vol01` ID 326 ↔ 52064, Synced, resync snapshot `rcpy.29.326.19`, iterations `185493/1`). The as-built has a settings table and a volume table per group | `06-verify-00.json`, `07-` and `08-showrcopy_d_groups_*.txt`, `asbuilt.docx` |

The Replication and As-built pages were looked at for this run on the branch's `frontend/src` (vite dev
server, no build) at 1366 × 768 and 1080 × 720: *2. Check RC link* in the parts bar and *Check RC link:
latency 0.022 ms* on its row; one folded section per group after Verify (*zz_rc_vvs_rcg: 1 volume ·
Periodic, every 5 minutes · Started · 1 of 1 synced*), its settings and its volume table on screen
without a horizontal scroll at both sizes; the As-built page's *Status at handover* with the alerts
only. Screenshots in `~/Documents/alletra-demo/bl64/screens/`.

The tool's own two `showrcopy -d` reads and the Verify event are now fixtures
(`tests/fixtures/rcip_pair/showrcopy_d/live_run_5ee6d1b9/`), pinned by a test that parses them back to
the event's `config`.

## Cleanup

The script pasted the run's merged removal set: A block on rack13-ARCUS (stop, dismiss and remove both
groups, the test volume and set, the target, `stoprcopy -f -stopgroups -clear`, the two RCIP addresses),
then B block on the Primera (the two peer sets, the two secondaries, the target), then removed
`zz_rc_vvs` and `zz_rc_vol01`, which it made itself. `dismissrcopyvv` answered *Manual cleanup required
on target system* as before; the B block did that cleanup. Script: *no zz_rc_\* object left on either
array* PASS, *the pair is back at the starting point* PASS (`13-cleanup.txt`).

After the run, from the main checkout's app folder:

```
$ demo_prep.py check
READY  rack13: Remote Copy not configured
READY  rack13: no RCIP address on 0:4:4 / 1:4:4
READY  rack13: no zz_rc_* volume or set
READY  Primera: no target rack13-ARCUS
READY  Primera: RCIP 10.93.18.19 / .20 ready
READY  Primera: no RCIP gateway (needed for a clean link check)
$ demo_objects.py check
rack13 volumes   demo_rc_vol01
rack13 sets      demo_rc_vvs
rack13 groups    -
primera volumes  -
primera sets     -
primera groups   -
READY  demo volume and set on rack13, nothing demo_rc* on the Primera
```

The branch's app on 8765 was stopped afterwards. The demo app was not restarted: `start-demo.sh` starts
a fresh one for the next demo.
