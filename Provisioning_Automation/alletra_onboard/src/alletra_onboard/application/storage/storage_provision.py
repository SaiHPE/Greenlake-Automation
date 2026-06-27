"""Storage provisioning: host(s) -> host set -> volumes -> (optional VV set) -> export (VLUN).

build_plan() reads the array and produces a preview (what will be created, what already exists) for
the operator to confirm. apply_plan() executes it idempotently — each create reports created/exists,
never failing on a re-run (EXISTENT_HOST / EXISTENT_SV / EXISTENT_VLUN).

Modelled on the verified design: ONE host definition per ESXi server carrying ALL its FC WWNs at
VMware persona 11, grouped in the cluster host set, with volumes exported to the host SET so every
host in the cluster sees them down multiple paths (ALUA).
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Callable

from alletra_onboard.application.storage.clients import make_wsapi
from alletra_onboard.domain.storage import (
    ActionOutcome,
    DiscoveryReport,
    PlannedAction,
    ProvisioningIntent,
    ProvisioningPlan,
    ProvisioningResult,
)

_GIB_TO_MIB = 1024


def _hosts_by_name(discovery: DiscoveryReport) -> "OrderedDict[str, list[str]]":
    """Group discovered HBA WWPNs by ESXi host name, de-duplicated, preserving order."""
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for hba in discovery.host_hbas:
        wwns = grouped.setdefault(hba.host_name, [])
        if hba.wwpn not in wwns:
            wwns.append(hba.wwpn)
    return grouped


def build_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    wsapi_factory: Callable = make_wsapi,
) -> ProvisioningPlan:
    plan = ProvisioningPlan()
    hosts = _hosts_by_name(discovery)
    if not hosts:
        plan.notes.append("No ESXi host HBAs discovered — nothing to provision until discovery finds hosts.")

    try:
        with wsapi_factory(intent.array) as array:
            existing_hosts = set(array.host_names())
            existing_host_sets = set(array.host_set_names())
            existing_volumes = set(array.volume_names())
            existing_vsets = set(array.volume_set_names())
            if intent.cpg not in set(array.cpg_names()):
                plan.notes.append(f"CPG '{intent.cpg}' was not found on the array — volume creation will fail.")
    except Exception as exc:  # noqa: BLE001
        plan.error = f"Could not read the array over WSAPI: {exc}"
        return plan

    for host_name, wwns in hosts.items():
        plan.actions.append(PlannedAction(
            kind="host", name=host_name,
            description=f"Host {host_name} — {len(wwns)} FC WWN(s), persona 11 (VMware/ALUA)",
            exists=host_name in existing_hosts,
            detail={"wwns": wwns},
        ))
    plan.actions.append(PlannedAction(
        kind="hostset", name=intent.host_set_name,
        description=f"Host set {intent.host_set_name} — {len(hosts)} host(s)",
        exists=intent.host_set_name in existing_host_sets,
        detail={"members": list(hosts)},
    ))

    vol_names = intent.volume.names()
    size_mib = intent.volume.size_gib * _GIB_TO_MIB
    for name in vol_names:
        plan.actions.append(PlannedAction(
            kind="volume", name=name,
            description=f"Volume {name} — {intent.volume.size_gib} GiB, {intent.provisioning_type}, CPG {intent.cpg}",
            exists=name in existing_volumes,
            detail={"size_mib": size_mib, "cpg": intent.cpg, "type": intent.provisioning_type},
        ))
    if intent.vvset_name:
        plan.actions.append(PlannedAction(
            kind="vvset", name=intent.vvset_name,
            description=f"Volume set {intent.vvset_name} — {len(vol_names)} volume(s)",
            exists=intent.vvset_name in existing_vsets,
            detail={"members": vol_names},
        ))
    for name in vol_names:
        plan.actions.append(PlannedAction(
            kind="vlun", name=name,
            description=f"Export {name} → host set {intent.host_set_name} (auto LUN)",
            detail={"host_set": intent.host_set_name},
        ))
    return plan


def apply_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    wsapi_factory: Callable = make_wsapi,
) -> ProvisioningResult:
    result = ProvisioningResult()
    hosts = _hosts_by_name(discovery)
    if not hosts:
        result.error = "No ESXi host HBAs discovered — refusing to provision with no hosts."
        return result

    host_set_ref = f"set:{intent.host_set_name}"  # VLUN export target for the whole cluster
    vol_names = intent.volume.names()
    size_mib = intent.volume.size_gib * _GIB_TO_MIB
    try:
        with wsapi_factory(intent.array) as array:
            for host_name, wwns in hosts.items():
                status = array.ensure_host(host_name, wwns)
                result.outcomes.append(ActionOutcome(kind="host", name=host_name, status=status))

            status = array.ensure_host_set(intent.host_set_name, list(hosts))
            result.outcomes.append(ActionOutcome(kind="hostset", name=intent.host_set_name, status=status))

            for name in vol_names:
                status = array.ensure_volume(name, intent.cpg, size_mib, intent.provisioning_type)
                result.outcomes.append(ActionOutcome(kind="volume", name=name, status=status))

            if intent.vvset_name:
                status = array.ensure_volume_set(intent.vvset_name, vol_names)
                result.outcomes.append(ActionOutcome(kind="vvset", name=intent.vvset_name, status=status))

            for name in vol_names:
                status = array.ensure_vlun(name, host_set_ref)
                result.outcomes.append(ActionOutcome(kind="vlun", name=name, status=status))
    except Exception as exc:  # noqa: BLE001 - record what we got, surface the failure
        result.error = str(exc)
    return result
