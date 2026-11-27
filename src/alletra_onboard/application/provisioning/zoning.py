"""SAN zoning: verify the dual-fabric odd/even zoning from the ARRAY (no switch), compute remediation.

Verification is array-side and READ-ONLY (ADR 0004): the fabric name server is zoning-filtered, so
what each array FC target port can SEE *is* its effective zoning, and the array names each host.

    showport                 -> the FC target ports that are 'ready' (odd card-port=>F1, even=>F2)
    showportdev ns <n:s:p>   -> host WWPNs ZONED to that port + logged in, with the host name

A host is correctly zoned when its WWPNs appear on BOTH fabrics. The array can only see hosts that
are logged in, so a host expected (from vCenter) but seen on NEITHER fabric is reported as
**unverified** ("not zoned OR offline") — never silently passed. The switch is NOT needed to verify.

`_remediations` below builds command TEXT for the missing zones. It is a string generator, nothing
more: this tool has no switch write path at any layer, so a consultant applies what it prints
(ADR 0012). `build_report` also fills `zoned_hosts` — the per-host provisioning gate.

`parse_active_zones` (the switch cfgshow parser) is kept for an optional config-hygiene audit / for
generating remediation, but the verify path no longer requires the switch.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from alletra_onboard.application.provisioning.hosts import union_hosts
from alletra_onboard.domain.discovery import ArrayHost, ArrayPort, DiscoveryReport
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import Fabric, normalize_wwpn, wwpn_colons
from alletra_onboard.domain.zoning import ExpectedZone, ZoneRemediation, ZoningReport

_WWPN_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$")
_CFGSHOW_SECTIONS: tuple[tuple[str, str], ...] = (
    ("defined configuration", "defined"),
    ("effective configuration", "effective"),
)
_CFGSHOW_ENTITIES: tuple[str, ...] = ("cfg", "zone", "alias")


def _is_wwpn(token: str) -> bool:
    return bool(_WWPN_RE.match(token.strip()))


def _tokens(text: str) -> list[str]:
    """Split a member list on ';' and whitespace into individual tokens (alias names or WWPNs)."""
    return [t for chunk in text.split(";") for t in chunk.split() if t]


@dataclass
class _CfgShowState:
    aliases: dict[str, set[str]] = field(default_factory=dict)
    defined_zones: dict[str, list[str]] = field(default_factory=dict)
    effective_zones: dict[str, list[str]] = field(default_factory=dict)
    effective_cfg: str | None = None
    defined_cfg: str | None = None

    def record_cfg(self, section: str | None, name: str) -> None:
        if section == "effective":
            self.effective_cfg = name
        elif self.defined_cfg is None:
            self.defined_cfg = name

    def record_members(self, section: str | None, kind: str, name: str, text: str) -> None:
        if kind == "alias":
            self.aliases.setdefault(name, set()).update(
                normalize_wwpn(t) for t in _tokens(text) if _is_wwpn(t)
            )
        elif kind == "zone":
            store = self.effective_zones if section == "effective" else self.defined_zones
            store.setdefault(name, []).extend(_tokens(text))


def _match_cfgshow_section(stripped: str) -> str | None:
    low = stripped.lower()
    for prefix, section in _CFGSHOW_SECTIONS:
        if low.startswith(prefix):
            return section
    return None


def _parse_cfgshow_entity(stripped: str) -> tuple[str, str, str] | None:
    for entity in _CFGSHOW_ENTITIES:
        if stripped.startswith(entity + ":"):
            rest = stripped[len(entity) + 1 :].strip()
            parts = rest.split(None, 1)
            return entity, (parts[0] if parts else ""), (parts[1] if len(parts) > 1 else "")
    return None


def _resolve_zone_members(
    raw_zones: dict[str, list[str]], aliases: dict[str, set[str]],
) -> dict[str, set[str]]:
    resolved: dict[str, set[str]] = {}
    for zone_name, tokens in raw_zones.items():
        wwpns: set[str] = set()
        for token in tokens:
            if _is_wwpn(token):
                wwpns.add(normalize_wwpn(token))
            elif token in aliases:
                wwpns |= aliases[token]
        resolved[zone_name] = wwpns
    return resolved


@dataclass(frozen=True)
class CfgShowParsed:
    """Strict separation of Defined and Effective sections from `cfgshow` (no fallback)."""

    defined_cfg: str | None
    defined_zones: dict[str, set[str]]
    effective_cfg: str | None
    effective_zones: dict[str, set[str]]
    aliases: dict[str, set[str]]


def parse_cfgshow_strict(cfgshow: str) -> CfgShowParsed:
    """Parse `cfgshow` keeping Defined and Effective strictly separate (no Defined fallback).

    Used by opt-in switch apply pre-flight and post-apply read-back (ADR 0033) so a switch with no
    effective configuration can never be misread as having one active.
    """
    state = _CfgShowState()
    section: str | None = None
    kind: str | None = None
    name: str | None = None

    for raw in (cfgshow or "").splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        new_section = _match_cfgshow_section(stripped)
        if new_section is not None:
            section, kind, name = new_section, None, None
            continue

        header = _parse_cfgshow_entity(stripped)
        if header is not None:
            kind, name, members = header
            if kind == "cfg":
                state.record_cfg(section, name)
            else:
                state.record_members(section, kind, name, members)
            continue

        # continuation line: more members for the current entity
        if kind in ("alias", "zone") and name is not None:
            state.record_members(section, kind, name, stripped)

    return CfgShowParsed(
        defined_cfg=state.defined_cfg,
        defined_zones=_resolve_zone_members(state.defined_zones, state.aliases),
        effective_cfg=state.effective_cfg,
        effective_zones=_resolve_zone_members(state.effective_zones, state.aliases),
        aliases=dict(state.aliases),
    )


def parse_active_zones(cfgshow: str) -> tuple[dict[str, set[str]], str | None]:
    """Parse `cfgshow` into {zone_name: {normalized WWPNs}} for the ACTIVE (effective) config, plus
    the active config name. Aliases are resolved to WWPNs. Falls back to the defined config if no
    effective section is present."""
    parsed = parse_cfgshow_strict(cfgshow)
    zones = parsed.effective_zones or parsed.defined_zones
    cfg = parsed.effective_cfg or parsed.defined_cfg
    return zones, cfg


def _index_fc_logins(
    fc_ports: list[ArrayPort], array_hosts: list[ArrayHost],
) -> tuple[dict[Fabric, set[str]], dict[Fabric, list[str]], dict[str, Fabric]]:
    # Which host WWPNs the ARRAY sees LOGGED IN, by fabric — from showhost. This INCLUDES the
    # array's unclaimed logins (host object not created yet): a WWPN that is logged in is zoned,
    # whether or not anyone has named it. Excluding them reported a cabled, zoned, logged-in host
    # as "not zoned on either fabric" — measured on rack13arcus, host 10.132.30.136.
    port_fabric: dict[str, Fabric] = {p.label: p.fabric for p in fc_ports if p.fabric}
    union: dict[Fabric, set[str]] = {"odd": set(), "even": set()}
    for host in array_hosts:
        for wwpn, ports in host.wwpns.items():
            for nsp in ports:
                fabric = port_fabric.get(nsp)
                if fabric:
                    union[fabric].add(wwpn)
    arr_by_fabric: dict[Fabric, list[str]] = {"odd": [], "even": []}
    for port in fc_ports:
        arr_by_fabric[port_fabric[port.label]].append(port.wwpn)
    return union, arr_by_fabric, port_fabric


def _fallback_logged_in_hosts(
    array_hosts: list[ArrayHost], port_fabric: dict[str, Fabric],
) -> dict[str, set[str]]:
    # The array-only fallback below survives for a run with no vCenter, no sheet hosts and no plan —
    # it verifies whatever is logged in.
    host_wwpns: dict[str, set[str]] = {}
    for host in array_hosts:
        if not host.name:      # the array's UNCLAIMED logins — real WWPNs, but not a named host
            continue
        logged_in = {w for w, ports in host.wwpns.items() if any(port_fabric.get(nsp) for nsp in ports)}
        if logged_in:
            host_wwpns.setdefault(host.name, set()).update(logged_in)
    return host_wwpns


def _record_fc_host_verdict(report: ZoningReport, host: str, on: dict[Fabric, list[str]]) -> None:
    if on["odd"] and on["even"]:
        report.zoned_hosts.append(host)
    elif not on["odd"] and not on["even"]:
        report.unverified_hosts.append(host)
        report.notes.append(
            f"{host}: not seen zoned to the array on EITHER fabric — it is NOT ZONED or the host "
            "is offline / not logged in (the array cannot tell which). Confirm the host is powered "
            "on; if it is, this is a real zoning gap — use the switch to create the zone."
        )
    else:
        report.notes.append(f"{host}: zoned on one fabric only — missing {'even/F2' if on['odd'] else 'odd/F1'}.")


def _evaluate_fc_hosts(
    report: ZoningReport,
    host_wwpns: dict[str, set[str]],
    union: dict[Fabric, set[str]],
    arr_by_fabric: dict[Fabric, list[str]],
    switch_by_fabric: dict[str, str],
) -> None:
    array_ports_str = {f: ", ".join(sorted(set(arr_by_fabric[f]))) or "(none)" for f in ("odd", "even")}
    for host in sorted(host_wwpns):
        wwns = host_wwpns[host]
        on: dict[Fabric, list[str]] = {f: sorted(wwns & union[f]) for f in ("odd", "even")}
        safe = re.sub(r"[^0-9A-Za-z]+", "_", host).strip("_")
        for fabric in ("odd", "even"):
            report.expected.append(ExpectedZone(
                fabric=fabric,
                switch_host=switch_by_fabric[fabric],
                name=f"{safe}_{fabric}",
                host_wwpn=on[fabric][0] if on[fabric] else "(not logged in on this fabric)",
                array_wwpn=array_ports_str[fabric],
                present=bool(on[fabric]),
            ))
        _record_fc_host_verdict(report, host, on)


def build_report(
    intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None = None,
) -> ZoningReport:
    """Verify dual-fabric zoning by COMPUTING over the DiscoveryReport and reconciling against the
    expected hosts. The array-side source is `showhost -d` (discovery.array_hosts) — the array's
    curated host view, so a storage/peer-array port can never be mistaken for a host. No array or
    switch read here.

    Expected hosts (Z-B, 2026-09-14): the SAME union provisioning plans from — vCenter, the sheet's
    Hosts tab, the fabric as the zoning plan recorded it, and any array host the intent puts in a
    host set. Until rc.13 this list was vCenter-only whenever vCenter answered, so a sheet-declared
    host (`arcus-win137`, logged in on F2, created by the run) never appeared in the gate table and
    could never pass the gate: its exports were held back for ever with no way to release them.
    Array hosts NOT in any set are other teams' objects and stay out of the table."""
    report = ZoningReport()
    fc_ports = [p for p in discovery.array_ports if p.protocol == "fc" and p.fabric]
    host_wwpns, iscsi_only = _hosts_in_scope(intent, discovery, zoning_plan)
    if not fc_ports:
        # An array with iSCSI host ports only still has a gate: the IQN logins (BL-44). FC hosts in
        # the same run cannot be checked, and a run with no iSCSI host keeps the old answer.
        _judge_iscsi(report, iscsi_only, discovery)
        if host_wwpns or not iscsi_only:
            report.error = (
                "The discovery has no array FC target ports, so zoning cannot be checked — re-run Discovery "
                "and make sure it reached the array."
            )
        report.proper = not report.error and all(report.iscsi_hosts.values())
        return report

    union, arr_by_fabric, port_fabric = _index_fc_logins(fc_ports, discovery.array_hosts)
    if not host_wwpns and not iscsi_only:
        host_wwpns = _fallback_logged_in_hosts(discovery.array_hosts, port_fabric)
        report.notes.append("No vCenter host list — verifying the hosts the array reports as logged in (showhost).")

    switch_by_fabric = {"odd": intent.switch_f1.host, "even": intent.switch_f2.host}
    _evaluate_fc_hosts(report, host_wwpns, union, arr_by_fabric, switch_by_fabric)
    _judge_iscsi(report, iscsi_only, discovery)
    report.proper = (
        bool(report.expected or report.iscsi_hosts)
        and all(z.present for z in report.expected) and not report.unverified_hosts
        and all(report.iscsi_hosts.values())
    )
    report.remediations = _remediations(host_wwpns, union, arr_by_fabric, switch_by_fabric)
    return report


