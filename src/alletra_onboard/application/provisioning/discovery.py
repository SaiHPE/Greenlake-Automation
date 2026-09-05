"""Discovery: read the real environment a provisioning run will act on — array-side, read-only.

ONE array SSH session gathers ALL FC + iSCSI target ports (`showport` + `showport -iscsi`, any state)
and the array's CURATED host view (`showhost -d`) — the authoritative host -> WWPN -> port mapping.
`showhost` lists only real hosts (with a persona); it can never mistake a storage/peer-array port for
a host the way the raw fabric name server (`showportdev ns`) can — which is why zoning is verified from
it. vCenter supplies each ESXi host's HBA WWPNs + OS; each is then assigned to the fabric its WWPN logs
into ON THE ARRAY. Zoning verification computes over this DiscoveryReport — it does not read again.

Any one source failing is captured as a note, not a hard error.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli, make_vcenter
from alletra_onboard.domain.shared import Fabric, normalize_wwpn
from alletra_onboard.domain.discovery import (
    ArrayHost,
    ArrayPort,
    DiscoveredHost,
    DiscoveryReport,
    EthernetPort,
    node_name_from_iqn,
    os_from_iqn,
    os_from_persona,
    os_from_switch_string,
)
from alletra_onboard.domain.provisioning import ProvisioningIntent

_LOGICAL_NAME_RE = re.compile(r"^\s*Logical Name:\s*(\S+)", re.IGNORECASE)


def parse_iscsi_ips(showport_iscsi: str) -> dict[str, str]:
    """`showport -iscsi` -> {n:s:p: target IP}. Columns: N:S:P State IPAddr ... (offline -> '')."""
    ips: dict[str, str] = {}
    for line in (showport_iscsi or "").splitlines():
        p = line.split()
        if len(p) >= 3 and p[0][:1].isdigit() and ":" in p[0]:
            ips[p[0]] = "" if p[1] == "offline" else p[2]
    return ips


#: Slot-4 card ports 1-2 carry data services (file OR iSCSI); 3-4 are the RCIP-capable ports. A
#: convention, not a law: it holds on every array measured (rack13arcus, AlletraMP_D22U27, and the
#: two Panduranga sampled), but Type is the array's own answer and always wins. Position is used
#: only to say what an UNCONFIGURED port could become, which Type cannot express — a capable-but-idle
#: RCIP port reports Type `free`, indistinguishable from any other spare.
RCIP_CAPABLE_PORTS = (3, 4)
DATA_SERVICES_PORTS = (1, 2)


def _nsp(token: str) -> tuple[int, int, int] | None:
    try:
        node, slot, card_port = (int(x) for x in token.split(":"))
    except ValueError:
        return None
    return node, slot, card_port


def parse_ports(showport: str, iscsi_ips: dict[str, str]) -> list[ArrayPort]:
    """HOST-FACING FC + iSCSI TARGET ports (any state) -> [ArrayPort].

    Deliberately narrow: this list feeds the zoning candidates, fabric resolution and path
    verification, all of which mean "ports that can serve a host". Disk, cluster, file and RCIP ports
    are parsed by the functions below into their own lists, never into this one.

    showport columns: N:S:P  Mode  State  Node_WWN/IP  Port_WWN/HW_Addr  Type  Protocol  Label ...
    Label is LAST and may contain spaces ("peer port"), so it is joined from token 7 onward rather
    than read as a single token.
    """
    out: list[ArrayPort] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0][:1].isdigit() or ":" not in p[0] or p[1] != "target":
            continue
        protocol = p[6]
        if protocol not in ("FC", "iSCSI"):
            continue
        nsp = _nsp(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        port_type = p[5]
        if protocol == "FC":
            fabric: Fabric = "odd" if card_port % 2 == 1 else "even"
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="fc",
                wwpn=normalize_wwpn(p[4]), link_state=p[2], fabric=fabric,
                mode=p[1], port_type=port_type,
                usage=" ".join(p[7:]) if len(p) > 7 else "",
            ))
        else:
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="iscsi",
                address=iscsi_ips.get(p[0], ""), link_state=p[2], fabric=None,
                mode=p[1], port_type=port_type,
                usage=" ".join(p[7:]) if len(p) > 7 else "",
            ))
    return out


def parse_replication_ports(showport: str) -> list[EthernetPort]:
    """RCIP (IP replication) ports from plain `showport`.

    Type `rcip` when configured, `free` when the port exists but has no RCIP config yet — both are
    reported, because "0:4:4 is available for replication" is the answer an operator planning
    replication actually needs.

    The trap this guards: on rack13arcus 0:5:1/0:5:2/1:5:1/1:5:2 are ALSO `peer` mode on `IP`
    protocol, and they are the node interconnect. Type `cluster` is the only thing separating them
    from a replication port, so a mode+protocol rule would invite an operator to configure the
    array's own inter-node links.
    """
    out: list[EthernetPort] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        mode, state, port_type, protocol = p[1], p[2], p[5], p[6]
        if mode != "peer" or protocol != "IP" or port_type == "cluster":
            continue
        nsp = _nsp(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        # p[3] is the IP for a configured port and "-" for an unconfigured one.
        address = p[3] if p[3] not in ("-", "") else ""
        out.append(EthernetPort(
            node=node, slot=slot, card_port=card_port, role=port_type,
            mode=mode, link_state=state, address=address,
        ))
    return out


def parse_rcip_detail(showport_rcip: str) -> dict[str, dict[str, str]]:
    """`showport -rcip` -> {n:s:p: {netmask, gateway, mtu, rate, duplex, autoneg}}.

    A THIRD column layout, sharing only N:S:P with the others and carrying no Mode column at all:

        N:S:P State HwAddr IPAddr Netmask/PrefixLen Gateway MTU Rate Duplex AutoNeg

    It lists only CONFIGURED links — on AlletraMP_D22U27 it returns 0:4:3 and 1:4:3 but not the
    idle 0:4:4 / 1:4:4, and on an array with no RCIP at all it answers "There is no specified port
    information". That is why the port LIST comes from plain `showport` and this view only enriches
    it: used alone, every capable-but-unconfigured port would vanish.

    The netmask and gateway are the reason to read it. Plain `showport` gives the address and
    nothing else, and an operator configuring replication needs the subnet it sits on.
    """
    out: dict[str, dict[str, str]] = {}
    for line in (showport_rcip or "").splitlines():
        p = line.split()
        if len(p) < 8 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        # "-" is the CLI's "unset" marker, normalised to "" exactly as parse_file_ports does — on LZ
        # the RCIP links carry no gateway and the raw "-" reached the UI as literal text.
        clean = lambda v: "" if v in ("-", "") else v  # noqa: E731
        out[p[0]] = {
            "netmask": clean(p[4]), "gateway": clean(p[5]), "mtu": clean(p[6]), "rate": clean(p[7]),
            "duplex": clean(p[8]) if len(p) > 8 else "", "autoneg": clean(p[9]) if len(p) > 9 else "",
        }
    return out


def parse_file_ports(showport_file: str) -> list[EthernetPort]:
    """`showport -file` -> [EthernetPort]. A separate view with its own columns:

        N:S:P  Mode  State  IPAddr/PrefixLen  IPDisable  Gateway  VLAN  MTU  Rate  Eth  Link  FailoverIPs

    File ports occupy the SAME n:s:p as iSCSI ports (x:4:1 / x:4:2), so position cannot tell the two
    apart — only the array's own Type and this view can. Real-output hazards, all present in the two
    captures this was written against: Gateway is "-" when unset, Rate is "n/a" on a down link, VLAN
    reads "untagged" rather than a number, and FailoverIPs is "-" or an address. On the second array
    1:4:1 is loss_sync with IPDisable Y and Link down, and its address appears as the FailoverIPs
    value of 1:4:2 — the pair must be read together or a covered port looks simply dead.
    """
    out: list[EthernetPort] = []
    for line in (showport_file or "").splitlines():
        p = line.split()
        if len(p) < 12 or not p[0][:1].isdigit() or ":" not in p[0]:
            continue
        nsp = _nsp(p[0])
        if nsp is None:
            continue
        node, slot, card_port = nsp
        address, _, prefix = p[3].partition("/")
        dash = lambda v: "" if v in ("-", "") else v  # noqa: E731 - the CLI's "unset" marker
        out.append(EthernetPort(
            node=node, slot=slot, card_port=card_port, role="file",
            mode=p[1], link_state=p[2], address=address, prefix_len=prefix,
            ip_disabled=p[4].upper() == "Y", gateway=dash(p[5]), vlan=p[6], mtu=p[7],
            rate=dash(p[8]) if p[8] != "n/a" else "", eth=p[9], link=p[10],
            failover_ips=[ip for ip in p[11:] if dash(ip)],
        ))
    return out


#: Name given to the array's UNCLAIMED FC logins — WWPNs logged in with no host object. Empty on
#: purpose: it is a real set of logins for fabric lookup, but never a host anyone can name, so any
#: caller assembling a list of host NAMES must filter it out.
UNCLAIMED_HOST = ""


def parse_showhost(showhost_d: str) -> list[ArrayHost]:
    """`showhost -d` -> [ArrayHost]. Columns: Id  Name  Persona  WWN/iSCSI_Name  Port  IP_addr.

    Parsed from the RIGHT (so a multi-word host name is tolerated). An initiator with no n:s:p
    (Port '---'/'--') is configured-but-not-logged-in.

    FC WWPNs (16 hex) and iSCSI IQNs are kept in SEPARATE fields. Until 2026-09-02 the IQN rows were
    dropped on a length check, so the array was telling us about every Windows, Linux and HPE VME
    iSCSI initiator attached to it and the parser threw them away — measured on rack13arcus, which
    reports `iqn.1991-05.com.microsoft:win-tn3n7rujk3v` at 10.132.30.87 and eight `HPE_VM_*` hosts.
    They stay out of `wwpns` because an IQN cannot be zoned and must never reach the fabric lookup.
    """
    hosts: "OrderedDict[str, ArrayHost]" = OrderedDict()
    for line in (showhost_d or "").splitlines():
        p = line.split()
        if len(p) < 6:
            continue
        claimed = p[0].isdigit()
        if not claimed and p[0] != "--":
            continue          # a header or a continuation line, not a login row
        port, wwn, persona = p[-2], p[-3], p[-4]
        # UNCLAIMED logins ('-- -- --  <wwpn>  n:s:p') are REAL logins that simply have no host
        # object yet — the normal state of a freshly zoned host, before provisioning creates one.
        # Skipping them (the old `p[0].isdigit()` guard) hid their WWPNs from fabric_by_wwpn, so a
        # host that was cabled, zoned AND logged in was reported "not zoned on either fabric".
        # MEASURED on rack13arcus: 10.132.30.136 (WWPNs …12:a8/…12:a9) is zoned in Vmware_Alletra
        # and kiranzone1 and visible in both name servers, yet the verify called it unzoned.
        # They are kept under the EMPTY host name, which callers building a host LIST must skip.
        name = (" ".join(p[1:-4]) or p[1]) if claimed else UNCLAIMED_HOST
        host = hosts.setdefault(name, ArrayHost(name=name, persona=persona))
        logged_in = ":" in port          # a real login (Port == n:s:p), not '---' / '--'
        if wwn.lower().startswith(("iqn.", "nqn.")):
            ports = host.iqns.setdefault(wwn, [])
            if logged_in and port not in ports:
                ports.append(port)
            # showhost's last column is the initiator's IP for iSCSI and 'n/a' for FC. Some rows
            # carry a placeholder (`f6ff:ffff:…`) for a configured-but-not-connected initiator, so
            # only a real login's address is trusted.
            addr = p[-1]
            if logged_in and addr not in ("n/a", "-", "--"):
                host.addresses.setdefault(wwn, addr)
            continue
        wwpn = normalize_wwpn(wwn)
        if len(wwpn) != 16:  # '--' / 'digtest' / anything that is not an FC WWPN
            continue
        ports = host.wwpns.setdefault(wwpn, [])
        if logged_in and port not in ports:
            ports.append(port)
    return list(hosts.values())


def assemble_hosts(report: DiscoveryReport, ns_os: dict[str, str] | None = None) -> list[DiscoveredHost]:
    """Join every source into one host per physical server, grouped by OS for display.

    Sources and what each contributes:
      * vCenter (`host_hbas`) — the ESXi name, its FC WWPNs and the ESXi version. Authoritative for
        naming an ESXi host; blind to everything that is not in that vCenter.
      * the array (`array_hosts`) — WWPNs and IQNs actually logged in, the array's own host-object
        name, and the initiator IP for iSCSI. Blind to OS.
      * the fabric name server (`ns_os`, WWPN -> OS string) — the OS an FC HBA registers. Blind to
        iSCSI entirely, since an iSCSI initiator never performs an FC login.

    Joined on the INITIATOR ID, never the name: the array calls a host `CRV_VZ_DL360G11D24U25` while
    vCenter calls it `10.99.1.1`, and those namespaces do not intersect. An exact-name join is what
    made path verification report no_path for every pre-existing host.

    Unclaimed logins (no array host object) still become hosts here — they are a real server someone
    has cabled — named from their IQN where it carries one, else from the initiator id.
    """
    ns_os = ns_os or {}
    by_initiator: dict[str, DiscoveredHost] = {}
    hosts: list[DiscoveredHost] = []

    def host_for(ids: list[str], name: str, source: str) -> DiscoveredHost:
        """The existing host owning any of these initiator ids, else a new one."""
        for i in ids:
            existing = by_initiator.get(i)
            if existing is not None:
                if source not in existing.sources:
                    existing.sources.append(source)
                return existing
        fresh = DiscoveredHost(name=name, sources=[source])
        hosts.append(fresh)
        return fresh

    # 1) vCenter first: it gives the best names, so it should win the naming race.
    for hba in report.host_hbas:
        host = host_for([normalize_wwpn(hba.wwpn)], hba.host_name, "vcenter")
        host.name = hba.host_name
        host.os = "esxi"                      # only ESXi hosts are in a vCenter inventory
        wwpn = normalize_wwpn(hba.wwpn)
        if wwpn not in host.wwpns:
            host.wwpns.append(wwpn)
        by_initiator[wwpn] = host
        if hba.fabric and hba.fabric not in host.fabrics:
            host.fabrics.append(hba.fabric)

    # 2) The array: what is actually logged in, plus every iSCSI initiator.
    port_fabric = {p.label: p.fabric for p in report.array_ports if p.protocol == "fc" and p.fabric}
    # UNCLAIMED logins are not one host. They are the array's bucket for every initiator no host
    # object claims, and on rack13arcus that single bucket holds a Windows IQN at 10.132.30.87 AND
    # an unrelated FC WWPN — two different machines. Nothing tells us which initiators belong
    # together, so each becomes its own unidentified server until a real source joins them.
    expanded: list[ArrayHost] = []
    for ah in report.array_hosts:
        if ah.name:
            expanded.append(ah)
            continue
        for wwpn, ports in ah.wwpns.items():
            expanded.append(ArrayHost(name="", persona=ah.persona, wwpns={wwpn: ports}))
        for iqn, ports in ah.iqns.items():
            expanded.append(ArrayHost(
                name="", persona=ah.persona, iqns={iqn: ports},
                addresses={iqn: ah.addresses[iqn]} if iqn in ah.addresses else {},
            ))

    for ah in expanded:
        ids = [*ah.wwpns, *ah.iqns]
        if not ids:
            # A host OBJECT with no initiators configured — `test2-alletra` on AlletraMP_D22U27
            # prints as `-- -- --`. It cannot be joined, zoned or provisioned, but it exists on the
            # array and an operator looking for it should see it rather than wonder where it went.
            hosts.append(DiscoveredHost(
                name=ah.name, os=os_from_persona(ah.persona), array_host_name=ah.name,
                sources=["array"],
            ))
            continue
        # The array's own name is preferred, EXCEPT when it is an auto-generated opaque one. HPE VME
        # registers as `HPE_VM_07dc508b8e41df1fcf6ab266` while its IQN says
        # `iqn.2024-12.com.hpe:hvm3:50796` — `hvm3` is the node an operator would recognise, and the
        # hash is not a name anyone should be shown. The array's version is kept in array_host_name.
        from_iqn = next((node_name_from_iqn(i) for i in ah.iqns if node_name_from_iqn(i)), "")
        opaque = ah.name.startswith("HPE_VM_")
        name = (from_iqn if (opaque and from_iqn) else ah.name) or from_iqn or ids[0]
        host = host_for(ids, name, "array")
        if ah.name and not host.array_host_name:
            host.array_host_name = ah.name
        for iqn, addr in ah.addresses.items():
            if addr and not host.address:
                host.address = addr
        for wwpn, ports in ah.wwpns.items():
            if wwpn not in host.wwpns:
                host.wwpns.append(wwpn)
            by_initiator[wwpn] = host
            for nsp in ports:
                host.logged_in = True
                fabric = port_fabric.get(nsp)
                if fabric and fabric not in host.fabrics:
                    host.fabrics.append(fabric)
        for iqn, ports in ah.iqns.items():
            if iqn not in host.iqns:
                host.iqns.append(iqn)
            by_initiator[iqn] = host
            if ports:
                host.logged_in = True
            if host.os == "unknown":
                host.os = os_from_iqn(iqn)
        # The array's own persona, after the IQN authority: an IQN is more specific (a VME host is
        # Generic-ALUA on the array but com.hpe in its IQN), and vCenter above is more specific
        # still. Without either, this is the only thing that identifies a Windows or ESXi FC host.
        if host.os == "unknown":
            host.os = os_from_persona(ah.persona)

    # 3) The fabric name server: the only OS signal for an FC host nothing else identified.
    for wwpn, os_text in ns_os.items():
        host = by_initiator.get(normalize_wwpn(wwpn))
        if host is not None and host.os == "unknown":
            host.os = os_from_switch_string(os_text)
            if "switch" not in host.sources:
                host.sources.append("switch")

    # Names derived from an IQN can collide: rack13arcus has three separate array host objects whose
    # IQNs all say `vmenode2` (…:38298, …:45566, …:62276) on different IPs. Three identical rows read
    # as one host listed thrice, so a collision falls back to the IQN's trailing id, which is what
    # distinguishes them. Names that came from vCenter or an array host object are left alone.
    seen: dict[str, int] = {}
    for host in hosts:
        seen[host.name] = seen.get(host.name, 0) + 1
    for host in hosts:
        if seen.get(host.name, 0) > 1 and host.iqns and not host.array_host_name.startswith(host.name):
            suffix = (host.iqns[0].rsplit(":", 1) + [""])[1]
            if suffix:
                host.name = f"{host.name}:{suffix}"

    return sorted(hosts, key=lambda h: (h.os, h.name.lower()))


def fabric_by_wwpn(array_hosts: list[ArrayHost], array_ports: list[ArrayPort]) -> dict[str, set[Fabric]]:
    """WWPN -> the fabrics it is logged into on the array (from showhost + the FC port fabric map)."""
    port_fabric = {port.label: port.fabric for port in array_ports if port.protocol == "fc" and port.fabric}
    out: dict[str, set[Fabric]] = {}
    for host in array_hosts:
        for wwpn, ports in host.wwpns.items():
            fabrics = {port_fabric[nsp] for nsp in ports if nsp in port_fabric}
            if fabrics:
                out.setdefault(wwpn, set()).update(fabrics)
    return out


def switch_for_wwpn(fcfabric: str, wwpn: str) -> str | None:
    """From `showportdev fcfabric <n:s:p>`, the switch this array port attaches to: the switch whose
    F-Port has the port's own WWPN as its attached N-Port. Returns the switch Logical Name, or None."""
    want = normalize_wwpn(wwpn)
    current: str | None = None
    for line in (fcfabric or "").splitlines():
        m = _LOGICAL_NAME_RE.match(line)
        if m:
            current = m.group(1)
            continue
        if "F-Port" in line and want and want in normalize_wwpn(line):
            return current
    return None


