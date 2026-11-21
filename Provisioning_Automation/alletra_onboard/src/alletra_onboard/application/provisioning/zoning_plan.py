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
from collections.abc import Callable
from dataclasses import dataclass, field

from alletra_onboard.application.provisioning.clients import make_brocade
from alletra_onboard.application.provisioning.hosts import (
    declared_mismatches,
    resolve_declared_hosts,
)
from alletra_onboard.application.provisioning.zoning import parse_active_zones
from alletra_onboard.domain.discovery import ArrayPort, DiscoveryReport
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds, normalize_wwpn, wwpn_colons
from alletra_onboard.domain.zoning import (
    FOS_NAME_MAX,
    AliasedWwpn,
    FabricZonePlan,
    NsDevice,
    ZoningPlan,
    fos_name_problem,
    fos_name_suggestion,
    fos_name_warning,
    proposed_array_alias,
    proposed_host_alias,
    suggest_alias,
)

_WWPN_COLON = re.compile(r"(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}")


# An array port's PortSymb self-describes it: "SGHD44LQLS - 0:3:1 - HPE64004-B" (serial, n:s:p).
_ARRAY_PORT_SYMB = re.compile(r"^(\S+) - (\d+:\d+:\d+) - ")

# Installer / OS default host names: many servers advertise them at once (the captured fabrics carry
# 29 WWPNs under localhost.bgl1…), so as a name they would merge strangers into one array host.
_PLACEHOLDER_HOSTNAMES = {"localhost", "smartstart", "ubuntu", "ubuntu-server"}


def _host_identity(advertised: str) -> str:
    return "" if advertised.rstrip(".").split(".")[0].lower() in _PLACEHOLDER_HOSTNAMES else advertised


def _apply_ns_port_symb(device: NsDevice, value: str) -> None:
    device.port_symb = value.strip()
    if arr := _ARRAY_PORT_SYMB.match(device.port_symb):
        device.array_serial, device.array_nsp = arr.group(1), arr.group(2)


def _apply_ns_node_symb(device: NsDevice, value: str) -> None:
    device.node_symb = value.strip()
    if hn := re.search(r"\bHN:(\S+)", device.node_symb):
        device.host_name = _host_identity(hn.group(1))
    if os_ := re.search(r"\bOS:(.+)$", device.node_symb):
        device.os = os_.group(1).strip()


def _apply_ns_device_type(device: NsDevice, value: str) -> None:
    device.device_type = value.strip()


def _apply_ns_permanent_wwpn(device: NsDevice, value: str) -> None:
    device.permanent_wwpn = normalize_wwpn(value)


_NS_FIELDS: tuple[tuple[re.Pattern[str], Callable[[NsDevice, str], None]], ...] = (
    (re.compile(r'PortSymb:\s*\[\d+\]\s*"(.*)"'), _apply_ns_port_symb),
    (re.compile(r'NodeSymb:\s*\[\d+\]\s*"(.*)"'), _apply_ns_node_symb),
    (re.compile(r"Device type:\s*(.+)"), _apply_ns_device_type),
    (re.compile(r"Permanent Port Name:\s*(\S+)"), _apply_ns_permanent_wwpn),
)


def parse_nameserver(text: str) -> dict[str, NsDevice]:
    """`nsshow`/`nscamshow` -> {normalized WWPN: NsDevice} for every ONLINE device. A device is here
    iff it is FLOGI'd — zoned or not — which is how we place an unzoned host on a fabric (the array
    can't; its NS queries are zone-filtered).

    Beyond placement, the entries carry identity (see NsDevice): host name + OS from NodeSymb
    ``HN:``/``OS:``, an array port's serial + n:s:p from PortSymb, and the initiator/target/NPIV
    classification — all measured against live captures in tests/fixtures/vz_fabric."""
    devices: dict[str, NsDevice] = {}
    current: NsDevice | None = None
    for line in (text or "").splitlines():
        if re.match(r"\s*N\s+\S+;", line):
            parts = line.split(";")
            wwpn = normalize_wwpn(parts[2]) if len(parts) > 2 else ""
            current = devices.setdefault(wwpn, NsDevice(wwpn=wwpn)) if len(wwpn) == 16 else None
            continue
        if current is None:
            continue
        for pattern, apply_field in _NS_FIELDS:
            if m := pattern.search(line):
                apply_field(current, m.group(1))
                break
    return devices


