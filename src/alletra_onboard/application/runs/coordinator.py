"""RunCoordinator — the genuinely shared core of every step: run lifecycle, the guarded
background-task spawner, status/phase persistence and event emission (store + SSE fan-out).

Step logic itself lives in the per-context step services (application/onboarding/steps.py,
application/storage/steps.py, application/documents/steps.py); they all compose this coordinator.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.config import Settings, load_settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    RunEvent,
    RunMode,
    RunRecord,
    RunStatus,
    WorkflowPhase,
)
from alletra_onboard.domain.ports import RunStore
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.workflow import initial_phase


class RunNotFoundError(LookupError):
    pass


class RunBusyError(RuntimeError):
    """A background step is already executing for this run."""


class StepPreconditionError(RuntimeError):
    """A step was requested before its prerequisite ran (e.g. zoning/provision before discovery)."""


class PendingSheetNotFoundError(LookupError):
    """A complete sheet was uploaded but its server-side hold is gone (already turned into a run, or
    the state DB was reset) — the operator should re-upload the Initialisation sheet."""


class RunCoordinator:
    def __init__(self, settings: Settings, store: RunStore, events: InMemoryEventBus) -> None:
        self.settings = settings
        self.store = store
        self.events = events
        self._tasks: dict[str, asyncio.Task] = {}

    def current_settings(self) -> Settings:
        # Re-read settings (incl. .env) at each step so GreenLake credentials entered in the
        # Configure screen AFTER the server started take effect without a restart. The startup
        # snapshot (self.settings) is only a fallback if reloading ever fails.
        try:
            return load_settings()
        except Exception:  # noqa: BLE001
            return self.settings

    # ------------------------------------------------------------------ run lifecycle

    def create_run(
        self,
        item: ArrayWorkItem,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
        provisioning_intent: ProvisioningIntent | None = None,
    ) -> RunRecord:
        selected = list(selected_steps or [])
        run = RunRecord(
            serial_number=item.serial_number,
            status=RunStatus.READY,
            current_phase=initial_phase(mode, selected),  # land on the first enabled step
            mode=mode,
            selected_steps=selected,
        )
        self.store.upsert_run(run)
        self.store.save_work_item(run.run_id, item)
        if provisioning_intent is not None:
            self.store.save_provisioning_intent(run.run_id, provisioning_intent)
        self.emit(
            run.run_id,
            run.current_phase,
            "run.created",
            f"Run created for {item.serial_number} ({mode.value})",
        )
        return run

    def stash_pending_sheet(
        self, work_item: ArrayWorkItem, provisioning_intent: ProvisioningIntent | None
    ) -> str:
        """Hold a parsed COMPLETE sheet server-side and return a single-use token. The run is minted
        later, when the operator picks a mode (ADR 0005 revision) — device passwords never round-trip
        to the browser."""
        token = uuid4().hex
        self.store.save_pending_sheet(token, work_item, provisioning_intent)
        return token

    def create_run_from_pending(
        self,
        token: str,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
    ) -> RunRecord:
        """Mint the run for a previously-uploaded complete sheet, now that the operator has chosen a
        mode. Consumes the pending-sheet hold (single use)."""
        popped = self.store.pop_pending_sheet(token)
        if popped is None:
            raise PendingSheetNotFoundError(token)
        work_item, provisioning_intent = popped
        return self.create_run(
            work_item,
            mode=mode,
            selected_steps=selected_steps,
            provisioning_intent=provisioning_intent,
        )

    def get_provisioning_intent(self, run_id: str) -> ProvisioningIntent:
        intent = self.store.get_provisioning_intent(run_id)
        if intent is None:
            raise RunNotFoundError(run_id)
        return intent

    def get_run(self, run_id: str) -> RunRecord:
        run = self.store.get_run(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return run

    def get_work_item(self, run_id: str) -> ArrayWorkItem:
        item = self.store.get_work_item(run_id)
        if item is None:
            raise RunNotFoundError(run_id)
        return item

    def list_runs(self) -> list[RunRecord]:
        return self.store.list_runs()

    def list_events(self, run_id: str) -> list[RunEvent]:
        return self.store.list_events(run_id)

    def mark_complete(self, run_id: str) -> RunRecord:
        run = self.get_run(run_id)
        self.set_state(run, RunStatus.SUCCEEDED, WorkflowPhase.COMPLETE)
        self.emit(run_id, WorkflowPhase.COMPLETE, "run.completed", "Operator confirmed DSCC finalize — onboarding complete")
        return run

    async def wait(self, run_id: str) -> None:
        """Await the run's active background task (used by tests and graceful shutdown)."""
        task = self._tasks.get(run_id)
        if task is not None:
            await task

    # ------------------------------------------------------------------ step infrastructure

    def spawn(self, run_id: str, coro) -> None:
        existing = self._tasks.get(run_id)
        if existing is not None and not existing.done():
            coro.close()
            raise RunBusyError(run_id)
        self._tasks[run_id] = asyncio.create_task(self._guarded(run_id, coro))

    async def _guarded(self, run_id: str, coro) -> None:
        # A crash must never leave a run stuck in RUNNING with no trace.
        try:
            await coro
        except Exception as exc:  # noqa: BLE001 - background task; record, don't crash the app.
            run = self.store.get_run(run_id)
            if run is not None:
                self.set_state(run, RunStatus.RETRYABLE_FAILURE)
            self.emit(
                run_id,
                run.current_phase if run else WorkflowPhase.NOT_STARTED,
                "step.crashed",
                f"{type(exc).__name__}: {str(exc)[:300]}",
            )

    def set_state(self, run: RunRecord, status: RunStatus, phase: WorkflowPhase | None = None) -> None:
        run.status = status
        if phase is not None:
            run.current_phase = phase
        run.updated_at = datetime.now(UTC)
        self.store.upsert_run(run)

    def emit(
        self, run_id: str, phase: WorkflowPhase, event_type: str, message: str, data: dict | None = None
    ) -> None:
        event = RunEvent(run_id=run_id, phase=phase, event_type=event_type, message=message, data=data or {})
        self.store.append_event(event)
        self.events.publish_sync(event)
