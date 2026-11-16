# Live validation: RCIP ports and partnership set up by the tool (SPEC-021), Alletra MP → Primera, 2026-11-03

First live record for BL-41. Run from a Mac on the HPE VPN (the GTS training arrays answer SSH and
WSAPI from there), the app from source on `feat/bl-41-rcip-setup`
(`PYTHONPATH=src python3 -m uvicorn alletra_onboard.api.app:app --port 8765`), driven by
`lab/rcip_tool_lab.py`. **Both arrays were changed and put back: the run's own removal set returned
the pair to where it started.**

**Outcome: from a pair with no partnership, one run set up the RCIP addresses, pinged each pair of
ports, started Remote Copy, created a target each way and waited for the links. It then checked the
link (0.018 ms), created the groups, verified them replicating, passed the failover test (1.6 s,
synced back in 1.5 s) and generated the as-built. 25 PASS / 0 FAIL (run fadc7d54). SPEC-021 R1–R5
are live-verified on an Alletra MP → Primera pair.**

## Environment

| | Array A (this run) | Array B (the peer) |
|---|---|---|
| System | rack13-ARCUS · CZ2D2K014S · 10.132.30.121 | PRIMERA630R11U22 · SGH339NK4C · 10.132.30.28 |
| OS | 10.5.55 | 4.6.20 |
| RCIP before | none (0:4:1 / 1:4:1 are live iSCSI host ports, left alone) | 0:1:1 10.93.18.19 · 1:1:1 10.93.18.20, 255.255.254.0 |
| Remote Copy before | not configured | Started, Normal, no target for the Alletra |

The lab mail asked for 0:4:1, 0:4:2, 1:4:1 and 1:4:2 on the Alletra. The capture
(`lab/rcip_pair_capture.py`) showed 0:4:1 and 1:4:1 carrying iSCSI hosts with live sessions, so the
run used the free peer ports with cable, 0:4:4 and 1:4:4, with two of the lab's addresses
(10.93.18.11 and .13). Network 10.93.18.0/23, MTU 1500, no gateway.

Sheet composed through `POST /init-sheet/compose`: Replication tab with peer 10.132.30.28, one sync
row `zz_rc_vvs` → peer CPG `SSD_r6`; Replication network tab with four rows (this 0:4:4 .11,
this 1:4:4 .13, peer 0:1:1 .19, peer 1:1:1 .20, mask 255.255.254.0). Mode Custom: Replication,
Failover test, As-built.

## The run (times UTC, 2026-11-03)

| Time | Event |
|---|---|
| 18:53:40 | Preview 1: *plan ready: 5 to create, 3 already there.* Rows: A 0:4:4 and 1:4:4 create; B 0:1:1 and 1:1:1 exist; Remote Copy A create, B exists; target PRIMERA630R11U22 on A and rack13-ARCUS on B create. No group yet, no blocker. |
| 18:54:05 | Apply 1: *Ports and partnership set up — 8 step(s), every link Up.* |
| 18:54:16 | Preview 2: partnership found, 2/2 links Up each way; every partnership row *exists*; groups to create. |
| — | Apply 2 before the link check: HTTP 409 *Check the link first.* |
| 18:54:48 | Link check: *Latency 0.018 ms on 2 link(s) (sync needs 10 ms or less) — within the limit.* Links still Up afterwards. |
| 18:54:50 | Apply 2: *Replication configured — zz_rc_vvs_rcg, zz_rc_test_rcg; 12 write(s).* |
| 18:55:01 | Verify: *2 replicating · 0 syncing · 0 not replicating · links Up.* |
| 18:55:36 | Failover test passed on zz_rc_test_rcg: failover 1.6 s, synced back 1.5 s. |
| 18:56:22 | As-built generated (788 KB). One warning: unfilled customer placeholders, expected on a lab sheet. |

The SSH writes, in the order the console log recorded them (all through `ArrayRcCliClient`):

```
A  controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4
A  controlport rcip addr -f 10.93.18.13 255.255.254.0 1:4:4
A  controlport rcip ping -c 3 10.93.18.19 0:4:4
A  controlport rcip ping -c 3 10.93.18.20 1:4:4
A  startrcopy
A  creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20
B  creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13
```

## The removal set, pasted as the as-built prints it

A block on the Alletra, then B block on the Primera; the groups apply comes first, then the
partnership apply. Every line answered without an error; `removercopytarget` was not busy.

```
# ---- A: rack13-ARCUS
stoprcopygroup -f zz_rc_vvs_rcg
dismissrcopyvv -f -removevv zz_rc_vol01 zz_rc_vvs_rcg
removercopygroup -f zz_rc_vvs_rcg
stoprcopygroup -f zz_rc_test_rcg
dismissrcopyvv -f -removevv zz_rc_test_v01 zz_rc_test_rcg
removercopygroup -f zz_rc_test_rcg
removevvset -f zz_rc_test
removevv -f zz_rc_test_v01
removercopytarget PRIMERA630R11U22
stoprcopy -f -stopgroups -clear
controlport rcip delete -f 0:4:4
controlport rcip delete -f 1:4:4
# ---- B: PRIMERA630R11U22
removevvset -f zz_rc_vvs_rc
removevvset -f zz_rc_test_rc
removevv -f zz_rc_vol01
removevv -f zz_rc_test_v01
removercopytarget rack13-ARCUS
```

