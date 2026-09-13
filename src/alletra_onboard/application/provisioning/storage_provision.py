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
    ArrayHostRecord,
    ArrayVolumeRecord,
    DiscoveredHostBrief,
    ExportRequest,
    PlannedAction,
    PlanState,
    ProvisioningIntent,
    ProvisioningPlan,
    ProvisioningResult,
    VlunTemplate,
    VolumeRequest,
)
from alletra_onboard.domain.shared import normalize_wwpn
from alletra_onboard.application.provisioning.hosts import union_hosts


def _union(intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None):
    """SPEC-003 R4: the one host union plan, apply, verification and the dropdown all derive from."""
    return union_hosts(discovery, getattr(intent, "declared_hosts", None) or [], zoning_plan)


def _hosts_by_name(
    discovery: DiscoveryReport, intent: ProvisioningIntent | None = None, zoning_plan: dict | None = None,
) -> "OrderedDict[str, list[str]]":
    """host name -> FC WWPNs, for every host the run can name (vCenter, sheet, array, fabric).

    An iSCSI-only host is included only when it already exists on the array (it can join a set;
    nothing has to be created for it). One that does not exist yet is left out: the WSAPI client
    registers FC WWNs only, and a host object created without its IQN would be a lie of omission."""
    hosts, _ = _union(intent, discovery, zoning_plan)
    return OrderedDict(
        (n, list(h.wwpns)) for n, h in hosts.items() if h.wwpns or (h.iqns and h.source == "array")
    )


def _host_notes(intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None,
                selected: OrderedDict[str, list[str]]) -> list[str]:
    """SPEC-003 R3/R5/R6 notes: nameless initiators, iSCSI-only members, hosts that cannot be created."""
    hosts, notes = _union(intent, discovery, zoning_plan)
    iscsi_members = [n for n in selected if not selected[n] and hosts[n].iqns]
    if iscsi_members:
        notes.append(
            "iSCSI-only member(s) in a host set: " + ", ".join(iscsi_members)
            + ". This tool's SAN zoning and path verification cover FC only — verify their paths by hand."
        )
    uncreatable = [n for n, h in hosts.items() if not h.wwpns and h.iqns and h.source != "array"]
    if uncreatable:
        notes.append(
            "Not planned — iSCSI host creation is not supported by this tool yet: " + ", ".join(uncreatable)
            + ". Create them on the array first; they can then be set members."
        )
    return notes


def _persona_by_host(
    discovery: DiscoveryReport, intent: ProvisioningIntent | None = None, zoning_plan: dict | None = None,
) -> dict[str, str]:
    """The host persona NAME for each host in the union (OS-derived, or the array's own)."""
    hosts, _ = _union(intent, discovery, zoning_plan)
    return {n: h.persona for n, h in hosts.items()}


def _members_for(host_set, all_hosts: "OrderedDict[str, list[str]]") -> list[str]:
    """A host set's members: the operator's selection, or ALL provisionable hosts when none is given.

    An explicit selection is still intersected with `all_hosts`, so a member that is not discovered —
    or that the zoning gate excluded — cannot reach the array as a set member with no host object
    behind it."""
    if not host_set.members:
        return list(all_hosts)
    return [m for m in host_set.members if m in all_hosts]


def _selected_hosts(
    intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None = None,
) -> "OrderedDict[str, list[str]]":
    """The hosts tier-1 will CREATE: only those the operator composed into a host set (ADR 0010's
    ideal subset) — never the whole inventory. On a shared vCenter, creating an array host object for
    every ESXi server in the inventory is pollution, not provisioning. With no host sets (the
    from_simple single-cluster shortcut) every host in the union is in scope, as before."""
    all_hosts = _hosts_by_name(discovery, intent, zoning_plan)
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


def _fabric_logins(discovery: DiscoveryReport, zoning_plan: dict | None) -> dict[str, list[set[str]]]:
    """host name -> [fabric labels seen by the array side, fabric labels seen by the switch side].
    Kept as two sets because the two sides label fabrics differently (odd/even vs F1/F2); the count
    that matters is the larger of the two, never their union."""
    array_side: dict[str, set[str]] = {}
    for hba in discovery.host_hbas:
        if hba.fabric:
            array_side.setdefault(hba.host_name, set()).add(hba.fabric)
    port_fabric = {p.label: p.fabric for p in discovery.array_ports if getattr(p, "fabric", None)}
    for ah in discovery.array_hosts:
        for ports in list(ah.wwpns.values()) + list(ah.iqns.values()):
            for port in ports:
                if port in port_fabric:
                    array_side.setdefault(ah.name, set()).add(port_fabric[port])
    switch_side: dict[str, set[str]] = {}
    for fab in (zoning_plan or {}).get("fabrics", []):
        for h in fab.get("hosts", []):
            if h.get("host_name") and h.get("fabric"):
                switch_side.setdefault(h["host_name"], set()).add(h["fabric"])
    return {n: [array_side.get(n, set()), switch_side.get(n, set())] for n in set(array_side) | set(switch_side)}


