"""SPEC-026 R4 to R9: the as-built section *Array status and performance at handover*.

Built from the read-only captures in `tests/fixtures/handover/` (rack13-ARCUS, OS 10.6.0, 2026-11-16;
D22U27, E18U31 and VZ, OS 10.5.x, 2026-11-17) with each array's `showport` from the same nights in
`tests/fixtures/peer_ports/` (BL-26). Each test names the requirement it proves.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import docx
import pytest
from docx.table import Table
from docx.text.paragraph import Paragraph

from alletra_onboard.application.documents import handover as h
from alletra_onboard.application.documents.asbuilt import (
    HANDOVER_HEADING,
    AsBuiltData,
    generate_asbuilt,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
READ_AT = datetime(2026, 11, 16, 18, 40, tzinfo=UTC)
CREATED = datetime(2026, 11, 11, 18, 0, tzinfo=UTC)   # between rack13's first alerts and alert 40's first occurrence


def _capture(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


def _data(array: str, *, cpu: str = "srstatcpu_24h_v2.txt", ports: str = "srstatport_24h_v2.txt", **over) -> AsBuiltData:
    """An as-built of one lab array, with the five handover reads as the as-built step makes them."""
    folder = FIXTURES / "handover" / array
    if array == "rack13":           # captured before the corrected forms existed
        cpu, ports = cpu.replace("_v2", ""), ports.replace("_v2", "")
    data = AsBuiltData(
        name=array, customer="ACME",
        showalert_d=_capture(folder / "showalert_d.txt"), showsys_space=_capture(folder / "showsys_space.txt"),
        srstatcpu=_capture(folder / cpu), srstatport=_capture(folder / ports),
        srstatvv=_capture(folder / "srstatvv_24h.txt"),
        showport=_capture(FIXTURES / "peer_ports" / array / "showport.txt"),
        handover_read_at=READ_AT, run_created_at=CREATED,
    )
    for key, value in over.items():
        setattr(data, key, value)
    return data


def _render(data: AsBuiltData, tmp_path) -> tuple[docx.document.Document, list[str]]:
    out, warnings = generate_asbuilt(data, tmp_path / f"{data.name}.docx")
    return docx.Document(str(out)), warnings


def _section(doc) -> tuple[list[str], list[list[list[str]]]]:
    """The section's paragraphs and tables, from its heading to the next Heading 1."""
    paragraphs: list[str] = []
    tables: list[list[list[str]]] = []
    inside = False
    for element in doc.element.body.iterchildren():
        if element.tag.endswith("}p"):
            para = Paragraph(element, doc)
            if para.style.name == "Heading 1":
                if inside:
                    break
                inside = para.text.strip() == HANDOVER_HEADING
                continue
            if inside and para.text.strip():
                paragraphs.append(para.text.strip())
        elif inside and element.tag.endswith("}tbl"):
            tables.append([[c.text.strip() for c in row.cells] for row in Table(element, doc).rows])
    return paragraphs, tables


def _table(tables, first_header: str) -> list[list[str]]:
    return next(t for t in tables if t[0][0] == first_header)


_TITLES = ("Alerts", "Capacity", "Performance", "Controller nodes", "Host ports", "All volumes")


def _after(paragraphs: list[str], title: str) -> list[str]:
    """The paragraphs of one subsection: up to the next title, or the section's two closing lines."""
    start = paragraphs.index(title) + 1
    end = next((i for i, p in enumerate(paragraphs[start:], start)
                if p in _TITLES or p.startswith("This section was read from the array")), len(paragraphs))
    return paragraphs[start:end]


# ------------------------------------------------------------------ R9: place

def test_the_section_follows_checkhealth_before_the_run_sections(tmp_path):
    doc, _ = _render(_data("rack13"), tmp_path)
    h1 = [p.text.strip() for p in doc.paragraphs if p.style.name == "Heading 1"]
    i = next(k for k, t in enumerate(h1) if "checkhealth" in t.lower())
    assert h1[i + 1:i + 3] == [HANDOVER_HEADING, "Hosts and host sets"]
    paragraphs, _ = _section(doc)
    assert [p for p in paragraphs if p in ("Alerts", "Capacity", "Performance")] == ["Alerts", "Capacity", "Performance"]
    assert paragraphs[-2] == ("This section was read from the array at 2026-11-16 18:40 UTC "
                              "(2026-11-17 00:10 on the array's clock, UTC+05:30).")


def test_no_section_when_the_reads_were_not_made(tmp_path):
    doc, warnings = _render(_data("rack13", handover_read_at=None), tmp_path)
    assert HANDOVER_HEADING not in [p.text.strip() for p in doc.paragraphs]
    assert not [w for w in warnings if "alert" in w]


