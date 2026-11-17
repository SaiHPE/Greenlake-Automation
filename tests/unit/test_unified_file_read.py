"""SPEC-028 R1: the Unified File parsers, pinned to tests/fixtures/unified_file/ (read-only captures):
rack13/ (rack13-ARCUS, OS 10.6.0, 2026-11-16: no File ports, the service off, nothing in it) and
d22u27/ (AlletraMP_D22U27, OS 10.5.0, 2026-11-17: four File ports, the service on, three file
systems, client groups and shares). See each fixtures README for the facts asserted here."""

import copy
import json
from pathlib import Path

import pytest

from alletra_onboard.adapters.array.wsapi_v3_client import (
    V3Answer,
    WsapiV3Error,
    WsapiV3LoginRefused,
)
from alletra_onboard.application.replication.read import parse_showsys, parse_showversion
from alletra_onboard.application.unified_file.read import (
    NO_ANSWER,
    OTHER_ARRAY,
    SERVICE_OFF,
    SESSION_REFUSED,
    UNREADABLE,
    UnexpectedAnswer,
    file_os,
    parse_array_serial,
    parse_fileservice,
    parse_fileshares,
    parse_filesystems,
    parse_help_syntax,
    parse_sharesettings,
    parse_showport_file,
    read_array_file,
    read_file_report,
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


# ---- SPEC-028 R1-R2: read_file_report, against the captures -----------------------------------------

_CLI_FILES = {"showsys": "showsys", "showversion": "showversion", "showport -file": "showport_file",
              "showport": "showport", "shownet": "shownet"}


class CapturedCli:
    """The run's read-only SSH session, answering from one capture; any other command answers ""."""

    def __init__(self, array: str, **override: str) -> None:
        self.array, self.override, self.sent = array, override, []

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def run(self, command: str, timeout: float | None = None) -> str:
        self.sent.append(command)
        if command in self.override:
            return self.override[command]
        name = _CLI_FILES.get(command)
        return _text(self.array, name) if name else ""


class CapturedV3:
    """Stands in for WsapiV3Client and replays one capture's four answers, with what the client
    does: `with` logs in (or raises what a failed login raises) and always logs out; `get` returns
    any HTTP status as an answer. `answers` replaces a resource's answer (a V3Answer, or an
    exception to raise); `edit` changes a copy of a captured body."""

    def __init__(self, array: str, *, login_error: Exception | None = None,
                 answers: dict | None = None, edit: dict | None = None) -> None:
        self.array, self.login_error = array, login_error
        self.answers, self.edit = answers or {}, edit or {}
        self.gets: list[str] = []
        self.withheld: list[str] = []   # what `withhold` said of each answer: "" = logged in full
        self.logins = self.logouts = 0

    def __enter__(self):
        self.logins += 1
        if self.login_error is not None:
            raise self.login_error
        return self

    def __exit__(self, *exc_info):
        self.logouts += 1
        return False

    def get(self, path: str, *, withhold=None) -> V3Answer:
        self.gets.append(path)
        resource = path.strip("/")
        if resource in self.answers:
            answer = self.answers[resource]
            if isinstance(answer, Exception):
                raise answer
        else:
            captured = _answer(self.array, f"wsapi_v3_{resource}")
            body = copy.deepcopy(captured["body"])
            if resource in self.edit:
                body = self.edit[resource](body)
            answer = V3Answer(status=captured["status"], body=body)
        self.withheld.append(withhold(answer) if withhold else "")
        return answer


def _ports(array: str):
    return parse_showport_file(_text(array, "showport_file"))


def _d22u27(**v3):
    v3 = CapturedV3("d22u27", **v3)
    return read_file_report(CapturedCli("d22u27"), v3, "10.5.0", _ports("d22u27")), v3


@pytest.mark.parametrize(("version", "capable"), [
    ("10.5.0", True), ("10.5.60", True), ("10.6.0", True), ("11.0.1", True),
    ("10.4.2", False), ("9.5.3", False), ("", None), ("unknown", None),
])
def test_unified_file_needs_os_10_5(version, capable):
    assert file_os(version) is capable


def test_d22u27_gives_the_whole_file_side_and_closes_its_session():
    report, v3 = _d22u27()
    assert report is not None and report.notes == []
    assert (report.os_version, report.array_serial) == ("10.5.0", "CZ2D320BT1")
    assert report.service.running and [n.status for n in report.service.nodes] == ["normal", "normal"]
    assert [fs.name for fs in report.file_systems] == ["fs01", "lab_100", "testfile"]
    assert [g.name for g in report.client_groups] == ["test1", "fs01", "lab_100"]
    assert [s.name for s in report.shares] == ["share01", "Lab_test", "test1"]
    star = [ClientRule(address="*", access="rw", options="root_squash")]
    assert all(report.clients_of(share) == star for share in report.shares)
    assert v3.gets == ["/fileservice", "/filesystems", "/filesharesettings", "/fileshares"]
    assert (v3.logins, v3.logouts) == (1, 1)


def test_rack13_shows_nothing_although_its_file_api_answers():
    """No File ports and the service off: R2's "most block arrays", read and still not shown."""
    v3 = CapturedV3("rack13")
    assert read_file_report(CapturedCli("rack13"), v3, "10.6.0", _ports("rack13")) is None
    assert len(v3.gets) == 4 and v3.logouts == 1


def test_no_file_ports_below_10_5_or_on_an_unread_os_is_not_read_at_all():
    for version in ("10.4.2", ""):
        v3 = CapturedV3("rack13")
        assert read_file_report(CapturedCli("rack13"), v3, version, []) is None
        assert v3.logins == 0


def test_file_ports_on_an_os_below_10_5_say_so_and_read_nothing():
    v3 = CapturedV3("d22u27")
    report = read_file_report(CapturedCli("d22u27"), v3, "10.4.2", _ports("d22u27"))
    assert report.notes == ["This array runs OS 10.4.2. File shares need OS 10.5 or later."]
    assert report.service is None and v3.logins == 0


def test_no_answer_from_the_file_api_is_a_note_not_a_failure():
    report, v3 = _d22u27(login_error=WsapiV3Error("POST /api/v3/credentials: no answer"))
    assert report.notes == [NO_ANSWER] and report.service is None and v3.gets == []
    report, _ = _d22u27(answers={"filesystems": WsapiV3Error("GET /api/v3/filesystems: no answer")})
    assert report.notes == [NO_ANSWER] and report.service is None and report.file_systems == []


@pytest.mark.parametrize("status", [401, 403])
def test_a_session_turned_down_after_a_good_login_is_the_session_note(status):
    report, v3 = _d22u27(answers={"filesharesettings": V3Answer(status, {"message": {"key": "INVALID_SESSION_KEY"}})})
    assert report.notes == [SESSION_REFUSED] and report.service is None and report.shares == []
    assert v3.gets == ["/fileservice", "/filesystems", "/filesharesettings"] and v3.logouts == 1


def test_a_refused_login_is_the_session_note():
    refused = WsapiV3LoginRefused(V3Answer(401, {"code": 5, "desc": "invalid username or password"}))
    report, _ = _d22u27(login_error=refused)
    assert report.notes == [SESSION_REFUSED]


def test_another_arrays_file_api_is_refused_and_nothing_of_it_is_kept():
    other = _body("rack13", "fileservice")["arraySerialNumber"]
    report, v3 = _d22u27(edit={"fileshares": lambda b: {**b, "arraySerialNumber": other}})
    assert report.notes == [OTHER_ARRAY.format(found="CZ2D2K014S", expected="CZ2D320BT1")]
    # The run's own three answers are logged; the other array's is kept out of the command log.
    assert v3.withheld == ["", "", "", ("(not recorded: the answer names array CZ2D2K014S, not this "
                                        "run's array CZ2D320BT1)")]
    assert report.notes[0] == (
        "The file API at this address belongs to array CZ2D2K014S, not to this run's array CZ2D320BT1, "
        "so file details are not shown. Check the array address in the workbook.")
    assert (report.service, report.file_systems, report.client_groups, report.shares) == (None, [], [], [])


def test_a_collection_that_names_no_array_is_refused_at_once():
    report, v3 = _d22u27(edit={"filesystems": lambda b: {k: v for k, v in b.items() if k != "arraySerialNumber"}})
    assert report.notes == [OTHER_ARRAY.format(found="(no serial given)", expected="CZ2D320BT1")]
    assert report.service is None and report.file_systems == []
    assert v3.gets == ["/fileservice", "/filesystems"] and v3.withheld[1].startswith("(not recorded")
    assert v3.logouts == 1


def test_a_showsys_without_a_serial_refuses_the_read():
    v3 = CapturedV3("d22u27")
    report = read_file_report(CapturedCli("d22u27", showsys=""), v3, "10.5.0", _ports("d22u27"))
    assert report.notes == [OTHER_ARRAY.format(found="CZ2D320BT1", expected="(no serial given)")]
    assert report.service is None


def test_an_answer_the_tool_cannot_read_is_a_note_and_shows_nothing_of_the_read():
    def drop_mountpath(body):
        del next(iter(body["members"].values()))["mountpath"]
        return body
    report, _ = _d22u27(edit={"fileshares": drop_mountpath})
    assert report.notes == [UNREADABLE] and report.service is None and report.file_systems == []
    report, _ = _d22u27(answers={"fileservice": V3Answer(404, {"message": {"key": "NON_EXISTENT_RESOURCE"}})})
    assert report.notes == [UNREADABLE] and report.service is None


def test_without_file_ports_a_failed_read_shows_nothing():
    for v3 in (CapturedV3("rack13", login_error=WsapiV3Error("no answer")),
               CapturedV3("rack13", answers={"fileservice": V3Answer(401, {})}),
               CapturedV3("rack13", edit={"fileshares": lambda b: {**b, "arraySerialNumber": "CZ2D320BT1"}})):
        assert read_file_report(CapturedCli("rack13"), v3, "10.6.0", []) is None


def test_file_ports_with_the_service_off_show_the_service_and_say_it_is_off():
    """rack13's stopped service, read as if its array had D22U27's File ports."""
    report = read_file_report(CapturedCli("rack13"), CapturedV3("rack13"), "10.6.0", _ports("d22u27"))
    assert report.notes == [SERVICE_OFF] and report.notes[0] == (
        "The file service is off on this array. Turn it on in the array's UI before shares can be made.")
    assert report.service is not None and not report.service.enabled and report.shares == []


def test_no_file_ports_with_the_service_on_is_shown():
    """D22U27's running service, read as if the array listed no File port: the service decides."""
    report = read_file_report(CapturedCli("d22u27"), CapturedV3("d22u27"), "10.5.0", [])
    assert report is not None and report.service.running and report.notes == []


def test_the_as_built_read_takes_the_os_and_ports_from_the_array():
    ports, report = read_array_file(CapturedCli("d22u27"), CapturedV3("d22u27"))
    assert [p.label for p in ports] == ["0:4:1", "0:4:2", "1:4:1", "1:4:2"]
    assert report.os_version == "10.5.0" and len(report.shares) == 3
    cli = CapturedCli("rack13")
    assert read_array_file(cli, CapturedV3("rack13")) == ([], None)
    assert cli.sent == ["showversion", "showport -file", "showsys"]


def test_the_as_built_read_refuses_a_showport_file_it_cannot_read_from_10_5():
    with pytest.raises(UnexpectedAnswer):
        read_array_file(CapturedCli("d22u27", **{"showport -file": "Error: unknown option"}), CapturedV3("d22u27"))
    old = CapturedCli("d22u27", **{"showport -file": "Error: unknown option", "showversion": "Release version 10.4.2\n"})
    assert read_array_file(old, CapturedV3("d22u27")) == ([], None)


# ---- Discovery reads the file side after `showport -file` ------------------------------------------

def _discover(array: str, v3):
    from alletra_onboard.application.provisioning import discovery as disc
    from tests.unit.test_storage_services import FakeVCenter, _intent

    return disc.discover(_intent(), array_cli_factory=lambda c: CapturedCli(array),
                         vcenter_factory=lambda c: FakeVCenter([]), wsapi_v3_factory=lambda c: v3)


def test_discovery_carries_the_file_report_beside_the_file_ports():
    report = _discover("d22u27", CapturedV3("d22u27"))
    assert report.error is None
    assert [p.label for p in report.file_ports] == ["0:4:1", "0:4:2", "1:4:1", "1:4:2"]
    assert report.file is not None and [s.name for s in report.file.shares] == ["share01", "Lab_test", "test1"]
    assert "file" in report.model_dump(mode="json")


def test_discovery_of_a_block_only_array_has_no_file_report():
    report = _discover("rack13", CapturedV3("rack13"))
    assert report.error is None and report.file_ports == [] and report.file is None


def test_a_file_side_that_breaks_never_breaks_discovery():
    class Broken(CapturedV3):
        def get(self, path):
            raise RuntimeError("a bug in the file read")
    report = _discover("d22u27", Broken("d22u27"))
    assert report.error is None and report.file.notes == [UNREADABLE]
    assert [p.label for p in report.file_ports] == ["0:4:1", "0:4:2", "1:4:1", "1:4:2"]
