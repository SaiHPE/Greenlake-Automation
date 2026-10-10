"""SPEC-017 — the failover test: stop → failover → recover → wait for sync → restore on ONE Remote
Copy group, over WSAPI's disaster-recovery action, reading both arrays after every step.

P is this run's array, S the peer. Every write names the array it is sent to. An unexpected state
stops the test at that step; the record then carries both sides as read and HPE's documented way
back (troubleshooting guide ED6, role/status table) as CLI lines. The tool never runs that way back.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, datetime

from alletra_onboard.application.provisioning.clients import make_array_cli, make_wsapi
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.verify import peer_group_name
from alletra_onboard.domain.provisioning import ProvisioningIntent
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
SYNC_WAIT_S = 15 * 60       # step 5: every volume Synced after the recover
RESTORE_WAIT_S = 300        # step 6: back to Primary on P, Secondary on S, Started, Synced
POLL_S = 10


def read_group(creds: EndpointCreds, group: str, *, array_cli_factory: Callable = make_array_cli) -> RcGroup | None:
    """`showrcopy groups <group>` on one array, read-only; None when the group is not there."""
    with array_cli_factory(creds) as cli:
        rc = replication_read.parse_showrcopy(cli.run(f"showrcopy groups {group}"))
    return next((g for g in rc["groups"] if g.name == group), None)


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
    return (f"Roles {pr}/{p.status} on {p.array} and {sr}/{s.status} on {s.array} are not a combination this tool "
            "knows the way back from. Do not change roles further; contact HPE Support with `showrcopy -d groups` from both arrays.")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def run_failover_test(
    intent: ProvisioningIntent, group: str, *,
    wsapi_factory: Callable = make_wsapi,
    read_fn: Callable = replication_read.read_array,
    read_group_fn: Callable = read_group,
    progress: Callable[[str], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    limits: dict[str, int] | None = None,
) -> FailoverRecord:
    """The R2 sequence on `group`, as the record. Writes only through `wsapi_factory`; every state
    through the read functions. Returns, never raises: a failure is a record with `result` failed."""
    lim = {"stop": STOP_WAIT_S, "failover": FAILOVER_WAIT_S, "recover": RECOVER_WAIT_S, "sync": SYNC_WAIT_S,
           "restore": RESTORE_WAIT_S, "poll": POLL_S}
    lim.update(limits or {})
    rep = intent.replication
    record = FailoverRecord(group=group, started_at=_now())
    if rep is None:
        record.error = "this run has no Replication tab"
        return record
    p_creds, s_creds = intent.array, rep.peer

    def _p(message: str) -> None:
        if progress:
            progress(message)

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

    def fail(step: FailoverStepRecord, detail: str, p: FailoverSide, s: FailoverSide, *, aborted: bool = False) -> FailoverRecord:
        step.outcome, step.detail, step.ended_at = "failed", detail, _now()
        step.primary, step.peer = p, s
        for later in record.steps[record.steps.index(step) + 1:]:
            later.outcome = "skipped"
        record.result = "aborted" if aborted else "failed"
        record.failed_step = step.seq
        record.observed_state = f"{p.array}: {p.summary} · {s.array}: {s.summary}"
        record.recovery_action = recovery_action(p, s)
        record.error = detail
        record.ended_at = _now()
        return record

    if not p_side.present:
        return fail(step0, f"Group '{group}' is not on {record.primary_array}; nothing was done.", p_side, s_side, aborted=True)
    if not s_side.present:
        return fail(step0, f"Group '{record.peer_group}' is not on {record.peer_array}; nothing was done.", p_side, s_side, aborted=True)
    if p_side.role != "Primary" or p_side.status.lower() != "started" or s_side.role != "Secondary" or s_side.status.lower() != "started":
        return fail(step0, "The group is not Primary/Started here with Secondary/Started on the peer; the test starts only from "
                           "the normal state. Nothing was done.", p_side, s_side, aborted=True)
    if p_side.volumes == 0 or p_side.synced != p_side.volumes:
        return fail(step0, f"{p_side.synced} of {p_side.volumes} volume(s) Synced; the test starts only when every volume is "
                           "Synced. Nothing was done.", p_side, s_side, aborted=True)
    step0.outcome = "ok"
    if record.mode == "async":
        record.data_loss_bound = (f"last sync before failover {p_side.last_sync}" if p_side.last_sync
                                  else "no last sync time was shown before failover")

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

    plan = [
        FailoverStepRecord(seq=1, title="Stop the group", where="P", action=f"PUT /remotecopygroups/{group} {{action: stop}}",
                           cli=f"stoprcopygroup -f {group}", expected="Stopped on both arrays"),
        FailoverStepRecord(seq=2, title="Fail over to the peer", where="S", action=f"POST /remotecopygroups/{record.peer_group} {{action: 7}}",
                           cli=f"setrcopygroup failover -f {record.peer_group}", expected="Primary-Rev on S; Primary/Stopped on P"),
        FailoverStepRecord(seq=3, title="The peer's volumes are now read/write", where="-", action="(read)",
                           expected="recorded, not written to"),
        FailoverStepRecord(seq=4, title="Recover", where="S", action=f"POST /remotecopygroups/{record.peer_group} {{action: 9}}",
                           cli=f"setrcopygroup recover -f {record.peer_group}", expected="Primary-Rev/Started on S; Secondary-Rev on P; syncing back to P"),
        FailoverStepRecord(seq=5, title="Wait until Synced", where="-", action="(read)", expected="every volume Synced"),
        FailoverStepRecord(seq=6, title="Restore the natural direction", where="S", action=f"POST /remotecopygroups/{record.peer_group} {{action: 10}}",
                           cli=f"setrcopygroup restore -f {record.peer_group}", expected="Primary/Started on P; Secondary/Started on S; Synced"),
    ]
    record.steps.extend(plan)
    s1, s2, s3, s4, s5, s6 = plan

    def begin(step: FailoverStepRecord) -> float:
        step.started_at = _now()
        return clock()

    def finish(step: FailoverStepRecord, p: FailoverSide, s: FailoverSide, start: float) -> None:
        step.primary, step.peer, step.outcome = p, s, "ok"
        step.seconds, step.ended_at = round(clock() - start, 1), _now()

    with wsapi_factory(p_creds) as wp, wsapi_factory(s_creds) as ws:
        # 1. stop on P
        t = begin(s1)
        _p(f"Stopping {group} on {record.primary_array}…")
        try:
            wp.stop_remote_copy_group(group)
        except Exception as exc:  # noqa: BLE001
            p, s = both()
            return fail(s1, f"{record.primary_array} refused the stop: {exc}", p, s)
        ok, p, s, _w = wait_for(lambda p, s: p.status.lower() == "stopped" and s.status.lower() == "stopped", lim["stop"])
        if not ok:
            return fail(s1, f"Not Stopped on both sides within {lim['stop']} s.", p, s)
        finish(s1, p, s, t)

        # 2. failover on S
        t = begin(s2)
        _p(f"Failing over: {record.peer_group} on {record.peer_array} becomes Primary-Rev…")
        try:
            ws.remote_copy_dr_action(record.peer_group, DR_ACTION_FAILOVER)
        except Exception as exc:  # noqa: BLE001
            p, s = both()
            return fail(s2, f"{record.peer_array} refused the failover: {exc}", p, s)
        ok, p, s, waited = wait_for(lambda p, s: s.role == "Primary-Rev", lim["failover"])
        if not ok:
            return fail(s2, f"The peer did not show Primary-Rev within {lim['failover']} s.", p, s)
        finish(s2, p, s, t)
        record.time_to_failover_s = s2.seconds
        if record.mode == "async" and record.data_loss_bound:
            record.data_loss_bound += f"; failover completed at {s2.ended_at}"

        # 3. read only: the peer's volumes are read/write now
        t = begin(s3)
        p, s = both()
        s3.detail = f"{s.array} holds the group as {s.role}/{s.status}; its {s.volumes} volume(s) are writable. Not written to."
        finish(s3, p, s, t)

        # 4. recover on S
        t = begin(s4)
        _p(f"Recovering: {group} on {record.primary_array} becomes Secondary-Rev, syncing back…")
        try:
            ws.remote_copy_dr_action(record.peer_group, DR_ACTION_RECOVER)
        except Exception as exc:  # noqa: BLE001
            p, s = both()
            return fail(s4, f"{record.peer_array} refused the recover: {exc}", p, s)
        ok, p, s, _w = wait_for(lambda p, s: p.role == "Secondary-Rev" and s.role == "Primary-Rev" and s.status.lower() == "started", lim["recover"])
        if not ok:
            return fail(s4, f"Not Secondary-Rev on P with Primary-Rev/Started on S within {lim['recover']} s.", p, s)
        finish(s4, p, s, t)

        # 5. wait for the sync back
        t = begin(s5)
        _p("Waiting until every volume is Synced…")
        ok, p, s, waited = wait_for(lambda p, s: s.volumes > 0 and s.synced == s.volumes and p.synced == p.volumes, lim["sync"])
        if not ok:
            return fail(s5, f"Not every volume was Synced within {lim['sync'] // 60} min ({s.synced}/{s.volumes} on {s.array}).", p, s)
        finish(s5, p, s, t)
        record.time_to_synced_s = waited

        # 6. restore on S
        t = begin(s6)
        _p(f"Restoring the natural direction: {group} Primary on {record.primary_array} again…")
        try:
            ws.remote_copy_dr_action(record.peer_group, DR_ACTION_RESTORE)
        except Exception as exc:  # noqa: BLE001
            p, s = both()
            return fail(s6, f"{record.peer_array} refused the restore: {exc}", p, s)
        ok, p, s, _w = wait_for(
            lambda p, s: p.role == "Primary" and s.role == "Secondary" and p.status.lower() == "started"
            and s.status.lower() == "started" and p.volumes > 0 and p.synced == p.volumes, lim["restore"])
        if not ok:
            return fail(s6, f"Not back to Primary/Started on P and Secondary/Started on S with every volume Synced within {lim['restore']} s.", p, s)
        finish(s6, p, s, t)

    record.result = "passed"
    record.ended_at = _now()
    return record
