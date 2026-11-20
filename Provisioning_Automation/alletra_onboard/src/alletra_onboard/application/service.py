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

from collections.abc import Callable

from alletra_onboard.application.documents.steps import DocumentSteps
from alletra_onboard.application.documents.verification import verify
from alletra_onboard.application.onboarding.clients import (
    default_cloudinit_factory,
    default_dscc_factory,
)
from alletra_onboard.application.onboarding.steps import (
    OnboardingSteps,
    default_provision_factory,
)
from alletra_onboard.application.platform.init_sheet import parse_workbook_bytes
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.provisioning.steps import (
    ArrayPortsSteps,
    DiscoveryZoningSteps,
    ProvisioningSteps,
)
from alletra_onboard.application.replication.steps import ReplicationSteps
from alletra_onboard.application.runs.console import ConsoleService
from alletra_onboard.application.runs.coordinator import (
    DevicePinNotFoundError,
    PendingSheetNotFoundError,
    RunBusyError,
    RunCoordinator,
    RunNotFoundError,
    StepPreconditionError,
)
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.snapshots.steps import SnapshotSteps
from alletra_onboard.config import Settings
from alletra_onboard.domain import events
from alletra_onboard.domain.models import (
    ArrayCredentialInfo,
    ArrayWorkItem,
    RunEvent,
    RunMode,
    RunRecord,
    WorkflowPhase,
)
from alletra_onboard.domain.ports import RunStore
from alletra_onboard.domain.provisioning import (
    PreflightReport,
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningIntent,
    ProvisioningObjects,
)
from alletra_onboard.domain.trust import DevicePinInfo, TrustKind