def host_briefs(
    discovery: DiscoveryReport, declared_hosts: list | None = None, zoning_plan: dict | None = None,
) -> list[DiscoveredHostBrief]:
    """Summarise each host in the union for the membership dropdown — the 'status text so a
    half-zoned host isn't picked blind' of ADR 0010, plus source and transport (SPEC-003 R5).
    FC-capable hosts first; iSCSI-only hosts last, saying that this tool does not zone or
    path-verify them."""
    hosts, _ = union_hosts(discovery, declared_hosts or [], zoning_plan)
    logins = _fabric_logins(discovery, zoning_plan)
    fc: list[DiscoveredHostBrief] = []
    iscsi: list[DiscoveredHostBrief] = []
    for name, h in hosts.items():
        if h.transport == "none":
            continue
        if not h.wwpns:
            iscsi.append(DiscoveredHostBrief(
                name=name, status="iSCSI only · not zoned or path-verified by this tool", wwpns=[],
                source=h.source, transport=h.transport, persona=h.persona, fc_capable=False,
            ))
            continue
        n_fabrics = max((len(s) for s in logins.get(name, [])), default=0)
        one = next((next(iter(s)) for s in logins.get(name, []) if len(s) == 1), "")
        if n_fabrics >= 2:
            status = f"{len(h.wwpns)} HBAs - both fabrics"
        elif n_fabrics == 1:
            status = f"{len(h.wwpns)} HBAs - one fabric ({one})"
        else:
            status = f"{len(h.wwpns)} HBAs - not logged in (off or unzoned)"
        fc.append(DiscoveredHostBrief(
            name=name, status=status, wwpns=list(h.wwpns),
            source=h.source, transport=h.transport, persona=h.persona, fc_capable=True,
        ))
    return fc + iscsi


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


def _reachable_targets(
    exports: list[ExportRequest],
    intent: ProvisioningIntent,
    all_hosts: "OrderedDict[str, list[str]]",
    reachable_hosts: set[str],
) -> tuple[list[ExportRequest], list[str]]:
    """Split the exports into (do now, skip) on whether the array can REACH the target.

    Gating the export and not the host is deliberate (ADR 0012, revised 2026-09-02). HPE's own
    documented order is register-first: `createhost -iscsi <name> <iqn>` takes an IQN the array has
    never seen, and the VME guidance says to register a host's IQN BEFORE it ever establishes a
    session. Host creation is harmless and reversible; an export to a host that cannot reach the
    array is the thing that reports "created" and is silently dead.

    A HOST-SET export needs only ONE reachable member. Exporting to the set is the practice HPE
    recommends for a cluster, and the remaining members pick the LUN up as they come online — that
    is the point of the set. It is skipped only when NO member can reach the array, because then
    there is nothing for it to be live for.
    """
    members_of = {hs.name: _members_for(hs, all_hosts) for hs in intent.host_sets}
    do: list[ExportRequest] = []
    skip: list[str] = []
    for ex in exports:
        if ex.target_kind == "hostset":
            members = members_of.get(ex.target_name, [])
            live = [m for m in members if m in reachable_hosts]
            if live:
                do.append(ex)
            else:
                skip.append(
                    f"{ex.source_name} → {ex.target_name}: no member of the host set can reach the "
                    f"array yet ({', '.join(members) or 'no members'})"
                )
        elif ex.target_name in reachable_hosts:
            do.append(ex)
        else:
            skip.append(f"{ex.source_name} → {ex.target_name}: the array cannot reach this host yet")
    return do, skip


