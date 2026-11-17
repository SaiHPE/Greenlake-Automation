"""A volume, volume set or host name the array refuses is refused on the sheet or in the plan, before any write.

Live on rack13-ARCUS (OS 10.6.0), 2026-11-17: `zz_bl45_vol02+` passed the sheet and the plan, and the array
refused it only at apply ("illegal character in input", HTTP 400 code 69), after three other objects were
made. The rule is the array's own `help createvv` (tests/fixtures/rack13_snap/help_createvv.txt). The rerun
that evening: the array refused the volume set name `zz_bl45_vvs+` the same way, after four objects. A host
name is held to `help createhost`'s 31 characters (tests/fixtures/d22u27_iscsi/help_createhost.txt).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.provisioning import DeclaredHost, HostSetRequest, VolumeRequest
from tests.unit.test_init_sheet import _PROV_TARGETS, _fill_tabs
from tests.unit.test_plan_truth import WWN_A, TruthfulFakeWsapi, _intent, _plan, _row

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
HELP_CREATEVV = FIXTURES / "rack13_snap" / "help_createvv.txt"
HELP_CREATEHOST = FIXTURES / "d22u27_iscsi" / "help_createhost.txt"


def _sheet(name: str, vvset: str = ""):
    volume = {"name": name, "size_gib": "1", **({"vvset": vvset} if vvset else {})}
    prov = {"targets": _PROV_TARGETS, "volumes": [volume], "hostsets": [{"name": "hs"}]}
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


# ------------------------------------------------------------------ volume sets: the characters, seen live


def test_the_volume_set_name_the_array_refused_on_2026_11_17_is_refused_on_the_sheet():
    with pytest.raises(ValueError) as err:
        _sheet("zz_bl45_vol01", vvset="zz_bl45_vvs+")
    assert str(err.value) == ("Volume 'zz_bl45_vol01' — VV-set: the array takes only letters, digits, '.', '-' and "
                              "'_' in a volume set name, not '+'. Rename it.")


def test_a_volume_set_name_is_not_held_to_a_length_no_captured_help_states():
    assert _sheet("vol01", vvset="vvs-01.a_b").volumes[0].vvset == "vvs-01.a_b"
    assert _sheet("vol01", vvset="s" * 300).volumes[0].vvset == "s" * 300


def test_the_plan_blocks_a_new_volume_set_with_a_name_the_array_refuses():
    """For a set that did not come through the sheet (the page's composition)."""
    intent = _intent(volumes=[VolumeRequest(name="vol01", size_gib=1, cpg="SSD_r6", vvset="zz_bl45_vvs+")], exports=[])
    plan = _plan(TruthfulFakeWsapi(), intent)
    row = _row(plan, "vvset", "zz_bl45_vvs+")
    assert row.state == "conflict" and len(plan.blockers) == 1
    assert row.reason == ("the array takes only letters, digits, '.', '-' and '_' in a volume set name, not '+'. "
                          "Rename it on the sheet's Volumes tab.")


# ------------------------------------------------------------------ hosts: the length only, from help createhost


def test_the_host_length_is_the_one_the_arrays_help_states():
    text = " ".join(HELP_CREATEHOST.read_text().split())
    assert "Specifies the name of the host using up to 31 characters." in text


def _host_plan(name: str, *, from_sheet: bool, on_array: tuple = ()):
    intent = _intent(host_sets=[HostSetRequest(name="hs", members=[name])], exports=[],
                     declared_hosts=[DeclaredHost(name=name, os="linux", wwpns=[WWN_A])] if from_sheet else [])
    discovery = DiscoveryReport() if from_sheet else DiscoveryReport(
        host_hbas=[HostHba(host_name=name, wwpn=WWN_A, fabric="odd", os="VMware ESXi")])
    return _plan(TruthfulFakeWsapi(hosts=on_array), intent, discovery)


def test_the_plan_blocks_a_new_host_from_the_sheet_with_a_name_over_31_characters():
    name = "dbserver-01.datacenter.example.com"     # 34
    plan = _host_plan(name, from_sheet=True)
    row = _row(plan, "host", name)
    assert row.state == "conflict" and plan.blockers == [f"host {name}: {row.reason}"]
    assert row.reason == ("the array takes at most 31 characters in a host name, this one has 34. Give it a shorter "
                          "name on the sheet's Hosts tab.")


def test_a_long_host_name_from_vcenter_says_the_operator_cannot_rename_it_here():
    name = "esx-prod-0001.datacenter.example.com"
    row = _row(_host_plan(name, from_sheet=False), "host", name)
    assert row.state == "conflict"
    assert row.reason.endswith("this one has 36. Leave it out of the host set: the tool cannot create it under this name.")


def test_a_host_name_of_31_characters_and_any_characters_is_created():
    name = "h" * 30 + "+"
    assert _row(_host_plan(name, from_sheet=True), "host", name).state == "create"
