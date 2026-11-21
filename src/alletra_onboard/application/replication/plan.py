"""SPEC-016 R3 (plan): from the checked array views and the Replication tab, the exists / create /
conflict plan — nothing written, nothing guessed.

Every sentence here is for the operator. Every WSAPI body shape and CLI line comes from the
`hpe3parclient` docstrings and the array's own `-h` (fixtures README). Partnership discovery and
blocking findings live in `plan_check.py`.
"""

from __future__ import annotations

from itertools import count
from typing import Literal

from alletra_onboard.application.replication.partnership import plan_partnership
from alletra_onboard.application.replication.plan_check import array_name
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    TEST_PEER_VVSET,
    TEST_VOLUME,
    TEST_VOLUME_GIB,
    TEST_VVSET,
    TRANSPORT_WORDS,
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

#: WSAPI remote-copy-group mode values (hpe3parclient `createRemoteCopyGroup` docs; 1 = sync, 2 = periodic).
WSAPI_MODE = {"sync": 1, "async": 2}


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
        cli_lines.append(f"setrcopygroup period {row.period_seconds // 60}m {target} {g}")
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


def _vvset_call(where: Literal["A", "B"], name: str, members: list[str]) -> PlannedCall:
    return PlannedCall(
        where=where,
        wsapi=f"POST /volumesets {{name: {name}, setmembers: [{', '.join(members)}]}}",
        cli=f"createvvset {name} {' '.join(members)}",
    )


def _number(seq: count[int], *calls: PlannedCall | None) -> None:
    for call in calls:
        if call is not None:
            call.seq = next(seq)


def _target_for(partnership: Partnership | None, mode: str) -> tuple[str, bool]:
    """(target name, mirror_config) for a row's mode — the per-mode choice, else the first target."""
    if partnership is None:
        return "<peer>", True
    t = partnership.target_for(mode)
    return (t.name, t.mirror_config) if t else (partnership.target_on_primary, partnership.mirror_config)


def _resolve_protection_rows(
    primary: ReplicationArrayView, intent: ReplicationIntent, provisioning: ProvisioningIntent,
) -> tuple[list[tuple[ProtectionRequest, list[str], str]], list[str]]:
    a = array_name(primary)
    rows: list[tuple[ProtectionRequest, list[str], str]] = []
    blockers: list[str] = []
    for row in intent.protections:
        members = primary.vvsets.get(row.vvset) or [v.name for v in provisioning.volumes if v.vvset == row.vvset]
        # WSAPI refuses a group with a target userCPG and no localUserCPG (live 2026-11-03, HTTP 400 code 40).
        local_cpg = next((v.cpg for v in provisioning.volumes if v.vvset == row.vvset), "") or provisioning.default_cpg
        if primary.cpg_free_mib and local_cpg not in primary.cpg_free_mib:
            blockers.append(
                f"Remote Copy group for '{row.vvset}' needs a local CPG on {a}; '{local_cpg}' is not one of its CPGs "
                f"({', '.join(sorted(primary.cpg_free_mib))}). Set 'Default CPG' on the Provisioning tab."
            )
        rows.append((row, members, local_cpg))
    return rows, blockers


def _plan_failover_test_objects(
    primary: ReplicationArrayView, intent: ReplicationIntent, provisioning: ProvisioningIntent, seq: count[int],
) -> tuple[list[ReplicationAction], list[str], tuple[ProtectionRequest, list[str], str]]:
    a = array_name(primary)
    # The test group rides the same target, so it takes the rows' mode (one mode per target).
    lead = intent.protections[0] if intent.protections else ProtectionRequest(vvset=TEST_VVSET, peer_cpg="")
    test_row = ProtectionRequest(
        vvset=TEST_VVSET, mode=lead.mode, rpo_minutes=lead.rpo_minutes,
        peer_cpg=lead.peer_cpg, peer_vvset=TEST_PEER_VVSET,
    )
    test_cpg = next((v.cpg for v in provisioning.volumes), "") or provisioning.default_cpg
    actions: list[ReplicationAction] = []
    blockers: list[str] = []
    if TEST_VOLUME not in primary.volume_size_mib:
        if primary.cpg_free_mib and test_cpg not in primary.cpg_free_mib:
            blockers.append(
                f"The failover test volume {TEST_VOLUME} goes in CPG '{test_cpg}' on {a}, which has no CPG of that name "
                f"(it has: {', '.join(sorted(primary.cpg_free_mib))}). Set 'Default CPG' on the Provisioning tab."
            )
        create_vv = PlannedCall(
            where="A",
            wsapi=f"POST /volumes {{name: {TEST_VOLUME}, cpg: {test_cpg}, sizeMiB: {TEST_VOLUME_GIB * 1024}, tpvv: true}}",
            cli=f"createvv -tpvv {test_cpg} {TEST_VOLUME} {TEST_VOLUME_GIB}g",
        )
        _number(seq, create_vv)
        actions.append(ReplicationAction(
            kind="test_volume", name=TEST_VOLUME, where="A", state="create",
            reason=f"{TEST_VOLUME_GIB} GiB tpvv for the failover test", calls=[create_vv],
            detail={"cpg": test_cpg, "size_gib": TEST_VOLUME_GIB},
        ))
    else:
        actions.append(ReplicationAction(kind="test_volume", name=TEST_VOLUME, state="exists", reason="already on the array"))
    if TEST_VVSET not in primary.vvsets:
        create_set = _vvset_call("A", TEST_VVSET, [TEST_VOLUME])
        _number(seq, create_set)
        actions.append(ReplicationAction(
            kind="test_vvset", name=TEST_VVSET, where="A", state="create",
            reason=f"holds {TEST_VOLUME}", calls=[create_set], detail={"members": [TEST_VOLUME]},
        ))
    else:
        actions.append(ReplicationAction(kind="test_vvset", name=TEST_VVSET, state="exists", reason="already on the array"))
    return actions, blockers, (test_row, primary.vvsets.get(TEST_VVSET) or [TEST_VOLUME], test_cpg)


