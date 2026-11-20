"""The operator's single input: ``Initialisation_sheet.xlsx``.

It mirrors HPE's official "Initialization Worksheet" (so it's familiar to the engineer) and adds
a GreenLake-API section, so one filled workbook carries BOTH the workspace API credentials and
all per-array parameters. One workbook = one array.

``build_template_bytes()`` produces the blank template to hand the customer; ``parse_workbook_bytes()``
reads a filled one back into (GreenLake creds, ArrayWorkItem). The operator fills the **Value**
column only — the **Field** column is the stable key the parser matches on, so it must not be renamed.
"""

from __future__ import annotations

import datetime
import io
import ipaddress
import re
import zipfile
from dataclasses import dataclass

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from pydantic import SecretStr

from alletra_onboard.application.platform import prereqs
from alletra_onboard.domain.migration import (
    MIGRATION_PROVISIONING,
    MIGRATION_TYPES,
    MigrationHostRequest,
    MigrationIntent,
)
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, RunMode
from alletra_onboard.domain.network import IscsiVlanRequest
from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSetRequest,
    ProvisioningIntent,
    VolumeRequest,
    volume_name_problem,
    volume_set_name_problem,
    volume_too_large,
)
from alletra_onboard.domain.replication import (
    RPO_MINUTES_DEFAULT,
    RPO_MINUTES_MIN,
    ProtectionRequest,
    RcipPortRequest,
    ReplicationIntent,
    pair_ports,
    rtt_limit_ms,
    rtt_limit_text,
)
from alletra_onboard.domain.shared import EndpointCreds, normalize_wwpn
from alletra_onboard.domain.snapshots import (
    ALLOWED_EVERY,
    HOURS_MAX,
    SCHEDULE_NAME_MAX,
    SNAPSHOTS_TAB_NEEDED,
    SnapshotIntent,
    SnapshotRequest,
)
from alletra_onboard.domain.workflow import enabled_steps

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
    ("As-built document", [
        ("customer_name", "Customer name", False, "goes on the as-built cover page (the array doesn't store it)"),
        ("site", "Site / location", False, "deployment site/location for the as-built (optional)"),
        ("application_workload", "Application / workload", False, "e.g. VMware vSphere cluster — names the workload in the as-built (optional)"),
        ("storage_purpose", "Purpose of using Block storage", False, "e.g. primary datastore for the vault zone (optional)"),
    ]),
]

_LABEL_TO_KEY = {label: key for _, fields in SECTIONS for key, label, _, _ in fields}
_KEY_TO_LABEL = {key: label for _, fields in SECTIONS for key, label, _, _ in fields}

# Decoupling: which sheet fields each step actually needs. A run's mode -> enabled steps -> the
# union of these is what we validate, so a verify-only / provision-only sheet isn't forced to carry
# GreenLake creds or DSCC contact details. serial_number is always required (it names the run).
_ALWAYS_REQUIRED: tuple[str, ...] = ("serial_number",)
_STEP_REQUIRES: dict[str, tuple[str, ...]] = {
    "greenlake": (
        "gl_client_id", "gl_client_secret", "gl_token_url",
        "part_number", "subscription_key", "service_catalog_region_id",
    ),
    "cloudinit": ("mgmt_ipv4", "mask", "gateway", "dns1", "ntp", "timezone"),
    "dscc": (
        "dscc_region_code",
        "contact_first_name", "contact_last_name", "contact_language",
        "contact_company", "contact_phone", "contact_email",
        "dscc_system_name", "dscc_country", "secret_name", "secret_username",
    ),
    # Provisioning steps validate against the separate 'Provisioning' tab (parsed below), so they
    # add no Initialisation-tab requirements beyond the always-required serial. Verify reuses the
    # onboarded network values, so it needs the array IP from the Initialisation tab.
    "discover": (),
    "ports": (),
    "zoning": (),
    "provision": (),
    # Replication steps need the Replication tab (checked when the run is minted), nothing more here.
    "replicate": (),
    "failover_test": (),
    # The Migration step needs the Migration tab (checked when the run is minted), nothing more here.
    "migrate": (),
    # The Snapshots step needs the Snapshots tab (checked when the run is minted), nothing more here.
    "snapshots": (),
    "verify": ("mgmt_ipv4",),
}

# The provisioning input (Phase 2 / ADR 0010 Stage 2) spans THREE fillable tabs, parsed only when a
# provisioning step is selected: 'Provisioning' carries the device targets (with passwords —
# customer-supplied) + defaults; 'Volumes' and 'Host sets' are ROW-TABLES (one object per row) so a
# run can create a plural/heterogeneous set of volumes and one or more host sets. The exports
# (which source is presented to which target, at which LUN) are composed later in the operator's
# dropdown builder over discovered + to-be-created objects — they are not in the sheet.
PROVISIONING_SHEET_NAME = "Provisioning"
VOLUMES_SHEET_NAME = "Volumes"
HOSTSETS_SHEET_NAME = "Host sets"
HOSTS_SHEET_NAME = "Hosts"

PROVISIONING_SECTIONS: list[tuple[str, list[tuple[str, str, bool, str]]]] = [
    ("Targets — array", [
        ("prov_array_host", "Array management IP", True, "the B10000 mgmt IP (WSAPI + SSH)"),
        ("prov_array_user", "Array admin username", True, "e.g. 3paradm"),
        ("prov_array_password", "Array admin password", True, "used for WSAPI + SSH this run"),
    ]),
    ("Targets — vCenter", [
        ("prov_vcenter_host", "vCenter host or IP", True, "for read-only ESXi HBA discovery"),
        ("prov_vcenter_user", "vCenter username", True, "e.g. administrator@vsphere.local"),
        ("prov_vcenter_password", "vCenter password", True, ""),
    ]),
    ("Targets — SAN switches (dual fabric) — needed for the SAN Zoning step (read-only)", [
        ("prov_sw1_host", "Switch 1 — odd / F1 — IP", False, "read-only account is enough; required for SAN Zoning"),
        ("prov_sw1_user", "Switch 1 username", False, "e.g. admin — the tool only READS the switch"),
        ("prov_sw1_password", "Switch 1 password", False, ""),
        ("prov_sw2_host", "Switch 2 — even / F2 — IP", False, "read-only account is enough; required for SAN Zoning"),
        ("prov_sw2_user", "Switch 2 username", False, "e.g. admin — the tool only READS the switch"),
        ("prov_sw2_password", "Switch 2 password", False, ""),
    ]),
    ("Defaults — used when a Volumes row leaves CPG / Type blank (optional)", [
        ("prov_default_cpg", "Default CPG", False, "default SSD_r6"),
        ("prov_default_type", "Default provisioning type", False, "tpvv (thin) or reduce (dedup+compress); default tpvv"),
    ]),
]

# Row-table columns for the Volumes / Host sets tabs: (key, header, required).
VOLUME_COLUMNS: list[tuple[str, str, bool]] = [
    ("name", "Volume name", True),
    ("size_gib", "Size (GiB)", True),
    ("provisioning_type", "Type (tpvv / reduce)", False),
    ("cpg", "CPG", False),
    ("vvset", "VV-set (optional)", False),
]
HOSTSET_COLUMNS: list[tuple[str, str, bool]] = [
    ("name", "Host set name", True),
    ("members", "Members — comma-separated host names; blank = choose in the app's Compose step", False),
]
# The hosts the run is for. A row with only a name (and IP) is looked up by discovery (SPEC-014 R1);
# WWPN/IQN are typed only for a server no source can see yet.
HOSTS_COLUMNS: list[tuple[str, str, bool]] = [
    ("name", "Host name", True),
    ("os", "OS (esxi / windows / linux / vme)", False),
    ("address", "IP address (optional)", False),
    ("wwpns", "FC WWPN(s) — comma-separated; blank if none", False),
    ("iqn", "iSCSI IQN — blank if none", False),
    ("username", "Login username (optional) — Linux SSH / Windows WinRM, read-only", False),
    ("password", "Login password (optional)", False),
]

_PROV_LABEL_TO_KEY = {label: key for _, fields in PROVISIONING_SECTIONS for key, label, _, _ in fields}
_PROV_KEY_TO_LABEL = {key: label for _, fields in PROVISIONING_SECTIONS for key, label, _, _ in fields}
_PROV_REQUIRED = [key for _, fields in PROVISIONING_SECTIONS for key, _, required, _ in fields if required]

# The Replication tab (SPEC-015): ONE optional tab, key/value sections on top (the peer array, the
# measured RTT, the failover test) and a Protection row-table beneath (one Remote Copy group per
# row). Direction is always this run's array -> the peer.
REPLICATION_SHEET_NAME = "Replication"
REPLICATION_SECTIONS: list[tuple[str, list[tuple[str, str, bool, str]]]] = [
    ("Peer array — the array this one replicates TO (the Replication network tab sets up the partnership; leave it blank if one exists)", [
        ("peer_host", "Peer array management IP", True, "the other B10000's mgmt IP (WSAPI + SSH)"),
        ("peer_user", "Peer array admin username", True, "e.g. 3paradm"),
        ("peer_password", "Peer array admin password", True, "used for WSAPI + SSH on the peer this run"),
    ]),
    ("Replication network", [
        ("rtt_ms", "Measured round-trip time (ms)", False,
         "optional — the Replication step measures RCIP links itself (checkrclink); sync needs 10 ms or less, async over RCIP 200 ms"),
    ]),
    ("Failover test", [
        ("failover_test", "Run the failover test (yes / no)", False, "default yes — on the tool's own 1 GiB test group"),
        ("failover_group", "Failover test group", False, "blank = the tool's own test group; a production group needs a typed confirmation in the app"),
    ]),
]
PROTECTION_COLUMNS: list[tuple[str, str, bool]] = [
    ("vvset", "Volume set", True),
    ("mode", "Mode (async / sync)", False),
    ("rpo_minutes", "RPO (minutes, async only)", False),
    ("peer_cpg", "Peer CPG", True),
    ("peer_vvset", "Peer volume set (optional)", False),
    ("auto_synchronize", "Auto synchronize (yes / no)", False),
    ("auto_recover", "Auto recover (yes / no)", False),
]
# SPEC-021 R1: the RCIP ports the tool sets up, one row per port, on this array or the peer.
REPLICATION_NETWORK_SHEET_NAME = "Replication network"
NETWORK_COLUMNS: list[tuple[str, str, bool]] = [
    ("array", "Array (this / peer)", True),
    ("port", "Port (N:S:P)", True),
    ("ip", "RCIP address", True),
    ("netmask", "Netmask", True),
    ("gateway", "Gateway (optional)", False),
]
# SPEC-024 R1: VLAN-tagged iSCSI addresses the tool adds to this array's iSCSI ports, one row per port and VLAN.
ISCSI_NETWORK_SHEET_NAME = "iSCSI network"
ISCSI_NETWORK_COLUMNS: list[tuple[str, str, bool]] = [
    ("port", "Port (N:S:P)", True),
    ("vlan", "VLAN ID", True),
    ("ip", "iSCSI address", True),
    ("netmask", "Netmask", True),
    ("gateway", "Gateway (optional)", False),
]
# SPEC-025 R1: free FC ports of this array to set to peer mode for a migration, one row per port.
PEER_PORTS_SHEET_NAME = "Peer ports"
PEER_PORT_COLUMNS: list[tuple[str, str, bool]] = [
    ("port", "Port (N:S:P)", True),
    ("source_wwpns", "Source array ports to zone (WWPNs)", False),
]
_REPL_LABEL_TO_KEY = {label: key for _, fields in REPLICATION_SECTIONS for key, label, _, _ in fields}
_REPL_KEY_TO_LABEL = {key: label for _, fields in REPLICATION_SECTIONS for key, label, _, _ in fields}
_REPL_REQUIRED = [key for _, fields in REPLICATION_SECTIONS for key, _, required, _ in fields if required]
_UNSUPPORTED_REPLICATION_TYPES = ("peer persistence", "active sync", "sld", "3dc", "streaming", "app")

