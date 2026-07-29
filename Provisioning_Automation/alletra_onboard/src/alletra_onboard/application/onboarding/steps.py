"""OnboardingSteps — the A -> B -> C init chain as a step service over the RunCoordinator.

A (GreenLake registration) runs the REST orchestrator; B (Cloud Connectivity) and C (DSCC Set Up
System) drive Playwright wizards. Each start_* spawns a guarded background task; the flow is
operator-gated (B waits for the operator's Submit, C stops at the credential gate).
"""

from __future__ import annotations

from typing import Any, Callable

from alletra_onboard.adapters.browser.cloudinit_wizard import CloudinitWizardAdapter
from alletra_onboard.adapters.browser.dscc_setup import DsccSetupAdapter
from alletra_onboard.application.onboarding.greenlake_provision import (
    FAILED,
    WARNING,
    build_provisioning_service,
)
from alletra_onboard.application.runs.coordinator import RunCoordinator
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    BrowserResultStatus,
    RunRecord,
    RunStatus,
    WorkflowPhase,
)
from alletra_onboard.domain.workflow import next_enabled_phase


def _next_hint(phase: WorkflowPhase) -> str:
    """A human hint for what comes after an init step, given the selection-aware next phase."""
    return {
        WorkflowPhase.CLOUDINIT_CONNECT: "next: Cloud Connectivity Wizard",
        WorkflowPhase.DSCC_SETUP_SYSTEM: "next: DSCC Setup",
        WorkflowPhase.STORAGE_DISCOVER: "next: storage discovery",
        WorkflowPhase.COMPLETE: "no further onboarding steps selected",
    }.get(phase, f"next: {phase.value}")


def default_provision_factory(settings: Settings, progress: Callable) -> Any:
    return build_provisioning_service(settings, progress=progress)


def default_cloudinit_factory(settings: Settings, on_status: Callable[[str], None]) -> Any:
    # Launch mode: the product flow opens its own browser at the pasted cloudinit URL.
    return CloudinitWizardAdapter(
        headless=settings.browser_headless,
        cdp_url=None,
        artifact_dir=settings.artifact_dir,
        on_status=on_status,
    )


def default_dscc_factory(settings: Settings, cdp_url: str) -> Any:
    return DsccSetupAdapter(cdp_url=cdp_url, artifact_dir=settings.artifact_dir)


