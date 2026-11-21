"""Stage 3 least-privilege checks (STANDARD S5, ADR 0031): undo on record before every write."""

from __future__ import annotations

import asyncio
import io
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters import device_trust
from alletra_onboard.adapters.array import wsapi_client
from alletra_onboard.adapters.persistence.sqlite import ARTIFACT_RETENTION_RUNS, SqliteRunStore
from alletra_onboard.application.documents.asbuilt_model import AsBuiltData
from alletra_onboard.application.provisioning import apply as prov_apply
from alletra_onboard.application.provisioning import storage_provision
from alletra_onboard.application.replication import apply as rc_apply
from alletra_onboard.application.replication import failover as replication_failover
from alletra_onboard.application.replication import partnership_apply as rc_partner_apply
from alletra_onboard.application.replication import read as replication_read
from alletra_onboard.application.replication.steps import (
    LINK_CHECK_ARTIFACT,
)
from alletra_onboard.application.replication.steps import (
    RESULT_ARTIFACT as RC_RESULT_ARTIFACT,
)
from alletra_onboard.application.runs.apply_record import APPLY_RECORD_ARTIFACT
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.application.snapshots import apply as snap_apply
from alletra_onboard.application.snapshots import read as snapshots_read
from alletra_onboard.config import Settings
from alletra_onboard.domain.approval import Approval, ApprovalError
from alletra_onboard.domain.discovery import DiscoveryReport, HostHba
from alletra_onboard.domain.errors import WsapiError
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunMode,
    RunRecord,
    RunStatus,
)
from alletra_onboard.domain.provisioning import (
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    ProvisioningResult,
    RemovalItem,
    VolumeRequest,
)
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
    LinkCheck,
    LinkCheckResult,
    LinkPair,
    PortRole,
    ProtectionRequest,
    RcipPort,
    RcipPortRequest,
    RcLink,
    RcTarget,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
)
from alletra_onboard.domain.shared import ArrayVolumeRecord, EndpointCreds
from alletra_onboard.domain.snapshots import (
    ArraySchedule,
    SnapshotArrayView,
    SnapshotIntent,
    SnapshotPlan,
    SnapshotRequest,
)
from alletra_onboard.domain.trust import DeviceKey, TrustKind

A_HOST, B_HOST = "192.0.2.1", "192.0.2.9"
CRASH_CODE = 99


def _creds(host: str = A_HOST) -> EndpointCreds:
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
            mgmt_ipv4=A_HOST, mask="255.255.255.0", gateway="192.0.2.254",
            dns=["192.0.2.53"], ntp="ntp.example.com", timezone="UTC",
        ),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )


def _intent(*, replication: bool = False, partnership: bool = False, snapshots: bool = False) -> ProvisioningIntent:
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        volumes=[VolumeRequest(name="vol_reviewed", size_gib=10, cpg="SSD_r6", vvset="vvs_reviewed")],
        host_sets=[HostSetRequest(name="hs_reviewed", members=["esx1"])],
        exports=[ExportRequest(source_kind="vvset", source_name="vvs_reviewed",
                               target_kind="hostset", target_name="hs_reviewed")],
    )
    if replication:
        net = [
            RcipPortRequest(side="A", nsp="0:4:4", ip="10.93.18.11", netmask="255.255.254.0"),
            RcipPortRequest(side="A", nsp="1:4:4", ip="10.93.18.13", netmask="255.255.254.0"),
            RcipPortRequest(side="B", nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0"),
            RcipPortRequest(side="B", nsp="1:1:1", ip="10.93.18.20", netmask="255.255.254.0"),
        ] if partnership else []
        intent.replication = ReplicationIntent(
            peer=_creds(B_HOST), failover_test=True, network=net,
            protections=[ProtectionRequest(vvset="vvs_reviewed", peer_cpg="SSD_r6")],
        )
    if snapshots:
        intent.snapshots = SnapshotIntent(requests=[
            SnapshotRequest(source="vvs_reviewed", kind="set", snapshot_now=True,
                            every=4, unit="hours", expire_hours=24, name="sched_one"),
            SnapshotRequest(source="vol_two", kind="volume", snapshot_now=False,
                            every=6, unit="hours", expire_hours=24, name="sched_two"),
        ])
    return intent


class _FakeSdk:
    """In-memory fake HPE3ParClient supporting storage, replication groups, snapshots, and crash hooks."""

    HOST_PERSONA_VMWARE = 8
    HOST_PERSONA_WINDOWS_SERVER = 11
    HOST_PERSONA_GENERIC_ALUA = 2
    HOST_EDIT_ADD = 1
    SET_MEM_ADD = 1

    def __init__(self, state: dict[str, Any], *, crash_on: str | None = None) -> None:
        self.state = state
        self.crash_on = crash_on
        self.http = type("_Http", (), {"request": lambda *_a, **_kw: None})()

    def _maybe_crash(self, op: str) -> None:
        if self.crash_on == op:
            os._exit(CRASH_CODE)

    def login(self, _u: str, _p: str) -> None:
        return None

    def logout(self) -> None:
        return None

    def getCPGs(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": [{"name": "SSD_r6", "freeSpaceMiB": 100_000}]}

    def getHosts(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": list(self.state.setdefault("hosts", []))}

    def getHostSets(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": [{"name": k, "setmembers": v} for k, v in self.state.setdefault("host_sets", {}).items()]}

    def getHostSet(self, name: str) -> dict[str, Any]:
        from hpe3parclient import exceptions as hpe_exc

        sets = self.state.setdefault("host_sets", {})
        if name not in sets:
            raise hpe_exc.HTTPNotFound({"code": 23, "desc": "not found"})
        return {"name": name, "setmembers": list(sets[name])}

    def getVolumes(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": list(self.state.setdefault("volumes", []))}

    def getVolumeSets(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": [{"name": k, "setmembers": v} for k, v in self.state.setdefault("vvsets", {}).items()]}

    def getVolumeSet(self, name: str) -> dict[str, Any]:
        from hpe3parclient import exceptions as hpe_exc

        sets = self.state.setdefault("vvsets", {})
        if name not in sets:
            raise hpe_exc.HTTPNotFound({"code": 23, "desc": "not found"})
        return {"name": name, "setmembers": list(sets[name])}

    def getVLUNs(self) -> dict[str, list[dict[str, Any]]]:
        return {"members": list(self.state.setdefault("vluns", []))}

    def createHost(self, name: str, FCWwns: list[str] | None = None, **_kw: Any) -> None:
        self._maybe_crash(f"createHost:{name}")
        paths = [{"wwn": w} for w in (FCWwns or [])]
        self.state.setdefault("hosts", []).append({"name": name, "persona": 8, "FCPaths": paths})

    def createHostSet(self, name: str, setmembers: list[str] | None = None, **_kw: Any) -> None:
        self._maybe_crash(f"createHostSet:{name}")
        self.state.setdefault("host_sets", {})[name] = list(setmembers or [])

    def createVolume(self, name: str, cpg: str, size_mib: int, **_kw: Any) -> None:
        self._maybe_crash(f"createVolume:{name}")
        self.state.setdefault("volumes", []).append({
            "name": name, "sizeMiB": size_mib, "userCPG": cpg, "provisioningType": 2,
        })

    def createVolumeSet(self, name: str, setmembers: list[str] | None = None, **_kw: Any) -> None:
        self._maybe_crash(f"createVolumeSet:{name}")
        self.state.setdefault("vvsets", {})[name] = list(setmembers or [])

    def createVLUN(self, volume: str, hostname: str = "", lun: int | None = None, **_kw: Any) -> None:
        self._maybe_crash(f"createVLUN:{volume}")
        vols = self.state["vvsets"][volume[4:]] if volume.startswith("set:") else [volume]
        next_lun = 0 if lun is None else lun
        for v in vols:
            self.state.setdefault("vluns", []).append({
                "volumeName": v, "hostname": hostname, "lun": next_lun, "active": False,
            })
            next_lun += 1

    def createSnapshotOfVolumeSet(self, _pattern: str, vvset: str, **_kw: Any) -> None:
        self._maybe_crash(f"createSetSnapshot:{vvset}")
        for m in self.state.get("vvsets", {}).get(vvset, []):
            self.state.setdefault("volumes", []).append({
                "name": f"{m}.initial", "copyOf": m, "sizeMiB": 10240, "userCPG": "SSD_r6",
                "readOnly": True, "expirationTime8601": "2026-11-21T12:00:00Z",
            })

    def createRemoteCopyGroup(self, name: str, _targets: list[dict[str, Any]], **_kw: Any) -> None:
        self._maybe_crash(f"createRemoteCopyGroup:{name}")
        self.state.setdefault("groups", []).append(name)

    def modifyRemoteCopyGroup(self, _name: str, **_kw: Any) -> None:
        return None

    def addVolumeToRemoteCopyGroup(self, group: str, volume: str, _targets: list[dict[str, Any]], **_kw: Any) -> None:
        self._maybe_crash(f"admit:{group}:{volume}")
        self.state.setdefault("admitted", []).append((group, volume))

    def startRemoteCopy(self, name: str) -> None:
        self._maybe_crash(f"start:{name}")
        self.state.setdefault("started", []).append(name)

    def stopRemoteCopy(self, name: str) -> None:
        self._maybe_crash(f"stop:{name}")
        self.state.setdefault("dr_calls", []).append(("stop", name))

    def recoverRemoteCopyGroupFromDisaster(self, name: str, action: int) -> None:
        self._maybe_crash(f"dr:{action}:{name}")
        self.state.setdefault("dr_calls", []).append((action, name))


class _FakePartnerSsh:
    """In-memory fake SSH for ArrayRcCliClient with optional crash trigger."""

    def __init__(self, side: str, state: dict[str, Any], *, crash_prefix: str | None = None) -> None:
        self.side = side
        self.state = state
        self.crash_prefix = crash_prefix

    def exec_command(self, command: str, timeout: float | None = None):
        if self.crash_prefix and command.startswith(self.crash_prefix):
            os._exit(CRASH_CODE)
        s = self.state[self.side]
        out = self._handle(command, s)
        return None, io.BytesIO(out.encode("utf-8")), io.BytesIO(b"")

    @staticmethod
    def _handle(command: str, s: dict[str, Any]) -> str:
        parts = command.split()
        if command.startswith("controlport rcip addr"):
            s["rcip"][parts[-1]] = (parts[-3], parts[-2])
            return "Remote Copy interface change successful.\n"
        if command.startswith("controlport rcip ping"):
            return "3 packets transmitted, 3 received, 0% packet loss, time 2035ms\n"
        if command == "startrcopy":
            s["rc"] = "Started"
            return "\n"
        if command.startswith("creatercopytarget"):
            s["targets"][parts[1]] = [lk.rsplit(":", 1) for lk in parts[3:]]
            return "\n"
        if command == "showport -rcip":
            return "N:S:P State HwAddr IPAddr Netmask Gateway MTU Rate\n" + "".join(
                f"{n} ready 00 {ip} {mask} - 1500 10Gbps\n" for n, (ip, mask) in s["rcip"].items()
            )
        if command in ("showrcopy", "showrcopy targets", "showrcopy links"):
            if not s["rc"]:
                return "Remote Copy is not configured on this system.\n"
            text = f"\nRemote Copy System Information\nStatus: {s['rc']}, Normal\n\nTarget Information\n\nName ID Type Status Options Policy\n"
            text += "".join(f"{t} 1 IP ready - mirror_config\n" for t in s["targets"])
            text += "\nLink Information\n\nTarget Node Address Status Options\n"
            text += "".join(f"{t} {nsp} {addr} Up -\n" for t, links in s["targets"].items() for nsp, addr in links)
            return text
        raise AssertionError(f"unexpected SSH command: {command}")

    def close(self) -> None:
        return None


class _FakeSnapSsh:
    """In-memory fake SSH for ArraySnapCliClient with optional crash trigger."""

    def __init__(self, schedules: list[ArraySchedule], *, crash_on: str | None = None) -> None:
        self.schedules = schedules
        self.crash_on = crash_on

    def exec_command(self, command: str, timeout: float | None = None):
        if self.crash_on and command.endswith(f" {self.crash_on}"):
            os._exit(CRASH_CODE)
        if command == "showsched":
            if not self.schedules:
                return None, io.BytesIO(b"No scheduled tasks listed\n"), io.BytesIO(b"")
            hdr = "SchedName File/Command Interval Min Hour DOM Month DOW CreatedBy Status Alert NextRunTime"
            rows = [
                f"{s.name} {s.command} {s.interval} {s.minute} {s.hour} {s.dom} {s.month} {s.dow} "
                f"{s.created_by} {s.status} {s.alert} {s.next_run}" for s in self.schedules
            ]
            out = "\n".join([hdr, *rows, "-" * 40, f"{len(rows)} total", ""])
            return None, io.BytesIO(out.encode("utf-8")), io.BytesIO(b"")
        if command.startswith("createsched "):
            m = re.match(r'^createsched -f "(.*)" "(.*)" (\S+)$', command)
            assert m is not None
            f = m.group(2).split()
            self.schedules.append(ArraySchedule(
                name=m.group(3), command=m.group(1), interval="-",
                minute=f[0], hour=f[1], dom=f[2], month=f[3], dow=f[4],
                created_by="3paradm", status="active", alert="Y", next_run="2026-11-20T04:00:00",
            ))
            return None, io.BytesIO(b""), io.BytesIO(b"")
        raise AssertionError(f"unexpected snap SSH command: {command}")

    def close(self) -> None:
        return None


def _patch_transports(sdk_factory, ssh_factory) -> None:
    device_trust.device_ca_bundle = lambda: None
    device_trust.bypass_proxy_for = lambda _h: None
    device_trust.check_tls = lambda *_a, **_kw: DeviceKey(
        kind=TrustKind.TLS, key_type="certificate", data="", fingerprint="00" * 32,
    )
    wsapi_client._pin_calls = lambda *_a, **_kw: None
    wsapi_client.HPE3ParClient = sdk_factory
    device_trust.open_ssh = ssh_factory


def _rc_views(*, with_partnership: bool) -> tuple[ReplicationArrayView, ReplicationArrayView]:
    if with_partnership:
        a = ReplicationArrayView(
            host=A_HOST, name="ArrayA", system_id=100, os_version="10.5.55", rc_status="Started",
            rcip_ports=[
                RcipPort(nsp="0:4:4", ip="10.93.18.11", netmask="255.255.254.0", state="ready"),
                RcipPort(nsp="1:4:4", ip="10.93.18.13", netmask="255.255.254.0", state="ready"),
            ],
            targets=[RcTarget(name="ArrayB", mode="IP", status="ready")],
            links=[
                RcLink(target="ArrayB", nsp="0:4:4", address="10.93.18.19", status="Up"),
                RcLink(target="ArrayB", nsp="1:4:4", address="10.93.18.20", status="Up"),
            ],
            vvsets={"vvs_reviewed": ["vol_reviewed"]}, volume_size_mib={"vol_reviewed": 10240},
            cpg_free_mib={"SSD_r6": 100_000},
        )
        b = ReplicationArrayView(
            host=B_HOST, name="ArrayB", system_id=200, os_version="10.5.55", rc_status="Started",
            rcip_ports=[
                RcipPort(nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0", state="ready"),
                RcipPort(nsp="1:1:1", ip="10.93.18.20", netmask="255.255.254.0", state="ready"),
            ],
            targets=[RcTarget(name="ArrayA", mode="IP", status="ready")],
            links=[
                RcLink(target="ArrayA", nsp="0:1:1", address="10.93.18.11", status="Up"),
                RcLink(target="ArrayA", nsp="1:1:1", address="10.93.18.13", status="Up"),
            ],
            cpg_free_mib={"SSD_r6": 100_000},
        )
        return a, b
    a = ReplicationArrayView(
        host=A_HOST, name="ArrayA", system_id=100, os_version="10.5.55",
        ports={
            "0:4:4": PortRole(nsp="0:4:4", mode="peer", state="ready", type="free", protocol="IP"),
            "1:4:4": PortRole(nsp="1:4:4", mode="peer", state="ready", type="free", protocol="IP"),
        },
        vvsets={"vvs_reviewed": ["vol_reviewed"]}, volume_size_mib={"vol_reviewed": 10240},
        cpg_free_mib={"SSD_r6": 100_000},
    )
    b = ReplicationArrayView(
        host=B_HOST, name="ArrayB", system_id=200, os_version="10.5.55", rc_status="Started",
        rcip_ports=[
            RcipPort(nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0", state="ready"),
            RcipPort(nsp="1:1:1", ip="10.93.18.20", netmask="255.255.254.0", state="ready"),
        ],
        ports={
            "0:1:1": PortRole(nsp="0:1:1", mode="peer", state="ready", type="rcip", protocol="IP"),
            "1:1:1": PortRole(nsp="1:1:1", mode="peer", state="ready", type="rcip", protocol="IP"),
        },
        cpg_free_mib={"SSD_r6": 100_000},
    )
    return a, b


def _snap_view() -> SnapshotArrayView:
    return SnapshotArrayView(
        host=A_HOST, name="ArrayA", os_version="10.5.55", time_zone="UTC",
        volumes=[
            ArrayVolumeRecord(name="vol_reviewed", size_mib=10240, cpg="SSD_r6", provisioning_type="tpvv"),
            ArrayVolumeRecord(name="vol_two", size_mib=10240, cpg="SSD_r6", provisioning_type="tpvv"),
        ],
        vvsets={"vvs_reviewed": ["vol_reviewed"]},
        schedules=[],
    )


def _child_storage(db: Path) -> None:
    store = SqliteRunStore(db)
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.PROVISION_ONLY, provisioning_intent=_intent())
    service.discovery_zoning.discovery[run.run_id] = DiscoveryReport(
        host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")],
    )
    state: dict[str, Any] = {}
    _patch_transports(lambda _url, **_kw: _FakeSdk(state, crash_on="createVolume:vol_reviewed"), lambda *_a, **_kw: None)

    async def _go() -> None:
        service.start_storage_preview(run.run_id)
        await service.wait(run.run_id)
        plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "storage.previewed").data["plan"]["plan_id"]
        service.start_storage_apply(run.run_id, approved_plan=plan_id)
        await service.wait(run.run_id)

    asyncio.run(_go())


def _child_rc_groups(db: Path) -> None:
    store = SqliteRunStore(db)
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.REPLICATE, provisioning_intent=_intent(replication=True))
    a_view, b_view = _rc_views(with_partnership=True)
    replication_read.read_array = lambda creds, progress=None: a_view if creds.host == A_HOST else b_view
    store.save_artifact(run.run_id, LINK_CHECK_ARTIFACT, LinkCheck(
        at="2026-11-20T00:00:00+00:00", modes=["sync"],
        results=[LinkCheckResult(pair=LinkPair(nsp_a="0:4:4", ip_a="10.93.18.11", nsp_b="0:1:1", ip_b="10.93.18.19"),
                                 latency_ms=0.5, pings_lost_pct=0.0)],
    ).model_dump_json().encode("utf-8"))
    state: dict[str, Any] = {}
    _patch_transports(lambda _url, **_kw: _FakeSdk(state, crash_on="admit:vvs_reviewed_rcg:vol_reviewed"), lambda *_a, **_kw: None)

    async def _go() -> None:
        service.start_replication_preview(run.run_id)
        await service.wait(run.run_id)
        plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "replication.previewed").data["plan"]["plan_id"]
        service.start_replication_apply(run.run_id, approved_plan=plan_id)
        await service.wait(run.run_id)

    asyncio.run(_go())


def _child_partnership(db: Path) -> None:
    store = SqliteRunStore(db)
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.REPLICATE,
                             provisioning_intent=_intent(replication=True, partnership=True))
    a_view, b_view = _rc_views(with_partnership=False)
    replication_read.read_array = lambda creds, progress=None: a_view if creds.host == A_HOST else b_view
    ssh_state = {
        "A": {"rcip": {}, "rc": "", "targets": {}},
        "B": {"rcip": {"0:1:1": ("10.93.18.19", "255.255.254.0"), "1:1:1": ("10.93.18.20", "255.255.254.0")},
              "rc": "Started", "targets": {}},
    }
    _patch_transports(
        lambda _url, **_kw: _FakeSdk({}),
        lambda host, *_a, **_kw: _FakePartnerSsh("A" if host == A_HOST else "B", ssh_state,
                                                 crash_prefix="creatercopytarget"),
    )

    async def _go() -> None:
        service.start_replication_preview(run.run_id)
        await service.wait(run.run_id)
        plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "replication.previewed").data["plan"]["plan_id"]
        service.start_replication_apply(run.run_id, approved_plan=plan_id)
        await service.wait(run.run_id)

    asyncio.run(_go())


def _child_snapshots(db: Path) -> None:
    store = SqliteRunStore(db)
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.CUSTOM, selected_steps=["snapshots"],
                             provisioning_intent=_intent(snapshots=True))
    view = _snap_view()
    snapshots_read.read_array = lambda _creds, progress=None: view
    service.snapshots._read = lambda _creds, progress=None: view
    wsapi_state: dict[str, Any] = {
        "volumes": [{"name": "vol_reviewed", "sizeMiB": 10240, "userCPG": "SSD_r6"},
                    {"name": "vol_two", "sizeMiB": 10240, "userCPG": "SSD_r6"}],
        "vvsets": {"vvs_reviewed": ["vol_reviewed"]},
    }
    schedules: list[ArraySchedule] = []
    _patch_transports(
        lambda _url, **_kw: _FakeSdk(wsapi_state),
        lambda *_a, **_kw: _FakeSnapSsh(schedules, crash_on="vol_two_snap"),
    )

    async def _go() -> None:
        service.start_snapshots_preview(run.run_id)
        await service.wait(run.run_id)
        plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "snapshots.previewed").data["plan"]["plan_id"]
        service.start_snapshots_apply(run.run_id, approved_plan=plan_id)
        await service.wait(run.run_id)

    asyncio.run(_go())


