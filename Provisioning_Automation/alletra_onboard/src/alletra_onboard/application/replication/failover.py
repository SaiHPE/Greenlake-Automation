"""SPEC-017 — the failover test: stop → failover → recover → wait for sync → restore on ONE Remote
Copy group, over WSAPI's disaster-recovery action, reading both arrays after every step.

P is this run's array, S the peer. Every write names the array it is sent to. An unexpected state
stops the test at that step; the record then carries both sides as read and HPE's documented way
back (troubleshooting guide ED6, role/status table) as CLI lines. The tool never runs that way back.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.verify import peer_group_name
from alletra_onboard.application.runs.apply_record import try_save_record
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.domain.approval import Approval, SaveRecord, require_approval
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
    FailoverRecord,
    FailoverSide,
    FailoverStepRecord,
    RcGroup,
    ReplicationArrayView,
)
from alletra_onboard.domain.shared import EndpointCreds

if TYPE_CHECKING:
    from alletra_onboard.application.runs.writer_clients import WsapiWriter

#: How long each wait may take before the test stops and reports (SPEC-017 R2).
STOP_WAIT_S = 120           # step 1: both sides Stopped
FAILOVER_WAIT_S = 180       # step 2: the peer shows Primary-Rev
RECOVER_WAIT_S = 180        # step 4: the old primary shows Secondary-Rev and the group is Started
AUTO_START_WAIT_S = 60      # step 4: how long to watch for the array starting the group itself after failover
SYNC_WAIT_S = 15 * 60       # step 5: every volume Synced after the recover
RESTORE_WAIT_S = 300        # step 6: back to Primary on P, Secondary on S, Started, Synced
PERIOD_MARGIN_S = 120       # async: steps 5 and 6 wait at least one period plus this
POLL_S = 10


def read_group(creds: EndpointCreds, group: str, *, array_cli_factory: Callable = make_array_cli) -> RcGroup | None:
    """`showrcopy groups <group>` on one array, read-only; None when the group is not there."""
    with array_cli_factory(creds) as cli:
        rc = replication_read.parse_showrcopy(cli.run(f"showrcopy groups {group}"))
    return next((g for g in rc["groups"] if g.name == group), None)


def period_seconds(text: str) -> int:
    """The Options column's period (`5m`, `30s`, `1h`, `1d`) in seconds; 0 when absent or unreadable."""
    m = re.fullmatch(r"(\d+)\s*([smhd])", (text or "").strip().lower())
    return int(m.group(1)) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)] if m else 0


def side_of(array_name: str, group: str, g: RcGroup | None) -> FailoverSide:
    if g is None:
        return FailoverSide(array=array_name, group=group, present=False)
    last = ""
    for v in g.volumes:
        if v.last_sync and v.last_sync != "NA" and v.last_sync > last:
            last = v.last_sync
    if not last and g.last_sync and g.last_sync != "NA":
        last = g.last_sync
    return FailoverSide(
        array=array_name, group=group, role=g.role, status=g.status, mode=g.mode_key, volumes=len(g.volumes),
        synced=sum(1 for v in g.volumes if v.sync_status.lower() == "synced"), last_sync=last,
    )


