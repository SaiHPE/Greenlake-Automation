"""SPEC-023 R3 to R8 through the snapshot context: the read, the step's preview and verify, and the
as-built section. The array is the D22U27 capture (`tests/fixtures/d22u27_snap/`, OS 10.5.0,
2026-11-17) behind fake SSH and WSAPI clients, or a view built from model objects. No live call."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import docx
import pytest
from docx.oxml.ns import qn
from pydantic import SecretStr

from alletra_onboard.adapters.array.wsapi_client import parse_sets, parse_volumes
from alletra_onboard.application.snapshots.read import read_array
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import ArrayVolumeRecord, EndpointCreds
from alletra_onboard.domain.snapshots import (
    ArraySchedule,
    SnapshotArrayView,
    SnapshotIntent,
    SnapshotPlan,
    SnapshotRequest,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures"
PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"


class _Cli:
    """A capture folder as the read-only SSH client: `<command>.txt`."""

    def __init__(self, folder: str, *, fail: bool = False) -> None:
        self.folder, self.fail, self.sent = folder, fail, []

    def __enter__(self):
        if self.fail:
            raise RuntimeError("Login failed for 3paradm@10.64.122.99")
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        self.sent.append(command)
        return (FIX / self.folder / f"{command}.txt").read_text(encoding="utf-8")


class _Wsapi:
    """A capture folder as the WSAPI client's reads (the adapter's own parsers over the captured GETs)."""

    def __init__(self, folder: str) -> None:
        self.folder = folder

    def _json(self, name: str):
        return json.loads((FIX / self.folder / name).read_text(encoding="utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def system_info(self) -> dict:
        return self._json("wsapi_system.json")

    def volumes(self) -> list[ArrayVolumeRecord]:
        return parse_volumes(self._json("wsapi_volumes.json"))

    def volume_sets(self) -> dict[str, list[str]]:
        return parse_sets(self._json("wsapi_volumesets.json"))


def _creds(host: str = "10.64.122.99") -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


def _d22u27() -> SnapshotArrayView:
    return read_array(_creds(), array_cli_factory=lambda c: _Cli("d22u27_snap"), wsapi_factory=lambda c: _Wsapi("d22u27_snap"))


def _vol(name: str, copy_of: str = "", *, ro: bool = True, created: str = "", expires: str = "") -> ArrayVolumeRecord:
    return ArrayVolumeRecord(name=name, size_mib=1024, cpg="SSD_r6", provisioning_type="snp" if copy_of else "tpvv",
                             copy_of=copy_of, read_only=ro and bool(copy_of), created=created, expires=expires)


def _req(**kw) -> SnapshotRequest:
    base = {"source": "zz_sn_vvs", "expire_hours": 24}
    base.update(kw)
    return SnapshotRequest(**base)


def _sched(req: SnapshotRequest, *, status: str = "active", cron: str | None = None) -> ArraySchedule:
    minute, hour, dom, month, dow = (cron or req.cron).split()
    return ArraySchedule(name=req.name, command=req.createsv_command(), interval="0", minute=minute, hour=hour, dom=dom,
                         month=month, dow=dow, created_by="3paradm", status=status, alert="Y",
                         next_run="2026-11-18 04:00:00 IST" if status == "active" else "--")


def _view(volumes=None, schedules=None) -> SnapshotArrayView:
    base = [_vol("zz_sn_vol01"), _vol("zz_sn_vol02")]
    return SnapshotArrayView(name="AlletraMP_D22U27", os_version="10.5.0", time_zone="IST (Asia/Calcutta)",
                             volumes=base + list(volumes or []), vvsets={"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02"]},
                             schedules=list(schedules or []), cpg_free_mib={"SSD_r6": 403200})


# ------------------------------------------------------------------ R3: the read

def test_the_read_takes_every_fact_the_plan_needs_from_the_capture():
    view = _d22u27()
    assert view.read_error == ""
    assert (view.name, view.os_version, view.time_zone) == ("AlletraMP_D22U27", "10.5.0", "IST (Asia/Calcutta)")
    assert view.retention_max_hours == 336                      # VVRetentionTimeMax 1209600 s
    assert [s.name for s in view.schedules][:2] == ["test_CRV_snapschedule", "compactcpg_SSD_r6_sun"]
    assert len(view.schedules) == 7 and view.cpg_free_mib["SSD_r6"] == 403200
    assert view.vvsets["300gb"] == ["300gb", "Test"]
    rcpy = view.volume("rcpy.41.269.5")
    assert rcpy is not None and rcpy.copy_of == "300gb" and rcpy.read_only


def test_the_read_sends_only_show_commands_and_names_a_failed_login():
    cli = _Cli("d22u27_snap")
    read_array(_creds(), array_cli_factory=lambda c: cli, wsapi_factory=lambda c: _Wsapi("d22u27_snap"))
    assert cli.sent == ["showversion", "showdate", "showsched", "showcpg"]
    failed = read_array(_creds(), array_cli_factory=lambda c: _Cli("d22u27_snap", fail=True),
                        wsapi_factory=lambda c: _Wsapi("d22u27_snap"))
    assert failed.read_error.startswith("Could not read 10.64.122.99: Login failed")


def test_a_plan_over_the_capture_notes_the_busy_midnight_and_the_other_schedule_on_the_set():
    from alletra_onboard.application.snapshots.plan import plan_snapshots

    plan = plan_snapshots(SnapshotIntent(requests=[_req(source="300gb", every=1, unit="days", at_hour=0)]), _d22u27())
    assert plan.blockers == []
    assert any("schedule Test. Both will run." in n for n in plan.notes)
    assert any(n.startswith("The array already starts 5 schedules at 00:00 on Sunday; 300gb_snap adds one.") for n in plan.notes)


# ------------------------------------------------------------------ R7: verify

def test_verify_counts_the_schedules_snapshots_by_name_and_parent_never_parent_alone():
    from alletra_onboard.application.snapshots.verify import check_row

    req = _req(every=4, unit="hours")
    view = _view(volumes=[
        _vol("zz_sn_vol01.261118040000", "zz_sn_vol01", created="2026-11-18T04:00:00+05:30"),
        _vol("zz_sn_vol02.261118040001", "zz_sn_vol02", created="2026-11-18T04:00:01+05:30"),
        _vol("rcpy.41.269.5", "zz_sn_vol01", created="2026-11-18T04:10:00+05:30"),       # Remote Copy's own
        _vol("zz_sn_vol01.old", "zz_sn_vol01", created="2026-11-18T04:20:00+05:30"),     # not the pattern
    ], schedules=[_sched(req)])
    row = check_row(req, view, ["zz_sn_vol01", "zz_sn_vol02"])
    assert (row.verdict, row.taken, row.next_run) == ("taking", 2, "2026-11-18 04:00:00 IST")
    # counted from the apply that made the schedule: one taken before it is not this schedule's
    later = check_row(req, view, ["zz_sn_vol01", "zz_sn_vol02"], since="2026-11-18T04:00:01+05:30")
    assert later.taken == 1


@pytest.mark.parametrize(("schedules", "detail"), [
    ([], "no schedule named zz_sn_vvs_snap on the array"),
    ("suspended", "zz_sn_vvs_snap is suspended"),
    ("other_cron", "not what was planned"),
])
def test_verify_says_why_a_schedule_is_not_scheduled(schedules, detail):
    from alletra_onboard.application.snapshots.verify import check_row

    req = _req(every=4, unit="hours")
    if schedules == "suspended":
        schedules = [_sched(req, status="suspended")]
    elif schedules == "other_cron":
        schedules = [_sched(req, cron="0 1,5,9,13,17,21 * * *")]
    row = check_row(req, _view(schedules=schedules), ["zz_sn_vol01", "zz_sn_vol02"])
    assert row.verdict == "not_scheduled" and detail in row.detail


def test_verify_says_when_another_schedule_takes_snapshots_under_the_same_names():
    from alletra_onboard.application.snapshots.verify import check_row

    req = _req(every=4, unit="hours")
    twin = ArraySchedule(**{**_sched(req).model_dump(), "name": "someone_elses"})
    row = check_row(req, _view(schedules=[_sched(req), twin]), ["zz_sn_vol01", "zz_sn_vol02"])
    assert row.verdict == "scheduled"
    assert "someone_elses also snapshots zz_sn_vvs under the same names" in row.detail


def test_verify_checks_each_snapshot_now_is_its_bases_read_only_copy_with_the_planned_expiry():
    from alletra_onboard.application.snapshots.verify import check_now

    req = _req(snapshot_now=True, expire_hours=2)
    good = _view(volumes=[
        _vol("zz_sn_vol01.initial", "zz_sn_vol01", created="2026-11-17T10:00:00+05:30", expires="2026-11-17T12:00:00+05:30"),
        _vol("zz_sn_vol02.initial", "zz_sn_vol02", created="2026-11-17T10:00:00+05:30", expires="2026-11-17T12:05:00+05:30"),
    ])
    assert check_now(req, ["zz_sn_vol01", "zz_sn_vol02"], good)[0]
    bad = _view(volumes=[
        _vol("zz_sn_vol01.initial", "zz_sn_vol01", ro=False, created="2026-11-17T10:00:00+05:30",
             expires="2026-11-17T12:00:00+05:30"),
        _vol("zz_sn_vol02.initial", "zz_sn_vol02", created="2026-11-17T10:00:00+05:30", expires="2026-11-18T10:00:00+05:30"),
    ])
    ok, detail = check_now(req, ["zz_sn_vol01", "zz_sn_vol02"], bad)
    assert not ok
    assert "zz_sn_vol01.initial is read-write" in detail and "zz_sn_vol02.initial expires" in detail


# ------------------------------------------------------------------ the step: preview and verify

def _service(tmp_path, view: SnapshotArrayView):
    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.application.service import OnboardingService
    from alletra_onboard.application.snapshots.steps import SnapshotSteps
    from alletra_onboard.config import Settings

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    reads: list[str] = []

    def read(creds, progress=None):
        reads.append(creds.host)
        return view

    service.snapshots = SnapshotSteps(service.coordinator, read_fn=read)
    return service, reads


def _run(service, requests: list[SnapshotRequest]):
    from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, RunMode

    creds = _creds()
    intent = ProvisioningIntent(array=creds, vcenter=creds, switch_f1=creds, switch_f2=creds,
                                snapshots=SnapshotIntent(requests=requests))
    item = ArrayWorkItem(
        serial_number="CZ2D320BT1", part_number="S0B84A", subscription_key=SecretStr("k"),
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1", cloudinit_url="https://169.254.0.1/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.64.122.99", mask="255.255.248.0", gateway="10.64.120.1", dns=["10.0.0.1"],
                              ntp="ntp.example.com", timezone="Asia/Kolkata"),
        dscc_setup=DsccSetupConfig(system_name="a", country="India"),
    )
    return service.create_run(item, mode=RunMode.CUSTOM, selected_steps=["snapshots"], provisioning_intent=intent)


async def _settle(service, run_id: str) -> None:
    for _ in range(200):
        task = service.coordinator._tasks.get(run_id)
        if task is None or task.done():
            return
        await asyncio.sleep(0.01)


def _last(service, run_id: str, *types: str):
    return next(e for e in reversed(service.list_events(run_id)) if e.event_type in types)


async def test_the_preview_reads_once_holds_the_plan_and_a_new_read_withdraws_it(tmp_path):
    service, reads = _service(tmp_path, _view())
    run = _run(service, [_req(snapshot_now=True, every=4, unit="hours")])
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    event = _last(service, run.run_id, "snapshots.previewed")
    plan = SnapshotPlan.model_validate(event.data["plan"])
    assert reads == ["10.64.122.99"] and plan.plan_id
    assert [(a.kind, a.state) for a in plan.actions] == [("snapshot", "create"), ("schedule", "create")]
    assert event.data["array"]["time_zone"] == "IST (Asia/Calcutta)"
    assert service.snapshots.previewed_plan(run.run_id).plan_id == plan.plan_id
    service.start_snapshots_preview(run.run_id)
    assert service.snapshots.previewed_plan(run.run_id) is None       # withdrawn at the click, LESSONS 6
    await _settle(service, run.run_id)
    assert service.snapshots.previewed_plan(run.run_id).plan_id != plan.plan_id


async def test_a_run_without_the_tab_is_refused_and_a_failed_read_is_named(tmp_path):
    from alletra_onboard.application.runs.coordinator import StepPreconditionError

    service, _ = _service(tmp_path, SnapshotArrayView(host="10.64.122.99", read_error="Could not read 10.64.122.99: boom"))
    run = _run(service, [_req(snapshot_now=True)])
    with pytest.raises(StepPreconditionError, match="read the array first"):
        service.start_snapshots_verify(run.run_id)
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    assert _last(service, run.run_id, "snapshots.preview.failed", "snapshots.previewed").event_type == "snapshots.preview.failed"
    assert service.snapshots.previewed_plan(run.run_id) is None


async def test_check_snapshots_reports_one_verdict_per_row(tmp_path):
    req = _req(every=4, unit="hours")
    view = _view(volumes=[_vol("zz_sn_vol01.261118040000", "zz_sn_vol01", created="2026-11-18T04:00:00+05:30")],
                 schedules=[_sched(req)])
    service, _ = _service(tmp_path, view)
    run = _run(service, [req])
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    service.start_snapshots_verify(run.run_id)
    await _settle(service, run.run_id)
    event = _last(service, run.run_id, "snapshots.verified", "snapshots.verify.failed")
    assert event.event_type == "snapshots.verified"
    (row,) = event.data["verification"]["rows"]
    assert (row["verdict"], row["taken"]) == ("taking", 1)


# ------------------------------------------------------------------ R8: the as-built section

def _doc_text(path) -> tuple[list[str], str]:
    doc = docx.Document(str(path))
    h1 = [p.text.strip() for p in doc.paragraphs if p.style is not None and p.style.name == "Heading 1"]
    return h1, "".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))


def test_a_run_without_the_snapshots_tab_produces_todays_document(tmp_path):
    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt

    out, _ = generate_asbuilt(AsBuiltData(customer="ACME", serial_no="CZ2D320BT1"), tmp_path / "plain.docx")
    h1, _text = _doc_text(out)
    assert "Snapshots" not in h1
    assert h1[-1] == "Provisioning performed in this run"


def test_the_section_lists_every_schedule_on_the_array_as_read(tmp_path):
    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt

    data = AsBuiltData(customer="ACME", serial_no="CZ2D320BT1", snapshots_tab=[_req(every=4, unit="hours").model_dump()],
                       snapshots_view=_d22u27())
    out, warnings = generate_asbuilt(data, tmp_path / "snap.docx")
    h1, text = _doc_text(out)
    assert h1[-1] == "Snapshots" and not any("snapshots section" in w for w in warnings)
    assert "The Snapshots step was not run in this run." in text
    table = _table_rows(out, "Minute Hour Day Month Weekday")
    assert [r[0] for r in table][:2] == ["test_CRV_snapschedule", "compactcpg_SSD_r6_sun"]
    assert len(table) == 7 and all(r[-1] == "not configured by this run" for r in table)
    assert "IST (Asia/Calcutta)" in text


def _table_rows(path, column: str) -> list[list[str]]:
    doc = docx.Document(str(path))
    for t in doc.tables:
        rows = [[c.text.strip() for c in r.cells] for r in t.rows]
        if column in rows[0]:
            return rows[1:]
    return []


def _made_by_this_run(*, twin: bool = False):
    """A run that took zz_sn_vvs's snapshots now and created its schedule; the array read afterwards."""
    from alletra_onboard.application.documents.asbuilt import AsBuiltData
    from alletra_onboard.application.snapshots.plan import plan_snapshots
    from alletra_onboard.domain.provisioning import RemovalItem
    from alletra_onboard.domain.snapshots import SnapshotOutcome, SnapshotResult

    req = _req(snapshot_now=True, every=4, unit="hours")
    plan = plan_snapshots(SnapshotIntent(requests=[req]), _view())
    result = SnapshotResult(
        started_at="2026-11-18T00:00:00+05:30", schedules_created=["zz_sn_vvs_snap"],
        outcomes=[SnapshotOutcome(kind="snapshot", name="Snapshot now zz_sn_vvs", source="zz_sn_vvs", status="created"),
                  SnapshotOutcome(kind="schedule", name="zz_sn_vvs_snap", source="zz_sn_vvs", status="created")],
        removals=[RemovalItem(kind="schedule", name="zz_sn_vvs_snap", command="removesched -f zz_sn_vvs_snap"),
                  RemovalItem(kind="snapshot", name="zz_sn_vol01.initial", command="removevv -f zz_sn_vol01.initial"),
                  RemovalItem(kind="snapshot", name="zz_sn_vol02.initial", command="removevv -f zz_sn_vol02.initial")],
        removal_notes=[("Snapshots the schedule zz_sn_vvs_snap takes expire on their own after 24 hours. To remove them "
                        "sooner, remove each with removevv -f.")],
    )
    schedules = [_sched(req), _showsched_row("Compact-Task", "compactcpg SSD_r6", "0 0,5,10,15,20 * * *")]
    if twin:
        schedules.append(ArraySchedule(**{**_sched(req).model_dump(), "name": "someone_elses"}))
    after = _view(volumes=[
        _vol("zz_sn_vol01.initial", "zz_sn_vol01", created="2026-11-18T00:00:01+05:30", expires="2026-11-19T00:00:01+05:30"),
        _vol("zz_sn_vol02.initial", "zz_sn_vol02", created="2026-11-18T00:00:01+05:30", expires="2026-11-19T00:00:01+05:30"),
        _vol("zz_sn_vol01.261118040000", "zz_sn_vol01", created="2026-11-18T04:00:00+05:30"),
        _vol("zz_sn_vol02.261117200000", "zz_sn_vol02", created="2026-11-17T20:00:00+05:30"),   # before this run
        _vol("rcpy.41.269.5", "zz_sn_vol01", created="2026-11-18T04:10:00+05:30"),             # Remote Copy's own
    ], schedules=schedules)
    return AsBuiltData(
        customer="ACME", serial_no="CZ2D320BT1", snapshots_tab=[req.model_dump(mode="json")], snapshots_view=after,
        snapshots_plan=plan.model_dump(mode="json"), snapshots_result=result.model_dump(mode="json"),
        snapshots_applies=[{"plan": plan.model_dump(mode="json"), "result": result.model_dump(mode="json")}],
        provisioning_result={"outcomes": [], "removals": []},
        provisioning_removals=[{"kind": "volume", "name": "zz_sn_vol01", "command": "removevv -f zz_sn_vol01"},
                               {"kind": "vvset", "name": "zz_sn_vvs", "command": "removevvset -f zz_sn_vvs"}],
    )


