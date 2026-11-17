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
import ipaddress
import os
import re
import sys
import zipfile
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from alletra_onboard.application.documents.asbuilt_docx import hpe_table
from alletra_onboard.domain.provisioning import REMOVAL_ORDER

# Template Table-01 label (column 0, as it appears in the doc) -> AsBuiltData field. Match is
# whitespace-normalised + case-insensitive (the template mixes "InServ"/"Inserv").
#: Narrative placeholders in the template -> the AsBuiltData field that fills them. Matched
#: case-insensitively; HPE's own template varies the capitalisation of the same field.
_PLACEHOLDER_TO_FIELD: dict[str, str] = {
    "<Customer Name>": "customer",
    "<Site Location>": "site",
    "<Application/Workload>": "application_workload",
    "<Purpose of using Block storage>": "purpose",
}
_PLACEHOLDER = re.compile(r"<[^<>]{1,60}>")

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


@dataclass
class AsBuiltData:
    """The per-deployment values that fill the as-built (from read-only array reads + operator input)."""

    customer: str = ""       # operator-supplied — fills <Customer Name> / <Customer name>
    site: str = ""           # operator-supplied — the array doesn't store a Location/Site
    application_workload: str = ""   # operator-supplied — <Application/Workload> (Introduction)
    purpose: str = ""                # operator-supplied — <Purpose of using Block storage>
    name: str = ""
    model: str = ""
    serial_no: str = ""
    controller_nodes: str = ""
    os_version: str = ""
    drive_cages: str = ""
    cache_gb: str = ""
    nvme_ssd_disks: str = ""
    raw_capacity: str = ""
    raid: str = ""
    host_ports: str = ""
    mgmt_ip: str = ""
    netmask: str = ""
    gateway: str = ""
    ntp: str = ""
    dns: str = ""
    inventory: str = ""      # showinventory, verbatim
    checkhealth: str = ""    # checkhealth -svc -detail, verbatim
    # SPEC-002 array sections — raw `show*` text, parsed by the renderer like inventory/checkhealth.
    showhost_d: str = ""
    showhostset: str = ""
    showvv: str = ""
    showvv_cpg: str = ""     # showvv -showcols …UsrCPG… (R7); "" when that read failed
    showvvset: str = ""
    showvlun_t: str = ""
    showvlun_a: str = ""
    showport: str = ""               # read for Table 01; SPEC-024 R7 and SPEC-026 R6 take each port's state from it
    showport_iscsivlans: str = ""    # SPEC-024 R7: the VLAN-tagged iSCSI addresses
    showport_par: str = ""           # SPEC-025 R9: each port's connection mode and type
    showport_peer: str = ""          # SPEC-025 R9: the array's own listing of its peer ports
    read_errors: dict[str, str] = field(default_factory=dict)   # command -> error text (R6)
    # SPEC-002 run sections — the run's event payloads (JSON-shaped); None when the step did not run.
    zoning_plan: dict | None = None
    zoning_report: dict | None = None
    zoning_rendered: dict | None = None      # {commands: {fabric: [..]}, aliases, selected_pairs}
    provisioning_plan: dict | None = None
    provisioning_result: dict | None = None
    provisioning_applied_at: str = ""
    provisioning_removals: list[dict] = field(default_factory=list)   # RemovalItem dicts from EVERY apply in the run (SPEC-007)
    path_verification: dict | None = None
    # SPEC-018: replication. All None/empty when the workbook has no Replication tab (R4).
    replication_tab: dict | None = None            # {peer_host, rows: [{vvset, mode, rpo_minutes, peer_cpg}], failover_test}
    replication_report: dict | None = None         # replication.previewed -> report (JSON)
    replication_plan: dict | None = None           # replication.previewed -> plan (JSON)
    replication_result: dict | None = None         # replication.applied / .apply.failed -> result (JSON)
    # SPEC-021: every apply's removal lines, newest apply first (its groups go before the partnership a
    # first apply set up: removercopytarget refuses while a group still uses the target)
    replication_removals_a: list[str] = field(default_factory=list)
    replication_removals_b: list[str] = field(default_factory=list)
    # SPEC-021: every apply in run order, each with the plan previewed before it: {"plan", "result"}
    replication_applies: list[dict] = field(default_factory=list)
    replication_applied_at: str = ""
    replication_primary: object | None = None      # ReplicationArrayView read when the document is made (R3)
    replication_peer: object | None = None         # ReplicationArrayView of the peer, same moment
    link_check: dict | None = None                 # SPEC-020 R6: replication.link_checked -> link_check (JSON)
    failover_record: dict | None = None            # SPEC-017 R6; None = the test did not run
    # SPEC-028 R3: the file side, read when the document is made. No section when `file_report` is
    # None (no File ports and the service off) and the read did not fail.
    file_ports: list = field(default_factory=list)  # EthernetPort, from showport -file
    file_report: object | None = None               # FileReport
    file_read_error: str = ""                       # the read failed: named in the section and the warnings
    # SPEC-023 R8: snapshots. snapshots_tab is None when the workbook has no Snapshots tab.
    snapshots_tab: list[dict] | None = None        # SnapshotRequest dicts, one per row
    snapshots_plan: dict | None = None             # snapshots.previewed -> plan (JSON)
    snapshots_result: dict | None = None           # the latest snapshots.applied / .apply.failed -> result
    snapshots_applies: list[dict] = field(default_factory=list)   # every apply in run order: {"plan", "result"}
    snapshots_applied_at: str = ""
    snapshots_view: object | None = None           # SnapshotArrayView read when the document is made
    commands: list[dict] = field(default_factory=list)   # SPEC-019 R2: the run's command log, without output
    # SPEC-026: the handover reads, raw (handover.READS names the command for each); a failed one is in
    # read_errors. handover_read_at is None when the reads were not made: the section is then left out.
    # (`showport`, which R6 takes each port's state from, is the field above, read for Table 01.)
    showalert_d: str = ""
    showsys_space: str = ""
    srstatcpu: str = ""
    srstatport: str = ""
    srstatvv: str = ""
    handover_read_at: datetime | None = None
    run_created_at: datetime | None = None         # R4: "Before this run" compares each alert with it
    trusted_devices: list[dict] = field(default_factory=list)   # ADR 0026: DevicePinInfo dicts, fingerprints only
    # SPEC-024 R7: the sheet's iSCSI network rows (IscsiVlanRequest dicts), and the (port, VLAN) pairs a
    # plan of this run had to add, so an interface found now is marked "set up by this run".
    iscsi_network_rows: list[dict] = field(default_factory=list)
    iscsi_set_up_in_run: list[tuple[str, int]] = field(default_factory=list)
    # SPEC-025 R9: the Peer ports tab's rows (PeerPortRequest dicts), the run's last plan that set ports
    # (its commands, pasted by a consultant in the first slice) and the last read after the paste.
    peer_ports_rows: list[dict] = field(default_factory=list)
    peer_ports_plan: dict | None = None
    peer_ports_result: dict | None = None


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
        zin = zipfile.ZipFile(template)
        ct = zin.read("[Content_Types].xml").decode("utf-8").replace(
            "wordprocessingml.template.main+xml", "wordprocessingml.document.main+xml")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                zout.writestr(item, ct.encode("utf-8") if item == "[Content_Types].xml" else zin.read(item))
        zin.close()
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
        for part in (
            section.first_page_header, section.header, section.even_page_header,
            section.first_page_footer, section.footer, section.even_page_footer,
        ):
            try:
                if part.is_linked_to_previous:
                    continue
                yield part._element
            except Exception:  # noqa: BLE001 - a malformed part must not stop the fill
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


def _fill_placeholders(doc, data) -> int:
    """Replace every known ``<placeholder>`` with its value, across the body and headers/footers.

    Two passes, because Word splits text into runs at arbitrary points (revision marks,
    spell-check), so a placeholder can be *fragmented* across runs and never match a per-run
    search. Pass 1 replaces within each run — fast, and preserves any per-run formatting. Pass 2
    only touches paragraphs whose JOINED text still holds a known placeholder: it rewrites the
    paragraph's text into its first run, which is the price of repairing a split placeholder.
    """
    filled = 0

    def _value_for(match) -> str:
        field = _FIELD_BY_KEY.get(_placeholder_key(match.group(0)))
        if field:
            value = getattr(data, field, "")
            if value:
                return value
        return match.group(0)

    for part in _text_parts(doc):
        for node in part.iter(qn("w:t")):                      # pass 1: within a run
            if node.text and "<" in node.text:
                replaced = _PLACEHOLDER.sub(_value_for, node.text)
                if replaced != node.text:
                    node.text = replaced
                    filled += 1

        for para in part.iter(qn("w:p")):                      # pass 2: split across runs
            nodes = list(para.iter(qn("w:t")))
            if len(nodes) < 2:
                continue
            joined = "".join(n.text or "" for n in nodes)
            if "<" not in joined:
                continue
            if not any(_placeholder_key(m) in _FIELD_BY_KEY for m in _PLACEHOLDER.findall(joined)):
                continue
            replaced = _PLACEHOLDER.sub(_value_for, joined)
            if replaced == joined:
                continue
            nodes[0].text = replaced
            for extra in nodes[1:]:
                extra.text = ""
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
        run._element.getparent().remove(run._element)
    first.add_run(text or "-")
    for extra in cell.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)