def parse_aliases(text: str) -> dict[str, list[str]]:
    """`alishow` -> {normalized WWPN: [aliases…]}. A WWPN can carry MANY aliases on a shared fabric, so
    EVERY one is kept in order (last-wins would silently pick a wrong/stale name).

    `alishow` does NOT print only aliases: on a real fabric it dumps the whole zone database — the
    defined cfg + zone blocks, then the alias blocks, then the ENTIRE effective configuration, whose
    zone members are raw WWPNs. So collect WWPNs only while inside an alias block, and stop at the
    effective section. Measured on the live F1 capture (tests/fixtures/vz_fabric) before this guard:
    every WWPN in the effective section was attributed to whichever alias happened to be listed last —
    `winhost_fc_port_2` came back bound to 888 WWPNs when the zone database binds it to exactly one.
    (That pollution is also how an honest per-device alias can be misjudged as shared junk.)"""
    out: dict[str, list[str]] = defaultdict(list)
    name: str | None = None
    for line in (text or "").splitlines():
        if "effective configuration" in line.lower():
            break  # aliases live in the DEFINED section; what follows is active zones as raw WWPNs
        m = re.match(r"\s*alias:\s+(\S+)", line)
        if m:
            name = m.group(1)
            rest = line[m.end():]
        elif re.match(r"\s*(?:zone|cfg):", line):
            name = None  # a new non-alias block ends the current alias's member list
            continue
        else:
            rest = line
        if name:
            for tok in _WWPN_COLON.findall(rest):
                wwpn = normalize_wwpn(tok)
                if name not in out[wwpn]:
                    out[wwpn].append(name)
    return dict(out)


def parse_defined_names(text: str) -> set[str]:
    """Every alias, zone and cfg name in the DEFINED zone database (`cfgshow` / `alishow`). FOS will
    not create a second object of a name it already has, so an `alicreate` of one fails and the
    following `zonecreate` silently uses the EXISTING object's members."""
    names: set[str] = set()
    for line in (text or "").splitlines():
        if "effective configuration" in line.lower():
            break
        if m := re.match(r"\s*(?:alias|zone|cfg):\s+(\S+)", line):
            names.add(m.group(1))
    return names


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


def parse_switchshow(text: str) -> tuple[str, int | None]:
    """`switchshow` -> (switchName, switchDomain). Either may be missing on a partial read."""
    name, domain = "", None
    for line in (text or "").splitlines():
        if m := re.match(r"\s*switchName:\s*(\S+)", line):
            name = m.group(1)
        elif m := re.match(r"\s*switchDomain:\s*(\d+)", line):
            domain = int(m.group(1))
    return name, domain


def parse_fabricshow(text: str) -> tuple[str, dict[int, str]]:
    """`fabricshow` -> (fabric name, {domain id: switch name}). One row per switch in the fabric:
    ``  12: fffc0c 10:00:88:94:71:af:36:a0 10.132.30.11 0.0.0.0 "SN6000B-SANB-ZR07U40"`` (the
    principal switch carries a leading ``>``). Measured on rack13 2026-09-12: both declared switches
    were ISL'd to a second switch each, and one host the plan offered lived on that other switch."""
    fabric_name = ""
    switches: dict[int, str] = {}
    for line in (text or "").splitlines():
        if m := re.match(r"\s*Fabric Name:\s*(.+?)\s*$", line):
            fabric_name = m.group(1)
        elif m := re.match(r'\s*(\d+):\s+fffc[0-9a-f]+\s+\S+\s+\S+\s+\S+\s+>?"([^"]+)"', line):
            switches[int(m.group(1))] = m.group(2)
    return fabric_name, switches


def parse_nscam_domains(text: str) -> dict[str, int]:
    """`nscamshow` -> {normalized WWPN: domain id of the REMOTE switch it is logged into}. The output
    is grouped: ``Switch entry for 32`` then that switch's ``N ...;`` device lines."""
    out: dict[str, int] = {}
    domain: int | None = None
    for line in (text or "").splitlines():
        if m := re.match(r"\s*Switch entry for\s+(\d+)", line):
            domain = int(m.group(1))
        elif domain is not None and re.match(r"\s*N\s+\S+;", line):
            parts = line.split(";")
            wwpn = normalize_wwpn(parts[2]) if len(parts) > 2 else ""
            if len(wwpn) == 16:
                out[wwpn] = domain
    return out


def _node_of(nsp: str) -> int | None:
    parts = nsp.split(":")
    return int(parts[0]) if len(parts) == 3 and parts[0].isdigit() else None


def _caution(port: ArrayPort) -> str:
    """Warn on the array's own Type, never on the Label.

    The Label is free text an operator typed. On AlletraMP_D22U27 three FC ports carry
    "peer port", "peer 1:3:1" and "Peer_port" — three spellings on one array — and all three are
    Type `host`, actively serving hosts. Keying the warning off that string flagged exactly the
    wrong ports, while the array's genuine peer ports are IP and never reach this code at all.
    """
    if port.port_type and port.port_type not in ("host", "free"):
        return f"Type {port.port_type}: the array does not report this as host-serving"
    return ""


