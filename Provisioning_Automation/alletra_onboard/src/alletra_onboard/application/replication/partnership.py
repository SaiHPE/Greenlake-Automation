"""SPEC-021: RCIP ports and the partnership, planned from the Replication network tab (read-only).
Applying the plan lives in `partnership_apply.py` (STANDARD S2).

Every command form and every answer here is the arrays' own, from the manual setup of the lab pair on
2026-11-03 (rack13-ARCUS OS 10.5.55 -> PRIMERA630R11U22 OS 4.6.20, tests/fixtures/rcip_pair/).
"""

from __future__ import annotations

import ipaddress
from typing import Literal

from alletra_onboard.application.replication.plan_check import array_name
from alletra_onboard.domain.plan_objects import RcPlanObjects
from alletra_onboard.domain.replication import (
    PlannedCall,
    RcipPortRequest,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
    ReplicationReport,
    pair_ports,
)

ArraySide = Literal["A", "B"]

#: SSH writes have no WSAPI equivalent (ADR 0015); the plan's WSAPI column says so.
SSH_ONLY = "— (no WSAPI call; over SSH)"


def _mask_matches(have: str, want: str) -> bool:
    try:
        return ipaddress.ip_network(f"0.0.0.0/{have}").prefixlen == ipaddress.ip_network(f"0.0.0.0/{want}").prefixlen
    except ValueError:
        return have == want


def _port_action(view: ReplicationArrayView, side: ArraySide, row: RcipPortRequest) -> ReplicationAction:
    label = array_name(view)
    rcip = {p.nsp: p for p in view.rcip_ports}
    have = rcip.get(row.nsp)
    action = ReplicationAction(kind="rcip_port", name=row.nsp, where=side,
                               detail={"ip": row.ip, "netmask": row.netmask, "gateway": row.gateway})
    if have is not None and have.ip:
        if have.ip == row.ip and _mask_matches(have.netmask, row.netmask):
            action.state, action.reason = "exists", f"{row.ip} {have.netmask} already set"
        else:
            action.state = "conflict"
            action.reason = (f"{label} {row.nsp} already has RCIP address {have.ip} {have.netmask}; the sheet says "
                             f"{row.ip} {row.netmask}. The tool never changes an address it did not set.")
        return action
    other = next((p.nsp for p in view.rcip_ports if p.ip == row.ip and p.nsp != row.nsp), None)
    if other:
        action.state = "conflict"
        action.reason = f"{row.ip} is already the RCIP address of {label} {other}."
        return action
    role = view.ports.get(row.nsp)
    if role is None:
        action.state, action.reason = "conflict", f"{label} has no port {row.nsp} (showport)."
        return action
    if not role.rcip_capable:
        action.state = "conflict"
        action.reason = (f"{label} {row.nsp} is not a free replication port: showport lists it as {role.mode} {role.state} "
                         f"{role.type} {role.protocol}. The tool never changes a port's role.")
        return action
    calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"controlport rcip addr -f {row.ip} {row.netmask} {row.nsp}")]
    if row.gateway:
        calls.append(PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"controlport rcip gw -f {row.gateway} {row.nsp}"))
    action.calls = calls
    action.reason = (f"RCIP address {row.ip} {row.netmask}" + (f", gateway {row.gateway}" if row.gateway else "")
                     + f" on {row.nsp} ({role.state})")
    return action


def _service_action(view: ReplicationArrayView, side: ArraySide) -> ReplicationAction:
    action = ReplicationAction(kind="rc_service", name="Remote Copy", where=side,
                               detail={"was_configured": bool(view.rc_status)})
    if view.rc_started:
        action.state, action.reason = "exists", "started"
        return action
    action.calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli="startrcopy")]
    action.reason = ("not configured on " if not view.rc_status else f"{view.rc_status.lower()} on ") + array_name(view)
    return action


def _target_action(view: ReplicationArrayView, side: ArraySide, name: str, links: list[str]) -> ReplicationAction:
    """links: `<local n:s:p>:<peer address>`. Exists when a target already carries exactly those links."""
    label = array_name(view)
    action = ReplicationAction(kind="target", name=name, where=side, detail={"links": links})
    wanted = {tuple(link.rsplit(":", 1)) for link in links}
    by_target: dict[str, set[tuple[str, str]]] = {}
    for link in view.links:
        if not link.inbound:
            by_target.setdefault(link.target, set()).add((link.nsp, link.address))
    same = next((t for t, have in by_target.items() if have == wanted), None)
    if same:
        action.state, action.reason = "exists", f"target '{same}' already has these links"
        action.detail["existing"] = same
        return action
    taken = sorted(f"{nsp}:{addr} (on '{t}')" for t, have in by_target.items() for nsp, addr in have & wanted)
    if taken:
        action.state = "conflict"
        action.reason = (f"{label} already has link(s) {', '.join(taken)}; a link belongs to one target. Remove it "
                         "on the array, or name other ports on the Replication network tab.")
        return action
    if any(t.name == name for t in view.targets):
        action.state = "conflict"
        action.reason = f"{label} already has a target named '{name}' with other links."
        return action
    action.calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"creatercopytarget {name} IP {' '.join(links)}")]
    action.reason = f"target '{name}' with {len(links)} link(s): {', '.join(links)}"
    return action


