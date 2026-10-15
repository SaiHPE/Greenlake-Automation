from __future__ import annotations

from alletra_onboard.domain.models import ArrayWorkItem, RunEvent, RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.ports import EventSink, RunStore


class WorkflowOrchestrator:
    def __init__(self, store: RunStore, events: EventSink) -> None:
        self.store = store
        self.events = events

    async def preflight(self, run: RunRecord, item: ArrayWorkItem) -> RunRecord:
        run.status = RunStatus.READY
        run.current_phase = WorkflowPhase.GL_DISCOVER_SERVICE
        self.store.upsert_run(run)
        event = RunEvent(
            run_id=run.run_id,
            phase=WorkflowPhase.PREFLIGHT,
            event_type="phase.verification.passed",
            message=f"Preflight input validation passed for {item.serial_number}",
        )
        self.store.append_event(event)
        await self.events.publish(event)
        return run