def summary(report: ZoningReport) -> str:
    """The zoning step's one-line result. A run with no iSCSI host reads exactly as before BL-44."""
    missing = sum(1 for z in report.expected if not z.present)
    ready = len(report.zoned_hosts)
    if not report.iscsi_hosts:
        if report.proper:
            return "Zoning is correct on both fabrics."
        return (f"Zoning needs {missing} zone(s). Build the plan, select the pairs and hand the command set "
                "to the SAN team to apply, then re-verify. "
                + (f"{ready} host(s) are already zoned and can be provisioned now."
                   if ready else "No host is zoned on both fabrics yet, so nothing can be provisioned."))
    if report.proper:
        return ("Zoning is correct on both fabrics, and every iSCSI host is logged in to the array."
                if report.expected else "Every iSCSI host is logged in to the array; no zoning is needed.")
    parts = []
    if missing or report.unverified_hosts:
        parts.append(f"Zoning needs {missing} zone(s). Build the plan, select the pairs and hand the command "
                     "set to the SAN team to apply, then re-verify.")
    waiting = sorted(h for h, ports in report.iscsi_hosts.items() if not ports)
    if waiting:
        parts.append(f"iSCSI not logged in: {', '.join(waiting)}. Connect the server to the array's iSCSI "
                     "ports, then re-verify.")
    parts.append(f"{ready} host(s) can take exports now." if ready else
                 "No host can take an export yet. Hosts, host sets and volumes can still be created; "
                 "the exports wait.")
    return " ".join(parts)


