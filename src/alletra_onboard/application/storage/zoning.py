"""SAN zoning: verify the dual-fabric odd/even zoning from the ARRAY (no switch), compute remediation.

Verification is array-side and READ-ONLY (ADR 0004): the fabric name server is zoning-filtered, so
what each array FC target port can SEE *is* its effective zoning, and the array names each host.

    showport                 -> the FC target ports that are 'ready' (odd card-port=>F1, even=>F2)
    showportdev ns <n:s:p>   -> host WWPNs ZONED to that port + logged in, with the host name

A host is correctly zoned when its WWPNs appear on BOTH fabrics. The array can only see hosts that
are logged in, so a host expected (from vCenter) but seen on NEITHER fabric is reported as
**unverified** ("not zoned OR offline") — never silently passed. The switch is NOT needed to verify;
it is only needed to CREATE missing zones (remediation, additive cfgadd->cfgenable), which is gated.

`parse_active_zones` (the switch cfgshow parser) is kept for an optional config-hygiene audit / for
generating remediation, but the verify path no longer requires the switch.
"""

from __future__ import annotations

import re
from typing import Callable

from alletra_onboard.application.storage.clients import make_brocade
from alletra_onboard.domain.storage import (
    DiscoveryReport,
    ExpectedZone,
    Fabric,
    ProvisioningIntent,
    ZoneRemediation,
    ZoningReport,
    normalize_wwpn,
    wwpn_colons,
)

_WWPN_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$")


def _is_wwpn(token: str) -> bool:
    return bool(_WWPN_RE.match(token.strip()))


def _tokens(text: str) -> list[str]:
    """Split a member list on ';' and whitespace into individual tokens (alias names or WWPNs)."""
    return [t for chunk in text.split(";") for t in chunk.split() if t]


def parse_active_zones(cfgshow: str) -> tuple[dict[str, set[str]], str | None]:
    """Parse `cfgshow` into {zone_name: {normalized WWPNs}} for the ACTIVE (effective) config, plus
    the active config name. Aliases are resolved to WWPNs. Falls back to the defined config if no
    effective section is present."""
    aliases: dict[str, set[str]] = {}
    defined_zones: dict[str, list[str]] = {}
    effective_zones: dict[str, list[str]] = {}
    effective_cfg: str | None = None
    defined_cfg: str | None = None

    section: str | None = None
    kind: str | None = None
    name: str | None = None

    for raw in (cfgshow or "").splitlines():
        stripped = raw.strip()
        low = stripped.lower()
        if low.startswith("defined configuration"):
            section, kind, name = "defined", None, None
            continue
        if low.startswith("effective configuration"):
            section, kind, name = "effective", None, None
            continue
        if not stripped:
            continue

        matched = False
        for entity in ("cfg", "zone", "alias"):
            if stripped.startswith(entity + ":"):
                rest = stripped[len(entity) + 1 :].strip()
                parts = rest.split(None, 1)
                kind, name = entity, (parts[0] if parts else "")
                members = parts[1] if len(parts) > 1 else ""
                if entity == "cfg":
                    if section == "effective":
                        effective_cfg = name
                    elif defined_cfg is None:
                        defined_cfg = name
                elif entity == "alias":
                    aliases.setdefault(name, set()).update(
                        normalize_wwpn(t) for t in _tokens(members) if _is_wwpn(t)
                    )
                elif entity == "zone":
                    store = effective_zones if section == "effective" else defined_zones
                    store.setdefault(name, []).extend(_tokens(members))
                matched = True
                break
        if matched:
            continue

        # continuation line: more members for the current entity
        if kind == "alias" and name is not None:
            aliases.setdefault(name, set()).update(
                normalize_wwpn(t) for t in _tokens(stripped) if _is_wwpn(t)
            )
        elif kind == "zone" and name is not None:
            store = effective_zones if section == "effective" else defined_zones
            store.setdefault(name, []).extend(_tokens(stripped))

    raw_zones = effective_zones or defined_zones
    resolved: dict[str, set[str]] = {}
    for zone_name, tokens in raw_zones.items():
        wwpns: set[str] = set()
        for token in tokens:
            if _is_wwpn(token):
                wwpns.add(normalize_wwpn(token))
            elif token in aliases:
                wwpns |= aliases[token]
        resolved[zone_name] = wwpns
    return resolved, (effective_cfg or defined_cfg)


