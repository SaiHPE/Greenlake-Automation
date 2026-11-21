"""As-built document generation (the 'Document' step — the LAST step after initialisation).

Fills HPE's "Block Storage" as-built Word template (bundled as ``resources/asbuilt_template.docx``)
with this deployment's **read-only** array facts, preserving everything the template already provides:
its cover page (with the ``<Customer Name>`` placeholder), table of contents, architecture sections,
HPE Graphik fonts, and Table 01's formatting. Only the per-deployment regions are written:

  * cover page — the customer name replaces ``<Customer Name>``.
  * Table 01 (Alletra configuration) — the config fields, matched by the label in column 0.
  * Alletra Inventory — ``showinventory`` output (verbatim, monospace — a raw hardware dump).
  * Alletra MP checkhealth output — rendered as two formatted Word tables (Summary + Details).

Parsing the raw ``show*`` text into ``AsBuiltData`` lives in ``asbuilt_parse.py`` (live-calibrated).
"""

from __future__ import annotations

import io
import os
import re
import sys
import zipfile
from collections import OrderedDict
from datetime import UTC
from functools import partial
from pathlib import Path
from types import EllipsisType

import docx
import structlog
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.paragraph import Paragraph

from alletra_onboard.application.documents import handover
from alletra_onboard.application.documents.asbuilt_docx import (
    add_h1,
    add_mono,
    add_para,
    add_table,
    content_widths,
    format_when,
    hpe_table,
    read_failed,
)
from alletra_onboard.application.documents.asbuilt_model import AsBuiltData
from alletra_onboard.application.documents.asbuilt_network import (
    add_iscsi_network_section,
    add_peer_ports_section,
    add_zoning_section,
)
from alletra_onboard.application.documents.asbuilt_parse import (
    parse_checkhealth,
    parse_inventory,
    parse_showvlun_templates_cli,
    parse_showvv,
)
from alletra_onboard.application.documents.asbuilt_replication import add_replication_section
from alletra_onboard.application.documents.asbuilt_snapshots import (
    add_snapshots_section,
    snapshot_removal_items,
)
from alletra_onboard.application.provisioning.discovery import (
    UNCLAIMED_HOST,
    parse_showhost,
)
from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active
from alletra_onboard.domain.array_parse import parse_cli_sets
from alletra_onboard.domain.shared import REMOVAL_ORDER
from alletra_onboard.domain.unified_file import NODE_RUNNING

_log = structlog.get_logger(__name__)

#: Narrative placeholders in the template -> the AsBuiltData field that fills them. Matched
#: case-insensitively; HPE's own template varies the capitalisation of the same field.
_PLACEHOLDER_TO_FIELD: dict[str, str] = {
    "<Customer Name>": "customer",
    "<Site Location>": "site",
    "<Application/Workload>": "application_workload",
    "<Purpose of using Block storage>": "purpose",
}
_PLACEHOLDER = re.compile(r"<[^<>]{1,60}>")
# Template Table-01 label (column 0, as it appears in the doc) -> AsBuiltData field. Match is
# whitespace-normalised + case-insensitive (the template mixes "InServ"/"Inserv").
_LABEL_TO_FIELD: dict[str, str] = {
    "name": "name",
    "model": "model",
    "serial no": "serial_no",
    "controller nodes": "controller_nodes",
    "os version": "os_version",
    "drive cages": "drive_cages",
    "cache(gb)": "cache_gb",
    "nvme ssd disks (15.36 tb)": "nvme_ssd_disks",
    "nvme ssd disks": "nvme_ssd_disks",
    "raw capacity": "raw_capacity",
    "raid": "raid",
    "host ports": "host_ports",
    "inserv ip address": "mgmt_ip",
    "inserv netmask address": "netmask",
    "inserv gateway address": "gateway",
    "ntp": "ntp",
    "dns servers": "dns",
}


def _resource_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", ".")) / "alletra_onboard" / "resources"
    return Path(__file__).resolve().parents[2] / "resources"  # …/src/alletra_onboard/resources


def default_template() -> Path | None:
    """The as-built template: an explicit env override, else the bundled template (prefer the filled
    ``.docx`` over a bare ``.dotx``), else a ``templates/`` drop-in, else None (plain document)."""
    env = os.environ.get("ALLETRA_ASBUILT_TEMPLATE")
    if env and Path(env).is_file():
        return Path(env)
    rd = _resource_dir()
    for name in ("asbuilt_template.docx", "asbuilt_template.dotx"):
        if (rd / name).is_file():
            return rd / name
    bases = [Path.cwd()]
    if getattr(sys, "argv", None) and sys.argv[0]:
        bases.append(Path(sys.argv[0]).resolve().parent)
    for base in bases:
        for name in ("asbuilt_template.docx", "asbuilt_template.dotx"):
            if (base / "templates" / name).is_file():
                return base / "templates" / name
    return None


def _norm(text: str) -> str:
    return " ".join(str(text).split()).strip().rstrip(":").strip()


def _load_document(template: str | Path | None):
    """Open a .docx/.dotx as a python-docx Document (patching a .dotx content-type in memory), or a
    blank document when no template is given."""
    if template is None:
        return docx.Document()
    template = Path(template)
    if template.suffix.lower() == ".dotx":
        with zipfile.ZipFile(template) as zin:
            ct = zin.read("[Content_Types].xml").decode("utf-8").replace(
                "wordprocessingml.template.main+xml", "wordprocessingml.document.main+xml")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.namelist():
                    zout.writestr(item, ct.encode("utf-8") if item == "[Content_Types].xml" else zin.read(item))
        buf.seek(0)
        return docx.Document(buf)
    return docx.Document(str(template))


