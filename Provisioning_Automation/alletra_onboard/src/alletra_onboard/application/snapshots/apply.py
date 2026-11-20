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
from datetime import UTC, datetime

from alletra_onboard.application.provisioning.clients import make_snap_cli, make_wsapi
from alletra_onboard.application.snapshots.read import parse_showsched, showsched_readable
from alletra_onboard.application.snapshots.verify import check_now
from alletra_onboard.domain.array_parse import answered_error
from alletra_onboard.domain.errors import ArrayCliError
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


def _whole_set(request: SnapshotRequest, action: SnapshotAction, view: SnapshotArrayView) -> bool:
    """One call for the set (one point in time) when every member lacks its snapshot, as the plan judged
    from the same read; each missing member on its own otherwise."""
    return request.kind == "set" and sorted(action.members) == sorted(view.vvsets.get(request.source, []))


def apply_plan(
    plan: SnapshotPlan, view: SnapshotArrayView, provisioning: ProvisioningIntent, *,
    wsapi_factory: Callable = make_wsapi, snap_cli_factory: Callable = make_snap_cli,
    progress: Callable[[str], None] | None = None, clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> SnapshotResult:
    """`view` is the read the plan was built from (LESSONS 37)."""
    result = SnapshotResult(started_at=clock().isoformat())
    intent = provisioning.snapshots
    if intent is None:
        result.error = "this run has no Snapshots tab"
        return result
    if plan.error or plan.blockers:
        result.error = plan.error or "the plan has blocking findings; nothing was applied"
        return result
    by_source = {r.source: r for r in intent.requests}
    say = progress or (lambda _m: None)

    def record(action: SnapshotAction, status: str, detail: str = "") -> None:
        result.outcomes.append(SnapshotOutcome(kind=action.kind, name=action.name, source=action.source,
                                               status=status, detail=detail))  # type: ignore[arg-type]

    def remove(names: list[str]) -> None:
        for name in names:
            if all(r.name != name for r in result.removals):
                result.removals.append(RemovalItem(kind="snapshot", name=name, command=f"removevv -f {name}"))

    for action in plan.actions:
        if action.state == "exists":
            record(action, "exists", action.reason)
    snapshots = [a for a in plan.actions if a.kind == "snapshot" and a.state == "create"]
    schedules = [a for a in plan.actions if a.kind == "schedule" and a.state == "create"]
    in_flight: tuple[SnapshotAction, set[str]] | None = None
    current: SnapshotAction | None = None
    written = 0
    try:
        with wsapi_factory(provisioning.array) if snapshots else _Nothing() as wsapi:
            # (1) every snapshot now over WSAPI
            for action in snapshots:
                current = action
                request = by_source[action.source]
                before = {v.name for v in wsapi.volumes()}
                in_flight = (action, before)
                if _whole_set(request, action, view):
                    say(f"Taking a snapshot of every volume in {request.source} ({len(action.members)})…")
                    wsapi.create_set_snapshot(request.source, f"@vvname@{NOW_SUFFIX}", read_only=request.read_only,
                                              expire_hours=request.expire_hours)
                    written += 1
                else:
                    for member in action.members:
                        say(f"Taking a snapshot of {member}…")
                        wsapi.create_snapshot(member, now_snapshot_name(member), read_only=request.read_only,
                                              expire_hours=request.expire_hours)
                        written += 1
                # R5: read back after each write; the removal set is what the read shows was made
                after = wsapi.volumes()
                in_flight = None
                remove(made_by(action, before, after))
                ok, detail = check_now(request, action.members, view.model_copy(update={"volumes": after}))
                if not ok:
                    raise RuntimeError(f"after the snapshot of {request.source}, the array does not show what was asked: {detail}")
                record(action, "created", detail)
        # (2) every schedule, over the write-scoped SSH client built for this plan's schedules only
        if schedules:
            current = schedules[0]
            with snap_cli_factory(provisioning.array, plan_objects(plan, intent)) as cli:
                for action in schedules:
                    current = action
                    request = by_source[action.source]
                    before = _read_schedules(cli, f"before creating {request.name}")
                    if any(s.name == request.name for s in before):
                        raise ArrayCliError(f"a schedule named {request.name} is on the array now and was not when the "
                                            "plan was read; nothing was written for it. Read the array again")
                    say(f"Creating the schedule {request.name}…")
                    line = RemovalItem(kind="schedule", name=request.name, command=f"removesched -f {request.name}")
                    result.removals.append(line)              # ADR 0025 condition 4: before the command is sent
                    try:
                        out = cli.write(request.createsched_command())
                        written += 1
                        if answered_error(out):
                            said = next(ln.strip() for ln in out.splitlines() if ln.strip().lower().startswith("error"))
                            raise ArrayCliError(f"the array refused createsched for {request.name}: {said}")
                        after = _read_schedules(cli, f"after creating {request.name}")
                        problem = schedule_readback(request, before, after)
                        if problem:
                            raise ArrayCliError(problem)
                    except Exception:
                        _schedule_after_failure(action, line, cli, result)   # while the session is still open
                        raise
                    result.schedules_created.append(request.name)
                    record(action, "created", f"{request.schedule_words()}; active, next run "
                           + next(s.next_run for s in after if s.name == request.name))
                    result.removal_notes.append(
                        f"Snapshots the schedule {request.name} takes expire on their own after {request.expire_hours} "
                        "hours. To remove them sooner, remove each with removevv -f.")
    except Exception as exc:  # the array's words, where it stopped, what to remove
        if in_flight is not None:
            _diff_after_failure(in_flight, provisioning, wsapi_factory, result, remove)
        done = sum(1 for o in result.outcomes if o.status == "created")
        result.error = (f"Stopped after {done} row(s) and {written} write(s): {str(exc).rstrip('.')}. The removal set "
                        "below undoes exactly what was created before the failure.")
        if current is not None and all(o.name != current.name or o.kind != current.kind for o in result.outcomes):
            record(current, "failed", str(exc))
    result.removals.sort(key=lambda i: REMOVAL_ORDER.get(i.kind, 9))
    return result


class _Nothing:
    """No WSAPI session when the plan has no snapshot to take now."""

    def __enter__(self):
        return None

    def __exit__(self, *exc):
        return None


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
    except Exception:  # the line stays, with a note to check by hand
        result.removal_notes.append(f"The array was not read after the schedule {action.name} failed. Check with "
                                    f"showsched {action.name}; if it is not there, skip its removesched line.")
        return
    if action.name not in names and line in result.removals:
        result.removals.remove(line)


def _diff_after_failure(in_flight: tuple[SnapshotAction, set[str]], provisioning: ProvisioningIntent,
                        wsapi_factory: Callable, result: SnapshotResult, remove: Callable[[list[str]], None]) -> None:
    """A write that failed, or whose read-back failed, may still have made snapshots: read once more and
    name what the diff shows. When even that read fails, say which names to check by hand."""
    action, before = in_flight
    try:
        with wsapi_factory(provisioning.array) as wsapi:
            remove(made_by(action, before, wsapi.volumes()))
    except Exception:  # the note below stands in for the read that failed
        names = " ".join(now_snapshot_name(m) for m in action.members)
        result.removal_notes.append(
            f"The array was not read after the snapshot of {action.source} failed. Check with showvv {names}; "
            "remove with removevv -f each one that was not there before this run.")