def exported_volumes_by_host(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    reachable_hosts: set[str],
    zoning_plan: dict | None = None,
) -> "OrderedDict[str, set[str]]":
    """{host: the volumes actually exported to it} — the tier-2 verification target.

    Resolves host-set exports down to their members and expands a VV-set source to its volumes, so
    the verifier asks "is THIS volume live on THIS host" instead of crossing every host with every
    volume in the intent. Every provisioned host appears, including those with an empty set: a host
    whose export is held back is a real state worth reporting, not an absence.
    """
    hosts = _selected_hosts(intent, discovery, zoning_plan)
    out: "OrderedDict[str, set[str]]" = OrderedDict((name, set()) for name in hosts)
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError:
        return out                       # the plan refuses; there is nothing presented to verify
    exports, _held = _reachable_targets(exports, intent, hosts, reachable_hosts)
    vvsets = _vvsets(intent)
    members_of = {hs.name: _members_for(hs, hosts) for hs in intent.host_sets}
    for ex in exports:
        volumes = set(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else {ex.source_name}
        targets = members_of.get(ex.target_name, []) if ex.target_kind == "hostset" else [ex.target_name]
        for target in targets:
            if target in out:
                out[target] |= volumes
    return out


def build_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    reachable_hosts: set[str],
    wsapi_factory: Callable = make_wsapi,
    zoning_plan: dict | None = None,
) -> ProvisioningPlan:
    """Preview what tier-1 will create, and — SPEC-001 — what it will find already there.

    Every row carries a `state` the operator can approve against: create / exists (and matches) /
    update (exists, apply will add to it) / conflict (exists and differs in a way apply cannot fix —
    collected in `plan.blockers`, which refuses apply). Six reads, no writes.

    `reachable_hosts` is the gate, and it gates the EXPORT only (ADR 0012 revised 2026-09-02). Hosts,
    host sets, volumes and VV sets are always created: HPE's documented order is register-first, and
    creating a host object for a server that is not cabled yet is harmless and reversible. Required,
    not defaulted — a gate with a default-open value is how the switch write path shipped
    unauthorised, and every caller should have to state its answer.

    `zoning_plan` is the run's latest `zoning.plan` payload (SPEC-003): hosts the fabric named that
    no other source knows join the union through it."""
    plan = ProvisioningPlan()
    hosts = _selected_hosts(intent, discovery, zoning_plan)
    unreachable = sorted(n for n in hosts if n not in reachable_hosts)
    if not hosts:
        plan.notes.append("No host HBAs found by any source — nothing to provision until discovery finds hosts.")
    elif unreachable:
        plan.notes.append(
            "Created but not yet reachable: " + ", ".join(unreachable)
            + ". The host objects are made now; their exports wait until the array sees them logged "
            "in. Nothing here needs redoing once zoning is applied and re-verified."
        )
    plan.notes.extend(_host_notes(intent, discovery, zoning_plan, hosts))

    try:
        with wsapi_factory(intent.array) as array:
            state = _ArrayState(
                hosts=array.hosts(),
                host_sets=array.host_sets(),
                volumes=array.volumes(),
                volume_sets=array.volume_sets(),
                vluns=array.vlun_templates(),
                cpgs=set(array.cpg_names()),
            )
    except Exception as exc:  # noqa: BLE001
        plan.error = f"Could not read the array over WSAPI: {exc}"
        return plan

    # HARD gate, not a note (sd00003946: volume create fails with NON_EXISTENT_CPG; SSD_r6 is
    # auto-created at array init, so a missing CPG means the sheet or the array is wrong — verify,
    # never auto-create).
    missing_cpgs = sorted({v.cpg for v in intent.volumes} - state.cpgs)
    if missing_cpgs:
        plan.error = (
            "CPG(s) not found on the array: " + ", ".join(missing_cpgs)
            + ". Volume creation is hard-gated on the CPG existing — fix the sheet's CPG name or "
            "have the CPG created on the array first."
        )
        return plan

    def add(kind: str, name: str, description: str, verdict: tuple[PlanState, str], detail: dict) -> None:
        st, reason = verdict
        plan.actions.append(PlannedAction(
            kind=kind, name=name, description=description, state=st, reason=reason,
            exists=st != "create", detail=detail,
        ))
        if st == "conflict":
            plan.blockers.append(f"{kind} {name}: {reason}")

    personas = _persona_by_host(discovery, intent, zoning_plan)
    sources = {n: h.source for n, h in _union(intent, discovery, zoning_plan)[0].items()}
    for host_name, wwns in hosts.items():
        persona = personas.get(host_name, "VMware")
        add("host", host_name, f"Host {host_name} — {len(wwns)} FC WWN(s), persona {persona}",
            _judge_host(host_name, wwns, persona, state.hosts),
            {"wwns": wwns, "persona": persona, "source": sources.get(host_name, "")})

    for hs in intent.host_sets:
        members = _members_for(hs, hosts)
        add("hostset", hs.name, f"Host set {hs.name} — {len(members)} host(s)",
            _judge_set(hs.name, members, state.host_sets, "host"), {"members": members})

    for v in intent.volumes:
        add("volume", v.name, f"Volume {v.name} — {v.size_gib} GiB, {v.provisioning_type}, CPG {v.cpg}",
            _judge_volume(v, state.volumes),
            {"size_mib": v.size_mib, "cpg": v.cpg, "type": v.provisioning_type, "vvset": v.vvset})

    vvsets = _vvsets(intent)
    for vvset, vols in vvsets.items():
        add("vvset", vvset, f"Volume set {vvset} — {len(vols)} volume(s)",
            _judge_set(vvset, vols, state.volume_sets, "volume"), {"members": vols})

    # Presentation: the operator-composed exports (source volume|vvset x target host|hostset x LUN),
    # or the single-host-set default (each volume -> the set, auto LUN). Multiple host sets with no
    # composed exports REFUSE — see _resolve_exports.
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        plan.error = str(exc)
        return plan
    exports, skipped = _reachable_targets(exports, intent, hosts, reachable_hosts)
    for ex in exports:
        lun_txt = "auto LUN" if ex.lun is None else f"LUN {ex.lun}"
        add("vlun", ex.source_name,
            f"Export {ex.source_kind} {ex.source_name} → {ex.target_kind} {ex.target_name} ({lun_txt})",
            _judge_export(ex, vvsets, state.vluns), {"source": ex.source_ref, "target": ex.target_ref, "lun": ex.lun})
    if skipped:
        plan.notes.append("Exports held back until the array can reach the target: " + "; ".join(skipped))
    return plan


