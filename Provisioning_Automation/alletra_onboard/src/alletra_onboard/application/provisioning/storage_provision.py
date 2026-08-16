"""Storage provisioning: host(s) -> host set -> volumes -> (optional VV set) -> export (VLUN).

build_plan() reads the array and produces a preview (what will be created, what already exists) for
the operator to confirm. apply_plan() executes it idempotently — each create reports created/exists,
never failing on a re-run (EXISTENT_HOST / EXISTENT_SV / EXISTENT_VLUN).

Modelled on the verified design: ONE host definition per ESXi server carrying ALL its FC WWNs at
the VMware persona, grouped in the cluster host set, with volumes exported to the host SET so every
host in the cluster sees them down multiple paths (ALUA).
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Callable

from alletra_onboard.application.provisioning.clients import make_wsapi
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.provisioning import (
    ActionOutcome,
    DiscoveredHostBrief,
    ExportRequest,
    PlannedAction,
    ProvisioningIntent,
    ProvisioningPlan,
    ProvisioningResult,
    persona_for_os,
)

def _hosts_by_name(discovery: DiscoveryReport) -> "OrderedDict[str, list[str]]":
    """Group discovered HBA WWPNs by ESXi host name, de-duplicated, preserving order."""
    grouped: OrderedDict[str, list[str]] = OrderedDict()
    for hba in discovery.host_hbas:
        wwns = grouped.setdefault(hba.host_name, [])
        if hba.wwpn not in wwns:
            wwns.append(hba.wwpn)
    return grouped


def _persona_by_host(discovery: DiscoveryReport) -> dict[str, str]:
    """The host persona NAME for each discovered host, derived from its OS (default VMware)."""
    personas: dict[str, str] = {}
    for hba in discovery.host_hbas:
        personas.setdefault(hba.host_name, persona_for_os(hba.os))
    return personas


def _members_for(host_set, all_hosts: "OrderedDict[str, list[str]]") -> list[str]:
    """A host set's members: the operator's selection, or ALL discovered hosts when none is given."""
    return list(host_set.members) if host_set.members else list(all_hosts)


def _selected_hosts(intent: ProvisioningIntent, discovery: DiscoveryReport) -> "OrderedDict[str, list[str]]":
    """The hosts tier-1 will CREATE: only those the operator composed into a host set (ADR 0010's
    ideal subset) — never the whole vCenter inventory. On a shared vCenter, creating an array host
    object for every ESXi server in the inventory is pollution, not provisioning. With no host sets
    (the from_simple single-cluster shortcut) every discovered host is in scope, as before."""
    all_hosts = _hosts_by_name(discovery)
    if not intent.host_sets:
        return all_hosts
    wanted = {m for hs in intent.host_sets for m in _members_for(hs, all_hosts)}
    return OrderedDict((n, w) for n, w in all_hosts.items() if n in wanted)


def _vvsets(intent: ProvisioningIntent) -> "OrderedDict[str, list[str]]":
    """Group volume names by the VV-set each volume asked to join (order preserved)."""
    sets: OrderedDict[str, list[str]] = OrderedDict()
    for v in intent.volumes:
        if v.vvset:
            sets.setdefault(v.vvset, []).append(v.name)
    return sets


def read_array_objects(intent: ProvisioningIntent, *, wsapi_factory: Callable = make_wsapi) -> dict:
    """Read the objects that already exist on the array (for the builder's dropdowns). Degrades
    gracefully: if the array can't be read, returns empty lists + an error string so the palette is
    still usable from the to-be-created + discovered objects."""
    try:
        with wsapi_factory(intent.array) as array:
            return {
                "cpgs": sorted(array.cpg_names()),
                "hosts": sorted(array.host_names()),
                "host_sets": sorted(array.host_set_names()),
                "volumes": sorted(array.volume_names()),
                "volume_sets": sorted(array.volume_set_names()),
                "error": None,
            }
    except Exception as exc:  # noqa: BLE001 - the palette still works without the existing objects
        return {"cpgs": [], "hosts": [], "host_sets": [], "volumes": [], "volume_sets": [], "error": str(exc)}


def host_briefs(discovery: DiscoveryReport) -> list[DiscoveredHostBrief]:
    """Summarise each discovered ESXi host's fabric-login state for the membership dropdown — the
    'status text so a half-zoned host isn't picked blind' of ADR 0010."""
    per_host = _hosts_by_name(discovery)
    fabrics_by_host: OrderedDict[str, set[str]] = OrderedDict()
    for hba in discovery.host_hbas:
        by = fabrics_by_host.setdefault(hba.host_name, set())
        if hba.fabric:
            by.add(hba.fabric)

    briefs: list[DiscoveredHostBrief] = []
    for name, wwns in per_host.items():
        fabrics = fabrics_by_host.get(name, set())
        if len(fabrics) >= 2:
            status = f"{len(wwns)} HBAs - both fabrics"
        elif len(fabrics) == 1:
            status = f"{len(wwns)} HBAs - one fabric ({next(iter(fabrics))})"
        else:
            status = f"{len(wwns)} HBAs - not logged in (off or unzoned)"
        briefs.append(DiscoveredHostBrief(name=name, status=status, wwpns=wwns))
    return briefs


class ExportDefaultError(ValueError):
    """No exports were composed and the default cannot be chosen safely."""


def _resolve_exports(intent: ProvisioningIntent) -> list[ExportRequest]:
    """The presentations (VLUNs) to create: the operator's explicit export list, or — when none was
    composed and there is exactly ONE host set — every volume to that set at an auto LUN (the
    verified single-cluster model: the array keeps the LUN id consistent across the set's hosts).

    With MULTIPLE host sets and no composed exports this REFUSES: the old default (every volume ×
    every host set) presents the same VMFS volume to unrelated clusters — a corruption-shaped
    default, not a convenience."""
    if intent.exports:
        return list(intent.exports)
    if len(intent.host_sets) > 1:
        raise ExportDefaultError(
            "No exports were composed and more than one host set is defined — refusing the "
            "every-volume-to-every-host-set default (it would present the same volume to unrelated "
            "clusters). Compose the exports explicitly in the builder."
        )
    return [
        ExportRequest(source_kind="volume", source_name=v.name, target_kind="hostset", target_name=hs.name)
        for hs in intent.host_sets
        for v in intent.volumes
    ]


def build_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    wsapi_factory: Callable = make_wsapi,
) -> ProvisioningPlan:
    plan = ProvisioningPlan()
    hosts = _selected_hosts(intent, discovery)
    if not hosts:
        plan.notes.append("No ESXi host HBAs discovered — nothing to provision until discovery finds hosts.")

    try:
        with wsapi_factory(intent.array) as array:
            existing_hosts = set(array.host_names())
            existing_host_sets = set(array.host_set_names())
            existing_volumes = set(array.volume_names())
            existing_vsets = set(array.volume_set_names())
            cpgs = set(array.cpg_names())
    except Exception as exc:  # noqa: BLE001
        plan.error = f"Could not read the array over WSAPI: {exc}"
        return plan

    # HARD gate, not a note (sd00003946: volume create fails with NON_EXISTENT_CPG; SSD_r6 is
    # auto-created at array init, so a missing CPG means the sheet or the array is wrong — verify,
    # never auto-create).
    missing_cpgs = sorted({v.cpg for v in intent.volumes} - cpgs)
    if missing_cpgs:
        plan.error = (
            "CPG(s) not found on the array: " + ", ".join(missing_cpgs)
            + ". Volume creation is hard-gated on the CPG existing — fix the sheet's CPG name or "
            "have the CPG created on the array first."
        )
        return plan

    personas = _persona_by_host(discovery)
    for host_name, wwns in hosts.items():
        persona = personas.get(host_name, "VMware")
        plan.actions.append(PlannedAction(
            kind="host", name=host_name,
            description=f"Host {host_name} — {len(wwns)} FC WWN(s), persona {persona}",
            exists=host_name in existing_hosts,
            detail={"wwns": wwns, "persona": persona},
        ))

    for hs in intent.host_sets:
        members = _members_for(hs, hosts)
        plan.actions.append(PlannedAction(
            kind="hostset", name=hs.name,
            description=f"Host set {hs.name} — {len(members)} host(s)",
            exists=hs.name in existing_host_sets,
            detail={"members": members},
        ))

    for v in intent.volumes:
        plan.actions.append(PlannedAction(
            kind="volume", name=v.name,
            description=f"Volume {v.name} — {v.size_gib} GiB, {v.provisioning_type}, CPG {v.cpg}",
            exists=v.name in existing_volumes,
            detail={"size_mib": v.size_mib, "cpg": v.cpg, "type": v.provisioning_type, "vvset": v.vvset},
        ))

    for vvset, vols in _vvsets(intent).items():
        plan.actions.append(PlannedAction(
            kind="vvset", name=vvset,
            description=f"Volume set {vvset} — {len(vols)} volume(s)",
            exists=vvset in existing_vsets,
            detail={"members": vols},
        ))

    # Presentation: the operator-composed exports (source volume|vvset x target host|hostset x LUN),
    # or the single-host-set default (each volume -> the set, auto LUN). Multiple host sets with no
    # composed exports REFUSE — see _resolve_exports.
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        plan.error = str(exc)
        return plan
    for ex in exports:
        lun_txt = "auto LUN" if ex.lun is None else f"LUN {ex.lun}"
        plan.actions.append(PlannedAction(
            kind="vlun", name=ex.source_name,
            description=f"Export {ex.source_kind} {ex.source_name} → {ex.target_kind} {ex.target_name} ({lun_txt})",
            detail={"source": ex.source_ref, "target": ex.target_ref, "lun": ex.lun},
        ))
    return plan


