# SPEC-025 — Peer ports for migration, set up by the tool

**Status:** first slice built 2026-11-17, pending live run (R1 to R3, R4's command set and read after
the paste, R5's removal set as text, R6 to R9; work packet steps 1, 3, 3b and 6 to 10). The tool's
write (R4 later, steps 4 and 5) is deferred by the owner. Proposed 2026-11-16; the read (R2) built
2026-11-16, pinned to rack13-ARCUS, and on 2026-11-17 to a port in peer mode (E18U31) and to OS
10.5.0 and 10.5.51 ·
**Decision:** ADR 0018 (accepted 2026-11-17: the command set first; the tool's write after the live
captures, over the array-port client of ADR 0025) ·
**Tracker:** BL-26 · **Used by:** BL-27 migration (SPEC-027) · **Sibling:** BL-25 VLAN (SPEC-024) ·
**Work packet:** `docs/workpackets/BL-26.md`

## 1. Problem

A data migration onto a B10000 (BL-27) imports volumes from a source array over Fibre Channel. The
destination array reaches the source through **peer ports**: FC ports on the destination set to
connection mode `peer`, so they log in to the fabric as initiators and see the source array's host
ports like a host would. A consultant sets them up by hand before the migration, then asks the SAN
team for zones between each peer port and the source array's ports. Nothing else in the tool needs
peer ports.

**What "read-only today" means in this code.** The tool reads peer ports and never sets one:

| Where | What it does with a peer port today |
|---|---|
| `adapters/array/wsapi_client.py` `_PORT_MODE` | maps WSAPI mode 4 to `peer`, which is the IP ports' mode. An FC peer port is mode 3 (`initiator`), type 6 (E18U31, 2026-11-17), so `array_fc_ports()` reports it as `initiator` and preflight excludes it as not serving hosts |
| `application/provisioning/discovery.py` `parse_ports` | keeps only `target` FC/iSCSI ports, so a peer FC port (mode `initiator`, Type `peer`) never becomes a zoning candidate |
| `application/provisioning/discovery.py` `parse_replication_ports` | reads IP ports in mode `peer` (RCIP and cluster), not FC peer ports |
| `application/provisioning/preflight.py` `_ports_check` | counts initiator/peer ports as "excluded, do not serve hosts" |
| `application/provisioning/zoning_plan.py` `_caution` | flags an FC port whose Type is not `host`/`free`, never on the Label |
| `application/replication/read.py` `parse_showport_roles` | keeps mode, Type and protocol per port for the RCIP plan |
| SPEC-021 | sets RCIP **addresses** on free IP ports (mode `peer`, protocol IP); it never changes a port's role |

Before BL-26 nothing read `showport -par` (the connection mode the array would restore). The read
side now does (`application/provisioning/peer_ports.py`, R2). Nothing changes an FC port's mode, and
nothing designs zones for a peer port. SCOPE row 3 lists "peer-port configuration" as partial for
this reason.

**What a peer port looks like on our arrays (captured, not assumed).**

- `tests/fixtures/rc_pair/E18U31/showport.txt` (AlletraMP_E18U31, OS 10.5.0, 2026-10-07): `0:3:2` and
  `1:3:2` are `initiator ready … peer FC`. Their node WWN is `2FF70202AC02DEF2` and port WWNs
  `20320202AC02DEF2` / `21320202AC02DEF2`, where the host ports of the same array show `2FF70002…` and
  `2031 0002…`. So a peer port presents its **own node WWN, and a port WWN different from the host-port
  pattern**. Whether the port WWN changes at the moment of the mode change is unconfirmed (one array,
  after the fact): **capture on the lab**. It matters for zoning (R7). The same two ports were still
  in peer mode on 2026-11-17, with every read (below).
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
  `GET /ports` and `GET /ports/<nsp>/iSCSIVlans/` only; the offline mirror has no WSAPI reference. The
  DSCC storage-fleet API documents one (`PUT …/ports/{id}/fc`, `configMode` `Peer`, in the mirror),
  rejected for now. See ADR 0018.

**Confirmed on rack13-ARCUS, OS 10.6.0, 2026-11-16** (`tests/fixtures/peer_ports/rack13/`,
`lab/peer_port_capture.py`, read-only; its README lists every file). rack13 has **no port in peer
mode**, so this is the array before a change. The capture of a peer port came on 2026-11-17
(E18U31, below).

- `showport -par` layout: `N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN IntCoal
  TMWO`, the same as the CLI help's example (§6 question 3 answered). One row per FC, NVMe and iSCSI
  port, none for IP ports. Every FC port reads `host point`, so the removal set restores
  `controlport config host -ct point -f <nsp>`.
- `help controlport` on 10.6.0 says the same as on 10.5.55 for everything this spec uses: `config`
  shows `[-f]`; `offline` shows no `-f` and *"If there are active hosts or physical disks when issuing
  the controlport rst or offline commands, a warning is returned and you are prompted for
  confirmation"*; `rst` is named as the way back online after `offline`; the `TPDFORCE_OVERRIDE`
  sentence is still there; `-ct` *"Sets the connection type. The specified port will be reset"*. The
  help's own peer example is `controlport config peer -ct point 1:5:1`, with no `offline` and no `-f`.
  Whether `config` with `-ct` brings the port back online, or `rst` is still needed, stays open (§6.1).
- `help showport`: `-peer` *"Displays information that is specific to the Fibre Channel ports for
  Data Migration"*. Its example peer port is `0:5:1 initiator ready 2FF70202AC000007
  20510202AC000007 2Gbps`: the same `0202` WWN pattern as E18U31's peer ports. HPE's own example
  supports "a peer port has WWNs of its own" (§6.2); the moment of the change is still not seen.
  On rack13 `showport -peer` answers *There is no specified port information.*
- `showport -c` ends in a `Mode_change` column: `allowed` on all eight slot-3 FC ports, `prohibited`
  on the NVMe, iSCSI and IP ports. Its Device column names host objects only: 0:3:4's unclaimed
  login shows as `---`. It never replaces `showhost -d` for "is anything logged in".
- **Type says what is attached now, not what a port is for.** 0:3:3 and 1:3:4 were Type `host` on
  2026-11-03 (host 10.132.30.136 logged in, `rack13_array/showhost_d.txt` of 2026-09-13) and Type
  `free` on 2026-11-16, with no login. A `free` port that is cabled and in a fabric can still be zoned
  to a host that is switched off (§6.9).
- WSAPI `GET /ports` carries `connectionMode` and `connectionType` (the `showport -par` values) as
  well as `mode` and `type`. Mapped side by side with the CLI, all 28 ports agree: mode 2 `target`,
  3 `initiator`, 4 `peer`; type 1 `host`, 2 `disk`, 3 `free`, -1 `cluster`; protocol 1 FC, 2 iSCSI,
  4 IP, 6 NVMe; linkState 4 `ready`, 5 `loss_sync`, 10 `offline`, 12 `link_idle_for_reset`;
  connectionMode 1 `disk`, 2 `host`; connectionType 2 `point`, 99 `eth`. Every FC port also lists one
  `virtualPorts` entry: vpi 31, protocol NVMe, WWNs `2FF70102…` / `2031 0102 ADF2…`, which
  `showportdev ns` shows logged in to the fabric beside the port's own WWPN.
- The free FC ports: 0:3:1, 0:3:2, 1:3:1, 1:3:2 are `loss_sync`, report no SFP in `showport -sfp`,
  and `showportdev ns` answers *Error: Unable to get device list*: no transceiver, no cable. 0:3:3
  and 1:3:4 are `ready`, in a fabric, with nothing zoned to them (0 devices in the name server).
  0:3:4 and 1:3:3 serve one unclaimed ESXi HBA (10005CED8C5312A9).
- No Partner or FailoverState column in `showport` and no failover field in `GET /ports` on 10.6.0
  either: no sign of persistent-port partners on the Alletra MP (§6.6).

**What the capture contradicts or changes in this spec as first written:**

1. The capture ran on rack13 only, not on E18U31 and D22U27 as §4 planned: nothing captured on
   2026-11-16 showed `showport -par`, `showport -peer` or `GET /ports` for a port in peer mode.
   *Done 2026-11-17, below.*
2. rack13 runs OS 10.6.0 now, not 10.5.55.
3. The plan tests' "0:3:3 serves hosts" is a 2026-11-03 fact. On 2026-11-16 0:3:3 is free; the tests
   keep the older captures for that case on purpose.
4. The live run's ports 0:3:2 and 1:3:2 have no SFP and no link: they need transceivers and cables
   before a live run on rack13 (§4).
5. `showport -peer` lists peer ports for data migration, physical ones included (help showport), not
   only virtual peer ports (the `-virt_ports` text in `help controlport`).

**Confirmed on E18U31 (OS 10.5.60), D22U27 (OS 10.5.0) and VZ (OS 10.5.51), 2026-11-17**
(`tests/fixtures/peer_ports/<array>/`, the same read-only script, run by labrat; the README lists
every file and the two names replaced). E18U31, now named `DHCI_B10K`, still has **0:3:2 and 1:3:2 in
peer mode**: the first capture of a peer port with every read this spec makes. D22U27 and VZ have none.

- **A peer port, every read** (E18U31, OS 10.5.60):
  - `showport`: `initiator ready 2FF70202AC02DEF2 20320202AC02DEF2 peer FC` (1:3:2: `21320202…`).
  - `showport -par`: Connmode `peer`, ConnType `point`. This is what a removal set restores FROM;
    every other FC port reads `host point`, what it restores TO.
  - `showport -peer`: one row per peer port, `N:S:P Mode State Node_WWN Port_WWN Rate VPI`. The
    real output has a `VPI` column (0 here) that the help's example lacks; the parser reads the first
    five columns. **It lists this array's own peer ports, never the source array's WWNs.**
  - `showport -c`: Mode `initiator`, Mode_change `allowed` (the way back is open), and the Device
    column holds the **source array's node WWN**, `2FF70002AC07E528`. `showportdev ns 0:3:2` names that
    source, an HPE 3PAR 20850 (4UW0002142), through its own 0:3:2 and 1:3:2 in host mode.
  - `showhost -d`: no login on a peer port; `showvlun -a`: no export on it. The source array is not a
    host, so a peer port looks idle to those two reads; only its Type (`peer`) keeps it out of the
    candidates. `is_free_fc_port` on E18U31 accepts 0:3:3 and 1:3:3 only.
  - WSAPI `GET /ports` (1.15.60): `mode` 3, `type` 6, `connectionMode` 4, `connectionType` 2,
    `device` `["2FF70002AC07E528"]`, and **no** `virtualPorts` entry, where every other FC port has the
    NVMe one (vpi 31). python-3parclient's type 6 = peer is confirmed; now mapped.
- **WWNs** (the open question §6.2): the peer ports carry `0202` in bytes 3 and 4 of both WWNs; every
  FC port in host mode on all four arrays carries `0002`; the NVMe virtual ports carry `0102`. The
  host-mode form of E18U31's 0:3:2 would be `20320002AC02DEF2`, and no capture has it. Still no
  before-and-after of one port.
- **Per OS.** The `showport -par` header is the same on 10.5.0, 10.5.51, 10.5.60 and 10.6.0. `showport
  -peer` with no peer port answers *There is no specified port information.* on all four. `showport -c`
  ends in `Mode_change` on all four, `allowed` on every FC port captured. The help texts are byte for
  byte the same on the three 10.5 arrays; for `config`, `offline`, `rst` and `-f` they match 10.6.0.
- **WSAPI on 10.5 is not a full port list.** `GET /ports` leaves out the IP ports of Type `free`
  (E18U31, D22U27) and `file` (D22U27); rack13 on 10.6.0 lists them. Every port it does list reads like
  `showport`, and its params like `showport -par`. Type 7 is `rcip` (D22U27, VZ); now mapped. The
  peer-port read stays on the CLI (`read_view`), so nothing depends on the missing IP ports.
- **Labels again** (LESSONS 42): D22U27's `peer port`, `peer 1:3:1` and `Peer_port` are still Type
  `host`, Connmode `host`, with logins. Its free FC ports are 0:3:2 (linked, nothing zoned), 0:3:3 and
  1:3:3; VZ's are 0:3:3, 0:3:4, 1:3:3, 1:3:4 (no link).

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
| Same port on the Replication FC ports tab (RCFC, BL-50; its rows for this array) | *Peer ports tab — port <nsp> is also on the Replication FC ports tab; a port has one role.* |

A port named by both the Peer ports tab and the Replication FC ports tab is refused here, in the
sheet, whichever tab names it first; SPEC-031 R11 refuses the same port from its side. A port on both
replication tabs as well gets one sentence naming both (*is also on the Replication network tab and
the Replication FC ports tab*). The Replication FC ports tab's rows for the `peer` array name the other
array's ports and are not compared. Until BL-50 adds that tab, the rule has nothing to compare.

Port existence, Type and use are array facts and are judged in the plan (R3), not the sheet.

**R2 — The read** (read-only client, every command already allowed under `showport`, `showhost`,
`showvlun`, `showportdev`): `showport` (mode, state, Type, protocol, node and port WWN, and on a
Primera the Partner and FailoverState columns), `showport -par` (Connmode and ConnType, the values the
removal set restores; layout pinned to rack13, OS 10.6.0, 2026-11-16, and the same on OS 10.5.0,
10.5.51 and 10.5.60, 2026-11-17), `showport -c` (`Mode_change`,
added 2026-11-16 from the capture), `showhost -d` (which hosts are logged in on which port;
`parse_showhost` already reads it), `showvlun -a` (active exports by port, every initiator kind,
NVMe included). `showport -peer` is read for the as-built when it answers (this array's own peer
ports and their WWNs; the source array shows only as the Device in `showport -c`). No allowlist change for
reads. If `showport`, `showport -par`, `showhost -d` or `showvlun -a` fails or answers `Error`, the
read fails as a whole: a half read could make a busy port look free. **Built:** `read_view`,
`build_view`, the parsers and `free_fc_ports` in `application/provisioning/peer_ports.py`, and
`parse_port_states` (WSAPI `GET /ports` in the CLI's words) in `adapters/array/wsapi_client.py`.

**R3 — The plan, one action per row.**
- **exists** — `showport` Type `peer`, protocol FC. Nothing to do.
- **create** — protocol FC, Type `free`, no login on the port in `showhost -d` (claimed or `-- --`),
  no active export on it in `showvlun -a`, no Partner with a FailoverState other than `none`/`-`, and
  `showport -c` does not call its mode change `prohibited` (added 2026-11-16; the tool never uses
  `rst -i`, the help's way to force a prohibited change, which moves the partner port too). This is
  `is_free_fc_port` (built); on rack13 on 2026-11-16 it accepts 0:3:1, 0:3:2, 0:3:3, 1:3:1, 1:3:2, 1:3:4;
  on E18U31 on 2026-11-17 0:3:3 and 1:3:3, never its peer ports, which have no login and no export
  but are Type `peer`.
  The action carries the command set of ADR 0018 in order (`controlport offline <nsp>`, `controlport
  config peer -ct point -f <nsp>`, then `controlport rst <nsp>` only if the lab shows the port stays
  offline: unconfirmed), printed for a consultant to paste in the first slice and run by the tool once
  the write lands (R4), and the restore lines from `showport -par` (R5).
- **conflict**, with the array's own facts in the sentence:
  - not on the array: *0:9:1 is not on this array (showport has no such port).*
  - not FC: *0:4:3 is not a Fibre Channel port (Type free, protocol IP). Peer ports are FC ports.*
  - serving hosts: *1:3:2 serves hosts (Type host; logged in: an unnamed initiator 1000040973C52799).
    The tool never takes a port from hosts: pick a free port, or move the hosts first.* This holds
    whatever the Label says.
  - logins or exports on a `free` port: same sentence, naming the hosts or the exported volumes.
  - another role: *0:3:2 is Type rcfc / disk / iscsi …; the tool changes only free FC ports.*
  - mode change prohibited: *0:3:2: the array does not allow a mode change on this port (showport -c).*
  - persistent-port partner in use (Primera): *0:3:1 is the failover partner of 1:3:1 (state
    failed_over); changing it removes that path protection.*

  Plan-level **blocker**: fewer than two ports that are `exists` or `create` on two different nodes,
  with the same sentence as the sheet rule. **Notes** (not blockers): both peer ports end up on one
  fabric by port parity (ADR 0009) — *"0:3:2 and 1:3:2 are both on the even fabric (F2) by port
  number; a fabric failure stops the migration"* (whether HPE requires one per fabric is unconfirmed,
  see §6); a planned port's link is `loss_sync` (no cable or no switch port: it can be set, but zones
  will not work until it is cabled); a planned port whose WWPN a zone still names in a switch's
  `cfgshow` (the zoning step's read-only switch read, `parse_active_zones`): *"0:3:3 (20330002AC02D495)
  is still in zone <zone> on <switch>: a host that is switched off may use this port. Ask the SAN team
  before setting it."* With no switch read in the run: *"The zones on 0:3:3's WWPN were not checked
  (no switch read): ask the SAN team before setting it."* The array cannot see zones, and a `free` port
  may still be zoned to a host that is off (§6.9, ADR 0018 *Risks*).

**R4 — The command set first, the tool's write later** (ADR 0018: accepted, write deferred).

*First slice: the command set.* The section prints each create's commands in sheet order (Copy /
Download .txt), with the removal set (R5) beside them, so the undo exists before anything is pasted.
The tool changes nothing, so there is no approval tick. The consultant pastes the lines on the array's
CLI, then presses *Read the array again*. That read is judged exactly as the apply will judge its own
read-back: each planned port must read Type `peer`, Connmode `peer`, ConnType `point`, **and every
other port's mode and Type must be unchanged from the read the plan was made from** (the CLI help warns
a mode change can move a partner port; LESSONS 44). Sentences: *"0:3:2 is now a peer port (port WWN
20320202AC02DEF2)."* / *"0:3:2 did not come back as a peer port (Type free, state offline)."* /
*"0:3:1 changed as well (mode target, now initiator): check the array before going on."* The new WWPN
read here is the one zoning uses (R7). One function judges both this read and the apply's read-back
(LESSONS 41).

*Later: the tool's write*, once the lab has answered ADR 0018's *Must confirm live before the write*
and the owner has said yes; over the array-port client of ADR 0025 condition 7. Only after the operator
ticks the approval sentence *"I approve setting these N ports to peer mode on <array>. They stop
serving anything else."* Port by port in sheet order, stopping at the first refusal: offline, config,
(rst), then read back `showport` and `showport -par`. Each command's answer is checked like SPEC-021 R4
(a line starting `Error` is a refusal; no answer in the exec timeout is a refusal). After each port the
read-back is judged as above; a port that does not read back as peer stops the apply with the same
sentence. The approval clears on every new read (LESSONS 6).

**R5 — The removal set** (SPEC-007 pattern): text the operator pastes, never run by the tool, in
reverse order. Printed with the command set for every create (first slice), or written to the run's
removal set before the port's first command (the write, ADR 0025 condition 4); after the read it keeps
only the ports that changed. Per port, from the `showport -par` read before the change:
`controlport offline <nsp>`, `controlport config <old connmode> -ct <old conntype> -f <nsp>`, then
`controlport rst -f <nsp>`, kept on every port whatever the change needed, so a port left offline comes
back. A port held offline in its old mode (the array refused its `config` with an `Error` line, or the
read after the paste shows it so) gets `controlport rst -f <nsp>` only, the help's way back online.
`rst` takes `-f` (`controlport rst [-m <mode>|-l|-i] [-f] <node:slot:port>...`, every captured help,
OS 10.5.0 to 10.6.0); `offline` has none (`controlport offline <node:slot:port>...`) and asked *"Are you
sure you want to run controlport offline on port 0:3:1? select q=quit y=yes n=no"* on rack13-ARCUS
(2026-11-17). The line stays, with a plain note on the page and as a `#` line at the head of the
command set and the removal set: *"`controlport offline` asks the array's own question (y, n or q)
every time and has no option to skip it: paste the lines one at a time and answer y when it asks.
Pasted as a block, the next line is taken as the answer."* Whether the tool's own write can send it
without a prompt is ADR 0018's open question (ADR 0025 condition 6). A port
whose `config` gave no answer in the exec timeout gets the whole restore, since its mode is unknown. A
create needs the `showport -par`
read: without it the plan blocks, because the change could not be undone. Header: *"Undo the peer
ports this run set. Remove the SAN team's peer-port zones and any migration that uses these ports
first."* BL-27's removal set goes above this block.

**R6 — Verify** (read-only, runs again from the Verify step): per planned port, Type `peer`, Connmode
`peer`, state `ready`. Sentences: *"0:3:2 is a peer port, link ready."* / *"0:3:2 is a peer port but its
link is loss_sync: check the cable and the switch port."* / *"0:3:2 is not a peer port (Type free)."*
Whether the source array's ports are visible through the peer port (after zoning) is BL-27's verify.

**R7 — Zoning** (ADR 0012: a command set for the SAN team, never a switch write). Reuse the existing
designer and renderer (`zoning_plan.render_commands`): one single-initiator single-target zone per
(peer port, source array port) pair from the sheet, on the fabric where both are in the name server.
The peer port's WWPN is **the one read after the change** (R4: the read after the paste, later the
apply's read-back), never the one read before: if the mode change gives the port a new WWPN, a zone
built from the old one is silently dead (LESSONS 32), and so is any zone that already named the old
WWPN (R3's `cfgshow` note names those for the SAN team).
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
StepShell) has its own command set, and with the write its own approval tick and button, because its
consequence differs from adding a VLAN. First slice (R4):

```
Peer ports                                                        [ Read the array again ]
Status: plan ready · 2 ports to set, 0 already peer, 0 conflicts
┌ Port  │ Now                     │ After        │ Why ─────────────────────────────────────┐
│ 0:3:2 │ free · FC · loss_sync   │ peer, point  │ free, nothing logged in, no exports       │
│ 1:3:2 │ free · FC · loss_sync   │ peer, point  │ free, nothing logged in, no exports       │
└───────┴─────────────────────────┴──────────────┴───────────────────────────────────────────┘
Note: 0:3:2 and 1:3:2 are both on the even fabric by port number.
Commands to paste on rack13-ARCUS (4 lines)                          [ Copy ] [ Download .txt ]
Removal set, to keep before you paste (6 lines)                      [ Copy ] [ Download .txt ]
Paste the commands on the array's CLI, then press Read the array again.
After the read: result per port · new WWPN per port · Verify
```

When the write lands, the two command blocks become *▸ Show 4 commands*, the approval tick *"I
approve setting these 2 ports to peer mode on rack13-ARCUS. They stop serving anything else."* and
*Set the peer ports*, disabled until ticked; the removal set shows after the apply.

**R9 — The as-built.** A section *Peer ports*: per port the mode, ConnType, state, node and port WWN
after the change, virtual peer ports from `showport -peer` when present, the commands in order and who
ran them (pasted by a consultant, or run by the tool), the peer-port zones designed in the run with
their command set, and the removal set.

## 3. Non-goals

Virtual peer ports (`-virt_ports`), `-unique_nwwn`, labels (`controlport label`), changing a port that
serves hosts or carries Remote Copy, iSCSI/NVMe/IP ports, the migration itself (SPEC-027), any switch
write, a peer port on the source array, running the removal set.

## 4. Verification

- Unit tests: `tests/unit/test_peer_ports.py`. Strict `xfail` until each part is built (the work
  packet names which step turns which test green); the guard tests on today's behaviour pass now.
  The read (R2) is green, pinned to rack13-ARCUS as one capture saw it (`peer_ports/rack13/`, OS
  10.6.0, 2026-11-16), to E18U31's two peer ports as one capture saw them (`peer_ports/E18U31/`, OS
  10.5.60, 2026-11-17: `showport`, `-par`, `-peer`, `-c`, `showhost -d`, `showvlun -a`, `GET /ports`),
  to D22U27 (OS 10.5.0) and VZ (OS 10.5.51) the same day, to the Primera's `showport`, and to the CLI
  help's `showport -peer` example. The plan tests use rack13's `rcip_pair/before/alletra/showport.txt` (2026-11-03) with
  `rack13_array/showhost_d.txt` (2026-09-13), when 0:3:3 still served a host, and the 2026-11-16
  `showport -par`; different days, said in the tests. No device output is invented: what is not
  captured is built from model objects.
