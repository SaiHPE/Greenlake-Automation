# ADR 0017 — How the tool writes a VLAN-tagged iSCSI address to an array port

**Status:** PROPOSED 2026-11-16 (not decided; the owner decides) · **Spec:**
[SPEC-024](../specs/SPEC-024-iscsi-vlans.md) · **Tracker:** BL-25 · **Keeps:** ADR 0001 (the read
client stays read-only), ADR 0012 (no switch writes), ADR 0003 (writes over WSAPI after an approved
plan) · **Would amend:** ADR 0015 only under option C

## Context

SPEC-024 has the tool add VLAN-tagged iSCSI interfaces to the array's iSCSI ports. The project's
rule is that array writes go over WSAPI after the operator approves a plan; the one SSH write path is
ADR 0015's, scoped to Remote Copy. What each candidate write plane is known to offer, from sources in
hand on 2026-11-16:

| Source | What it confirms |
|---|---|
| python-3parclient 4.5 (installed), `client.py` `_getIscsiVlan` and `getPorts` | **Read only**: `GET /ports/<n:s:p>/iSCSIVlans/`, called when a port's `iSCSIPortInfo.vlan == 1`. The SDK has no method that creates, changes or deletes an iSCSI VLAN. Its unit test mocks a VLAN record as `IPAddr`, `gateway`, `tpgt`, `vlanTag` (a mock, not a capture: github.com/hpe-storage/python-3parclient `test/test_HPE3ParClient_ports.py`, read 2026-11-16) |
| HPE 3PAR / Primera WSAPI reference | Not in hand. A POST / PUT / DELETE on `/ports/<n:s:p>/iSCSIVlans[/<tag>]` is recalled from that guide but **unconfirmed** |
| DSCC storage-fleet API, offline mirror `reference/greenlake_api_docs/.../ports/devicetype4iscsiportedit.md` (scraped 2026-06-07) | **Write, documented**: `PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/edit-iscsi` with `vlans[]` = `vlanId`, `ipAddress`, `netMask`, `gatewayAddress`, `sendTargetGroupTag`; answers `202` and a task URI. Whether `vlans` replaces the port's whole list or adds to it is not said. `edit-rcip` has no VLAN field |
| Array CLI help captured on the lab (`tests/fixtures/rc_pair/help/help_controlport.txt`, OS 10.5) | `controlport` carries `-vlan` for `file` and `nvme` only, none for `rcip` or iSCSI. The Primera's help names `controliscsiport addr` and `delete`. `help controliscsiport` was never captured, so the iSCSI VLAN create and delete forms are **unconfirmed** |

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

**C — A write-scoped SSH form, the ADR 0015 way.** `controliscsiport` create and delete forms, each
checked for its whole shape (port, tag 1 to 4094, IPv4 address and mask), on a client built only
inside the apply of an approved plan. Works with the CLI dialect the tool already reads back. Costs:
widens ADR 0015's write client beyond Remote Copy (or adds a third client); the forms must be pinned
to the array's own help, which is not captured yet.

## Decision (proposed)

**A, if a live probe confirms it; otherwise C. Not B for now.**

1. Capture first (`lab/iscsi_vlan_capture.py`, read-only): `help controliscsiport`, `showport
   -iscsivlans`, and `GET /ports/<n:s:p>/iSCSIVlans/` on every iSCSI port.
2. Read the HPE WSAPI developer guide for the lab OS (10.5) for the iSCSI VLAN create and delete
   calls. If it documents them, one lab probe (create on a free iSCSI port, read, delete) pins the
   accepted body in a test; then A.
3. If WSAPI has no such call on this OS, C: add the create and delete forms to a write-scoped client
   with the same rules as `RC_WRITE_FORMS`, and say so in the pull request. That amends ADR 0015.
4. B stays on record for when the tool gains a DSCC data-plane client for another reason (snapshots,
   BL-21).

Either way: the read-back and verification use the read client (`showport -iscsivlans`); the removal
set is CLI text the operator pastes (SPEC-007); the switch is never written (ADR 0012).

## Consequences

- SPEC-024 R1 to R3 (sheet, read, plan) and R6 to R8 (verify, as-built, page) do not depend on this
  decision and can be built first. Only R4 (apply) and the removal command wait.
- Under C, `.github/instructions/adapters.instructions.md`, `AGENTS.md` hard rule 2 and ADR 0015 need
  one sentence each naming the new forms.
- Under A, nothing in the allowlists changes.