@dataclass
class _FabricRead:
    """Everything read from one fabric switch (F1 or F2), read-only."""

    label: str
    switch_host: str
    ns: dict[str, NsDevice] = field(default_factory=dict)
    local_ns: dict[str, NsDevice] = field(default_factory=dict)  # nsshow ONLY: devices on the declared switch itself
    # Aliases are PER FABRIC. One flat pool looks harmless but is wrong twice over: an alias that
    # exists only on F2 would suppress the F1 alicreate (leaving F1's zonecreate referencing an
    # undefined name, which the switch rejects), and "uniquely bound" for suggestions must mean
    # unique on ITS fabric. Measured live 2026-08-15: 41 alias names exist on BOTH lab fabrics.
    aliases: dict[str, list[str]] = field(default_factory=dict)
    alias_freq: dict[str, int] = field(default_factory=dict)
    active_cfg: str = ""
    active_zones: dict[str, set[str]] = field(default_factory=dict)      # {zone name: member WWPNs}
    defined: set[str] = field(default_factory=set)
    switch_name: str = ""
    fabric_name: str = ""
    fabric_switches: dict[int, str] = field(default_factory=dict)        # {domain: switch name} (fabricshow)
    remote_domain: dict[str, int] = field(default_factory=dict)          # {wwpn: remote domain} (nscamshow)

    def remote_switch(self, wwpn: str) -> str:
        # Placed via nscamshow => plugged into another switch of this fabric; name it so the
        # operator can see WHY a host they never cabled to the declared switch is offered here.
        if wwpn in self.local_ns or wwpn not in self.remote_domain:
            return ""
        domain = self.remote_domain[wwpn]
        return self.fabric_switches.get(domain) or f"domain {domain}"

    def host_entry(self, wwpn: str, candidates: _HostCandidates) -> AliasedWwpn:
        existing = self.aliases.get(wwpn, [])
        host_name = candidates.name[wwpn]
        return AliasedWwpn(
            wwpn=wwpn, display=wwpn_colons(wwpn), role="host", fabric=self.label,
            host_name=host_name, host_source=candidates.source.get(wwpn, ""),
            os=candidates.os.get(wwpn, ""), placed_on_switch=self.remote_switch(wwpn),
            existing_aliases=existing,
            suggested_alias=suggest_alias(existing, "host", "", self.alias_freq),
            proposed_alias="" if existing else proposed_host_alias(host_name, wwpn, candidates.hba_index.get(wwpn, 1)),
        )

    def array_entry(self, wwpn: str, *, nsp: str = "", serial: str = "", caution: str = "") -> AliasedWwpn:
        existing = self.aliases.get(wwpn, [])
        return AliasedWwpn(
            wwpn=wwpn, display=wwpn_colons(wwpn), role="array", fabric=self.label, nsp=nsp, node=_node_of(nsp),
            caution=caution, existing_aliases=existing,
            suggested_alias=suggest_alias(existing, "array", nsp, self.alias_freq),
            proposed_alias="" if existing else proposed_array_alias(nsp, wwpn, serial),
        )


def _read_fabric(label: str, creds: EndpointCreds, brocade_factory: Callable, plan: ZoningPlan) -> _FabricRead:
    fab = _FabricRead(label=label, switch_host=creds.host)
    try:
        with brocade_factory(creds) as switch:
            nsshow_text, nscam_text = switch.nsshow(), switch.nscamshow()
            fab.local_ns = parse_nameserver(nsshow_text)
            fab.ns = parse_nameserver(nsshow_text + "\n" + nscam_text)
            fab.remote_domain = parse_nscam_domains(nscam_text)
            alishow_text, cfg_text = switch.alishow(), switch.cfgshow()
            for wwpn, found in parse_aliases(alishow_text).items():
                per = fab.aliases.setdefault(wwpn, [])
                per.extend(a for a in found if a not in per)
            # How many distinct WWPNs each alias is bound to ON ITS FABRIC — a shared alias is junk (never suggested).
            freq: dict[str, int] = defaultdict(int)
            for names in fab.aliases.values():
                for alias in set(names):
                    freq[alias] += 1
            fab.alias_freq = dict(freq)
            fab.defined = parse_defined_names(alishow_text) | parse_defined_names(cfg_text)
            fab.active_cfg = parse_active_cfg(cfg_text)
            fab.active_zones, _ = parse_active_zones(cfg_text)
            plan.active_zones[f"the {label} switch {creds.host}"] = {
                zone: sorted(members) for zone, members in fab.active_zones.items()
            }
            _note_switch_anomalies(fab, creds.host, plan)
            _read_switch_identity(switch, fab)
    except DeviceError as exc:
        fab.ns, fab.local_ns, fab.remote_domain, fab.active_cfg, fab.active_zones = {}, {}, {}, "", {}
        plan.active_zones[f"the {label} switch {creds.host or '(none on the sheet)'}"] = None
        plan.notes.append(f"Could not read the {label} switch {creds.host}: {exc}")
    return fab


def _read_switch_identity(switch, fab: _FabricRead) -> None:
    # Identity reads are optional.
    try:
        fab.switch_name, _domain = parse_switchshow(switch.read("switchshow"))
    except DeviceError:
        fab.switch_name = ""
    try:
        fab.fabric_name, fab.fabric_switches = parse_fabricshow(switch.fabricshow())
    except DeviceError:
        fab.fabric_name, fab.fabric_switches = "", {}