- Captures: rack13-ARCUS taken 2026-11-16 (no peer port there); E18U31 (two FC peer ports), D22U27
  and VZ taken 2026-11-17, all in `tests/fixtures/peer_ports/<array>/`. The three tests that waited
  for a port in peer mode are green. Still owed, and only a live change gives it: one port read before
  and after the change (the WWN question, §6.2).
- Live run of the first slice (needs the owner's yes and a lab booking): two free FC ports on two
  nodes planned, the printed command set pasted by a consultant with `showport`, `showport -par`,
  `showport -c` and `showhost -d` saved before, after the change and after the restore; the read after
  the paste judged (R4), verify, the removal set pasted and the ports read back exactly as before.
  It also answers ADR 0018's *Must confirm live before the write* (a prompt despite `-f`, `rst` after
  `config`, the WWN at the three moments, every other port unchanged), which the tool's write waits
  for. Checklist in the work packet. Candidate ports (the owner chooses): rack13-ARCUS `0:3:3` and
  `1:3:4`, free, linked and in a fabric with nothing zoned to them, one per fabric by parity (they
  served host 10.132.30.136 until at least 2026-11-03); or E18U31's peer ports `0:3:2` and `1:3:2`,
  restored and set again (they see the source array). **On 2026-11-16 rack13's `0:3:2` and `1:3:2`
  (and `0:3:1`, `1:3:1`) have no SFP and no link** (`loss_sync`): the change itself can be tested on
  them, but zones and BL-27's migration cannot until they are cabled.

