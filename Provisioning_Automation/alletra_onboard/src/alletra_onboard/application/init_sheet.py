"""The operator's single input: ``Initialisation_sheet.xlsx``.

It mirrors HPE's official "Initialization Worksheet" (so it's familiar to the engineer) and adds
a GreenLake-API section, so one filled workbook carries BOTH the workspace API credentials and
all per-array parameters. One workbook = one array.

``build_template_bytes()`` produces the blank template to hand the customer; ``parse_workbook_bytes()``
reads a filled one back into (GreenLake creds, ArrayWorkItem). The operator fills the **Value**
column only — the **Field** column is the stable key the parser matches on, so it must not be renamed.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig

SHEET_NAME = "Initialisation"
# The link-local cloudinit URL changes every boot, so it is NOT in the sheet — the operator pastes
# the fresh one in the Cloud Connectivity step. This placeholder keeps the work item valid until then.
DEFAULT_CLOUDINIT_URL = "https://169.254.0.0/cloudinit"
_HPE_GREEN = "01A982"

# section title -> list of (key, label, required, note). `key` is the stable identifier; `label`
# is what appears in the Field column (the parser strips a trailing " *" required marker).
SECTIONS: list[tuple[str, list[tuple[str, str, bool, str]]]] = [
    ("HPE GreenLake API access", [
        ("gl_client_id", "API Client ID", True, "GreenLake > Manage > API clients (create one)"),
        ("gl_client_secret", "API Client Secret", True, "shown once when you create the API client"),
        ("gl_token_url", "API Token URL", True, "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/<tenant>/token"),
    ]),
    ("Array (cloud enablement)", [
        ("serial_number", "Storage system serial number", True, "e.g. SGHD45FF0Y"),
        ("part_number", "Product number (SKU)", True, "product SKU e.g. S0B84A — NOT the box FRU"),
        ("subscription_key", "Subscription key", True, "GreenLake activation key from the ESD receipt email"),
        ("service_catalog_region_id", "Data Services region", True, "e.g. ap-northeast"),
        ("dscc_region_code", "DSCC region code", True, "e.g. jp1"),
    ]),
    ("Network", [
        ("mgmt_ipv4", "IP address", True, "array management IPv4 address"),
        ("mask", "Netmask", True, "e.g. 255.255.248.0"),
        ("gateway", "Gateway", True, ""),
        ("dns1", "DNS server 1", True, ""),
        ("dns2", "DNS server 2", False, "optional"),
        ("dns3", "DNS server 3", False, "optional"),
        ("ntp", "Time (NTP) server", True, "must keep array time within 2 minutes of correct"),
        ("timezone", "Timezone", True, "e.g. Asia/Kolkata"),
        ("proxy_host", "HTTP proxy server", False, "leave blank for no proxy"),
        ("proxy_port", "HTTP proxy port", False, "e.g. 8080"),
    ]),
    ("DSCC Setup — Support Contact", [
        ("contact_first_name", "First name", True, ""),
        ("contact_last_name", "Last name", True, ""),
        ("contact_language", "Preferred language", True, "e.g. English"),
        ("contact_company", "Company", True, ""),
        ("contact_phone", "Phone number", True, ""),
        ("contact_email", "Contact email", True, ""),
    ]),
    ("DSCC Setup — System", [
        ("dscc_system_name", "System name", True, "the name DSCC will show for this array"),
        ("dscc_country", "System country location", True, "e.g. India"),
    ]),
    ("DSCC Setup — System Credentials", [
        ("secret_name", "Credential name", True, "e.g. b10000-admin"),
        ("secret_username", "Administrator name", True, "e.g. 3paradm — you enter the PASSWORD in the DSCC wizard, not here"),
    ]),
]

_LABEL_TO_KEY = {label: key for _, fields in SECTIONS for key, label, _, _ in fields}
_REQUIRED = [key for _, fields in SECTIONS for key, _, required, _ in fields if required]
_KEY_TO_LABEL = {key: label for _, fields in SECTIONS for key, label, _, _ in fields}


@dataclass
class ParsedInitSheet:
    work_item: ArrayWorkItem
    gl_client_id: str
    gl_client_secret: str
    gl_token_url: str


def _normalize_label(text: str) -> str:
    return text.strip().removesuffix("*").strip()


def build_template_bytes() -> bytes:
    """A blank Initialisation_sheet.xlsx: Field | Value | Notes, grouped by section."""
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME
    ws.append(["Field", "Value", "Notes / example"])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    header_fill = PatternFill("solid", fgColor=_HPE_GREEN)
    for section, fields in SECTIONS:
        row = ws.max_row + 1
        for col in (1, 2, 3):
            cell = ws.cell(row=row, column=col, value=section if col == 1 else None)
            cell.fill = header_fill
            cell.font = Font(bold=True, color="FFFFFF")
        for key, label, required, note in fields:
            display = f"{label} *" if required else label
            ws.append([display, "", note])
            ws.cell(row=ws.max_row, column=3).font = Font(italic=True, color="808080")

    ws.column_dimensions["A"].width = 36
    ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 64
    for row in ws.iter_rows():
        row[1].alignment = Alignment(wrap_text=False)
    ws.freeze_panes = "A2"

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def parse_workbook_bytes(data: bytes) -> ParsedInitSheet:
    """Read a filled Initialisation_sheet.xlsx back into (GreenLake creds, ArrayWorkItem)."""
    workbook = load_workbook(io.BytesIO(data), data_only=True)
    sheet = workbook[SHEET_NAME] if SHEET_NAME in workbook.sheetnames else workbook.active

    values: dict[str, str] = {}
    for row in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
        label = row[0]
        value = row[1] if len(row) > 1 else None
        if label is None or value is None:
            continue
        key = _LABEL_TO_KEY.get(_normalize_label(str(label)))
        text = str(value).strip()
        if key and text:
            values[key] = text
    return _build(values)


def _build(values: dict[str, str]) -> ParsedInitSheet:
    missing = [_KEY_TO_LABEL[key] for key in _REQUIRED if not values.get(key)]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))

    dns = [values[key] for key in ("dns1", "dns2", "dns3") if values.get(key)]
    network = NetworkConfig(
        mgmt_ipv4=values["mgmt_ipv4"],
        mask=values["mask"],
        gateway=values["gateway"],
        dns=dns,
        ntp=values["ntp"],
        timezone=values["timezone"],
        proxy_host=values.get("proxy_host") or None,
        proxy_port=int(float(values["proxy_port"])) if values.get("proxy_port") else None,
    )
    dscc_setup = DsccSetupConfig(
        system_name=values["dscc_system_name"],
        country=values["dscc_country"],
        credential_name=values.get("secret_name") or "b10000-admin",
        username=values.get("secret_username") or "3paradm",
        password=values.get("secret_password") or None,
        contact_first_name=values.get("contact_first_name"),
        contact_last_name=values.get("contact_last_name"),
        contact_language=values.get("contact_language") or "English",
        contact_company=values.get("contact_company"),
        contact_phone=values.get("contact_phone"),
        contact_email=values.get("contact_email"),
    )
    work_item = ArrayWorkItem(
        serial_number=values["serial_number"],
        part_number=values["part_number"],
        subscription_key=values["subscription_key"],
        service_catalog_region_id=values["service_catalog_region_id"],
        dscc_region_code=values["dscc_region_code"],
        cloudinit_url=values.get("cloudinit_url") or DEFAULT_CLOUDINIT_URL,
        network=network,
        dscc_setup=dscc_setup,
    )
    return ParsedInitSheet(
        work_item=work_item,
        gl_client_id=values["gl_client_id"],
        gl_client_secret=values["gl_client_secret"],
        gl_token_url=values["gl_token_url"],
    )
