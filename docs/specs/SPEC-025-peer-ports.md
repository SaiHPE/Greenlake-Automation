# SPEC-025 — Peer ports for migration, set up by the tool

**Status:** proposed 2026-11-16, not built · **Decision:** ADR 0018 (PROPOSED: the write plane) ·
**Tracker:** BL-26 · **Used by:** BL-27 migration (SPEC-027) · **Sibling:** BL-25 VLAN (SPEC-024) ·
**Work packet:** `docs/workpackets/BL-26.md`

## 1. Problem

A data migration onto a B10000 (BL-27) imports volumes from a source array over Fibre Channel. The
destination array reaches the source through **peer ports**: FC ports on the destination set to
connection mode `peer`, so they log in to the fabric as initiators and see the source array's host
ports like a host would. A consultant sets them up by hand before the migration, then asks the SAN
team for zones between each peer port and the source array's ports.

**What "read-only today" means in this code.** The tool reads peer ports and never sets one:

| Where | What it does with a peer port today |
|---|---|
| `adapters/array/wsapi_client.py` `_PORT_MODE` | maps WSAPI mode 4 to `peer`; `array_fc_ports()` lists FC ports with that mode |
| `application/provisioning/discovery.py` `parse_ports` | keeps only `target` FC/iSCSI ports, so a peer FC port (mode `initiator`, Type `peer`) never becomes a zoning candidate |
| `application/provisioning/discovery.py` `parse_replication_ports` | reads IP ports in mode `peer` (RCIP and cluster), not FC peer ports |
| `application/provisioning/preflight.py` `_ports_check` | counts initiator/peer ports as "excluded, do not serve hosts" |
| `application/provisioning/zoning_plan.py` `_caution` | flags an FC port whose Type is not `host`/`free`, never on the Label |
| `application/replication/read.py` `parse_showport_roles` | keeps mode, Type and protocol per port for the RCIP plan |
| SPEC-021 | sets RCIP **addresses** on free IP ports (mode `peer`, protocol IP); it never changes a port's role |

Nothing reads `showport -par` (the connection mode the array would restore), nothing changes an FC
port's mode, and nothing designs zones for a peer port. SCOPE row 3 lists "peer-port configuration"
as partial for this reason.

**What a peer port looks like on our arrays (captured, not assumed).**

- `tests/fixtures/rc_pair/E18U31/showport.txt` (AlletraMP_E18U31, OS 10.5.0, 2026-10-07): `0:3:2` and
  `1:3:2` are `initiator ready … peer FC`. Their node WWN is `2FF70202AC02DEF2` and port WWNs
  `20320202AC02DEF2` / `21320202AC02DEF2`, where the host ports of the same array show `2FF70002…` and
  `2031 0002…`. So a peer port presents its **own node WWN, and a port WWN different from the host-port
  pattern**. Whether the port WWN changes at the moment of the mode change is unconfirmed (one array,
  after the fact): **capture on the lab**. It matters for zoning (R7).
- On the same card, `0:3:1` is a `target` host port beside the `0:3:2` peer port: this Alletra MP FC
  card does not force both ports of a pair into one mode (the "port pair protection" the CLI help
  describes for LSI adapters).
- `tests/fixtures/rc_pair/D22U27/showport.txt`: three FC ports carry the Labels `peer port`,
  `peer 1:3:1` and `Peer_port` and are Type `host`, serving hosts. **A Label never makes a peer port.**
- `help controlport` (`tests/fixtures/rcip_pair/help/alletra_help_controlport.txt`, Alletra MP OS
  10.5.55; same text on Primera OS 4.6.20 and D22U27 OS 10.5.0):
  `controlport config <connmode> [-ct <ctval>] [-unique_nwwn enable|disable] [-virt_ports <n>] [-f]
  [-sysreboot] <node:slot:port>...`; *"if <connmode> is "peer", then <ctval> can only be "point""*;
  *"Controlport config mode changes are not allowed when ports are online"*; `controlport offline
  <node:slot:port>...` *"Holds the specified port offline indefinitely. Issue controlport rst to bring
  the port back online"*; *"Issue the showport command with either the -i or -par options to verify
  the success of the controlport command"*; virtual peer ports are listed by `showport -peer`.
- No WSAPI call to change a port's connection mode is known: python-3parclient 4.5 (installed) has
  `GET /ports` and `GET /ports/<nsp>/iSCSIVlans/` only; the offline mirror holds GreenLake APIs only.
  See ADR 0018.

