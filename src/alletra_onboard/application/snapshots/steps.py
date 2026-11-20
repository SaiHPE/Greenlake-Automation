"""Step service for the snapshot context, over the RunCoordinator (SPEC-023).

Read the array and plan (read-only); apply the approved plan; verify by reading back. The plan is
held in memory with the read it came from: an approval, not a result, withdrawn whenever the array is
read again (LESSONS 6) and spent by an apply.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import partial

from alletra_onboard.application.runs.coordinator import (
    RunCoordinator,
    StepPreconditionError,
    check_approval,
    new_plan_id,
)
from alletra_onboard.application.snapshots import apply as snapshots_apply
from alletra_onboard.application.snapshots import read as snapshots_read
from alletra_onboard.application.snapshots import verify as snapshots_verify
from alletra_onboard.application.snapshots.plan import plan_snapshots
from alletra_onboard.domain import events
from alletra_onboard.domain.approval import Approval
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.snapshots import SnapshotArrayView, SnapshotPlan, SnapshotVerification

PHASE = WorkflowPhase.STORAGE_SNAPSHOT
RESULT_ARTIFACT = "snapshot_result"


def _array_summary(view: SnapshotArrayView) -> events.SnapshotArraySummary:
    """What the page and the as-built show of the read: not every volume, only the array and its
    schedules."""
    return events.SnapshotArraySummary(
        host=view.host, name=view.name, os_version=view.os_version, time_zone=view.time_zone,
        retention_max_hours=view.retention_max_hours, schedules=view.schedules,
    )


def _planned(intent: ProvisioningIntent) -> tuple[frozenset[str], frozenset[str]]:
    """The Volumes tab's volumes and sets: a source the run has still to provision."""
    return (frozenset(v.name for v in intent.volumes),
            frozenset(v.vvset for v in intent.volumes if v.vvset))


def _writes(plan: SnapshotPlan) -> list:
    """The creates an apply will make: every snapshot now and every schedule."""
    return [a for a in plan.actions if a.state == "create"]