def test_the_section_records_what_the_run_made_and_removes_it_schedule_first(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt

    out, _ = generate_asbuilt(_made_by_this_run(), tmp_path / "made.docx")
    _h1, text = _doc_text(out)
    section = text.split("To remove what the Snapshots step created")[-1]
    order = ["removesched -f zz_sn_vvs_snap", "removevv -f zz_sn_vol01.initial", "removevv -f zz_sn_vol02.initial",
             "removevv -f zz_sn_vol01.261118040000"]
    assert [section.index(line) for line in order] == sorted(section.index(line) for line in order)
    assert "rcpy.41.269.5" not in section and "zz_sn_vol02.261117200000" not in section
    assert "expire on their own after 24 hours" in section
    # the provisioning block unions them, ahead of its own lines (removevv refuses a volume with snapshots)
    prov = text.split("To remove what this run created")[1].split("Path verification")[0]
    assert prov.index("removevv -f zz_sn_vol01.261118040000") < prov.index("removevvset -f zz_sn_vvs")
    assert prov.endswith("removevvset -f zz_sn_vvsremovevv -f zz_sn_vol01")      # the base volume last
    assert "snapshot schedules, snapshots, exports" in prov
    (row,) = _table_rows(out, "In words")
    assert row[:2] == ["zz_sn_vvs", "zz_sn_vvs_snap"]
    assert row[2] == "every 4 hours from 00:00, every day, kept 24 hours, read-only (configured by this run)"
    assert row[3:] == ["Active, next run 2026-11-18 04:00:00 IST", "1 snapshot(s)"]
    calls = _table_rows(out, "The CLI it equals")
    assert [c[2] for c in calls] == ["createsv -ro -exp 24h @vvname@.initial set:zz_sn_vvs",
                                     _req(snapshot_now=True, every=4, unit="hours").createsched_command()]
    schedules = {r[0]: r[-1] for r in _table_rows(out, "Minute Hour Day Month Weekday")}
    assert schedules == {"zz_sn_vvs_snap": "configured by this run", "Compact-Task": "not configured by this run"}


def test_snapshots_another_schedule_could_have_taken_get_no_removal_line(tmp_path):
    from alletra_onboard.application.documents.asbuilt import generate_asbuilt

    out, _ = generate_asbuilt(_made_by_this_run(twin=True), tmp_path / "twin.docx")
    _h1, text = _doc_text(out)
    section = text.split("To remove what the Snapshots step created")[-1]
    assert "removevv -f zz_sn_vol01.261118040000" not in text
    assert "removesched -f zz_sn_vvs_snap" in section and "removevv -f zz_sn_vol01.initial" in section
    assert ("Schedule someone_elses also takes snapshots of zz_sn_vvs under the same names as zz_sn_vvs_snap, so the "
            "two cannot be told apart: no removevv line is given for them.") in section


def test_run_records_keep_the_snapshot_plan_and_every_apply():
    from types import SimpleNamespace

    from alletra_onboard.application.documents import steps as st
    from alletra_onboard.application.documents.asbuilt import AsBuiltData

    def ev(t, data, ts):
        return SimpleNamespace(event_type=t, data=data, created_at=ts)

    events = [
        ev("snapshots.previewed", {"plan": {"actions": [], "v": 1}}, "t1"),
        ev("snapshots.apply.failed", {"result": {"outcomes": [], "error": "boom"}}, "t2"),
        ev("snapshots.previewed", {"plan": {"actions": [], "v": 2}}, "t3"),
        ev("snapshots.applied", {"result": {"outcomes": [{"kind": "snapshot"}], "error": None}}, "t4"),
    ]
    data = AsBuiltData()
    st.DocumentSteps(coord=SimpleNamespace(list_events=lambda run_id: events, list_commands=lambda run_id, since=0: []))._run_records("r1", data)
    assert data.snapshots_plan == {"actions": [], "v": 2}
    assert data.snapshots_result == {"outcomes": [{"kind": "snapshot"}], "error": None}
    assert [(a["plan"]["v"], a["result"].get("error")) for a in data.snapshots_applies] == [(1, "boom"), (2, None)]
    assert data.snapshots_applied_at == "t4"


# ------------------------------------------------------------------ R5, R6: apply and the removal set

class _ArrayWsapi:
    """An array behind the WSAPI client's snapshot calls (their names and arguments, nothing more).
    `fail` raises the array's refusal on that call (after `half` made the first member's snapshot);
    `read_write` makes every snapshot read-write whatever was asked; `rcpy` adds a Remote Copy snapshot
    of a member during the call."""

    def __init__(self, volumes, sets, *, fail: int | None = None, half: bool = False, read_write: bool = False,
                 rcpy: bool = False, unreadable_after_fail: bool = False) -> None:
        self.vols = list(volumes)
        self.sets = sets
        self.calls: list[tuple] = []
        self.fail, self.half, self.read_write, self.rcpy = fail, half, read_write, rcpy
        self.unreadable = False
        self.unreadable_after_fail = unreadable_after_fail

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def volumes(self):
        if self.unreadable:
            raise RuntimeError("WSAPI getVolumes failed: connection reset")
        return list(self.vols)

    def volume_sets(self):
        return dict(self.sets)

    def _make(self, members: list[str], name_of, read_only: bool, hours: int) -> None:
        from alletra_onboard.adapters.array.wsapi_client import WsapiError

        if len(self.calls) - 1 == self.fail:          # the call just recorded is number `fail`
            if self.half:
                self.vols.append(_vol(name_of(members[0]), members[0], ro=read_only, created="2026-11-17T10:00:00+05:30",
                                      expires="2026-11-17T12:00:00+05:30"))
            self.unreadable = self.unreadable_after_fail
            raise WsapiError("WSAPI createSnapshotOfVolumeSet failed: Max number of snapshots has been reached "
                             "(HTTP 503, code 223)")
        for m in members:
            self.vols.append(_vol(name_of(m), m, ro=read_only and not self.read_write, created="2026-11-17T10:00:00+05:30",
                                  expires=f"2026-11-17T{10 + hours:02d}:00:00+05:30"))
        if self.rcpy:
            self.vols.append(_vol("rcpy.41.269.5", members[0], created="2026-11-17T10:00:00+05:30"))

    def create_set_snapshot(self, vvset, pattern, *, read_only, expire_hours):
        self.calls.append(("set", vvset, pattern, read_only, expire_hours))
        self._make(self.sets[vvset], lambda m: pattern.replace("@vvname@", m), read_only, expire_hours)

    def create_snapshot(self, volume, name, *, read_only, expire_hours):
        self.calls.append(("volume", volume, name, read_only, expire_hours))
        self._make([volume], lambda m: name, read_only, expire_hours)


_SETS = {"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02"], "zz_sn_vvs2": ["zz_sn_vol03"]}


