"""Stage-3 write-ordering proof (STANDARD S5, ADR 0025, ADR 0031):

For every write site across all four apply modules (`provisioning/apply.py`, `replication/apply.py`,
`replication/partnership_apply.py`, `snapshots/apply.py`) plus every DR send in
`replication/failover.py`, asserts that at the exact moment the fake device receives the write,
the LAST SAVED in-progress record already carries the inspect-first note (and, for partnership SSH
writes under ADR 0025 condition 4, the removal line).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from pydantic import BaseModel, SecretStr

from alletra_onboard.application.provisioning import apply as prov_apply
from alletra_onboard.application.replication import apply as rc_apply
from alletra_onboard.application.replication import failover as rc_failover
from alletra_onboard.application.replication import partnership_apply as rc_partner_apply
from alletra_onboard.application.snapshots import apply as snap_apply
from alletra_onboard.domain.approval import Approval, Purpose
from alletra_onboard.domain.discovery import ArrayHost, DiscoveryReport, HostHba
from alletra_onboard.domain.provisioning import (
    ArrayHostRecord,
    ExportRequest,
    HostSetRequest,
    ProvisioningIntent,
    ProvisioningPlan,
    VlunTemplate,
    VolumeRequest,
)
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
    RcGroup,
    RcGroupVolume,
    RcipPortRequest,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
)
from alletra_onboard.domain.shared import ArrayVolumeRecord, EndpointCreds
from alletra_onboard.domain.snapshots import (
    SnapshotAction,
    SnapshotArrayView,
    SnapshotIntent,
    SnapshotPlan,
    SnapshotRequest,
)

A_HOST, B_HOST = "192.0.2.1", "192.0.2.9"


def _creds(host: str = A_HOST) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


class _SaveRecorder:
    """Captures deep JSON snapshots of every saved record so fakes inspect what is on disk NOW."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def __call__(self, model: BaseModel) -> None:
        self.records.append(model.model_dump(mode="json"))

    def last(self) -> dict[str, Any] | None:
        return self.records[-1] if self.records else None


def _approval(purpose: Purpose, recorder: _SaveRecorder, *, both: bool = False) -> Approval:
    arrays = {"A": _creds(A_HOST), "B": _creds(B_HOST)} if both else {"A": _creds(A_HOST)}
    return Approval(run_id="run-s5", purpose=purpose, arrays=arrays, save_record=recorder)


# ------------------------------------------------------------------ scenario 1: provisioning/apply.py

class _FakeProvWsapi:
    def __init__(self, recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None]) -> None:
        self._recorder = recorder
        self._seen = seen
        self._templates: list[VlunTemplate] = [
            VlunTemplate(volume="vol_p1", target="set:hs_main", lun=0),
        ]
        self._hosts: list[ArrayHostRecord] = []
        self._vols: list[ArrayVolumeRecord] = []

    def __enter__(self) -> _FakeProvWsapi:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def hosts(self) -> list[ArrayHostRecord]:
        return list(self._hosts)

    def host_sets(self) -> dict[str, list[str]]:
        return {}

    def volumes(self) -> list[ArrayVolumeRecord]:
        return list(self._vols)

    def volume_sets(self) -> dict[str, list[str]]:
        return {"vvs_full": ["vol_full"], "vvs_partial": ["vol_p1", "vol_p2"]}

    def vlun_templates(self) -> list[VlunTemplate]:
        return list(self._templates)

    def ensure_host(self, name: str, wwns: list[str], *, persona: str = "VMware") -> str:
        self._seen["provisioning:ensure_host"] = self._recorder.last()
        self._hosts.append(ArrayHostRecord(id=1, name=name, persona=persona, wwns=list(wwns)))
        return "created"

    def ensure_iscsi_host(self, name: str, iqns: list[str], *, persona: str = "VMware") -> str:
        self._seen["provisioning:ensure_iscsi_host"] = self._recorder.last()
        self._hosts.append(ArrayHostRecord(id=2, name=name, persona=persona, iqns=list(iqns)))
        return "created"

    def ensure_host_set(self, _name: str, _members: list[str]) -> str:
        self._seen["provisioning:ensure_host_set"] = self._recorder.last()
        return "created"

    def ensure_volume(self, name: str, cpg: str, size_mib: int, prov_type: str) -> str:
        self._seen.setdefault("provisioning:ensure_volume", self._recorder.last())
        self._vols.append(ArrayVolumeRecord(id=1, name=name, size_mib=size_mib, cpg=cpg, provisioning_type=prov_type))
        return "created"

    def ensure_volume_set(self, _name: str, _vols: list[str]) -> str:
        self._seen.setdefault("provisioning:ensure_volume_set", self._recorder.last())
        return "created"

    def ensure_vlun(self, volume: str, target: str, *, lun: int | None = None) -> str:
        if volume.startswith("set:"):
            self._seen["provisioning:ensure_vlun_create"] = self._recorder.last()
            self._templates.append(VlunTemplate(volume="vol_full", target=target, lun=1 if lun is None else lun))
        else:
            self._seen["provisioning:ensure_vlun_update"] = self._recorder.last()
            self._templates.append(VlunTemplate(volume=volume, target=target, lun=2 if lun is None else lun))
        return "created"


