"""Step service for the replication context, over the RunCoordinator (SPEC-016).

Release (a): read both arrays, check, plan — read-only. The plan is held in memory like the
provisioning plan: an approval, not a result, withdrawn whenever the step is re-run.
"""

from __future__ import annotations

import asyncio
from functools import partial

from alletra_onboard.application.replication import plan as replication_plan
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.replication import ReplicationPlan, ReplicationReport

REPORT_ARTIFACT = "replication_report"


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
                       "Review, then confirm to configure replication.")
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, "replication.previewed", summary,
                   data={"report": report.model_dump(mode="json"), "plan": plan.model_dump(mode="json")})