def _showsched_row(name: str, command: str, cron: str, status: str = "active") -> ArraySchedule:
    minute, hour, dom, month, dow = cron.split()
    return ArraySchedule(name=name, command=command, interval="0", minute=minute, hour=hour, dom=dom, month=month,
                         dow=dow, created_by="3paradm", status=status, alert="Y",
                         next_run="2026-11-18 04:00:00 IST" if status == "active" else "--")


class _Ssh:
    """An array behind SSH: `showsched` printed as the array prints it, and `createsched`. The client in
    front of it is the real ArraySnapCliClient (its form and object checks, its command log); only the
    SSH session is fake."""

    def __init__(self, schedules: list[ArraySchedule], *, refuse: str = "", suspend: bool = False,
                 touch_other: bool = False, lose_answer: bool = False, drop_before: bool = False,
                 busy_after_write: bool = False, os_10_6: bool = False) -> None:
        self.schedules = list(schedules)
        self.os_10_6 = os_10_6
        self.refuse, self.suspend, self.touch_other, self.lose_answer = refuse, suspend, touch_other, lose_answer
        self.drop_before, self.busy_after_write, self.written = drop_before, busy_after_write, False
        self.sent: list[str] = []
        self.bound: set[tuple[str, str]] = set()

    def client(self, approval, objects):
        from alletra_onboard.adapters.array.snap_cli_client import ArraySnapCliClient

        creds = approval.creds_for("snapshots", "A")
        array = self
        self.bound = set(objects.schedules)

        class _Client(ArraySnapCliClient):
            def connect(self) -> None:
                self._client = array

        return _Client(creds.host, creds.username, creds.password.get_secret_value(), objects=objects, approval=approval)

    def _showsched(self) -> str:
        if not self.schedules:
            return "No scheduled tasks listed\n"
        rows = [f"{s.name} {s.command} {s.interval} {s.minute} {s.hour} {s.dom} {s.month} {s.dow} {s.created_by} "
                f"{s.status} {s.alert} {s.next_run}" for s in self.schedules]
        head = "SchedName File/Command Interval Min Hour DOM Month DOW CreatedBy Status Alert NextRunTime"
        if self.os_10_6:        # Id first and Rebal before NextRunTime, as tests/fixtures/rack13_snap/showsched_one.txt
            rows = [f" {i} {r}".replace(f" {s.alert} {s.next_run}", f" {s.alert} Y {s.next_run}")
                    for i, (r, s) in enumerate(zip(rows, self.schedules, strict=True), start=6)]
            head = "Id " + head.replace(" NextRunTime", " Rebal NextRunTime")
        return "\n".join([head, *rows, "-" * 40, f"{len(rows)} total", ""])

    def exec_command(self, command: str, timeout=None):
        import io
        import re

        self.sent.append(command)
        out = ""
        if command == "showsched":
            out = "Error: CLI server busy, try again\n" if self.busy_after_write and self.written else self._showsched()
        elif command.startswith("createsched "):
            self.written = True
            if self.drop_before:
                raise ConnectionResetError("connection reset by peer")
            if self.refuse:
                out = self.refuse + "\n"
            else:
                m = re.match(r'^createsched -f "(.*)" "(.*)" (\S+)$', command)
                self.schedules.append(_showsched_row(m.group(3), m.group(1), m.group(2),
                                                     "suspended" if self.suspend else "active"))
                if self.touch_other:
                    self.schedules[0] = _showsched_row(self.schedules[0].name, self.schedules[0].command,
                                                       self.schedules[0].cron, "suspended")
                if self.lose_answer:
                    raise ConnectionResetError("connection reset by peer")
        return None, io.BytesIO(out.encode()), io.BytesIO(b"")

    def close(self) -> None:
        return None


