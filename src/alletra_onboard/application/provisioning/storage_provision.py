"""Storage provisioning planning (read-only; STANDARD S2): host(s) -> host set -> volumes ->
(optional VV set) -> export (VLUN).

build_plan() reads the array through `WsapiReader` and produces a preview (what will be created,
what already exists) for the operator to confirm. Executing the plan lives in `apply.py`.

Modelled on the verified design: ONE host definition per ESXi server carrying ALL its FC WWNs at
the VMware persona, grouped in the cluster host set, with volumes exported to the host SET so every
host in the cluster sees them down multiple paths (ALUA).
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass

from alletra_onboard.application.provisioning.clients import make_wsapi
from alletra_onboard.application.provisioning.hosts import (
    declared_mismatches,
    host_fabric_logins,
    union_hosts,
)
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.provisioning import (
    ArrayHostRecord,
    DiscoveredHostBrief,
    ExportRequest,
    PlannedAction,
    PlanState,
    ProvisioningIntent,
    ProvisioningPlan,
    VlunTemplate,
    VolumeRequest,
    host_name_problem,
    volume_name_problem,
    volume_set_name_problem,
    volume_too_large,
)
from alletra_onboard.domain.shared import ActionKind, ArrayVolumeRecord, normalize_wwpn

HostWwns = OrderedDict[str, list[str]]
VolumeSetMembers = OrderedDict[str, list[str]]


def _union(intent: ProvisioningIntent | None, discovery: DiscoveryReport, zoning_plan: dict | None):
    """SPEC-003 R4: the one host union plan, apply, verification and the dropdown all derive from."""
    return union_hosts(discovery, getattr(intent, "declared_hosts", None) or [], zoning_plan)


def hosts_by_name(
    discovery: DiscoveryReport, intent: ProvisioningIntent | None = None, zoning_plan: dict | None = None,
) -> HostWwns:
    """host name -> FC WWPNs, for every host the run can name (vCenter, sheet, array, fabric). An
    iSCSI-only host maps to an empty list: it is made from its iSCSI names (`_iqns_by_host`). A host
    with neither (an NVMe/TCP host, its NQN filed with the IQNs) is kept only when the array has it."""
    hosts, _ = _union(intent, discovery, zoning_plan)
    return OrderedDict(
        (n, list(h.wwpns)) for n, h in hosts.items() if h.wwpns or _iscsi(h.iqns) or (h.iqns and h.on_array)
    )


def _iscsi(names: list[str]) -> list[str]:
    """The iSCSI names among a host's `iqns`: discovery files NVMe NQNs there too (`showhost -d`)."""
    return [n for n in names if not n.lower().startswith("nqn.")]


def _iqns_by_host(
    discovery: DiscoveryReport, intent: ProvisioningIntent | None = None, zoning_plan: dict | None = None,
) -> dict[str, list[str]]:
    hosts, _ = _union(intent, discovery, zoning_plan)
    return {n: _iscsi(h.iqns) for n, h in hosts.items()}


def _host_notes(intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None,
                selected: HostWwns) -> list[str]:
    """SPEC-003 R3/R5/R6 notes: nameless initiators, iSCSI-only members, hosts with both transports."""
    hosts, notes = _union(intent, discovery, zoning_plan)
    iscsi_members = [n for n in selected if not selected[n] and hosts[n].iqns]
    if iscsi_members:
        notes.append(
            "iSCSI-only member(s) in a host set: " + ", ".join(iscsi_members)
            + ". iSCSI needs no SAN zoning; Verify paths reads their iSCSI paths per controller node."
        )
    # WSAPI refuses FC and iSCSI names in one request, and no lab array has a host with both.
    both = [n for n in selected if selected[n] and _iscsi(hosts[n].iqns) and not hosts[n].on_array]
    if both:
        notes.append(
            "FC and iSCSI both found for " + ", ".join(both) + " — the host is made with its FC WWPNs "
            "only; its iSCSI name is not added (this tool does not put both on one host)."
        )
    guessed = [n for n in selected if n in hosts and not hosts[n].os and not hosts[n].on_array
               and hosts[n].source != "vcenter"]
    if guessed:
        notes.append(
            "No OS known for " + ", ".join(guessed) + " — created with the VMware persona. Set the OS on "
            "the sheet's Hosts tab if any of them is not an ESXi host."
        )
    return notes