def _insert_mono_after(heading, text: str):
    new_p = OxmlElement("w:p")
    heading._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
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


def _content_widths(headers: list[str], rows) -> list[float]:
    """Column-width fractions proportional to the widest cell in each column (min 4% each)."""
    n = len(headers)
    widest = [max([len(headers[i])] + [len(r[i]) for r in rows if i < len(r)]) for i in range(n)]
    total = sum(widest) or n
    return [max(0.04, w / total) for w in widest]


def _bold_para_after(anchor, caption: str, doc):
    para = doc.add_paragraph()
    para.add_run(caption).bold = True
    return _place_after(anchor, para)


def _add_inventory_after(heading, text: str, doc) -> None:
    """Render each ``showinventory`` sub-section as its own HPE-styled table under the heading; falls
    back to a monospace dump if nothing parsed."""
    from alletra_onboard.application.documents.asbuilt_parse import (
        parse_inventory,  # local: avoid import cycle
    )

    sections = parse_inventory(text)
    if not sections:
        _insert_mono_after(heading, text)
        return
    anchor = heading._p
    for title, headers, rows in sections:
        if title:
            anchor = _bold_para_after(anchor, title, doc)
        tbl = hpe_table(doc, headers, rows, widths=_content_widths(headers, rows), font_size=7, header_size=7)
        anchor = _place_after(anchor, tbl)


def _add_checkhealth_after(heading, text: str, doc) -> None:
    """Render checkhealth as two HPE-styled Word tables (Summary + Details); falls back to monospace."""
    from alletra_onboard.application.documents.asbuilt_parse import (
        parse_checkhealth,  # local: avoid import cycle
    )

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


