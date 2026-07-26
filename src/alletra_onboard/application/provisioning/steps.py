"""Step services for the storage-provisioning context, over the RunCoordinator.

Two services: DiscoveryZoningSteps (discovery + zoning verify/plan — the shared read-only
foundation) and ProvisioningSteps (tier-1 preview/apply, the Stage-2 builder, tier-2 path
verification). Provisioning CONSUMES discovery/zoning (ADR 0010), so ProvisioningSteps depends on
DiscoveryZoningSteps for the per-run discovery artifact.

The storage functions are called through their modules (storage_discovery.discover, …) so tests can
monkeypatch the modules themselves.
"""

from __future__ import annotations

import asyncio

from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.application.provisioning import discovery as storage_discovery
from alletra_onboard.application.provisioning import path_verify as storage_path_verify
from alletra_onboard.application.provisioning import storage_provision
from alletra_onboard.application.provisioning import zoning as storage_zoning
from alletra_onboard.application.provisioning import zoning_plan as storage_zoning_plan
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.provisioning import (
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningObjects,
    ProvisioningPlan,
)


class DiscoveryZoningSteps:
    """Discovery + SAN-zoning verify/plan — read-only reads of array, vCenter and both switches."""

    def __init__(self, coord: RunCoordinator) -> None:
        self._coord = coord
        # Per-run discovery cache over the durable run_artifacts store (C7): the store is the truth
        # (a server restart mid-engagement must not force re-discovery), the dict avoids re-parsing.
        self._discovery: dict[str, DiscoveryReport] = {}

    def current_discovery(self, run_id: str) -> DiscoveryReport | None:
        """The discovery in effect, or None. Unlike require_discovery this never raises — callers use
        it to detect that discovery has been re-run since they last read it."""
        try:
            return self.require_discovery(run_id)
        except StepPreconditionError:
            return None

    def require_discovery(self, run_id: str) -> DiscoveryReport:
        report = self._discovery.get(run_id)
        if report is None:
            raw = self._coord.store.load_artifact(run_id, "discovery")
            if raw is not None:
                try:
                    report = DiscoveryReport.model_validate_json(raw)
                    self._discovery[run_id] = report
                except Exception:  # noqa: BLE001
                    # A stored report the current model can no longer read (an upgrade changed the
                    # schema, or the row is damaged). Treat it as absent so the operator can simply
                    # re-run discovery, instead of every step failing with a 500 and no way out.
                    report = None
        if report is None:
            raise StepPreconditionError("run discovery first — it provides the ports/HBAs zoning and provisioning need")
        return report

    def start_discover(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        coord.spawn(run_id, self._run_discover(run, intent))
        return run

    async def _run_discover(self, run: RunRecord, intent) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_DISCOVER)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_DISCOVER, "step.started", "Discovering array ports, ESXi HBAs and fabric logins…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            # discover() runs in a worker thread; the SSE fan-out uses asyncio.Queues (not thread-safe),
            # so marshal each progress event back onto the event loop.
            loop.call_soon_threadsafe(
                coord.emit, run.run_id, WorkflowPhase.STORAGE_DISCOVER, "phase.progress", message
            )

        report = await asyncio.to_thread(storage_discovery.discover, intent, progress=progress)
        self._discovery[run.run_id] = report
        try:
            coord.store.save_artifact(run.run_id, "discovery", report.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001 - discovery succeeded; failing to cache it must not fail the step.
            pass
        coord.set_state(run, RunStatus.READY, WorkflowPhase.STORAGE_DISCOVER)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_DISCOVER, "discover.completed",
            f"Discovery complete — {len(report.array_ports)} array port(s), {len(report.host_hbas)} host HBA(s)"
            + (f"; {len(report.notes)} note(s)" if report.notes else ""),
            data={"report": report.model_dump(mode="json")},
        )

    def start_zoning_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self.require_discovery(run_id)
        coord.spawn(run_id, self._run_zoning_preview(run, intent, discovery))
        return run

    async def _run_zoning_preview(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_ZONING)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_ZONING, "step.started", "Verifying SAN zoning on both fabrics…")
        report = await asyncio.to_thread(storage_zoning.build_report, intent, discovery)
        coord.set_state(run, RunStatus.READY if report.proper else RunStatus.WAITING_FOR_OPERATOR, WorkflowPhase.STORAGE_ZONING)
        missing = sum(1 for z in report.expected if not z.present)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_ZONING,
            "zoning.proper" if report.proper else "zoning.previewed",
            "Zoning is correct on both fabrics." if report.proper
            else f"Zoning needs {missing} zone(s) — the plan lists the exact commands for the SAN team to "
            "apply on the switch (the tool makes no switch writes); re-verify after they are applied.",
            data={"report": report.model_dump(mode="json")},
        )

    def start_zoning_plan(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self.require_discovery(run_id)
        coord.spawn(run_id, self._run_zoning_plan(run, intent, discovery))
        return run

    async def _run_zoning_plan(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_ZONING)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_ZONING, "step.started",
                   "Reading both fabric switches (read-only) to build the zoning plan…")
        plan = await asyncio.to_thread(storage_zoning_plan.build_zoning_plan, intent, discovery)
        pairs = sum(len(f.pairs) for f in plan.fabrics)
        coord.set_state(run, RunStatus.READY, WorkflowPhase.STORAGE_ZONING)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_ZONING, "zoning.plan",
            f"Zoning plan: {pairs} single-initiator-single-target zone(s) across the fabrics"
            + (f"; {len(plan.offline_hosts)} host WWPN(s) offline (cable + power)" if plan.offline_hosts else "")
            + (f"; {len(plan.notes)} note(s)" if plan.notes else ""),
            data={"plan": plan.model_dump(mode="json")},
        )


