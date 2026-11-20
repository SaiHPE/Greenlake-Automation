"""Stage 1 & Stage 2 least-privilege checks (STANDARD S2, S3, ADR 0031)."""

from __future__ import annotations

import asyncio
import inspect
import io
import re
import threading
import time
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from alletra_onboard.adapters import device_trust
from alletra_onboard.adapters.array import wsapi_client
from alletra_onboard.adapters.array.rc_cli_client import ArrayRcCliClient
from alletra_onboard.adapters.array.snap_cli_client import ArraySnapCliClient
from alletra_onboard.adapters.array.wsapi_client import WsapiReader
from alletra_onboard.adapters.array.wsapi_writer import WsapiWriter
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.provisioning import storage_provision
from alletra_onboard.application.provisioning.clients import make_wsapi
from alletra_onboard.application.replication import failover as replication_failover
from alletra_onboard.application.replication.clients import make_rc_writer
from alletra_onboard.application.runs.coordinator import RunBusyError, StepPreconditionError
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.runs.writer_clients import make_wsapi_writer
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.application.snapshots.clients import make_snap_writer
from alletra_onboard.config import Settings
from alletra_onboard.domain.approval import Approval, ApprovalError
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, RunMode
from alletra_onboard.domain.plan_objects import RcPlanObjects, SnapPlanObjects
from alletra_onboard.domain.provisioning import (
    ExportRequest,
    HostSetRequest,
    ProvisioningBuilder,
    ProvisioningIntent,
    VolumeRequest,
)
from alletra_onboard.domain.replication import ProtectionRequest, ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.trust import DeviceKey, TrustKind


