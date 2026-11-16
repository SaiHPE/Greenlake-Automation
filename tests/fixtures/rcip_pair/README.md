# Alletra MP -> Primera RCIP pair — 2026-11-03 (BL-41)

The GTS training pair the lab gave for replication testing, reached from a laptop on the VPN:

| | Alletra MP | Primera |
|---|---|---|
| System | rack13-ARCUS · CZ2D2K014S · 10.132.30.121 · OS 10.5.55 | PRIMERA630R11U22 · SGH339NK4C · 10.132.30.28 · OS 4.6.20 |
| RCIP | 0:4:4 10.93.18.11 · 1:4:4 10.93.18.13 (set by `lab/rcip_setup_lab.py`) | 0:1:1 10.93.18.19 · 1:1:1 10.93.18.20 (set by the lab) |

`cleanup_2026-11-03.txt`: the removal of run `f55b3722` (`lab/rcip_pair_lab.py`, 21 PASS / 0 FAIL).
A's `dismissrcopyvv -f -removevv` answered *"target system PRIMERA630R11U22 has indicated that one or
more volumes in the group could not be deleted. Manual cleanup required on target system."* for both
groups; removing the peer volume sets and then the secondaries by name on the Primera cleared them.
Pinned by `tests/unit/test_replication_apply.py`.

The link check of 2026-11-03 22:53, with the Primera's RCIP gateway 10.93.18.1 set (as the lab left it):

- `checkrclink_startserver_gateway.txt`: the Primera's server routes the Alletra's address through the
  gateway (`Adding route: 10.93.18.11 -> 10.93.18.1`). This capture is the second start, after a
  `stopserver`: `SIOCADDRT: File exists` shows the first route was still there.
- `checkrclink_startclient_lost.txt`: the Alletra's client: `Pings Lost: 100 %`, no latency line,
  *"No connection with remote side, check IP Address"*.
- `showrcopy_links_alletra_after_check.txt`: both outbound links Down afterwards (Up before).
- `showport_rcip_primera_gateway.txt`: the Primera's RCIP ports with that gateway.

`controlport rcip state down -f` / `up -f` on each Primera RCIP port removed the route; with the
gateway cleared the check measured 0.018 ms and the links stayed Up. Pinned by
`tests/unit/test_replication_link_check.py`.

`rcip_setup_commands_2026-11-03.log`: every command `lab/rcip_setup_lab.py setup` sent to both arrays and
what each answered (RCIP addresses, ping, `startrcopy`, `creatercopytarget` both ways, link reads).
`help/`: both arrays' CLI help for the Remote Copy setup and undo commands. Pinned by
`tests/unit/test_rc_cli_client.py`.

`tool_run/`: the tool setting up the partnership itself (SPEC-021), `lab/rcip_tool_lab.py`.
`replication_events.json` is run `58da7c29` (2026-11-03 18:48 UTC): the plan of each preview and the
result of each apply, in order: partnership first (8 steps), groups second (12 writes). Pinned by
`tests/unit/test_asbuilt_replication.py` (the as-built lists both applies). `removal_set_pasted.txt` is
the rerun `fadc7d54` (25 PASS / 0 FAIL): the merged removal set as pasted, A block then B block, and
what each line answered; the pair was back at the start afterwards.

`checkrclink_startclient_routed_no_number.txt`: 2026-11-06, the Alletra's ports on a /28 with the lab router 10.93.18.1 as gateway (`RCIP_NET=routed lab/rcip_tool_lab.py`, run 1b2cfe2d). The client added `10.93.18.19 -> 10.93.18.1`, lost no ping, passed the MTU 1500 test and connected over TCP 5001, but printed `Average measured latency: min ms`: no number. The router answers every ping twice (a ping through it showed `+2 duplicates`). Pinned by `tests/unit/test_replication_link_check.py`.

`controlport_rcip_ping_routed_redirect.txt`: 2026-11-06, the same probe's ping from 0:4:4 (10.93.18.11/28, gateway 10.93.18.1) to 10.93.18.19: the router forwards the first packet, sends `Redirect Host(New nexthop: 10.93.18.19)`, and the reply comes twice (`+2 duplicates`); the array then goes direct. The ping the link check falls back to (SPEC-020 R2a). Pinned by `tests/unit/test_replication_link_check.py`.
