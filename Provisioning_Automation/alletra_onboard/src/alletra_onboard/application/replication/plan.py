"""SPEC-016 R2 (check) and R3 (plan): from two array views and the Replication tab, the blocking
findings and the exists / create / conflict plan — nothing written, nothing guessed.

Every sentence here is for the operator. Every WSAPI body shape and CLI line comes from the
`hpe3parclient` docstrings and the array's own `-h` (fixtures README).
"""

from __future__ import annotations

from collections.abc import Iterable

from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    RTT_LIMIT_MS,
    TEST_GROUP,
    TEST_PEER_VVSET,
    TEST_VOLUME,
    TEST_VOLUME_GIB,
    TEST_VVSET,
    Partnership,
    PartnerTarget,
    PlannedCall,
    ProtectionRequest,
    RcGroup,
    RcLink,
    RcTarget,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
    ReplicationReport,
)

#: Support Matrix, 2-node system (research 2026-10-07 §3). Checked per mode; practically never hit.
GROUP_LIMIT = {"sync": 800, "async": 2400}
#: WSAPI remote-copy-group mode values (hpe3parclient `createRemoteCopyGroup` docs; 1 = sync, 2 = periodic).
WSAPI_MODE = {"sync": 1, "async": 2}


# ------------------------------------------------------------------ the partnership (by address)

