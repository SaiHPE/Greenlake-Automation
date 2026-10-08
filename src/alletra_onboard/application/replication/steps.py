"""Step service for the replication context, over the RunCoordinator (SPEC-016).

Read both arrays, check, plan (read-only); apply the approved plan over WSAPI; verify by reading
back. The plan is held in memory like the provisioning plan: an approval, not a result, withdrawn
whenever the step is re-run and spent by an apply.
"""

from __future__ import annotations

import asyncio
from functools import partial

from alletra_onboard.application.replication import apply as replication_apply
from alletra_onboard.application.replication import plan as replication_plan
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication import verify as replication_verify
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.replication import ReplicationPlan, ReplicationReport

REPORT_ARTIFACT = "replication_report"
RESULT_ARTIFACT = "replication_result"


class ReplicationSteps:
    def __init__(self, coord: RunCoordinator) -> None:
        self._coord = coord
        self._plan: dict[str, tuple[ReplicationPlan, ReplicationReport]] = {}

    def _require_replication(self, run_id: str):
        intent = self._coord.get_provisioning_intent(run_id)
        if intent.replication is None:
            raise StepPreconditionError(
                "this run's workbook has no Replication tab — add the peer array and the volume sets to "
                "protect, then start a new run"
            )
        return intent

    def current_report(self, run_id: str) -> ReplicationReport | None:
        raw = self._coord.store.load_artifact(run_id, REPORT_ARTIFACT)
        if raw is None:
            return None
        try:
            return ReplicationReport.model_validate_json(raw)
        except Exception:  # noqa: BLE001 - an unreadable stored report means "read again"
            return None

    def previewed_plan(self, run_id: str) -> ReplicationPlan | None:
        entry = self._plan.get(run_id)
        return entry[0] if entry else None

    def start_replication_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        self._plan.pop(run_id, None)
        coord.spawn(run_id, self._run_preview(run, intent))
        return run

    async def _run_preview(self, run: RunRecord, intent) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "step.started", "Reading Remote Copy on both arrays…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        primary = await asyncio.to_thread(partial(replication_read.read_array, intent.array, progress=progress))
        peer = await asyncio.to_thread(partial(replication_read.read_array, intent.replication.peer, progress=progress))
        report = replication_plan.check(primary, peer, intent.replication)
        plan = replication_plan.build_plan(report, intent.replication, intent)
        try:
            coord.store.save_artifact(run.run_id, REPORT_ARTIFACT, report.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001, S110 - the read succeeded; failing to cache it must not fail the step
            pass
        self._plan[run.run_id] = (plan, report)

        if plan.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, "replication.preview.failed", plan.error,
                       data={"report": report.model_dump(mode="json"), "plan": plan.model_dump(mode="json")})
            return
        creates = sum(1 for a in plan.actions if a.state == "create")
        exists = sum(1 for a in plan.actions if a.state == "exists")
        a_name, b_name = primary.name or primary.host, peer.name or peer.host
        if plan.blockers:
            summary = (f"Read {a_name} and {b_name} — {len(plan.blockers)} blocking finding(s); "
                       "nothing can be configured until they are resolved.")
        else:
            summary = (f"Read {a_name} and {b_name} — plan ready: {creates} to create, {exists} already there. "
                       "Review the plan.")
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, "replication.previewed", summary,
                   data={"report": report.model_dump(mode="json"), "plan": plan.model_dump(mode="json")})

    # ------------------------------------------------------------------ R4/R7: apply the approved plan

    def start_replication_apply(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        entry = self._plan.get(run_id)
        if entry is None:
            raise StepPreconditionError("no replication plan to apply — read both arrays first")
        plan, _report = entry
        if plan.error:
            raise StepPreconditionError(f"the replication preview reported a blocking problem: {plan.error}")
        if plan.blockers:
            raise StepPreconditionError("the plan has findings that must be resolved first: " + "; ".join(plan.blockers))
        if not any(a.state == "create" for a in plan.actions):
            raise StepPreconditionError("nothing to create — every object in the plan already exists")
        coord.spawn(run_id, self._run_apply(run, intent, plan))
        return run

    async def _run_apply(self, run: RunRecord, intent, plan: ReplicationPlan) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "replication.apply.started", "Configuring replication over WSAPI…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        result = await asyncio.to_thread(partial(replication_apply.apply_plan, plan, intent, progress=progress))
        # the approval is spent: a second apply needs a fresh read and plan
        self._plan.pop(run.run_id, None)
        try:
            coord.store.save_artifact(run.run_id, RESULT_ARTIFACT, result.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001, S110 - the writes happened; failing to cache the record must not fail the step
            pass
        created = sum(1 for o in result.outcomes if o.status == "created")
        existed = sum(1 for o in result.outcomes if o.status == "exists")
        if result.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, "replication.apply.failed", result.error, data={"result": result.model_dump(mode="json")})
            return
        coord.set_state(run, RunStatus.READY, phase)
        groups = ", ".join(result.groups_created) or "no new group"
        coord.emit(run.run_id, phase, "replication.applied",
                   f"Replication configured — {groups}; {created} write(s), {existed} already there. Verify replication to read it back.",
                   data={"result": result.model_dump(mode="json")})

    # ------------------------------------------------------------------ R6: verify (read-only)

    def start_replication_verify(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        plan = self._plan_for_verify(run_id)
        if plan is None:
            raise StepPreconditionError("nothing to verify yet — read both arrays first so the tool knows which groups to look for")
        coord.spawn(run_id, self._run_verify(run, intent, plan))
        return run

    def _plan_for_verify(self, run_id: str) -> ReplicationPlan | None:
        entry = self._plan.get(run_id)
        if entry is not None:
            return entry[0]
        # after an apply the approval is spent, but the plan it came from is in the run's events
        for event in reversed(self._coord.list_events(run_id)):
            if event.event_type == "replication.previewed" and event.data and event.data.get("plan"):
                try:
                    return ReplicationPlan.model_validate(event.data["plan"])
                except Exception:  # noqa: BLE001
                    return None
        return None

    async def _run_verify(self, run: RunRecord, intent, plan: ReplicationPlan) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "replication.verify.started", "Reading Remote Copy back on both arrays…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        verification = await asyncio.to_thread(partial(replication_verify.verify, intent, plan, progress=progress))
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE if verification.error else RunStatus.READY, phase)
        if verification.error:
            coord.emit(run.run_id, phase, "replication.verify.failed", verification.error,
                       data={"verification": verification.model_dump(mode="json")})
            return
        counts = {"replicating": 0, "syncing": 0, "not_replicating": 0}
        for g in verification.groups:
            counts[g.verdict] += 1
        summary = (f"{counts['replicating']} replicating · {counts['syncing']} syncing · {counts['not_replicating']} not replicating · "
                   + ("links Up" if verification.links_ok else "links NOT all Up"))
        coord.emit(run.run_id, phase, "replication.verified", summary, data={"verification": verification.model_dump(mode="json")})
