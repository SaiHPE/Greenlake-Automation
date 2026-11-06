# SPEC-021 — RCIP ports and the partnership, set up by the tool

**Status:** built 2026-11-04, pending live run · **Decision:** ADR 0015 (layers 1–2 over a
write-scoped SSH client) · **Tracker:** BL-41 · **Lab:** Alletra MP rack13-ARCUS (10.132.30.121,
OS 10.5.55) → Primera PRIMERA630R11U22 (10.132.30.28, OS 4.6.20), 2026-11-03

## 1. Problem

The Replication step (SPEC-016) needs a partnership someone made by hand: RCIP addresses on both
arrays, Remote Copy started, a target on each array pointing at the other, links Up. A consultant
does that first on a new pair. The lab asked for the whole flow on a pair with nothing set up on
the Alletra side.

The manual setup on the lab pair (`lab/rcip_setup_lab.py`, 9 PASS) showed the exact commands and
their answers, and three things to guard against: a gateway on one network that routes the link
test away (SPEC-020 R2 step 5), a stale FC target on the peer for the same array (the new IP target
never binds: `SysName None`, and every group create fails with *"Failed to send message to target"*),
and a peer that keeps secondaries in a set on removal (SPEC-016 R7, fixed).

## 2. Requirements

**R1 — The sheet.** A tab *Replication network*: one row per RCIP port the run uses, on either
array. Columns: *Array* (`this` or `peer`), *Port* (N:S:P), *RCIP address*, *Netmask*, *Gateway*
(optional). A workbook without the tab parses as before (no partnership is set up). Two rows on one
port, a port named twice, an address used twice, or a netmask that is not a mask are refused with a
sentence. The ports pair node to node, in sheet order (this array's node-0 port with the peer's
node-0 port): every row needs a partner on the other array on the same node.

**R2 — The read.** The preview reads, besides SPEC-016 R1: `showport` (each port's mode, state,
type and protocol, and the FC node WWN).

**R3 — The plan, partnership rows first.** Per array, in order:
1. *RCIP port* per row: **exists** when `showport -rcip` shows that address and netmask on the
   port; **create** (`controlport rcip addr -f <ip> <mask> <port>`, plus `controlport rcip gw -f`
   when the row has a gateway) when the port is a free or RCIP Ethernet port with no address;
   **conflict** when the port has another address, or is not a free/RCIP Ethernet port (iSCSI,
   file, host, FC). The tool never changes a port's role or an existing address.
2. *Remote Copy service*: **exists** when started, **create** (`startrcopy`) otherwise.
3. *Target*: on this array, named after the peer's system name, links to the peer's addresses;
   on the peer, named after this array's name. **exists** when a target already has those links;
   **conflict** when a target of that name has other links, or a link (local port, peer address)
   already belongs to another target (the array allows one).

Blockers before anything is planned: an FC target on either array whose options carry the other
array's FC node WWN (*"…already has target X for this array over Fibre Channel, status failed. The
array binds one partnership per pair of arrays…"*, with the command to remove it and what that
removes). A Replication tab that mixes sync and async rows: the partnership has one target and a
target carries one mode, so the run is refused before anything is written. When the partnership is
planned, the groups are not: the plan says the groups come after
the partnership is up and the link checked (SPEC-020), on a second preview.

**R4 — Apply, partnership only.** Over `ArrayRcCliClient` (ADR 0015), in order, stopping at the
first refusal: RCIP addresses on this array, then on the peer; a ping from every this-array port to
its partner address (`controlport rcip ping -c 3`), any loss stops the apply; `startrcopy` where
planned; the target on this array, then on the peer; then `showrcopy links` on both until every
planned link is Up (3 minutes). Each command's answer is checked (an `Error` line is a refusal),
and each change is read back (`showport -rcip`, `showrcopy`, `showrcopy targets`).

**R5 — The removal set.** Exactly what the apply created, as lines the operator pastes, this array
first: `removercopytarget <target>`; `stoprcopy -f -stopgroups -clear` only when the apply started
Remote Copy on an array where it was not configured; `controlport rcip delete -f <port>` per
address the apply set. Then the same on the peer.

**R6 — The page and the as-built.** The plan table shows the new rows; the result lists them; the
as-built's replication section names the ports, addresses and targets the run set up, every apply in
order. The partnership plan has its own button (*Set up the partnership*) and approval sentence. After
it the step is not complete: it reads *partnership set up*, says nothing is replicated yet, and offers
*Read both arrays again* first. The approval box clears on every new read or apply, so the groups plan
is approved on its own. The sheet review lists the ports to set up.

## 3. Non-goals

RCFC, VLANs on RCIP ports, MTU other than 1500, more than one target per pair, changing or removing
anything the tool did not create.

## 4. Verification

Unit tests on the 2026-11-03 captures (`tests/fixtures/rcip_pair/`). Live: `lab/rcip_setup_lab.py
undo` on the lab pair, then a run that sets up the ports and the partnership, previews again, checks
the link, configures the groups, runs the failover test, and removes everything with its removal
sets.