# ------------------------------------------------------------------ R4: alerts

def test_verdict_with_the_cloud_sentence(tmp_path):
    paragraphs, _ = _section(_render(_data("rack13"), tmp_path)[0])
    assert _after(paragraphs, "Alerts")[0] == (
        "9 new alerts; the oldest first occurred on 2026-11-11 23:22:51 IST. Alerts record an event, not the "
        "current state: compare each with checkhealth before acting. The array reports it is disconnected from "
        "Data Services Cloud Console (alert 40).")


def test_verdict_without_the_cloud_sentence(tmp_path):
    text = _capture(FIXTURES / "handover" / "rack13" / "showalert_d.txt")
    without_40 = text[:text.index("Id          : 40")] + "8 alerts\n"
    paragraphs, _ = _section(_render(_data("rack13", showalert_d=without_40), tmp_path)[0])
    verdict = _after(paragraphs, "Alerts")[0]
    assert verdict.startswith("8 new alerts; the oldest first occurred on 2026-11-11 23:22:51 IST.")
    assert "Data Services Cloud Console" not in verdict


def test_no_new_alerts(tmp_path):
    """E18U31 prints `no alerts`: one sentence, no table, no warning."""
    doc, warnings = _render(_data("E18U31"), tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "Alerts") == ["No new alerts."]
    assert not [t for t in tables if t[0][0] in ("Id", "Severity")]
    assert not [w for w in warnings if "alert" in w]


def test_major_and_worse_in_full_with_before_this_run(tmp_path):
    """rack13: 27, 28, 31 and 34 first occurred before the run was created; alert 40 first occurred
    after it, though its Time says otherwise only by its latest occurrence."""
    paragraphs, tables = _section(_render(_data("rack13"), tmp_path)[0])
    full = _table(tables, "Id")
    assert full[0] == ["Id", "Severity", "Message code", "Message", "First occurred", "Latest", "Before this run"]
    assert [(r[0], r[1], r[-1]) for r in full[1:]] == [
        ("40", "Major", "No"), ("34", "Critical", "Yes"), ("31", "Critical", "Yes"),
        ("28", "Major", "Yes"), ("27", "Major", "Yes")]
    assert full[1][3:6] == [("Storage system has been disconnected from Data Services Cloud Console for more "
                             "than 7200 minutes."), "2026-11-11 23:54:31 IST", "2026-11-16 23:25:20 IST"]
    assert "Before this run is unknown" not in " ".join(paragraphs)


def test_the_rest_grouped_and_the_pointer_to_the_array(tmp_path):
    paragraphs, tables = _section(_render(_data("D22U27"), tmp_path)[0])
    assert len(_table(tables, "Id")) == 1 + 4
    grouped = _table(tables, "Severity")
    assert grouped[0] == ["Severity", "Message code", "Alerts", "First occurred", "Latest", "Sample message"]
    assert [r[:4] for r in grouped[1:]] == [["Minor", "0x00e000a", "521", "2026-09-30 20:00:00 IST"]]
    assert ("The full list is on the array: showalert -d. Once the cause of an alert is dealt with, setalert or "
            "removealert on the array acknowledges or removes it; the tool runs neither.") in paragraphs


@pytest.mark.parametrize("array, groups", [("rack13", 2), ("VZ", 3)])
def test_every_alert_is_in_a_row_or_a_group(array, groups, tmp_path):
    _paragraphs, tables = _section(_render(_data(array), tmp_path)[0])
    grouped = _table(tables, "Severity")[1:]
    assert len(grouped) == groups
    count = len(_table(tables, "Id")) - 1 + sum(int(r[2]) for r in grouped)
    assert count == len(h.parse_alerts(_data(array).showalert_d))


def test_before_this_run_is_unknown_without_a_system_reporter_read(tmp_path):
    """ADR 0019 change 5: the offset comes only from System Reporter; with none read, every row says unknown."""
    failed = {cmd: "ArrayCliError: timed out" for cmd in (h.CPU, h.PORTS, h.VOLUMES)}
    paragraphs, tables = _section(_render(_data("rack13", read_errors=dict(failed)), tmp_path)[0])
    assert {r[-1] for r in _table(tables, "Id")[1:]} == {"unknown"}
    assert ("Before this run is unknown: no System Reporter report was read, so the array's time zone is not "
            "known.") in paragraphs
    assert paragraphs[-2] == "This section was read from the array at 2026-11-16 18:40 UTC."