def _text_parts(doc):
    """Every XML part whose text this document fills: the body AND each section's headers/footers.

    Word keeps running headers and footers in SEPARATE parts, so walking ``doc.element.body`` alone
    silently skips them — measured on HPE's template, the running header is
    ``"<Customer Name> HPE GreenLake for Block … Technical Whitepaper"`` and the footer carries
    ``<CustomerName>``, so every page after the cover shipped with a raw placeholder on it.

    Only parts this section actually OWNS are yielded: a header linked to the previous section has
    no definition of its own, and asking python-docx for one would create an empty part.
    """
    yield doc.element.body
    for section in doc.sections:
        for attr in ("first_page_header", "header", "even_page_header",
                     "first_page_footer", "footer", "even_page_footer"):
            try:
                part = getattr(section, attr)
                if part.is_linked_to_previous:
                    continue
                yield part._element
            except (AttributeError, KeyError, ValueError) as exc:
                _log.debug("docx_part_unreadable", error=str(exc))
                continue


def _placeholder_key(text: str) -> str:
    """``'<Customer Name>'``/``'<CustomerName>'``/``'<Customer name>'`` -> ``'customername'``.

    HPE's template spells one field FOUR ways across the cover, body, header and footer. Matching
    on the squeezed, lower-cased inner text makes the spelling irrelevant.
    """
    return re.sub(r"\s+", "", text.strip().strip("<>")).lower()


_FIELD_BY_KEY: dict[str, str] = {
    _placeholder_key(p): field for p, field in _PLACEHOLDER_TO_FIELD.items()
}


def _placeholder_value(data, match) -> str:
    field = _FIELD_BY_KEY.get(_placeholder_key(match.group(0)))
    if field:
        value = getattr(data, field, "")
        if value:
            return value
    return match.group(0)


def _replace_in_paragraph(para, value_for) -> bool:
    nodes = list(para.iter(qn("w:t")))
    if len(nodes) < 2:
        return False
    joined = "".join(n.text or "" for n in nodes)
    if "<" not in joined:
        return False
    if not any(_placeholder_key(m) in _FIELD_BY_KEY for m in _PLACEHOLDER.findall(joined)):
        return False
    replaced = _PLACEHOLDER.sub(value_for, joined)
    if replaced == joined:
        return False
    nodes[0].text = replaced
    for extra in nodes[1:]:
        extra.text = ""
    return True


def _fill_placeholders(doc, data) -> int:
    """Replace every known ``<placeholder>`` with its value, across the body and headers/footers.

    Two passes, because Word splits text into runs at arbitrary points (revision marks,
    spell-check), so a placeholder can be *fragmented* across runs and never match a per-run
    search. Pass 1 replaces within each run — fast, and preserves any per-run formatting. Pass 2
    only touches paragraphs whose JOINED text still holds a known placeholder: it rewrites the
    paragraph's text into its first run, which is the price of repairing a split placeholder.
    """
    filled = 0
    replace = partial(_placeholder_value, data)

    for part in _text_parts(doc):
        for node in part.iter(qn("w:t")):                      # pass 1: within a run
            if node.text and "<" in node.text:
                replaced = _PLACEHOLDER.sub(replace, node.text)
                if replaced != node.text:
                    node.text = replaced
                    filled += 1

        for para in part.iter(qn("w:p")):                      # pass 2: split across runs
            if _replace_in_paragraph(para, replace):
                filled += 1
    return filled


def _remaining_placeholders(doc) -> list[str]:
    """Every ``<...>`` still in the finished document — body, headers and footers — first seen first.

    Per-paragraph, not per-run: a placeholder fragmented across runs is still visible to the reader
    and must be reported, or the warning quietly under-counts what the customer will see.
    """
    found: list[str] = []
    for part in _text_parts(doc):
        for para in part.iter(qn("w:p")):
            joined = "".join(n.text or "" for n in para.iter(qn("w:t")))
            for match in _PLACEHOLDER.findall(joined):
                if match not in found:
                    found.append(match)
    return found


def _start_sections_on_new_pages(doc) -> int:
    """Begin every top-level section on a fresh page.

    The template carries exactly ONE explicit page break (before Executive Summary); every other
    Heading 1 flows inline, so once the generated inventory and health tables are injected the
    later headings land halfway down a page. ``page_break_before`` is the Word-native way to say
    this — it survives content reflow, unlike an inserted break paragraph that drifts as the tables
    above it grow. Headings that already carry an explicit break are left alone so no blank page
    appears, and each heading is kept with the content under it.
    """
    added = 0
    for para in doc.paragraphs:
        style = (para.style.name or "").lower() if para.style is not None else ""
        if not style.startswith("heading"):
            continue
        para.paragraph_format.keep_with_next = True          # never strand a heading at a page foot
        if style != "heading 1":
            continue
        if any(b.get(qn("w:type")) == "page" for b in para._p.iter(qn("w:br"))):
            continue                                          # the template already breaks here
        if para.paragraph_format.page_break_before:
            continue
        if para.text.strip() in _FLOWS_ON:
            continue                                          # SPEC-012 R3: flows on from the section above
        para.paragraph_format.page_break_before = True
        added += 1
    return added


def _drop_blank_paragraphs_after(heading) -> None:
    """Remove the run of empty paragraphs directly under a section heading.

    The template leaves ~23 blank paragraphs as space for the content we generate; without this the
    inserted tables are followed by a page of whitespace before the next heading.
    """
    node = heading._p.getnext()
    while node is not None and node.tag == qn("w:p"):
        following = node.getnext()
        if "".join(node.itertext()).strip():
            break
        node.getparent().remove(node)
        node = following


def _set_cell_text(cell, text: str) -> None:
    first = cell.paragraphs[0]
    for run in list(first.runs):
        run.element.getparent().remove(run.element)
    first.add_run(text or "-")
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)


