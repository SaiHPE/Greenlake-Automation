"""SPEC-014 slice 2 — a Linux host on the sheet reports its own serial, WWPNs, IQN and multipath over
a read-only SSH login; a typed WWPN the server does not have blocks the plan; the login's password is
held with the run and never serialised anywhere else.

Output fixtures are shaped on RHEL 9 / SLES 15 command output; no rack13 Linux host exists, so the
live read is owed (SPEC-014 slice 2: built — pending live run)."""

import json
from pathlib import Path

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
# `multipath -ll` as printed in published documents: no lab Linux host has an Alletra volume yet
# (tests/fixtures/linux_multipath/README.md says where each came from and how to replace them).
MP_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "linux_multipath"
MP_HPE_P67 = (MP_DIR / "hpe_primera_rhel_guide_p67_documented_sample.txt").read_text()
MP_HPE_P76 = (MP_DIR / "hpe_primera_rhel_guide_p76_documented_sample.txt").read_text()
MP_SUSE_NETAPP = (MP_DIR / "suse_sles15sp6_storage_guide_documented_sample.txt").read_text()
# The lab RHEL 8.9 host as root, 2026-11-16: the real answers when multipath is not set up.
MP_LAB_NOT_SET_UP = (MP_DIR / "rhel89_lab_2026-11-16_not_set_up.txt").read_text()


def _captured(text: str) -> dict[str, tuple[int, str]]:
    """`=== name` sections of a hand capture -> (exit status, output); `exit=N` closes a section."""
    out: dict[str, tuple[int, str]] = {}
    name, lines = "", []
    for line in text.splitlines():
        if line.startswith("=== "):
            if name and name not in out:
                out[name] = (0, "\n".join(lines) + "\n")
            name, lines = line[4:], []
        elif line.startswith("exit="):
            out[name] = (int(line[5:]), "\n".join(lines) + "\n")
        else:
            lines.append(line)
    return out


class FakeLinux:
    """`read(key)` like the real client: '' for a command that failed (not root, file absent)."""

    def __init__(self, outputs: dict[str, str]):
        self.outputs = outputs
        self.keys: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def run(self, key):
        """(exit status, stdout): a key with an output ran (exit 0); a key without one failed (exit 1)."""
        assert key in linux_ssh.COMMANDS
        self.keys.append(key)
        return (0, self.outputs[key]) if key in self.outputs else (1, "")

    def read(self, key):
        status, out = self.run(key)
        return out if status == 0 else ""


FULL = {"hostname": "rhel92lab01\n", "os": OS_RELEASE, "serial": "CZJ3140ABC\n", "fc": PORT_NAMES,
        "iqn": INITIATOR, "multipath": MP_HPE_P67}


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


def test_a_full_read_as_root():
    read = linux_ssh.read_linux_host(FakeLinux(FULL), "rhel92lab01", "10.132.30.140")
    assert read.serial_number == "CZJ3140ABC" and read.hostname == "rhel92lab01"
    assert read.wwpns == ["10000090FA8B1234", "10000090FA8B1235"]
    assert read.iqns == ["iqn.1994-05.com.redhat:rhel92lab01"]
    assert read.os == "linux" and read.os_text.startswith("Red Hat") and read.error == ""


def test_a_non_root_login_falls_back_to_sudo_n_and_says_what_it_could_not_read():
    # BL-36: multipath is loaded, but neither `multipath -ll` nor `sudo -n multipath -ll` ran.
    outputs = {k: v for k, v in FULL.items() if k not in ("serial", "multipath")} | {"dm_multipath": "live\n"}
    fake = FakeLinux(outputs)
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "10.132.30.140")
    assert "serial_sudo" in fake.keys and "multipath_sudo" in fake.keys
    assert read.serial_number == ""
    assert read.multipath_state == "not_permitted"
    assert read.multipath == ("not read: it needs root, or sudo without a password. "
                              "Use a root login on the Hosts tab to see it.")
    assert any("serial number not readable" in n for n in read.notes)
    assert any("multipath not readable" in n for n in read.notes)
    assert read.wwpns                                           # sysfs port_name is world-readable


# ------------------------------------------------------------------ BL-36: the multipath summary

def test_the_parser_reads_the_documented_alletra_samples():
    (one,) = linux_ssh.parse_multipath(MP_HPE_P67)
    assert one.name == "360002ac000000000000003e3000185df"
    assert one.paths == ("active ready running",) * 4 and one.failed == 0
    (two,) = linux_ssh.parse_multipath(MP_HPE_P76)              # header line ends in a space
    assert two.name == "350002ac000160121" and len(two.paths) == 4