`dismissrcopyvv -removevv` answers *target system PRIMERA630R11U22 has indicated that one or more
volumes in the group could not be deleted. Manual cleanup required on target system.* The Primera
keeps a secondary that sits in a volume set; the B block's `removevvset` and `removevv` lines are that
cleanup. Afterwards: no `zz_rc_*` object on either array, the Alletra back to *Remote Copy is not
configured* with no RCIP address, the Primera without a target for the Alletra and its addresses
unchanged.

## How it got here: five runs on a partnership set up by hand

Before the tool set up the partnership itself, `lab/rcip_setup_lab.py setup` built one by hand from a
journal (9/0), and `lab/rcip_pair_lab.py` ran the app's group steps over it. Each failure left a fix:

| Try | What failed | Fix |
|---|---|---|
| 1 | The link check left every link Down. The Primera's RCIP ports had gateway 10.93.18.1; `checkrclink` routed through it, and Primera OS 4.6 kept the route after `stopserver` (*SIOCADDRT: File exists*). | `controlport rcip state down -f` / `up -f` on the Primera ports cleared it. The gateway was then cleared (journaled). The link check now re-reads the links afterwards and fails if one went Down, naming the way back; a 100% loss names the gateway (commit 69648560). |
| 2 | The test volume was created with an empty CPG. | The sheet's Default CPG (d27f314e). |
| 3 | WSAPI refused the group: no `localUserCPG`. | The local CPG falls back to the Default CPG. |
| 4 | `creatercopygroup` failed: *Failed to send message to target*. The Primera's new IP target showed SysName None: an old failed FC target for the same Alletra blocked it. | Removed after saving its config (`removercopytarget -cleargroups -f rack13-ARCUS_PRIMERA`; its five stopped groups cannot be restored). The plan now blocks on such a target and names the command (SPEC-021 R3). |
| 5 | 21 PASS / 0 FAIL. The removal set left two secondaries on the Primera. | The B block also removes the secondaries the admits created (58b290d9). |

Then `rcip_setup_lab.py undo-setup` removed the hand-made partnership (4/0), and this run's tool built
it again. The first tool run (58da7c29) was 23/2: the as-built showed only the groups apply, so the
ports and targets were missing from *What was run* and *What each array reported*. The as-built now
lists every apply of the run in order (`tests/fixtures/rcip_pair/tool_run/replication_events.json`
is that run's plans and results). Rerun fadc7d54: 25/0.

## 2026-11-05: through the screens

The same flow clicked through the app's pages in a 1366 × 768 browser on the Mac (app from source,
upload of the composed sheet, mode Custom: Replication, Failover test, As-built). The Primera's
gateway was cleared for each run and put back after (journaled).

**Run 3cb3a8c8, first pass: every array result right, four screen faults.**

| What the screen did | Fix |
|---|---|
| After the partnership apply the step read *Complete · replication configured* and *Nothing new to create*; the green button was *Verify replication* and Continue to the failover test dropped "without configuring replication". No group existed yet. | A partnership-only apply leaves the step at *Action required · partnership set up*, says nothing is replicated yet, and the green button is *Read both arrays again* (page and step rail). |
| The approval box ticked for the partnership plan was still ticked under the groups plan. | A new read or an apply clears it. |
| *2. Check the link* showed a tick on the partnership plan, before any link existed. | Not done until a link check ran. |
| The page said the partnership must already exist; the sheet review named the peer but not the four port rows. | Wording for both cases; the review lists the ports to set up. |

The groups plan, the link check (0.018 ms), the configure, verify (2 of 2 replicating), the
failover test (2.6 s, synced back 2.4 s), the as-built and the removal set were right on the first
pass.

**Run 179121cc, with the fixes: clean.** The partnership plan showed *Set up the partnership* and
its own approval sentence, *Check the link* not done. After it: *Action required · partnership set
up*, green button *Read both arrays again*. The groups plan came with the box empty. Link 0.02 ms,
2 of 2 replicating, failover passed, as-built ready. The run's merged removal set (17 lines) ran with
no error, and the pair was back at the start.

## 2026-11-05: async (periodic) over the same pair

`RCIP_MODE=async lab/rcip_tool_lab.py`, one row `zz_rc_vvs` async with RPO 10 min. **27 PASS / 0 FAIL**
(run 4dc6331e). The tool set up the partnership again, planned the group as *async, RPO 10 min
(period 5 min)*, measured 0.019 ms (*async needs 200 ms or less*), created both groups, and both
arrays reported them *Started · Periodic · Synced*. The failover test passed in 2.3 s, synced back in
2.0 s. The as-built read the period back from the array (*RPO 10 min (period 5m)*). The run's removal
set put the pair back at the start, and the Primera's gateway was restored.

