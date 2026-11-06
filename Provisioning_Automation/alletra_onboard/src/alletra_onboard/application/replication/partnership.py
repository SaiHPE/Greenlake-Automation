"""SPEC-021: RCIP ports and the partnership, planned from the Replication network tab and applied
over the write-scoped SSH client (ADR 0015). Groups (SPEC-016) come after, on a second preview.

Every command form and every answer here is the arrays' own, from the manual setup of the lab pair on
2026-11-03 (rack13-ARCUS OS 10.5.55 -> PRIMERA630R11U22 OS 4.6.20, tests/fixtures/rcip_pair/).
"""

from __future__ import annotations

import ipaddress
import time
from collections.abc import Callable

from alletra_onboard.adapters.array.cli_client import ArrayCliError
from alletra_onboard.adapters.array.rc_cli_client import answered_error
from alletra_onboard.application.provisioning.clients import make_rc_cli
from alletra_onboard.application.replication.read import parse_showport_rcip, parse_showrcopy
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    PlannedCall,
    RcipPortRequest,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationOutcome,
    ReplicationPlan,
    ReplicationReport,
    ReplicationResult,
    pair_ports,
)

#: SSH writes have no WSAPI equivalent (ADR 0015); the plan's WSAPI column says so.
SSH_ONLY = "— (no WSAPI call; over SSH)"
#: How long the apply waits for every planned link to show Up.
LINKS_UP_WAIT_S = 180.0
LINKS_UP_POLL_S = 10.0


def _name(view: ReplicationArrayView) -> str:
    return view.name or view.host


def _mask_matches(have: str, want: str) -> bool:
    try:
        return ipaddress.ip_network(f"0.0.0.0/{have}").prefixlen == ipaddress.ip_network(f"0.0.0.0/{want}").prefixlen
    except ValueError:
        return have == want


def _port_action(view: ReplicationArrayView, side: str, row: RcipPortRequest) -> ReplicationAction:
    label = _name(view)
    rcip = {p.nsp: p for p in view.rcip_ports}
    have = rcip.get(row.nsp)
    action = ReplicationAction(kind="rcip_port", name=row.nsp, where=side,  # type: ignore[arg-type]
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
    calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"controlport rcip addr -f {row.ip} {row.netmask} {row.nsp}")]  # type: ignore[arg-type]
    if row.gateway:
        calls.append(PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"controlport rcip gw -f {row.gateway} {row.nsp}"))  # type: ignore[arg-type]
    action.calls = calls
    action.reason = (f"RCIP address {row.ip} {row.netmask}" + (f", gateway {row.gateway}" if row.gateway else "")
                     + f" on {row.nsp} ({role.state})")
    return action


def _service_action(view: ReplicationArrayView, side: str) -> ReplicationAction:
    action = ReplicationAction(kind="rc_service", name="Remote Copy", where=side,  # type: ignore[arg-type]
                               detail={"was_configured": bool(view.rc_status)})
    if view.rc_started:
        action.state, action.reason = "exists", "started"
        return action
    action.calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli="startrcopy")]  # type: ignore[arg-type]
    action.reason = ("not configured on " if not view.rc_status else f"{view.rc_status.lower()} on ") + _name(view)
    return action


def _target_action(view: ReplicationArrayView, side: str, name: str, links: list[str]) -> ReplicationAction:
    """links: `<local n:s:p>:<peer address>`. Exists when a target already carries exactly those links."""
    label = _name(view)
    action = ReplicationAction(kind="target", name=name, where=side, detail={"links": links})  # type: ignore[arg-type]
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
    action.calls = [PlannedCall(where=side, wsapi=SSH_ONLY, cli=f"creatercopytarget {name} IP {' '.join(links)}")]  # type: ignore[arg-type]
    action.reason = f"target '{name}' with {len(links)} link(s): {', '.join(links)}"
    return action


