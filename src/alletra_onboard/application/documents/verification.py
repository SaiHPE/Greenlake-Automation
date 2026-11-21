"""Post-init configuration verification (SSH-only) — see docs/adr/0001.

Logs into the initialized array over SSH and compares its on-array running config (read from the
``show*`` commands) against the values the operator intended (the work item). Read-only; the result
is a per-field report, never a gate.

Calibrated against a live HPE Alletra Storage MP B10000 (OS 10.5.51). All verified config comes from
three read-only commands:

  * ``showsys -d`` — ``System Name`` / ``Serial Number`` / ``Product Number`` / ``Contact`` as
    ``Key : Value`` lines.
  * ``shownet``    — mgmt IP + netmask in a table row (``<ip>  <netmask>  <nodes> ...``); gateway as
    ``Default IPv4 route :``; plus ``NTP server :`` and ``DNS server :`` lines.
  * ``showdate``   — timezone in parentheses after the date, e.g. ``... IST (Asia/Kolkata)``.

Notes from calibration: ``showdns`` / ``showntp`` do not exist on this platform (DNS/NTP are read
from ``shownet``), and the DSCC "System country" is not stored on the array (``Location`` is empty),
so it is not verified here.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from pydantic import SecretStr

from alletra_onboard.application.provisioning.clients import make_array_cli, make_wsapi_v3
from alletra_onboard.application.unified_file.read import read_file_side
from alletra_onboard.domain.array_parse import parse_showversion
from alletra_onboard.domain.errors import ArrayCliError, DeviceError
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    FieldCheck,
    FieldCheckStatus,
    HealthDetail,
    HealthIssue,
    VerificationReport,
)
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.unified_file import NODE_RUNNING, FileReport

if TYPE_CHECKING:
    from alletra_onboard.adapters.array.cli_client import ArrayCliClient
    from alletra_onboard.adapters.array.wsapi_v3_client import WsapiV3Client

_IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
# shownet's data row: the only line that starts with two IPv4s (mgmt IP then netmask).
_IPV4_ROW = re.compile(r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b")
_PARENS = re.compile(r"\(([^)]+)\)")
# Read-only commands, in order: config verification (parsed into field checks) + array health /
# inventory (checkhealth is parsed into issues; the rest are captured raw for operator review).
_CONFIG_COMMANDS = ("showsys -d", "shownet", "showdate")
_HEALTH_COMMANDS = ("checkhealth -svc -detail", "showversion", "showsys", "showcpg", "showpd", "showinventory")
# SPEC-028 R3: the File ports; the file service itself is read over the array's WSAPI v3.
_FILE_COMMANDS = ("showport -file",)
_COMMANDS = _CONFIG_COMMANDS + _HEALTH_COMMANDS + _FILE_COMMANDS


def _kv(text: str) -> dict[str, str]:
    """Parse 'Key : Value' lines into a lowercased-key dict (first occurrence wins).

    Partitions on the FIRST ':' only, so values that themselves contain ':' (e.g. a proxy URL
    'http://host:8080') survive intact.
    """
    out: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        if key and key not in out:
            out[key] = value.strip()
    return out


def _ipv4s(text: str) -> list[str]:
    seen: list[str] = []
    for match in _IPV4.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


def _ip_and_mask(shownet: str) -> tuple[str | None, str | None]:
    """Mgmt IP + netmask live in shownet's table row, not as labeled key:value lines."""
    for line in shownet.splitlines():
        match = _IPV4_ROW.match(line)
        if match:
            return match.group(1), match.group(2)
    return None, None


def _timezone(showdate: str) -> str | None:
    match = _PARENS.search(showdate)
    return match.group(1) if match else None


def _exact(field: str, expected: str, actual: str | None, *, critical: bool = False) -> FieldCheck:
    if not actual:
        status = FieldCheckStatus.NOT_READABLE
    elif str(expected).strip().lower() == str(actual).strip().lower():
        status = FieldCheckStatus.PASS
    else:
        status = FieldCheckStatus.MISMATCH
    return FieldCheck(field=field, expected=str(expected), actual=actual, status=status, critical=critical)


