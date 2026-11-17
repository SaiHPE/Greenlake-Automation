"""SPEC-028 R1: the Unified File parsers, pinned to tests/fixtures/unified_file/ (read-only captures):
rack13/ (rack13-ARCUS, OS 10.6.0, 2026-11-16: no File ports, the service off, nothing in it) and
d22u27/ (AlletraMP_D22U27, OS 10.5.0, 2026-11-17: four File ports, the service on, three file
systems, client groups and shares). See each fixtures README for the facts asserted here."""

import json
from pathlib import Path

import pytest

from alletra_onboard.application.replication.read import parse_showsys, parse_showversion
from alletra_onboard.application.unified_file.read import (
    UnexpectedAnswer,
    parse_array_serial,
    parse_fileservice,
    parse_fileshares,
    parse_filesystems,
    parse_help_syntax,
    parse_sharesettings,
    parse_showport_file,
)
from alletra_onboard.domain.unified_file import (
    FILE_CLI_SYNTAX,
    NODE_RUNNING,
    ClientRule,
    FileCapacity,
    FileNodeStatus,
    FilePortStatus,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "unified_file"
ARRAYS = ("rack13", "d22u27")
V3 = ("fileservice", "filesystems", "filesharesettings", "fileshares")


def _text(array: str, name: str) -> str:
    return (FIX / array / f"{name}.txt").read_text(encoding="utf-8")


def _answer(array: str, name: str) -> dict:
    """One saved HTTP answer: {"request", "port", "status", "headers", "body"}."""
    return json.loads((FIX / array / f"{name}.json").read_text(encoding="utf-8"))


def _body(array: str, resource: str) -> dict:
    answer = _answer(array, f"wsapi_v3_{resource}")
    assert (answer["status"], answer["port"]) == (200, 443)
    return answer["body"]


# ---- rack13-ARCUS: no File ports, the service off -----------------------------------------------

def test_the_file_service_is_there_and_stopped_on_an_array_with_no_file_ports():
    service = parse_fileservice(_body("rack13", "fileservice"))
    assert service is not None
    assert service.uid == "ceae1a870c8099a87e32dc556b891cca"
    assert (service.enabled, service.running) == (False, False)
    assert (service.name, service.system_wwn) == ("File Service on 2FF70002AC02D495", "2FF70002AC02D495")
    assert "2FF70002AC02D495" in _text("rack13", "showport")    # the FC Node_WWN
    assert (service.domain, service.ransomware_check) == ("", False)
    # Two ports per node, and no port id on either: which N:S:P they stand for is not shown.
    idle = FilePortStatus(configured=False, online=False, mtu=0)
    assert service.nodes == [FileNodeStatus(node=0, status="stopped", ports=[idle, idle]),
                             FileNodeStatus(node=1, status="stopped", ports=[idle, idle])]
    assert service.capacity == FileCapacity(total=0, used=0, available=0, limit_percentage=0,
                                            file_systems=0, file_shares=0)


def test_an_empty_collection_is_an_empty_members_map_and_agrees_with_the_service_counts():
    for resource in ("filesystems", "filesharesettings", "fileshares"):
        assert _body("rack13", resource)["members"] == {}
    assert parse_filesystems(_body("rack13", "filesystems")) == []
    assert parse_sharesettings(_body("rack13", "filesharesettings")) == []
    assert parse_fileshares(_body("rack13", "fileshares")) == []
    capacity = parse_fileservice(_body("rack13", "fileservice")).capacity
    assert (capacity.file_systems, capacity.file_shares) == (0, 0)


def test_showport_file_no_port_answer_means_no_file_ports_and_showport_agrees():
    assert _text("rack13", "showport_file").splitlines()[1] == "There is no specified port information."
    assert parse_showport_file(_text("rack13", "showport_file")) == []
    rows = [line.split() for line in _text("rack13", "showport").splitlines()]
    assert [r[0] for r in rows if len(r) >= 8 and r[5] == "file"] == []
    assert {r[0]: r[6] for r in rows if len(r) >= 8 and r[0].endswith((":4:1", ":4:2"))} == {
        "0:4:1": "iSCSI", "0:4:2": "iSCSI", "1:4:1": "iSCSI", "1:4:2": "iSCSI"}


# ---- AlletraMP_D22U27: four File ports, the service on, three of everything ---------------------

def test_the_file_service_runs_on_both_nodes_of_d22u27():
    service = parse_fileservice(_body("d22u27", "fileservice"))
    assert (service.enabled, service.running, NODE_RUNNING) == (True, True, "normal")
    assert (service.name, service.system_wwn) == ("File Service on 2FF70002AC02DEF6", "2FF70002AC02DEF6")
    assert "2FF70002AC02DEF6" in _text("d22u27", "showport")
    up = FilePortStatus(configured=True, online=True, mtu=1500)
    assert service.nodes == [FileNodeStatus(node=0, status="normal", ports=[up, up]),
                             FileNodeStatus(node=1, status="normal", ports=[up, up])]
    # OS 10.5.0 (v3 2.5.0) sends three capacity fields and no ransomware flag; None = not said.
    assert service.capacity == FileCapacity(total=5855641, used=256000, available=5599641)
    assert service.ransomware_check is None


def test_capacity_is_in_mib_used_is_the_file_systems_volumes():
    service = parse_fileservice(_body("d22u27", "fileservice"))
    systems = parse_filesystems(_body("d22u27", "filesystems"))
    assert service.capacity.used == sum(fs.vv_size_mib for fs in systems) == 256000
    assert service.capacity.total == service.capacity.used + service.capacity.available


def test_file_systems_have_their_real_fields():
    systems = parse_filesystems(_body("d22u27", "filesystems"))
    assert [(fs.name, fs.size_mib, fs.vv_size_mib, fs.reduce, fs.prov) for fs in systems] == [
        ("fs01", 102272, 102400, False, "tpvv"),
        ("lab_100", 102272, 102400, False, "tpvv"),
        ("testfile", 51072, 51200, True, "tdvv"),
    ]
    for fs in systems:
        assert (fs.state, fs.share_count, fs.owner_node, fs.volumes) == ("STATE_NORMAL", 1, 0, [fs.name])
    assert [fs.id for fs in systems] == [0, 2, 10]
    assert list(_body("d22u27", "filesystems")["members"]) == [fs.uid for fs in systems]


def test_client_groups_list_their_clients():
    groups = parse_sharesettings(_body("d22u27", "filesharesettings"))
    assert [g.name for g in groups] == ["test1", "fs01", "lab_100"]
    for group in groups:
        assert group.clients == [ClientRule(address="*", access="rw", options="root_squash")]
        assert (group.state, group.host_count, group.share_count) == ("STATE_NORMAL", 1, 1)
    assert list(_body("d22u27", "filesharesettings")["members"]) == [g.uid for g in groups]


def test_shares_name_their_file_system_client_group_mount_path_and_port():
    shares = parse_fileshares(_body("d22u27", "fileshares"))
    assert [(s.name, s.file_system, s.client_group, s.mount_path, s.host_ip) for s in shares] == [
        ("share01", "fs01", "fs01", "/file/fs01/share01", "10.54.90.70"),
        ("Lab_test", "lab_100", "lab_100", "/file/lab_100/Lab_test", "10.54.90.70"),
        ("test1", "testfile", "test1", "/file/testfile/test1", "10.54.90.71"),
    ]
    for share in shares:
        assert (share.state, share.protocols) == ("STATE_NORMAL", ["NFS"])
    assert list(_body("d22u27", "fileshares")["members"]) == [s.uid for s in shares]


def test_a_share_joins_its_file_system_client_group_and_file_port_by_name():
    systems = {fs.name: fs for fs in parse_filesystems(_body("d22u27", "filesystems"))}
    groups = {g.name: g for g in parse_sharesettings(_body("d22u27", "filesharesettings"))}
    ports = {p.address for p in parse_showport_file(_text("d22u27", "showport_file"))}
    records = {r["name"]: r for r in _body("d22u27", "fileshares")["members"].values()}
    for share in parse_fileshares(_body("d22u27", "fileshares")):
        assert share.file_system in systems and share.client_group in groups
        assert share.mount_path == f"/file/{share.file_system}/{share.name}"
        assert share.host_ip in ports
        # The share repeats its group's clients; the group is the one source read (lesson 41).
        repeated = [ClientRule(address=c["ipaddress"], access=c["access"], options=c["options"])
                    for c in records[share.name]["sharesettings"]["clientInfo"]]
        assert repeated == groups[share.client_group].clients
    # "Maximum of one share can be created in a filesystem" (help createfileshare).
    assert all(fs.share_count == 1 for fs in systems.values())


def test_showport_file_lists_the_four_file_ports_two_per_node_as_portstatus_does():
    ports = parse_showport_file(_text("d22u27", "showport_file"))
    assert [(p.label, p.address, p.prefix_len, p.link, p.mtu) for p in ports] == [
        ("0:4:1", "10.54.90.70", "21", "up", "1500"), ("0:4:2", "10.54.90.71", "21", "up", "1500"),
        ("1:4:1", "10.54.90.73", "21", "up", "1500"), ("1:4:2", "10.54.90.74", "21", "up", "1500"),
    ]
    service = parse_fileservice(_body("d22u27", "fileservice"))
    for node in service.nodes:
        assert len(node.ports) == sum(1 for p in ports if p.node == node.node)


# ---- both arrays ------------------------------------------------------------------------------------

@pytest.mark.parametrize(("array", "serial", "os", "v3"), [
    ("rack13", "CZ2D2K014S", "10.6.0", "2.6.0.1895"),
    ("d22u27", "CZ2D320BT1", "10.5.0", "2.5.0.1463"),
])
def test_every_v3_answer_names_the_array_showsys_names(array, serial, os, v3):
    assert parse_showsys(_text(array, "showsys"))["serial"] == serial
    assert {parse_array_serial(_body(array, r)) for r in V3} == {serial}
    assert parse_showversion(_text(array, "showversion")) == os
    assert {dict(_answer(array, f"wsapi_v3_{r}")["headers"])["X-Server-Version"] for r in V3} == {v3}


def test_an_answer_without_a_members_map_is_refused_not_read_as_empty():
    logout = _answer("rack13", "wsapi_v3_logout")["body"]            # "" (the logout's empty body)
    system = _answer("rack13", "wsapi_v1_system")["body"]            # a v1 record, no members
    for body in (logout, system):
        for parse in (parse_fileservice, parse_filesystems, parse_sharesettings, parse_fileshares):
            with pytest.raises(UnexpectedAnswer):
                parse(body)
    assert parse_array_serial(logout) == ""


@pytest.mark.parametrize(("array", "resource", "field", "parse"), [
    ("rack13", "fileservice", "fileServiceSummary", parse_fileservice),
    ("d22u27", "filesystems", "sizeInMiB", parse_filesystems),
    ("d22u27", "filesharesettings", "clientInfo", parse_sharesettings),
    ("d22u27", "fileshares", "mountpath", parse_fileshares),
])
def test_a_record_missing_a_field_it_needs_is_refused(array, resource, field, parse):
    body = _body(array, resource)
    del next(iter(body["members"].values()))[field]
    with pytest.raises(UnexpectedAnswer):
        parse(body)


def test_an_empty_showport_file_reply_is_not_no_file_ports():
    with pytest.raises(UnexpectedAnswer):
        parse_showport_file("")


def test_the_file_cli_forms_are_the_arrays_own_syntax_lines():
    assert set(FILE_CLI_SYNTAX) == {
        "showfileservice", "showfilesystem", "showfileshare", "showsharesetting",
        "createfilesystem", "createsharesetting", "createfileshare",
        "removefileshare", "removefilesystem", "removesharesetting",
    }
    for command, form in FILE_CLI_SYNTAX.items():
        assert parse_help_syntax(_text("d22u27", f"help_{command}")) == [form]
        verb = next(v for v in ("show", "create", "remove") if command.startswith(v))
        assert f"    {command} " in _text("d22u27", f"help_{verb}")    # listed in the help index
    for command in ("showfileservice", "showfilesystem", "showfileshare"):
        assert parse_help_syntax(_text("rack13", f"help_{command}")) == [FILE_CLI_SYNTAX[command]]
    assert "    showsharesetting " in _text("rack13", "help_show")


def test_the_help_facts_the_spec_cites():
    def said(name: str) -> str:
        return " ".join(_text("d22u27", name).split())
    assert ("User supplied names for the create* commands are limited to alphanumeric characters, "
            'period/dot, dash and underscore. Names cannot start with a "-".') in said("help_create")
    assert "Maximum of one share can be created in a filesystem." in said("help_createfileshare")
    assert "The size is rounded up to the next multiple of 256 MB." in said("help_createfilesystem")
    assert ("-reduce Specifies that the filesystem should use thin provisioning with compression and "
            "dedup technologies. This is the default option.") in said("help_createfilesystem")
    assert ("Following options will be applied by default and cannot be changed: sync, wdelay, "
            "sec=sys, subtree_check, secure, hide.") in said("help_createsharesetting")
    assert "A sharesetting needs to be created before creating a fileshare." in said(
        "help_createsharesetting")
    assert "if fileshare is present on it will fail the command." in said("help_removefilesystem")
    assert ("if there is any file share object associated with this setting causes the command to "
            "fail") in said("help_removesharesetting")
    assert "The fileshare can only be removed if there is no user data in the share." in said(
        "help_removefileshare")


def test_the_cli_has_no_file_persona_commands():
    for array in ARRAYS:
        for old in ("showfs", "showfpg", "showvfs", "showfshare", "showfstore"):
            assert _text(array, f"help_{old}").splitlines()[1] == f"No help for {old}"
        assert "required only when switching out of or into File mode" in " ".join(
            _text(array, "help_controlport").split())


@pytest.mark.parametrize("array", ARRAYS)
def test_the_capture_keeps_no_session_value_and_no_contact(array):
    for name in ("wsapi_v1_login", "wsapi_v3_login"):
        answer = _answer(array, name)
        assert answer["status"] == 201
        assert all(str(v).startswith("<redacted") for v in answer["body"].values())
        headers = answer["headers"]
        assert dict(headers)["Location"].endswith("/credentials/<redacted>")
        for key, value in headers:
            if key == "Set-Cookie":
                assert value.split(";")[0].endswith("=<redacted>")
    login = _answer(array, "wsapi_v3_login")
    assert [v.split("=")[0] for k, v in login["headers"] if k == "Set-Cookie"] == [
        "sessionToken", "hpeWsapiSentryLineage", "hpeWsapiSentryUsername"]
    assert sorted(login["body"]) == ["arrayPrivileges", "key", "sessionId", "username"]
    assert _answer(array, "wsapi_v1_system")["body"]["contact"].startswith("<removed")
