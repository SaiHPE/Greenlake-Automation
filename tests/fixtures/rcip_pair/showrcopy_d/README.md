# `showrcopy -d` on the Alletra MP -> Primera RCIP pair — 2026-11-19 (BL-64)

Read-only captures from the lab pair (rack13-ARCUS, 10.132.30.121, OS 10.6.0 → PRIMERA630R11U22,
10.132.30.28, OS 4.6.20), taken on 2026-11-19 at about 16:15 IST from a laptop on the VPN, one SSH
`exec_command` per file, so each file starts with `# <command>`. Nothing was written. The groups are the
morning's customer demo run, still configured: `demo_rc_vvs_rcg` (the demo volume set) and `zz_rc_test_rcg`
(the tool's failover test group), both async periodic, period 5 minutes, Started and Synced. Trailing
spaces were trimmed; nothing else changed. Lab names and addresses only.

| File | Array | What it shows |
|---|---|---|
| `alletra_showrcopy_d.txt` | rack13-ARCUS (Primary) | the whole `-d` view: target (`Socks`, `Buffsz`, `SysID`, …), links with a `VLAN` column, both groups with `ID`, `LocalUserCpg`, `RmUserCpg`, the periodic Options (`Last-Sync …, Period 5m,…`) and per volume `Resync_ss`, `Sync_ss`, `VV_iter`, `R_iter`, `S_iter`, `LastSyncTime`, `LocalSet`, `RemoteSet` |
| `alletra_showrcopy_d_groups_demo_rc_vvs_rcg.txt` | rack13-ARCUS | the form the tool sends, `showrcopy -d groups <group>`: one group block |
| `primera_showrcopy_d.txt` | PRIMERA630R11U22 (Secondary) | OS 4.6.20 adds `LocalSnapCpg` and `RmSnapCpg` to the group row; the secondary's Options have no `Last-Sync`; its volume header has no `LocalSet` / `RemoteSet`; no `VLAN` column on links |
| `alletra_clihelp_col_showrcopy.txt` | rack13-ARCUS | `clihelp -col showrcopy`: the array's own meaning of every column (the page's plain labels come from it) |

Differences from the OS 10.5.0 captures in `../../rc_pair/` (2026-10-07 to 10): the same group and volume
columns on the primary; IDs are right-aligned and can start left of their heading (`  demo_rc_vol01 51913`
under `  LocalVV        ID`), so the parser cuts each row by its header and gives a word to the column
its last character falls under. Pinned by `tests/unit/test_replication_group_detail.py`.

## `live_run_5ee6d1b9/` — the tool's own reads in the BL-64 live run (2026-11-19, about 16:39 IST)

Run `5ee6d1b9` of `lab/rcip_tool_lab.py` (`RCIP_MODE=async`, 37 PASS / 0 FAIL) on the same pair, after the
morning's demo objects were removed: the tool set up the partnership, created `zz_rc_vvs_rcg` and
`zz_rc_test_rcg` (async periodic, RPO 10 min, period 5 min) and verified them. The two
`showrcopy_d_groups_*.txt` files are the outputs of the tool's own `showrcopy -d groups <group>` reads on
rack13-ARCUS, taken from the run's command log; `replication_verified.json` is the `replication.verified`
event's data (the verdicts and each group's `config`). Everything was removed with the run's removal set
afterwards. Pinned by `tests/unit/test_replication_group_detail.py`: the parser gives back exactly the
`config` the live Verify reported.