## 5. Decisions taken here (defaults, owner may change)

1. The tool changes only `free` FC ports with no login and no export; it never takes a port from hosts.
2. Two ports on two nodes minimum; one-fabric-only is a note, not a refusal.
3. The write plane is ADR 0018, accepted 2026-11-17: the command set first (printed, pasted by a
   consultant, read back by the tool); the tool's write over the array-port client of ADR 0025
   condition 7 once the live captures are in and the owner says yes. Not WSAPI (no call known), not
   DSCC (rejected for now).
4. Zoning reuses the host-zoning renderer; the peer WWPN comes from the read-back.
5. Peer ports live in SPEC-024's shared *Array ports* step (`ports`), not a step of their own.

## 6. Open questions (for the owner, or capture on the lab)

1. Does `controlport config peer -ct point -f <nsp>` on an offline port bring it back online, or is
   `controlport rst <nsp>` needed? Does it prompt despite `-f` (help: *"unless the TPDFORCE_OVERRIDE
   environment variable is set, the command will ask for confirmation even if the -f flag is
   specified"*)? An SSH exec has no terminal to answer.
   *Still open on 2026-11-16:* rack13's help (OS 10.6.0) reads the same; its peer example omits both
   `offline` and `-f`, and `-ct` resets the port. Only the first live change answers it.
   *2026-11-17:* the owner made it a condition: the tool's write waits for this answer (ADR 0018
   *Must confirm live before the write*); the first slice's pasted command set gives it.