def _run_provisioning() -> dict[str, dict[str, Any] | None]:
    recorder = _SaveRecorder()
    seen: dict[str, dict[str, Any] | None] = {}
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        volumes=[
            VolumeRequest(name="vol_full", size_gib=10, cpg="SSD_r6", vvset="vvs_full"),
            VolumeRequest(name="vol_p1", size_gib=10, cpg="SSD_r6", vvset="vvs_partial"),
            VolumeRequest(name="vol_p2", size_gib=10, cpg="SSD_r6", vvset="vvs_partial"),
        ],
        host_sets=[HostSetRequest(name="hs_main", members=["esx1", "lin1"])],
        exports=[
            ExportRequest(source_kind="vvset", source_name="vvs_full", target_kind="hostset", target_name="hs_main"),
            ExportRequest(source_kind="vvset", source_name="vvs_partial", target_kind="hostset", target_name="hs_main"),
        ],
    )
    discovery = DiscoveryReport(
        host_hbas=[HostHba(host_name="esx1", wwpn="10000090FA8B1111", fabric="odd", os="VMware ESXi")],
        array_hosts=[ArrayHost(name="lin1", persona="Generic-ALUA", iqns={"iqn.2026-01.com.example:lin1": ["0:4:1"]})],
    )
    inputs = prov_apply.StorageInputs(
        intent=intent,
        discovery=discovery,
        reachable_hosts={"esx1", "lin1"},
        plan=ProvisioningPlan(),
    )
    result = prov_apply.apply_plan(
        inputs, _approval("storage", recorder),
        wsapi_factory=lambda *_a: _FakeProvWsapi(recorder, seen),
    )
    assert result.error is None
    return seen


# ------------------------------------------------------------------ scenario 2: replication/apply.py

class _FakeRcWsapi:
    def __init__(self, side: str, recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None]) -> None:
        self.side = side
        self._recorder = recorder
        self._seen = seen

    def __enter__(self) -> _FakeRcWsapi:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def ensure_volume(self, *_args: object, **_kwargs: object) -> str:
        self._seen["replication:test_volume"] = self._recorder.last()
        return "created"

    def ensure_volume_set(self, *_args: object, **_kwargs: object) -> str:
        key = "replication:test_vvset" if self.side == "A" else "replication:peer_vvset"
        self._seen[key] = self._recorder.last()
        return "created"

    def create_remote_copy_group(self, *_args: object, **_kwargs: object) -> str:
        self._seen["replication:create_group"] = self._recorder.last()
        return "created"

    def set_remote_copy_group(self, *_args: object, **_kwargs: object) -> str:
        self._seen["replication:set_policy"] = self._recorder.last()
        return ""

    def admit_remote_copy_volume(self, *_args: object, **_kwargs: object) -> str:
        self._seen["replication:admit_volume"] = self._recorder.last()
        return "created"

    def start_remote_copy_group(self, *_args: object, **_kwargs: object) -> str:
        self._seen["replication:start_group"] = self._recorder.last()
        return "started"