class ProvisioningSteps:
    """Tier-1 create (preview/apply), the Stage-2 dropdown builder, and tier-2 path verification."""

    def __init__(self, coord: RunCoordinator, discovery_steps: DiscoveryZoningSteps) -> None:
        self._coord = coord
        self._discovery_steps = discovery_steps
        # The previewed plan, per run — the gate that stops the only step which writes to the array
        # running against something the operator never saw.
        #
        # Deliberately NOT durable, unlike the discovery report and the as-built document. This is an
        # approval, not a result: it must not outlive the process, and it is discarded the moment its
        # inputs change (a re-run of discovery, or an edit to the composition). Persisting it would
        # let a plan approved before a restart authorise an apply of a different composition.
        # Held with the exact discovery it was built from, so a re-run of discovery withdraws it too.
        self._plan: dict[str, tuple[ProvisioningPlan, DiscoveryReport]] = {}

    def invalidate_plan(self, run_id: str) -> None:
        """Withdraw a previous approval. The operator must preview again before anything is created."""
        self._plan.pop(run_id, None)

    def _previewed_plan(self, run_id: str) -> ProvisioningPlan | None:
        entry = self._plan.get(run_id)
        if entry is None:
            return None
        plan, approved_against = entry
        if self._discovery_steps.current_discovery(run_id) is not approved_against:
            # Discovery was re-run: the environment the operator approved against no longer applies.
            self.invalidate_plan(run_id)
            return None
        return plan

    def start_storage_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self._discovery_steps.require_discovery(run_id)
        coord.spawn(run_id, self._run_storage_preview(run, intent, discovery))
        return run

    async def _run_storage_preview(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, "step.started", "Building the provisioning plan…")
        plan = await asyncio.to_thread(storage_provision.build_plan, intent, discovery)
        self._plan[run.run_id] = (plan, discovery)
        status = RunStatus.RETRYABLE_FAILURE if plan.error else RunStatus.WAITING_FOR_OPERATOR
        coord.set_state(run, status, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            "storage.preview.failed" if plan.error else "storage.previewed",
            plan.error or f"Plan ready — {len(plan.actions)} action(s). Review, then confirm to create.",
            data={"plan": plan.model_dump(mode="json")},
        )

    def start_storage_apply(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self._discovery_steps.require_discovery(run_id)
        if self._previewed_plan(run_id) is None:
            raise StepPreconditionError("no provisioning plan to apply — run the provisioning preview first")
        coord.spawn(run_id, self._run_storage_apply(run, intent, discovery))
        return run

    async def _run_storage_apply(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, "storage.apply.started", "Creating host, volumes and exports…")
        result = await asyncio.to_thread(storage_provision.apply_plan, intent, discovery)
        created = sum(1 for o in result.outcomes if o.status == "created")
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE if result.error else RunStatus.READY, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            "storage.apply.failed" if result.error else "storage.applied",
            result.error or f"Provisioning complete — {created} created, {len(result.outcomes) - created} already existed.",
            data={"result": result.model_dump(mode="json")},
        )

    def start_path_verify(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self._discovery_steps.require_discovery(run_id)
        coord.spawn(run_id, self._run_path_verify(run, intent, discovery))
        return run

    async def _run_path_verify(self, run: RunRecord, intent, discovery) -> None:
        # Tier-2: read `showvlun -a` (read-only SSH) and report per host whether the exported LUNs are
        # actually live, over how many fabrics. Report-only — it never gates the run (ADR 0010).
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, "storage.paths.checking",
                   "Reading showvlun -a to verify the exported LUNs are live (read-only)…")
        verification = await asyncio.to_thread(storage_path_verify.verify_provisioned_paths, intent, discovery)
        live = sum(1 for h in verification.hosts if h.verdict == "live")
        status = RunStatus.RETRYABLE_FAILURE if verification.error else RunStatus.WAITING_FOR_OPERATOR
        coord.set_state(run, status, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            "storage.paths.failed" if verification.error else "storage.paths.verified",
            verification.error or f"Path check: {live}/{len(verification.hosts)} host(s) live on both fabrics (report-only).",
            data={"verification": verification.model_dump(mode="json")},
        )

    # ------------------------------------------------------------------ provisioning builder (Stage 2)

    def get_storage_objects(self, run_id: str) -> ProvisioningObjects:
        """The dropdown 'palette': array objects (WSAPI read) + to-be-created (sheet intent) + discovered
        hosts + the currently-composed host sets/exports. Synchronous — the caller runs it off-loop."""
        coord = self._coord
        intent = coord.get_provisioning_intent(run_id)
        discovery = self._discovery_steps.require_discovery(run_id)
        existing = storage_provision.read_array_objects(intent)
        return ProvisioningObjects(
            existing_cpgs=existing["cpgs"],
            existing_hosts=existing["hosts"],
            existing_host_sets=existing["host_sets"],
            existing_volumes=existing["volumes"],
            existing_volume_sets=existing["volume_sets"],
            array_error=existing["error"],
            new_volumes=[v.name for v in intent.volumes],
            new_host_sets=[hs.name for hs in intent.host_sets],
            new_vvsets=sorted({v.vvset for v in intent.volumes if v.vvset}),
            discovered_hosts=storage_provision.host_briefs(discovery),
            host_sets=list(intent.host_sets),
            exports=list(intent.exports),
        )

    def set_provisioning_builder(self, run_id: str, builder: ProvisioningBuilder) -> ProvisioningComposition:
        """Save the operator's composed host-set membership + VV-set membership + exports onto the run's
        ProvisioningIntent, so the subsequent preview/apply act on them."""
        coord = self._coord
        intent = coord.get_provisioning_intent(run_id)
        updated = intent.model_copy(deep=True, update={
            "host_sets": builder.host_sets if builder.host_sets else intent.host_sets,
            "exports": builder.exports,
        })
        if builder.vvsets:  # authoritative when provided: a volume in no set is un-set
            vol_to_vvset = {vol: name for name, vols in builder.vvsets.items() for vol in vols}
            for v in updated.volumes:
                v.vvset = vol_to_vvset.get(v.name)
        coord.store.save_provisioning_intent(run_id, updated)
        # The composition just changed, so any plan the operator already approved described something
        # else. Withdraw it — apply must not run against an approval for a different composition.
        self.invalidate_plan(run_id)
        return ProvisioningComposition(host_sets=updated.host_sets, exports=updated.exports, volumes=updated.volumes)
