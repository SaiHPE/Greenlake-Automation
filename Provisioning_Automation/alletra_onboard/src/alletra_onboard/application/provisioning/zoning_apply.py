"""Opt-in Brocade Fabric OS SAN zoning apply (ADR 0033, following ADR 0025).

Copy-paste remains the default deliverable (`render_commands`). When the operator reviews the
rendered command set, ticks approval and opts in, this module:
1. builds a per-fabric `ZoningApplyPlan` covering host-to-array and peer-port zones (refusing
   alias/zone collisions across host and peer blocks, validating every generated command against
   the exact write-form grammar at build time, dropping `cfgtransshow` and `cfgsave`, using
   prompt-free `cfgenable "<cfg>" -f`, and computing the exact reverse-order removal set),
2. verifies `switch_host` and `active_cfg` against the run's intent and stored `zoning.plan`,
3. saves the undo record to `apply_in_progress` BEFORE sending any write (STANDARD S5),
4. checks `cfgtransshow` (refusing any open transaction) and strict `cfgshow` (refusing missing
   Effective cfg, cfg drift, or existing alias/zone names) before sending any write,
5. sends `alicreate` -> `zonecreate` -> `cfgadd` -> `cfgenable "<cfg>" -f` through
   `make_brocade_writer` (ADR 0025), running confirmed `cfgtransabort` on any mid-apply failure
   before `cfgenable`, and reading back switch state if `cfgenable` fails or times out, and
6. re-reads strict `cfgshow` after `cfgenable` to verify every planned zone is in the Effective
   configuration with the exact planned member WWPNs.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any

from alletra_onboard.application.provisioning.brocade_writer_factory import make_brocade_writer
from alletra_onboard.application.provisioning.zoning import CfgShowParsed, parse_cfgshow_strict
from alletra_onboard.application.provisioning.zoning_apply_plan import (
    LABEL_TO_FABRIC,
    build_apply_plan,
    fabric_label,
    plan_objects_for,
)
from alletra_onboard.application.provisioning.zoning_plan import parse_defined_names
from alletra_onboard.application.runs.apply_record import try_save_record
from alletra_onboard.application.runs.coordinator import (
    RunCoordinator,
    StepPreconditionError,
    check_approval,
)
from alletra_onboard.domain import events
from alletra_onboard.domain.approval import Approval, ApprovalError, SaveRecord
from alletra_onboard.domain.errors import ApplyRecordError, DeviceError
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds, Fabric, normalize_wwpn
from alletra_onboard.domain.zoning import (
    FabricZoningApplyPlan,
    FabricZoningApplyResult,
    ZoningApplyPlan,
    ZoningApplyResult,
    ZoningCommandOutcome,
)

__all__ = [
    "apply_zoning_plan",
    "build_apply_plan",
    "fabric_label",
    "resolve_switch_creds",
    "run_zoning_apply",
    "start_approved_apply",
    "verify_plan_for_run",
]

_WWPN_COLON_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$")


@dataclass
class _ApplyContext:
    approval: Approval
    result: ZoningApplyResult
    save: SaveRecord
    progress: Callable[[str], None] | None
    writer_factory: Callable[[Approval, Fabric, ZoningPlanObjects], Any]

    def report(self, message: str) -> None:
        if self.progress is not None:
            self.progress(message)


def _preflight_check(writer: Any, fab: FabricZoningApplyPlan) -> str | None:
    trans = writer.cfgtransshow()
    if "no outstanding" not in trans.lower():
        return (
            f"Another zoning transaction is already open on {fab.switch_host}. "
            "Finish or abort it on the switch first; nothing was changed."
        )
    cfg_text = writer.cfgshow()
    parsed = parse_cfgshow_strict(cfg_text)
    defined_names = parse_defined_names(cfg_text)
    if not parsed.effective_cfg:
        return (
            f"No effective zoning configuration is active on {fab.switch_host}. "
            "Activate a baseline configuration on the switch first; nothing was changed."
        )
    if parsed.effective_cfg != fab.active_cfg:
        return (
            f"Active configuration on {fab.switch_host} is now '{parsed.effective_cfg}', "
            f"not '{fab.active_cfg}'. Rebuild the zoning plan first; nothing was changed."
        )
    existing_aliases = [name for name in fab.aliases if name in defined_names or name in parsed.aliases]
    existing_zones = [
        name for name in fab.zones
        if name in defined_names or name in parsed.defined_zones or name in parsed.effective_zones
    ]
    if existing_aliases or existing_zones:
        clashes = [
            *(f"alias '{name}'" for name in existing_aliases),
            *(f"zone '{name}'" for name in existing_zones),
        ]
        return (
            f"Already exists on {fab.switch_host}: {', '.join(clashes)}. "
            "Rebuild the zoning plan first; nothing was changed."
        )
    return None


def _try_abort(writer: Any, fab_result: FabricZoningApplyResult) -> bool:
    """Attempt `cfgtransabort` and confirm via `cfgtransshow` that no transaction remains open."""
    try:
        out = writer.write("cfgtransabort")
        trans = writer.cfgtransshow()
    except (DeviceError, ApprovalError, ValueError) as exc:
        fab_result.transaction_aborted = False
        fab_result.outcomes.append(ZoningCommandOutcome(command="cfgtransabort", status="failed", detail=str(exc)))
        return False
    confirmed = "no outstanding" in trans.lower()
    fab_result.transaction_aborted = confirmed
    detail = next((ln.strip() for ln in out.splitlines() if ln.strip()), "")
    if confirmed:
        fab_result.outcomes.append(ZoningCommandOutcome(
            command="cfgtransabort", status="aborted",
            detail=detail or "Uncommitted transaction aborted and confirmed clean.",
        ))
        return True
    fab_result.outcomes.append(ZoningCommandOutcome(
        command="cfgtransabort", status="failed",
        detail=f"cfgtransshow still reported an open transaction: {trans.strip()}",
    ))
    return False


def _member_wwpns(member: str, fab: FabricZoningApplyPlan, parsed: CfgShowParsed) -> set[str]:
    if member in fab.aliases:
        return {normalize_wwpn(fab.aliases[member])}
    if member in parsed.aliases:
        return set(parsed.aliases[member])
    if _WWPN_COLON_RE.match(member):
        return {normalize_wwpn(member)}
    return set()


def _check_effective_zones(
    parsed: CfgShowParsed, fab: FabricZoningApplyPlan,
) -> tuple[list[str], list[str], list[str]]:
    verified: list[str] = []
    missing: list[str] = []
    mismatches: list[str] = []
    for zone, (m1, m2) in fab.zones.items():
        if zone not in parsed.effective_zones:
            missing.append(zone)
            continue
        expected = _member_wwpns(m1, fab, parsed) | _member_wwpns(m2, fab, parsed)
        actual = parsed.effective_zones[zone]
        if not expected or actual != expected:
            missing.append(zone)
            mismatches.append(f"{zone} (expected {sorted(expected)}, found {sorted(actual)})")
        else:
            verified.append(zone)
    return verified, missing, mismatches


def _verify_effective(writer: Any, fab: FabricZoningApplyPlan, fab_result: FabricZoningApplyResult) -> None:
    parsed = parse_cfgshow_strict(writer.cfgshow())
    verified, missing, mismatches = _check_effective_zones(parsed, fab)
    fab_result.verified_zones = verified
    fab_result.missing_zones = missing
    if parsed.effective_cfg != fab.active_cfg:
        fab_result.status = "failed"
        fab_result.error = (
            f"Read-back on {fab.switch_host} showed effective cfg '{parsed.effective_cfg or 'none'}' "
            f"instead of '{fab.active_cfg}'."
        )
    elif mismatches:
        fab_result.status = "failed"
        fab_result.error = (
            f"Read-back on {fab.switch_host} found mismatched effective zone members: "
            f"{'; '.join(mismatches)}."
        )
    elif missing:
        fab_result.status = "failed"
        fab_result.error = (
            f"Read-back on {fab.switch_host} did not find activated zone(s) in effective config: "
            f"{', '.join(missing)}."
        )
    else:
        fab_result.status = "applied"


def _inspect_after_cfgenable_error(
    writer: Any, fab: FabricZoningApplyPlan, fab_result: FabricZoningApplyResult,
) -> None:
    notes: list[str] = []
    try:
        trans = writer.cfgtransshow()
        if "no outstanding" not in trans.lower():
            if _try_abort(writer, fab_result):
                notes.append("Open transaction was aborted and confirmed clean via cfgtransshow.")
            else:
                notes.append("A zoning transaction may still be open on the switch.")
        parsed = parse_cfgshow_strict(writer.cfgshow())
        verified, missing, _mismatches = _check_effective_zones(parsed, fab)
        fab_result.verified_zones = verified
        fab_result.missing_zones = missing
        if verified:
            notes.append(f"Effective config already shows: {', '.join(verified)}.")
        else:
            notes.append("None of the planned zones appeared in effective config.")
    except DeviceError as exc:
        notes.append(f"Post-error read-back failed ({exc}).")
    notes.append("Inspect the switch with cfgtransshow and cfgshow before running any removal commands.")
    fab_result.error = f"{fab_result.error} {' '.join(notes)}"


def _handle_pre_enable_error(
    writer: Any, fab_result: FabricZoningApplyResult,
) -> None:
    """After any non-`cfgenable` write error (including the first write), check and abort any open transaction."""
    try:
        trans = writer.cfgtransshow()
    except DeviceError as exc:
        fab_result.error = (
            f"{fab_result.error} Could not check cfgtransshow after error ({exc}); "
            "inspect the switch with cfgtransshow and cfgshow first."
        )
        return
    if "no outstanding" in trans.lower():
        fab_result.removals = []
        return
    if _try_abort(writer, fab_result):
        fab_result.removals = []
        fab_result.error = (
            f"{fab_result.error} Uncommitted transaction was aborted and confirmed clean; "
            "nothing persisted on the switch."
        )
    else:
        fab_result.error = (
            f"{fab_result.error} Could not confirm transaction abort; "
            "inspect with cfgtransshow and cfgshow first."
        )


def _send_commands(
    writer: Any, fab: FabricZoningApplyPlan, fab_result: FabricZoningApplyResult,
) -> bool:
    write_attempted = False
    for cmd in fab.commands:
        is_enable = cmd.startswith("cfgenable ")
        write_attempted = True
        try:
            out = writer.write(cmd)
        except (DeviceError, ApprovalError, ValueError) as exc:
            fab_result.outcomes.append(ZoningCommandOutcome(command=cmd, status="failed", detail=str(exc)))
            fab_result.error = f"Stopped on {fab.switch_host} at '{cmd}': {exc}"
            if is_enable:
                _inspect_after_cfgenable_error(writer, fab, fab_result)
            elif write_attempted:
                _handle_pre_enable_error(writer, fab_result)
            return False
        first = next((ln.strip() for ln in out.splitlines() if ln.strip()), "")
        fab_result.outcomes.append(ZoningCommandOutcome(command=cmd, status="created", detail=first))
    return True


def _apply_fabric(ctx: _ApplyContext, fab: FabricZoningApplyPlan) -> bool:
    label = fabric_label(fab.fabric)
    fab_result = FabricZoningApplyResult(
        fabric=fab.fabric,
        switch_host=fab.switch_host,
        active_cfg=fab.active_cfg,
        status="failed",
        removals=list(fab.removals),
    )
    ctx.result.fabrics.append(fab_result)
    # ADR 0025 condition 4 / STANDARD S5: persist the removal set before any write leaves the process.
    try:
        ctx.save(ctx.result)
    except ApplyRecordError as exc:
        fab_result.removals = []
        fab_result.error = (
            f"Could not save the undo record before writing to {fab.switch_host}: {exc}. "
            "Nothing was sent to this switch."
        )
        return False
    objects = plan_objects_for(fab)
    ctx.report(f"Checking {label} switch {fab.switch_host}…")
    try:
        with ctx.writer_factory(ctx.approval, fab.fabric, objects) as writer:
            if refusal := _preflight_check(writer, fab):
                fab_result.error = refusal
                fab_result.removals = []
                try_save_record(ctx.save, ctx.result)
                return False
            ctx.report(f"Applying {len(fab.zones)} zone(s) on {label} switch {fab.switch_host}…")
            if not _send_commands(writer, fab, fab_result):
                try_save_record(ctx.save, ctx.result)
                return False
            ctx.report(f"Verifying effective configuration on {label} switch {fab.switch_host}…")
            try:
                _verify_effective(writer, fab, fab_result)
            except DeviceError as exc:
                fab_result.error = f"Read-back after cfgenable failed on {fab.switch_host}: {exc}."
                _inspect_after_cfgenable_error(writer, fab, fab_result)
            else:
                if fab_result.status != "applied":
                    _inspect_after_cfgenable_error(writer, fab, fab_result)
            try_save_record(ctx.save, ctx.result)
            return fab_result.status == "applied"
    except (DeviceError, ApprovalError, ApplyRecordError) as exc:
        if not fab_result.outcomes:
            fab_result.removals = []
        fab_result.error = str(exc)
        try_save_record(ctx.save, ctx.result)
        return False


def apply_zoning_plan(
    approval: Approval,
    apply_plan: ZoningApplyPlan,
    *,
    progress: Callable[[str], None] | None = None,
    writer_factory: Callable[[Approval, Fabric, ZoningPlanObjects], Any] | None = None,
) -> ZoningApplyResult:
    """Apply an operator-approved `ZoningApplyPlan` to each Brocade fabric switch in order."""
    save = approval.require_saver()
    result = ZoningApplyResult(plan_id=apply_plan.plan_id, fabrics=[])
    ctx = _ApplyContext(approval, result, save, progress, writer_factory or make_brocade_writer)
    stopped = False
    for fab in apply_plan.fabrics:
        if not fab.commands or not fab.active_cfg:
            result.fabrics.append(FabricZoningApplyResult(
                fabric=fab.fabric, switch_host=fab.switch_host, active_cfg=fab.active_cfg, status="skipped",
            ))
            continue
        if stopped:
            result.fabrics.append(FabricZoningApplyResult(
                fabric=fab.fabric, switch_host=fab.switch_host, active_cfg=fab.active_cfg,
                status="skipped", error="Skipped because an earlier fabric switch failed.",
            ))
            continue
        if not _apply_fabric(ctx, fab):
            stopped = True
    failed = [f.error for f in result.fabrics if f.status == "failed" and f.error]
    if failed:
        result.error = "; ".join(failed)
    return result


def resolve_switch_creds(
    intent: ProvisioningIntent, apply_plan: ZoningApplyPlan,
) -> dict[Fabric, EndpointCreds]:
    """Extract and validate switch credentials and matching host for every fabric in `apply_plan`."""
    switches: dict[Fabric, EndpointCreds] = {}
    if intent.switch_f1:
        switches["odd"] = intent.switch_f1
    if intent.switch_f2:
        switches["even"] = intent.switch_f2
    for fab in apply_plan.fabrics:
        if fab.fabric not in switches:
            raise StepPreconditionError(
                f"Switch credentials for fabric {fabric_label(fab.fabric)} are missing."
            )
        configured = switches[fab.fabric].host.strip()
        if fab.switch_host.strip() != configured:
            raise StepPreconditionError(
                f"Switch host '{fab.switch_host}' does not match this run's configured "
                f"{fabric_label(fab.fabric)} switch '{configured}'."
            )
    return switches


def _verify_fabric_against_stored(
    fab: FabricZoningApplyPlan, stored: dict[str, Any] | None,
) -> None:
    if stored is None:
        raise StepPreconditionError(
            f"Fabric {fabric_label(fab.fabric)} was not present in this run's zoning plan."
        )
    if (stored.get("switch_host") or "").strip() != fab.switch_host.strip():
        raise StepPreconditionError(
            f"Switch host '{fab.switch_host}' does not match this run's zoning plan "
            f"('{stored.get('switch_host', '')}')."
        )
    if (stored.get("active_cfg") or "").strip() != fab.active_cfg.strip():
        raise StepPreconditionError(
            f"Active cfg '{fab.active_cfg}' does not match this run's zoning plan "
            f"('{stored.get('active_cfg', '')}')."
        )


def verify_plan_for_run(
    coord: RunCoordinator, run_id: str, apply_plan: ZoningApplyPlan,
) -> None:
    """Verify `switch_host` and `active_cfg` against the run's stored intent and latest `zoning.plan`."""
    if not apply_plan.fabrics:
        return
    if (intent := coord.store.get_provisioning_intent(run_id)) is not None:
        resolve_switch_creds(intent, apply_plan)
    latest_plan = next(
        (ev.data["plan"] for ev in reversed(coord.list_events(run_id))
         if ev.event_type == "zoning.plan" and ev.data.get("plan")),
        None,
    )
    if latest_plan is None:
        return
    by_fabric = {
        mapped: entry
        for entry in (latest_plan.get("fabrics") or [])
        if (mapped := LABEL_TO_FABRIC.get(entry.get("fabric", ""))) is not None
    }
    for fab in apply_plan.fabrics:
        _verify_fabric_against_stored(fab, by_fabric.get(fab.fabric))


