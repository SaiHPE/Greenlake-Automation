"""Discovery: read the real environment a provisioning run will act on.

Combines three read-only sources into one DiscoveryReport:
- the **array** (WSAPI): FC target ports + WWPNs + state, fabric by card-port parity;
- **vCenter** (pyVmomi): each ESXi host's FC HBA WWPNs + OS;
- **both SAN switches** (Brocade nsshow): who is logged into each fabric — the live truth that tells
  us which fabric each host HBA WWPN actually sits on (odd vs even).

Any one source failing is captured as a note, not a hard error — a partial report still helps the
operator (e.g. discover the array + hosts even if a switch is unreachable).
"""

from __future__ import annotations

import re
from typing import Callable

from alletra_onboard.application.storage.clients import make_brocade, make_vcenter, make_wsapi
from alletra_onboard.domain.storage import (
    DiscoveryReport,
    Fabric,
    NameserverEntry,
    ProvisioningIntent,
    normalize_wwpn,
)

_WWPN_RE = re.compile(r"\b(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}\b")


def parse_nameserver_wwpns(text: str) -> set[str]:
    """Every WWPN-shaped token in nsshow output, normalized (colon-hex -> canonical)."""
    return {normalize_wwpn(m.group(0)) for m in _WWPN_RE.finditer(text or "")}


def discover(
    intent: ProvisioningIntent,
    *,
    wsapi_factory: Callable = make_wsapi,
    vcenter_factory: Callable = make_vcenter,
    brocade_factory: Callable = make_brocade,
) -> DiscoveryReport:
    report = DiscoveryReport()

    try:
        with wsapi_factory(intent.array) as array:
            report.array_ports = array.array_fc_ports()
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"Array WSAPI discovery failed: {exc}")

    try:
        with vcenter_factory(intent.vcenter) as vcenter:
            report.host_hbas = vcenter.host_fc_hbas()
    except Exception as exc:  # noqa: BLE001
        report.notes.append(f"vCenter discovery failed: {exc}")

    array_wwpns = {p.wwpn for p in report.array_ports}
    ns_by_fabric: dict[Fabric, set[str]] = {"odd": set(), "even": set()}
    for fabric, creds in (("odd", intent.switch_f1), ("even", intent.switch_f2)):
        try:
            with brocade_factory(creds) as switch:
                wwpns = parse_nameserver_wwpns(switch.nsshow())
        except Exception as exc:  # noqa: BLE001
            report.notes.append(f"{fabric} switch ({creds.host}) nsshow failed: {exc}")
            continue
        ns_by_fabric[fabric] = wwpns
        for wwpn in sorted(wwpns):
            report.nameserver.append(
                NameserverEntry(
                    fabric=fabric, switch_host=creds.host, wwpn=wwpn,
                    is_array_port=wwpn in array_wwpns,
                )
            )

    # Assign each host HBA to the fabric whose nameserver it logs into (the physical-cabling truth).
    for hba in report.host_hbas:
        if hba.wwpn in ns_by_fabric["odd"]:
            hba.fabric = "odd"
        elif hba.wwpn in ns_by_fabric["even"]:
            hba.fabric = "even"
        else:
            report.notes.append(
                f"Host {hba.host_name} HBA {hba.wwpn} is not logged into either fabric — "
                "check cabling/zoning for that port."
            )
    return report