def recovery_action(p: FailoverSide, s: FailoverSide) -> str:
    """HPE's documented way back for the role/status pair observed (ED6 role/status table), as the CLI
    lines to run and where. Chosen by what the arrays show, not by which step failed."""
    pr, ps, sr, ss = p.role, p.status.lower(), s.role, s.status.lower()
    if not p.present or not s.present:
        return "The group is missing on one side. Check `showrcopy groups` on both arrays before doing anything; contact HPE Support."
    if "failsafe" in (ps, ss):
        return (f"A side is in Failsafe (I/O blocked). On {s.array}: setrcopygroup recover -f {s.group}  (or restore -f); "
                "if the group stays in Failsafe, setrcopygroup override and contact HPE Support.")
    if pr == "Primary" and sr == "Primary-Rev":
        # after failover, before recover: both still Stopped
        return f"On {s.array}: setrcopygroup recover -f {s.group} ; then setrcopygroup restore -f {s.group}"
    if pr == "Secondary-Rev" and sr == "Primary-Rev":
        return f"On {s.array}: setrcopygroup restore -f {s.group}  (returns the group to its natural direction and starts it)"
    if pr == "Primary" and sr == "Secondary":
        if ps == "stopped" or ss == "stopped":
            return f"On {p.array}: startrcopygroup {p.group}"
        return "The group is already in its natural direction and started; nothing to do."
    if pr == "Primary-Rev" and sr == "Secondary":
        return f"On {p.array}: setrcopygroup reverse -natural -f {p.group}  (reverse local natural; ED6)"
    if pr == "Secondary" and sr == "Primary":
        # live 2026-10-10: the array made the peer the natural primary; this put it back on the lab pair
        return (f"The peer is now the group's natural primary. On {s.array}: stoprcopygroup -f {s.group} ; "
                f"setrcopygroup reverse -f {s.group} ; then on {p.array}: startrcopygroup {p.group}")
    return (f"Roles {pr}/{p.status} on {p.array} and {sr}/{s.status} on {s.array} are not a combination this tool "
            "knows the way back from. Do not change roles further; contact HPE Support with `showrcopy -d groups` from both arrays.")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _precheck_group(record: FailoverRecord, p_side: FailoverSide, s_side: FailoverSide) -> str | None:
    if not p_side.present:
        return f"Group '{record.group}' is not on {record.primary_array}; nothing was done."
    if not s_side.present:
        return f"Group '{record.peer_group}' is not on {record.peer_array}; nothing was done."
    if p_side.role != "Primary" or p_side.status.lower() != "started" or s_side.role != "Secondary" or s_side.status.lower() != "started":
        return ("The group is not Primary/Started here with Secondary/Started on the peer; the test starts only from "
                "the normal state. Nothing was done.")
    if p_side.volumes == 0 or p_side.synced != p_side.volumes:
        return (f"{p_side.synced} of {p_side.volumes} volume(s) Synced; the test starts only when every volume is "
                "Synced. Nothing was done.")
    return None


def _checkpoint_recovery(
    step_seq: int, observed: tuple[FailoverSide, FailoverSide], after: tuple[FailoverSide, FailoverSide],
) -> str:
    if_done, if_not = recovery_action(*after), recovery_action(*observed)
    if if_done == if_not:
        return if_done
    return f"Check `showrcopy groups` on both arrays: if step {step_seq} took effect: {if_done} ; if not: {if_not}"


def _sides_summary(p: FailoverSide, s: FailoverSide) -> str:
    return f"{p.array}: {p.summary} · {s.array}: {s.summary}"


def _checkpoint(
    save: SaveRecord,
    record: FailoverRecord,
    step: FailoverStepRecord,
    observed: tuple[FailoverSide, FailoverSide],
    after: tuple[FailoverSide, FailoverSide],
) -> str | None:
    """Save the in-progress record with only the last-read sides and recovery for both outcomes."""
    snap = record.model_copy(update={
        "result": "failed",
        "failed_step": step.seq,
        "observed_state": _sides_summary(*observed),
        "recovery_action": _checkpoint_recovery(step.seq, observed, after),
        "error": (f"Interrupted during step {step.seq} ({step.title}). "
                  "Check `showrcopy groups` on both arrays before running any recovery command."),
    })
    return try_save_record(save, snap)


def _fail(
    record: FailoverRecord,
    step: FailoverStepRecord,
    detail: str,
    sides: tuple[FailoverSide, FailoverSide],
    *,
    aborted: bool = False,
) -> FailoverRecord:
    p, s = sides
    step.outcome, step.detail, step.ended_at = "failed", detail, _now()
    step.primary, step.peer = p, s
    for later in record.steps[record.steps.index(step) + 1:]:
        later.outcome = "skipped"
    record.result = "aborted" if aborted else "failed"
    record.failed_step = step.seq
    record.observed_state = _sides_summary(p, s)
    record.recovery_action = recovery_action(p, s)
    record.error = detail
    record.ended_at = _now()
    return record


def _note_checkpoint(
    save: SaveRecord,
    record: FailoverRecord,
    step: FailoverStepRecord,
    observed: tuple[FailoverSide, FailoverSide],
    after: tuple[FailoverSide, FailoverSide],
) -> None:
    if (err := _checkpoint(save, record, step, observed, after)) is not None:
        note = f"Checkpoint save before step {step.seq} failed ({err}); continuing to restore."
        step.detail = f"{step.detail} {note}".strip()


