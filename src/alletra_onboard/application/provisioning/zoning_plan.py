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

from alletra_onboard.application.provisioning.clients import make_brocade
from alletra_onboard.application.provisioning.zoning import parse_active_zones
from alletra_onboard.domain.shared import normalize_wwpn, wwpn_colons
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.zoning import AliasedWwpn, FabricZonePlan, NsDevice, ZoningPlan
from alletra_onboard.domain.provisioning import ProvisioningIntent

_WWPN_COLON = re.compile(r"(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}")


# An array port's PortSymb self-describes it: "SGHD44LQLS - 0:3:1 - HPE64004-B" (serial, n:s:p).
_ARRAY_PORT_SYMB = re.compile(r"^(\S+) - (\d+:\d+:\d+) - ")


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
        if sym := re.search(r'PortSymb:\s*\[\d+\]\s*"(.*)"', line):
            current.port_symb = sym.group(1).strip()
            if arr := _ARRAY_PORT_SYMB.match(current.port_symb):
                current.array_serial, current.array_nsp = arr.group(1), arr.group(2)
        elif node := re.search(r'NodeSymb:\s*\[\d+\]\s*"(.*)"', line):
            current.node_symb = node.group(1).strip()
            if hn := re.search(r"\bHN:(\S+)", current.node_symb):
                current.host_name = hn.group(1)
            if os_ := re.search(r"\bOS:(.+)$", current.node_symb):
                current.os = os_.group(1).strip()
        elif dev := re.search(r"Device type:\s*(.+)", line):
            current.device_type = dev.group(1).strip()
        elif perm := re.search(r"Permanent Port Name:\s*(\S+)", line):
            current.permanent_wwpn = normalize_wwpn(perm.group(1))
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


# Brocade FOS zone-object names (FOS Command Reference, aliCreate/zoneCreate): first character a
# letter or digit; then letters, digits, `_`, `-`, `$`, `^`; case-sensitive; zone names ≤ 64.
# `-`, `$`, `^` and a leading digit are "enhanced" names that need EVERY switch in the fabric on
# FOS 8.1.0+ — an older switch joining segments the fabric — so they are legal-but-warned.
_FOS_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-$^]*$")
_FOS_ENHANCED = re.compile(r"^[0-9]|[-$^]")
FOS_NAME_MAX = 64


def fos_name_problem(name: str) -> str:
    """Why FOS would REJECT this alias/zone name ("" = acceptable). Rejection is the only thing that
    stops a render; portability concerns are `fos_name_warning`."""
    if not name:
        return "is empty"
    if len(name) > FOS_NAME_MAX:
        return f"is {len(name)} characters; FOS allows {FOS_NAME_MAX}"
    if not _FOS_NAME.match(name):
        bad = sorted({c for c in name if not re.match(r"[A-Za-z0-9_\-$^]", c)})
        return "contains " + ", ".join(repr(c) for c in bad) + " — FOS names allow letters, digits and _ (- $ ^ on FOS 8.1+)"
    return ""


def fos_name_warning(name: str) -> str:
    """A legal name that is not portable to every fabric ("" = plain)."""
    if name and not fos_name_problem(name) and _FOS_ENHANCED.search(name):
        return "uses - $ ^ or starts with a digit: every switch in the fabric must run FOS 8.1.0 or later"
    return ""


def _fos_safe(text: str) -> str:
    """Fold arbitrary text (an IP, a DNS name, a serial) into a plain FOS name fragment."""
    return re.sub(r"[^A-Za-z0-9]+", "_", text or "").strip("_")


def _proposed_alias(role: str, *, host_name: str, wwpn: str, hba_index: int, nsp: str, serial: str) -> str:
    """A UI pre-fill for a WWPN that has NO alias on the switch, from the HPE field convention
    (ADR 0004): host HBA port -> ``<host>_hba<n>``; array port -> ``<serial>_N<n>S<s>P<p>``. Always
    FOS-plain (letters, digits, underscore; starts with a letter) and ≤ 64 characters."""
    if role == "array":
        parts = nsp.split(":")
        code = "N{}S{}P{}".format(*parts) if len(parts) == 3 else _fos_safe(wwpn)[-6:]
        base = _fos_safe(serial) or "array"
        name = f"{base}_{code}"
    else:
        base = _fos_safe(host_name) or f"host_{wwpn[-4:].lower()}"
        name = f"{base}_hba{hba_index}"
    if not name[0].isalpha():
        name = ("array_" if role == "array" else "host_") + name
    return name[:FOS_NAME_MAX]