def stale_fc_targets(primary: ReplicationArrayView, peer: ReplicationArrayView) -> list[str]:
    """SPEC-021 R3: an FC target on one array that carries the other array's FC node WWN. Live
    2026-11-03: with the Primera's failed FC target to rack13-ARCUS in place, its new IP target never
    learned the Alletra's identity (`showrcopy -d targets`: SysName None) and every group create on the
    Alletra failed with "Failed to send message to target"."""
    out = []
    for here, there in ((primary, peer), (peer, primary)):
        # Every node WWN `there` shows, not only its first FC row's: a peer port has one of its own (LESSONS 41).
        wwns = there.fc_node_wwns
        if not wwns:
            continue
        for t in here.targets:
            if t.type.upper() != "FC" or t.options.upper() not in wwns:
                continue
            # BL-57: the removal command is printed only for a dead target. On a working FC pair it would
            # delete the target and every group on it, and replication would stop.
            links_up = [ln for ln in here.links if ln.target == t.name and ln.status.lower() == "up"]
            started = [g.name for g in here.groups if g.target == t.name and g.status.lower() == "started"]
            if t.status.lower() == "failed" and not links_up and not started:
                out.append(
                    f"{array_name(here)} already has target '{t.name}' for {array_name(there)} over Fibre Channel (status "
                    f"{t.status}). The arrays keep one partnership per pair, so an IP target beside it does not "
                    f"work. Remove it on {array_name(here)} first: `removercopytarget -cleargroups -f {t.name}` (this also "
                    "removes the groups on that target; their volumes stay). Save `showrcopy -d groups` before."
                )
                continue
            alive = [f"status {t.status or 'unknown'}"]
            if links_up:
                alive.append(f"{len(links_up)} link{'s' if len(links_up) != 1 else ''} up")
            if started:
                alive.append(f"started group{'s' if len(started) != 1 else ''} {', '.join(started)}")
            out.append(
                f"{array_name(here)} already replicates to {array_name(there)} over Fibre Channel (target '{t.name}': "
                f"{'; '.join(alive)}). The arrays keep one partnership per pair, so the tool will not set up an IP "
                "target beside it, and it will not remove a target that is in use. Leave the Replication network "
                "tab empty to keep the Fibre Channel partnership; moving it to IP is a planned change outside this tool."
            )
    return out


def plan_partnership(report: ReplicationReport, intent: ReplicationIntent) -> tuple[list[ReplicationAction], list[str], list[str]]:
    """(actions in apply order, blockers, notes) for SPEC-021 R3. Empty when the sheet has no network."""
    if not intent.network:
        return [], [], []
    a, b = report.primary, report.peer
    blockers: list[str] = list(stale_fc_targets(a, b))
    notes: list[str] = []
    pairs = pair_ports(intent.network)
    if len(pairs) < 2:
        missing = ("The Replication network tab needs at least 2 pairs of ports, one per node: the groups need at "
                   "least 2 links Up each way.")
        return [], [*blockers, missing], notes
    actions: list[ReplicationAction] = []
    sides: tuple[tuple[ArraySide, ReplicationArrayView], ...] = (("A", a), ("B", b))
    for side, view in sides:
        for row in (r for r in intent.network if r.side == side):
            actions.append(_port_action(view, side, row))
    actions += [_service_action(a, "A"), _service_action(b, "B")]
    actions.append(_target_action(a, "A", array_name(b), [f"{pa.nsp}:{pb.ip}" for pa, pb in pairs]))
    actions.append(_target_action(b, "B", array_name(a), [f"{pb.nsp}:{pa.ip}" for pa, pb in pairs]))
    for pa, pb in pairs:
        for row, other in ((pa, pb), (pb, pa)):
            if row.gateway and _same_net(row, other.ip):
                notes.append(f"{row.nsp} on {'this array' if row.side == 'A' else 'the peer'} gets gateway {row.gateway}, "
                             f"although {other.ip} is on its own network. The link check sends its test through that "
                             "gateway; leave Gateway blank when both arrays are on one network.")
    blockers += [x.reason for x in actions if x.state == "conflict"]
    return actions, blockers, notes


def _same_net(row: RcipPortRequest, address: str) -> bool:
    try:
        return ipaddress.ip_address(address) in ipaddress.ip_network(f"{row.ip}/{row.netmask}", strict=False)
    except ValueError:
        return False


# ------------------------------------------------------------------ R4 apply, R5 removal set

def plan_objects(plan: ReplicationPlan, side: ArraySide) -> RcPlanObjects:
    """ADR 0025 condition 3: the ports, addresses and target the approved plan names on one array. That
    array's write client is built with them and refuses a command on anything else. A conflict row is
    one the plan will not touch, so it adds nothing."""
    ports: set[str] = set()
    addresses: set[str] = set()
    peers: set[str] = set()
    targets: set[str] = set()
    for x in plan.actions:
        if x.where != side or x.state == "conflict":
            continue
        if x.kind == "rcip_port":
            ports.add(x.name)
            addresses.update(a for a in (x.detail.get("ip"), x.detail.get("gateway")) if a)
        elif x.kind == "target":
            targets.add(x.name)
            for link in x.detail.get("links", []):
                nsp, peer = link.rsplit(":", 1)
                ports.add(nsp)
                peers.add(peer)
    return RcPlanObjects(ports=frozenset(ports), addresses=frozenset(addresses), peer_addresses=frozenset(peers),
                         targets=frozenset(targets))