def _insert_mono_after(heading, text: str):
    new_p = OxmlElement("w:p")
    heading._p.addnext(new_p)
    para = Paragraph(new_p, heading._parent)
    lines = (text or "").splitlines() or ["(no output captured)"]
    for i, line in enumerate(lines):
        run = para.add_run(line or " ")
        run.font.name = "Consolas"
        run.font.size = Pt(7)
        if i < len(lines) - 1:
            run.add_break()
    return new_p


def _place_after(anchor, element):
    """Move a python-docx Paragraph/Table's XML to right after ``anchor`` (an lxml element)."""
    xml = element._p if hasattr(element, "_p") else element._tbl
    anchor.addnext(xml)
    return xml


def _bold_para_after(anchor, caption: str, doc):
    para = doc.add_paragraph()
    para.add_run(caption).bold = True
    return _place_after(anchor, para)


def _add_inventory_after(heading, text: str, doc) -> None:
    """Render each ``showinventory`` sub-section as its own HPE-styled table under the heading; falls
    back to a monospace dump if nothing parsed."""
    sections = parse_inventory(text)
    if not sections:
        _insert_mono_after(heading, text)
        return
    anchor = heading._p
    for title, headers, rows in sections:
        if title:
            anchor = _bold_para_after(anchor, title, doc)
        tbl = hpe_table(doc, headers, rows, widths=content_widths(headers, rows), font_size=7, header_size=7)
        anchor = _place_after(anchor, tbl)


def _add_checkhealth_after(heading, text: str, doc) -> None:
    """Render checkhealth as two HPE-styled Word tables (Summary + Details); falls back to monospace."""
    summary, detail = parse_checkhealth(text)
    if not summary and not detail:
        _insert_mono_after(heading, text)
        return
    anchor = heading._p
    if summary:
        anchor = _bold_para_after(anchor, "Summary", doc)
        tbl = hpe_table(doc, ["Component", "Summary Description", "Qty"], summary,
                        widths=[0.20, 0.66, 0.14], font_size=8, header_size=8)
        anchor = _place_after(anchor, tbl)
    if detail:
        anchor = _bold_para_after(anchor, "Details", doc)
        tbl = hpe_table(doc, ["Component", "Identifier", "Detailed Description", "Resolution"], detail,
                        widths=[0.12, 0.28, 0.48, 0.12], font_size=8, header_size=8)
        anchor = _place_after(anchor, tbl)


def _fill_config_table(doc, data: AsBuiltData) -> None:
    values = {label: getattr(data, field) for label, field in _LABEL_TO_FIELD.items()}
    for table in doc.tables:
        for row in table.rows:
            key = _norm(row.cells[0].text).lower()
            if key in values and len(row.cells) > 1:
                _set_cell_text(row.cells[1], values[key])
                if key.startswith("nvme ssd disks ("):
                    # the template's label carries a sample drive size; the value states the real one
                    _set_cell_text(row.cells[0], "NVMe SSD Disks")


def _find_template_headings(doc) -> tuple[Paragraph | None, Paragraph | None]:
    inv_heading = ch_heading = None
    for para in doc.paragraphs:
        if not (para.style and para.style.name and para.style.name.lower().startswith("heading")):
            continue
        heading = _norm(para.text).lower()
        if "inventory" in heading:
            inv_heading = para
        elif "checkhealth" in heading:
            ch_heading = para
    return inv_heading, ch_heading


def generate_asbuilt(
    data: AsBuiltData, out_path: str | Path, *, template: str | Path | EllipsisType | None = ...,
) -> tuple[Path, list[str]]:
    """Fill the bundled template with ``data`` and write the finished as-built .docx to ``out_path``.

    Returns ``(path, warnings)``. The document is ALWAYS produced — an operator in the field would
    rather hand over a partial document than be blocked — but anything that did not fill is
    reported so it can be seen before the document is sent:

      * a section whose heading could not be found (its content would be missing entirely)
      * any ``<placeholder>`` still present in the finished text

    Section headings are matched by INTENT, not by exact string. HPE renamed "Alletra Inventory" to
    "HPE GreenLake for Block hardware Inventory" between template revisions; the old exact match
    silently produced an as-built with no inventory section at all.
    """
    if template is ...:
        template = default_template()
    doc = _load_document(template)
    warnings: list[str] = []

    _fill_placeholders(doc, data)
    _fill_config_table(doc, data)
    inv_heading, ch_heading = _find_template_headings(doc)

    if inv_heading is not None:
        _drop_blank_paragraphs_after(inv_heading)
        _add_inventory_after(inv_heading, data.inventory, doc)
    else:
        warnings.append(
            "No 'Inventory' heading was found in the template, so the hardware inventory is NOT in "
            "this document."
        )
    if ch_heading is not None:
        _drop_blank_paragraphs_after(ch_heading)
        _add_checkhealth_after(ch_heading, data.checkhealth, doc)
    else:
        warnings.append(
            "No 'checkhealth' heading was found in the template, so the health report is NOT in "
            "this document."
        )

    _add_handover_section(doc, data, warnings)
    _add_provisioned_sections(doc, data, warnings)
    _update_fields_on_open(doc)
    _start_sections_on_new_pages(doc)

    left = _remaining_placeholders(doc)
    if left:
        warnings.append(
            "Placeholders are still unfilled and will be visible to the customer: "
            + ", ".join(left) + ". Fill them in the workbook (or the As-built step) and regenerate, "
            "or edit the document before sending."
        )

    out_path = Path(out_path)
    doc.save(str(out_path))
    return out_path, warnings


# ------------------------------------------------------------------ SPEC-002: the provisioned array

_SYSTEM_VOLUME = re.compile(r"^(\.|admin$)")