## 2026-11-06: the in-scope paths not yet run live

`lab/rcip_scope_lab.py`, four scenarios on the same pair, **35 PASS / 0 FAIL**; the pair ended where it
started and the Primera's addresses, gateway and Remote Copy were as the lab set them.

| Scenario | What happened |
|---|---|
| A sync row and an async row with the Replication network tab (run cb0ee6d0) | Refused at the first read: the partnership the tool sets up has one target, and a target carries one mode. Configure answered 409; nothing was written. Before this change the refusal came only after the partnership was set up. |
| This array's ports on another network, 192.0.2.11/.13 (run cfe07a5a) | Addresses set, then *ping from 0:4:4 to 10.93.18.19: … 100% packet loss … nothing after the addresses was done*. Removal set: the two `controlport rcip delete` lines, nothing on the peer. Pasted without an error. |
| The Primera's gateway 10.93.18.1 left on (run 29d4a304) | The partnership came up. The link check noted the gateway before it ran, measured no latency (*routed its answers through gateway 10.93.18.1*), then found all four links Down that were Up before, and printed the way back. Configure answered 409. The printed way back (`controlport rcip state down -f` / `up -f` on 0:1:1 and 1:1:1) brought every link Up in under a minute. |
| The peer's side set up by the tool (run 529bc2af) | The Primera's Remote Copy stopped and its RCIP addresses removed first (journaled). The plan created both sides' addresses and started Remote Copy on both. The apply did 11 steps, every link Up. The B block undid the peer's side (`removercopytarget`, `stoprcopy -f -stopgroups -clear`, both `controlport rcip delete`). Groups replicating. |
| Failover test on a group the run did not create (run f8022167, same sheet) | Refused without the name typed back (HTTP 409, *hosts running on its primary volumes lose access*); with `zz_rc_vvs_rcg` typed back it ran on that group and passed: 2.2 s, synced back in 2.0 s. |

## 2026-11-06: through a router

The lab's 10.93.18.1 is a router. Probe first: with 0:4:4 on 10.93.18.11/28 and gateway 10.93.18.1, pings to
10.93.18.19 and .20 got through (with `+2 duplicates`); with a gateway that is not a router (10.93.18.14) every
ping was lost. So with a gateway set, the Alletra sends its traffic to the peer through it
(`routed_probe.txt` in the session evidence).

`RCIP_NET=routed lab/rcip_tool_lab.py` (run 1b2cfe2d): this array's rows 10.93.18.11 and .13 on
255.255.255.240 with gateway 10.93.18.1; the Primera's gateway cleared for the run, so only the Alletra's
direction is routed. **17 PASS / 2 FAIL.**

- Through the router: the tool wrote each address and then its gateway, and read both back (a new check: a
  gateway the array did not take stops the apply). The pings passed, Remote Copy started, the targets were
  created, and both Remote Copy links came Up. The removal set removed it all.
- The link check could not measure. The array's client added `10.93.18.19 -> 10.93.18.1`, lost no ping,
  passed the MTU 1500 test and connected over TCP 5001, but printed `Average measured latency: min ms`,
  with no number. The router answers every ping twice, and the array's test cannot work out a latency from
  that. The tool refused to configure the groups without a measured latency, as it must. Its message said
  "printed no latency within 120 s", which was wrong (it stopped reading after 3 s). It now quotes the line
  the array printed and says the link answers but the latency is unknown.

Then the link check fell back to ping when the array's test printed no number (SPEC-020 R2a, the
choice taken that day: block, ping, or continue unmeasured; ping). Rerun (run b8e5f956): **28 PASS /
0 FAIL**. Both links measured with 10 pings each, 0.089 ms and 0.106 ms, each with its detail
*Measured with ping: … printed 'Average measured latency: min ms' with no number …*; groups created
and replicating; failover 2.3 s, synced back 2.1 s; the as-built marks the latencies *(ping)* and says
why; the removal set put the pair back; the Primera's gateway was restored.

What this shows, and what it does not. The router forwards the first packet and then sends an ICMP
redirect (`Redirect Host(New nexthop: 10.93.18.19)`, `tests/fixtures/rcip_pair/
controlport_rcip_ping_routed_redirect.txt`), and the array follows it: once a peer address has been
reached, the array talks to it directly, because both arrays sit on one network. So the run proves the
tool's side of a routed setup (address and gateway written and read back, the peer reached through
the gateway, targets, links, groups, failover, the latency gate and its fallback, the removal set). It
does not prove steady replication across a router between two networks: that needs two networks
that cannot reach each other directly.

## Still owed

- The Primera's old, empty FC target is in the journal and can be restored with
  `rcip_setup_lab.py undo`; the five groups removed with that target cannot. The gateway is back.
