# SPEC-017 — Failover test

**Status:** APPROVED 2026-10-07 (operator: failover testing is required) — not implemented
**ADR:** [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md) (the DR operations are
on the write-scoped client's list)
**Depends on:** SPEC-016 (a replicating group)
**Research:** [2026-10-07](../research/2026-10-07-replication-document-review.md) §4.1; the
`setrcopygroup -h` capture (D22U27); troubleshooting guide ED6, role/status table p.34
**Owner:** `application/replication/failover.py`, `frontend/src/steps/FailoverTestStep.tsx`,
`application/documents/asbuilt.py` (record)

## 1. Problem

A customer's acceptance of a replication deployment includes proving that the DR copy can take over
and that production can come back. Done by hand it is a sequence of role-changing commands on two
arrays whose order matters, with states to check between each. The tool configured the group; it
should be able to prove it — on a group where that is safe — and write the proof into the as-built.

## 2. Requirements

**R1 — Which group.** By default the tool's own test group `zz_rc_test_rcg` (SPEC-015 R6), created by
the Replicate step for this purpose. A production group may be chosen only by typing its name into a
confirmation field; the UI states that hosts lose access to the primary volumes for the duration if
they are running on them. Groups the run did not create are never offered by default.

**R2 — The sequence (1-to-1 sync and async; no host on the secondary).** `switchover` is **not** used:
per the array's own help it requires hosts connected to both arrays with a persona supporting RTPG
(the Peer Persistence topology, out of scope). The test is the planned-DR sequence:

| # | Where | Command | Expected after (both arrays, `showrcopy groups <group>`) |
|---|---|---|---|
| 0 | both | *(read)* | Primary/Started on P · Secondary/Started on S · all volumes Synced |
| 1 | P | `syncrcopy -w <group>` *(async only)* | last sync time advanced; nothing lost by step 2 |
| 2 | P | `stoprcopygroup -f <group>` | both Stopped |
| 3 | S | `setrcopygroup failover -f <group>` | S: **Primary-Rev**; P: Primary, Stopped |
| 4 | — | *(read)* the secondary volumes are now read/write on S — recorded, not written to | — |
| 5 | S | `setrcopygroup recover -f <group>` | S: Primary-Rev, Started; P: **Secondary-Rev**; volumes syncing back to P |
| 6 | — | wait until Synced (async: one period + margin; sync: until Synced), ≤ 15 min, else stop and report | Synced |
| 7 | S | `setrcopygroup restore -f <group>` | back to step 0's state: Primary on P, Secondary on S, Started, Synced |

Each step reads both arrays before continuing; an unexpected state stops the test at that step with
the observed roles/status and HPE's recovery action for that combination (ED6 p.34: *Primary/Failsafe
+ Primary-Rev/Stopped → recover or restore*; *Secondary-Rev/Stopped + Primary-Rev/Stopped → restore
or reverse natural*; *Primary-Rev/Stopped + Secondary/Stopped → reverse local natural*). The tool
does **not** run those recovery actions automatically — it shows them.

The `-f` (no confirmation prompt) option and the optional `-t` for a single-target group are confirmed
in the captured `setrcopygroup -h` (D22U27). The `stoprcopygroup` and `syncrcopy` options, and the
array each DR command is issued on, are confirmed against their `-h` and the CLI guide in BL-38 before
implementation; the sequence is not. `restore` alone would run the recover implicitly (captured help);
the test runs `recover` separately so the sync back to P is measured on its own.

**R3 — Measured, not assumed.** The record captures: start/end time of each step, the roles and
status read after each, time to Primary-Rev (failover), time to Synced after recover, and — for
async — the last sync time before failover (the data-loss bound = time since that sync).

**R4 — Approval gate.** A separate tick-box and button (*Run failover test*), naming the group and
both arrays. Not part of *Configure replication*.

**R5 — Always ends in the starting state, or says why not.** If any step fails, the screen and the
record say which step, the observed state on both arrays and the one documented action that returns
the group to normal. Leaving a production group in Primary-Rev silently is the one outcome this spec
exists to prevent.

**R6 — As-built.** A *Failover test* section: group, mode, the table of R2 with times and observed
states, the async data-loss bound, result (**Passed** / **Failed at step n**).

## 3. Non-goals

Switchover / transparent failover (Peer Persistence); automatic failover policies; `reverse` other
than as a displayed recovery action; host-side validation (mounting the DR copy on a host). Unplanned
failure simulation (pulling links).

## 4. Verification

Unit: the R2 state machine over captured `showrcopy groups` outputs for each state (Primary/Started,
Primary-Rev, Secondary-Rev, Failsafe, Stopped), the stop-and-explain path for each unexpected
combination, the R3 timings. Live: on the lab pair, `zz_rc_test_rcg` async then sync — the full
sequence returns to the starting state; the record lands in the pair's as-built.

## 5. Size

Sequence and state checks (~250), UI step (~200), as-built section (~60), ~20 unit tests. One
release, after SPEC-016 (b).
