"""Post-init configuration verification (SSH-only) — see docs/adr/0001.

Logs into the initialized array over SSH and compares its on-array running config (read from the
``show*`` commands) against the values the operator intended (the work item). Read-only; the result
is a per-field report, never a gate.

NOTE: the exact ``show*`` output formats for the Alletra MP B10000 (OS 10.4) are calibrated against
the first live array. The extraction below is deliberately tolerant (labeled key:value + IPv4
scanning) and the raw output is returned so the operator can eyeball anything the parser misses.
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
# Commands run, in order. showsys carries identity/location; the rest carry network/time config.
_COMMANDS = ("showsys -d", "shownet", "showdns", "showntp", "showdate")


def _key_values(text: str) -> dict[str, str]:
    """Parse 'Key : Value' / 'Key = Value' lines into a lowercased-key dict."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        for sep in (":", "="):
            if sep in line:
                key, _, value = line.partition(sep)
                key, value = key.strip().lower(), value.strip()
                if key and value and key not in out:
                    out[key] = value
                break
    return out


def _labeled(text: str, labels: tuple[str, ...]) -> str | None:
    """First value on a line whose key matches one of `labels`."""
    kv = _key_values(text)
    for label in labels:
        for key, value in kv.items():
            if label in key:
                return value
    return None


def _ipv4s(text: str) -> list[str]:
    seen: list[str] = []
    for match in _IPV4.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


def _exact(field: str, expected: str, actual: str | None, *, critical: bool = False) -> FieldCheck:
    if not actual:
        status = FieldCheckStatus.NOT_READABLE
    elif str(expected).strip().lower() == str(actual).strip().lower():
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
    elif want <= got:  # every intended value is present (extras like an inherited DNS are fine)
        status = FieldCheckStatus.PASS
    else:
        status = FieldCheckStatus.MISMATCH
    return FieldCheck(field=field, expected=", ".join(sorted(want)), actual=actual, status=status, critical=critical)


def _build_checks(item: ArrayWorkItem, outputs: dict[str, str]) -> list[FieldCheck]:
    net, dscc = item.network, item.dscc_setup
    sysinfo = outputs.get("showsys -d", "")
    netinfo = outputs.get("shownet", "")
    checks = [
        _exact("System name", dscc.system_name, _labeled(sysinfo, ("system name", "name")), critical=True),
        _exact("Serial number", item.serial_number, _labeled(sysinfo, ("serial",))),
        _exact("Management IP", net.mgmt_ipv4, _labeled(netinfo, ("ip address", "ipaddress")) or (_ipv4s(netinfo)[0] if _ipv4s(netinfo) else None), critical=True),
        _exact("Netmask", net.mask, _labeled(netinfo, ("netmask", "subnet", "prefix")), critical=True),
        _exact("Gateway", net.gateway, _labeled(netinfo, ("gateway", "default route")), critical=True),
        _set("DNS servers", net.dns, _ipv4s(outputs.get("showdns", "")) or _ipv4s(netinfo)),
        _set("NTP servers", [net.ntp], _ipv4s(outputs.get("showntp", ""))),
        _exact("Timezone", net.timezone, _labeled(outputs.get("showdate", ""), ("timezone", "time zone"))),
        _exact("System country", dscc.country, _labeled(sysinfo, ("location", "country"))),
    ]
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