def _contains(field: str, expected: str, actual: str | None, *, critical: bool = False) -> FieldCheck:
    """PASS if `expected` appears within `actual` (the array reports the contact as one combined line)."""
    if not actual:
        status = FieldCheckStatus.NOT_READABLE
    elif str(expected).strip().lower() in str(actual).strip().lower():
        status = FieldCheckStatus.PASS
    else:
        status = FieldCheckStatus.MISMATCH
    return FieldCheck(field=field, expected=str(expected), actual=actual, status=status, critical=critical, match="contains")


def _set(field: str, expected: list[str], found: list[str], *, critical: bool = False) -> FieldCheck:
    want = {v.strip() for v in expected if v.strip()}
    got = {v.strip() for v in found if v.strip()}
    actual = ", ".join(sorted(got)) if got else None
    if not got:
        status = FieldCheckStatus.NOT_READABLE
    elif want <= got:  # every intended value is present (extras are tolerated)
        status = FieldCheckStatus.PASS
    else:
        status = FieldCheckStatus.MISMATCH
    return FieldCheck(field=field, expected=", ".join(sorted(want)), actual=actual, status=status, critical=critical, match="includes")


def _build_checks(item: ArrayWorkItem, outputs: dict[str, str]) -> list[FieldCheck]:
    net, dscc = item.network, item.dscc_setup
    sys_kv = _kv(outputs.get("showsys -d", ""))
    net_kv = _kv(outputs.get("shownet", ""))
    ip, mask = _ip_and_mask(outputs.get("shownet", ""))
    checks = [
        _exact("System name", dscc.system_name, sys_kv.get("system name"), critical=True),
        _exact("Serial number", item.serial_number, sys_kv.get("serial number")),
        _exact("Product number", item.part_number, sys_kv.get("product number")),
        _exact("Management IP", net.mgmt_ipv4, ip, critical=True),
        _exact("Netmask", net.mask, mask, critical=True),
        _exact("Gateway", net.gateway, net_kv.get("default ipv4 route"), critical=True),
        _set("DNS servers", net.dns, _ipv4s(net_kv.get("dns server", ""))),
        _exact("NTP server", net.ntp, net_kv.get("ntp server")),
        _exact("Timezone", net.timezone, _timezone(outputs.get("showdate", ""))),
    ]
    if dscc.contact_email:  # DSCC pushes the support contact onto the array (showsys -d "Contact")
        checks.append(_contains("Support contact", dscc.contact_email, sys_kv.get("contact")))
    return checks


def _consume_health_row(
    mode: str,
    tokens: list[str],
    issues: list[HealthIssue],
    details: dict[str, list[HealthDetail]],
) -> None:
    if tokens[0].isdigit():     # the 'N total M' footer
        return
    if mode == "summary" and len(tokens) >= 3 and tokens[0].isalpha() and tokens[0] != "Checking" and tokens[-1].isdigit():
        issues.append(HealthIssue(component=tokens[0], summary=" ".join(tokens[1:-1]), qty=int(tokens[-1])))
    elif mode == "detail" and len(tokens) >= 4:
        details.setdefault(tokens[0], []).append(
            HealthDetail(identifier=tokens[1], description=" ".join(tokens[2:-1]), resolution=tokens[-1])
        )