@pytest.mark.parametrize("array, ids", [("rack13", [40, 34, 31, 28, 27]), ("D22U27", None), ("E18U31", [])])
def test_each_major_or_worse_alert_is_a_warning_never_a_block(array, ids, tmp_path):
    doc, warnings = _render(_data(array), tmp_path)
    alert_warnings = [w for w in warnings if w.startswith("The array has a new ")]
    if ids is not None:
        assert [int(w.split(" alert ")[1].split()[0]) for w in alert_warnings] == ids
    else:
        assert len(alert_warnings) == 4
    assert HANDOVER_HEADING in [p.text.strip() for p in doc.paragraphs]   # the document is still produced
    if array == "rack13":
        assert alert_warnings[0] == (
            "The array has a new Major alert 40 (first occurred 2026-11-11 23:54:31 IST): Storage system has been "
            "disconnected from Data Services Cloud Console for more than 7200 minutes. Check whether it still "
            "applies before you send the document.")


# ------------------------------------------------------------------ R5: capacity

def test_capacity_in_tib_with_the_arrays_own_figure(tmp_path):
    paragraphs, tables = _section(_render(_data("VZ"), tmp_path)[0])
    capacity = _table(tables, "Capacity")
    assert capacity == [
        ["Capacity", "TiB", "MiB, as the array prints it"],
        ["Raw total", "41.9", "43929600"], ["Raw allocated", "0.7", "696198"], ["Raw free", "35.5", "37244026"],
        ["Usable total", "28.2", "29547910"], ["Usable used", "0.6", "599314"], ["Usable free", "27.6", "28948596"],
    ]
    assert "Data reduction: >25 (the array's ratio)." in paragraphs


# ------------------------------------------------------------------ R6: performance

@pytest.mark.parametrize("array, ports, idle", [
    ("rack13", "srstatport_24h_v2.txt", True),       # no host I/O; its volumes still show 27.6 IO/s
    ("VZ", "srstatport_24h_v2.txt", True),            # 0.9 IO/s
    ("E18U31", "srstatport_24h.txt", True),           # FC only: 2.7 IO/s
    ("E18U31", "srstatport_24h_v2.txt", False),       # with its iSCSI ports: 26.3 IO/s
    ("D22U27", "srstatport_24h_v2.txt", False),       # 44.2 IO/s
])
def test_the_performance_sentence_always_and_the_idle_sentence_below_idle_iops(array, ports, idle, tmp_path):
    paragraphs, _ = _section(_render(_data(array, ports=ports), tmp_path)[0])
    performance = _after(paragraphs, "Performance")
    assert performance[0].startswith("From the array's System Reporter, the 24 hours before the read: from ")
    assert "in 5-minute samples" in performance[0]
    assert performance[1] == "These figures are the load seen in this window, not what the array can do."
    assert (h.IDLE_NOTE in performance) is idle


def test_cpu_table_per_node_busy(tmp_path):
    _paragraphs, tables = _section(_render(_data("D22U27"), tmp_path)[0])
    assert _table(tables, "Node") == [
        ["Node", "Average % busy", "95th percentile % busy", "Busiest sample % busy"],
        ["0", "3.5", "3.5", "6.0"], ["1", "4.2", "4.3", "5.8"],
    ]


def test_the_first_cpu_form_leaves_the_busiest_sample_unknown_not_zero(tmp_path):
    _paragraphs, tables = _section(_render(_data("rack13"), tmp_path)[0])
    assert _table(tables, "Node")[1:] == [["0", "7.8", "—", "—"], ["1", "7.5", "—", "—"]]


def test_ready_ports_in_the_table_and_the_others_in_one_line(tmp_path):
    """VZ (§2a item 9): four ready FC ports in the table; four offline, unconfigured iSCSI ports named."""
    paragraphs, tables = _section(_render(_data("VZ"), tmp_path)[0])
    ports = _table(tables, "Port")
    assert ports[0] == ["Port", "Protocol", "IO/s", "MB/s", "Service time (ms)"]
    assert [r[:2] for r in ports[1:]] == [["0:3:1", "FC"], ["0:3:2", "FC"], ["1:3:1", "FC"], ["1:3:2", "FC"]]
    assert ports[1][2:] == ["0.4 / 1.5 / 1.5", "0.0 / 0.6 / 0.6", "0.14 / 0.19 / 0.20"]
    assert _after(paragraphs, "Host ports") == ["4 iSCSI ports not configured, no I/O: 0:4:1, 0:4:2, 1:4:1, 1:4:2."]


def test_volumes_for_the_whole_array(tmp_path):
    _paragraphs, tables = _section(_render(_data("rack13"), tmp_path)[0])
    assert _table(tables, "Volumes") == [["Volumes", "IO/s", "MB/s", "Service time (ms)"],
                                         ["All volumes together", "27.6 / 30.8 / 104.9", "0.2 / 0.2 / 2.3",
                                          "0.23 / 0.26 / 0.27"]]


