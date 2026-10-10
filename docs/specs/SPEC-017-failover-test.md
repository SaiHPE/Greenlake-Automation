# SPEC-017 — Failover test

**Status:** APPROVED 2026-10-07 (operator: failover testing is required); **re-cut the same day** —
the role changes go through WSAPI's disaster-recovery action on `/remotecopygroups`, not SSH.
**Built 2026-10-10, not yet run live:** `application/replication/failover.py` (the R2 sequence,
R3 timings, R5 stop with the observed state and the ED6 way back), `WsapiClient.remote_copy_dr_action`,
`POST /runs/{id}/replication/failover-test` (R1 group rule: the test group or a group this run
created; any other group only with its name typed back), the Failover test step page (R4 tick-box
and button), the as-built section (R6). 11 sequence tests on a fake pair that moves roles the way
the arrays do, plus service, API and as-built tests. Checked on the Mac through the real HTTP API
and UI against a faked pair (passed and failed screens). **First live run 2026-10-10 18:18** on
`zz_rc_test_rcg` (sync, lab pair): steps 0 to 3 as specified, action 7 confirmed as failover. Then
the array differed from the table below: with both arrays up, the failover was mirrored to P
(**Secondary-Rev** at once, not Primary/Stopped) and the array **started the group from S by
itself** within seconds, so the recover sent at step 4 was refused (HTTP 403 code 284, *Remote copy
group not stopped*). The test stopped there as designed and named the right way back (restore on
S). Fixed the same evening: step 4 first watches for the array's own start and sends recover only
when it does not come; a code-284 refusal with the group already recovered is not a failure. Also
fixed: `Syncing (100%)` in the SyncStatus column. **Second live run 18:45** (same group, after the
script had swapped its direction back with stop, `setrcopygroup reverse`, start): steps 0 to 5
passed, step 4 correctly sent no recover. Then the array did one more thing the table below does not
say: as soon as the sync back finished, it turned Primary-Rev/Secondary-Rev into plain **Primary on
S and Secondary on P** (the peer became the group's natural primary), and `restore` was refused
(HTTP 400 code 29, *the role of group … was not previously switched*). The first run's state 25
minutes later was the same, so this is the array's normal behaviour with both arrays up, not a
race. Step 6 now restores only while the roles still carry -Rev; otherwise it fails back the way the
failover went, from the other side (stop on S, failover on P) and waits for the array to settle on
Primary/Secondary again. **Owed:** a clean live pass, sync then async.
**ADR:** [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md) §4 (DR operations are
WSAPI calls on the write plane provisioning already uses)
**Depends on:** SPEC-016 (a replicating group)
**Research:** [2026-10-07](../research/2026-10-07-replication-document-review.md) §4.1; the
`setrcopygroup -h` capture (D22U27); troubleshooting guide ED6, role/status table p.34; the
`hpe3parclient` DR action codes (`recoverRemoteCopyGroupFromDisaster`, values 6–11)
**Owner:** `application/replication/failover.py`, `frontend/src/steps/FailoverTestStep.tsx`,
`application/documents/asbuilt.py` (record)

## 1. Problem

A customer's acceptance of a replication deployment includes proving that the DR copy can take over
and that production can come back. Done by hand it is a sequence of role-changing commands on two
arrays whose order matters, with states to check between each. The tool configured the group; it
should be able to prove it — on a group where that is safe — and write the proof into the as-built.

## 2. Requirements

**R1 — Which group.** By default the tool's own test group `zz_rc_test_rcg` (SPEC-015 R3), created by
the Replication step for this purpose. A production group may be chosen only by typing its name into a
confirmation field; the UI states that hosts lose access to the primary volumes for the duration if
they are running on them. Groups the run did not create are never offered by default.

**R2 — The sequence (1-to-1 sync and async; no host on the peer).** `switchover` (WSAPI action 8,
*migrate group*) is **not** used: per the array's own help it requires hosts connected to both arrays
with a persona supporting RTPG — the Peer Persistence topology, out of scope. The test is HPE's
planned-DR sequence. P = this run's array, S = the peer; every action is a
`POST /remotecopygroups/<group>` with the action code, issued through the array named in *Where*.

| # | Where | Action | CLI equivalent | Expected after (`showrcopy groups <group>` on both) |
|---|---|---|---|---|
| 0 | both | *(read)* | — | Primary/Started on P · Secondary/Started on S · all volumes Synced; async: last sync time recorded (the data-loss bound) |
| 1 | P | `stopRemoteCopy` | `stoprcopygroup -f <group>` | both Stopped |
| 2 | S | action **7** change to primary | `setrcopygroup failover -f <group>` | S: **Primary-Rev**; P: Primary, Stopped |
| 3 | — | *(read)* S's volumes are now read/write — recorded, not written to | — | — |
| 4 | S | action **9** change to secondary | `setrcopygroup recover -f <group>` | S: Primary-Rev, Started; P: **Secondary-Rev**; volumes syncing back to P |
| 5 | — | wait until Synced (async: one period + margin; sync: until Synced), ≤ 15 min, else stop and report | — | Synced |
| 6 | S | action **10** change to natural direction | `setrcopygroup restore -f <group>` | back to step 0: Primary on P, Secondary on S, Started, Synced |

Each step reads both arrays before continuing; an unexpected state stops the test at that step with
the observed roles/status and HPE's recovery action for that combination (ED6 p.34: *Primary/Failsafe
+ Primary-Rev/Stopped → recover or restore*; *Secondary-Rev/Stopped + Primary-Rev/Stopped → restore
or reverse natural*; *Primary-Rev/Stopped + Secondary/Stopped → reverse local natural*). The tool
does **not** run those recovery actions automatically — it shows them, as CLI lines.

`restore` alone would run the recover implicitly (captured help); the test runs step 4 separately so
the sync back to P is measured on its own. WSAPI 1.15 on both lab arrays serves `/remotecopygroups`
with `role` 1 Primary / 2 Secondary (BL-38 fixtures); the action codes' mapping to the CLI verbs comes
from the client's own documentation and is observed live on the test group before any production
group is offered. The sequence is not up for confirmation.

**R3 — Measured, not assumed.** The record captures: start/end time of each step, the roles and
status read after each, time to Primary-Rev (failover), time to Synced after recover, and — for
async — the last sync time before failover (data-loss bound = time since that sync).

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
sequence returns to the starting state; the record lands in the as-built.

## 5. Size

Sequence and state checks (~220), UI step (~200), as-built section (~60), ~20 unit tests. **One
release (v0.18)**, after v0.17 is live.
