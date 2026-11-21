"""SPEC-016 R2 (check): from two array views and the Replication tab, the partnership and blocking
findings — what is wrong with the request before any action is planned.

Every sentence here is for the operator. `plan.py` builds the exists / create / conflict actions
from the report this module returns.
"""

from __future__ import annotations

from collections.abc import Iterable

from alletra_onboard.domain.replication import (
    TEST_GROUP,
    TEST_VVSET,
    Partnership,
    PartnerTarget,
    ProtectionRequest,
    RcGroup,
    RcLink,
    RcTarget,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationReport,
    Transport,
    rtt_limit_ms,
    rtt_limit_text,
    sync_refused_target,
)

#: Support Matrix, 2-node system (research 2026-10-07 §3). Checked per mode; practically never hit.
GROUP_LIMIT = {"sync": 800, "async": 2400}


# ------------------------------------------------------------------ the partnership (by address or WWN)

def _outbound(view: ReplicationArrayView, target: RcTarget) -> list[RcLink]:
    return [link for link in view.links if link.target == target.name and not link.inbound]


def _addresses(links: list[RcLink]) -> set[str]:
    """What the links address: RCIP addresses, or port WWNs (upper case, as `showport` prints them)."""
    return {link.address.upper() for link in links}


def _transport(target: RcTarget) -> Transport:
    return "FC" if target.is_fc else "IP"


def _targets_towards(view: ReplicationArrayView, other: ReplicationArrayView) -> list[tuple[RcTarget, list[RcLink]]]:
    """Every target on `view` that points at `other`: an IP target whose outbound links all point at
    `other`'s RCIP addresses (SPEC-016 R2); an FC target whose Options carry one of `other`'s FC node WWNs
    and whose outbound links all address `other`'s FC port WWNs (SPEC-031 R3)."""
    out = []
    for target in view.targets:
        links = _outbound(view, target)
        if not links:
            continue
        if target.is_fc:
            resolves = target.options.upper() in other.fc_node_wwns and _addresses(links) <= other.fc_port_wwns
        else:
            resolves = _addresses(links) <= other.rcip_addresses
        if resolves:
            out.append((target, links))
    return out


def _fc_targets_naming(view: ReplicationArrayView, other: ReplicationArrayView) -> list[RcTarget]:
    """Every FC target on `view` that names `other`, resolved or not: its Options carry one of `other`'s FC
    node WWNs, or one of its links addresses one of `other`'s FC port WWNs."""
    return [t for t in view.targets if t.is_fc and (
        t.options.upper() in other.fc_node_wwns or _addresses(_outbound(view, t)) & other.fc_port_wwns)]


def _local_addresses(view: ReplicationArrayView, links: list[RcLink], transport: Transport) -> set[str]:
    """What the other array's links address when they point back over the same ports: the RCIP address of
    each port the links use, or its port WWN over Fibre Channel."""
    if transport == "FC":
        return {view.ports[link.nsp].port_wwn for link in links if link.nsp in view.ports} - {""}
    port_ip = {p.nsp: p.ip for p in view.rcip_ports}
    return {port_ip.get(link.nsp, "").upper() for link in links} - {""}


def _assign(targets: list[PartnerTarget], modes: Iterable[str]) -> dict[str, str]:
    """One target per sheet mode: the one already holding this run's groups of that mode (rerun), else
    one carrying only that mode, else an empty one not taken by the other mode. Fixed order, so the
    choice is the same on every preview."""
    chosen: dict[str, str] = {}
    taken: set[str] = set()
    for mode in ("sync", "async"):
        if mode not in modes:
            continue
        pick = (next((t for t in targets if mode in t.own_modes and t.name not in taken), None)
                or next((t for t in targets if t.modes == [mode] and t.name not in taken), None)
                or next((t for t in targets if not t.modes and t.name not in taken), None))
        if pick is not None:
            chosen[mode] = pick.name
            taken.add(pick.name)
    return chosen


