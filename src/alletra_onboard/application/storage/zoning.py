"""SAN zoning: verify the dual-fabric odd/even zoning and compute additive remediation.

The rule (fixed best practice, ADR 0004): odd array ports zone on the odd switch (F1), even ports on
the even switch (F2); each zone pairs one host HBA WWPN with one array target-port WWPN on the SAME
fabric (single-initiator-single-target). A pairing is "present" if the switch's active config already
has a zone whose member WWPNs include both.

Remediation is **additive only** and activated with **cfgenable** (never cfgsave-alone — deep-research
verified pitfall): `zonecreate` the missing pairings, `cfgadd` them to the active config, `cfgenable`.

The cfgshow parser is deliberately tolerant of FOS formatting; calibrate it against a live `cfgshow`
the way the array verification parsers were calibrated (see the runbook).
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


def _zone_name(host_name: str, node: int, slot: int, card_port: int) -> str:
    """A stable zone name: <sanitized host>_<n><s><p> (matches the lab's _031/_131 suffix style)."""
    safe = re.sub(r"[^0-9A-Za-z]+", "_", host_name).strip("_")
    return f"{safe}_{node}{slot}{card_port}"


def expected_zones(intent: ProvisioningIntent, discovery: DiscoveryReport) -> list[ExpectedZone]:
    """One ExpectedZone per (host HBA WWPN, array port WWPN) pair on the SAME fabric."""
    zones: list[ExpectedZone] = []
    fabrics: list[tuple[Fabric, str]] = [
        ("odd", intent.switch_f1.host),
        ("even", intent.switch_f2.host),
    ]
    for fabric, switch_host in fabrics:
        ports = [p for p in discovery.array_ports if p.fabric == fabric]
        hbas = [h for h in discovery.host_hbas if h.fabric == fabric]
        for hba in hbas:
            for port in ports:
                zones.append(
                    ExpectedZone(
                        fabric=fabric,
                        switch_host=switch_host,
                        name=_zone_name(hba.host_name, port.node, port.slot, port.card_port),
                        host_wwpn=hba.wwpn,
                        array_wwpn=port.wwpn,
                    )
                )
    return zones


def build_report(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    brocade_factory: Callable = make_brocade,
) -> ZoningReport:
    """Verify zoning across both fabrics and compute the additive remediation for what's missing."""
    report = ZoningReport()
    report.expected = expected_zones(intent, discovery)

    active_by_switch: dict[str, tuple[dict[str, set[str]], str | None]] = {}
    for fabric, creds in (("odd", intent.switch_f1), ("even", intent.switch_f2)):
        try:
            with brocade_factory(creds) as switch:
                active_by_switch[creds.host] = parse_active_zones(switch.cfgshow())
        except Exception as exc:  # noqa: BLE001
            report.notes.append(f"{fabric} switch ({creds.host}) cfgshow failed: {exc}")

    if not report.expected:
        report.notes.append(
            "No expected zones computed — discovery found no host/array WWPNs on a shared fabric "
            "(check discovery notes: cabling, vCenter, or switch reachability)."
        )

    # Mark presence
    for zone in report.expected:
        active = active_by_switch.get(zone.switch_host)
        if active is None:
            continue  # couldn't read this switch — leave present=False, noted above
        zones_map, _cfg = active
        pair = {zone.host_wwpn, zone.array_wwpn}
        zone.present = any(pair <= members for members in zones_map.values())

    report.proper = bool(report.expected) and all(z.present for z in report.expected)
    report.remediations = _remediations(report, intent, active_by_switch)
    return report


def _remediations(
    report: ZoningReport,
    intent: ProvisioningIntent,
    active_by_switch: dict[str, tuple[dict[str, set[str]], str | None]],
) -> list[ZoneRemediation]:
    """Group the missing zones per fabric into an additive command batch (zonecreate→cfgadd→cfgenable)."""
    by_switch: dict[str, tuple[Fabric, list[ExpectedZone]]] = {}
    for zone in report.expected:
        if zone.present:
            continue
        by_switch.setdefault(zone.switch_host, (zone.fabric, []))[1].append(zone)

    remediations: list[ZoneRemediation] = []
    for switch_host, (fabric, missing) in by_switch.items():
        active = active_by_switch.get(switch_host)
        cfg_name = (active[1] if active else None) or "<active_cfg>"
        commands = [
            f'zonecreate "{z.name}","{wwpn_colons(z.host_wwpn)};{wwpn_colons(z.array_wwpn)}"'
            for z in missing
        ]
        zone_list = ";".join(z.name for z in missing)
        commands.append(f'cfgadd "{cfg_name}","{zone_list}"')
        commands.append(f'cfgenable "{cfg_name}"')  # activates AND persists; never cfgsave-alone
        remediations.append(
            ZoneRemediation(fabric=fabric, switch_host=switch_host, cfg_name=cfg_name, commands=commands)
        )
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
