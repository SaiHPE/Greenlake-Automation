"""SPEC-023 R4 — the plan: exists / create / conflict per row (SPEC-001), from the same read apply
uses (LESSONS 37). Read-only: nothing here talks to the array.

A row gives at most two actions, in apply order: the snapshot now of every member (one WSAPI call),
then the schedule. Blockers carry every conflict and every reason the row cannot be applied; notes
say what the operator should know and need not act on.
"""

from __future__ import annotations

import json
from itertools import product

from alletra_onboard.application.snapshots.read import parse_createsv
from alletra_onboard.domain.snapshots import (
    DAY_NAMES,
    NOW_SUFFIX,
    SCHEDULE_SUFFIX_LEN,
    SNAPSHOTS_PER_VOLUME_MAX,
    ArraySchedule,
    SnapshotAction,
    SnapshotArrayView,
    SnapshotIntent,
    SnapshotPlan,
    SnapshotRequest,
    cron_values,
    now_snapshot_name,
    same_command,
    same_cron,
    snapshot_name_max,
)


def now_call(request: SnapshotRequest, members: list[str], all_members: list[str]) -> str:
    """The WSAPI call the snapshot now makes, as text. A set whose members all lack their snapshot is
    snapshotted in one call (one point in time); otherwise each missing member on its own."""
    params = {"readOnly": request.read_only, "expirationHours": request.expire_hours}
    if request.kind == "set" and sorted(members) == sorted(all_members):
        body = {"action": "createSnapshot", "parameters": {"name": f"@vvname@{NOW_SUFFIX}", **params}}
        return f"POST /volumesets/{request.source} {json.dumps(body)}"
    return "\n".join(
        f"POST /volumes/{m} " + json.dumps({"action": "createSnapshot", "parameters": {"name": now_snapshot_name(m), **params}})
        for m in members
    )


def now_cli(request: SnapshotRequest, members: list[str], all_members: list[str]) -> str:
    """The CLI the snapshot now equals (SPEC-023 R4 table, row 1)."""
    if request.kind == "set" and sorted(members) == sorted(all_members):
        return request.now_command()
    ro = " -ro" if request.read_only else ""
    return "\n".join(f"createsv{ro} -exp {request.expire_hours}h {now_snapshot_name(m)} {m}" for m in members)


def schedule_call(request: SnapshotRequest) -> str:
    """The write as text: no WSAPI call exists for a schedule, so it goes over SSH through the snapshot
    schedule client, built with this plan's schedules only (ADR 0016)."""
    return f"over SSH, through the snapshot schedule client: {request.createsched_command()}"


def _members(request: SnapshotRequest, view: SnapshotArrayView, planned_volumes: frozenset[str],
             planned_vvsets: frozenset[str], blockers: list[str]) -> list[str] | None:
    """The volumes a row covers on the array, or None (with its blocker) when it covers none."""
    source = request.source
    if request.kind == "set":
        if source in view.vvsets:
            members = list(view.vvsets[source])
            if not members:
                blockers.append(f"Volume set {source} has no volumes, so there is nothing to snapshot. "
                                "Add its volumes first, or name another set on the Snapshots tab.")
                return None
            return members
        planned = source in planned_vvsets
    else:
        if view.volume(source) is not None:
            return [source]
        planned = source in planned_volumes
    if planned:
        blockers.append(f"Provision storage first: {source} is not on the array yet.")
    else:
        blockers.append(f"{source} is not on the array and not on the Volumes tab.")
    return None


