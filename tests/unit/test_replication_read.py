"""SPEC-016 R1 — the replication parsers, pinned to tests/fixtures/rc_pair/ (D22U27 <-> E18U31,
OS 10.5.0, captured 2026-10-07). See the fixtures README for every fact asserted here."""

from pathlib import Path

from alletra_onboard.application.replication.read import (
    parse_showcpg_free,
    parse_showport_rcip,
    parse_showrcopy,
    parse_showrctransport_rcip,
    parse_showsys,
    parse_showversion,
    parse_showvv_sizes,
    read_array,
)
from alletra_onboard.domain.shared import EndpointCreds

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "rc_pair"


def _fx(array: str, name: str) -> str:
    return (_FIXTURES / array / f"{name}.txt").read_text(encoding="utf-8", errors="replace")


def test_showsys_gives_name_serial_and_the_decimal_system_id_the_peer_group_names_carry():
    d22 = parse_showsys(_fx("D22U27", "showsys"))
    assert d22 == {"id": 188150, "name": "AlletraMP_D22U27", "model": "HPE Alletra Storage MP", "serial": "CZ2D320BT1"}
    e18 = parse_showsys(_fx("E18U31", "showsys"))
    assert (e18["id"], e18["name"], e18["serial"]) == (188146, "AlletraMP_E18U31", "CZ2D3209YV")


def test_showversion_release():
    assert parse_showversion(_fx("D22U27", "showversion")) == "10.5.0"
    assert parse_showversion(_fx("E18U31", "showversion")) == "10.5.0"


def test_showport_rcip_two_ports_one_per_node_with_mask_and_gateway():
    ports = parse_showport_rcip(_fx("D22U27", "showport_rcip"))
    assert [(p.nsp, p.state, p.ip, p.netmask, p.gateway, p.mtu, p.rate) for p in ports] == [
        ("0:4:3", "ready", "10.54.122.92", "255.255.248.0", "10.54.127.254", "1500", "10Gbps"),
        ("1:4:3", "ready", "10.54.122.93", "255.255.248.0", "10.54.127.254", "1500", "10Gbps"),
    ]
    assert [p.ip for p in parse_showport_rcip(_fx("E18U31", "showport_rcip"))] == ["10.54.154.192", "10.54.154.193"]
    assert parse_showport_rcip("There is no specified port information\n") == []


def test_showrctransport_rcip_pairs_each_port_with_its_peer_address():
    rows = parse_showrctransport_rcip(_fx("D22U27", "showrctransport_rcip"))
    assert [(r.nsp, r.ip, r.peer_ip, r.gateway) for r in rows] == [
        ("0:4:3", "10.54.122.92", "10.54.154.192", "10.54.127.254"),
        ("1:4:3", "10.54.122.93", "10.54.154.193", "10.54.127.254"),
    ]
    rows = parse_showrctransport_rcip(_fx("E18U31", "showrctransport_rcip"))
    assert [(r.ip, r.peer_ip) for r in rows] == [("10.54.154.192", "10.54.122.92"), ("10.54.154.193", "10.54.122.93")]


def test_showrcopy_system_targets_and_links_on_the_primary():
    rc = parse_showrcopy(_fx("D22U27", "showrcopy"))
    assert (rc["status"], rc["health"]) == ("Started", "Normal")
    [target] = rc["targets"]
    assert (target.name, target.id, target.type, target.status, target.policy) == ("AlletraMP_E18U31", 5, "IP", "ready", "mirror_config")
    assert target.mirror_config
    assert [(l.target, l.nsp, l.address, l.status) for l in rc["links"]] == [
        ("AlletraMP_E18U31", "0:4:3", "10.54.154.192", "Up"),
        ("AlletraMP_E18U31", "1:4:3", "10.54.154.193", "Up"),
        ("receive", "0:4:3", "10.54.122.92", "Up"),
        ("receive", "1:4:3", "10.54.122.93", "Up"),
    ]
    assert [l.inbound for l in rc["links"]] == [False, False, True, True]


def test_the_peer_names_its_target_for_us_after_itself():
    # The fact SPEC-016 R2 is built on: never match a partnership by target name.
    rc = parse_showrcopy(_fx("E18U31", "showrcopy"))
    [target] = rc["targets"]
    assert target.name == "AlletraMP_E18U31"
    assert {l.address for l in rc["links"] if not l.inbound} == {"10.54.122.92", "10.54.122.93"}   # D22U27's RCIP


def test_showrcopy_groups_six_sync_groups_with_roles_options_and_volumes():
    rc = parse_showrcopy(_fx("D22U27", "showrcopy"))
    groups = {g.name: g for g in rc["groups"]}
    assert list(groups) == ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]
    g = groups["300gb"]
    assert (g.target, g.status, g.role, g.mode, g.options) == ("AlletraMP_E18U31", "Started", "Primary", "Sync", ["auto_recover", "auto_synchronize"])
    assert g.mode_key == "sync"
    assert [(v.local_name, v.local_id, v.remote_name, v.remote_id, v.sync_status, v.last_sync) for v in g.volumes] == [
        ("300gb", 269, "300gb", 1521, "Synced", "NA"), ("Test", 9342, "Test", 1522, "Synced", "NA"),
    ]
    # the Peer Persistence group: Secondary here, active_active in its options
    app = groups["APP_Test"]
    assert app.role == "Secondary" and "active_active" in app.options and app.volume_names == ["APP.test.vv"]
    # a group with NO options column still parses (5 tokens on the row)
    assert groups["Intern_Automation"].options == [] and len(groups["Intern_Automation"].volumes) == 4
    assert len(groups["Test-RCG2"].volumes) == 2


