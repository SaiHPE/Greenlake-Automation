"""SPEC-016 R6 — verify, read-only, on both arrays: links Up, each planned group Started with the
right role on each side and its volumes Synced. Vocabulary from the Remote Copy troubleshooting
guide (ED6): Status Started/Stopped/Failsafe · Role Primary/Secondary/-Rev · SyncStatus
Synced/Syncing/Stopped/Stale. The tool never retries a write here — it reports and names HPE's step.

BL-64 (the owner, 2026-11-19): each group's settings and every volume in it, read with `showrcopy -d
groups <group>` on this array, travel with the verdict (`GroupVerification.config`). They are shown,
never judged: the verdict still comes from `showrcopy` on both arrays.
"""

from __future__ import annotations

from collections.abc import Callable

from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.plan_check import find_partnership
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    GroupVerification,
    RcGroup,
    RcGroupDetail,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
    ReplicationVerification,
)

#: HPE's documented next step per observed state (troubleshooting guide ED6).
_NEXT_STEP = {
    "stopped": "Start the group (`startrcopygroup <group>`); if it stops again, check the links and the target's status.",
    "stale": "A Stale volume needs a full resynchronisation; if it persists after a start, contact HPE Support.",
    "failsafe": "The group is in Failsafe: I/O is blocked on the primary. Follow HPE's disaster recovery procedure (recover or restore).",
    "missing_peer": "The peer has no group of that name: the start did not mirror. Check `showrcopy groups` on the peer.",
    "role": "Roles are not Primary here / Secondary on the peer: a failover or reverse has happened. Check the roles on both arrays (`showrcopy groups`) before going on.",
}


def peer_group_name(group: str, primary: ReplicationArrayView) -> str:
    return f"{group}.r{primary.system_id}" if primary.system_id is not None else group


def _judge(group: str, a_group: RcGroup | None, b_group: RcGroup | None, expected_mode: str, expected_period: int | None) -> GroupVerification:
    peer = b_group.name if b_group else ""
    v = GroupVerification(group=group, peer_group=peer)
    if a_group is None:
        v.detail, v.next_step = "not on this array", "The group was not created; apply again from a fresh plan."
        return v
    v.volumes_total = len(a_group.volumes)
    v.volumes_synced = sum(1 for x in a_group.volumes if x.sync_status.lower() == "synced")
    statuses = {x.sync_status.lower() for x in a_group.volumes}
    status = a_group.status.lower()
    bits = [f"{a_group.status}", f"{a_group.role} here" + (f", {b_group.role} on the peer" if b_group else ""), a_group.mode]
    if expected_mode and a_group.mode_key != expected_mode:
        bits.append(f"expected {expected_mode}")
    if status == "failsafe":
        v.detail, v.next_step = " · ".join(bits), _NEXT_STEP["failsafe"]
        return v
    if status != "started":
        v.detail, v.next_step = " · ".join(bits), _NEXT_STEP["stopped"]
        return v
    if a_group.role != "Primary" or (b_group is not None and b_group.role != "Secondary"):
        v.detail, v.next_step = " · ".join(bits), _NEXT_STEP["role"]
        return v
    if b_group is None:
        v.detail, v.next_step = " · ".join(bits) + " · not found on the peer", _NEXT_STEP["missing_peer"]
        return v
    if "stale" in statuses:
        v.detail, v.next_step = " · ".join(bits) + f" · {v.volumes_synced}/{v.volumes_total} synced, some Stale", _NEXT_STEP["stale"]
        return v
    if v.volumes_synced == v.volumes_total and v.volumes_total > 0:
        v.verdict = "replicating"
        last = next((x.last_sync for x in a_group.volumes if x.last_sync and x.last_sync != "NA"), "")
        v.detail = " · ".join(bits) + f" · {v.volumes_total} volume(s) Synced" + (f" · last sync {last}" if last else "")
        return v
    if "syncing" in statuses or "notsynced" in statuses or "new" in statuses:
        v.verdict = "syncing"
        v.detail = " · ".join(bits) + f" · initial sync in progress ({v.volumes_synced} of {v.volumes_total} volumes Synced)"
        return v
    v.detail = " · ".join(bits) + f" · volumes: {', '.join(sorted(statuses)) or 'none'}"
    v.next_step = _NEXT_STEP["stopped"]
    return v