class SnapshotSteps:
    def __init__(self, coord: RunCoordinator, *, read_fn: Callable = snapshots_read.read_array,
                 apply_fn: Callable = snapshots_apply.apply_plan) -> None:
        self._coord = coord
        self._read = read_fn
        self._apply = apply_fn
        self._plan: dict[str, tuple[SnapshotPlan, SnapshotArrayView]] = {}

    def _require_snapshots(self, run_id: str) -> ProvisioningIntent:
        intent = self._coord.get_provisioning_intent(run_id)
        if intent.snapshots is None:
            raise StepPreconditionError(
                "this run's workbook has no Snapshots tab — add the volume sets or volumes to snapshot, then start "
                "a new run"
            )
        return intent

    def _progress(self, run_id: str) -> Callable[[str], None]:
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(self._coord.emit, run_id, PHASE, events.PHASE_PROGRESS, message)

        return progress

    def tab(self, run_id: str) -> dict:
        """The page's inputs: the Snapshots tab's rows in words, and the id of the plan the server holds
        ("" after an apply, a restart or before a read), so the page never offers an apply it would refuse."""
        intent = self._coord.get_provisioning_intent(run_id)
        rows = intent.snapshots.requests if intent.snapshots is not None else []
        held = self.previewed_plan(run_id)
        return {
            "rows": [{"source": r.source, "kind": r.kind, "schedule": r.name if r.has_schedule else "",
                      "summary": r.summary()} for r in rows],
            "held_plan_id": held.plan_id if held is not None else "",
        }

    def previewed_plan(self, run_id: str) -> SnapshotPlan | None:
        entry = self._plan.get(run_id)
        return entry[0] if entry else None

    # ------------------------------------------------------------------ R3, R4: read and plan

    def start_snapshots_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_snapshots(run_id)
        # A new read is a new plan to approve: the old approval goes now, not when the read finishes.
        self._plan.pop(run_id, None)
        coord.spawn(run_id, self._run_preview(run, intent))
        return run

    async def _run_preview(self, run: RunRecord, intent: ProvisioningIntent) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, PHASE)
        coord.emit(run.run_id, PHASE, events.STEP_STARTED, "Reading snapshots and snapshot schedules on the array…")
        view = await asyncio.to_thread(partial(self._read, intent.array, progress=self._progress(run.run_id)))
        if view.read_error:
            plan = SnapshotPlan(error=view.read_error)
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, PHASE)
            coord.emit(run.run_id, PHASE, events.SNAPSHOTS_PREVIEW_FAILED, view.read_error,
                       events.SnapshotPlanData(array=_array_summary(view), plan=plan))
            return
        volumes, vvsets = _planned(intent)
        plan = plan_snapshots(intent.snapshots, view, planned_volumes=volumes, planned_vvsets=vvsets)
        plan = plan.model_copy(update={"plan_id": new_plan_id()})
        self._plan[run.run_id] = (plan, view)
        creates = sum(1 for a in plan.actions if a.state == "create")
        exists = sum(1 for a in plan.actions if a.state == "exists")
        name = view.name or view.host
        if plan.blockers:
            summary = (f"Read {name} — {len(plan.blockers)} blocking finding(s); nothing can be created until they "
                       "are resolved.")
        else:
            summary = f"Read {name} — plan ready: {creates} to create, {exists} already there. Review the plan."
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, PHASE)
        coord.emit(run.run_id, PHASE, events.SNAPSHOTS_PREVIEWED, summary,
                   events.SnapshotPlanData(array=_array_summary(view), plan=plan))

    # ------------------------------------------------------------------ R5, R6: apply the approved plan

    def start_snapshots_apply(self, run_id: str, *, approved_plan: str | None) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_snapshots(run_id)
        entry = self._plan.get(run_id)
        if entry is None:
            raise StepPreconditionError("no snapshot plan to apply — read the array first")
        plan, view = entry
        if plan.error:
            raise StepPreconditionError(f"the snapshot preview reported a blocking problem: {plan.error}")
        if plan.blockers:
            raise StepPreconditionError("the plan has findings that must be resolved first: " + "; ".join(plan.blockers))
        if not _writes(plan):
            raise StepPreconditionError("nothing to create — every snapshot and schedule in the plan is already there")
        # LESSONS 7: the operator's tick reaches the server as the id of the plan it was given for.
        check_approval(approved_plan, plan.plan_id)
        approval = coord.issue_approval(run_id, "snapshots", {"A": intent.array})
        self._plan.pop(run_id, None)
        coord.spawn(run_id, self._run_apply(run, intent, plan, view, approval), approval=approval)
        return run

    async def _run_apply(self, run: RunRecord, intent: ProvisioningIntent, plan: SnapshotPlan,
                         view: SnapshotArrayView, approval: Approval) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, PHASE)
        coord.emit(run.run_id, PHASE, events.SNAPSHOTS_APPLY_STARTED, "Creating the snapshots and schedules…")
        result = await coord.run_approved(
            approval, partial(self._apply, plan, view, intent, approval, progress=self._progress(run.run_id)),
        )
        # the writes happened; failing to cache the record must not fail the step
        coord.save_artifact_best_effort(run.run_id, RESULT_ARTIFACT, result.model_dump_json().encode("utf-8"))
        data = events.SnapshotResultData(result=result)
        if result.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, PHASE)
            coord.emit(run.run_id, PHASE, events.SNAPSHOTS_APPLY_FAILED, result.error, data)
            return
        created = sum(1 for o in result.outcomes if o.status == "created")
        existed = sum(1 for o in result.outcomes if o.status == "exists")
        message = f"Snapshots and schedules created — {created} row(s) written, {existed} already there."
        if result.schedules_created:
            message += (f" The array now runs {', '.join(result.schedules_created)} until someone removes "
                        f"{'it' if len(result.schedules_created) == 1 else 'them'}.")
        coord.set_state(run, RunStatus.READY, PHASE)
        coord.emit(run.run_id, PHASE, events.SNAPSHOTS_APPLIED, message, data)
        # R7: read back after apply, as the operator's Check snapshots does
        await self._run_verify(run, intent, plan, result.started_at if result.schedules_created else "")

    # ------------------------------------------------------------------ R7: verify (read-only)

    def _plan_for_verify(self, run_id: str) -> SnapshotPlan | None:
        held = self.previewed_plan(run_id)
        if held is not None:
            return held
        # after an apply the approval is spent, but the plan it came from is in the run's events
        for event in reversed(self._coord.list_events(run_id)):
            if event.event_type == "snapshots.previewed" and event.data and event.data.get("plan"):
                try:
                    return SnapshotPlan.model_validate(event.data["plan"])
                except ValueError:
                    return None
        return None

    def _applied_since(self, run_id: str) -> str:
        """When this run's first apply that created a schedule began: its snapshots are counted from then."""
        for event in self._coord.list_events(run_id):
            if event.event_type in ("snapshots.applied", "snapshots.apply.failed"):
                result = event.data.get("result") or {}
                if result.get("schedules_created"):
                    return str(result.get("started_at") or "")
        return ""

    def start_snapshots_verify(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_snapshots(run_id)
        plan = self._plan_for_verify(run_id)
        if plan is None:
            raise StepPreconditionError("nothing to check yet — read the array first so the tool knows what to look for")
        coord.spawn(run_id, self._run_verify(run, intent, plan, self._applied_since(run_id)))
        return run

    async def _run_verify(self, run: RunRecord, intent: ProvisioningIntent, plan: SnapshotPlan, since: str) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, PHASE)
        coord.emit(run.run_id, PHASE, events.SNAPSHOTS_VERIFY_STARTED, "Reading the snapshots and schedules back…")
        verification: SnapshotVerification = await asyncio.to_thread(partial(
            snapshots_verify.verify, intent, plan, since=since, read_fn=self._read, progress=self._progress(run.run_id)))
        data = events.SnapshotVerifyData(verification=verification)
        if verification.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, PHASE)
            coord.emit(run.run_id, PHASE, events.SNAPSHOTS_VERIFY_FAILED, verification.error, data)
            return
        coord.set_state(run, RunStatus.READY, PHASE)
        coord.emit(run.run_id, PHASE, events.SNAPSHOTS_VERIFIED, _verify_summary(verification), data)


def _verify_summary(verification: SnapshotVerification) -> str:
    rows = verification.rows
    parts = []
    for verdict, label in (("scheduled", "scheduled"), ("taking", "taking snapshots"), ("not_scheduled", "not scheduled")):
        n = sum(1 for r in rows if r.verdict == verdict)
        if n or verdict != "taking":
            parts.append(f"{n} {label}")
    now = [r for r in rows if r.now_ok is not None]
    if now:
        parts.append(f"snapshot now in place on {sum(1 for r in now if r.now_ok)} of {len(now)} row(s)")
    return " · ".join(parts)