# The Migration tab (SPEC-027 R1): ONE optional tab, key/value sections on top (the source array, where
# the import runs) and one row per host to migrate beneath. The run's array is the destination; the
# source is only read. Name, model, serial and OS of the source are read from it, never asked.
MIGRATION_SHEET_NAME = "Migration"
MIGRATION_SECTIONS: list[tuple[str, list[tuple[str, str, bool, str]]]] = [
    ("Source array — the array the data moves FROM (the tool only reads it)", [
        ("source_host", "Source array management address", True,
         "the 3PAR, Primera or Alletra 9000 the hosts move from; not this run's array"),
        ("source_user", "Source array user", True,
         "a read-only account is enough for this tool; Peer Motion asks for its own account in the array UI or DSCC"),
        ("source_password", "Source array password", True, "used only to read the source array"),
    ]),
    ("Orchestration", [
        ("orchestration", "Where the import runs (array UI / DSCC)", False,
         "default array UI (this array's own UI); DSCC needs a newer OS on this array for a Primera or Alletra 9000 source"),
    ]),
]
MIGRATION_HOST_COLUMNS: list[tuple[str, str, bool]] = [
    ("host", "Host (its name on the source array)", True),
    ("type", "Migration type (online / minimally disruptive / offline)", False),
    ("cpg", "Destination CPG", True),
    ("provisioning", "Provisioning (thin / reduce)", False),
]
_MIG_LABEL_TO_KEY = {label: key for _, fields in MIGRATION_SECTIONS for key, label, _, _ in fields}
# What an operator may type for each list value; the key is the normalised text (lower case, single
# spaces, '-' and '_' read as spaces).
_MIGRATION_TYPE_WORDS: dict[str, str] = {
    "online": "online", "minimally disruptive": "minimally disruptive", "mdm": "minimally disruptive",
    "offline": "offline",
}
_MIGRATION_PROVISIONING_WORDS: dict[str, str] = {"thin": "thin", "tpvv": "thin", "reduce": "reduce"}
_ORCHESTRATION_WORDS: dict[str, str] = {"array ui": "array UI", "array": "array UI", "dscc": "DSCC"}

# The Snapshots tab (SPEC-023 R1): one row per volume set (or volume), a snapshot now and/or a
# schedule. A tab, not columns on the Volumes tab: a schedule protects a set, and a row may name a set
# that is already on the array.
SNAPSHOTS_SHEET_NAME = "Snapshots"
SNAPSHOT_COLUMNS: list[tuple[str, str, bool]] = [
    ("source", "Volume set or volume", True),
    ("kind", "Kind (set / volume)", False),
    ("snapshot_now", "Snapshot now (yes / no)", False),
    ("every", "Every", False),
    ("unit", "Unit (minutes / hours / days)", False),
    ("at_hour", "Start hour (0-23, array time)", False),
    ("days", "Days (blank = every day)", False),
    ("expire_hours", "Keep for (hours)", True),
    ("retain_hours", "Lock for (hours, optional)", False),
    ("read_only", "Read-only (yes / no)", False),
    ("schedule_name", "Schedule name (optional)", False),
]
_DAY_NUMBERS = {
    name: number
    for number, full in enumerate(("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"))
    for name in (full, full[:3])
}
_UNITS = {"minute": "minutes", "minutes": "minutes", "hour": "hours", "hours": "hours", "day": "days", "days": "days"}
_SCHEDULE_NAME = re.compile(rf"[A-Za-z0-9._-]{{1,{SCHEDULE_NAME_MAX}}}")
#: `help createsched` / `help removesched`: names the array keeps for itself.
_RESERVED_SCHEDULE_NAMES = ("all", "upgrade")


def required_keys_for(mode: RunMode, selected_steps: list[str] | None = None) -> set[str]:
    """The sheet field keys a run of this mode must have filled."""
    keys = set(_ALWAYS_REQUIRED)
    for step in enabled_steps(mode, selected_steps):
        keys.update(_STEP_REQUIRES.get(step.key, ()))
    return keys


def all_required_keys() -> set[str]:
    """Every main-tab field a COMPLETE sheet must have — the union across all steps, mode-independent.
    RunMode.BOTH enables the whole step registry, so its required set is the full superset. The upload
    validates against this (see ADR 0005 revision): the sheet is filled once, in full, BEFORE a mode
    is chosen, so an incomplete sheet is rejected regardless of the intent picked later."""
    return required_keys_for(RunMode.BOTH)


@dataclass
class ParsedInitSheet:
    work_item: ArrayWorkItem
    gl_client_id: str
    gl_client_secret: str
    gl_token_url: str
    provisioning_intent: ProvisioningIntent | None = None  # set when a provisioning step is selected
    customer_name: str = ""  # for the as-built cover page (operator-supplied; not on the array)
    site: str = ""


def _provisioning_selected(mode: RunMode, selected_steps: list[str] | None) -> bool:
    return any(step.kind in ("provision", "replicate", "migrate", "snapshot") for step in enabled_steps(mode, selected_steps))


def _replication_selected(mode: RunMode, selected_steps: list[str] | None) -> bool:
    return any(step.kind == "replicate" for step in enabled_steps(mode, selected_steps))


def _migration_selected(mode: RunMode, selected_steps: list[str] | None) -> bool:
    return any(step.kind == "migrate" for step in enabled_steps(mode, selected_steps))


def _snapshots_selected(mode: RunMode, selected_steps: list[str] | None) -> bool:
    return any(step.kind == "snapshot" for step in enabled_steps(mode, selected_steps))


def _normalize_label(text: str) -> str:
    return text.strip().removesuffix("*").strip()


def _column_key(text: str) -> str:
    """A row-table header reduced to its leading phrase: `Members — comma-separated …` -> `members`,
    `Size (GiB) *` -> `size`. The explanatory tail after " — " or " (" is guidance for the operator
    and changes between template revisions; matching on it silently dropped a whole column when it
    did (P-17, 2026-09-14: rc.10 renamed the Members hint and every existing sheet lost its members)."""
    head = _normalize_label(text)
    for sep in (" — ", " - ", " ("):
        if sep in head:
            head = head.split(sep, 1)[0]
    return " ".join(head.lower().split())


def _write_fillable_tab(ws, sections: list[tuple[str, list[tuple[str, str, bool, str]]]]) -> None:
    """Write a Field | Value | Notes tab grouped by section header (the operator fills Value)."""
    ws.append(["Field", "Value", "Notes / example"])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    header_fill = PatternFill("solid", fgColor=_HPE_GREEN)
    for section, fields in sections:
        row = ws.max_row + 1
        for col in (1, 2, 3):
            cell = ws.cell(row=row, column=col, value=section if col == 1 else None)
            cell.fill = header_fill
            cell.font = Font(bold=True, color="FFFFFF")
        for _key, label, required, note in fields:
            display = f"{label} *" if required else label
            ws.append([display, "", note])
            ws.cell(row=ws.max_row, column=3).font = Font(italic=True, color="808080")

    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 42
    ws.column_dimensions["C"].width = 64
    for row in ws.iter_rows():
        row[1].alignment = Alignment(wrap_text=False)
    ws.freeze_panes = "A2"


def build_template_bytes(*, init_only: bool = False) -> bytes:
    """A blank Initialisation_sheet.xlsx: Initialisation (fillable) + Prerequisites, plus the
    Provisioning tab unless ``init_only`` (the Initialization accelerator ships an onboarding-only
    sheet — no array/vCenter/switch credentials)."""
    wb = Workbook()
    ws = wb.active or wb.create_sheet()
    ws.title = SHEET_NAME
    _write_fillable_tab(ws, SECTIONS)

    if not init_only:
        _add_provisioning_sheet(wb)
        _add_replication_sheet(wb)
        _add_replication_network_sheet(wb)
        _add_iscsi_network_sheet(wb)
        _add_peer_ports_sheet(wb)
        _add_migration_sheet(wb)
        _add_snapshots_sheet(wb)
    _add_prereq_sheet(wb)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _write_table_tab(ws, columns: list[tuple[str, str, bool]], *, blank_rows: int, intro: str) -> None:
    """Write a ROW-TABLE: an intro line, a bold header row (one column per field), then blank rows
    the operator fills — one object per row (ADR 0010 Stage 2). Appends below whatever the sheet
    already holds (the Replication tab puts it under its key/value sections)."""
    ws.append([intro])
    ws.cell(row=ws.max_row, column=1).font = Font(italic=True, color="808080")

    header_fill = PatternFill("solid", fgColor=_HPE_GREEN)
    header = [f"{label} *" if required else label for _key, label, required in columns]
    ws.append(header)
    header_row = ws.max_row
    for cell in ws[header_row]:
        cell.fill = header_fill
        cell.font = Font(bold=True, color="FFFFFF")

    # Materialise blank rows as a bordered, fillable grid (append([None,...]) creates no cells, so the
    # operator would otherwise see just a header with nowhere obvious to type).
    thin = Side(style="thin", color="D0D0D0")
    grid = Border(left=thin, right=thin, top=thin, bottom=thin)
    for r in range(header_row + 1, header_row + 1 + blank_rows):
        for c in range(1, len(columns) + 1):
            ws.cell(row=r, column=c).border = grid

    for i, (_key, label, _required) in enumerate(columns, start=1):
        ws.column_dimensions[ws.cell(row=header_row, column=i).column_letter].width = max(20, len(label) + 4)
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1).coordinate