class _ArrayState:
    """What the array holds, read once per object type (SPEC-001 R9)."""

    def __init__(self, *, hosts, host_sets, volumes, volume_sets, vluns, cpgs) -> None:
        self.hosts: list[ArrayHostRecord] = list(hosts)
        self.host_sets: dict[str, list[str]] = dict(host_sets)
        self.volumes: list[ArrayVolumeRecord] = list(volumes)
        self.volume_sets: dict[str, list[str]] = dict(volume_sets)
        self.vluns: list[VlunTemplate] = list(vluns)
        self.cpgs: set[str] = set(cpgs)


def _gib(mib: int) -> str:
    return f"{mib / 1024:g} GiB"


def _judge_host(name: str, wwns: list[str], persona: str, on_array: list[ArrayHostRecord]) -> tuple[PlanState, str]:
    """R3: exists (carries every WWN) / update (adds the missing ones) / conflict (a WWN is someone
    else's — apply would raise). A persona difference is reported, never acted on."""
    wanted = {normalize_wwpn(w): w for w in wwns}
    owners = {normalize_wwpn(w): h.name for h in on_array for w in h.wwns}
    others = sorted({f"{wanted[w]} belongs to host {owners[w]}" for w in wanted if w in owners and owners[w] != name})
    if others:
        return "conflict", "; ".join(others) + " — resolve on the array before provisioning"
    mine = next((h for h in on_array if h.name == name), None)
    if mine is None:
        return "create", ""
    carried = {normalize_wwpn(w) for w in mine.wwns}
    missing = [wanted[w] for w in wanted if w not in carried]
    persona_note = (
        f" · persona on the array: {mine.persona}, intent {persona} — left unchanged"
        if mine.persona and mine.persona != persona else ""
    )
    if missing:
        return "update", f"adds {len(missing)} WWN: {', '.join(missing)}" + persona_note
    return "exists", f"carries all {len(wwns)} WWN(s)" + persona_note


def _judge_set(name: str, members: list[str], on_array: dict[str, list[str]], noun: str) -> tuple[PlanState, str]:
    """R4: additive only — exists (every member present) or update (adds the missing ones)."""
    if name not in on_array:
        return "create", ""
    missing = [m for m in members if m not in set(on_array[name])]
    if missing:
        return "update", f"adds {len(missing)} {noun}(s): {', '.join(missing)}"
    return "exists", f"has all {len(members)} {noun}(s)"


