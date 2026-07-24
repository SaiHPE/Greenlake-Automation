"""As-built document generation (the 'Document' step — the LAST step after initialisation).

Generates the per-deployment as-built from **read-only** array facts (`show*` + `checkhealth`; no
writes, no switch login), rendered into HPE's house-style Word template so the output carries the HPE
logo / headers / footers / fonts.

Design (so no proprietary HPE artifact lands in this public repo):
  * The template is **not bundled here**. At runtime the generator loads HPE's house-style template
    (`HPE_Graphik_A4.dotx`, or any .docx/.dotx) from a path resolved by ``default_template()`` — an
    env var or a ``templates/`` folder the engineer populates once next to the app. If none is found,
    it renders a plain (unbranded) document, so it always works.
  * We keep the template's branding + styles + section (headers/footers), delete its instructional
    body ("delete all content and start typing", per the template itself), then add our content.

The content = what HPE's "Block Storage" as-built defines: the config table, inventory, checkhealth.
Parsing the raw `show*` text into ``AsBuiltData`` lives in ``asbuilt_parse.py`` (calibrated on a live dump).
"""

from __future__ import annotations

import io
import os
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import docx
from docx.shared import Pt

# Template Table-01 label -> AsBuiltData field, in the order HPE's Block-Storage as-built lists them.
_TABLE01_ROWS: list[tuple[str, str]] = [
    ("Name", "name"),
    ("Model", "model"),
    ("Serial No", "serial_no"),
    ("Controller Nodes", "controller_nodes"),
    ("OS Version", "os_version"),
    ("Drive Cages", "drive_cages"),
    ("Cache (GB)", "cache_gb"),
    ("NVMe SSD Disks", "nvme_ssd_disks"),
    ("RAW Capacity", "raw_capacity"),
    ("RAID", "raid"),
    ("Host Ports", "host_ports"),
    ("InServ IP Address", "mgmt_ip"),
    ("InServ Netmask Address", "netmask"),
    ("InServ Gateway Address", "gateway"),
    ("NTP", "ntp"),
    ("DNS Servers", "dns"),
]


@dataclass
class AsBuiltData:
    """The per-deployment values that fill the as-built (all from read-only array reads)."""

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
    inventory: str = ""     # showinventory, verbatim
    checkhealth: str = ""   # checkhealth -svc -detail, verbatim


def default_template() -> Path | None:
    """Resolve the house-style template WITHOUT bundling it in the repo: an explicit env var, else a
    ``templates/asbuilt_template.(dotx|docx)`` next to the app / cwd. None => render unbranded."""
    env = os.environ.get("ALLETRA_ASBUILT_TEMPLATE")
    if env and Path(env).is_file():
        return Path(env)
    bases = [Path.cwd()]
    if getattr(sys, "argv", None) and sys.argv[0]:
        bases.append(Path(sys.argv[0]).resolve().parent)
    for base in bases:
        for name in ("asbuilt_template.dotx", "asbuilt_template.docx"):
            cand = base / "templates" / name
            if cand.is_file():
                return cand
    return None


def _load_document(template: str | Path | None):
    """Open a .docx/.dotx as a python-docx Document (patching a .dotx content-type in memory so
    python-docx accepts it), or a blank document when no template is given."""
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


def _clear_body(doc) -> None:
    """Delete the template's instructional body (paragraphs + tables) but KEEP the final section
    properties (page setup + header/footer links) so the branding survives."""
    body = doc.element.body
    for child in list(body):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag in ("p", "tbl"):
            body.remove(child)


def _style(doc, name: str, fallback: str = "Normal") -> str:
    return name if name in [s.name for s in doc.styles] else fallback


def _mono(paragraph, text: str) -> None:
    lines = (text or "").splitlines() or ["(no output captured)"]
    for i, line in enumerate(lines):
        run = paragraph.add_run(line or " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8)
        if i < len(lines) - 1:
            run.add_break()


def generate_asbuilt(data: AsBuiltData, out_path: str | Path, *, template: str | Path | None = ...) -> Path:
    """Render the as-built to ``out_path``. ``template`` defaults to ``default_template()``; pass an
    explicit path/None to override (None = unbranded)."""
    if template is ...:
        template = default_template()
    doc = _load_document(template)
    _clear_body(doc)

    h1 = _style(doc, "Heading 1")
    title_style = _style(doc, "Title", "Heading 1")

    title = doc.add_paragraph(style=title_style)
    title.add_run(f"As-Built — HPE GreenLake for Block Storage\n{data.name or data.serial_no}".strip())

    doc.add_paragraph("Environment Overview", style=h1)
    doc.add_paragraph(
        f"This document is the as-built record for {data.name or 'the array'} "
        f"(model {data.model or '-'}, serial {data.serial_no or '-'}), management IP "
        f"{data.mgmt_ip or '-'}, running OS {data.os_version or '-'}. It is generated from a read-only "
        "read of the array's own configuration after initialisation.",
        style=_style(doc, "Normal"),
    )

    doc.add_paragraph("Alletra configuration", style=h1)
    doc.add_paragraph("Table 01 — hardware, capacity and network configuration.", style=_style(doc, "Normal"))
    table = doc.add_table(rows=0, cols=2)
    table.style = _style_table(doc)
    for label, field in _TABLE01_ROWS:
        cells = table.add_row().cells
        cells[0].text = label
        cells[1].text = getattr(data, field) or "-"

    doc.add_paragraph("Alletra Inventory", style=h1)
    _mono(doc.add_paragraph(style=_style(doc, "Normal")), data.inventory)

    doc.add_paragraph("Alletra MP checkhealth output", style=h1)
    _mono(doc.add_paragraph(style=_style(doc, "Normal")), data.checkhealth)

    out_path = Path(out_path)
    doc.save(str(out_path))
    return out_path


def _style_table(doc) -> str:
    for name in ("Table Grid", "Grid Table 4", "Light Grid"):
        if name in [s.name for s in doc.styles]:
            return name
    return "Normal Table"
