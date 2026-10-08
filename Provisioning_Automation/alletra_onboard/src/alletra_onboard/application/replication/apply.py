"""SPEC-016 R4 (apply) and R7 (removal set): write exactly what the approved plan says, over WSAPI,
in the fixed order — test objects, then per group: create → policies/period → admit each volume →
the peer volume set → start. Stop at the first failure; the removal set covers what was created.

Nothing here reads the plan's CLI strings: the actions carry their parameters in `detail`.
"""

from __future__ import annotations

from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_wsapi
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    ReplicationAction,
    ReplicationOutcome,
    ReplicationPlan,
    ReplicationResult,
)


def _group_actions(plan: ReplicationPlan) -> list[ReplicationAction]:
    # Protection rows first, the failover test's own group last (it depends on the test objects).
    groups = [a for a in plan.actions if a.kind == "group" and a.state == "create"]
    return sorted(groups, key=lambda a: bool(a.detail.get("is_test")))


def _peer_set_action(plan: ReplicationPlan, group: str) -> ReplicationAction | None:
    return next((a for a in plan.actions if a.kind == "peer_vvset" and a.state == "create" and a.detail.get("group") == group), None)


def apply_plan(
    plan: ReplicationPlan, provisioning: ProvisioningIntent, *, wsapi_factory: Callable = make_wsapi,
    progress: Callable[[str], None] | None = None,
) -> ReplicationResult:
    result = ReplicationResult()
    if plan.error or plan.blockers:
        result.error = plan.error or "the plan has blocking findings; nothing was applied"
        return result
    intent = provisioning.replication
    if intent is None:
        result.error = "this run has no Replication tab"
        return result

    def _p(message: str) -> None:
        if progress:
            progress(message)

    def record(kind, name, where, status, detail="") -> ReplicationOutcome:
        o = ReplicationOutcome(kind=kind, name=name, where=where, status=status, detail=detail)
        result.outcomes.append(o)
        return o

    # R7 paste order on A: every group (stop, dismiss its volumes, remove), then the test set, then
    # the test volume — a volume cannot go while a group or a set still holds it.
    group_lines: list[str] = []
    test_set_lines: list[str] = []
    test_vol_lines: list[str] = []

    def compose_removals() -> None:
        result.removals_a = [*group_lines, *test_set_lines, *test_vol_lines]

    try:
        with wsapi_factory(provisioning.array) as a, wsapi_factory(intent.peer) as b:
            # 1. the failover test's own volume and set, through the same calls provisioning uses
            for action in (x for x in plan.actions if x.kind == "test_volume" and x.state == "create"):
                _p(f"Creating {action.name} on A…")
                status = a.ensure_volume(action.name, action.detail["cpg"], int(action.detail["size_gib"]) * 1024, "tpvv")
                record("test_volume", action.name, "A", status, f"{action.detail['size_gib']} GiB tpvv on {action.detail['cpg']}")
                if status == "created":
                    test_vol_lines.append(f"removevv -f {action.name}")
            for action in (x for x in plan.actions if x.kind == "test_vvset" and x.state == "create"):
                status = a.ensure_volume_set(action.name, list(action.detail["members"]))
                record("test_vvset", action.name, "A", "created" if status in ("created", "updated") else status,
                       f"{len(action.detail['members'])} member(s)")
                if status == "created":
                    test_set_lines.append(f"removevvset -f {action.name}")

            # 2. each group, in R4 order
            for action in _group_actions(plan):
                d = action.detail
                g, target = action.name, d["target"]
                _p(f"Creating Remote Copy group {g} on A…")
                status = a.create_remote_copy_group(g, target=target, mode=d["mode"], peer_cpg=d["peer_cpg"], local_cpg=d.get("local_cpg", ""))
                record("group", g, "A", status, f"{d['mode']} → {target}" + (f", period {d['period_seconds']} s" if d.get("period_seconds") else ""))
                created_group = status == "created"
                if created_group:
                    result.groups_created.append(g)
                    group_lines.append(f"stoprcopygroup -f {g}")
                    group_lines.append(f"removercopygroup -f {g}")
                compose_removals()
                note = a.set_remote_copy_group(
                    g, target=target, period_seconds=d.get("period_seconds"),
                    auto_recover=bool(d.get("auto_recover", True)), auto_synchronize=bool(d.get("auto_synchronize", True)),
                )
                record("policy", g, "A", "created", "auto_recover=" + str(d.get("auto_recover", True)).lower()
                       + ", auto_synchronize=" + str(d.get("auto_synchronize", True)).lower()
                       + (f", period {d['period_seconds']} s" if d.get("period_seconds") else ""))
                if note:
                    result.notes.append(note)
                for volume in d["volumes"]:
                    _p(f"Admitting {volume} to {g} (secondary auto-created on B)…")
                    status = a.admit_remote_copy_volume(g, volume, target=target)
                    record("volume_admit", volume, "A", status, f"→ {g}, secondary {volume} on {d['peer_cpg']}")
                    if status == "created" and created_group:
                        # between this group's stop and remove lines
                        group_lines.insert(group_lines.index(f"removercopygroup -f {g}"), f"dismissrcopyvv -f -removevv {volume} {g}")
                        compose_removals()
                peer_set = _peer_set_action(plan, g)
                if peer_set is not None:
                    _p(f"Creating volume set {peer_set.name} on B…")
                    status = b.ensure_volume_set(peer_set.name, list(peer_set.detail["members"]))
                    record("peer_vvset", peer_set.name, "B", "created" if status in ("created", "updated") else status,
                           f"{len(peer_set.detail['members'])} member(s)")
                    if status == "created":
                        result.removals_b.append(f"removevvset -f {peer_set.name}")
                _p(f"Starting {g}…")
                starter = b if d.get("start_where") == "B" else a
                status = starter.start_remote_copy_group(g)
                record("start", g, d.get("start_where", "A"), "created" if status == "started" else status,
                       "started" if status == "started" else "was already started")
    except Exception as exc:  # noqa: BLE001 - the array's message, where it stopped, what was created
        done = [o for o in result.outcomes if o.status == "created"]
        result.error = (f"Stopped after {len(done)} write(s): {exc} The removal set below undoes exactly what "
                        "was created before the failure.")
        record("group", "—", "A", "failed", str(exc))
    compose_removals()
    return result