def _async_setup(mode: str, group_obj: RcGroup | None, p_side: FailoverSide) -> tuple[str, int]:
    """Pure helper: for an async group, compute its data-loss-bound text and period wait margin."""
    if mode != "async":
        return "", 0
    bound = (f"last sync before failover {p_side.last_sync}" if p_side.last_sync
             else "no last sync time was shown before failover")
    period = period_seconds(group_obj.period if group_obj else "")
    return bound, (period + PERIOD_MARGIN_S if period else 0)


def _stopped(p: FailoverSide, s: FailoverSide) -> bool:
    return p.status.lower() == "stopped" and s.status.lower() == "stopped"


def _recovered(p: FailoverSide, s: FailoverSide) -> bool:
    return (p.role in ("Secondary-Rev", "Secondary") and s.role in ("Primary-Rev", "Primary")
            and s.status.lower() == "started")


def _all_synced(p: FailoverSide, s: FailoverSide) -> bool:
    return s.volumes > 0 and s.synced == s.volumes and p.synced == p.volumes


def _normal(p: FailoverSide, s: FailoverSide) -> bool:
    return (p.role == "Primary" and s.role == "Secondary" and p.status.lower() == "started"
            and s.status.lower() == "started" and p.volumes > 0 and p.synced == p.volumes)


def _flipped(p: FailoverSide, s: FailoverSide) -> bool:
    return p.role == "Secondary" and s.role == "Primary"


def _run_dr_call(fn: Callable[..., object], *args: object) -> Exception | None:
    """Run a DR call under failover's 'returns, never raises' contract."""
    try:
        fn(*args)
        return None
    except Exception as exc:  # returns, never raises
        return exc


@dataclass
class _DrRuntime:
    record: FailoverRecord
    both: Callable[[], tuple[FailoverSide, FailoverSide]]
    wait_for: Callable[[Callable[[FailoverSide, FailoverSide], bool], int], tuple[bool, FailoverSide, FailoverSide, float]]
    save: SaveRecord
    progress: Callable[[str], None]
    lim: dict[str, int]
    clock: Callable[[], float]
    primary_view: ReplicationArrayView
    last_sides: tuple[FailoverSide, FailoverSide]
    step: FailoverStepRecord
    activity: str = ""
    sent: str = ""
    in_flight_recovery: str = ""
    refusal: str = ""

    def begin(self, step: FailoverStepRecord) -> float:
        self.step, self.activity, self.sent, self.in_flight_recovery, self.refusal = step, "", "", "", ""
        step.started_at = _now()
        return self.clock()

    def finish(self, step: FailoverStepRecord, p: FailoverSide, s: FailoverSide, start: float) -> None:
        self.sent = self.in_flight_recovery = ""
        step.primary, step.peer, step.outcome = p, s, "ok"
        step.seconds, step.ended_at = round(self.clock() - start, 1), _now()

    def checkpoint(
        self, observed: tuple[FailoverSide, FailoverSide], after: tuple[FailoverSide, FailoverSide],
        *, note: bool = True,
    ) -> str | None:
        if note:
            _note_checkpoint(self.save, self.record, self.step, observed, after)
            err = None
        else:
            err = _checkpoint(self.save, self.record, self.step, observed, after)
        if err is None:
            self.in_flight_recovery = _checkpoint_recovery(self.step.seq, observed, after)
        return err

    def send(self, label: str, fn: Callable[..., object], *args: object) -> Exception | None:
        self.sent = label
        return _run_dr_call(fn, *args)

    def refused(self, msg: str) -> tuple[FailoverSide, FailoverSide, str]:
        self.refusal = msg
        p, s = self.both()
        return p, s, msg


def _stop_and_wait(
    stop_fn: Callable[[str], object], group: str, array_name: str, rt: _DrRuntime,
) -> tuple[FailoverSide, FailoverSide, str | None]:
    if (exc := rt.send("the stop", stop_fn, group)) is not None:
        return rt.refused(f"{array_name} refused the stop: {exc}")
    ok, p, s, _w = rt.wait_for(_stopped, rt.lim["stop"])
    if not ok:
        return p, s, f"Not Stopped on both sides within {rt.lim['stop']} s."
    return p, s, None