def start_approved_apply(
    coord: RunCoordinator,
    run_id: str,
    held_plans: dict[str, ZoningApplyPlan],
    approved_plan: str | None,
) -> RunRecord:
    """Validate the operator's approval, issue a zoning Approval, and spawn the switch apply."""
    run = coord.get_run(run_id)
    intent = coord.get_provisioning_intent(run_id)
    held = held_plans.get(run_id)
    if held is None or not held.fabrics:
        raise StepPreconditionError("No zoning apply plan is held — generate the command set first.")
    check_approval(approved_plan, held.plan_id)
    switches = resolve_switch_creds(intent, held)
    approval = coord.issue_approval(run_id, "zoning", switches=switches)
    held_plans.pop(run_id, None)
    coord.spawn(run_id, run_zoning_apply(coord, run, held, approval), approval=approval)
    return run


async def run_zoning_apply(
    coord: RunCoordinator,
    run: RunRecord,
    apply_plan: ZoningApplyPlan,
    approval: Approval,
) -> None:
    """Background worker for opt-in Brocade switch zoning apply."""
    phase = WorkflowPhase.STORAGE_ZONING
    coord.set_state(run, RunStatus.RUNNING, phase)
    coord.emit(
        run.run_id, phase, events.ZONING_APPLY_STARTED,
        "Applying approved Brocade zoning commands to the fabric switches…",
    )
    loop = asyncio.get_running_loop()

    def progress(message: str) -> None:
        loop.call_soon_threadsafe(coord.emit, run.run_id, phase, events.PHASE_PROGRESS, message)

    result = await coord.run_approved(approval, partial(apply_zoning_plan, approval, apply_plan, progress=progress))
    if result.error:
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
        coord.emit(run.run_id, phase, events.ZONING_APPLY_FAILED, result.error, events.ZoningApplyData(result=result))
        return
    applied = [f for f in result.fabrics if f.status == "applied"]
    total_zones = sum(len(f.verified_zones) for f in applied)
    coord.set_state(run, RunStatus.READY, phase)
    coord.emit(
        run.run_id, phase, events.ZONING_APPLIED,
        f"Applied and verified {total_zones} zone(s) on {len(applied)} switch(es). "
        "Check zoning again to confirm the host has logged in on the array.",
        events.ZoningApplyData(result=result),
    )
