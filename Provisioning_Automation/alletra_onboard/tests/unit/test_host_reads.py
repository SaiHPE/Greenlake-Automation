"""SPEC-014 slice 2 — a Linux host on the sheet reports its own serial, WWPNs, IQN and multipath over
a read-only SSH login; a typed WWPN the server does not have blocks the plan; the login's password is
held with the run and never serialised anywhere else.

Output fixtures are shaped on RHEL 9 / SLES 15 command output; no rack13 Linux host exists, so the
live read is owed (SPEC-014 slice 2: built — pending live run)."""

import json

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.hosts import linux_ssh
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore, _provisioning_intent_json
from alletra_onboard.application.provisioning import discovery as disc
from alletra_onboard.application.provisioning.hosts import declared_mismatches
from alletra_onboard.domain.discovery import DiscoveryReport, HostRead
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSetRequest,
    ProvisioningIntent,
    VolumeRequest,
)
from alletra_onboard.domain.shared import EndpointCreds

OS_RELEASE = '''NAME="Red Hat Enterprise Linux"
VERSION="9.2 (Plow)"
ID="rhel"
ID_LIKE="fedora"
VERSION_ID="9.2"
PRETTY_NAME="Red Hat Enterprise Linux 9.2 (Plow)"
'''
PORT_NAMES = "0x10000090fa8b1234\n0x10000090fa8b1235\n"
INITIATOR = "## DO NOT EDIT OR REMOVE THIS FILE!\nInitiatorName=iqn.1994-05.com.redhat:rhel92lab01\n"
MULTIPATH = """mpatha (360002ac0000000000000007a0002d495) dm-2 3PARdata,VV
size=10G features='1 queue_if_no_path' hwhandler='1 alua' wp=rw
`-+- policy='service-time 0' prio=50 status=active
  |- 1:0:0:1 sdb 8:16  active ready running
  |- 1:0:1:1 sdc 8:32  active ready running
  |- 2:0:0:1 sdd 8:48  active ready running
  `- 2:0:1:1 sde 8:64  active ready running
360002ac0000000000000007b0002d495 dm-3 3PARdata,VV
size=2.0G features='1 queue_if_no_path' hwhandler='1 alua' wp=rw
`-+- policy='service-time 0' prio=50 status=active
  |- 1:0:0:2 sdf 8:80  active ready running
  |- 1:0:1:2 sdg 8:96  failed faulty running
  |- 2:0:0:2 sdh 8:112 active ready running
  `- 2:0:1:2 sdi 8:128 active ready running
mpathc (3600508b1001c7e4f0000000000000001) dm-4 HPE,LOGICAL VOLUME
size=446G features='0' hwhandler='0' wp=rw
`-+- policy='service-time 0' prio=1 status=active
  `- 0:1:0:0 sda 8:0   active ready running
"""


class FakeLinux:
    """`read(key)` like the real client: '' for a command that failed (not root, file absent)."""

    def __init__(self, outputs: dict[str, str]):
        self.outputs = outputs
        self.keys: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, key):
        assert key in linux_ssh.COMMANDS
        self.keys.append(key)
        return self.outputs.get(key, "")


FULL = {"hostname": "rhel92lab01\n", "os": OS_RELEASE, "serial": "CZJ3140ABC\n", "fc": PORT_NAMES,
        "iqn": INITIATOR, "multipath": MULTIPATH}


# ------------------------------------------------------------------ R4: the read

def test_the_command_set_is_fixed_and_read_only():
    for command in linux_ssh.COMMANDS.values():
        verb = command.removeprefix("sudo -n ").split()[0]
        assert verb in ("cat", "hostname", "multipath")
        assert not set(";|&`$><\n") & set(command)
    assert "multipath -ll" in linux_ssh.COMMANDS.values()     # list only; never -F / -f / -r


def test_parsers_read_rhel_output():
    assert linux_ssh.parse_os_release(OS_RELEASE) == "Red Hat Enterprise Linux 9.2 (Plow)"
    assert linux_ssh.parse_fc_port_names(PORT_NAMES) == ["10000090FA8B1234", "10000090FA8B1235"]
    assert linux_ssh.parse_initiator_name(INITIATOR) == ["iqn.1994-05.com.redhat:rhel92lab01"]
    assert linux_ssh.parse_serial("To Be Filled By O.E.M.\n") == ""
    # Two Alletra devices (the local HPE LOGICAL VOLUME is not counted), 4 paths each, one faulty.
    assert linux_ssh.parse_multipath(MULTIPATH) == "2 Alletra/3PAR device(s), 4 path(s) each, 1 path(s) not active"


def test_a_full_read_as_root():
    read = linux_ssh.read_linux_host(FakeLinux(FULL), "rhel92lab01", "10.132.30.140")
    assert read.serial_number == "CZJ3140ABC" and read.hostname == "rhel92lab01"
    assert read.wwpns == ["10000090FA8B1234", "10000090FA8B1235"]
    assert read.iqns == ["iqn.1994-05.com.redhat:rhel92lab01"]
    assert read.os == "linux" and read.os_text.startswith("Red Hat") and read.error == ""