def _judge_volume(v: VolumeRequest, on_array: list[ArrayVolumeRecord]) -> tuple[PlanState, str]:
    """R2: a name match is not a match. Size, CPG and provisioning type must all agree, or the row is
    a conflict apply cannot fix (the array has no 'resize to intent' that is safe to do unasked)."""
    found = next((r for r in on_array if r.name == v.name), None)
    if found is None:
        return "create", ""
    on = f"{_gib(found.size_mib)} {found.provisioning_type} on {found.cpg}"
    want = f"{v.size_gib} GiB {v.provisioning_type} on {v.cpg}"
    if found.size_mib == v.size_mib and found.cpg == v.cpg and found.provisioning_type == v.provisioning_type:
        return "exists", f"{on} — matches"
    return "conflict", f"on the array: {on} · intent: {want}"


def _judge_export(ex: ExportRequest, vvsets: OrderedDict[str, list[str]], templates: list[VlunTemplate]) -> tuple[PlanState, str]:
    """R5: judged against the array's VLUN templates, one per member volume for a set export."""
    volumes = list(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else [ex.source_name]
    to_target = [t for t in templates if t.target == ex.target_ref]
    if ex.lun is not None:
        # a different volume already sits at that LUN on that target
        taken = sorted({t.volume for t in to_target if t.lun == ex.lun and t.volume not in volumes})
        if taken:
            return "conflict", f"LUN {ex.lun} on {ex.target_ref} is taken by volume {', '.join(taken)}"
        # our volume is already exported there, at a different LUN
        moved = sorted({f"{t.volume} at LUN {t.lun}" for t in to_target if t.volume in volumes and t.lun != ex.lun})
        if moved:
            return "conflict", f"already exported ({'; '.join(moved)}), intent says LUN {ex.lun}"
    present = {t.volume: t.lun for t in to_target if t.volume in volumes and (ex.lun is None or t.lun == ex.lun)}
    if not present:
        return "create", ""
    luns = ", ".join(f"LUN {present[v]}" for v in volumes if v in present)
    if len(present) < len(volumes):
        return "update", f"{len(present)} of {len(volumes)} member volumes already exported ({luns}); apply completes the set"
    return "exists", f"already exported at {luns}"


def apply_plan(
    intent: ProvisioningIntent,
    discovery: DiscoveryReport,
    *,
    reachable_hosts: set[str],
    wsapi_factory: Callable = make_wsapi,
    zoning_plan: dict | None = None,
) -> ProvisioningResult:
    """Create the objects. `reachable_hosts` and `zoning_plan` must be the SAME inputs `build_plan`
    was given: apply re-derives everything from the intent rather than replaying the plan, so
    without them here the held-back exports would be cosmetic and the host list would differ."""
    result = ProvisioningResult()
    hosts = _selected_hosts(intent, discovery, zoning_plan)
    if not hosts:
        result.error = "No host HBAs found by any source — refusing to provision with no hosts."
        return result
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        result.error = str(exc)
        return result
    exports, held = _reachable_targets(exports, intent, hosts, reachable_hosts)

    personas = _persona_by_host(discovery, intent, zoning_plan)
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

            export_outcomes: list[ActionOutcome] = []
            for ex in exports:
                status = array.ensure_vlun(ex.source_ref, ex.target_ref, lun=ex.lun)
                export_outcomes.append(ActionOutcome(kind="vlun", name=ex.source_name, status=status))

            # R8: "created" is the array's word; read the templates back ONCE and hold it to it.
            if exports:
                _confirm_exports(exports, export_outcomes, _vvsets(intent), array.vlun_templates())
            result.outcomes.extend(export_outcomes)
    except Exception as exc:  # noqa: BLE001 - record what we got, surface the failure
        result.error = str(exc)
    return result


def _confirm_exports(
    exports: list[ExportRequest],
    outcomes: list[ActionOutcome],
    vvsets: OrderedDict[str, list[str]],
    templates: list[VlunTemplate],
) -> None:
    """Annotate each export outcome with the LUN(s) the array actually recorded. A `created` export
    with no template on read-back becomes `failed` — the silent-dead-export case R8 exists for."""
    for ex, out in zip(exports, outcomes):
        volumes = list(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else [ex.source_name]
        found = {t.volume: t.lun for t in templates if t.target == ex.target_ref and t.volume in volumes}
        if found:
            out.detail = ", ".join(f"LUN {found[v]}" for v in volumes if v in found) + f" → {ex.target_ref}"
        elif out.status == "created":
            out.status = "failed"
            out.detail = f"the array reported created but no export {ex.source_ref} → {ex.target_ref} was found on read-back"
