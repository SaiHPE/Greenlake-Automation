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

from alletra_onboard.application.provisioning import storage_provision
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
    expected_by_host: dict[str, set[str]],
    vlun_paths: list[VolumePath],
    fabric_by_port: dict[str, str] | None = None,
    wwpns_by_host: dict[str, set[str]] | None = None,
) -> PathVerification:
    """Per host, classify the live paths to the volumes EXPORTED TO THAT HOST (from `showvlun -a`).

    `expected_by_host` is {host: volumes exported to it}, so the verifier reports on what was
    actually presented rather than on the intent as a whole. It replaces a (target_hosts,
    target_volumes) pair that crossed every host with every volume: on 2026-08-31 that told `.47`
    and `.86` they had a dead export of a volume only ever destined for `.136`. An empty volume set
    means "this host is a target but nothing is exported to it yet", which is a real state now that
    exports can be held back while host objects are created (ADR 0012 revised).

    verdict: `live` (paths on BOTH fabrics), `partial` (one fabric only), `no_path` (none — host off
    or not zoned). `fabric_by_port` (n:s:p -> odd/even, from discovery's switch-derived resolution)
    corrects the parity fallback on non-standard cabling — see _fabric.

    `wwpns_by_host` maps a target host to its HBA WWPNs, and a path whose Host_WWN is one of them
    counts for that host EVEN when the array's host-object name differs. The two names come from
    different namespaces — vCenter reports bare IPs/FQDNs while array host objects carry names like
    `CRV_VZ_DL360G11D24U25` (measured live: zero exact-name matches across three arrays) — so an
    exact-name join would report `no_path` for every pre-existing host, the one wrong answer a path
    verifier must not produce. The name match remains as the secondary key for hosts with no
    discovered HBAs.
    """
    report = PathVerification()
    if not expected_by_host:
        report.notes.append("No exports to verify.")
        return report

    for host in sorted(expected_by_host):
        expected = expected_by_host[host]
        hba_wwpns = (wwpns_by_host or {}).get(host, set())
        paths = [
            vp for vp in vlun_paths
            if (vp.host == host or vp.host_wwpn in hba_wwpns)
            and vp.status in _LIVE_STATUS
            and (not expected or vp.volume in expected)
        ]
        live_vols = sorted({vp.volume for vp in paths})
        # PER HOST, from what was actually exported TO THIS HOST. Until 2026-09-02 this was
        # "every intent volume minus the live ones" for every host verified, so a host in no export
        # row at all was reported as having an export with no path — measured on 2026-08-31, where
        # .47 and .86 were both told they had a dead export of a volume destined only for .136.
        dead_vols = sorted(expected - set(live_vols))
        fabrics = sorted({_fabric(vp.port, fabric_by_port) for vp in paths} - {"?"})
        hbas = len({vp.host_wwpn for vp in paths})

        if not paths:
            verdict = "no_path"
            # Only claim an export exists when one does. The old wording asserted it unconditionally
            # and was printed for volumes that had never been created, which reads as reassurance.
            detail = (
                f"0 live paths for {len(expected)} exported volume(s) — the host is off or not zoned; "
                "each activates once it is on and zoned"
                if expected else
                "0 live paths, and nothing is exported to this host"
            )
        elif len(fabrics) >= 2:
            verdict = "live"
            detail = f"{hbas} HBA(s) live on both fabrics ({', '.join(fabrics)})"
        else:
            verdict = "partial"
            missing = "even" if fabrics == ["odd"] else "odd"
            detail = f"{hbas} HBA(s) live on {fabrics[0]} fabric only — missing the {missing} fabric (single path)"

        if dead_vols and paths:
            detail += f"; exported but no path yet: {', '.join(dead_vols)}"
        # WWPN-matched under a different array host-object name: say which, so the operator can
        # correlate this verdict with `showhost` output on the array.
        object_names = sorted({vp.host for vp in paths if vp.host != host})
        if object_names:
            detail += f" [array host object: {', '.join(object_names)}]"
        report.hosts.append(HostPathStatus(
            host=host, verdict=verdict, hbas_with_paths=hbas, fabrics=fabrics,
            live_volumes=live_vols, dead_volumes=dead_vols, detail=detail,
        ))
    return report


def verify_provisioned_paths(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    reachable_hosts: set[str],
    array_cli_factory=make_array_cli,
    zoning_plan: dict | None = None,
) -> PathVerification:
    """Flow hook: read `showvlun -a` from the array (read-only SSH) and verify the exported LUNs are
    actually LIVE on the hosts they were presented to.

    Targets come from the PROVISIONING INTENT's exports, resolved per host — not from the vCenter
    inventory. Verifying every host vCenter happens to know produced verdicts about machines this run
    never touched (2026-08-31: `.47` and `.86`, neither of them in any export row, were both reported
    as having a dead export). Read-only, and it reports rather than gating (ADR 0010)."""
    try:
        with array_cli_factory(intent.array) as cli:
            text = cli.run("showvlun -a")
    except Exception as exc:  # noqa: BLE001
        return PathVerification(error=f"Could not read 'showvlun -a' over SSH: {exc}")
    expected_by_host = storage_provision.exported_volumes_by_host(intent, discovery, reachable_hosts, zoning_plan)
    # The join key between "the hosts the run knows" and "the paths the array reports" is the HBA
    # WWPN, never the name — the two namespaces don't intersect on real arrays (see verify_paths).
    # SPEC-003: the hosts come from the same union plan and apply used, so a sheet-declared or
    # fabric-named host is verified, not reported as pathless because vCenter never heard of it.
    wwpns_by_host: dict[str, set[str]] = {
        name: {normalize_wwpn(w) for w in wwpns}
        for name, wwpns in storage_provision._hosts_by_name(discovery, intent, zoning_plan).items()
    }
    # Discovery resolved each port's REAL fabric from the switch it attaches to (parity is only its
    # fallback) — hand that to the classifier so non-standard cabling can't fake dual-fabric redundancy.
    fabric_by_port = {
        p.label: p.fabric for p in discovery.array_ports if p.protocol == "fc" and p.fabric
    }
    return verify_paths(
        dict(expected_by_host), parse_showvlun_active(text), fabric_by_port, wwpns_by_host,
    )
