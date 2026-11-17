"""SPEC-023 R7 — verify, read-only: each snapshot now is in place as asked, and each schedule is on the
array, active, running the planned command at the planned times, and taking snapshots.

The tool finds its snapshots by name and parent, never by parent alone (ADR 0016 decision 5): Remote
Copy makes snapshots of the same members (`rcpy.41.269.5` on D22U27), and they must not be counted.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from alletra_onboard.application.snapshots import read as snapshots_read
from alletra_onboard.application.snapshots.read import parse_createsv
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.snapshots import (
    SCHEDULE_PATTERN,
    SnapshotArrayView,
    SnapshotPlan,
    SnapshotRequest,
    SnapshotRowCheck,
    SnapshotVerification,
    is_scheduled_snapshot_name,
    now_snapshot_name,
    same_command,
    same_cron,
)

#: R7: an expiry within ten minutes of creation + Keep for.
EXPIRY_SLACK = timedelta(minutes=10)


def _time(text: str) -> datetime | None:
    try:
        return datetime.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def check_now(request: SnapshotRequest, members: list[str], view: SnapshotArrayView) -> tuple[bool, str]:
    """Every member's `<member>.initial` is its snapshot, read-only as asked, expiring Keep for after it
    was made. Used by verify and by apply's read-back."""
    problems: list[str] = []
    for member in members:
        name = now_snapshot_name(member)
        snap = view.volume(name)
        if snap is None:
            problems.append(f"{name} is not on the array")
            continue
        if snap.copy_of != member:
            problems.append(f"{name} is not a snapshot of {member}")
            continue
        if snap.read_only != request.read_only:
            problems.append(f"{name} is {'read-only' if snap.read_only else 'read-write'}, not as asked")
        created, expires = _time(snap.created), _time(snap.expires)
        if not snap.expires:
            problems.append(f"{name} has no expiry")
        elif created is not None and expires is not None:
            off = abs(expires - (created + timedelta(hours=request.expire_hours)))
            if off > EXPIRY_SLACK:
                problems.append(f"{name} expires {snap.expires}, not {request.expire_hours} hours after it was made")
    if problems:
        return False, "; ".join(problems) + "."
    mode = "read-only" if request.read_only else "read-write"
    return True, f"{len(members)} in place ({', '.join(now_snapshot_name(m) for m in members)}), {mode}, expiring after {request.expire_hours} hours."


def scheduled_snapshots(members: list[str], view: SnapshotArrayView, since: str = "") -> list[str]:
    """The snapshots a schedule of these members has taken: `copyOf` a member and named `<member>.` and
    twelve digits; with `since`, made after it."""
    start = _time(since)
    out = []
    for v in view.volumes:
        if v.copy_of in members and is_scheduled_snapshot_name(v.copy_of, v.name):
            made = _time(v.created)
            if start is None or made is None or made >= start:
                out.append(v.name)
    return out


def twins(request: SnapshotRequest, view: SnapshotArrayView, members: list[str]) -> dict[str, set[str]]:
    """{other schedule: the members it shares with this row} for every other schedule that takes
    snapshots of any of these members under the same name pattern, whether it names the same source or
    a set holding one of them: their snapshots and this row's cannot be told apart by name."""
    out: dict[str, set[str]] = {}
    for s in view.schedules:
        parsed = parse_createsv(s.command)
        if s.name == request.name or parsed.get("pattern") != SCHEDULE_PATTERN:
            continue
        source = parsed.get("source", "")
        covers = view.vvsets.get(source[4:], []) if source.startswith("set:") else [source]
        shared = set(members) & set(covers)
        if shared:
            out[s.name] = shared
    return out


def _what(request: SnapshotRequest, members: list[str], same: dict[str, set[str]]) -> str:
    shared = set().union(*same.values())
    return request.source if shared >= set(members) else ", ".join(sorted(shared))


def check_row(request: SnapshotRequest, view: SnapshotArrayView, members: list[str], since: str = "") -> SnapshotRowCheck:
    row = SnapshotRowCheck(source=request.source, schedule=request.name if request.has_schedule else "")
    if request.snapshot_now:
        row.now_ok, row.now_detail = check_now(request, members, view)
    if not request.has_schedule:
        return row
    have = view.schedule(request.name)
    if have is None:
        row.verdict = "not_scheduled"
        row.detail = f"no schedule named {request.name} on the array"
        return row
    if have.status.lower() != "active":
        row.verdict, row.detail = "not_scheduled", f"{request.name} is {have.status}"
        return row
    if not same_command(have.command, request.createsv_command()) or not same_cron(have.cron, request.cron):
        row.verdict = "not_scheduled"
        row.detail = f"{request.name} runs '{have.command}' at '{have.cron}', not what was planned"
        return row
    row.next_run = have.next_run
    taken = scheduled_snapshots(members, view, since)
    row.taken = len(taken)
    row.verdict = "taking" if taken else "scheduled"
    row.detail = request.schedule_words()
    same = twins(request, view, members)
    if same:
        row.detail += (f". Schedule {', '.join(sorted(same))} also snapshots {_what(request, members, same)} under the "
                       "same names; the count cannot tell them apart and includes both")
    return row


def verify(
    provisioning: ProvisioningIntent, plan: SnapshotPlan, *, since: str = "", read_fn: Callable = snapshots_read.read_array,
    progress: Callable[[str], None] | None = None,
) -> SnapshotVerification:
    """Read the array once and judge every row of the tab. `since` is when this run's apply began: a
    schedule's snapshots are counted from it."""
    out = SnapshotVerification()
    intent = provisioning.snapshots
    if intent is None:
        out.error = "this run has no Snapshots tab"
        return out
    view = read_fn(provisioning.array, progress=progress)
    if view.read_error:
        out.error = view.read_error
        return out
    for request in intent.requests:
        members = (list(view.vvsets.get(request.source, [])) if request.kind == "set"
                   else ([request.source] if view.volume(request.source) else []))
        out.rows.append(check_row(request, view, members, since))
    return out