def build_report(intent: ProvisioningIntent, discovery: DiscoveryReport) -> ZoningReport:
    """Verify dual-fabric zoning by COMPUTING over the DiscoveryReport (which already read the array's
    showportdev ns) and reconciling against the expected hosts. No array or switch read here."""
    report = ZoningReport()
    if not discovery.array_ports:
        report.notes.append(
            "No array FC target ports in the discovery — run Discovery first (and check it reached the array)."
        )
        return report

    # The array's per-port nameserver (from discovery) is the effective zoning, by fabric.
    union: dict[Fabric, set[str]] = {"odd": set(), "even": set()}
    name_by_wwpn: dict[str, str] = {}
    for entry in discovery.nameserver:
        union[entry.fabric].add(entry.host_wwpn)
        if entry.host_name:
            name_by_wwpn[entry.host_wwpn] = entry.host_name
    arr_by_fabric: dict[Fabric, list[str]] = {"odd": [], "even": []}
    for port in discovery.array_ports:
        arr_by_fabric[port.fabric].append(port.wwpn)

    # Expected hosts: prefer the vCenter discovery list; otherwise verify whoever the array reports.
    host_wwpns: dict[str, set[str]] = {}
    for hba in discovery.host_hbas:
        host_wwpns.setdefault(hba.host_name, set()).add(normalize_wwpn(hba.wwpn))
    if not host_wwpns:
        for wwpn, name in name_by_wwpn.items():
            host_wwpns.setdefault(name, set()).add(wwpn)
        report.notes.append("No vCenter host list — verifying the hosts the array reports as zoned.")

    switch_by_fabric = {"odd": intent.switch_f1.host, "even": intent.switch_f2.host}
    array_ports_str = {f: ", ".join(sorted(set(arr_by_fabric[f]))) or "(none)" for f in ("odd", "even")}
    for host in sorted(host_wwpns):
        wwns = host_wwpns[host]
        on: dict[Fabric, list[str]] = {f: sorted(wwns & union[f]) for f in ("odd", "even")}
        for fabric in ("odd", "even"):
            report.expected.append(ExpectedZone(
                fabric=fabric,
                switch_host=switch_by_fabric[fabric],
                name=f"{re.sub(r'[^0-9A-Za-z]+', '_', host).strip('_')}_{fabric}",
                host_wwpn=on[fabric][0] if on[fabric] else "(not logged in on this fabric)",
                array_wwpn=array_ports_str[fabric],
                present=bool(on[fabric]),
            ))
        if not on["odd"] and not on["even"]:
            report.unverified_hosts.append(host)
            report.notes.append(
                f"{host}: not seen zoned to the array on EITHER fabric — it is NOT ZONED or the host "
                "is offline / not logged in (the array cannot tell which). Confirm the host is powered "
                "on; if it is, this is a real zoning gap — use the switch to create the zone."
            )
        elif not on["odd"] or not on["even"]:
            report.notes.append(f"{host}: zoned on one fabric only — missing {'even/F2' if on['odd'] else 'odd/F1'}.")

    report.proper = bool(report.expected) and all(z.present for z in report.expected) and not report.unverified_hosts
    report.remediations = _remediations(host_wwpns, union, arr_by_fabric, switch_by_fabric)
    return report


def _remediations(
    host_wwpns: dict[str, set[str]],
    union: dict[Fabric, set[str]],
    arr_by_fabric: dict[Fabric, list[str]],
    switch_by_fabric: dict[str, str],
) -> list[ZoneRemediation]:
    """Best-effort additive remediation for hosts zoned on one fabric but missing the other.

    Uses vCenter-known host WWPNs for the missing fabric (a WWPN the array isn't seeing anywhere). The
    active cfg name is resolved at apply time (placeholder here) — and apply is gated behind the freeze.
    Activated with cfgenable, never cfgsave-alone.
    """
    per_fabric: dict[Fabric, list[str]] = {"odd": [], "even": []}
    for host, wwns in host_wwpns.items():
        on_odd, on_even = wwns & union["odd"], wwns & union["even"]
        if on_odd and on_even:
            continue  # fully zoned
        if not on_odd and not on_even:
            continue  # fully missing/offline -> reported as unverified, not auto-remediated
        missing_fabric: Fabric = "even" if on_odd else "odd"
        # the host's WWPN(s) the array isn't seeing on either fabric -> belong to the missing side
        candidates = sorted(wwns - union["odd"] - union["even"])
        safe = re.sub(r"[^0-9A-Za-z]+", "_", host).strip("_")
        for wwpn in candidates:
            for arr in sorted(set(arr_by_fabric[missing_fabric])):
                per_fabric[missing_fabric].append(
                    f'zonecreate "{safe}_{arr[-3:]}","{wwpn_colons(wwpn)};{wwpn_colons(arr)}"'
                )

    remediations: list[ZoneRemediation] = []
    for fabric in ("odd", "even"):
        cmds = per_fabric[fabric]
        if not cmds:
            continue
        names = ";".join(c.split('"')[1] for c in cmds)
        cmds = cmds + [f'cfgadd "<active_cfg>","{names}"', 'cfgenable "<active_cfg>"']
        remediations.append(ZoneRemediation(fabric=fabric, switch_host=switch_by_fabric[fabric], cfg_name="<active_cfg>", commands=cmds))
    return remediations


def apply_remediation(
    intent: ProvisioningIntent,
    remediations: list[ZoneRemediation],
    *,
    brocade_factory: Callable = make_brocade,
) -> list[tuple[str, str]]:
    """Execute the (already operator-confirmed) additive commands on each fabric. Returns (cmd, output)."""
    creds_by_host = {intent.switch_f1.host: intent.switch_f1, intent.switch_f2.host: intent.switch_f2}
    results: list[tuple[str, str]] = []
    for remediation in remediations:
        creds = creds_by_host.get(remediation.switch_host)
        if creds is None:
            raise ValueError(f"No credentials for switch {remediation.switch_host}")
        with brocade_factory(creds) as switch:
            results.extend(switch.apply(remediation.commands))
    return results