def apply_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    wsapi_factory: Callable = make_wsapi,
) -> ProvisioningResult:
    result = ProvisioningResult()
    hosts = _selected_hosts(intent, discovery)
    if not hosts:
        result.error = "No ESXi host HBAs discovered — refusing to provision with no hosts."
        return result
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        result.error = str(exc)
        return result

    personas = _persona_by_host(discovery)
    try:
        with wsapi_factory(intent.array) as array:
            for host_name, wwns in hosts.items():
                status = array.ensure_host(host_name, wwns, persona=personas.get(host_name, "VMware"))
                result.outcomes.append(ActionOutcome(kind="host", name=host_name, status=status))

            for hs in intent.host_sets:
                status = array.ensure_host_set(hs.name, _members_for(hs, hosts))
                result.outcomes.append(ActionOutcome(kind="hostset", name=hs.name, status=status))

            for v in intent.volumes:
                status = array.ensure_volume(v.name, v.cpg, v.size_mib, v.provisioning_type)
                result.outcomes.append(ActionOutcome(kind="volume", name=v.name, status=status))

            for vvset, vols in _vvsets(intent).items():
                status = array.ensure_volume_set(vvset, vols)
                result.outcomes.append(ActionOutcome(kind="vvset", name=vvset, status=status))

            for ex in exports:
                status = array.ensure_vlun(ex.source_ref, ex.target_ref, lun=ex.lun)
                result.outcomes.append(ActionOutcome(kind="vlun", name=ex.source_name, status=status))
    except Exception as exc:  # noqa: BLE001 - record what we got, surface the failure
        result.error = str(exc)
    return result