def test_another_vendors_device_is_not_counted():
    # An aliased device with two path groups (`| |-` lines), from a NetApp array.
    assert linux_ssh.parse_multipath(MP_SUSE_NETAPP) == []
    assert linux_ssh.parse_multipath(MP_SUSE_NETAPP + MP_HPE_P67)[0].paths == ("active ready running",) * 4


def test_a_root_read_summarises_the_alletra_devices():
    fake = FakeLinux(FULL)
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "10.132.30.140")
    assert "multipath_sudo" not in fake.keys and "dm_multipath" not in fake.keys
    assert read.multipath_state == "ok"
    assert read.multipath == "1 Alletra/3PAR device, 4 paths, all active"


def test_multipath_not_set_up_is_said_plainly():
    # BL-10's lab host: non-root login, no /etc/multipath.conf, dm-multipath not loaded.
    fake = FakeLinux({k: v for k, v in FULL.items() if k != "multipath"})
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "10.132.30.140")
    assert fake.keys[-1] == "dm_multipath"
    assert read.multipath_state == "not_set_up"
    assert read.multipath.startswith("not set up on this server (the dm-multipath module is not loaded)")
    assert not any("multipath not readable" in n for n in read.notes)


def test_the_lab_hosts_real_answers_read_as_not_set_up():
    """The lab RHEL 8.9 host as root (tests/fixtures/linux_multipath/README.md): `multipath -ll` exits 1
    and the module's initstate file is absent, so the sentence says multipath is not set up."""
    real = _captured(MP_LAB_NOT_SET_UP)
    assert real["multipath -ll"][0] == 1 and "DM multipath kernel driver not loaded" in real["multipath -ll"][1]
    answers = {"hostname": real["hostname"], "multipath": real["multipath -ll"],
               "multipath_sudo": real["multipath -ll"], "dm_multipath": real["initstate"]}

    class LabHost(FakeLinux):
        def run(self, key):
            assert key in linux_ssh.COMMANDS
            self.keys.append(key)
            return answers.get(key, (1, ""))

    read = linux_ssh.read_linux_host(LabHost({}), "localhost.localdomain", "10.54.159.49")
    assert read.hostname == "localhost.localdomain"
    assert read.multipath_state == "not_set_up"
    assert read.multipath == ("not set up on this server (the dm-multipath module is not loaded). "
                              "Set up multipath before volumes are presented.")


def test_the_tools_own_read_of_the_lab_host_replays_to_the_summary_it_gave():
    """2026-11-17: the tool's own client as root on the lab RHEL 8.9 host saved each command's exit code
    and stdout, and the summary it made of them (tests/fixtures/linux_multipath/README.md)."""
    folder = MP_DIR / "rhel89_lab_2026-11-17_tool_read"

    def saved(key: str) -> tuple[int, str]:
        command, status, out = (folder / f"{key}.txt").read_text().split("\n", 2)
        assert command == "# " + linux_ssh.COMMANDS[key]
        return int(status.removeprefix("# exit ")), out

    answers = {key: saved(key) for key in ("hostname", "multipath", "multipath_sudo", "dm_multipath")}
    assert [answers[k][0] for k in ("multipath", "multipath_sudo", "dm_multipath")] == [1, 1, 1]

    class LabHost(FakeLinux):
        def run(self, key):
            assert key in linux_ssh.COMMANDS
            self.keys.append(key)
            return answers.get(key, (1, ""))

    read = linux_ssh.read_linux_host(LabHost({}), "localhost.localdomain", "10.54.159.49")
    summary = dict(line.split(": ", 1) for line in (folder / "summary.txt").read_text().splitlines())
    assert read.hostname == "localhost.localdomain"
    assert (read.multipath_state, read.multipath) == (summary["state"], summary["multipath"]) == (
        "not_set_up", ("not set up on this server (the dm-multipath module is not loaded). "
                       "Set up multipath before volumes are presented."))


def test_multipath_set_up_with_no_alletra_devices_yet():
    for listing in ("", MP_SUSE_NETAPP):                       # nothing listed, or another vendor only
        read = linux_ssh.read_linux_host(FakeLinux(FULL | {"multipath": listing, "dm_multipath": "live\n"}),
                                         "rhel92lab01", "10.132.30.140")
        assert read.multipath_state == "none"
        assert read.multipath.startswith("set up, no Alletra/3PAR devices yet")