def _plan_group_actions(
    report: ReplicationReport, row: ProtectionRequest, members: list[str], local_cpg: str, seq: count[int],
) -> tuple[list[ReplicationAction], list[str]]:
    primary, peer = report.primary, report.peer
    a, b = array_name(primary), array_name(peer)
    g = row.group_name
    target, mirror_config = _target_for(report.partnership, row.mode)
    existing = primary.group(g)
    peer_set = row.peer_vvset_name
    peer_set_call = None if peer_set in peer.vvsets else _vvset_call("B", peer_set, members)
    actions: list[ReplicationAction] = []
    blockers: list[str] = []
    if existing is None:
        setup, start = _group_calls(row, members, target, local_cpg, mirror_config)
        _number(seq, *setup, peer_set_call, start)
        actions.append(ReplicationAction(
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
            actions.append(ReplicationAction(kind="group", name=g, state="conflict", reason=f"exists but {diff}"))
            blockers.append(
                f"Remote Copy group '{g}' exists on {a} but {diff}. The tool never changes an existing group; "
                "remove it on the array or rename the volume set."
            )
        else:
            actions.append(ReplicationAction(
                kind="group", name=g, state="exists",
                reason=f"{existing.status}, {existing.role}, {existing.mode}, {len(existing.volumes)} volume(s)",
            ))
        _number(seq, peer_set_call)
    if peer_set_call is None:
        actions.append(ReplicationAction(
            kind="peer_vvset", name=peer_set, where="B", state="exists",
            reason=f"{len(peer.vvsets[peer_set])} member(s) on {b}",
        ))
    else:
        actions.append(ReplicationAction(
            kind="peer_vvset", name=peer_set, where="B", state="create",
            reason=f"the secondary volumes on {b}, for the DR site's exports",
            calls=[peer_set_call], detail={"members": members, "group": g},
        ))
    return actions, blockers


def _plan_notes(report: ReplicationReport, existing_groups: list[str]) -> list[str]:
    primary, peer = report.primary, report.peer
    a, b = array_name(primary), array_name(peer)
    notes: list[str] = []
    if existing_groups:
        notes.append(
            f"{len(existing_groups)} Remote Copy group(s) already on {a} are not part of this plan and will not be touched: "
            + ", ".join(existing_groups) + "."
        )
    if report.partnership:
        p = report.partnership
        legs = "; ".join(
            f"{a} → {b} via target '{t.name}' ({t.links_up}/{t.links_total} links Up), {b} → {a} via '{t.peer_name}' "
            f"({t.peer_links_up}/{t.peer_links_total} Up), policy " + ("mirror_config" if t.mirror_config else "no_mirror_config")
            + ("" if not t.modes else f", carries {t.groups} {'/'.join(t.modes)} group(s)")
            for t in p.targets
        )
        notes.append(f"Partnership {TRANSPORT_WORDS[p.transport]}: {legs}.")
        if len(p.targets) > 1 and p.target_by_mode:
            notes.append("Target per mode this run: " + ", ".join(f"{m} → '{n}'" for m, n in sorted(p.target_by_mode.items())) + ".")
    if primary.system_id is not None:
        notes.append(f"On {b} each new group will be named '<group>.r{primary.system_id}'.")
    return notes


def build_plan(report: ReplicationReport, intent: ReplicationIntent, provisioning: ProvisioningIntent) -> ReplicationPlan:
    plan = ReplicationPlan(blockers=list(report.findings), notes=list(report.notes))
    if report.error:
        plan.error = report.error
        return plan
    if report.mixed_transports:
        return plan     # SPEC-031 R3: a pair with IP and FC targets towards each other plans nothing
    primary, peer = report.primary, report.peer
    a, b = array_name(primary), array_name(peer)
    # SPEC-021 R3: the partnership rows come first; when any is to create, the groups wait for a second
    # preview (the link check needs the partnership, and the groups need the link check).
    p_actions, p_blockers, p_notes = plan_partnership(report, intent)
    plan.actions += p_actions
    plan.blockers += p_blockers
    plan.notes += p_notes
    if plan.sets_up_partnership or (intent.network and report.partnership is None):
        for seq_num, call in enumerate((c for x in p_actions for c in x.calls), start=1):
            call.seq = seq_num
        plan.notes.append(
            f"This configures the replication ports and the partnership between {a} and {b} first. "
            "The Remote Copy groups are planned after it: read both arrays again, press Check RC link, "
            "then configure the groups."
        )
        return plan

    rows, row_blockers = _resolve_protection_rows(primary, intent, provisioning)
    plan.blockers.extend(row_blockers)
    seq = count(1)
    if intent.failover_test and not intent.failover_group:
        t_actions, t_blockers, test_entry = _plan_failover_test_objects(primary, intent, provisioning, seq)
        plan.actions.extend(t_actions)
        plan.blockers.extend(t_blockers)
        rows.append(test_entry)
    for row, members, local_cpg in rows:
        g_actions, g_blockers = _plan_group_actions(report, row, members, local_cpg, seq)
        plan.actions.extend(g_actions)
        plan.blockers.extend(g_blockers)

    planned = {row.group_name for row, _, _ in rows}
    plan.existing_groups = [g.name for g in primary.groups if g.name not in planned]
    plan.notes.extend(_plan_notes(report, plan.existing_groups))
    return plan