def _targets_towards(view: ReplicationArrayView, other: ReplicationArrayView) -> list[tuple[RcTarget, list[RcLink]]]:
    """Every target on `view` whose outbound links all point at `other`'s RCIP addresses."""
    if not other.rcip_addresses:
        return []
    out = []
    for target in view.targets:
        links = [link for link in view.links if link.target == target.name and not link.inbound]
        if links and {link.address for link in links} <= other.rcip_addresses:
            out.append((target, links))
    return out


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
    """The target(s) on each array whose outbound links point at the OTHER array's RCIP addresses.
    Names are never compared: on the lab pair E18U31's target for D22U27 is named AlletraMP_E18U31.
    Each primary target is paired with the peer target that answers over the same ports (its links
    point back at the addresses of the ports the primary target uses)."""
    forward, backward = _targets_towards(primary, peer), _targets_towards(peer, primary)
    if not forward or not backward:
        return None
    own = set(own_groups)
    port_ip = {p.nsp: p.ip for p in primary.rcip_ports}
    targets: list[PartnerTarget] = []
    for t, links in forward:
        local = {port_ip.get(link.nsp, "") for link in links} - {""}
        pair = (next((bt for bt in backward if {link.address for link in bt[1]} == local), None)
                or next((bt for bt in backward if {link.address for link in bt[1]} & local), None)
                or backward[0])
        on_target = [g for g in primary.groups if g.target == t.name]
        targets.append(PartnerTarget(
            name=t.name, peer_name=pair[0].name,
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
        target_on_primary=first.name, target_on_peer=first.peer_name,
        links_primary_up=first.links_up, links_primary_total=first.links_total,
        links_peer_up=first.peer_links_up, links_peer_total=first.peer_links_total,
        mirror_config=first.mirror_config, targets=targets, target_by_mode=chosen,
    )


# ------------------------------------------------------------------ R2: findings

def check(primary: ReplicationArrayView, peer: ReplicationArrayView, intent: ReplicationIntent) -> ReplicationReport:
    report = ReplicationReport(primary=primary, peer=peer)
    f = report.findings
    if primary.read_error:
        report.error = primary.read_error
        return report
    if peer.read_error:
        report.error = peer.read_error
        return report

    a, b = primary.name or primary.host, peer.name or peer.host
    row_modes = {row.mode for row in intent.protections}
    planned = {row.group_name for row in intent.protections} | {TEST_GROUP}
    report.partnership = find_partnership(primary, peer, modes=row_modes, own_groups=planned)
    if report.partnership is None:
        f.append(
            f"No Remote Copy partnership between {a} and {b}: neither array has a target whose links point at "
            f"the other's RCIP addresses. The tool configures partnerships from v0.19 (ADR 0015); until then it "
            "has to exist before this step."
        )
        fc = [t.name for v in (primary, peer) for t in v.targets if t.type.upper() == "FC"]
        if fc:
            f.append(f"Remote Copy over Fibre Channel target(s) found ({', '.join(sorted(set(fc)))}); this release "
                     "supports Remote Copy over IP only (ADR 0015).")
    else:
        p = report.partnership
        used = [p.target_for(m) for m in sorted(row_modes)]
        for t in [t for t in used if t is not None] or p.targets[:1]:
            if t.links_up < 2 or t.peer_links_up < 2:
                f.append(
                    f"The partnership needs at least 2 links Up each way: {a} → {b} via target '{t.name}' has "
                    f"{t.links_up} of {t.links_total} Up, {b} → {a} via '{t.peer_name}' has {t.peer_links_up} of "
                    f"{t.peer_links_total} Up."
                )
    for view, label in ((primary, a), (peer, b)):
        if not view.rc_started:
            f.append(f"Remote Copy is not started on {label} (showrcopy says '{view.rc_status or 'unknown'}'); "
                     "it has to be started before groups can be created.")

    rtt = intent.rtt_ms
    # One mode per target (Support Matrix: "RC Groups using the same RC-Target must replicate in the
    # same mode"; proven live 2026-10-09 — the array refuses the START, HTTP 400 code 236, after
    # every other write has succeeded). HPE's answer is a target per mode over links of their own
    # (a link belongs to one target, live 2026-10-09), so a pair with such targets serves mixed rows.
    if report.partnership is not None:
        p = report.partnership
        for mode in sorted(row_modes):
            if mode in p.target_by_mode:
                continue
            tail = ("Use {have} on the Replication tab, or a second target over spare RCIP ports (a link belongs "
                    "to one target; the tool configures targets from v0.19).")
            if len(p.targets) == 1 and p.targets[0].modes:
                t = p.targets[0]
                have = t.modes[0]
                on_target = [g for g in primary.groups if g.target == t.name and g.name not in planned]
                names = ", ".join(g.name for g in on_target[:4]) + ("…" if len(on_target) > 4 else "")
                f.append(
                    f"Target '{t.name}' already carries {len(on_target)} {have} group(s) ({names}); every group on one "
                    f"target must replicate in the same mode (HPE Support Matrix), so {mode} groups cannot be started "
                    f"there. " + tail.format(have=have)
                )
            elif len(p.targets) == 1:
                f.append(
                    f"The Replication tab mixes sync and async rows and {a} → {b} has one target ('{p.targets[0].name}'); "
                    "every group on one target must replicate in the same mode (HPE Support Matrix). Make all rows one "
                    "mode, or add a second target over spare RCIP ports (a link belongs to one target; the tool "
                    "configures targets from v0.19)."
                )
            else:
                other = next((m for m, n in p.target_by_mode.items() if m != mode), None)
                parts = []
                for t in p.targets:
                    if t.modes:
                        parts.append(f"'{t.name}' carries {t.groups} {'/'.join(t.modes)} group(s)")
                    elif other and p.target_by_mode.get(other) == t.name:
                        parts.append(f"'{t.name}' takes this run's {other} rows")
                    else:
                        parts.append(f"'{t.name}' is free")
                f.append(
                    f"None of the {len(p.targets)} targets from {a} to {b} can carry a {mode} group ({'; '.join(parts)}); "
                    "every group on one target must replicate in the same mode (HPE Support Matrix). Use that mode on "
                    "the Replication tab, or a target of its own over spare RCIP ports (a link belongs to one target; "
                    "the tool configures targets from v0.19)."
                )
    for row in intent.protections:
        limit = RTT_LIMIT_MS[row.mode]
        if rtt is not None and rtt > limit:
            f.append(f"Volume set '{row.vvset}': the measured round-trip time is {rtt:g} ms; {row.mode} replication "
                     f"over RCIP needs {limit:g} ms or less.")
        members = primary.vvsets.get(row.vvset)
        if members is None:
            f.append(f"Volume set '{row.vvset}' does not exist on {a}. Run Provision storage first, or correct the name.")
            continue
        if not members:
            f.append(f"Volume set '{row.vvset}' on {a} is empty; a Remote Copy group needs at least one volume.")
            continue
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
    return report


# ------------------------------------------------------------------ R3: plan

def _group_matches(group: RcGroup, row: ProtectionRequest, members: list[str], target: str) -> str:
    """'' when the existing group is what the row asks for; otherwise the first difference."""
    if group.target != target:
        return f"replicates to target '{group.target}', not '{target}'"
    if group.mode_key != row.mode:
        return f"is {group.mode.lower()}, the sheet asks for {row.mode}"
    have, want = set(group.volume_names), set(members)
    if have != want:
        missing, extra = sorted(want - have), sorted(have - want)
        parts = []
        if missing:
            parts.append("does not hold " + ", ".join(missing))
        if extra:
            parts.append("also holds " + ", ".join(extra))
        return "; ".join(parts)
    return ""


def _group_calls(row: ProtectionRequest, members: list[str], target: str, local_cpg: str, mirror_config: bool) -> tuple[list[PlannedCall], PlannedCall]:
    """(the calls that build the group, the start) — the start is sequenced after the peer set."""
    g, mode = row.group_name, WSAPI_MODE[row.mode]
    cli_mode = "sync" if row.mode == "sync" else "periodic"
    calls = [PlannedCall(
        where="A",
        wsapi=f"POST /remotecopygroups {{name: {g}, targets: [{{targetName: {target}, mode: {mode}, userCPG: {row.peer_cpg}}}]"
              + (f", localUserCPG: {local_cpg}" if local_cpg else "") + "}",
        cli="creatercopygroup" + (f" -usr_cpg {local_cpg} {target}:{row.peer_cpg}" if local_cpg else "") + f" {g} {target}:{cli_mode}",
    )]
    policies = {"autoRecover": row.auto_recover, "autoSynchronize": row.auto_synchronize}
    body = f"targets: [{{targetName: {target}" + (f", syncPeriod: {row.period_seconds}" if row.period_seconds else "") \
        + f", policies: {{autoRecover: {str(row.auto_recover).lower()}, autoSynchronize: {str(row.auto_synchronize).lower()}}}}}]"
    cli_lines = []
    if row.period_seconds:
        cli_lines.append(f"setrcopygroup period {row.rpo_minutes * 30 // 60}m {target} {g}")
    for pol, on in (("auto_recover", policies["autoRecover"]), ("auto_synchronize", policies["autoSynchronize"])):
        cli_lines.append(f"setrcopygroup pol {pol if on else 'no_' + pol} {g}")
    calls.append(PlannedCall(where="A", wsapi=f"PUT /remotecopygroups/{g} {{{body}}}", cli=" ; ".join(cli_lines)))
    for volume in members:
        calls.append(PlannedCall(
            where="A",
            wsapi=f"PUT /remotecopygroups/{g} {{action: admit, volumeName: {volume}, "
                  f"targets: [{{targetName: {target}, secVolumeName: {volume}}}], volumeAutoCreation: true}}",
            cli=f"admitrcopyvv -createvv {volume} {g} {target}:{volume}",
        ))
    start_where = "A" if mirror_config else "B"
    start = PlannedCall(
        where=start_where,
        wsapi=f"PUT /remotecopygroups/{g} {{action: start}}" + ("" if mirror_config else "  (on the peer first: target policy is no_mirror_config)"),
        cli=f"startrcopygroup {g}",
    )
    return calls, start


def build_plan(report: ReplicationReport, intent: ReplicationIntent, provisioning: ProvisioningIntent) -> ReplicationPlan:
    plan = ReplicationPlan(blockers=list(report.findings))
    if report.error:
        plan.error = report.error
        return plan
    primary, peer = report.primary, report.peer
    partnership = report.partnership
    a, b = primary.name or primary.host, peer.name or peer.host

    def target_for(mode: str) -> tuple[str, bool]:
        """(target name, mirror_config) for a row's mode — the per-mode choice, else the first target."""
        if partnership is None:
            return "<peer>", True
        t = partnership.target_for(mode)
        return (t.name, t.mirror_config) if t else (partnership.target_on_primary, partnership.mirror_config)

    rows: list[tuple[ProtectionRequest, list[str], str]] = []
    for row in intent.protections:
        members = primary.vvsets.get(row.vvset) or [v.name for v in provisioning.volumes if v.vvset == row.vvset]
        local_cpg = next((v.cpg for v in provisioning.volumes if v.vvset == row.vvset), "")
        rows.append((row, members, local_cpg))
    seq = 0

    def number(*calls: PlannedCall) -> None:
        nonlocal seq
        for c in calls:
            seq += 1
            c.seq = seq

    if intent.failover_test and not intent.failover_group:
        # The test group rides the same target, so it takes the rows' mode (one mode per target).
        lead = intent.protections[0] if intent.protections else ProtectionRequest(vvset=TEST_VVSET, peer_cpg="")
        test_row = ProtectionRequest(vvset=TEST_VVSET, mode=lead.mode, rpo_minutes=lead.rpo_minutes, peer_cpg=lead.peer_cpg,
                                     peer_vvset=TEST_PEER_VVSET)
        test_cpg = next((v.cpg for v in provisioning.volumes), "")
        if TEST_VOLUME not in primary.volume_size_mib:
            create_vv = PlannedCall(where="A", wsapi=f"POST /volumes {{name: {TEST_VOLUME}, cpg: {test_cpg}, sizeMiB: {TEST_VOLUME_GIB * 1024}, tpvv: true}}",
                                    cli=f"createvv -tpvv {test_cpg} {TEST_VOLUME} {TEST_VOLUME_GIB}g")
            number(create_vv)
            plan.actions.append(ReplicationAction(
                kind="test_volume", name=TEST_VOLUME, where="A", state="create",
                reason=f"{TEST_VOLUME_GIB} GiB tpvv for the failover test", calls=[create_vv],
                detail={"cpg": test_cpg, "size_gib": TEST_VOLUME_GIB},
            ))
        else:
            plan.actions.append(ReplicationAction(kind="test_volume", name=TEST_VOLUME, state="exists", reason="already on the array"))
        if TEST_VVSET not in primary.vvsets:
            create_set = PlannedCall(where="A", wsapi=f"POST /volumesets {{name: {TEST_VVSET}, setmembers: [{TEST_VOLUME}]}}",
                                     cli=f"createvvset {TEST_VVSET} {TEST_VOLUME}")
            number(create_set)
            plan.actions.append(ReplicationAction(
                kind="test_vvset", name=TEST_VVSET, where="A", state="create", reason=f"holds {TEST_VOLUME}", calls=[create_set],
                detail={"members": [TEST_VOLUME]},
            ))
        else:
            plan.actions.append(ReplicationAction(kind="test_vvset", name=TEST_VVSET, state="exists", reason="already on the array"))
        rows.append((test_row, primary.vvsets.get(TEST_VVSET) or [TEST_VOLUME], test_cpg))

    for row, members, local_cpg in rows:
        g = row.group_name
        target, mirror_config = target_for(row.mode)
        existing = primary.group(g)
        peer_set = row.peer_vvset_name
        peer_set_call: PlannedCall | None = None
        if peer_set not in peer.vvsets:
            peer_set_call = PlannedCall(where="B", wsapi=f"POST /volumesets {{name: {peer_set}, setmembers: [{', '.join(members)}]}}",
                                        cli=f"createvvset {peer_set} {' '.join(members)}")
        if existing is None:
            setup, start = _group_calls(row, members, target, local_cpg, mirror_config)
            number(*setup)
            if peer_set_call is not None:
                number(peer_set_call)
            number(start)
            plan.actions.append(ReplicationAction(
                kind="group", name=g, where="A", state="create",
                reason=f"{row.mode}" + (f", RPO {row.rpo_minutes} min (period {row.period_seconds // 60} min)" if row.period_seconds else "")
                       + f" → {target}, {len(members)} volume(s) from set '{row.vvset}', secondaries on {row.peer_cpg}",
                calls=[*setup, start],
                detail={
                    "vvset": row.vvset, "mode": row.mode, "volumes": members, "target": target,
                    "peer_cpg": row.peer_cpg, "local_cpg": local_cpg, "period_seconds": row.period_seconds,
                    "auto_recover": row.auto_recover, "auto_synchronize": row.auto_synchronize,
                    "peer_vvset": peer_set, "start_where": start.where, "is_test": row.vvset == TEST_VVSET,
                },
            ))
        else:
            diff = _group_matches(existing, row, members, target)
            if diff:
                plan.actions.append(ReplicationAction(kind="group", name=g, state="conflict", reason=f"exists but {diff}"))
                plan.blockers.append(f"Remote Copy group '{g}' exists on {a} but {diff}. The tool never changes an existing group; "
                                     "remove it on the array or rename the volume set.")
            else:
                plan.actions.append(ReplicationAction(
                    kind="group", name=g, state="exists",
                    reason=f"{existing.status}, {existing.role}, {existing.mode}, {len(existing.volumes)} volume(s)",
                ))
            if peer_set_call is not None:
                number(peer_set_call)
        if peer_set_call is None:
            plan.actions.append(ReplicationAction(kind="peer_vvset", name=peer_set, where="B", state="exists",
                                                  reason=f"{len(peer.vvsets[peer_set])} member(s) on {b}"))
        else:
            plan.actions.append(ReplicationAction(
                kind="peer_vvset", name=peer_set, where="B", state="create",
                reason=f"the secondary volumes on {b}, for the DR site's exports", calls=[peer_set_call],
                detail={"members": members, "group": g},
            ))

    planned = {row.group_name for row, _, _ in rows}
    plan.existing_groups = [g.name for g in primary.groups if g.name not in planned]
    if plan.existing_groups:
        plan.notes.append(f"{len(plan.existing_groups)} Remote Copy group(s) already on {a} are not part of this plan and will not be touched: "
                          + ", ".join(plan.existing_groups) + ".")
    if report.partnership:
        p = report.partnership
        legs = "; ".join(
            f"{a} → {b} via target '{t.name}' ({t.links_up}/{t.links_total} links Up), {b} → {a} via '{t.peer_name}' "
            f"({t.peer_links_up}/{t.peer_links_total} Up), policy " + ("mirror_config" if t.mirror_config else "no_mirror_config")
            + ("" if not t.modes else f", carries {t.groups} {'/'.join(t.modes)} group(s)")
            for t in p.targets)
        plan.notes.append(f"Partnership: {legs}.")
        if len(p.targets) > 1 and p.target_by_mode:
            plan.notes.append("Target per mode this run: " + ", ".join(f"{m} → '{n}'" for m, n in sorted(p.target_by_mode.items())) + ".")
    if primary.system_id is not None:
        plan.notes.append(f"On {b} each new group will be named '<group>.r{primary.system_id}'.")
    return plan
