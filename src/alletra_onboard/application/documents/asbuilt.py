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
from dataclasses import dataclass, field
from pathlib import Path

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from alletra_onboard.application.documents.asbuilt_docx import hpe_table

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
    read_errors: dict[str, str] = field(default_factory=dict)   # command -> error text (R6)
    # SPEC-002 run sections — the run's event payloads (JSON-shaped); None when the step did not run.
    zoning_plan: dict | None = None
    zoning_report: dict | None = None
    zoning_rendered: dict | None = None      # {commands: {fabric: [..]}, aliases, selected_pairs}
    provisioning_plan: dict | None = None
    provisioning_result: dict | None = None
    provisioning_applied_at: str = ""
    path_verification: dict | None = None


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
    from alletra_onboard.application.documents.asbuilt_parse import parse_inventory  # local: avoid import cycle

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
    from alletra_onboard.application.documents.asbuilt_parse import parse_checkhealth  # local: avoid import cycle

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
            cpg_by_name = {r.get("Name", ""): r.get("UsrCPG", "") for r in parse_showvv(data.showvv_cpg)}
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
                   [[r.get("Name", ""), r.get("Prov", "—"), r.get("Dedup", "—"), r.get("Compr", "—"),
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


def _add_zoning_section(doc, data: AsBuiltData) -> None:
    _h1(doc, "SAN zoning designed in this run")
    plan = data.zoning_plan
    if not plan:
        _para(doc, "This run did not include the SAN zoning step.")
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
    report = data.zoning_report
    if report:
        zoned_hosts = report.get("zoned_hosts", [])
        unverified = report.get("unverified_hosts", [])
        _para(doc, "Zoning check on the array: "
                   + (f"zoned on both fabrics — {', '.join(zoned_hosts)}. " if zoned_hosts else "no host zoned on both fabrics. ")
                   + (f"Not verified — {', '.join(unverified)}." if unverified else ""))
    else:
        _para(doc, "The zoning check was not run.")


_OUTCOME_LABEL = {"created": "Created", "updated": "Updated", "exists": "Already existed", "failed": "Failed"}
_VERDICT_LABEL = {"live": "Live", "partial": "Partial", "no_path": "No path"}


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
               "was there and matched; 'Updated' means members or WWNs were added, nothing removed.")
    outcomes = result.get("outcomes", [])
    if outcomes:
        _table(doc, ["Kind", "Name", "Result", "Detail"],
               [[o.get("kind", ""), o.get("name", ""), _OUTCOME_LABEL.get(o.get("status", ""), o.get("status", "")),
                 o.get("detail") or "—"] for o in outcomes],
               widths=[0.10, 0.30, 0.18, 0.42])
    if result.get("error"):
        _para(doc, f"Provisioning stopped with an error: {result['error']}")
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
        _table(doc, ["Host", "Verdict", "Detail"],
               [[h.get("host", ""), _VERDICT_LABEL.get(h.get("verdict", ""), h.get("verdict", "")), h.get("detail", "")]
                for h in hosts],
               widths=[0.25, 0.15, 0.60])
    else:
        _para(doc, "No target hosts to verify.")


def _add_provisioned_sections(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-002: the five sections appended after the template's last section."""
    _add_hosts_section(doc, data, warnings)
    _add_volumes_section(doc, data, warnings)
    _add_presentations_section(doc, data, warnings)
    _add_zoning_section(doc, data)
    _add_provisioning_section(doc, data)


def _update_fields_on_open(doc) -> None:
    """R9: ask Word to refresh fields (the TOC, page numbers) when the document is opened."""
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        el = OxmlElement("w:updateFields")
        el.set(qn("w:val"), "true")
        settings.append(el)