def _snap_approval(creds=None):
    from alletra_onboard.domain.approval import Approval

    return Approval("test-run", "snapshots", {"A": creds or _creds()})


def _apply(requests, fake: _ArrayWsapi, volumes=None, ssh: _Ssh | None = None):
    from alletra_onboard.application.snapshots.apply import apply_plan
    from alletra_onboard.application.snapshots.plan import plan_snapshots

    ssh = ssh or _Ssh([])
    view = SnapshotArrayView(name="AlletraMP_D22U27", os_version="10.5.0", volumes=list(volumes or fake.vols),
                             vvsets=dict(fake.sets), schedules=list(ssh.schedules), cpg_free_mib={"SSD_r6": 403200})
    intent = SnapshotIntent(requests=requests)
    plan = plan_snapshots(intent, view)
    creds = _creds()
    prov = ProvisioningIntent(array=creds, vcenter=creds, switch_f1=creds, switch_f2=creds, snapshots=intent)
    return plan, apply_plan(plan, view, prov, _snap_approval(creds), wsapi_factory=lambda a, p, s: fake, snap_cli_factory=ssh.client)


def _base():
    return [_vol("zz_sn_vol01"), _vol("zz_sn_vol02"), _vol("zz_sn_vol03")]


def test_apply_takes_each_snapshot_now_in_order_and_removes_only_what_it_made():
    fake = _ArrayWsapi(_base(), _SETS, rcpy=True)
    _plan, result = _apply([_req(snapshot_now=True, expire_hours=2), _req(source="zz_sn_vol03", kind="volume",
                                                                          snapshot_now=True, expire_hours=2)], fake)
    assert result.error is None
    assert fake.calls == [("set", "zz_sn_vvs", "@vvname@.initial", True, 2),
                          ("volume", "zz_sn_vol03", "zz_sn_vol03.initial", True, 2)]
    assert [o.status for o in result.outcomes] == ["created", "created"]
    # Remote Copy's rcpy.41.269.5 appeared during the write, copyOf a member: never in the removal set
    assert [r.command for r in result.removals] == [
        "removevv -f zz_sn_vol01.initial", "removevv -f zz_sn_vol02.initial", "removevv -f zz_sn_vol03.initial"]