def stale_fc_targets(primary: ReplicationArrayView, peer: ReplicationArrayView) -> list[str]:
    """SPEC-021 R3: an FC target on one array that carries the other array's FC node WWN. Live
    2026-11-03: with the Primera's failed FC target to rack13-ARCUS in place, its new IP target never
    learned the Alletra's identity (`showrcopy -d targets`: SysName None) and every group create on the
    Alletra failed with "Failed to send message to target"."""
    out = []
    for here, there in ((primary, peer), (peer, primary)):
        if not there.fc_node_wwn:
            continue
        for t in here.targets:
            if t.type.upper() == "FC" and t.options.upper() == there.fc_node_wwn:
                out.append(
                    f"{_name(here)} already has target '{t.name}' for {_name(there)} over Fibre Channel (status "
                    f"{t.status}). The arrays keep one partnership per pair, so an IP target beside it does not "
                    f"work. Remove it on {_name(here)} first: `removercopytarget -cleargroups -f {t.name}` (this also "
                    "removes the groups on that target; their volumes stay). Save `showrcopy -d groups` before."
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
    for side, view in (("A", a), ("B", b)):
        for row in (r for r in intent.network if r.side == side):
            actions.append(_port_action(view, side, row))
    actions += [_service_action(a, "A"), _service_action(b, "B")]
    actions.append(_target_action(a, "A", _name(b), [f"{pa.nsp}:{pb.ip}" for pa, pb in pairs]))
    actions.append(_target_action(b, "B", _name(a), [f"{pb.nsp}:{pa.ip}" for pa, pb in pairs]))
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

def apply_partnership(
    plan: ReplicationPlan, provisioning: ProvisioningIntent, *, rc_cli_factory: Callable = make_rc_cli,
    progress: Callable[[str], None] | None = None, sleep: Callable[[float], None] = time.sleep,
) -> ReplicationResult:
    """SPEC-021 R4: ports on A, ports on B, ping each pair, start Remote Copy, a target each way, links
    Up. Stops at the first refusal; the removal set (R5) covers exactly what was created."""
    result = ReplicationResult()
    intent = provisioning.replication
    if intent is None:
        result.error = "this run has no Replication tab"
        return result
    say = progress or (lambda _m: None)
    created_ports: dict[str, list[str]] = {"A": [], "B": []}
    started: dict[str, bool] = {}               # side -> Remote Copy was not configured before
    targets: dict[str, str] = {}

    def record(kind, name, where, status, detail="") -> None:
        result.outcomes.append(ReplicationOutcome(kind=kind, name=name, where=where, status=status, detail=detail))

    def compose() -> None:
        for side in ("A", "B"):
            lines = [f"removercopytarget {targets[side]}"] if side in targets else []
            if side in started:
                lines.append("stoprcopy -f -stopgroups -clear" if started[side] else "stoprcopy -f")
            lines += [f"controlport rcip delete -f {nsp}" for nsp in created_ports[side]]
            if side == "A":
                result.removals_a = lines
            else:
                result.removals_b = lines

    def actions(kind: str, side: str) -> list[ReplicationAction]:
        return [x for x in plan.actions if x.kind == kind and x.where == side and x.state == "create"]

    try:
        with rc_cli_factory(provisioning.array) as a_cli, rc_cli_factory(intent.peer) as b_cli:
            cli = {"A": a_cli, "B": b_cli}

            def write(side: str, command: str) -> str:
                out = cli[side].write(command)
                if answered_error(out):
                    raise ArrayCliError(f"{'this array' if side == 'A' else 'the peer'} refused `{command}`: "
                                        + next(ln.strip() for ln in out.splitlines() if ln.strip().lower().startswith("error")))
                return out

            for side in ("A", "B"):
                for x in actions("rcip_port", side):
                    d = x.detail
                    say(f"Setting RCIP address {d['ip']} on {x.name} ({side})…")
                    created_ports[side].append(x.name)          # before the write: a half-done address is undone too
                    compose()
                    write(side, f"controlport rcip addr -f {d['ip']} {d['netmask']} {x.name}")
                    if d.get("gateway"):
                        write(side, f"controlport rcip gw -f {d['gateway']} {x.name}")
                    back = {p.nsp: p for p in parse_showport_rcip(cli[side].run("showport -rcip"))}.get(x.name)
                    if back is None or back.ip != d["ip"]:
                        raise ArrayCliError(f"after setting it, showport -rcip does not show {d['ip']} on {x.name}")
                    if d.get("gateway") and back.gateway != d["gateway"]:
                        raise ArrayCliError(f"after setting it, showport -rcip shows gateway {back.gateway or 'none'} on "
                                            f"{x.name}, not {d['gateway']}")
                    record("rcip_port", x.name, side, "created",
                           f"{d['ip']} {d['netmask']}" + (f", gateway {d['gateway']}" if d.get("gateway") else "") + f", {back.state}")

            for pa, pb in pair_ports(intent.network):
                say(f"Ping {pb.ip} from {pa.nsp}…")
                out = a_cli.write(f"controlport rcip ping -c 3 {pb.ip} {pa.nsp}")
                line = next((ln.strip() for ln in out.splitlines() if "packet loss" in ln), out.strip()[-120:])
                if " 0% packet loss" not in f" {line}":
                    raise ArrayCliError(f"ping from {pa.nsp} to {pb.ip}: {line}. Check the cable and the network of "
                                        f"{pa.nsp}; nothing after the addresses was done")
                record("ping", f"{pa.nsp} → {pb.ip}", "A", "created", line)

            for side in ("A", "B"):
                for x in actions("rc_service", side):
                    say(f"Starting Remote Copy ({side})…")
                    started[side] = not x.detail.get("was_configured")
                    compose()
                    write(side, "startrcopy")
                    status = parse_showrcopy(cli[side].run("showrcopy"))["status"]
                    if status != "Started":
                        raise ArrayCliError(f"after startrcopy, showrcopy says '{status or 'not configured'}'")
                    record("rc_service", "Remote Copy", side, "created", "started")

            for side in ("A", "B"):
                for x in actions("target", side):
                    links = x.detail["links"]
                    say(f"Creating target {x.name} ({side})…")
                    targets[side] = x.name
                    compose()
                    write(side, f"creatercopytarget {x.name} IP {' '.join(links)}")
                    names = [t.name for t in parse_showrcopy(cli[side].run("showrcopy targets"))["targets"]]
                    if x.name not in names:
                        raise ArrayCliError(f"after creatercopytarget, showrcopy targets does not list '{x.name}'")
                    record("target", x.name, side, "created", f"{len(links)} link(s): {', '.join(links)}")

            say("Waiting for the links to come up…")
            waited, down = 0.0, []
            while True:
                down = []
                for side, cli_ in cli.items():
                    want = next((x for x in plan.actions if x.kind == "target" and x.where == side), None)
                    if want is None:
                        continue
                    target = want.detail.get("existing") or want.name
                    links = [lk for lk in parse_showrcopy(cli_.run("showrcopy links"))["links"] if lk.target == target]
                    down += [f"{side} {lk.nsp} → {lk.address} {lk.status}" for lk in links if not lk.up]
                    if not links:
                        down.append(f"{side}: no link on target '{target}'")
                if not down or waited >= LINKS_UP_WAIT_S:
                    break
                sleep(LINKS_UP_POLL_S)
                waited += LINKS_UP_POLL_S
            if down:
                raise ArrayCliError(f"links not Up after {LINKS_UP_WAIT_S:g} s: {'; '.join(down)}")
            record("links", "Remote Copy links", "A", "created", "every planned link Up on both arrays")
    except Exception as exc:  # noqa: BLE001 - the array's words, where it stopped, what to remove
        done = sum(1 for o in result.outcomes if o.status == "created")
        result.error = (f"Stopped after {done} step(s): {exc}. The removal set below undoes exactly what was "
                        "created before the failure.")
        record("links", "—", "A", "failed", str(exc))
    compose()
    return result