def test_sudo_n_is_used_when_the_login_is_not_root():
    fake = FakeLinux({k: v for k, v in FULL.items() if k != "multipath"} | {"multipath_sudo": MP_HPE_P76})
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "10.132.30.140")
    assert read.multipath == "1 Alletra/3PAR device, 4 paths, all active"


Device = linux_ssh.MultipathDevice
OK4 = ("active ready running",) * 4


def test_the_sentence_for_several_devices_all_healthy():
    devices = [Device("mpatha", OK4), Device("mpathb", OK4)]
    assert linux_ssh.multipath_summary(devices, listed=True, module_loaded=True) == (
        "ok", "2 Alletra/3PAR devices, 4 paths each, all active")


def test_uneven_path_counts_name_the_device():
    devices = [Device("mpatha", OK4), Device("mpathb", OK4[:2]), Device("mpathc", OK4)]
    assert linux_ssh.multipath_summary(devices, listed=True, module_loaded=True) == (
        "uneven", "3 Alletra/3PAR devices, 4 paths each except mpathb (2 paths). Check the zoning and cabling.")


def test_a_failed_path_names_the_device_and_a_standby_path_is_not_a_failure():
    failed = ("active ready running", "failed faulty running", "active ready running", "active ready running")
    standby = ("active ready running",) * 2 + ("active ghost running",) * 2
    devices = [Device("mpatha", standby), Device("mpathb", failed)]
    assert linux_ssh.multipath_summary(devices, listed=True, module_loaded=True) == (
        "degraded", "2 Alletra/3PAR devices, 4 paths each; 1 path failed on mpathb. Check the zoning and cabling.")


def _aliased(sample: str, alias: str) -> str:
    """A published sample's header in the aliased form the SUSE sample prints: `alias (wwid) dm-N …`."""
    header, rest = sample.split("\n", 1)
    wwid, tail = header.split(" ", 1)
    return f"{alias} ({wwid}) {tail}\n{rest}"


def test_an_aliased_alletra_device_keeps_its_own_paths_when_another_vendor_follows():
    # Composed from the published samples: the HPE device under an alias, then the NetApp device, then
    # the second HPE device. NetApp's three paths must not land on mpatha.
    text = _aliased(MP_HPE_P67, "mpatha") + MP_SUSE_NETAPP.replace("mpatha ", "mpathb ", 1) + MP_HPE_P76
    first, second = linux_ssh.parse_multipath(text)
    assert (first.name, first.wwid) == ("mpatha", "360002ac000000000000003e3000185df")
    assert first.paths == ("active ready running",) * 4
    assert (second.name, second.wwid, len(second.paths)) == ("350002ac000160121", "350002ac000160121", 4)


# SYNTHETIC edge cases, NOT array output: no lab capture or published sample shows these yet. Each is
# one line in the shape multipath-tools prints for it, to test the parser's robustness: a failed path,
# a path whose device has left sysfs (`#:#:#:#` and `-`), a path check still running (a two-word
# checker state), and the header of a map that has lost every path (`##,##` for vendor and product).
SYN_FAILED = "  |- 7:0:1:1  sdv  65:80  failed faulty running"
SYN_GONE = "  |- #:#:#:# -    #:#    failed faulty running"
SYN_PENDING = "  |- 8:0:0:1  sdap 66:144 active i/o pending running"
SYN_LOST_HEADER = "mpathb (360002AC000000000000003e3000185e0) dm-4 ##,##"


def _lost_map(header: str = SYN_LOST_HEADER) -> str:
    """A map with no paths left: the synthetic header and the p67 sample's size line."""
    return header + "\n" + MP_HPE_P67.splitlines()[1] + "\n"


def test_a_failed_a_gone_and_a_pending_path_are_read():
    head = MP_HPE_P67.splitlines()[:3]
    last = MP_HPE_P67.splitlines()[-1]
    (one,) = linux_ssh.parse_multipath("\n".join([*head, SYN_FAILED, SYN_GONE, SYN_PENDING, last]) + "\n")
    assert one.paths == ("failed faulty running", "no device: failed faulty running",
                         "active i/o pending running", "active ready running")
    assert one.failed == 2                                     # a running check is not a failure


def test_a_map_that_lost_every_path_is_still_an_alletra_device_by_its_wwid():
    (dead,) = linux_ssh.parse_multipath(_lost_map())
    assert (dead.name, dead.wwid, dead.paths) == ("mpathb", "360002AC000000000000003e3000185e0", ())
    # The NAA-5 WWID form of the p76 sample counts too; another vendor's WWID does not.
    assert len(linux_ssh.parse_multipath(_lost_map("mpathc (350002ac000160121) dm-5 ##,##"))) == 1
    assert linux_ssh.parse_multipath(_lost_map("mpathd (3600a098000aad1e300000b4b5a275d45) dm-0 ##,##")) == []


