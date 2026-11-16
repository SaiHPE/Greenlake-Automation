# ADR 0018 — Peer ports are set over a port-scoped SSH client

**Status:** PROPOSED 2026-11-16 (needs the owner's decision) · **Spec:** SPEC-025 · **Tracker:** BL-26 ·
**Amends, if accepted:** ADR 0001 (one more write-scoped client beside ADR 0015's) · **Keeps:** ADR 0012
(no switch writes), ADR 0015 (`ArrayRcCliClient` unchanged)

## Context

SPEC-025 sets chosen FC ports on this run's array to connection mode `peer` for a data migration
(BL-27). The array's own help (`help controlport`, captured on Alletra MP OS 10.5.55 and 10.5.0 and on
Primera OS 4.6.20) gives the commands: `controlport offline <nsp>`, `controlport config peer -ct point
[-f] <nsp>`, and `controlport rst <nsp>` to bring a held-offline port back. *"Controlport config mode
changes are not allowed when ports are online."*

There is no confirmed REST call for it:

- python-3parclient 4.5, the WSAPI client the tool provisions with, reads ports (`GET /ports`,
  `GET /ports/<nsp>/iSCSIVlans/`) and has no port-modify call.
- The offline mirror (`reference/`) holds the GreenLake APIs only; no WSAPI port reference.
- The DSCC Block Storage API was not checked for a port-mode call; DSCC is not a write plane this
  tool uses (ADR 0015 §4).

ADR 0015 §1 limited the Remote Copy write client to `controlport rcip addr|gw|ping`, *"never `offline`
or `config`"*. That sentence stays true whatever is decided here.

Two parallel proposals make the same kind of choice: BL-21 snapshots (ADR 0016, proposed) and BL-25
iSCSI VLANs (ADR 0017, proposed: WSAPI first, a write-scoped SSH client if WSAPI has no call). Peer
ports and iSCSI VLANs share one *Array ports* step (SPEC-024 R8, SPEC-025 R8). The owner may want one
rule for all three, and one *array port* write client for both port features instead of two, each
feature's forms bound to the ports its own plan approved.

## Options

**A. WSAPI.** Use a WSAPI port-modify call if one exists. It would fit the existing plan → approve →
apply flow with no new SSH write. It is **unconfirmed**: nothing in the client library or the mirror
shows one. The capture script reads `GET /ports` only; a write cannot be probed without a decision.

**B. A port-scoped SSH write client (default).** A new class `ArrayPortCliClient(ArrayCliClient)` in
`adapters/array/port_cli_client.py`, separate from `ArrayRcCliClient`, built only inside the apply of
an approved peer-port plan, **constructed with the approved port list**. Its `write()` accepts exactly:

| Form | Why |
|---|---|
| `controlport offline <nsp>` | the help refuses a mode change on an online port |
| `controlport config peer -ct point -f <nsp>` | the change; `-ct point` is the only value for `peer` |
| `controlport rst <nsp>` | only if the lab shows the port stays offline after `config` (unconfirmed) |

and each `<nsp>` must be in the approved list. Anything else is refused: another connmode (`host`,
`disk`, `rcfc`, `iscsi`, `nvme`, `file`, `eth`), `-virt_ports`, `-unique_nwwn`, `-sysreboot`, `rst -m`,
`rst -l`, `rst -i`, a port not approved, more than one port per command, shell metacharacters. Every
command goes through `command_log.record(..., write=True)`. The restore commands are **not** on the
list: the removal set is text the operator pastes (SPEC-007).

**C. Command set only.** The tool plans and prints the commands; a consultant pastes them; the tool
reads back and verifies. Smallest blast radius, but it is the arrangement the operator turned down for
array-side Remote Copy setup on 2026-10-07 (ADR 0015 *Context*): both ends are B10000 arrays the tool
already writes to, with one CLI dialect.

## Proposed decision

**B**, with A replacing it if a WSAPI call is confirmed on the lab, and C as the fallback if the owner
prefers no new SSH write. Reasons: the ADR 0015 reasoning applies unchanged (one dialect, an array the
tool already writes); the port list bound at construction keeps the reach to ports the operator
approved; the plan refuses any port with a login, an export or a role other than `free` (SPEC-025 R3),
so an `offline` can only reach an idle port.

**This is an allowlist change, said plainly:** a second write-scoped SSH client with three
`controlport` forms. It needs tests pinned to the array's own help (`tests/unit/test_peer_ports.py`
has them as strict xfail) and a sentence in the pull request that adds it.

## Consequences

- If accepted: ADR 0001's statement becomes "the read client is read-only; two write-scoped clients
  exist, one for Remote Copy links and targets (ADR 0015), one for setting approved FC ports to peer
  mode (ADR 0018), each reachable only through an approved plan". `AGENTS.md` hard rule 2,
  `.github/instructions/adapters.instructions.md` and `docs/ARCHITECTURE.md` change in the same pull
  request.
- The blast radius of a wrong apply is the approved idle FC ports; the removal set restores each to
  the Connmode and ConnType read before the apply.
- Open, to capture on the lab before building: whether `config` prompts despite `-f` (the help names
  `TPDFORCE_OVERRIDE`), whether `rst` is needed, whether the port WWN changes.
