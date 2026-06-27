"""Run orchestration for the A -> B -> C onboarding flow — the service the API (and later the
frontend) drives.

Each component runs as a background asyncio task that updates the persisted RunRecord and
emits RunEvents (stored + fanned out live to SSE subscribers). The flow is operator-gated, so
the service exposes one start_* per step instead of a fire-and-forget pipeline:

    create_run(work_item)                       status=READY,   phase=PREFLIGHT
    start_provision(dry_run?)        -> A       status=RUNNING, then READY (next: cloudinit)
    start_cloudinit(cloudinit_url?)  -> B       fills, emits operator.review_ready, waits for
                                                the operator's Submit in the launched browser
    start_dscc(cdp_url)              -> C       fills through System, stops at the credential
    mark_complete()                             operator confirms they finalized in DSCC

The cloudinit URL is a RUNTIME parameter (the link-local IP changes every boot) — passing it
to start_cloudinit overrides the work item's stored value.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, Callable

from alletra_onboard.adapters.browser.cloudinit_wizard import CloudinitWizardAdapter
from alletra_onboard.adapters.browser.dscc_setup import DsccSetupAdapter
from alletra_onboard.application.event_bus import InMemoryEventBus
from alletra_onboard.application.provisioning import (
    FAILED,
    WARNING,
    build_provisioning_service,
)
from alletra_onboard.application.verification import verify
from alletra_onboard.config import Settings, load_settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    BrowserResultStatus,
    RunEvent,
    RunMode,
    RunRecord,
    RunStatus,
    WorkflowPhase,
)
from alletra_onboard.domain.ports import RunStore
from alletra_onboard.domain.storage import ProvisioningIntent
from alletra_onboard.domain.workflow import initial_phase, next_enabled_phase


def _next_hint(phase: WorkflowPhase) -> str:
    """A human hint for what comes after an init step, given the selection-aware next phase."""
    return {
        WorkflowPhase.CLOUDINIT_CONNECT: "next: Cloud Connectivity Wizard",
        WorkflowPhase.DSCC_SETUP_SYSTEM: "next: DSCC Setup",
        WorkflowPhase.STORAGE_DISCOVER: "next: storage discovery",
        WorkflowPhase.COMPLETE: "no further onboarding steps selected",
    }.get(phase, f"next: {phase.value}")


class RunNotFoundError(LookupError):
    pass


class RunBusyError(RuntimeError):
    """A background step is already executing for this run."""


def _default_provision_factory(settings: Settings, progress: Callable) -> Any:
    return build_provisioning_service(settings, progress=progress)


def _default_cloudinit_factory(settings: Settings, on_status: Callable[[str], None]) -> Any:
    # Launch mode: the product flow opens its own browser at the pasted cloudinit URL.
    return CloudinitWizardAdapter(
        headless=settings.browser_headless,
        cdp_url=None,
        artifact_dir=settings.artifact_dir,
        on_status=on_status,
    )


def _default_dscc_factory(settings: Settings, cdp_url: str) -> Any:
    return DsccSetupAdapter(cdp_url=cdp_url, artifact_dir=settings.artifact_dir)


class OnboardingService:
    def __init__(
        self,
        settings: Settings,
        store: RunStore,
        events: InMemoryEventBus,
        *,
        provision_factory: Callable = _default_provision_factory,
        cloudinit_factory: Callable = _default_cloudinit_factory,
        dscc_factory: Callable = _default_dscc_factory,
        verify_fn: Callable = verify,
    ) -> None:
        self.settings = settings
        self.store = store
        self.events = events
        self._provision_factory = provision_factory
        self._cloudinit_factory = cloudinit_factory
        self._dscc_factory = dscc_factory
        self._verify_fn = verify_fn
        self._tasks: dict[str, asyncio.Task] = {}

    def _current_settings(self) -> Settings:
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
        self._emit(
            run.run_id,
            run.current_phase,
            "run.created",
            f"Run created for {item.serial_number} ({mode.value})",
        )
        return run

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
        self._set(run, RunStatus.SUCCEEDED, WorkflowPhase.COMPLETE)
        self._emit(run_id, WorkflowPhase.COMPLETE, "run.completed", "Operator confirmed DSCC finalize — onboarding complete")
        return run

    async def wait(self, run_id: str) -> None:
        """Await the run's active background task (used by tests and graceful shutdown)."""
        task = self._tasks.get(run_id)
        if task is not None:
            await task

    # ------------------------------------------------------------------ step A: GreenLake

    def start_provision(self, run_id: str, *, dry_run: bool = False) -> RunRecord:
        run, item = self.get_run(run_id), self.get_work_item(run_id)
        self._spawn(run_id, self._run_provision(run, item, dry_run))
        return run

    async def _run_provision(self, run: RunRecord, item: ArrayWorkItem, dry_run: bool) -> None:
        self._set(run, RunStatus.RUNNING, WorkflowPhase.GL_DISCOVER_SERVICE)
        label = "GreenLake provisioning (dry-run)" if dry_run else "GreenLake provisioning"
        self._emit(run.run_id, WorkflowPhase.GL_DISCOVER_SERVICE, "step.started", f"{label} started")

        def progress(phase: WorkflowPhase, message: str) -> None:
            run.current_phase = phase
            self.store.upsert_run(run)
            self._emit(run.run_id, phase, "phase.progress", message)

        service = self._provision_factory(self._current_settings(), progress)
        result = await service.provision(item, dry_run=dry_run)

        # Recompute from scratch (don't accumulate across re-runs of this step).
        run.warnings = [
            f"{outcome.phase.value}: {outcome.detail}" for outcome in result.phases if outcome.status == WARNING
        ]
        run.resources.device_id = result.device_id or run.resources.device_id
        run.resources.subscription_id = result.subscription_id or run.resources.subscription_id
        run.resources.service_manager_id = result.service_manager_id or run.resources.service_manager_id
        run.resources.service_catalog_region_id = result.region or run.resources.service_catalog_region_id
        failed = result.error is not None or any(p.status == FAILED for p in result.phases)
        if failed:
            self._set(run, RunStatus.RETRYABLE_FAILURE)
            self._emit(run.run_id, run.current_phase, "step.failed", result.error or f"{label} failed")
        elif dry_run:
            self._set(run, RunStatus.READY, WorkflowPhase.PREFLIGHT)
            self._emit(run.run_id, WorkflowPhase.PREFLIGHT, "step.completed", f"{label} completed — no writes made")
        else:
            after = next_enabled_phase(run.mode, run.selected_steps, "greenlake")
            self._set(run, RunStatus.READY, after)
            self._emit(
                run.run_id,
                WorkflowPhase.GL_VERIFY_DEVICE,
                "step.completed",
                f"{label} completed — {_next_hint(after)}",
            )

    # ------------------------------------------------------------------ step B: cloudinit

    def start_cloudinit(self, run_id: str, *, cloudinit_url: str | None = None, auto_submit: bool = True) -> RunRecord:
        run, item = self.get_run(run_id), self.get_work_item(run_id)
        if cloudinit_url:
            # The link-local URL changes per boot — the operator pastes the fresh one at runtime.
            item = item.model_copy(update={"cloudinit_url": cloudinit_url})
            self.store.save_work_item(run_id, item)
        self._spawn(run_id, self._run_cloudinit(run, item, auto_submit))
        return run

    async def _run_cloudinit(self, run: RunRecord, item: ArrayWorkItem, auto_submit: bool) -> None:
        self._set(run, RunStatus.RUNNING, WorkflowPhase.CLOUDINIT_CONNECT)
        self._emit(
            run.run_id,
            WorkflowPhase.CLOUDINIT_CONNECT,
            "step.started",
            f"Cloud Connectivity Wizard started -> {item.cloudinit_url}",
        )
        review_ready = False
        refused = False
        last_error: str | None = None

        def on_status(message: str) -> None:
            nonlocal review_ready, refused, last_error
            if message.startswith("error:"):
                last_error = message[len("error:") :].strip()
            elif message == "review_ready":
                review_ready = True
                self._set(run, RunStatus.WAITING_FOR_OPERATOR)
                self._emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "operator.review_ready",
                    "Wizard filled — review the values in the browser and click Submit",
                )
            elif message == "reasserted":
                self._emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    "Network values had decayed to the link-local default — re-filled and re-verifying before submit",
                )
            elif message == "applying":
                self._emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    "Network values verified on the Review screen — applying configuration and connecting the array…",
                )
            elif message == "refused":
                refused = True

        adapter = self._cloudinit_factory(self._current_settings(), on_status)
        result = await adapter.run(item, run_id=run.run_id, auto_submit=auto_submit)

        if result in (BrowserResultStatus.SUCCEEDED, BrowserResultStatus.ALREADY_DONE):
            after = next_enabled_phase(run.mode, run.selected_steps, "cloudinit")
            self._set(run, RunStatus.READY, after)
            self._emit(run.run_id, WorkflowPhase.CLOUDINIT_CONNECT, "step.completed", f"Array connected — {_next_hint(after)}")
        elif result == BrowserResultStatus.WAITING_FOR_OPERATOR and review_ready:
            self._set(run, RunStatus.WAITING_FOR_OPERATOR)
            self._emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.stalled",
                "Submit was not detected (browser closed or review window expired) — re-run the step to retry",
            )
        elif refused:
            # The guard re-filled the Network fields but they kept decaying to link-local, so it
            # never clicked Submit. Nothing was applied — safe to just retry.
            self._set(run, RunStatus.RETRYABLE_FAILURE)
            self._emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.failed",
                "Refused to submit: the wizard kept reverting the Network IP to its link-local "
                "default, so nothing was applied. Re-run to retry.",
            )
        elif result == BrowserResultStatus.FAILED_TERMINAL:
            self._set(run, RunStatus.TERMINAL_FAILURE)
            self._emit(run.run_id, WorkflowPhase.CLOUDINIT_CONNECT, "step.failed", "Invalid cloudinit URL (must be https://169.254.x.x/cloudinit)")
        else:
            self._set(run, RunStatus.RETRYABLE_FAILURE)
            self._emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.failed",
                last_error or "Browser automation did not complete — check the artifact screenshot and retry",
            )

    # ------------------------------------------------------------------ step C: DSCC

    def start_dscc(self, run_id: str, *, cdp_url: str) -> RunRecord:
        run, item = self.get_run(run_id), self.get_work_item(run_id)
        self._spawn(run_id, self._run_dscc(run, item, cdp_url))
        return run

    async def _run_dscc(self, run: RunRecord, item: ArrayWorkItem, cdp_url: str) -> None:
        self._set(run, RunStatus.RUNNING, WorkflowPhase.DSCC_SETUP_SYSTEM)
        self._emit(run.run_id, WorkflowPhase.DSCC_SETUP_SYSTEM, "step.started", "DSCC Set Up System wizard started")

        adapter = self._dscc_factory(self._current_settings(), cdp_url)
        result = await adapter.run(item, run_id=run.run_id)

        if result == BrowserResultStatus.WAITING_FOR_OPERATOR:
            self._set(run, RunStatus.WAITING_FOR_OPERATOR)
            self._emit(
                run.run_id,
                WorkflowPhase.DSCC_SETUP_SYSTEM,
                "operator.credentials_ready",
                "Filled through System — add the Credentials secret in the browser, Continue, "
                "review, Submit, then mark the run complete",
            )
        elif result == BrowserResultStatus.FAILED_TERMINAL:
            self._set(run, RunStatus.TERMINAL_FAILURE)
            self._emit(run.run_id, WorkflowPhase.DSCC_SETUP_SYSTEM, "step.failed", "Work item is missing required DSCC fields — fix it and re-run")
        else:
            self._set(run, RunStatus.RETRYABLE_FAILURE)
            self._emit(
                run.run_id,
                WorkflowPhase.DSCC_SETUP_SYSTEM,
                "step.failed",
                "Could not drive the DSCC browser — make sure the debug Chrome is open on the "
                "Set Up System wizard (Welcome), then retry",
            )

    # ------------------------------------------------------------------ post-init verification

    def start_verify(self, run_id: str, *, username: str, password: str) -> RunRecord:
        run, item = self.get_run(run_id), self.get_work_item(run_id)
        self._spawn(run_id, self._run_verify(run, item, username, password))
        return run

    async def _run_verify(self, run: RunRecord, item: ArrayWorkItem, username: str, password: str) -> None:
        # The run is already COMPLETE; verification is a read-only confidence check and must NEVER
        # change the run status — a failure here can't un-succeed the onboarding.
        self._emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "step.started", "Verifying the array configuration over SSH…")
        try:
            report = await asyncio.to_thread(self._verify_fn, item, username, password)
        except Exception as exc:  # noqa: BLE001 - never propagate (the guard would mark the run failed)
            self._emit(
                run.run_id,
                WorkflowPhase.CONFIG_VERIFY,
                "verify.failed",
                f"Verification error: {type(exc).__name__}: {str(exc)[:200]}",
            )
            return
        if not report.reachable:
            self._emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "verify.failed", report.error or "Could not reach the array over SSH.")
            return
        self._emit(
            run.run_id,
            WorkflowPhase.CONFIG_VERIFY,
            "verify.completed",
            f"Verified the array — {report.passed} OK, {report.mismatches} mismatch(es), "
            f"{report.health_total} health issue(s).",
            data={"report": report.model_dump(mode="json")},
        )

    # ------------------------------------------------------------------ internals

    def _spawn(self, run_id: str, coro) -> None:
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
                self._set(run, RunStatus.RETRYABLE_FAILURE)
            self._emit(
                run_id,
                run.current_phase if run else WorkflowPhase.NOT_STARTED,
                "step.crashed",
                f"{type(exc).__name__}: {str(exc)[:300]}",
            )

    def _set(self, run: RunRecord, status: RunStatus, phase: WorkflowPhase | None = None) -> None:
        run.status = status
        if phase is not None:
            run.current_phase = phase
        run.updated_at = datetime.now(UTC)
        self.store.upsert_run(run)

    def _emit(
        self, run_id: str, phase: WorkflowPhase, event_type: str, message: str, data: dict | None = None
    ) -> None:
        event = RunEvent(run_id=run_id, phase=phase, event_type=event_type, message=message, data=data or {})
        self.store.append_event(event)
        self.events.publish_sync(event)
