"""Post-init SSH verification: the parser/compare logic and the read-only command guard.

No real SSH — a fake client returns canned ``show*`` output. The canned output mirrors the real
formats from a live HPE Alletra Storage MP B10000 (OS 10.5.51), so these double as a regression
against that array (see docs/adr/0001).
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
        "dns": ["10.203.96.10", "10.203.96.9"],
        "ntp": "NTP1.bgl1.globl.tslabs.hpecorp.net",
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
        dscc_setup=DsccSetupConfig(
            system_name="MPB10K-E24U21-LZ", country="India", contact_email="g-sai-roopesh@hpe.com"
        ),
    )


def _outputs(*, gateway="10.64.159.254"):
    # Real command output formats from the live B10000.
    return {
        "showsys -d": (
            "------------------------General------------------------\n"
            "System Name                  :         MPB10K-E24U21-LZ\n"
            "System Model                 :   HPE Alletra Storage MP\n"
            "Serial Number                :               SGHD45FF0Y\n"
            "Product Number               :                   S0B84A\n"
            "System ID                    :                  0x2F629\n"
            "--------System Descriptors--------\n"
            "Location    :\n"
            "Owner       :\n"
            "Contact     : Sai Roopesh, 8217270831, g-sai-roopesh@hpe.com\n"
            "Comment     :\n"
        ),
        "shownet": (
            "IP Address    Netmask/PrefixLen Nodes Active Speed Duplex AutoNeg Status Mode\n"
            "10.64.154.225     255.255.248.0    01      0  1000 Full   Yes     Active Static\n"
            "\n"
            f"Default IPv4 route :                                      {gateway}\n"
            "Default IPv6 route :                                               None\n"
            "NTP server         :                 NTP1.bgl1.globl.tslabs.hpecorp.net\n"
            "DNS server         :                           10.203.96.10 10.203.96.9\n"
            "Proxy server       :   http://Proxy.bgl1.global.tslabs.hpecorp.net:8080\n"
        ),
        "showdate": (
            "Node Date\n"
            "0    2026-06-22 16:28:55 IST (Asia/Kolkata)\n"
            "1    2026-06-22 16:28:55 IST (Asia/Kolkata)\n"
        ),
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


def test_netmask_gateway_dns_ntp_timezone_parse_from_real_formats():
    # The fields that were "not readable" before calibration: netmask (table row), gateway
    # ("Default IPv4 route"), NTP/DNS (inside shownet), timezone (parenthesised in showdate).
    fields = _by_field(verify(_item(), "3paradm", "pw", client_factory=_factory(_FakeClient(_outputs()))))
    assert fields["Netmask"].actual == "255.255.248.0"
    assert fields["Gateway"].actual == "10.64.159.254"
    assert fields["NTP server"].actual == "NTP1.bgl1.globl.tslabs.hpecorp.net"
    assert fields["Timezone"].actual == "Asia/Kolkata"
    # DNS reads ONLY the "DNS server" line — not every IPv4 in shownet (no mgmt-IP/gateway pollution).
    assert fields["DNS servers"].actual == "10.203.96.10, 10.203.96.9"
    assert fields["Support contact"].status == FieldCheckStatus.PASS


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
    assert fields["System name"].status == FieldCheckStatus.PASS  # showsys -d still parsed


def test_unreachable_array_returns_not_reachable():
    client = _FakeClient(_outputs(), fail_connect=True)
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(client))
    assert report.reachable is False
    assert report.error
    assert report.checks == []


def test_raw_outputs_are_returned_for_operator_review():
    report = verify(_item(), "3paradm", "pw", client_factory=_factory(_FakeClient(_outputs())))
    assert "MPB10K-E24U21-LZ" in report.raw["showsys -d"]


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


def test_cli_client_refuses_non_show_and_metacharacters():
    client = ArrayCliClient(host="h", username="u", password="p")
    client._client = _FakeSSH()
    danger = (
        "removevv badvv",
        "shutdownsys",
        "createvv x",
        "showsys -d; rm -rf /",  # metacharacter: command chaining
        "showsys && reboot",
        "shownet | sh",
        "showsys `reboot`",
    )
    for command in danger:
        with pytest.raises(ArrayCliError):
            client.run(command)
    assert client._client.commands == []  # nothing dangerous ever reached the transport


def test_cli_client_allows_show_commands_with_args():
    client = ArrayCliClient(host="h", username="u", password="p")
    fake = _FakeSSH()
    client._client = fake
    assert client.run("showsys -d") == "ok\n"
    assert client.run("showportdev ns 0:3:1") == "ok\n"
    assert fake.commands == ["showsys -d", "showportdev ns 0:3:1"]
