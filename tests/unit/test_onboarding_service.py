import asyncio

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.event_bus import InMemoryEventBus
from alletra_onboard.application.onboarding_service import OnboardingService, RunBusyError
from alletra_onboard.application.provisioning import DONE, FAILED, WARNING, PhaseOutcome, ProvisionResult
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    BrowserResultStatus,
    DsccSetupConfig,
    FieldCheck,
    FieldCheckStatus,
    NetworkConfig,
    RunMode,
    RunStatus,
    VerificationReport,
    WorkflowPhase,
)


def _item(**overrides):
    data = {
        "serial_number": "SGHD45FF0Y",
        "part_number": "S0B84A",
        "subscription_key": SecretStr("secret"),
        "service_catalog_region_id": "ap-northeast",
        "dscc_region_code": "jp1",
        "cloudinit_url": "https://169.254.239.27/cloudinit",
        "network": NetworkConfig(
            mgmt_ipv4="10.64.154.225",
            mask="255.255.248.0",
            gateway="10.64.159.254",
            dns=["10.203.96.10"],
            ntp="ntp.example.com",
            timezone="Asia/Kolkata",
        ),
        "dscc_setup": DsccSetupConfig(system_name="array01", country="India"),
    }
    data.update(overrides)
    return ArrayWorkItem(**data)


def _service(tmp_path, **factories) -> OnboardingService:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    return OnboardingService(Settings(), store, InMemoryEventBus(), **factories)


def _provision_factory(result: ProvisionResult, *, emit_phase=None):
    def factory(settings, progress):
        class Service:
            async def provision(self, item, *, dry_run=False):
                if emit_phase is not None:
                    progress(emit_phase, "DONE: registered")
                return result

        return Service()

    return factory


def _browser_factory(result: BrowserResultStatus, *, status_message: str | None = None):
    def factory(settings, arg):
        on_status = arg if callable(arg) else (lambda message: None)

        class Adapter:
            async def run(self, item, run_id, *, auto_submit=False):
                if status_message:
                    on_status(status_message)
                return result

        return Adapter()

    return factory


async def test_create_run_persists_work_item_and_event(tmp_path):
    service = _service(tmp_path)
    run = service.create_run(_item())
    assert run.status == RunStatus.READY
    assert service.get_work_item(run.run_id).serial_number == "SGHD45FF0Y"
    assert [e.event_type for e in service.list_events(run.run_id)] == ["run.created"]


async def test_create_run_records_mode_and_initial_phase(tmp_path):
    service = _service(tmp_path)
    run = service.create_run(_item(), mode=RunMode.PROVISION_ONLY)
    assert run.mode == RunMode.PROVISION_ONLY
    assert run.current_phase == WorkflowPhase.STORAGE_DISCOVER  # first enabled provision step

    verify_run = service.create_run(_item(), mode=RunMode.VERIFY_ONLY)
    assert verify_run.current_phase == WorkflowPhase.CONFIG_VERIFY


async def test_provision_advance_is_selection_aware(tmp_path):
    # A custom run that drops cloudinit: GreenLake should advance straight to DSCC.
    result = ProvisionResult(serial="SGHD45FF0Y", succeeded=True)
    result.phases.append(PhaseOutcome(WorkflowPhase.GL_REGISTER_DEVICE, DONE, "registered"))
    service = _service(tmp_path, provision_factory=_provision_factory(result))
    run = service.create_run(_item(), mode=RunMode.CUSTOM, selected_steps=["greenlake", "dscc"])
    service.start_provision(run.run_id)
    await service.wait(run.run_id)
    assert service.get_run(run.run_id).current_phase == WorkflowPhase.DSCC_SETUP_SYSTEM


async def test_provision_success_advances_to_cloudinit(tmp_path):
    result = ProvisionResult(serial="SGHD45FF0Y", succeeded=True)
    result.phases.append(PhaseOutcome(WorkflowPhase.GL_REGISTER_DEVICE, DONE, "registered"))
    service = _service(
        tmp_path,
        provision_factory=_provision_factory(result, emit_phase=WorkflowPhase.GL_REGISTER_DEVICE),
    )
    run = service.create_run(_item())
    service.start_provision(run.run_id)
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.READY
    assert updated.current_phase == WorkflowPhase.CLOUDINIT_CONNECT
    types = [e.event_type for e in service.list_events(run.run_id)]
    assert "phase.progress" in types and "step.completed" in types


async def test_provision_failure_is_retryable_and_warnings_collected(tmp_path):
    result = ProvisionResult(serial="SGHD45FF0Y", error="HTTP 400 — boom")
    result.phases.append(PhaseOutcome(WorkflowPhase.GL_APPLY_SUBSCRIPTION, WARNING, "no seat"))
    result.phases.append(PhaseOutcome(WorkflowPhase.GL_REGISTER_DEVICE, FAILED, "boom"))
    service = _service(tmp_path, provision_factory=_provision_factory(result))
    run = service.create_run(_item())
    service.start_provision(run.run_id)
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.RETRYABLE_FAILURE
    assert any("no seat" in w for w in updated.warnings)


async def test_cloudinit_review_then_submit_succeeds(tmp_path):
    service = _service(
        tmp_path,
        cloudinit_factory=_browser_factory(BrowserResultStatus.SUCCEEDED, status_message="review_ready"),
    )
    run = service.create_run(_item())
    service.start_cloudinit(run.run_id, cloudinit_url="https://169.254.184.89/cloudinit")
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.READY
    assert updated.current_phase == WorkflowPhase.DSCC_SETUP_SYSTEM
    # the runtime URL override is persisted on the work item
    assert service.get_work_item(run.run_id).cloudinit_url == "https://169.254.184.89/cloudinit"
    types = [e.event_type for e in service.list_events(run.run_id)]
    assert "operator.review_ready" in types