def _run_replication_groups() -> dict[str, dict[str, Any] | None]:
    recorder = _SaveRecorder()
    seen: dict[str, dict[str, Any] | None] = {}
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        replication=ReplicationIntent(peer=_creds(B_HOST)),
    )
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="test_volume", name="zz_rc_test_v01", where="A", state="create",
                          detail={"cpg": "SSD_r6", "size_gib": 1}),
        ReplicationAction(kind="test_vvset", name="zz_rc_test", where="A", state="create",
                          detail={"members": ["zz_rc_test_v01"]}),
        ReplicationAction(kind="group", name="vvs_prod_rcg", where="A", state="create", detail={
            "target": "ArrayB", "mode": "sync", "peer_cpg": "SSD_r6", "local_cpg": "SSD_r6",
            "volumes": ["vol_prod"], "start_where": "A",
        }),
        ReplicationAction(kind="peer_vvset", name="vvs_prod", where="B", state="create",
                          detail={"group": "vvs_prod_rcg", "members": ["vol_prod"]}),
    ])
    result = rc_apply.apply_plan(
        plan, intent, _approval("rc_groups", recorder, both=True),
        wsapi_factory=lambda _app, _purpose, side: _FakeRcWsapi(side, recorder, seen),
    )
    assert result.error is None
    return seen


# ------------------------------------------------------------------ scenario 3: partnership_apply.py

class _FakeRcCli:
    def __init__(
        self, side: str, state: dict[str, dict[str, Any]],
        recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None],
    ) -> None:
        self.side = side
        self._state = state
        self._recorder = recorder
        self._seen = seen

    def __enter__(self) -> _FakeRcCli:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def write(self, command: str) -> str:
        s = self._state[self.side]
        if command.startswith("controlport rcip addr "):
            self._seen["partnership:rcip_addr"] = self._recorder.last()
            s["ip"] = command.split()[4]
            return "Remote Copy interface change successful.\n"
        if command.startswith("controlport rcip gw "):
            self._seen["partnership:rcip_gw"] = self._recorder.last()
            s["gw"] = command.split()[4]
            return "Remote Copy interface change successful.\n"
        if command.startswith("controlport rcip ping "):
            return "3 packets transmitted, 3 received, 0% packet loss, time 2000ms\n"
        if command == "startrcopy":
            self._seen["partnership:startrcopy"] = self._recorder.last()
            s["rc"] = "Started"
            return "\n"
        if command.startswith("creatercopytarget "):
            self._seen["partnership:creatercopytarget"] = self._recorder.last()
            s["targets"].append(command.split()[1])
            return "\n"
        raise AssertionError(f"unexpected partnership write: {command}")

    def run(self, command: str) -> str:
        s = self._state[self.side]
        if command == "showport -rcip":
            gw = s["gw"] or "-"
            return f"N:S:P State HwAddr IPAddr Netmask Gateway MTU Rate\n0:4:4 ready 00 {s['ip']} 255.255.254.0 {gw} 1500 10Gbps\n"
        if command in ("showrcopy", "showrcopy targets", "showrcopy links"):
            text = f"Remote Copy System Information\nStatus: {s['rc']}, Normal\nTarget Information\nName ID Type Status Options Policy\n"
            text += "".join(f"{t} 1 IP ready - mirror_config\n" for t in s["targets"])
            text += "Link Information\nTarget Node Address Status Options\n"
            text += "".join(f"{t} 0:4:4 10.93.18.19 Up -\n" for t in s["targets"])
            return text
        raise AssertionError(f"unexpected partnership read: {command}")


