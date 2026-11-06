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


def test_a_sheet_host_nothing_finds_is_named_in_the_discovery_notes():
    # 2026-09-24 review: the note loop ran before assemble_hosts filled report.hosts, so it never fired.
    report = _discover(_intent(DeclaredHost(name="ghost", os="linux", address="10.9.9.9")),
                       lambda creds: pytest.fail("no login without a username"))
    ghost = next(h for h in report.hosts if h.name == "ghost")
    assert ghost.lookup.startswith("not found")
    assert any(n.startswith("Sheet host ghost: not found") for n in report.notes)


VME_IQN = "iqn.2024-12.com.hpe:vmenode3:42802"
VME_READ = {"hostname": "vmenode3\n", "os": 'PRETTY_NAME="Ubuntu 24.04.1 LTS"\n',
            "iqn": f"InitiatorName={VME_IQN}\n"}


def test_esxi_is_not_logged_in_and_a_vme_node_is_read_over_ssh():
    """An HPE VME node is Ubuntu: a `vme` row with a login is read like any Linux host and keeps its
    VME label (rack13 has eight HPE_VM_* nodes on iSCSI)."""
    report = _discover(_intent(
        DeclaredHost(name="esx01", os="esxi", address="10.132.30.136", username="root"),
        DeclaredHost(name="vmenode3", os="vme", address="10.132.30.90", username="root"),
    ), lambda creds: FakeLinux(VME_READ))
    assert "read through vCenter" in " ".join(report.notes)
    vme = next(h for h in report.hosts if h.name == "vmenode3")
    assert vme.host_read.startswith("read over SSH") and vme.os == "vme" and vme.iqns == [VME_IQN]


def test_a_host_found_by_its_own_read_plans_under_the_array_name_with_a_linux_persona():
    """The array already has this IQN as HPE_VM_7f21...: planning a second host object for it would be
    refused, so the read-found row plans under the array's name (as vCenter/array lookups already do)."""
    from alletra_onboard.application.provisioning.hosts import union_hosts
    from alletra_onboard.domain.discovery import ArrayHost
    from alletra_onboard.domain.provisioning import persona_for_os

    report = DiscoveryReport(
        array_hosts=[ArrayHost(name="HPE_VM_7f21bf6bf27da180152ea344", persona="Generic-ALUA",
                               iqns={VME_IQN: ["0:4:1"]})],
        host_reads=[HostRead(host_name="vmenode3", address="10.132.30.90", os="linux", iqns=[VME_IQN])],
    )
    hosts, _ = union_hosts(report, [DeclaredHost(name="vmenode3", os="vme", address="10.132.30.90", username="root")])
    assert list(hosts) == ["HPE_VM_7f21bf6bf27da180152ea344"] and hosts["HPE_VM_7f21bf6bf27da180152ea344"].iqns == [VME_IQN]
    assert hosts["HPE_VM_7f21bf6bf27da180152ea344"].persona == "Generic-ALUA"
    assert persona_for_os("vme") == "Generic-ALUA"                # was VMware by fall-through


def test_a_blank_sheet_os_takes_the_os_the_server_reported_for_the_persona():
    from alletra_onboard.application.provisioning.hosts import union_hosts

    report = DiscoveryReport(host_reads=[HostRead(host_name="rhel01", address="10.1.1.1", os="linux",
                                                  wwpns=["10000090FA8B1234"])])
    hosts, _ = union_hosts(report, [DeclaredHost(name="rhel01", address="10.1.1.1", username="root")])
    assert hosts["rhel01"].os == "linux" and hosts["rhel01"].persona == "Generic-ALUA"   # was VMware


def test_a_typed_iqn_in_another_case_is_not_a_mismatch():
    report = DiscoveryReport(host_reads=[HostRead(host_name="w", address="x", iqns=["iqn.1991-05.com.microsoft:win01"])])
    assert declared_mismatches([DeclaredHost(name="w", iqn="IQN.1991-05.COM.MICROSOFT:WIN01")], report) == []


def test_a_read_found_iscsi_host_the_array_already_has_is_planned_not_refused():
    """The sheet claims the array's name before the array does, so 'source' is sheet; the host object
    still exists and can be a set member. It was told 'create it on the array first'."""
    from alletra_onboard.application.provisioning import storage_provision as sp
    from alletra_onboard.domain.discovery import ArrayHost

    name = "HPE_VM_7f21bf6bf27da180152ea344"
    report = DiscoveryReport(
        array_hosts=[ArrayHost(name=name, persona="Generic-ALUA", iqns={VME_IQN: ["0:4:1"]})],
        host_reads=[HostRead(host_name="vmenode3", address="10.132.30.90", os="linux", iqns=[VME_IQN])],
    )
    intent = _intent(DeclaredHost(name="vmenode3", os="vme", address="10.132.30.90", username="root"))
    assert sp._hosts_by_name(report, intent) == {name: []}
    assert not any("not supported" in n for n in sp._host_notes(intent, report, None, sp._hosts_by_name(report, intent)))


def test_a_planned_host_with_no_os_from_any_source_is_flagged_not_blocked():
    from alletra_onboard.application.provisioning import storage_provision as sp

    intent = _intent(DeclaredHost(name="mystery", wwpns=["10000090FA8B9999"]))
    report = DiscoveryReport()
    notes = sp._host_notes(intent, report, None, sp._hosts_by_name(report, intent))
    assert any(n.startswith("No OS known for mystery") and "VMware persona" in n for n in notes)


def test_a_blank_os_login_that_fails_says_it_was_tried_as_linux():
    def refuse(creds):
        raise ConnectionError("port 22 refused")

    report = _discover(_intent(DeclaredHost(name="srv", address="10.1.1.9", username="administrator")), refuse)
    assert "tried as Linux" in next(n for n in report.notes if n.startswith("Host srv"))


