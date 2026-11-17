"""BL-55 — a volume size the array cannot take is refused on the sheet and in the plan.

Live on rack13-ARCUS (OS 10.6.0), 2026-11-16: a 1 PiB volume passed the sheet and the plan, and only the
array refused it (HTTP 400 code 28, "client request contains value that is too large"). The limit comes
from the array's own `help createvv`, captured on rack13-ARCUS 2026-11-17
(tests/fixtures/rack13_snap/help_createvv.txt): 64 TiB for thin and for reduced volumes. The mechanism is
pinned with a stand-in limit; the last tests pin the captured one.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
from alletra_onboard.domain import provisioning
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.provisioning import ArrayVolumeRecord, VolumeRequest
from tests.unit.test_init_sheet import _PROV_TARGETS, _fill_tabs
from tests.unit.test_plan_truth import TruthfulFakeWsapi, _intent, _plan, _row

FIX = Path(__file__).resolve().parents[1] / "fixtures"
ONE_PIB_GIB = 1024 * 1024          # the size rack13-ARCUS refused on 2026-11-16
STAND_IN_GIB = 2048                # not the array's limit: a value to exercise the check with


def _sheet(size_gib: int):
    prov = {"targets": _PROV_TARGETS, "volumes": [{"name": "zz_big", "size_gib": str(size_gib)}],
            "hostsets": [{"name": "hs"}]}
    return parse_workbook_bytes(_fill_tabs({"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.122.140"}, prov),
                                mode=RunMode.PROVISION_ONLY).provisioning_intent


def _big_plan(size_gib: int, *, on_array=()):
    intent = _intent(volumes=[VolumeRequest(name="vol01", size_gib=size_gib, cpg="SSD_r6", vvset="vvs")])
    return _plan(TruthfulFakeWsapi(volumes=on_array), intent)


@pytest.fixture
def stand_in_limit(monkeypatch):
    monkeypatch.setattr(provisioning, "VOLUME_MAX_GIB", STAND_IN_GIB)


# ------------------------------------------------------------------ the mechanism, with a stand-in limit

def test_without_a_captured_limit_nothing_is_refused(monkeypatch):
    """With no limit set, the 1 PiB volume of 2026-11-16 passes, and the array has the last word."""
    monkeypatch.setattr(provisioning, "VOLUME_MAX_GIB", None)
    assert _sheet(ONE_PIB_GIB).volumes[0].size_gib == ONE_PIB_GIB
    plan = _big_plan(ONE_PIB_GIB)
    assert _row(plan, "volume", "vol01").state == "create" and plan.blockers == []


def test_the_sheet_refuses_a_volume_over_the_limit_with_a_sentence(stand_in_limit):
    assert _sheet(STAND_IN_GIB).volumes[0].size_gib == STAND_IN_GIB
    with pytest.raises(ValueError) as exc:
        _sheet(STAND_IN_GIB + 1)
    assert str(exc.value) == (
        f"Volume 'zz_big' — Size (GiB): {STAND_IN_GIB + 1} GiB is more than the array can create in one volume, "
        f"at most {STAND_IN_GIB} GiB. Make it smaller.")


def test_the_plan_blocks_a_new_volume_over_the_limit(stand_in_limit):
    plan = _big_plan(STAND_IN_GIB + 1)
    row = _row(plan, "volume", "vol01")
    assert row.state == "conflict"
    assert row.reason == (f"{STAND_IN_GIB + 1} GiB is more than the array can create in one volume, at most "
                          f"{STAND_IN_GIB} GiB. Make it smaller on the sheet's Volumes tab.")
    assert plan.blockers == [f"volume vol01: {row.reason}"]
    assert _row(_big_plan(STAND_IN_GIB), "volume", "vol01").state == "create"


def test_a_volume_already_on_the_array_is_judged_as_before(stand_in_limit):
    """The limit is about what the array can create; one it already holds is compared, not refused."""
    found = ArrayVolumeRecord(name="vol01", size_mib=(STAND_IN_GIB + 1) * 1024, cpg="SSD_r6", provisioning_type="tpvv")
    row = _row(_big_plan(STAND_IN_GIB + 1, on_array=[found]), "volume", "vol01")
    assert row.state == "exists" and "matches" in row.reason


# ------------------------------------------------------------------ the real limit, once captured

def test_the_arrays_createvv_help_is_captured_and_its_limit_is_set():
    """Set VOLUME_MAX_GIB to the size the captured page states; never edit the capture to fit."""
    pages = sorted(FIX.glob("**/help_createvv.txt"))
    assert pages, "no help_createvv.txt under tests/fixtures/"
    assert all("createvv" in page.read_text() for page in pages)
    assert isinstance(provisioning.VOLUME_MAX_GIB, int) and provisioning.VOLUME_MAX_GIB > 0


def test_the_one_pib_volume_of_2026_11_16_is_refused_on_the_sheet():
    with pytest.raises(ValueError, match="more than the array can create in one volume"):
        _sheet(ONE_PIB_GIB)


def test_the_one_pib_volume_of_2026_11_16_is_blocked_in_the_plan():
    plan = _big_plan(ONE_PIB_GIB)
    assert _row(plan, "volume", "vol01").state == "conflict" and len(plan.blockers) == 1


def test_exactly_64_tib_passes_and_one_gib_more_is_refused():
    assert _sheet(64 * 1024).volumes[0].size_gib == 64 * 1024
    with pytest.raises(ValueError, match="more than the array can create in one volume"):
        _sheet(64 * 1024 + 1)
