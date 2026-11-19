"""SPEC-023 R8 — the as-built's Snapshots section, placed after *Provisioning performed* (after the
replication sections when present), only when the run's workbook has the Snapshots tab.

Everything about the array is read when the document is made (`AsBuiltData.snapshots_view`), never
copied from the plan. The removal set names only what the run made: the schedules and snapshots its
applies created, and the snapshots its own schedules hold now, matched by name and parent as verify
counts them (ADR 0016 decision 5). When another schedule takes snapshots of the same source under the
same names, the two cannot be told apart, so those snapshots get no removal line: they expire on their
own. Kept apart from asbuilt.py, which calls `add_snapshots_section` and `snapshot_removal_items`.
"""

from __future__ import annotations

from alletra_onboard.application.documents.asbuilt import (
    AsBuiltData,
    _h1,
    _mono,
    _para,
    _table,
    _when,
)
from alletra_onboard.application.snapshots.read import parse_createsv
from alletra_onboard.application.snapshots.verify import scheduled_snapshots, twins
from alletra_onboard.domain.provisioning import REMOVAL_ORDER
from alletra_onboard.domain.snapshots import SnapshotArrayView, SnapshotRequest, now_snapshot_name

_STATUS = {"active": "Active", "suspended": "Suspended"}


def _view(data: AsBuiltData) -> SnapshotArrayView | None:
    view = data.snapshots_view
    if isinstance(view, SnapshotArrayView) and not view.read_error:
        return view
    return None


def _requests(data: AsBuiltData) -> list[SnapshotRequest]:
    out = []
    for row in data.snapshots_tab or []:
        try:
            out.append(SnapshotRequest.model_validate(row))
        except Exception:  # a row that no longer reads is left out, never guessed
            continue
    return out


def _results(data: AsBuiltData) -> list[dict]:
    return [a.get("result") or {} for a in data.snapshots_applies] or ([data.snapshots_result] if data.snapshots_result else [])


def schedules_created(data: AsBuiltData) -> dict[str, str]:
    """{schedule this run created: when the apply that created it began}."""
    out: dict[str, str] = {}
    for result in _results(data):
        for name in result.get("schedules_created") or []:
            out.setdefault(name, str(result.get("started_at") or ""))
    return out


def _members(request: SnapshotRequest, view: SnapshotArrayView) -> list[str]:
    if request.kind == "set":
        return list(view.vvsets.get(request.source, []))
    return [request.source] if view.volume(request.source) is not None else []


def _taken_now(data: AsBuiltData) -> list[tuple[str, str]]:
    """(snapshot, base) for every snapshot now this run's applies created, each once."""
    out: list[tuple[str, str]] = []
    for result in _results(data):
        for item in result.get("removals") or []:
            name = item.get("name", "")
            base = name.removesuffix(".initial")
            if item.get("kind") == "snapshot" and name == now_snapshot_name(base) and (name, base) not in out:
                out.append((name, base))
    return out


def _held(data: AsBuiltData, view: SnapshotArrayView | None) -> tuple[list[dict], list[str]]:
    """The removal items for the snapshots this run's schedules hold now, and a sentence for each
    schedule whose snapshots cannot be told apart from another schedule's."""
    items: list[dict] = []
    sentences: list[str] = []
    if view is None:
        return items, sentences
    created = schedules_created(data)
    for request in _requests(data):
        if not request.has_schedule or request.name not in created:
            continue
        members = _members(request, view)
        same = twins(request, view, members)
        shared: set[str] = set().union(*same.values()) if same else set()
        if same:
            what = request.source if shared >= set(members) else ", ".join(sorted(shared))
            sentences.append(
                f"Schedule {', '.join(sorted(same))} also takes snapshots of {what} under the same names as "
                f"{request.name}, so the two cannot be told apart: no removevv line is given for them. They expire on "
                f"their own after {request.expire_hours} hours.")
        for name in scheduled_snapshots([m for m in members if m not in shared], view, since=created[request.name]):
            items.append({"kind": "snapshot", "name": name, "command": f"removevv -f {name}"})
    return items, sentences


def snapshot_removal_items(data: AsBuiltData) -> list[dict]:
    """SPEC-023 R6 and R8: every line that undoes what the Snapshots step made, as RemovalItem dicts in
    REMOVAL_ORDER (schedules first, then snapshots), each once. The provisioning section puts them ahead
    of its own lines: a volume with snapshots cannot be removed."""
    items: list[dict] = []
    for result in _results(data):
        items += result.get("removals") or []
    items += _held(data, _view(data))[0]
    out: list[dict] = []
    for item in sorted(items, key=lambda i: REMOVAL_ORDER.get(i.get("kind", ""), 9)):
        if item.get("command") and all(o.get("command") != item["command"] for o in out):
            out.append(item)
    return out


