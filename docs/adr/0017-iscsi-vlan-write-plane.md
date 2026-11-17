# ADR 0017 — How the tool writes a VLAN-tagged iSCSI address to an array port

**Status:** accepted 2026-11-17 (owner's decision), with the changes below; follows ADR 0025 ·
**Spec:** [SPEC-024](../specs/SPEC-024-iscsi-vlans.md) · **Tracker:** BL-25 · **Follows:**
[ADR 0025](0025-one-rule-for-ssh-writes.md) (one rule for every write over the array's SSH; the forms
go on its one array-port write client) · **Keeps:** ADR 0001 (the read client stays read-only), ADR
0012 (no switch writes), ADR 0015 (`ArrayRcCliClient` is not widened)

Proposed on 2026-11-16 as *"A, if a live probe confirms it; otherwise C"*. On 2026-11-17 the owner
took C now, with the changes a review recommended: the forms go on ADR 0025's one array-port client,
every form carries `-vlan`, a first slice ships without the apply, and the forms are confirmed live
before the apply is built (Decision, points 1 to 7).

## Context

SPEC-024 has the tool add VLAN-tagged iSCSI interfaces to the array's iSCSI ports. The project's
rule is that array writes go over WSAPI after the operator approves a plan; the one SSH write path was
ADR 0015's, scoped to Remote Copy, until ADR 0025 (accepted 2026-11-17) set one rule for every write
over the array's SSH. What each candidate write plane is known to offer, from sources in hand on
2026-11-16 and 2026-11-17:

| Source | What it confirms |
|---|---|
| python-3parclient 4.5 (installed), `client.py` `_getIscsiVlan` and `getPorts` | **Read only**: `GET /ports/<n:s:p>/iSCSIVlans/`, called when a port's `iSCSIPortInfo.vlan == 1`. The SDK has no method that creates, changes or deletes an iSCSI VLAN. Its unit test mocks a VLAN record as `IPAddr`, `gateway`, `tpgt`, `vlanTag` (a mock, not a capture: github.com/hpe-storage/python-3parclient `test/test_HPE3ParClient_ports.py`, read 2026-11-16) |
| HPE 3PAR / Primera WSAPI reference | Not in hand. A POST / PUT / DELETE on `/ports/<n:s:p>/iSCSIVlans[/<tag>]` is recalled from that guide but **unconfirmed** |
| DSCC storage-fleet API, offline mirror `reference/greenlake_api_docs/.../ports/devicetype4iscsiportedit.md` (scraped 2026-06-07) | **Write, documented**: `PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi` with `vlans[]` = `vlanId`, `ipAddress`, `netMask`, `gatewayAddress`, `sendTargetGroupTag`; answers `202` and a task URI. Whether `vlans` replaces the port's whole list or adds to it is not said. `edit-rcip` has no VLAN field |
| Array CLI help captured on the lab (`tests/fixtures/rc_pair/help/help_controlport.txt`, OS 10.5) | `controlport` carries `-vlan` for `file` and `nvme` only, none for `rcip` or iSCSI. The Primera's help names `controliscsiport addr` and `delete`. `help controliscsiport` was never captured, so the iSCSI VLAN create and delete forms are **unconfirmed** (captured since: the two rows below) |
| `help controliscsiport`, `help controlport` and WSAPI GETs, **rack13-ARCUS, OS 10.6.0, 2026-11-16** (`tests/fixtures/iscsi_vlan/rack13/`) | **CLI forms confirmed**: `controliscsiport addr <IP_address> <netmask\|prefix_len> [-vlan <vlan_tag>] [-f] <node:slot:port>`, `gw <gw_address> [-vlan <vlan_tag>] [-f] <node:slot:port>`, `delete [-vlan <vlan_tag>] [-f] <node:slot:port>`, tag 1 to 4094. Without `-vlan` the same commands change or delete the port's untagged address. On this OS `controlport rcip` takes `-vlan` too (it did not on 10.5). **WSAPI read confirmed, write still not**: `GET /ports/<n:s:p>/iSCSIVlans/` answers `{"iSCSIVlans": [], "total": 0, "links": [...]}` on every iSCSI port, leaving out the untagged address; the GETs show nothing about a POST or DELETE |
| The same capture on **D22U27 (OS 10.5.0), VZ (OS 10.5.51) and E18U31 (OS 10.5.60), 2026-11-17** (`tests/fixtures/iscsi_vlan/D22U27/`, `VZ/`, `E18U31/`) | **The CLI forms hold on OS 10.5 too**: the three print one and the same `help controliscsiport`, with `addr`, `gw` and `delete` taking `[-vlan <vlan_tag>]` exactly as on 10.6.0 (tag "1 to 4094"). `controlport rcip` takes no `-vlan` on any of them. **WSAPI**: the iSCSIVlans GET answers with the same envelope; on 10.5.60 it lists the untagged address as a record with `vlanTag` 0 (fields `IPAddr`, `netmask`, `gateway`, `vlanTag`, `mtu`, `stgt`, `tpgt`, `iSNSAddr`, `iSNSPort`), which 10.6.0 left out. Still nothing about a write |

## Options

**A — Array WSAPI, `/ports/<n:s:p>/iSCSIVlans`.** Same plane, client and approval machinery as host,
volume and Remote Copy group writes; no new client; no allowlist change. The SDK has no write
method, so the adapter would call the SDK's own `http.post` / `http.delete` directly, which no
adapter does today. Not confirmed: the route, the body and the delete. LESSONS 28: a fake proves
nothing about the body; one live probe on a lab port pins it.

**B — DSCC storage-fleet `edit-iscsi`.** The only write documented in a source in hand. Costs: the
tool has no DSCC data-plane client (ADR 0006 lists it as a gap); the run would need GreenLake API
credentials with DSCC rights; the call is asynchronous (task polling); its semantics for an existing
VLAN list are unknown; and the write goes through the cloud, so an array not yet connected to DSCC,
or a jump box without the cloud path, cannot use it.

**C — A write-scoped SSH form, the ADR 0015 way.** `controliscsiport` create forms, each checked
for its whole shape (port, tag 1 to 4094, IPv4 address and mask), on a client built only inside the
apply of an approved plan. Works with the CLI dialect the tool already reads back. Costs: a write over
SSH beyond Remote Copy (proposed as a wider ADR 0015 client or a third client; ADR 0025 has since
settled where it goes: one array-port client); the forms must be pinned to the array's own help
(captured since, on OS 10.5 and 10.6).

**D — Command set only.** The plan prints the `controliscsiport addr` and `gw` lines; the engineer
pastes them on the array's CLI; the tool reads the array again and verifies. *For:* no new write path
and hard rule 2 untouched; the plan, the lines, verify and the as-built are the same code as C without
the apply. *Against:* the owner turned this shape down for array-side writes on 2026-10-07 (ADR 0015):
the tool already writes to this array, in a CLI dialect it reads. The operator types what the tool
could have run with the same checks, and nothing checks a paste before it runs: a line pasted without
`-vlan` changes the port's untagged address and cuts off the hosts logged in on it.

## Decision (accepted 2026-11-17)

**C, the CLI forms, on ADR 0025's one array-port write client. A later; B on record. The first slice
prints the lines and applies nothing, which is D in practice.**

1. **The write plane is C**: the `controliscsiport` forms, the same in the help of OS 10.5.0, 10.5.51,
   10.5.60 and 10.6.0 (table above). **A becomes a later swap**, once a WSAPI iSCSI VLAN write for OS
   10.5 is documented and probed on a lab port (LESSONS 28). Until then the read-back is `showport
   -iscsivlans` over the read client on every OS, because WSAPI's iSCSIVlans read differs by OS: only
   10.5.60 lists a record (the untagged address, `vlanTag` 0), 10.6.0 leaves it out, and `GET /ports`
   on 10.5.0 and 10.5.51 has no `iSCSIVlans` field at all. `parse_iscsi_vlans_wsapi` stays built and
   pinned, unused until A.
2. **One array-port write client** (ADR 0025 condition 7), shared with ADR 0018 (peer ports) and ADR
   0024 part B (RCFC ports); **not** `ArrayRcCliClient`, and ADR 0015 is not amended. The apply builds
   it from the (port, form family) pairs of the approved plan, so a VLAN apply's client takes the iSCSI
   VLAN forms on the plan's ports and nothing else: `controlport offline`, `controlport config` or any
   other family is refused, even on the same port. A VLAN apply can never take a port offline.
   Whichever of the three features is built first creates the client (ADR 0018 proposes
   `ArrayPortCliClient` in `adapters/array/port_cli_client.py`).
3. **Safety: `-vlan` on every form.** The client accepts only forms carrying `-vlan` with a tag of 1
   to 4094. Without `-vlan`, `addr` and `delete` act on the port's untagged address, the one the hosts
   already logged in use, and cut them off. The removal set (text the operator pastes, SPEC-007) never
   prints a `delete` without `-vlan` either: the help's own example, `controliscsiport delete -f
   1:1:1`, deletes the port's whole iSCSI configuration.
4. **First slice: no apply.** Read, plan, the printed CLI lines, verify and the as-built (SPEC-024 R1
   to R3 and R6 to R8). No write client, no tick, no apply button.
5. **Confirm live before the apply is built**, with the owner's yes, on the array's CLI, with
   `lab/iscsi_vlan_capture.py` (read-only) run before and after. The candidate array is rack13-ARCUS:
   iSCSI ports 0:4:1 and 1:4:1 ready on 10.93.18.0/23 behind 10.93.18.1, two lab hosts logged in
   (2026-11-16). It must show:
   - `addr ... -vlan N` leaves the untagged address and its sessions alone (`showport -iscsi` and
     `showhost -d` compared before and after);
   - `delete -vlan N` removes VLAN N only;
   - `-f` never prompts, on `addr`, `gw` and `delete`;
   - a tagged row, captured into `tests/fixtures/iscsi_vlan/tagged/`, including the `*` that `showport
     -iscsi` puts after an address when the port has VLAN addresses. `parse_iscsi_ips` (discovery's
     address column) keeps the star today; it is fixed on that capture before the apply.

   If one of these does not hold, the apply is not built and the tool stays at the first slice.
6. **Then the apply: create only, two forms**, both with `-vlan`:
   `controliscsiport addr <ip> <netmask> -vlan <tag> -f <n:s:p>` and
   `controliscsiport gw <gw> -vlan <tag> -f <n:s:p>`. No `delete` on the client, no port taken
   offline, no role changed. The rest is ADR 0025: each form a whole-command pattern, with tests that
   refuse its near-misses (no `-vlan`, tag 0 or 4095, no `-f`, a port or a form family the plan does
   not name, `delete`, the shell and Tcl characters); the client built only inside the apply of an
   approved plan; each create's removal line (`controliscsiport delete -vlan <tag> -f <n:s:p>`) in the
   run's removal set before its `addr` is sent; `showport -iscsivlans` read after each write, and the
   apply stopped if the interface is missing or the port's untagged row changed.
7. **B stays on record** for when the tool gains a DSCC data-plane client for another reason
   (snapshots, BL-21).

Unchanged: the switch is never written (ADR 0012). The network team gets a sentence, which now also
says to keep the untagged (native) VLAN: a trunk port with no native VLAN would drop the hosts on the
untagged address (SPEC-024 R3). VLANs on RCIP ports stay out of scope (owner, 2026-11-17; SPEC-024 §2).

## Consequences

- SPEC-024 R1 to R3 and R6 to R8 are the first slice. R4 (apply) and the lines of R5 wait on the live
  confirmation and the owner's yes.
- The first slice changes no allowlist and adds no write client. The apply adds the array-port client,
  or two forms on it if ADR 0018 or ADR 0024 part B built it first; the pull request says so plainly,
  with the tests and the live capture (ADR 0025 condition 7). Hard rule 2 in `AGENTS.md` names ADR
  0025's rule, not a list of clients; the sentence there and in `.github/instructions/adapters.instructions.md`
  that names today's write clients gains the port client in that pull request.
- SPEC-024 follows: R3's CLI lines are the write (the plan carries no WSAPI call), the network team's
  sentence keeps the native VLAN, R4 is create-only on the port client, R5's lines are written before
  each send (ADR 0025 condition 4), and §6 starts with the live confirmation.
- If A is taken later, the client's two forms give way to WSAPI calls; the plan, the printed lines,
  the read-back, the removal set, verify and the as-built stay as they are.