def _members_of(sets: OrderedDict[str, list[str]]) -> dict[str, list[str]]:
    """member -> [set names] (a host or volume may sit in several sets)."""
    inverse: dict[str, list[str]] = {}
    for name, members in sets.items():
        for m in members:
            inverse.setdefault(m, []).append(name)
    return inverse


# ------------------------------------------------------------------ SPEC-026: status at handover

# 2026-11-19: performance removed from the as-built at the owner's request (the title lost "and performance").
HANDOVER_HEADING = "Array status at handover"

# Capacity lines of `showsys -space` (R5): label -> (section, path)
_SPACE_LINES = (
    ("Raw total", ("Raw Capacity", "Total")),
    ("Raw allocated", ("Raw Capacity", "Total", "Usable", "Allocated")),
    ("Raw free", ("Raw Capacity", "Total", "Usable", "Free")),
    ("Usable total", ("Usable Capacity", "Total")),
    ("Usable used", ("Usable Capacity", "Total", "Used")),
    ("Usable free", ("Usable Capacity", "Total", "Free")),
)
_YES_NO = {True: "Yes", False: "No", None: "unknown"}


def _add_handover_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-026 R4, R5, R8 and R9: what the array said about itself when the document was made. Every read
    that failed or could not be parsed is named in its subsection and in the warnings (R8), never shown as 0."""
    if (read_at := data.handover_read_at) is None:
        return                                      # the reads were not made: nothing to report
    reads = handover.read_from(data)
    for command, words in reads.errors.items():
        data.read_errors.setdefault(command, words)
    add_h1(doc, HANDOVER_HEADING)
    add_para(doc, "What the array reported about itself when this document was generated: its new alerts and its "
                  "capacity in use. Reading it changed nothing on the array.")
    _add_handover_alerts(doc, data, reads, warnings)
    _add_handover_capacity(doc, data, reads, warnings)
    clock_error = data.read_errors.get(handover.CLOCK)
    if clock_error is not None:
        add_para(doc, f"`{handover.CLOCK}` could not be read: {clock_error}")
        warnings.append(f"`{handover.CLOCK}` could not be read ({clock_error}); whether each alert came before "
                        "this run is unknown.")
    read_at = read_at.astimezone(UTC) if read_at.tzinfo else read_at
    line = f"This section was read from the array at {read_at:%Y-%m-%d %H:%M} UTC"
    if reads.offset is not None:
        local = read_at.replace(tzinfo=None) + reads.offset
        line += f" ({local:%Y-%m-%d %H:%M} on the array's clock, {handover.offset_text(reads.offset)})"
    add_para(doc, line + ".")
    add_para(doc, handover.cloud_line(reads.alerts))


def _add_handover_alerts(doc, data: AsBuiltData, reads, warnings: list[str]) -> None:
    add_para(doc, "Alerts", bold=True)
    if read_failed(doc, data.read_errors, handover.ALERTS, warnings):
        return
    alerts = reads.alerts
    add_para(doc, handover.alerts_verdict(alerts))
    if not alerts:
        return
    full, groups = handover.alert_table(alerts)
    offset = reads.offset
    if full:
        add_para(doc, "Major, Critical and Fatal alerts, newest first. Before this run: whether the alert first "
                      "occurred before this run was created.")
        add_table(doc, ["Id", "Severity", "Message code", "Message", "First occurred", "Latest", "Before this run"],
                  [[str(a.id), a.severity, a.message_code or "—", a.message, a.first_seen, a.time,
                    _YES_NO[handover.before_run(a, offset, reads.run_created_at)]] for a in full],
                  widths=[0.05, 0.09, 0.10, 0.36, 0.15, 0.15, 0.10])
        if offset is None:
            add_para(doc, "Before this run is unknown: the array's clock (showdate) could not be read, so its time "
                          "zone is not known.")
    if groups:
        add_para(doc, "The other new alerts, one row for each message code and severity.")
        add_table(doc, ["Severity", "Message code", "Alerts", "First occurred", "Latest", "Sample message"],
                  [[g.severity, g.message_code or "—", str(g.count), g.first_seen, g.latest, g.sample] for g in groups],
                  widths=[0.10, 0.11, 0.07, 0.16, 0.16, 0.40])
    add_para(doc, "The full list is on the array: showalert -d. Once the cause of an alert is dealt with, setalert or "
                  "removealert on the array acknowledges or removes it; the tool runs neither.")
    for a in full:
        warnings.append(f"The array has a new {a.severity} alert {a.id} (first occurred {a.first_seen}): "
                        f"{a.message.rstrip('.')}. Check whether it still applies before you send the document.")


def _add_handover_capacity(doc, data: AsBuiltData, reads, warnings: list[str]) -> None:
    add_para(doc, "Capacity", bold=True)
    if read_failed(doc, data.read_errors, handover.SPACE, warnings):
        return
    rows = []
    for label, (section, *path) in _SPACE_LINES:
        line = reads.space.get(section, *path)
        mib = reads.space.mib(section, *path)
        rows.append([label, "—" if mib is None else f"{handover.tib(mib):.1f}", line.text if line else "not printed"])
    add_para(doc, "From showsys -space: in TiB with one decimal, and the array's own figure in MiB beside it.")
    add_table(doc, ["Capacity", "TiB", "MiB, as the array prints it"], rows, widths=[0.40, 0.20, 0.40])
    if reads.space.reduction:
        add_para(doc, f"Data reduction: {reads.space.reduction} (the array's ratio).")


def _add_hosts_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    add_h1(doc, "Hosts and host sets")
    sets = OrderedDict() if data.read_errors.get("showhostset") else parse_cli_sets(data.showhostset)
    in_sets = _members_of(sets)
    if not read_failed(doc, data.read_errors, "showhost -d", warnings):
        hosts = parse_showhost(data.showhost_d)
        named = [h for h in hosts if h.name != UNCLAIMED_HOST]
        unclaimed = [h for h in hosts if h.name == UNCLAIMED_HOST]
        add_para(doc, "Every host object on the array, with the initiators it carries and the array ports "
                      "those initiators are logged in on. An initiator with no port is registered but not "
                      "logged in (not zoned, or the server is off).")
        if named:
            rows = []
            for h in named:
                initiators = list(h.wwpns) + list(h.iqns)
                ports = sorted({p for ps in list(h.wwpns.values()) + list(h.iqns.values()) for p in ps})
                rows.append([h.name, h.persona or "—", "\n".join(initiators) or "—",
                             ", ".join(ports) or "none", ", ".join(in_sets.get(h.name, [])) or "—"])
            add_table(doc, ["Host", "Persona", "Initiators", "Logged in on", "Host sets"], rows,
                      widths=[0.20, 0.12, 0.30, 0.20, 0.18])
        else:
            add_para(doc, "The array reports no host objects.")
        logins = [(i, ps, "") for u in unclaimed for i, ps in u.wwpns.items()]
        logins += [(i, ps, u.addresses.get(i, "")) for u in unclaimed for i, ps in u.iqns.items()]
        add_para(doc, "Logged in, no host object", bold=True)
        if logins:
            add_para(doc, "Initiators the array sees on its ports that belong to no host object — zoned or "
                          "connected, never provisioned.")
            add_table(doc, ["Initiator", "Logged in on", "Address"],
                      [[i, ", ".join(sorted(ps)) or "none", a or "—"] for i, ps, a in logins],
                      widths=[0.50, 0.30, 0.20])
        else:
            add_para(doc, "Every initiator logged in on the array belongs to a host object.")
    _add_sets_table(doc, data, warnings, "Host", sets)


def _add_sets_table(doc, data: AsBuiltData, warnings: list[str], kind: str, sets: OrderedDict[str, list[str]]) -> None:
    add_para(doc, f"{kind} sets", bold=True)
    cmd = "showhostset" if kind == "Host" else "showvvset"
    if not read_failed(doc, data.read_errors, cmd, warnings):
        if sets:
            add_table(doc, [f"{kind} set", "Members"], [[n, ", ".join(m) or "—"] for n, m in sets.items()],
                      widths=[0.35, 0.65])
        else:
            add_para(doc, f"The array reports no {kind.lower()} sets.")


def _gib(mib: str) -> str:
    try:
        return f"{int(mib) / 1024:g}"
    except ValueError:
        return "—"


_COMPR = {"no": "No", "na": "—", "": "—"}


def _compression(value: str) -> str:
    """`showvv` Compr: `No`, `NA` (system/dds volumes), or a version tag like `v2` = compressed."""
    return _COMPR.get(value.strip().lower(), f"Yes ({value})")


def _add_volumes_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    add_h1(doc, "Volumes and volume sets")
    sets = OrderedDict() if data.read_errors.get("showvvset") else parse_cli_sets(data.showvvset)
    in_sets = _members_of(sets)
    if not read_failed(doc, data.read_errors, "showvv", warnings):
        rows_all = parse_showvv(data.showvv)
        size_key = next((k for k in rows_all[0] if k.startswith("VSize")), "VSize(MiB)") if rows_all else "VSize(MiB)"
        cpg_by_name: dict[str, str] = {}
        cpg_cmd = next((c for c in data.read_errors if c.startswith("showvv -showcols")), None)
        if cpg_cmd:
            warnings.append(f"`{cpg_cmd}` could not be read ({data.read_errors[cpg_cmd]}); the CPG column reads —.")
        else:
            cpg_by_name = {
                r.get("Name", ""): (r.get("CPG") or r.get("UsrCPG") or "") for r in parse_showvv(data.showvv_cpg)
            }
        snapshots = [r for r in rows_all if r.get("Type") == "vcopy" or r.get("Prov") == "snp"]
        snap_count: dict[str, int] = {}
        for s in snapshots:
            snap_count[s.get("CopyOf", "")] = snap_count.get(s.get("CopyOf", ""), 0) + 1
        base = [r for r in rows_all if r not in snapshots]
        system = [r for r in base if _SYSTEM_VOLUME.match(r.get("Name", ""))]
        user = [r for r in base if r not in system]
        add_para(doc, "Every user volume on the array. Provisioning is the array's word: tpvv (thin), tdvv "
                      "(thin with data reduction), full, dds (dedup store).")
        if user:
            add_table(doc, ["Volume", "Provisioning", "Dedup", "Compression", "Size (GiB)", "CPG", "Snapshots", "VV set"],
                      [[r.get("Name", ""), r.get("Prov", "—"), r.get("Dedup", "—"), _compression(r.get("Compr", "")),
                        _gib(r.get(size_key, "")), cpg_by_name.get(r.get("Name", "")) or "—",
                        str(snap_count.get(r.get("Name", ""), 0)), ", ".join(in_sets.get(r.get("Name", ""), [])) or "—"]
                       for r in user],
                      widths=[0.26, 0.10, 0.08, 0.10, 0.10, 0.12, 0.10, 0.14])
        else:
            add_para(doc, "The array reports no user volumes.")
        add_para(doc, f"Not listed: {len(system)} system volume(s) and {len(snapshots)} snapshot(s).")
    _add_sets_table(doc, data, warnings, "Volume", sets)


def _add_presentations_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    add_h1(doc, "Presentations")
    if read_failed(doc, data.read_errors, "showvlun -t", warnings):
        return
    templates = parse_showvlun_templates_cli(data.showvlun_t)
    active_ok = not read_failed(doc, data.read_errors, "showvlun -a", warnings)
    active = parse_showvlun_active(data.showvlun_a) if active_ok else []
    add_para(doc, "What is presented to whom (the array's VLUN templates), and whether anyone can see it "
                  "right now (active paths).")
    if not templates:
        add_para(doc, "The array reports no presentations.")
        return
    rows = []
    for t in templates:
        paths = [p for p in active if p.lun == t.lun and p.volume == t.volume]
        target = f"host set {t.target[4:]}" if t.target.startswith("set:") else f"host {t.target}"
        if not active_ok:
            live = "unknown — showvlun -a could not be read"
        elif paths:
            live = f"{len(paths)} on {', '.join(sorted({p.host for p in paths}))}"
        else:
            live = "none — nobody can see this presentation"
        rows.append([str(t.lun), t.volume, target, live])
    add_table(doc, ["LUN", "Volume", "Presented to", "Active paths"], rows, widths=[0.08, 0.30, 0.30, 0.32])


_OUTCOME_LABEL = {"created": "Created", "updated": "Updated", "exists": "Already existed", "failed": "Failed"}
_VERDICT_LABEL = {"live": "Live", "partial": "Partial", "no_path": "No path"}


def _removal_lines(items: list[dict]) -> list[str]:
    """SPEC-007 R3 over JSON-shaped RemovalItems: dependency order, de-duplicated across applies."""
    out: list[str] = []
    for item in sorted(items, key=lambda i: REMOVAL_ORDER.get(i.get("kind", ""), 9)):
        cmd = item.get("command", "")
        if cmd and cmd not in out:
            out.append(cmd)
    return out


def _add_provisioning_section(doc, data: AsBuiltData) -> None:
    add_h1(doc, "Provisioning performed in this run")
    result = data.provisioning_result
    if not result:
        add_para(doc, "A plan was built but not applied." if data.provisioning_plan
                 else "This run did not include the provisioning step.")
        return
    when = f" at {format_when(data.provisioning_applied_at)}" if data.provisioning_applied_at else ""
    add_para(doc, f"Objects the tool created or found on the array{when}. 'Already existed' means the object "
                  "was there and matched; 'Updated' means members, WWNs or iSCSI names were added, nothing removed.")
    outcomes = result.get("outcomes", [])
    if outcomes:
        add_table(doc, ["Kind", "Name", "Result", "Detail"],
                  [[str(o.get("kind", "")), str(o.get("name", "")),
                    str(_OUTCOME_LABEL.get(o.get("status", ""), o.get("status", ""))),
                    str(o.get("detail") or "—")] for o in outcomes],
                  widths=[0.10, 0.30, 0.18, 0.42])
    if result.get("error"):
        add_para(doc, f"Provisioning stopped with an error: {result['error']}")
    add_para(doc, "To remove what this run created", bold=True)
    snapshot_items: list[dict] = []
    if data.snapshots_tab is not None:
        # SPEC-023 R6: the snapshot lines go first; removevv refuses a volume that still has snapshots
        snapshot_items = snapshot_removal_items(data)
    removal_lines = _removal_lines(snapshot_items + (data.provisioning_removals or result.get("removals") or []))
    if removal_lines:
        add_para(doc, "The undo for exactly the objects this run created, in dependency order ("
                      + ("snapshot schedules, snapshots, " if snapshot_items else "") + "exports, VV sets, "
                      "volumes, host sets, hosts). Objects that existed before the run are not listed. Review "
                      "before pasting; the tool never runs these.")
        add_mono(doc, removal_lines)
    else:
        add_para(doc, "Nothing — this run created no objects.")
    add_para(doc, "Path verification", bold=True)
    paths = data.path_verification
    if not paths:
        add_para(doc, "Path verification was not run.")
        return
    if paths.get("error"):
        add_para(doc, f"Path verification failed: {paths['error']}")
        return
    hosts = paths.get("hosts", [])
    if hosts:
        # SPEC-013 R5: the array's view and the ESXi host's view side by side.
        add_table(doc, ["Host", "Verdict", "Array view", "ESXi view"],
                  [[str(h.get("host", "")), str(_VERDICT_LABEL.get(h.get("verdict", ""), h.get("verdict", ""))),
                    str(h.get("detail", "")), str(h.get("esxi_note") or "not read")]
                   for h in hosts],
                  widths=[0.20, 0.12, 0.38, 0.30])
    else:
        add_para(doc, "No target hosts to verify.")


def _add_provisioned_sections(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-002: the five sections appended after the template's last section; SPEC-024 and SPEC-025
    add the iSCSI network and Peer ports sections when the sheet or the array has them; SPEC-028 adds
    the file service when the array has one; SPEC-018 adds two more when the run's workbook has a
    Replication tab."""
    _add_hosts_section(doc, data, warnings)
    _add_volumes_section(doc, data, warnings)
    _add_presentations_section(doc, data, warnings)
    add_iscsi_network_section(doc, data, warnings)
    add_peer_ports_section(doc, data, warnings)
    add_zoning_section(doc, data)
    _add_provisioning_section(doc, data)
    _add_file_section(doc, data, warnings)
    if data.replication_tab is not None:
        add_replication_section(doc, data, warnings)
        _add_failover_section(doc, data)
    if data.snapshots_tab is not None:
        add_snapshots_section(doc, data, warnings)
    if data.trusted_devices:
        _add_device_fingerprints(doc, data)
    if data.commands:
        _add_commands_appendix(doc, data)


