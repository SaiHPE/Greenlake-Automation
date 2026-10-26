# SPEC-020 — Link check: the latency between the arrays, measured before replication

**Status:** PROPOSED 2026-10-12 from field feedback (operator: "port is configured but before
replication we have to do that start stop and show the latency"; "give option to continue or not by
latency"). Built the same day. **Live on one array 2026-10-12** (`rc_link_solo_lab.py`, D22U27's two
RCIP ports, 8/0: the sequence, the read-until, the parser, the stops — fixtures `rc_pair/D22U27/checkrclink_*.txt`);
the pair, the gate and the page wait for the replacement peer (TRACKER BL-42).
**ADRs:** [0001](../adr/0001-post-init-verification-via-ssh-cli.md) (addendum: `checkrclink` is the one
non-`show` command the SSH client runs, on its own allowlist) · [0015](../adr/0015-tool-configures-remote-copy-write-scoped-ssh.md)
(the same check runs before the tool configures links and targets in v0.19)
**Owner:** `adapters/array/cli_client.py` (`run_diagnostic`), `application/replication/link_check.py`,
`application/replication/steps.py` (step + apply gate), `api/app.py` (`POST /runs/{id}/replication/link-check`),
`frontend/src/steps/ReplicationStep.tsx`, `application/documents/asbuilt.py`

## 1. Problem

HPE's limits for Remote Copy over RCIP are a round-trip time of 10 ms for sync and 200 ms for
async (Support Matrix). Today the tool takes the RTT as a number typed on the Replication tab
("Measured round-trip time (ms)") and refuses a sheet that is over the limit. Nobody measures it
for the sheet. HPE's own procedure before configuring replication is `checkrclink`: a test server
on one array's Remote Copy port, a test client on the other's, and the latency it prints. Field
engineers do it by hand from two CLI sessions (screenshots, 2026-10-12: `checkrclink startserver
4:5:4` on B, `checkrclink startclient 4:5:4 <B's address> 600` on A, "Average measured latency:
200 ms", then stop both). The tool should do it, show the latency against the limit for the mode
on the tab, and let the operator decide to go on or not.

## 2. Requirements

**R1 — The link pairs.** From the Replication preview's read (SPEC-016 R1): for the target(s) this
run uses, every outbound link on A toward B gives a pair *(A's port, A's address) → (B's port, B's
address)*: A's address from `showport -rcip` for the link's port; B's port is the one whose RCIP
address equals the link's address. A link that does not resolve on both sides is listed as not
checkable with the reason, and the others are checked. RCIP only: a fibre-channel partnership gets
the sentence *"The link check measures RCIP links; this pair replicates over fibre channel"* and
no gate (R4).

**R2 — The test, per pair, in this order, all over the run's SSH credentials.**
1. On B: `checkrclink stopserver <B port>` (a server left by an earlier, interrupted check runs for
   48 hours by default; the stop is ignored when nothing was running), then
   `checkrclink startserver <B port> <A's address>`.
2. On A: `checkrclink startclient <A port> <B's address> <time>`. The client prints the latency
   first ("Measuring link latency … Average measured latency: N ms / Pings Lost: N %") and then
   starts a throughput test that runs for `<time>`. The tool reads the client's output only until
   the *Pings Lost* line (or 120 s), then
3. on A: `checkrclink stopclient <A port>`, and
4. on B: `checkrclink stopserver <B port>`.

Steps 3 and 4 run whatever happened in 1 and 2 (a failure to start the client still stops the
server). `<time>` is 600 s unless the request says otherwise; the array accepts 300 to 172800
(CLI reference). The throughput part of the test is not waited for (non-goal §3).

`checkrclink` is not a `show` command and never goes on ADR 0001's read allowlist. The SSH client
gets `run_diagnostic()`: a second allowlist of exactly `checkrclink startserver|stopserver|startclient|stopclient`
with the port as `N:S:P`, the address as a dotted IPv4 and the time as an integer in the array's
range; anything else is refused with a sentence. The Console prompt (SPEC-019 R3) keeps using the
read allowlist and cannot reach it. Every command is recorded in the command log like any other.

**R3 — The result.** Per pair: the latency in ms, the pings lost in %, and the client's output up
to the stop; or *failed* with the array's words. The report: when it ran, the test length, the
pairs, the pairs not checked and why, the modes on the tab with HPE's limit for each, and the
worst latency. Stored as the run artifact `link_check`; emitted as `replication.link_checked`
(or `replication.link_check.failed`) with the report in `data.link_check`; progress lines name
each step ("Starting the test server on B 0:4:3", "Measuring latency A 0:4:3 → 10.54.154.192 …",
"Stopping the client on A", "Stopping the server on B").

**R4 — The gate, and the option to continue.** When the partnership is RCIP and the plan has
something to create, *Configure replication* needs a link check from this run: without one the
apply is refused with *"Check the link first: the latency between the arrays has not been measured
in this run."* When the worst latency is over the limit for a mode on the tab, the apply is refused
with *"The measured latency is N ms; sync replication over RCIP needs 10 ms or less. Tick 'Continue
anyway' to configure it regardless."* until the request carries `accept_latency: true`; the page
offers that tick-box only in that case, and the result's notes and the as-built say the operator
accepted a latency over the limit. Pings lost above 0 % is a warning line, never a gate. A rerun
whose plan has nothing to create is refused as before (*nothing to create*) and does not need a
check.

The sheet's "Measured round-trip time (ms)" stays, optional for every mode (the rule *sync but RTT
blank* is dropped: the tool measures it). A typed value over the limit is still refused at upload
(the operator knew the value when filling the sheet).