# ------------------------------------------------------------------ R5: Windows over WinRM

WIN_OS = '{"Caption":"Microsoft Windows Server 2022 Standard","Version":"10.0.20348"}'
# Get-InitiatorPort on a host with two FC ports and the iSCSI initiator enabled.
WIN_INITIATORS = (
    '[{"NodeAddress":"50402ec02089cc1c","PortAddress":"51402ec02089cc1c"},'
    '{"NodeAddress":"50402ec02089cc1e","PortAddress":"51402ec02089cc1e"},'
    '{"NodeAddress":"iqn.1991-05.com.microsoft:arcus-win137","PortAddress":"ISCSI ANY PORT"}]'
)
WIN_FULL = {"hostname": "ARCUS-WIN137\r\n", "os": "\ufeff" + WIN_OS, "serial": "CZ2D2K01WN\r\n",
            "initiators": WIN_INITIATORS, "mpio": '{"feature":"Installed","claimed":1,"disks":2}'}


class FakeWindows(FakeLinux):
    def read(self, key):
        from alletra_onboard.adapters.hosts import windows_winrm

        assert key in windows_winrm.SCRIPTS
        self.keys.append(key)
        return self.outputs.get(key, "")


def test_windows_scripts_are_fixed_reads():
    from alletra_onboard.adapters.hosts import windows_winrm

    verbs = ("$env:", "Get-", "(Get-", "ConvertTo-Json", "$f =")
    for script in windows_winrm.SCRIPTS.values():
        assert script.startswith(verbs)
        for forbidden in ("Set-", "New-", "Remove-", "Enable-", "Disable-", "Invoke-", "Start-", "Stop-", "mpclaim"):
            assert forbidden not in script


def test_windows_parsers():
    from alletra_onboard.adapters.hosts import windows_winrm as w

    assert w.parse_os("\ufeff" + WIN_OS) == "Microsoft Windows Server 2022 Standard"
    assert w.parse_initiators(WIN_INITIATORS) == (
        ["51402EC02089CC1C", "51402EC02089CC1E"], ["iqn.1991-05.com.microsoft:arcus-win137"],
    )
    # One port, no -InputObject array wrapper (older PowerShell) -> a bare object still parses.
    assert w.parse_initiators('{"NodeAddress":"x","PortAddress":"51402ec02089cc1c"}') == (["51402EC02089CC1C"], [])
    assert w.parse_initiators("") == ([], [])
    assert w.parse_serial("System Serial Number") == ""
    assert w.parse_mpio('{"feature":"Available","claimed":0,"disks":0}') == (
        "MPIO Available; 3PARdata VV NOT claimed by MSDSM; 0 Alletra/3PAR disk(s)"
    )


def test_a_sheet_windows_host_with_a_login_is_read_over_winrm():
    report = disc.discover(
        _intent(DeclaredHost(name="arcus-win137", os="windows", address="10.132.30.137",
                             username="administrator", password=SecretStr("win-pw"))),
        array_cli_factory=lambda c: _Cli(), vcenter_factory=lambda c: _VCenter(),
        linux_host_factory=lambda c: pytest.fail("Windows is not read over SSH"),
        windows_host_factory=lambda c: FakeWindows(WIN_FULL),
    )
    host = next(h for h in report.hosts if h.name == "arcus-win137")
    assert host.serial_number == "CZ2D2K01WN" and host.os == "windows"
    assert host.wwpns == ["51402EC02089CC1C", "51402EC02089CC1E"]
    assert host.iqns == ["iqn.1991-05.com.microsoft:arcus-win137"]
    assert host.lookup == "read from the server over WINRM (10.132.30.137)"
    assert host.host_read == "read over WINRM from 10.132.30.137"      # ARCUS-WIN137 is the same name
    assert host.multipath == "MPIO Installed; 3PARdata VV claimed by MSDSM; 2 Alletra/3PAR disk(s)"
    assert "win-pw" not in json.dumps(report.model_dump(mode="json"))


def test_a_winrm_session_never_uses_the_environment_proxy(monkeypatch):
    from alletra_onboard.adapters.hosts import windows_winrm

    captured: dict = {}

    class FakeSession:
        def __init__(self, url, auth, **kwargs):
            captured.update(kwargs, url=url)

    monkeypatch.setattr(windows_winrm, "winrm", type("W", (), {"Session": FakeSession}))
    windows_winrm.WindowsHostClient("10.132.30.137", "administrator", "pw")._session_for("http://10.132.30.137:5985/wsman")
    assert captured["proxy"] is None and captured["transport"] == "ntlm"


@pytest.mark.parametrize("user, hinted", [
    ("administrator", True), ("ELJR0NB1UV\\Administrator", False), ("svc@asiapacific.hpqcorp.net", False),
])
def test_a_refused_bare_windows_user_gets_the_qualified_form_hint(monkeypatch, user, hinted):
    """rack13 2026-09-28: a domain-joined server refused bare 'administrator'; ELJR0NB1UV\\Administrator worked."""
    from alletra_onboard.adapters.hosts import windows_winrm

    class Refusing:
        def __init__(self, *a, **k):
            pass

        def run_ps(self, script):
            raise windows_winrm.InvalidCredentialsError("401")

    monkeypatch.setattr(windows_winrm, "winrm", type("W", (), {"Session": Refusing}))
    with pytest.raises(windows_winrm.WindowsHostError) as exc:
        windows_winrm.WindowsHostClient("10.132.30.137", user, "pw").connect()
    assert ("COMPUTERNAME\\user" in str(exc.value)) is hinted


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