def _note_switch_anomalies(fab: _FabricRead, host: str, plan: ZoningPlan) -> None:
    if not fab.active_cfg:
        plan.notes.append(
            f"No effective zoning configuration was read on the {fab.label} switch {host} "
            "(cfgshow), so its command set has no cfgadd / cfgenable: zones created there take "
            "no effect until they are in an enabled configuration. Check cfgactvshow on the "
            "switch and ask the SAN owner before pasting."
        )
    if not fab.local_ns:
        # Measured live 2026-08-15: one plan run got an empty local NS from a healthy switch
        # (transient), so its resident array ports vanished from the plan with no explanation. An
        # empty LOCAL name server on a production switch is an anomaly to report, not a fact to
        # silently accept.
        plan.notes.append(
            f"The {fab.label} switch {host} returned no LOCAL name-server entries "
            "(nsshow) — devices plugged into that switch (typically this deployment's "
            "array ports) cannot be placed. Likely transient: rebuild the plan."
        )


def _note_fabric_overlap(f1: _FabricRead, f2: _FabricRead, plan: ZoningPlan) -> None:
    # The declared switches must front two DISJOINT fabrics. If they are ISL'd into ONE merged fabric,
    # first-match placement lands every device on F1 and the "dual-fabric" plan is fiction — the exact
    # silent failure the meshed-lab episode produced. Measured healthy baseline 2026-08-15: 73 of ~955
    # WWPNs (≈8%) appear in both name servers (stale nscamshow cache), so a small overlap only warrants
    # a verify note; a large one means merged.
    seen_f1, seen_f2 = set(f1.ns), set(f2.ns)
    overlap = seen_f1 & seen_f2
    if not (seen_f1 and seen_f2 and overlap):
        return
    share = len(overlap) / min(len(seen_f1), len(seen_f2))
    if share > 0.2:
        plan.notes.append(
            f"The declared F1 and F2 switches see {len(overlap)} of the same device WWPNs "
            f"({share:.0%} of the smaller fabric) — they appear to be ONE merged fabric, not a "
            "dual fabric. Fabric placement below is unreliable (dual-seen devices land on F1). "
            "Fix the fabric split (or declare switches from two separate fabrics) before acting "
            "on this plan."
        )
    else:
        plan.notes.append(
            f"{len(overlap)} device WWPN(s) appear in BOTH fabrics' name servers (likely stale "
            "nscamshow cache) — each is placed on F1. Verify placement for any of these you "
            "intend to zone."
        )


_SOURCE_LABELS = {"sheet": "the sheet", "array": "array logins", "switch": "the fabric name servers"}


@dataclass
class _HostCandidates:
    """Host HBA WWPN union across vCenter, sheet, array logins and switch local name servers."""

    name: OrderedDict[str, str] = field(default_factory=OrderedDict)
    source: dict[str, str] = field(default_factory=dict)
    os: dict[str, str] = field(default_factory=dict)
    hba_index: dict[str, int] = field(default_factory=dict)

    def claim(self, wwpn: str, host_name: str, src: str, os_: str = "") -> None:
        if wwpn not in self.name:
            self.name[wwpn] = host_name
            self.source[wwpn] = src
            self.os[wwpn] = os_
        elif host_name and not self.name[wwpn]:
            self.name[wwpn] = host_name
            self.source[wwpn] = src
        if os_ and not self.os.get(wwpn):
            self.os[wwpn] = os_

    def index_hbas(self) -> None:
        # For the convention pre-fill: which HBA of its host each WWPN is (1-based, by WWPN order).
        by_host: dict[str, list[str]] = defaultdict(list)
        for wwpn, host_name in self.name.items():
            by_host[host_name or wwpn].append(wwpn)
        for wwpns in by_host.values():
            for i, wwpn in enumerate(sorted(wwpns), start=1):
                self.hba_index[wwpn] = i