def resolve_port_fabrics(fc_ports: list[ArrayPort], switch_by_label: dict[str, str]) -> list[str]:
    """Assign each FC port's fabric, preferring the SWITCH it attaches to (from showportdev fcfabric)
    over card-port parity. Mutates `fabric` + `fabric_switch`; returns explanatory notes.

    Design (see docs/adr/0009): parity is a reliable default on standard dual-fabric cabling, but it is
    only a heuristic — the physical truth is which switch a port lands on. So:
      * exactly two attach-switches -> those ARE the two fabrics; map each to a slot (odd/even),
        preferring the slot its ports' parity already implies, and OVERRIDE parity where they differ
        (a note flags the non-standard cabling — the real bug parity can't see);
      * anything else (0/1/>2 switches, or ports down like a loss_sync array) -> fall back to parity,
        which is exactly what we did before this refinement. Never silently mislead: fallbacks/overrides
        are noted.
    """
    notes: list[str] = []
    for port in fc_ports:
        sw = switch_by_label.get(port.label)
        if sw:
            port.fabric_switch = sw

    def parity(port: ArrayPort) -> Fabric:
        return "odd" if port.card_port % 2 == 1 else "even"

    switches = sorted({sw for sw in switch_by_label.values() if sw})

    if len(switches) != 2:
        for port in fc_ports:
            port.fabric = parity(port)
        if len(switches) > 2:
            notes.append(
                f"Array FC ports resolved to {len(switches)} fabric switches ({', '.join(switches)}); "
                "used card-port parity for fabric (could not map them to exactly two fabrics)."
            )
        elif len(switches) == 1:
            on_sw = [p for p in fc_ports if switch_by_label.get(p.label) == switches[0]]
            if any(p.card_port % 2 for p in on_sw) and any(not p.card_port % 2 for p in on_sw):
                notes.append(
                    f"All resolved array FC ports attach to a single fabric ({switches[0]}) — the SAN "
                    "may be single-fabric; the dual-fabric (odd/even) zoning check assumes two fabrics."
                )
        return notes

    # Exactly two fabrics. Map each switch to a slot, preferring the parity its own ports imply.
    majority: dict[str, Fabric] = {}
    for sw in switches:
        on_sw = [p for p in fc_ports if switch_by_label.get(p.label) == sw]
        odd = sum(1 for p in on_sw if p.card_port % 2)
        majority[sw] = "odd" if odd * 2 >= len(on_sw) else "even"
    if len(set(majority.values())) == 2:
        label_of = majority
    else:  # both switches sit at the same port-parity -> parity can't name them; use a stable order
        label_of = {switches[0]: "odd", switches[1]: "even"}
        notes.append(
            f"Both array fabrics attach at the same card-port parity; labelled by switch: "
            f"{switches[0]}=odd, {switches[1]}=even."
        )
    for port in fc_ports:
        sw = switch_by_label.get(port.label)
        if sw in label_of:
            resolved = label_of[sw]
            if resolved != parity(port):
                notes.append(
                    f"Port {port.label} attaches to switch {sw} ({resolved} fabric) but its card-port "
                    f"parity is {parity(port)} — using the switch (non-standard cabling)."
                )
            port.fabric = resolved
        else:
            port.fabric = parity(port)  # not attached (e.g. loss_sync) -> parity fallback
    return notes