def _node_of(nsp: str) -> int | None:
    parts = nsp.split(":")
    return int(parts[0]) if len(parts) == 3 and parts[0].isdigit() else None


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
             alias_freq: dict[str, int], *, nsp: str = "", host_name: str = "",
             host_source: str = "", caution: str = "", os: str = "", placed_on_switch: str = "",
             hba_index: int = 1, serial: str = "") -> AliasedWwpn:
    existing = aliases.get(wwpn, [])
    return AliasedWwpn(
        wwpn=wwpn, display=wwpn_colons(wwpn), role=role, fabric=fabric, nsp=nsp, node=_node_of(nsp),
        host_name=host_name, host_source=host_source, caution=caution, os=os,
        placed_on_switch=placed_on_switch,
        existing_aliases=existing, suggested_alias=_suggest_alias(existing, role, nsp, alias_freq),
        proposed_alias="" if existing else _proposed_alias(
            role, host_name=host_name, wwpn=wwpn, hba_index=hba_index, nsp=nsp, serial=serial,
        ),
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
    # Aliases are PER FABRIC. One flat pool looks harmless but is wrong twice over: an alias that
    # exists only on F2 would suppress the F1 alicreate (leaving F1's zonecreate referencing an
    # undefined name, which the switch rejects), and "uniquely bound" for suggestions must mean
    # unique on ITS fabric. Measured live 2026-08-15: 41 alias names exist on BOTH lab fabrics.
    aliases: dict[str, dict[str, list[str]]] = {"F1": {}, "F2": {}}
    active_cfg: dict[str, str] = {}
    active_zones: dict[str, dict[str, set[str]]] = {}   # fabric -> {zone name: member WWPNs}
    switch_host: dict[str, str] = {}
    local_ns: dict[str, dict[str, "NsDevice"]] = {}   # nsshow ONLY: devices on the declared switch itself
    switch_name: dict[str, str] = {}
    fabric_name: dict[str, str] = {}
    fabric_switches: dict[str, dict[int, str]] = {}    # fabric -> {domain: switch name} (fabricshow)
    remote_domain: dict[str, dict[str, int]] = {}      # fabric -> {wwpn: remote domain} (nscamshow)
    for label, creds in (("F1", intent.switch_f1), ("F2", intent.switch_f2)):
        switch_host[label] = creds.host
        try:
            with brocade_factory(creds) as switch:
                nsshow_text = switch.nsshow()
                nscam_text = switch.nscamshow()
                local_ns[label] = parse_nameserver(nsshow_text)
                ns[label] = parse_nameserver(nsshow_text + "\n" + nscam_text)
                remote_domain[label] = parse_nscam_domains(nscam_text)
                for wwpn, found in parse_aliases(switch.alishow()).items():
                    for alias in found:
                        per = aliases[label].setdefault(wwpn, [])
                        if alias not in per:
                            per.append(alias)
                cfg_text = switch.cfgshow()
                active_cfg[label] = parse_active_cfg(cfg_text)
                active_zones[label], _ = parse_active_zones(cfg_text)
                # Identity reads are best-effort: a fake or an older FOS without them must not sink
                # the plan, which is complete without names.
                try:
                    switch_name[label], _domain = parse_switchshow(switch.read("switchshow"))
                except Exception:  # noqa: BLE001
                    switch_name[label] = ""
                try:
                    fabric_name[label], fabric_switches[label] = parse_fabricshow(switch.fabricshow())
                except Exception:  # noqa: BLE001
                    fabric_name[label], fabric_switches[label] = "", {}
                if not local_ns[label]:
                    # Measured live 2026-08-15: one plan run got an empty local NS from a healthy
                    # switch (transient), so its resident array ports vanished from the plan with
                    # no explanation. An empty LOCAL name server on a production switch is an
                    # anomaly to report, not a fact to silently accept.
                    plan.notes.append(
                        f"The {label} switch {creds.host} returned no LOCAL name-server entries "
                        "(nsshow) — devices plugged into that switch (typically this deployment's "
                        "array ports) cannot be placed. Likely transient: rebuild the plan."
                    )
        except Exception as exc:  # noqa: BLE001 - one unreachable switch must not sink the plan
            ns[label] = {}
            local_ns[label] = {}
            remote_domain[label] = {}
            active_cfg[label] = ""
            active_zones[label] = {}
            switch_name.setdefault(label, "")
            fabric_name.setdefault(label, "")
            fabric_switches.setdefault(label, {})
            plan.notes.append(f"Could not read the {label} switch {creds.host}: {exc}")

    # How many distinct WWPNs each alias is bound to ON ITS FABRIC — a shared alias is junk (never
    # suggested).
    alias_freq: dict[str, dict[str, int]] = {"F1": defaultdict(int), "F2": defaultdict(int)}
    for label in ("F1", "F2"):
        for names in aliases[label].values():
            for alias in set(names):
                alias_freq[label][alias] += 1

    # The declared switches must front two DISJOINT fabrics. If they are ISL'd into ONE merged fabric,
    # first-match placement lands every device on F1 and the "dual-fabric" plan is fiction — the exact
    # silent failure the meshed-lab episode produced. Measured healthy baseline 2026-08-15: 73 of ~955
    # WWPNs (≈8%) appear in both name servers (stale nscamshow cache), so a small overlap only warrants
    # a verify note; a large one means merged.
    seen_f1, seen_f2 = set(ns.get("F1", {})), set(ns.get("F2", {}))
    overlap = seen_f1 & seen_f2
    if seen_f1 and seen_f2 and overlap:
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

    def fabric_of(wwpn: str) -> str:
        return next((label for label in ("F1", "F2") if wwpn in ns.get(label, {})), "")

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
    host_by_wwpn: "OrderedDict[str, str]" = OrderedDict()
    host_source: dict[str, str] = {}
    host_os: dict[str, str] = {}

    def _claim(wwpn: str, name: str, source: str, os_: str = "") -> None:
        if wwpn not in host_by_wwpn:
            host_by_wwpn[wwpn] = name
            host_source[wwpn] = source
            host_os[wwpn] = os_
        elif name and not host_by_wwpn[wwpn]:
            host_by_wwpn[wwpn] = name
            host_source[wwpn] = source
        if os_ and not host_os.get(wwpn):
            host_os[wwpn] = os_

    for hba in discovery.host_hbas:
        _claim(normalize_wwpn(hba.wwpn), hba.host_name, "vcenter", hba.os or "")
    vcenter_count = len(host_by_wwpn)
    for declared in getattr(intent, "declared_hosts", None) or []:
        for wwpn in declared.wwpns:
            _claim(normalize_wwpn(wwpn), declared.name, "sheet", declared.os or "")
    for array_host in discovery.array_hosts:
        for wwpn in array_host.wwpns:
            _claim(normalize_wwpn(wwpn), array_host.name, "array")
    for label in ("F1", "F2"):
        for wwpn, device in local_ns.get(label, {}).items():
            if device.is_physical_initiator:
                _claim(wwpn, device.host_name, "switch", device.os)
    added = len(host_by_wwpn) - vcenter_count
    if not vcenter_count and host_by_wwpn:
        plan.notes.append(
            f"vCenter reported no hosts — {len(host_by_wwpn)} host port(s) were identified from "
            "the sheet, the array's logins and the declared switches' own name servers instead "
            "(names from the fabric where the HBA advertises one)."
        )
    elif added:
        by_source = defaultdict(int)
        for wwpn in host_by_wwpn:
            if host_source[wwpn] != "vcenter":
                by_source[host_source[wwpn]] += 1
        detail = ", ".join(
            f"{n} from {({'sheet': 'the sheet', 'array': 'array logins', 'switch': 'the fabric name servers'})[s]}"
            for s, n in by_source.items()
        )
        plan.notes.append(
            f"{added} host port(s) not known to vCenter were added ({detail}). Unnamed ones are "
            "shown by WWPN — name them on the sheet's Hosts tab if you intend to zone them."
        )

    # For the convention pre-fill: which HBA of its host each WWPN is (1-based, by WWPN order).
    hba_index: dict[str, int] = {}
    by_host: dict[str, list[str]] = defaultdict(list)
    for wwpn, name in host_by_wwpn.items():
        by_host[name or wwpn].append(wwpn)
    for wwpns in by_host.values():
        for i, wwpn in enumerate(sorted(wwpns), start=1):
            hba_index[wwpn] = i

    # 3) Array FC ports (discovery). RCFC/Peer-labelled ports are INCLUDED but FLAGGED, never
    #    hard-dropped (ADR 0004 refinement 2026-07-04, re-proven live 2026-08-15: a production
    #    Primera's RCFC-labelled target ports carry HOST logins — Type=host — so a hard exclusion
    #    removes host-serving ports). They are never pre-selected; the operator sees the label and
    #    decides. Only ports online in a fabric NS end up placed either way.
    def _caution(p) -> str:
        """Warn on the array's own Type, never on the Label.

        The Label is free text an operator typed. On AlletraMP_D22U27 three FC ports carry
        "peer port", "peer 1:3:1" and "Peer_port" — three spellings on one array — and all three are
        Type `host`, actively serving hosts. Keying the warning off that string flagged exactly the
        wrong ports, while the array's genuine peer ports are IP and never reach this code at all.
        """
        if p.port_type and p.port_type not in ("host", "free"):
            return f"Type {p.port_type}: the array does not report this as host-serving"
        return ""

    array_ports = [p for p in discovery.array_ports if p.protocol == "fc" and p.wwpn]
    flagged = [f"{p.label} (Type {p.port_type})" for p in array_ports if _caution(p)]
    if flagged:
        plan.notes.append(
            "Flagged, not excluded — the array reports these as something other than host-serving, "
            "but such a port can still serve hosts; select them only knowingly: " + ", ".join(flagged)
        )

    # 4) Per fabric: the host + array WWPNs present, and every SIST pair (each host port x each array port).
    def _remote_switch(label: str, wwpn: str) -> str:
        # Placed via nscamshow => plugged into another switch of this fabric; name it so the
        # operator can see WHY a host they never cabled to the declared switch is offered here.
        remote = remote_domain.get(label, {})
        if wwpn in local_ns.get(label, {}) or wwpn not in remote:
            return ""
        return fabric_switches.get(label, {}).get(remote[wwpn]) or f"domain {remote[wwpn]}"

    for label in ("F1", "F2"):
        names_by_domain = fabric_switches.get(label, {})
        hosts = [
            _aliased(wwpn, "host", label, aliases[label], alias_freq[label],
                     host_name=host_by_wwpn[wwpn], host_source=host_source.get(wwpn, ""),
                     os=host_os.get(wwpn, ""), placed_on_switch=_remote_switch(label, wwpn),
                     hba_index=hba_index.get(wwpn, 1))
            for wwpn in host_by_wwpn if fabric_of(wwpn) == label
        ]
        ports = [
            _aliased(p.wwpn, "array", label, aliases[label], alias_freq[label], nsp=p.label,
                     caution=_caution(p),
                     serial=(ns.get(label, {}).get(p.wwpn).array_serial if ns.get(label, {}).get(p.wwpn) else ""))
            for p in array_ports if fabric_of(p.wwpn) == label
        ]
        pairs = [(host.wwpn, port.wwpn) for host in hosts for port in ports]
        # The DELTA: a candidate pair is already zoned iff some zone in this fabric's effective
        # config contains BOTH WWPNs (aliases were resolved by parse_active_zones). Proven against
        # the live VZ captures: all 12 host<->array pairs land in already_zoned, so the preview
        # creates nothing on a bed that is already correct.
        zones = active_zones.get(label, {})
        already: list[tuple[str, str]] = []
        zone_names: dict[str, list[str]] = {}
        for pair in pairs:
            covering = [z for z, members in zones.items() if pair[0] in members and pair[1] in members]
            if covering:
                already.append(pair)
                zone_names[f"{pair[0]}|{pair[1]}"] = covering
        plan.fabrics.append(FabricZonePlan(
            fabric=label, switch_host=switch_host[label], active_cfg=active_cfg.get(label, ""),
            switch_name=switch_name.get(label, ""), fabric_name=fabric_name.get(label, ""),
            switch_count=len(names_by_domain),
            hosts=hosts, array_ports=ports, pairs=pairs, already_zoned=already, zone_names=zone_names,
        ))

    # 5) Host WWPNs on NO fabric -> offline; can't be placed (cable + power, then re-run).
    for wwpn, name in host_by_wwpn.items():
        if not fabric_of(wwpn):
            plan.offline_hosts.append(f"{name} ({wwpn_colons(wwpn)})")

    # 6) A READY array port in neither fabric's name server is an anomaly (a link-up port IS
    #    FLOGI'd into some fabric): either a transient switch read or the wrong declared switches.
    #    Measured live: F2's plan lost both its array ports this way while those ports carried
    #    ACTIVE VLUNs — the plan must say so instead of quietly offering fewer candidates.
    unplaced = [p.label for p in array_ports if p.link_state == "ready" and not fabric_of(p.wwpn)]
    if unplaced:
        plan.notes.append(
            "Array port(s) ONLINE but present in neither declared fabric's name server: "
            + ", ".join(unplaced)
            + " — likely a transient switch read (or the declared switches front the wrong "
            "fabrics). Rebuild the plan before acting on it."
        )

    # 7) Discovery's cabling notes belong on THIS screen: the array is cross-cabled on rack13 (0:3:4
    #    on the odd fabric), discovery said so, and the zoning step never showed it.
    for note in discovery.notes:
        if re.search(r"parity|fabric", note, re.IGNORECASE) and note not in plan.notes:
            plan.notes.append(note)
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
    wanted = None if selected_pairs is None else {tuple(pair) for pair in selected_pairs}
    for fabric in plan.fabrics:
        by_wwpn = {entry.wwpn: entry for entry in (fabric.hosts + fabric.array_ports)}

        def alias_for(wwpn: str) -> str:
            return aliases.get(wwpn) or by_wwpn[wwpn].suggested_alias

        # The DELTA only: pairs the fabric's effective config already covers create NOTHING —
        # re-proposing existing zones against a production config is the failure this guards.
        # The operator's selection then narrows further; it can never resurrect a zoned pair.
        zoned = set(fabric.already_zoned)
        new_pairs = [
            pair for pair in fabric.pairs
            if pair not in zoned and (wanted is None or tuple(pair) in wanted)
        ]

        def describe(wwpn: str) -> str:
            entry = by_wwpn[wwpn]
            if entry.role == "array":
                return f"array port {entry.nsp or entry.display}"
            return f"host {entry.host_name or entry.display}"

        # Classify FIRST: a pair renders only when both members have names FOS will accept; the
        # rest is reported. A name the switch would reject (a dot, a space, 65 characters) is as
        # useless as no name — the paste would fail half-way and leave an open transaction.
        renderable: list[tuple[str, str]] = []
        skipped: list[str] = []
        for host_wwpn, array_wwpn in new_pairs:
            nameless = [describe(w) for w in (host_wwpn, array_wwpn) if not alias_for(w)]
            if nameless:
                skipped.append(
                    f"{describe(host_wwpn)} × {describe(array_wwpn)} — enter an alias name for "
                    + " and ".join(nameless)
                )
                continue
            illegal = [
                f"alias '{alias_for(w)}' for {describe(w)} {fos_name_problem(alias_for(w))}"
                for w in (host_wwpn, array_wwpn)
                if alias_for(w) not in by_wwpn[w].existing_aliases and fos_name_problem(alias_for(w))
            ]
            if illegal:
                skipped.append(f"{describe(host_wwpn)} × {describe(array_wwpn)} — " + "; ".join(illegal))
            else:
                renderable.append((host_wwpn, array_wwpn))

        # alicreate only for WWPNs that participate in at least one RENDERED zone (not merely a
        # selected one — a skipped pair must not leave an orphan alicreate behind), and only for
        # names the switch doesn't already have.
        cmds: list[str] = []
        emitted: set[str] = set()
        in_rendered = {wwpn for pair in renderable for wwpn in pair}
        for entry in fabric.hosts + fabric.array_ports:
            if entry.wwpn not in in_rendered:
                continue
            name = alias_for(entry.wwpn)
            if name and name not in entry.existing_aliases and name not in emitted:
                cmds.append(f'alicreate "{name}","{entry.display}"')
                emitted.add(name)

        zone_names: list[str] = []
        for host_wwpn, array_wwpn in renderable:
            zone = f"{alias_for(host_wwpn)}_{alias_for(array_wwpn)}"
            if zone in zone_names:            # dedupe: colliding aliases must not double a zone
                continue
            zone_names.append(zone)
            cmds.append(f'zonecreate "{zone}","{alias_for(host_wwpn)};{alias_for(array_wwpn)}"')

        if zone_names and fabric.active_cfg:
            cmds.append(f'cfgadd "{fabric.active_cfg}","{";".join(zone_names)}"')
            # Activation, kept apart by the UI: `cfgsave` commits the defined config and CLOSES the
            # zoning transaction (FOS 9 holds a fabric lock while one is open); `cfgenable` then
            # replaces the effective config fabric-wide — the SAN team's act, in a window.
            cmds.append("cfgsave")
            cmds.append(f"cfgenable {fabric.active_cfg}")
        out[fabric.fabric] = cmds
        skipped_out[fabric.fabric] = skipped
    return out, skipped_out