def _collect_host_candidates(
    intent: ProvisioningIntent, discovery: DiscoveryReport, fabrics: tuple[_FabricRead, _FabricRead], plan: ZoningPlan,
) -> _HostCandidates:
    # 2) Host HBA WWPNs — the UNION of every source that can name or see an initiator, in order of
    #    trust for the NAME: vCenter (ESXi, authoritative for its hosts), the sheet's Hosts tab (the
    #    customer's Windows/Linux servers), the array's own host objects (showhost -d), and finally
    #    the DECLARED switches' LOCAL name servers (`nsshow`, never the fabric-wide `nscamshow`,
    #    which on a shared SAN would drag in every other team's initiators).
    #
    #    Until 2026-09-12 the list was vCenter-only whenever vCenter answered, with the switches
    #    consulted only as a fallback. Measured live on rack13arcus that day: a Windows host's
    #    unzoned HBA (51:40:2e:c0:20:89:cc:1e) and two other live initiators sat in the declared
    #    switches' name servers and the step could not zone any of them — the exact mixed-estate
    #    case (Windows/Linux beside a vCenter) the tool exists for. A first source names a WWPN; a
    #    later one only fills a name that is still empty. Array UNCLAIMED logins carry no name.
    cand = _HostCandidates()
    for hba in discovery.host_hbas:
        cand.claim(normalize_wwpn(hba.wwpn), hba.host_name, "vcenter", hba.os or "")
    vcenter_count = len(cand.name)
    declared_raw = getattr(intent, "declared_hosts", None) or []
    for declared in resolve_declared_hosts(declared_raw, discovery, canonical_names=True)[0]:
        for wwpn in declared.wwpns:
            cand.claim(normalize_wwpn(wwpn), declared.name, "sheet", declared.os or "")
    for array_host in discovery.array_hosts:
        for wwpn in array_host.wwpns:
            cand.claim(normalize_wwpn(wwpn), array_host.name, "array")
    for fab in fabrics:
        for wwpn, device in fab.local_ns.items():
            if device.is_physical_initiator:
                cand.claim(wwpn, device.host_name, "switch", device.os)
    # SPEC-014 R6: a typed WWPN the server does not report would be zoned to nothing.
    plan.notes.extend(declared_mismatches(declared_raw, discovery))
    _note_non_vcenter_hosts(cand, vcenter_count, plan)
    cand.index_hbas()
    return cand


def _note_non_vcenter_hosts(cand: _HostCandidates, vcenter_count: int, plan: ZoningPlan) -> None:
    added = len(cand.name) - vcenter_count
    if not vcenter_count and cand.name:
        plan.notes.append(
            f"vCenter reported no hosts — {len(cand.name)} host port(s) were identified from "
            "the sheet, the array's logins and the declared switches' own name servers instead "
            "(names from the fabric where the HBA advertises one)."
        )
    elif added:
        by_source: dict[str, int] = defaultdict(int)
        for wwpn in cand.name:
            if cand.source[wwpn] != "vcenter":
                by_source[cand.source[wwpn]] += 1
        detail = ", ".join(f"{n} from {_SOURCE_LABELS[s]}" for s, n in by_source.items())
        plan.notes.append(
            f"{added} host port(s) not known to vCenter were added ({detail}). Unnamed ones are "
            "shown by WWPN — name them on the sheet's Hosts tab if you intend to zone them."
        )


def _build_fabric_plan(
    fab: _FabricRead,
    fabric_of: Callable[[str], str],
    cand: _HostCandidates,
    array_ports: list[ArrayPort],
) -> FabricZonePlan:
    hosts = [fab.host_entry(wwpn, cand) for wwpn in cand.name if fabric_of(wwpn) == fab.label]
    ports = [
        fab.array_entry(p.wwpn, nsp=p.label, caution=_caution(p),
                        serial=(dev.array_serial if (dev := fab.ns.get(p.wwpn)) else ""))
        for p in array_ports if fabric_of(p.wwpn) == fab.label
    ]
    pairs = [(host.wwpn, port.wwpn) for host in hosts for port in ports]
    # The DELTA: a candidate pair is already zoned iff some zone in this fabric's effective
    # config contains BOTH WWPNs (aliases were resolved by parse_active_zones). Proven against
    # the live VZ captures: all 12 host<->array pairs land in already_zoned, so the preview
    # creates nothing on a bed that is already correct.
    already: list[tuple[str, str]] = []
    zone_names: dict[str, list[str]] = {}
    for pair in pairs:
        if covering := [z for z, members in fab.active_zones.items() if pair[0] in members and pair[1] in members]:
            already.append(pair)
            zone_names[f"{pair[0]}|{pair[1]}"] = covering
    return FabricZonePlan(
        fabric=fab.label, switch_host=fab.switch_host, active_cfg=fab.active_cfg,
        switch_name=fab.switch_name, fabric_name=fab.fabric_name, switch_count=len(fab.fabric_switches),
        hosts=hosts, array_ports=ports, pairs=pairs, already_zoned=already, zone_names=zone_names,
        defined_names=sorted(fab.defined),
    )


def _populate_peer_block(
    fabric_plan: FabricZonePlan,
    fab: _FabricRead,
    peer_pairs: list[tuple[str, str]],
    peer_nsps: dict[str, str],
    own_serial: str,
) -> None:
    on_fabric = [(p, s) for p, s in peer_pairs if p in fab.ns and s in fab.ns]
    peers: list[AliasedWwpn] = []
    sources: list[AliasedWwpn] = []
    for peer, source in on_fabric:
        if all(e.wwpn != peer for e in peers):
            entry = fab.array_entry(peer, nsp=peer_nsps.get(peer, ""), serial=own_serial)
            if entry.proposed_alias:
                entry.proposed_alias = f"{entry.proposed_alias}_PEER"[:FOS_NAME_MAX]
            peers.append(entry)
        if all(e.wwpn != source for e in sources):
            device = fab.ns[source]
            sources.append(fab.array_entry(source, nsp=device.array_nsp, serial=device.array_serial))
    fabric_plan.peer_ports = peers
    fabric_plan.sources = sources
    fabric_plan.peer_pairs = on_fabric
    fabric_plan.peer_already_zoned = [
        pair for pair in on_fabric
        if any(pair[0] in members and pair[1] in members for members in fab.active_zones.values())
    ]