# `showportdev fcfabric` dumps the whole fabric mesh; on a large shared fabric each probe can be slow.
# It is best-effort (parity is the fallback), so cap each probe well under the CLI's default so one
# slow/hung port can't stall discovery for minutes.
_FCFABRIC_TIMEOUT = 30.0


def _refine_fabrics_from_switches(cli, array_ports: list[ArrayPort], *, progress=None) -> list[str]:
    """Run `showportdev fcfabric` on each READY FC port to learn the switch it attaches to, then
    resolve fabrics (switch-derived, parity fallback). Best-effort: a failed/empty per-port lookup
    just leaves that port on its parity fabric. Only 'ready' ports are probed — a down/loss_sync port
    isn't attached to a fabric, so probing it would only waste an SSH round-trip. `progress(msg)` (if
    given) is called before each probe so the operator sees which port is being resolved."""
    fc_ports = [p for p in array_ports if p.protocol == "fc"]
    ready = [p for p in fc_ports if p.link_state == "ready" and p.wwpn]
    switch_by_label: dict[str, str] = {}
    for i, port in enumerate(ready, 1):
        if progress:
            progress(f"Resolving the fabric switch for port {port.label} ({i}/{len(ready)})…")
        try:
            text = cli.run(f"showportdev fcfabric {port.label}", timeout=_FCFABRIC_TIMEOUT)
        except Exception:  # noqa: BLE001 - one flaky/slow lookup must not sink discovery
            continue
        sw = switch_for_wwpn(text, port.wwpn)
        if sw:
            switch_by_label[port.label] = sw
    return resolve_port_fabrics(fc_ports, switch_by_label)