def generate_asbuilt(
    data: AsBuiltData, out_path: str | Path, *, template: str | Path | None = ...,
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

    values = {label: getattr(data, field) for label, field in _LABEL_TO_FIELD.items()}
    for table in doc.tables:
        for row in table.rows:
            key = _norm(row.cells[0].text).lower()
            if key in values and len(row.cells) > 1:
                _set_cell_text(row.cells[1], values[key])
                if key.startswith("nvme ssd disks ("):
                    # the template's label carries a sample drive size; the value states the real one
                    _set_cell_text(row.cells[0], "NVMe SSD Disks")

    inv_heading = ch_heading = None
    for para in doc.paragraphs:
        if not para.style.name.lower().startswith("heading"):
            continue
        heading = _norm(para.text).lower()
        if "inventory" in heading:
            inv_heading = para
        elif "checkhealth" in heading:
            ch_heading = para

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


def _h1(doc, title: str):
    return doc.add_paragraph(title, style="Heading 1")


def _para(doc, text: str, *, bold: bool = False):
    p = doc.add_paragraph()
    p.add_run(text).bold = bold
    return p


def _mono(doc, lines: list[str]):
    p = doc.add_paragraph()
    for i, line in enumerate(lines):
        run = p.add_run(line or " ")
        run.font.name = "Consolas"
        run.font.size = Pt(7)
        if i < len(lines) - 1:
            run.add_break()
    return p


def _table(doc, headers: list[str], rows: list[list[str]], widths=None):
    hpe_table(doc, headers, rows, widths=widths or _content_widths(headers, rows), font_size=7, header_size=7)


def _read_failed(doc, data: AsBuiltData, command: str, warnings: list[str]) -> bool:
    """R6: a failed read is named in the section AND in the warnings; returns True when it failed."""
    err = data.read_errors.get(command)
    if err is None:
        return False
    _para(doc, f"`{command}` could not be read: {err}")
    warnings.append(f"`{command}` could not be read ({err}); its section of the as-built is empty.")
    return True


def _members_of(sets: OrderedDict[str, list[str]]) -> dict[str, list[str]]:
    """member -> [set names] (a host or volume may sit in several sets)."""
    inverse: dict[str, list[str]] = {}
    for name, members in sets.items():
        for m in members:
            inverse.setdefault(m, []).append(name)
    return inverse


# ------------------------------------------------------------------ SPEC-026: status and performance at handover

HANDOVER_HEADING = "Array status and performance at handover"

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


def _figure(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _three(stats: dict, attr: str, *, scale: float = 1.0, digits: int = 1) -> str:
    """'average / 95th percentile / maximum' of one figure; '—' where the array printed none."""
    values = []
    for stat in ("avg", "95%", "max"):
        value = getattr(stats[stat], attr) if stat in stats else None
        values.append(_figure(None if value is None else value / scale, digits))
    return " / ".join(values)


def _io_cells(stats: dict) -> list[str]:
    return [_three(stats, "iops"), _three(stats, "kbytes_s", scale=1024), _three(stats, "svct_ms", digits=2)]


def _add_handover_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-026 R4 to R9: what the array said about itself when the document was made. Every read that
    failed or could not be parsed is named in its subsection and in the warnings (R8), never shown as 0."""
    from alletra_onboard.application.documents import handover

    if data.handover_read_at is None:
        return                                      # the reads were not made: nothing to report
    reads = handover.read_from(data)
    for command, words in reads.errors.items():
        data.read_errors.setdefault(command, words)
    _h1(doc, HANDOVER_HEADING)
    _para(doc, "What the array reported about itself when this document was generated: its new alerts, its "
               "capacity in use and 24 hours of performance from its own System Reporter. Reading it changed "
               "nothing on the array.")
    _add_handover_alerts(doc, data, reads, warnings)
    _add_handover_capacity(doc, data, reads, warnings)
    _add_handover_performance(doc, data, reads, warnings)
    read_at = reads.read_at.astimezone(UTC) if reads.read_at.tzinfo else reads.read_at
    line = f"This section was read from the array at {read_at:%Y-%m-%d %H:%M} UTC"
    if reads.offset is not None:
        local = read_at.replace(tzinfo=None) + reads.offset
        line += f" ({local:%Y-%m-%d %H:%M} on the array's clock, {handover.offset_text(reads.offset)})"
    _para(doc, line + ".")
    _para(doc, handover.cloud_line(reads.alerts))


def _add_handover_alerts(doc, data: AsBuiltData, reads, warnings: list[str]) -> None:
    from alletra_onboard.application.documents import handover

    _para(doc, "Alerts", bold=True)
    if _read_failed(doc, data, handover.ALERTS, warnings):
        return
    alerts = reads.alerts
    _para(doc, handover.alerts_verdict(alerts))
    if not alerts:
        return
    full, groups = handover.alert_table(alerts)
    offset = reads.offset
    if full:
        _para(doc, "Major, Critical and Fatal alerts, newest first. Before this run: whether the alert first "
                   "occurred before this run was created.")
        _table(doc, ["Id", "Severity", "Message code", "Message", "First occurred", "Latest", "Before this run"],
               [[str(a.id), a.severity, a.message_code or "—", a.message, a.first_seen, a.time,
                 _YES_NO[handover.before_run(a, offset, reads.run_created_at)]] for a in full],
               widths=[0.05, 0.09, 0.10, 0.36, 0.15, 0.15, 0.10])
        if offset is None:
            _para(doc, "Before this run is unknown: no System Reporter report was read, so the array's time zone "
                       "is not known.")
    if groups:
        _para(doc, "The other new alerts, one row for each message code and severity.")
        _table(doc, ["Severity", "Message code", "Alerts", "First occurred", "Latest", "Sample message"],
               [[g.severity, g.message_code or "—", str(g.count), g.first_seen, g.latest, g.sample] for g in groups],
               widths=[0.10, 0.11, 0.07, 0.16, 0.16, 0.40])
    _para(doc, "The full list is on the array: showalert -d. Once the cause of an alert is dealt with, setalert or "
               "removealert on the array acknowledges or removes it; the tool runs neither.")
    for a in full:
        warnings.append(f"The array has a new {a.severity} alert {a.id} (first occurred {a.first_seen}): "
                        f"{a.message.rstrip('.')}. Check whether it still applies before you send the document.")


def _add_handover_capacity(doc, data: AsBuiltData, reads, warnings: list[str]) -> None:
    from alletra_onboard.application.documents import handover

    _para(doc, "Capacity", bold=True)
    if _read_failed(doc, data, handover.SPACE, warnings):
        return
    rows = []
    for label, (section, *path) in _SPACE_LINES:
        line = reads.space.get(section, *path)
        mib = reads.space.mib(section, *path)
        rows.append([label, "—" if mib is None else f"{handover.tib(mib):.1f}", line.text if line else "not printed"])
    _para(doc, "From showsys -space: in TiB with one decimal, and the array's own figure in MiB beside it.")
    _table(doc, ["Capacity", "TiB", "MiB, as the array prints it"], rows, widths=[0.40, 0.20, 0.40])
    if reads.space.reduction:
        _para(doc, f"Data reduction: {reads.space.reduction} (the array's ratio).")


def _add_handover_performance(doc, data: AsBuiltData, reads, warnings: list[str]) -> None:
    from alletra_onboard.application.documents import handover

    _para(doc, "Performance", bold=True)
    window = reads.window
    if window is not None:
        end = window.end_text if window.end is not None else "the read (System Reporter had no sample in it)"
        _para(doc, f"From the array's System Reporter, the 24 hours before the read: from {window.start_text} to "
                   f"{end}, in 5-minute samples. Each cell is the average / the 95th percentile / the maximum.")
        _para(doc, handover.PERFORMANCE_NOTE)
        if reads.idle:
            _para(doc, handover.IDLE_NOTE)

    _para(doc, "Controller nodes", bold=True)
    if not _read_failed(doc, data, handover.CPU, warnings):
        if reads.cpu_nodes:
            _para(doc, "CPU busy is 100 % minus the array's idle figure; the busiest sample comes from its lowest idle.")
            _table(doc, ["Node", "Average % busy", "95th percentile % busy", "Busiest sample % busy"],
                   [[n.node, _figure(n.busy_avg), _figure(n.busy_p95), _figure(n.busy_max)] for n in reads.cpu_nodes],
                   widths=[0.16, 0.28, 0.28, 0.28])
        else:
            _para(doc, "System Reporter printed no CPU figure for this window.")

    _para(doc, "Host ports", bold=True)
    if not _read_failed(doc, data, handover.PORTS, warnings):
        rows, lines = handover.split_ports(reads.port_loads, reads.roles)
        if rows:
            _table(doc, ["Port", "Protocol", "IO/s", "MB/s", "Service time (ms)"],
                   [[r.load.name, r.protocol or "—", *_io_cells(r.load.stats)] for r in rows],
                   widths=[0.10, 0.12, 0.24, 0.24, 0.30])
        elif not lines:
            _para(doc, "System Reporter printed no FC or iSCSI host port for this window.")
        for line in lines:
            _para(doc, line)

    _para(doc, "All volumes", bold=True)
    if not _read_failed(doc, data, handover.VOLUMES, warnings):
        if reads.volume_load is not None:
            _table(doc, ["Volumes", "IO/s", "MB/s", "Service time (ms)"],
                   [["All volumes together", *_io_cells(reads.volume_load.stats)]], widths=[0.22, 0.24, 0.24, 0.30])
        else:
            _para(doc, "System Reporter printed no volume figure for this window.")


def _add_hosts_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    from alletra_onboard.application.documents.asbuilt_parse import parse_cli_sets
    from alletra_onboard.application.provisioning.discovery import UNCLAIMED_HOST, parse_showhost

    _h1(doc, "Hosts and host sets")
    sets = OrderedDict() if data.read_errors.get("showhostset") else parse_cli_sets(data.showhostset)
    in_sets = _members_of(sets)
    if not _read_failed(doc, data, "showhost -d", warnings):
        hosts = parse_showhost(data.showhost_d)
        named = [h for h in hosts if h.name != UNCLAIMED_HOST]
        unclaimed = [h for h in hosts if h.name == UNCLAIMED_HOST]
        _para(doc, "Every host object on the array, with the initiators it carries and the array ports "
                   "those initiators are logged in on. An initiator with no port is registered but not "
                   "logged in (not zoned, or the server is off).")
        if named:
            rows = []
            for h in named:
                initiators = list(h.wwpns) + list(h.iqns)
                ports = sorted({p for ps in list(h.wwpns.values()) + list(h.iqns.values()) for p in ps})
                rows.append([h.name, h.persona or "—", "\n".join(initiators) or "—",
                             ", ".join(ports) or "none", ", ".join(in_sets.get(h.name, [])) or "—"])
            _table(doc, ["Host", "Persona", "Initiators", "Logged in on", "Host sets"], rows,
                   widths=[0.20, 0.12, 0.30, 0.20, 0.18])
        else:
            _para(doc, "The array reports no host objects.")
        logins = [(i, ps, "") for u in unclaimed for i, ps in u.wwpns.items()]
        logins += [(i, ps, u.addresses.get(i, "")) for u in unclaimed for i, ps in u.iqns.items()]
        _para(doc, "Logged in, no host object", bold=True)
        if logins:
            _para(doc, "Initiators the array sees on its ports that belong to no host object — zoned or "
                       "connected, never provisioned.")
            _table(doc, ["Initiator", "Logged in on", "Address"],
                   [[i, ", ".join(sorted(ps)) or "none", a or "—"] for i, ps, a in logins],
                   widths=[0.50, 0.30, 0.20])
        else:
            _para(doc, "Every initiator logged in on the array belongs to a host object.")
    _para(doc, "Host sets", bold=True)
    if not _read_failed(doc, data, "showhostset", warnings):
        if sets:
            _table(doc, ["Host set", "Members"], [[n, ", ".join(m) or "—"] for n, m in sets.items()],
                   widths=[0.35, 0.65])
        else:
            _para(doc, "The array reports no host sets.")


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
    from alletra_onboard.application.documents.asbuilt_parse import parse_cli_sets, parse_showvv

    _h1(doc, "Volumes and volume sets")
    sets = OrderedDict() if data.read_errors.get("showvvset") else parse_cli_sets(data.showvvset)
    in_sets = _members_of(sets)
    if not _read_failed(doc, data, "showvv", warnings):
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
        _para(doc, "Every user volume on the array. Provisioning is the array's word: tpvv (thin), tdvv "
                   "(thin with data reduction), full, dds (dedup store).")
        if user:
            _table(doc, ["Volume", "Provisioning", "Dedup", "Compression", "Size (GiB)", "CPG", "Snapshots", "VV set"],
                   [[r.get("Name", ""), r.get("Prov", "—"), r.get("Dedup", "—"), _compression(r.get("Compr", "")),
                     _gib(r.get(size_key, "")), cpg_by_name.get(r.get("Name", "")) or "—",
                     str(snap_count.get(r.get("Name", ""), 0)), ", ".join(in_sets.get(r.get("Name", ""), [])) or "—"]
                    for r in user],
                   widths=[0.26, 0.10, 0.08, 0.10, 0.10, 0.12, 0.10, 0.14])
        else:
            _para(doc, "The array reports no user volumes.")
        _para(doc, f"Not listed: {len(system)} system volume(s) and {len(snapshots)} snapshot(s).")
    _para(doc, "Volume sets", bold=True)
    if not _read_failed(doc, data, "showvvset", warnings):
        if sets:
            _table(doc, ["Volume set", "Members"], [[n, ", ".join(m) or "—"] for n, m in sets.items()],
                   widths=[0.35, 0.65])
        else:
            _para(doc, "The array reports no volume sets.")


def _add_presentations_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    from alletra_onboard.application.documents.asbuilt_parse import parse_showvlun_templates_cli
    from alletra_onboard.application.provisioning.path_verify import parse_showvlun_active

    _h1(doc, "Presentations")
    if _read_failed(doc, data, "showvlun -t", warnings):
        return
    templates = parse_showvlun_templates_cli(data.showvlun_t)
    active_ok = not _read_failed(doc, data, "showvlun -a", warnings)
    active = parse_showvlun_active(data.showvlun_a) if active_ok else []
    _para(doc, "What is presented to whom (the array's VLUN templates), and whether anyone can see it "
               "right now (active paths).")
    if not templates:
        _para(doc, "The array reports no presentations.")
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
    _table(doc, ["LUN", "Volume", "Presented to", "Active paths"], rows, widths=[0.08, 0.30, 0.30, 0.32])


def _zoning_check_text(report: dict, *, check_only: bool) -> str:
    """What the zoning check found, host by host. The check's gate list (`zoned_hosts`) also holds iSCSI
    hosts logged in on the array, which need no zone and are on no fabric: they are named apart, so the
    document never calls one zoned (live 2026-11-17: *Zoned on both fabrics: zz_is_eljr*, an iSCSI host)."""
    iscsi: dict[str, list[str]] = report.get("iscsi_hosts") or {}
    fc_zoned = [h for h in report.get("zoned_hosts", []) if h not in iscsi]
    unverified = report.get("unverified_hosts", [])
    logged_in = [f"{h} (logged in on {', '.join(ports)})" for h, ports in sorted(iscsi.items()) if ports]
    waiting = sorted(h for h, ports in iscsi.items() if not ports)
    parts = []
    if fc_zoned or unverified or report.get("expected") or not iscsi:
        if check_only:
            parts.append("Zoned on both fabrics: " + (", ".join(fc_zoned) or "none") + ".")
        else:
            parts.append(f"zoned on both fabrics — {', '.join(fc_zoned)}." if fc_zoned else "no host zoned on both fabrics.")
    if logged_in:
        parts.append("iSCSI, no zoning needed: " + ", ".join(logged_in) + ".")
    if waiting:
        parts.append("iSCSI, not logged in on the array yet, so nothing is exported to it: " + ", ".join(waiting) + ".")
    if unverified:
        parts.append(f"Not seen by the array on either fabric: {', '.join(unverified)}." if check_only
                     else f"Not verified — {', '.join(unverified)}.")
    return " ".join(parts)


def _add_zoning_section(doc, data: AsBuiltData) -> None:
    _h1(doc, "SAN zoning designed in this run")
    plan = data.zoning_plan
    report = data.zoning_report
    if not plan and not report:
        _para(doc, "This run did not include the SAN zoning step.")
        return
    if not plan:
        # The check ran (array-side) but no plan was built: say what the check found, plainly.
        _para(doc, "The zoning check ran against the array's logins; no zoning plan was built and no "
                   "command set was generated in this run.")
        _para(doc, _zoning_check_text(report, check_only=True))
        return
    rendered = data.zoning_rendered or {}
    aliases: dict[str, str] = rendered.get("aliases") or {}
    delivered = {tuple(p) for p in rendered.get("selected_pairs") or []}
    commands: dict[str, list[str]] = rendered.get("commands") or {}
    _para(doc, "The tool designs zones and hands the SAN team a command set; it never writes to a switch. "
               "Rows marked 'already zoned' were found in the fabric's effective configuration.")
    for fab in plan.get("fabrics", []):
        name = fab.get("fabric", "")
        bits = [f"{name} — switch {fab.get('switch_host', '')} {fab.get('switch_name', '')}".rstrip()]
        if fab.get("fabric_name"):
            bits.append(f"fabric {fab['fabric_name']}")
        if fab.get("active_cfg"):
            bits.append(f"active cfg {fab['active_cfg']}")
        if fab.get("switch_count"):
            bits.append(f"{fab['switch_count']} switch(es) in fabric")
        _para(doc, " · ".join(bits), bold=True)
        by_wwpn = {w["wwpn"]: w for w in fab.get("hosts", []) + fab.get("array_ports", [])}
        zoned = {tuple(p) for p in fab.get("already_zoned", [])}
        zone_names = fab.get("zone_names", {})

        def alias(wwpn: str, _by=by_wwpn) -> str:
            return aliases.get(wwpn) or _by.get(wwpn, {}).get("suggested_alias") or "—"

        rows = []
        for h, a in (tuple(p) for p in fab.get("pairs", [])):
            host, port = by_wwpn.get(h, {}), by_wwpn.get(a, {})
            if (h, a) in zoned:
                status = "already zoned"
            elif (h, a) in delivered:
                status = "command set delivered"
            else:
                status = "not selected"
            rows.append([host.get("host_name") or "—", host.get("display", h), alias(h),
                         port.get("nsp", "—"), port.get("display", a), alias(a),
                         ", ".join(zone_names.get(f"{h}|{a}", [])) or "—", status])
        if rows:
            _table(doc, ["Host", "HBA WWPN", "Alias", "Array port", "Array WWPN", "Alias", "Zone(s)", "Status"], rows,
                   widths=[0.14, 0.16, 0.12, 0.08, 0.16, 0.12, 0.12, 0.10])
        else:
            _para(doc, "No host HBA on this fabric needed a zone to this array.")
        if commands.get(name):
            _para(doc, "Delivered to the SAN team for application; confirm against the fabric before relying on it.")
            _mono(doc, commands[name])
    if plan.get("offline_hosts"):
        _para(doc, "On no fabric (cable and power first): " + ", ".join(plan["offline_hosts"]))
    if not rendered:
        _para(doc, "No command set was generated in this run.")
    if report:
        _para(doc, "Zoning check on the array: " + _zoning_check_text(report, check_only=False))
    else:
        _para(doc, "The zoning check was not run.")


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


def _when(iso: str) -> str:
    """'2026-09-13T00:05:12.123+00:00' -> '2026-09-13 00:05 UTC' (anything else passes through)."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2}(?:\.\d+)?)?(Z|[+-]00:00)?", iso or "")
    if not m:
        return iso
    return f"{m.group(1)} {m.group(2)}" + (" UTC" if m.group(3) else "")


def _add_provisioning_section(doc, data: AsBuiltData) -> None:
    _h1(doc, "Provisioning performed in this run")
    result = data.provisioning_result
    if not result:
        _para(doc, "A plan was built but not applied." if data.provisioning_plan
              else "This run did not include the provisioning step.")
        return
    when = f" at {_when(data.provisioning_applied_at)}" if data.provisioning_applied_at else ""
    _para(doc, f"Objects the tool created or found on the array{when}. 'Already existed' means the object "
               "was there and matched; 'Updated' means members, WWNs or iSCSI names were added, nothing removed.")
    outcomes = result.get("outcomes", [])
    if outcomes:
        _table(doc, ["Kind", "Name", "Result", "Detail"],
               [[o.get("kind", ""), o.get("name", ""), _OUTCOME_LABEL.get(o.get("status", ""), o.get("status", "")),
                 o.get("detail") or "—"] for o in outcomes],
               widths=[0.10, 0.30, 0.18, 0.42])
    if result.get("error"):
        _para(doc, f"Provisioning stopped with an error: {result['error']}")
    _para(doc, "To remove what this run created", bold=True)
    snapshot_items: list[dict] = []
    if data.snapshots_tab is not None:
        # SPEC-023 R6: the snapshot lines go first; removevv refuses a volume that still has snapshots
        from alletra_onboard.application.documents.asbuilt_snapshots import snapshot_removal_items

        snapshot_items = snapshot_removal_items(data)
    removal_lines = _removal_lines(snapshot_items + (data.provisioning_removals or result.get("removals") or []))
    if removal_lines:
        _para(doc, "The undo for exactly the objects this run created, in dependency order ("
                   + ("snapshot schedules, snapshots, " if snapshot_items else "") + "exports, VV sets, "
                   "volumes, host sets, hosts). Objects that existed before the run are not listed. Review "
                   "before pasting; the tool never runs these.")
        _mono(doc, removal_lines)
    else:
        _para(doc, "Nothing — this run created no objects.")
    _para(doc, "Path verification", bold=True)
    paths = data.path_verification
    if not paths:
        _para(doc, "Path verification was not run.")
        return
    if paths.get("error"):
        _para(doc, f"Path verification failed: {paths['error']}")
        return
    hosts = paths.get("hosts", [])
    if hosts:
        # SPEC-013 R5: the array's view and the ESXi host's view side by side.
        _table(doc, ["Host", "Verdict", "Array view", "ESXi view"],
               [[h.get("host", ""), _VERDICT_LABEL.get(h.get("verdict", ""), h.get("verdict", "")), h.get("detail", ""),
                 h.get("esxi_note") or "not read"]
                for h in hosts],
               widths=[0.20, 0.12, 0.38, 0.30])
    else:
        _para(doc, "No target hosts to verify.")


def _add_iscsi_network_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-024 R7: when the array has a VLAN-tagged iSCSI address or the sheet asks for one: every
    interface on every iSCSI port with the port's state (showport -iscsivlans has no State column),
    whether this run set it up, then the sentences for the network team."""
    # Imported here: replication.read imports this module (through asbuilt_parse) at load time.
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans
    from alletra_onboard.application.provisioning.iscsi_network import (
        GATEWAY_WINDOW,
        gateway_window,
        gw_line,
        switch_handoff_for,
    )
    from alletra_onboard.application.replication.read import parse_showport_roles
    from alletra_onboard.domain.network import IscsiVlanAction, IscsiVlanRequest

    command = "showport -iscsivlans"
    rows = data.iscsi_network_rows
    unreadable = ""
    answer = data.showport_iscsivlans.strip()
    if answer.lower().startswith("error"):
        vlans, unreadable = [], answer.splitlines()[0]
    else:
        try:
            vlans = parse_iscsi_vlans(answer)
        except ValueError as exc:
            vlans, unreadable = [], str(exc)
    # A read that failed cannot say the array has no interface, so the section names the failure.
    if not vlans and not rows and not unreadable and command not in data.read_errors:
        return
    _h1(doc, "iSCSI network")
    if _read_failed(doc, data, command, warnings):
        return
    if unreadable:
        _para(doc, f"`{command}` could not be read: {unreadable}")
        warnings.append(f"`{command}` could not be read ({unreadable}); the iSCSI network section is empty.")
        return
    roles, _wwn = parse_showport_roles(data.showport)
    name = data.name or data.serial_no or "the array"
    if vlans:
        _para(doc, f"The VLAN-tagged iSCSI addresses on {name}'s iSCSI ports when this document was made. Each port's "
                   "untagged address is not listed here; it stays as it was.")
        set_up = {(nsp, vlan) for nsp, vlan in data.iscsi_set_up_in_run}
        _table(doc, ["Port", "VLAN", "Address", "Gateway", "MTU", "Port state", "Set up"],
               [[v.nsp, str(v.vlan_id), f"{v.ip}/{_prefix(v.netmask)}", v.gateway or "—", v.mtu or "—",
                 roles[v.nsp].state if v.nsp in roles else "—",
                 "By this run" if (v.nsp, v.vlan_id) in set_up else "Already there"] for v in vlans])
    else:
        _para(doc, f"{name} has no VLAN-tagged iSCSI address.")
    there = {(v.nsp, v.vlan_id) for v in vlans}
    absent = [r for r in rows if (r.get("nsp"), r.get("vlan_id")) not in there]
    if absent:
        _para(doc, "Asked for on the sheet but not on the array: "
                   + ", ".join(f"{r.get('nsp')} VLAN {r.get('vlan_id')} ({r.get('ip')})" for r in absent) + ".")
    # ADR 0017, amended 2026-11-17: the tool adds the address without its gateway; a gateway the sheet gives
    # and the array does not have yet is the change window's, printed here with its lines.
    gateways = {(v.nsp, v.vlan_id): v.gateway for v in vlans}
    pending = []
    for row in rows:
        key = (row.get("nsp"), row.get("vlan_id"))
        if row.get("gateway") and key in gateways and not gateways[key]:
            req = IscsiVlanRequest.model_validate(row)
            pending.append(IscsiVlanAction(nsp=req.nsp, vlan_id=req.vlan_id, state="exists", gateway_cli=gw_line(req)))
    if pending:
        _para(doc, "Gateways for a change window", bold=True)
        _para(doc, "The sheet gives a gateway for "
                   + ", ".join(f"{a.nsp} VLAN {a.vlan_id}" for a in pending)
                   + f", and the array has none. {GATEWAY_WINDOW} The lines, kept for that window:")
        _mono(doc, gateway_window(pending))
    sentences = switch_handoff_for(name, vlans)
    if sentences:
        _para(doc, "For the network team", bold=True)
        _para(doc, "The tool does not change any switch. Each switch port cabled to these array ports carries the "
                   "VLANs tagged and keeps its native VLAN for the untagged address:")
        _mono(doc, sentences)


def _add_peer_ports_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-025 R9, when the sheet has the Peer ports tab: each port as the array reads it now (mode,
    connection, state, WWNs), the array's own peer-port listing, the commands and who ran them, the
    peer-port zones designed in the run, and the removal set."""
    if not data.peer_ports_rows:
        return
    # Imported here: replication.read imports this module (through asbuilt_parse) at load time.
    from alletra_onboard.application.provisioning.peer_ports import (
        parse_showport_par,
        parse_showport_peer,
        parse_showport_ports,
    )

    _h1(doc, "Peer ports")
    name = data.name or data.serial_no or "the array"
    ports = parse_showport_ports(data.showport)
    params = parse_showport_par(data.showport_par)
    _para(doc, f"The Fibre Channel ports of {name} named on the sheet's Peer ports tab, as the array reads them when "
               "this document was made. A peer port logs in to the fabric as an initiator so a data migration can "
               "read the source array through it.")
    rows = []
    for req in data.peer_ports_rows:
        nsp = req.get("nsp", "")
        p, par = ports.get(nsp), params.get(nsp)
        rows.append([nsp, p.type if p else "not on the array", f"{par.connmode}, {par.conntype}" if par else "—",
                     p.state if p else "—", p.node_wwn if p and p.node_wwn else "—", p.port_wwn if p and p.port_wwn else "—",
                     ", ".join(req.get("source_wwpns") or []) or "—"])
    _table(doc, ["Port", "Type", "Connection", "State", "Node WWN", "Port WWN", "Source ports to zone"], rows)
    listed = parse_showport_peer(data.showport_peer)
    if listed:
        _para(doc, "The array's own list of its peer ports (showport -peer)", bold=True)
        _table(doc, ["Port", "Mode", "State", "Node WWN", "Port WWN"],
               [[r.nsp, r.mode, r.state, r.node_wwn or "—", r.port_wwn or "—"] for r in listed])
    _para(doc, "How they were set", bold=True)
    plan = data.peer_ports_plan or {}
    creates = [a for a in plan.get("actions") or [] if a.get("state") == "create"]
    result = data.peer_ports_result or {}
    if creates and result.get("changed"):
        _para(doc, "The tool printed these commands and a consultant pasted them on the array's CLI; the tool does "
                   "not run them. The read after the paste checked each port and every other port.")
        _mono(doc, [line for a in creates for line in [f"# {a.get('nsp', '')}", *(a.get("commands") or [])]])
    elif creates:
        _para(doc, "The tool printed these commands for a consultant to paste; no port change was seen on the array "
                   "in this run.")
        _mono(doc, [line for a in creates for line in [f"# {a.get('nsp', '')}", *(a.get("commands") or [])]])
    else:
        _para(doc, "No port was set in this run: every port the sheet names was already in peer mode, or no plan "
                   "had a port to set.")
    if result.get("sentences"):
        _mono(doc, list(result["sentences"]))
    if result.get("error"):
        warnings.append(f"Peer ports: the read after the paste did not match the plan: {result['error']}")
    _para(doc, "Peer-port zones designed in this run", bold=True)
    zones = (data.zoning_rendered or {}).get("peer_commands") or {}
    if any(zones.values()):
        _para(doc, "The command set given to the SAN team; the tool never writes to a switch.")
        for fabric, commands in sorted(zones.items()):
            if commands:
                _mono(doc, [f"# {fabric}", *commands])
    else:
        _para(doc, "No peer-port zone command set was generated in this run.")
    _para(doc, "To remove the peer ports", bold=True)
    removals = result.get("removals") or []
    if removals:
        _para(doc, "Puts each port this run set back in the mode it had, last port first. Remove the SAN team's "
                   "peer-port zones and any migration that uses these ports first. The tool never runs these.")
        _mono(doc, removals)
    else:
        _para(doc, "Nothing: the tool saw no port change in this run.")


def _prefix(mask: str) -> str:
    try:
        return str(ipaddress.ip_network(f"0.0.0.0/{mask}").prefixlen)
    except ValueError:
        return mask


def _add_provisioned_sections(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-002: the five sections appended after the template's last section; SPEC-024 and SPEC-025
    add the iSCSI network and Peer ports sections when the sheet or the array has them; SPEC-028 adds
    the file service when the array has one; SPEC-018 adds two more when the run's workbook has a
    Replication tab."""
    _add_hosts_section(doc, data, warnings)
    _add_volumes_section(doc, data, warnings)
    _add_presentations_section(doc, data, warnings)
    _add_iscsi_network_section(doc, data, warnings)
    _add_peer_ports_section(doc, data, warnings)
    _add_zoning_section(doc, data)
    _add_provisioning_section(doc, data)
    _add_file_section(doc, data, warnings)
    if data.replication_tab is not None:
        _add_replication_section(doc, data, warnings)
        _add_failover_section(doc, data)
    if data.snapshots_tab is not None:
        from alletra_onboard.application.documents.asbuilt_snapshots import add_snapshots_section

        add_snapshots_section(doc, data, warnings)
    if data.trusted_devices:
        _add_device_fingerprints(doc, data)
    if data.commands:
        _add_commands_appendix(doc, data)


_DEVICE_LABEL = {"array": "Array", "switch": "SAN switch", "Linux host": "Linux host", "vCenter": "vCenter"}


def _add_device_fingerprints(doc, data: AsBuiltData) -> None:
    """ADR 0026: the key each on-site device presented, so the customer can compare it with the device."""
    _h1(doc, "Device fingerprints")
    _para(doc, "The tool trusted each device below the first time this run connected to it, and checked the "
               "same key on every later connection. Compare each fingerprint with the one the device's own "
               "console shows.")
    rows = []
    for d in data.trusted_devices:
        port = d.get("port")
        address = d.get("host", "") if port in (22, 443) else f"{d.get('host', '')}:{port}"
        key = f"SSH host key ({d.get('key_type', '')})" if d.get("kind") == "ssh" else "TLS certificate"
        how = "Again, by the operator" if d.get("how") == "retrusted" else "First contact"
        trusted = f"{how}, {_when(str(d.get('trusted_at') or ''))}"
        if d.get("refused_fingerprint"):
            trusted += (f". Later presented {d['refused_fingerprint']}, which was refused "
                        f"({_when(str(d.get('refused_at') or ''))})")
        rows.append([_DEVICE_LABEL.get(d.get("device", ""), d.get("device", "")), address, key,
                     d.get("fingerprint", ""), trusted])
    _table(doc, ["Device", "Address", "Key", "SHA-256 fingerprint", "Trusted"], rows)


# ------------------------------------------------------------------ SPEC-028 R3: the file service

def _size(mib: int) -> str:
    """The file side counts in MiB."""
    if mib >= 1024 * 1024:
        return f"{mib / (1024 * 1024):.1f} TiB"
    return f"{mib / 1024:.1f} GiB".replace(".0 GiB", " GiB")


def _state(state: str) -> str:
    """'STATE_NORMAL' -> 'normal'."""
    return state.removeprefix("STATE_").replace("_", " ").lower()


def _add_file_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-028 R3: the file service, its File ports, file systems and shares with their clients, as
    the array reports them when the document is made. Absent on an array with no File ports and the
    file service off; nothing here was changed by the run."""
    from alletra_onboard.domain.unified_file import NODE_RUNNING

    report = data.file_report
    if not data.file_read_error and report is None:
        return
    _h1(doc, "File service")
    if data.file_read_error:
        _para(doc, f"The file side could not be read: {data.file_read_error}")
        warnings.append(f"The file side could not be read ({data.file_read_error}); the File service "
                        "section is empty.")
        return
    service = report.service
    _para(doc, "The array's NFS file service, its File ports, file systems and shares, as read from the "
               "array when this document was made. This run changed nothing on the file side.")
    for note in report.notes:
        _para(doc, note)
    if service is None:
        reason = report.notes[0] if report.notes else "the file service was not read"
        warnings.append(f"The File service section lists only the File ports: {reason}")
    else:
        running = sum(1 for n in service.nodes if n.status == NODE_RUNNING)
        line = (f"File service: on, running on {running} of {len(service.nodes)} nodes."
                if service.enabled else "File service: off.")
        cap = service.capacity
        if cap is not None:
            line += (f" Capacity for file: {_size(cap.total)}, {_size(cap.used)} used, "
                     f"{_size(cap.available)} available.")
        _para(doc, line)

    _para(doc, "File ports", bold=True)
    if data.file_ports:
        _table(doc, ["Port", "Address", "Gateway", "VLAN", "MTU", "Link"],
               [[p.label, f"{p.address}/{p.prefix_len}" if p.address else "—", p.gateway or "—",
                 p.vlan or "—", p.mtu or "—", f"{p.link} ({p.link_state})" if p.link else p.link_state or "—"]
                for p in data.file_ports])
    else:
        _para(doc, "The array has no File ports.")
    if service is None:
        return

    _para(doc, "File systems", bold=True)
    if report.file_systems:
        _table(doc, ["File system", "Size", "Data reduction", "Shares", "Owner node", "State"],
               [[fs.name, _size(fs.size_mib), "Yes" if fs.reduce else "No", str(fs.share_count),
                 str(fs.owner_node), _state(fs.state)] for fs in report.file_systems])
    else:
        _para(doc, "The array has no file systems.")

    _para(doc, "Shares", bold=True)
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
        _table(doc, ["Share", "File system", "Client group", "Clients", "Mount", "Protocol", "State"], rows)
        _para(doc, "A share's clients are its client group's. A client of * is any host that can reach "
                   "the File ports.")
    else:
        _para(doc, "The array has no shares.")


_TRANSPORT_LABEL = {
    "ssh": "CLI (SSH)", "wsapi": "WSAPI", "fos": "switch (SSH)", "vcenter": "vCenter",
    "host-ssh": "Linux host (SSH)", "winrm": "Windows host (WinRM)", "greenlake": "GreenLake API",
}


def _add_commands_appendix(doc, data: AsBuiltData) -> None:
    """SPEC-019 R2: what touched the arrays in this run, and the switches, vCenter, hosts and GreenLake
    the run reached. Changes one by one; reads counted, not shown."""
    _h1(doc, "Commands run on the array")
    writes = [c for c in data.commands if c.get("write")]
    reads = [c for c in data.commands if not c.get("write")]
    _para(doc, f"The tool recorded every command it sent for this run as it ran, to the array and to any "
               f"switch, vCenter, host or GreenLake service it reached: {len(writes)} change(s) and "
               f"{len(reads)} read-only command(s). The full output of each is in the run's command log "
               "(the app's console, Download .txt).")
    if writes:
        _para(doc, "Changes", bold=True)
        _table(doc, ["Time", "Device", "Via", "Call", "Result"],
               [[_when(c.get("at", "")), c.get("target", ""), _TRANSPORT_LABEL.get(c.get("transport", ""), c.get("transport", "")),
                 c.get("command", "")[:160], c.get("result", "")[:120]] for c in writes])
    else:
        _para(doc, "No change was made to any array by this run.")
    counted: OrderedDict[tuple[str, str, str], int] = OrderedDict()
    for c in reads:
        key = (c.get("target", ""), c.get("transport", ""), c.get("command", "")[:120])
        counted[key] = counted.get(key, 0) + 1
    if counted:
        _para(doc, "Read-only commands", bold=True)
        _table(doc, ["Device", "Via", "Command", "Times"],
               [[t, _TRANSPORT_LABEL.get(v, v), cmd, str(n)] for (t, v, cmd), n in counted.items()])


# ------------------------------------------------------------------ SPEC-018: replication

_RC_OUTCOME_LABEL = {"created": "Done", "exists": "Already existed", "failed": "Failed", "skipped": "Skipped"}
_RC_KIND_LABEL = {
    "group": "Remote Copy group", "peer_vvset": "Peer volume set", "test_volume": "Test volume",
    "test_vvset": "Test volume set", "volume_admit": "Volume admitted", "start": "Group started",
    "policy": "Policies and period", "rcip_port": "Replication port", "rc_service": "Remote Copy service",
    "target": "Remote Copy target", "ping": "Ping between the ports", "links": "Links Up",
}


def _rc_view(view, name_fallback: str):
    """(view or None, display name, read error or '') for one side."""
    if view is None:
        return None, name_fallback, "not read"
    err = getattr(view, "read_error", None) or ""
    return (None if err else view), (getattr(view, "name", "") or getattr(view, "host", "") or name_fallback), err


def _rc_group_rows(data: AsBuiltData) -> list[dict]:
    """The groups this run configured: from the apply's outcomes when it ran; without an apply, only the
    groups the plan found already in place (a planned-but-not-created group is not on the array)."""
    if data.replication_result:
        names = [o.get("name") for o in data.replication_result.get("outcomes", [])
                 if o.get("kind") == "group" and o.get("status") in ("created", "exists")]
    elif data.replication_plan:
        names = [a.get("name") for a in data.replication_plan.get("actions", [])
                 if a.get("kind") == "group" and a.get("state") == "exists"]
    else:
        names = []
    detail = {a.get("name"): a.get("detail") or {} for a in (data.replication_plan or {}).get("actions", []) if a.get("kind") == "group"}
    return [{"name": n, **detail.get(n, {})} for n in dict.fromkeys(n for n in names if n)]


def _rc_peer_set(peer, peer_group) -> str:
    """The peer volume set holding exactly the peer group's volumes (the array's own RCP_ sets aside)."""
    if peer is None or peer_group is None or not peer_group.volumes:
        return ""
    want = set(peer_group.volume_names)
    return next((name for name, members in peer.vvsets.items() if set(members) == want and not name.startswith("RCP_")), "")


def _rc_rpo_text(row: dict, tab: dict, period_read: str = "") -> str:
    """'RPO 10 min (period 5m)' for a periodic group, 'sync (every write)' otherwise. The period comes
    from the array when it was read; the RPO is the workbook's number for that volume set."""
    period = row.get("period_seconds")
    if not period and not period_read:
        return "sync (every write)"
    rpo = next((r.get("rpo_minutes") for r in tab.get("rows", []) if r.get("vvset") == row.get("vvset")), None)
    if not rpo and period:
        rpo = period * 2 // 60
    shown = period_read or (f"{period // 60}m" if period else "?")
    return (f"RPO {rpo} min " if rpo else "") + f"(period {shown})"


def _add_link_check(doc, data: AsBuiltData) -> None:
    """SPEC-020 R6: what `checkrclink` measured, the limit for each configured mode, and whether the
    operator accepted a latency over it (the apply's note says so)."""
    from alletra_onboard.application.replication.link_check import PING_COUNT
    from alletra_onboard.domain.replication import RTT_LIMIT_MS, rtt_limit_ms, rtt_limit_text

    check = data.link_check or {}
    _para(doc, "Link check", bold=True)
    results = check.get("results", [])
    measured = [r for r in results if r.get("status") == "measured" and r.get("latency_ms") is not None]
    modes = check.get("modes", [])
    limits = "; ".join(rtt_limit_text("IP", m) for m in modes if m in RTT_LIMIT_MS["IP"])
    if check.get("error") or not measured:
        _para(doc, f"The latency between the arrays was not measured: {check.get('error') or 'no link could be tested'}.")
        return
    worst = max(r["latency_ms"] for r in measured)
    accepted = any("accepted it and chose to continue" in n for n in (data.replication_result or {}).get("notes", []))
    over = [m for m in modes if worst > rtt_limit_ms("IP", m)]
    verdict = ("over HPE's limit for " + "/".join(over) + (" — the operator accepted the measured latency and continued." if accepted else ".")
               if over else "within HPE's limit.")
    _para(doc, f"Measured with checkrclink on {check.get('at', '')} (test length {check.get('duration_s', '')} s, stopped "
               f"once the latency was printed): worst latency {worst:g} ms on {len(measured)} link(s); {limits}. "
               f"The latency is {verdict}")
    rows = []
    by_ping = False
    for r in results:
        pair = r.get("pair", {})
        link = f"A {pair.get('nsp_a', '')} ({pair.get('ip_a', '')}) → B {pair.get('nsp_b', '')} ({pair.get('ip_b', '')})"
        if r.get("status") == "measured":
            lost = r.get("pings_lost_pct")
            ping = (r.get("detail") or "").startswith("Measured with ping")
            by_ping = by_ping or ping
            rows.append([link, f"{r.get('latency_ms'):g} ms" + (" (ping)" if ping else ""), f"{lost:g} %" if lost is not None else "—"])
        else:
            rows.append([link, "not measured", r.get("detail") or "—"])
    _table(doc, ["Link", "Latency", "Pings lost"], rows, widths=[0.56, 0.18, 0.26])
    if by_ping:
        _para(doc, "(ping): the array's link test printed its latency line with no number on that link, so the tool "
                   f"measured the average round trip with {PING_COUNT} pings from the same port to the same address.")
    for line in check.get("unchecked", []):
        _para(doc, f"Not checked: {line}")


def _add_typed_latency(doc, data: AsBuiltData) -> None:
    """SPEC-031 R6/R7: over Fibre Channel the latency is the round-trip time the engineer typed on the
    Replication tab, held to the FC limit; the document says it was typed, not measured."""
    from alletra_onboard.domain.replication import rtt_limit_ms, rtt_limit_text

    tab = data.replication_tab or {}
    rtt = tab.get("rtt_ms")
    modes = sorted({r.get("mode") for r in tab.get("rows", []) if r.get("mode")}) or ["async"]
    _para(doc, "Round-trip time", bold=True)
    if rtt is None:
        _para(doc, "The arrays replicate over Fibre Channel and no round-trip time was typed on the Replication tab. "
                   "The tool cannot measure Fibre Channel links yet, so the latency between the arrays is not recorded.")
        return
    over = [m for m in modes if rtt > rtt_limit_ms("FC", m)]
    accepted = any("accepted it and chose to continue" in n for n in (data.replication_result or {}).get("notes", []))
    verdict = ("over HPE's limit for " + "/".join(over) + (" — the operator accepted the typed time and continued." if accepted else ".")
               if over else "within HPE's limit.")
    limits = "; ".join(rtt_limit_text("FC", m) for m in modes)
    _para(doc, f"Typed by the engineer on the Replication tab, not measured: {rtt:g} ms. The tool cannot measure Fibre "
               f"Channel links yet. {limits[0].upper() + limits[1:]}. The typed time is {verdict}")


def _add_replication_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    from alletra_onboard.application.replication.plan import find_partnership
    from alletra_onboard.application.replication.verify import peer_group_name

    tab = data.replication_tab or {}
    _h1(doc, "Replication configured in this run")
    a, a_name, a_err = _rc_view(data.replication_primary, data.name or "this array")
    b, b_name, b_err = _rc_view(data.replication_peer, tab.get("peer_host", "the peer array"))
    rows = tab.get("rows", [])
    _para(doc, f"The workbook's Replication tab asked for {len(rows)} volume set(s) to be replicated to "
               f"{b_name}. Everything below was read from both arrays when this document was generated; "
               "nothing is copied from the plan.")
    if a_err:
        _para(doc, f"{a_name} could not be read for this section: {a_err}")
        warnings.append(f"The replication section could not read this array ({a_err}); its states are missing.")
    if b_err:
        _para(doc, f"The peer array could not be read for this section: {b_err}. Its columns below say so.")
        warnings.append(f"The replication section could not read the peer array ({b_err}); the peer's columns are empty.")

    # -- partner array and partnership
    _para(doc, "Partner array", bold=True)
    partnership = find_partnership(a, b) if a is not None and b is not None else None
    # SPEC-031 R7: the replication ports are RCIP addresses, or over Fibre Channel each FC link (port → peer WWN)
    transport = (partnership.transport if partnership is not None
                 else ((data.replication_report or {}).get("partnership") or {}).get("transport", "IP"))

    def side(view, name, err):
        if view is None:
            return [name, "could not be read" if err else "—", "—", "—", "—"]
        rc = f"{view.rc_status}{', ' + view.rc_health if view.rc_health else ''}" or "—"
        if transport == "FC":
            fc = {t.name for t in view.targets if t.is_fc}
            ports = "; ".join(f"{link.nsp} → {link.address}" for link in view.links if link.target in fc) or "none"
        else:
            ports = "; ".join(f"{p.nsp} {p.ip}" for p in view.rcip_ports) or "none configured"
        return [name, view.serial or "—", view.os_version or "—", rc, ports]
    _table(doc, ["Array", "Serial", "OS", "Remote Copy", "Replication ports"],
           [["This array: " + a_name, *side(a, a_name, a_err)[1:]], ["Peer: " + b_name, *side(b, b_name, b_err)[1:]]],
           widths=[0.26, 0.14, 0.10, 0.16, 0.34])
    if partnership is None:
        _para(doc, "No Remote Copy partnership between the two arrays could be confirmed when this document was "
                   "generated" + (" (one side was not readable)." if a_err or b_err else "."))
    else:
        link_rows = []
        for view, name in ((a, a_name), (b, b_name)):
            for t in view.targets:
                for link in view.links:
                    if link.target == t.name and not link.inbound:
                        link_rows.append([name, t.name, t.policy or "—", f"{link.nsp} → {link.address}", link.status])
        _para(doc, f"Partnered: {a_name} → {b_name} via target '{partnership.target_on_primary}' "
                   f"({partnership.links_primary_up}/{partnership.links_primary_total} links Up); "
                   f"{b_name} → {a_name} via target '{partnership.target_on_peer}' "
                   f"({partnership.links_peer_up}/{partnership.links_peer_total} links Up). "
                   + ("Over Fibre Channel, found by port WWN." if partnership.transport == "FC"
                      else "Over RCIP, found by link address."))
        _table(doc, ["Array", "Target", "Policy",
                     "Link (port → peer port WWN)" if partnership.transport == "FC" else "Link (port → peer address)",
                     "Status"], link_rows, widths=[0.22, 0.22, 0.16, 0.28, 0.12])

    # -- SPEC-020 R6: the measured latency; SPEC-031 R6: over Fibre Channel, the typed one
    if transport == "FC":
        _add_typed_latency(doc, data)
    elif data.link_check:
        _add_link_check(doc, data)

    # -- groups configured by this run
    _para(doc, "Remote Copy groups configured by this run", bold=True)
    groups = _rc_group_rows(data)
    planned_new = [a for a in (data.replication_plan or {}).get("actions", []) if a.get("kind") == "group" and a.get("state") == "create"]
    if not data.replication_result and not data.replication_plan:
        _para(doc, "The replication step was not run in this run.")
    elif not data.replication_result and planned_new:
        _para(doc, "A replication plan was built but not applied.")
    elif data.replication_result and not groups:
        _para(doc, "The apply created no Remote Copy group.")
    if groups:
        suffix = (f" On the peer each group's name carries the suffix .r{a.system_id} (this array's system ID)."
                  if a is not None and a.system_id is not None else "")
        if data.replication_result:
            when = f" at {_when(data.replication_applied_at)}" if data.replication_applied_at else ""
            _para(doc, f"Configured over WSAPI{when}. Roles and states are as read now.{suffix}")
        else:
            _para(doc, "Already in place when this run read the arrays (configured by an earlier run); this run made no "
                       f"replication change. Roles and states are as read now.{suffix}")
        group_rows, volume_rows = [], []
        for row in groups:
            g = row["name"]
            ag = a.group(g) if a is not None else None
            bg = b.group(peer_group_name(g, a)) if (a is not None and b is not None) else None
            if ag is None:
                state = "could not be read" if a_err else "not on the array now"
                group_rows.append([g, row.get("mode", "—"), _rc_rpo_text(row, tab), "—", state, "—", "—", row.get("peer_vvset") or "—"])
                continue
            period = _rc_rpo_text(row, tab, ag.period)
            peer_role = (bg.role if bg else ("could not be read" if b_err else "not found on the peer"))
            peer_set = row.get("peer_vvset") or _rc_peer_set(b, bg) or "—"
            if b is not None and peer_set != "—":
                members = b.vvsets.get(peer_set)
                peer_set += " (missing on the peer)" if members is None else f" ({len(members)} volume(s))"
            synced = sum(1 for v in ag.volumes if v.sync_status.lower() == "synced")
            status = f"{ag.status} · {synced}/{len(ag.volumes)} Synced" + (f" · last sync {ag.last_sync}" if ag.last_sync and ag.last_sync != "NA" else "")
            group_rows.append([g, ag.mode, period, ", ".join(ag.options) or "—", ag.role, peer_role, status, peer_set])
            for v in ag.volumes:
                size = a.volume_size_mib.get(v.local_name) if a is not None else None
                volume_rows.append([g, v.local_name, _gib(str(size)) if size else "—", v.remote_name or "—",
                                    v.sync_status or "—", v.last_sync if v.last_sync and v.last_sync != "NA" else "—"])
        _table(doc, ["Group", "Mode", "RPO / period", "Policies", "Role here", "Role on peer", "Status", "Peer volume set"],
               group_rows, widths=[0.14, 0.08, 0.14, 0.16, 0.09, 0.10, 0.17, 0.12])
        if volume_rows:
            _table(doc, ["Group", "Volume here", "Size (GiB)", "Volume on peer", "Sync status", "Last sync"],
                   volume_rows, widths=[0.18, 0.20, 0.10, 0.20, 0.12, 0.20])

    # -- groups the run did not create
    _para(doc, "Replication already present", bold=True)
    ours = {row["name"] for row in groups}
    others = [g for g in (a.groups if a is not None else []) if g.name not in ours]
    if a is None:
        _para(doc, "Not known: this array could not be read.")
    elif not others:
        _para(doc, f"No other Remote Copy groups are on {a_name}.")
    else:
        _para(doc, "Groups on this array that this run did not configure. Listed for the record; not changed by the tool.")
        _table(doc, ["Group", "Target", "Mode", "Role here", "Status", "Volumes"],
               [[g.name, g.target, g.mode + (f" every {g.period}" if g.period else ""), g.role, g.status, str(len(g.volumes))] for g in others],
               widths=[0.28, 0.22, 0.14, 0.10, 0.12, 0.14])

    # -- what was run and how to undo it
    result = data.replication_result
    if result:
        applies = data.replication_applies or [{"plan": data.replication_plan, "result": result}]
        calls = [(where, cli) for x in applies for _seq, where, cli in sorted(
            ((c.get("seq", 0), c.get("where", "A"), c.get("cli", "")) for act in (x.get("plan") or {}).get("actions", [])
             for c in act.get("calls", [])), key=lambda t: t[0])]
        if calls:
            _para(doc, "What was run, in order", bold=True)
            _para(doc, "Each call the tool made, shown as the array CLI command (a WSAPI call as the command it is "
                       "equivalent to). A = this array, B = the peer.")
            _mono(doc, [f"{where}  {cli}" for where, cli in calls])
        outcomes = [o for x in applies for o in (x.get("result") or {}).get("outcomes", [])]
        if outcomes:
            _para(doc, "What each array reported", bold=True)
            _table(doc, ["Kind", "Name", "On", "Result", "Detail"],
                   [[_RC_KIND_LABEL.get(o.get("kind", ""), o.get("kind", "")), o.get("name", ""), o.get("where", "A"),
                     _RC_OUTCOME_LABEL.get(o.get("status", ""), o.get("status", "")), o.get("detail") or "—"] for o in outcomes],
                   widths=[0.18, 0.22, 0.06, 0.14, 0.40])
        if result.get("error"):
            _para(doc, f"Replication stopped with an error: {result['error']}")
        _para(doc, "To remove what this run created", bold=True)
        rem_a = data.replication_removals_a or result.get("removals_a") or []
        rem_b = data.replication_removals_b or result.get("removals_b") or []
        if rem_a or rem_b:
            _para(doc, "Paste the A block on this array first, then the B block on the peer. Depending on the "
                       "peer, the array may already have removed a peer volume set or a secondary volume, so a "
                       "B line may answer 'does not exist'. "
                       "Objects that existed before the run are not listed. The tool never runs these.")
            lines = []
            if rem_a:
                lines += [f"# ---- A: {a_name}", *rem_a]
            if rem_b:
                lines += [f"# ---- B: {b_name}", *rem_b]
            _mono(doc, lines)
        else:
            _para(doc, "Nothing — this run created no replication objects.")


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


def _add_failover_section(doc, data: AsBuiltData) -> None:
    _h1(doc, "Failover test")
    rec = data.failover_record
    if not rec:
        _para(doc, "The failover test was not run in this run.")
        return
    result = rec.get("result", "")
    label = _FAILOVER_RESULT.get(result, result)
    if result == "failed" and rec.get("failed_step") is not None:
        label += f" at step {rec['failed_step']}"
    mode = rec.get("mode") or "—"
    _para(doc, f"Result: {label}.", bold=True)
    _para(doc, f"Group {rec.get('group', '')} ({mode}) on {rec.get('primary_array', 'this array')} (P), named "
               f"{rec.get('peer_group') or '—'} on {rec.get('peer_array', 'the peer')} (S). Started {_when(rec.get('started_at', ''))}, "
               f"ended {_when(rec.get('ended_at', ''))}. Each role change is the array's own disaster-recovery action over WSAPI; "
               "both arrays were read after every step.")
    if rec.get("time_to_failover_s") is not None or rec.get("time_to_synced_s") is not None:
        bits = []
        if rec.get("time_to_failover_s") is not None:
            bits.append(f"the peer took over (Primary-Rev) {rec['time_to_failover_s']:g} s after the failover was issued")
        if rec.get("time_to_synced_s") is not None:
            bits.append(f"every volume was Synced again {rec['time_to_synced_s']:g} s after the recover")
        _para(doc, "Measured: " + "; ".join(bits) + ".")
    if mode == "async":
        _para(doc, "Data-loss bound (async): " + (rec.get("data_loss_bound") or "not recorded") + ". Writes after that sync and "
                   "before the failover would not have reached the peer.")
    rows = []
    for s in rec.get("steps", []):
        when = _when(s.get("started_at", "")) if s.get("started_at") else "—"
        secs = f"{s['seconds']:g} s" if s.get("seconds") is not None else "—"
        rows.append([str(s.get("seq", "")), s.get("title", ""), s.get("where", "-"), s.get("cli") or s.get("action") or "—",
                     when, secs, _side_text(s.get("primary")), _side_text(s.get("peer")), _FAILOVER_OUTCOME.get(s.get("outcome", ""), s.get("outcome", ""))])
    if rows:
        _table(doc, ["#", "Step", "On", "Command (CLI equivalent)", "Started", "Took", "P after", "S after", "Outcome"], rows,
               widths=[0.03, 0.14, 0.04, 0.22, 0.11, 0.06, 0.16, 0.16, 0.08])
    if result != "passed":
        if rec.get("error"):
            _para(doc, f"Stopped: {rec['error']}")
        if rec.get("observed_state"):
            _para(doc, f"Observed when it stopped: {rec['observed_state']}")
        if rec.get("recovery_action"):
            _para(doc, "The documented way back to the normal state (not run by the tool):", bold=True)
            _mono(doc, [rec["recovery_action"]])
    else:
        _para(doc, "The group ended the test in its starting state: Primary and Started on this array, Secondary and Started "
                   "on the peer, every volume Synced.")


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
