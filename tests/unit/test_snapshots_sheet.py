"""SPEC-023 R1/R2 — the Snapshots tab: parsed only when filled, one sentence per validation rule, the
step refused without it. Back-compat: a workbook without the tab parses exactly as before. Written
2026-11-16 as expected failures; built 2026-11-17 (docs/workpackets/BL-21.md step 4)."""

import io

import pytest
from openpyxl import load_workbook

from alletra_onboard.application.platform.init_sheet import (
    compose_workbook_bytes,
    parse_workbook_bytes,
)
from alletra_onboard.domain.models import RunMode

_INIT = {"serial_number": "CZ2D320BT1", "mgmt_ipv4": "10.64.122.99"}
_TARGETS = {
    "prov_array_host": "10.64.122.99", "prov_array_user": "3paradm", "prov_array_password": "pw",
    "prov_vcenter_host": "vc.example.net", "prov_vcenter_user": "administrator@vsphere.local",
    "prov_vcenter_password": "vpw",
}
_VOLUMES = [
    {"name": "zz_sn_vol01", "size_gib": "1", "vvset": "zz_sn_vvs"},
    {"name": "zz_sn_vol02", "size_gib": "1", "vvset": "zz_sn_vvs"},
]
_HOSTSETS = [{"name": "zz_sn_hs", "members": "esx1"}]
_SNAP_STEPS = ["discover", "provision", "snapshots", "verify", "asbuilt"]


def _sheet(rows: list[dict[str, str]] | None) -> bytes:
    return compose_workbook_bytes(
        base=None, init=_INIT, targets=_TARGETS, volumes=_VOLUMES, hostsets=_HOSTSETS, snapshots=rows,
    )


def _parse(rows, *, mode=RunMode.CUSTOM, steps=None):
    return parse_workbook_bytes(_sheet(rows), mode=mode, selected_steps=steps or _SNAP_STEPS)


def _row(**kw) -> dict[str, str]:
    row = {"source": "zz_sn_vvs", "snapshot_now": "yes", "expire_hours": "24"}
    row.update(kw)
    return row


# ------------------------------------------------------------------ template + back-compat

def test_the_template_has_the_snapshots_tab_and_the_initialisation_accelerator_does_not():
    from alletra_onboard.application.platform.init_sheet import (
        SNAPSHOT_COLUMNS,
        SNAPSHOTS_SHEET_NAME,
        build_template_bytes,
    )

    wb = load_workbook(io.BytesIO(build_template_bytes()))
    assert SNAPSHOTS_SHEET_NAME == "Snapshots"
    texts = {str(c.value).strip().removesuffix("*").strip()
             for row in wb[SNAPSHOTS_SHEET_NAME].iter_rows() for c in row if c.value}
    for _, label, _ in SNAPSHOT_COLUMNS:
        assert label in texts
    assert SNAPSHOTS_SHEET_NAME not in load_workbook(io.BytesIO(build_template_bytes(init_only=True))).sheetnames


def test_a_workbook_without_the_tab_parses_as_before_with_no_snapshots():
    wb = load_workbook(io.BytesIO(_sheet(None)))
    del wb["Snapshots"]
    older = io.BytesIO()
    wb.save(older)
    parsed = parse_workbook_bytes(older.getvalue(), mode=RunMode.PROVISION_ONLY)
    assert parsed.provisioning_intent.snapshots is None


def test_a_blank_tab_is_not_an_error_when_the_step_is_not_chosen():
    parsed = parse_workbook_bytes(_sheet([]), mode=RunMode.PROVISION_ONLY)
    assert parsed.provisioning_intent.snapshots is None


def test_the_snapshots_step_refuses_a_workbook_whose_tab_is_blank():
    with pytest.raises(ValueError, match="The Snapshots step needs the 'Snapshots' tab"):
        _parse([])


# ------------------------------------------------------------------ R1: defaults

def test_a_filled_row_parses_with_its_defaults():
    parsed = _parse([_row(every="4", unit="hours")])
    (req,) = parsed.provisioning_intent.snapshots.requests
    assert (req.source, req.kind, req.snapshot_now) == ("zz_sn_vvs", "set", True)
    assert (req.every, req.unit, req.at_hour, req.days) == (4, "hours", 0, [])
    assert (req.expire_hours, req.retain_hours, req.read_only) == (24, None, True)
    assert req.name == "zz_sn_vvs_snap"


def test_days_are_read_as_numbers_with_sunday_zero():
    parsed = _parse([_row(every="1", unit="days", at_hour="23", days="Mon, tue,WEDNESDAY, sun")])
    assert parsed.provisioning_intent.snapshots.requests[0].days == [0, 1, 2, 3]


def test_a_set_already_on_the_array_may_be_named():
    parsed = _parse([_row(source="existing_vvs")])
    assert parsed.provisioning_intent.snapshots.requests[0].source == "existing_vvs"