def _run_partnership() -> dict[str, dict[str, Any] | None]:
    recorder = _SaveRecorder()
    seen: dict[str, dict[str, Any] | None] = {}
    state: dict[str, dict[str, Any]] = {
        "A": {"ip": "", "gw": "", "rc": "", "targets": []},
        "B": {"ip": "10.93.18.19", "gw": "", "rc": "Started", "targets": ["ArrayA"]},
    }
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        replication=ReplicationIntent(
            peer=_creds(B_HOST),
            network=[
                RcipPortRequest(side="A", nsp="0:4:4", ip="10.93.18.11", netmask="255.255.254.0", gateway="10.93.18.1"),
                RcipPortRequest(side="B", nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0"),
            ],
        ),
    )
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="rcip_port", name="0:4:4", where="A", state="create",
                          detail={"ip": "10.93.18.11", "netmask": "255.255.254.0", "gateway": "10.93.18.1"}),
        ReplicationAction(kind="rc_service", name="Remote Copy", where="A", state="create",
                          detail={"was_configured": False}),
        ReplicationAction(kind="target", name="ArrayB", where="A", state="create",
                          detail={"links": ["0:4:4:10.93.18.19"]}),
    ])
    result = rc_partner_apply.apply_partnership(
        plan, intent, _approval("rc_partnership", recorder, both=True),
        rc_cli_factory=lambda _app, side, _objs: _FakeRcCli(side, state, recorder, seen),
    )
    assert result.error is None
    return seen


# ------------------------------------------------------------------ scenario 4: snapshots/apply.py

class _FakeSnapWsapi:
    def __init__(
        self, vols: list[ArrayVolumeRecord],
        recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None],
    ) -> None:
        self._vols = vols
        self._recorder = recorder
        self._seen = seen

    def __enter__(self) -> _FakeSnapWsapi:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def volumes(self) -> list[ArrayVolumeRecord]:
        return list(self._vols)

    def volume_sets(self) -> dict[str, list[str]]:
        return {"vvs_set": ["vol_s1"]}

    def create_set_snapshot(self, _vvset: str, _pattern: str, **_kwargs: object) -> None:
        self._seen["snapshots:create_set_snapshot"] = self._recorder.last()
        self._vols.append(ArrayVolumeRecord(
            name="vol_s1.initial", copy_of="vol_s1", size_mib=10240, cpg="SSD_r6",
            provisioning_type="snp", read_only=True, expires="2026-11-21T12:00:00Z",
        ))

    def create_snapshot(self, base: str, snap_name: str, **_kwargs: object) -> None:
        self._seen["snapshots:create_snapshot"] = self._recorder.last()
        self._vols.append(ArrayVolumeRecord(
            name=snap_name, copy_of=base, size_mib=10240, cpg="SSD_r6",
            provisioning_type="snp", read_only=True, expires="2026-11-21T12:00:00Z",
        ))


class _FakeSnapCli:
    def __init__(
        self, schedules: list[tuple[str, str, str]],
        recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None],
    ) -> None:
        self._schedules = schedules
        self._recorder = recorder
        self._seen = seen

    def __enter__(self) -> _FakeSnapCli:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def run(self, command: str) -> str:
        assert command == "showsched"
        if not self._schedules:
            return "No scheduled tasks listed\n"
        hdr = "SchedName File/Command Interval Min Hour DOM Month DOW CreatedBy Status Alert NextRunTime"
        rows = [f"{n} {cmd} - {cron} 3paradm active Y 2026-11-21T04:00:00" for n, cmd, cron in self._schedules]
        return "\n".join([hdr, *rows, "-" * 40, f"{len(rows)} total", ""])

    def write(self, command: str) -> str:
        self._seen["snapshots:createsched"] = self._recorder.last()
        parts = command.split('"')
        self._schedules.append((parts[4].strip(), parts[1], parts[3]))
        return ""


