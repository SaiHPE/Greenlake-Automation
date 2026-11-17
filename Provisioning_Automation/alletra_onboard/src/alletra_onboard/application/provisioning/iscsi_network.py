"""SPEC-024: VLAN-tagged iSCSI addresses on the array's iSCSI ports, planned from the iSCSI network tab.

The first slice of ADR 0017: the plan and the CLI lines it prints, for the engineer to read; nothing
here writes. The lines are the array's own forms (`help controliscsiport`, the same on OS 10.5.0,
10.5.51, 10.5.60 and 10.6.0, tests/fixtures/iscsi_vlan/), and every one carries `-vlan` with a tag of
1 to 4094: without it `addr` changes and `delete` removes the port's untagged address, the one the
hosts already logged in use. The switch side is a sentence for the network team; the tool never
writes a switch (ADR 0012).

The address goes in without its gateway (ADR 0017, amended 2026-11-17, the owner's decision after the
live check): the array sets a VLAN gateway only while the port is offline, and offline stops every
iSCSI session on the port. A gateway the sheet gives is printed in a separate set for a change window
agreed with the customer, with the sessions the port carries now; the tool never sends it.
"""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.provisioning.discovery import (
    parse_file_ports,
    parse_iscsi_untagged_ports,
    parse_iscsi_vlans,
    parse_showhost,
    parse_showport_iscsi,
)
from alletra_onboard.application.provisioning.peer_ports import OFFLINE_ASKS
from alletra_onboard.application.replication.read import (
    parse_showport_rcip,
    parse_showport_roles,
    parse_showsys,
)
from alletra_onboard.domain.network import (
    IscsiNetworkPlan,
    IscsiPortAddress,
    IscsiVlanAction,
    IscsiVlanCheck,
    IscsiVlanInterface,
    IscsiVlanOutcome,
    IscsiVlanRequest,
    PortNetworkView,
)
from alletra_onboard.domain.shared import EndpointCreds

