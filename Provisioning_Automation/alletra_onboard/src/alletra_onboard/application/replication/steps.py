"""Step service for the replication context, over the RunCoordinator (SPEC-016).

Read both arrays, check, plan (read-only); apply the approved plan over WSAPI; verify by reading
back. The plan is held in memory like the provisioning plan: an approval, not a result, withdrawn
whenever the step is re-run and spent by an apply.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from functools import partial

from alletra_onboard.application.replication import apply as replication_apply
from alletra_onboard.application.replication import failover as replication_failover
from alletra_onboard.application.replication import link_check as replication_link
from alletra_onboard.application.replication import (
    partnership_apply as replication_partnership_apply,
)
from alletra_onboard.application.replication import plan as replication_plan
from alletra_onboard.application.replication import plan_check as replication_plan_check
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication import verify as replication_verify
from alletra_onboard.application.runs.coordinator import (
    APPROVAL_REQUIRED,
    RunCoordinator,
    StepPreconditionError,
    check_approval,
    new_plan_id,
)
from alletra_onboard.domain import events
from alletra_onboard.domain.approval import Approval, Purpose
from alletra_onboard.domain.models import RunRecord, RunStatus, WorkflowPhase
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import (
    LINK_CHECK_TIME_DEFAULT,
    TEST_GROUP,
    FailoverRecord,
    LinkCheck,
    ReplicationIntent,
    ReplicationPlan,
    ReplicationReport,
    ReplicationResult,
    rtt_limit_ms,
    rtt_limit_text,
)


def applied_message(plan: ReplicationPlan, result: ReplicationResult) -> str:
    """The sentence after a good apply. The apply writes only the plan's creates, so what was already
    there is what the plan found there, plus any create the array answered was there by then."""
    created = sum(1 for o in result.outcomes if o.status == "created")
    if plan.sets_up_partnership:
        return (f"Ports and partnership set up — {created} step(s), every link Up. Read both arrays again, "
                "press Check RC link, then configure the groups.")
    existed = sum(1 for a in plan.actions if a.state == "exists") + sum(1 for o in result.outcomes if o.status == "exists")
    groups = ", ".join(result.groups_created) or "no new group"
    return f"Replication configured — {groups}; {created} write(s), {existed} already there. Verify replication to read it back."


REPORT_ARTIFACT = "replication_report"
RESULT_ARTIFACT = "replication_result"
FAILOVER_ARTIFACT = "failover_record"
LINK_CHECK_ARTIFACT = "link_check"
#: SPEC-031 R6: over Fibre Channel the typed round-trip time stands in for the link check.
FC_RTT_MISSING = ("Type the round-trip time between the arrays on the Replication tab: the tool cannot measure "
                  "Fibre Channel links yet.")


def gate_on_typed_rtt(report: ReplicationReport, rtt_ms: float | None, accept_latency: bool) -> list[str]:
    """SPEC-031 R6: a Fibre Channel partnership's latency is the round-trip time typed on the Replication tab,
    until the array's link test is known to measure FC links. Blank is refused; over the limit is refused unless
    the operator ticked 'Continue anyway'. The note says the value was typed, not measured."""
    if rtt_ms is None:
        raise StepPreconditionError(FC_RTT_MISSING)
    modes = report.modes or ["async"]
    over = [m for m in modes if rtt_ms > rtt_limit_ms("FC", m)]
    if over and not accept_latency:
        raise StepPreconditionError(
            f"The round-trip time typed on the Replication tab is {rtt_ms:g} ms; {rtt_limit_text('FC', over[0])}. "
            "Tick 'Continue anyway' to configure it regardless."
        )
    note = (f"Round-trip time {rtt_ms:g} ms, typed on the Replication tab by the engineer, not measured (the tool "
            "cannot measure Fibre Channel links yet)")
    if over:
        note += (f"; over the {rtt_limit_ms('FC', over[0]):g} ms limit for {'/'.join(over)} over Fibre Channel — "
                 "the operator accepted it and chose to continue.")
    else:
        note += "; within the limit."
    return [note]


class ReplicationSteps:
    def __init__(self, coord: RunCoordinator) -> None:
        self._coord = coord
        self._plan: dict[str, tuple[ReplicationPlan, ReplicationReport]] = {}

    def _progress(self, run_id: str, phase: WorkflowPhase) -> Callable[[str], None]:
        loop = asyncio.get_running_loop()

        def emit(message: str) -> None:
            loop.call_soon_threadsafe(self._coord.emit, run_id, phase, events.PHASE_PROGRESS, message)

        return emit

    def _require_replication(self, run_id: str) -> tuple[ProvisioningIntent, ReplicationIntent]:
        intent = self._coord.get_provisioning_intent(run_id)
        if intent.replication is None:
            raise StepPreconditionError(
                "this run's workbook has no Replication tab — add the peer array and the volume sets to "
                "protect, then start a new run"
            )
        return intent, intent.replication

    def current_report(self, run_id: str) -> ReplicationReport | None:
        raw = self._coord.store.load_artifact(run_id, REPORT_ARTIFACT)
        if raw is None:
            return None
        try:
            return ReplicationReport.model_validate_json(raw)
        except ValueError:  # an unreadable stored report means "read again"
            return None

    def previewed_plan(self, run_id: str) -> ReplicationPlan | None:
        entry = self._plan.get(run_id)
        return entry[0] if entry else None

    def start_replication_preview(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent, _rep = self._require_replication(run_id)
        self._plan.pop(run_id, None)
        coord.spawn(run_id, self._run_preview(run, intent))
        return run

    async def _run_preview(self, run: RunRecord, intent) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.STEP_STARTED, "Reading Remote Copy on both arrays…")
        progress = self._progress(run.run_id, phase)
        primary = await asyncio.to_thread(partial(replication_read.read_array, intent.array, progress=progress))
        peer = await asyncio.to_thread(partial(replication_read.read_array, intent.replication.peer, progress=progress))
        report = replication_plan_check.check(primary, peer, intent.replication)
        # The identity the apply must quote back: a new read is a new plan to approve.
        plan = replication_plan.build_plan(report, intent.replication, intent).model_copy(update={"plan_id": new_plan_id()})
        coord.save_artifact_best_effort(run.run_id, REPORT_ARTIFACT, report.model_dump_json().encode("utf-8"))
        self._plan[run.run_id] = (plan, report)

        if plan.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, events.REPLICATION_PREVIEW_FAILED, plan.error,
                       events.ReplicationPlanData(report=report, plan=plan))
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
        coord.emit(run.run_id, phase, events.REPLICATION_PREVIEWED, summary,
                   events.ReplicationPlanData(report=report, plan=plan))

    # ------------------------------------------------------------------ SPEC-020: the link check

    def link_check(self, run_id: str) -> LinkCheck | None:
        raw = self._coord.store.load_artifact(run_id, LINK_CHECK_ARTIFACT)
        if raw is None:
            return None
        try:
            return LinkCheck.model_validate_json(raw)
        except ValueError:  # an unreadable stored check means "check again"
            return None

    def start_link_check(self, run_id: str, *, duration_s: int = LINK_CHECK_TIME_DEFAULT) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent, _rep = self._require_replication(run_id)
        report = self.current_report(run_id)
        if report is None or report.error:
            raise StepPreconditionError("read both arrays first — the link check needs the ports and links the read found")
        if report.partnership is None:
            raise StepPreconditionError("no Remote Copy partnership between the arrays was found; there is no link to check")
        if report.partnership.transport == "FC":
            raise StepPreconditionError(f"the arrays replicate over Fibre Channel. {FC_RTT_MISSING}")
        coord.spawn(run_id, self._run_link_check(run, intent, report, duration_s))
        return run

    async def _run_link_check(self, run: RunRecord, intent, report: ReplicationReport, duration_s: int) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.REPLICATION_LINK_CHECK_STARTED,
                   "Measuring the latency between the arrays with checkrclink…")
        check = await asyncio.to_thread(partial(
            replication_link.run_link_check, intent.array, intent.replication, report,
            duration_s=duration_s, progress=self._progress(run.run_id, phase),
        ))
        coord.save_artifact_best_effort(run.run_id, LINK_CHECK_ARTIFACT, check.model_dump_json().encode("utf-8"))
        data = events.LinkCheckData(link_check=check)
        failed = [r for r in check.results if r.status == "failed"]
        if check.error or not check.measured:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, events.REPLICATION_LINK_CHECK_FAILED,
                       check.error or "; ".join(r.detail for r in failed) or "No link was measured.", data)
            return
        coord.set_state(run, RunStatus.WAITING_FOR_OPERATOR, phase)
        coord.emit(run.run_id, phase, events.REPLICATION_LINK_CHECKED, self._link_summary(check, failed), data)

    @staticmethod
    def _link_summary(check: LinkCheck, failed: list) -> str:
        measured = [r for r in check.results if r.status == "measured"]
        worst = check.worst_ms
        limits = ", ".join(f"{m} needs {rtt_limit_ms('IP', m):g} ms or less" for m in check.modes)
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

    def _gate_on_link(self, run_id: str, report: ReplicationReport, accept_latency: bool,
                      rtt_ms: float | None = None) -> list[str]:
        """R4: notes for the result, or a StepPreconditionError. An RCIP partnership needs this run's link check;
        a Fibre Channel one the round-trip time typed on the Replication tab (SPEC-031 R6)."""
        if report.partnership is None:
            return []
        if report.partnership.transport == "FC":
            return gate_on_typed_rtt(report, rtt_ms, accept_latency)
        check = self.link_check(run_id)
        if check is None or not check.measured:
            raise StepPreconditionError(
                "Check RC link first: the latency between the arrays has not been measured in this run."
            )
        over = check.over_limit()
        if over and not accept_latency:
            mode = over[0]
            raise StepPreconditionError(
                f"The measured latency is {check.worst_ms:g} ms; {rtt_limit_text('IP', mode)}. "
                "Tick 'Continue anyway' to configure it regardless."
            )
        note = f"Link check {check.at}: latency {check.worst_ms:g} ms on {len(check.results)} link(s)"
        if over:
            note += (f"; over the {rtt_limit_ms('IP', over[0]):g} ms limit for {'/'.join(over)} — "
                     "the operator accepted it and chose to continue.")
        else:
            note += "; within the limit."
        return [note]

    # ------------------------------------------------------------------ R4/R7: apply the approved plan

    def start_replication_apply(self, run_id: str, *, approved_plan: str | None, accept_latency: bool = False) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent, rep = self._require_replication(run_id)
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
        # LESSONS 7: the operator's tick reaches the server as the id of the plan it was given for.
        check_approval(approved_plan, plan.plan_id)
        notes = self._gate_on_link(run_id, report, accept_latency, rep.rtt_ms)
        purpose: Purpose = "rc_partnership" if plan.sets_up_partnership else "rc_groups"
        approval = coord.issue_approval(run_id, purpose, {"A": intent.array, "B": rep.peer})
        self._plan.pop(run_id, None)
        coord.spawn(run_id, self._run_apply(run, intent, plan, approval, notes), approval=approval)
        return run

    async def _run_apply(
        self, run: RunRecord, intent, plan: ReplicationPlan, approval: Approval, notes: list[str] | None = None,
    ) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.REPLICATION_APPLY_STARTED,
                   "Setting up the replication ports and the partnership over SSH…" if plan.sets_up_partnership
                   else "Configuring replication over WSAPI…")
        fn = replication_partnership_apply.apply_partnership if plan.sets_up_partnership else replication_apply.apply_plan
        result = await coord.run_approved(approval, partial(fn, plan, intent, approval, progress=self._progress(run.run_id, phase)))
        result.notes.extend(notes or [])
        coord.save_artifact_best_effort(run.run_id, RESULT_ARTIFACT, result.model_dump_json().encode("utf-8"))
        if result.error:
            coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
            coord.emit(run.run_id, phase, events.REPLICATION_APPLY_FAILED, result.error,
                       events.ReplicationResultData(result=result))
            return
        coord.set_state(run, RunStatus.READY, phase)
        coord.emit(run.run_id, phase, events.REPLICATION_APPLIED, applied_message(plan, result),
                   events.ReplicationResultData(result=result))

    # ------------------------------------------------------------------ R6: verify (read-only)

    def start_replication_verify(self, run_id: str) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent, _rep = self._require_replication(run_id)
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
                except ValueError:
                    return None
        return None

    async def _run_verify(self, run: RunRecord, intent, plan: ReplicationPlan) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_REPLICATE
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.REPLICATION_VERIFY_STARTED, "Reading Remote Copy back on both arrays…")
        verification = await asyncio.to_thread(partial(
            replication_verify.verify, intent, plan, progress=self._progress(run.run_id, phase),
            detail_fn=replication_read.read_group_details,
        ))
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE if verification.error else RunStatus.READY, phase)
        if verification.error:
            coord.emit(run.run_id, phase, events.REPLICATION_VERIFY_FAILED, verification.error,
                       events.ReplicationVerifyData(verification=verification))
            return
        counts = {"replicating": 0, "syncing": 0, "not_replicating": 0}
        for g in verification.groups:
            counts[g.verdict] += 1
        summary = (f"{counts['replicating']} replicating · {counts['syncing']} syncing · {counts['not_replicating']} not replicating · "
                   + ("links Up" if verification.links_ok else "links NOT all Up"))
        coord.emit(run.run_id, phase, events.REPLICATION_VERIFIED, summary,
                   events.ReplicationVerifyData(verification=verification))

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
        _intent, rep = self._require_replication(run_id)
        chosen = (group or "").strip() or rep.failover_group_name
        offered = {TEST_GROUP, rep.failover_group_name, *self.groups_created(run_id)}
        if chosen not in offered and (confirm or "").strip() != chosen:
            raise StepPreconditionError(
                f"'{chosen}' was not created by this run. To test failover on it, type its name in the confirmation "
                "field: hosts running on its primary volumes lose access for the duration of the test."
            )
        return chosen

    def start_failover_test(
        self, run_id: str, *, group: str | None = None, confirm: str | None = None, authorised: bool = False,
    ) -> RunRecord:
        coord = self._coord
        run = coord.get_run(run_id)
        intent, rep = self._require_replication(run_id)
        chosen = self.failover_group_choice(run_id, group, confirm)
        if not authorised:
            raise StepPreconditionError(APPROVAL_REQUIRED)
        approval = coord.issue_approval(run_id, "failover", {"A": intent.array, "B": rep.peer})
        coord.spawn(run_id, self._run_failover(run, chosen, approval), approval=approval)
        return run

    async def _run_failover(self, run: RunRecord, group: str, approval: Approval) -> None:
        coord = self._coord
        phase = WorkflowPhase.STORAGE_FAILOVER_TEST
        coord.set_state(run, RunStatus.RUNNING, phase)
        coord.emit(run.run_id, phase, events.FAILOVER_STARTED,
                   f"Failover test on {group}: stop → fail over to the peer → recover → wait for sync → restore…",
                   events.FailoverStartData(group=group))
        record: FailoverRecord = await coord.run_approved(
            approval, partial(replication_failover.run_failover_test, approval, group, progress=self._progress(run.run_id, phase)),
        )
        coord.save_artifact_best_effort(run.run_id, FAILOVER_ARTIFACT, record.model_dump_json().encode("utf-8"))
        data = events.FailoverData(record=record)
        if record.result == "passed":
            coord.set_state(run, RunStatus.READY, phase)
            timing = (f" Failover in {record.time_to_failover_s:g} s, synced back in {record.time_to_synced_s:g} s."
                      if record.time_to_failover_s is not None and record.time_to_synced_s is not None else "")
            coord.emit(run.run_id, phase, events.FAILOVER_COMPLETED,
                       f"Failover test passed on {group}: the peer took over and the group is back to its normal state.{timing}",
                       data)
            return
        coord.set_state(run, RunStatus.RETRYABLE_FAILURE, phase)
        where = f" at step {record.failed_step}" if record.failed_step is not None else ""
        coord.emit(run.run_id, phase, events.FAILOVER_FAILED,
                   f"Failover test {record.result}{where}: {record.error} " + (f"Way back: {record.recovery_action}" if record.recovery_action else ""),
                   data)

    def failover_record(self, run_id: str) -> FailoverRecord | None:
        raw = self._coord.store.load_artifact(run_id, FAILOVER_ARTIFACT)
        if raw is None:
            return None
        try:
            return FailoverRecord.model_validate_json(raw)
        except ValueError:
            return None