def test_a_set_whose_members_partly_have_their_snapshot_takes_only_the_missing_ones():
    have = _vol("zz_sn_vol01.initial", "zz_sn_vol01", created="2026-11-16T10:00:00+05:30", expires="2026-11-16T12:00:00+05:30")
    fake = _ArrayWsapi([*_base(), have], _SETS)
    _plan, result = _apply([_req(snapshot_now=True, expire_hours=2)], fake)
    assert result.error is None
    assert fake.calls == [("volume", "zz_sn_vol02", "zz_sn_vol02.initial", True, 2)]
    assert [r.name for r in result.removals] == ["zz_sn_vol02.initial"]      # the one that was there stays


def test_apply_stops_at_the_first_refusal_and_the_removal_set_covers_the_half_made_write():
    fake = _ArrayWsapi(_base(), _SETS, fail=0, half=True)
    _plan, result = _apply([_req(snapshot_now=True, expire_hours=2), _req(source="zz_sn_vvs2", snapshot_now=True,
                                                                          expire_hours=2)], fake)
    assert len(fake.calls) == 1                                       # the second row is never written
    assert "Max number of snapshots has been reached (HTTP 503, code 223)" in result.error
    assert [(o.source, o.status) for o in result.outcomes] == [("zz_sn_vvs", "failed")]
    assert [r.name for r in result.removals] == ["zz_sn_vol01.initial"]