def _rpo_minutes(action, intent) -> int | None:
    """The workbook's RPO for a periodic group: its volume set's row, else twice the planned period
    (the tool's own test group copies the first row's mode and period)."""
    if action.detail.get("mode") == "sync":
        return None
    row = next((r for r in intent.protections if r.vvset == action.detail.get("vvset")), None)
    if row is not None and row.rpo_minutes:
        return row.rpo_minutes
    period = action.detail.get("period_seconds")
    return period * 2 // 60 if period else None


def _verify_links(
    a: ReplicationArrayView, b: ReplicationArrayView, plan: ReplicationPlan,
) -> tuple[bool, str]:
    p = find_partnership(a, b)
    if p is None:
        return False, "no partnership found between the two arrays"
    used = {x.detail.get("target") for x in plan.actions if x.kind == "group"} - {None, ""}
    targets = [t for t in p.targets if t.name in used] or p.targets
    links_ok = all(t.links_up >= 2 and t.peer_links_up >= 2 for t in targets)
    links_detail = " · ".join(
        f"{a.name} → {b.name} via '{t.name}' {t.links_up}/{t.links_total} links Up · "
        f"{b.name} → {a.name} via '{t.peer_name}' {t.peer_links_up}/{t.peer_links_total} links Up"
        for t in targets
    )
    return links_ok, links_detail


def _verify_groups(
    group_actions: list[ReplicationAction], a: ReplicationArrayView, b: ReplicationArrayView,
) -> list[GroupVerification]:
    groups: list[GroupVerification] = []
    for action in group_actions:
        g = action.name
        expected_mode = action.detail.get("mode", "")
        expected_period = action.detail.get("period_seconds")
        a_group = a.group(g)
        b_group = b.group(peer_group_name(g, a))
        v = _judge(g, a_group, b_group, expected_mode, expected_period)
        peer_set = action.detail.get("peer_vvset")
        if v.verdict == "replicating" and peer_set and a_group is not None:
            members = b.vvsets.get(peer_set)
            if members is None:
                v.detail += f" · peer set {peer_set} missing"
            elif len(members) != len(a_group.volumes):
                v.detail += f" · peer set {peer_set} has {len(members)} of {len(a_group.volumes)} volumes"
        groups.append(v)
    return groups


def _attach_group_details(
    out: ReplicationVerification,
    group_actions: list[ReplicationAction],
    intent: ReplicationIntent,
    details: dict[str, RcGroupDetail],
    errors: dict[str, str],
) -> None:
    rpo = {x.name: _rpo_minutes(x, intent) for x in group_actions}
    for v in out.groups:
        config = details.get(v.group)
        if config is not None:
            v.config = config.model_copy(update={"rpo_minutes": rpo.get(v.group)})
        elif v.group in errors:
            out.notes.append(f"The settings and volumes of {v.group} could not be read (showrcopy -d): {errors[v.group]}")


def _rcp_note(vvsets: dict[str, list[str]]) -> str | None:
    rcp = [s for s in vvsets if s.startswith("RCP_")]
    if not rcp:
        return None
    return (
        "The array keeps its own VV set per group (" + ", ".join(sorted(rcp)[:6]) + ("…" if len(rcp) > 6 else "")
        + "); expected, and removed with the group."
    )


def verify(
    provisioning: ProvisioningIntent, plan: ReplicationPlan, *,
    read_fn: Callable = replication_read.read_array, detail_fn: Callable | None = None,
    progress: Callable[[str], None] | None = None,
) -> ReplicationVerification:
    """`detail_fn` (`replication_read.read_group_details` in the step) reads each group's `showrcopy -d`
    on this array; without it the groups carry no `config`."""
    out = ReplicationVerification()
    intent = provisioning.replication
    if intent is None:
        out.error = "this run has no Replication tab"
        return out
    a = read_fn(provisioning.array, progress=progress)
    b = read_fn(intent.peer, progress=progress)
    if a.read_error or b.read_error:
        out.error = a.read_error or b.read_error
        return out
    out.links_ok, out.links_detail = _verify_links(a, b, plan)
    group_actions = [x for x in plan.actions if x.kind == "group" and x.state in ("create", "exists")]
    out.groups = _verify_groups(group_actions, a, b)
    present = [v.group for v in out.groups if a.group(v.group) is not None]
    if detail_fn is not None and present:
        details, errors = detail_fn(provisioning.array, present, progress=progress)
        _attach_group_details(out, group_actions, intent, details, errors)
    if note := _rcp_note(a.vvsets):
        out.notes.append(note)
    return out
