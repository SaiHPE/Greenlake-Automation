# SPEC-031 — Remote Copy over Fibre Channel (RCFC)

**Status:** part A accepted 2026-11-17 (owner's decision); **part A built 2026-11-17, pending live run**
(BL-50, branch `feat/bl-50-rcfc-part-a`; R1 without the optional reads, R2–R4, R6 with the proposed answer
to §6 question 2, R7, R8); R5 done by BL-57; part B deferred ·
**Decision:** [ADR 0024](../adr/0024-rcfc-ports-and-targets.md) (part A accepted, part B deferred) ·
**Tracker:** BL-50 · **Research:** [2026-11-17-rcfc.md](../research/2026-11-17-rcfc.md) ·
**Work packet:** [BL-50](../workpackets/BL-50.md) ·
**Builds on:** SPEC-016 (groups), SPEC-020 (link check), SPEC-021 (RCIP partnership), ADR 0012 (zoning
command set) · **Shares with:** BL-26 peer ports (SPEC-025, ADR 0018, on the BL-26 branch): the FC
port-mode change, the free-port rule and the array-to-array zone block

## 1. Problem

Some customers replicate over Fibre Channel: an FC port on each array set to RCFC mode, zoned to the
other array's RCFC port, and a Remote Copy target of type FC. Today the Replication step finds a
partnership only by RCIP address. On an RCFC pair it says there is no partnership, tells the engineer
to name RCIP ports on the Replication network tab, and says the tool *"supports Remote Copy over IP
only"*, although every group call it makes (WSAPI `/remotecopygroups`, by target name) would work
unchanged. And when the workbook has a Replication network tab, it told the operator to remove any FC
target to the peer with `-cleargroups`, even a working one (research §6); BL-57 fixed that (R5).

Part A makes the step work on an RCFC partnership that already exists; the owner accepted it on
2026-11-17. Part B, the tool setting one up, is deferred (ADR 0024): it stays below as the design to
start from, and is built only if the owner re-opens it.

## 2. Part A — an existing RCFC partnership (first slice, no new write)

**R1 — Read.** No new command. `showport` rows keep each FC port's **port WWN** (column 5) beside the
node WWN, and the view keeps every FC node WWN the array shows, not only the first row's (a peer port
listed first has a `0202` node WWN of its own, research §2). `showport -rcfc` and `showrctransport
-rcfc` are read only after a capture pins their output (research §10); nothing below depends on them.

**R2 — The transport of a target** is the `Type` column of `showrcopy targets`: `IP` or `FC`. Every
partner target, the partnership, the plan notes, the page and the as-built carry it.

**R3 — The partnership by WWN.** Besides SPEC-016 R2's match by RCIP address: on A, a target of Type
`FC` whose Options equal one of B's FC node WWNs and whose outbound links all address B's FC port
WWNs; on B, the mirror image. A's FC target is paired with the B target whose links address the WWNs
of the ports A's links use. Names are never compared (as SPEC-016). A pair may have several FC targets
(a target per mode, as SPEC-016 R2), and SPEC-016's one-mode-per-target choice runs over them.

One pair, one transport. The arrays keep one partnership per pair, and an older target in one transport
stops a newer one in the other from working, without an error (LESSONS 44). So when the two arrays
show both IP and FC targets towards each other, the step does not pick one: it blocks with one sentence
naming both targets and their status, and plans nothing. The removal command is offered only on R5's
terms (a failed target, no link Up, no started group); a target in use is never offered for removal.

**R4 — Findings.** SPEC-016 R2's rules hold for FC targets (2 links Up each way, Remote Copy started,
one mode per target). The sentence *"this tool supports Remote Copy over IP only"* goes. When an FC
target to the other array exists, the "no partnership" finding no longer tells the engineer to name
ports on the Replication network tab (that tab sets up RCIP only). When an FC target exists but does
not resolve (its node WWN or a link WWN is not on the other array), one sentence names the target and
the WWN that did not match.