# ------------------------------------------------------------------ R2: one sentence per rule

_P = "Snapshots tab — row 'zz_sn_vvs'"


@pytest.mark.parametrize(("rows", "sentence"), [
    ([_row(), _row()], f"{_P} appears twice; one row per volume set or volume."),
    ([_row(kind="lun")], f"{_P}: Kind must be 'set' or 'volume' (got 'lun')."),
    ([_row(snapshot_now="no")], f"{_P} asks for nothing: set Snapshot now to yes, or fill Every and Unit."),
    ([_row(every="4")], f"{_P}: Every and Unit go together; fill both or neither."),
    ([_row(unit="hours")], f"{_P}: Every and Unit go together; fill both or neither."),
    ([_row(every="5", unit="hours")],
     (f"{_P}: every 5 hours is not a period the array schedules; use 15, 20 or 30 minutes, "
      "1, 2, 3, 4, 6, 8 or 12 hours, or 1 day.")),
    ([_row(every="15", unit="minutes", at_hour="2")],
     f"{_P}: Start hour applies to hours and days; leave it blank for a schedule in minutes."),
    ([_row(every="1", unit="days", at_hour="24")], f"{_P}: Start hour must be a whole number from 0 to 23 (got '24')."),
    ([_row(days="mon")], f"{_P}: Days applies to a schedule; fill Every and Unit, or leave Days blank."),
    ([_row(every="1", unit="days", days="mon, funday")],
     f"{_P}: Days must be day names separated by commas, such as mon, tue (got 'mon, funday')."),
    ([_row(expire_hours="")], f"{_P}: Keep for must be a whole number of hours from 1 to 43800."),
    ([_row(expire_hours="1.5")], f"{_P}: Keep for must be a whole number of hours from 1 to 43800."),
    ([_row(expire_hours="43801")], f"{_P}: Keep for must be a whole number of hours from 1 to 43800."),
    ([_row(retain_hours="0")], f"{_P}: Lock for must be a whole number of hours from 1 to 43800, or blank."),
    ([_row(retain_hours="48")], f"{_P}: Lock for cannot be longer than Keep for; the array refuses it."),
    ([_row(every="4", unit="hours", schedule_name="my sched")],
     f"{_P}: Schedule name may use letters, digits, '.', '_' and '-' only, up to 31 characters."),
    ([_row(every="4", unit="hours", schedule_name="nightly"),
      _row(source="other_vvs", every="4", unit="hours", schedule_name="nightly")],
     "Snapshots tab — row 'other_vvs': schedule name 'nightly' is used by two rows."),
    ([_row(read_only="maybe")], f"{_P}: Read-only must be 'yes' or 'no' (got 'maybe')."),
])
def test_each_rule_refuses_with_its_sentence(rows, sentence):
    with pytest.raises(ValueError) as caught:
        _parse(rows)
    assert str(caught.value) == sentence


def test_a_run_with_the_snapshots_step_is_refused_without_the_tab(tmp_path):
    """R2's last sentence also holds when the run is minted (HTTP 422 from POST /runs/from-sheet)."""
    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.runs.coordinator import RunCoordinator
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.config import Settings

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    coord = RunCoordinator(Settings(), store, InMemoryEventBus())
    without = parse_workbook_bytes(_sheet([]), mode=RunMode.PROVISION_ONLY)
    with pytest.raises(ValueError, match="The Snapshots step needs the 'Snapshots' tab"):
        coord.create_run(without.work_item, mode=RunMode.CUSTOM, selected_steps=_SNAP_STEPS,
                         provisioning_intent=without.provisioning_intent)
    filled = _parse([_row(every="4", unit="hours")])
    run = coord.create_run(filled.work_item, mode=RunMode.CUSTOM, selected_steps=_SNAP_STEPS,
                           provisioning_intent=filled.provisioning_intent)
    assert store.get_provisioning_intent(run.run_id).snapshots.requests[0].name == "zz_sn_vvs_snap"


def test_a_workbook_that_only_snapshots_sets_on_the_array_may_leave_volumes_empty():
    sheet = compose_workbook_bytes(base=None, init=_INIT, targets=_TARGETS, volumes=[], hostsets=[],
                                   snapshots=[_row(source="existing_vvs")])
    parsed = parse_workbook_bytes(sheet, mode=RunMode.CUSTOM, selected_steps=["snapshots", "asbuilt"])
    assert parsed.provisioning_intent.volumes == []
    assert parsed.provisioning_intent.snapshots.requests[0].source == "existing_vvs"


def test_a_schedule_name_starting_with_a_dash_is_refused():
    with pytest.raises(ValueError, match="Schedule name cannot start with '-'"):
        _parse([_row(every="4", unit="hours", schedule_name="-run_once")])
