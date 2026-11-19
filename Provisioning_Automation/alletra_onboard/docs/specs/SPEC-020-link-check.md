# SPEC-020 — Link check: the latency between the arrays, measured before replication

**Status:** PROPOSED 2026-10-12 from field feedback (operator: "port is configured but before
replication we have to do that start stop and show the latency"; "give option to continue or not by
latency"). Built the same day. **Live on one array 2026-10-12** (`rc_link_solo_lab.py`, D22U27's two
RCIP ports, 8/0: the sequence, the read-until, the parser, the stops — fixtures `rc_pair/D22U27/checkrclink_*.txt`);
the pair, the gate and the page wait for the replacement peer (TRACKER BL-42).
**Live on a pair 2026-11-03 to 2026-11-06** (Alletra MP rack13-ARCUS → Primera PRIMERA630R11U22, BL-41 runs
fadc7d54, 4dc6331e, 29d4a304, b8e5f956, and through the screens 179121cc): R1 to R3, R2a, R6, and R4 and R5 in the
*not measured* and *within the limit* states. **Built, pending live run (2026-11-16):** the over-the-limit
path of R4 and R5 (the refusal, *Continue anyway*, the accepted note in the result and the as-built) and the
per-link verdict column. The lab pair measures 0.02 ms, so it cannot show them. **Closed 2026-11-17 on the owner's
decision:** the over-the-limit path stands on its unit tests, since no lab pair is over 10 ms; a live run is still welcome
when one is. One known limit: every link
is judged against every mode on the sheet, whatever target it carries. See the addendum.
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
checkable with the reason, and the others are checked. RCIP only: a Fibre Channel partnership gets
the sentence *"The link check measures RCIP links; this pair replicates over Fibre Channel. Type the
round-trip time between the arrays on the Replication tab instead."*, the check is refused, and the
apply's gate takes the typed round-trip time against the FC limit instead
([SPEC-031](SPEC-031-rcfc.md) R6, built 2026-11-17).

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

5. After the last pair, on A and on B: `showrcopy links`. A link that was Up in the preview's read
   and is not Up again within 60 s (read every 10 s) makes the check an error, never a pass. *Added
   2026-11-03:* on PRIMERA630R11U22 (OS 4.6.20) the server's route to A's address
   (`Adding route: 10.93.18.11 -> 10.93.18.1`, through the RCIP gateway) stayed after `stopserver`
   (a second `startserver` answered `SIOCADDRT: File exists`), and every RCIP link went Down. The
   error names the links and the way back: on B, `controlport rcip state down -f` then `up -f` on
   the port (it keeps its address), which removed the route live.

A gateway on a B port whose A address is on the port's own network is a note before the test: the
server routes through the gateway anyway. When a pair loses every ping and the server routed
through a gateway, the pair's detail says so and that the gateway is not needed on one network.

**R2a — No number in the latency line.** *Added 2026-11-06:* with this array's ports on a /28 behind
the lab router 10.93.18.1, the client lost no ping and passed its MTU test, but printed `Average
measured latency: min ms`. The router answers every ping twice and sends an ICMP redirect, and the
array's test cannot work out a number from that. Then, after steps 3 and 4: on A,
`controlport rcip ping -c 10 <B's address> <A port>`; with no reply lost, the pair's latency is the
ping's average round trip, and its detail says it was measured with ping and why. Any lost reply
leaves the pair unmeasured, with both outputs. The as-built marks such a latency *(ping)*.

