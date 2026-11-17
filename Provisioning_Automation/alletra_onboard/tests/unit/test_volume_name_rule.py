"""A volume name the array refuses is refused on the sheet and in the plan, before any write.

Live on rack13-ARCUS (OS 10.6.0), 2026-11-17: `zz_bl45_vol02+` passed the sheet and the plan, and the array
refused it only at apply ("illegal character in input", HTTP 400 code 69), after three other objects were
made. The rule is the array's own `help createvv` (tests/fixtures/rack13_snap/help_createvv.txt).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.provisioning import VolumeRequest
from tests.unit.test_init_sheet import _PROV_TARGETS, _fill_tabs
from tests.unit.test_plan_truth import TruthfulFakeWsapi, _intent, _plan, _row

HELP_CREATEVV = Path(__file__).resolve().parents[1] / "fixtures" / "rack13_snap" / "help_createvv.txt"


def _sheet(name: str):
    prov = {"targets": _PROV_TARGETS, "volumes": [{"name": name, "size_gib": "1"}], "hostsets": [{"name": "hs"}]}
    return parse_workbook_bytes(_fill_tabs({"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.122.140"}, prov),
                                mode=RunMode.PROVISION_ONLY).provisioning_intent


def _name_plan(name: str):
    intent = _intent(volumes=[VolumeRequest(name=name, size_gib=1, cpg="SSD_r6", vvset="vvs")])
    return _plan(TruthfulFakeWsapi(), intent)


def test_the_rule_is_the_one_the_arrays_help_states():
    text = " ".join(HELP_CREATEVV.read_text().split())
    assert ("Specifies a VV name up to 255 characters in length. Valid characters include alphanumeric "
            "characters, periods, dashes, and underscores.") in text


def test_the_name_the_array_refused_on_2026_11_17_is_refused_on_the_sheet():
    with pytest.raises(ValueError) as err:
        _sheet("zz_bl45_vol02+")
    assert str(err.value) == ("Volume 'zz_bl45_vol02+' — Name: the array takes only letters, digits, '.', '-' and '_' "
                              "in a volume name, not '+'. Rename it.")


@pytest.mark.parametrize("name, why", [
    ("my vol", "not a space"),
    ("vol/01", "not '/'"),
    ("völ01", "not 'ö'"),
    ("v" * 256, "at most 255 characters in a volume name, this one has 256"),
])
def test_other_names_the_help_rules_out_are_refused(name, why):
    with pytest.raises(ValueError, match=why):
        _sheet(name)


def test_letters_digits_periods_dashes_and_underscores_up_to_255_pass():
    assert _sheet("Vol-01.a_b").volumes[0].name == "Vol-01.a_b"
    assert _sheet("v" * 255).volumes[0].name == "v" * 255


def test_the_plan_blocks_a_new_volume_with_a_name_the_array_refuses():
    """For a volume that did not come through the sheet (the page's composition)."""
    plan = _name_plan("zz_bl45_vol02+")
    row = _row(plan, "volume", "zz_bl45_vol02+")
    assert row.state == "conflict" and len(plan.blockers) == 1
    assert "not '+'. Rename it on the sheet's Volumes tab." in row.reason


def test_the_plan_creates_a_new_volume_with_a_good_name():
    plan = _name_plan("zz_bl45_vol02")
    assert _row(plan, "volume", "zz_bl45_vol02").state == "create" and plan.blockers == []