2. Does the port WWN change when the mode changes (E18U31 suggests yes)? *2026-11-16:* the CLI help's
   own `showport -peer` example has the same `0202` pattern as E18U31's peer ports, so very likely;
   the moment of the change is still to be seen live (R7 already takes the WWPN from the read-back).
   *2026-11-17:* E18U31's peer ports carry `0202` in WWN bytes 3 and 4; every FC port in host mode on
   E18U31, rack13, D22U27 and VZ carries `0002`, and a peer port loses the NVMe virtual port (`0102`)
   the host-mode ports have. No capture holds E18U31's 0:3:2 in host mode (`20320002AC02DEF2`), so the
   change itself is still unseen. `showport -peer` does not help here: it lists the array's own peer
   ports, not the source's WWNs.
3. ~~`showport -par` column layout on OS 10.5~~ *Answered 2026-11-16 (rack13, OS 10.6.0):*
   `N:S:P Connmode ConnType CfgRate MaxRate Class2 UniqNodeWwn VCN IntCoal TMWO`, as in the help.
4. WSAPI: is there a `PUT /ports/<nsp>` that sets the FC connection mode, and what does `GET /ports`
   report for an FC peer port (mode 3 initiator with type 6 peer, per python-3parclient's constants)?
   *Partly answered 2026-11-16:* `GET /ports` reports `connectionMode` (1 disk, 2 host) and
   `connectionType` (2 point, 99 eth) beside mode and type. A peer port's values and any write call
   are still unknown: the capture was GET only, on an array with no peer port.
   *GET answered 2026-11-17 (E18U31, WSAPI 1.15.60):* an FC peer port is `mode` 3, `type` 6,
   `connectionMode` 4, `connectionType` 2, with the source array's node WWN in `device`. A write call
   is still unknown (nothing was probed). The DSCC storage-fleet API documents one (`PUT
   …/devtype4-storage-systems/{systemId}/ports/{id}/fc`, `configMode` `Peer`); ADR 0018 option D
   rejects it for now.
5. HPE's rules for peer ports in a B10000 data migration (how many, one per fabric or per node, same
   slot:port partner): the public HPE pages could not be reached through the search tools on
   2026-11-16 (Bing returned unrelated pages, DuckDuckGo a bot check). Needs the HPE data migration
   guide for the B10000 or the owner's field practice.
