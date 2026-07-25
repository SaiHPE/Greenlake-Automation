"""OnboardingService — the composition root the API drives.

A thin façade that wires the RunCoordinator (run lifecycle + step infrastructure) and the four
per-context step services, then delegates one-to-one. Step logic does NOT live here:

    application/runs/coordinator.py    run lifecycle, guarded spawn, set_state/emit (store + SSE)
    application/onboarding/steps.py    A GreenLake -> B Cloud Connectivity -> C DSCC
    application/storage/steps.py       discovery + zoning verify/plan; provisioning tiers + builder
    application/documents/steps.py     post-init verification + the as-built document

The flow is operator-gated, so the service exposes one start_* per step instead of a
fire-and-forget pipeline (see the step services for each step's contract).
"""

from __future__ import annotations

from typing import Callable

from alletra_onboard.application.documents.steps import DocumentSteps
from alletra_onboard.application.event_bus import InMemoryEventBus
from alletra_onboard.application.onboarding.steps import (
    OnboardingSteps,
    default_cloudinit_factory,
    default_dscc_factory,
    default_provision_factory,
)
from alletra_onboard.application.runs.coordinator import (
    PendingSheetNotFoundError,
    RunBusyError,
    RunCoordinator,
    RunNotFoundError,
    StepPreconditionError,
)
from alletra_onboard.application.storage.steps import DiscoveryZoningSteps, ProvisioningSteps
from alletra_onboard.application.verification import verify
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, RunEvent, RunMode, RunRecord
from alletra_onboard.domain.ports import RunStore
from alletra_onboard.domain.storage import (
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningIntent,
    ProvisioningObjects,
)

__all__ = [
    "OnboardingService",
    "RunNotFoundError",
    "RunBusyError",
    "StepPreconditionError",
    "PendingSheetNotFoundError",
]


class OnboardingService:
    def __init__(
        self,
        settings: Settings,
        store: RunStore,
        events: InMemoryEventBus,
        *,
        provision_factory: Callable = default_provision_factory,
        cloudinit_factory: Callable = default_cloudinit_factory,
        dscc_factory: Callable = default_dscc_factory,
        verify_fn: Callable = verify,
    ) -> None:
        self.settings = settings
        self.store = store
        self.events = events
        self.coordinator = RunCoordinator(settings, store, events)
        self.onboarding = OnboardingSteps(
            self.coordinator,
            provision_factory=provision_factory,
            cloudinit_factory=cloudinit_factory,
            dscc_factory=dscc_factory,
        )
        self.discovery_zoning = DiscoveryZoningSteps(self.coordinator)
        self.provisioning = ProvisioningSteps(self.coordinator, self.discovery_zoning)
        self.documents = DocumentSteps(self.coordinator, verify_fn=verify_fn)

    # ------------------------------------------------------------------ run lifecycle (coordinator)

    def create_run(
        self,
        item: ArrayWorkItem,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
        provisioning_intent: ProvisioningIntent | None = None,
    ) -> RunRecord:
        return self.coordinator.create_run(
            item, mode=mode, selected_steps=selected_steps, provisioning_intent=provisioning_intent
        )

    def stash_pending_sheet(
        self, work_item: ArrayWorkItem, provisioning_intent: ProvisioningIntent | None
    ) -> str:
        return self.coordinator.stash_pending_sheet(work_item, provisioning_intent)

    def create_run_from_pending(
        self,
        token: str,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
    ) -> RunRecord:
        return self.coordinator.create_run_from_pending(token, mode=mode, selected_steps=selected_steps)

    def get_provisioning_intent(self, run_id: str) -> ProvisioningIntent:
        return self.coordinator.get_provisioning_intent(run_id)

    def get_run(self, run_id: str) -> RunRecord:
        return self.coordinator.get_run(run_id)

    def get_work_item(self, run_id: str) -> ArrayWorkItem:
        return self.coordinator.get_work_item(run_id)

    def list_runs(self) -> list[RunRecord]:
        return self.coordinator.list_runs()

    def list_events(self, run_id: str) -> list[RunEvent]:
        return self.coordinator.list_events(run_id)

    def mark_complete(self, run_id: str) -> RunRecord:
        return self.coordinator.mark_complete(run_id)

    async def wait(self, run_id: str) -> None:
        await self.coordinator.wait(run_id)

    # ------------------------------------------------------------------ onboarding steps A/B/C

    def start_provision(self, run_id: str, *, dry_run: bool = False) -> RunRecord:
        return self.onboarding.start_provision(run_id, dry_run=dry_run)

    def start_cloudinit(self, run_id: str, *, cloudinit_url: str | None = None, auto_submit: bool = True) -> RunRecord:
        return self.onboarding.start_cloudinit(run_id, cloudinit_url=cloudinit_url, auto_submit=auto_submit)

    def start_dscc(self, run_id: str, *, cdp_url: str) -> RunRecord:
        return self.onboarding.start_dscc(run_id, cdp_url=cdp_url)

    # ------------------------------------------------------------------ discovery + zoning

    def start_discover(self, run_id: str) -> RunRecord:
        return self.discovery_zoning.start_discover(run_id)

    def start_zoning_preview(self, run_id: str) -> RunRecord:
        return self.discovery_zoning.start_zoning_preview(run_id)

    def start_zoning_plan(self, run_id: str) -> RunRecord:
        return self.discovery_zoning.start_zoning_plan(run_id)

    # ------------------------------------------------------------------ provisioning tiers + builder

    def start_storage_preview(self, run_id: str) -> RunRecord:
        return self.provisioning.start_storage_preview(run_id)

    def start_storage_apply(self, run_id: str) -> RunRecord:
        return self.provisioning.start_storage_apply(run_id)

    def start_path_verify(self, run_id: str) -> RunRecord:
        return self.provisioning.start_path_verify(run_id)

    def get_storage_objects(self, run_id: str) -> ProvisioningObjects:
        return self.provisioning.get_storage_objects(run_id)

    def set_provisioning_builder(self, run_id: str, builder: ProvisioningBuilder) -> ProvisioningComposition:
        return self.provisioning.set_provisioning_builder(run_id, builder)

    # ------------------------------------------------------------------ documents (verify + as-built)

    def start_verify(self, run_id: str, *, username: str, password: str) -> RunRecord:
        return self.documents.start_verify(run_id, username=username, password=password)

    def start_asbuilt(self, run_id: str, *, username: str, password: str, customer: str = "", site: str = "") -> RunRecord:
        return self.documents.start_asbuilt(run_id, username=username, password=password, customer=customer, site=site)

    def get_asbuilt(self, run_id: str) -> bytes | None:
        return self.documents.get_asbuilt(run_id)

    # ------------------------------------------------------------------ test seam

    @property
    def _discovery(self):
        """The per-run discovery artifacts (owned by the DiscoveryZoning service) — exposed so tests
        can seed discovery without running it."""
        return self.discovery_zoning._discovery