def _persona_by_host(
    discovery: DiscoveryReport, intent: ProvisioningIntent | None = None, zoning_plan: dict | None = None,
) -> dict[str, str]:
    """The host persona NAME for each host in the union (OS-derived, or the array's own)."""
    hosts, _ = _union(intent, discovery, zoning_plan)
    return {n: h.persona for n, h in hosts.items()}


def planned_host_names(
    intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None = None,
) -> tuple[ProvisioningIntent, list[str]]:
    """SPEC-014: the intent with host-set members and host exports that use a sheet name renamed to
    the name the host is planned under, plus notes for each rename and each member nothing names."""
    hosts, _ = _union(intent, discovery, zoning_plan)
    alias = {a: n for n, h in hosts.items() for a in h.aliases}
    notes: list[str] = []
    host_sets = []
    for hs in intent.host_sets:
        members: list[str] = []
        for m in hs.members:
            to = alias.get(m, m)
            if to != m:
                notes.append(f"Host set {hs.name}: sheet host '{m}' is the same server as '{to}' and is planned under that name.")
            elif m not in hosts:
                notes.append(f"Host set {hs.name}: member '{m}' is not a host this run can name — left out of the set.")
            if to not in members:
                members.append(to)
        host_sets.append(hs.model_copy(update={"members": members}))
    exports = [
        ex.model_copy(update={"target_name": alias[ex.target_name]})
        if ex.target_kind == "host" and ex.target_name in alias else ex
        for ex in intent.exports
    ]
    return intent.model_copy(update={"host_sets": host_sets, "exports": exports}), notes


def _members_for(host_set, all_hosts: HostWwns) -> list[str]:
    """A host set's members: the operator's selection, intersected with the hosts the run can name, so
    a member that is not known — or that the zoning gate excluded — cannot reach the array as a set
    member with no host object behind it. An EMPTY selection selects nothing (SPEC-005): until
    2026-09-13 it meant "every host", and with the SPEC-003 union that planned fifteen other teams'
    host objects into one set on a shared array."""
    return [m for m in host_set.members if m in all_hosts]


def _empty_host_sets(intent: ProvisioningIntent) -> list[str]:
    return [hs.name for hs in intent.host_sets if not hs.members]


def _empty_set_blocker(name: str) -> str:
    return (
        f"Host set {name} has no members — choose them in the Compose card (or fill Members on the "
        "Host sets tab). Blank no longer means every host."
    )


def _selected_hosts(
    intent: ProvisioningIntent, discovery: DiscoveryReport, zoning_plan: dict | None = None,
) -> HostWwns:
    """The hosts tier-1 will CREATE: only those the operator composed into a host set (ADR 0010's
    ideal subset) — never the whole inventory. On a shared vCenter, creating an array host object for
    every ESXi server in the inventory is pollution, not provisioning. No host sets, or host sets with
    no members, select no hosts (SPEC-005)."""
    all_hosts = hosts_by_name(discovery, intent, zoning_plan)
    wanted = {m for hs in intent.host_sets for m in _members_for(hs, all_hosts)}
    return OrderedDict((n, w) for n, w in all_hosts.items() if n in wanted)


def _vvsets(intent: ProvisioningIntent) -> VolumeSetMembers:
    """Group volume names by the VV-set each volume asked to join (order preserved)."""
    sets: VolumeSetMembers = OrderedDict()
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
    except DeviceError as exc:  # the palette still works without the existing objects
        return {"cpgs": [], "hosts": [], "host_sets": [], "volumes": [], "volume_sets": [], "error": str(exc)}