async def test_cloudinit_browser_problem_is_retryable(tmp_path):
    # WAITING without review_ready means the browser never got to Review -> retryable failure.
    service = _service(tmp_path, cloudinit_factory=_browser_factory(BrowserResultStatus.WAITING_FOR_OPERATOR))
    run = service.create_run(_item())
    service.start_cloudinit(run.run_id)
    await service.wait(run.run_id)
    assert service.get_run(run.run_id).status == RunStatus.RETRYABLE_FAILURE


async def test_cloudinit_refused_submit_is_retryable_with_clear_reason(tmp_path):
    # The Review guard re-filled but the Network values kept decaying, so it never submitted.
    # Nothing was applied -> retryable, with a message that says exactly that.
    service = _service(
        tmp_path,
        cloudinit_factory=_browser_factory(BrowserResultStatus.FAILED_RETRYABLE, status_message="refused"),
    )
    run = service.create_run(_item())
    service.start_cloudinit(run.run_id)
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.RETRYABLE_FAILURE
    messages = [e.message for e in service.list_events(run.run_id)]
    assert any("Refused to submit" in m and "nothing was applied" in m for m in messages)


async def test_dscc_stops_at_credentials_gate(tmp_path):
    service = _service(tmp_path, dscc_factory=_browser_factory(BrowserResultStatus.WAITING_FOR_OPERATOR))
    run = service.create_run(_item())
    service.start_dscc(run.run_id, cdp_url="http://localhost:9222")
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.WAITING_FOR_OPERATOR
    assert any(e.event_type == "operator.credentials_ready" for e in service.list_events(run.run_id))

    completed = service.mark_complete(run.run_id)
    assert completed.status == RunStatus.SUCCEEDED
    assert completed.current_phase == WorkflowPhase.COMPLETE


async def test_dscc_attach_failure_is_retryable(tmp_path):
    service = _service(tmp_path, dscc_factory=_browser_factory(BrowserResultStatus.FAILED_RETRYABLE))
    run = service.create_run(_item())
    service.start_dscc(run.run_id, cdp_url="http://localhost:9222")
    await service.wait(run.run_id)
    assert service.get_run(run.run_id).status == RunStatus.RETRYABLE_FAILURE


async def _complete(service, run_id):
    """Drive a run to COMPLETE the way DSCC does, so verification runs on a finished run."""
    service.mark_complete(run_id)


async def test_verify_success_emits_report_without_changing_run_status(tmp_path):
    report = VerificationReport(
        reachable=True,
        checks=[
            FieldCheck(
                field="Gateway", expected="10.0.0.1", actual="10.0.0.1",
                status=FieldCheckStatus.PASS, critical=True,
            )
        ],
    )
    service = _service(tmp_path, verify_fn=lambda item, username, password: report)
    run = service.create_run(_item())
    await _complete(service, run.run_id)

    service.start_verify(run.run_id, username="3paradm", password="pw")
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.SUCCEEDED  # verification never changes the run outcome
    assert updated.current_phase == WorkflowPhase.COMPLETE
    done = [e for e in service.list_events(run.run_id) if e.event_type == "verify.completed"]
    assert done and done[-1].data["report"]["checks"][0]["field"] == "Gateway"


async def test_verify_unreachable_emits_failure_but_keeps_run_succeeded(tmp_path):
    report = VerificationReport(reachable=False, error="Could not reach the array")
    service = _service(tmp_path, verify_fn=lambda item, username, password: report)
    run = service.create_run(_item())
    await _complete(service, run.run_id)

    service.start_verify(run.run_id, username="u", password="p")
    await service.wait(run.run_id)

    assert service.get_run(run.run_id).status == RunStatus.SUCCEEDED
    assert any(e.event_type == "verify.failed" for e in service.list_events(run.run_id))


async def test_verify_exception_never_unsucceeds_the_run(tmp_path):
    def boom(item, username, password):
        raise RuntimeError("ssh library blew up")

    service = _service(tmp_path, verify_fn=boom)
    run = service.create_run(_item())
    await _complete(service, run.run_id)

    service.start_verify(run.run_id, username="u", password="p")
    await service.wait(run.run_id)

    updated = service.get_run(run.run_id)
    assert updated.status == RunStatus.SUCCEEDED  # the guard must not mark a finished run retryable
    assert any(e.event_type == "verify.failed" for e in service.list_events(run.run_id))


async def test_concurrent_step_rejected(tmp_path):
    release = asyncio.Event()

    def blocking_factory(settings, on_status):
        class Adapter:
            async def run(self, item, run_id):
                await release.wait()
                return BrowserResultStatus.SUCCEEDED

        return Adapter()

    service = _service(tmp_path, cloudinit_factory=blocking_factory)
    run = service.create_run(_item())
    service.start_cloudinit(run.run_id)
    with pytest.raises(RunBusyError):
        service.start_cloudinit(run.run_id)
    release.set()
    await service.wait(run.run_id)


async def test_crash_in_step_marks_retryable(tmp_path):
    def exploding_factory(settings, on_status):
        class Adapter:
            async def run(self, item, run_id):
                raise RuntimeError("kaboom")

        return Adapter()

    service = _service(tmp_path, cloudinit_factory=exploding_factory)
    run = service.create_run(_item())
    service.start_cloudinit(run.run_id)
    await service.wait(run.run_id)

    assert service.get_run(run.run_id).status == RunStatus.RETRYABLE_FAILURE
    assert any(e.event_type == "step.crashed" for e in service.list_events(run.run_id))