class _FakeFailoverSsh:
    """In-memory fake read-only SSH serving showrcopy/showsys/showdate for real failover reads."""

    def __init__(self, host: str, roles: dict[str, str]) -> None:
        self.host = host
        self.roles = roles

    def exec_command(self, command: str, timeout: float | None = None):
        is_a = self.host == A_HOST
        name = "ArrayA" if is_a else "ArrayB"
        sys_id = "0x64" if is_a else "0xc8"
        grp = "zz_rc_test_rcg" if is_a else "zz_rc_test_rcg.r100"
        target = "ArrayB" if is_a else "ArrayA"
        role = self.roles["p_role"] if is_a else self.roles["s_role"]
        status = self.roles["p_status"] if is_a else self.roles["s_status"]
        if command == "showsys":
            out = (
                "     ID ------Name------ --------Model--------- --Serial-- Nodes Master TotalCap AllocCap  FreeCap FailedCap\n"
                f"{sys_id} {name} HPE Alletra Storage MP CZ2D320BT1 2 0 1000 100 900 0\n"
            )
        elif command == "showdate":
            out = "2026-11-20 12:00:00 UTC\n"
        elif command.startswith("showrcopy"):
            out = (
                "\nRemote Copy System Information\nStatus: Started, Normal\n\n"
                "Group Information\n\nName Target Status Role Mode Options\n"
                f"{grp} {target} {status} {role} Sync -\n"
                "  LocalVV ID RemoteVV ID SyncStatus LastSyncTime\n"
                "  v1 1 v1 2 Synced NA\n"
            )
        else:
            out = ""
        return None, io.BytesIO(out.encode("utf-8")), io.BytesIO(b"")

    def close(self) -> None:
        return None


