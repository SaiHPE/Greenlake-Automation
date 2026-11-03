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

## Still owed

- A run through the UI on the jump box (this one drove the API from a script).
- The Primera's gateway (10.93.18.1) and its old, empty FC target are in the journal and can be
  restored with `rcip_setup_lab.py undo`; the five groups removed with that target cannot.
- Async (periodic) over this pair.