class _ReadOnlyFakeSdk:
    """Records every SDK call and returns minimal valid payloads for reads."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __getattr__(self, name: str):
        def _call(*_args, **_kwargs):
            self.calls.append(name)
            if name == "getStorageSystemInfo":
                return {"name": "array-a"}
            if name == "getRemoteCopyGroup":
                return {"name": "grp1"}
            return {"members": []}

        return _call


class _RecordingSdk:
    """Fake hpe3parclient.HPE3ParClient recording every mutating SDK call."""

    HOST_PERSONA_VMWARE = 8
    HOST_PERSONA_WINDOWS_SERVER = 11
    HOST_PERSONA_GENERIC_ALUA = 2
    HOST_EDIT_ADD = 1
    SET_MEM_ADD = 1

    def __init__(self, writes: list[tuple[str, tuple[Any, ...]]], api_url: str, **_kwargs: Any) -> None:
        self.api_url = api_url
        self.writes = writes
        self.http = type("_Http", (), {"request": lambda *_a, **_kw: None})()

    def login(self, _u: str, _p: str) -> None:
        return None

    def logout(self) -> None:
        return None

    def getCPGs(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": [{"name": "SSD_r6", "freeSpaceMiB": 100_000}]}

    def getHosts(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": []}

    def getHostSets(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": []}

    def getHostSet(self, _name: str) -> dict[str, Any]:
        from hpe3parclient import exceptions as hpe_exc

        raise hpe_exc.HTTPNotFound({"code": 23, "desc": "not found"})

    def getVolumes(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": []}

    def getVolumeSets(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": []}

    def getVolumeSet(self, _name: str) -> dict[str, Any]:
        from hpe3parclient import exceptions as hpe_exc

        raise hpe_exc.HTTPNotFound({"code": 23, "desc": "not found"})

    def getVLUNs(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": []}

    def createHost(self, name: str, **_kw: Any) -> None:
        self.writes.append(("createHost", (name,)))

    def createHostSet(self, name: str, **_kw: Any) -> None:
        self.writes.append(("createHostSet", (name,)))

    def createVolume(self, name: str, *_a: Any, **_kw: Any) -> None:
        self.writes.append(("createVolume", (name,)))

    def createVolumeSet(self, name: str, **_kw: Any) -> None:
        self.writes.append(("createVolumeSet", (name,)))

    def createVLUN(self, volume: str, **_kw: Any) -> None:
        self.writes.append(("createVLUN", (volume,)))

    def createSnapshot(self, name: str, volume: str, **_kw: Any) -> None:
        self.writes.append(("createSnapshot", (name, volume)))

    def stopRemoteCopy(self, name: str) -> None:
        self.writes.append(("stopRemoteCopy", (name,)))

    def recoverRemoteCopyGroupFromDisaster(self, name: str, action: int) -> None:
        self.writes.append(("recoverRemoteCopyGroupFromDisaster", (name, action)))


class _RecordingSsh:
    """Fake paramiko SSHClient recording every exec_command."""

    def __init__(self, sent: list[str]) -> None:
        self.sent = sent

    def exec_command(self, command: str, timeout: float | None = None):
        self.sent.append(command)
        return None, io.BytesIO(b""), io.BytesIO(b"")

    def close(self) -> None:
        return None


def _creds(host: str = "192.0.2.1") -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


def _work_item(serial: str = "SN001") -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number=serial,
        part_number="S0B84A",
        subscription_key=SecretStr("secret"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.1.1/cloudinit",
        network=NetworkConfig(
            mgmt_ipv4="192.0.2.1", mask="255.255.255.0", gateway="192.0.2.254",
            dns=["192.0.2.53"], ntp="ntp.example.com", timezone="UTC",
        ),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )


def _service_and_run(tmp_path: Path, *, replication: bool = False) -> tuple[OnboardingService, str]:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    intent = ProvisioningIntent(
        array=_creds("192.0.2.1"),
        vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"),
        switch_f2=_creds("192.0.2.4"),
        volumes=[VolumeRequest(name="vol_reviewed", size_gib=10, cpg="SSD_r6", vvset="vvs_reviewed")],
        host_sets=[HostSetRequest(name="hs_reviewed", members=["esx1"])],
        exports=[ExportRequest(source_kind="vvset", source_name="vvs_reviewed", target_kind="hostset", target_name="hs_reviewed")],
    )
    if replication:
        intent.replication = ReplicationIntent(
            peer=_creds("192.0.2.9"), failover_test=True,
            protections=[ProtectionRequest(vvset="vvs_reviewed", peer_cpg="SSD_r6")],
        )
    run = service.create_run(
        _work_item(), mode=RunMode.REPLICATE if replication else RunMode.PROVISION_ONLY, provisioning_intent=intent,
    )
    service.discovery_zoning.discovery[run.run_id] = DiscoveryReport(
        host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")],
    )
    return service, run.run_id


def _patch_fake_transports(monkeypatch: pytest.MonkeyPatch) -> tuple[list[tuple[str, tuple[Any, ...]]], list[str]]:
    wsapi_writes: list[tuple[str, tuple[Any, ...]]] = []
    ssh_writes: list[str] = []
    monkeypatch.setattr(device_trust, "device_ca_bundle", lambda: None)
    monkeypatch.setattr(device_trust, "bypass_proxy_for", lambda _h: None)
    monkeypatch.setattr(
        device_trust, "check_tls",
        lambda *_a, **_kw: DeviceKey(kind=TrustKind.TLS, key_type="certificate", data="", fingerprint="00" * 32),
    )
    monkeypatch.setattr(wsapi_client, "_pin_calls", lambda *_a, **_kw: None)
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda api_url, **kw: _RecordingSdk(wsapi_writes, api_url, **kw))
    monkeypatch.setattr(device_trust, "open_ssh", lambda *_a, **_kw: _RecordingSsh(ssh_writes))
    return wsapi_writes, ssh_writes


# ------------------------------------------------------------------ Stage 1 (S2)

def test_wsapi_reader_invokes_only_read_sdk_methods_and_exposes_no_writes():
    sdk = _ReadOnlyFakeSdk()
    reader = WsapiReader("192.0.2.1", "3paradm", "pw")
    reader._client = sdk

    args_for = {
        "find_host_by_wwn": ("10000090FA8B1111",),
        "remote_copy_group": ("grp1",),
    }
    public = sorted(
        name for name, obj in inspect.getmembers(WsapiReader, predicate=callable)
        if not name.startswith("_") and name not in ("connect", "close")
    )
    assert public, "expected public read methods on WsapiReader"
    for name in public:
        getattr(reader, name)(*args_for.get(name, ()))

    assert sdk.calls, "expected WsapiReader methods to query the SDK"
    non_reads = [c for c in sdk.calls if not c.startswith("get")]
    assert non_reads == [], f"WsapiReader invoked non-read SDK call(s): {non_reads}"

    writer_only = {
        name for name, obj in WsapiWriter.__dict__.items()
        if not name.startswith("_") and callable(obj)
    }
    assert writer_only and writer_only.isdisjoint(public)


def test_reader_and_writer_factories_return_distinct_privileges(tmp_path):
    service, run_id = _service_and_run(tmp_path)
    creds = _creds()
    approval = service.coordinator.issue_approval(run_id, "storage", {"A": creds})
    reader = make_wsapi(creds)
    writer = make_wsapi_writer(approval, "storage", "A")
    assert type(reader) is WsapiReader
    assert not isinstance(reader, WsapiWriter)
    assert isinstance(writer, WsapiWriter)
    assert isinstance(writer, WsapiReader)


# ------------------------------------------------------------------ Stage 2 (S3): single Approval( site

def test_approval_is_constructed_only_in_run_coordinator():
    src_root = Path(__file__).resolve().parents[2] / "src" / "alletra_onboard"
    pattern = re.compile(r"\bApproval\s*\(")
    hits: list[str] = []
    for path in sorted(src_root.rglob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if pattern.search(line):
                hits.append(f"{path.relative_to(src_root).as_posix()}:{lineno}")
    assert len(hits) == 1, f"expected exactly one Approval( site in src, found: {hits}"
    assert hits[0].startswith("application/runs/coordinator.py:")


# ------------------------------------------------------------------ Stage 2 (S3): real factory + real writer over fakes

def test_missing_wrong_purpose_wrong_side_and_wrong_run_produce_zero_writes(tmp_path, monkeypatch):
    wsapi_writes, ssh_writes = _patch_fake_transports(monkeypatch)
    service, run1 = _service_and_run(tmp_path, replication=True)
    run2 = service.create_run(
        _work_item("SN002"),
        mode=RunMode.PROVISION_ONLY,
        provisioning_intent=service.get_provisioning_intent(run1),
    ).run_id
    rc_objs = RcPlanObjects(ports=frozenset({"0:4:4"}))
    snap_objs = SnapPlanObjects(schedules=frozenset({("s1", "vol_reviewed")}))

    # Missing approval (None) -> refused at real factories and direct writer constructors, zero writes.
    none_approval: Any = None
    with pytest.raises(ApprovalError):
        make_wsapi_writer(none_approval, "storage", "A")
    with pytest.raises(ApprovalError):
        make_rc_writer(none_approval, "A", rc_objs)
    with pytest.raises(ApprovalError):
        make_snap_writer(none_approval, snap_objs)
    with pytest.raises(ApprovalError):
        WsapiWriter("192.0.2.1", "3paradm", "pw", approval=none_approval)
    with pytest.raises(ApprovalError):
        ArrayRcCliClient("192.0.2.1", "3paradm", "pw", approval=none_approval, objects=rc_objs)
    with pytest.raises(ApprovalError):
        ArraySnapCliClient("192.0.2.1", "3paradm", "pw", approval=none_approval, objects=snap_objs)
    with pytest.raises(ApprovalError):
        replication_failover.run_failover_test(none_approval, "zz_rc_test_rcg")

    # Wrong purpose and wrong side -> refused at real factories, zero writes.
    storage_app = service.coordinator.issue_approval(run1, "storage", {"A": _creds("192.0.2.1")})
    with pytest.raises(ApprovalError, match="storage, not failover"):
        make_wsapi_writer(storage_app, "failover", "A")
    with pytest.raises(ApprovalError, match="storage, not rc_partnership"):
        make_rc_writer(storage_app, "A", rc_objs)
    with pytest.raises(ApprovalError, match="storage, not snapshots"):
        make_snap_writer(storage_app, snap_objs)
    with pytest.raises(ApprovalError, match="does not include array B"):
        make_wsapi_writer(storage_app, "storage", "B")

    # Wrong run -> coordinator refuses to spawn run2 with run1's approval.
    async def _noop() -> None:
        return None

    with pytest.raises(ApprovalError, match="not valid for this run"):
        service.coordinator.spawn(run2, _noop(), approval=storage_app)

    assert wsapi_writes == []
    assert ssh_writes == []


def test_spent_approval_blocks_every_writer_with_zero_writes(tmp_path, monkeypatch):
    wsapi_writes, ssh_writes = _patch_fake_transports(monkeypatch)
    service, run1 = _service_and_run(tmp_path, replication=True)
    rc_objs = RcPlanObjects(ports=frozenset({"0:4:4"}))
    snap_objs = SnapPlanObjects(schedules=frozenset({("s1", "vol_reviewed")}))

    storage_app = service.coordinator.issue_approval(run1, "storage", {"A": _creds("192.0.2.1")})
    with make_wsapi_writer(storage_app, "storage", "A") as writer:
        storage_app.spent = True
        with pytest.raises(ApprovalError, match="already been used"):
            writer.ensure_volume("v1", "SSD_r6", 1024, "tpvv")
        with pytest.raises(ApprovalError, match="already been used"):
            writer.create_remote_copy_group("g1", target="B", mode="sync", peer_cpg="SSD_r6")
        with pytest.raises(ApprovalError, match="already been used"):
            writer.create_snapshot("v1", "v1.initial", read_only=True, expire_hours=2)
    with pytest.raises(ApprovalError, match="already been used"):
        make_wsapi_writer(storage_app, "storage", "A")

    rc_app = service.coordinator.issue_approval(run1, "rc_partnership", {"A": _creds("192.0.2.1")})
    with make_rc_writer(rc_app, "A", rc_objs) as rc_cli:
        rc_app.spent = True
        with pytest.raises(ApprovalError, match="already been used"):
            rc_cli.write("startrcopy")
    with pytest.raises(ApprovalError, match="already been used"):
        make_rc_writer(rc_app, "A", rc_objs)

    snap_app = service.coordinator.issue_approval(run1, "snapshots", {"A": _creds("192.0.2.1")})
    with make_snap_writer(snap_app, snap_objs) as snap_cli:
        snap_app.spent = True
        with pytest.raises(ApprovalError, match="already been used"):
            snap_cli.write('createsched -f "createsv -f -ro -exp 24h @vvname@.@y@@m@@d@@H@@M@@S@ vol_reviewed" "0 * * * *" s1')
    with pytest.raises(ApprovalError, match="already been used"):
        make_snap_writer(snap_app, snap_objs)

    assert wsapi_writes == []
    assert ssh_writes == []


# ------------------------------------------------------------------ Astra 2: cancel keeps run busy until thread exits

async def test_second_apply_cannot_start_while_cancelled_worker_thread_still_runs(tmp_path):
    service, run_id = _service_and_run(tmp_path)
    coord = service.coordinator
    entered = threading.Event()
    release = threading.Event()
    approval = coord.issue_approval(run_id, "storage", {"A": _creds()})

    def slow_write() -> str:
        entered.set()
        release.wait(timeout=5.0)
        return "done"

    async def worker() -> None:
        await coord.run_approved(approval, slow_write)

    coord.spawn(run_id, worker(), approval=approval)
    assert await asyncio.to_thread(entered.wait, 2.0), "worker thread never started"

    # Cancel the coroutine while the worker thread is still running.
    task = coord._tasks[run_id]
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert approval.spent is False
    assert coord.is_busy(run_id) is True
    with pytest.raises(RunBusyError, match="a step is already running for this run"):
        coord.issue_approval(run_id, "storage", {"A": _creds()})
    with pytest.raises(RunBusyError, match="a step is already running for this run"):
        service.set_provisioning_builder(run_id, ProvisioningBuilder(exports=[]))

    # Release the worker thread; its finally spends the approval and frees the run.
    release.set()
    for _ in range(200):
        if approval.spent:
            break
        await asyncio.sleep(0.01)
    assert approval.spent is True
    assert coord.is_busy(run_id) is False


# ------------------------------------------------------------------ Failover: empty POST refused (409)

def test_failover_post_requires_authorised_true(tmp_path, monkeypatch):
    wsapi_writes, _ = _patch_fake_transports(monkeypatch)
    service, run_id = _service_and_run(tmp_path, replication=True)
    called: list[str] = []

    def fake_failover(approval: Approval, group: str, **_kw: Any):
        assert approval.purpose == "failover" and not approval.spent
        assert approval.creds_for("failover", "A").host == "192.0.2.1"
        assert approval.creds_for("failover", "B").host == "192.0.2.9"
        called.append(group)
        from alletra_onboard.domain.replication import FailoverRecord
        return FailoverRecord(group=group, result="passed")

    monkeypatch.setattr(replication_failover, "run_failover_test", fake_failover)
    with TestClient(create_app(service)) as client:
        for body in (None, {}, {"authorised": False}, {"group": "zz_rc_test_rcg"}):
            resp = client.post(f"/runs/{run_id}/replication/failover-test", json=body)
            assert resp.status_code == 409
            assert resp.json()["detail"] == "Tick the approval for this plan first."
        assert called == [] and wsapi_writes == []

        ok = client.post(f"/runs/{run_id}/replication/failover-test", json={"authorised": True})
        assert ok.status_code == 200
        for _ in range(200):
            if any(e["event_type"] == "failover.completed" for e in client.get(f"/runs/{run_id}/events").json()["events"]):
                break
            time.sleep(0.01)
        assert called == ["zz_rc_test_rcg"]


# ------------------------------------------------------------------ Astra 3: builder save refused during preview; frozen inputs applied

async def test_builder_save_refused_during_preview_and_storage_applies_frozen_inputs(tmp_path, monkeypatch):
    wsapi_writes, _ = _patch_fake_transports(monkeypatch)
    service, run_id = _service_and_run(tmp_path)
    preview_entered = threading.Event()
    preview_release = threading.Event()
    real_build_plan = storage_provision.build_plan

    def blocking_build_plan(*args: Any, **kwargs: Any):
        preview_entered.set()
        preview_release.wait(timeout=5.0)
        return real_build_plan(*args, **kwargs)

    monkeypatch.setattr(storage_provision, "build_plan", blocking_build_plan)
    service.start_storage_preview(run_id)
    assert await asyncio.to_thread(preview_entered.wait, 2.0)

    # Builder save is refused while preview runs (RunBusyError -> 409).
    with pytest.raises(RunBusyError, match="a step is already running for this run"):
        service.set_provisioning_builder(
            run_id,
            ProvisioningBuilder(host_sets=[HostSetRequest(name="hs_edited", members=["esx1"])], exports=[]),
        )
    preview_release.set()
    await service.wait(run_id)

    preview_ev = next(e for e in service.list_events(run_id) if e.event_type == "storage.previewed")
    plan_id = preview_ev.data["plan"]["plan_id"]
    assert plan_id

    # Even if the stored intent is mutated after preview, apply writes ONLY the frozen reviewed inputs
    # through the real factory and real WsapiWriter.
    mutated = service.get_provisioning_intent(run_id).model_copy(deep=True)
    mutated.volumes = [VolumeRequest(name="vol_unreviewed", size_gib=10, cpg="SSD_r6", vvset="vvs_unreviewed")]
    service.store.save_provisioning_intent(run_id, mutated)

    service.start_storage_apply(run_id, approved_plan=plan_id)
    await service.wait(run_id)

    created_vols = [args[0] for kind, args in wsapi_writes if kind == "createVolume"]
    assert created_vols == ["vol_reviewed"]
    assert "vol_unreviewed" not in created_vols

    # A second apply with the same plan id is refused (plan was popped on apply).
    with pytest.raises(StepPreconditionError, match="run the provisioning preview first"):
        service.start_storage_apply(run_id, approved_plan=plan_id)

    # Editing the composition after a preview withdraws the held plan so apply is refused.
    wsapi_writes.clear()
    monkeypatch.setattr(storage_provision, "build_plan", real_build_plan)
    service.start_storage_preview(run_id)
    await service.wait(run_id)
    second_id = [e for e in service.list_events(run_id) if e.event_type == "storage.previewed"][-1].data["plan"]["plan_id"]
    service.set_provisioning_builder(
        run_id,
        ProvisioningBuilder(host_sets=[HostSetRequest(name="hs_after", members=["esx1"])], exports=[]),
    )
    with pytest.raises(StepPreconditionError, match="run the provisioning preview first"):
        service.start_storage_apply(run_id, approved_plan=second_id)
    assert wsapi_writes == []


async def test_partnership_service_apply_passes_rc_partnership_approval_for_both_sides(tmp_path, monkeypatch):
    """Stage 2 gap: partnership apply through OnboardingService issues an `rc_partnership` approval
    carrying both A and B credentials (and refusing `rc_groups`)."""
    from alletra_onboard.application.replication import partnership_apply as rc_partner_apply
    from alletra_onboard.application.replication import read as replication_read
    from alletra_onboard.domain.replication import (
        PortRole,
        RcipPortRequest,
        ReplicationArrayView,
        ReplicationOutcome,
        ReplicationResult,
    )

    service, run_id = _service_and_run(tmp_path, replication=True)
    intent = service.get_provisioning_intent(run_id).model_copy(deep=True)
    assert intent.replication is not None
    intent.replication.network = [
        RcipPortRequest(side="A", nsp="0:4:4", ip="10.93.18.11", netmask="255.255.254.0"),
        RcipPortRequest(side="A", nsp="1:4:4", ip="10.93.18.13", netmask="255.255.254.0"),
        RcipPortRequest(side="B", nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0"),
        RcipPortRequest(side="B", nsp="1:1:1", ip="10.93.18.20", netmask="255.255.254.0"),
    ]
    service.store.save_provisioning_intent(run_id, intent)

    view_a = ReplicationArrayView(
        host="192.0.2.1", name="ArrayA", system_id=100, os_version="10.5.55",
        ports={
            "0:4:4": PortRole(nsp="0:4:4", mode="peer", state="ready", type="free", protocol="IP"),
            "1:4:4": PortRole(nsp="1:4:4", mode="peer", state="ready", type="free", protocol="IP"),
        },
        vvsets={"vvs_reviewed": ["vol_reviewed"]}, volume_size_mib={"vol_reviewed": 10240},
        cpg_free_mib={"SSD_r6": 100_000},
    )
    view_b = ReplicationArrayView(
        host="192.0.2.9", name="ArrayB", system_id=200, os_version="10.5.55",
        ports={
            "0:1:1": PortRole(nsp="0:1:1", mode="peer", state="ready", type="free", protocol="IP"),
            "1:1:1": PortRole(nsp="1:1:1", mode="peer", state="ready", type="free", protocol="IP"),
        },
        cpg_free_mib={"SSD_r6": 100_000},
    )
    monkeypatch.setattr(replication_read, "read_array", lambda creds, progress=None: view_a if creds.host == "192.0.2.1" else view_b)

    seen_hosts: list[tuple[str, str]] = []

    def fake_partner(plan, provisioning, approval, *, rc_cli_factory=None, progress=None):
        assert plan.sets_up_partnership is True
        a_host = approval.creds_for("rc_partnership", "A").host
        b_host = approval.creds_for("rc_partnership", "B").host
        with pytest.raises(ApprovalError):
            approval.creds_for("rc_groups", "B")
        seen_hosts.append((a_host, b_host))
        return ReplicationResult(
            outcomes=[ReplicationOutcome(kind="target", name="ArrayB", where="A", status="created")],
            removals_a=["removercopytarget ArrayB"],
        )

    monkeypatch.setattr(rc_partner_apply, "apply_partnership", fake_partner)

    service.start_replication_preview(run_id)
    await service.wait(run_id)
    plan_id = next(e for e in service.list_events(run_id) if e.event_type == "replication.previewed").data["plan"]["plan_id"]
    service.start_replication_apply(run_id, approved_plan=plan_id)
    await service.wait(run_id)

    assert seen_hosts == [("192.0.2.1", "192.0.2.9")]
    assert any(e.event_type == "replication.applied" for e in service.list_events(run_id))


def test_writer_factory_modules_do_not_reexport_writer_classes() -> None:
    """STANDARD S2: apply modules may only obtain writers through the approval-checked factories,
    never by importing the writer class directly from the factory module at runtime."""
    from alletra_onboard.application.replication import clients as rc_clients
    from alletra_onboard.application.runs import writer_clients
    from alletra_onboard.application.snapshots import clients as snap_clients

    assert writer_clients.__all__ == ["make_wsapi_writer"]
    assert not hasattr(writer_clients, "WsapiWriter")
    assert rc_clients.__all__ == ["make_rc_writer"]
    assert not hasattr(rc_clients, "ArrayRcCliClient")
    assert snap_clients.__all__ == ["make_snap_writer"]
    assert not hasattr(snap_clients, "ArraySnapCliClient")