def _child_failover(db: Path) -> None:
    store = SqliteRunStore(db)
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.REPLICATE, provisioning_intent=_intent(replication=True))
    roles = {"p_role": "Primary", "p_status": "Started", "s_role": "Secondary", "s_status": "Started"}
    state: dict[str, Any] = {}

    class _FailoverSdk(_FakeSdk):
        def stopRemoteCopy(self, name: str) -> None:
            roles["p_status"] = roles["s_status"] = "Stopped"
            super().stopRemoteCopy(name)

    _patch_transports(
        lambda _url, **_kw: _FailoverSdk(state, crash_on=f"dr:{DR_ACTION_FAILOVER}:zz_rc_test_rcg.r100"),
        lambda host, *_a, **_kw: _FakeFailoverSsh(host, roles),
    )

    async def _go() -> None:
        service.start_failover_test(run.run_id, authorised=True)
        await service.wait(run.run_id)

    asyncio.run(_go())


def _run_crash_child(kind: str, db: Path) -> str:
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src"))
    proc = subprocess.run(
        [sys.executable, str(Path(__file__)), kind, str(db)],
        check=False, env=env, capture_output=True, text=True,
    )
    assert proc.returncode == CRASH_CODE, f"expected exit {CRASH_CODE}, got {proc.returncode}: {proc.stderr}"
    store = SqliteRunStore(db)
    runs = store.list_runs()
    assert len(runs) == 1
    return runs[0].run_id


# ------------------------------------------------------------------ crash mid-apply (all 4 + failover)

def test_crash_mid_apply_storage_recovers_confirmed_removals_and_inspect_first_note(tmp_path):
    db = tmp_path / "state.db"
    run_id = _run_crash_child("storage", db)

    store = SqliteRunStore(db)
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.get_run(run_id)
    assert run.status == RunStatus.RETRYABLE_FAILURE

    failed = [e for e in service.list_events(run_id) if e.event_type == "storage.apply.failed"]
    assert len(failed) == 1
    result = failed[0].data["result"]
    assert [r["command"] for r in result["removals"]] == ["removehostset -f hs_reviewed", "removehost esx1"]
    assert not any("vol_reviewed" in r["command"] for r in result["removals"])
    assert any("vol_reviewed" in n and "showvv vol_reviewed" in n for n in result["removal_notes"])

    # As-built reads the same recovered event with no new reader; reopen is idempotent.
    data = AsBuiltData()
    service.documents._run_records(run_id, data)
    assert [r["command"] for r in data.provisioning_removals] == ["removehostset -f hs_reviewed", "removehost esx1"]
    assert service.coordinator.recover_interrupted_apply(run_id) is False
    assert len([e for e in service.list_events(run_id) if e.event_type == "storage.apply.failed"]) == 1

    # No approval survives the crash.
    plan_id = next(e for e in service.list_events(run_id) if e.event_type == "storage.previewed").data["plan"]["plan_id"]
    service.discovery_zoning.discovery[run_id] = DiscoveryReport()
    with pytest.raises(StepPreconditionError, match="run the provisioning preview first"):
        service.start_storage_apply(run_id, approved_plan=plan_id)


def test_crash_mid_apply_replication_groups_recovers_confirmed_removals_and_inspect_first_note(tmp_path):
    db = tmp_path / "state.db"
    run_id = _run_crash_child("rc_groups", db)

    store = SqliteRunStore(db)
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    assert service.get_run(run_id).status == RunStatus.RETRYABLE_FAILURE

    failed = [e for e in service.list_events(run_id) if e.event_type == "replication.apply.failed"]
    assert len(failed) == 1
    result = failed[0].data["result"]
    assert result["removals_a"] == [
        "stoprcopygroup -f vvs_reviewed_rcg",
        "removercopygroup -f vvs_reviewed_rcg",
        "removevvset -f zz_rc_test",
        "removevv -f zz_rc_test_v01",
    ]
    assert result["removals_b"] == []
    assert not any("dismissrcopyvv" in line for line in result["removals_a"])
    assert any("vol_reviewed" in n and "showrcopy groups vvs_reviewed_rcg" in n for n in result["notes"])

    plan_id = next(e for e in service.list_events(run_id) if e.event_type == "replication.previewed").data["plan"]["plan_id"]
    with pytest.raises(StepPreconditionError, match="read both arrays first"):
        service.start_replication_apply(run_id, approved_plan=plan_id)


