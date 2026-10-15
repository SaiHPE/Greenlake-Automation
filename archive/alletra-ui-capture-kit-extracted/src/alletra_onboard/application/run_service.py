from __future__ import annotations

from datetime import UTC, datetime

from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.ports import RunStore


class RunService:
    def __init__(self, store: RunStore) -> None:
        self.store = store

    def create_run(self, serial_number: str) -> RunRecord:
        run = RunRecord(
            serial_number=serial_number,
            status=RunStatus.READY,
            current_phase=WorkflowPhase.PREFLIGHT,
        )
        self.store.upsert_run(run)
        return run

    def update_status(self, run: RunRecord, status: RunStatus, phase: WorkflowPhase) -> RunRecord:
        run.status = status
        run.current_phase = phase
        run.updated_at = datetime.now(UTC)
        self.store.upsert_run(run)
        return run