def build_zoning_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    brocade_factory: Callable = make_brocade,
    peer_pairs: list[tuple[str, str]] | None = None,
    peer_nsps: dict[str, str] | None = None,
) -> ZoningPlan:
    """Read both fabrics READ-ONLY and compute the per-fabric single-initiator-single-target plan.
    Writes nothing. A switch that can't be read leaves that fabric empty with a note.

    `peer_pairs` (SPEC-025 R7): (peer port WWPN, source array port WWPN) from `peer_ports.peer_zone_pairs`,
    the peer WWPN read after the change; `peer_nsps` names each peer WWPN's port. They make the peer-port
    block of each fabric where both WWPNs are in the name server."""
    plan = ZoningPlan()
    # 1) Read each fabric switch (F1 = odd, F2 = even), read-only.
    f1 = _read_fabric("F1", intent.switch_f1, brocade_factory, plan)
    f2 = _read_fabric("F2", intent.switch_f2, brocade_factory, plan)
    fabrics = (f1, f2)
    _note_fabric_overlap(f1, f2, plan)

    def fabric_of(wwpn: str) -> str:
        return next((f.label for f in fabrics if wwpn in f.ns), "")

    cand = _collect_host_candidates(intent, discovery, fabrics, plan)

    # 3) Array FC ports (discovery). RCFC/Peer-labelled ports are INCLUDED but FLAGGED, never
    #    hard-dropped (ADR 0004 refinement 2026-07-04, re-proven live 2026-08-15: a production
    #    Primera's RCFC-labelled target ports carry HOST logins — Type=host — so a hard exclusion
    #    removes host-serving ports). They are never pre-selected; the operator sees the label and
    #    decides. Only ports online in a fabric NS end up placed either way.
    array_ports = [p for p in discovery.array_ports if p.protocol == "fc" and p.wwpn]
    if flagged := [f"{p.label} (Type {p.port_type})" for p in array_ports if _caution(p)]:
        plan.notes.append(
            "Flagged, not excluded — the array reports these as something other than host-serving, "
            "but such a port can still serve hosts; select them only knowingly: " + ", ".join(flagged)
        )

    # 4) Per fabric: the host + array WWPNs present, and every SIST pair (each host port x each array port).
    # SPEC-025 R7: the alias pre-fill for a peer port is this array's convention name with a PEER marker.
    own_serial = next((f.ns[p.wwpn].array_serial for f in fabrics for p in array_ports
                       if p.wwpn in f.ns and f.ns[p.wwpn].array_serial), "")
    peer_list = list(peer_pairs or [])
    peer_nsp_map = dict(peer_nsps or {})
    for peer, source in peer_list:
        if not any(peer in f.ns and source in f.ns for f in fabrics):
            plan.notes.append(
                f"Peer port {peer_nsp_map.get(peer, '')} ({wwpn_colons(peer)}) and the source port {wwpn_colons(source)} "
                "are not both in one fabric's name server, so no zone is drafted for them. Check the cabling and "
                "the WWPN on the Peer ports tab."
            )

    for fab in fabrics:
        fabric_plan = _build_fabric_plan(fab, fabric_of, cand, array_ports)
        _populate_peer_block(fabric_plan, fab, peer_list, peer_nsp_map, own_serial)
        plan.fabrics.append(fabric_plan)

    # 5) Host WWPNs on NO fabric -> offline; can't be placed (cable + power, then re-run).
    plan.offline_hosts = [f"{name} ({wwpn_colons(wwpn)})" for wwpn, name in cand.name.items() if not fabric_of(wwpn)]

    # 6) A READY array port in neither fabric's name server is an anomaly (a link-up port IS
    #    FLOGI'd into some fabric): either a transient switch read or the wrong declared switches.
    #    Measured live: F2's plan lost both its array ports this way while those ports carried
    #    ACTIVE VLUNs — the plan must say so instead of quietly offering fewer candidates.
    if unplaced := [p.label for p in array_ports if p.link_state == "ready" and not fabric_of(p.wwpn)]:
        plan.notes.append(
            "Array port(s) ONLINE but present in neither declared fabric's name server: "
            + ", ".join(unplaced)
            + " — likely a transient switch read (or the declared switches front the wrong "
            "fabrics). Rebuild the plan before acting on it."
        )

    # 7) Discovery's cabling notes belong on THIS screen: the array is cross-cabled on rack13 (0:3:4
    #    on the odd fabric), discovery said so, and the zoning step never showed it.
    plan.notes.extend(
        note for note in discovery.notes
        if re.search(r"parity|fabric", note, re.IGNORECASE) and note not in plan.notes
    )
    return plan