def test_a_read_back_that_does_not_show_what_was_asked_stops_apply():
    fake = _ArrayWsapi(_base(), _SETS, read_write=True)
    _plan, result = _apply([_req(snapshot_now=True, expire_hours=2), _req(source="zz_sn_vvs2", snapshot_now=True,
                                                                          expire_hours=2)], fake)
    assert len(fake.calls) == 1
    assert "does not show what was asked" in result.error and "zz_sn_vol01.initial is read-write" in result.error
    assert [r.name for r in result.removals] == ["zz_sn_vol01.initial", "zz_sn_vol02.initial"]


def test_when_the_array_cannot_be_read_after_a_failed_write_the_names_to_check_are_given():
    fake = _ArrayWsapi(_base(), _SETS, fail=0, half=True, unreadable_after_fail=True)
    _plan, result = _apply([_req(snapshot_now=True, expire_hours=2)], fake)
    assert result.removals == []
    assert result.removal_notes == [(
        "The array was not read after the snapshot of zz_sn_vvs failed. Check with showvv zz_sn_vol01.initial "
        "zz_sn_vol02.initial; remove with removevv -f each one that was not there before this run.")]


def test_whole_set_snapshot_refuses_when_set_membership_changed_after_preview():
    """Astra 6: a member added to a volume set after preview must not get an unreviewed snapshot
    from a whole-set call; apply re-reads live membership and refuses with a plain message."""
    from alletra_onboard.application.snapshots.apply import apply_plan
    from alletra_onboard.application.snapshots.plan import plan_snapshots

    fake = _ArrayWsapi(_base(), {"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02"]})
    view = SnapshotArrayView(name="AlletraMP_D22U27", os_version="10.5.0", volumes=list(fake.vols),
                             vvsets=dict(fake.sets), schedules=[], cpg_free_mib={"SSD_r6": 403200})
    intent = SnapshotIntent(requests=[_req(snapshot_now=True, expire_hours=2)])
    plan = plan_snapshots(intent, view)
    creds = _creds()
    prov = ProvisioningIntent(array=creds, vcenter=creds, switch_f1=creds, switch_f2=creds, snapshots=intent)

    # Another volume is added to the set on the array after the operator reviewed the preview.
    fake.sets = {"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02", "zz_sn_vol03"]}
    result = apply_plan(plan, view, prov, _snap_approval(creds), wsapi_factory=lambda a, p, s: fake, snap_cli_factory=_Ssh([]).client)

    assert fake.calls == []                                              # zero writes sent
    assert result.error is not None
    assert "volume set zz_sn_vvs changed on the array since the preview — no snapshot of it was taken" in result.error
    assert "read the array again" in result.error.lower()
    assert result.removals == []
    assert result.removal_notes == []
    assert [(o.source, o.status) for o in result.outcomes] == [("zz_sn_vvs", "failed")]


def test_whole_set_snapshot_succeeds_in_one_call_when_set_membership_is_unchanged():
    """Astra 6: when live set membership matches the preview, apply still takes one whole-set snapshot."""
    from alletra_onboard.application.snapshots.apply import apply_plan
    from alletra_onboard.application.snapshots.plan import plan_snapshots

    fake = _ArrayWsapi(_base(), {"zz_sn_vvs": ["zz_sn_vol01", "zz_sn_vol02"]})
    view = SnapshotArrayView(name="AlletraMP_D22U27", os_version="10.5.0", volumes=list(fake.vols),
                             vvsets=dict(fake.sets), schedules=[], cpg_free_mib={"SSD_r6": 403200})
    intent = SnapshotIntent(requests=[_req(snapshot_now=True, expire_hours=2)])
    plan = plan_snapshots(intent, view)
    creds = _creds()
    prov = ProvisioningIntent(array=creds, vcenter=creds, switch_f1=creds, switch_f2=creds, snapshots=intent)

    result = apply_plan(plan, view, prov, _snap_approval(creds), wsapi_factory=lambda a, p, s: fake, snap_cli_factory=_Ssh([]).client)

    assert result.error is None
    assert fake.calls == [("set", "zz_sn_vvs", "@vvname@.initial", True, 2)]
    assert [(o.source, o.status) for o in result.outcomes] == [("zz_sn_vvs", "created")]
    assert [r.name for r in result.removals] == ["zz_sn_vol01.initial", "zz_sn_vol02.initial"]


