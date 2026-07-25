import asyncio

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService, RunBusyError
from alletra_onboard.application.onboarding.greenlake_provision import DONE, FAILED, WARNING, PhaseOutcome, ProvisionResult
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


def _service(tmp_path, *, settings: Settings | None = None, **factories) -> OnboardingService:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    return OnboardingService(settings or Settings(), store, InMemoryEventBus(), **factories)


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


def _prov_intent():
    from alletra_onboard.domain.shared import EndpointCreds
    from alletra_onboard.domain.provisioning import ProvisioningIntent

    def creds(host):
        return EndpointCreds(host=host, username="u", password=SecretStr("p"))

    return ProvisioningIntent.from_simple(
        host_set_name="HS", array=creds("a"), vcenter=creds("vc"),
        switch_f1=creds("sw1"), switch_f2=creds("sw2"),
        name_prefix="V", size_gib=10, count=1,
    )


async def test_get_storage_objects_builds_the_dropdown_palette(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import storage_provision as sp
    from alletra_onboard.domain.shared import normalize_wwpn
    from alletra_onboard.domain.discovery import DiscoveryReport, HostHba

    service = _service(tmp_path)
    run = service.create_run(_item(), provisioning_intent=_prov_intent())
    # discovery is required for the palette (it supplies the membership hosts)
    service._discovery[run.run_id] = DiscoveryReport(host_hbas=[
        HostHba(host_name="esx1", wwpn=normalize_wwpn("10:00:00:00:00:00:00:a1"), fabric="odd"),
        HostHba(host_name="esx1", wwpn=normalize_wwpn("10:00:00:00:00:00:00:b1"), fabric="even"),
    ])
    monkeypatch.setattr(sp, "read_array_objects", lambda intent: {
        "cpgs": ["SSD_r6"], "hosts": ["existing_host"], "host_sets": ["existing_hs"],
        "volumes": ["existing_vol"], "volume_sets": [], "error": None,
    })
    objs = service.get_storage_objects(run.run_id)
    assert objs.existing_hosts == ["existing_host"] and objs.existing_cpgs == ["SSD_r6"]
    assert objs.new_volumes == ["V"] and objs.new_host_sets == ["HS"]  # from _prov_intent
    assert objs.discovered_hosts[0].name == "esx1" and "both fabrics" in objs.discovered_hosts[0].status


async def test_set_provisioning_builder_persists_membership_vvsets_and_exports(tmp_path):
    from alletra_onboard.domain.provisioning import ExportRequest, HostSetRequest, ProvisioningBuilder

    service = _service(tmp_path)
    run = service.create_run(_item(), provisioning_intent=_prov_intent())
    comp = service.set_provisioning_builder(run.run_id, ProvisioningBuilder(
        host_sets=[HostSetRequest(name="HS", members=["esx1", "esx2"])],
        exports=[ExportRequest(source_kind="volume", source_name="V", target_kind="hostset", target_name="HS", lun=5)],
        vvsets={"myvvset": ["V"]},
    ))
    assert comp.host_sets[0].members == ["esx1", "esx2"] and comp.exports[0].lun == 5
    # composed relationships are persisted onto the run's intent for preview/apply
    saved = service.get_provisioning_intent(run.run_id)
    assert saved.exports[0].source_name == "V"
    assert saved.host_sets[0].members == ["esx1", "esx2"]
    assert saved.volumes[0].vvset == "myvvset"


async def test_path_verify_emits_per_host_report(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import path_verify as pv
    from alletra_onboard.domain.discovery import DiscoveryReport
    from alletra_onboard.domain.provisioning import HostPathStatus, PathVerification

    service = _service(tmp_path)
    run = service.create_run(_item(), provisioning_intent=_prov_intent())
    service._discovery[run.run_id] = DiscoveryReport()  # tier-2 needs discovery present
    monkeypatch.setattr(pv, "verify_provisioned_paths", lambda intent, discovery: PathVerification(
        hosts=[HostPathStatus(host="esx1", verdict="live", hbas_with_paths=2, fabrics=["odd", "even"], detail="ok")]))

    service.start_path_verify(run.run_id)
    await service.wait(run.run_id)
    verified = next(e for e in service.list_events(run.run_id) if e.event_type == "storage.paths.verified")
    assert verified.data["verification"]["hosts"][0]["verdict"] == "live"
    # report-only: the run is not failed by a verdict
    assert service.get_run(run.run_id).status == RunStatus.WAITING_FOR_OPERATOR


async def test_start_asbuilt_reads_array_and_produces_downloadable_docx(tmp_path, monkeypatch):
    from alletra_onboard.application.documents import steps as doc_steps

    canned = {
        "showsys -d": ("System Name : TEST-01\nSystem Model : HPE Alletra Storage MP\n"
                       "Serial Number : SGH1\nNumber of Nodes : 2\n"
                       "---Raw System Capacity (MiB)---\nTotal Capacity : 36608000\n"),
        "shownet": ("IP Address Netmask\n10.0.0.10 255.255.255.0\n\n"
                    "Default IPv4 route : 10.0.0.1\nNTP server : ntp.x\nDNS server : 10.1.1.1\n"),
        "showversion": "Release version 10.5.51\n",
        "shownode": "Node Name Encl Master InCluster Mem(MiB) Up\n0 SN-0 1:1 Yes Yes 257498 x\n",
        "showcage": "Id Name Drives\n1 cage1 10\n",
        "showpd": "Id CagePos Type RPM State Total Free Cap\n0 1:1 SSD N/A normal 1 1 3840\n",
        "showcpg": "Id Name Warn VVs\n0 SSD_r6 - 8\n",
        "showport": "N:S:P Mode State Node Port Type Protocol Label\n0:3:1 target ready X 2031 host FC -\n",
        "showport -par": "N:S:P Connmode ConnType CfgRate MaxRate\n0:3:1 host point auto 32Gbps\n",
        "showinventory -csvtable": "ID,Name\nx,TEST-01\n",
        "checkhealth -svc -detail": "Checking alert\nComponent Summary Description Qty\nAlert New 1\n---\n1 total 1\n",
    }

    class FakeCli:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def run(self, cmd, timeout=None):
            return canned.get(cmd, "")

    monkeypatch.setattr(doc_steps, "make_array_cli", lambda creds: FakeCli())

    service = _service(tmp_path)
    run = service.create_run(_item())
    service.start_asbuilt(run.run_id, username="3paradm", password="pw", customer="ACME Corp")
    await service.wait(run.run_id)

    ev = next(e for e in service.list_events(run.run_id) if e.event_type == "asbuilt.generated")
    assert ev.data["customer"] == "ACME Corp" and ev.data["serial"] == "SGH1"
    docx_bytes = service.get_asbuilt(run.run_id)
    assert docx_bytes and docx_bytes[:2] == b"PK"  # a .docx is a zip


async def test_pending_sheet_stash_mints_run_and_preserves_intent(tmp_path):
    # ADR 0005 revision: the sheet is held server-side (with device passwords) until a mode is
    # chosen; create_run_from_pending then mints the run and preserves the provisioning intent.
    from alletra_onboard.application.service import PendingSheetNotFoundError

    service = _service(tmp_path)
    intent = _prov_intent()
    token = service.stash_pending_sheet(_item(), intent)

    run = service.create_run_from_pending(token, mode=RunMode.BOTH)
    assert run.mode == RunMode.BOTH
    assert run.current_phase == WorkflowPhase.PREFLIGHT  # BOTH starts at GreenLake/preflight
    # the intent (with passwords) round-tripped through the durable stash into the run
    restored = service.get_provisioning_intent(run.run_id)
    assert restored.array.host == "a"
    assert restored.array.password.get_secret_value() == "p"

    # single-use: the hold is consumed, so a second mint fails cleanly
    with pytest.raises(PendingSheetNotFoundError):
        service.create_run_from_pending(token, mode=RunMode.BOTH)


async def test_discover_then_zoning_then_provision_flow(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import discovery as sd
    from alletra_onboard.application.provisioning import storage_provision as sp
    from alletra_onboard.application.provisioning import zoning as sz
    from alletra_onboard.domain.discovery import DiscoveryReport
    from alletra_onboard.domain.zoning import ExpectedZone, ZoneRemediation, ZoningReport
    from alletra_onboard.domain.provisioning import (
        ActionOutcome,
        PlannedAction,
        ProvisioningPlan,
        ProvisioningResult,
    )

    monkeypatch.setattr(sd, "discover", lambda intent, progress=None: DiscoveryReport(notes=[]))
    zoning_report = ZoningReport(
        expected=[ExpectedZone(fabric="odd", switch_host="sw1", name="z", host_wwpn="A", array_wwpn="B")],
        remediations=[ZoneRemediation(fabric="odd", switch_host="sw1", cfg_name="CFG", commands=['cfgenable "CFG"'])],
        proper=False,
    )
    monkeypatch.setattr(sz, "build_report", lambda intent, discovery: zoning_report)
    monkeypatch.setattr(sp, "build_plan", lambda intent, discovery: ProvisioningPlan(actions=[PlannedAction(kind="host", name="esx1", description="d")]))
    monkeypatch.setattr(sp, "apply_plan", lambda intent, discovery: ProvisioningResult(outcomes=[ActionOutcome(kind="host", name="esx1", status="created")]))

    service = _service(tmp_path)
    run = service.create_run(_item(), provisioning_intent=_prov_intent())

    service.start_discover(run.run_id)
    await service.wait(run.run_id)
    assert any(e.event_type == "discover.completed" for e in service.list_events(run.run_id))

    service.start_zoning_preview(run.run_id)
    await service.wait(run.run_id)
    assert service.get_run(run.run_id).status == RunStatus.WAITING_FOR_OPERATOR  # remediation needs confirm
    assert any(e.event_type == "zoning.previewed" for e in service.list_events(run.run_id))

    service.start_storage_preview(run.run_id)
    await service.wait(run.run_id)
    assert any(e.event_type == "storage.previewed" for e in service.list_events(run.run_id))

    service.start_storage_apply(run.run_id)
    await service.wait(run.run_id)
    applied = [e for e in service.list_events(run.run_id) if e.event_type == "storage.applied"]
    assert applied and applied[-1].data["result"]["outcomes"][0]["status"] == "created"


async def test_discovery_survives_a_service_restart(tmp_path, monkeypatch):
    # C7 (ADR 0011): step artifacts are durable — a new service over the SAME store (= app restart
    # mid-engagement) reads discovery back from run_artifacts instead of forcing a re-run.
    from alletra_onboard.application.provisioning import discovery as sd
    from alletra_onboard.domain.discovery import DiscoveryReport

    monkeypatch.setattr(sd, "discover", lambda intent, progress=None: DiscoveryReport(notes=["from-run-1"]))
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_item(), provisioning_intent=_prov_intent())
    service.start_discover(run.run_id)
    await service.wait(run.run_id)

    restarted = OnboardingService(Settings(), store, InMemoryEventBus())
    assert restarted.discovery_zoning._discovery.get(run.run_id) is None  # nothing in memory...
    report = restarted.discovery_zoning.require_discovery(run.run_id)     # ...read through the store
    assert report.notes == ["from-run-1"]


async def test_zoning_before_discovery_is_a_precondition_error(tmp_path):
    from alletra_onboard.application.service import StepPreconditionError

    service = _service(tmp_path)
    run = service.create_run(_item(), provisioning_intent=_prov_intent())
    with pytest.raises(StepPreconditionError):
        service.start_zoning_preview(run.run_id)


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
