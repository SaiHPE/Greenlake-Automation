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
from alletra_onboard.domain.errors import DeviceError
from tests.unit import fake_tls
from tests.unit.test_storage_services import _ARRAY_BLOCKS, FakeArrayCli, FakeVCenter, _intent


class _Refuses:
    def __init__(self, message: str) -> None:
        self.message = message

    def __enter__(self):
        raise DeviceError(self.message)

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
    # BL-53: the certificate is read and compared before login; a made-up one stands in for vCenter's
    fake_tls.install(monkeypatch).devices[("vc", 443)] = fake_tls.self_signed_der("vc")
    client = vcenter_client.VCenterClient("vc", "zz_nobody@vsphere.local", "x")
    try:
        client.connect()
    except vcenter_client.VCenterError as exc:
        text = str(exc)
    else:  # pragma: no cover
        raise AssertionError("connect() should have raised")
    assert text.startswith("Login failed for zz_nobody@vsphere.local@vc — check the vCenter username/password")
    assert "incorrect user name or password" in text and "dynamicType" not in text


def test_vcenter_read_fault_translates_to_device_error_and_destroy_tolerates_fault():
    """STANDARD E1, E2: pyVmomi read faults become VCenterError (DeviceError) with .msg preserved,
    and view.Destroy() / Disconnect failures log and do not raise."""
    import pytest
    from pyVmomi import vmodl

    from alletra_onboard.domain.errors import DeviceError, VCenterError

    class _FailingSi:
        def RetrieveContent(self):
            fault = vmodl.fault.HostNotConnected()
            fault.msg = "The host is not connected."
            raise fault

    client = vcenter_client.VCenterClient("vc", "u", "p")
    client._si = _FailingSi()
    with pytest.raises(VCenterError, match="The host is not connected.") as exc_info:
        client.host_fc_hbas()
    assert isinstance(exc_info.value, DeviceError)

    class _FailingView:
        view: tuple[object, ...] = ()

        def Destroy(self):
            raise vmodl.fault.SystemError()

    class _ViewSi:
        def RetrieveContent(self):
            class _VM:
                def CreateContainerView(self, *_a):
                    return _FailingView()

            return type("C", (), {"viewManager": _VM(), "rootFolder": None})()

    client._si = _ViewSi()
    assert client.host_fc_hbas() == []
    client.close()
    assert client._si is None


def test_provisioning_catches_device_error_and_surfaces_bugs():
    """STANDARD E1: real adapter DeviceError becomes report.error, while a non-DeviceError bug surfaces."""
    import pytest

    from alletra_onboard.domain.errors import ArrayCliError

    class _ArrayErrorCli:
        def __enter__(self):
            raise ArrayCliError("Could not reach the array at 10.0.0.5:22 (TimeoutError)")

        def __exit__(self, *a):
            return False

    class _BuggyCli:
        def __enter__(self):
            raise KeyError("unexpected bug")

        def __exit__(self, *a):
            return False

    report = disc.discover(
        _intent(),
        array_cli_factory=lambda c: _ArrayErrorCli(),
        vcenter_factory=lambda c: FakeVCenter([HostHba(host_name="esx1", wwpn="10000000C9000001")]),
    )
    assert report.error and "TimeoutError" in report.error

    with pytest.raises(KeyError, match="unexpected bug"):
        disc.discover(
            _intent(),
            array_cli_factory=lambda c: _BuggyCli(),
            vcenter_factory=lambda c: FakeVCenter([]),
        )
