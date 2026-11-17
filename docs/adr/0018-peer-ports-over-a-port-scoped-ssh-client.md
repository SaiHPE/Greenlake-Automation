# ADR 0018 — Peer ports are set over a port-scoped SSH client

**Status:** accepted 2026-11-17 (owner's decision); the port-mode write is deferred until the live
captures below; follows ADR 0025 · **Spec:** SPEC-025 · **Tracker:** BL-26 · **Keeps:** ADR 0012 (no
switch writes), ADR 0015 (`ArrayRcCliClient` unchanged) · **Used by:** ADR 0024 item 1 (RCFC port
modes, BL-50)

**Built:** the first slice (option C) on 2026-11-17, pending live run: the plan, the printed command
set and removal set, the read after the paste, verify, zoning and the as-built. No write client and
no allowlist change; option B waits as decided.

## Context

SPEC-025 sets chosen FC ports on this run's array to connection mode `peer`. Peer ports are needed
only for a data migration (BL-27): nothing else in the tool uses them. The array's own help
(`help controlport`, captured on Alletra MP OS 10.5.55 and 10.5.0 and on Primera OS 4.6.20) gives the
commands: `controlport offline <nsp>`, `controlport config peer -ct point [-f] <nsp>`, and
`controlport rst <nsp>` to bring a held-offline port back. *"Controlport config mode changes are not
allowed when ports are online."*

**Confirmed on rack13-ARCUS, OS 10.6.0, 2026-11-16** (`tests/fixtures/peer_ports/rack13/help_controlport.txt`,
read-only capture): the `config`, `offline`, `rst` and `-f` text is the same as on 10.5.55.

- `config` shows `[-f]` in its syntax. The `-f` option: *"If this option is not used, the command
  requires confirmation"*; and still *"In some cases, unless the TPDFORCE_OVERRIDE environment
  variable is set, the command will ask for confirmation even if the -f flag is specified"*.
- `offline` takes no `-f` (`controlport offline <node:slot:port>...`). It prompts only *"If there are
  active hosts or physical disks"*; the plan only offers ports with neither.
- `rst` is named twice: *"Issue controlport rst to bring the port back online"* (after `offline`), and
  `rst -m`/`-i`/`-l` change modes or reload firmware (refused below).
- `-ct` *"Sets the connection type. The specified port will be reset."* So `config peer -ct point`
  may bring the port back by itself; whether `rst` is still needed stays open.
- The help's own peer example is `controlport config peer -ct point 1:5:1`: no `offline` before it,
  no `-f`.
- `showport -c` reports `Mode_change` per port: `allowed` on every free FC port on rack13. The help
  says `rst -m` fails on a `prohibited` port and `-i` forces it and moves the partner port too. The
  plan refuses a `prohibited` port (SPEC-025 R3), so the client never needs `-i`.

**Confirmed on OS 10.5.0, 10.5.51 and 10.5.60, 2026-11-17** (D22U27, VZ and E18U31,
`tests/fixtures/peer_ports/<array>/`, read-only): `help controlport` is byte for byte the same on the
three, and its `config`, `offline`, `rst` and `-f` text is the same as on 10.6.0 and 10.5.55. So the
three forms below read the same on every OS the lab runs. E18U31's ports in peer mode show what a
successful change must read back: `showport` `initiator` and Type `peer`, `showport -par` `peer point`,
`showport -c` Mode_change still `allowed` (so the removal set's `config host` is not blocked), and a
new WWN pattern (`0202` where host mode has `0002`). The removal set therefore restores FROM
`peer point` TO the `host point` every other FC port reads on all four arrays.

There is no confirmed WSAPI call for it:

- python-3parclient 4.5, the WSAPI client the tool provisions with, reads ports (`GET /ports`,
  `GET /ports/<nsp>/iSCSIVlans/`) and has no port-modify call. On rack13 (2026-11-16) `GET /ports`
  reports `connectionMode` and `connectionType` with the same values as `showport -par` (1 disk,
  2 host; 2 point, 99 eth): the port object carries the mode, but no write was probed. On E18U31
  (WSAPI 1.15.60, 2026-11-17) an FC peer port reads `mode` 3, `type` 6, `connectionMode` 4: still GET
  only, so option A stays unconfirmed.
- DSCC: the block-storage API has no port-mode call. The **storage-fleet** API does (option D); the
  first draft of this ADR listed DSCC as not checked.

ADR 0015 §1 limited the Remote Copy write client to `controlport rcip addr|gw|ping`, *"never `offline`
or `config`"*. That sentence stays true.

Three proposals asked for an SSH write of their own: BL-21 snapshots (ADR 0016), BL-25 iSCSI VLANs
(ADR 0017) and this one; BL-50's RCFC ports (ADR 0024 part B) change an FC port's mode with the same
three commands. ADR 0025 (accepted 2026-11-17, BL-58) settled the rule once: every SSH write meets its
seven conditions, and condition 7 names **one array-port client** shared by ADRs 0017, 0018 and 0024
part B, built from the (port, form family) pairs of the approved plan.

## Options

**A. WSAPI.** Use a WSAPI port-modify call if one exists. It would fit the existing plan, approve,
apply flow with no new SSH write. It is **unconfirmed**: nothing in the client library or the mirror
shows one. The capture script reads `GET /ports` only; a write cannot be probed without a decision.

**B. The array-port SSH client.** The tool runs `controlport offline`, `controlport config peer` and,
if needed, `controlport rst` on the approved ports, through the shared client of ADR 0025 condition 7.
The design is the section *FC port-mode changes* below.

**C. Command set only.** The tool plans and prints the commands; a consultant pastes them; the tool
reads back and verifies. Smallest blast radius, but it is the arrangement the operator turned down for
array-side Remote Copy setup on 2026-10-07 (ADR 0015 *Context*): both ends are B10000 arrays the tool
already writes to, with one CLI dialect.

**D. DSCC storage-fleet API.** The GreenLake storage-fleet API documents
`PUT /storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}/ports/{id}/fc` with `configMode`
`Peer` (*"Possible Values: Disk, Host, RCFC, Peer"*), `connectionType` `Point`, answering 202 with a
task (operation `devicetype4fcportedit`, offline mirror
`reference/greenlake_api_docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/ports/devicetype4fcportedit.md`,
scraped 2026-06-07). The BL-50 research reports a v1 of the API now live. **Rejected for now**, for
ADR 0024's reasons: the mirrored version is an alpha, the tool has no DSCC client with write scope and
the permissions such a client needs are unknown, our DSCC workspace entitlements are unknown (SCOPE),
and nothing was probed. Worth a probe if DSCC writes arrive for another feature.

## Decision

**B, deferred; C first.** Peer ports matter only to a migration (BL-27), and the three unknowns below
can only be answered by a live change. So the first slice ships what needs no SSH write: the read
(built), the plan, the printed CLI lines (the command set a consultant pastes on the array), the read
after the paste, verify and the as-built (SPEC-025 R3 to R9). The tool's write (option B) follows once
the lab has answered the unknowns (*Must confirm live before the write*) and the owner has said yes.
Until then no allowlist changes and no port write client exists. A is not pursued (no call known); D
is rejected for now.

Why B when the write comes: the ADR 0015 reasoning applies unchanged (one dialect, an array the tool
already writes); ADR 0025's conditions bind every command to a port and a mode the operator approved;
the plan refuses any port with a login, an export or a role other than `free` (SPEC-025 R3), so an
`offline` can only reach an idle port.

**When the write lands it is an allowlist change, said plainly:** three `controlport` forms on the
array-port client. They need tests pinned to the array's own help and to the live answers
(`tests/unit/test_peer_ports.py` has them as strict xfail) and a sentence in the pull request.

## FC port-mode changes: one design for peer and RCFC

Peer ports (this ADR) and RCFC ports (ADR 0024 item 1) change an FC port's connection mode with the
same three commands and compete for the same free FC ports. One design covers both; ADR 0024 item 1
refers to it.

1. **The client** is the array-port write client of ADR 0025 condition 7: `ArrayPortCliClient(ArrayCliClient)`
   in `adapters/array/port_cli_client.py`, one class for ADR 0017 (iSCSI VLANs), this ADR and ADR 0024
   part B, separate from `ArrayRcCliClient`. Only the apply of an approved plan builds it, from the
   plan's (port, form family) pairs. For a mode change the family is the mode the plan sets on that
   port: `peer` or `rcfc`, nothing else. A port approved for one family takes no form of another: a
   peer apply cannot make an RCFC port, a VLAN apply cannot take a port offline.
2. **The forms**, one port per command, the port approved for that mode:

   | Form | Why |
   |---|---|
   | `controlport offline <nsp>` | the help refuses a mode change on an online port |
   | `controlport config <mode> -ct point -f <nsp>`, `<mode>` the port's approved mode | the change; `point` is the only value for `peer`, and the one SPEC-031 plans for `rcfc` |
   | `controlport rst <nsp>` | only if the live capture shows the port stays offline after `config` |

   Refused: every other connmode (`host`, `disk`, `iscsi`, `nvme`, `file`, `eth`), a mode other than
   the one approved for that port, `-virt_ports`, `-unique_nwwn`, `-sysreboot`, `rst -m`, `rst -l`,
   `rst -i`, a port not in the plan, more than one port per command, shell characters and the Tcl
   quoting and substitution characters (ADR 0025 condition 1). Every command goes through
   `command_log.record(..., write=True)`. The `config rcfc` form comes with ADR 0024 part B and its own
   live capture (ADR 0025 condition 7); BL-26 adds the `peer` form only.
3. **The restore is a removal line**, never a client form (SPEC-007, ADR 0025 condition 4). Per port,
   from the `showport -par` read before the change, written to the run's removal set before the port's
   first command is sent: `controlport offline <nsp>`, `controlport config <old connmode> -ct <old
   conntype> -f <nsp>`, `controlport rst -f <nsp>` (the help's `rst` takes `-f`; added 2026-11-17). A
   plan without that read blocks.
4. **Read back after each port** (ADR 0025 condition 5): Type and Connmode are the approved mode,
   ConnType `point`, and every other port's mode, Type and logins are as before; otherwise stop.
5. **No prompts** (ADR 0025 condition 6): the `config` form goes on the client only after a live
   capture shows `-f` takes it through without a confirmation.

RCFC's Remote Copy objects (`controlport rcfc init`, targets, links) are not mode changes: they stay
where ADR 0024 item 3 puts them, on the Remote Copy client.

## Risks

- **A "free" port may still be zoned.** Type `free` says nothing is logged in now (rack13's 0:3:3
  went from `host` to `free` when its host left). A cabled port can still sit in a zone with a host
  that is switched off; that host loses the path when the port changes role. The array cannot see
  zones. The plan therefore adds a note when a switch's `cfgshow` (the zoning step's read-only switch
  read) has a zone naming that port's WWPN, and says the zones were not checked when the run has no
  switch read (SPEC-025 R3).
- **A `config` that hangs leaves the port offline.** `offline` worked, then `config` gave no answer
  (or the paste stopped there): the port is held offline in a mode nobody saw. So every port's restore
  keeps the `controlport rst -f <nsp>` line, and a port whose `config` did not answer gets the whole
  restore, since its mode is unknown. A `config` the array refused (an `Error` line) gets `rst` only.
- **The WWPN changes.** The captures point that way (`0202` on every peer port, `0002` on every
  host-mode port). Zones use the WWPN read back after the change (SPEC-025 R7); a zone that names the
  old WWPN goes dead, the zones the first risk's note names included. The restore changes it back, so
  the peer-port zones go dead too: the removal set's header has them removed first.

## Must confirm live before the write

The owner's yes and a lab booking. The first slice's own command set, pasted on a lab array with a
read saved before, after the change and after the restore, gives every answer:

1. Whether `controlport config peer -ct point -f <nsp>` still asks for a confirmation
   (`TPDFORCE_OVERRIDE`). If it does, the form cannot go on the client.
2. Whether `controlport rst <nsp>` is needed after `config` (the port's state after `config`).
3. The port WWN before, after and after the restore (`0202` on peer ports against `0002` on host
   ports in the captures).
4. Every other port reads the same afterwards (`showport`, `showport -par`, `showport -c`,
   `showhost -d` against the read before).

Candidate ports: rack13-ARCUS 0:3:3 and 1:3:4 (free, linked, one per fabric by parity, nothing zoned
to them on 2026-11-16; they served host 10.132.30.136 until at least 2026-11-03), or E18U31's existing
peer ports 0:3:2 and 1:3:2 (restore, then set again; they show the source array, a 3PAR 20850, as
their Device, so whoever uses it is asked first). The owner chooses. The answers go to
`docs/validation/` and to fixtures before the client is written.

## Consequences

- First slice: no allowlist change and no new write client. The page prints the command set and the
  removal set; the consultant pastes them; the tool reads the array again, checks it like an apply
  would (SPEC-025 R4) and verifies. Hard rule 2 is unchanged.
- When the write lands: the array-port client gains the `peer` mode family (the three forms above) in
  the pull request that adds it, with its tests and the live captures. If ADR 0017's VLAN forms land
  first, the client exists and this adds a family; otherwise this pull request creates it.
  `docs/ARCHITECTURE.md` and `.github/instructions/adapters.instructions.md` change in that pull
  request.
- The blast radius of a wrong apply is the approved idle FC ports; the removal set restores each to
  the Connmode and ConnType read before the change, and brings it back online.
- Nothing in the 2026-11-16 or 2026-11-17 captures contradicts option B. The help's example omits
  `-f`; the client form keeps it, since without it the command asks for a confirmation an SSH exec
  cannot give.
