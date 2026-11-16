# SPEC-024 — VLAN-tagged iSCSI addresses on the array's ports, set up by the tool

**Status:** PROPOSED 2026-11-16, not built · **Decision:** [ADR 0017](../adr/0017-iscsi-vlan-write-plane.md)
(PROPOSED: which write plane) · **Tracker:** BL-25 (issue #11) · **Work packet:**
[workpackets/BL-25.md](../workpackets/BL-25.md) · **Tests:** `tests/unit/test_iscsi_vlans.py` (strict
xfail until built) · **Sibling:** SPEC-025 (BL-26, peer ports), written in parallel; see §8

## 1. Problem, and what the tool reads today

SCOPE area 3 lists "VLAN configuration"; the tracker calls it *read-only today*. What that means in
the code on 2026-11-16 (main `b7006373`):

| What | Where it is read | Where it shows |
|---|---|---|
| File service ports: the `VLAN` column of `showport -file` (`untagged` or a tag) | `parse_file_ports` → `EthernetPort.vlan` (`application/provisioning/discovery.py`) | Discovery page, *file service ports* table, column VLAN |
| iSCSI ports: `showport -iscsi`, address only | `parse_iscsi_ips` → `ArrayPort.address` | Discovery page, *array iSCSI ports* table. The `VLAN`/`VLANs` and `Peer_Enabled` columns are read past and dropped |
| iSCSI VLAN interfaces: `showport -iscsivlans` | lab capture scripts only (`lab/iscsi_port_probe.py`, `lab/rcip_pair_capture.py`); no parser, no fixture in the repo | nowhere |
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
RCIP ports (the help captured on both lab arrays, OS 10.5, lists no `-vlan` on `controlport rcip`;
the ED8 CLI guide documents one for a later OS, research 2026-10-07 §2); VLANs on file ports (BL-28)
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

| Rule | Sentence after the prefix |
|---|---|
| a required cell is blank | `missing <labels>.` |
| port shape | `Port must be N:S:P, like 0:4:1 (got '<text>').` |
| VLAN ID | `VLAN ID must be a whole number from 1 to 4094 (got '<text>').` (the range is the array's own help: `-vlan` *"Specifies the VLAN tag number (1 to 4094)"*, `tests/fixtures/rc_pair/help/help_controlport.txt`) |
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
`showport`, `shownet`, `showhost`); **no read allowlist change**. The `showport -iscsivlans` layout
is **unconfirmed: capture on the lab** (`lab/iscsi_vlan_capture.py`). WSAPI offers the same read
(`GET /ports/<n:s:p>/iSCSIVlans/`, confirmed by python-3parclient 4.5 `_getIscsiVlan`); it is used
for the read-back only if ADR 0017 picks WSAPI writes.

**R3 — The plan.** One action per sheet row, in sheet order, with the plan state words of SPEC-001:

- **exists**: the port already has that VLAN with the same address and prefix length (and the same
  gateway when the row names one). No call.
- **create**: the port is an iSCSI port, has no interface on that VLAN, and nothing below applies.
  The action carries the write (ADR 0017) and its CLI equivalent, printed as in SPEC-016.
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

**The switch side, as a sentence.** The plan ends with one line per port that has a planned or
existing VLAN, for the network team: *"Switch port cabled to `<array>` 0:4:1: carry VLAN 120, 130
tagged (802.1Q)."* No command: the tool reads no Ethernet switch, does not know its vendor, and
never writes one (ADR 0012). The page, the removal set header and the as-built carry the same lines.

**R4 — Apply.** Only from a plan the operator approved with a tick, and only while that plan stands:
a new read, a sheet change or a restart withdraws it (LESSONS 6). The apply first reads again (R2)
and refuses if any action's judgement would now differ (LESSONS 37). Then one write per *create*
action, in sheet order, stopping at the first refusal. After each write, read `showport -iscsivlans`
and check the interface is there with the planned values; a write the array accepted but the read
does not show is a failure. Every write and every read goes through `command_log.record` with the
client's secrets.

**R5 — The removal set.** Exactly the interfaces this apply created, as CLI lines the operator
pastes (SPEC-007), last created first, one line each. The delete form is the array's own, taken from
`help controliscsiport` (**unconfirmed: capture on the lab**). Header: *"Removing an interface ends
every iSCSI session on it. Check `showhost -d` first."* Interfaces that existed are never in it.

**R6 — Verify.** The *Verify configuration* step compares each sheet row with `showport -iscsivlans`:
*present*, *missing* or *different (field: array value, sheet value)*. Read-only.

**R7 — The as-built.** A section *iSCSI network* when the array has any VLAN interface or the sheet
has the tab: every VLAN interface on every iSCSI port (port, VLAN, address/prefix, gateway, MTU,
state), each marked *set up by this run* or *already there*, then the switch sentences of R3, then
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
   (exists / add / conflict), Why, and in a folded `Section` the write and its CLI equivalent.
4. *For the network team*: the switch sentences, with *Copy*.
5. Tick *"I have checked this plan. Add these iSCSI addresses to `<array>`."* and the button *Add the
   iSCSI addresses*, disabled while there is a conflict or no tick.
6. Result, the removal set (*Copy*, *Download .txt*), and *Read the array again*.

A mockup goes in `frontend/mockups` for review before the page is built.

## 4. Data contract

```python
# domain/network.py (no I/O)
class IscsiVlanRequest(BaseModel):        # one sheet row (R1)
    nsp: str; vlan_id: int; ip: str; netmask: str; gateway: str = ""
class IscsiPortAddress(BaseModel):        # one row of `showport -iscsi`
    nsp: str; ip: str = ""; netmask: str = ""; gateway: str = ""; peer_enabled: bool = False
class IscsiVlanInterface(BaseModel):      # one row of `showport -iscsivlans` (layout to capture)
    nsp: str; vlan_id: int; ip: str; netmask: str; gateway: str = ""; mtu: str = ""; state: str = ""
class PortNetworkView(BaseModel):         # what R2 read, one array
    name: str = ""; mgmt_ip: str = ""; mgmt_netmask: str = ""
    roles: dict[str, PortRole]            # PortRole from domain/replication.py (SPEC-021), shared
    iscsi_ports: list[IscsiPortAddress]; vlans: list[IscsiVlanInterface]
    other_addresses: dict[str, str]       # address -> "RCIP port 0:4:3" / "file port 0:4:1"
class IscsiVlanAction(BaseModel):
    nsp: str; vlan_id: int; state: Literal["create", "exists", "conflict"]
    reason: str = ""; wsapi: str = ""; cli: str = ""
class IscsiNetworkPlan(BaseModel):
    array: str = ""; actions: list[IscsiVlanAction]; blockers: list[str]; notes: list[str]
    switch_handoff: list[str]
class IscsiVlanOutcome(BaseModel):
    nsp: str; vlan_id: int; status: Literal["created", "exists", "failed"]; detail: str = ""

ProvisioningIntent.iscsi_network: list[IscsiVlanRequest] = []          # domain/provisioning.py

# application/platform/init_sheet.py
ISCSI_NETWORK_SHEET_NAME = "iSCSI network"; ISCSI_NETWORK_COLUMNS = [...]
# application/provisioning/discovery.py
def parse_showport_iscsi(text: str) -> list[IscsiPortAddress]
def parse_iscsi_vlans(text: str) -> list[IscsiVlanInterface]
# application/provisioning/iscsi_network.py
def plan_iscsi_vlans(requests: list[IscsiVlanRequest], view: PortNetworkView) -> IscsiNetworkPlan
def removal_lines(outcomes: list[IscsiVlanOutcome]) -> list[str]
```

## 5. Acceptance (`tests/unit/test_iscsi_vlans.py`)

Sheet: the tab parses into `iscsi_network`; every R1 sentence; the template has the tab with the
port column as text; a workbook without it parses as today. Parsers: `showport -iscsi` from the
E18U31 capture (both layouts: `VLAN` and `VLANs Peer_Enabled`); `showport -iscsivlans` from the
capture still owed. Plan (on E18U31's real `showport`, `showport -iscsi`, `showport -rcip` and
`shownet`): add on an iSCSI port; conflict on FC, RCIP, free IP, a missing port, a peer-enabled
port; exists; other values; address in use (iSCSI, RCIP, management); network taken; one-node note;
switch sentences. Removal: only what was created, last first. Step registry: `ports` sits between
`discover` and `zoning`. Adapter: the accepted write body pinned once from a live probe (LESSONS 28).

## 6. Live run (what "done" needs, rule 7)

On a lab array with iSCSI ports cabled to a switch that carries a test VLAN (to be agreed with the lab):
1. `lab/iscsi_vlan_capture.py` run and its files committed under `tests/fixtures/iscsi_vlan/`.
2. A run with two rows, one port per node, on the VLAN the lab gives. Interfaces have no name to
   prefix with `zz_`, so the lab script checks first that the port has no interface on that VLAN,
   journals what it adds, and removes it at the end even after a failure.
3. Plan shows 2 *add*; a third row on an FC port shows the conflict sentence; apply adds both;
   `showport -iscsivlans` shows them; the plan read again shows 2 *exists*.
4. A lab host on that VLAN logs in; the SAN Zoning check shows the login; an export to it passes.
5. Verify configuration reports both *present*; the as-built has the section.
6. The removal set, pasted as rendered, removes both; `showport -iscsivlans` is back to the start.

## 7. Open questions for the owner

1. ADR 0017: the write plane (WSAPI, DSCC, or a new SSH form). The build of R4 waits on it.
2. `showport -iscsivlans` and `help controliscsiport` on Alletra MP OS 10.5: layout, create and
   delete syntax, and whether VLANs can be added while the port carries sessions. Capture first.
3. Does the array refuse two VLANs on one port in the same network, or a VLAN in the port's own
   untagged network? R1 and R3 refuse both by the tool's rule until the array says.
4. The lab: which array has iSCSI ports on a switch that can carry a test VLAN (E18U31's 0:4:1 to
   1:4:2 were live on 10.30.14.0/24 on 2026-10-05).
5. Peer-enabled iSCSI ports: refuse (as proposed), or allow? Decide together with SPEC-025.
6. The new step `ports`: agree it with SPEC-025 so both sit in one step (§8).

## 8. Fit with SPEC-025 (BL-26, peer ports)

Both specs configure array ports from the sheet before zoning. Proposed to share: the *Array ports*
step (R8) with one section per tab; `PortRole` from `parse_showport_roles` as the one source of a
port's role; the conflict wording *"The tool never changes a port's role"* where a row names a port of
another kind; rows keyed by the N:S:P as text; one removal block per run. Whichever spec merges
second adapts to the first.