_DEVICE_LABEL = {"array": "Array", "switch": "SAN switch", "Linux host": "Linux host", "vCenter": "vCenter"}


def _add_device_fingerprints(doc, data: AsBuiltData) -> None:
    """ADR 0026: the key each on-site device presented, so the customer can compare it with the device."""
    add_h1(doc, "Device fingerprints")
    add_para(doc, "The tool trusted each device below the first time this run connected to it, and checked the "
                  "same key on every later connection. Compare each fingerprint with the one the device's own "
                  "console shows.")
    rows = []
    for d in data.trusted_devices:
        port = d.get("port")
        address = d.get("host", "") if port in (22, 443) else f"{d.get('host', '')}:{port}"
        key = f"SSH host key ({d.get('key_type', '')})" if d.get("kind") == "ssh" else "TLS certificate"
        how = "Again, by the operator" if d.get("how") == "retrusted" else "First contact"
        trusted = f"{how}, {format_when(str(d.get('trusted_at') or ''))}"
        if d.get("refused_fingerprint"):
            trusted += (f". Later presented {d['refused_fingerprint']}, which was refused "
                        f"({format_when(str(d.get('refused_at') or ''))})")
        rows.append([_DEVICE_LABEL.get(d.get("device", ""), d.get("device", "")), address, key,
                     d.get("fingerprint", ""), trusted])
    add_table(doc, ["Device", "Address", "Key", "SHA-256 fingerprint", "Trusted"], rows)