`checkrclink` is not a `show` command and never goes on ADR 0001's read allowlist. The SSH client
gets `run_diagnostic()`: a second allowlist of exactly `checkrclink startserver|stopserver|startclient|stopclient`
with the port as `N:S:P`, the address as a dotted IPv4 and the time as an integer in the array's
range, and `controlport rcip ping -c <1 to 20> <IPv4> <N:S:P>` (ICMP echo only, it changes nothing;
every other `controlport` form stays out); anything else is refused with a sentence. The Console prompt (SPEC-019 R3) keeps using the
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
apply is refused with *"Check RC link first: the latency between the arrays has not been measured
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
latency* panel: *Check RC link* (after the read; RCIP only), the progress lines while it runs, then
one row per pair (A port → B port, latency, pings lost, verdict against each mode's limit), the
pairs not checked with their reason, and *Check RC link again*. Over the limit: the tick-box *Continue
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

## Addendum 2026-11-16 — gap analysis (BL-42)

Each requirement against the code, the tests and the live records. *VR* is
[`validation/2026-11-03-rcip-partnership.md`](../validation/2026-11-03-rcip-partnership.md). A live claim cites
the VR, `docs/TRACKER.md`, this spec's status line or a capture under `tests/fixtures/`; what none of them
records is marked *not in the record*. Unit tests are in `tests/unit/test_replication_link_check.py` unless
another file is named.

| Req | Built | Live | Status |
|---|---|---|---|
| R1 the pairs | `link_check.plan_pairs`; `test_pairs_come_from_the_links_on_a_and_the_ports_on_b`, `test_a_link_whose_address_no_peer_port_carries_is_listed_not_checked`, `test_no_partnership_means_nothing_to_measure` | VR *The run* 18:54:48 (run fadc7d54): 2 links measured. The targets in the VR pair them: A 0:4:4 → 10.93.18.19 (B 0:1:1) and A 1:4:4 → 10.93.18.20 (B 1:1:1). A link that does not resolve: unit only (the lab pair has none). A fibre-channel pair never reaches the check: the read finds no partnership and the plan refuses it (`test_replication_plan.py::test_a_fibre_channel_only_pair_says_so`); no FC pair in the lab | Live |
| R2 the sequence | `link_check._check_pair`, `_links_still_down`; `cli_client.run_diagnostic` and its allowlist; `test_the_sequence_per_pair_is_…`, `test_a_refused_server_fails_the_pair_and_the_stops_still_run`, `test_run_diagnostic_*`, `test_links_left_down_after_the_check_are_an_error_with_the_way_back`, `test_a_gateway_on_b_…`, `test_no_reply_names_the_gateway_…` | On one array, 2026-10-12: the sequence, the read-until (the client read in under 2 minutes, not for the 600 s test), the stops and the 300 s floor: `lab/rc_link_solo_lab.py`, 8/0 (this spec's status line; captures `rc_pair/D22U27/checkrclink_*.txt`). On the pair: the server on B and the client on A, captures `rcip_pair/checkrclink_startserver_gateway.txt` and `checkrclink_startclient_lost.txt` (2026-11-03); VR *The run* 18:54:48: "Links still Up afterwards". Each pair's commands in the console log: not in the record. Gateway note, no reply through the gateway, links left Down with the way back, and the way back working: VR *2026-11-06: the in-scope paths*, gateway row (run 29d4a304) and *How it got here*, try 1 | Live |
| R2a ping fallback | `link_check._ping_latency`; `test_a_latency_line_with_no_number_is_measured_with_ping_and_says_so`, `test_a_ping_that_loses_any_reply_leaves_the_pair_unmeasured` (captures `rcip_pair/checkrclink_startclient_routed_no_number.txt`, `controlport_rcip_ping_routed_redirect.txt`) | VR *2026-11-06: through a router*, run b8e5f956: 0.089 ms and 0.106 ms, 10 pings each; the no-number refusal before it, run 1b2cfe2d. A ping that loses a reply: unit only | Live |
| R3 the result | `LinkCheck`, `steps._run_link_check`, artifact `link_check`, events `replication.link_checked` / `.failed`; `test_onboarding_service.py` (link check in the replication test), `test_within_the_limit_is_told_apart_from_over_it` | Run fadc7d54: *Latency 0.018 ms on 2 link(s) (sync needs 10 ms or less) — within the limit.*; async run 4dc6331e: *… (async needs 200 ms or less)*; a failed check, run 29d4a304 (VR, gateway row). Progress lines in order: `rc_link_solo_lab.py`, 8/0 (R2) | Live |
| R4 the gate | `steps._gate_on_link`, `start_replication_apply`; `ReplicationApplyRequest.accept_latency`; sheet rule in `init_sheet.py`; `test_onboarding_service.py::test_the_link_gate_refuses_over_the_limit_without_the_tick_…` (with a *nothing to create* case added 2026-11-16), `test_replication_sheet.py::test_rtt_within_limits_is_accepted_for_both_modes` | No check → 409 *Check the link first*: VR *The run* (fadc7d54). Within the limit → the apply went through after the check: fadc7d54, 4dc6331e, b8e5f956; **the result's note (*… within the limit.*): not in the record**. Unmeasured → refused: 29d4a304, 1b2cfe2d. A sync sheet with no typed RTT accepted: every BL-41 run (the runners' sheet, `lab/rcip_pair_lab.py` `compose_body`, has none). **Over the limit → refused without `accept_latency`, allowed with it, the accepted note: unit only.** *Nothing to create* before the gate: the sentence live 2026-10-11 (`rc_preset_lab.py` 7c, 32/0 in TRACKER BL-20), before the gate existed; unit since 2026-11-16 | **Built, pending live run** (over the limit, and the result's note) |
| R5 the page | `ReplicationStep.tsx`: *Check the link* section between *What the arrays say* and *Review the plan*, progress, one row per link, *Not checked*, *Check again*, the tick-box, the three gate texts. **Added 2026-11-16:** an *Against the limit* column, the verdict for each mode on each link (it was only on the summary line); a check that ended in an error shows `--` there | VR *2026-11-05: through the screens*, run 179121cc: *Check the link* not done, then 0.02 ms and the groups configured, 2 of 2 replicating. **Over the limit (status line, tick-box) and the new column: not seen live** | **Built, pending live run** |
| R6 as-built | `asbuilt._add_link_check`; `test_the_as_built_states_the_measured_latency_and_the_operators_choice` | Run b8e5f956 (VR *through a router*): the as-built marks the latencies *(ping)* and says why. The paragraph's wording for a `checkrclink` latency: not in the record. The accepted wording: unit only (it follows R4) | Live, except the accepted wording |
| R7 runners | `lab/rc_link_lab.py`, `lab/rc_preset_lab.py` (check between preview and apply). Both point at the D22U27/E18U31 pair (their docstrings), which the BL-41 runs do not use; no run of `rc_link_lab.py` is recorded | Superseded by `lab/rcip_tool_lab.py` (preview, apply refused until checked, link check, apply), live 25/0, 27/0 and 28/0, and `lab/rcip_scope_lab.py` (the gateway case), 35/0 | Live (through the BL-41 runners) |
| Limit: every link against every mode | `LinkCheck.over_limit`, `asbuilt._add_link_check` and the page (status line and *Against the limit*) judge the measured latency against every mode on the sheet, whatever target each link carries | Cannot arise on the lab pair: the partnership the tool sets up has one target (VR *2026-11-06: the in-scope paths*, first row) | **Known limit**, below |

Two corrections to the text above. The panel is titled *Check RC link* (*Check the link* until 2026-11-19), not *Link latency*. §4's "six
commands per pair" is five `checkrclink` commands per pair (stop server, start server, start client, stop
client, stop server), then one `showrcopy links` on each array after the last pair, and a
`controlport rcip ping` per pair only when R2a applies.

**Renamed 2026-11-19 (owner, after the customer demo; BL-64):** the button, its *again* form, the part name in the
parts bar, the panel and section title, the sentences that tell the operator to press it and the apply's 409 text
say *Check RC link* (*Check RC link again*, *Check RC link first: …*) where they said *Check the link*. Behaviour is
unchanged. The table above keeps the old words where it quotes what a past run showed. The lab runners
(`rc_link_lab.py`, `rc_preset_lab.py`, `rcip_tool_lab.py`) look for the new 409 text.

### Known limit: every link is judged against every mode on the sheet

`plan_pairs` measures the links of every target this run uses (one per mode, `target_by_mode`).
`LinkCheck.over_limit` then compares the worst latency with the limit of every mode on the sheet; the
as-built paragraph does the same, and the page's *Against the limit* column compares each link with every
mode. On an existing partnership with one target per mode (a sync target and an async target, the HPE
layout), a link that carries only the async target is still judged against sync's 10 ms. An async link at
40 ms reads *Over sync (10 ms)*, and the gate refuses to configure the sync groups until the operator ticks
*Continue anyway*, although no sync group uses that link. The partnership the tool sets up has one target,
so the limit only arises on a partnership that was already there.

Not changed in BL-42. The fix: record the link's target on `LinkPair` (`plan_pairs` has it, `RcLink.target`),
and judge each link only against the modes whose target it carries (`target_by_mode`). Change the backend
(`over_limit`, the gate's sentence, the result's note, the as-built paragraph) and the page (status line
and column) together, so the page and the gate never disagree. A unit test with two targets, one per mode,
pins it.

### What the live run must show to close BL-42

It needs a pair whose measured round trip is over 10 ms: two sites over a WAN, or a delay inserted
between two RCIP networks. The lab pair measures 0.02 ms and cannot show it. On a sheet with one sync row:

1. *Check RC link* measures every link. Each row's *Against the limit* reads *Over sync (10 ms)*. The
   status line reads *The measured latency is N ms, over HPE's limit for sync*, and *Configure replication*
   is blocked.
2. The apply without the tick answers HTTP 409: *The measured latency is N ms; sync replication over RCIP
   needs 10 ms or less. Tick 'Continue anyway' to configure it regardless.* Nothing is written.
3. The tick-box *Continue anyway: I accept the measured latency of N ms for sync replication.* enables
   *Configure replication*; the groups are created and verified replicating.
4. The result's note reads *Link check …: latency N ms on 2 link(s); over the 10 ms limit for sync — the
   operator accepted it and chose to continue.*
5. The as-built's *Link check* paragraph says the latency was over HPE's limit for sync and that the
   operator accepted it and continued.
6. The run's removal set puts the pair back where it started.

The column alone can be seen on the lab pair: after a link check each row reads *Within sync (10 ms)*
(screenshots at 1366 × 768 and 1080 × 720).

If no pair over 10 ms can be found, the owner decides whether the unit tests for the over-the-limit branch
are enough to close it.