def test_one_healthy_and_one_dead_alletra_device_is_degraded_and_names_the_dead_one():
    read = linux_ssh.read_linux_host(FakeLinux(FULL | {"multipath": MP_HPE_P67 + _lost_map()}), "rhel92lab01", "x")
    assert read.multipath_state == "degraded"
    assert read.multipath == "2 Alletra/3PAR devices, 4 paths each except mpathb (no paths). Check the zoning and cabling."
    only = linux_ssh.read_linux_host(FakeLinux(FULL | {"multipath": _lost_map()}), "rhel92lab01", "x")
    assert only.multipath_state == "degraded"
    assert only.multipath == "1 Alletra/3PAR device with no paths: mpathb. Check the zoning and cabling."


def test_a_device_with_a_single_path_is_degraded_because_it_has_no_redundancy():
    assert linux_ssh.multipath_summary([Device("mpatha", OK4), Device("mpathc", OK4[:1])],
                                       listed=True, module_loaded=True) == (
        "degraded", ("2 Alletra/3PAR devices, 4 paths each except mpathc (1 path). "
                     "A single path is no redundancy. Check the zoning and cabling."))
    assert linux_ssh.multipath_summary([Device("mpathc", OK4[:1])], listed=True, module_loaded=True) == (
        "degraded", "1 Alletra/3PAR device, 1 path. A single path is no redundancy. Check the zoning and cabling.")


def test_many_devices_are_named_three_at_most():
    # One fabric down: every device lost a path.
    half = ("active ready running", "failed faulty running")
    devices = [Device(f"mpath{c}", half) for c in "abcde"]
    assert linux_ssh.multipath_summary(devices, listed=True, module_loaded=True)[1] == (
        "5 Alletra/3PAR devices, 2 paths each; 5 paths failed on mpatha, mpathb, mpathc and 2 more. "
        "Check the zoning and cabling.")
    uneven = [Device("mpathz", OK4)] * 5 + [Device(f"mpath{c}", OK4[:2]) for c in "abcd"]
    assert linux_ssh.multipath_summary(uneven, listed=True, module_loaded=True)[1] == (
        "9 Alletra/3PAR devices, 4 paths each except mpatha (2 paths), mpathb (2 paths), mpathc (2 paths) "
        "and 1 more. Check the zoning and cabling.")


class SlowLinux(FakeLinux):
    """`run` gives -1 for the keys in `slow`, as the real client does when a command does not answer."""

    def __init__(self, outputs: dict[str, str], slow: set[str]):
        super().__init__(outputs)
        self.slow = slow

    def run(self, key):
        if key in self.slow:
            self.keys.append(key)
            return -1, ""
        return super().run(key)


def test_a_timed_out_multipath_read_says_so_and_does_not_ask_for_root():
    as_root = SlowLinux(FULL | {"dm_multipath": "live\n"}, slow={"multipath"})
    read = linux_ssh.read_linux_host(as_root, "rhel92lab01", "x")
    assert "multipath_sudo" not in as_root.keys                 # sudo would only wait again
    assert read.multipath_state == "timed_out"
    assert read.multipath == "could not be read: the command timed out. Run Discovery again."
    assert "multipath not read: the command timed out" in read.notes
    assert not any("needs root" in n for n in read.notes if n.startswith("multipath"))
    not_root = SlowLinux({k: v for k, v in FULL.items() if k != "multipath"}, slow={"multipath_sudo"})
    assert linux_ssh.read_linux_host(not_root, "rhel92lab01", "x").multipath_state == "timed_out"


def test_a_listing_with_maps_means_multipath_is_loaded_even_without_the_module_file():
    # dm-multipath built into the kernel has no initstate file; the listing itself proves it is there.
    fake = FakeLinux(FULL | {"multipath": MP_SUSE_NETAPP})                # no "dm_multipath" answer
    read = linux_ssh.read_linux_host(fake, "rhel92lab01", "x")
    assert read.multipath_state == "none"
    assert read.multipath.startswith("set up, no Alletra/3PAR devices yet")


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
    assert host.os == "linux" and host.multipath == "1 Alletra/3PAR device, 4 paths, all active"
    assert host.multipath_state == "ok"
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