def test_crash_mid_apply_partnership_recovers_confirmed_removals_and_inspect_first_note(tmp_path):
    db = tmp_path / "state.db"
    run_id = _run_crash_child("partnership", db)

    store = SqliteRunStore(db)
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    assert service.get_run(run_id).status == RunStatus.RETRYABLE_FAILURE

    failed = [e for e in service.list_events(run_id) if e.event_type == "replication.apply.failed"]
    assert len(failed) == 1
    result = failed[0].data["result"]
    # ADR 0025 condition 4: the in-flight target's removal line is on record before the command is sent,
    # with the inspect-first note sitting next to it until read-back confirms.
    assert result["removals_a"] == [
        "removercopytarget ArrayB",
        "stoprcopy -f -stopgroups -clear",
        "controlport rcip delete -f 0:4:4",
        "controlport rcip delete -f 1:4:4",
    ]
    assert result["removals_b"] == []
    assert any("ArrayB" in n and "showrcopy targets" in n for n in result["notes"])

    plan_id = next(e for e in service.list_events(run_id) if e.event_type == "replication.previewed").data["plan"]["plan_id"]
    with pytest.raises(StepPreconditionError, match="read both arrays first"):
        service.start_replication_apply(run_id, approved_plan=plan_id)


def test_crash_mid_apply_snapshots_recovers_confirmed_removals_and_inspect_first_note(tmp_path):
    db = tmp_path / "state.db"
    run_id = _run_crash_child("snapshots", db)

    store = SqliteRunStore(db)
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    assert service.get_run(run_id).status == RunStatus.RETRYABLE_FAILURE

    failed = [e for e in service.list_events(run_id) if e.event_type == "snapshots.apply.failed"]
    assert len(failed) == 1
    result = failed[0].data["result"]
    assert [r["command"] for r in result["removals"]] == [
        "removesched -f vvs_reviewed_snap",
        "removevv -f vol_reviewed.initial",
    ]
    assert not any("vol_two_snap" in r["command"] for r in result["removals"])
    assert any("vol_two_snap" in n and "showsched" in n for n in result["removal_notes"])

    plan_id = next(e for e in service.list_events(run_id) if e.event_type == "snapshots.previewed").data["plan"]["plan_id"]
    with pytest.raises(StepPreconditionError, match="read the array first"):
        service.start_snapshots_apply(run_id, approved_plan=plan_id)


def test_crash_mid_failover_recovers_failover_failed_with_recovery_guidance(tmp_path):
    db = tmp_path / "state.db"
    run_id = _run_crash_child("failover", db)

    store = SqliteRunStore(db)
    coord = RunCoordinator(Settings(), store, InMemoryEventBus())
    assert coord.get_run(run_id).status == RunStatus.RETRYABLE_FAILURE

    failed = [e for e in coord.list_events(run_id) if e.event_type == "failover.failed"]
    assert len(failed) == 1
    rec = failed[0].data["record"]
    assert rec["result"] == "failed" and rec["failed_step"] == 2
    # observed_state holds ONLY what was actually read before step 2, never fabricated Primary-Rev.
    assert "ArrayB: Secondary/Stopped" in rec["observed_state"]
    assert "Primary-Rev" not in rec["observed_state"]
    assert "if step 2 took effect:" in rec["recovery_action"]
    assert "setrcopygroup recover -f zz_rc_test_rcg.r100" in rec["recovery_action"]
    assert "if not:" in rec["recovery_action"]
    assert "startrcopygroup zz_rc_test_rcg" in rec["recovery_action"]


# ------------------------------------------------------------------ prune exemption

def test_run_older_than_prune_window_keeps_in_progress_record(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    coord = RunCoordinator(Settings(), store, InMemoryEventBus())
    old_run = coord.create_run(_work_item("SGH0000"), mode=RunMode.PROVISION_ONLY, provisioning_intent=_intent())
    coord.set_state(old_run, RunStatus.RUNNING)

    save = coord.apply_record(old_run.run_id, "storage.apply.failed")
    save(ProvisioningResult(
        removals=[RemovalItem(kind="host", name="esx1", command="removehost esx1")],
        removal_notes=["The array may have made volume vol01 before the error."],
    ))
    store.save_artifact(old_run.run_id, "asbuilt_docx", b"old-docx")
    store.save_artifact(old_run.run_id, RC_RESULT_ARTIFACT, b'{"removals_a": ["a"]}')

    for i in range(1, ARTIFACT_RETENTION_RUNS + 6):
        newer = RunRecord(serial_number=f"SGH{i:04d}")
        store.upsert_run(newer)
        store.save_artifact(newer.run_id, "asbuilt_docx", b"newer-docx")

    assert store.load_artifact(old_run.run_id, "asbuilt_docx") is None
    assert store.load_artifact(old_run.run_id, RC_RESULT_ARTIFACT) is None
    assert store.load_artifact(old_run.run_id, APPLY_RECORD_ARTIFACT)

    fresh = RunCoordinator(Settings(), store, InMemoryEventBus())
    assert fresh.get_run(old_run.run_id).status == RunStatus.RETRYABLE_FAILURE
    ev = next(e for e in fresh.list_events(old_run.run_id) if e.event_type == "storage.apply.failed")
    assert [r["command"] for r in ev.data["result"]["removals"]] == ["removehost esx1"]


# ------------------------------------------------------------------ failover save failure (Astra 8, N1)

class _FailingSaveStore(SqliteRunStore):
    def __init__(self, path: Path, *, fail_on_call: int, fail_from_call: int | None = None) -> None:
        super().__init__(path)
        self.fail_on_call = fail_on_call
        self.fail_from_call = fail_from_call
        self.apply_saves = 0

    def save_artifact(self, run_id: str, kind: str, payload: bytes) -> None:
        if kind == APPLY_RECORD_ARTIFACT and payload:
            self.apply_saves += 1
            if self.apply_saves == self.fail_on_call or (
                self.fail_from_call is not None and self.apply_saves >= self.fail_from_call
            ):
                raise sqlite3.OperationalError("database is locked")
        super().save_artifact(run_id, kind, payload)


async def _run_failover_with_store(store: _FailingSaveStore, monkeypatch: pytest.MonkeyPatch):
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.REPLICATE, provisioning_intent=_intent(replication=True))
    calls: list[tuple[str, Any]] = []
    roles = {"p_role": "Primary", "p_status": "Started", "s_role": "Secondary", "s_status": "Started"}

    monkeypatch.setattr(replication_failover.time, "sleep", lambda _s: None)
    monkeypatch.setattr(replication_failover, "AUTO_START_WAIT_S", 0)

    class _PairSdk(_FakeSdk):
        def stopRemoteCopy(self, name: str) -> None:
            calls.append(("stop", name))
            roles["p_status"] = roles["s_status"] = "Stopped"

        def recoverRemoteCopyGroupFromDisaster(self, name: str, action: int) -> None:
            calls.append(("dr", action))
            if action == DR_ACTION_FAILOVER:
                roles["s_role"] = "Primary-Rev"
            elif action == DR_ACTION_RECOVER:
                roles["p_role"], roles["p_status"], roles["s_status"] = "Secondary-Rev", "Started", "Started"
            elif action == DR_ACTION_RESTORE:
                roles.update(p_role="Primary", p_status="Started", s_role="Secondary", s_status="Started")

    monkeypatch.setattr(device_trust, "device_ca_bundle", lambda: None)
    monkeypatch.setattr(device_trust, "bypass_proxy_for", lambda _h: None)
    monkeypatch.setattr(device_trust, "check_tls", lambda *_a, **_kw: DeviceKey(
        kind=TrustKind.TLS, key_type="certificate", data="", fingerprint="00" * 32,
    ))
    monkeypatch.setattr(wsapi_client, "_pin_calls", lambda *_a, **_kw: None)
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _PairSdk({}))
    monkeypatch.setattr(device_trust, "open_ssh", lambda host, *_a, **_kw: _FakeFailoverSsh(host, roles))

    service.start_failover_test(run.run_id, authorised=True)
    await service.wait(run.run_id)
    return service, run.run_id, calls


