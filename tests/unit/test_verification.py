"""Post-init SSH verification: the parser/compare logic and the read-only command guard.

No real SSH — a fake client returns canned ``show*`` output. The parser formats here are
representative; they get calibrated against the first live array (see docs/adr/0001).
"""

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError
from alletra_onboard.application.verification import verify
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    FieldCheckStatus,
    NetworkConfig,
)


def _item(**net_over):
    net = {
        "mgmt_ipv4": "10.64.154.225",
        "mask": "255.255.248.0",
        "gateway": "10.64.159.254",
        "dns": ["10.203.96.10"],
        "ntp": "10.203.96.20",
        "timezone": "Asia/Kolkata",
    }
    net.update(net_over)
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y",
        part_number="S0B84A",
        subscription_key=SecretStr("k"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.1.1/cloudinit",
        network=NetworkConfig(**net),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )


def _outputs(*, gateway="10.64.159.254"):
    return {
        "showsys -d": (
            "System Name : array01\n"
            "Serial Number : SGHD45FF0Y\n"
            "System Model : HPE Alletra MP B10000\n"
            "Location : India\n"
        ),
        "shownet": (
            "IP Address : 10.64.154.225\n"
            "Netmask : 255.255.248.0\n"
            f"Gateway : {gateway}\n"
        ),
        "showdns": "DNS Server : 10.203.96.10\n",
        "showntp": "NTP Server : 10.203.96.20\n",
        "showdate": "Timezone : Asia/Kolkata\nDate : 2026-06-21 10:30:00 IST\n",
    }


class _FakeClient:
    def __init__(self, outputs, *, fail_connect=False, fail_commands=()):
        self._outputs = outputs
        self._fail_connect = fail_connect
        self._fail_commands = set(fail_commands)
        self.closed = False

    def connect(self):
        if self._fail_connect:
            raise ArrayCliError("Could not reach the array at 10.64.154.225:22")

    def run(self, command):
        if command in self._fail_commands:
            raise ArrayCliError(f"running '{command}' failed")
        return self._outputs.get(command, "")

    def close(self):
        self.closed = True


def _factory(client):
    def make(*, host, username, password):
        return client

    return make


def _by_field(report):
    return {c.field: c for c in report.checks}


def test_all_values_match_reports_all_pass():
    client = _FakeClient(_outputs())
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(client))
    assert report.reachable
    assert report.error is None
    assert {c.status for c in report.checks} == {FieldCheckStatus.PASS}
    assert report.passed == len(report.checks)
    assert report.mismatches == 0
    assert client.closed  # the SSH session is always closed


def test_wrong_gateway_is_a_critical_mismatch():
    client = _FakeClient(_outputs(gateway="10.0.0.1"))
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(client))
    gw = _by_field(report)["Gateway"]
    assert gw.status == FieldCheckStatus.MISMATCH
    assert gw.critical
    assert gw.actual == "10.0.0.1"
    assert report.mismatches == 1


def test_failed_command_makes_its_fields_not_readable():
    client = _FakeClient(_outputs(), fail_commands={"shownet"})
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(client))
    fields = _by_field(report)
    assert fields["Management IP"].status == FieldCheckStatus.NOT_READABLE
    assert fields["Gateway"].status == FieldCheckStatus.NOT_READABLE
    assert fields["System name"].status == FieldCheckStatus.PASS  # other commands still parsed


def test_unreachable_array_returns_not_reachable():
    client = _FakeClient(_outputs(), fail_connect=True)
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(client))
    assert report.reachable is False
    assert report.error
    assert report.checks == []


def test_raw_outputs_are_returned_for_operator_review():
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(_FakeClient(_outputs())))
    assert "array01" in report.raw["showsys -d"]


# ---------------------------------------------------------------- read-only guard


class _FakeChannel:
    def __init__(self, data=b""):
        self._data = data

    def read(self):
        return self._data


class _FakeSSH:
    def __init__(self):
        self.commands = []

    def exec_command(self, command, timeout=None):
        self.commands.append(command)
        return None, _FakeChannel(b"ok\n"), _FakeChannel(b"")

    def close(self):
        pass


def test_cli_client_refuses_non_show_commands():
    client = ArrayCliClient(host="h", username="u", password="p")
    client._client = _FakeSSH()
    for danger in ("removevv badvv", "shutdownsys", "createvv x", "showsys; rm -rf /"):
        with pytest.raises(ArrayCliError):
            client.run(danger)
    assert client._client.commands == []  # nothing dangerous ever reached the transport


def test_cli_client_allows_show_commands():
    client = ArrayCliClient(host="h", username="u", password="p")
    fake = _FakeSSH()
    client._client = fake
    assert client.run("showsys -d") == "ok\n"
    assert fake.commands == ["showsys -d"]