def _run_snapshots() -> dict[str, dict[str, Any] | None]:
    recorder = _SaveRecorder()
    seen: dict[str, dict[str, Any] | None] = {}
    vols: list[ArrayVolumeRecord] = [
        ArrayVolumeRecord(name="vol_s1", size_mib=10240, cpg="SSD_r6", provisioning_type="tpvv"),
        ArrayVolumeRecord(name="vol_solo", size_mib=10240, cpg="SSD_r6", provisioning_type="tpvv"),
    ]
    schedules: list[tuple[str, str, str]] = []
    req_set = SnapshotRequest(source="vvs_set", kind="set", snapshot_now=True,
                              every=4, unit="hours", expire_hours=24, name="sched_set")
    req_solo = SnapshotRequest(source="vol_solo", kind="volume", snapshot_now=True,
                               every=None, unit=None, expire_hours=24, name="sched_solo")
    intent = ProvisioningIntent(
        array=_creds(A_HOST), vcenter=_creds("192.0.2.2"),
        switch_f1=_creds("192.0.2.3"), switch_f2=_creds("192.0.2.4"),
        snapshots=SnapshotIntent(requests=[req_set, req_solo]),
    )
    view = SnapshotArrayView(
        host=A_HOST, name="ArrayA", os_version="10.5.55", time_zone="UTC",
        volumes=list(vols), vvsets={"vvs_set": ["vol_s1"]}, schedules=[],
    )
    plan = SnapshotPlan(actions=[
        SnapshotAction(kind="snapshot", name="vvs_set", source="vvs_set", state="create", members=["vol_s1"]),
        SnapshotAction(kind="snapshot", name="vol_solo", source="vol_solo", state="create", members=["vol_solo"]),
        SnapshotAction(kind="schedule", name="sched_set", source="vvs_set", state="create", members=["vol_s1"]),
    ])
    result = snap_apply.apply_plan(
        plan, view, intent, _approval("snapshots", recorder),
        wsapi_factory=lambda *_a: _FakeSnapWsapi(vols, recorder, seen),
        snap_cli_factory=lambda *_a: _FakeSnapCli(schedules, recorder, seen),
    )
    assert result.error is None
    return seen


# ------------------------------------------------------------------ scenario 5: replication/failover.py

class _FakeDrWsapi:
    def __init__(
        self, side: str, roles: dict[str, str], *, flipped_after_sync: bool,
        recorder: _SaveRecorder, seen: dict[str, dict[str, Any] | None],
    ) -> None:
        self.side = side
        self._roles = roles
        self._flipped_after_sync = flipped_after_sync
        self._recorder = recorder
        self._seen = seen

    def __enter__(self) -> _FakeDrWsapi:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def stop_remote_copy_group(self, _name: str) -> None:
        key = "failover:step1_stop" if self.side == "A" else "failover:step6_failback_stop"
        self._seen[key] = self._recorder.last()
        self._roles["p_status"] = self._roles["s_status"] = "Stopped"

    def remote_copy_dr_action(self, _name: str, action: int) -> None:
        if action == DR_ACTION_FAILOVER and self.side == "B":
            self._seen["failover:step2_failover"] = self._recorder.last()
            self._roles["s_role"], self._roles["s_status"] = "Primary-Rev", "Stopped"
        elif action == DR_ACTION_RECOVER:
            self._seen["failover:step4_recover"] = self._recorder.last()
            if self._flipped_after_sync:
                self._roles.update(p_role="Secondary", p_status="Started", s_role="Primary", s_status="Started")
            else:
                self._roles.update(p_role="Secondary-Rev", p_status="Started", s_role="Primary-Rev", s_status="Started")
        elif action == DR_ACTION_RESTORE:
            self._seen["failover:step6_restore"] = self._recorder.last()
            self._roles.update(p_role="Primary", p_status="Started", s_role="Secondary", s_status="Started")
        elif action == DR_ACTION_FAILOVER and self.side == "A":
            self._seen["failover:step6_failback_failover"] = self._recorder.last()
            self._roles.update(p_role="Primary", p_status="Started", s_role="Secondary", s_status="Started")
        else:
            raise AssertionError(f"unexpected DR action {action} on {self.side}")


def _failover_group(host: str, roles: dict[str, str]) -> RcGroup:
    is_a = host == A_HOST
    return RcGroup(
        name="grp" if is_a else "grp.r100",
        target="ArrayB" if is_a else "ArrayA",
        status=roles["p_status"] if is_a else roles["s_status"],
        role=roles["p_role"] if is_a else roles["s_role"],
        mode="Sync",
        volumes=[RcGroupVolume(local_name="v1", remote_name="v1", sync_status="Synced")],
    )


