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
from typing import Callable

from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    FieldCheck,
    FieldCheckStatus,
    VerificationReport,
)

_IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
# shownet's data row: the only line that starts with two IPv4s (mgmt IP then netmask).
_IPV4_ROW = re.compile(r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b")
_PARENS = re.compile(r"\(([^)]+)\)")
# Read-only commands, in order. Everything we verify is read from these three.
_COMMANDS = ("showsys -d", "shownet", "showdate")


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
    return FieldCheck(field=field, expected=str(expected), actual=actual, status=status, critical=critical)


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
    return FieldCheck(field=field, expected=", ".join(sorted(want)), actual=actual, status=status, critical=critical)


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


def verify(
    item: ArrayWorkItem,
    username: str,
    password: str,
    *,
    client_factory: Callable[..., ArrayCliClient] = ArrayCliClient,
) -> VerificationReport:
    """Connect over SSH, read the config, and compare it to the work item. Never writes."""
    client = client_factory(host=item.network.mgmt_ipv4, username=username, password=password)
    try:
        client.connect()
    except ArrayCliError as exc:
        return VerificationReport(reachable=False, error=str(exc))

    outputs: dict[str, str] = {}
    try:
        for command in _COMMANDS:
            try:
                outputs[command] = client.run(command)
            except ArrayCliError:
                outputs[command] = ""  # that command failed — its fields become "not readable"
    finally:
        client.close()

    return VerificationReport(reachable=True, checks=_build_checks(item, outputs), raw=outputs)