def _health_issues(checkhealth: str) -> list[HealthIssue]:
    """Parse `checkhealth -svc -detail` into per-component issue rows.

    The SUMMARY table sits between the 'Component ... Summary Description ... Qty' header and the dashed
    separator; each data row is '<Component> <free-text summary...> <Qty>'. The DETAIL table follows
    ('Component ... Identifier ... Resolution'); each row is '<Component> <Identifier> <description...>
    <Resolution>'. SPEC-011 R1: detail rows are attached to the summary row of their component - they
    are what makes 'vlun - Hosts not connected to a port - 4' actionable - and never counted as issues
    of their own. An array with no issues yields an empty list.
    """
    issues: list[HealthIssue] = []
    details: dict[str, list[HealthDetail]] = {}
    mode: str | None = None
    for line in checkhealth.splitlines():
        if "Summary Description" in line:
            mode = "summary"
            continue
        if "Identifier" in line and "Resolution" in line:
            mode = "detail"
            continue
        stripped = line.strip()
        if mode is None or not stripped:
            continue
        if set(stripped) <= {"-"}:  # dashed separator ends a table
            mode = None if mode == "detail" else "between"
            continue
        _consume_health_row(mode, line.split(), issues, details)
    for issue in issues:
        issue.details = details.get(issue.component, [])
    return issues


_FILE_SERVICE = "File service"
_FILE_PORTS_UP = "File ports up"


def _file_checks(ports: list, report: FileReport | None) -> list[FieldCheck]:
    """SPEC-028 R3: the file service state and its File ports, read-only. No rows on an array with
    no File ports and the file service off (most block arrays). The sheet says nothing about file
    yet, so the service is expected on and every File port up."""
    if report is None:
        return []
    service = report.service
    if service is None:   # not read, or refused: the reason is in Discovery's notes
        service_check = FieldCheck(field=_FILE_SERVICE, expected="on", actual=None,
                                   status=FieldCheckStatus.NOT_READABLE)
    else:
        running = sum(1 for n in service.nodes if n.status == NODE_RUNNING)
        actual = f"on, {running} of {len(service.nodes)} nodes running" if service.enabled else "off"
        service_check = FieldCheck(
            field=_FILE_SERVICE, expected="on", actual=actual,
            status=FieldCheckStatus.PASS if service.running else FieldCheckStatus.MISMATCH,
        )
    up = sum(1 for p in ports if p.link == "up")
    ports_check = FieldCheck(
        field=_FILE_PORTS_UP, expected=f"{len(ports)} of {len(ports)}" if ports else "at least 1",
        actual=f"{up} of {len(ports)}",
        status=FieldCheckStatus.PASS if ports and up == len(ports) else FieldCheckStatus.MISMATCH,
    )
    return [service_check, ports_check]


def _unreadable_file_checks() -> list[FieldCheck]:
    return [FieldCheck(field=name, expected=expected, actual=None, status=FieldCheckStatus.NOT_READABLE)
            for name, expected in ((_FILE_SERVICE, "on"), (_FILE_PORTS_UP, "every File port"))]


def verify(
    item: ArrayWorkItem,
    username: str,
    password: str,
    *,
    client_factory: Callable[[EndpointCreds], ArrayCliClient] = make_array_cli,
    wsapi_v3_factory: Callable[[EndpointCreds], WsapiV3Client] = make_wsapi_v3,
) -> VerificationReport:
    """Connect over SSH, read the config, and compare it to the work item. Never writes. The file
    service is read over the array's WSAPI v3, GETs only, when the array has a file side."""
    creds = EndpointCreds(host=item.network.mgmt_ipv4, username=username, password=SecretStr(password))
    client = client_factory(creds)
    try:
        client.connect()
    except ArrayCliError as exc:
        return VerificationReport(reachable=False, error=str(exc))

    outputs: dict[str, str] = {}
    file_checks: list[FieldCheck] = []
    try:
        for command in _COMMANDS:
            try:
                outputs[command] = client.run(command)
            except ArrayCliError:
                outputs[command] = ""  # that command failed — its fields become "not readable"
        try:
            ports, report = read_file_side(
                client, wsapi_v3_factory(creds),
                parse_showversion(outputs["showversion"]), outputs["showport -file"],
            )
            file_checks = _file_checks(ports, report)
        except (DeviceError, ValueError):  # the file side cannot sink verification
            file_checks = _unreadable_file_checks()
    finally:
        client.close()

    return VerificationReport(
        reachable=True,
        checks=_build_checks(item, outputs) + file_checks,
        health_issues=_health_issues(outputs.get("checkhealth -svc -detail", "")),
        raw=outputs,
    )