def _run_failover(*, flipped_after_sync: bool) -> dict[str, dict[str, Any] | None]:
    recorder = _SaveRecorder()
    seen: dict[str, dict[str, Any] | None] = {}
    roles = {"p_role": "Primary", "p_status": "Started", "s_role": "Secondary", "s_status": "Started"}

    def _read_array(creds: EndpointCreds) -> ReplicationArrayView:
        is_a = creds.host == A_HOST
        return ReplicationArrayView(
            host=creds.host, name="ArrayA" if is_a else "ArrayB",
            system_id=100 if is_a else 200, os_version="10.5.55", rc_status="Started",
            groups=[_failover_group(creds.host, roles)],
        )

    record = rc_failover.run_failover_test(
        _approval("failover", recorder, both=True),
        "grp",
        wsapi_factory=lambda _app, _purpose, side: _FakeDrWsapi(
            side, roles, flipped_after_sync=flipped_after_sync, recorder=recorder, seen=seen,
        ),
        read_fn=_read_array,
        read_group_fn=lambda creds, _name: _failover_group(creds.host, roles),
        sleep=lambda _s: None,
        limits={"auto_start": 0, "poll": 0},
    )
    assert record.result == "passed", record.error
    return seen


# ------------------------------------------------------------------ one parametrised test over every write site

def _has_note(field_name: str, *needles: str) -> Callable[[dict[str, Any]], None]:
    def _check(saved: dict[str, Any]) -> None:
        notes = saved.get(field_name, [])
        assert any(all(n in note for n in needles) for note in notes), (
            f"expected note matching {needles!r} in {field_name}, got {notes!r}"
        )
    return _check


def _has_partnership(removal_line: str, *note_needles: str) -> Callable[[dict[str, Any]], None]:
    def _check(saved: dict[str, Any]) -> None:
        removals = saved.get("removals_a", [])
        assert removal_line in removals, f"expected ADR 0025 removal {removal_line!r} in removals_a, got {removals!r}"
        _has_note("notes", *note_needles)(saved)
    return _check


def _has_failover(step_seq: int, recovery_needle: str, *observed_needles: str) -> Callable[[dict[str, Any]], None]:
    def _check(saved: dict[str, Any]) -> None:
        assert saved.get("failed_step") == step_seq, f"expected failed_step={step_seq}, got {saved.get('failed_step')}"
        assert f"Interrupted during step {step_seq}" in saved.get("error", ""), saved.get("error")
        assert "showrcopy groups" in saved.get("error", ""), saved.get("error")
        assert recovery_needle in saved.get("recovery_action", ""), saved.get("recovery_action")
        observed = saved.get("observed_state", "")
        for needle in observed_needles:
            assert needle in observed, f"expected {needle!r} in observed_state {observed!r}"
    return _check