def _add_provisioning_sheet(wb: Workbook) -> None:
    """The fillable provisioning input — parsed only when a provisioning step is selected: the
    'Provisioning' tab (targets + defaults) plus the 'Volumes' and 'Host sets' row-tables."""
    _write_fillable_tab(wb.create_sheet(PROVISIONING_SHEET_NAME), PROVISIONING_SECTIONS)
    _write_table_tab(
        wb.create_sheet(VOLUMES_SHEET_NAME), VOLUME_COLUMNS, blank_rows=15,
        intro="Volumes to create — one per row. Type/CPG blank = the Provisioning-tab defaults.",
    )
    _write_table_tab(
        wb.create_sheet(HOSTS_SHEET_NAME), HOSTS_COLUMNS, blank_rows=10,
        intro=(
            "The hosts this run is for. Name + OS + IP is enough: discovery looks each one up (vCenter "
            "by name/IP, the array by host name, iSCSI login IP or IQN) and fills in its serial, WWPNs "
            "and IQN. For a Linux or Windows host, add a login and discovery reads them from the server "
            "itself (read-only): Linux over SSH (serial and multipath need root or passwordless sudo), "
            "Windows over WinRM 5985/5986 with a local administrator login. "
            "Type the WWPN/IQN only for a server nothing can see yet: "
            "Windows 'Get-InitiatorPort'; Linux 'cat /etc/iscsi/initiatorname.iscsi' for the IQN and "
            "'cat /sys/class/fc_host/host*/port_name' for the WWPN; ESXi 'esxcli storage san fc list'."
        ),
    )
    _write_table_tab(
        wb.create_sheet(HOSTSETS_SHEET_NAME), HOSTSET_COLUMNS, blank_rows=8,
        intro="Host sets to create — one per row. Leave Members blank to include all discovered hosts.",
    )


def _add_replication_sheet(wb: Workbook) -> None:
    """The optional 'Replication' tab (SPEC-015 R1): key/value sections, then the Protection row-table
    on the SAME tab. `_read_tab` matches the labels and ignores the table; `_read_table` finds the
    header by its 'Volume set' column and ignores the sections above it."""
    ws = wb.create_sheet(REPLICATION_SHEET_NAME)
    _write_fillable_tab(ws, REPLICATION_SECTIONS)
    ws.append([])
    _write_table_tab(
        ws, PROTECTION_COLUMNS, blank_rows=8,
        intro=(
            "Volume sets to protect — one Remote Copy group per row, from THIS array to the peer. "
            "Mode blank = async; RPO blank = 10 minutes (the array period is RPO / 2); Peer volume set "
            "blank = '<set>_rc'; policies blank = yes. Only async and sync are supported in this version."
        ),
    )
    # _write_table_tab sized the first columns for the table; widen column A for the labels above it.
    ws.column_dimensions["A"].width = 44
    ws.freeze_panes = "A2"


