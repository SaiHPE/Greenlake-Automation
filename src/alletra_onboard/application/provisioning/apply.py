"""Storage provisioning apply (STANDARD S2): writes hosts, host sets, volumes, volume sets and
exports over the WSAPI writer factory and builds the removal set (SPEC-007)."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from alletra_onboard.application.provisioning.storage_provision import (
    ExportDefaultError,
    _empty_host_sets,
    _empty_set_blocker,
    _iqns_by_host,
    _judge_export,
    _luns_text,
    _members_for,
    _persona_by_host,
    _reachable_targets,
    _resolve_exports,
    _selected_hosts,
    _vvsets,
    planned_host_names,
)
from alletra_onboard.application.runs.apply_record import recorded_write
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.domain.approval import Approval, SaveRecord
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.errors import ApplyRecordError, DeviceError
from alletra_onboard.domain.provisioning import (
    ActionOutcome,
    ArrayHostRecord,
    ExportRequest,
    ProvisioningIntent,
    ProvisioningPlan,
    ProvisioningResult,
    RemovalItem,
    VlunTemplate,
)
from alletra_onboard.domain.shared import REMOVAL_ORDER, ArrayVolumeRecord

# How each object is named on screen, read on the array and removed (`-f` where the CLI prompts).
_LABEL = {"host": "host", "hostset": "host set", "volume": "volume", "vvset": "volume set", "vlun": "export of"}
_SHOW = {"host": "showhost {n}", "hostset": "showhostset {n}", "volume": "showvv {n}", "vvset": "showvvset {n}"}
_REMOVE = {"host": "removehost {n}", "hostset": "removehostset -f {n}", "volume": "removevv -f {n}", "vvset": "removevvset -f {n}"}


class _PlanDriftError(RuntimeError):
    """An object the reviewed plan marked 'exists' vanished from the array before apply."""


@dataclass(frozen=True, slots=True)
class StorageInputs:
    """Inputs for provisioning apply; `plan` is the reviewed preview whose 'exists' rows must not
    silently turn into creates if they vanish before apply."""

    intent: ProvisioningIntent
    discovery: DiscoveryReport
    reachable_hosts: set[str]
    plan: ProvisioningPlan
    zoning_plan: dict | None = None


@dataclass
class _ApplyState:
    save: SaveRecord
    result: ProvisioningResult = field(default_factory=ProvisioningResult)
    outcomes: list[ActionOutcome] = field(default_factory=list)
    export_outcomes: list[ActionOutcome] = field(default_factory=list)
    export_notes: list[str] = field(default_factory=list)
    doing: tuple[str, str] = ("", "")
    templates: list[VlunTemplate] | None = None
    export_scope: set[tuple[str, str]] = field(default_factory=set)
    reviewed_exports: set[tuple[str, str]] = field(default_factory=set)


def _sync_result(state: _ApplyState, after: list[VlunTemplate] | None = None) -> None:
    """Keep `state.result` current in paste order so each checkpoint holds every confirmed removal."""
    state.result.outcomes = state.outcomes + state.export_outcomes
    before = state.templates or []
    removals, touched = removal_set(state.result.outcomes, before, before if after is None else after,
                                    scope=state.export_scope)
    state.result.removals = removals
    extra = [n for n in state.result.removal_notes if not n.startswith("Not reverted — ")]
    state.result.removal_notes[:] = touched + extra


def _reviewed_exists(plan: ProvisioningPlan) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    objects = {(a.kind, a.name) for a in plan.actions if a.kind != "vlun" and a.state == "exists"}
    exports = {
        (str(a.detail["source"]), str(a.detail["target"]))
        for a in plan.actions if a.kind == "vlun" and a.state == "exists"
    }
    return objects, exports


def _check_reviewed_objects(array, reviewed: set[tuple[str, str]]) -> None:
    """Refuse before any write if any host, host set, volume or volume set the reviewed plan marked
    'exists' is no longer on the array."""
    checks: tuple[tuple[str, Callable[[], set[str]]], ...] = (
        ("host", lambda: {h.name for h in array.hosts()}),
        ("hostset", lambda: set(array.host_sets())),
        ("volume", lambda: {v.name for v in array.volumes()}),
        ("vvset", lambda: set(array.volume_sets())),
    )
    for kind, read_names in checks:
        wanted = sorted(name for k, name in reviewed if k == kind)
        if not wanted:
            continue
        present = read_names()
        for name in wanted:
            if name not in present:
                raise _PlanDriftError(
                    f"{_LABEL[kind]} {name} existed when the plan was reviewed but is no longer on the array — "
                    "refusing to create an object the plan marked exists. Rebuild the plan."
                )


def _apply_hosts(
    array,
    inputs: StorageInputs,
    hosts: OrderedDict[str, list[str]],
    state: _ApplyState,
) -> None:
    personas = _persona_by_host(inputs.discovery, inputs.intent, inputs.zoning_plan)
    iqns_of = _iqns_by_host(inputs.discovery, inputs.intent, inputs.zoning_plan)
    for host_name, wwns in hosts.items():
        state.doing = ("host", host_name)
        persona = personas.get(host_name, "VMware")
        with recorded_write(state.result, _maybe_made_note("host", host_name), state.save):
            if wwns or not iqns_of.get(host_name):
                # FC, or an array host with only an NVMe NQN (ensure_host with no WWN = exists, no write)
                status = array.ensure_host(host_name, wwns, persona=persona)
            else:
                status = array.ensure_iscsi_host(host_name, iqns_of[host_name], persona=persona)
            state.outcomes.append(ActionOutcome(kind="host", name=host_name, status=status))
            _sync_result(state)


def _apply_core_objects(
    array,
    inputs: StorageInputs,
    hosts: OrderedDict[str, list[str]],
    state: _ApplyState,
) -> None:
    _apply_hosts(array, inputs, hosts, state)
    intent = inputs.intent

    for hs in intent.host_sets:
        state.doing = ("hostset", hs.name)
        with recorded_write(state.result, _maybe_made_note("hostset", hs.name), state.save):
            status = array.ensure_host_set(hs.name, _members_for(hs, hosts))
            state.outcomes.append(ActionOutcome(kind="hostset", name=hs.name, status=status))
            _sync_result(state)

    for v in intent.volumes:
        state.doing = ("volume", v.name)
        with recorded_write(state.result, _maybe_made_note("volume", v.name), state.save):
            status = array.ensure_volume(v.name, v.cpg, v.size_mib, v.provisioning_type)
            state.outcomes.append(ActionOutcome(kind="volume", name=v.name, status=status))
            _sync_result(state)

    for vvset, vols in _vvsets(intent).items():
        state.doing = ("vvset", vvset)
        with recorded_write(state.result, _maybe_made_note("vvset", vvset), state.save):
            status = array.ensure_volume_set(vvset, vols)
            state.outcomes.append(ActionOutcome(kind="vvset", name=vvset, status=status))
            _sync_result(state)

    # SPEC-012 R1 (P-8): the Result row names the object the array holds, not only the verb.
    # One read-back of hosts and volumes; sets are described from what was sent.
    state.doing = ("", "")
    _describe_outcomes(state.outcomes, array.hosts(), array.volumes(),
                       {hs.name: _members_for(hs, hosts) for hs in intent.host_sets}, _vvsets(intent))


def _complete_set_export(
    array, ex: ExportRequest, volumes: list[str], before: list[VlunTemplate], scope: set[tuple[str, str]],
) -> Literal["created", "exists"]:
    present = {t.volume for t in before if t.target == ex.target_ref and t.volume in volumes}
    missing = [v for v in volumes if v not in present]
    scope.update((v, ex.target_ref) for v in missing)
    statuses = [
        array.ensure_vlun(v, ex.target_ref, lun=None if ex.lun is None else ex.lun + volumes.index(v))
        for v in missing
    ]
    return "created" if "created" in statuses else "exists"


def _execute_export(
    array,
    ex: ExportRequest,
    vvsets: OrderedDict[str, list[str]],
    members_of: dict[str, list[str]],
    state: _ApplyState,
) -> None:
    before = state.templates or []
    verdict, reason = _judge_export(ex, vvsets, before, members_of.get(ex.target_name, []))
    if (ex.source_ref, ex.target_ref) in state.reviewed_exports and verdict != "exists":
        raise _PlanDriftError(
            f"export of {ex.source_name} to {ex.target_name} existed when the plan was reviewed "
            "but is no longer present on the array — refusing to create an export the plan marked "
            "exists. Rebuild the plan."
        )
    if verdict == "exists":
        state.export_outcomes.append(ActionOutcome(kind="vlun", name=ex.source_name, status="exists", detail=reason))
        return
    if verdict == "conflict":
        state.export_outcomes.append(ActionOutcome(kind="vlun", name=ex.source_name, status="failed", detail=reason))
        return
    volumes = list(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else [ex.source_name]
    note = _maybe_made_note("vlun", f"{ex.source_name} to {ex.target_name}")
    state.result.removal_notes.append(note)
    state.export_notes.append(note)
    state.save(state.result)
    if verdict == "update":
        status = _complete_set_export(array, ex, volumes, before, state.export_scope)
    else:
        # createVLUN on a volume set presents every member currently in that set on the array
        # (including pre-existing members not in this intent), so scope covers the live set too.
        scope_vols = (
            set(volumes) | set(array.volume_sets().get(ex.source_name, ()))
            if ex.source_kind == "vvset" else set(volumes)
        )
        state.export_scope.update((v, ex.target_ref) for v in scope_vols)
        status = array.ensure_vlun(ex.source_ref, ex.target_ref, lun=ex.lun)
    state.export_outcomes.append(ActionOutcome(kind="vlun", name=ex.source_name, status=status))
    state.save(state.result)


def _apply_exports(
    array,
    intent: ProvisioningIntent,
    hosts: OrderedDict[str, list[str]],
    exports: list[ExportRequest],
    state: _ApplyState,
) -> list[VlunTemplate]:
    # SPEC-001 R11 (P-21, live 2026-09-14 12:39): judge every export against the templates BEFORE
    # sending it, exactly as the plan did. `createVLUN(auto=True)` never raises EXISTENT_VLUN —
    # the array just picks the next LUN — so the conflict-swallow that makes the other ensure_*
    # idempotent never fired here, and an export the approved plan called Exists (LUN 0, 1) was
    # presented a second time at LUN 3, 4. One read; skip what exists, refuse what conflicts,
    # complete a partial set member by member (never re-sending the whole set).
    vvsets = _vvsets(intent)
    members_of = {hs.name: _members_for(hs, hosts) for hs in intent.host_sets}
    before: list[VlunTemplate] = array.vlun_templates()
    state.templates = before
    for ex in exports:
        state.doing = ("vlun", f"{ex.source_name} to {ex.target_name}")
        _execute_export(array, ex, vvsets, members_of, state)
    # R8: "created" is the array's word; read the templates back ONCE and hold it to it.
    state.doing = ("", "")
    after: list[VlunTemplate] = array.vlun_templates() if exports else before
    if exports:
        _confirm_exports(exports, state.export_outcomes, vvsets, after)
        for note in state.export_notes:
            if note in state.result.removal_notes:
                state.result.removal_notes.remove(note)
        state.export_notes.clear()
        _sync_result(state, after=after)
        state.save(state.result)
    return after


def apply_plan(
    inputs: StorageInputs,
    approval: Approval,
    *,
    wsapi_factory: Callable = make_wsapi_writer,
) -> ProvisioningResult:
    """Create the objects. `reachable_hosts` and `zoning_plan` must be the SAME inputs `build_plan`
    was given: apply re-derives everything from the intent rather than replaying the plan, so
    without them here the held-back exports would be cosmetic and the host list would differ."""
    result = ProvisioningResult()
    intent, _ = planned_host_names(inputs.intent, inputs.discovery, inputs.zoning_plan)
    resolved = StorageInputs(intent, inputs.discovery, inputs.reachable_hosts, inputs.plan, inputs.zoning_plan)
    empty_sets = _empty_host_sets(intent)
    if empty_sets:
        result.error = "; ".join(_empty_set_blocker(n) for n in empty_sets)
        return result
    hosts = _selected_hosts(intent, inputs.discovery, inputs.zoning_plan)
    if not hosts:
        result.error = "No host is selected for any host set — refusing to provision with no hosts."
        return result
    try:
        exports = _resolve_exports(intent)
    except ExportDefaultError as exc:
        result.error = str(exc)
        return result
    exports, _held = _reachable_targets(exports, intent, hosts, inputs.reachable_hosts)

    reviewed_objects, reviewed_exports = _reviewed_exists(inputs.plan)
    state = _ApplyState(save=approval.require_saver(), result=result, reviewed_exports=reviewed_exports)
    failure_notes: list[str] = []
    # SPEC-007 R6: a failed apply has a removal set too. Writes stop at the first error, inside the
    # array session, so the undo can still be read for what was made before it.
    try:
        with wsapi_factory(approval, "storage", "A") as array:
            try:
                _check_reviewed_objects(array, reviewed_objects)
                _apply_core_objects(array, resolved, hosts, state)
                after = _apply_exports(array, intent, hosts, exports, state)
            except (DeviceError, ApplyRecordError, _PlanDriftError) as exc:  # stop at the first failure; the undo still covers what was made
                kind, name = state.doing
                result.error = f"Stopped while creating {_LABEL[kind]} {name}: {exc}" if kind else str(exc)
                if kind in _REMOVE:
                    # The array may have made it before the answer was lost (a timeout, a 5xx). It is not
                    # put in the set: it may have been there before this run, and nothing here can tell.
                    failure_notes.append(_maybe_made_note(kind, name))
                after = list(state.templates or [])
                if state.templates is not None:
                    # Stopped among the exports: what the array presents now is the only record of
                    # which LUNs this apply made, the failed call's included.
                    try:
                        after = array.vlun_templates()
                    except DeviceError:
                        failure_notes.append("The exports could not be read back after the failure. Check `showvlun -t` "
                                             "on the array for exports this apply made; they are not in this removal set.")
            result.outcomes = state.outcomes + state.export_outcomes
            # SPEC-007: the undo for exactly what this apply created, from the same reads.
            result.removals, notes = removal_set(result.outcomes, state.templates or [], after, scope=state.export_scope)
            result.removal_notes = notes + failure_notes
    except DeviceError as exc:  # no session (nothing was written), or it failed to close
        result.error = result.error or str(exc)
    return result


def _maybe_made_note(kind: str, name: str) -> str:
    """SPEC-007 R6: the object whose write failed, for the operator to check by hand."""
    if kind == "vlun":
        return (f"The array may have made {_LABEL[kind]} {name} before the error. "
                "Check `showvlun -t` on the array; if it was not there before this run, remove it with `removevlun -f`.")
    return (f"The array may have made {_LABEL[kind]} {name} before the error. If `{_SHOW[kind].format(n=name)}` lists it "
            f"and it was not there before this run, `{_REMOVE[kind].format(n=name)}` removes it.")


def _describe_outcomes(
    outcomes: list[ActionOutcome], hosts: list[ArrayHostRecord], volumes: list[ArrayVolumeRecord],
    set_members: dict[str, list[str]], vvsets: dict[str, list[str]],
) -> None:
    """SPEC-012 R1: fill each object outcome's `detail` with the array's own identifiers from ONE
    read-back (host id / persona / WWN count; volume id / WWN / size / type / CPG) and, for sets, the
    members this run sent. Rows the read-back does not hold keep whatever detail they had."""
    host_by = {h.name: h for h in hosts}
    vol_by = {v.name: v for v in volumes}

    def plural(n: int, word: str) -> str:
        return f"{n} {word}{'' if n == 1 else 's'}"

    for o in outcomes:
        if o.detail:
            continue
        if o.kind == "host" and o.name in host_by:
            h = host_by[o.name]
            initiators = plural(len(h.wwns), "WWN") if h.wwns or not h.iqns else plural(len(h.iqns), "iSCSI name")
            parts = [f"id {h.id}" if h.id is not None else "", f"persona {h.persona}" if h.persona else "", initiators]
            o.detail = " · ".join(p for p in parts if p)
        elif o.kind == "volume" and o.name in vol_by:
            v = vol_by[o.name]
            parts = [f"id {v.id}" if v.id is not None else "", f"WWN {v.wwn}" if v.wwn else "",
                     f"{v.size_mib} MiB {v.provisioning_type} on {v.cpg}".strip()]
            o.detail = " · ".join(p for p in parts if p)
        elif o.kind == "hostset" and o.name in set_members:
            members = set_members[o.name]
            o.detail = f"{plural(len(members), 'member')}: {', '.join(members)}" if members else "no members"
        elif o.kind == "vvset" and o.name in vvsets:
            vols = vvsets[o.name]
            o.detail = f"{plural(len(vols), 'volume')}: {', '.join(vols)}" if vols else "no volumes"


def removal_set(
    outcomes: list[ActionOutcome],
    before: list[VlunTemplate],
    after: list[VlunTemplate],
    *,
    scope: set[tuple[str, str]] | None = None,
) -> tuple[list[RemovalItem], list[str]]:
    """SPEC-007 R1/R2: undo lines for what THIS apply created — objects by `created` status, exports
    by the template diff (after − before) filtered to this apply's `(volume, target)` scope so a
    concurrent foreign export never enters this run's removal set. `updated` objects are not
    reverted (their members or WWNs were someone's before this run) and are named in a note."""
    items: list[RemovalItem] = []
    seen = {(t.volume, t.target, t.lun) for t in before}
    for t in after:
        if (t.volume, t.target, t.lun) not in seen and (scope is None or (t.volume, t.target) in scope):
            items.append(RemovalItem(kind="vlun", name=f"{t.volume} LUN {t.lun} → {t.target}",
                                     command=f"removevlun -f {t.volume} {t.lun} {t.target}"))
    for o in outcomes:
        if o.status == "created" and o.kind in _REMOVE:
            items.append(RemovalItem(kind=o.kind, name=o.name, command=_REMOVE[o.kind].format(n=o.name)))
    touched = [f"{o.kind} {o.name}" for o in outcomes if o.status == "updated"]
    notes = ["Not reverted — members, WWNs or iSCSI names were added to: " + ", ".join(touched) + ". They existed before this run."] if touched else []
    # S-12 (2026-09-14): the runner pasted the raw list and removed hosts before their set. The LIST
    # is in paste order, not only the rendering.
    items.sort(key=lambda i: REMOVAL_ORDER.get(i.kind, 9))
    return items, notes


def render_removal_commands(items: list[RemovalItem]) -> list[str]:
    """R3: dependency order, one command per object, de-duplicated — usable across several applies."""
    out: list[str] = []
    for item in sorted(items, key=lambda i: REMOVAL_ORDER.get(i.kind, 9)):
        if item.command not in out:
            out.append(item.command)
    return out


def _confirm_exports(
    exports: list[ExportRequest],
    outcomes: list[ActionOutcome],
    vvsets: OrderedDict[str, list[str]],
    templates: list[VlunTemplate],
) -> None:
    """Annotate each export outcome with the LUN(s) the array actually recorded. A `created` export
    with no template on read-back becomes `failed` — the silent-dead-export case R8 exists for."""
    for ex, out in zip(exports, outcomes):
        if out.status == "failed":
            continue                                     # refused before it was sent; keep the reason
        volumes = list(vvsets.get(ex.source_name, [])) if ex.source_kind == "vvset" else [ex.source_name]
        luns = _luns_text(volumes, templates, ex.target_ref)
        if luns:
            out.detail = f"{luns} → {ex.target_ref}"
        elif out.status == "created":
            out.status = "failed"
            out.detail = f"the array reported created but no export {ex.source_ref} → {ex.target_ref} was found on read-back"