def _add_rows(doc, data: AsBuiltData, view: SnapshotArrayView | None) -> None:
    requests = _requests(data)
    if not requests:
        return
    created = schedules_created(data)
    rows = []
    for request in requests:
        if not request.has_schedule:
            rows.append([request.source, "—", "snapshot now only", "—", "—"])
            continue
        have = view.schedule(request.name) if view is not None else None
        if have is None:
            state = "not on the array" if view is not None else "not read"
        else:
            state = _STATUS.get(have.status.lower(), have.status) + (f", next run {have.next_run}" if have.next_run != "--" else "")
        held = "—"
        if view is not None and have is not None:
            members = _members(request, view)
            n = len(scheduled_snapshots(members, view, since=created.get(request.name, "")))
            held = f"{n} snapshot(s)"
        by = "configured by this run" if request.name in created else "not configured by this run"
        rows.append([request.source, request.name, f"{request.schedule_words()} ({by})", state, held])
    _para(doc, "What the Snapshots tab asked for", bold=True)
    _table(doc, ["Volume set or volume", "Schedule", "In words", "Status (as read)", "It holds now"], rows,
           widths=[0.16, 0.16, 0.36, 0.18, 0.14])
    if created:
        _para(doc, "The array will take a snapshot of each source above on its schedule until someone removes the "
                   "schedule; each snapshot expires on its own after its Keep for.")


def _add_taken_now(doc, data: AsBuiltData, view: SnapshotArrayView | None) -> None:
    _para(doc, "Snapshots taken now", bold=True)
    taken = _taken_now(data)
    if not taken:
        _para(doc, "None: this run took no snapshot now." if _results(data) else "The snapshots were not applied in this run.")
        return
    rows = []
    for name, base in taken:
        snap = view.volume(name) if view is not None else None
        if snap is None:
            rows.append([name, base, "—", "not on the array when this document was made"])
        else:
            rows.append([name, snap.copy_of or base, "yes" if snap.read_only else "no", snap.expires or "no expiry"])
    _table(doc, ["Snapshot", "Of", "Read-only", "Expires (as read)"], rows, widths=[0.30, 0.25, 0.12, 0.33])


def _add_array_schedules(doc, data: AsBuiltData, view: SnapshotArrayView | None) -> None:
    _para(doc, "Snapshot schedules on the array", bold=True)
    if view is None:
        _para(doc, "The array was not read, so its schedules are not listed.")
        return
    if not view.schedules:
        _para(doc, "The array holds no schedule (showsched: No scheduled tasks listed).")
        return
    mine = schedules_created(data)
    sources = {r.source_ref for r in _requests(data)}
    zone = f" Times are in the array's own time zone, {view.time_zone}." if view.time_zone else ""
    _para(doc, "Every schedule on the array when this document was made, as showsched printed it. A schedule keeps "
               f"running after the run ends, until someone removes it.{zone}")
    _table(doc, ["Schedule", "Runs", "Minute Hour Day Month Weekday", "Status", "Next run", "This run"],
           [[s.name, s.command, s.cron, _STATUS.get(s.status.lower(), s.status), s.next_run,
             "configured by this run" if s.name in mine else "not configured by this run"] for s in view.schedules],
           widths=[0.14, 0.34, 0.14, 0.09, 0.14, 0.15])
    others = sorted({s.name for s in view.schedules if s.name not in mine
                     and parse_createsv(s.command).get("source") in sources})
    if others:
        _para(doc, f"Also taking snapshots of the sources on the tab, not configured by this run: {', '.join(others)}.")


def _add_calls(doc, data: AsBuiltData) -> None:
    rows = []
    for applied in data.snapshots_applies:
        plan, result = applied.get("plan") or {}, applied.get("result") or {}
        made = {(o.get("kind"), o.get("name")) for o in result.get("outcomes", []) if o.get("status") == "created"}
        for action in plan.get("actions", []):
            if (action.get("kind"), action.get("name")) in made:
                rows.append([action.get("name", ""), action.get("call", ""), action.get("cli", "")])
    if rows:
        _para(doc, "The calls the tool made", bold=True)
        _table(doc, ["What", "Call", "The CLI it equals"], rows, widths=[0.18, 0.46, 0.36])


def _add_removal(doc, data: AsBuiltData, view: SnapshotArrayView | None) -> None:
    _para(doc, "To remove what the Snapshots step created", bold=True)
    lines = [i["command"] for i in snapshot_removal_items(data)]
    _items, sentences = _held(data, view)
    if lines:
        _para(doc, "The schedule first, so it takes no more snapshots, then each snapshot this run made or its schedule "
                   "holds now. Objects that were there before the run are not listed. Review before pasting; the tool "
                   "never runs these. The same lines head the removal set under Provisioning performed.")
        _mono(doc, lines)
    else:
        _para(doc, "Nothing — this run created no snapshot and no schedule.")
    notes: list[str] = []
    for result in _results(data):
        notes += [n for n in result.get("removal_notes") or [] if n not in notes]
    for text in [*sentences, *notes]:
        _para(doc, text)


def add_snapshots_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    _h1(doc, "Snapshots")
    raw = data.snapshots_view
    if isinstance(raw, SnapshotArrayView) and raw.read_error:
        _para(doc, f"The array could not be read for this section: {raw.read_error}")
        warnings.append(f"The snapshots section could not read the array ({raw.read_error}); its states are missing.")
    view = _view(data)
    results = _results(data)
    if not results:
        _para(doc, "A snapshot plan was built but not applied." if data.snapshots_plan
              else "The Snapshots step was not run in this run.")
    else:
        when = f" Applied at {_when(data.snapshots_applied_at)}." if data.snapshots_applied_at else ""
        failed = [r["error"] for r in results if r.get("error")]
        _para(doc, f"States are as read when this document was made.{when}"
                   + (f" An apply stopped: {failed[-1]}" if failed else ""))
    _add_rows(doc, data, view)
    _add_taken_now(doc, data, view)
    _add_array_schedules(doc, data, view)
    _add_calls(doc, data)
    if results:
        _add_removal(doc, data, view)