def _run_failover_step(
    record: FailoverRecord,
    step: FailoverStepRecord,
    sides: tuple[FailoverSide, FailoverSide],
    ws: WsapiWriter,
    rt: _DrRuntime,
) -> tuple[FailoverSide, FailoverSide, str | None]:
    p, s = sides
    rt.checkpoint(
        sides,
        (p.model_copy(update={"role": "Primary", "status": "Stopped"}),
         s.model_copy(update={"role": "Primary-Rev", "status": "Stopped"})),
    )
    rt.progress(f"Failing over: {record.peer_group} on {record.peer_array} becomes Primary-Rev…")
    if (exc := rt.send("the failover", ws.remote_copy_dr_action, record.peer_group, DR_ACTION_FAILOVER)) is not None:
        return rt.refused(f"{record.peer_array} refused the failover: {exc}")
    ok, p, s, _w = rt.wait_for(lambda _p, side: side.role in ("Primary-Rev", "Primary"), rt.lim["failover"])
    if not ok:
        return p, s, f"The peer did not show Primary-Rev within {rt.lim['failover']} s."
    return p, s, None


def _run_recover(
    record: FailoverRecord, step: FailoverStepRecord, ws: WsapiWriter, rt: _DrRuntime,
) -> tuple[FailoverSide, FailoverSide, str | None]:
    # 4. recover on S, unless the array already did it. Live 2026-10-10 (both arrays up): the failover
    # was mirrored to P as Secondary-Rev and the array started the group from S within seconds; a
    # recover sent then is refused with 403 code 284 "Remote copy group not stopped".
    ok, p, s, _w = rt.wait_for(_recovered, rt.lim["auto_start"])
    if ok:
        step.title, step.action, step.cli = "Recover (done by the array)", "(not sent: the array did it)", ""
        step.detail = (f"Recover was not needed: the array made {p.array} Secondary-Rev and started the group from "
                       f"{s.array} by itself after the failover.")
        return p, s, None
    rt.checkpoint(
        (p, s),
        (p.model_copy(update={"role": "Secondary-Rev", "status": "Started"}),
         s.model_copy(update={"role": "Primary-Rev", "status": "Started"})),
    )
    rt.progress(f"Recovering: {record.group} on {record.primary_array} becomes Secondary-Rev, syncing back…")
    if (exc := rt.send("the recover", ws.remote_copy_dr_action, record.peer_group, DR_ACTION_RECOVER)) is not None:
        p, s, msg = rt.refused(f"{record.peer_array} refused the recover: {exc}")
        if not _recovered(p, s):
            return p, s, msg
        step.detail = f"{record.peer_array} answered '{exc}', and the group is already in the recovered state."
    ok, p, s, _w = rt.wait_for(_recovered, rt.lim["recover"])
    if not ok:
        return p, s, f"Not Secondary-Rev on P with Primary-Rev/Started on S within {rt.lim['recover']} s."
    return p, s, None


def _run_failback(
    record: FailoverRecord, step: FailoverStepRecord, wp: WsapiWriter, ws: WsapiWriter, rt: _DrRuntime,
) -> tuple[FailoverSide, FailoverSide, str | None]:
    ok, p, s, _w = rt.wait_for(_flipped, rt.lim["auto_start"])
    if not ok:
        return p, s, f"The array did not settle on {record.peer_array} as primary within {rt.lim['auto_start']} s."
    step.title, step.where = "Fail back to this array", "P"
    step.action = (f"PUT /remotecopygroups/{record.peer_group} {{action: stop}} on S; "
                   f"POST /remotecopygroups/{record.group} {{action: 7}} on P")
    step.cli = f"stoprcopygroup -f {record.peer_group}  (on S) ; setrcopygroup failover -f {record.group}  (on P)"
    step.detail += (f"The array had made {record.peer_array} the natural primary after the sync, so the group was "
                    f"failed back the same way: stopped on {record.peer_array}, failed over on {record.primary_array}.")
    rt.checkpoint(
        (p, s),
        (p.model_copy(update={"status": "Stopped"}), s.model_copy(update={"status": "Stopped"})),
    )
    rt.progress(f"Failing back: stopping {record.peer_group} on {record.peer_array}, then failing over to {record.primary_array}…")
    p, s, err = _stop_and_wait(ws.stop_remote_copy_group, record.peer_group, record.peer_array, rt)
    if err is not None:
        return p, s, err
    rt.checkpoint((p, s), (p.model_copy(update={"role": "Primary-Rev"}), s))
    if (exc := rt.send("the failover back", wp.remote_copy_dr_action, record.group, DR_ACTION_FAILOVER)) is not None:
        return rt.refused(f"{record.primary_array} refused the failover back: {exc}")
    return p, s, None