__all__ = [
    "DevicePinNotFoundError",
    "OnboardingService",
    "PendingSheetNotFoundError",
    "RunBusyError",
    "RunNotFoundError",
    "StepPreconditionError",
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
        self.ports = ArrayPortsSteps(self.coordinator)
        self.replication = ReplicationSteps(self.coordinator)
        self.snapshots = SnapshotSteps(self.coordinator)
        self.documents = DocumentSteps(self.coordinator, verify_fn=verify_fn)
        self.console = ConsoleService(self.coordinator, cli_factory=make_array_cli)
        self.coordinator.recover_interrupted_applies()

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
        self, work_item: ArrayWorkItem, provisioning_intent: ProvisioningIntent | None,
        workbook: bytes | None = None,
    ) -> str:
        return self.coordinator.stash_pending_sheet(work_item, provisioning_intent, workbook)

    def create_run_from_pending(
        self,
        token: str,
        *,
        mode: RunMode = RunMode.FULL_ONBOARDING,
        selected_steps: list[str] | None = None,
    ) -> RunRecord:
        # The upload listed problems in some tabs (parse_upload): check the sheet again for the chosen
        # steps. A problem in a tab they use refuses the run (ValueError) and the hold stays for another mode.
        checked_intent = None
        workbook = self.coordinator.pending_sheet_workbook(token)
        if workbook is not None:
            checked_intent = parse_workbook_bytes(workbook, mode=mode, selected_steps=selected_steps).provisioning_intent
        return self.coordinator.create_run_from_pending(
            token, mode=mode, selected_steps=selected_steps, checked_intent=checked_intent
        )

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

    def record_zoning_render(
        self, run_id: str, *, commands: dict[str, list[str]], skipped: dict[str, list[str]],
        aliases: dict[str, str], selected_pairs: list[tuple[str, str]],
        peer_commands: dict[str, list[str]] | None = None,
    ) -> None:
        """Put the generated zoning command set on the run's record (SPEC-002 R4), with the peer-port
        block (SPEC-025 R7) when there is one. Raises RunNotFoundError for an unknown run; never
        touches the run's status."""
        self.coordinator.get_run(run_id)
        peer_commands = peer_commands or {}
        total = sum(len(c) for c in commands.values()) + sum(len(c) for c in peer_commands.values())
        fabrics = sorted({f for f, c in [*commands.items(), *peer_commands.items()] if c})
        self.coordinator.emit(
            run_id, WorkflowPhase.STORAGE_ZONING, events.ZONING_RENDERED,
            f"Zoning command set generated — {total} command(s) for {', '.join(fabrics) or 'no fabric'}.",
            events.ZoningRenderedData(commands=commands, skipped=skipped, aliases=aliases,
                                      selected_pairs=selected_pairs, peer_commands=peer_commands),
        )

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

    def start_ports_preview(self, run_id: str) -> RunRecord:
        return self.ports.start_ports_preview(run_id)

    def get_ports(self, run_id: str) -> dict:
        """The Array ports step's sheet rows, and whether each plan last shown is still held (LESSONS 6)."""
        return {"iscsi_network": self.ports.iscsi_rows(run_id),
                "iscsi_plan_held": self.ports.held_iscsi_plan(run_id) is not None,
                "peer_ports": self.ports.peer_rows(run_id),
                "peer_plan_held": self.ports.held_peer_plan(run_id) is not None}

    def start_storage_preview(self, run_id: str) -> RunRecord:
        return self.provisioning.start_storage_preview(run_id)

    def start_storage_apply(self, run_id: str, *, approved_plan: str | None) -> RunRecord:
        return self.provisioning.start_storage_apply(run_id, approved_plan=approved_plan)

    def start_path_verify(self, run_id: str) -> RunRecord:
        return self.provisioning.start_path_verify(run_id)

    def get_storage_preflight(self, run_id: str) -> PreflightReport:
        return self.provisioning.get_storage_preflight(run_id)

    def get_storage_objects(self, run_id: str) -> ProvisioningObjects:
        return self.provisioning.get_storage_objects(run_id)

    def set_provisioning_builder(self, run_id: str, builder: ProvisioningBuilder) -> ProvisioningComposition:
        return self.provisioning.set_provisioning_builder(run_id, builder)

    # ------------------------------------------------------------------ replication (SPEC-016)

    def start_replication_preview(self, run_id: str) -> RunRecord:
        return self.replication.start_replication_preview(run_id)

    def start_replication_apply(self, run_id: str, *, approved_plan: str | None, accept_latency: bool = False) -> RunRecord:
        return self.replication.start_replication_apply(run_id, approved_plan=approved_plan, accept_latency=accept_latency)

    def start_link_check(self, run_id: str, *, duration_s: int) -> RunRecord:
        return self.replication.start_link_check(run_id, duration_s=duration_s)

    def start_replication_verify(self, run_id: str) -> RunRecord:
        return self.replication.start_replication_verify(run_id)

    def start_failover_test(
        self, run_id: str, *, group: str | None = None, confirm: str | None = None, authorised: bool = False,
    ) -> RunRecord:
        return self.replication.start_failover_test(run_id, group=group, confirm=confirm, authorised=authorised)

    # ------------------------------------------------------------------ snapshots (SPEC-023)

    def get_snapshots(self, run_id: str) -> dict:
        return self.snapshots.tab(run_id)

    def start_snapshots_preview(self, run_id: str) -> RunRecord:
        return self.snapshots.start_snapshots_preview(run_id)

    def start_snapshots_apply(self, run_id: str, *, approved_plan: str | None) -> RunRecord:
        return self.snapshots.start_snapshots_apply(run_id, approved_plan=approved_plan)

    def start_snapshots_verify(self, run_id: str) -> RunRecord:
        return self.snapshots.start_snapshots_verify(run_id)

    # ------------------------------------------------------------------ documents (verify + as-built)

    def start_verify(self, run_id: str, *, username: str | None = None, password: str | None = None) -> RunRecord:
        return self.documents.start_verify(run_id, username=username, password=password)

    def start_asbuilt(
        self, run_id: str, *, username: str | None = None, password: str | None = None, customer: str = "",
        site: str = "", application_workload: str = "", purpose: str = "",
    ) -> RunRecord:
        return self.documents.start_asbuilt(
            run_id, username=username, password=password, customer=customer, site=site,
            application_workload=application_workload, purpose=purpose,
        )

    def array_credential_info(self, run_id: str) -> ArrayCredentialInfo:
        """ADR 0013 / SPEC-008 R3: what the UI may know about the run's array credential."""
        return self.coordinator.array_credential(run_id).public()

    def get_asbuilt(self, run_id: str) -> bytes | None:
        return self.documents.get_asbuilt(run_id)

    # ------------------------------------------------------------------ device trust (ADR 0026)

    def trusted_devices(self, run_id: str) -> list[DevicePinInfo]:
        return [DevicePinInfo.of(pin) for pin in self.coordinator.device_pins(run_id)]

    def device_ca_bundle(self) -> str | None:
        return self.coordinator.device_ca_bundle()

    def retrust_device(self, run_id: str, *, kind: TrustKind, host: str, port: int, fingerprint: str) -> DevicePinInfo:
        return DevicePinInfo.of(self.coordinator.retrust_device(
            run_id, kind=kind, host=host, port=port, fingerprint=fingerprint))

    # ------------------------------------------------------------------ test seam

    @property
    def _discovery(self):
        """The per-run discovery artifacts (owned by the DiscoveryZoning service) — exposed so tests
        can seed discovery without running it."""
        return self.discovery_zoning.discovery