# ------------------------------------------------------------------ R5, R6: schedules over the write client (ADR 0016)

@pytest.mark.parametrize("os_10_6", [False, True])
def test_the_schedule_goes_through_the_bound_client_after_the_snapshots_and_is_read_back(os_10_6):
    others = [_showsched_row("Compact-Task", "compactcpg SSD_r6", "0 0,5,10,15,20 * * *")]
    ssh = _Ssh(others, os_10_6=os_10_6)
    _plan, result = _apply([_req(snapshot_now=True, every=4, unit="hours", expire_hours=24)], _ArrayWsapi(_base(), _SETS),
                           ssh=ssh)
    assert result.error is None
    req = _req(snapshot_now=True, every=4, unit="hours", expire_hours=24)
    assert ssh.sent == ["showsched", req.createsched_command(), "showsched"]
    assert ssh.bound == {("zz_sn_vvs_snap", "set:zz_sn_vvs")}                # the plan's pair, nothing else
    assert [(o.kind, o.status) for o in result.outcomes] == [("snapshot", "created"), ("schedule", "created")]
    assert result.schedules_created == ["zz_sn_vvs_snap"]
    assert [r.command for r in result.removals] == [
        "removesched -f zz_sn_vvs_snap", "removevv -f zz_sn_vol01.initial", "removevv -f zz_sn_vol02.initial"]
    assert result.removal_notes == [("Snapshots the schedule zz_sn_vvs_snap takes expire on their own after 24 hours. "
                                     "To remove them sooner, remove each with removevv -f.")]


def test_a_write_whose_answer_is_lost_keeps_its_removal_line_when_the_schedule_is_there():
    """ADR 0025 condition 4: the line goes in before the command, so a write that half-works is covered."""
    ssh = _Ssh([], lose_answer=True)
    _plan, result = _apply([_req(every=4, unit="hours")], _ArrayWsapi(_base(), _SETS), ssh=ssh)
    assert "failed: ConnectionResetError" in result.error
    assert ssh.sent[-1] == "showsched" and len(ssh.sent) == 3          # read again, in the same session
    assert [r.command for r in result.removals] == ["removesched -f zz_sn_vvs_snap"]
    assert result.removal_notes == []
    assert [(o.kind, o.status) for o in result.outcomes] == [("schedule", "failed")]


def test_a_write_lost_before_the_array_acted_drops_the_line_after_reading_it_absent():
    ssh = _Ssh([], drop_before=True)
    _plan, result = _apply([_req(every=4, unit="hours")], _ArrayWsapi(_base(), _SETS), ssh=ssh)
    assert "failed: ConnectionResetError" in result.error
    assert ssh.sent[-1] == "showsched" and ssh.schedules == []
    assert result.removals == []


def test_a_showsched_that_answers_an_error_is_never_read_as_no_schedule():
    """parse_showsched makes an error an empty list; read as "absent", it would drop the line of a
    schedule that is running."""
    ssh = _Ssh([], busy_after_write=True)
    _plan, result = _apply([_req(every=4, unit="hours")], _ArrayWsapi(_base(), _SETS), ssh=ssh)
    assert "showsched could not be read after creating zz_sn_vvs_snap; it answered: Error: CLI server busy" in result.error
    assert [s.name for s in ssh.schedules] == ["zz_sn_vvs_snap"]
    assert [r.command for r in result.removals] == ["removesched -f zz_sn_vvs_snap"]
    assert result.removal_notes == [(
        "The array was not read after the schedule zz_sn_vvs_snap failed. Check with showsched zz_sn_vvs_snap; if it "
        "is not there, skip its removesched line.")]


def test_the_arrays_refusal_stops_apply_and_drops_the_line_of_a_schedule_never_made():
    ssh = _Ssh([], refuse="Error: The schedule format is <minute> <hour> <dom> <month> <dow>")
    _plan, result = _apply([_req(every=4, unit="hours")], _ArrayWsapi(_base(), _SETS), ssh=ssh)
    assert "the array refused createsched for zz_sn_vvs_snap: Error: The schedule format is" in result.error
    assert result.removals == []


@pytest.mark.parametrize(("change", "says"), [
    ("suspend", "zz_sn_vvs_snap is suspended, not active"),
    ("touch_other", "the schedule Compact-Task that was on the array before is not as it was"),
])
def test_a_read_back_that_is_not_what_was_planned_stops_apply(change, says):
    ssh = _Ssh([_showsched_row("Compact-Task", "compactcpg SSD_r6", "0 0,5,10,15,20 * * *")], **{change: True})
    _plan, result = _apply([_req(every=4, unit="hours"), _req(source="zz_sn_vvs2", every=4, unit="hours")],
                           _ArrayWsapi(_base(), _SETS), ssh=ssh)
    assert says in result.error
    assert sum(1 for c in ssh.sent if c.startswith("createsched")) == 1      # the second row is never written
    assert [r.command for r in result.removals] == ["removesched -f zz_sn_vvs_snap"]


def test_the_client_gets_only_the_schedules_the_plan_creates():
    from alletra_onboard.application.snapshots.apply import plan_objects
    from alletra_onboard.application.snapshots.plan import plan_snapshots

    there = _req(source="zz_sn_vol03", kind="volume", every=1, unit="days")
    view = _view(volumes=[_vol("zz_sn_vol03")], schedules=[_sched(there)])
    intent = SnapshotIntent(requests=[_req(every=4, unit="hours"), there])
    plan = plan_snapshots(intent, view)
    assert [(a.name, a.state) for a in plan.actions] == [("zz_sn_vvs_snap", "create"), ("zz_sn_vol03_snap", "exists")]
    assert plan_objects(plan, intent).schedules == frozenset({("zz_sn_vvs_snap", "set:zz_sn_vvs")})


# ------------------------------------------------------------------ the step: approval, 409, spent approval