def _run_restore(
    record: FailoverRecord, step: FailoverStepRecord, wp: WsapiWriter, ws: WsapiWriter, rt: _DrRuntime,
) -> tuple[FailoverSide, FailoverSide, str | None]:
    # 6. back to this array. Live 2026-10-10 (twice): once the sync back completed, the array turned
    # Primary-Rev/Secondary-Rev into plain Primary on S and Secondary on P, and `restore` was then
    # refused (HTTP 400 code 29, "was not previously switched"). So: restore while the roles still
    # carry -Rev; otherwise fail back the way the failover went, from the other side.
    p, s = rt.both()
    if not _flipped(p, s) and p.role != "Secondary":
        rt.checkpoint((p, s), (p, s))
        rt.progress(f"Restoring the natural direction: {record.group} Primary on {record.primary_array} again…")
        if (exc := rt.send("the restore", ws.remote_copy_dr_action, record.peer_group, DR_ACTION_RESTORE)) is not None:
            p, s, msg = rt.refused(f"{record.peer_array} refused the restore: {exc}")
            if not _flipped(p, s) and p.role != "Secondary":
                return p, s, msg
            step.detail = f"{record.peer_array} answered '{exc}': the array had already made it the natural primary. "
    if _flipped(p, s) or p.role == "Secondary":
        p, s, err = _run_failback(record, step, wp, ws, rt)
        if err is not None:
            return p, s, err
    ok, p, s, _w = rt.wait_for(_normal, rt.lim["restore"])
    if not ok:
        return p, s, f"Not back to Primary/Started on P and Secondary/Started on S with every volume Synced within {rt.lim['restore']} s."
    return p, s, None


def _build_plan(group: str, pg: str) -> list[FailoverStepRecord]:
    def _dr(seq: int, title: str, act: int, verb: str, expected: str) -> FailoverStepRecord:
        return FailoverStepRecord(
            seq=seq, title=title, where="S", action=f"POST /remotecopygroups/{pg} {{action: {act}}}",
            cli=f"setrcopygroup {verb} -f {pg}", expected=expected,
        )

    return [
        FailoverStepRecord(seq=1, title="Stop the group", where="P", action=f"PUT /remotecopygroups/{group} {{action: stop}}",
                           cli=f"stoprcopygroup -f {group}", expected="Stopped on both arrays"),
        _dr(2, "Fail over to the peer", 7, "failover", "Primary-Rev on S; with both arrays up the array also makes P Secondary-Rev"),
        FailoverStepRecord(seq=3, title="The peer's volumes are now read/write", where="-", action="(read)",
                           expected="recorded, not written to"),
        _dr(4, "Recover", 9, "recover", "Primary-Rev/Started on S; Secondary-Rev on P; syncing back to P"),
        FailoverStepRecord(seq=5, title="Wait until Synced", where="-", action="(read)", expected="every volume Synced"),
        _dr(6, "Restore the natural direction", 10, "restore", "Primary/Started on P; Secondary/Started on S; Synced"),
    ]


def _fail_unexpected(record: FailoverRecord, s1: FailoverStepRecord, rt: _DrRuntime, exc: Exception) -> FailoverRecord:
    if rt.activity == "opening":
        return _fail(
            record, s1,
            f"Could not open a write session before step 1: {exc}. Nothing was sent to either array.",
            rt.last_sides, aborted=True,
        )
    if rt.refusal and rt.activity.startswith("reading "):
        detail = f"{rt.refusal}; could not read {rt.activity.removeprefix('reading ')} afterward: {exc}."
    else:
        when = f"after {rt.sent} was sent" if rt.sent else f"during step {rt.step.seq} ({rt.step.title})"
        tail = "" if rt.sent else " No command was sent in this step."
        if rt.activity.startswith("reading "):
            detail = f"Could not read {rt.activity.removeprefix('reading ')} {when}: {exc}.{tail}"
        elif rt.activity == "progress":
            detail = f"Progress update failed {when}: {exc}.{tail}"
        else:
            detail = f"Step {rt.step.seq} ({rt.step.title}) failed {when}: {exc}.{tail}"
    failed = _fail(record, rt.step, detail, rt.last_sides)
    if rt.in_flight_recovery and rt.activity != "progress":
        failed.recovery_action = rt.in_flight_recovery
    return failed


