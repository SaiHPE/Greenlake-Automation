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
from datetime import UTC, datetime

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.verify import peer_group_name
from alletra_onboard.application.runs.apply_record import try_save_record
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.domain.approval import Approval, SaveRecord, require_approval
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
    FailoverRecord,
    FailoverSide,
    FailoverStepRecord,
    RcGroup,
)
from alletra_onboard.domain.shared import EndpointCreds

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
    if err := _checkpoint(save, record, step, observed, after):
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


def _run_dr_call(fn: Callable[..., object], *args: object) -> Exception | None:
    """Run a DR call under failover's 'returns, never raises' contract."""
    try:
        fn(*args)
        return None
    except Exception as exc:  # returns, never raises
        return exc


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
    p_creds = live.creds_for("failover", "A")
    s_creds = live.creds_for("failover", "B")
    lim = {"stop": STOP_WAIT_S, "failover": FAILOVER_WAIT_S, "recover": RECOVER_WAIT_S, "sync": SYNC_WAIT_S,
           "restore": RESTORE_WAIT_S, "poll": POLL_S, "auto_start": AUTO_START_WAIT_S}
    lim.update(limits or {})
    record = FailoverRecord(group=group, started_at=_now())
    _p = progress or (lambda _m: None)

    # ---- step 0: both arrays, in full (names, system id, the group's mode)
    step0 = FailoverStepRecord(seq=0, title="Read both arrays", where="-", action="(read)", started_at=_now(),
                               expected="Primary/Started on P, Secondary/Started on S, every volume Synced")
    record.steps.append(step0)
    t0 = clock()
    _p("Reading both arrays before the test…")
    a = read_fn(p_creds)
    b = read_fn(s_creds)
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

    def both() -> tuple[FailoverSide, FailoverSide]:
        return (side_of(record.primary_array, group, read_group_fn(p_creds, group)),
                side_of(record.peer_array, record.peer_group, read_group_fn(s_creds, record.peer_group)))

    def wait_for(check: Callable[[FailoverSide, FailoverSide], bool], limit_s: int) -> tuple[bool, FailoverSide, FailoverSide, float]:
        start = clock()
        while True:
            p, s = both()
            if check(p, s):
                return True, p, s, round(clock() - start, 1)
            if clock() - start >= limit_s:
                return False, p, s, round(clock() - start, 1)
            sleep(lim["poll"])

    plan = _build_plan(group, record.peer_group)
    record.steps.extend(plan)
    s1, s2, s3, s4, s5, s6 = plan

    def begin(step: FailoverStepRecord) -> float:
        step.started_at = _now()
        return clock()

    def finish(step: FailoverStepRecord, p: FailoverSide, s: FailoverSide, start: float) -> None:
        step.primary, step.peer, step.outcome = p, s, "ok"
        step.seconds, step.ended_at = round(clock() - start, 1), _now()

    t = begin(s1)
    with ExitStack() as stack:
        try:
            wp = stack.enter_context(wsapi_factory(approval, "failover", "A"))
            ws = stack.enter_context(wsapi_factory(approval, "failover", "B"))
        except DeviceError as exc:
            return _fail(record, s1, f"Could not open a write session before step 1: {exc}. Nothing was sent to either array.", (p_side, s_side), aborted=True)
        if err := _checkpoint(
            save, record, s1, (p_side, s_side),
            (p_side.model_copy(update={"status": "Stopped"}), s_side.model_copy(update={"status": "Stopped"})),
        ):
            return _fail(record, s1, f"Could not save the failover record before step 1: {err}. Nothing was sent to either array.", (p_side, s_side), aborted=True)
        # 1. stop on P
        _p(f"Stopping {group} on {record.primary_array}…")
        if (exc := _run_dr_call(wp.stop_remote_copy_group, group)) is not None:
            return _fail(record, s1, f"{record.primary_array} refused the stop: {exc}", both())
        ok, p, s, _w = wait_for(_stopped, lim["stop"])
        if not ok:
            return _fail(record, s1, f"Not Stopped on both sides within {lim['stop']} s.", (p, s))
        finish(s1, p, s, t)

        # 2. failover on S
        t = begin(s2)
        _note_checkpoint(save, record, s2, (p, s), (p.model_copy(update={"role": "Primary", "status": "Stopped"}),
                                                    s.model_copy(update={"role": "Primary-Rev", "status": "Stopped"})))
        _p(f"Failing over: {record.peer_group} on {record.peer_array} becomes Primary-Rev…")
        if (exc := _run_dr_call(ws.remote_copy_dr_action, record.peer_group, DR_ACTION_FAILOVER)) is not None:
            return _fail(record, s2, f"{record.peer_array} refused the failover: {exc}", both())
        ok, p, s, waited = wait_for(lambda p, s: s.role in ("Primary-Rev", "Primary"), lim["failover"])
        if not ok:
            return _fail(record, s2, f"The peer did not show Primary-Rev within {lim['failover']} s.", (p, s))
        finish(s2, p, s, t)
        record.time_to_failover_s = s2.seconds
        if record.mode == "async" and record.data_loss_bound:
            # in this array's zone, the zone its last sync time is written in
            record.data_loss_bound += f"; failover completed at {replication_read.array_time(s2.ended_at, a)}"

        # 3. read only: the peer's volumes are read/write now
        t = begin(s3)
        p, s = both()
        s3.detail = f"{s.array} holds the group as {s.role}/{s.status}; its {s.volumes} volume(s) are writable. Not written to."
        finish(s3, p, s, t)

        # 4. recover on S, unless the array already did it. Live 2026-10-10 (both arrays up): the failover
        # was mirrored to P as Secondary-Rev and the array started the group from S within seconds; a
        # recover sent then is refused with 403 code 284 "Remote copy group not stopped".
        t = begin(s4)
        recovered = lambda p, s: (p.role in ("Secondary-Rev", "Secondary") and s.role in ("Primary-Rev", "Primary")
                                  and s.status.lower() == "started")
        ok, p, s, _w = wait_for(recovered, lim["auto_start"])
        if ok:
            s4.title, s4.action, s4.cli = "Recover (done by the array)", "(not sent: the array did it)", ""
            s4.detail = (f"Recover was not needed: the array made {p.array} Secondary-Rev and started the group from "
                         f"{s.array} by itself after the failover.")
        else:
            _note_checkpoint(save, record, s4, (p, s), (p.model_copy(update={"role": "Secondary-Rev", "status": "Started"}),
                                                        s.model_copy(update={"role": "Primary-Rev", "status": "Started"})))
            _p(f"Recovering: {group} on {record.primary_array} becomes Secondary-Rev, syncing back…")
            if (exc := _run_dr_call(ws.remote_copy_dr_action, record.peer_group, DR_ACTION_RECOVER)) is not None:
                p, s = both()
                if not recovered(p, s):
                    return _fail(record, s4, f"{record.peer_array} refused the recover: {exc}", (p, s))
                s4.detail = f"{record.peer_array} answered '{exc}', and the group is already in the recovered state."
            ok, p, s, _w = wait_for(recovered, lim["recover"])
            if not ok:
                return _fail(record, s4, f"Not Secondary-Rev on P with Primary-Rev/Started on S within {lim['recover']} s.", (p, s))
        finish(s4, p, s, t)

        # 5. wait for the sync back
        t = begin(s5)
        _p("Waiting until every volume is Synced…")
        ok, p, s, waited = wait_for(lambda p, s: s.volumes > 0 and s.synced == s.volumes and p.synced == p.volumes, lim["sync"])
        if not ok:
            return _fail(record, s5, f"Not every volume was Synced within {lim['sync'] // 60} min ({s.synced}/{s.volumes} on {s.array}).", (p, s))
        finish(s5, p, s, t)
        record.time_to_synced_s = waited

        # 6. back to this array. Live 2026-10-10 (twice): once the sync back completed, the array turned
        # Primary-Rev/Secondary-Rev into plain Primary on S and Secondary on P, and `restore` was then
        # refused (HTTP 400 code 29, "was not previously switched"). So: restore while the roles still
        # carry -Rev; otherwise fail back the way the failover went, from the other side.
        t = begin(s6)
        normal = lambda p, s: (p.role == "Primary" and s.role == "Secondary" and p.status.lower() == "started"
                               and s.status.lower() == "started" and p.volumes > 0 and p.synced == p.volumes)
        flipped = lambda p, s: p.role == "Secondary" and s.role == "Primary"
        p, s = both()
        if not flipped(p, s) and p.role != "Secondary":
            _note_checkpoint(save, record, s6, (p, s), (p, s))
            _p(f"Restoring the natural direction: {group} Primary on {record.primary_array} again…")
            if (exc := _run_dr_call(ws.remote_copy_dr_action, record.peer_group, DR_ACTION_RESTORE)) is not None:
                p, s = both()
                if not flipped(p, s) and p.role != "Secondary":
                    return _fail(record, s6, f"{record.peer_array} refused the restore: {exc}", (p, s))
                s6.detail = f"{record.peer_array} answered '{exc}': the array had already made it the natural primary. "
        if flipped(p, s) or p.role == "Secondary":
            ok, p, s, _w = wait_for(flipped, lim["auto_start"])
            if not ok:
                return _fail(record, s6, f"The array did not settle on {record.peer_array} as primary within {lim['auto_start']} s.", (p, s))
            s6.title, s6.where = "Fail back to this array", "P"
            s6.action = (f"PUT /remotecopygroups/{record.peer_group} {{action: stop}} on S; "
                         f"POST /remotecopygroups/{group} {{action: 7}} on P")
            s6.cli = f"stoprcopygroup -f {record.peer_group}  (on S) ; setrcopygroup failover -f {group}  (on P)"
            s6.detail += (f"The array had made {record.peer_array} the natural primary after the sync, so the group was "
                          f"failed back the same way: stopped on {record.peer_array}, failed over on {record.primary_array}.")
            _note_checkpoint(save, record, s6, (p, s), (p.model_copy(update={"status": "Stopped"}),
                                                        s.model_copy(update={"status": "Stopped"})))
            _p(f"Failing back: stopping {record.peer_group} on {record.peer_array}, then failing over to {record.primary_array}…")
            if (exc := _run_dr_call(ws.stop_remote_copy_group, record.peer_group)) is not None:
                return _fail(record, s6, f"{record.peer_array} refused the stop: {exc}", both())
            ok, p, s, _w = wait_for(_stopped, lim["stop"])
            if not ok:
                return _fail(record, s6, f"Not Stopped on both sides within {lim['stop']} s.", (p, s))
            _note_checkpoint(save, record, s6, (p, s), (p.model_copy(update={"role": "Primary-Rev"}), s))
            if (exc := _run_dr_call(wp.remote_copy_dr_action, group, DR_ACTION_FAILOVER)) is not None:
                return _fail(record, s6, f"{record.primary_array} refused the failover back: {exc}", both())
        ok, p, s, _w = wait_for(normal, lim["restore"])
        if not ok:
            return _fail(record, s6, f"Not back to Primary/Started on P and Secondary/Started on S with every volume Synced within {lim['restore']} s.", (p, s))
        finish(s6, p, s, t)

    record.result = "passed"
    record.ended_at = _now()
    return record
