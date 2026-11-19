# SPEC-024 — VLAN-tagged iSCSI addresses on the array's ports, set up by the tool

**Status:** first slice built 2026-11-17, pending live run (R1 to R3 and R6 to R8: the sheet, the read,
the plan with its printed lines, the *Array ports* step, Verify and the as-built; work packet steps 1
to 7). R4 waits on the live confirmation (§6) and the owner's yes. **Amended 2026-11-17** (the owner's
decision after the live check, ADR 0017 *Amendment*): the lines add the address without its gateway; a
sheet gateway goes in a separate change-window set the tool never sends (R3, R5 to R7). Proposed
2026-11-16; the read-side parsers are built on the captures of rack13-ARCUS (OS 10.6.0, 2026-11-16)
and three OS 10.5 arrays (2026-11-17), §9 ·
**Decision:** [ADR 0017](../adr/0017-iscsi-vlan-write-plane.md) (accepted 2026-11-17: the CLI forms
on ADR 0025's one array-port write client; a first slice without the apply) ·
**Tracker:** BL-25 (issue #11) · **Work packet:** [workpackets/BL-25.md](../workpackets/BL-25.md) · **Tests:** `tests/unit/test_iscsi_vlans.py` (strict
xfail until built) · **Sibling:** SPEC-025 (BL-26, peer ports), written in parallel; see §8

## 1. Problem, and what the tool reads today

SCOPE area 3 lists "VLAN configuration"; the tracker calls it *read-only today*. What that means in
the code on 2026-11-16 (main `b7006373`):

| What | Where it is read | Where it shows |
|---|---|---|
| File service ports: the `VLAN` column of `showport -file` (`untagged` or a tag) | `parse_file_ports` → `EthernetPort.vlan` (`application/provisioning/discovery.py`) | Discovery page, *file service ports* table, column VLAN |
| iSCSI ports: `showport -iscsi`, address only | `parse_iscsi_ips` → `ArrayPort.address` | Discovery page, *array iSCSI ports* table. The `VLAN`/`VLANs` and `Peer_Enabled` columns are read past and dropped |
| iSCSI VLAN interfaces: `showport -iscsivlans` | lab capture scripts only (`lab/iscsi_port_probe.py`, `lab/rcip_pair_capture.py`); no parser, no fixture in the repo (since then: `parse_iscsi_vlans` and the lab fixtures, §9; nothing calls it yet) | nowhere |
| RCIP ports: address, mask, gateway (`showport -rcip`) | `parse_rcip_detail`, `application/replication/read.py` | Discovery, Replication step |

Nothing writes a VLAN, and the as-built document names none.

Engineers put iSCSI on its own VLAN as a matter of course, so a host can reach an iSCSI port only
when the array's port carries an address on that VLAN, the switch port carries the VLAN tagged, and
the host has an address on it. Today the engineer sets the array's side by hand before the run, and
the tool's iSCSI gate (ADR 0012 revised: an iSCSI export waits for a login) holds every export until
then. This spec has the tool set the array's side from the workbook, under the same plan, approve,
apply, removal set, verify and as-built pattern as SPEC-001, SPEC-007 and SPEC-021.

## 2. Scope

**In:** VLAN-tagged IPv4 interfaces on the array's iSCSI ports (Type `host` or `free`, Protocol
`iSCSI`): one VLAN ID, address, netmask and optional gateway per interface. Created only; an
interface already on the array is left as it is.

**Out (non-goals):** the untagged (base) address of an iSCSI port; changing a port's role or mode
(`controlport config iscsi` needs an array reboot); MTU, STGT, iSNS and flow control; IPv6; VLANs on
RCIP ports (the help of OS 10.5.0, 10.5.51 and 10.5.60 lists no `-vlan` on `controlport rcip`,
captured 2026-10-07 and 2026-11-17; OS 10.6.0's does, rack13-ARCUS 2026-11-16, as the ED8 CLI guide
said, research 2026-10-07 §2; out of scope by the owner's decision of 2026-11-17, because they would
work on OS 10.6 arrays only); VLANs on file ports (BL-28)
and NVMe/TCP ports; the host side (ESXi port groups, Windows and Linux NICs); **any write to a switch**
(ADR 0012; §R3 gives the network team a sentence instead).

## 3. Requirements