def alias_name_warnings(plan: ZoningPlan, aliases: dict[str, str]) -> dict[str, list[str]]:
    """Per fabric: legal-but-non-portable alias names among the operator's entries (FOS 8.1+ only
    characters). Advisory — rendering proceeds; `render_commands` skips only names FOS would reject."""
    out: dict[str, list[str]] = {}
    for fabric in plan.fabrics:
        notes: list[str] = []
        for entry in fabric.hosts + fabric.array_ports:
            name = aliases.get(entry.wwpn) or entry.suggested_alias
            if name and name not in entry.existing_aliases and (why := fos_name_warning(name)):
                notes.append(f"alias '{name}' {why}")
        out[fabric.fabric] = notes
    return out


@dataclass
class _FabricRenderContext:
    by_wwpn: dict[str, AliasedWwpn]
    aliases: dict[str, str]
    defined: set[str]
    new_alias: dict[str, str] = field(default_factory=dict)   # alias name this set will alicreate -> the WWPN it is for

    def alias_for(self, wwpn: str) -> str:
        return self.aliases.get(wwpn) or self.by_wwpn[wwpn].suggested_alias

    def describe(self, wwpn: str) -> str:
        entry = self.by_wwpn[wwpn]
        if entry.role == "array":
            return f"array port {entry.nsp or entry.display}"
        return f"host {entry.host_name or entry.display}"

    def is_new_alias(self, wwpn: str, name: str) -> bool:
        return name not in self.by_wwpn[wwpn].existing_aliases


def _missing_alias_reason(pair: tuple[str, str], ctx: _FabricRenderContext) -> str:
    nameless = [ctx.describe(w) for w in pair if not ctx.alias_for(w)]
    return "enter an alias name for " + " and ".join(nameless) if nameless else ""


def _illegal_alias_reason(pair: tuple[str, str], ctx: _FabricRenderContext) -> str:
    illegal = [
        f"alias '{name}' for {ctx.describe(w)} {why} — try '{fos_name_suggestion(name)}'"
        for w in pair
        if ctx.is_new_alias(w, name := ctx.alias_for(w)) and (why := fos_name_problem(name))
    ]
    return "; ".join(illegal)


def _clash_reason(pair: tuple[str, str], ctx: _FabricRenderContext) -> str:
    # One name, one object: a name the switch already defines (or another port here takes)
    # would make alicreate fail and the zone pick up someone else's WWPN.
    clash: list[str] = []
    for w in pair:
        name = ctx.alias_for(w)
        if not ctx.is_new_alias(w, name):
            continue
        if name in ctx.defined:
            clash.append(f"alias '{name}' for {ctx.describe(w)} already exists on the switch for another device")
        elif ctx.new_alias.get(name, w) != w:
            clash.append(f"alias '{name}' for {ctx.describe(w)} is also the name chosen for {ctx.describe(ctx.new_alias[name])}")
    zone = f"{ctx.alias_for(pair[0])}_{ctx.alias_for(pair[1])}"
    if zone in ctx.defined:
        clash.append(f"zone '{zone}' already exists on the switch")
    elif why := fos_name_problem(zone):
        clash.append(f"zone name '{zone}' {why} — shorten an alias")
    return "; ".join(clash)


# Ordered pair validation checks before rendering a zone (SPEC-010 R3/R5).
_PAIR_CHECKS: tuple[Callable[[tuple[str, str], _FabricRenderContext], str], ...] = (
    _missing_alias_reason,
    _illegal_alias_reason,
    _clash_reason,
)


def _classify_pairs(
    new_pairs: list[tuple[str, str]], ctx: _FabricRenderContext,
) -> tuple[list[tuple[str, str]], list[str]]:
    # Classify FIRST: a pair renders only when both members have names FOS will accept; the
    # rest is reported. A name the switch would reject (a dot, a space, 65 characters) is as
    # useless as no name — the paste would fail half-way and leave an open transaction.
    renderable: list[tuple[str, str]] = []
    skipped: list[str] = []
    for pair in new_pairs:
        if reason := next((msg for check in _PAIR_CHECKS if (msg := check(pair, ctx))), ""):
            skipped.append(f"{ctx.describe(pair[0])} × {ctx.describe(pair[1])} — {reason}")
            continue
        for w in pair:
            name = ctx.alias_for(w)
            if ctx.is_new_alias(w, name):
                ctx.new_alias.setdefault(name, w)
        renderable.append(pair)
    return renderable, skipped