def _now_action(request: SnapshotRequest, members: list[str], view: SnapshotArrayView, limit: int,
                blockers: list[str]) -> SnapshotAction:
    missing: list[str] = []
    present: list[str] = []
    for member in members:
        name = now_snapshot_name(member)
        if len(name) > limit:
            blockers.append(f"{name} would be longer than {limit} characters, the most this array's OS allows "
                            f"in a snapshot name. Snapshot now cannot be taken of {member}.")
        found = view.volume(name)
        if found is None:
            missing.append(member)
        elif found.copy_of == member:
            present.append(member)
        else:
            reason = (f"{name} is already on the array and is not a snapshot of {member}. The tool never "
                      f"changes a volume it did not make: rename or remove {name}, or leave Snapshot now as no.")
            blockers.append(reason)
            return SnapshotAction(kind="snapshot", name=name, source=request.source, state="conflict",
                                  reason=reason, members=[member])
    label = f"Snapshot now {request.source}"
    if not missing:
        return SnapshotAction(kind="snapshot", name=label, source=request.source, state="exists",
                              members=members, reason=", ".join(now_snapshot_name(m) for m in members) + " already there")
    reason = ", ".join(now_snapshot_name(m) for m in missing)
    if present:
        reason += (f"; {', '.join(now_snapshot_name(m) for m in present)} already there, so each missing one "
                   "is taken on its own")
    mode = "read-only" if request.read_only else "read-write"
    reason += f" ({mode}, expires after {request.expire_hours} hours)"
    return SnapshotAction(kind="snapshot", name=label, source=request.source, state="create", members=missing,
                          reason=reason, cli=now_cli(request, missing, members), call=now_call(request, missing, members))


def _schedule_action(request: SnapshotRequest, members: list[str], view: SnapshotArrayView, limit: int,
                     blockers: list[str]) -> SnapshotAction:
    name = request.name
    longest = max(members, key=len)
    if len(longest) + SCHEDULE_SUFFIX_LEN > limit:
        blockers.append(f"The snapshots of {longest} would be named {longest}.YYMMDDHHMMSS, longer than {limit} "
                        "characters, the most this array's OS allows in a snapshot name.")
    action = SnapshotAction(kind="schedule", name=name, source=request.source, state="create", members=members,
                            cli=request.createsched_command(), call=schedule_call(request))
    have = view.schedule(name)
    if have is None:
        action.reason = request.schedule_words()
        return action
    if have.status.lower() == "suspended":
        action.state = "conflict"
        action.reason = (f"A schedule named {name} is on the array but suspended, so it takes no snapshots. The tool "
                         "never changes a schedule it did not make: name another on the Snapshots tab, or remove "
                         "that one first.")
    elif have.status.lower() == "active" and same_command(have.command, request.createsv_command()) and same_cron(
            have.cron, request.cron):
        action.state = "exists"
        action.reason = f"{request.schedule_words()}; active, next run {have.next_run}"
        return action
    else:
        action.state = "conflict"
        action.reason = (f"A schedule named {name} already runs '{have.command}' at '{have.cron}'. The tool never "
                         "changes a schedule it did not make: name another on the Snapshots tab, or remove that one first.")
    blockers.append(action.reason)
    return action


def _count_per_member(request: SnapshotRequest, members: list[str], view: SnapshotArrayView,
                      now: SnapshotAction | None, schedule: SnapshotAction | None, blockers: list[str]) -> None:
    """ADR 0016 decision 3: no member past 2048 snapshots. Every snapshot of the member counts, read-only
    or not, until a live run shows which do (open question in the work packet, check 5)."""
    taking_now = set(now.members) if now is not None and now.state == "create" else set()
    kept = request.kept_alive if schedule is not None and schedule.state == "create" else 0
    for member in members:
        held = sum(1 for v in view.volumes if v.copy_of == member)
        total = held + (1 if member in taking_now else 0) + kept
        if total > SNAPSHOTS_PER_VOLUME_MAX:
            blockers.append(f"{member} would hold up to {total} snapshots; the array allows {SNAPSHOTS_PER_VOLUME_MAX} "
                            "per volume. Keep them for less time, or take them less often.")


def _starts(cron: str) -> set[tuple[int, int, int]] | None:
    """The minutes of the week a cron starts in, as (day of week, hour, minute). Day of month and month
    are not narrowed: a schedule counts on every day it might fall on."""
    values = cron_values(cron)
    if values is None:
        return None
    minutes, hours, _dom, _month, dows = values
    return set(product(dows, hours, minutes))