def host_briefs(
    discovery: DiscoveryReport, declared_hosts: list | None = None, zoning_plan: dict | None = None,
) -> list[DiscoveredHostBrief]:
    """Summarise each host in the union for the membership dropdown — the 'status text so a
    half-zoned host isn't picked blind' of ADR 0010, plus source and transport (SPEC-003 R5).
    FC-capable hosts first; iSCSI-only hosts last, saying they need no zone."""
    hosts, _ = union_hosts(discovery, declared_hosts or [], zoning_plan)
    logins = host_fabric_logins(discovery, zoning_plan)
    fc: list[DiscoveredHostBrief] = []
    iscsi: list[DiscoveredHostBrief] = []
    for name, h in hosts.items():
        if h.transport == "none":
            continue
        if not h.wwpns:
            status, wwpns, target = "iSCSI only · no zoning needed", [], iscsi
        else:
            n_fabrics = max((len(s) for s in logins.get(name, [])), default=0)
            one = next((next(iter(s)) for s in logins.get(name, []) if len(s) == 1), "")
            status = (
                f"{len(h.wwpns)} HBAs - both fabrics" if n_fabrics >= 2
                else f"{len(h.wwpns)} HBAs - one fabric ({one})" if n_fabrics == 1
                else f"{len(h.wwpns)} HBAs - not logged in (off or unzoned)"
            )
            wwpns, target = list(h.wwpns), fc
        target.append(DiscoveredHostBrief(
            name=name, status=status, wwpns=wwpns,
            source=h.source, transport=h.transport, persona=h.persona, fc_capable=bool(h.wwpns),
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
    all_hosts: HostWwns,
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
) -> OrderedDict[str, set[str]]:
    """{host: the volumes actually exported to it} — the tier-2 verification target.

    Resolves host-set exports down to their members and expands a VV-set source to its volumes, so
    the verifier asks "is THIS volume live on THIS host" instead of crossing every host with every
    volume in the intent. Every provisioned host appears, including those with an empty set: a host
    whose export is held back is a real state worth reporting, not an absence.
    """
    intent, _ = planned_host_names(intent, discovery, zoning_plan)
    hosts = _selected_hosts(intent, discovery, zoning_plan)
    out: OrderedDict[str, set[str]] = OrderedDict((name, set()) for name in hosts)
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


def _action(
    kind: ActionKind, name: str, description: str, verdict: tuple[PlanState, str], detail: dict,
) -> PlannedAction:
    st, reason = verdict
    return PlannedAction(
        kind=kind, name=name, description=description, state=st, reason=reason, exists=st != "create", detail=detail,
    )


def _unreachable_notes(hosts: HostWwns, reachable_hosts: set[str], union_map: OrderedDict) -> list[str]:
    unreachable = sorted(n for n in hosts if n not in reachable_hosts)
    if not unreachable:
        return []
    fc_wait = [n for n in unreachable if hosts[n] or not _iscsi(union_map[n].iqns)]
    iscsi_wait = [n for n in unreachable if n not in fc_wait]
    notes: list[str] = []
    if fc_wait:
        notes.append(
            "Not yet reachable (no login on both fabrics): " + ", ".join(fc_wait)
            + " — host objects are made or kept now; their exports wait until zoning is applied and "
            "re-checked."
        )
    if iscsi_wait:
        notes.append(
            "Not yet reachable over iSCSI (IQN not logged in on the array): " + ", ".join(iscsi_wait)
            + " — host objects are made or kept now; their exports wait until the server logs in to the "
            "array's iSCSI ports and the zoning check is run again."
        )
    return notes


def _plan_host_actions(
    hosts: HostWwns, union_map: OrderedDict, on_array: list[ArrayHostRecord],
) -> list[PlannedAction]:
    out: list[PlannedAction] = []
    for name, wwns in hosts.items():
        u = union_map.get(name)
        persona, src = (u.persona if u else "VMware"), (u.source if u else "")
        iqns: list[str] = []
        if wwns:
            desc = f"Host {name} — {len(wwns)} FC WWN(s), persona {persona}"
            verdict = _new_host_name(_judge_host(name, wwns, persona, on_array), name, src)
        elif iqns := (_iscsi(u.iqns) if u else []):
            desc = f"Host {name} — iSCSI {', '.join(iqns)}, persona {persona}"
            verdict = _new_host_name(_judge_iscsi_host(name, iqns, persona, on_array), name, src)
        else:
            # An array host with only an NVMe NQN: it joins sets as it is, never changed.
            desc = f"Host {name} — on the array, persona {persona}"
            verdict = ("exists", "exists on the array (NVMe initiator; not changed by this tool)")
        detail: dict = {"wwns": wwns, **({"iqns": iqns} if iqns else {}), "persona": persona, "source": src}
        out.append(_action("host", name, desc, verdict, detail))
    return out


def _plan_export_actions(
    intent: ProvisioningIntent, hosts: HostWwns, vvsets: VolumeSetMembers,
    vluns: list[VlunTemplate], reachable_hosts: set[str],
) -> tuple[list[PlannedAction], list[str], str | None]:
    # Presentation: the operator-composed exports (source volume|vvset x target host|hostset x LUN),
    # or the single-host-set default (each volume -> the set, auto LUN). Multiple host sets with no
    # composed exports REFUSE — see _resolve_exports.
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        return [], [], str(exc)
    notes: list[str] = []
    # SPEC-008 R5 (P-19): a sheet volume no export presents is a fact about the composition, said here
    # (S-1, 2026-09-14: zz_t2_vol03 was simply absent from an approved plan). Judged before the
    # reachability filter — a held-back export still presents its volume.
    presented = {
        n for ex in exports
        for n in ([ex.source_name] if ex.source_kind == "volume" else vvsets.get(ex.source_name, []))
    }
    if unpresented := [v.name for v in intent.volumes if v.name not in presented]:
        n = len(unpresented)
        notes.append(f"{n} volume{'s are' if n > 1 else ' is'} not presented by this plan: " + ", ".join(unpresented))
    exports, skipped = _reachable_targets(exports, intent, hosts, reachable_hosts)
    empty_sets = set(_empty_host_sets(intent))
    members_of = {hs.name: _members_for(hs, hosts) for hs in intent.host_sets}
    out: list[PlannedAction] = []
    for ex in exports:
        if ex.target_kind == "hostset" and ex.target_name in empty_sets:
            continue                                 # the set itself is the blocker; nothing to export to
        lun_txt = "auto LUN" if ex.lun is None else f"LUN {ex.lun}"
        out.append(_action(
            "vlun", ex.source_name,
            f"Export {ex.source_kind} {ex.source_name} → {ex.target_kind} {ex.target_name} ({lun_txt})",
            _judge_export(ex, vvsets, vluns, members_of.get(ex.target_name, [])),
            {"source": ex.source_ref, "target": ex.target_ref, "lun": ex.lun},
        ))
    if skipped:
        notes.append("Exports held back until the array can reach the target: " + "; ".join(skipped))
    return out, notes, None


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
    intent, name_notes = planned_host_names(intent, discovery, zoning_plan)
    hosts = _selected_hosts(intent, discovery, zoning_plan)
    empty_sets = _empty_host_sets(intent)
    if empty_sets:
        plan.blockers.extend(_empty_set_blocker(n) for n in empty_sets)
    elif not hosts:
        plan.notes.append("No host is selected for any host set — nothing to provision until members are chosen.")
    plan.blockers.extend(declared_mismatches(intent.declared_hosts, discovery))
    union_map, _ = _union(intent, discovery, zoning_plan)
    plan.notes.extend(_unreachable_notes(hosts, reachable_hosts, union_map))
    plan.notes.extend(_host_notes(intent, discovery, zoning_plan, hosts))
    plan.notes.extend(name_notes)

    try:
        with wsapi_factory(intent.array) as array:
            state = _ArrayState(
                list(array.hosts()), dict(array.host_sets()), list(array.volumes()),
                dict(array.volume_sets()), list(array.vlun_templates()), set(array.cpg_names()),
            )
    except DeviceError as exc:
        plan.error = f"Could not read the array over WSAPI: {exc}"
        return plan

    # HARD gate, not a note (sd00003946: volume create fails with NON_EXISTENT_CPG; SSD_r6 is
    # auto-created at array init, so a missing CPG means the sheet or the array is wrong — verify,
    # never auto-create).
    if missing_cpgs := sorted({v.cpg for v in intent.volumes} - state.cpgs):
        plan.error = (
            "CPG(s) not found on the array: " + ", ".join(missing_cpgs)
            + ". Volume creation is hard-gated on the CPG existing — fix the sheet's CPG name or "
            "have the CPG created on the array first."
        )
        return plan

    add = plan.actions.append
    plan.actions.extend(_plan_host_actions(hosts, union_map, state.hosts))
    for hs in intent.host_sets:
        members = _members_for(hs, hosts) if hs.members else []
        desc = f"Host set {hs.name} — {len(members)} host(s)" if hs.members else f"Host set {hs.name} — no members chosen"
        verdict = (
            _judge_set(hs.name, members, state.host_sets, "host") if hs.members
            else ("conflict", "no members — choose them in Compose or on the Host sets tab")
        )
        add(_action("hostset", hs.name, desc, verdict, {"members": members}))
    for v in intent.volumes:
        add(_action(
            "volume", v.name, f"Volume {v.name} — {v.size_gib} GiB, {v.provisioning_type}, CPG {v.cpg}",
            _judge_volume(v, state.volumes),
            {"size_mib": v.size_mib, "cpg": v.cpg, "type": v.provisioning_type, "vvset": v.vvset},
        ))
    vvsets = _vvsets(intent)
    for vvset, vols in vvsets.items():
        add(_action(
            "vvset", vvset, f"Volume set {vvset} — {len(vols)} volume(s)",
            _judge_volume_set(vvset, vols, state.volume_sets), {"members": vols},
        ))

    export_actions, export_notes, export_error = _plan_export_actions(
        intent, hosts, vvsets, state.vluns, reachable_hosts,
    )
    if export_error:
        plan.error = export_error
    else:
        plan.notes.extend(export_notes)
        plan.actions.extend(export_actions)
    plan.blockers.extend(f"{a.kind} {a.name}: {a.reason}" for a in plan.actions if a.state == "conflict")
    return plan


@dataclass
class _ArrayState:
    """What the array holds, read once per object type (SPEC-001 R9)."""

    hosts: list[ArrayHostRecord]
    host_sets: dict[str, list[str]]
    volumes: list[ArrayVolumeRecord]
    volume_sets: dict[str, list[str]]
    vluns: list[VlunTemplate]
    cpgs: set[str]


def _gib(mib: int) -> str:
    return f"{mib / 1024:g} GiB"


def _judge_host(name: str, wwns: list[str], persona: str, on_array: list[ArrayHostRecord]) -> tuple[PlanState, str]:
    """R3: exists (carries every WWN) / update (adds the missing ones) / conflict (a WWN is someone
    else's — apply would raise). A persona difference is reported, never acted on."""
    wanted = list({normalize_wwpn(w): w for w in wwns}.items())
    owners = {normalize_wwpn(w): h.name for h in on_array for w in h.wwns}
    others = sorted({f"{label} belongs to host {owners[k]}" for k, label in wanted if k in owners and owners[k] != name})
    if others:
        return "conflict", "; ".join(others) + " — resolve on the array before provisioning"
    mine = next((h for h in on_array if h.name == name), None)
    if mine is None:
        return "create", ""
    carried = {normalize_wwpn(w) for w in mine.wwns}
    missing = [label for k, label in wanted if k not in carried]
    persona_note = _persona_note(mine, persona)
    if missing:
        return "update", f"adds {len(missing)} WWN: {', '.join(missing)}" + persona_note
    return "exists", f"carries all {len(wwns)} WWN(s)" + persona_note


def _persona_note(mine: ArrayHostRecord, persona: str) -> str:
    if mine.persona and mine.persona != persona:
        return f" · persona on the array: {mine.persona}, intent {persona} — left unchanged"
    return ""


def _judge_iscsi_host(name: str, iqns: list[str], persona: str, on_array: list[ArrayHostRecord]) -> tuple[PlanState, str]:
    """R3 for an iSCSI-only host, by iSCSI name (case-insensitive): create / exists / update (adds the
    missing names) / conflict (a name is another host's, or the host of that name carries FC WWNs —
    `ensure_iscsi_host` refuses both)."""
    wanted = [(i.lower(), i) for i in iqns]
    owners = {i.lower(): h.name for h in on_array for i in h.iqns}
    others = sorted({f"{label} belongs to host {owners[k]}" for k, label in wanted if owners.get(k, name) != name})
    if others:
        return "conflict", "; ".join(others) + " — resolve on the array before provisioning"
    mine = next((h for h in on_array if h.name == name), None)
    if mine is None:
        return "create", ""
    if mine.wwns:
        return "conflict", (f"exists on the array with {len(mine.wwns)} FC WWN(s); this tool does not add an "
                            "iSCSI name to an FC host — use another host name, or add the IQN on the array")
    carried = {i.lower() for i in mine.iqns}
    missing = [label for k, label in wanted if k not in carried]
    persona_note = _persona_note(mine, persona)
    if missing:
        return "update", f"adds {len(missing)} iSCSI name: {', '.join(missing)}" + persona_note
    return "exists", f"carries its iSCSI name{'s' if len(iqns) > 1 else ''} ({', '.join(iqns)})" + persona_note


def _judge_set(name: str, members: list[str], on_array: dict[str, list[str]], noun: str) -> tuple[PlanState, str]:
    """R4: additive only — exists (every member present) or update (adds the missing ones)."""
    if name not in on_array:
        return "create", ""
    missing = [m for m in members if m not in set(on_array[name])]
    if missing:
        return "update", f"adds {len(missing)} {noun}(s): {', '.join(missing)}"
    return "exists", f"has all {len(members)} {noun}(s)"


def _new_host_name(verdict: tuple[PlanState, str], name: str, source: str) -> tuple[PlanState, str]:
    """A host the plan would create under a name the array refuses is a conflict. Only the sheet's name
    can be changed by the operator; a name vCenter, the array or the fabric gave cannot."""
    state, _ = verdict
    if state == "create" and (bad := host_name_problem(name)):
        fix = ("Give it a shorter name on the sheet's Hosts tab." if source == "sheet"
               else "Leave it out of the host set: the tool cannot create it under this name.")
        return "conflict", f"{bad}. {fix}"
    return verdict


def _judge_volume_set(name: str, volumes: list[str], on_array: dict[str, list[str]]) -> tuple[PlanState, str]:
    """A new volume set with a name the array refuses is a conflict; otherwise as `_judge_set`."""
    if name not in on_array and (bad := volume_set_name_problem(name)):
        return "conflict", f"{bad}. Rename it on the sheet's Volumes tab."
    return _judge_set(name, volumes, on_array, "volume")


def _judge_volume(v: VolumeRequest, on_array: list[ArrayVolumeRecord]) -> tuple[PlanState, str]:
    """R2: a name match is not a match. Size, CPG and provisioning type must all agree, or the row is
    a conflict apply cannot fix (the array has no 'resize to intent' that is safe to do unasked).
    A new volume larger than the array can create, or with a name it refuses, is a conflict too."""
    found = next((r for r in on_array if r.name == v.name), None)
    if found is None:
        if bad_name := volume_name_problem(v.name):
            return "conflict", f"{bad_name}. Rename it on the sheet's Volumes tab."
        if too_large := volume_too_large(v.size_gib):
            return "conflict", f"{too_large}. Make it smaller on the sheet's Volumes tab."
        return "create", ""
    on = f"{_gib(found.size_mib)} {found.provisioning_type} on {found.cpg}"
    want = f"{v.size_gib} GiB {v.provisioning_type} on {v.cpg}"
    if found.size_mib == v.size_mib and found.cpg == v.cpg and found.provisioning_type == v.provisioning_type:
        return "exists", f"{on} — matches"
    return "conflict", f"on the array: {on} · intent: {want}"


def _judge_export(
    ex: ExportRequest, vvsets: VolumeSetMembers, templates: list[VlunTemplate],
    set_members: list[str] | None = None,
) -> tuple[PlanState, str]:
    """R5: judged against the array's VLUN templates, one per member volume for a set export.
    SPEC-005 R4: a set export of a volume a MEMBER host already has directly is a conflict — the same
    volume would reach that host twice."""
    volumes = list(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else [ex.source_name]
    if ex.target_kind == "hostset":
        direct = sorted(
            f"{t.volume} is already presented directly to member {t.target} at LUN {t.lun}"
            for t in templates if t.volume in volumes and t.target in (set_members or [])
        )
        if direct:
            return "conflict", "; ".join(direct) + " — a set export would present it a second time; remove one or the other"
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
    luns = _luns_text(volumes, to_target, ex.target_ref)
    if len(present) < len(volumes):
        return "update", f"{len(present)} of {len(volumes)} member volumes already exported ({luns}); apply completes the set"
    return "exists", f"already exported at {luns}"


def _luns_text(volumes: list[str], templates: list[VlunTemplate], target_ref: str) -> str:
    """"LUN 0, LUN 1" — or "LUN 0/3" when a volume sits at more than one LUN on that target: the
    duplicate the P-21 apply produced must be visible, not collapsed to whichever LUN came last."""
    by_vol: dict[str, list[int]] = {}
    for t in templates:
        if t.target == target_ref and t.volume in volumes:
            by_vol.setdefault(t.volume, []).append(t.lun)
    return ", ".join("LUN " + "/".join(str(n) for n in sorted(by_vol[v])) for v in volumes if v in by_vol)