def find_partnership(primary: ReplicationArrayView, peer: ReplicationArrayView, *,
                     modes: Iterable[str] = (), own_groups: Iterable[str] = ()) -> Partnership | None:
    """The target(s) on each array that point at the OTHER array: by RCIP address over IP, by node WWN and
    port WWNs over Fibre Channel (SPEC-031 R3). Names are never compared: on the lab pair E18U31's target
    for D22U27 is named AlletraMP_E18U31. Each primary target is paired with the peer target that answers
    over the same ports (its links point back at the addresses or WWNs of the ports the primary target
    uses). A pair has one transport: when the targets found are IP and FC both, there is no partnership to
    use (SPEC-031 R3; `check` says why)."""
    forward, backward = _targets_towards(primary, peer), _targets_towards(peer, primary)
    if not forward or not backward:
        return None
    transports: set[Transport] = {_transport(t) for t, _ in forward + backward}
    if len(transports) != 1:
        return None
    transport = transports.pop()
    own = set(own_groups)
    targets: list[PartnerTarget] = []
    for t, links in forward:
        local = _local_addresses(primary, links, transport)
        pair = (next((bt for bt in backward if _addresses(bt[1]) == local), None)
                or next((bt for bt in backward if _addresses(bt[1]) & local), None)
                or backward[0])
        on_target = [g for g in primary.groups if g.target == t.name]
        targets.append(PartnerTarget(
            name=t.name, peer_name=pair[0].name, transport=transport,
            links_up=sum(1 for link in links if link.up), links_total=len(links),
            peer_links_up=sum(1 for link in pair[1] if link.up), peer_links_total=len(pair[1]),
            mirror_config=t.mirror_config,
            modes=sorted({g.mode_key for g in on_target if g.name not in own}),
            groups=sum(1 for g in on_target if g.name not in own),
            own_modes=sorted({g.mode_key for g in on_target if g.name in own}),
        ))
    chosen = _assign(targets, set(modes))
    first = next((t for t in targets if t.name in chosen.values()), targets[0])
    return Partnership(
        target_on_primary=first.name, target_on_peer=first.peer_name, transport=transport,
        links_primary_up=first.links_up, links_primary_total=first.links_total,
        links_peer_up=first.peer_links_up, links_peer_total=first.peer_links_total,
        mirror_config=first.mirror_config, targets=targets, target_by_mode=chosen,
    )


def _name(view: ReplicationArrayView) -> str:
    return view.name or view.host


def _state(view: ReplicationArrayView, target: RcTarget) -> tuple[str, bool]:
    """(what shows the target's state, whether it is dead). Dead on SPEC-031 R5's terms, which BL-57 set
    for an FC target: status failed, no link Up, no started group. Only a dead target is offered for removal."""
    links = _outbound(view, target)
    up = sum(1 for link in links if link.up)
    started = [g.name for g in view.groups if g.target == target.name and g.status.lower() == "started"]
    text = f"{'Fibre Channel' if target.is_fc else 'IP'}, status {target.status or 'unknown'}, {up} of {len(links)} links Up"
    if started:
        text += f", started group{'s' if len(started) != 1 else ''} {', '.join(started)}"
    return text, target.status.lower() == "failed" and not up and not started


def _mixed_transports(primary: ReplicationArrayView, peer: ReplicationArrayView) -> str:
    """SPEC-031 R3, one pair one transport: the sentence when the two arrays show IP and FC targets towards
    each other, else ''. An older target in one transport stops a newer one in the other from working,
    without an error (LESSONS 44), so the step does not pick one. A target in use is never offered for removal."""
    sides = ((primary, peer), (peer, primary))
    ip = [(v, t) for v, o in sides for t, _ in _targets_towards(v, o) if not t.is_fc]
    fc = [(v, t) for v, o in sides for t in _fc_targets_naming(v, o)]
    if not ip or not fc:
        return ""
    named = "; ".join(f"{_name(v)} target '{t.name}' ({_state(v, t)[0]})" for v, t in ip + fc)
    text = (f"{_name(primary)} and {_name(peer)} show Remote Copy targets towards each other over IP and over Fibre "
            f"Channel: {named}. The arrays keep one partnership per pair, and a target in one transport stops one in "
            "the other from working, so the tool will not use either and plans nothing.")
    dead = [(v, t) for v, t in ip + fc if _state(v, t)[1]]
    if dead:
        text += (" Remove the failed one first: " + "; ".join(f"on {_name(v)}, `removercopytarget -cleargroups -f {t.name}`"
                                                             for v, t in dead)
                 + " (this also removes the groups on that target; their volumes stay). Save `showrcopy -d groups` before.")
    else:
        text += " None of them is failed, so the tool offers no removal: agree with the array owners which transport stays."
    return text


