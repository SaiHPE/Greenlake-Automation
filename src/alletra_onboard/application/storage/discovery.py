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


def discover(
    intent: ProvisioningIntent,
    *,
    array_cli_factory: Callable = make_array_cli,
    vcenter_factory: Callable = make_vcenter,
) -> DiscoveryReport:
    report = DiscoveryReport()

    # 1) Array (one SSH session): all FC + iSCSI target ports + the curated host view.
    try:
        with array_cli_factory(intent.array) as cli:
            iscsi_ips = parse_iscsi_ips(cli.run("showport -iscsi"))
            report.array_ports = parse_ports(cli.run("showport"), iscsi_ips)
            report.array_hosts = parse_showhost(cli.run("showhost -d"))
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"Array discovery (SSH) failed: {exc}")

    # 2) vCenter: each ESXi host's FC HBA WWPNs + OS.
    try:
        with vcenter_factory(intent.vcenter) as vcenter:
            report.host_hbas = vcenter.host_fc_hbas()
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"vCenter discovery failed: {exc}")

    # 3) Assign each vCenter HBA to the fabric its WWPN logs into ON THE ARRAY (from showhost).
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