async def test_failover_save_failure_before_first_send_aborts_with_zero_writes(tmp_path, monkeypatch):
    store = _FailingSaveStore(tmp_path / "state.db", fail_on_call=1)
    service, run_id, calls = await _run_failover_with_store(store, monkeypatch)
    assert calls == []
    events = service.list_events(run_id)
    assert not any(e.event_type == "step.crashed" for e in events)
    failed = next(e for e in events if e.event_type == "failover.failed")
    assert failed.data["record"]["result"] == "aborted"
    assert failed.data["record"]["failed_step"] == 1
    assert "database is locked" in failed.data["record"]["error"]


async def test_failover_save_failure_after_first_send_notes_and_completes_to_restore(tmp_path, monkeypatch):
    store = _FailingSaveStore(tmp_path / "state.db", fail_on_call=2, fail_from_call=2)
    service, run_id, calls = await _run_failover_with_store(store, monkeypatch)
    assert calls == [("stop", "zz_rc_test_rcg"), ("dr", DR_ACTION_FAILOVER),
                     ("dr", DR_ACTION_RECOVER), ("dr", DR_ACTION_RESTORE)]
    events = service.list_events(run_id)
    assert not any(e.event_type == "step.crashed" for e in events)
    done = next(e for e in events if e.event_type == "failover.completed")
    rec = done.data["record"]
    assert rec["result"] == "passed"
    assert "Checkpoint save before step 2 failed (database is locked)" in rec["steps"][2]["detail"]


# ------------------------------------------------------------------ normal apply byte-identical (no double counting)

async def test_normal_apply_removal_set_is_byte_identical_with_and_without_apply_record(tmp_path, monkeypatch):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    intent = _intent()
    run = service.create_run(_work_item(), mode=RunMode.PROVISION_ONLY, provisioning_intent=intent)
    discovery = DiscoveryReport(host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")])
    service.discovery_zoning.discovery[run.run_id] = discovery
    store.save_artifact(run.run_id, "zoned_hosts", b"esx1")

    state_with: dict[str, Any] = {}
    monkeypatch.setattr(device_trust, "device_ca_bundle", lambda: None)
    monkeypatch.setattr(device_trust, "bypass_proxy_for", lambda _h: None)
    monkeypatch.setattr(device_trust, "check_tls", lambda *_a, **_kw: DeviceKey(
        kind=TrustKind.TLS, key_type="certificate", data="", fingerprint="00" * 32,
    ))
    monkeypatch.setattr(wsapi_client, "_pin_calls", lambda *_a, **_kw: None)
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk(state_with))

    service.start_storage_preview(run.run_id)
    await service.wait(run.run_id)
    plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "storage.previewed").data["plan"]["plan_id"]
    service.start_storage_apply(run.run_id, approved_plan=plan_id)
    await service.wait(run.run_id)

    applied_ev = next(e for e in service.list_events(run.run_id) if e.event_type == "storage.applied")
    recorded = ProvisioningResult.model_validate(applied_ev.data["result"])
    assert not store.load_artifact(run.run_id, APPLY_RECORD_ARTIFACT)

    # Compare against direct apply_plan with no apply_record bound (main's exact path).
    state_plain: dict[str, Any] = {}
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk(state_plain))
    plan = storage_provision.build_plan(intent, discovery, reachable_hosts={"esx1"})
    plain = prov_apply.apply_plan(
        prov_apply.StorageInputs(intent, discovery, {"esx1"}, plan),
        Approval("direct", "storage", {"A": intent.array},
                 save_record=lambda m: m.model_dump(mode="json")),
    )

    assert recorded.model_dump(mode="json") == plain.model_dump(mode="json")
    assert recorded.removal_notes == []
    assert [r.command for r in recorded.removals] == [
        "removevlun -f vol_reviewed 0 set:hs_reviewed",
        "removevvset -f vvs_reviewed",
        "removevv -f vol_reviewed",
        "removehostset -f hs_reviewed",
        "removehost esx1",
    ]
    data = AsBuiltData()
    service.documents._run_records(run.run_id, data)
    assert [r["command"] for r in data.provisioning_removals] == [r.command for r in plain.removals]


def _patch_tls_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(device_trust, "device_ca_bundle", lambda: None)
    monkeypatch.setattr(device_trust, "bypass_proxy_for", lambda _h: None)
    monkeypatch.setattr(device_trust, "check_tls", lambda *_a, **_kw: DeviceKey(
        kind=TrustKind.TLS, key_type="certificate", data="", fingerprint="00" * 32,
    ))
    monkeypatch.setattr(wsapi_client, "_pin_calls", lambda *_a, **_kw: None)


async def test_normal_rc_groups_removal_set_is_byte_identical(tmp_path, monkeypatch):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    _patch_tls_noop(monkeypatch)
    rc_intent = _intent(replication=True)
    rc_run = service.create_run(_work_item("SN10"), mode=RunMode.REPLICATE, provisioning_intent=rc_intent)
    a_view, b_view = _rc_views(with_partnership=True)
    monkeypatch.setattr(replication_read, "read_array", lambda creds, progress=None: a_view if creds.host == A_HOST else b_view)
    store.save_artifact(rc_run.run_id, LINK_CHECK_ARTIFACT, LinkCheck(
        at="2026-11-20T00:00:00+00:00", modes=["sync"],
        results=[LinkCheckResult(pair=LinkPair(nsp_a="0:4:4", ip_a="10.93.18.11", nsp_b="0:1:1", ip_b="10.93.18.19"),
                                 latency_ms=0.5, pings_lost_pct=0.0)],
    ).model_dump_json().encode("utf-8"))
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk({}))
    service.start_replication_preview(rc_run.run_id)
    await service.wait(rc_run.run_id)
    rc_plan_ev = next(e for e in service.list_events(rc_run.run_id) if e.event_type == "replication.previewed")
    service.start_replication_apply(rc_run.run_id, approved_plan=rc_plan_ev.data["plan"]["plan_id"])
    await service.wait(rc_run.run_id)
    rc_recorded = next(e for e in service.list_events(rc_run.run_id) if e.event_type == "replication.applied").data["result"]
    assert not store.load_artifact(rc_run.run_id, APPLY_RECORD_ARTIFACT)
    rc_plain = rc_apply.apply_plan(
        ReplicationPlan.model_validate(rc_plan_ev.data["plan"]), rc_intent,
        Approval("plain", "rc_groups", {"A": rc_intent.array, "B": _creds(B_HOST)},
                 save_record=lambda m: m.model_dump(mode="json")),
    )
    assert (rc_recorded["removals_a"], rc_recorded["removals_b"]) == (rc_plain.removals_a, rc_plain.removals_b)
    assert not any("may have" in n for n in rc_recorded["notes"])


