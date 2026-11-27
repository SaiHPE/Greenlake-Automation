"""Step services for the storage-provisioning context, over the RunCoordinator.

Three services: DiscoveryZoningSteps (discovery + zoning verify/plan — the shared read-only
foundation), ArrayPortsSteps (the Array ports step: the array's own ports, set from the sheet before
zoning, SPEC-024) and ProvisioningSteps (tier-1 preview/apply, the Stage-2 builder, tier-2 path
verification). Provisioning CONSUMES discovery/zoning (ADR 0010), so ProvisioningSteps depends on
DiscoveryZoningSteps for the per-run discovery artifact.

The storage functions are called through their modules (storage_discovery.discover, …) so tests can
monkeypatch the modules themselves.
"""

from __future__ import annotations

import asyncio
import copy
import json
from functools import partial

import structlog

from alletra_onboard.application.provisioning import (
    apply,
    iscsi_network,
    peer_ports,
    peer_ports_read,
    storage_provision,
    zoning_apply,
)
from alletra_onboard.application.provisioning import discovery as storage_discovery
from alletra_onboard.application.provisioning import path_verify as storage_path_verify
from alletra_onboard.application.provisioning import preflight as storage_preflight
from alletra_onboard.application.provisioning import zoning as storage_zoning
from alletra_onboard.application.provisioning import zoning_plan as storage_zoning_plan
from alletra_onboard.application.runs.coordinator import (
    RunBusyError,
    RunCoordinator,
    StepPreconditionError,
    check_approval,
    new_plan_id,
)
from alletra_onboard.domain import events
from alletra_onboard.domain.approval import Approval
from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.network import IscsiNetworkPlan, IscsiVlanRequest, PortNetworkView
from alletra_onboard.domain.peer_ports import (
    PeerPortAction,
    PeerPortIntent,
    PeerPortPlan,
    PeerPortView,
)
from alletra_onboard.domain.provisioning import (
    PreflightReport,
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningObjects,
)
from alletra_onboard.domain.zoning import ZoningApplyPlan

_log = structlog.get_logger(__name__)