async def test_apply_needs_the_ticked_plan_and_a_plan_without_blockers(tmp_path):
    from functools import partial

    from alletra_onboard.application.runs.coordinator import StepPreconditionError
    from alletra_onboard.application.snapshots.apply import apply_plan
    from alletra_onboard.application.snapshots.steps import SnapshotSteps

    fake = _ArrayWsapi(_base(), _SETS)
    view = SnapshotArrayView(name="AlletraMP_D22U27", os_version="10.5.0", volumes=list(fake.vols), vvsets=dict(_SETS))
    service, _ = _service(tmp_path, view)
    def checked_wsapi(approval, purpose, side):
        assert approval.creds_for(purpose, side).host == "10.64.122.99"
        return fake

    service.snapshots = SnapshotSteps(service.coordinator, read_fn=lambda creds, progress=None: view.model_copy(
        update={"volumes": fake.volumes()}), apply_fn=partial(apply_plan, wsapi_factory=checked_wsapi, snap_cli_factory=_Ssh([]).client))
    run = _run(service, [_req(snapshot_now=True, expire_hours=2)])
    with pytest.raises(StepPreconditionError, match="read the array first"):
        service.start_snapshots_apply(run.run_id, approved_plan="x")
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    first = service.snapshots.previewed_plan(run.run_id).plan_id
    with pytest.raises(StepPreconditionError, match="Tick the approval for this plan first."):
        service.start_snapshots_apply(run.run_id, approved_plan=None)
    with pytest.raises(StepPreconditionError, match="The plan changed since it was approved"):
        service.start_snapshots_apply(run.run_id, approved_plan="an older plan")
    service.start_snapshots_apply(run.run_id, approved_plan=first)
    await _settle(service, run.run_id)
    assert fake.calls and _last(service, run.run_id, "snapshots.applied", "snapshots.apply.failed").event_type == "snapshots.applied"
    assert _last(service, run.run_id, "snapshots.verified", "snapshots.verify.failed").event_type == "snapshots.verified"
    with pytest.raises(StepPreconditionError, match="read the array first"):     # the approval is spent
        service.start_snapshots_apply(run.run_id, approved_plan=first)
    # a second read finds them: nothing to create
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    again = service.snapshots.previewed_plan(run.run_id)
    assert [a.state for a in again.actions] == ["exists"]
    with pytest.raises(StepPreconditionError, match="nothing to create"):
        service.start_snapshots_apply(run.run_id, approved_plan=again.plan_id)


def test_the_apply_route_answers_409_on_a_blocker(tmp_path):
    from fastapi.testclient import TestClient

    from alletra_onboard.api.app import create_app

    service, _ = _service(tmp_path, _view())
    run = _run(service, [_req(snapshot_now=True, retain_hours=8)])              # Lock for: a blocker
    plan = SnapshotPlan(blockers=["zz_sn_vvs: Lock for is not offered yet."], plan_id="p1")
    service.snapshots._plan[run.run_id] = (plan, _view())
    with TestClient(create_app(service)) as client:
        refused = client.post(f"/runs/{run.run_id}/snapshots/apply", json={"approved_plan": "p1"})
    assert refused.status_code == 409 and "Lock for is not offered yet" in refused.json()["detail"]


def test_a_set_schedule_holding_the_rows_volume_is_a_twin_too(tmp_path):
    """Names are `<member>.` and twelve digits whichever schedule took them: a schedule on a set that
    holds this row's volume makes the same names, so its snapshots get no removal line."""
    from alletra_onboard.application.documents.asbuilt import AsBuiltData
    from alletra_onboard.application.documents.asbuilt_snapshots import snapshot_removal_items
    from alletra_onboard.application.snapshots.verify import check_row
    from alletra_onboard.domain.snapshots import SnapshotResult

    req = _req(source="zz_sn_vol01", kind="volume", every=4, unit="hours")
    pol = _showsched_row("Pol-999", f"createsv -f -ro -exp 24h {PATTERN} set:zz_sn_vvs", "0 * * * *")
    view = _view(volumes=[_vol("zz_sn_vol01.261118010000", "zz_sn_vol01", created="2026-11-18T01:00:00+05:30")],
                 schedules=[_sched(req), pol])
    row = check_row(req, view, ["zz_sn_vol01"])
    assert "Schedule Pol-999 also snapshots zz_sn_vol01 under the same names" in row.detail
    result = SnapshotResult(started_at="2026-11-18T00:00:00+05:30", schedules_created=[req.name])
    data = AsBuiltData(snapshots_tab=[req.model_dump(mode="json")], snapshots_view=view,
                       snapshots_applies=[{"plan": None, "result": result.model_dump(mode="json")}])
    assert snapshot_removal_items(data) == []


def test_a_showsched_that_is_not_its_table_fails_the_read():
    class _Busy(_Cli):
        def run(self, command: str, timeout=None) -> str:
            return "Error: CLI server busy, try again\n" if command == "showsched" else super().run(command, timeout)

    view = read_array(_creds(), array_cli_factory=lambda c: _Busy("d22u27_snap"), wsapi_factory=lambda c: _Wsapi("d22u27_snap"))
    assert view.read_error == ("Could not read 10.64.122.99: showsched did not list the schedules; it answered: "
                               "Error: CLI server busy, try again")


async def test_the_page_reads_the_tab_in_words_and_whether_the_plan_is_still_held(tmp_path):
    from fastapi.testclient import TestClient

    from alletra_onboard.api.app import create_app

    service, _ = _service(tmp_path, _view())
    run = _run(service, [_req(snapshot_now=True, every=4, unit="hours"), _req(source="zz_sn_vol03", kind="volume",
                                                                             snapshot_now=True, expire_hours=2)])
    client = TestClient(create_app(service))
    before = client.get(f"/runs/{run.run_id}/snapshots").json()
    assert before == {"rows": [
        {"source": "zz_sn_vvs", "kind": "set", "schedule": "zz_sn_vvs_snap",
         "summary": "Snapshot now · every 4 hours from 00:00, every day, kept 24 hours, read-only"},
        {"source": "zz_sn_vol03", "kind": "volume", "schedule": "", "summary": "Snapshot now · kept 2 hours, read-only"},
    ], "held_plan_id": ""}
    service.start_snapshots_preview(run.run_id)
    await _settle(service, run.run_id)
    held = client.get(f"/runs/{run.run_id}/snapshots").json()["held_plan_id"]
    assert held and held == _last(service, run.run_id, "snapshots.previewed").data["plan"]["plan_id"]