def test_a_non_root_login_falls_back_to_sudo_n_and_says_what_it_could_not_read():
    fake = FakeLinux({k: v for k, v in FULL.items() if k not in ("serial", "multipath")})
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "10.132.30.140")
    assert "serial_sudo" in fake.keys and "multipath_sudo" in fake.keys
    assert read.serial_number == "" and read.multipath == ""
    assert any("serial number not readable" in n for n in read.notes)
    assert read.wwpns                                           # sysfs port_name is world-readable


# ------------------------------------------------------------------ discovery end to end

class _Cli:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def run(self, cmd, timeout=None):
        return ""


class _VCenter(_Cli):
    def host_fc_hbas(self):
        return []

    def host_identities(self):
        return []


def _intent(*hosts: DeclaredHost) -> ProvisioningIntent:
    creds = lambda h: EndpointCreds(host=h, username="u", password=SecretStr("p"))
    return ProvisioningIntent(
        array=creds("10.132.30.121"), vcenter=creds("vc"), switch_f1=creds("f1"), switch_f2=creds("f2"),
        volumes=[VolumeRequest(name="v1", size_gib=1)], host_sets=[HostSetRequest(name="hs")],
        declared_hosts=list(hosts),
    )


def _discover(intent, linux_factory):
    return disc.discover(intent, array_cli_factory=lambda c: _Cli(), vcenter_factory=lambda c: _VCenter(),
                         linux_host_factory=linux_factory)


def test_a_sheet_linux_host_with_only_a_name_ip_and_login_is_fully_discovered():
    seen: list[EndpointCreds] = []

    def factory(creds):
        seen.append(creds)
        return FakeLinux(FULL)

    report = _discover(_intent(DeclaredHost(name="rhel92lab01", os="linux", address="10.132.30.140",
                                            username="root", password=SecretStr("pw"))), factory)
    assert seen[0].host == "10.132.30.140" and seen[0].password.get_secret_value() == "pw"
    host = next(h for h in report.hosts if h.name == "rhel92lab01")
    assert host.serial_number == "CZJ3140ABC"
    assert host.wwpns == ["10000090FA8B1234", "10000090FA8B1235"]
    assert host.iqns == ["iqn.1994-05.com.redhat:rhel92lab01"]
    assert host.lookup == "read from the server over SSH (10.132.30.140)"
    assert host.host_read == "read over SSH from 10.132.30.140" and "host" in host.sources
    assert host.os == "linux" and host.multipath.startswith("2 Alletra/3PAR")
    assert "pw" not in json.dumps(report.model_dump(mode="json"))


def test_a_failed_login_is_a_note_and_the_host_is_still_listed():
    def factory(creds):
        raise linux_ssh.LinuxHostError("login failed for root@10.132.30.140 — check the Hosts tab login")

    report = _discover(_intent(DeclaredHost(name="rhel92lab01", os="linux", address="10.132.30.140",
                                            username="root", password=SecretStr("bad"))), factory)
    host = next(h for h in report.hosts if h.name == "rhel92lab01")
    assert host.host_read.startswith("SSH read failed — login failed")
    assert any("rhel92lab01: SSH read failed" in n for n in report.notes)
    assert report.error is None                                   # a host is never the step's error


def test_windows_and_esxi_logins_are_not_attempted_yet():
    report = _discover(_intent(
        DeclaredHost(name="arcus-win137", os="windows", address="10.132.30.137", username="administrator"),
        DeclaredHost(name="esx01", os="esxi", address="10.132.30.136", username="root"),
    ), lambda creds: pytest.fail("no SSH login for Windows or ESXi"))
    notes = " ".join(report.notes)
    assert "Windows login (WinRM) is not built yet" in notes and "read through vCenter" in notes


# ------------------------------------------------------------------ R6: typed vs read

def test_a_typed_wwpn_the_server_does_not_have_is_a_blocker():
    report = DiscoveryReport(host_reads=[HostRead(host_name="rhel92lab01", address="10.132.30.140",
                                                  wwpns=["10000090FA8B1234", "10000090FA8B1235"],
                                                  iqns=["iqn.1994-05.com.redhat:rhel92lab01"])])
    ok = DeclaredHost(name="rhel92lab01", wwpns=["10:00:00:90:fa:8b:12:34"])
    typo = DeclaredHost(name="rhel92lab01", wwpns=["10000090FA8B1243"], iqn="iqn.1994-05.com.redhat:other")
    assert declared_mismatches([ok], report) == []
    blockers = declared_mismatches([typo], report)
    assert "10000090FA8B1243 not on the server" in blockers[0]
    assert "IQN iqn.1994-05.com.redhat:other is not the server's" in blockers[1]
    unread = DiscoveryReport(host_reads=[HostRead(host_name="rhel92lab01", address="x", error="timeout")])
    assert declared_mismatches([typo], unread) == []              # no read, nothing to compare


# ------------------------------------------------------------------ R7: the password

def test_the_host_password_round_trips_the_state_db_and_nowhere_else(tmp_path):
    intent = _intent(DeclaredHost(name="rhel92lab01", os="linux", address="10.132.30.140",
                                  username="root", password=SecretStr("host-pw")))
    assert "host-pw" not in intent.model_dump_json()
    assert "host-pw" not in json.dumps(intent.model_dump(mode="json"))
    assert "host-pw" in _provisioning_intent_json(intent)
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    store.save_provisioning_intent("r1", intent)
    back = store.get_provisioning_intent("r1")
    assert back.declared_hosts[0].password.get_secret_value() == "host-pw"