def _hosts_in_scope(
    intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None,
) -> tuple[dict[str, set[str]], dict[str, list[str]]]:
    """Expected hosts: the provisioning union (see build_report), as (FC host -> WWPNs, iSCSI-only
    host -> IQNs). Array hosts in no host set are other teams' objects and are left out."""
    in_a_set = {m for hs in getattr(intent, "host_sets", []) for m in hs.members}
    host_wwpns: dict[str, set[str]] = {}
    iscsi_only: dict[str, list[str]] = {}
    for name, h in union_hosts(discovery, getattr(intent, "declared_hosts", None) or [], zoning_plan)[0].items():
        if h.source == "array" and name not in in_a_set and not in_a_set.intersection(h.aliases):
            continue
        if h.wwpns:
            host_wwpns[name] = {normalize_wwpn(w) for w in h.wwpns}
        elif h.iqns:
            iscsi_only[name] = h.iqns
    return host_wwpns, iscsi_only


def _judge_iscsi(report: ZoningReport, iscsi_only: dict[str, list[str]], discovery: DiscoveryReport) -> None:
    """An iSCSI host needs no zone: it can take an export once the array sees its IQN logged in."""
    iqn_ports = {iqn.lower(): ports for ah in discovery.array_hosts for iqn, ports in ah.iqns.items()}
    for host in sorted(iscsi_only):
        ports = sorted({p for iqn in iscsi_only[host] for p in iqn_ports.get(iqn.lower(), [])})
        report.iscsi_hosts[host] = ports
        if ports:
            report.zoned_hosts.append(host)
            report.notes.append(f"{host}: iSCSI, logged in on {', '.join(ports)} — no zoning needed; exports allowed.")
        else:
            report.notes.append(f"{host}: iSCSI, IQN not logged in on the array — exports to it are held back.")


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