class OnboardingSteps:
    def __init__(
        self,
        coord: RunCoordinator,
        *,
        provision_factory: Callable = default_provision_factory,
        cloudinit_factory: Callable = default_cloudinit_factory,
        dscc_factory: Callable = default_dscc_factory,
    ) -> None:
        self._coord = coord
        self._provision_factory = provision_factory
        self._cloudinit_factory = cloudinit_factory
        self._dscc_factory = dscc_factory

    # ------------------------------------------------------------------ step A: GreenLake

    def start_provision(self, run_id: str, *, dry_run: bool = False) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        coord.spawn(run_id, self._run_provision(run, item, dry_run))
        return run

    async def _run_provision(self, run: RunRecord, item: ArrayWorkItem, dry_run: bool) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.GL_DISCOVER_SERVICE)
        label = "GreenLake provisioning (dry-run)" if dry_run else "GreenLake provisioning"
        coord.emit(run.run_id, WorkflowPhase.GL_DISCOVER_SERVICE, "step.started", f"{label} started")

        def progress(phase: WorkflowPhase, message: str) -> None:
            run.current_phase = phase
            coord.store.upsert_run(run)
            coord.emit(run.run_id, phase, "phase.progress", message)

        service = self._provision_factory(coord.current_settings(), progress)
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
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE)
            coord.emit(run.run_id, run.current_phase, "step.failed", result.error or f"{label} failed")
        elif dry_run:
            coord.set_state(run, RunStatus.READY, WorkflowPhase.PREFLIGHT)
            coord.emit(run.run_id, WorkflowPhase.PREFLIGHT, "step.completed", f"{label} completed — no writes made")
        else:
            after = next_enabled_phase(run.mode, run.selected_steps, "greenlake")
            coord.set_state(run, RunStatus.READY, after)
            coord.emit(
                run.run_id,
                WorkflowPhase.GL_VERIFY_DEVICE,
                "step.completed",
                f"{label} completed — {_next_hint(after)}",
            )

    # ------------------------------------------------------------------ step B: cloudinit

    def start_cloudinit(self, run_id: str, *, cloudinit_url: str | None = None, auto_submit: bool = True) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        if cloudinit_url:
            # The link-local URL changes per boot — the operator pastes the fresh one at runtime.
            item = item.model_copy(update={"cloudinit_url": cloudinit_url})
            coord.store.save_work_item(run_id, item)
        coord.spawn(run_id, self._run_cloudinit(run, item, auto_submit))
        return run

    async def _run_cloudinit(self, run: RunRecord, item: ArrayWorkItem, auto_submit: bool) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.CLOUDINIT_CONNECT)
        coord.emit(
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
            elif message.startswith("initializing"):
                # The array is still booting its own system; the wizard has no form yet. Emitted
                # about once a minute so the operator sees the wait is deliberate, not a hang.
                _, _, seconds = message.partition(":")
                minutes = int(seconds or 0) // 60
                waited = f" (waiting {minutes} min so far)" if minutes else ""
                coord.emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    f"The array is still initializing its system — the wizard is not ready yet{waited}.",
                )
            elif message.startswith("wizard_pending"):
                # The page is up but no known wizard screen has rendered yet.
                _, _, seconds = message.partition(":")
                minutes = max(1, int(seconds or 0) // 60)
                coord.emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    f"Waiting for the wizard interface to load ({minutes} min so far)…",
                )
            elif message == "review_ready":
                review_ready = True
                coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR)
                coord.emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "operator.review_ready",
                    "Wizard filled — review the values in the browser and click Submit",
                )
            elif message == "reasserted":
                coord.emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    "Network values had decayed to the link-local default — re-filled and re-verifying before submit",
                )
            elif message == "applying":
                coord.emit(
                    run.run_id,
                    WorkflowPhase.CLOUDINIT_CONNECT,
                    "phase.progress",
                    "Network values verified on the Review screen — applying configuration and connecting the array…",
                )
            elif message == "refused":
                refused = True

        adapter = self._cloudinit_factory(coord.current_settings(), on_status)
        result = await adapter.run(item, run_id=run.run_id, auto_submit=auto_submit)

        if result in (BrowserResultStatus.SUCCEEDED, BrowserResultStatus.ALREADY_DONE):
            after = next_enabled_phase(run.mode, run.selected_steps, "cloudinit")
            coord.set_state(run, RunStatus.READY, after)
            coord.emit(run.run_id, WorkflowPhase.CLOUDINIT_CONNECT, "step.completed", f"Array connected — {_next_hint(after)}")
        elif result == BrowserResultStatus.WAITING_FOR_OPERATOR and review_ready:
            coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR)
            coord.emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.stalled",
                "Submit was not detected (browser closed or review window expired) — re-run the step to retry",
            )
        elif refused:
            # The guard re-filled the Network fields but they kept decaying to link-local, so it
            # never clicked Submit. Nothing was applied — safe to just retry.
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE)
            coord.emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.failed",
                "Refused to submit: the wizard kept reverting the Network IP to its link-local "
                "default, so nothing was applied. Re-run to retry.",
            )
        elif result == BrowserResultStatus.FAILED_TERMINAL:
            coord.set_state(run, RunStatus.TERMINAL_FAILURE)
            coord.emit(run.run_id, WorkflowPhase.CLOUDINIT_CONNECT, "step.failed", "Invalid cloudinit URL (must be https://169.254.x.x/cloudinit)")
        else:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE)
            coord.emit(
                run.run_id,
                WorkflowPhase.CLOUDINIT_CONNECT,
                "step.failed",
                last_error or "Browser automation did not complete — check the artifact screenshot and retry",
            )

    # ------------------------------------------------------------------ step C: DSCC

    def start_dscc(self, run_id: str, *, cdp_url: str) -> RunRecord:
        coord = self._coord
        run, item = coord.get_run(run_id), coord.get_work_item(run_id)
        coord.spawn(run_id, self._run_dscc(run, item, cdp_url))
        return run

    async def _run_dscc(self, run: RunRecord, item: ArrayWorkItem, cdp_url: str) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.DSCC_SETUP_SYSTEM)
        coord.emit(run.run_id, WorkflowPhase.DSCC_SETUP_SYSTEM, "step.started", "DSCC Set Up System wizard started")

        adapter = self._dscc_factory(coord.current_settings(), cdp_url)
        result = await adapter.run(item, run_id=run.run_id)

        if result == BrowserResultStatus.WAITING_FOR_OPERATOR:
            coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR)
            coord.emit(
                run.run_id,
                WorkflowPhase.DSCC_SETUP_SYSTEM,
                "operator.credentials_ready",
                "Filled through System — add the Credentials secret in the browser, Continue, "
                "review, Submit, then mark the run complete",
            )
        elif result == BrowserResultStatus.FAILED_TERMINAL:
            coord.set_state(run, RunStatus.TERMINAL_FAILURE)
            coord.emit(run.run_id, WorkflowPhase.DSCC_SETUP_SYSTEM, "step.failed", "Work item is missing required DSCC fields — fix it and re-run")
        else:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE)
            coord.emit(
                run.run_id,
                WorkflowPhase.DSCC_SETUP_SYSTEM,
                "step.failed",
                "Could not drive the DSCC browser — make sure the debug Chrome is open on the "
                "Set Up System wizard (Welcome), then retry",
            )