## 2. Requirements

**R1 — The sheet.** An optional tab *Peer ports*, one row per FC port to use as a peer port on this
run's array. Columns: *Port (N:S:P)* (required, a text cell like the Replication network tab), *Source
array ports to zone (WWPNs)* (optional; one or more WWPNs separated by spaces or commas, colons
allowed). A workbook without the tab parses as before (`ProvisioningIntent.peer_ports` is `None`).
Refused with a sentence, nothing planned:

| Rule | Sentence |
|---|---|
| Port is not N:S:P | *Peer ports tab — row '<port>': Port must be N:S:P, like 0:3:2 (got '<port>').* |
| Port named twice | *Peer ports tab — port 0:3:2 is named twice.* |
| Fewer than two rows, or every row on one node | *Peer ports tab — peer ports go in pairs across nodes: name at least one port on each of two nodes (got 0:3:2 only on node 0), so the migration keeps a path when a node restarts.* |
| A source WWPN that is not 16 hex digits | *Peer ports tab — row '0:3:2': '<text>' is not a WWPN (16 hex digits, colons allowed).* |
| Same port on the Replication network tab | *Peer ports tab — port <nsp> is also on the Replication network tab; a port has one role.* |

Port existence, Type and use are array facts and are judged in the plan (R3), not the sheet.

**R2 — The read** (read-only client, every command already allowed under `showport`, `showhost`,
`showvlun`, `showportdev`): `showport` (mode, state, Type, protocol, node and port WWN, and on a
Primera the Partner and FailoverState columns), `showport -par` (Connmode and ConnType, the values the
removal set restores; layout to be pinned to a capture), `showhost -d` (which hosts are logged in on
which port; `parse_showhost` already reads it), `showvlun -a` (active exports by port). `showport -peer`
is read for the as-built when it answers. No allowlist change for reads.

**R3 — The plan, one action per row.**
- **exists** — `showport` Type `peer`, protocol FC. Nothing to do.
- **create** — protocol FC, Type `free`, no login on the port in `showhost -d` (claimed or `-- --`),
  no active export on it in `showvlun -a`, and no Partner with a FailoverState other than `none`/`-`.
  The action carries the commands of ADR 0018 in order (`controlport offline <nsp>`, `controlport config
  peer -ct point -f <nsp>`, then `controlport rst <nsp>` only if the lab shows the port stays offline:
  unconfirmed) and the restore lines from `showport -par` (R5).
- **conflict**, with the array's own facts in the sentence:
  - not on the array: *0:9:1 is not on this array (showport has no such port).*
  - not FC: *0:4:3 is not a Fibre Channel port (Type free, protocol IP). Peer ports are FC ports.*
  - serving hosts: *1:3:2 serves hosts (Type host; logged in: an unnamed initiator 1000040973C52799).
    The tool never takes a port from hosts: pick a free port, or move the hosts first.* This holds
    whatever the Label says.
  - logins or exports on a `free` port: same sentence, naming the hosts or the exported volumes.
  - another role: *0:3:2 is Type rcfc / disk / iscsi …; the tool changes only free FC ports.*
  - persistent-port partner in use (Primera): *0:3:1 is the failover partner of 1:3:1 (state
    failed_over); changing it removes that path protection.*

  Plan-level **blocker**: fewer than two ports that are `exists` or `create` on two different nodes,
  with the same sentence as the sheet rule. **Notes** (not blockers): both peer ports end up on one
  fabric by port parity (ADR 0009) — *"0:3:2 and 1:3:2 are both on the even fabric (F2) by port
  number; a fabric failure stops the migration"* (whether HPE requires one per fabric is unconfirmed,
  see §6); a planned port's link is `loss_sync` (no cable or no switch port: it can be set, but zones
  will not work until it is cabled).

**R4 — Apply** (ADR 0018), only after the operator ticks the approval sentence *"I approve setting
these N ports to peer mode on <array>. They stop serving anything else."* Port by port in sheet order,
stopping at the first refusal: offline, config, (rst), then read back `showport` and `showport -par`.
Each command's answer is checked like SPEC-021 R4 (a line starting `Error` is a refusal; no answer in
the exec timeout is a refusal). After each port the read-back must show Type `peer`, Connmode `peer`,
ConnType `point`, **and every other port's mode and Type unchanged from the read before the apply**
(the CLI help warns a mode change can move a partner port; LESSONS 44). A port that does not read back
as peer stops the apply with *"0:3:2 did not come back as a peer port (Type free, state offline)."*
The approval clears on every new read (LESSONS 6).