**R5 — The page.** On the Replication step, between *What the arrays say* and *Plan*, a *Link
latency* panel: *Check the link* (after the read; RCIP only), the progress lines while it runs, then
one row per pair (A port → B port, latency, pings lost, verdict against each mode's limit), the
pairs not checked with their reason, and *Check again*. Over the limit: the tick-box *Continue
anyway — I accept the measured latency* enables *Configure replication*. The step's gate text says
which of the three states applies: not measured, measured within the limit, measured over it.

**R6 — As-built.** The replication section gains a *Link check* paragraph: when, each pair with its
latency and pings lost, the limit for the configured mode, and whether the operator accepted a
latency over it. Absent when no check ran.

**R7 — Runner.** `rc_preset_lab.py` runs the check between preview and apply and asserts the latency
is within the limit on the lab pair. A read-only `rc_link_lab.py` runs the preview and the check and
nothing else, for the first live run.

## 3. Non-goals

Throughput (the client's second phase): the operator who wants it runs the full test from *Open
terminal*; the tool stops after the latency. VLAN-tagged RCIP ports (`-vlan`) and FCIP (`-fcip`).
A CPU check before the test (HPE: do not run it when CPU use is near 100 %). Configuring the ports
(v0.19, ADR 0015).

## 4. Verification

Unit: the pairs from the rc_pair fixtures (two links, both resolved; an unresolved address listed);
`run_diagnostic` refuses `checkrclink` with a bad port, address, time or subcommand, and refuses
every other command; the sequence on a fake pair (stop, start server, client read until *Pings
Lost*, stop client, stop server — in that order, and the stops still run when the client fails);
the parser on the screenshot's lines; the gate (no check → refused; over the limit → refused
without `accept_latency`, allowed with it; nothing to create → the old sentence); the as-built
paragraph. Live: on the lab pair, the check from the page, both links measured, the console log
showing the six commands per pair, then the apply.

## 5. Size

`run_diagnostic` + allowlist (~60 lines), `link_check.py` (~150), step + gate (~70), route + schema
(~25), page panel (~120), as-built (~25), sheet rule (~5), ~18 unit tests, two lab scripts.