async def test_normal_partnership_and_snapshots_removal_sets_are_byte_identical(tmp_path, monkeypatch):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    _patch_tls_noop(monkeypatch)

    p_intent = _intent(replication=True, partnership=True)
    p_run = service.create_run(_work_item("SN11"), mode=RunMode.REPLICATE, provisioning_intent=p_intent)
    pa_view, pb_view = _rc_views(with_partnership=False)
    monkeypatch.setattr(replication_read, "read_array", lambda creds, progress=None: pa_view if creds.host == A_HOST else pb_view)

    def _fresh_ssh_state() -> dict[str, Any]:
        return {
            "A": {"rcip": {}, "rc": "", "targets": {}},
            "B": {"rcip": {"0:1:1": ("10.93.18.19", "255.255.254.0"), "1:1:1": ("10.93.18.20", "255.255.254.0")},
                  "rc": "Started", "targets": {}},
        }

    s1, s2 = _fresh_ssh_state(), _fresh_ssh_state()
    monkeypatch.setattr(device_trust, "open_ssh", lambda host, *_a, **_kw: _FakePartnerSsh("A" if host == A_HOST else "B", s1))
    service.start_replication_preview(p_run.run_id)
    await service.wait(p_run.run_id)
    p_plan_ev = next(e for e in service.list_events(p_run.run_id) if e.event_type == "replication.previewed")
    service.start_replication_apply(p_run.run_id, approved_plan=p_plan_ev.data["plan"]["plan_id"])
    await service.wait(p_run.run_id)
    p_recorded = next(e for e in service.list_events(p_run.run_id) if e.event_type == "replication.applied").data["result"]
    assert not store.load_artifact(p_run.run_id, APPLY_RECORD_ARTIFACT)
    monkeypatch.setattr(device_trust, "open_ssh", lambda host, *_a, **_kw: _FakePartnerSsh("A" if host == A_HOST else "B", s2))
    p_plain = rc_partner_apply.apply_partnership(
        ReplicationPlan.model_validate(p_plan_ev.data["plan"]), p_intent,
        Approval("plain", "rc_partnership", {"A": p_intent.array, "B": _creds(B_HOST)},
                 save_record=lambda m: m.model_dump(mode="json")),
    )
    assert (p_recorded["removals_a"], p_recorded["removals_b"]) == (p_plain.removals_a, p_plain.removals_b)
    assert p_recorded["notes"] == p_plain.notes == []

    s_intent = _intent(snapshots=True)
    s_run = service.create_run(_work_item("SN12"), mode=RunMode.CUSTOM, selected_steps=["snapshots"],
                               provisioning_intent=s_intent)
    view = _snap_view()
    monkeypatch.setattr(service.snapshots, "_read", lambda _c, progress=None: view)

    def _fresh_ws() -> dict[str, Any]:
        return {
            "volumes": [{"name": "vol_reviewed", "sizeMiB": 10240, "userCPG": "SSD_r6"},
                        {"name": "vol_two", "sizeMiB": 10240, "userCPG": "SSD_r6"}],
            "vvsets": {"vvs_reviewed": ["vol_reviewed"]},
        }

    ws1, ws2 = _fresh_ws(), _fresh_ws()
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk(ws1))
    monkeypatch.setattr(device_trust, "open_ssh", lambda *_a, **_kw: _FakeSnapSsh([]))
    service.start_snapshots_preview(s_run.run_id)
    await service.wait(s_run.run_id)
    s_plan_ev = next(e for e in service.list_events(s_run.run_id) if e.event_type == "snapshots.previewed")
    service.start_snapshots_apply(s_run.run_id, approved_plan=s_plan_ev.data["plan"]["plan_id"])
    await service.wait(s_run.run_id)
    s_recorded = next(e for e in service.list_events(s_run.run_id) if e.event_type == "snapshots.applied").data["result"]
    assert not store.load_artifact(s_run.run_id, APPLY_RECORD_ARTIFACT)
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk(ws2))
    monkeypatch.setattr(device_trust, "open_ssh", lambda *_a, **_kw: _FakeSnapSsh([]))
    s_plain = snap_apply.apply_plan(
        SnapshotPlan.model_validate(s_plan_ev.data["plan"]), view, s_intent,
        Approval("plain", "snapshots", {"A": s_intent.array},
                 save_record=lambda m: m.model_dump(mode="json")),
    )
    assert [r["command"] for r in s_recorded["removals"]] == [r.command for r in s_plain.removals]
    assert s_recorded["removal_notes"] == s_plain.removal_notes


# ------------------------------------------------------------------ Fable review regression tests

def test_multiple_existing_exports_of_one_vvset_do_not_collapse_or_shift_confirm(monkeypatch):
    """Blocking #1: vvs exported to hs1 (exists), hs2 (exists), hs3 (new) must produce 3 rows
    and label hs3 as `→ set:hs3`, never collapsing the two `exists` outcomes."""
    _patch_tls_noop(monkeypatch)
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        volumes=[VolumeRequest(name="vol01", size_gib=10, cpg="SSD_r6", vvset="vvs")],
        host_sets=[
            HostSetRequest(name="hs1", members=["esx1"]),
            HostSetRequest(name="hs2", members=["esx1"]),
            HostSetRequest(name="hs3", members=["esx1"]),
        ],
        exports=[
            ExportRequest(source_kind="vvset", source_name="vvs", target_kind="hostset", target_name="hs1"),
            ExportRequest(source_kind="vvset", source_name="vvs", target_kind="hostset", target_name="hs2"),
            ExportRequest(source_kind="vvset", source_name="vvs", target_kind="hostset", target_name="hs3"),
        ],
    )
    discovery = DiscoveryReport(
        host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")],
    )
    state: dict[str, Any] = {
        "hosts": [{"name": "esx1", "persona": 8, "FCPaths": [{"wwn": "10000090FA8B1111"}]}],
        "host_sets": {"hs1": ["esx1"], "hs2": ["esx1"], "hs3": ["esx1"]},
        "volumes": [{"name": "vol01", "sizeMiB": 10240, "userCPG": "SSD_r6", "provisioningType": 2}],
        "vvsets": {"vvs": ["vol01"]},
        "vluns": [
            {"volumeName": "vol01", "hostname": "set:hs1", "lun": 0, "active": False},
            {"volumeName": "vol01", "hostname": "set:hs2", "lun": 0, "active": False},
        ],
    }
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _FakeSdk(state))
    plan = storage_provision.build_plan(intent, discovery, reachable_hosts={"esx1"})
    result = prov_apply.apply_plan(
        prov_apply.StorageInputs(intent, discovery, {"esx1"}, plan),
        Approval("test", "storage", {"A": intent.array},
                 save_record=lambda m: m.model_dump(mode="json")),
    )
    assert result.error is None
    vluns = [o for o in result.outcomes if o.kind == "vlun"]
    assert len(vluns) == 3
    assert [o.status for o in vluns] == ["exists", "exists", "created"]
    assert vluns[0].detail.endswith("→ set:hs1")
    assert vluns[1].detail.endswith("→ set:hs2")
    assert vluns[2].detail.endswith("→ set:hs3")


