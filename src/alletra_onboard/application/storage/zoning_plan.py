"""The read-only SAN zoning PLAN (ADR 0004, revised) — an ASSISTED command builder, not an
auto-remediator. The tool NEVER writes to the switch.

It reads both fabric switches READ-ONLY — `nsshow` + `nscamshow` (which fabric each WWPN is online on;
the array can't tell us, because its name-server queries are zone-filtered), `alishow` (the existing
aliases — a WWPN can have several on a shared fabric, so all are kept), and `cfgshow` (the active cfg
per fabric) — and computes, per fabric, the single-initiator-single-target pairs: each host HBA port
on that fabric zoned to every array target port online on it. The operator names the aliases in the UI;
`render_commands` turns the plan + those aliases into the `alicreate` / `zonecreate` / `cfgadd` /
`cfgenable` preview the SAN team applies by hand. See ADR 0004 for the method + naming convention.
"""

from __future__ import annotations

import re
from collections import OrderedDict, defaultdict
from typing import Callable

from alletra_onboard.application.storage.clients import make_brocade
from alletra_onboard.domain.storage import (
    AliasedWwpn,
    DiscoveryReport,
    FabricZonePlan,
    ProvisioningIntent,
    ZoningPlan,
    normalize_wwpn,
    wwpn_colons,
)

_WWPN_COLON = re.compile(r"(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}")


def parse_nameserver(text: str) -> dict[str, dict]:
    """`nsshow`/`nscamshow` -> {normalized WWPN: {'type':…, 'symb':…}} for every ONLINE device. A
    device is here iff it is FLOGI'd — zoned or not — which is how we place an unzoned host on a fabric
    (the array can't; its NS queries are zone-filtered)."""
    devices: dict[str, dict] = {}
    wwpn: str | None = None
    for line in (text or "").splitlines():
        if re.match(r"\s*N\s+\S+;", line):
            parts = line.split(";")
            candidate = normalize_wwpn(parts[2]) if len(parts) > 2 else ""
            wwpn = candidate if len(candidate) == 16 else None
            if wwpn:
                devices.setdefault(wwpn, {"type": "", "symb": ""})
            continue
        if wwpn:
            sym = re.search(r'PortSymb:\s*\[\d+\]\s*"(.*)"', line)
            dev = re.search(r"Device type:\s*(.+)", line)
            if sym:
                devices[wwpn]["symb"] = sym.group(1).strip()
            if dev:
                devices[wwpn]["type"] = dev.group(1).strip()
    return devices


def parse_aliases(text: str) -> dict[str, list[str]]:
    """`alishow` -> {normalized WWPN: [aliases…]}. A WWPN can carry MANY aliases on a shared fabric, so
    EVERY one is kept in order (last-wins would silently pick a wrong/stale name)."""
    out: dict[str, list[str]] = defaultdict(list)
    name: str | None = None
    for line in (text or "").splitlines():
        m = re.match(r"\s*alias:\s+(\S+)", line)
        if m:
            name = m.group(1)
            rest = line[m.end():]
        else:
            rest = line
        if name:
            for tok in _WWPN_COLON.findall(rest):
                wwpn = normalize_wwpn(tok)
                if name not in out[wwpn]:
                    out[wwpn].append(name)
    return dict(out)


def parse_active_cfg(cfgshow: str) -> str:
    """The EFFECTIVE (active) config name from `cfgshow` — never the first *defined* cfg (there are
    decoys like `F2_CFG1` / `F2_CFGclone`)."""
    effective = False
    for line in (cfgshow or "").splitlines():
        if "effective configuration" in line.lower():
            effective = True
            continue
        if effective:
            m = re.match(r"\s*cfg:\s+(\S+)", line)
            if m:
                return m.group(1)
    return ""


def _suggest_alias(existing: list[str], role: str, nsp: str, alias_freq: dict[str, int]) -> str:
    """Pre-fill: prefer an alias UNIQUELY bound to this WWPN — the real per-device name. A *shared* alias
    (bound to many WWPNs on a busy fabric, e.g. `winhost_fc_port_2`, `sy480g108wlrb_0012`) is junk and
    must NOT be suggested: if two hosts share one, their single-init-single-target zone names collide.
    Among the unique candidates, prefer the convention match (the array port's n:s:p code). Else "" so
    the operator types it."""
    if not existing:
        return ""
    pool = [alias for alias in existing if alias_freq.get(alias, 1) <= 1] or existing
    if role == "array" and nsp:
        parts = nsp.split(":")
        code = "N{}S{}P{}".format(*parts) if len(parts) == 3 else ""   # 0:3:1 -> N0S3P1
        digits = "".join(parts)                                        # 031
        for alias in pool:
            if (code and code.lower() in alias.lower()) or (digits and digits in alias):
                return alias
    return pool[0]


def _aliased(wwpn: str, role: str, fabric: str, aliases: dict[str, list[str]],
             alias_freq: dict[str, int], *, nsp: str = "", host_name: str = "") -> AliasedWwpn:
    existing = aliases.get(wwpn, [])
    return AliasedWwpn(
        wwpn=wwpn, display=wwpn_colons(wwpn), role=role, fabric=fabric, nsp=nsp, host_name=host_name,
        existing_aliases=existing, suggested_alias=_suggest_alias(existing, role, nsp, alias_freq),
    )


