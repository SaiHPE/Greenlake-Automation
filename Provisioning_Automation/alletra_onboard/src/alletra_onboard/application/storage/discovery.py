"""Discovery: read the real environment a provisioning run will act on — array-side, read-only.

ONE array SSH session gathers the FC target ports (`showport`) and, per port, who is zoned + logged
in (`showportdev ns`) — the array names each host. vCenter supplies each ESXi host's HBA WWPNs + OS.
Each host HBA is then assigned to the fabric it logs into ON THE ARRAY (no switch needed). Zoning
verification computes over this DiscoveryReport — it does not read the array (or the switch) again.

Any one source failing is captured as a note, not a hard error.
"""

from __future__ import annotations

import re
from typing import Callable

from alletra_onboard.application.storage.clients import make_array_cli, make_vcenter
from alletra_onboard.domain.storage import (
    ArrayPort,
    DiscoveryReport,
    Fabric,
    NameserverEntry,
    ProvisioningIntent,
    normalize_wwpn,
)

_HEX16 = re.compile(r"\b[0-9A-Fa-f]{16}\b")  # bare 16-hex WWPN (array showport / showportdev ns form)


def array_target_ports(showport: str) -> list[tuple[str, Fabric, str]]:
    """FC target ports that are READY -> [(n:s:p, fabric, array_port_wwpn)]. Skips iSCSI + loss_sync.

    showport columns: N:S:P  Mode  State  Node_WWN  Port_WWN  Type  Protocol  Label
    """
    out: list[tuple[str, Fabric, str]] = []
    for line in (showport or "").splitlines():
        p = line.split()
        if len(p) >= 7 and ":" in p[0] and p[1] == "target" and p[2] == "ready" and "FC" in p:
            fabric: Fabric = "odd" if int(p[0].split(":")[2]) % 2 == 1 else "even"
            out.append((p[0], fabric, normalize_wwpn(p[4])))
    return out


def parse_ns(block: str) -> list[tuple[str, str]]:
    """Parse `showportdev ns` -> [(host_name, host_port_wwpn)], excluding the array's own self-row.

    Rows start with the PtId (0x…); the three 16-hex tokens are Node_WWN, Port_WWN, vp_WWN. We take
    Port_WWN (the initiator) and skip the array's self-listing (Node 2FF7… or Port == vp_WWN).
    """
    out: list[tuple[str, str]] = []
    for line in (block or "").splitlines():
        if not line.strip().startswith("0x"):
            continue
        hexes = [normalize_wwpn(h) for h in _HEX16.findall(line)]
        if len(hexes) < 2:
            continue
        node, port = hexes[0], hexes[1]
        vp = hexes[2] if len(hexes) >= 3 else ""
        if node.startswith("2FF7") or port == vp:
            continue
        out.append((line.split()[-1], port))
    return out


def discover(
    intent: ProvisioningIntent,
    *,
    array_cli_factory: Callable = make_array_cli,
    vcenter_factory: Callable = make_vcenter,
) -> DiscoveryReport:
    report = DiscoveryReport()
    union: dict[Fabric, set[str]] = {"odd": set(), "even": set()}

    # 1) Array (one SSH session): FC target ports + per-port nameserver (who's zoned + logged in).
    try:
        with array_cli_factory(intent.array) as cli:
            for nsp, fabric, arr_wwpn in array_target_ports(cli.run("showport")):
                node, slot, card_port = (int(x) for x in nsp.split(":"))
                report.array_ports.append(
                    ArrayPort(node=node, slot=slot, card_port=card_port, wwpn=arr_wwpn, link_state="ready", fabric=fabric)
                )
                for host_name, host_wwpn in parse_ns(cli.run(f"showportdev ns {nsp}")):
                    report.nameserver.append(
                        NameserverEntry(fabric=fabric, array_port=nsp, array_wwpn=arr_wwpn, host_wwpn=host_wwpn, host_name=host_name)
                    )
                    union[fabric].add(host_wwpn)
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"Array discovery (SSH) failed: {exc}")

    # 2) vCenter: each ESXi host's FC HBA WWPNs + OS.
    try:
        with vcenter_factory(intent.vcenter) as vcenter:
            report.host_hbas = vcenter.host_fc_hbas()
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"vCenter discovery failed: {exc}")

    # 3) Assign each host HBA to the fabric it logs into ON THE ARRAY (no switch).
    for hba in report.host_hbas:
        wwpn = normalize_wwpn(hba.wwpn)
        hba.fabric = "odd" if wwpn in union["odd"] else "even" if wwpn in union["even"] else None
        if hba.fabric is None:
            report.notes.append(
                f"Host {hba.host_name} HBA {hba.wwpn} is not zoned/logged in on either fabric — "
                "check cabling/zoning, or that the host is powered on."
            )
    return report