class DiscoveryZoningSteps:
    """Discovery + SAN-zoning verify/plan (read-only) and opt-in Brocade switch apply (ADR 0033)."""

    def __init__(self, coord: RunCoordinator) -> None:
        self._coord = coord
        # Per-run discovery cache over the durable run_artifacts store (C7): the store is the truth
        # (a server restart mid-engagement must not force re-discovery), the dict avoids re-parsing.
        self.discovery: dict[str, DiscoveryReport] = {}
        self._zoning_apply: dict[str, ZoningApplyPlan] = {}

    def current_discovery(self, run_id: str) -> DiscoveryReport | None:
        """The discovery in effect, or None. Unlike require_discovery this never raises — callers use
        it to detect that discovery has been re-run since they last read it."""
        try:
            return self.require_discovery(run_id)
        except StepPreconditionError:
            return None

    def require_discovery(self, run_id: str) -> DiscoveryReport:
        report = self.discovery.get(run_id)
        if report is None:
            raw = self._coord.store.load_artifact(run_id, "discovery")
            if raw is not None:
                try:
                    report = DiscoveryReport.model_validate_json(raw)
                    self.discovery[run_id] = report
                except ValueError:
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
        self._zoning_apply.pop(run_id, None)
        coord.spawn(run_id, self._run_discover(run, intent))
        return run

    async def _run_discover(self, run: RunRecord, intent) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_DISCOVER)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_DISCOVER, events.STEP_STARTED, "Discovering array ports, ESXi HBAs and fabric logins…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            # discover() runs in a worker thread; the SSE fan-out uses asyncio.Queues (not thread-safe),
            # so marshal each progress event back onto the event loop.
            loop.call_soon_threadsafe(
                coord.emit, run.run_id, WorkflowPhase.STORAGE_DISCOVER, events.PHASE_PROGRESS, message
            )

        report = await asyncio.to_thread(storage_discovery.discover, intent, progress=progress)
        self.discovery[run.run_id] = report
        # discovery succeeded; failing to cache it must not fail the step.
        coord.save_artifact_best_effort(run.run_id, "discovery", report.model_dump_json().encode("utf-8"))
        if report.error:
            # D-10: the event's own message says what failed and what to do; the UI marks the step failed
            # from report.error. A run keeps its sheet's credential (ADR 0013), so the fix is a new run.
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, WorkflowPhase.STORAGE_DISCOVER)
            coord.emit(
                run.run_id, WorkflowPhase.STORAGE_DISCOVER, events.DISCOVER_COMPLETED,
                f"{report.error} Nothing downstream can run without the array: fix the address or "
                "credential on the sheet and start a new run.",
                events.DiscoveryData(report=report),
            )
            return
        coord.set_state(run, RunStatus.READY, WorkflowPhase.STORAGE_DISCOVER)
        vcenter_down = any(n.startswith("vCenter discovery failed") for n in report.notes)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_DISCOVER, events.DISCOVER_COMPLETED,
            f"Discovery complete — {len(report.array_ports)} array port(s), {len(report.host_hbas)} host HBA(s)"
            + ("; vCenter was NOT reached — hosts come from the array and the sheet only" if vcenter_down else "")
            + (f"; {len(report.notes)} note(s)" if report.notes else ""),
            events.DiscoveryData(report=report),
        )

    def zoning_plan_payload(self, run_id: str) -> dict | None:
        """The run's latest `zoning.plan` payload, or None — the fabric-named hosts reach the zoning
        check and provisioning through it (SPEC-003 R1)."""
        latest = None
        for event in self._coord.list_events(run_id):
            if event.event_type == "zoning.plan" and event.data.get("plan"):
                latest = event.data["plan"]
        return latest

    def zoned_hosts(self, run_id: str) -> set[str]:
        """The hosts the last zoning verify confirmed on BOTH fabrics — the provisioning gate.

        Per host, not one global flag (ADR 0012). The old gate also accepted a "staged" state, set
        when the tool wrote zones to the switch itself; the tool no longer does that, and staging was
        the wrong thing to gate on anyway: it recorded that somebody had asked for zoning, not that
        zoning was live. On 2026-08-31 a staged-but-unactivated zone opened the gate for a host that
        then correctly reported `no_path`, because writing the defined config is not activation.
        """
        raw = self._coord.store.load_artifact(run_id, "zoned_hosts")
        if not raw:
            return set()
        return {h for h in raw.decode("utf-8", "replace").split("\n") if h}

    def hold_zoning_apply_plan(self, run_id: str, apply_plan: ZoningApplyPlan) -> None:
        self._coord.get_run(run_id)
        if apply_plan.fabrics and apply_plan.plan_id:
            zoning_apply.verify_plan_for_run(self._coord, run_id, apply_plan)
            self._zoning_apply[run_id] = apply_plan
        else:
            self._zoning_apply.pop(run_id, None)

    def held_zoning_apply_plan(self, run_id: str) -> ZoningApplyPlan | None:
        return self._zoning_apply.get(run_id)

    def start_zoning_apply(self, run_id: str, *, approved_plan: str | None) -> RunRecord:
        return zoning_apply.start_approved_apply(self._coord, run_id, self._zoning_apply, approved_plan)

    def _save_zoned_hosts(self, run_id: str, hosts: list[str]) -> None:
        # the step succeeded; persisting the gate must not fail it
        self._coord.save_artifact_best_effort(run_id, "zoned_hosts", "\n".join(hosts).encode("utf-8"))

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
        coord.emit(run.run_id, WorkflowPhase.STORAGE_ZONING, events.STEP_STARTED, "Verifying SAN zoning on both fabrics…")
        report = await asyncio.to_thread(
            storage_zoning.build_report, intent, discovery, self.zoning_plan_payload(run.run_id)
        )
        # Every verify OVERWRITES the gate. The verify is the ONLY thing that can open it, because a
        # host is provisionable exactly when the array can see it logged in on both fabrics.
        self._save_zoned_hosts(run.run_id, report.zoned_hosts)
        if report.error:
            # Z-7 (S-3, 2026-09-17): with no array ports the check said "Zoning needs 0 zone(s)" and
            # "nothing can be provisioned" in one breath. The error is the whole message.
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, WorkflowPhase.STORAGE_ZONING)
            coord.emit(run.run_id, WorkflowPhase.STORAGE_ZONING, events.ZONING_PREVIEWED, report.error,
                       events.ZoningCheckData(report=report))
            return
        coord.set_state(run, RunStatus.READY if report.proper else RunStatus.WAITING_FOR_OPERATOR, WorkflowPhase.STORAGE_ZONING)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_ZONING,
            events.ZONING_PROPER if report.proper else events.ZONING_PREVIEWED,
            storage_zoning.summary(report),
            events.ZoningCheckData(report=report),
        )

    def start_zoning_plan(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        discovery = self.require_discovery(run_id)
        self._zoning_apply.pop(run_id, None)
        coord.spawn(run_id, self._run_zoning_plan(run, intent, discovery))
        return run

    async def _run_zoning_plan(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_ZONING)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_ZONING, events.STEP_STARTED,
                   "Reading both fabric switches (read-only) to build the zoning plan…")
        peer_pairs, peer_nsps = self._peer_zone_input(run.run_id, intent)
        plan = await asyncio.to_thread(partial(
            storage_zoning_plan.build_zoning_plan, intent, discovery, peer_pairs=peer_pairs, peer_nsps=peer_nsps))
        # The Array ports step's peer-port plan names a free port still zoned (SPEC-025 R3) from this read.
        # the plan stands; failing to keep the zones only loses a note
        coord.save_artifact_best_effort(run.run_id, ACTIVE_ZONES_ARTIFACT, json.dumps(plan.active_zones).encode("utf-8"))
        pairs = sum(len(f.pairs) for f in plan.fabrics)
        coord.set_state(run, RunStatus.READY, WorkflowPhase.STORAGE_ZONING)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_ZONING, events.ZONING_PLAN,
            f"Zoning plan: {pairs} single-initiator-single-target zone(s) across the fabrics"
            + (f"; {len(plan.offline_hosts)} host WWPN(s) offline (cable + power)" if plan.offline_hosts else "")
            + (f"; {len(plan.notes)} note(s)" if plan.notes else ""),
            events.ZoningPlanData(plan=plan),
        )


    def _peer_zone_input(self, run_id: str, intent) -> tuple[list[tuple[str, str]], dict[str, str]]:
        """SPEC-025 R7: the (peer WWPN, source WWPN) pairs from the latest read of the Array ports step,
        the read after the change, and each peer WWPN's port. None before a peer port exists."""
        if intent.peer_ports is None:
            return [], {}
        view = latest_peer_view(self._coord, run_id)
        if view is None:
            return [], {}
        pairs = peer_ports.peer_zone_pairs(intent.peer_ports, view)
        nsps = {p.port_wwn: nsp for nsp, p in view.ports.items() if p.port_wwn}
        return pairs, {wwpn: nsps[wwpn] for wwpn, _source in pairs if wwpn in nsps}