def _render_fabric_commands(
    fabric: FabricZonePlan, aliases: dict[str, str], wanted: set[tuple[str, ...]] | None,
) -> tuple[list[str], list[str]]:
    ctx = _FabricRenderContext(
        by_wwpn={entry.wwpn: entry for entry in (fabric.hosts + fabric.array_ports)},
        aliases=aliases,
        defined=set(fabric.defined_names),
    )
    # The DELTA only: pairs the fabric's effective config already covers create NOTHING —
    # re-proposing existing zones against a production config is the failure this guards.
    # The operator's selection then narrows further; it can never resurrect a zoned pair.
    zoned = set(fabric.already_zoned)
    new_pairs = [p for p in fabric.pairs if p not in zoned and (wanted is None or tuple(p) in wanted)]
    renderable, skipped = _classify_pairs(new_pairs, ctx)

    # alicreate only for WWPNs that participate in at least one RENDERED zone (not merely a
    # selected one — a skipped pair must not leave an orphan alicreate behind), and only for
    # names the switch doesn't already have.
    cmds: list[str] = []
    emitted: set[str] = set()
    in_rendered = {wwpn for pair in renderable for wwpn in pair}
    for entry in fabric.hosts + fabric.array_ports:
        if entry.wwpn in in_rendered and (name := ctx.alias_for(entry.wwpn)) and name not in entry.existing_aliases and name not in emitted:
            cmds.append(f'alicreate "{name}","{entry.display}"')
            emitted.add(name)

    zone_names: list[str] = []
    for host_wwpn, array_wwpn in renderable:
        zone = f"{ctx.alias_for(host_wwpn)}_{ctx.alias_for(array_wwpn)}"
        if zone not in zone_names:            # dedupe: colliding aliases must not double a zone
            zone_names.append(zone)
            cmds.append(f'zonecreate "{zone}","{ctx.alias_for(host_wwpn)};{ctx.alias_for(array_wwpn)}"')

    if zone_names and fabric.active_cfg:
        cmds.append(f'cfgadd "{fabric.active_cfg}","{";".join(zone_names)}"')
        # Activation, kept apart by the UI: `cfgsave` commits the defined config and CLOSES the
        # zoning transaction (FOS 9 holds a fabric lock while one is open); `cfgenable` then
        # replaces the effective config fabric-wide — the SAN team's act, in a window.
        cmds.append("cfgsave")
        cmds.append(f"cfgenable {fabric.active_cfg}")
    if cmds:
        # SPEC-010 R1: the FOS procedure starts by proving no zoning transaction is open. A line,
        # not a sentence beside a button — the .txt the SAN team receives must begin with it.
        cmds.insert(0, "cfgtransshow")
    return cmds, skipped


def render_commands(
    plan: ZoningPlan,
    aliases: dict[str, str],
    selected_pairs: list[tuple[str, str]] | None = None,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Assemble the read-only command preview per fabric from the plan + the operator's chosen aliases
    (`wwpn -> alias name`, falling back to each WWPN's suggested alias). `alicreate` only for aliases
    that do NOT already exist on the switch; SIST `zonecreate`; then `cfgadd` + `cfgenable`. The tool
    never RUNS these — this is the script for the SAN team.

    `selected_pairs` is the operator's selection (ADR 0004 refinement: the operator PICKS which array
    ports serve each host — candidates are a menu, not a mandate). None means every candidate, which
    is only appropriate for headless/preview use; the UI always passes an explicit selection.

    Returns (commands, skipped) per fabric. A selected pair whose member has NO alias name cannot be
    zoned — but it must never vanish silently: on the live BGL run the operator ticked 0:3:4 (a port
    the fabric has no alias for), got an unchanged preview, and had no way to know why. Every such
    pair is reported in `skipped` naming exactly which member needs a name."""
    out: dict[str, list[str]] = {}
    skipped_out: dict[str, list[str]] = {}
    wanted: set[tuple[str, ...]] | None = None if selected_pairs is None else {tuple(pair) for pair in selected_pairs}
    for fabric in plan.fabrics:
        out[fabric.fabric], skipped_out[fabric.fabric] = _render_fabric_commands(fabric, aliases, wanted)
    return out, skipped_out


def render_peer_commands(
    plan: ZoningPlan, aliases: dict[str, str],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """SPEC-025 R7: the peer-port block, its own command set per fabric, through the same renderer as
    the host zones (`render_commands`): one single-initiator single-target zone per (peer port, source
    port) pair the sheet asks for, `<peer alias>_<source alias>`, `cfgsave` and `cfgenable` kept apart
    by the page as today. The tool never runs these (ADR 0012)."""
    blocks = ZoningPlan(fabrics=[
        FabricZonePlan(
            fabric=f.fabric, switch_host=f.switch_host, active_cfg=f.active_cfg, switch_name=f.switch_name,
            fabric_name=f.fabric_name, hosts=f.peer_ports, array_ports=f.sources, pairs=f.peer_pairs,
            already_zoned=f.peer_already_zoned, defined_names=f.defined_names,
        )
        for f in plan.fabrics if f.peer_pairs
    ])
    return render_commands(blocks, aliases, None)
