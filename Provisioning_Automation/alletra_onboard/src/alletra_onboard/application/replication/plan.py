"""SPEC-016 R2 (check) and R3 (plan): from two array views and the Replication tab, the blocking
findings and the exists / create / conflict plan — nothing written, nothing guessed.

Every sentence here is for the operator. Every WSAPI body shape and CLI line comes from the
`hpe3parclient` docstrings and the array's own `-h` (fixtures README).
"""

from __future__ import annotations

from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    RTT_LIMIT_MS,
    TEST_PEER_VVSET,
    TEST_VOLUME,
    TEST_VOLUME_GIB,
    TEST_VVSET,
    Partnership,
    PlannedCall,
    ProtectionRequest,
    RcGroup,
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

def find_partnership(primary: ReplicationArrayView, peer: ReplicationArrayView) -> Partnership | None:
    """The target on each array whose outbound links point at the OTHER array's RCIP addresses.
    Names are never compared: on the lab pair E18U31's target for D22U27 is named AlletraMP_E18U31."""
    def _target_towards(view: ReplicationArrayView, other: ReplicationArrayView) -> tuple[str, int, int] | None:
        if not other.rcip_addresses:
            return None
        for target in view.targets:
            links = [link for link in view.links if link.target == target.name and not link.inbound]
            if links and {link.address for link in links} <= other.rcip_addresses:
                return target.name, sum(1 for link in links if link.up), len(links)
        return None

    forward = _target_towards(primary, peer)
    backward = _target_towards(peer, primary)
    if forward is None or backward is None:
        return None
    target = next(t for t in primary.targets if t.name == forward[0])
    return Partnership(
        target_on_primary=forward[0], target_on_peer=backward[0],
        links_primary_up=forward[1], links_primary_total=forward[2],
        links_peer_up=backward[1], links_peer_total=backward[2],
        mirror_config=target.mirror_config,
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
    report.partnership = find_partnership(primary, peer)
    if report.partnership is None:
        f.append(
            f"No Remote Copy partnership between {a} and {b}: neither array has a target whose links point at "
            f"the other's RCIP addresses. The tool configures partnerships from v0.19 (ADR 0015); until then it "
            "has to exist before this step."
        )
    else:
        p = report.partnership
        if p.links_primary_up < 2 or p.links_peer_up < 2:
            f.append(
                f"The partnership needs at least 2 links Up each way: {a} → {b} has {p.links_primary_up} of "
                f"{p.links_primary_total} Up, {b} → {a} has {p.links_peer_up} of {p.links_peer_total} Up."
            )
    for view, label in ((primary, a), (peer, b)):
        if not view.rc_started:
            f.append(f"Remote Copy is not started on {label} (showrcopy says '{view.rc_status or 'unknown'}'); "
                     "it has to be started before groups can be created.")

    rtt = intent.rtt_ms
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
    target = report.partnership.target_on_primary if report.partnership else "<peer>"
    mirror_config = report.partnership.mirror_config if report.partnership else True
    a, b = primary.name or primary.host, peer.name or peer.host

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
        test_row = ProtectionRequest(vvset=TEST_VVSET, mode="async", peer_cpg=(intent.protections[0].peer_cpg if intent.protections else ""),
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
        plan.notes.append(f"Partnership: {a} → {b} via target '{p.target_on_primary}' ({p.links_primary_up}/{p.links_primary_total} links Up), "
                          f"{b} → {a} via target '{p.target_on_peer}' ({p.links_peer_up}/{p.links_peer_total} Up), policy "
                          + ("mirror_config" if p.mirror_config else "no_mirror_config") + ".")
    if primary.system_id is not None:
        plan.notes.append(f"On {b} each new group will be named '<group>.r{primary.system_id}'.")
    return plan