_SITES: list[tuple[str, Callable[[], dict[str, dict[str, Any] | None]], Callable[[dict[str, Any]], None]]] = [
    # provisioning/apply.py (all 7 write sites)
    ("provisioning:ensure_host", _run_provisioning, _has_note("removal_notes", "host esx1", "showhost esx1")),
    ("provisioning:ensure_iscsi_host", _run_provisioning, _has_note("removal_notes", "host lin1", "showhost lin1")),
    ("provisioning:ensure_host_set", _run_provisioning, _has_note("removal_notes", "host set hs_main", "showhostset hs_main")),
    ("provisioning:ensure_volume", _run_provisioning, _has_note("removal_notes", "volume vol_full", "showvv vol_full")),
    ("provisioning:ensure_volume_set", _run_provisioning, _has_note("removal_notes", "volume set vvs_full", "showvvset vvs_full")),
    ("provisioning:ensure_vlun_create", _run_provisioning, _has_note("removal_notes", "export of vvs_full to hs_main", "showvlun -t")),
    ("provisioning:ensure_vlun_update", _run_provisioning, _has_note("removal_notes", "export of vvs_partial to hs_main", "showvlun -t")),
    # replication/apply.py (all 7 write sites)
    ("replication:test_volume", _run_replication_groups, _has_note("notes", "volume zz_rc_test_v01 on A", "showvv zz_rc_test_v01")),
    ("replication:test_vvset", _run_replication_groups, _has_note("notes", "volume set zz_rc_test on A", "showvvset zz_rc_test")),
    ("replication:create_group", _run_replication_groups, _has_note("notes", "Remote Copy group vvs_prod_rcg on A", "showrcopy groups vvs_prod_rcg")),
    ("replication:set_policy", _run_replication_groups, _has_note("notes", "policies on Remote Copy group vvs_prod_rcg", "showrcopy -d groups vvs_prod_rcg")),
    ("replication:admit_volume", _run_replication_groups, _has_note("notes", "admitted vol_prod into vvs_prod_rcg", "showrcopy groups vvs_prod_rcg")),
    ("replication:peer_vvset", _run_replication_groups, _has_note("notes", "volume set vvs_prod on B", "showvvset vvs_prod")),
    ("replication:start_group", _run_replication_groups, _has_note("notes", "Remote Copy group vvs_prod_rcg", "showrcopy groups vvs_prod_rcg")),
    # replication/partnership_apply.py (all 4 mutating SSH write sites — ADR 0025 removal line + inspect-first note)
    ("partnership:rcip_addr", _run_partnership, _has_partnership("controlport rcip delete -f 0:4:4", "10.93.18.11", "showport -rcip")),
    ("partnership:rcip_gw", _run_partnership, _has_partnership("controlport rcip delete -f 0:4:4", "10.93.18.11", "showport -rcip")),
    ("partnership:startrcopy", _run_partnership, _has_partnership("stoprcopy -f -stopgroups -clear", "Remote Copy (A)", "showrcopy")),
    ("partnership:creatercopytarget", _run_partnership, _has_partnership("removercopytarget ArrayB", "target ArrayB (A)", "showrcopy targets")),
    # snapshots/apply.py (all 3 write sites)
    ("snapshots:create_set_snapshot", _run_snapshots, _has_note("removal_notes", "snapshots of vvs_set", "showvv vol_s1.initial")),
    ("snapshots:create_snapshot", _run_snapshots, _has_note("removal_notes", "snapshots of vol_solo", "showvv vol_solo.initial")),
    ("snapshots:createsched", _run_snapshots, _has_note("removal_notes", "schedule vvs_set_snap", "showsched", "removesched -f vvs_set_snap")),
    # replication/failover.py (all 6 DR send sites across restore and failback paths)
    ("failover:step1_stop", lambda: _run_failover(flipped_after_sync=False), _has_failover(1, "if step 1 took effect:", "Primary/Started", "Secondary/Started")),
    ("failover:step2_failover", lambda: _run_failover(flipped_after_sync=False), _has_failover(2, "if step 2 took effect:", "Primary/Stopped", "Secondary/Stopped")),
    ("failover:step4_recover", lambda: _run_failover(flipped_after_sync=False), _has_failover(4, "if step 4 took effect:", "Primary-Rev/Stopped")),
    ("failover:step6_restore", lambda: _run_failover(flipped_after_sync=False), _has_failover(6, "setrcopygroup restore -f grp.r100", "Secondary-Rev/Started", "Primary-Rev/Started")),
    ("failover:step6_failback_stop", lambda: _run_failover(flipped_after_sync=True), _has_failover(6, "stoprcopygroup -f grp.r100", "Secondary/Started", "Primary/Started")),
    ("failover:step6_failback_failover", lambda: _run_failover(flipped_after_sync=True), _has_failover(6, "if step 6 took effect:", "Secondary/Stopped", "Primary/Stopped")),
]


@pytest.mark.parametrize(("site", "runner", "verify"), _SITES, ids=[s[0] for s in _SITES])
def test_record_is_saved_before_device_receives_write(
    site: str,
    runner: Callable[[], dict[str, dict[str, Any] | None]],
    verify: Callable[[dict[str, Any]], None],
) -> None:
    observations = runner()
    assert site in observations, f"write site {site} was never invoked"
    last_saved = observations[site]
    assert last_saved is not None, f"no record had been saved before {site}"
    verify(last_saved)
