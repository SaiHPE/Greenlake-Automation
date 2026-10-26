"""Step service for the replication context, over the RunCoordinator (SPEC-016).

Read both arrays, check, plan (read-only); apply the approved plan over WSAPI; verify by reading
back. The plan is held in memory like the provisioning plan: an approval, not a result, withdrawn
whenever the step is re-run and spent by an apply.
"""

from __future__ import annotations

import asyncio
from functools import partial

from alletra_onboard.application.replication import apply as replication_apply
from alletra_onboard.application.replication import failover as replication_failover
from alletra_onboard.application.replication import link_check as replication_link
from alletra_onboard.application.replication import plan as replication_plan
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication import verify as replication_verify
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.replication import (
    LINK_CHECK_TIME_DEFAULT,
    RTT_LIMIT_MS,
    TEST_GROUP,
    FailoverRecord,
    LinkCheck,
    ReplicationPlan,
    ReplicationReport,
)

REPORT_ARTIFACT = "replication_report"
RESULT_ARTIFACT = "replication_result"
FAILOVER_ARTIFACT = "failover_record"
LINK_CHECK_ARTIFACT = "link_check"


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
        except Exception:  # noqa: BLE001 - the read succeeded; failing to cache it must not fail the step
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
                       "Review the plan.")
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, "replication.previewed", summary,
                   data={"report": report.model_dump(mode="json"), "plan": plan.model_dump(mode="json")})

    # ------------------------------------------------------------------ SPEC-020: the link check

    def link_check(self, run_id: str) -> LinkCheck | None:
        raw = self._coord.store.load_artifact(run_id, LINK_CHECK_ARTIFACT)
        if raw is None:
            return None
        try:
            return LinkCheck.model_validate_json(raw)
        except Exception:  # noqa: BLE001 - an unreadable stored check means "check again"
            return None

    def start_link_check(self, run_id: str, *, duration_s: int = LINK_CHECK_TIME_DEFAULT) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        report = self.current_report(run_id)
        if report is None or report.error:
            raise StepPreconditionError("read both arrays first — the link check needs the ports and links the read found")
        if report.partnership is None:
            raise StepPreconditionError("no Remote Copy partnership between the arrays was found; there is no link to check")
        coord.spawn(run_id, self._run_link_check(run, intent, report, duration_s))
        return run

    async def _run_link_check(self, run: RunRecord, intent, report: ReplicationReport, duration_s: int) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "replication.link_check.started",
                   "Measuring the latency between the arrays with checkrclink…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        check = await asyncio.to_thread(partial(
            replication_link.run_link_check, intent.array, intent.replication, report,
            duration_s=duration_s, progress=progress,
        ))
        try:
            coord.store.save_artifact(run.run_id, LINK_CHECK_ARTIFACT, check.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001 - the test ran; failing to cache it must not fail the step
            pass
        data = {"link_check": check.model_dump(mode="json")}
        failed = [r for r in check.results if r.status == "failed"]
        if check.error or not check.measured:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, "replication.link_check.failed",
                       check.error or "; ".join(r.detail for r in failed) or "No link was measured.", data=data)
            return
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, "replication.link_checked", self._link_summary(check, failed), data=data)

    @staticmethod
    def _link_summary(check: LinkCheck, failed: list) -> str:
        measured = [r for r in check.results if r.status == "measured"]
        worst = check.worst_ms
        limits = ", ".join(f"{m} needs {RTT_LIMIT_MS[m]:g} ms or less" for m in check.modes)
        text = f"Latency {worst:g} ms on {len(measured)} link(s)" + (f" ({limits})" if limits else "")
        over = check.over_limit()
        if over:
            text += f" — over the limit for {'/'.join(over)}; the operator decides whether to continue."
        else:
            text += " — within the limit."
        if failed:
            text += f" {len(failed)} link(s) could not be measured."
        lost = [r for r in measured if (r.pings_lost_pct or 0) > 0]
        if lost:
            text += " Pings were lost on " + ", ".join(f"{r.pair.nsp_a} ({r.pings_lost_pct:g} %)" for r in lost) + "."
        return text

    def _gate_on_link(self, run_id: str, report: ReplicationReport, accept_latency: bool) -> list[str]:
        """R4: notes for the result, or a StepPreconditionError. RCIP partnerships only."""
        if report.partnership is None:
            return []
        check = self.link_check(run_id)
        if check is None or not check.measured:
            raise StepPreconditionError(
                "Check the link first: the latency between the arrays has not been measured in this run."
            )
        over = check.over_limit()
        if over and not accept_latency:
            mode = over[0]
            raise StepPreconditionError(
                f"The measured latency is {check.worst_ms:g} ms; {mode} replication over RCIP needs "
                f"{RTT_LIMIT_MS[mode]:g} ms or less. Tick 'Continue anyway' to configure it regardless."
            )
        note = f"Link check {check.at}: latency {check.worst_ms:g} ms on {len(check.results)} link(s)"
        if over:
            note += (f"; over the {RTT_LIMIT_MS[over[0]]:g} ms limit for {'/'.join(over)} — "
                     "the operator accepted it and chose to continue.")
        else:
            note += "; within the limit."
        return [note]

    # ------------------------------------------------------------------ R4/R7: apply the approved plan

    def start_replication_apply(self, run_id: str, *, accept_latency: bool = False) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        entry = self._plan.get(run_id)
        if entry is None:
            raise StepPreconditionError("no replication plan to apply — read both arrays first")
        plan, report = entry
        if plan.error:
            raise StepPreconditionError(f"the replication preview reported a blocking problem: {plan.error}")
        if plan.blockers:
            raise StepPreconditionError("the plan has findings that must be resolved first: " + "; ".join(plan.blockers))
        if not any(a.state == "create" for a in plan.actions):
            raise StepPreconditionError("nothing to create — every object in the plan already exists")
        notes = self._gate_on_link(run_id, report, accept_latency)
        coord.spawn(run_id, self._run_apply(run, intent, plan, notes))
        return run

    async def _run_apply(self, run: RunRecord, intent, plan: ReplicationPlan, notes: list[str] | None = None) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "replication.apply.started", "Configuring replication over WSAPI…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        result = await asyncio.to_thread(partial(replication_apply.apply_plan, plan, intent, progress=progress))
        result.notes.extend(notes or [])
        # the approval is spent: a second apply needs a fresh read and plan
        self._plan.pop(run.run_id, None)
        try:
            coord.store.save_artifact(run.run_id, RESULT_ARTIFACT, result.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001 - the writes happened; failing to cache the record must not fail the step
            pass
        created = sum(1 for o in result.outcomes if o.status == "created")
        existed = sum(1 for o in result.outcomes if o.status == "exists")
        if result.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, "replication.apply.failed", result.error, data={"result": result.model_dump(mode="json")})
            return
        coord.set_state(run, RunStatus.READY, phase)
        groups = ", ".join(result.groups_created) or "no new group"
        coord.emit(run.run_id, phase, "replication.applied",
                   f"Replication configured — {groups}; {created} write(s), {existed} already there. Verify replication to read it back.",
                   data={"result": result.model_dump(mode="json")})

    # ------------------------------------------------------------------ R6: verify (read-only)

    def start_replication_verify(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        plan = self._plan_for_verify(run_id)
        if plan is None:
            raise StepPreconditionError("nothing to verify yet — read both arrays first so the tool knows which groups to look for")
        coord.spawn(run_id, self._run_verify(run, intent, plan))
        return run

    def _plan_for_verify(self, run_id: str) -> ReplicationPlan | None:
        entry = self._plan.get(run_id)
        if entry is not None:
            return entry[0]
        # after an apply the approval is spent, but the plan it came from is in the run's events
        for event in reversed(self._coord.list_events(run_id)):
            if event.event_type == "replication.previewed" and event.data and event.data.get("plan"):
                try:
                    return ReplicationPlan.model_validate(event.data["plan"])
                except Exception:  # noqa: BLE001
                    return None
        return None

    async def _run_verify(self, run: RunRecord, intent, plan: ReplicationPlan) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "replication.verify.started", "Reading Remote Copy back on both arrays…")
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        verification = await asyncio.to_thread(partial(replication_verify.verify, intent, plan, progress=progress))
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE if verification.error else RunStatus.READY, phase)
        if verification.error:
            coord.emit(run.run_id, phase, "replication.verify.failed", verification.error,
                       data={"verification": verification.model_dump(mode="json")})
            return
        counts = {"replicating": 0, "syncing": 0, "not_replicating": 0}
        for g in verification.groups:
            counts[g.verdict] += 1
        summary = (f"{counts['replicating']} replicating · {counts['syncing']} syncing · {counts['not_replicating']} not replicating · "
                   + ("links Up" if verification.links_ok else "links NOT all Up"))
        coord.emit(run.run_id, phase, "replication.verified", summary, data={"verification": verification.model_dump(mode="json")})

    # ------------------------------------------------------------------ SPEC-017: the failover test

    def groups_created(self, run_id: str) -> list[str]:
        """The Remote Copy groups this run's applies created (from the run's events)."""
        names: list[str] = []
        for event in self._coord.list_events(run_id):
            if event.event_type in ("replication.applied", "replication.apply.failed"):
                for g in (event.data.get("result") or {}).get("groups_created") or []:
                    if g not in names:
                        names.append(g)
        return names

    def failover_group_choice(self, run_id: str, group: str | None, confirm: str | None) -> str:
        """SPEC-017 R1: the tool's own test group by default; a group this run created may be picked;
        any other group only when its name is typed back in the confirmation field."""
        intent = self._require_replication(run_id)
        chosen = (group or "").strip() or intent.replication.failover_group_name
        offered = {TEST_GROUP, intent.replication.failover_group_name, *self.groups_created(run_id)}
        if chosen not in offered and (confirm or "").strip() != chosen:
            raise StepPreconditionError(
                f"'{chosen}' was not created by this run. To test failover on it, type its name in the confirmation "
                "field: hosts running on its primary volumes lose access for the duration of the test."
            )
        return chosen

    def start_failover_test(self, run_id: str, *, group: str | None = None, confirm: str | None = None) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent = self._require_replication(run_id)
        chosen = self.failover_group_choice(run_id, group, confirm)
        coord.spawn(run_id, self._run_failover(run, intent, chosen))
        return run

    async def _run_failover(self, run: RunRecord, intent, group: str) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_FAILOVER_TEST
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, "failover.started",
                   f"Failover test on {group}: stop → fail over to the peer → recover → wait for sync → restore…",
                   data={"group": group})
        loop = asyncio.get_running_loop()

        def progress(message: str) -> None:
            loop.call_soon_threadsafe(coord.emit, run.run_id, phase, "phase.progress", message)

        record: FailoverRecord = await asyncio.to_thread(partial(replication_failover.run_failover_test, intent, group, progress=progress))
        try:
            coord.store.save_artifact(run.run_id, FAILOVER_ARTIFACT, record.model_dump_json().encode("utf-8"))
        except Exception:  # noqa: BLE001 - the test ran; failing to cache the record must not fail the step
            pass
        data = {"record": record.model_dump(mode="json")}
        if record.result == "passed":
            coord.set_state(run, RunStatus.READY, phase)
            timing = (f" Failover in {record.time_to_failover_s:g} s, synced back in {record.time_to_synced_s:g} s."
                      if record.time_to_failover_s is not None and record.time_to_synced_s is not None else "")
            coord.emit(run.run_id, phase, "failover.completed",
                       f"Failover test passed on {group}: the peer took over and the group is back to its normal state.{timing}",
                       data=data)
            return
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
        where = f" at step {record.failed_step}" if record.failed_step is not None else ""
        coord.emit(run.run_id, phase, "failover.failed",
                   f"Failover test {record.result}{where}: {record.error} " + (f"Way back: {record.recovery_action}" if record.recovery_action else ""),
                   data=data)

    def failover_record(self, run_id: str) -> FailoverRecord | None:
        raw = self._coord.store.load_artifact(run_id, FAILOVER_ARTIFACT)
        if raw is None:
            return None
        try:
            return FailoverRecord.model_validate_json(raw)
        except Exception:  # noqa: BLE001
            return None