6. Does the Alletra MP have persistent-port partners like the Primera (no Partner column in its
   `showport`)? *2026-11-16:* still no Partner column on OS 10.6.0 and no failover field in
   `GET /ports`; the partner check stays, and only a Primera can trigger it.
7. SPEC-024 asks whether a peer-enabled iSCSI port (`showport -iscsi` column `Peer_Enabled`, `N` on
   every E18U31 iSCSI port captured 2026-10-07) should be refused for VLANs. For this spec it does not
   change anything: peer ports here are FC only, and an iSCSI port on the *Peer ports* tab is already a
   conflict (*"not a Fibre Channel port"*). It matters for BL-27 if migration may also run over iSCSI:
   a peer-enabled iSCSI port is then the iSCSI counterpart of an FC peer port. Recommended answer, in
   line with decision 1 (never change a port that has another role): refuse, as SPEC-024 proposes.
   What `Peer_Enabled Y` means on the array is unconfirmed: capture on the lab.
8. ~~Write plane shared with SPEC-024~~ *Answered 2026-11-17:* ADR 0025 condition 7, one array-port
   write client for ADR 0017 (VLANs), ADR 0018 (peer ports) and ADR 0024 part B (RCFC ports), built
   from the (port, form family) pairs of the approved plan. ADR 0018 *FC port-mode changes* gives the
   one design for peer and RCFC mode changes.
9. *New, 2026-11-16.* Type `free` means nothing is logged in now (rack13 0:3:3 went from `host` to
   `free` when its host left). A free port that is cabled and in a fabric may still be zoned to a host
   that is switched off, and that host loses the path when the port becomes a peer port. The array
   cannot see zones. *Answered 2026-11-17:* a plan note from the switch's `cfgshow` for that port's
   WWPN (R3), and a note that the zones were not checked when the run has no switch read.

**Note for BL-27 (migration).** On rack13-ARCUS the four free FC ports with no link (0:3:1, 0:3:2,
1:3:1, 1:3:2) report no SFP: they need transceivers and cables before any peer-port live run there
that goes as far as zones or a migration.

## 7. Sources

Captured fixtures named above; python-3parclient 4.5 `client.py` (installed in the venv); the
storage-fleet mirror page `devicetype4fcportedit.md` (scraped 2026-06-07); ADR 0004, 0009, 0012, 0015,
0018, 0024 (BL-50), 0025 (BL-58); SPEC-007, SPEC-021, SPEC-031 (BL-50); LESSONS 6, 32, 41, 42, 44.