def test_a_report_with_no_rows_says_so_without_a_warning(tmp_path):
    """R8: nothing in the window is a sentence, not a failed read."""
    vv = _capture(FIXTURES / "handover" / "VZ" / "srstatvv_24h.txt")
    header_only = vv[:vv.index("\n", vv.index("Summary")) + 1]
    doc, warnings = _render(_data("VZ", srstatvv=header_only), tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "All volumes") == ["System Reporter printed no volume figure for this window."]
    assert not [t for t in tables if t[0][0] == "Volumes"]
    assert not [w for w in warnings if "srstatvv" in w]


def test_no_host_port_row_is_said_and_never_called_idle(tmp_path):
    ports = _capture(FIXTURES / "handover" / "VZ" / "srstatport_24h_v2.txt")
    header_only = ports[:ports.index("\n", ports.index("Summary")) + 1]
    doc, warnings = _render(_data("VZ", srstatport=header_only), tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "Host ports") == ["System Reporter printed no FC or iSCSI host port for this window."]
    assert h.PERFORMANCE_NOTE in paragraphs and h.IDLE_NOTE not in paragraphs
    assert not [t for t in tables if t[0][0] == "Port"] and not [w for w in warnings if "srstatport" in w]


# ------------------------------------------------------------------ R8: failed reads

def test_a_refused_read_is_named_with_a_warning_and_the_rest_renders(tmp_path):
    """One read refused by the client, one refused by the array (its words), one that printed nothing."""
    refused = "ArrayCliError: refused: 'srstatcpu' is not a read-only show command"
    data = _data("VZ", srstatcpu="", read_errors={h.CPU: refused}, showsys_space="Error: Invalid option -space\n",
                 srstatvv="")
    doc, warnings = _render(data, tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "Controller nodes") == [f"`{h.CPU}` could not be read: {refused}"]
    assert _after(paragraphs, "Capacity") == [f"`{h.SPACE}` could not be read: Error: Invalid option -space"]
    assert _after(paragraphs, "All volumes") == [f"`{h.VOLUMES}` could not be read: the array printed nothing"]
    for cmd in (h.CPU, h.SPACE, h.VOLUMES):
        assert any(w.startswith(f"`{cmd}` could not be read (") for w in warnings), cmd
    assert not [t for t in tables if t[0][0] in ("Node", "Capacity", "Volumes")]   # no table of zeros
    assert _table(tables, "Port") and _table(tables, "Id")                        # the others still render
    assert h.PERFORMANCE_NOTE in paragraphs and h.IDLE_NOTE in paragraphs


def test_alerts_not_read(tmp_path):
    data = _data("rack13", showalert_d="", read_errors={h.ALERTS: "ArrayCliError: running 'showalert -d' failed: timeout"})
    doc, warnings = _render(data, tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "Alerts") == [(f"`{h.ALERTS}` could not be read: ArrayCliError: running "
                                             "'showalert -d' failed: timeout")]
    assert not [t for t in tables if t[0][0] == "Id"]
    assert paragraphs[-1].startswith("Cloud connection: unknown, the alerts could not be read.")
    assert any(w.startswith(f"`{h.ALERTS}` could not be read") for w in warnings)


# ------------------------------------------------------------------ R9: the cloud line

@pytest.mark.parametrize("array, line", [
    ("rack13", ('Cloud connection: the array reports it is disconnected from Data Services Cloud Console (alert 40: '
                '"Storage system has been disconnected from Data Services Cloud Console for more than 7200 minutes."). '
                "The tool did not read HPE's cloud view of this array (call-home).")),
    ("E18U31", ("Cloud connection: the array has no New alert about it. The tool did not read HPE's cloud view of "
                "this array (cloud connection, call-home).")),
])
def test_the_cloud_line_closes_the_section(array, line, tmp_path):
    paragraphs, _ = _section(_render(_data(array), tmp_path)[0])
    assert paragraphs[-1] == line


# ------------------------------------------------------------------ UX-GUIDELINES §4

@pytest.mark.parametrize("array", ["rack13", "D22U27", "E18U31", "VZ"])
def test_the_section_never_says_health_outside_the_command_name(array, tmp_path):
    doc, warnings = _render(_data(array), tmp_path)
    paragraphs, tables = _section(doc)
    ours = [w for w in warnings if w.startswith("The array has a new ")]
    text = " ".join(paragraphs + [c for t in tables for r in t for c in r] + ours).lower()
    assert "health" not in text.replace("checkhealth", "")