**R5 — Never offer to remove a working FC partnership. Done by BL-57** (branch
`feat/bl-57-fc-target-guard`, issue #33), not part of BL-50's work. SPEC-021 R3's blocker on an FC
target to the other array (`stale_fc_targets`) now prints `removercopytarget -cleargroups -f <t>` only
for a target that is `failed`, with no link Up and no started group, as live-tested on 2026-11-03. Any
other FC target to the peer blocks with a sentence that says the arrays already replicate over Fibre
Channel, names the target and what shows it is alive, and prints no removal command. BL-57's three
tests pin it; part A keeps them green.

**R6 — Latency.** The Support Matrix limit over RCFC is **10 ms for sync and for async** (research
§7). `RTT_LIMIT_MS` becomes a table per transport; every sentence names the transport (*"async
replication over Fibre Channel needs 10 ms or less"*). `checkrclink` is not run on FC links until its
help shows an FC form (research §2). For an FC partner target with something to create:
- the tab's *Measured round-trip time (ms)* stands in for the measurement. Blank: the apply is refused
  with *"Type the round-trip time between the arrays on the Replication tab: the tool cannot measure
  Fibre Channel links yet."* Over 10 ms: refused, with SPEC-020 R4's *Continue anyway* tick.
- the link-check gate (`_gate_on_link`) asks for the typed value, not an RCIP link check; the page
  offers no *Check the link* for FC targets and says why; the result's notes and the as-built say the
  latency was typed by the engineer, not measured.
A pair never mixes transports (R3), so a run's targets are all checked one way.

**R7 — Page and as-built.** The partnership line names the transport (*"over Fibre Channel, found by
port WWN"*). The array card lists the ports each target uses (`0:3:3 → 20330002AC02D495`) instead of
"RCIP: no configured ports". The as-built's partner table column *RCIP ports* becomes *Replication
ports* (an address, or an RCFC port with its peer WWN); the link-check paragraph says *typed* for FC.
`ReplicationStep.tsx` stops treating every partnership as RCIP (`const rcip = !!report?.partnership`).

**R8 — Groups, verify, failover test, removal set: unchanged.** They address the target by name over
WSAPI (SPEC-016 R4–R7, SPEC-017); verify finds the partnership through `find_partnership`, so R3
covers it. A unit test runs plan → apply → verify on an FC partnership to prove
nothing in them reads RCIP.

## 3. Part B — the tool sets RCFC up (deferred, ADR 0024)

Deferred on 2026-11-17: nothing of it can be proven in the lab, the command order is unknown, and no
one has measured how much RCFC is used. R9–R14 stay as the design to start from. Before any of it is
built: every item in ADR 0024 *Before part B*, then the owner's choice between option B (the array's
SSH, under ADR 0025) and option C (DSCC storage-fleet v1). Hard rules 1 and 7 hold as ADR 0024 says.

**R9 — The sheet.** A tab *Replication FC ports*: one row per FC port the partnership uses, on either
array. Columns: *Array* (`this` or `peer`), *Port* (N:S:P, a text cell). At least one port per node on
each array; ports pair node to node in sheet order (as SPEC-021 R1). A port named twice, or a workbook
with both this tab and the Replication network tab, is refused with a sentence (one partnership, one
transport). Without the tab nothing changes.

**R10 — Read, per array.** `showport`, `showport -par` (the connection mode to restore), `showport -c`
(`Mode_change`), `showhost -d` (logins), `showvlun -a` (exports), `showportdev ns <each named port>`;
and the run's two switches through the existing zoning read, to place each port's WWN on a fabric.

**R11 — Plan, partnership rows first, per array.**
1. *RCFC port*: **exists** when the port is already in RCFC mode; **create** (`controlport offline`,
   `controlport config rcfc -ct point -f`, `controlport rst` if the live run shows it is needed) when it
   is free: FC, Type `free`, no login, no export, `Mode_change` `allowed`, linked (`ready`), as SPEC-025
   sets for peer ports; **conflict** otherwise, with the reason (serving hosts, a peer port, no SFP,
   prohibited). A Label never decides (LESSONS 42).
2. *Zones* (the SAN team's): one zone per node pair, this array's RCFC port with the peer's, both
   WWNs read from the name server of one declared fabric. Rendered by the zoning designer's
   array-to-array block (the block BL-26 adds for peer ports), `cfgenable` shown apart (ADR 0012).
   A pair whose two ports are not on one declared fabric is a blocker naming both fabrics.
3. *Remote Copy interface*: `controlport rcfc init -f <nsp>` per port.
4. *Remote Copy service*: as SPEC-021 R3 (`startrcopy` when not started).
5. *Target*: on this array, named after the peer, `creatercopytarget <peer> FC <peer node WWN>
   <nsp>:<peer port WWN> …`; on the peer, the mirror image. Exists / conflict as SPEC-021 R3.

Blockers before anything is planned: R5; fewer than two ports per array on two nodes; mixed sync and
async rows (one target); a port the run's peer-port tab also names.

**R12 — Apply, in two phases.** Over the clients ADR 0025 allows (option B: the one array-port client
shared with ADR 0018, mode `peer` or `rcfc` only, for the port rows; `ArrayRcCliClient` for the Remote
Copy rows; each bound to the plan's ports and WWNs) or over DSCC v1 (option C). Stopping at the first
refusal (an `Error` line), each change read back. Each write's removal line is written before it is
sent, so the removal set is valid after phase 1 alone: a run that stops there, waiting for the SAN
team or for good, is undone from it (LESSONS 45).
- *Phase 1*: the RCFC port rows, this array then the peer. Read back: `showport -par` reads `rcfc
  point` (value to confirm live) and no other port's mode, Type or login changed (LESSONS 44). The
  step then stops and shows the zoning command set, built from the WWNs read **after** phase 1.
- *Phase 2*, its own approval: only when a fresh read shows each port seeing its planned partner (the
  partner's port WWN in `showportdev ns <nsp>`). Then `controlport rcfc init`, `startrcopy` where
  planned, the target on this array, then on the peer, then `showrcopy links` until every planned link
  is Up (3 minutes, as SPEC-021 R4). The order of `rcfc init` against the zones and the target is
  confirmed from the CLI guide or the manual lab run before this is built.

**R13 — Removal set** (SPEC-007; lines the operator pastes, this array first): `removercopytarget
<t>`; `stoprcopy -f -stopgroups -clear` only where the apply started Remote Copy on an array that had
none; per port the apply changed: `controlport rcfc delete -f <nsp>`, `controlport offline <nsp>`,
`controlport config <old connmode> -ct <old conntype> -f <nsp>` (from `showport -par` before) and
`controlport rst <nsp>` if phase 1 needed it. Then the peer. For the SAN team: `cfgremove`,
`zonedelete` and `alidelete` for what the command set added, `cfgenable` shown apart.

**R14 — Verify and as-built.** Links Up both ways; each port in RCFC mode; each port sees its partner.
The as-built names the RCFC ports with their WWNs before and after, the zones delivered, the targets,
every apply in order, and the typed latency.

## 4. Non-goals

Writing to a switch (ADR 0012); Cisco MDS; FCIP and its 120 ms limit (the array cannot tell FCIP from
RCFC; open question 4); an IP and an FC partnership to the same array (R3); Peer Persistence over FC;
the tool setting up a second FC target per pair; changing a port that has a login or an export; port
speed or label; any DSCC call in part A (DSCC v1 is ADR 0024 option C for part B).

## 5. Verification

**Part A, unit:** the Primera's FC target of 2026-11-03 (`tests/fixtures/rcip_pair/before/primera/`)
resolves to rack13-ARCUS by node WWN and link WWNs (`2FF70002AC02D495`, `20330002AC02D495`,
`21340002AC02D495`) and is reported failed, links Down; R3 blocks a pair that shows an IP and an FC
target towards each other; R4 drops the Replication network tab advice when an FC target exists; R6
refuses a blank RTT and 11 ms for an FC target (sync and async), takes 10; R8 on model objects of a
working FC pair (no capture of one exists). R5's tests are BL-57's and stay green. **Part A, live:** needs a working RCFC pair (research §4); until then *built, pending live
run*.

**Part B (if re-opened):** first a hand-run, journaled setup on the lab pair (as `lab/rcip_setup_lab.py` for RCIP)
that records every command and answer as fixtures; then unit tests pinned to them; then a tool run
that sets up, replicates, runs the failover test, and returns both arrays to their `before/` state
with its removal sets.

## 6. Open questions for the owner

1. ADR 0024: *answered 2026-11-17*: part A accepted, part B deferred.
2. R6: typed RTT required for FC, or a *Continue without a measured latency* tick? *Not answered; part A is
   built with the proposed behaviour, a typed RTT is required* (`gate_on_typed_rtt` in
   `application/replication/steps.py`). A tick would replace its first refusal.
3. The CLI guide ED8's RCFC section: the order of `rcfc init`, zoning and `creatercopytarget`. Part B
   only; on ADR 0024's *Before part B* list.
4. FCIP: ask the engineer on the tab (*links run over FCIP*, 120 ms async), or leave it out? *Not answered;
   part A applies the RCFC limit, 10 ms, to every FC pair.*
5. The lab: may two rack13 FC ports change mode (0:3:3 and 1:3:4 are free; 0:3:4 and 1:3:3 carry an
   ESXi login), and can the lab team put the Primera's RCFC ports on the same fabric with zones? Part
   A's live run needs a working pair either way; part B's list has it too.
6. Field input: how many deployments replicate over FC rather than IP? No public HPE figure was found.
   Asked before part B's ~550 lines and a lab rebuild.

## 6a. Part A as built (2026-11-17)

- **R1.** `parse_showport_roles` keeps each FC row's port WWN; `ReplicationArrayView.fc_node_wwns` and
  `fc_port_wwns` (both from `showport`) are the one source for the WWNs of an array, read by the partnership,
  the as-built and R5's guard (`stale_fc_targets` now matches every node WWN, so a peer port listed first no
  longer hides an FC target; its rule and sentences are BL-57's, unchanged). `fc_node_wwn` stays for SPEC-021.
  The optional reads (`showport -rcfc`, `showrctransport -rcfc`) are **not** read: no capture pins their
  output (research §10, step 0 of the work packet not done).
- **R3/R4.** `find_partnership` matches FC targets by node WWN and link WWNs and pairs them by the port WWNs
  in use; `Partnership.transport` and `PartnerTarget.transport` carry `IP` or `FC`. A pair with IP and FC
  targets towards each other is blocked with one finding and no plan (`ReplicationReport.mixed_transports`);
  the removal command is offered only for a failed target with no link Up and no started group. An FC target
  that does not resolve is named with the WWN that did not match: a blocking finding when no partnership is
  found, a plan note when an FC partnership is.
- **R6.** `RTT_LIMIT_MS` is a table per transport, read through `rtt_limit_ms(transport, mode)`. The sheet
  still refuses a typed time over the RCIP limit (it does not know the transport); the Replication step holds
  an FC pair to 10 ms at the apply, with *Continue anyway*. `checkrclink` is not run on FC links: its help
  has never been captured (R6's question, research §2), so the link check is refused for an FC pair.
- **R7.** Page: transport on the partnership line, FC links on the array cards, a *Round-trip time* panel in
  place of *Check the link* (mockup `frontend/mockups/screens/ReplicationFc.tsx`; screenshots not taken).
  As-built: *Replication ports* column, transport in the partnership sentence, a typed-latency paragraph.
- **R8.** `tests/unit/test_replication_rcfc.py` runs plan → apply → verify on the lab pair's captures
  carried over FC: the calls are the RCIP calls.

## 7. Size

Part A: read and partnership (~80 lines), findings and limits (~40), page and as-built (~60), ~12 unit
tests; R5 is not counted (BL-57). Part B, deferred: sheet (~60), plan (~180), two-phase apply (~150),
zoning block shared with BL-26 (~40 on top of it), client forms (~40), removal and verify (~80): about
550 lines, ~30 unit tests, one lab script and a lab rebuild.