#: The switches' effective zones from the run's zoning plan read: {switch: {zone: [WWPNs]}}.
ACTIVE_ZONES_ARTIFACT = "active_zones"


def latest_peer_view(coord: RunCoordinator, run_id: str) -> PeerPortView | None:
    """The peer-port read of the newest Array ports event that holds one, or None."""
    for event in reversed(coord.list_events(run_id)):
        view = ((event.data or {}).get("peer") or {}).get("view") if event.event_type.startswith("ports.") else None
        if view:
            try:
                return PeerPortView.model_validate(view)
            except ValueError:  # an unreadable stored view means "read the array again"
                return None
    return None


class ArrayPortsSteps:
    """The Array ports step (SPEC-024 R8, SPEC-025 R8): read the array and plan what the sheet asks of
    its ports, one section per tab: the iSCSI VLAN addresses (iSCSI network tab) and the peer ports
    (Peer ports tab). The first slices of ADR 0017 and ADR 0018: each plan prints the commands for the
    engineer; nothing here writes, and there is no apply yet. A read after the engineer pasted the
    peer-port commands is judged as the apply will judge its read-back (SPEC-025 R4)."""

    def __init__(self, coord: RunCoordinator) -> None:
        self._coord = coord
        # Each plan, held with the read and the sheet rows it came from (LESSONS 6): in memory only, so a
        # restart withdraws it, a new read replaces it, and rows that differ from the run's sheet void it.
        # The applies (the later slices) act only on a plan this still holds.
        self._iscsi: dict[str, tuple[IscsiNetworkPlan, PortNetworkView, list[IscsiVlanRequest]]] = {}
        self._peer: dict[str, tuple[PeerPortPlan, PeerPortView, PeerPortIntent]] = {}

    def iscsi_rows(self, run_id: str) -> list[IscsiVlanRequest]:
        return list(self._coord.get_provisioning_intent(run_id).iscsi_network)

    def peer_rows(self, run_id: str) -> PeerPortIntent | None:
        return self._coord.get_provisioning_intent(run_id).peer_ports

    def held_iscsi_plan(self, run_id: str) -> IscsiNetworkPlan | None:
        entry = self._iscsi.get(run_id)
        if entry is None:
            return None
        plan, _view, rows = entry
        if rows != self.iscsi_rows(run_id):
            self._iscsi.pop(run_id, None)
            return None
        return plan

    def held_peer_plan(self, run_id: str) -> PeerPortPlan | None:
        entry = self._peer.get(run_id)
        if entry is None:
            return None
        plan, _view, rows = entry
        if rows != self.peer_rows(run_id):
            self._peer.pop(run_id, None)
            return None
        return plan

    def start_ports_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = coord.get_provisioning_intent(run_id)
        self._iscsi.pop(run_id, None)
        self._peer.pop(run_id, None)
        if not intent.iscsi_network and intent.peer_ports is None:
            # R8: nothing to read, and the step is complete. The run stays where it is.
            coord.emit(run_id, WorkflowPhase.STORAGE_PORTS, events.PORTS_COMPLETED,
                       "The sheet asks for no iSCSI VLANs and no peer ports. Nothing to set up here.",
                       events.PortsData())
            return run
        coord.spawn(run_id, self._run_ports_preview(run, intent))
        return run

    async def _run_ports_preview(self, run: RunRecord, intent) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_PORTS
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.STEP_STARTED,
                   f"Reading {intent.array.host} (read-only): its ports"
                   + (", iSCSI addresses and VLANs" if intent.iscsi_network else "")
                   + (", connection modes, logins and exports" if intent.peer_ports is not None else "") + "…")
        failures: list[str] = []
        pending, summary, done = False, [], []
        name = intent.array.host
        data = events.PortsData()

        if intent.iscsi_network:
            rows = list(intent.iscsi_network)
            try:
                view = await asyncio.to_thread(iscsi_network.read_port_network, intent.array)
            except (DeviceError, ValueError) as exc:  # the step reports; nothing is planned on half a read
                err = f"Could not read {intent.array.host}: {exc}. Nothing was planned. Read the array again."
                data.iscsi = events.IscsiSection(requests=rows, error=err)
                failures.append(err)
            else:
                plan = iscsi_network.plan_iscsi_vlans(rows, view)
                self._iscsi[run.run_id] = (plan, view, rows)
                data.iscsi = events.IscsiSection(
                    requests=rows, view=view, plan=plan,
                    commands_text=iscsi_network.command_set_text(plan),
                    removals_text=iscsi_network.removal_set_text(plan),
                    gateway_text=iscsi_network.gateway_set_text(plan),
                )
                name = plan.array or name
                adds = sum(1 for a in plan.actions if a.state == "create")
                conflicts = sum(1 for a in plan.actions if a.state == "conflict")
                there = len(plan.actions) - adds - conflicts
                pending = pending or bool(adds or conflicts)
                summary.append(f"{adds} to add, {conflicts} conflict(s), {there} already there")
                done.append(f"all {there} iSCSI address(es) the sheet asks for are on the array")

        if intent.peer_ports is not None:
            peer = intent.peer_ports
            view = await asyncio.to_thread(peer_ports_read.read_view, intent.array)
            if view.read_error:
                err = f"{view.read_error}. Nothing was planned for the peer ports. Read the array again."
                data.peer = events.PeerSection(requests=list(peer.ports), error=err)
                failures.append(err)
            else:
                zones = self._active_zones(run.run_id)
                plan = peer_ports.plan_peer_ports(peer, view, zones)
                result = None
                before = self._before_the_paste(run.run_id, peer)
                if before is not None and peer_ports.changed_since(before[0], before[1], view):
                    result = peer_ports.read_back_peer_ports(before[0], before=before[1], after=view)
                self._peer[run.run_id] = (plan, view, peer)
                removals = peer_ports.planned_removals(plan)
                data.peer = events.PeerSection(
                    requests=list(peer.ports), view=view, plan=plan, result=result, removals=removals,
                    zones_checked=zones is not None,
                    commands_text=peer_ports.command_set_text(plan, name),
                    removals_text=peer_ports.removal_set_text(removals, name),
                    result_removals_text=peer_ports.removal_set_text(result.removals, name) if result else "",
                )
                sets = sum(1 for a in plan.actions if a.state == "create")
                peers = sum(1 for a in plan.actions if a.state == "exists")
                conflicts = sum(1 for a in plan.actions if a.state == "conflict")
                pending = pending or bool(sets or plan.blockers or (result and result.error))
                summary.append(f"peer ports: {sets} to set, {peers} already peer, {conflicts} conflict(s)"
                               + (f", {len(result.changed)} set since the plan" if result else ""))
                done.append(f"all {peers} peer port(s) the sheet asks for are in peer mode")

        if failures:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, events.PORTS_PREVIEW_FAILED, " ".join(failures), data)
            return
        if not pending:
            coord.set_state(run, RunStatus.READY, phase)
            coord.emit(run.run_id, phase, events.PORTS_COMPLETED, f"Read {name}: {'; '.join(done)}.", data)
            return
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, events.PORTS_PREVIEWED, f"Read {name}: plan ready, {'; '.join(summary)}.", data)

    def _active_zones(self, run_id: str) -> dict[str, dict[str, set[str]] | None] | None:
        """The switches' effective zones from this run's zoning plan read ({switch: None} for a switch it
        could not read), or None when no switch was read at all."""
        raw = self._coord.store.load_artifact(run_id, ACTIVE_ZONES_ARTIFACT)
        if not raw:
            return None
        try:
            stored = json.loads(raw)
            zones = {switch: None if active is None else {zone: set(members) for zone, members in active.items()}
                     for switch, active in stored.items()}
        except (ValueError, TypeError, AttributeError):  # unreadable: say the zones were not checked
            return None
        return zones if any(active is not None for active in zones.values()) else None

    def _before_the_paste(self, run_id: str, peer: PeerPortIntent) -> tuple[PeerPortPlan, PeerPortView] | None:
        """SPEC-025 R4: what a read is judged against as the read after the paste. Each port is judged
        against the FIRST read of this run (same sheet rows) that planned to set it, so a port set by an
        earlier paste keeps its restore while a later paste sets the others; every other port against
        the first read that planned any. None before any read planned a port to set."""
        rows = [r.model_dump(mode="json") for r in peer.ports]
        first: PeerPortView | None = None
        creates: dict[str, tuple[PeerPortAction, PeerPortView]] = {}
        for event in self._coord.list_events(run_id):
            section = (event.data or {}).get("peer") if event.event_type.startswith("ports.") else None
            if not section or not section.get("plan") or section.get("requests") != rows:
                continue
            try:
                plan = PeerPortPlan.model_validate(section["plan"])
                view = PeerPortView.model_validate(section["view"])
            except (ValueError, KeyError, TypeError) as exc:  # an unreadable stored plan is no plan to judge against
                _log.debug("stored_peer_plan_unreadable", run_id=run_id, error=str(exc))
                continue
            for action in plan.actions:
                if action.state == "create" and action.nsp not in creates:
                    creates[action.nsp] = (action, view)
                    first = first or view
        if first is None:
            return None
        before = first.model_copy(deep=True)
        for nsp, (_action, view) in creates.items():
            before.ports[nsp] = view.ports[nsp]
            if nsp in view.params:
                before.params[nsp] = view.params[nsp]
        actions = [creates[r.nsp][0] for r in peer.ports if r.nsp in creates]
        return PeerPortPlan(actions=actions), before


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
        self._plan: dict[str, apply.StorageInputs] = {}

    def invalidate_plan(self, run_id: str) -> None:
        """Withdraw a previous approval. The operator must preview again before anything is created."""
        self._plan.pop(run_id, None)

    def _previewed_plan(self, run_id: str) -> apply.StorageInputs | None:
        entry = self._plan.get(run_id)
        if entry is None:
            return None
        if self._discovery_steps.current_discovery(run_id) is not entry.discovery:
            # Discovery was re-run: the environment the operator approved against no longer applies.
            self.invalidate_plan(run_id)
            return None
        return entry

    def _ready(self, run_id: str):
        return (
            self._coord.get_run(run_id),
            self._coord.get_provisioning_intent(run_id),
            self._discovery_steps.require_discovery(run_id),
        )

    def start_storage_preview(self, run_id: str) -> RunRecord:
        run, intent, discovery = self._ready(run_id)
        self._coord.spawn(run_id, self._run_storage_preview(run, intent, discovery))
        return run

    async def _run_storage_preview(self, run: RunRecord, intent, discovery) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        self.invalidate_plan(run.run_id)   # a new preview withdraws the old approval, even if it fails
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, events.STEP_STARTED, "Building the provisioning plan…")
        frozen = intent.model_copy(deep=True)
        zoned = set(self._discovery_steps.zoned_hosts(run.run_id))
        zoning = copy.deepcopy(self._discovery_steps.zoning_plan_payload(run.run_id))
        plan = await asyncio.to_thread(
            partial(storage_provision.build_plan, frozen, discovery, reachable_hosts=zoned, zoning_plan=zoning)
        )
        # The identity the apply must quote back: a new preview is a new plan to approve.
        plan = plan.model_copy(update={"plan_id": new_plan_id()})
        self._plan[run.run_id] = apply.StorageInputs(frozen, discovery, zoned, plan, zoning)
        status = RunStatus.RETRYABLE_FAILURE if plan.error else RunStatus.WAITING_FOR_OPERATOR
        coord.set_state(run, status, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            events.STORAGE_PREVIEW_FAILED if plan.error else events.STORAGE_PREVIEWED,
            plan.error or f"Plan ready — {len(plan.actions)} action(s). Review, then confirm to create.",
            events.StoragePlanData(plan=plan),
        )

    def start_storage_apply(self, run_id: str, *, approved_plan: str | None) -> RunRecord:
        run, _intent, _discovery = self._ready(run_id)
        # Zoning gates the EXPORT, per host, not the whole run (ADR 0012 revised 2026-09-02). Host
        # objects are created regardless: HPE's documented order is register-first, and a host object
        # for a server that is not cabled yet is harmless and reversible. The exports for hosts the
        # array cannot reach are held back and named in the plan the operator approves.
        inputs = self._previewed_plan(run_id)
        if inputs is None:
            raise StepPreconditionError("no provisioning plan to apply — run the provisioning preview first")
        plan = inputs.plan
        if plan.error:
            # A previewed-but-failed plan is not an approval (e.g. the CPG hard gate) — fix, re-preview.
            raise StepPreconditionError(f"the provisioning preview reported a blocking problem: {plan.error}")
        if plan.blockers:
            # SPEC-001 R6: an object that exists and differs cannot be approved into existence.
            raise StepPreconditionError(
                "the plan has conflicts that must be resolved on the array first: " + "; ".join(plan.blockers)
            )
        # LESSONS 7: the operator's tick reaches the server as the id of the plan it was given for.
        check_approval(approved_plan, plan.plan_id)
        approval = self._coord.issue_approval(run_id, "storage", {"A": inputs.intent.array})
        self._plan.pop(run_id, None)
        self._coord.spawn(run_id, self._run_storage_apply(run, inputs, approval), approval=approval)
        return run

    async def _run_storage_apply(self, run: RunRecord, inputs: apply.StorageInputs, approval: Approval) -> None:
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, events.STORAGE_APPLY_STARTED, "Creating host, volumes and exports…")
        result = await coord.run_approved(approval, partial(apply.apply_plan, inputs, approval))
        created = sum(1 for o in result.outcomes if o.status == "created")
        updated = sum(1 for o in result.outcomes if o.status == "updated")
        failed = sum(1 for o in result.outcomes if o.status == "failed")
        existed = len(result.outcomes) - created - updated - failed
        summary = f"Provisioning complete — {created} created, {updated} updated, {existed} already existed"
        if failed:
            summary += f", {failed} failed read-back"
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE if result.error else RunStatus.READY, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            events.STORAGE_APPLY_FAILED if result.error else events.STORAGE_APPLIED,
            result.error or summary + ".",
            events.StorageResultData(result=result),
        )

    def start_path_verify(self, run_id: str) -> RunRecord:
        run, intent, discovery = self._ready(run_id)
        self._coord.spawn(run_id, self._run_path_verify(run, intent, discovery))
        return run

    async def _run_path_verify(self, run: RunRecord, intent, discovery) -> None:
        # Tier-2: read `showvlun -a` (read-only SSH) and report per host whether the exported LUNs are
        # actually live, over how many fabrics. Report-only — it never gates the run (ADR 0010).
        coord = self._coord
        coord.set_state(run, RunStatus.RUNNING, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(run.run_id, WorkflowPhase.STORAGE_PROVISION, events.STORAGE_PATHS_CHECKING,
                   "Reading showvlun -a to verify the exported LUNs are live (read-only)…")
        zoned = self._discovery_steps.zoned_hosts(run.run_id)
        verification = await asyncio.to_thread(partial(
            storage_path_verify.verify_provisioned_paths, intent, discovery, reachable_hosts=zoned,
            zoning_plan=self._discovery_steps.zoning_plan_payload(run.run_id),
        ))
        live = sum(1 for h in verification.hosts if h.verdict == "live")
        status = RunStatus.RETRYABLE_FAILURE if verification.error else RunStatus.WAITING_FOR_OPERATOR
        coord.set_state(run, status, WorkflowPhase.STORAGE_PROVISION)
        coord.emit(
            run.run_id, WorkflowPhase.STORAGE_PROVISION,
            events.STORAGE_PATHS_FAILED if verification.error else events.STORAGE_PATHS_VERIFIED,
            verification.error or f"Path check: {live}/{len(verification.hosts)} host(s) live on both fabrics (report-only).",
            events.PathsData(verification=verification),
        )

    # ------------------------------------------------------------------ provisioning builder (Stage 2)

    def get_storage_preflight(self, run_id: str) -> PreflightReport:
        """Read-only readiness of the array + vCenter the sheet points at. Deliberately does NOT
        require discovery — the point is to name the missing prerequisite *before* discovery runs.
        Synchronous (network reads); the caller runs it off the event loop."""
        intent = self._coord.get_provisioning_intent(run_id)
        return storage_preflight.run_preflight(intent)

    def get_storage_objects(self, run_id: str) -> ProvisioningObjects:
        """The dropdown 'palette': array objects (WSAPI read) + to-be-created (sheet intent) + discovered
        hosts + the currently-composed host sets/exports. Synchronous — the caller runs it off-loop."""
        coord = self._coord
        intent = coord.get_provisioning_intent(run_id)
        discovery = self._discovery_steps.require_discovery(run_id)
        existing = storage_provision.read_array_objects(intent)
        zoning = self._discovery_steps.zoning_plan_payload(run_id)
        shown, _ = storage_provision.planned_host_names(intent, discovery, zoning)
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
            discovered_hosts=storage_provision.host_briefs(discovery, intent.declared_hosts, zoning),
            host_sets=list(shown.host_sets),
            exports=list(shown.exports),
        )

    def set_provisioning_builder(self, run_id: str, builder: ProvisioningBuilder) -> ProvisioningComposition:
        """Save the operator's composed host-set membership + VV-set membership + exports onto the run's
        ProvisioningIntent, so the subsequent preview/apply act on them."""
        coord = self._coord
        if coord.is_busy(run_id):
            raise RunBusyError(run_id)
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