def discover(
    intent: ProvisioningIntent,
    *,
    array_cli_factory: Callable = make_array_cli,
    vcenter_factory: Callable = make_vcenter,
    progress: Callable[[str], None] | None = None,
) -> DiscoveryReport:
    """Read the environment (array-side + vCenter), read-only. `progress(msg)`, if given, is called at
    each sub-step so a long run (the per-port fabric probe + vCenter connect can each take a while)
    shows live activity instead of looking hung."""
    report = DiscoveryReport()

    def _p(message: str) -> None:
        if progress:
            try:
                progress(message)
            except Exception:  # noqa: BLE001 - progress reporting must never break discovery
                pass

    # 1) Array (one SSH session): all FC + iSCSI target ports + the curated host view, then refine each
    #    FC port's fabric from the switch it attaches to (showportdev fcfabric; parity is the fallback).
    try:
        _p("Connecting to the array over SSH…")
        with array_cli_factory(intent.array) as cli:
            _p("Reading FC + iSCSI target ports (showport)…")
            iscsi_ips = parse_iscsi_ips(cli.run("showport -iscsi"))
            showport = cli.run("showport")
            report.array_ports = parse_ports(showport, iscsi_ips)
            # RCIP comes out of the SAME showport (Type rcip / free on a peer IP port). `showport
            # -rcip` only reports CONFIGURED links and answers "There is no specified port
            # information" when none exist, so it cannot enumerate the capable-but-idle ports.
            report.replication_ports = parse_replication_ports(showport)
            # `showport -rcip` adds the netmask + gateway a replication link actually needs. It
            # covers only CONFIGURED ports, so it enriches the list above rather than replacing it.
            try:
                detail = parse_rcip_detail(cli.run("showport -rcip"))
            except Exception:  # noqa: BLE001 - enrichment only; the ports are already listed
                detail = {}
            for port in report.replication_ports:
                extra = detail.get(port.label)
                if extra:
                    for field, value in extra.items():
                        setattr(port, field, value)
            # File services are a separate view with different columns, and are absent on arrays
            # without file configured — an empty result is normal, not a failure.
            try:
                report.file_ports = parse_file_ports(cli.run("showport -file"))
            except Exception:  # noqa: BLE001 - `showport -file` is unsupported on some releases
                report.notes.append("Could not read 'showport -file' — file ports not reported.")
            _p("Reading the array's host view (showhost)…")
            report.array_hosts = parse_showhost(cli.run("showhost -d"))
            fc = sum(1 for p in report.array_ports if p.protocol == "fc")
            isc = sum(1 for p in report.array_ports if p.protocol == "iscsi")
            # Count NAMED hosts and unclaimed logins separately: the unclaimed entry is one bucket
            # holding many WWPNs, so folding it into "N host(s)" would both inflate and understate.
            named = sum(1 for h in report.array_hosts if h.name)
            unclaimed = sum(len(h.wwpns) for h in report.array_hosts if not h.name)
            extra = f", {unclaimed} unclaimed login(s)" if unclaimed else ""
            roles = []
            if report.file_ports:
                roles.append(f"{len(report.file_ports)} file")
            if report.replication_ports:
                configured = sum(1 for p in report.replication_ports if p.role == "rcip")
                roles.append(f"{configured}/{len(report.replication_ports)} replication configured")
            role_text = f", {', '.join(roles)}" if roles else ""
            _p(f"Array: {fc} FC + {isc} iSCSI target port(s){role_text}, {named} host(s){extra}. "
               "Resolving fabrics…")
            report.notes.extend(_refine_fabrics_from_switches(cli, report.array_ports, progress=_p))
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"Array discovery (SSH) failed: {exc}")

    # 2) vCenter: each ESXi host's FC HBA WWPNs + OS.
    try:
        _p(f"Connecting to vCenter {intent.vcenter.host} (read-only)…")
        with vcenter_factory(intent.vcenter) as vcenter:
            report.host_hbas = vcenter.host_fc_hbas()
        _p(f"vCenter: {len(report.host_hbas)} ESXi host HBA(s).")
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"vCenter discovery failed: {exc}")

    # 3) Assign each vCenter HBA to the fabric its WWPN logs into ON THE ARRAY (from showhost).
    _p("Matching host HBAs to the array fabrics…")
    wwpn_fabric = fabric_by_wwpn(report.array_hosts, report.array_ports)
    for hba in report.host_hbas:
        fabrics = wwpn_fabric.get(normalize_wwpn(hba.wwpn))
        hba.fabric = sorted(fabrics)[0] if fabrics else None
        if not fabrics:
            report.notes.append(
                f"Host {hba.host_name} HBA {hba.wwpn} is not logged in on either fabric per the array "
                "(showhost) — check zoning/cabling, or that the host is powered on."
            )

    # 4) Join every source into one record per server, grouped by OS. Done last so it sees the
    #    fabric assignment above.
    #
    #    No `ns_os` yet: the fabric name server's OS string is read by the ZONING step, which logs
    #    into the switches; discovery deliberately needs only the array and vCenter, and the sheet
    #    makes switch credentials optional. So an FC host that is not in vCenter is reported with an
    #    unknown OS rather than guessed at. Wiring nsshow in here would make switch credentials a
    #    discovery prerequisite, which is a bigger change than this one.
    report.hosts = assemble_hosts(report)
    by_os: dict[str, int] = {}
    for host in report.hosts:
        by_os[host.os] = by_os.get(host.os, 0) + 1
    if by_os:
        _p("Hosts: " + ", ".join(f"{n} {os_}" for os_, n in sorted(by_os.items())))
    return report