def _run_dr_sequence(
    record: FailoverRecord,
    plan: list[FailoverStepRecord],
    approval: Approval,
    wsapi_factory: Callable,
    rt: _DrRuntime,
) -> FailoverRecord:
    p_side, s_side = rt.last_sides
    s1, s2, s3, s4, s5, s6 = plan
    t = rt.begin(s1)
    stack = ExitStack()
    try:
        rt.activity = "opening"
        wp: WsapiWriter = stack.enter_context(wsapi_factory(approval, "failover", "A"))
        ws: WsapiWriter = stack.enter_context(wsapi_factory(approval, "failover", "B"))
        rt.activity = ""
        err = rt.checkpoint(
            (p_side, s_side),
            (p_side.model_copy(update={"status": "Stopped"}), s_side.model_copy(update={"status": "Stopped"})),
            note=False,
        )
        if err is not None:
            return _fail(record, s1, f"Could not save the failover record before step 1: {err}. Nothing was sent to either array.", (p_side, s_side), aborted=True)
        # 1. stop on P
        rt.progress(f"Stopping {record.group} on {record.primary_array}…")
        p, s, err = _stop_and_wait(wp.stop_remote_copy_group, record.group, record.primary_array, rt)
        if err is not None:
            return _fail(record, s1, err, (p, s))
        rt.finish(s1, p, s, t)

        # 2. failover on S
        t = rt.begin(s2)
        p, s, err = _run_failover_step(record, s2, (p, s), ws, rt)
        if err is not None:
            return _fail(record, s2, err, (p, s))
        rt.finish(s2, p, s, t)
        record.time_to_failover_s = s2.seconds
        if record.mode == "async" and record.data_loss_bound:
            # in this array's zone, the zone its last sync time is written in
            record.data_loss_bound += f"; failover completed at {replication_read.array_time(s2.ended_at, rt.primary_view)}"

        # 3. read only: the peer's volumes are read/write now
        t = rt.begin(s3)
        p, s = rt.both()
        s3.detail = f"{s.array} holds the group as {s.role}/{s.status}; its {s.volumes} volume(s) are writable. Not written to."
        rt.finish(s3, p, s, t)

        # 4. recover on S, unless the array already did it
        t = rt.begin(s4)
        p, s, err = _run_recover(record, s4, ws, rt)
        if err is not None:
            return _fail(record, s4, err, (p, s))
        rt.finish(s4, p, s, t)

        # 5. wait for the sync back
        t = rt.begin(s5)
        rt.progress("Waiting until every volume is Synced…")
        ok, p, s, waited = rt.wait_for(_all_synced, rt.lim["sync"])
        if not ok:
            return _fail(record, s5, f"Not every volume was Synced within {rt.lim['sync'] // 60} min ({s.synced}/{s.volumes} on {s.array}).", (p, s))
        rt.finish(s5, p, s, t)
        record.time_to_synced_s = waited

        # 6. back to this array
        t = rt.begin(s6)
        p, s, err = _run_restore(record, s6, wp, ws, rt)
        if err is not None:
            return _fail(record, s6, err, (p, s))
        rt.finish(s6, p, s, t)
        record.result, record.ended_at = "passed", _now()
        return record
    finally:
        if (close_exc := _run_dr_call(stack.close)) is not None:
            note = f"Write session close failed after step {rt.step.seq}: {close_exc}."
            rt.step.detail = f"{rt.step.detail} {note}".strip()