**R5 — The removal set** (SPEC-007 pattern): text the operator pastes, never run by the tool, only for
ports this apply changed, in reverse order. Per port, from the `showport -par` read before the apply:
`controlport offline <nsp>` then `controlport config <old connmode> -ct <old conntype> -f <nsp>` (and
`controlport rst <nsp>` if the apply needed it). A port the apply took offline and then could not
change (it stopped at that port's `config`) gets `controlport rst <nsp>` only, the help's way back
online. A create needs the `showport -par` read: without it the plan blocks, because the change could
not be undone. Header: *"Undo the peer ports this run set. Remove the
SAN team's peer-port zones and any migration that uses these ports first."* BL-27's removal set goes
above this block.

**R6 — Verify** (read-only, runs again from the Verify step): per planned port, Type `peer`, Connmode
`peer`, state `ready`. Sentences: *"0:3:2 is a peer port, link ready."* / *"0:3:2 is a peer port but its
link is loss_sync: check the cable and the switch port."* / *"0:3:2 is not a peer port (Type free)."*
Whether the source array's ports are visible through the peer port (after zoning) is BL-27's verify.

**R7 — Zoning** (ADR 0012: a command set for the SAN team, never a switch write). Reuse the existing
designer and renderer (`zoning_plan.render_commands`): one single-initiator single-target zone per
(peer port, source array port) pair from the sheet, on the fabric where both are in the name server.
The peer port's WWPN is **the one read back after the apply** (R4), never the one read before: if the
mode change gives the port a new WWPN, a zone built from the old one is silently dead (LESSONS 32).
Alias pre-fill follows ADR 0004's array-port convention with a `PEER` marker
(`<serial>_N0S3P2_PEER`); an alias the switch already has for that WWPN is reused. The peer-port zones
are their own block under the zoning step's command set, `cfgenable` shown separately as today. BL-27
replaces the sheet's source WWPNs with the source array's ports it discovers (SPEC-027).

**R8 — The step and the page.** Peer ports are a section of the *Array ports* step that SPEC-024
(BL-25, iSCSI VLANs) proposes: key `ports`, kind `provision`, between `discover` and `zoning`, one
section per tab, one removal block per run. No step of its own: both features configure array ports
from the sheet before zoning, and zoning must see the result (the peer WWPN after the change, R7).
The step's presets are SPEC-024's; with no *Peer ports* tab this section says *"The sheet asks for no
peer ports. Nothing to set up here."*, reads nothing and is complete. Shared with SPEC-024 as well:
`PortRole` from `parse_showport_roles` as the one source of a port's role (LESSONS 41), N:S:P kept as
text, and the conflict wording *"The tool never changes a port's role"* for a port of another kind.
Whichever spec merges second adapts to the first. The section (UX-GUIDELINES, on the step's
StepShell), with its own approval tick and button because its consequence differs from adding a VLAN:

```
Peer ports                                                        [ Read the array again ]
Status: plan ready · 2 ports to set, 0 already peer, 0 conflicts
┌ Port  │ Now                     │ After        │ Why ─────────────────────────────────────┐
│ 0:3:2 │ free · FC · loss_sync   │ peer, point  │ free, nothing logged in, no exports       │
│ 1:3:2 │ free · FC · loss_sync   │ peer, point  │ free, nothing logged in, no exports       │
└───────┴─────────────────────────┴──────────────┴───────────────────────────────────────────┘
Note: 0:3:2 and 1:3:2 are both on the even fabric by port number.
▸ Show 4 commands
[ ] I approve setting these 2 ports to peer mode on rack13-ARCUS. They stop serving anything else.
                                                             [ Set the peer ports ] (disabled until ticked)
After: result per port · new WWPN per port · Removal set (Copy / Download .txt) · Verify
```

**R9 — The as-built.** A section *Peer ports*: per port the mode, ConnType, state, node and port WWN
after the apply, virtual peer ports from `showport -peer` when present, the commands run in order, the
peer-port zones designed in the run with their command set, and the removal set.

## 3. Non-goals

Virtual peer ports (`-virt_ports`), `-unique_nwwn`, labels (`controlport label`), changing a port that
serves hosts or carries Remote Copy, iSCSI/NVMe/IP ports, the migration itself (SPEC-027), any switch
write, a peer port on the source array, running the removal set.

## 4. Verification

- Unit tests: `tests/unit/test_peer_ports.py`. Strict `xfail` until each part is built (the work
  packet names which step turns which test green); the guard tests on today's behaviour pass now.
  Planned on real captures: rack13-ARCUS (`rcip_pair/before/alletra/showport.txt` 2026-11-03 with
  `rack13_array/showhost_d.txt` 2026-09-13; different days, said in the tests), D22U27, E18U31 and the
  Primera. No device output is invented: what is not captured is built from model objects.
- Captures owed (`lab/peer_port_capture.py`, read-only, not yet run): `showport -par`, `showport -peer`,
  `showport -c`, `showportdev ns <nsp>` for the peer ports, WSAPI `GET /ports`, `help showport`,
  `help showportdev`, on E18U31 (has peer ports) and D22U27. Fixtures go to `tests/fixtures/peer_ports/`.
- Live run (needs the owner's yes and a lab booking): on rack13-ARCUS, two free FC ports on two nodes
  (`0:3:2`, `1:3:2`, Type free today) set to peer by the tool, read back, verify, the removal set pasted
  and the ports read back exactly as before (`showport`, `showport -par` diffed). Checklist in the work
  packet.

## 5. Decisions taken here (defaults, owner may change)

1. The tool changes only `free` FC ports with no login and no export; it never takes a port from hosts.
2. Two ports on two nodes minimum; one-fabric-only is a note, not a refusal.
3. The write plane is ADR 0018 (proposed): a port-scoped SSH client, not WSAPI, not a command set.
4. Zoning reuses the host-zoning renderer; the peer WWPN comes from the read-back.
5. Peer ports live in SPEC-024's shared *Array ports* step (`ports`), not a step of their own.

## 6. Open questions (for the owner, or capture on the lab)

1. Does `controlport config peer -ct point -f <nsp>` on an offline port bring it back online, or is
   `controlport rst <nsp>` needed? Does it prompt despite `-f` (help: *"unless the TPDFORCE_OVERRIDE
   environment variable is set, the command will ask for confirmation even if the -f flag is
   specified"*)? An SSH exec has no terminal to answer.
2. Does the port WWN change when the mode changes (E18U31 suggests yes)?
3. `showport -par` column layout on OS 10.5 (only a hand-written example is in `test_asbuilt_parse.py`).
4. WSAPI: is there a `PUT /ports/<nsp>` that sets the FC connection mode, and what does `GET /ports`
   report for an FC peer port (mode 3 initiator with type 6 peer, per python-3parclient's constants)?
5. HPE's rules for peer ports in a B10000 data migration (how many, one per fabric or per node, same
   slot:port partner): the public HPE pages could not be reached through the search tools on
   2026-11-16 (Bing returned unrelated pages, DuckDuckGo a bot check). Needs the HPE data migration
   guide for the B10000 or the owner's field practice.
6. Does the Alletra MP have persistent-port partners like the Primera (no Partner column in its
   `showport`)?
7. SPEC-024 asks whether a peer-enabled iSCSI port (`showport -iscsi` column `Peer_Enabled`, `N` on
   every E18U31 iSCSI port captured 2026-10-07) should be refused for VLANs. For this spec it does not
   change anything: peer ports here are FC only, and an iSCSI port on the *Peer ports* tab is already a
   conflict (*"not a Fibre Channel port"*). It matters for BL-27 if migration may also run over iSCSI:
   a peer-enabled iSCSI port is then the iSCSI counterpart of an FC peer port. Recommended answer, in
   line with decision 1 (never change a port that has another role): refuse, as SPEC-024 proposes.
   What `Peer_Enabled Y` means on the array is unconfirmed: capture on the lab.
8. Write plane shared with SPEC-024: ADR 0017 (BL-25) falls back to a write-scoped SSH client if WSAPI
   has no iSCSI VLAN call; ADR 0018 proposes one for peer ports; ADR 0016 (BL-21) one for snapshots.
   The owner may want one *array port* write client for both port features, with each feature's forms
   bound to its own approved ports, rather than two.

## 7. Sources

Captured fixtures named above; python-3parclient 4.5 `client.py` (installed in the venv); ADR 0004,
0009, 0012, 0015; SPEC-007, SPEC-021; LESSONS 6, 32, 41, 42, 44.
