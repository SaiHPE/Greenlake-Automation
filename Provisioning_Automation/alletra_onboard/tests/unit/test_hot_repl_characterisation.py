"""Focused behavioural tests covering paths missed by existing replication and as-built tests,
plus regressions for the four review findings on arch/hot-repl."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import docx
from docx.oxml.ns import qn
from pydantic import BaseModel

from alletra_onboard.application.documents import steps as doc_steps
from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt
from alletra_onboard.application.replication import failover as rc_failover
from alletra_onboard.application.replication.plan import build_plan
from alletra_onboard.application.replication.plan_check import GROUP_LIMIT, check
from alletra_onboard.application.replication.read import parse_showrcopy_detail
from alletra_onboard.domain.approval import Approval
from alletra_onboard.domain.errors import ArrayCliError
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RESTORE,
    TEST_GROUP,
    TEST_PEER_VVSET,
    TEST_VOLUME,
    TEST_VVSET,
    FailoverSide,
    RcGroup,
    RcGroupVolume,
    ReplicationArrayView,
)
from alletra_onboard.domain.shared import EndpointCreds
from tests.unit import test_asbuilt_replication as ab_rc
from tests.unit import test_replication_failover as fo
from tests.unit import test_replication_plan as rc_pair

FIX = Path(__file__).resolve().parents[1] / "fixtures"
RCIP = FIX / "rcip_pair"


def _read_docx(path: Path) -> tuple[dict[tuple[str, ...], list[list[str]]], str]:
    doc = docx.Document(str(path))
    tables: dict[tuple[str, ...], list[list[str]]] = {}
    for tbl in doc.tables:
        rows = [[cell.text.strip() for cell in row.cells] for row in tbl.rows]
        tables.setdefault(tuple(rows[0]), []).extend(rows[1:])
    text = "".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))
    return tables, text


# ------------------------------------------------------------------ 1. replication/plan.py

def test_plan_multi_target_all_occupied_finding():
    a, b = rc_pair._two_target_views()
    a.groups.append(RcGroup(
        name="pre_sync_2", target="E18U31_async", status="Started", role="Primary", mode="Sync",
        volumes=[RcGroupVolume(local_name="pre_vol")],
    ))
    report = check(a, b, rc_pair._intent([rc_pair._ASYNC_ROW], failover=False))
    assert report.findings == [(
        "None of the 2 targets from AlletraMP_D22U27 to AlletraMP_E18U31 can carry a async group "
        "('AlletraMP_E18U31' carries 6 sync group(s); 'E18U31_async' carries 1 sync group(s)); "
        "every group on one target must replicate in the same mode (HPE Support Matrix). "
        "Use that mode on the Replication tab, or a target of its own over spare RCIP ports "
        "(a link belongs to one target; set it up on the arrays, the tool makes only the first target of a pair)."
    )]


def test_plan_group_limit_finding():
    a, b = rc_pair._views()
    a.groups.extend(
        RcGroup(name=f"g_{i}", target="AlletraMP_E18U31", status="Started", role="Primary", mode="Sync")
        for i in range(GROUP_LIMIT["sync"] - len(a.groups))
    )
    report = check(a, b, rc_pair._intent(failover=False))
    assert report.findings == [
        f"AlletraMP_D22U27 already has {GROUP_LIMIT['sync']} sync groups, the limit for a 2-node system."
    ]


def test_plan_existing_test_vvset_and_peer_vvset_actions_and_call_order():
    a, b = rc_pair._views()
    a.vvsets[TEST_VVSET] = [TEST_VOLUME]
    b.vvsets["zz_rc_vvs_rc"] = ["zz_rc_vol01", "zz_rc_vol02"]
    b.vvsets[TEST_PEER_VVSET] = [TEST_VOLUME]
    intent = rc_pair._intent()
    report = check(a, b, intent)
    plan = build_plan(report, intent, rc_pair._prov())
    assert report.findings == []
    assert [(act.kind, act.name, act.state) for act in plan.actions] == [
        ("test_volume", TEST_VOLUME, "exists"),
        ("test_vvset", TEST_VVSET, "exists"),
        ("group", "zz_rc_vvs_rcg", "create"),
        ("peer_vvset", "zz_rc_vvs_rc", "exists"),
        ("group", TEST_GROUP, "create"),
        ("peer_vvset", TEST_PEER_VVSET, "exists"),
    ]
    ordered_calls = sorted((c for act in plan.actions for c in act.calls), key=lambda c: c.seq)
    assert [(c.seq, c.where, c.cli) for c in ordered_calls] == [
        (1, "A", "creatercopygroup -usr_cpg SSD_r6 AlletraMP_E18U31:SSD_r6 zz_rc_vvs_rcg AlletraMP_E18U31:sync"),
        (2, "A", "setrcopygroup pol auto_recover zz_rc_vvs_rcg ; setrcopygroup pol auto_synchronize zz_rc_vvs_rcg"),
        (3, "A", "admitrcopyvv -createvv zz_rc_vol01 zz_rc_vvs_rcg AlletraMP_E18U31:zz_rc_vol01"),
        (4, "A", "admitrcopyvv -createvv zz_rc_vol02 zz_rc_vvs_rcg AlletraMP_E18U31:zz_rc_vol02"),
        (5, "A", "startrcopygroup zz_rc_vvs_rcg"),
        (6, "A", f"creatercopygroup -usr_cpg SSD_r6 AlletraMP_E18U31:SSD_r6 {TEST_GROUP} AlletraMP_E18U31:sync"),
        (7, "A", f"setrcopygroup pol auto_recover {TEST_GROUP} ; setrcopygroup pol auto_synchronize {TEST_GROUP}"),
        (8, "A", f"admitrcopyvv -createvv {TEST_VOLUME} {TEST_GROUP} AlletraMP_E18U31:{TEST_VOLUME}"),
        (9, "A", f"startrcopygroup {TEST_GROUP}"),
    ]


# ------------------------------------------------------------------ 2. replication/failover.py

@dataclasses.dataclass
class _FailoverHarness:
    pair: fo.FakePair
    stop_exc: Exception | None = None
    failback_stop_exc: Exception | None = None
    failback_fo_exc: Exception | None = None
    peer_name_override: str | None = None
    checkpoints_at_call: list[tuple[tuple[str, str, str], int]] = dataclasses.field(default_factory=list)
    saves: list[dict[str, Any]] = dataclasses.field(default_factory=list)

    def save(self, model: BaseModel) -> None:
        self.saves.append(model.model_dump(mode="json"))

    def wsapi(self, approval: Approval, purpose: str, side: str) -> Any:
        return _RecordingWsapi(self, approval.creds_for(purpose, side).host)

    def read_array(self, creds: EndpointCreds) -> ReplicationArrayView:
        view = self.pair.view(creds.host)
        if creds.host == fo.S and self.peer_name_override is not None:
            return view.model_copy(update={"name": self.peer_name_override})
        return view


class _RecordingWsapi:
    def __init__(self, harness: _FailoverHarness, host: str) -> None:
        self.h = harness
        self.host = host

    def __enter__(self) -> _RecordingWsapi:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def stop_remote_copy_group(self, name: str) -> str:
        self.h.checkpoints_at_call.append(((self.host, "stop", name), len(self.h.saves)))
        if self.host == fo.P and self.h.stop_exc is not None:
            self.h.pair.calls.append((self.host, "stop", name))
            raise self.h.stop_exc
        if self.host == fo.S and self.h.failback_stop_exc is not None:
            self.h.pair.calls.append((self.host, "stop", name))
            raise self.h.failback_stop_exc
        self.h.pair.stop(self.host, name)
        return "stopped"

    def remote_copy_dr_action(self, name: str, action: int) -> None:
        self.h.checkpoints_at_call.append(((self.host, f"dr:{action}", name), len(self.h.saves)))
        if self.host == fo.P and action == DR_ACTION_FAILOVER and self.h.failback_fo_exc is not None:
            self.h.pair.calls.append((self.host, "failover", name))
            raise self.h.failback_fo_exc
        self.h.pair.dr(self.host, name, action)


def _run_failover(harness: _FailoverHarness, *, limits: dict[str, int] | None = None):
    clock = {"t": 0.0}

    def tick() -> float:
        clock["t"] += 1.0
        return clock["t"]

    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=harness.save)
    default_limits = {"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1, "auto_start": 2}
    if limits:
        default_limits.update(limits)
    return rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=harness.wsapi,
        read_fn=harness.read_array,
        read_group_fn=lambda creds, name: harness.pair.group(creds.host, name),
        sleep=lambda _s: None,
        clock=tick,
        limits=default_limits,
    )


def _assert_saved_before_each_call(harness: _FailoverHarness) -> None:
    prev = 0
    for call, save_count in harness.checkpoints_at_call:
        assert save_count > prev, f"expected a new checkpoint save before {call}"
        prev = save_count


def test_failover_stop_restore_and_failback_refusals():
    h_stop = _FailoverHarness(fo.FakePair(), stop_exc=RuntimeError("busy"))
    r_stop = _run_failover(h_stop)
    assert (r_stop.result, r_stop.failed_step) == ("failed", 1)
    assert r_stop.error == "AlletraMP_D22U27 refused the stop: busy"
    assert r_stop.observed_state == "AlletraMP_D22U27: Primary/Started · 1/1 Synced · AlletraMP_E18U31: Secondary/Started · 1/1 Synced"
    assert r_stop.recovery_action == "The group is already in its natural direction and started; nothing to do."
    assert h_stop.pair.calls == [(fo.P, "stop", fo.G)]
    _assert_saved_before_each_call(h_stop)

    h_rest = _FailoverHarness(fo.FakePair(refuse=("restore",)))
    r_rest = _run_failover(h_rest)
    assert (r_rest.result, r_rest.failed_step) == ("failed", 6)
    assert "AlletraMP_E18U31 refused the restore:" in (r_rest.error or "")
    assert r_rest.observed_state == "AlletraMP_D22U27: Secondary-Rev/Started · 1/1 Synced · AlletraMP_E18U31: Primary-Rev/Started · 1/1 Synced"
    assert r_rest.recovery_action.startswith(f"On AlletraMP_E18U31: setrcopygroup restore -f {fo.PG}")
    assert h_rest.pair.calls == [(fo.P, "stop", fo.G), (fo.S, "failover", fo.PG), (fo.S, "recover", fo.PG), (fo.S, "restore", fo.PG)]
    _assert_saved_before_each_call(h_rest)

    h_fb = _FailoverHarness(fo.FakePair(mirror=True, flip=True), failback_fo_exc=RuntimeError("no fo"))
    r_fb = _run_failover(h_fb)
    assert (r_fb.result, r_fb.failed_step) == ("failed", 6)
    assert r_fb.error == "AlletraMP_D22U27 refused the failover back: no fo"
    assert r_fb.observed_state == "AlletraMP_D22U27: Secondary/Stopped · 1/1 Synced · AlletraMP_E18U31: Primary/Stopped · 1/1 Synced"
    assert f"stoprcopygroup -f {fo.PG}" in r_fb.recovery_action
    assert h_fb.pair.calls == [(fo.P, "stop", fo.G), (fo.S, "failover", fo.PG), (fo.S, "stop", fo.PG), (fo.P, "failover", fo.G)]
    _assert_saved_before_each_call(h_fb)


def test_failover_timeouts_at_each_step():
    for stuck_verb, step_seq, snippet in (
        ("failover", 2, "The peer did not show Primary-Rev within 5 s."),
        ("recover", 4, "Not Secondary-Rev on P with Primary-Rev/Started on S within 5 s."),
    ):
        h = _FailoverHarness(fo.FakePair(stuck=(stuck_verb,)))
        rec = _run_failover(h)
        assert (rec.result, rec.failed_step, rec.error) == ("failed", step_seq, snippet)
        assert rec.observed_state and rec.recovery_action
        _assert_saved_before_each_call(h)

    p_half = fo.FakePair(mirror=True, flip=True)
    real_group = p_half.group

    def _stuck_half(host: str, name: str):
        g = real_group(host, name)
        if g is not None and p_half.p["role"] == "Secondary" and host == fo.S:
            return g.model_copy(update={"role": "Primary-Rev"})
        return g

    p_half.group = _stuck_half
    h_half = _FailoverHarness(p_half)
    r_half = _run_failover(h_half)
    assert (r_half.result, r_half.failed_step) == ("failed", 6)
    assert r_half.error == "The array did not settle on AlletraMP_E18U31 as primary within 2 s."
    _assert_saved_before_each_call(h_half)

    p_fb_stop = fo.FakePair(mirror=True, flip=True)
    real_stop = p_fb_stop.stop

    def _stop_only_p(where: str, name: str) -> None:
        if where == fo.S:
            p_fb_stop.calls.append((where, "stop", name))
            return
        real_stop(where, name)

    p_fb_stop.stop = _stop_only_p
    h_fb_stop = _FailoverHarness(p_fb_stop)
    r_fb_stop = _run_failover(h_fb_stop)
    assert (r_fb_stop.result, r_fb_stop.failed_step, r_fb_stop.error) == ("failed", 6, "Not Stopped on both sides within 5 s.")
    _assert_saved_before_each_call(h_fb_stop)


def test_blocking_1_falsy_exception_from_dr_call_still_stops_failover():
    class _FalsyError(Exception):
        def __bool__(self) -> bool:
            return False

    h = _FailoverHarness(fo.FakePair(), stop_exc=_FalsyError("empty-bool"))
    rec = _run_failover(h)
    assert (rec.result, rec.failed_step) == ("failed", 1)
    assert rec.error == "AlletraMP_D22U27 refused the stop: empty-bool"
    assert h.pair.calls == [(fo.P, "stop", fo.G)]


def test_blocking_2_peer_name_with_braces_does_not_raise_on_timeout():
    p_half = fo.FakePair(mirror=True, flip=True)
    real_group = p_half.group

    def _stuck_half(host: str, name: str):
        g = real_group(host, name)
        if g is not None and p_half.p["role"] == "Secondary" and host == fo.S:
            return g.model_copy(update={"role": "Primary-Rev"})
        return g

    p_half.group = _stuck_half
    h = _FailoverHarness(p_half, peer_name_override="Peer{bad}")
    rec = _run_failover(h)
    assert (rec.result, rec.failed_step) == ("failed", 6)
    assert rec.error == "The array did not settle on Peer{bad} as primary within 2 s."


def test_blocking_3_negative_limits_are_clamped_to_zero_for_sync_mode():
    h = _FailoverHarness(fo.FakePair(mode="Sync", sync_after=10_000))
    rec = _run_failover(h, limits={"sync": -5, "restore": -3})
    assert (rec.result, rec.failed_step) == ("failed", 5)
    assert rec.error == "Not every volume was Synced within 0 min (0/1 on AlletraMP_E18U31)."


def test_failover_bug_a_read_group_error_after_stop_returns_failed_record():
    pair = fo.FakePair()
    h = _FailoverHarness(pair)
    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=h.save)

    def broken_read_group(_creds: EndpointCreds, _name: str):
        raise ArrayCliError("SSH connection dropped")

    rec = rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=h.wsapi,
        read_fn=h.read_array,
        read_group_fn=broken_read_group,
        sleep=lambda _s: None,
        limits={"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1, "auto_start": 2},
    )
    assert (rec.result, rec.failed_step) == ("failed", 1)
    assert rec.error == "Could not read AlletraMP_D22U27 after the stop was sent: SSH connection dropped."
    assert rec.observed_state == "AlletraMP_D22U27: Primary/Started · 1/1 Synced · AlletraMP_E18U31: Secondary/Started · 1/1 Synced"
    assert f"startrcopygroup {fo.G}" in rec.recovery_action
    assert pair.calls == [(fo.P, "stop", fo.G)]


def test_failover_bug_a_progress_error_mid_test_returns_failed_record():
    pair = fo.FakePair(sync_after=5)
    h = _FailoverHarness(pair)
    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=h.save)

    def broken_progress(msg: str) -> None:
        if "Waiting until every volume is Synced" in msg:
            raise RuntimeError("SSE stream closed")

    rec = rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=h.wsapi,
        read_fn=h.read_array,
        read_group_fn=lambda creds, name: pair.group(creds.host, name),
        progress=broken_progress,
        sleep=lambda _s: None,
        limits={"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1, "auto_start": 2},
    )
    assert (rec.result, rec.failed_step) == ("failed", 5)
    assert rec.error == "Progress update failed during step 5 (Wait until Synced): SSE stream closed. No command was sent in this step."
    assert rec.observed_state == "AlletraMP_D22U27: Secondary-Rev/Started · 0/1 Synced · AlletraMP_E18U31: Primary-Rev/Started · 0/1 Synced"
    assert f"setrcopygroup restore -f {fo.PG}" in rec.recovery_action

    h0 = _FailoverHarness(fo.FakePair())
    approval0 = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                         save_record=h0.save)
    rec0 = rc_failover.run_failover_test(
        approval0, fo.G,
        wsapi_factory=h0.wsapi,
        read_fn=h0.read_array,
        read_group_fn=lambda creds, name: h0.pair.group(creds.host, name),
        progress=lambda _msg: (_ for _ in ()).throw(RuntimeError("step0 callback error")),
        sleep=lambda _s: None,
    )
    assert (rec0.result, rec0.failed_step) == ("aborted", 0)
    assert rec0.error == "Progress update failed before reading the arrays: step0 callback error. Nothing was sent to either array."
    assert h0.pair.calls == []


def test_failover_stale_recovery_cleared_after_restore_refused_and_flipped_read():
    """Fable case 1: restore refused because the array flipped, follow-up read observes Secondary/Primary,
    then a read fails while fail-back settles -> recovery must match the observed flipped state."""
    pair = fo.FakePair(mirror=True, flip=True)
    real_group, real_dr = pair.group, pair.dr
    state = {"flipped": False, "reads_after_flip": 0}

    def _group(host: str, name: str):
        if state["flipped"]:
            state["reads_after_flip"] += 1
            if state["reads_after_flip"] > 2 and host == fo.S:
                raise ArrayCliError("SSH timeout on peer")
            return real_group(host, name)
        saved_flip = pair.flip
        pair.flip = False
        try:
            return real_group(host, name)
        finally:
            pair.flip = saved_flip

    def _dr(where: str, name: str, action: int) -> None:
        if action == DR_ACTION_RESTORE:
            for side in (pair.p, pair.s):
                side["role"] = side["role"].replace("-Rev", "")
            state["flipped"] = True
        real_dr(where, name, action)

    pair.group, pair.dr = _group, _dr
    rec = _run_failover(_FailoverHarness(pair))
    assert (rec.result, rec.failed_step) == ("failed", 6)
    assert rec.error == "Could not read AlletraMP_E18U31 after the restore was sent: SSH timeout on peer."
    expected = rc_failover.recovery_action(
        FailoverSide(array="AlletraMP_D22U27", group=fo.G, role="Secondary", status="Started", volumes=1, synced=1),
        FailoverSide(array="AlletraMP_E18U31", group=fo.PG, role="Primary", status="Started", volumes=1, synced=1),
    )
    assert rec.recovery_action == expected
    assert "setrcopygroup restore -f" not in rec.recovery_action


def test_failover_stale_recovery_cleared_after_restore_accepted_and_read_back():
    """Fable case 2: restore accepted, array back to Primary/Secondary Started (syncing), then a read
    fails -> recovery must match the observed Primary/Secondary Started state ('nothing to do')."""
    pair = fo.FakePair()
    real_group, real_dr = pair.group, pair.dr
    state = {"restored": False, "reads_after_restore": 0}

    def _dr(where: str, name: str, action: int) -> None:
        real_dr(where, name, action)
        if action == DR_ACTION_RESTORE:
            pair.p["synced"] = pair.s["synced"] = False
            state["restored"] = True

    def _group(host: str, name: str):
        if state["restored"]:
            state["reads_after_restore"] += 1
            if state["reads_after_restore"] > 2 and host == fo.P:
                raise ArrayCliError("SSH lost on primary")
        return real_group(host, name)

    pair.group, pair.dr = _group, _dr
    rec = _run_failover(_FailoverHarness(pair))
    assert (rec.result, rec.failed_step) == ("failed", 6)
    assert rec.error == "Could not read AlletraMP_D22U27 after the restore was sent: SSH lost on primary."
    expected = rc_failover.recovery_action(
        FailoverSide(array="AlletraMP_D22U27", group=fo.G, role="Primary", status="Started", volumes=1, synced=0),
        FailoverSide(array="AlletraMP_E18U31", group=fo.PG, role="Secondary", status="Started", volumes=1, synced=0),
    )
    assert rec.recovery_action == expected


def test_failover_keeps_refusal_reason_when_followup_read_fails():
    pair = fo.FakePair(refuse=("failover",))
    real_group = pair.group

    def _group(host: str, name: str):
        if any(verb == "failover" for _w, verb, _n in pair.calls) and host == fo.S:
            raise ArrayCliError("SSH dropped on peer")
        return real_group(host, name)

    pair.group = _group
    rec = _run_failover(_FailoverHarness(pair))
    assert (rec.result, rec.failed_step) == ("failed", 2)
    assert "AlletraMP_E18U31 refused the failover:" in (rec.error or "")
    assert "could not read AlletraMP_E18U31 afterward: SSH dropped on peer." in (rec.error or "")


def test_failover_read_failure_before_send_names_array_and_says_nothing_sent():
    pair = fo.FakePair()
    real_group = pair.group
    calls_seen = {"n": 0}

    def _group(host: str, name: str):
        if any(verb == "failover" for _w, verb, _n in pair.calls):
            calls_seen["n"] += 1
            if calls_seen["n"] > 2 and host == fo.S:
                raise ArrayCliError("SSH busy on peer")
        return real_group(host, name)

    pair.group = _group
    rec = _run_failover(_FailoverHarness(pair))
    assert (rec.result, rec.failed_step) == ("failed", 3)
    assert rec.error == (
        "Could not read AlletraMP_E18U31 during step 3 (The peer's volumes are now read/write): "
        "SSH busy on peer. No command was sent in this step."
    )


def test_failover_non_device_error_opening_session_says_nothing_sent():
    pair = fo.FakePair()
    h = _FailoverHarness(pair)
    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=h.save)

    def bad_wsapi(_approval: Approval, _purpose: str, _side: str):
        raise RuntimeError("TLS context broken")

    rec = rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=bad_wsapi,
        read_fn=h.read_array,
        read_group_fn=lambda creds, name: pair.group(creds.host, name),
        sleep=lambda _s: None,
    )
    assert (rec.result, rec.failed_step) == ("aborted", 1)
    assert rec.error == "Could not open a write session before step 1: TLS context broken. Nothing was sent to either array."
    assert pair.calls == []


def test_failover_close_error_after_step_6_keeps_passed_result_and_notes_error():
    pair = fo.FakePair()
    h = _FailoverHarness(pair)

    class _BadCloseWsapi(_RecordingWsapi):
        def __exit__(self, *_exc: object) -> None:
            if self.host == fo.S:
                raise RuntimeError("logout HTTP 500")

    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=h.save)
    rec = rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=lambda app, purpose, side: _BadCloseWsapi(h, app.creds_for(purpose, side).host),
        read_fn=h.read_array,
        read_group_fn=lambda creds, name: pair.group(creds.host, name),
        sleep=lambda _s: None,
        limits={"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1, "auto_start": 2},
    )
    assert rec.result == "passed" and rec.failed_step is None and rec.error is None
    assert rec.steps[6].outcome == "ok"
    assert "Write session close failed after step 6: logout HTTP 500." in rec.steps[6].detail


def test_failover_base_exception_propagates():
    pair = fo.FakePair()
    h = _FailoverHarness(pair)
    intent = fo._intent()
    assert intent.replication is not None
    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=h.save)
    try:
        rc_failover.run_failover_test(
            approval, fo.G,
            wsapi_factory=h.wsapi,
            read_fn=h.read_array,
            read_group_fn=lambda _c, _n: (_ for _ in ()).throw(KeyboardInterrupt("ctrl-c")),
            sleep=lambda _s: None,
        )
    except KeyboardInterrupt:
        return
    raise AssertionError("KeyboardInterrupt must propagate out of run_failover_test")


def test_failover_bug_b_empty_message_save_error_aborts_before_step_1_and_notes_later():
    pair = fo.FakePair()
    h = _FailoverHarness(pair)
    intent = fo._intent()
    assert intent.replication is not None

    def empty_oserror(_model: BaseModel) -> None:
        raise OSError()

    approval = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                        save_record=empty_oserror)
    rec = rc_failover.run_failover_test(
        approval, fo.G,
        wsapi_factory=h.wsapi,
        read_fn=h.read_array,
        read_group_fn=lambda creds, name: pair.group(creds.host, name),
        sleep=lambda _s: None,
    )
    assert (rec.result, rec.failed_step) == ("aborted", 1)
    assert "OSError" in (rec.error or "")
    assert pair.calls == []

    pair2 = fo.FakePair()
    h2 = _FailoverHarness(pair2)
    save_calls = {"n": 0}

    def fail_second_save(model: BaseModel) -> None:
        save_calls["n"] += 1
        if save_calls["n"] == 2:
            raise OSError()
        h2.save(model)

    approval2 = Approval("test-run", "failover", {"A": intent.array, "B": intent.replication.peer},
                         save_record=fail_second_save)
    rec2 = rc_failover.run_failover_test(
        approval2, fo.G,
        wsapi_factory=h2.wsapi,
        read_fn=h2.read_array,
        read_group_fn=lambda creds, name: pair2.group(creds.host, name),
        sleep=lambda _s: None,
        limits={"stop": 5, "failover": 5, "recover": 5, "sync": 30, "restore": 5, "poll": 1, "auto_start": 2},
    )
    assert rec2.result == "passed"
    assert "Checkpoint save before step 2 failed (OSError); continuing to restore." in rec2.steps[2].detail


# ------------------------------------------------------------------ 3. documents/asbuilt.py

def test_asbuilt_missing_group_snapshot_cpgs_and_apply_error_text(tmp_path: Path):
    a_sync, b_sync = ab_rc._views("after_apply")
    primera_detail = parse_showrcopy_detail((RCIP / "showrcopy_d" / "primera_showrcopy_d.txt").read_text(encoding="utf-8"))[0]
    primera_detail = primera_detail.model_copy(update={"name": "zz_rc_vvs_rcg"})
    sync_plan = {"actions": [
        {"kind": "group", "name": "zz_rc_vvs_rcg", "state": "create",
         "detail": {"vvset": "zz_rc_vvs", "mode": "sync", "period_seconds": None, "peer_vvset": "zz_rc_vvs_rc"}, "calls": []},
        {"kind": "group", "name": "zz_rc_test_rcg", "state": "create",
         "detail": {"vvset": "zz_rc_test", "mode": "sync", "period_seconds": None, "peer_vvset": "zz_rc_test_rc"}, "calls": []},
    ]}
    sync_res = {
        "outcomes": [
            {"kind": "group", "name": "zz_rc_vvs_rcg", "where": "A", "status": "created", "detail": "sync"},
            {"kind": "group", "name": "zz_rc_test_rcg", "where": "A", "status": "created", "detail": "sync"},
        ],
        "removals_a": [], "removals_b": [], "error": "WSAPI 500",
    }
    data = ab_rc._data(
        replication_tab=ab_rc._tab("sync"),
        replication_plan=sync_plan,
        replication_result=sync_res,
        replication_primary=a_sync.model_copy(update={"groups": [g for g in a_sync.groups if g.name != "zz_rc_test_rcg"]}),
        replication_peer=b_sync.model_copy(update={"vvsets": {}}),
        replication_details={"zz_rc_vvs_rcg": primera_detail},
    )
    out, _warnings = generate_asbuilt(data, tmp_path / "rc_edges.docx")
    tables, text = _read_docx(out)
    groups = tables[("Group", "Mode", "RPO / period", "Policies", "Role here", "Role on peer", "Status", "Peer volume set")]
    missing_row = next(r for r in groups if r[0] == "zz_rc_test_rcg")
    assert missing_row[4] == "not on the array now"
    settings = tables[("Setting", "Value")]
    assert ["Snapshot CPG here", "SSD_r6"] in settings
    assert ["Snapshot CPG on the peer", "SSD_r6"] in settings
    assert "Replication stopped with an error: WSAPI 500" in text


# ------------------------------------------------------------------ 4. documents/steps.py (_run_records)

def test_blocking_4_run_records_writes_none_string_for_none_created_at():
    def ev(etype: str, data: dict[str, Any]) -> SimpleNamespace:
        return SimpleNamespace(event_type=etype, data=data, created_at=None)

    events = [
        ev("storage.applied", {"result": {"outcomes": []}}),
        ev("replication.applied", {"result": {"outcomes": [], "removals_a": ["a1", "dup"], "removals_b": ["b1"]}}),
        ev("replication.applied", {"result": {"outcomes": [], "removals_a": ["a2", "dup"], "removals_b": ["b2", "b1"]}}),
        ev("snapshots.applied", {"result": {"outcomes": []}}),
    ]
    data = AsBuiltData()
    coord = SimpleNamespace(list_events=lambda _id: events, list_commands=lambda _id: [])
    doc_steps.DocumentSteps(coord=coord)._run_records("r1", data)
    assert data.provisioning_applied_at == "None"
    assert data.replication_applied_at == "None"
    assert data.snapshots_applied_at == "None"
    assert data.replication_removals_a == ["a2", "dup", "a1"]
    assert data.replication_removals_b == ["b2", "b1"]