def run_failover_test(
    approval: Approval, group: str, *,
    wsapi_factory: Callable = make_wsapi_writer,
    read_fn: Callable = replication_read.read_array,
    read_group_fn: Callable = read_group,
    progress: Callable[[str], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    limits: dict[str, int] | None = None,
) -> FailoverRecord:
    """The R2 sequence on `group`, as the record. Writes only through `wsapi_factory`; every state
    through the read functions. Returns, never raises for device failures: a failure is a record
    with `result` failed."""
    live = require_approval(approval)
    save = live.require_saver()
    p_creds, s_creds = live.creds_for("failover", "A"), live.creds_for("failover", "B")
    lim = {"stop": STOP_WAIT_S, "failover": FAILOVER_WAIT_S, "recover": RECOVER_WAIT_S, "sync": SYNC_WAIT_S,
           "restore": RESTORE_WAIT_S, "poll": POLL_S, "auto_start": AUTO_START_WAIT_S, **(limits or {})}
    record = FailoverRecord(group=group, started_at=_now())
    _p = progress or (lambda _m: None)

    # ---- step 0: both arrays, in full (names, system id, the group's mode)
    step0 = FailoverStepRecord(seq=0, title="Read both arrays", where="-", action="(read)", started_at=_now(),
                               expected="Primary/Started on P, Secondary/Started on S, every volume Synced")
    record.steps.append(step0)
    t0 = clock()
    if (exc := _run_dr_call(_p, "Reading both arrays before the test…")) is not None:
        step0.outcome, step0.detail, step0.ended_at = "failed", f"Progress update failed before reading the arrays: {exc}. Nothing was sent to either array.", _now()
        record.result, record.failed_step, record.error, record.ended_at = "aborted", 0, step0.detail, _now()
        return record
    a, b = read_fn(p_creds), read_fn(s_creds)
    if a.read_error or b.read_error:
        step0.outcome, step0.detail, step0.ended_at = "failed", a.read_error or b.read_error, _now()
        record.result, record.failed_step, record.error, record.ended_at = "aborted", 0, step0.detail, _now()
        return record
    record.primary_array, record.peer_array = a.name or p_creds.host, b.name or s_creds.host
    record.peer_group = peer_group_name(group, a)
    p_side, s_side = side_of(record.primary_array, group, a.group(group)), side_of(record.peer_array, record.peer_group, b.group(record.peer_group))
    step0.primary, step0.peer, step0.seconds, step0.ended_at = p_side, s_side, round(clock() - t0, 1), _now()
    record.mode = p_side.mode

    if err := _precheck_group(record, p_side, s_side):
        return _fail(record, step0, err, (p_side, s_side), aborted=True)
    step0.outcome = "ok"
    record.data_loss_bound, margin = _async_setup(record.mode, a.group(group), p_side)
    lim["sync"], lim["restore"] = max(lim["sync"], margin), max(lim["restore"], margin)

    plan = _build_plan(group, record.peer_group)
    record.steps.extend(plan)

    def both() -> tuple[FailoverSide, FailoverSide]:
        rt.activity = f"reading {record.primary_array}"
        p_grp = read_group_fn(p_creds, group)
        rt.activity = f"reading {record.peer_array}"
        s_grp = read_group_fn(s_creds, record.peer_group)
        rt.activity = ""
        sides = (side_of(record.primary_array, group, p_grp),
                 side_of(record.peer_array, record.peer_group, s_grp))
        rt.last_sides, rt.in_flight_recovery, rt.refusal = sides, "", ""
        return sides

    def wait_for(check: Callable[[FailoverSide, FailoverSide], bool], limit_s: int) -> tuple[bool, FailoverSide, FailoverSide, float]:
        start = clock()
        while True:
            p, s = both()
            if check(p, s):
                return True, p, s, round(clock() - start, 1)
            if clock() - start >= limit_s:
                return False, p, s, round(clock() - start, 1)
            sleep(lim["poll"])

    def emit(msg: str) -> None:
        rt.activity = "progress"
        _p(msg)
        rt.activity = ""

    rt = _DrRuntime(
        record=record, both=both, wait_for=wait_for, save=save, progress=emit, lim=lim,
        clock=clock, primary_view=a, last_sides=(p_side, s_side), step=plan[0],
    )
    if (exc := _run_dr_call(_run_dr_sequence, record, plan, approval, wsapi_factory, rt)) is not None:
        return _fail_unexpected(record, plan[0], rt, exc)
    return record
