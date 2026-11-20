"""SPEC-023 R5 (apply) and R6 (removal set): write exactly what the approved plan says, in its order
(every snapshot now over WSAPI, then every schedule), read the array back after each write, and stop
at the first refusal or at a read-back that does not show the change.

The removal set names only what this apply made. A snapshot is found by diff and name: a volume
present after the write and not before, `copyOf` one of the row's members, named `<member>.initial`;
never by `copyOf` alone (Remote Copy makes snapshots of the same members) and never by the planned
name alone. A schedule's `removesched -f <name>` goes in before `createsched` is sent (ADR 0025
condition 4) and comes out only when the array, read after a failure, does not hold that schedule.

Schedules go over SSH through `ArraySnapCliClient` (ADR 0016), built here, after the server checked
the approval, with this plan's (schedule name, source) pairs and nothing else.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from alletra_onboard.application.runs.apply_record import maybe_made, recorded_write
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.application.snapshots.clients import make_snap_writer
from alletra_onboard.application.snapshots.read import parse_showsched, showsched_readable
from alletra_onboard.application.snapshots.verify import check_now
from alletra_onboard.domain.approval import Approval, SaveRecord
from alletra_onboard.domain.array_parse import answered_error
from alletra_onboard.domain.errors import ApplyRecordError, ArrayCliError, DeviceError, WsapiError
from alletra_onboard.domain.plan_objects import SnapPlanObjects
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import REMOVAL_ORDER, ArrayVolumeRecord, RemovalItem
from alletra_onboard.domain.snapshots import (
    NOW_SUFFIX,
    ArraySchedule,
    SnapshotAction,
    SnapshotArrayView,
    SnapshotIntent,
    SnapshotOutcome,
    SnapshotPlan,
    SnapshotRequest,
    SnapshotResult,
    now_snapshot_name,
    same_command,
    same_cron,
)


def made_by(action: SnapshotAction, before: set[str], after: list[ArrayVolumeRecord]) -> list[str]:
    """The snapshots one snapshot-now write made: new since `before`, a copy of a member it was asked
    for, under the name asked for."""
    return [v.name for v in after if v.name not in before and v.copy_of in action.members
            and v.name == now_snapshot_name(v.copy_of)]


def plan_objects(plan: SnapshotPlan, intent: SnapshotIntent) -> SnapPlanObjects:
    """ADR 0025 condition 3: the (schedule name, source) pairs the approved plan creates. The schedule
    client is built with them and refuses every other schedule. A conflict or an exists row adds nothing."""
    creating = {a.name for a in plan.actions if a.kind == "schedule" and a.state == "create"}
    return SnapPlanObjects(schedules=frozenset(
        (r.name, r.source_ref) for r in intent.requests if r.has_schedule and r.name in creating))


def schedule_readback(request: SnapshotRequest, before: list[ArraySchedule], after: list[ArraySchedule]) -> str:
    """ADR 0025 condition 5: "" when the schedule is there, active, with the planned command and cron, and
    every schedule that was there before is as it was; else what is wrong."""
    mine = next((s for s in after if s.name == request.name), None)
    if mine is None:
        return f"after createsched, showsched does not list {request.name}"
    if mine.status.lower() != "active":
        return f"after createsched, {request.name} is {mine.status}, not active"
    if not same_command(mine.command, request.createsv_command()) or not same_cron(mine.cron, request.cron):
        return f"after createsched, {request.name} runs '{mine.command}' at '{mine.cron}', not what was planned"
    now = {s.name: s for s in after}
    for old in before:
        new = now.get(old.name)
        if (new is None or not same_command(new.command, old.command) or not same_cron(new.cron, old.cron)
                or new.status != old.status):
            return f"after createsched, the schedule {old.name} that was on the array before is not as it was"
    return ""


def _whole_set(wsapi, request: SnapshotRequest, action: SnapshotAction, view: SnapshotArrayView) -> bool:
    """One call for the set (one point in time) when every member lacks its snapshot, as the plan judged
    from the same read; each missing member on its own otherwise. Before taking a whole-set snapshot,
    re-read live membership and refuse if it differs from the reviewed members."""
    if request.kind != "set" or sorted(action.members) != sorted(view.vvsets.get(request.source, [])):
        return False
    live = wsapi.volume_sets().get(request.source)
    if live is None or sorted(live) != sorted(action.members):
        raise WsapiError(
            f"volume set {request.source} changed on the array since the preview — no snapshot of it was taken. "
            "Read the array again and approve the new plan"
        )
    return True


@dataclass
class _SnapState:
    result: SnapshotResult
    save: SaveRecord
    say: Callable[[str], None]
    in_flight: tuple[SnapshotAction, set[str]] | None = None
    current: SnapshotAction | None = None
    pending_notes: list[str] = field(default_factory=list)
    written: int = 0

    def record(self, action: SnapshotAction, status: str, detail: str = "") -> None:
        self.result.outcomes.append(SnapshotOutcome(kind=action.kind, name=action.name, source=action.source,
                                                    status=status, detail=detail))  # type: ignore[arg-type]

    def remove(self, names: list[str]) -> None:
        seen = {r.name for r in self.result.removals}
        self.result.removals.extend(RemovalItem(kind="snapshot", name=n, command=f"removevv -f {n}")
                                    for n in names if n not in seen)
        self.result.removals.sort(key=lambda i: REMOVAL_ORDER.get(i.kind, 9))

    def clear_pending(self) -> None:
        for note in self.pending_notes:
            if note in self.result.removal_notes:
                self.result.removal_notes.remove(note)
        self.pending_notes.clear()


def _snap_note(source: str, members: list[str]) -> str:
    names = " ".join(now_snapshot_name(m) for m in members)
    return (f"The array may have made snapshots of {source} before the error. Inspect with `showvv {names}` first; "
            "remove with `removevv -f` each one that was not there before this run.")


def _apply_snapshot_action(
    wsapi, action: SnapshotAction, request: SnapshotRequest, view: SnapshotArrayView, st: _SnapState,
) -> None:
    st.current = action
    whole = _whole_set(wsapi, request, action, view)
    before = {v.name for v in wsapi.volumes()}
    st.in_flight = (action, before)
    st.pending_notes = []
    if whole:
        st.say(f"Taking a snapshot of every volume in {request.source} ({len(action.members)})…")
        note = _snap_note(request.source, action.members)
        st.pending_notes.append(note)
        st.result.removal_notes.append(note)
        st.save(st.result)
        wsapi.create_set_snapshot(request.source, f"@vvname@{NOW_SUFFIX}", read_only=request.read_only,
                                  expire_hours=request.expire_hours)
        st.written += 1
    else:
        for member in action.members:
            st.say(f"Taking a snapshot of {member}…")
            note = _snap_note(member, [member])
            st.pending_notes.append(note)
            st.result.removal_notes.append(note)
            st.save(st.result)
            wsapi.create_snapshot(member, now_snapshot_name(member), read_only=request.read_only,
                                  expire_hours=request.expire_hours)
            st.written += 1
    # One read-back per row, as on main; clear the inspect-first note(s) once the diff settles removals.
    after = wsapi.volumes()
    st.in_flight = None
    st.remove(made_by(action, before, after))
    st.clear_pending()
    st.save(st.result)
    ok, detail = check_now(request, action.members, view.model_copy(update={"volumes": after}))
    if not ok:
        raise WsapiError(f"after the snapshot of {request.source}, the array does not show what was asked: {detail}")
    st.record(action, "created", detail)
    st.save(st.result)


def _apply_schedule_action(cli, action: SnapshotAction, request: SnapshotRequest, st: _SnapState) -> None:
    st.current = action
    before = _read_schedules(cli, f"before creating {request.name}")
    if any(s.name == request.name for s in before):
        raise ArrayCliError(f"a schedule named {request.name} is on the array now and was not when the "
                            "plan was read; nothing was written for it. Read the array again")
    st.say(f"Creating the schedule {request.name}…")
    line = RemovalItem(kind="schedule", name=request.name, command=f"removesched -f {request.name}")
    note = maybe_made(f"schedule {request.name}", "showsched", f"removesched -f {request.name}")
    with recorded_write(st.result, note, st.save):
        try:
            out = cli.write(request.createsched_command())
            st.written += 1
            if answered_error(out):
                said = next(ln.strip() for ln in out.splitlines() if ln.strip().lower().startswith("error"))
                raise ArrayCliError(f"the array refused createsched for {request.name}: {said}")
            after = _read_schedules(cli, f"after creating {request.name}")
            if problem := schedule_readback(request, before, after):
                raise ArrayCliError(problem)
        except Exception:
            st.result.removals.append(line)
            _schedule_after_failure(action, line, cli, st.result)   # while the session is still open
            if note in st.result.removal_notes:
                st.result.removal_notes.remove(note)
            raise
        st.result.removals.append(line)
        st.result.removals.sort(key=lambda i: REMOVAL_ORDER.get(i.kind, 9))
        st.result.schedules_created.append(request.name)
        st.record(action, "created", f"{request.schedule_words()}; active, next run "
                  + next(s.next_run for s in after if s.name == request.name))
        st.result.removal_notes.append(
            f"Snapshots the schedule {request.name} takes expire on their own after {request.expire_hours} "
            "hours. To remove them sooner, remove each with removevv -f.")


def apply_plan(
    plan: SnapshotPlan, view: SnapshotArrayView, provisioning: ProvisioningIntent, approval: Approval, *,
    wsapi_factory: Callable = make_wsapi_writer, snap_cli_factory: Callable = make_snap_writer,
    progress: Callable[[str], None] | None = None,
) -> SnapshotResult:
    """`view` is the read the plan was built from (LESSONS 37)."""
    result = SnapshotResult(started_at=datetime.now(UTC).isoformat())
    intent = provisioning.snapshots
    if intent is None:
        result.error = "this run has no Snapshots tab"
        return result
    if plan.error or plan.blockers:
        result.error = plan.error or "the plan has blocking findings; nothing was applied"
        return result
    by_source = {r.source: r for r in intent.requests}
    result.outcomes = [SnapshotOutcome(kind=a.kind, name=a.name, source=a.source, status="exists", detail=a.reason)
                       for a in plan.actions if a.state == "exists"]
    snapshots = [a for a in plan.actions if a.kind == "snapshot" and a.state == "create"]
    schedules = [a for a in plan.actions if a.kind == "schedule" and a.state == "create"]
    st = _SnapState(result=result, save=approval.require_saver(), say=progress or (lambda _m: None))
    try:
        if snapshots:
            with wsapi_factory(approval, "snapshots", "A") as wsapi:
                for action in snapshots:
                    _apply_snapshot_action(wsapi, action, by_source[action.source], view, st)
        if schedules:
            st.current = schedules[0]
            with snap_cli_factory(approval, plan_objects(plan, intent)) as cli:
                for action in schedules:
                    _apply_schedule_action(cli, action, by_source[action.source], st)
    except (DeviceError, ApplyRecordError) as exc:  # the array's words, where it stopped, what to remove
        if st.in_flight is not None:
            _diff_after_failure(st.in_flight, approval, wsapi_factory, result, st.remove)
            st.clear_pending()
        done = sum(1 for o in result.outcomes if o.status == "created")
        result.error = (f"Stopped after {done} row(s) and {st.written} write(s): {str(exc).rstrip('.')}. The removal set "
                        "below undoes exactly what was created before the failure.")
        if st.current is not None and all(o.name != st.current.name or o.kind != st.current.kind for o in result.outcomes):
            st.record(st.current, "failed", str(exc))
    result.removals.sort(key=lambda i: REMOVAL_ORDER.get(i.kind, 9))
    return result


def _read_schedules(cli, when: str) -> list[ArraySchedule]:
    """`showsched` as a read that must succeed: an answer that is not its table is an error, never "none"."""
    text = cli.run("showsched")
    if not showsched_readable(text):
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "nothing")
        raise ArrayCliError(f"showsched could not be read {when}; it answered: {first}")
    return parse_showsched(text)


def _schedule_after_failure(action: SnapshotAction, line: RemovalItem, cli, result: SnapshotResult) -> None:
    """The createsched or its read-back failed: keep the removal line unless the array, read once more
    and read well, shows the schedule was not made."""
    try:
        names = {s.name for s in _read_schedules(cli, f"after {action.name} failed")}
    except DeviceError:  # the line stays, with a note to check by hand
        result.removal_notes.append(f"The array was not read after the schedule {action.name} failed. Check with "
                                    f"showsched {action.name}; if it is not there, skip its removesched line.")
        return
    if action.name not in names and line in result.removals:
        result.removals.remove(line)


def _diff_after_failure(in_flight: tuple[SnapshotAction, set[str]], approval: Approval,
                        wsapi_factory: Callable, result: SnapshotResult, remove: Callable[[list[str]], None]) -> None:
    """A write that failed, or whose read-back failed, may still have made snapshots: read once more and
    name what the diff shows. When even that read fails, say which names to check by hand."""
    action, before = in_flight
    try:
        with wsapi_factory(approval, "snapshots", "A") as wsapi:
            remove(made_by(action, before, wsapi.volumes()))
    except DeviceError:  # the note below stands in for the read that failed
        names = " ".join(now_snapshot_name(m) for m in action.members)
        result.removal_notes.append(
            f"The array was not read after the snapshot of {action.source} failed. Check with showvv {names}; "
            "remove with removevv -f each one that was not there before this run.")