def _fc_unresolved(view: ReplicationArrayView, other: ReplicationArrayView) -> list[str]:
    """SPEC-031 R4: an FC target that names `other` but does not resolve to it, one sentence each with the
    WWN that did not match."""
    resolved = {t.name for t, _ in _targets_towards(view, other)}
    out = []
    for t in _fc_targets_naming(view, other):
        if t.name in resolved:
            continue
        misses = []
        if t.options.upper() not in other.fc_node_wwns:
            misses.append(f"its node WWN {t.options or '(none)'} is not one of {_name(other)}'s "
                          f"({', '.join(sorted(other.fc_node_wwns))})")
        links = _outbound(view, t)
        stray = [f"{link.nsp} → {link.address}" for link in links if link.address.upper() not in other.fc_port_wwns]
        if stray:
            misses.append(f"link{'s' if len(stray) != 1 else ''} {', '.join(stray)} address{'' if len(stray) != 1 else 'es'} "
                          f"no port of {_name(other)}")
        if not links:
            misses.append("it has no outbound link")
        out.append(f"{_name(view)} has Fibre Channel target '{t.name}' that does not resolve to {_name(other)}: "
                   + "; ".join(misses) + ".")
    return out


def _fc_one_way(view: ReplicationArrayView, other: ReplicationArrayView) -> list[str]:
    """An FC target that resolves to `other` while `other` has none that resolves back."""
    if any(t.is_fc for t, _ in _targets_towards(other, view)):
        return []
    return [f"{_name(view)} has target '{t.name}' for {_name(other)} over Fibre Channel, found by node WWN and port "
            f"WWN ({_state(view, t)[0]}); {_name(other)} has no Fibre Channel target that points back at {_name(view)}."
            for t, _ in _targets_towards(view, other) if t.is_fc]


# ------------------------------------------------------------------ R2: findings

def run_modes(intent: ReplicationIntent) -> list[str]:
    """The modes this run's groups replicate in: the rows', or the failover test group's alone (it takes the
    first row's mode, and a default row's without one)."""
    modes = {row.mode for row in intent.protections}
    if not modes and intent.failover_test and not intent.failover_group:
        modes = {ProtectionRequest(vvset=TEST_VVSET, peer_cpg="").mode}
    return sorted(modes)


def _sync_refused(primary: ReplicationArrayView, peer: ReplicationArrayView, intent: ReplicationIntent) -> str:
    """BL-62: the sentence when this run would create a sync group that this array refuses for the peer's OS
    (`sync_refused_target`), else ''. Said at the first read, before the partnership is set up; a sync group
    already on the array is not a write, so it is not refused."""
    family = sync_refused_target(primary.os_version, peer.os_version)
    if not family:
        return ""
    sets = [row.vvset for row in intent.protections if row.mode == "sync" and primary.group(row.group_name) is None]
    lead = intent.protections[0].mode if intent.protections else ProtectionRequest(vvset=TEST_VVSET, peer_cpg="").mode
    test = intent.failover_test and not intent.failover_group and lead == "sync" and primary.group(TEST_GROUP) is None
    if sets:
        what = (f"the sync row{'s' if len(sets) != 1 else ''} for volume set{'s' if len(sets) != 1 else ''} "
                + ", ".join(f"'{s}'" for s in sets) + " cannot be configured: set Mode to async (periodic)")
    elif test:
        what = "the failover test group, which takes the first row's mode, cannot be sync: set that row's Mode to async (periodic)"
    else:
        return ""
    a, b = primary.name or primary.host, peer.name or peer.host
    return (f"{a} (OS {primary.os_version}) refuses sync replication to {b} (OS {peer.os_version}), as it does to any "
            f"{family} array, so {what} on the Replication tab for this pair.")