# ------------------------------------------------------------------ SPEC-028 R3: the file service

def _size(mib: int) -> str:
    """The file side counts in MiB."""
    if mib >= 1024 * 1024:
        return f"{mib / (1024 * 1024):.1f} TiB"
    return f"{mib / 1024:.1f} GiB".replace(".0 GiB", " GiB")


def _state(state: str) -> str:
    """'STATE_NORMAL' -> 'normal'."""
    return state.removeprefix("STATE_").replace("_", " ").lower()


def _add_file_service_summary(doc, report, warnings: list[str]) -> None:
    for note in report.notes:
        add_para(doc, note)
    service = report.service
    if service is None:
        reason = report.notes[0] if report.notes else "the file service was not read"
        warnings.append(f"The File service section lists only the File ports: {reason}")
        return
    running = sum(1 for n in service.nodes if n.status == NODE_RUNNING)
    line = (f"File service: on, running on {running} of {len(service.nodes)} nodes."
            if service.enabled else "File service: off.")
    cap = service.capacity
    if cap is not None:
        line += (f" Capacity for file: {_size(cap.total)}, {_size(cap.used)} used, "
                 f"{_size(cap.available)} available.")
    add_para(doc, line)


def _add_file_systems(doc, report) -> None:
    add_para(doc, "File systems", bold=True)
    if report.file_systems:
        add_table(doc, ["File system", "Size", "Data reduction", "Shares", "Owner node", "State"],
                  [[fs.name, _size(fs.size_mib), "Yes" if fs.reduce else "No", str(fs.share_count),
                    str(fs.owner_node), _state(fs.state)] for fs in report.file_systems])
    else:
        add_para(doc, "The array has no file systems.")