# shownet's data row: the only line that starts with two IPv4s (the management address, then its mask).
_SHOWNET_ROW = re.compile(r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b")


def _nsp_key(nsp: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in nsp.split(":"))
    except ValueError:
        return (999,)


def _prefix_len(mask: str) -> int | None:
    try:
        return ipaddress.ip_network(f"0.0.0.0/{mask}").prefixlen
    except ValueError:
        return None


def _mask_matches(have: str, want: str) -> bool:
    """Same prefix length, whether the array prints a dotted mask or a prefix length."""
    a, b = _prefix_len(have), _prefix_len(want)
    return a == b if a is not None and b is not None else have == want


def _network(ip: str, mask: str) -> ipaddress.IPv4Network | None:
    try:
        net = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
    except ValueError:
        return None
    return net if isinstance(net, ipaddress.IPv4Network) else None


def addr_line(req: IscsiVlanRequest) -> str:
    return f"controliscsiport addr {req.ip} {req.netmask} -vlan {req.vlan_id} -f {req.nsp}"


def gw_line(req: IscsiVlanRequest) -> str:
    return f"controliscsiport gw {req.gateway} -vlan {req.vlan_id} -f {req.nsp}"


def offline_line(nsp: str) -> str:
    """`controlport offline <node:slot:port>...`: no -f in any captured help; it asks y, n or q every time."""
    return f"controlport offline {nsp}"


def rst_line(nsp: str) -> str:
    """`controlport rst [-m <mode>|-l|-i] [-f] <node:slot:port>...`: brings a held-offline port back."""
    return f"controlport rst -f {nsp}"


def delete_line(nsp: str, vlan_id: int) -> str:
    """R5. Never without `-vlan`: `controliscsiport delete -f <port>` deletes the port's whole iSCSI
    configuration, untagged address included (the help's own example)."""
    return f"controliscsiport delete -vlan {vlan_id} -f {nsp}"


def differences(have: IscsiVlanInterface, req: IscsiVlanRequest) -> list[str]:
    """How an interface on the array differs from a sheet row with the same port and VLAN, one
    "field: array value, sheet value" entry each. The gateway counts only when the row and the array
    both have one: the tool adds the address without it (ADR 0017, amended 2026-11-17), so an array
    without the sheet's gateway is what the tool's own lines leave. The plan's *exists* and Verify's
    *present* are both "no difference" (LESSONS 41)."""
    out = []
    if have.ip != req.ip:
        out.append(f"address: {have.ip} on the array, {req.ip} on the sheet")
    if not _mask_matches(have.netmask, req.netmask):
        out.append(f"netmask: {have.netmask} on the array, {req.netmask} on the sheet")
    if req.gateway and have.gateway and have.gateway != req.gateway:
        out.append(f"gateway: {have.gateway or 'none'} on the array, {req.gateway} on the sheet")
    return out


def _in_use(req: IscsiVlanRequest, view: PortNetworkView) -> str:
    """Where the array already uses the request's address, or ""."""
    if req.ip == view.mgmt_ip:
        return "management"
    for port in view.iscsi_ports:
        if port.ip == req.ip:
            return f"iSCSI port {port.nsp}"
    for vlan in view.vlans:
        if vlan.ip == req.ip and (vlan.nsp, vlan.vlan_id) != (req.nsp, req.vlan_id):
            return f"iSCSI port {vlan.nsp} VLAN {vlan.vlan_id}"
    return view.other_addresses.get(req.ip, "")


def _action(req: IscsiVlanRequest, view: PortNetworkView) -> IscsiVlanAction:
    array = view.name
    action = IscsiVlanAction(nsp=req.nsp, vlan_id=req.vlan_id, state="conflict")
    role = view.roles.get(req.nsp)
    if role is None:
        action.reason = f"{array} has no port {req.nsp} (showport)."
        return action
    if not (role.protocol == "iSCSI" and role.type in ("host", "free")):
        action.reason = (f"{array} {req.nsp} is not an iSCSI port: showport lists it as {role.mode} {role.state} "
                         f"{role.type} {role.protocol}. The tool never changes a port's role.")
        return action
    base = next((p for p in view.iscsi_ports if p.nsp == req.nsp), None)
    if base is not None and base.peer_enabled:
        action.reason = (f"{array} {req.nsp} is a peer-enabled iSCSI port (showport -iscsi: Peer_Enabled Y). "
                         "The tool does not add VLANs to it.")
        return action
    have = next((v for v in view.vlans if v.nsp == req.nsp and v.vlan_id == req.vlan_id), None)
    if have is not None:
        if not differences(have, req):
            action.state, action.reason = "exists", f"{req.ip} {have.netmask} already set"
            if req.gateway and not have.gateway:
                action.gateway_cli = gw_line(req)
                action.reason += f"; gateway {req.gateway} not set yet (a change window's job)"
            return action
        action.reason = (f"{array} {req.nsp} already has VLAN {req.vlan_id} with {have.ip} {have.netmask} "
                         f"(gateway {have.gateway or 'none'}); the sheet says {req.ip} {req.netmask} "
                         f"(gateway {req.gateway or 'none'}). The tool never changes an address it did not set.")
        return action
    where = _in_use(req, view)
    if where:
        action.reason = f"{req.ip} is already in use on {array}: {where}."
        return action
    net = _network(req.ip, req.netmask)
    taken = [(f"iSCSI port {req.nsp}", base.ip, base.netmask)] if base is not None and base.ip else []
    if view.mgmt_ip:
        taken.append(("management", view.mgmt_ip, view.mgmt_netmask))
    for label, ip, mask in taken:
        if net is not None and net == _network(ip, mask):
            action.reason = f"{net} is already the network of {label} on {array}; a VLAN needs a network of its own."
            return action
    action.state, action.cli, action.undo = "create", addr_line(req), delete_line(req.nsp, req.vlan_id)
    action.reason = f"{req.ip} {req.netmask} on VLAN {req.vlan_id} ({role.state})"
    if req.gateway:
        action.gateway_cli = gw_line(req)
        action.reason += f"; gateway {req.gateway} not set by the tool (a change window's job)"
    return action


GATEWAY_WINDOW = ("The tool does not set these gateways. The array sets a VLAN gateway only while the port is "
                  "offline, and taking a port offline stops every iSCSI session on it. Hosts on the VLAN's own "
                  "subnet need no gateway. Run these lines only in a change window agreed with the customer.")


def sessions_sentence(nsp: str, count: int | None) -> str:
    """How many iSCSI sessions the change-window lines would stop on one port, from `showhost -d`."""
    if count is None:
        return f"{nsp}: its iSCSI sessions were not read. Check `showhost -d` before the change window."
    if count == 0:
        return f"{nsp} has no iSCSI session now (showhost -d). Check again just before the change window."
    return (f"{nsp} carries {count} iSCSI session{'s' if count != 1 else ''} now (showhost -d): "
            f"{'all of them stop' if count != 1 else 'it stops'} while the port is offline.")


def gateway_window(actions: list[IscsiVlanAction]) -> list[str]:
    """The change-window set: per port in port order, `controlport offline`, the port's gw lines, then
    `controlport rst -f`, the forms of `help controlport` and `help controliscsiport` (OS 10.5.0 to
    10.6.0). The array asked for exactly this (*To modify the Gateway IP, please use controlport to
    offline the port first*, rack13-ARCUS, 2026-11-17). Never sent by the tool."""
    by_port: dict[str, list[str]] = {}
    for action in actions:
        if action.gateway_cli:
            by_port.setdefault(action.nsp, []).append(action.gateway_cli)
    lines: list[str] = []
    for nsp in sorted(by_port, key=_nsp_key):
        lines += [offline_line(nsp), *by_port[nsp], rst_line(nsp)]
    return lines


def switch_sentence(array: str, nsp: str, vlan_ids: list[int]) -> str:
    """R3: what the network team sets on the switch port. The native VLAN stays: the hosts already
    logged in use the port's untagged address, and a trunk with no native VLAN would drop them."""
    tags = ", ".join(str(v) for v in sorted(set(vlan_ids)))
    return (f"Switch port cabled to {array} {nsp}: carry VLAN {tags} tagged (802.1Q); "
            "keep the untagged (native) VLAN as it is.")


def plan_iscsi_vlans(requests: list[IscsiVlanRequest], view: PortNetworkView) -> IscsiNetworkPlan:
    """R3: one action per sheet row, in sheet order; the first rule that applies decides. Pure."""
    actions = [_action(req, view) for req in requests]
    plan = IscsiNetworkPlan(array=view.name, actions=actions)
    plan.blockers = [a.reason for a in actions if a.state == "conflict"]

    nodes: dict[int, set[str]] = {}
    for req in requests:
        nodes.setdefault(req.vlan_id, set()).add(req.nsp.split(":", 1)[0])
    for vlan_id, on in nodes.items():
        if len(on) == 1:
            (node,) = on
            plan.notes.append(f"VLAN {vlan_id} is only on node {node}. If that node stops, hosts on VLAN {vlan_id} "
                              "lose every path.")
    for action in actions:
        role = view.roles.get(action.nsp)
        if action.state == "create" and role is not None and role.state != "ready":
            note = f"{action.nsp} is {role.state}: the address is set, but no host reaches it until the link is up."
            if note not in plan.notes:
                plan.notes.append(note)
    for action, req in zip(actions, requests, strict=True):
        if action.gateway_cli:
            plan.notes.append(f"{action.nsp} VLAN {action.vlan_id}: the tool adds the address without the gateway "
                              f"{req.gateway}. The gateway needs the port offline, so it is in a separate set for a "
                              "change window.")
    plan.removal_lines = [a.undo for a in reversed(actions) if a.state == "create"]
    plan.gateway_window = gateway_window(actions)
    if plan.gateway_window:
        ports = sorted({a.nsp for a in actions if a.gateway_cli}, key=_nsp_key)
        plan.gateway_notes = [GATEWAY_WINDOW] + [sessions_sentence(nsp, view.sessions.get(nsp)) for nsp in ports]

    # R3: a line per sheet port with a planned or existing VLAN. A conflict row keeps its port's line when
    # the array already has a VLAN there (live 2026-11-17: VLAN 2999 on 0:4:2 with another gateway).
    wanted: dict[str, list[int]] = {}
    for action in actions:
        tags = wanted.setdefault(action.nsp, [])
        if action.state in ("create", "exists"):
            tags.append(action.vlan_id)
    for nsp in sorted(wanted, key=_nsp_key):
        tags = wanted[nsp] + [v.vlan_id for v in view.vlans if v.nsp == nsp]
        if tags:
            plan.switch_handoff.append(switch_sentence(view.name, nsp, tags))
    return plan


REMOVAL_HEADER = "Removing an interface ends every iSCSI session on it. Check `showhost -d` first."


def command_set_text(plan: IscsiNetworkPlan) -> str:
    """The lines a consultant pastes now, as one text for Copy and Download: no gateway, no offline."""
    lines = [(f"# iSCSI VLAN addresses on {plan.array}: paste on the array's CLI, then read the array again in "
              "the tool. No gateway and no port offline: the hosts logged in keep their sessions.")]
    lines += [a.cli for a in plan.actions if a.state == "create"]
    return "\n".join(lines) + "\n"


def removal_set_text(plan: IscsiNetworkPlan) -> str:
    """R5 before the paste: each create's removal line, last first, with the R5 header. Never run by the tool."""
    head = [f"# Undo the iSCSI VLAN addresses this plan adds on {plan.array}. {REMOVAL_HEADER}",
            "# Review before pasting. The tool never runs these."]
    return "\n".join(head + plan.removal_lines) + "\n"


def gateway_set_text(plan: IscsiNetworkPlan) -> str:
    """The change-window set, its own text: why, the sessions per port, the offline prompt. "" when none."""
    if not plan.gateway_window:
        return ""
    head = [(f"# CHANGE WINDOW ONLY: the VLAN gateways on {plan.array}. This stops every iSCSI session on each "
             "port below while it is offline.")]
    head += [f"# {n}" for n in plan.gateway_notes] + [f"# {OFFLINE_ASKS}"]
    return "\n".join(head + plan.gateway_window) + "\n"


def removal_lines(outcomes: list[IscsiVlanOutcome]) -> list[str]:
    """R5: one line per interface the apply sent (created, or failed after the send: ADR 0025 wrote
    its line before the send), last sent first. An interface that existed never has one."""
    return [delete_line(o.nsp, o.vlan_id) for o in reversed(outcomes) if o.status in ("created", "failed")]


def verify_iscsi_vlans(requests: list[IscsiVlanRequest], vlans: list[IscsiVlanInterface]) -> list[IscsiVlanCheck]:
    """R6: each sheet row against `showport -iscsivlans`: present, missing or different. Read-only."""
    checks = []
    for req in requests:
        have = next((v for v in vlans if v.nsp == req.nsp and v.vlan_id == req.vlan_id), None)
        if have is None:
            checks.append(IscsiVlanCheck(nsp=req.nsp, vlan_id=req.vlan_id, status="missing"))
            continue
        diff = differences(have, req)
        note = (f"The gateway {req.gateway} is not set: the tool leaves it to a change window (it needs the port "
                "offline)." if not diff and req.gateway and not have.gateway else "")
        checks.append(IscsiVlanCheck(nsp=req.nsp, vlan_id=req.vlan_id, status="different" if diff else "present",
                                     differences=diff, note=note))
    return checks


def switch_handoff_for(array: str, vlans: list[IscsiVlanInterface]) -> list[str]:
    """R3's sentences for every port that carries a VLAN interface on the array, in port order (the
    as-built documents what is there, whoever set it up)."""
    by_port: dict[str, list[int]] = {}
    for vlan in vlans:
        by_port.setdefault(vlan.nsp, []).append(vlan.vlan_id)
    return [switch_sentence(array, nsp, by_port[nsp]) for nsp in sorted(by_port, key=_nsp_key)]


# ------------------------------------------------------------------ R2: the read

def parse_shownet_mgmt(text: str) -> tuple[str, str]:
    """`shownet` -> (management address, netmask) from its first data row; ("", "") when none."""
    for line in (text or "").splitlines():
        m = _SHOWNET_ROW.match(line)
        if m:
            return m.group(1), m.group(2)
    return "", ""


def _read(cli, command: str) -> str:
    """A read the plan stands on. The CLI answers a refusal in text (`Error: ...`); reading that as
    "nothing configured" would plan an add over an interface the array has, so it fails the read."""
    text = cli.run(command)
    if text.lstrip().lower().startswith("error"):
        raise ValueError(f"`{command}` answered: {text.strip().splitlines()[0]}")
    return text


def untagged_addresses(
    ports: list[IscsiPortAddress], untagged: set[str], vlans: list[IscsiVlanInterface],
) -> list[IscsiPortAddress]:
    """Each port's base address only when it is untagged. A port with no `untagged` row in `showport
    -iscsivlans` whose base columns hold one of its own VLAN addresses has no untagged address: read as
    one, a second VLAN in that network would be refused as the port's own (live 2026-11-17)."""
    out = []
    for port in ports:
        if port.ip and port.nsp not in untagged and port.ip in {v.ip for v in vlans if v.nsp == port.nsp}:
            port = port.model_copy(update={"ip": "", "netmask": "", "gateway": ""})
        out.append(port)
    return out


def sessions_by_port(showhost_d: str) -> dict[str, int]:
    """`showhost -d` -> {n:s:p: iSCSI initiators logged in}, claimed or not (`-- --`)."""
    out: dict[str, int] = {}
    for host in parse_showhost(showhost_d):
        for ports in host.iqns.values():
            for port in ports:
                out[port] = out.get(port, 0) + 1
    return out


def read_port_network(creds: EndpointCreds, *, array_cli_factory: Callable = make_array_cli) -> PortNetworkView:
    """R2: one SSH session over the read-only client (ADR 0001), every read already allowed. A failed
    login or read raises: the plan is not built on half a read."""
    with array_cli_factory(creds) as cli:
        sysinfo = parse_showsys(_read(cli, "showsys"))
        roles, _node_wwn = parse_showport_roles(_read(cli, "showport"))
        iscsi_ports = parse_showport_iscsi(_read(cli, "showport -iscsi"))
        vlans_text = _read(cli, "showport -iscsivlans")
        vlans = parse_iscsi_vlans(vlans_text)
        iscsi_ports = untagged_addresses(iscsi_ports, parse_iscsi_untagged_ports(vlans_text), vlans)
        rcip = parse_showport_rcip(_read(cli, "showport -rcip"))
        files = parse_file_ports(_read(cli, "showport -file"))
        mgmt_ip, mgmt_netmask = parse_shownet_mgmt(_read(cli, "shownet"))
        sessions = sessions_by_port(_read(cli, "showhost -d"))
    other: dict[str, str] = {}
    for port in rcip:
        if port.ip:
            other.setdefault(port.ip, f"RCIP port {port.nsp}")
    for port in files:
        if port.address:
            other.setdefault(port.address, f"file port {port.node}:{port.slot}:{port.card_port}")
    return PortNetworkView(
        name=sysinfo.get("name", "") or creds.host, mgmt_ip=mgmt_ip, mgmt_netmask=mgmt_netmask,
        roles=roles, iscsi_ports=iscsi_ports, vlans=vlans, other_addresses=other,
        sessions={nsp: sessions.get(nsp, 0) for nsp in (p.nsp for p in iscsi_ports)},
    )


def read_iscsi_vlans(creds: EndpointCreds, *, array_cli_factory: Callable = make_array_cli) -> list[IscsiVlanInterface]:
    """R6: Verify's one read, `showport -iscsivlans`, over the read-only client."""
    with array_cli_factory(creds) as cli:
        return parse_iscsi_vlans(_read(cli, "showport -iscsivlans"))