def build_zoning_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    brocade_factory: Callable = make_brocade,
) -> ZoningPlan:
    """Read both fabrics READ-ONLY and compute the per-fabric single-initiator-single-target plan.
    Writes nothing. A switch that can't be read leaves that fabric empty with a note."""
    plan = ZoningPlan()

    # 1) Read each fabric switch (F1 = odd, F2 = even), read-only.
    ns: dict[str, dict[str, dict]] = {}
    aliases: dict[str, list[str]] = {}
    active_cfg: dict[str, str] = {}
    switch_host: dict[str, str] = {}
    for label, creds in (("F1", intent.switch_f1), ("F2", intent.switch_f2)):
        switch_host[label] = creds.host
        try:
            with brocade_factory(creds) as switch:
                ns[label] = parse_nameserver(switch.nsshow() + "\n" + switch.nscamshow())
                for wwpn, found in parse_aliases(switch.alishow()).items():
                    for alias in found:
                        aliases.setdefault(wwpn, [])
                        if alias not in aliases[wwpn]:
                            aliases[wwpn].append(alias)
                active_cfg[label] = parse_active_cfg(switch.cfgshow())
        except Exception as exc:  # noqa: BLE001 - one unreachable switch must not sink the plan
            ns[label] = {}
            active_cfg[label] = ""
            plan.notes.append(f"Could not read the {label} switch {creds.host}: {exc}")

    # How many distinct WWPNs each alias is bound to — a shared alias is junk (never suggested).
    alias_freq: dict[str, int] = defaultdict(int)
    for names in aliases.values():
        for alias in set(names):
            alias_freq[alias] += 1

    def fabric_of(wwpn: str) -> str:
        return next((label for label in ("F1", "F2") if wwpn in ns.get(label, {})), "")

    # 2) Host HBA WWPNs (vCenter is the authoritative host list) -> host name.
    host_by_wwpn: "OrderedDict[str, str]" = OrderedDict()
    for hba in discovery.host_hbas:
        host_by_wwpn.setdefault(normalize_wwpn(hba.wwpn), hba.host_name)

    # 3) Array FC target ports (discovery), EXCLUDING Remote-Copy-FC and Peer ports (showport Label
    #    "RCFC" / "Peer") — those are replication/peer ports, not host targets. HPE/3PAR guidance:
    #    RCFC ports are excluded from host zoning (they get their own RCFC<->RCFC zones). Only the
    #    ports online in a fabric NS end up placed.
    def _is_host_target(p) -> bool:
        u = p.usage.upper()
        return p.protocol == "fc" and bool(p.wwpn) and u != "RCFC" and not u.startswith("PEER")

    array_ports = [p for p in discovery.array_ports if _is_host_target(p)]
    excluded = [
        f"{p.label} ({p.usage})" for p in discovery.array_ports
        if p.protocol == "fc" and p.wwpn and not _is_host_target(p)
    ]
    if excluded:
        plan.notes.append(
            "Excluded from host zoning (replication/peer ports, not host targets): " + ", ".join(excluded)
        )

    # 4) Per fabric: the host + array WWPNs present, and every SIST pair (each host port x each array port).
    for label in ("F1", "F2"):
        hosts = [
            _aliased(wwpn, "host", label, aliases, alias_freq, host_name=host_by_wwpn[wwpn])
            for wwpn in host_by_wwpn if fabric_of(wwpn) == label
        ]
        ports = [
            _aliased(p.wwpn, "array", label, aliases, alias_freq, nsp=p.label)
            for p in array_ports if fabric_of(p.wwpn) == label
        ]
        pairs = [(host.wwpn, port.wwpn) for host in hosts for port in ports]
        plan.fabrics.append(FabricZonePlan(
            fabric=label, switch_host=switch_host[label], active_cfg=active_cfg.get(label, ""),
            hosts=hosts, array_ports=ports, pairs=pairs,
        ))

    # 5) Host WWPNs on NO fabric -> offline; can't be placed (cable + power, then re-run).
    for wwpn, name in host_by_wwpn.items():
        if not fabric_of(wwpn):
            plan.offline_hosts.append(f"{name} ({wwpn_colons(wwpn)})")
    return plan


def render_commands(plan: ZoningPlan, aliases: dict[str, str]) -> dict[str, list[str]]:
    """Assemble the read-only command preview per fabric from the plan + the operator's chosen aliases
    (`wwpn -> alias name`, falling back to each WWPN's suggested alias). `alicreate` only for aliases
    that do NOT already exist on the switch; SIST `zonecreate`; then `cfgadd` + `cfgenable`. The tool
    never RUNS these — this is the script for the SAN team."""
    out: dict[str, list[str]] = {}
    for fabric in plan.fabrics:
        by_wwpn = {entry.wwpn: entry for entry in (fabric.hosts + fabric.array_ports)}

        def alias_for(wwpn: str) -> str:
            return aliases.get(wwpn) or by_wwpn[wwpn].suggested_alias

        cmds: list[str] = []
        emitted: set[str] = set()
        for entry in fabric.hosts + fabric.array_ports:
            name = alias_for(entry.wwpn)
            if name and name not in entry.existing_aliases and name not in emitted:
                cmds.append(f'alicreate "{name}","{entry.display}"')
                emitted.add(name)

        zone_names: list[str] = []
        for host_wwpn, array_wwpn in fabric.pairs:
            host_alias, array_alias = alias_for(host_wwpn), alias_for(array_wwpn)
            if not host_alias or not array_alias:
                continue
            zone = f"{host_alias}_{array_alias}"
            if zone in zone_names:            # dedupe: colliding aliases must not double a zone
                continue
            zone_names.append(zone)
            cmds.append(f'zonecreate "{zone}","{host_alias};{array_alias}"')

        if zone_names and fabric.active_cfg:
            cmds.append(f'cfgadd "{fabric.active_cfg}","{";".join(zone_names)}"')
            cmds.append(f"cfgenable {fabric.active_cfg}")
        out[fabric.fabric] = cmds
    return out