def _add_file_shares(doc, report) -> None:
    add_para(doc, "Shares", bold=True)
    if report.shares:
        rows = []
        for share in report.shares:
            clients = report.clients_of(share)
            rows.append([
                share.name, share.file_system, share.client_group,
                "\n".join(" ".join(x for x in (c.address, c.access, c.options) if x) for c in clients) or "—",
                f"{share.host_ip}:{share.mount_path}" if share.host_ip else share.mount_path,
                ", ".join(share.protocols) or "—", _state(share.state),
            ])
        add_table(doc, ["Share", "File system", "Client group", "Clients", "Mount", "Protocol", "State"], rows)
        add_para(doc, "A share's clients are its client group's. A client of * is any host that can reach "
                      "the File ports.")
    else:
        add_para(doc, "The array has no shares.")


def _add_file_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-028 R3: the file service, its File ports, file systems and shares with their clients, as
    the array reports them when the document is made. Absent on an array with no File ports and the
    file service off; nothing here was changed by the run."""
    if data.file_read_error:
        add_h1(doc, "File service")
        add_para(doc, f"The file side could not be read: {data.file_read_error}")
        warnings.append(f"The file side could not be read ({data.file_read_error}); the File service "
                        "section is empty.")
        return
    report = data.file_report
    if report is None:
        return
    add_h1(doc, "File service")
    add_para(doc, "The array's NFS file service, its File ports, file systems and shares, as read from the "
                  "array when this document was made. This run changed nothing on the file side.")
    _add_file_service_summary(doc, report, warnings)

    add_para(doc, "File ports", bold=True)
    if data.file_ports:
        add_table(doc, ["Port", "Address", "Gateway", "VLAN", "MTU", "Link"],
                  [[p.label, f"{p.address}/{p.prefix_len}" if p.address else "—", p.gateway or "—",
                    p.vlan or "—", p.mtu or "—", f"{p.link} ({p.link_state})" if p.link else p.link_state or "—"]
                   for p in data.file_ports])
    else:
        add_para(doc, "The array has no File ports.")
    if report.service is None:
        return
    _add_file_systems(doc, report)
    _add_file_shares(doc, report)


_TRANSPORT_LABEL = {
    "ssh": "CLI (SSH)", "wsapi": "WSAPI", "fos": "switch (SSH)", "vcenter": "vCenter",
    "host-ssh": "Linux host (SSH)", "winrm": "Windows host (WinRM)", "greenlake": "GreenLake API",
}


def _add_commands_appendix(doc, data: AsBuiltData) -> None:
    """SPEC-019 R2: what touched the arrays in this run, and the switches, vCenter, hosts and GreenLake
    the run reached. Changes one by one; reads counted, not shown."""
    add_h1(doc, "Commands run on the array")
    writes = [c for c in data.commands if c.get("write")]
    reads = [c for c in data.commands if not c.get("write")]
    add_para(doc, f"The tool recorded every command it sent for this run as it ran, to the array and to any "
                  f"switch, vCenter, host or GreenLake service it reached: {len(writes)} change(s) and "
                  f"{len(reads)} read-only command(s). The full output of each is in the run's command log "
                  "(the app's console, Download .txt).")
    if writes:
        add_para(doc, "Changes", bold=True)
        add_table(doc, ["Time", "Device", "Via", "Call", "Result"],
                  [[format_when(c.get("at", "")), str(c.get("target", "")),
                    str(_TRANSPORT_LABEL.get(c.get("transport", ""), c.get("transport", ""))),
                    str(c.get("command", ""))[:160], str(c.get("result", ""))[:120]] for c in writes])
    else:
        add_para(doc, "No change was made to any array by this run.")
    counted: OrderedDict[tuple[str, str, str], int] = OrderedDict()
    for c in reads:
        key = (c.get("target", ""), c.get("transport", ""), c.get("command", "")[:120])
        counted[key] = counted.get(key, 0) + 1
    if counted:
        add_para(doc, "Read-only commands", bold=True)
        add_table(doc, ["Device", "Via", "Command", "Times"],
                  [[t, _TRANSPORT_LABEL.get(v, v), cmd, str(n)] for (t, v, cmd), n in counted.items()])


_FAILOVER_RESULT = {"passed": "Passed", "failed": "Failed", "aborted": "Not started"}
_FAILOVER_OUTCOME = {"ok": "OK", "failed": "Failed", "skipped": "Skipped", "pending": "—"}


def _side_text(side: dict | None) -> str:
    if not side:
        return "—"
    if not side.get("present", True):
        return "not on the array"
    bits = [f"{side.get('role', '')}/{side.get('status', '')}", f"{side.get('synced', 0)}/{side.get('volumes', 0)} Synced"]
    last = side.get("last_sync")
    if last and last != "NA":
        bits.append(f"last sync {last}")
    return " · ".join(bits)


def _add_failover_timing(doc, rec: dict) -> None:
    bits = []
    if rec.get("time_to_failover_s") is not None:
        bits.append(f"the peer took over (Primary-Rev) {rec['time_to_failover_s']:g} s after the failover was issued")
    if rec.get("time_to_synced_s") is not None:
        bits.append(f"every volume was Synced again {rec['time_to_synced_s']:g} s after the recover")
    if bits:
        add_para(doc, "Measured: " + "; ".join(bits) + ".")


def _failover_step_rows(rec: dict) -> list[list[str]]:
    rows = []
    for s in rec.get("steps", []):
        when = format_when(s.get("started_at", "")) if s.get("started_at") else "—"
        secs = f"{s['seconds']:g} s" if s.get("seconds") is not None else "—"
        rows.append([
            str(s.get("seq", "")), s.get("title", ""), s.get("where", "-"), s.get("cli") or s.get("action") or "—",
            when, secs, _side_text(s.get("primary")), _side_text(s.get("peer")),
            _FAILOVER_OUTCOME.get(s.get("outcome", ""), s.get("outcome", "")),
        ])
    return rows


def _add_failover_outcome(doc, result: str, rec: dict) -> None:
    if result == "passed":
        add_para(doc, "The group ended the test in its starting state: Primary and Started on this array, Secondary and Started "
                      "on the peer, every volume Synced.")
        return
    if rec.get("error"):
        add_para(doc, f"Stopped: {rec['error']}")
    if rec.get("observed_state"):
        add_para(doc, f"Observed when it stopped: {rec['observed_state']}")
    if rec.get("recovery_action"):
        add_para(doc, "The documented way back to the normal state (not run by the tool):", bold=True)
        add_mono(doc, [rec["recovery_action"]])


def _add_failover_section(doc, data: AsBuiltData) -> None:
    add_h1(doc, "Failover test")
    rec = data.failover_record
    if not rec:
        add_para(doc, "The failover test was not run in this run.")
        return
    result = str(rec.get("result", ""))
    label = _FAILOVER_RESULT.get(result, result)
    if result == "failed" and rec.get("failed_step") is not None:
        label += f" at step {rec['failed_step']}"
    mode = rec.get("mode") or "—"
    add_para(doc, f"Result: {label}.", bold=True)
    add_para(doc, f"Group {rec.get('group', '')} ({mode}) on {rec.get('primary_array', 'this array')} (P), named "
                  f"{rec.get('peer_group') or '—'} on {rec.get('peer_array', 'the peer')} (S). Started {format_when(rec.get('started_at', ''))}, "
                  f"ended {format_when(rec.get('ended_at', ''))}. Each role change is the array's own disaster-recovery action over WSAPI; "
                  "both arrays were read after every step.")
    _add_failover_timing(doc, rec)
    if mode == "async":
        add_para(doc, "Data-loss bound (async): " + (rec.get("data_loss_bound") or "not recorded") + ". Writes after that sync and "
                      "before the failover would not have reached the peer.")
    rows = _failover_step_rows(rec)
    if rows:
        add_table(doc, ["#", "Step", "On", "Command (CLI equivalent)", "Started", "Took", "P after", "S after", "Outcome"], rows,
                  widths=[0.03, 0.14, 0.04, 0.22, 0.11, 0.06, 0.16, 0.16, 0.08])
    _add_failover_outcome(doc, result, rec)


# SPEC-012 R3 (A-4): the two run sections share a page — a one-sentence zoning record owned a whole
# page when every Heading 1 broke. The second run section flows on from the first. SPEC-018: the
# failover section (one sentence until SPEC-017) flows on from the replication section.
_FLOWS_ON = {"Provisioning performed in this run", "Failover test"}


def _update_fields_on_open(doc) -> None:
    """R9: ask Word to refresh fields (the TOC, page numbers) when the document is opened."""
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        el = OxmlElement("w:updateFields")
        el.set(qn("w:val"), "true")
        settings.append(el)