def test_the_peer_side_group_names_carry_the_primary_system_id():
    rc = parse_showrcopy(_fx("E18U31", "showrcopy"))
    names = [g.name for g in rc["groups"]]
    assert names == [n + ".r188150" for n in ["300gb", "APP_Test", "Intern_Automation", "Intern_Automation2", "Test-RCG", "Test-RCG2"]]
    roles = {g.name: g.role for g in rc["groups"]}
    assert roles["300gb.r188150"] == "Secondary" and roles["APP_Test.r188150"] == "Primary"


def test_showrcopy_groups_subset_and_a_missing_group_parse_cleanly():
    rc = parse_showrcopy(_fx("D22U27", "showrcopy_groups"))
    assert len(rc["groups"]) == 6 and rc["targets"] == [] and rc["status"] == "Started"
    missing = parse_showrcopy(_fx("D22U27", "showrcopy_groups_rcopy_async_test"))
    assert missing["groups"] == [] and missing["status"] == "Started"
    links_only = parse_showrcopy(_fx("D22U27", "showrcopy_links"))
    assert len(links_only["links"]) == 4 and links_only["groups"] == []


def test_a_periodic_group_block_parses_its_timestamped_last_sync():
    # No periodic group exists on the lab pair yet (README); the format follows the CLI reference —
    # re-pin this against the first live async run's capture.
    text = (
        "Group Information\n\n"
        "Name            Target           Status   Role       Mode     Options\n"
        "zz_rc_test_rcg  AlletraMP_E18U31 Started  Primary    Periodic Period 5m,auto_recover,auto_synchronize\n"
        "  LocalVV        ID   RemoteVV       ID   SyncStatus    LastSyncTime\n"
        "  zz_rc_test_v01 9901 zz_rc_test_v01 1601 Syncing       2026-10-07 19:10:03 IST\n"
    )
    [g] = parse_showrcopy(text)["groups"]
    assert g.mode == "Periodic" and g.mode_key == "async"
    assert g.volumes[0].sync_status == "Syncing" and g.volumes[0].last_sync == "2026-10-07 19:10:03 IST"


def test_showcpg_free_space_per_cpg():
    assert parse_showcpg_free(_fx("D22U27", "showcpg")) == {"3sc": 179025, "SSD_r6": 410550, "test": 507150}
    assert parse_showcpg_free(_fx("E18U31", "showcpg")) == {"SSD_r6": 2395050}


def test_showvv_sizes_from_showcols():
    text = " Id Name        Prov Type CPG    VSize_MB\n101 zz_t3_vol01 tpvv base SSD_r6    10240\n-----\n  1 total                           10240\n"
    assert parse_showvv_sizes(text) == {"zz_t3_vol01": 10240}
    assert parse_showvv_sizes("Name   VSize_MB\nv1     1024\nv2     2048\n----\n2 total 3072\n") == {"v1": 1024, "v2": 2048}


class _FakeCli:
    """Serves the fixture files for one array as if over SSH."""

    def __init__(self, array: str, *, fail_login: bool = False) -> None:
        self.array, self.fail_login, self.commands = array, fail_login, []

    def __enter__(self):
        if self.fail_login:
            raise RuntimeError("Login failed for 3paradm@10.0.0.9")
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        self.commands.append(command)
        if command.startswith("showvv "):
            return "Name VSize_MB\n300gb 307200\nTest 1024\n"
        return _fx(self.array, command.replace(" -", "_").replace(" ", "_"))


def test_read_array_assembles_the_view_from_one_read_only_session():
    cli = _FakeCli("D22U27")
    view = read_array(EndpointCreds(host="10.64.122.99", username="u", password="p"), array_cli_factory=lambda creds: cli)
    assert view.read_error is None
    assert (view.name, view.serial, view.system_id, view.os_version) == ("AlletraMP_D22U27", "CZ2D320BT1", 188150, "10.5.0")
    assert view.rc_started and view.rc_health == "Normal"
    assert view.rcip_addresses == {"10.54.122.92", "10.54.122.93"}
    assert [t.name for t in view.targets] == ["AlletraMP_E18U31"] and len(view.links) == 4 and len(view.groups) == 6
    assert view.cpg_free_mib["SSD_r6"] == 410550
    assert view.vvsets["300gb"] == ["300gb", "Test"] and view.vvsets["APP_Test"] == ["APP.test.vv"]
    assert view.volume_size_mib == {"300gb": 307200, "Test": 1024}
    assert view.volume_group("300gb") == "300gb" and view.volume_group("nothing") is None
    assert all(c.split()[0].startswith("show") for c in cli.commands)      # ADR 0001: reads only


def test_read_array_reports_a_failed_login_instead_of_raising():
    view = read_array(EndpointCreds(host="10.0.0.9", username="u", password="p"),
                      array_cli_factory=lambda creds: _FakeCli("D22U27", fail_login=True))
    assert view.read_error == "Could not read 10.0.0.9: Login failed for 3paradm@10.0.0.9"
    assert view.groups == [] and view.host == "10.0.0.9"
