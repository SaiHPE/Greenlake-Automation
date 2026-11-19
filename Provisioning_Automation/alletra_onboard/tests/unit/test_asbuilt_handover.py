"""SPEC-026 R4, R5, R8 and R9: the as-built section *Array status at handover*.

Built from the read-only captures in `tests/fixtures/handover/` (rack13-ARCUS, OS 10.6.0, 2026-11-16;
D22U27, E18U31 and VZ, OS 10.5.x, 2026-11-17). Each test names the requirement it proves. Performance
left the section on 2026-11-19 at the owner's request.
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
# The moment each capture's showdate was printed, in UTC: what the as-built step records as the read time.
READ_AT = {
    "rack13": datetime(2026, 11, 16, 17, 57, 23, tzinfo=UTC),
    "D22U27": datetime(2026, 11, 16, 18, 33, 14, tzinfo=UTC),
    "E18U31": datetime(2026, 11, 16, 18, 34, 36, tzinfo=UTC),
    "VZ": datetime(2026, 11, 16, 18, 38, 54, tzinfo=UTC),
}
CREATED = datetime(2026, 11, 11, 18, 0, tzinfo=UTC)   # between rack13's first alerts and alert 40's first occurrence


def _capture(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


def _data(array: str, **over) -> AsBuiltData:
    """An as-built of one lab array, with the three handover reads as the as-built step makes them."""
    folder = FIXTURES / "handover" / array
    data = AsBuiltData(
        name=array, customer="ACME", showdate=_capture(folder / "showdate.txt"),
        showalert_d=_capture(folder / "showalert_d.txt"), showsys_space=_capture(folder / "showsys_space.txt"),
        handover_read_at=READ_AT[array], run_created_at=CREATED,
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


_TITLES = ("Alerts", "Capacity")


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
    assert [p for p in paragraphs if p in ("Alerts", "Capacity")] == ["Alerts", "Capacity"]
    assert paragraphs[-2] == ("This section was read from the array at 2026-11-16 17:57 UTC "
                              "(2026-11-16 23:27 on the array's clock, UTC+05:30).")


@pytest.mark.parametrize("array", ["rack13", "D22U27", "E18U31", "VZ"])
def test_the_section_has_no_performance(array, tmp_path):
    """2026-11-19, the owner's decision: performance removed from the as-built. The title lost "and
    performance"; no window, no figure, no table of nodes, ports or volumes."""
    doc, _ = _render(_data(array), tmp_path)
    assert HANDOVER_HEADING == "Array status at handover"
    assert not [p.text for p in doc.paragraphs if p.style.name.startswith("Heading") and "performance" in p.text.lower()]
    paragraphs, tables = _section(doc)
    assert not [p for p in paragraphs if "performance" in p.lower()]
    assert paragraphs[0] == ("What the array reported about itself when this document was generated: its new alerts "
                             "and its capacity in use. Reading it changed nothing on the array.")
    assert not [p for p in paragraphs if "System Reporter" in p or p in ("Controller nodes", "Host ports", "All volumes")]
    assert [t[0][0] for t in tables if t[0][0] not in ("Id", "Severity")] == ["Capacity"]


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


def test_before_this_run_is_unknown_without_the_arrays_clock(tmp_path):
    """ADR 0019 change 5: the offset comes from showdate against the read; with no clock, every row says unknown."""
    doc, warnings = _render(_data("rack13", read_errors={h.CLOCK: "ArrayCliError: timed out"}), tmp_path)
    paragraphs, tables = _section(doc)
    assert {r[-1] for r in _table(tables, "Id")[1:]} == {"unknown"}
    assert ("Before this run is unknown: the array's clock (showdate) could not be read, so its time zone is not "
            "known.") in paragraphs
    assert paragraphs[-2] == "This section was read from the array at 2026-11-16 17:57 UTC."
    assert any(w.startswith("`showdate` could not be read (") for w in warnings)


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


# ------------------------------------------------------------------ R8: failed reads

def test_a_refused_read_is_named_with_a_warning_and_the_rest_renders(tmp_path):
    """One read refused by the array (its words), one that printed nothing."""
    data = _data("VZ", showsys_space="Error: Invalid option -space\n", showdate="")
    doc, warnings = _render(data, tmp_path)
    paragraphs, tables = _section(doc)
    assert _after(paragraphs, "Capacity") == [f"`{h.SPACE}` could not be read: Error: Invalid option -space",
                                              f"`{h.CLOCK}` could not be read: the array printed nothing"]
    for cmd in (h.CLOCK, h.SPACE):
        assert any(w.startswith(f"`{cmd}` could not be read (") for w in warnings), cmd
    assert not [t for t in tables if t[0][0] == "Capacity"]   # no table of zeros
    assert _table(tables, "Id")                               # the alerts still render


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
