"""S-3 (2026-09-17, pending.ps1 on rack13arcus): the failure paths as the operator meets them.

D-10  the array not reached is discovery's ERROR, not note 1 of 7 behind "Discovery complete".
D-11  a vCenter login failure reads as one sentence, not a vim fault property dump.
Z-7   a zoning check with no array ports is an error, not "Zoning needs 0 zone(s) ... nothing can be
      provisioned" in one breath.
"""

from __future__ import annotations

from alletra_onboard.adapters.vcenter import vcenter_client
from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.application.provisioning import zoning
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from tests.unit.test_storage_services import _ARRAY_BLOCKS, FakeArrayCli, FakeVCenter, _intent


class _Refuses:
    def __init__(self, message: str) -> None:
        self.message = message

    def __enter__(self):
        raise RuntimeError(self.message)

    def __exit__(self, *exc_info: object) -> None:
        pass


def test_array_login_failure_is_the_discovery_error_not_a_note():
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: _Refuses("Login failed for zz_nobody@10.0.0.5"),
        vcenter_factory=lambda c: FakeVCenter([HostHba(host_name="esx1", wwpn="10000000C9000001")]),
    )
    assert report.error and "Login failed for zz_nobody@10.0.0.5" in report.error
    assert not any("Array discovery" in n for n in report.notes)
    assert report.array_ports == [] and len(report.host_hbas) == 1   # the vCenter side still reads


def test_vcenter_failure_stays_a_note_and_the_array_side_survives():
    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: FakeArrayCli(_ARRAY_BLOCKS),
        vcenter_factory=lambda c: _Refuses("Login failed for zz_nobody@vsphere.local@vc"),
    )
    assert report.error is None
    assert any(n.startswith("vCenter discovery failed: Login failed") for n in report.notes)
    assert report.array_ports and report.host_hbas == []


def test_zoning_check_without_array_ports_is_an_error(monkeypatch):
    report = zoning.build_report(_intent(), DiscoveryReport())
    assert report.error and "re-run Discovery" in report.error
    assert report.expected == [] and report.notes == [] and not report.proper


def test_vcenter_invalid_login_reads_as_one_sentence(monkeypatch):
    class InvalidLogin(Exception):
        # pyVmomi faults stringify to their whole property dump; the sentence is in .msg
        msg = "Cannot complete login due to an incorrect user name or password."

        def __str__(self) -> str:
            return "(vim.fault.InvalidLogin) {    dynamicType = <unset>,    dynamicProperty = (vmodl.DynamicProperty) [],    msg = '...'"

    def _connect(**kwargs):
        raise InvalidLogin()

    monkeypatch.setattr(vcenter_client, "SmartConnect", _connect)
    client = vcenter_client.VCenterClient("vc", "zz_nobody@vsphere.local", "x")
    try:
        client.connect()
    except vcenter_client.VCenterError as exc:
        text = str(exc)
    else:  # pragma: no cover
        raise AssertionError("connect() should have raised")
    assert text.startswith("Login failed for zz_nobody@vsphere.local@vc — check the vCenter username/password")
    assert "incorrect user name or password" in text and "dynamicType" not in text
