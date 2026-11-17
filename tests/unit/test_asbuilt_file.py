"""SPEC-028 R3: the as-built's File service section, read when the document is made, from the
Unified File captures (`tests/fixtures/unified_file/`): D22U27 (four File ports, the service on,
three file systems and shares) and rack13-ARCUS (no File ports, the service off: no section)."""

from __future__ import annotations

from alletra_onboard.adapters.array.wsapi_v3_client import V3Answer
from alletra_onboard.application.documents import steps as st
from alletra_onboard.application.documents.asbuilt import generate_asbuilt
from alletra_onboard.application.unified_file.read import SESSION_REFUSED, read_array_file
from alletra_onboard.domain.shared import EndpointCreds
from tests.unit.test_asbuilt_replication import _data, _h1, _read, _tables
from tests.unit.test_unified_file_read import CapturedCli, CapturedV3


def _file_data(array: str, v3: CapturedV3 | None = None):
    ports, report = read_array_file(CapturedCli(array), v3 or CapturedV3(array))
    return _data(file_ports=ports, file_report=report)


def test_the_section_shows_the_service_ports_file_systems_and_shares_with_their_clients(tmp_path):
    out, warnings = generate_asbuilt(_file_data("d22u27"), tmp_path / "file.docx")
    doc, text = _read(out)
    assert _h1(doc)[-3:] == ["SAN zoning designed in this run", "Provisioning performed in this run", "File service"]
    assert not [w for w in warnings if "file" in w.lower()]
    section = text.split("Provisioning performed in this run")[-1]
    assert ("File service: on, running on 2 of 2 nodes. Capacity for file: 5.6 TiB, 250 GiB used, "
            "5.3 TiB available.") in section
    tables = _tables(doc)
    assert tables[("Port", "Address", "Gateway", "VLAN", "MTU", "Link")] == [
        ["0:4:1", "10.54.90.70/21", "10.54.95.254", "untagged", "1500", "up (ready)"],
        ["0:4:2", "10.54.90.71/21", "10.54.95.254", "untagged", "1500", "up (ready)"],
        ["1:4:1", "10.54.90.73/21", "10.54.95.254", "untagged", "1500", "up (ready)"],
        ["1:4:2", "10.54.90.74/21", "10.54.95.254", "untagged", "1500", "up (ready)"],
    ]
    assert tables[("File system", "Size", "Data reduction", "Shares", "Owner node", "State")] == [
        ["fs01", "99.9 GiB", "No", "1", "0", "normal"],
        ["lab_100", "99.9 GiB", "No", "1", "0", "normal"],
        ["testfile", "49.9 GiB", "Yes", "1", "0", "normal"],
    ]
    assert tables[("Share", "File system", "Client group", "Clients", "Mount", "Protocol", "State")] == [
        ["share01", "fs01", "fs01", "* rw root_squash", "10.54.90.70:/file/fs01/share01", "NFS", "normal"],
        ["Lab_test", "lab_100", "lab_100", "* rw root_squash", "10.54.90.70:/file/lab_100/Lab_test", "NFS", "normal"],
        ["test1", "testfile", "test1", "* rw root_squash", "10.54.90.71:/file/testfile/test1", "NFS", "normal"],
    ]
    assert "A client of * is any host that can reach the File ports." in section


def test_an_array_without_file_ports_and_its_service_off_has_no_section(tmp_path):
    data = _file_data("rack13")
    assert (data.file_ports, data.file_report) == ([], None)
    out, warnings = generate_asbuilt(data, tmp_path / "block.docx")
    doc, _text = _read(out)
    assert "File service" not in _h1(doc)
    assert not [w for w in warnings if "file" in w.lower()]


def test_a_refused_read_keeps_the_ports_says_why_and_warns(tmp_path):
    v3 = CapturedV3("d22u27", answers={"filesystems": V3Answer(401, {"message": {"key": "INVALID_SESSION_KEY"}})})
    out, warnings = generate_asbuilt(_file_data("d22u27", v3), tmp_path / "refused.docx")
    doc, text = _read(out)
    section = text.split("Provisioning performed in this run")[-1]
    assert SESSION_REFUSED in section
    tables = _tables(doc)
    assert len(tables[("Port", "Address", "Gateway", "VLAN", "MTU", "Link")]) == 4
    assert not any(h[0] in ("File system", "Share") for h in tables)
    assert f"The File service section lists only the File ports: {SESSION_REFUSED}" in warnings


def test_a_read_that_failed_is_named_in_the_section_and_the_warnings(tmp_path):
    out, warnings = generate_asbuilt(_data(file_read_error="ArrayCliError: showport -file failed"),
                                     tmp_path / "failed.docx")
    doc, text = _read(out)
    assert _h1(doc)[-1] == "File service"
    assert "The file side could not be read: ArrayCliError: showport -file failed" in text
    assert any(w.startswith("The file side could not be read (ArrayCliError") for w in warnings)


def test_the_step_reads_the_file_side_in_its_own_ssh_session_with_the_runs_credential(monkeypatch):
    seen = []
    cli = CapturedCli("d22u27")
    monkeypatch.setattr(st, "make_array_cli", lambda creds: cli)
    steps = st.DocumentSteps(coord=None, wsapi_v3_factory=lambda creds: seen.append(creds) or CapturedV3("d22u27"))
    data = steps._collect_asbuilt("10.64.122.99", "3paradm", "pw")
    assert [s.name for s in data.file_report.shares] == ["share01", "Lab_test", "test1"]
    assert len(data.file_ports) == 4 and data.file_read_error == ""
    assert [(c.host, c.username, c.password.get_secret_value()) for c in seen] == [("10.64.122.99", "3paradm", "pw")]
    assert {"showport -file", "showsys"} <= set(cli.sent)


def test_a_file_read_that_raises_never_stops_the_document():
    def boom(cli, v3):
        raise RuntimeError("showport -file: neither a File port nor the array's no-port answer")
    steps = st.DocumentSteps(coord=None, read_file=boom, wsapi_v3_factory=lambda creds: None)
    creds = EndpointCreds(host="10.64.122.99", username="3paradm", password="pw")
    assert steps._collect_file(CapturedCli("d22u27"), creds) == (
        [], None, "RuntimeError: showport -file: neither a File port nor the array's no-port answer")