@pytest.mark.parametrize(("fail_prefix", "mode", "expected_line"), [
    ("controlport rcip addr", "error", "controlport rcip delete -f 0:4:4"),
    ("controlport rcip addr", "timeout", "controlport rcip delete -f 0:4:4"),
    ("startrcopy", "timeout", "stoprcopy -f -stopgroups -clear"),
    ("creatercopytarget", "timeout", "removercopytarget ArrayB"),
])
def test_partnership_removal_line_is_on_record_before_error_or_timeout(
    monkeypatch, fail_prefix: str, mode: str, expected_line: str,
):
    """Blocking #2 (ADR 0025 condition 4): whether addr returns Error or addr/startrcopy/creatercopytarget
    times out, the removal line is already on record with an inspect-first note next to it."""
    from alletra_onboard.application.replication import plan as rc_plan
    from alletra_onboard.application.replication import plan_check as rc_plan_check

    _patch_tls_noop(monkeypatch)
    intent = _intent(replication=True, partnership=True)
    a_view, b_view = _rc_views(with_partnership=False)
    plan = rc_plan.build_plan(rc_plan_check.check(a_view, b_view, intent.replication), intent.replication, intent)
    ssh_state = {
        "A": {"rcip": {}, "rc": "", "targets": {}},
        "B": {"rcip": {"0:1:1": ("10.93.18.19", "255.255.254.0"), "1:1:1": ("10.93.18.20", "255.255.254.0")},
              "rc": "Started", "targets": {}},
    }

    class _FailPartnerSsh(_FakePartnerSsh):
        def exec_command(self, command: str, timeout: float | None = None):
            if command.startswith(fail_prefix):
                if mode == "error":
                    return None, io.BytesIO(b"Error: simulated array error\n"), io.BytesIO(b"")
                raise TimeoutError("SSH command timed out")
            return super().exec_command(command, timeout)

    monkeypatch.setattr(device_trust, "open_ssh",
                        lambda host, *_a, **_kw: _FailPartnerSsh("A" if host == A_HOST else "B", ssh_state))
    result = rc_partner_apply.apply_partnership(
        plan, intent, Approval("test", "rc_partnership", {"A": intent.array, "B": _creds(B_HOST)},
                               save_record=lambda m: m.model_dump(mode="json")),
    )
    assert result.error is not None
    assert expected_line in result.removals_a
    assert any("may have" in n for n in result.notes)


async def test_failover_login_failure_returns_aborted_record_with_zero_sends_and_no_crash(tmp_path, monkeypatch):
    """Blocking #3: a write-session login failure before step 1 aborts cleanly with zero sends and no step.crashed."""
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_work_item(), mode=RunMode.REPLICATE, provisioning_intent=_intent(replication=True))
    roles = {"p_role": "Primary", "p_status": "Started", "s_role": "Secondary", "s_status": "Started"}
    _patch_tls_noop(monkeypatch)
    monkeypatch.setattr(device_trust, "open_ssh", lambda host, *_a, **_kw: _FakeFailoverSsh(host, roles))

    class _RefusingSdk(_FakeSdk):
        def login(self, _u: str, _p: str) -> None:
            raise WsapiError("HTTP 401: invalid array password")

    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _RefusingSdk({}))
    service.start_failover_test(run.run_id, authorised=True)
    await service.wait(run.run_id)

    events = service.list_events(run.run_id)
    assert not any(e.event_type == "step.crashed" for e in events)
    failed = next(e for e in events if e.event_type == "failover.failed")
    assert failed.data["record"]["result"] == "aborted"
    assert failed.data["record"]["failed_step"] == 1
    assert "invalid array password" in failed.data["record"]["error"]


async def test_get_run_during_live_apply_leaves_it_running_with_no_failed_event(tmp_path, monkeypatch):
    """Blocking #5: polling get_run while an apply has saved apply_in_progress and is still live must
    leave the run RUNNING and emit no *.apply.failed event."""
    import threading

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    intent = _intent()
    run = service.create_run(_work_item(), mode=RunMode.PROVISION_ONLY, provisioning_intent=intent)
    service.discovery_zoning.discovery[run.run_id] = DiscoveryReport(
        host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")],
    )
    entered = threading.Event()
    release = threading.Event()
    state: dict[str, Any] = {}

    class _BlockingSdk(_FakeSdk):
        def createVolume(self, name: str, cpg: str, size_mib: int, **_kw: Any) -> None:
            entered.set()
            release.wait(timeout=5.0)
            super().createVolume(name, cpg, size_mib, **_kw)

    _patch_tls_noop(monkeypatch)
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", lambda _url, **_kw: _BlockingSdk(state))

    service.start_storage_preview(run.run_id)
    await service.wait(run.run_id)
    plan_id = next(e for e in service.list_events(run.run_id) if e.event_type == "storage.previewed").data["plan"]["plan_id"]
    service.start_storage_apply(run.run_id, approved_plan=plan_id)
    assert await asyncio.to_thread(entered.wait, 2.0)

    assert store.load_artifact(run.run_id, APPLY_RECORD_ARTIFACT)
    live_run = service.get_run(run.run_id)
    assert live_run.status == RunStatus.RUNNING
    assert not any(e.event_type == "storage.apply.failed" for e in service.list_events(run.run_id))

    release.set()
    await service.wait(run.run_id)
    assert service.get_run(run.run_id).status == RunStatus.READY
    assert any(e.event_type == "storage.applied" for e in service.list_events(run.run_id))
    assert not any(e.event_type == "storage.apply.failed" for e in service.list_events(run.run_id))


def test_approval_without_bound_saver_is_refused():
    """Smaller shape: a missing saver on Approval is impossible in production, never a silent no-op."""
    approval = Approval("run-1", "storage", {"A": _creds()})
    assert approval.save_record is None
    with pytest.raises(ApprovalError, match="no apply record saver bound"):
        approval.require_saver()


if __name__ == "__main__":
    _DISPATCH = {
        "storage": _child_storage,
        "rc_groups": _child_rc_groups,
        "partnership": _child_partnership,
        "snapshots": _child_snapshots,
        "failover": _child_failover,
    }
    _DISPATCH[sys.argv[1]](Path(sys.argv[2]))
