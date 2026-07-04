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

from alletra_onboard.application.storage.clients import make_array_cli, make_vcenter
from alletra_onboard.domain.storage import (
    ArrayHost,
    ArrayPort,
    DiscoveryReport,
    Fabric,
    ProvisioningIntent,
    normalize_wwpn,
)

_LOGICAL_NAME_RE = re.compile(r"^\s*Logical Name:\s*(\S+)", re.IGNORECASE)


def parse_iscsi_ips(showport_iscsi: str) -> dict[str, str]:
    """`showport -iscsi` -> {n:s:p: target IP}. Columns: N:S:P State IPAddr ... (offline -> '')."""
    ips: dict[str, str] = {}
    for line in (showport_iscsi or "").splitlines():
        p = line.split()
        if len(p) >= 3 and p[0][:1].isdigit() and ":" in p[0]:
            ips[p[0]] = "" if p[1] == "offline" else p[2]
    return ips


def parse_ports(showport: str, iscsi_ips: dict[str, str]) -> list[ArrayPort]:
    """ALL FC + iSCSI TARGET ports (any state) -> [ArrayPort]. Skips SAS/disk + IP/rcip peer ports.

    showport columns: N:S:P  Mode  State  Node_WWN/IP  Port_WWN/HW_Addr  Type  Protocol  Label ...
    (a multi-word Label like "Peer Port 2" trails Protocol, so token[6] is always the Protocol).
    """
    out: list[ArrayPort] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0][:1].isdigit() or ":" not in p[0] or p[1] != "target":
            continue
        protocol = p[6]
        if protocol not in ("FC", "iSCSI"):
            continue
        try:
            node, slot, card_port = (int(x) for x in p[0].split(":"))
        except ValueError:
            continue
        if protocol == "FC":
            fabric: Fabric = "odd" if card_port % 2 == 1 else "even"
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="fc",
                wwpn=normalize_wwpn(p[4]), link_state=p[2], fabric=fabric,
            ))
        else:
            out.append(ArrayPort(
                node=node, slot=slot, card_port=card_port, protocol="iscsi",
                address=iscsi_ips.get(p[0], ""), link_state=p[2], fabric=None,
            ))
    return out


def parse_showhost(showhost_d: str) -> list[ArrayHost]:
    """`showhost -d` -> [ArrayHost]. Columns: Id  Name  Persona  WWN/iSCSI_Name  Port  IP_addr.

    Parsed from the RIGHT (so a multi-word host name is tolerated). Keeps only real FC WWPNs (16 hex)
    and real n:s:p logins; a WWPN with no n:s:p (Port '---'/'--') is configured-but-not-logged-in.
    iSCSI IQNs / NQNs are not 16-hex so they are ignored for FC zoning.
    """
    hosts: "OrderedDict[str, ArrayHost]" = OrderedDict()
    for line in (showhost_d or "").splitlines():
        p = line.split()
        if len(p) < 6 or not p[0].isdigit():
            continue
        port, wwn, persona = p[-2], p[-3], p[-4]
        name = " ".join(p[1:-4]) or p[1]
        host = hosts.setdefault(name, ArrayHost(name=name, persona=persona))
        wwpn = normalize_wwpn(wwn)
        if len(wwpn) != 16:  # an iqn / NQN / '--' / 'digtest' — not an FC WWPN
            continue
        ports = host.wwpns.setdefault(wwpn, [])
        if ":" in port and port not in ports:  # a real login (Port == n:s:p), not '---' / '--'
            ports.append(port)
    return list(hosts.values())


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
            report.array_ports = parse_ports(cli.run("showport"), iscsi_ips)
            _p("Reading the array's host view (showhost)…")
            report.array_hosts = parse_showhost(cli.run("showhost -d"))
            fc = sum(1 for p in report.array_ports if p.protocol == "fc")
            isc = sum(1 for p in report.array_ports if p.protocol == "iscsi")
            _p(f"Array: {fc} FC + {isc} iSCSI target port(s), {len(report.array_hosts)} host(s). Resolving fabrics…")
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
    return report
