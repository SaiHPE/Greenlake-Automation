"""SPEC-016 R6 — verify, read-only, on both arrays: links Up, each planned group Started with the
right role on each side and its volumes Synced. Vocabulary from the Remote Copy troubleshooting
guide (ED6): Status Started/Stopped/Failsafe · Role Primary/Secondary/-Rev · SyncStatus
Synced/Syncing/Stopped/Stale. The tool never retries a write here — it reports and names HPE's step.
"""

from __future__ import annotations

from collections.abc import Callable

from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.plan import find_partnership
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    GroupVerification,
    RcGroup,
    ReplicationArrayView,
    ReplicationPlan,
    ReplicationVerification,
)

#: HPE's documented next step per observed state (troubleshooting guide ED6).
_NEXT_STEP = {
    "stopped": "Start the group (`startrcopygroup <group>`); if it stops again, check the links and the target's status.",
    "stale": "A Stale volume needs a full resynchronisation; if it persists after a start, contact HPE Support.",
    "failsafe": "The group is in Failsafe: I/O is blocked on the primary. Follow the DR procedure (recover or restore) — see SPEC-017.",
    "missing_peer": "The peer has no group of that name: the start did not mirror. Check `showrcopy groups` on the peer.",
    "role": "Roles are not Primary here / Secondary on the peer: a failover or reverse has happened. See the DR role table (SPEC-017).",
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


def verify(
    provisioning: ProvisioningIntent, plan: ReplicationPlan, *,
    read_fn: Callable = replication_read.read_array, progress: Callable[[str], None] | None = None,
) -> ReplicationVerification:
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
    p = find_partnership(a, b)
    if p is None:
        out.links_detail = "no partnership found between the two arrays"
    else:
        used = {x.detail.get("target") for x in plan.actions if x.kind == "group"} - {None, ""}
        targets = [t for t in p.targets if t.name in used] or p.targets
        out.links_ok = all(t.links_up >= 2 and t.peer_links_up >= 2 for t in targets)
        out.links_detail = " · ".join(
            f"{a.name} → {b.name} via '{t.name}' {t.links_up}/{t.links_total} links Up · "
            f"{b.name} → {a.name} via '{t.peer_name}' {t.peer_links_up}/{t.peer_links_total} links Up"
            for t in targets)
    for action in (x for x in plan.actions if x.kind == "group" and x.state in ("create", "exists")):
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
        out.groups.append(v)
    rcp = [s for s in a.vvsets if s.startswith("RCP_")]
    if rcp:
        out.notes.append("The array keeps its own VV set per group (" + ", ".join(sorted(rcp)[:6]) + ("…" if len(rcp) > 6 else "")
                         + "); expected, and removed with the group.")
    return out