**R1 — The sheet.** A new optional row-table tab, *iSCSI network*. One row per VLAN interface.
Columns: *Port (N:S:P)* (required, stored as text so Excel keeps 0:4:1), *VLAN ID* (required),
*iSCSI address* (required), *Netmask* (required), *Gateway (optional)*. Intro line: *"Fill this only
when the tool should add VLAN-tagged iSCSI addresses to this array's iSCSI ports. One row per port and
VLAN. Put each VLAN on a port of both nodes. The switch ports are not changed by the tool."* A
workbook without the tab, or with a blank one, parses exactly as today and the ports step has nothing to do (R8).

Each rule is refused at upload with one sentence, prefixed
`iSCSI network tab — row '<port> VLAN <vlan>':`
*Since 2026-11-19 (owner, ADR 0005): the sentence is listed at upload and on the Initialisation sheet page, and refuses the run when it is created with a step that uses this tab; it no longer stops the upload or a Full onboarding run.*

| Rule | Sentence after the prefix |
|---|---|
| a required cell is blank | `missing <labels>.` |
| port shape | `Port must be N:S:P, like 0:4:1 (got '<text>').` |
| VLAN ID | `VLAN ID must be a whole number from 1 to 4094 (got '<text>').` (the range is the array's own help: `-vlan` *"Specifies the VLAN tag number (1 to 4094)"*, `tests/fixtures/rc_pair/help/help_controlport.txt`; confirmed for iSCSI, rack13-ARCUS, OS 10.6.0, 2026-11-16: `help controliscsiport` *"For other commands, the VLAN tag is in the range [1-4094]"*; OS 10.5.x, 2026-11-17: *"Indicates the VLAN tag number (1 to 4094)"*) |
| address | `iSCSI address '<text>' is not an IPv4 address.` |
| netmask | `Netmask '<text>' is not a netmask (like 255.255.255.0).` (the same check as the Replication network tab) |
| gateway | `Gateway '<text>' is not an IPv4 address.` |
| gateway off the network | `Gateway <gw> is not on the network <net> of <ip>.` |
| network or broadcast address | `<ip> is the network or broadcast address of <net>.` |
| one port, one VLAN, twice | `port <port> has VLAN <vlan> twice.` |
| one address, twice | `address <ip> is used twice.` |

Two rules across rows, with the prefix `iSCSI network tab —` only:

| Rule | Sentence |
|---|---|
| one VLAN, two networks | `VLAN <vlan> is on two networks: <net1> on <port1> and <net2> on <port2>. One VLAN is one network.` |
| two VLANs, one network | `VLAN <a> and VLAN <b> are both on <net>. Give each VLAN a network of its own.` |

The two cross-row rules are the tool's own (a VLAN is one IP network); the array may be more
lenient. They are refusals because a sheet that breaks them is almost always a typing slip.

**R2 — The read.** Read-only, over the read client (ADR 0001), one SSH session: `showport`
(each port's mode, state, type, protocol: `parse_showport_roles`, already pinned), `showport -iscsi`
(base address, netmask, gateway, `Peer_Enabled`), `showport -iscsivlans` (the VLAN interfaces),
`showport -rcip`, `showport -file`, `shownet` (management address and mask), `showhost -d` (which
IQNs are logged in on which port). Every one is already allowed by `ALLOWED_COMMANDS` (base word
`showport`, `shownet`, `showhost`); **no read allowlist change**. `showhost -d` gives the number of
iSCSI sessions on each port (one row per logged-in initiator and port, claimed or not), which the
change-window set states (R3; read since 2026-11-17). The `showport -iscsivlans` layout
is **confirmed (rack13-ARCUS, OS 10.6.0, 2026-11-16; E18U31, OS 10.5.60, 2026-11-17)**: `N:S:P VLAN
IPAddr Netmask/PrefixLen Gateway MTU TPGT STGT iSNS_Addr iSNS_Port`, no State column, and it also
lists each port's untagged address as a row with VLAN `untagged` (the same values as `showport
-iscsi`; a port with no address has no row, and with no address on any port the answer is `no ports
listed`). `parse_iscsi_vlans` leaves the untagged rows out: they are the port's base address, not VLAN
interfaces. A tagged row is captured (rack13-ARCUS, OS 10.6.0, 2026-11-17, `tests/fixtures/iscsi_vlan/tagged/`):
on a port whose only address is a VLAN address, `showport -iscsi` prints that address in the base
columns with no `*`. So the read takes a port's base address as untagged only when `showport
-iscsivlans` has an `untagged` row for that port, or the address is none of the port's VLAN addresses
(`untagged_addresses`); otherwise the port has no untagged address. WSAPI offers the same read
(`GET /ports/<n:s:p>/iSCSIVlans/`, confirmed by python-3parclient 4.5 `_getIscsiVlan` and answered
on rack13-ARCUS, VZ and E18U31, §9; OS 10.5.60 lists the untagged address in it as `vlanTag` 0, which
the parser leaves out). The tool does not use it: ADR 0017 took the CLI forms, and the answer differs
by OS (10.6.0 leaves the untagged address out, 10.5.60 lists it, `GET /ports` on 10.5.0 and 10.5.51
has no `iSCSIVlans` field). It waits for ADR 0017's later option A.

**R3 — The plan.** One action per sheet row, in sheet order, with the plan state words of SPEC-001:

- **exists**: the port already has that VLAN with the same address and prefix length (and the same
  gateway when the row and the array both have one: an interface without the row's gateway is what the
  tool's own line leaves, ADR 0017 amended 2026-11-17). No call. A row whose gateway the array lacks
  stays in the change-window set below.
- **create**: the port is an iSCSI port, has no interface on that VLAN, and nothing below applies.
  The action carries its CLI lines, printed as in SPEC-016: in the first slice for the engineer to
  read, and later the very lines the apply sends (ADR 0017). The CLI forms are the array's own (`help controliscsiport`, rack13-ARCUS, OS 10.6.0, 2026-11-16, and the
  same on OS 10.5.0, 10.5.51 and 10.5.60, 2026-11-17): one line per row,
  `controliscsiport addr <ip> <netmask> -vlan <vlan> -f <port>`, **with no gateway**, and the row's
  removal line (R5). It always carries `-vlan` with the row's tag (1 to 4094): without it the line
  changes the port's untagged address, which the tool never touches, and cuts off the hosts already
  logged in on it. When the row gives a gateway, the reason says so (*"…; gateway 192.0.2.1 not set by
  the tool (a change window's job)"*) and a note says why: *"0:4:2 VLAN 2999: the tool adds the address
  without the gateway 192.0.2.1. The gateway needs the port offline, so it is in a separate set for a
  change window."*
- **conflict**, with the reason, which blocks apply:

| Case | Reason |
|---|---|
| no such port | `<array> has no port <port> (showport).` |
| not an iSCSI port | `<array> <port> is not an iSCSI port: showport lists it as <mode> <state> <type> <protocol>. The tool never changes a port's role.` |
| peer-enabled iSCSI port | `<array> <port> is a peer-enabled iSCSI port (showport -iscsi: Peer_Enabled Y). The tool does not add VLANs to it.` |
| the VLAN is there with other values | `<array> <port> already has VLAN <vlan> with <ip> <mask> (gateway <gw>); the sheet says <ip2> <mask2> (gateway <gw2>). The tool never changes an address it did not set.` |
| the address is in use | `<ip> is already in use on <array>: <where>.` where is *management*, *iSCSI port 0:4:2*, *iSCSI port 0:4:1 VLAN 130*, *RCIP port 0:4:3*, *file port 0:4:1* |
| the network is taken | `<net> is already the network of <where> on <array>; a VLAN needs a network of its own.` where is the port's own untagged address or the management address |

Notes, not blockers: a VLAN on ports of one node only (*"VLAN 120 is only on node 0. If that node
stops, hosts on VLAN 120 lose every path."*); a port whose link is not `ready` (*"0:4:2 is offline:
the address is set, but no host reaches it until the link is up."*).

**The gateways, for a change window** (ADR 0017, amended 2026-11-17). Live on rack13-ARCUS, the
array refused `controliscsiport gw … -vlan 2999 -f 0:4:2` on a port that was up: *Port 0:4:2 is not in
offline state. To modify the Gateway IP, please use controlport to offline the port first.* Offline
stops every iSCSI session on the port, so the tool never sets a gateway. For every sheet gateway the
array does not have, the plan prints a separate, clearly labelled set, per port in port order:
`controlport offline <port>`, then `controliscsiport gw <gw> -vlan <vlan> -f <port>` for each such row
on that port, then `controlport rst -f <port>` (the forms of `help controlport` and `help
controliscsiport`, OS 10.5.0 to 10.6.0). Above it: *"The tool does not set these gateways. The array
sets a VLAN gateway only while the port is offline, and taking a port offline stops every iSCSI session
on it. Hosts on the VLAN's own subnet need no gateway. Run these lines only in a change window agreed
with the customer."*, then per port *"0:4:1 carries 3 iSCSI sessions now (showhost -d): all of them
stop while the port is offline."* or *"0:4:2 has no iSCSI session now (showhost -d). Check again just
before the change window."*, and the note that `controlport offline` asks *y/n/q* (paste one line at a
time, answer `y`). The tool never sends this set; a consultant pastes it, by hand, in that window.

**The switch side, as a sentence.** The plan ends with one line per sheet port that has a planned or
existing VLAN, whatever its row's state (a conflict row on a port that already carries a VLAN keeps the
line; live 2026-11-17 it was dropped), for the network team: *"Switch port cabled to `<array>` 0:4:1: carry VLAN 120, 130
tagged (802.1Q); keep the untagged (native) VLAN as it is."* The second half matters: the hosts already
logged in use the port's untagged address, and a trunk port with no native VLAN would drop them. No
command: the tool reads no Ethernet switch, does not know its vendor, and
never writes one (ADR 0012). The page, the removal set header and the as-built carry the same lines.

**R4 — Apply.** Not in the first slice (ADR 0017): built only after the live confirmation of §6 and
the owner's yes. Only from a plan the operator approved with a tick, and only while that plan stands:
a new read, a sheet change or a restart withdraws it (LESSONS 6). The apply first reads again (R2)
and refuses if any action's judgement would now differ (LESSONS 37). Then, per *create* action in
sheet order, stopping at the first refusal: the action's removal line (R5) goes into the run's removal
set, then the `addr` line is sent. That one form is all it sends, with `-vlan`, over the one array-port
write client of ADR 0025, built from the approved plan's (port, iSCSI VLAN) pairs: it never sends a
`gw` (ADR 0017 amended 2026-11-17: it needs the port offline), a `delete` or a `controlport` line,
never takes a port offline and never changes a port's role. After each write, read `showport -iscsivlans` and check the interface is there
with the planned values and the port's untagged row is unchanged; a write the array accepted but the
read does not show is a failure. Every write and every read goes through `command_log.record` with
the client's secrets.

**R5 — The removal set.** First slice (2026-11-17, live finding 6): the plan prints one line per
*create* action, last first, with the command set, so the undo is kept before anything is pasted. With
the apply: one line per *create* action whose `addr` the apply sent, last sent first,
as CLI lines the operator pastes (SPEC-007); the apply never runs one. Each line is written into the
run's removal set before its `addr` goes (ADR 0025: the undo comes before the write). The delete
takes the VLAN address with whatever gateway it has, so the change-window set has no undo line of its
own. The delete form is the array's own, taken from
`help controliscsiport` (**confirmed, rack13-ARCUS, OS 10.6.0, 2026-11-16; the same on OS 10.5.0,
10.5.51 and 10.5.60, 2026-11-17**):
`controliscsiport delete -vlan <vlan> -f <port>`. A line without `-vlan` deletes the port's whole
configuration, untagged address included (the help's own example, `controliscsiport delete -f
1:1:1`), and ends every session on it, so the tool never renders one. Header: *"Removing an interface ends
every iSCSI session on it. Check `showhost -d` first."* Interfaces that existed are never in it.

**R6 — Verify.** The *Verify configuration* step compares each sheet row with `showport -iscsivlans`:
*present*, *missing* or *different (field: array value, sheet value)*. Read-only. The gateway is
compared only when the sheet and the array both have one (the rule of R3's *exists*); a row whose
gateway the array lacks is *present* with the note *"The gateway <gw> is not set: the tool leaves it to
a change window (it needs the port offline)."*

**R7 — The as-built.** A section *iSCSI network* when the array has any VLAN interface or the sheet
has the tab: every VLAN interface on every iSCSI port (port, VLAN, address/prefix, gateway, MTU,
and the port's state from `showport`, since `showport -iscsivlans` has no State column), each marked
*set up by this run* or *already there*; *Gateways for a change window* with R3's sentence and lines
for any sheet gateway the array does not have; then the switch sentences of R3, then
the run's removal lines in the provisioning record's removal block.

**R8 — The page.** A step *Array ports* (key `ports`, kind `provision`) between *Discovery* and *SAN
Zoning*, in every preset that has *Discovery* (Provision only, Both, Provision then replicate) and
offered in Custom. It must come before *SAN Zoning*: the zoning check is what sees an iSCSI host's
login and opens its export. With no rows on the iSCSI network tab the page says *"The sheet asks for
no iSCSI VLANs. Nothing to set up here."*, reads nothing, and the step is complete. Layout, on
`ui/StepShell`:

1. `StatusLine`: *Not read yet* / *Plan ready: 4 to add, 0 conflicts* / *Set up: 4 added* / *Stopped at 1:4:1*.
2. *What the sheet asks for*: the rows.
3. Button *Read the array and plan*. Then the plan table: Port, VLAN, Address, Gateway, Plan
   (exists / add / conflict), Why, and in a folded `Section` the CLI lines of each add (R3).
4. *For the network team*: the switch sentences, with *Copy*.
5. Tick *"I have checked this plan. Add these iSCSI addresses to `<array>`."* and the button *Add the
   iSCSI addresses*, disabled while there is a conflict or no tick.
6. Result, the removal set (*Copy*, *Download .txt*), and *Read the array again*.

Items 5 and 6 come with the apply (R4). In the first slice the page ends with *Read the array again*
and says *"Adding the addresses is not built yet."*

A mockup goes in `frontend/mockups` for review before the page is built.

## 4. Data contract

```python
# domain/network.py (no I/O)
class IscsiVlanRequest(BaseModel):        # one sheet row (R1)
    nsp: str; vlan_id: int; ip: str; netmask: str; gateway: str = ""
class IscsiPortAddress(BaseModel):        # one row of `showport -iscsi` (built)
    nsp: str; ip: str = ""; netmask: str = ""; gateway: str = ""; peer_enabled: bool = False
    vlans: str = ""                       # the VLANs (older: VLAN) column as printed; display only
class IscsiVlanInterface(BaseModel):      # one TAGGED row of `showport -iscsivlans` (built)
    nsp: str; vlan_id: int; ip: str; netmask: str; gateway: str = ""; mtu: str = ""
    # no `state`: the view has no State column (rack13-ARCUS, 2026-11-16); R7 takes it from showport
class PortNetworkView(BaseModel):         # what R2 read, one array
    name: str = ""; mgmt_ip: str = ""; mgmt_netmask: str = ""
    roles: dict[str, PortRole]            # PortRole from domain/replication.py (SPEC-021), shared
    iscsi_ports: list[IscsiPortAddress]; vlans: list[IscsiVlanInterface]
    other_addresses: dict[str, str]       # address -> "RCIP port 0:4:3" / "file port 0:4:1"
class IscsiVlanAction(BaseModel):
    nsp: str; vlan_id: int; state: Literal["create", "exists", "conflict"]
    reason: str = ""; cli: str = ""       # the addr line, with -vlan; never a gateway (ADR 0017 amended 2026-11-17)
    undo: str = ""; gateway_cli: str = "" # a create's removal line; the gw line for the change-window set
class IscsiNetworkPlan(BaseModel):
    array: str = ""; actions: list[IscsiVlanAction]; blockers: list[str]; notes: list[str]
    switch_handoff: list[str]
    removal_lines: list[str]              # each create's undo, last first (R5, first slice)
    gateway_window: list[str]; gateway_notes: list[str]   # the change-window set and why (R3), never sent
class IscsiVlanOutcome(BaseModel):
    nsp: str; vlan_id: int; status: Literal["created", "exists", "failed"]; detail: str = ""
    # failed: sent, then refused or not seen in the read-back; its removal line stays (R5)

ProvisioningIntent.iscsi_network: list[IscsiVlanRequest] = []          # domain/provisioning.py

# application/platform/init_sheet.py
ISCSI_NETWORK_SHEET_NAME = "iSCSI network"; ISCSI_NETWORK_COLUMNS = [...]
# application/provisioning/discovery.py (built)
def parse_showport_iscsi(text: str) -> list[IscsiPortAddress]
def parse_iscsi_vlans(text: str) -> list[IscsiVlanInterface]          # untagged rows left out
# adapters/array/wsapi_client.py (built; field names from E18U31's untagged records, vlanTag 0 left out;
# unused until ADR 0017's later option A)
def parse_iscsi_vlans_wsapi(nsp: str, body: object) -> list[IscsiVlanInterface]
# application/provisioning/iscsi_network.py
def plan_iscsi_vlans(requests: list[IscsiVlanRequest], view: PortNetworkView) -> IscsiNetworkPlan
def removal_lines(outcomes: list[IscsiVlanOutcome]) -> list[str]
```

## 5. Acceptance (`tests/unit/test_iscsi_vlans.py`)

Sheet: the tab parses into `iscsi_network`; every R1 sentence; the template has the tab with the
port column as text; a workbook without it parses as today. Parsers: `showport -iscsi` from the
E18U31 and rack13-ARCUS captures (both layouts: `VLAN` and `VLANs Peer_Enabled`); `showport
-iscsivlans` and the WSAPI iSCSIVlans answer from rack13-ARCUS (untagged rows and empty answers),
D22U27 (no iSCSI port), VZ (offline ports, `no ports listed`) and E18U31 (ready ports at MTU 9000, the
`vlanTag` 0 record); the help forms of R3 and R5 on OS 10.5 and 10.6; a tagged row and a tagged WSAPI
record from the capture still owed (§9). Plan (on E18U31's real `showport`, `showport -iscsi`, `showport -rcip` and
`shownet`): add on an iSCSI port; conflict on FC, RCIP, free IP, a missing port, a peer-enabled
port; exists; other values; address in use (iSCSI, RCIP, management); network taken; one-node note;
switch sentences; every printed line carries `-vlan`, and no client the tool has today takes one.
Removal: one line per create the apply sent (created or failed), last first, each with `-vlan`. Step
registry: `ports` sits between `discover` and `zoning`. Discovery: the starred address of the tagged
capture read without its `*`. Apply (later slice): the port client's two forms, each accepted and its
near-misses refused (ADR 0025), a VLAN apply's client refusing `controlport offline` on its own port,
and the forms pinned to the live confirmation's capture.

## 6. Live run (what "done" needs, rule 7)

**Before the apply is built: the live confirmation** (ADR 0017, with the owner's yes). On
rack13-ARCUS, the candidate array: one VLAN interface added on a ready iSCSI port from the array's CLI,
then deleted, with `lab/iscsi_vlan_capture.py` run before, while it is there (into `tagged/`) and
after. It must show:

- `controliscsiport addr ... -vlan N` leaves the untagged address and its sessions alone: `showport
  -iscsi` and `showhost -d` are the same before and after;
- `controliscsiport delete -vlan N` removes VLAN N only;
- `-f` never prompts, on `addr` and `delete` (`gw` is no longer the tool's: ADR 0017 amended 2026-11-17);
- a tagged row of `showport -iscsivlans`, its WSAPI record, and `showport -iscsi` with the `*` marker
  (§9), so the parsers are pinned to it before the apply.

If one of the first three does not hold, the apply is not built and the step stays at the first slice.

**The live run of the whole step.** On a lab array with iSCSI ports cabled to a switch that carries a test VLAN (to be agreed with the lab).
**rack13-ARCUS is the candidate (owner, 2026-11-17):** on 2026-11-16 its iSCSI ports 0:4:1 and 1:4:1 were ready on
10.93.18.10 and .12 (10.93.18.0/23, untagged, behind the lab router 10.93.18.1), with two lab hosts
logged in; 0:4:2 and 1:4:2 were offline. **E18U31 could serve too:** on 2026-11-17 (OS 10.5.60) all
four of its iSCSI ports were ready, untagged, on 10.1.1.0/24 (0:4:1, 1:4:1) and 20.1.1.0/24 (0:4:2,
1:4:2), no gateway, MTU 9000, with three lab hosts logged in on every port. The lab still has to say
which VLAN the switch ports carry tagged and which subnet goes with it.
1. `lab/iscsi_vlan_capture.py` run and its files committed under `tests/fixtures/iscsi_vlan/` (done
   for rack13-ARCUS, D22U27, VZ and E18U31, none with a tagged interface; `tagged/` comes from the
   live confirmation above).
2. A run with two rows, one port per node, on the VLAN the lab gives. Interfaces have no name to
   prefix with `zz_`, so the lab script checks first that the port has no interface on that VLAN,
   journals what it adds, and removes it at the end even after a failure.
3. Plan shows 2 *add*; a third row on an FC port shows the conflict sentence; apply adds both;
   `showport -iscsivlans` shows them; the plan read again shows 2 *exists*.
4. A lab host on that VLAN logs in; the SAN Zoning check shows the login; an export to it passes.
5. Verify configuration reports both *present*; the as-built has the section.
6. The removal set, pasted as rendered, removes both; `showport -iscsivlans` is back to the start.

## 7. Open questions for the owner

1. Answered 2026-11-17: ADR 0017 is accepted, the CLI forms on ADR 0025's one array-port write
   client. R4 waits on the live confirmation (§6) and the owner's yes.
2. Answered (§9): layout, create and delete syntax, the same on OS 10.6.0 (rack13-ARCUS) and OS
   10.5.0, 10.5.51 and 10.5.60 (D22U27, VZ, E18U31). Still open, and now confirmed live before the
   apply is built (§6): whether a VLAN can be added while the port carries sessions, leaving the
   untagged address and its sessions alone (rack13-ARCUS's 0:4:1 and 1:4:1 carry two hosts,
   E18U31's four ports three).
3. Does the array refuse two VLANs on one port in the same network, or a VLAN in the port's own
   untagged network? R1 and R3 refuse both by the tool's rule until the array says.
4. The lab: which array has iSCSI ports on a switch that can carry a test VLAN (E18U31's 0:4:1 to
   1:4:2 were live on 10.30.14.0/24 on 2026-10-05 and on 10.1.1.0/24 and 20.1.1.0/24 on 2026-11-17;
   rack13-ARCUS's 0:4:1 and 1:4:1 on 10.93.18.0/23 on 2026-11-16, §6). rack13-ARCUS is the
   candidate (owner, 2026-11-17); the lab still names the VLAN and subnet for §6's host login.
5. Peer-enabled iSCSI ports: refuse (as proposed), or allow? Decide together with SPEC-025.
6. The new step `ports`: agree it with SPEC-025 so both sit in one step (§8).

## 8. Fit with SPEC-025 (BL-26, peer ports)

Both specs configure array ports from the sheet before zoning. Proposed to share: the *Array ports*
step (R8) with one section per tab; `PortRole` from `parse_showport_roles` as the one source of a
port's role; the conflict wording *"The tool never changes a port's role"* where a row names a port of
another kind; rows keyed by the N:S:P as text; one removal block per run. Whichever spec merges
second adapts to the first.

## 9. What the captures settled (rack13-ARCUS, OS 10.6.0, 2026-11-16)

`lab/iscsi_vlan_capture.py`, read-only, files in `tests/fixtures/iscsi_vlan/rack13/` (README there).
No port had a tagged interface, so everything about a tagged row is still owed.

**Confirmed:**

- `controliscsiport addr <IP_address> <netmask|prefix_len> [-vlan <vlan_tag>] [-f] <node:slot:port>`,
  `gw <gw_address> [-vlan <vlan_tag>] [-f] <node:slot:port>` and `delete [-vlan <vlan_tag>] [-f]
  <node:slot:port>` exist; the tag is 1 to 4094 (0 to 4094, 0 = untagged, for the initiator commands).
  The address and the gateway are two commands. `allowpeer [-f] <false/true> <node:slot:port>` is the
  peer flag of R3 (SPEC-025's business).
- `showport -iscsi` on OS 10.6.0 has the `VLANs Peer_Enabled` layout E18U31 had on OS 10.5.0. Unset
  addresses print `0.0.0.0`.
- `showport -iscsivlans`: the layout in R2.
- WSAPI `GET /ports/<n:s:p>/iSCSIVlans/` answers on every iSCSI port, ready or offline, with
  `{"iSCSIVlans": [...], "total": N, "links": [...]}`. `GET /ports` carries `iSCSIVlans: []` on every
  port and `iSCSIPortInfo.vlan` 0 on the iSCSI ports.

**Contradicted, or different from what this spec assumed:**

- `showport -iscsivlans` is not a list of VLAN interfaces only: it lists the untagged address too
  (VLAN `untagged`). The parser leaves those rows out; a plan or verify that read them as VLANs
  would print "VLAN 0" to the network team.
- It has no State column, so `IscsiVlanInterface.state` is gone (§4) and R7 takes the state from
  `showport`.
- WSAPI's iSCSIVlans answer leaves the untagged address out (empty on 0:4:1, which has one; OS
  10.5.60 does not, below), and its envelope is `iSCSIVlans`, not `members`: the client's `_members`
  helper reads it as empty.
- The `VLANs` column of `showport -iscsi` is 1 on a port with an address and 0 without, so it is not
  a count of tagged VLANs (and not the older layout's `Y`). Display only.
- On OS 10.6.0 `controlport rcip` takes `-vlan` (§2); OS 10.5 did not (seen again on 10.5.0, 10.5.51
  and 10.5.60, below).

### What three OS 10.5 arrays added (2026-11-17)

The same script on D22U27 (OS 10.5.0, no iSCSI port), VZ (OS 10.5.51, four offline iSCSI ports) and
E18U31 (OS 10.5.60, now named DHCI_B10K, four ready iSCSI ports), files in `D22U27/`, `VZ/` and
`E18U31/` beside `rack13/`. None has a tagged interface either.

**Confirmed:**

- OS 10.5.0, 10.5.51 and 10.5.60 print one and the same `help controliscsiport`, with the `addr`,
  `gw` and `delete` forms and `-vlan` exactly as on 10.6.0. R3's and R5's lines hold on both OS lines.
  10.5 words the range "(1 to 4094)" and lacks 10.6.0's initiator range and `-skip_rescan`.
- `controlport rcip` takes no `-vlan` on any of the three; only 10.6.0's does (§2).
- `showport -iscsivlans` on 10.5.60 has the 10.6.0 layout and the untagged rows (E18U31: four, MTU
  9000). `showport -iscsi` has the `VLANs Peer_Enabled` layout on 10.5.51 and 10.5.60 too; VLANs is
  1 on a port with an address, 0 without.

**Contradicted, or new:**

- With no address on any iSCSI port, `showport -iscsivlans` answers `no ports listed`: on VZ, which
  has four offline iSCSI ports, and on D22U27, which has none. The view cannot tell the two apart;
  `showport` (R2) can. `showport -iscsi` differs: four rows on VZ, *"There is no specified port
  information."* on D22U27.
- On OS 10.5.60 WSAPI's iSCSIVlans answer **includes** the untagged address, as one record with
  `vlanTag` 0 (`total` 1), and `GET /ports` carries the same record in the port's `iSCSIVlans`.
  `parse_iscsi_vlans_wsapi` would have read it as VLAN 0; it now leaves tag 0 out and refuses a tag
  above 4094. The record's field names are now seen, not inferred: `IPAddr`, `netmask`, `gateway`,
  `vlanTag`, `mtu`, `stgt`, `tpgt`, `iSNSAddr`, `iSNSPort`.
- `GET /ports` on 10.5.0 and 10.5.51 has no `iSCSIVlans` field at all. `iSCSIPortInfo.vlan` is 0 on
  every iSCSI port of rack13-ARCUS, VZ and E18U31, even where the list has a record, so it is no sign of a tagged
  interface; what sets it to 1 (python-3parclient reads the list only then) is not seen yet.
- E18U31 changed since the plan tests' capture (`rc_pair/E18U31/`, 2026-10-07): renamed, readdressed,
  RCIP ports gone. The plan tests stay on the older capture, which is still a real array state.

**For later steps:** `help showport` says an address shown with `*` means the port has more than one
address configured with VLANs. `parse_showport_iscsi` drops the star; `parse_iscsi_ips` (discovery's
address column) keeps it, so after the tool adds a VLAN discovery would show `10.93.18.10*`. The live
confirmation (§6) captures a starred row, and `parse_iscsi_ips` is fixed on it before the apply
(`test_discovery_reads_a_starred_iscsi_address_without_its_star`, strict xfail until `tagged/`
exists).