def _add_replication_network_sheet(wb: Workbook) -> None:
    """SPEC-021 R1: the optional 'Replication network' tab. Blank -> the partnership must exist already."""
    ws = wb.create_sheet(REPLICATION_NETWORK_SHEET_NAME)
    _write_table_tab(
        ws, NETWORK_COLUMNS, blank_rows=8,
        intro=(
            "Fill this only when the tool should set up the replication ports and the partnership. One row per "
            "RCIP port: Array 'this' (the array of this run) or 'peer'. Ports pair node to node (this array's "
            "node-0 port with the peer's node-0 port). Leave Gateway blank when both arrays are on one network."
        ),
    )
    for row in ws.iter_rows(min_row=ws.max_row - 8, max_row=ws.max_row, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = "@"          # text: Excel would turn 0:4:4 into a time


def _add_migration_sheet(wb: Workbook) -> None:
    """The optional 'Migration' tab (SPEC-027 R1): key/value sections, then the hosts to migrate on the
    SAME tab, read the way the Replication tab is (labels above, the table found by its 'Host' column)."""
    ws = wb.create_sheet(MIGRATION_SHEET_NAME)
    _write_fillable_tab(ws, MIGRATION_SECTIONS)
    ws.append([])
    _write_table_tab(
        ws, MIGRATION_HOST_COLUMNS, blank_rows=8,
        intro=(
            "Hosts to migrate — one per row, named as on the SOURCE array. Migration type blank = online; "
            "Provisioning blank = thin. The tool reads the source array and checks it is ready; Peer Motion, "
            "in this array's UI or DSCC, does the import. The tool never writes to the source array."
        ),
    )
    ws.column_dimensions["A"].width = 44
    ws.freeze_panes = "A2"


def _add_snapshots_sheet(wb: Workbook) -> None:
    """SPEC-023 R1: the optional 'Snapshots' tab. Blank -> no Snapshots step."""
    _write_table_tab(
        wb.create_sheet(SNAPSHOTS_SHEET_NAME), SNAPSHOT_COLUMNS, blank_rows=8,
        intro=(
            "Fill this only when the tool should take snapshots. One row per volume set (or volume, with Kind "
            "'volume'): Snapshot now takes one read-only snapshot of each volume, named <volume>.initial; Every "
            "and Unit set up a schedule on the array (15, 20 or 30 minutes; 1, 2, 3, 4, 6, 8 or 12 hours; 1 day). "
            "Keep for is how long each snapshot lives. Start hour and Days are in the array's own time. "
            "A schedule keeps taking snapshots after the run ends, until someone removes it."
        ),
    )


def _add_iscsi_network_sheet(wb: Workbook) -> None:
    """SPEC-024 R1: the optional 'iSCSI network' tab. Blank -> the Array ports step has nothing to do."""
    ws = wb.create_sheet(ISCSI_NETWORK_SHEET_NAME)
    _write_table_tab(
        ws, ISCSI_NETWORK_COLUMNS, blank_rows=8,
        intro=(
            "Fill this only when the tool should add VLAN-tagged iSCSI addresses to this array's iSCSI ports. "
            "One row per port and VLAN. Put each VLAN on a port of both nodes. The switch ports are not changed "
            "by the tool."
        ),
    )
    for row in ws.iter_rows(min_row=ws.max_row - 7, max_row=ws.max_row, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = "@"          # text: Excel would turn 0:4:1 into a time


def _add_peer_ports_sheet(wb: Workbook) -> None:
    """SPEC-025 R1: the optional 'Peer ports' tab. Blank -> the Array ports step has no peer ports to set."""
    ws = wb.create_sheet(PEER_PORTS_SHEET_NAME)
    _write_table_tab(
        ws, PEER_PORT_COLUMNS, blank_rows=8,
        intro=(
            "Fill this only when a data migration needs peer ports: free Fibre Channel ports of this array set to peer "
            "mode. One row per port, at least one port on each of two nodes. Source array ports: the WWPNs of the "
            "source array's ports to zone to this port, separated by spaces or commas. The switches are not changed "
            "by the tool."
        ),
    )
    for row in ws.iter_rows(min_row=ws.max_row - 7, max_row=ws.max_row, min_col=1, max_col=1):
        for cell in row:
            cell.number_format = "@"          # text: Excel would turn 0:3:2 into a time


def _add_prereq_sheet(wb: Workbook) -> None:
    """A reference 'Prerequisites' tab: firewall rules to open + a short readiness checklist.

    The parser ignores this tab (it only reads the 'Initialisation' sheet), so it is documentation
    only. The firewall list is the same single source used by the app and the downloadable .txt.
    """
    ws = wb.create_sheet("Prerequisites")
    header_fill = PatternFill("solid", fgColor=_HPE_GREEN)

    def band(text: str) -> None:
        ws.append([text, None, None])
        for col in (1, 2, 3):
            cell = ws.cell(row=ws.max_row, column=col)
            cell.fill = header_fill
            cell.font = Font(bold=True, color="FFFFFF")

    def note(text: str) -> None:
        ws.append([text, None, None])
        ws.cell(row=ws.max_row, column=1).font = Font(italic=True, color="808080")

    ws.append(["Prerequisites — complete before onboarding"])
    ws.cell(row=1, column=1).font = Font(bold=True, size=13)

    band("Firewall — open these OUTBOUND rules (send to your network team)")
    ws.append(["Destination (FQDN)", "Port", "Purpose"])
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
    for fqdn, port, _initiator, purpose in prereqs.rules_for("<instance>"):
        ws.append([fqdn, port, purpose])
    note("<instance> = your DSCC region (e.g. jp1).  Also required: mDNS UDP 5353 for local discovery.")
    note("Reserved — do NOT assign these: " + ", ".join(prereqs.RESERVED_IPS) + " (CDM link-local).")

    band("Management-network cabling (each controller → management switch)")
    for item in (
        "Admin port — each controller → management LAN switch (cable ALL controllers; the shared IP fails over).",
        "iLO port — each controller → the same management network (out-of-band management).",
        "CDM Ethernet port — each controller chassis (OCuLink-to-Ethernet dongle) + at least one drive chassis per rack.",
    ):
        ws.append([item, None, None])

    band("Account, network & time")
    for item in (
        "HPE GreenLake account + workspace; Data Services deployed; Administrator role assigned.",
        "Personal API client created (Client ID / Secret / token URL) — enter these on the Initialisation tab.",
        "Array DNS resolves the global names above; system time within 2 minutes of correct.",
        "Onboarding jump box on the same subnet as the array (for the 169.254.x Cloud Connectivity URL).",
    ):
        ws.append([item, None, None])

    band("Reference")
    ws.append(["HPE Alletra Storage MP B10000 — Network requirement details (Planning / install guide, sd00002405)."])

    ws.column_dimensions["A"].width = 64
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 44


def parse_workbook_bytes(
    data: bytes,
    *,
    mode: RunMode = RunMode.FULL_ONBOARDING,
    selected_steps: list[str] | None = None,
    complete: bool = False,
) -> ParsedInitSheet:
    """Read a filled Initialisation_sheet.xlsx back into (GreenLake creds, ArrayWorkItem).

    ``complete=True`` (the upload path, ADR 0005 revision) validates the FULL superset and always
    parses the Provisioning tab — the sheet is filled once, in full, before a mode is chosen. Passing
    a ``mode`` instead scopes validation to that mode's fields (used where a mode is already known).
    """
    workbook = load_workbook(io.BytesIO(data), data_only=True)
    sheet = workbook[SHEET_NAME] if SHEET_NAME in workbook.sheetnames else workbook.active

    values = _read_tab(sheet, _LABEL_TO_KEY)
    required = all_required_keys() if complete else required_keys_for(mode, selected_steps)
    parsed = _build(values, required)

    if complete or _provisioning_selected(mode, selected_steps):
        volumes_required = complete or any(s.key == "provision" for s in enabled_steps(mode, selected_steps))
        parsed.provisioning_intent = _parse_provisioning_tab(workbook, volumes_required=volumes_required)
        parsed.provisioning_intent.iscsi_network = _parse_iscsi_network_tab(workbook)
        parsed.provisioning_intent.peer_ports = _parse_peer_ports_tab(workbook)
        _reject_two_arrays(parsed)
        replication = _parse_replication_tab(workbook)
        if replication is None and _replication_selected(mode, selected_steps):
            raise ValueError(
                "The Replication and Failover test steps need the 'Replication' tab (peer array and the "
                "volume sets to protect), and this workbook has none filled in."
            )
        parsed.provisioning_intent.replication = replication
        _reject_peer_is_this_array(parsed)
        migration = _parse_migration_tab(workbook)
        if migration is None and _migration_selected(mode, selected_steps):
            raise ValueError(
                "The Migration step needs the 'Migration' tab (the source array and the hosts to migrate), and "
                "this workbook has none filled in."
            )
        parsed.provisioning_intent.migration = migration
        _reject_source_is_this_array(parsed)
        snapshots = _parse_snapshots_tab(workbook)
        if snapshots is None and _snapshots_selected(mode, selected_steps):
            raise ValueError(SNAPSHOTS_TAB_NEEDED)
        parsed.provisioning_intent.snapshots = snapshots
        _reject_a_port_with_two_roles(parsed.provisioning_intent)
    return parsed


def parse_upload(data: bytes) -> tuple[ParsedInitSheet, list[str]]:
    """The upload of the full app: refuse only what initialising the array needs, list the rest.

    Owner, 2026-11-19: check a tab only when the run uses it. A sheet that passes the complete check
    parses exactly as before, with no problems. Otherwise the Initialisation tab is checked as a Full
    onboarding run checks it (a problem there still raises), every other tab is read on its own, and
    each problem found is one sentence in the list, the same sentence the complete check raises. A bad
    row is left out of the intent, a tab with a problem is left out whole, and the run is refused when it
    is created with steps that use them (`parse_workbook_bytes` with the chosen mode). A workbook that
    names two arrays is still refused here: a run is one array.
    """
    try:
        return parse_workbook_bytes(data, complete=True), []
    except ValueError as exc:
        complete_problem = str(exc)
    parsed = parse_workbook_bytes(data, mode=RunMode.FULL_ONBOARDING)
    workbook = load_workbook(io.BytesIO(data), data_only=True)
    problems: list[str] = []

    def tab(read, fallback=None):
        try:
            return read()
        except ValueError as exc:
            problems.append(str(exc))
            return fallback

    def passes(check) -> bool:
        return tab(lambda: check() or True, False)

    intent = tab(lambda: _parse_provisioning_tab(workbook, problems=problems))
    iscsi_network = tab(lambda: _parse_iscsi_network_tab(workbook), [])
    peer_ports = tab(lambda: _parse_peer_ports_tab(workbook))
    replication = tab(lambda: _parse_replication_tab(workbook))
    migration = tab(lambda: _parse_migration_tab(workbook))
    snapshots = tab(lambda: _parse_snapshots_tab(workbook))
    if intent is not None:
        intent.iscsi_network, intent.peer_ports = iscsi_network, peer_ports
        intent.replication, intent.migration, intent.snapshots = replication, migration, snapshots
        parsed.provisioning_intent = intent
        _reject_two_arrays(parsed)
        if not passes(lambda: _reject_peer_is_this_array(parsed)):
            intent.replication = None
        if not passes(lambda: _reject_source_is_this_array(parsed)):
            intent.migration = None
        passes(lambda: _reject_a_port_with_two_roles(intent))
    return parsed, problems or [complete_problem]


def _reject_source_is_this_array(parsed: ParsedInitSheet) -> None:
    intent = parsed.provisioning_intent
    if intent is None or intent.migration is None:
        return
    source = intent.migration.source.host.strip()
    own = {ip.lower() for ip in ((intent.array.host or "").strip(), (parsed.work_item.network.mgmt_ipv4 or "").strip()) if ip}
    if source.lower() in own:
        raise ValueError(
            f"Migration tab — the source array ({source}) is this run's own array. This run's array is the "
            "destination: enter the address of the array the data moves from."
        )


def _reject_peer_is_this_array(parsed: ParsedInitSheet) -> None:
    intent = parsed.provisioning_intent
    if intent is None or intent.replication is None:
        return
    peer = intent.replication.peer.host.strip()
    own = {ip for ip in ((intent.array.host or "").strip(), (parsed.work_item.network.mgmt_ipv4 or "").strip()) if ip}
    if peer in own:
        raise ValueError(
            f"Replication tab — the peer array ({peer}) is this run's own array. Replication needs a second "
            "array: enter the OTHER array's management IP."
        )


def _reject_two_arrays(parsed: ParsedInitSheet) -> None:
    """A run is ONE array. Refuse a workbook that names two.

    The array's management IP appears twice — 'IP address' on the Initialisation tab (what
    cloudinit APPLIES to the array, and what verify reads) and 'Array management IP' on the
    Provisioning tab (where discovery/zoning/provisioning connect). They are the same array by
    definition, and the second field exists only because a PROVISION_ONLY run has no Initialisation
    section to read.

    Nothing used to tie them together, so a workbook could name two different arrays and the run
    would half-work: verify checked one box while the as-built read the other and timed out
    (measured live — init 10.132.30.121, provisioning 10.64.186.90, same run). Resolving that with
    a precedence rule only hides which array each step actually touched. Refuse it here instead,
    while there is still a human looking at the workbook, and say exactly which two values disagree.
    """
    intent = parsed.provisioning_intent
    if intent is None:
        return
    init_ip = (parsed.work_item.network.mgmt_ipv4 or "").strip()
    prov_ip = (intent.array.host or "").strip()
    # Empty means "this run doesn't use that tab" (a PROVISION_ONLY sheet has no Network section),
    # which is not a conflict — only two DIFFERENT stated addresses are.
    if not init_ip or not prov_ip or init_ip == prov_ip:
        return
    raise ValueError(
        f"This workbook names two different arrays: the Initialisation tab's 'IP address' is "
        f"{init_ip} and the Provisioning tab's 'Array management IP' is {prov_ip}. A run covers one "
        "array — every step (initialise, verify, provision, as-built) acts on it. Correct whichever "
        "is wrong, or use a separate workbook/run for the other array."
    )


#: Credential fields are used exactly as typed; every other field is trimmed.
_VERBATIM_KEYS = frozenset({
    "gl_client_secret", "prov_array_password", "prov_vcenter_password",
    "prov_sw1_password", "prov_sw2_password", "password", "peer_password", "source_password",
})


def _cell_text(key: str | None, value) -> str:
    if isinstance(value, datetime.time) and key == "port":
        # Excel stores 0:4:4 typed in a General cell as a time; a port N:S:P reads back as H:M:S.
        return f"{value.hour}:{value.minute}:{value.second}"
    text = str(value)
    return text if key in _VERBATIM_KEYS else text.strip()


def _read_tab(sheet, label_to_key: dict[str, str]) -> dict[str, str]:
    """Collect Field->Value pairs from a fillable tab, matching labels to stable keys."""
    values: dict[str, str] = {}
    for row in sheet.iter_rows(min_row=1, max_col=2, values_only=True):
        label = row[0]
        value = row[1] if len(row) > 1 else None
        if label is None or value is None:
            continue
        key = label_to_key.get(_normalize_label(str(label)))
        text = _cell_text(key, value)
        if key and text.strip():
            values[key] = text
    return values


def _read_table(ws, columns: list[tuple[str, str, bool]], *, any_cell: bool = False) -> list[dict[str, str]]:
    """Read a row-table tab into a list of {key: value} dicts. Locates the header row as the first row
    that carries the NAME column (tolerant of the intro line and of the operator's column order);
    columns match on their leading phrase, never on the hint text after it (P-17). Then reads data
    rows to the end, skipping any row whose name column is blank (`any_cell`: only rows with no value
    at all, so the tab's own "missing" rule can refuse a row whose first cell is blank)."""
    header_to_key = {_column_key(label): key for key, label, _ in columns}
    name_key = columns[0][0]
    rows = list(ws.iter_rows(values_only=True))
    header_idx: int | None = None
    col_index: dict[int, str] = {}
    for i, row in enumerate(rows):
        mapping = {ci: header_to_key[_column_key(str(cell))]
                   for ci, cell in enumerate(row)
                   if cell is not None and _column_key(str(cell)) in header_to_key}
        if name_key in mapping.values():
            header_idx, col_index = i, mapping
            break
    if header_idx is None:
        return []

    records: list[dict[str, str]] = []
    for row in rows[header_idx + 1:]:
        record = {
            key: _cell_text(key, row[ci])
            for ci, key in col_index.items()
            if ci < len(row) and row[ci] is not None and str(row[ci]).strip()
        }
        if record.get(name_key) or (any_cell and record):
            records.append(record)
    return records


def _note_or_raise(problems: list[str] | None, exc: ValueError) -> None:
    """Strict (`problems` is None): raise. The upload: note the sentence and leave that row out."""
    if problems is None:
        raise exc
    problems.append(str(exc))


def _volume_request(r: dict[str, str], *, default_type: str, default_cpg: str) -> VolumeRequest:
    if bad_name := volume_name_problem(r["name"]):
        raise ValueError(f"Volume '{r['name']}' — Name: {bad_name}. Rename it.")
    if r.get("vvset") and (bad_set := volume_set_name_problem(r["vvset"])):
        raise ValueError(f"Volume '{r['name']}' — VV-set: {bad_set}. Rename it.")
    ptype = (r.get("provisioning_type") or default_type).strip().lower()
    if ptype not in ("tpvv", "reduce"):
        raise ValueError(f"Volume '{r['name']}' — Type must be 'tpvv' or 'reduce'.")
    try:
        size = float(r["size_gib"])
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Volume '{r.get('name', '?')}' — Size (GiB) must be a number.") from exc
    if size <= 0 or not size.is_integer():
        raise ValueError(f"Volume '{r['name']}' — Size (GiB) must be a whole number above 0 (got {r['size_gib']}).")
    size_gib = int(size)
    if too_large := volume_too_large(size_gib):
        raise ValueError(f"Volume '{r['name']}' — Size (GiB): {too_large}. Make it smaller.")
    return VolumeRequest(
        name=r["name"], size_gib=size_gib,
        provisioning_type=ptype,  # type: ignore[arg-type]
        cpg=r.get("cpg") or default_cpg, vvset=r.get("vvset") or None,
    )


def _declared_host(r: dict[str, str]) -> DeclaredHost:
    wwpns = [normalize_wwpn(w) for w in (r.get("wwpns") or "").replace(";", ",").split(",") if w.strip()]
    iqn = (r.get("iqn") or "").strip()
    bad = [w for w in wwpns if len(w) != 16]
    if bad:
        raise ValueError(
            f"Hosts tab — host '{r['name']}' has an FC WWPN that is not 16 hex digits: "
            + ", ".join(bad) + ". A mistyped WWPN produces a zone that matches nothing."
        )
    if iqn and not iqn.lower().startswith("iqn."):
        raise ValueError(f"Hosts tab — host '{r['name']}' has an iSCSI IQN that does not start with 'iqn.': {iqn}")
    # SPEC-014 R1: a row with neither id is a lookup request — discovery finds it by name/IP.
    os_ = (r.get("os") or "").strip().lower()
    if os_ and os_ not in ("esxi", "windows", "linux", "vme"):
        raise ValueError(f"Hosts tab — host '{r['name']}' has an unrecognised OS '{os_}' (esxi / windows / linux / vme).")
    username, password = (r.get("username") or "").strip(), r.get("password") or ""
    address = (r.get("address") or "").strip()
    if password and not username:
        raise ValueError(f"Hosts tab — host '{r['name']}' has a login password but no login username.")
    if username and not address:
        raise ValueError(f"Hosts tab — host '{r['name']}' has a login but no IP address to log in to.")
    return DeclaredHost(
        name=r["name"], os=os_, address=address, wwpns=wwpns, iqn=iqn,
        username=username, password=SecretStr(password) if password else None,
    )


def _parse_provisioning_tab(
    workbook, *, volumes_required: bool = True, problems: list[str] | None = None,
) -> ProvisioningIntent:
    """Read the provisioning input (Provisioning targets + Volumes + Host sets row-tables) into a plural
    ProvisioningIntent (passwords included — customer-supplied). Exports are composed later in the UI.
    `volumes_required` False: a run without the Provision step may leave Volumes and Host sets empty.
    `problems` (the upload): a bad Volumes or Hosts row, or an empty Volumes or Host sets tab, is noted
    there and left out instead of refused; a missing tab or target field is still raised."""
    for name in (PROVISIONING_SHEET_NAME, VOLUMES_SHEET_NAME, HOSTSETS_SHEET_NAME):
        if name not in workbook.sheetnames:
            raise ValueError(f"The '{name}' tab is required for provisioning but was not found in the workbook.")

    targets = _read_tab(workbook[PROVISIONING_SHEET_NAME], _PROV_LABEL_TO_KEY)
    missing = [_PROV_KEY_TO_LABEL[key] for key in _PROV_REQUIRED if not targets.get(key)]
    if missing:
        raise ValueError("Provisioning tab — missing required fields: " + ", ".join(sorted(missing)))

    default_cpg = targets.get("prov_default_cpg") or "SSD_r6"
    default_type = (targets.get("prov_default_type") or "tpvv").strip().lower()
    if default_type not in ("tpvv", "reduce"):
        raise ValueError("Default provisioning type must be 'tpvv' or 'reduce'.")

    vol_rows = _read_table(workbook[VOLUMES_SHEET_NAME], VOLUME_COLUMNS)
    # A workbook that provisions nothing may leave Volumes and Host sets empty: a run without the Provision
    # step, or one that only replicates or snapshots sets already on the array, migrates hosts from another
    # array (Peer Motion creates their volumes here) or sets up the array's own ports. The run guard then
    # refuses the Provision step (nothing to provision).
    replicate_only = not vol_rows and (
        not volumes_required
        or _replication_rows_present(workbook)
        or _snapshot_rows_present(workbook)
        or _migration_rows_present(workbook)
        or _table_rows_present(workbook, ISCSI_NETWORK_SHEET_NAME, ISCSI_NETWORK_COLUMNS)
        or _table_rows_present(workbook, PEER_PORTS_SHEET_NAME, PEER_PORT_COLUMNS)
    )
    if not vol_rows and not replicate_only:
        _note_or_raise(problems, ValueError(
            "Volumes tab — add at least one volume (a name and a size). Or leave Volumes and Host sets empty and "
            "fill the Replication tab or the Snapshots tab (volume sets already on the array), fill the Migration "
            "tab (hosts from another array), or fill the iSCSI network or Peer ports tab (the array's own ports)."
        ))
    volumes: list[VolumeRequest] = []
    for r in vol_rows:
        try:
            volumes.append(_volume_request(r, default_type=default_type, default_cpg=default_cpg))
        except ValueError as exc:
            _note_or_raise(problems, exc)

    hs_rows = _read_table(workbook[HOSTSETS_SHEET_NAME], HOSTSET_COLUMNS)
    if not hs_rows and not replicate_only:
        _note_or_raise(problems, ValueError("Host sets tab — add at least one host set (a name)."))
    host_sets = [
        HostSetRequest(name=r["name"], members=[m.strip() for m in (r.get("members") or "").split(",") if m.strip()])
        for r in hs_rows
    ]

    # OPTIONAL tab: only servers nothing can discover yet. Absent on an older workbook, which must
    # still parse — the tab adds capability, it is not a new requirement.
    declared: list[DeclaredHost] = []
    if HOSTS_SHEET_NAME in workbook.sheetnames:
        for r in _read_table(workbook[HOSTS_SHEET_NAME], HOSTS_COLUMNS):
            try:
                declared.append(_declared_host(r))
            except ValueError as exc:
                _note_or_raise(problems, exc)

    return ProvisioningIntent(
        array=EndpointCreds(host=targets["prov_array_host"], username=targets["prov_array_user"], password=SecretStr(targets["prov_array_password"])),
        vcenter=EndpointCreds(host=targets["prov_vcenter_host"], username=targets["prov_vcenter_user"], password=SecretStr(targets["prov_vcenter_password"])),
        # Switches are OPTIONAL (verify is array-side; switches only needed to CREATE zones) -> default blank.
        switch_f1=EndpointCreds(host=targets.get("prov_sw1_host", ""), username=targets.get("prov_sw1_user", ""), password=SecretStr(targets.get("prov_sw1_password", ""))),
        switch_f2=EndpointCreds(host=targets.get("prov_sw2_host", ""), username=targets.get("prov_sw2_user", ""), password=SecretStr(targets.get("prov_sw2_password", ""))),
        volumes=volumes,
        host_sets=host_sets,
        declared_hosts=declared,
        default_cpg=default_cpg,
    )


def _yes_no(text: str | None, *, default: bool, where: str) -> bool:
    value = (text or "").strip().lower()
    if not value:
        return default
    if value in ("yes", "y", "true", "1"):
        return True
    if value in ("no", "n", "false", "0"):
        return False
    raise ValueError(f"{where} must be 'yes' or 'no' (got '{text}').")


def _table_rows_present(workbook, name: str, columns: list[tuple[str, str, bool]]) -> bool:
    return name in workbook.sheetnames and bool(_read_table(workbook[name], columns))


def _replication_rows_present(workbook) -> bool:
    return REPLICATION_SHEET_NAME in workbook.sheetnames and bool(
        _read_table(workbook[REPLICATION_SHEET_NAME], PROTECTION_COLUMNS)
    )


def _parse_replication_tab(workbook) -> ReplicationIntent | None:
    """The optional Replication tab (SPEC-015 R1/R2). Absent, or present but blank, -> None (an
    older workbook parses exactly as before). Filled -> validated to one sentence per rule."""
    if REPLICATION_SHEET_NAME not in workbook.sheetnames:
        return None
    ws = workbook[REPLICATION_SHEET_NAME]
    fields = _read_tab(ws, _REPL_LABEL_TO_KEY)
    rows = _read_table(ws, PROTECTION_COLUMNS)
    if not any(fields.get(k) for k in _REPL_REQUIRED) and not rows:
        return None

    missing = [_REPL_KEY_TO_LABEL[key] for key in _REPL_REQUIRED if not fields.get(key)]
    if missing:
        raise ValueError("Replication tab — missing required fields: " + ", ".join(sorted(missing)))
    if not rows:
        raise ValueError("Replication tab — add at least one volume set to protect (a Volume set and a Peer CPG).")

    rtt: float | None = None
    if fields.get("rtt_ms"):
        try:
            rtt = float(fields["rtt_ms"])
        except ValueError as exc:
            raise ValueError(f"Replication tab — 'Measured round-trip time (ms)' must be a number (got '{fields['rtt_ms']}').") from exc
        if rtt < 0:
            raise ValueError("Replication tab — 'Measured round-trip time (ms)' cannot be negative.")

    # A set not on the Volumes tab is an EXISTING set: the Replication preview reads the array and
    # refuses it there if it is missing or empty (plan.check).
    protections: list[ProtectionRequest] = []
    seen: set[str] = set()
    for r in rows:
        vvset = r["vvset"]
        where = f"Replication tab — row '{vvset}'"
        if vvset in seen:
            raise ValueError(f"{where} appears twice; one row per volume set.")
        seen.add(vvset)
        mode_text = (r.get("mode") or "async").strip().lower()
        if mode_text in ("periodic", "asynchronous", "asynchronous periodic"):
            mode_text = "async"
        elif mode_text == "synchronous":
            mode_text = "sync"
        if mode_text not in ("async", "sync"):
            unsupported = any(t in mode_text for t in _UNSUPPORTED_REPLICATION_TYPES)
            raise ValueError(
                f"{where}: Mode must be 'async' or 'sync' (got '{r.get('mode')}')"
                + ("; Peer Persistence, Active Sync, SLD and 3DC are not supported in this version." if unsupported else ".")
            )
        rpo: int | None = None
        if mode_text == "async":
            raw = (r.get("rpo_minutes") or "").strip()
            if not raw:
                rpo = RPO_MINUTES_DEFAULT
            else:
                try:
                    value = float(raw)
                except ValueError as exc:
                    raise ValueError(f"{where}: RPO must be a whole number of minutes, {RPO_MINUTES_MIN} or more (got '{raw}').") from exc
                if not value.is_integer() or value < RPO_MINUTES_MIN:
                    raise ValueError(f"{where}: RPO must be a whole number of minutes, {RPO_MINUTES_MIN} or more (got '{raw}').")
                rpo = int(value)
        # SPEC-020: a blank RTT is fine here — the Replication step measures it (checkrclink), or over Fibre
        # Channel asks for it (SPEC-031 R6). The sheet does not know the transport yet: it refuses only what RCIP,
        # the looser limit, refuses, and the step holds a Fibre Channel pair to its own.
        if rtt is not None and rtt > rtt_limit_ms("IP", mode_text):
            raise ValueError(
                f"{where}: the measured round-trip time is {rtt:g} ms; {rtt_limit_text('IP', mode_text)} "
                "(HPE Support Matrix)."
            )
        peer_cpg = (r.get("peer_cpg") or "").strip()
        if not peer_cpg:
            raise ValueError(f"{where}: Peer CPG is required (the CPG on the peer array for the secondary volumes).")
        protections.append(ProtectionRequest(
            vvset=vvset, mode=mode_text, rpo_minutes=rpo, peer_cpg=peer_cpg,  # type: ignore[arg-type]
            peer_vvset=(r.get("peer_vvset") or "").strip(),
            auto_synchronize=_yes_no(r.get("auto_synchronize"), default=True, where=f"{where}: Auto synchronize"),
            auto_recover=_yes_no(r.get("auto_recover"), default=True, where=f"{where}: Auto recover"),
        ))

    network = _parse_network_tab(workbook)
    return ReplicationIntent(
        peer=EndpointCreds(host=fields["peer_host"], username=fields["peer_user"], password=SecretStr(fields["peer_password"])),
        rtt_ms=rtt,
        protections=protections,
        failover_test=_yes_no(fields.get("failover_test"), default=True, where="Replication tab — 'Run the failover test'"),
        failover_group=(fields.get("failover_group") or "").strip(),
        network=network,
    )


def _snapshot_rows_present(workbook) -> bool:
    return SNAPSHOTS_SHEET_NAME in workbook.sheetnames and bool(
        _read_table(workbook[SNAPSHOTS_SHEET_NAME], SNAPSHOT_COLUMNS)
    )


def _whole(text: str) -> int | None:
    """A whole number as typed or as Excel stores it ('24', 24.0); None for anything else."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return int(value) if value.is_integer() else None


def _parse_snapshots_tab(workbook) -> SnapshotIntent | None:
    """SPEC-023 R1/R2. No tab, or a blank one -> None (an older workbook parses exactly as before).
    Each row is checked in R2's order and the first rule it breaks is raised, one sentence each."""
    if SNAPSHOTS_SHEET_NAME not in workbook.sheetnames:
        return None
    rows = _read_table(workbook[SNAPSHOTS_SHEET_NAME], SNAPSHOT_COLUMNS)
    if not rows:
        return None
    requests: list[SnapshotRequest] = []
    seen: set[str] = set()
    names: set[str] = set()
    for r in rows:
        source = r["source"]
        where = f"Snapshots tab — row '{source}'"
        if source in seen:
            raise ValueError(f"{where} appears twice; one row per volume set or volume.")
        seen.add(source)
        kind = (r.get("kind") or "set").strip().lower()
        if kind not in ("set", "volume"):
            raise ValueError(f"{where}: Kind must be 'set' or 'volume' (got '{r.get('kind')}').")
        every_text, unit_text = (r.get("every") or "").strip(), (r.get("unit") or "").strip()
        snapshot_now = _yes_no(r.get("snapshot_now"), default=False, where=f"{where}: Snapshot now")
        if not snapshot_now and not every_text and not unit_text:
            raise ValueError(f"{where} asks for nothing: set Snapshot now to yes, or fill Every and Unit.")
        if bool(every_text) != bool(unit_text):
            raise ValueError(f"{where}: Every and Unit go together; fill both or neither.")
        every: int | None = None
        unit: str | None = None
        if every_text:
            every, unit = _whole(every_text), _UNITS.get(unit_text.lower())
            if every is None or unit is None or every not in ALLOWED_EVERY[unit]:
                raise ValueError(
                    f"{where}: every {every if every is not None else every_text} {unit_text} is not a period the "
                    "array schedules; use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day."
                )
        hour_text = (r.get("at_hour") or "").strip()
        if unit == "minutes" and hour_text:
            raise ValueError(f"{where}: Start hour applies to hours and days; leave it blank for a schedule in minutes.")
        at_hour = 0
        if hour_text and unit is not None:
            parsed_hour = _whole(hour_text)
            if parsed_hour is None or not 0 <= parsed_hour <= 23:
                raise ValueError(f"{where}: Start hour must be a whole number from 0 to 23 (got '{hour_text}').")
            at_hour = parsed_hour
        days_text = (r.get("days") or "").strip()
        if days_text and unit is None:
            raise ValueError(f"{where}: Days applies to a schedule; fill Every and Unit, or leave Days blank.")
        days: set[int] = set()
        for item in (d.strip().lower() for d in days_text.split(",")):
            if not item:
                continue
            if item not in _DAY_NUMBERS:
                raise ValueError(f"{where}: Days must be day names separated by commas, such as mon, tue (got '{days_text}').")
            days.add(_DAY_NUMBERS[item])
        expire = _whole((r.get("expire_hours") or "").strip())
        if expire is None or not 1 <= expire <= HOURS_MAX:
            raise ValueError(f"{where}: Keep for must be a whole number of hours from 1 to {HOURS_MAX}.")
        retain: int | None = None
        retain_text = (r.get("retain_hours") or "").strip()
        if retain_text:
            retain = _whole(retain_text)
            if retain is None or not 1 <= retain <= HOURS_MAX:
                raise ValueError(f"{where}: Lock for must be a whole number of hours from 1 to {HOURS_MAX}, or blank.")
            if retain > expire:
                raise ValueError(f"{where}: Lock for cannot be longer than Keep for; the array refuses it.")
        schedule_name = (r.get("schedule_name") or "").strip()
        if schedule_name and not _SCHEDULE_NAME.fullmatch(schedule_name):
            raise ValueError(
                f"{where}: Schedule name may use letters, digits, '.', '_' and '-' only, up to {SCHEDULE_NAME_MAX} characters."
            )
        if schedule_name.startswith("-"):
            raise ValueError(f"{where}: Schedule name cannot start with '-'; the array would read it as an option.")
        if schedule_name.lower() in _RESERVED_SCHEDULE_NAMES:
            raise ValueError(f"{where}: Schedule name '{schedule_name}' is kept by the array for itself; choose another.")
        read_only = _yes_no(r.get("read_only"), default=True, where=f"{where}: Read-only")
        request = SnapshotRequest(
            source=source, kind=kind, snapshot_now=snapshot_now, every=every, unit=unit,  # type: ignore[arg-type]
            at_hour=at_hour, days=sorted(days), expire_hours=expire, retain_hours=retain, read_only=read_only,
            schedule_name=schedule_name,
        )
        if request.has_schedule:
            if request.name in names:
                raise ValueError(f"{where}: schedule name '{request.name}' is used by two rows.")
            names.add(request.name)
        requests.append(request)
    return SnapshotIntent(requests=requests)


def _ipv4(text: str) -> bool:
    try:
        ipaddress.IPv4Address(text)
        return True
    except ValueError:
        return False


def _netmask(text: str) -> bool:
    """A dotted netmask with at least one bit (255.255.254.0), never a host mask (0.0.0.255) or /0."""
    if not _ipv4(text):
        return False
    bits = int(ipaddress.IPv4Address(text))
    return bits != 0 and (bits | (bits - 1)) & 0xFFFFFFFF == 0xFFFFFFFF and str(
        ipaddress.ip_network(f"0.0.0.0/{text}").netmask) == text


def _parse_network_tab(workbook) -> list[RcipPortRequest]:
    """SPEC-021 R1, one sentence per rule. No tab, or a blank one -> [] (the partnership must exist)."""
    if REPLICATION_NETWORK_SHEET_NAME not in workbook.sheetnames:
        return []
    rows = _read_table(workbook[REPLICATION_NETWORK_SHEET_NAME], NETWORK_COLUMNS)
    out: list[RcipPortRequest] = []
    seen_ports: set[tuple[str, str]] = set()
    seen_ips: set[str] = set()
    for r in rows:
        where = f"Replication network tab — row '{r.get('array')} {r.get('port', '')}'"
        side = {"this": "A", "peer": "B"}.get((r.get("array") or "").strip().lower())
        if side is None:
            raise ValueError(f"{where}: Array must be 'this' or 'peer' (got '{r.get('array')}').")
        missing = [label for key, label, required in NETWORK_COLUMNS if required and not (r.get(key) or "").strip()]
        if missing:
            raise ValueError(f"{where}: missing {', '.join(missing)}.")
        port, ip, mask, gw = (r.get(k, "").strip() for k in ("port", "ip", "netmask", "gateway"))
        if not re.fullmatch(r"(?:0|[1-9]\d?):(?:0|[1-9]\d?):(?:0|[1-9]\d?)", port):
            raise ValueError(f"{where}: Port must be N:S:P, like 0:4:4 (got '{port}').")
        if not _ipv4(ip):
            raise ValueError(f"{where}: RCIP address '{ip}' is not an IPv4 address.")
        if not _netmask(mask):
            raise ValueError(f"{where}: Netmask '{mask}' is not a netmask (like 255.255.254.0).")
        if gw and not _ipv4(gw):
            raise ValueError(f"{where}: Gateway '{gw}' is not an IPv4 address.")
        if (side, port) in seen_ports:
            raise ValueError(f"{where}: port {port} is named twice on the same array.")
        if ip in seen_ips:
            raise ValueError(f"{where}: address {ip} is used twice.")
        seen_ports.add((side, port))
        seen_ips.add(ip)
        out.append(RcipPortRequest(side=side, nsp=port, ip=ip, netmask=mask, gateway=gw))  # type: ignore[arg-type]
    if not out:
        return []
    pairs = pair_ports(out)
    paired = {(p.side, p.nsp) for pair in pairs for p in pair}
    lonely = [f"{'this' if r.side == 'A' else 'peer'} {r.nsp}" for r in out if (r.side, r.nsp) not in paired]
    if lonely:
        raise ValueError("Replication network tab — ports pair node to node, and these have no partner on the other "
                         "array's same node: " + ", ".join(lonely) + ".")
    if len(pairs) < 2:
        raise ValueError("Replication network tab — the partnership needs at least 2 links: name two ports on this "
                         "array and two on the peer, one per node.")
    return out


def _migration_rows_present(workbook) -> bool:
    return MIGRATION_SHEET_NAME in workbook.sheetnames and bool(
        _read_table(workbook[MIGRATION_SHEET_NAME], MIGRATION_HOST_COLUMNS)
    )


def _list_word(text: str) -> str:
    return " ".join(text.strip().lower().replace("-", " ").replace("_", " ").split())


def _one_of(values: tuple[str, ...]) -> str:
    return ", ".join(values[:-1]) + " or " + values[-1]


def _parse_migration_tab(workbook) -> MigrationIntent | None:
    """The optional Migration tab (SPEC-027 R1). Absent, or present but blank, -> None (an older
    workbook parses exactly as before). Filled -> one sentence per refused rule. The source array's
    name, model, serial and OS are read from it later, never taken from the sheet."""
    if MIGRATION_SHEET_NAME not in workbook.sheetnames:
        return None
    ws = workbook[MIGRATION_SHEET_NAME]
    fields = _read_tab(ws, _MIG_LABEL_TO_KEY)
    rows = _read_table(ws, MIGRATION_HOST_COLUMNS)
    if not fields and not rows:
        return None

    if not fields.get("source_host", "").strip():
        raise ValueError("Migration tab — enter the source array's management address (the array the data moves from).")
    if not fields.get("source_user", "").strip():
        raise ValueError("Migration tab — enter a user for the source array; a read-only account is enough.")
    if not fields.get("source_password"):
        raise ValueError("Migration tab — enter the password of the source array's user.")
    orchestration = _ORCHESTRATION_WORDS.get(_list_word(fields.get("orchestration") or "array UI"))
    if orchestration is None:
        raise ValueError(
            f"Migration tab — 'Where the import runs' must be 'array UI' or 'DSCC' (got '{fields['orchestration']}')."
        )
    if not rows:
        raise ValueError("Migration tab — add at least one host to migrate: its name on the source array and a destination CPG.")

    hosts: list[MigrationHostRequest] = []
    seen: set[str] = set()
    for r in rows:
        name = r["host"]
        where = f"Migration tab — host '{name}'"
        if name in seen:
            raise ValueError(f"{where} appears twice; one row per host.")
        seen.add(name)
        kind = _MIGRATION_TYPE_WORDS.get(_list_word(r.get("type") or "online"))
        if kind is None:
            raise ValueError(f"{where}: Migration type must be {_one_of(MIGRATION_TYPES)} (got '{r['type']}').")
        provisioning = _MIGRATION_PROVISIONING_WORDS.get(_list_word(r.get("provisioning") or "thin"))
        if provisioning is None:
            raise ValueError(
                f"{where}: Provisioning must be {_one_of(MIGRATION_PROVISIONING)} (got '{r['provisioning']}')."
            )
        cpg = (r.get("cpg") or "").strip()
        if not cpg:
            raise ValueError(f"{where}: enter the destination CPG, the CPG on this array that receives its volumes.")
        hosts.append(MigrationHostRequest(
            host=name, type=kind, cpg=cpg, provisioning=provisioning,  # type: ignore[arg-type]
        ))

    return MigrationIntent(
        source=EndpointCreds(host=fields["source_host"].strip(), username=fields["source_user"].strip(), password=SecretStr(fields["source_password"])),
        orchestration=orchestration,  # type: ignore[arg-type]
        hosts=hosts,
    )


_PORT_RE = re.compile(r"(?:0|[1-9]\d?):(?:0|[1-9]\d?):(?:0|[1-9]\d?)")


def _parse_iscsi_network_tab(workbook) -> list[IscsiVlanRequest]:
    """SPEC-024 R1, one sentence per rule, the first that applies. No tab, or a blank one -> [].
    The two cross-row rules are the tool's own (one VLAN is one IP network); the array may be more
    lenient, but a sheet that breaks them is almost always a typing slip."""
    if ISCSI_NETWORK_SHEET_NAME not in workbook.sheetnames:
        return []
    rows = _read_table(workbook[ISCSI_NETWORK_SHEET_NAME], ISCSI_NETWORK_COLUMNS, any_cell=True)
    out: list[IscsiVlanRequest] = []
    nets: list[ipaddress.IPv4Network] = []
    seen_ports: set[tuple[str, int]] = set()
    seen_ips: set[str] = set()
    for r in rows:
        port, vlan, ip, mask, gw = (r.get(k, "").strip() for k in ("port", "vlan", "ip", "netmask", "gateway"))
        where = f"iSCSI network tab — row '{port} VLAN {vlan}'"
        missing = [label for key, label, required in ISCSI_NETWORK_COLUMNS if required and not (r.get(key) or "").strip()]
        if missing:
            raise ValueError(f"{where}: missing {', '.join(missing)}.")
        if not _PORT_RE.fullmatch(port):
            raise ValueError(f"{where}: Port must be N:S:P, like 0:4:1 (got '{port}').")
        if not (vlan.isdigit() and 1 <= int(vlan) <= 4094):
            raise ValueError(f"{where}: VLAN ID must be a whole number from 1 to 4094 (got '{vlan}').")
        if not _ipv4(ip):
            raise ValueError(f"{where}: iSCSI address '{ip}' is not an IPv4 address.")
        if not _netmask(mask):
            raise ValueError(f"{where}: Netmask '{mask}' is not a netmask (like 255.255.255.0).")
        if gw and not _ipv4(gw):
            raise ValueError(f"{where}: Gateway '{gw}' is not an IPv4 address.")
        net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        if gw and ipaddress.IPv4Address(gw) not in net:
            raise ValueError(f"{where}: Gateway {gw} is not on the network {net} of {ip}.")
        # A /31 or /32 has no network or broadcast address to avoid.
        if net.prefixlen < 31 and ipaddress.IPv4Address(ip) in (net.network_address, net.broadcast_address):
            raise ValueError(f"{where}: {ip} is the network or broadcast address of {net}.")
        if (port, int(vlan)) in seen_ports:
            raise ValueError(f"{where}: port {port} has VLAN {vlan} twice.")
        if ip in seen_ips:
            raise ValueError(f"{where}: address {ip} is used twice.")
        seen_ports.add((port, int(vlan)))
        seen_ips.add(ip)
        nets.append(net)
        out.append(IscsiVlanRequest(nsp=port, vlan_id=int(vlan), ip=ip, netmask=mask, gateway=gw))
    first_of_vlan: dict[int, tuple[ipaddress.IPv4Network, str]] = {}
    for req, net in zip(out, nets, strict=True):
        net1, port1 = first_of_vlan.setdefault(req.vlan_id, (net, req.nsp))
        if net != net1:
            raise ValueError(f"iSCSI network tab — VLAN {req.vlan_id} is on two networks: {net1} on {port1} and "
                             f"{net} on {req.nsp}. One VLAN is one network.")
    vlan_of_net: dict[ipaddress.IPv4Network, int] = {}
    for req, net in zip(out, nets, strict=True):
        other = vlan_of_net.setdefault(net, req.vlan_id)
        if other != req.vlan_id:
            raise ValueError(f"iSCSI network tab — VLAN {other} and VLAN {req.vlan_id} are both on {net}. "
                             "Give each VLAN a network of its own.")
    return out


_WWPN_SPLIT = re.compile(r"[\s,;]+")


def _parse_peer_ports_tab(workbook) -> PeerPortIntent | None:
    """SPEC-025 R1, one sentence per rule. No tab, or a blank one -> None (the workbook parses as before).
    Port existence, Type and use are array facts, judged in the plan (R3), not here."""
    if PEER_PORTS_SHEET_NAME not in workbook.sheetnames:
        return None
    rows = _read_table(workbook[PEER_PORTS_SHEET_NAME], PEER_PORT_COLUMNS)
    if not rows:
        return None
    ports: list[PeerPortRequest] = []
    for r in rows:
        port = (r.get("port") or "").strip()
        where = f"Peer ports tab — row '{port}'"
        if not _PORT_RE.fullmatch(port):
            raise ValueError(f"{where}: Port must be N:S:P, like 0:3:2 (got '{port}').")
        wwpns: list[str] = []
        for text in _WWPN_SPLIT.split((r.get("source_wwpns") or "").strip()):
            if not text:
                continue
            wwpn = normalize_wwpn(text)
            if not re.fullmatch(r"[0-9A-F]{16}", wwpn):
                raise ValueError(f"{where}: '{text}' is not a WWPN (16 hex digits, colons allowed).")
            if wwpn not in wwpns:
                wwpns.append(wwpn)
        if any(p.nsp == port for p in ports):
            raise ValueError(f"Peer ports tab — port {port} is named twice.")
        ports.append(PeerPortRequest(nsp=port, source_wwpns=wwpns))
    nodes = {p.node for p in ports}
    if len(nodes) < 2:
        (node,) = nodes
        raise ValueError(
            f"Peer ports tab — peer ports go in pairs across nodes: name at least one port on each of two nodes "
            f"(got {', '.join(p.nsp for p in ports)} only on node {node}), so the migration keeps a path when a "
            "node restarts."
        )
    return PeerPortIntent(ports=ports)


def _reject_a_port_with_two_roles(intent: ProvisioningIntent) -> None:
    """SPEC-025 R1: a port on the Peer ports tab and on this array's rows of the Replication network
    tab has two roles. (The Replication FC ports tab of BL-50 joins this rule when it exists.)"""
    if intent.peer_ports is None or intent.replication is None:
        return
    rcip = {r.nsp for r in intent.replication.network if r.side == "A"}
    for port in intent.peer_ports.ports:
        if port.nsp in rcip:
            raise ValueError(f"Peer ports tab — port {port.nsp} is also on the Replication network tab; a port "
                             "has one role.")


def _build(values: dict[str, str], required: set[str]) -> ParsedInitSheet:
    missing = [_KEY_TO_LABEL[key] for key in required if not values.get(key)]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(sorted(missing)))

    # Fields not required by this mode but still mandatory on the models get harmless placeholders
    # (they are never used by the steps that didn't ask for them).
    def get(key: str, default: str = "") -> str:
        return values.get(key) or default

    dns = [values[key] for key in ("dns1", "dns2", "dns3") if values.get(key)]
    network = NetworkConfig(
        mgmt_ipv4=get("mgmt_ipv4"),
        mask=get("mask"),
        gateway=get("gateway"),
        dns=dns,
        ntp=get("ntp"),
        timezone=get("timezone"),
        proxy_host=values.get("proxy_host") or None,
        proxy_port=int(float(values["proxy_port"])) if values.get("proxy_port") else None,
    )
    dscc_setup = DsccSetupConfig(
        system_name=get("dscc_system_name", get("serial_number", "array")),
        country=get("dscc_country", "—"),
        credential_name=values.get("secret_name") or "b10000-admin",
        username=values.get("secret_username") or "3paradm",
        password=SecretStr(values["secret_password"]) if values.get("secret_password") else None,
        contact_first_name=values.get("contact_first_name"),
        contact_last_name=values.get("contact_last_name"),
        contact_language=values.get("contact_language") or "English",
        contact_company=values.get("contact_company"),
        contact_phone=values.get("contact_phone"),
        contact_email=values.get("contact_email"),
    )
    work_item = ArrayWorkItem(
        serial_number=values["serial_number"],  # always required
        part_number=get("part_number", "—"),
        subscription_key=SecretStr(get("subscription_key", "—")),
        service_catalog_region_id=get("service_catalog_region_id", "—"),
        dscc_region_code=get("dscc_region_code", "—"),
        cloudinit_url=values.get("cloudinit_url") or DEFAULT_CLOUDINIT_URL,
        network=network,
        dscc_setup=dscc_setup,
        customer_name=values.get("customer_name", ""),
        site=values.get("site", ""),
        application_workload=values.get("application_workload", ""),
        storage_purpose=values.get("storage_purpose", ""),
    )
    return ParsedInitSheet(
        work_item=work_item,
        gl_client_id=get("gl_client_id"),
        gl_client_secret=get("gl_client_secret"),
        gl_token_url=get("gl_token_url"),
        customer_name=values.get("customer_name", ""),
        site=values.get("site", ""),
    )


# ------------------------------------------------------------------ SPEC-006 R3: compose a sheet from JSON

def _fill_kv_tab(ws, label_to_key: dict[str, str], values: dict[str, str]) -> None:
    """Write `values` into the Value column of a Field | Value | Notes tab, matched by label."""
    for row in ws.iter_rows(min_row=2):
        label = row[0].value
        if label is None:
            continue
        key = label_to_key.get(_normalize_label(str(label)))
        if key is not None and key in values:
            _write_text(row[1], values[key])


def _write_text(cell, value) -> None:
    """Write a composed value as-is: a string starting with '=' is text (a password), never a formula."""
    cell.value = value
    if isinstance(value, str) and value.startswith("="):
        cell.data_type = "s"


def _replace_row_table(ws, columns: list[tuple[str, str, bool]], records: list[dict[str, str]]) -> None:
    """Replace every data row of a row-table tab with `records`. The header is located the way
    `_read_table` locates it (leading phrase, name column present); everything below it is cleared
    first, so a scenario sheet never carries a stale row from the base workbook."""
    header_to_key = {_column_key(label): key for key, label, _ in columns}
    name_key = columns[0][0]
    header_row: int | None = None
    col_of_key: dict[str, int] = {}
    for row in ws.iter_rows():
        found = {header_to_key[_column_key(str(c.value))]: c.column
                 for c in row if c.value is not None and _column_key(str(c.value)) in header_to_key}
        if name_key in found:
            header_row, col_of_key = row[0].row, found
            break
    if header_row is None:
        raise ValueError(f"'{ws.title}' has no header row with a '{columns[0][1]}' column")
    requested = {key for rec in records for key, value in rec.items() if value not in (None, "")}
    for key, label, _ in columns:
        if key in requested and key not in col_of_key:
            column = ws.max_column + 1
            ws.cell(row=header_row, column=column, value=label)
            col_of_key[key] = column
    for r in range(header_row + 1, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(row=r, column=c).value = None
    for i, rec in enumerate(records):
        for key, val in rec.items():
            if key in col_of_key and val not in (None, ""):
                _write_text(ws.cell(row=header_row + 1 + i, column=col_of_key[key]), val)


def compose_workbook_bytes(
    *,
    base: bytes | None,
    init: dict[str, str] | None = None,
    targets: dict[str, str] | None = None,
    volumes: list[dict[str, str]] | None = None,
    hostsets: list[dict[str, str]] | None = None,
    hosts: list[dict[str, str]] | None = None,
    replication: dict | None = None,
    migration: dict | None = None,
    snapshots: list[dict[str, str]] | None = None,
    iscsi_network: list[dict[str, str]] | None = None,
    peer_ports: list[dict[str, str]] | None = None,
) -> bytes:
    """A filled Initialisation_sheet.xlsx from JSON (SPEC-006 R3): start from `base` (the operator's
    working sheet) or the blank template; fill the key/value tabs given; REPLACE each row table given.
    A table not given is left as it is. `replication` = {"fields": {...}, "rows": [...]} fills the
    Replication tab and `migration` (same shape) the Migration tab, each added to a base workbook that
    predates it; `snapshots`, `iscsi_network` (SPEC-024 R1) and `peer_ports` (SPEC-025 R1) replace the
    rows of the Snapshots, iSCSI network and Peer ports tabs (each tab added the same way). The result
    parses exactly as an operator-edited sheet would."""
    try:
        wb = load_workbook(io.BytesIO(base)) if base else load_workbook(io.BytesIO(build_template_bytes()))
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise ValueError("The base is not an .xlsx workbook.") from exc
    if init:
        _fill_kv_tab(wb[wb.sheetnames[0]], _LABEL_TO_KEY, init)
    if targets and PROVISIONING_SHEET_NAME in wb.sheetnames:
        _fill_kv_tab(wb[PROVISIONING_SHEET_NAME], _PROV_LABEL_TO_KEY, targets)
    for name, columns, records in (
        (VOLUMES_SHEET_NAME, VOLUME_COLUMNS, volumes),
        (HOSTSETS_SHEET_NAME, HOSTSET_COLUMNS, hostsets),
        (HOSTS_SHEET_NAME, HOSTS_COLUMNS, hosts),
    ):
        if records is None:
            continue
        if name not in wb.sheetnames:
            raise ValueError(f"The base workbook has no '{name}' tab.")
        _replace_row_table(wb[name], columns, records)
    if replication is not None:
        if REPLICATION_SHEET_NAME not in wb.sheetnames:
            _add_replication_sheet(wb)
        ws = wb[REPLICATION_SHEET_NAME]
        _fill_kv_tab(ws, _REPL_LABEL_TO_KEY, replication.get("fields") or {})
        if replication.get("rows") is not None:
            _replace_row_table(ws, PROTECTION_COLUMNS, replication["rows"])
        if replication.get("network") is not None:
            if REPLICATION_NETWORK_SHEET_NAME not in wb.sheetnames:
                _add_replication_network_sheet(wb)
            _replace_row_table(wb[REPLICATION_NETWORK_SHEET_NAME], NETWORK_COLUMNS, replication["network"])
    if iscsi_network is not None:
        if ISCSI_NETWORK_SHEET_NAME not in wb.sheetnames:
            _add_iscsi_network_sheet(wb)
        _replace_row_table(wb[ISCSI_NETWORK_SHEET_NAME], ISCSI_NETWORK_COLUMNS, iscsi_network)
    if peer_ports is not None:
        if PEER_PORTS_SHEET_NAME not in wb.sheetnames:
            _add_peer_ports_sheet(wb)
        _replace_row_table(wb[PEER_PORTS_SHEET_NAME], PEER_PORT_COLUMNS, peer_ports)
    if migration is not None:
        if MIGRATION_SHEET_NAME not in wb.sheetnames:
            _add_migration_sheet(wb)
        ws = wb[MIGRATION_SHEET_NAME]
        _fill_kv_tab(ws, _MIG_LABEL_TO_KEY, migration.get("fields") or {})
        if migration.get("rows") is not None:
            _replace_row_table(ws, MIGRATION_HOST_COLUMNS, migration["rows"])
    if snapshots is not None:
        if SNAPSHOTS_SHEET_NAME not in wb.sheetnames:
            _add_snapshots_sheet(wb)
        _replace_row_table(wb[SNAPSHOTS_SHEET_NAME], SNAPSHOT_COLUMNS, snapshots)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