def _check_partnership(report: ReplicationReport, row_modes: set[str], sets_up: bool) -> None:
    primary, peer = report.primary, report.peer
    a, b = _name(primary), _name(peer)
    f = report.findings
    p = report.partnership
    if p is None:
        if sets_up:
            return
        fc = [*_fc_one_way(primary, peer), *_fc_one_way(peer, primary),
              *_fc_unresolved(primary, peer), *_fc_unresolved(peer, primary)]
        if fc:
            # SPEC-031 R4: the Replication network tab sets up RCIP only; an FC pair is never sent there.
            f.append(
                f"No Remote Copy partnership between {a} and {b}: no two targets point at each other, by RCIP address "
                "or by Fibre Channel WWN. Fix the Fibre Channel partnership on the arrays (what each target shows is "
                "below), then read both arrays again."
            )
            f.extend(fc)
        else:
            f.append(
                f"No Remote Copy partnership between {a} and {b}: neither array has a target whose links point at "
                "the other's RCIP addresses. Name the replication ports on the Replication network tab and the tool "
                "sets it up, or set it up on the arrays first."
            )
        return
    used = [p.target_for(m) for m in sorted(row_modes)]
    for t in [t for t in used if t is not None] or p.targets[:1]:
        if t.links_up < 2 or t.peer_links_up < 2:
            f.append(
                f"The partnership needs at least 2 links Up each way: {a} → {b} via target '{t.name}' has "
                f"{t.links_up} of {t.links_total} Up, {b} → {a} via '{t.peer_name}' has {t.peer_links_up} of "
                f"{t.peer_links_total} Up."
            )
    if p.transport == "FC":
        # An extra FC target that half-matches does not stop the pair the step found; say so, do not block.
        report.notes.extend([*_fc_unresolved(primary, peer), *_fc_unresolved(peer, primary)])


def _busy_target_finding(
    t: PartnerTarget, mode: str, groups: list[RcGroup], planned: set[str], spare: str,
) -> str:
    have = t.modes[0]
    on_target = [g for g in groups if g.target == t.name and g.name not in planned]
    names = ", ".join(g.name for g in on_target[:4]) + ("…" if len(on_target) > 4 else "")
    if any(g.status.lower() == "started" for g in on_target):
        return (
            f"Target '{t.name}' already carries {len(on_target)} {have} group(s) ({names}); every group on one "
            f"target must replicate in the same mode (HPE Support Matrix), so {mode} groups cannot be started "
            f"there. Use {have} on the Replication tab, or a second target over {spare}."
        )
    # Live 2026-10-09: the array starts a periodic group beside STOPPED sync groups. The
    # rule still binds the stopped ones when they restart, so the tool does not go there.
    return (
        f"Target '{t.name}' already carries {len(on_target)} {have} group(s) ({names}), all stopped. The array "
        f"would start {mode} groups beside them, but every group on one target must replicate in the same "
        f"mode (HPE Support Matrix), so the tool will not put their restart at risk. Use {have} on the "
        f"Replication tab, or a second target over {spare}."
    )


def _target_slot_summary(t: PartnerTarget, target_by_mode: dict[str, str], other: str | None) -> str:
    if t.modes:
        return f"'{t.name}' carries {t.groups} {'/'.join(t.modes)} group(s)"
    if other and target_by_mode.get(other) == t.name:
        return f"'{t.name}' takes this run's {other} rows"
    return f"'{t.name}' is free"


def _check_target_modes(report: ReplicationReport, row_modes: set[str], planned: set[str]) -> None:
    # One mode per target (Support Matrix: "RC Groups using the same RC-Target must replicate in the
    # same mode"; proven live 2026-10-09 — the array refuses the START, HTTP 400 code 236, after
    # every other write has succeeded). HPE's answer is a target per mode over links of their own
    # (a link belongs to one target, live 2026-10-09), so a pair with such targets serves mixed rows.
    p = report.partnership
    if p is None:
        return
    a, b = _name(report.primary), _name(report.peer)
    f = report.findings
    spare = (
        "spare RCIP ports (a link belongs to one target; set it up on the arrays, the tool makes only the "
        "first target of a pair)"
        if p.transport == "IP"
        else "spare Fibre Channel ports (a link belongs to one target; set it up on the arrays)"
    )
    for mode in sorted(row_modes):
        if mode in p.target_by_mode:
            continue
        if len(p.targets) == 1 and p.targets[0].modes:
            f.append(_busy_target_finding(p.targets[0], mode, report.primary.groups, planned, spare))
        elif len(p.targets) == 1:
            f.append(
                f"The Replication tab mixes sync and async rows and {a} → {b} has one target ('{p.targets[0].name}'); "
                "every group on one target must replicate in the same mode (HPE Support Matrix). Make all rows one "
                f"mode, or add a second target over {spare}."
            )
        else:
            other = next((m for m, _n in p.target_by_mode.items() if m != mode), None)
            parts = [_target_slot_summary(t, p.target_by_mode, other) for t in p.targets]
            f.append(
                f"None of the {len(p.targets)} targets from {a} to {b} can carry a {mode} group ({'; '.join(parts)}); "
                "every group on one target must replicate in the same mode (HPE Support Matrix). Use that mode on "
                f"the Replication tab, or a target of its own over {spare}."
            )


