"""SPEC-016 R4 (apply) and R7 (removal set): write exactly what the approved plan says, over WSAPI,
in the fixed order — test objects, then per group: create → policies/period → admit each volume →
the peer volume set → start. Stop at the first failure; the removal set covers what was created.

Nothing here reads the plan's CLI strings: the actions carry their parameters in `detail`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from alletra_onboard.application.runs.apply_record import maybe_made, recorded_write
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.domain.approval import Approval, SaveRecord
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    ReplicationAction,
    ReplicationOutcome,
    ReplicationPlan,
    ReplicationResult,
)

if TYPE_CHECKING:
    from alletra_onboard.application.runs.writer_clients import WsapiWriter


def _group_actions(plan: ReplicationPlan) -> list[ReplicationAction]:
    # Protection rows first, the failover test's own group last (it depends on the test objects).
    groups = [a for a in plan.actions if a.kind == "group" and a.state == "create"]
    return sorted(groups, key=lambda a: bool(a.detail.get("is_test")))


def _peer_set_action(plan: ReplicationPlan, group: str) -> ReplicationAction | None:
    return next((a for a in plan.actions if a.kind == "peer_vvset" and a.state == "create" and a.detail.get("group") == group), None)


@dataclass
class _RcState:
    a: WsapiWriter
    b: WsapiWriter
    result: ReplicationResult
    save: SaveRecord
    progress: Callable[[str], None] | None
    # R7 paste order on A: every group (stop, dismiss its volumes, remove), then the test set, then
    # the test volume — a volume cannot go while a group or a set still holds it.
    group_lines: list[str] = field(default_factory=list)
    test_set_lines: list[str] = field(default_factory=list)
    test_vol_lines: list[str] = field(default_factory=list)
    # On B, after A: the peer volume sets, then the secondaries the admits auto-created. A Primera
    # (OS 4.6.20, live 2026-11-03) keeps a secondary that is in a set when A's `dismissrcopyvv
    # -removevv` asks it to delete it ("Manual cleanup required on target system").
    peer_set_lines: list[str] = field(default_factory=list)
    secondary_lines: list[str] = field(default_factory=list)

    def say(self, message: str) -> None:
        if self.progress:
            self.progress(message)

    def record(self, kind, name, where, status, detail="") -> ReplicationOutcome:
        o = ReplicationOutcome(kind=kind, name=name, where=where, status=status, detail=detail)
        self.result.outcomes.append(o)
        return o

    def compose(self) -> None:
        self.result.removals_a = [*self.group_lines, *self.test_set_lines, *self.test_vol_lines]
        self.result.removals_b = [*self.peer_set_lines, *self.secondary_lines]


def _apply_test_objects(plan: ReplicationPlan, st: _RcState) -> None:
    for action in (x for x in plan.actions if x.kind == "test_volume" and x.state == "create"):
        st.say(f"Creating {action.name} on A…")
        note = maybe_made(f"volume {action.name} on A", f"showvv {action.name}", f"removevv -f {action.name}")
        with recorded_write(st.result, note, st.save):
            status = st.a.ensure_volume(action.name, action.detail["cpg"], int(action.detail["size_gib"]) * 1024, "tpvv")
            st.record("test_volume", action.name, "A", status, f"{action.detail['size_gib']} GiB tpvv on {action.detail['cpg']}")
            if status == "created":
                st.test_vol_lines.append(f"removevv -f {action.name}")
                st.compose()
    for action in (x for x in plan.actions if x.kind == "test_vvset" and x.state == "create"):
        note = maybe_made(f"volume set {action.name} on A", f"showvvset {action.name}", f"removevvset -f {action.name}")
        with recorded_write(st.result, note, st.save):
            status = st.a.ensure_volume_set(action.name, list(action.detail["members"]))
            st.record("test_vvset", action.name, "A", "created" if status in ("created", "updated") else status,
                      f"{len(action.detail['members'])} member(s)")
            if status == "created":
                st.test_set_lines.append(f"removevvset -f {action.name}")
                st.compose()


def _apply_peer_set_and_start(plan: ReplicationPlan, action: ReplicationAction, st: _RcState) -> None:
    g, d = action.name, action.detail
    peer_set = _peer_set_action(plan, g)
    if peer_set is not None:
        st.say(f"Creating volume set {peer_set.name} on B…")
        note = maybe_made(f"volume set {peer_set.name} on B", f"showvvset {peer_set.name}", f"removevvset -f {peer_set.name}")
        with recorded_write(st.result, note, st.save):
            status = st.b.ensure_volume_set(peer_set.name, list(peer_set.detail["members"]))
            st.record("peer_vvset", peer_set.name, "B", "created" if status in ("created", "updated") else status,
                      f"{len(peer_set.detail['members'])} member(s)")
            if status == "created":
                st.peer_set_lines.append(f"removevvset -f {peer_set.name}")
                st.compose()
    st.say(f"Starting {g}…")
    starter = st.b if d.get("start_where") == "B" else st.a
    with recorded_write(st.result, maybe_made(f"Remote Copy group {g}", f"showrcopy groups {g}"), st.save):
        status = starter.start_remote_copy_group(g)
        st.record("start", g, d.get("start_where", "A"), "created" if status == "started" else status,
                  "started" if status == "started" else "was already started")


def _apply_group(plan: ReplicationPlan, action: ReplicationAction, st: _RcState) -> None:
    d = action.detail
    g, target = action.name, d["target"]
    st.say(f"Creating Remote Copy group {g} on A…")
    group_note = (f"The array may have made Remote Copy group {g} on A before the error. If `showrcopy groups {g}` "
                  f"lists it and it was not there before this run, `stoprcopygroup -f {g}` then "
                  f"`removercopygroup -f {g}` removes it.")
    with recorded_write(st.result, group_note, st.save):
        status = st.a.create_remote_copy_group(g, target=target, mode=d["mode"], peer_cpg=d["peer_cpg"],
                                               local_cpg=d.get("local_cpg", ""))
        period_text = f", period {d['period_seconds']} s" if d.get("period_seconds") else ""
        st.record("group", g, "A", status, f"{d['mode']} → {target}{period_text}")
        created_group = status == "created"
        if created_group:
            st.result.groups_created.append(g)
            st.group_lines.extend([f"stoprcopygroup -f {g}", f"removercopygroup -f {g}"])
            st.compose()
    with recorded_write(st.result, maybe_made(f"policies on Remote Copy group {g}", f"showrcopy -d groups {g}"), st.save):
        api_note = st.a.set_remote_copy_group(
            g, target=target, period_seconds=d.get("period_seconds"),
            auto_recover=bool(d.get("auto_recover", True)), auto_synchronize=bool(d.get("auto_synchronize", True)),
        )
        st.record("policy", g, "A", "created", "auto_recover=" + str(d.get("auto_recover", True)).lower()
                  + ", auto_synchronize=" + str(d.get("auto_synchronize", True)).lower() + period_text)
        if api_note:
            st.result.notes.append(api_note)
    for volume in d["volumes"]:
        st.say(f"Admitting {volume} to {g} (secondary auto-created on B)…")
        admit_note = (f"The array may have admitted {volume} into {g} (and auto-created its secondary on B) before the "
                      f"error. Inspect with `showrcopy groups {g}` on A and `showvv {volume}` on B first.")
        with recorded_write(st.result, admit_note, st.save):
            status = st.a.admit_remote_copy_volume(g, volume, target=target)
            st.record("volume_admit", volume, "A", status, f"→ {g}, secondary {volume} on {d['peer_cpg']}")
            if status == "created" and created_group:
                # between this group's stop and remove lines
                st.group_lines.insert(st.group_lines.index(f"removercopygroup -f {g}"),
                                      f"dismissrcopyvv -f -removevv {volume} {g}")
                # the admit auto-created the secondary on B under the same name
                st.secondary_lines.append(f"removevv -f {volume}")
                st.compose()
    _apply_peer_set_and_start(plan, action, st)


def apply_plan(
    plan: ReplicationPlan, provisioning: ProvisioningIntent, approval: Approval, *,
    wsapi_factory: Callable = make_wsapi_writer, progress: Callable[[str], None] | None = None,
) -> ReplicationResult:
    result = ReplicationResult()
    if plan.error or plan.blockers:
        result.error = plan.error or "the plan has blocking findings; nothing was applied"
        return result
    if provisioning.replication is None:
        result.error = "this run has no Replication tab"
        return result

    st: _RcState | None = None
    save = approval.require_saver()
    try:
        with wsapi_factory(approval, "rc_groups", "A") as a, wsapi_factory(approval, "rc_groups", "B") as b:
            st = _RcState(a=a, b=b, result=result, save=save, progress=progress)
            _apply_test_objects(plan, st)
            for action in _group_actions(plan):
                _apply_group(plan, action, st)
    except Exception as exc:  # the array's message, where it stopped, what was created
        done = [o for o in result.outcomes if o.status == "created"]
        result.error = (f"Stopped after {len(done)} write(s): {exc} The removal set below undoes exactly what "
                        "was created before the failure.")
        result.outcomes.append(ReplicationOutcome(kind="group", name="—", where="A", status="failed", detail=str(exc)))
    if st is not None:
        st.compose()
    return result
