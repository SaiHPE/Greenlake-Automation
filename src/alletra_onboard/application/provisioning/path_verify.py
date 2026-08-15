"""Tier-2 path verification (ADR 0010): after the array-side export, read `showvlun -a` back and
report, per host, whether the exported LUN is actually LIVE — over how many HBAs and which fabrics —
or "0 paths (host off / not zoned)". Strictly read-only; it *reports*, it never gates provisioning
(a `no_path` host is fine — the VLUN exists and activates the moment the host is on + zoned).

Calibrated against a live Alletra MP (OS 10.5.51) `showvlun -a`:

    Lun VVName                HostName              -Host_WWN/iSCSI_Name/Host_NQN- Port  Type     Status ID
      4 2nd_..._CRV_LZ_Infra  CRV_VZ_DL360G11D24U25 10009440C9D01212              0:3:1 host set active 10

`showvlun -a` lists only ACTIVE VLUNs, so a row here == a live path. Status is the ALUA path state:
`active` (active-optimized) and `nonopt` (active-non-optimized) both carry / can carry I/O — both count
as a live path. `Type` is one or two words (`host` / `host set`), so we anchor parsing on the unambiguous
`n:s:p` port token rather than fixed column offsets (tolerates a spaced volume name).
"""

from __future__ import annotations

import re

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.domain.shared import normalize_wwpn
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.provisioning import (
    HostPathStatus,
    PathVerification,
    ProvisioningIntent,
    VolumePath,
)

_NSP = re.compile(r"^\d+:\d+:\d+$")
# ALUA states that mean the path carries (or can carry) I/O — i.e. a LIVE path.
_LIVE_STATUS = {"active", "nonopt"}


def _fabric(port: str, fabric_by_port: dict[str, str] | None = None) -> str:
    """The fabric a path's array port sits on: the DISCOVERED (switch-derived) fabric when we have
    it, card-port parity only as the fallback (ADR 0009). Parity alone is a measured hazard: on
    4UW0004497 port 0:3:4 is even-parity but cabled to the F1 switch, so parity would count a
    0:3:1 + 0:3:4 host as redundant across both fabrics when both its paths are on F1 — a false
    redundancy claim, which is the one wrong answer a path VERIFIER must not produce."""
    if fabric_by_port and port in fabric_by_port:
        return fabric_by_port[port]
    try:
        return "odd" if int(port.split(":")[2]) % 2 == 1 else "even"
    except (ValueError, IndexError):
        return "?"


def parse_showvlun_active(text: str) -> list[VolumePath]:
    """`showvlun -a` -> [VolumePath] (one per active path). Columns:
    Lun VVName HostName Host_WWN Port Type[ set] Status ID. Anchored on the n:s:p port token."""
    out: list[VolumePath] = []
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) < 7 or not p[0].isdigit():
            continue
        port_idx = next((i for i, tok in enumerate(p) if _NSP.match(tok)), None)
        if port_idx is None or port_idx < 3:
            continue  # header / not a data row
        host_wwn = normalize_wwpn(p[port_idx - 1])
        if len(host_wwn) != 16:  # iSCSI IQN / NQN — not an FC path we verify here
            continue
        out.append(VolumePath(
            lun=int(p[0]),
            volume=" ".join(p[1 : port_idx - 2]),  # VVName may be multi-token; HostName is p[port_idx-2]
            host=p[port_idx - 2],
            host_wwpn=host_wwn,
            port=p[port_idx],
            status=p[-2].lower(),
        ))
    return out


def verify_paths(
    target_hosts: set[str],
    target_volumes: set[str],
    vlun_paths: list[VolumePath],
    fabric_by_port: dict[str, str] | None = None,
) -> PathVerification:
    """Per target host, classify the live paths to the target volumes (from `showvlun -a`).

    verdict: `live` (paths on BOTH fabrics), `partial` (one fabric only), `no_path` (none — host off or
    not zoned). `target_volumes` empty => consider every volume the host has an active path to.
    `fabric_by_port` (n:s:p -> odd/even, from discovery's switch-derived resolution) corrects the
    parity fallback on non-standard cabling — see _fabric.
    """
    report = PathVerification()
    if not target_hosts:
        report.notes.append("No target hosts to verify.")
        return report

    for host in sorted(target_hosts):
        paths = [
            vp for vp in vlun_paths
            if vp.host == host
            and vp.status in _LIVE_STATUS
            and (not target_volumes or vp.volume in target_volumes)
        ]
        live_vols = sorted({vp.volume for vp in paths})
        dead_vols = sorted(target_volumes - set(live_vols)) if target_volumes else []
        fabrics = sorted({_fabric(vp.port, fabric_by_port) for vp in paths} - {"?"})
        hbas = len({vp.host_wwpn for vp in paths})

        if not paths:
            verdict = "no_path"
            detail = "0 live paths — host off OR not zoned (export exists; it activates once the host is on + zoned)"
        elif len(fabrics) >= 2:
            verdict = "live"
            detail = f"{hbas} HBA(s) live on both fabrics ({', '.join(fabrics)})"
        else:
            verdict = "partial"
            missing = "even" if fabrics == ["odd"] else "odd"
            detail = f"{hbas} HBA(s) live on {fabrics[0]} fabric only — missing the {missing} fabric (single path)"

        if dead_vols:
            detail += f"; exported-but-no-path: {', '.join(dead_vols)}"
        report.hosts.append(HostPathStatus(
            host=host, verdict=verdict, hbas_with_paths=hbas, fabrics=fabrics,
            live_volumes=live_vols, dead_volumes=dead_vols, detail=detail,
        ))
    return report


def verify_provisioned_paths(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    array_cli_factory=make_array_cli,
) -> PathVerification:
    """Flow hook: read `showvlun -a` from the array (read-only SSH) and verify the exported LUNs are
    actually LIVE to the provisioned hosts. Target hosts = the discovered host-set members (the vCenter
    host list, else the array's own `showhost` hosts); target volumes = the intent's volumes. This is the
    tier-2 step called after `apply_plan` — read-only, and it reports rather than gating."""
    try:
        with array_cli_factory(intent.array) as cli:
            text = cli.run("showvlun -a")
    except Exception as exc:  # noqa: BLE001
        return PathVerification(error=f"Could not read 'showvlun -a' over SSH: {exc}")
    hosts = {h.host_name for h in discovery.host_hbas} or {ah.name for ah in discovery.array_hosts}
    # Discovery resolved each port's REAL fabric from the switch it attaches to (parity is only its
    # fallback) — hand that to the classifier so non-standard cabling can't fake dual-fabric redundancy.
    fabric_by_port = {
        p.label: p.fabric for p in discovery.array_ports if p.protocol == "fc" and p.fabric
    }
    return verify_paths(hosts, {v.name for v in intent.volumes}, parse_showvlun_active(text), fabric_by_port)