def _check_protection_row(
    report: ReplicationReport, row: ProtectionRequest, transport: str, rtt: float | None,
) -> None:
    primary, peer = report.primary, report.peer
    a, b = _name(primary), _name(peer)
    f = report.findings
    if transport == "IP" and rtt is not None and rtt > rtt_limit_ms("IP", row.mode):
        f.append(f"Volume set '{row.vvset}': the measured round-trip time is {rtt:g} ms; "
                 f"{rtt_limit_text('IP', row.mode)}.")
    members = primary.vvsets.get(row.vvset)
    if members is None:
        f.append(f"Volume set '{row.vvset}' does not exist on {a}. Create it first (Volumes tab and "
                 "Provision storage, or on the array), or correct the name.")
        return
    if not members:
        f.append(f"Volume set '{row.vvset}' on {a} is empty; a Remote Copy group needs at least one volume.")
        return
    for volume in members:
        existing = primary.volume_group(volume)
        if existing is not None and existing != row.group_name:
            f.append(f"Volume '{volume}' (in set '{row.vvset}') is already in Remote Copy group '{existing}'; "
                     "a volume can be in one group only.")
    if row.peer_cpg not in peer.cpg_free_mib:
        f.append(f"Peer CPG '{row.peer_cpg}' does not exist on {b} (it has: {', '.join(sorted(peer.cpg_free_mib)) or 'none'}).")
    else:
        need = sum(primary.volume_size_mib.get(v, 0) for v in members)
        free = peer.cpg_free_mib[row.peer_cpg]
        if need and free < need:
            f.append(f"Peer CPG '{row.peer_cpg}' on {b} has {free // 1024} GiB free; the volumes in '{row.vvset}' "
                     f"need {need // 1024} GiB.")
    count = sum(1 for g in primary.groups if g.mode_key == row.mode)
    if count >= GROUP_LIMIT[row.mode]:
        f.append(f"{a} already has {count} {row.mode} groups, the limit for a 2-node system.")


def check(primary: ReplicationArrayView, peer: ReplicationArrayView, intent: ReplicationIntent) -> ReplicationReport:
    report = ReplicationReport(primary=primary, peer=peer)
    f = report.findings
    if primary.read_error:
        report.error = primary.read_error
        return report
    if peer.read_error:
        report.error = peer.read_error
        return report

    a, b = _name(primary), _name(peer)
    row_modes = {row.mode for row in intent.protections}
    planned = {row.group_name for row in intent.protections} | {TEST_GROUP}
    report.rtt_ms, report.modes = intent.rtt_ms, run_modes(intent)
    mixed = _mixed_transports(primary, peer)
    if mixed:
        # SPEC-031 R3: one pair, one transport. The step does not pick one, and plans nothing.
        report.mixed_transports = True
        f.append(mixed)
        return report
    report.partnership = find_partnership(primary, peer, modes=row_modes, own_groups=planned)
    sets_up = bool(intent.network) and report.partnership is None   # SPEC-021: the tool makes it
    _check_partnership(report, row_modes, sets_up)
    if sets_up and len(row_modes) > 1:
        # SPEC-021 makes one target per pair, and every group on a target must replicate in one mode: say
        # so before the partnership is set up, not after.
        f.append(
            f"The Replication tab mixes sync and async rows, and the partnership the tool sets up between {a} and "
            f"{b} has one target; every group on one target must replicate in the same mode (HPE Support Matrix). "
            "Make all rows one mode, or set up a second target over spare RCIP ports on the arrays first."
        )
    refused = _sync_refused(primary, peer, intent)
    if refused:
        f.append(refused)
    for view, label in ((primary, a), (peer, b)):
        if not view.rc_started and not sets_up:
            f.append(f"Remote Copy is not started on {label} (showrcopy says '{view.rc_status or 'unknown'}'); "
                     "it has to be started before groups can be created.")
    _check_target_modes(report, row_modes, planned)
    # Over RCIP a typed RTT over the limit is a finding. Over Fibre Channel the typed RTT stands in for the
    # measurement, so the apply holds it to the limit with the 'Continue anyway' tick instead (SPEC-031 R6).
    transport = report.partnership.transport if report.partnership is not None else "IP"
    for row in intent.protections:
        _check_protection_row(report, row, transport, intent.rtt_ms)
    return report