def _busiest_note(name: str, cron: str, others: list[tuple[str, set[tuple[int, int, int]]]]) -> str | None:
    """SPEC-023 R4, *Starts per minute*: createsched -f turns off the array's own check, so the plan
    makes it. A note, not a blocker, until the array's recommended number is known."""
    mine = _starts(cron)
    if not mine:
        return None
    counts = {start: sum(1 for _n, starts in others if start in starts) for start in mine}
    top = max(counts.values())
    if top == 0:
        return None
    dow, hour, minute = min(start for start, n in counts.items() if n == top)
    same_every_day = all(counts.get((d, hour, minute)) == top for d in range(7))
    when = f"{hour:02d}:{minute:02d} {'every day' if same_every_day else 'on ' + DAY_NAMES[dow]}"
    return (f"The array already starts {top} schedule{'s' if top != 1 else ''} at {when}; {name} adds one. "
            "The array advises spreading schedule start times.")


def _cpg_notes(rows: list[list[str]], view: SnapshotArrayView) -> list[str]:
    cpgs: list[str] = []
    for members in rows:
        for member in members:
            vol = view.volume(member)
            if vol is not None and vol.cpg and vol.cpg not in cpgs:
                cpgs.append(vol.cpg)
    notes = []
    for cpg in cpgs:
        free = view.cpg_free_mib.get(cpg)
        if free is None:
            notes.append(f"{cpg}: its free space was not read; snapshots use the volume's own CPG.")
        else:
            size = f"{free / 1024 / 1024:.1f} TiB" if free >= 1024 * 1024 else f"{free / 1024:.0f} GiB"
            notes.append(f"{cpg} has {size} free; snapshots use the volume's own CPG.")
    return notes


def _array_starts(schedules: list[ArraySchedule]) -> list[tuple[str, set[tuple[int, int, int]]]]:
    out = []
    for s in schedules:
        if s.status.lower() != "active":
            continue                      # a suspended schedule does not run
        starts = _starts(s.cron)
        if starts:
            out.append((s.name, starts))
    return out


def plan_snapshots(
    intent: SnapshotIntent, view: SnapshotArrayView, *,
    planned_volumes: frozenset[str] | set[str] = frozenset(), planned_vvsets: frozenset[str] | set[str] = frozenset(),
) -> SnapshotPlan:
    """SPEC-023 R4 over one read of the array. `planned_*` are the Volumes tab's names, so a source the
    run still has to provision is told apart from one that exists nowhere."""
    plan = SnapshotPlan()
    limit = snapshot_name_max(view.os_version)
    covered: list[list[str]] = []
    new_schedules: list[tuple[SnapshotRequest, SnapshotAction]] = []
    for request in intent.requests:
        if request.retain_hours:
            plan.blockers.append(f"{request.source}: Lock for is not offered yet. A locked snapshot cannot be removed "
                                 "until the lock ends; leave Lock for blank.")
        members = _members(request, view, frozenset(planned_volumes), frozenset(planned_vvsets), plan.blockers)
        if members is None:
            continue
        covered.append(members)
        now = _now_action(request, members, view, limit, plan.blockers) if request.snapshot_now else None
        schedule = _schedule_action(request, members, view, limit, plan.blockers) if request.has_schedule else None
        plan.actions += [a for a in (now, schedule) if a is not None]
        _count_per_member(request, members, view, now, schedule, plan.blockers)
        if schedule is not None:
            for other in view.schedules:
                if other.name != schedule.name and parse_createsv(other.command).get("source") == request.source_ref:
                    plan.notes.append(f"The array already takes snapshots of {request.source} on schedule {other.name}. "
                                      "Both will run.")
            if schedule.state == "create":
                new_schedules.append((request, schedule))
                plan.notes.append(f"Once created, the array takes a snapshot of {request.source} {request.schedule_words()},"
                                  f" until someone removes the schedule {schedule.name}.")
    array_starts = _array_starts(view.schedules)
    for request, schedule in new_schedules:
        others = array_starts + [(r.name, _starts(r.cron) or set()) for r, s in new_schedules if s is not schedule]
        note = _busiest_note(schedule.name, request.cron, others)
        if note:
            plan.notes.append(note)
    plan.notes += _cpg_notes(covered, view)
    return plan
