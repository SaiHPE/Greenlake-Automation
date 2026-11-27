"""Unit and API tests for opt-in Brocade FOS SAN zoning apply (ADR 0033)."""

from __future__ import annotations

import time
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.documents.asbuilt import generate_asbuilt
from alletra_onboard.application.documents.asbuilt_model import AsBuiltData
from alletra_onboard.application.provisioning import zoning_apply
from alletra_onboard.application.provisioning.zoning_plan import (
    render_commands,
    render_peer_commands,
)
from alletra_onboard.application.runs.apply_record import APPLY_RECORD_ARTIFACT
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain import events
from alletra_onboard.domain.approval import Approval
from alletra_onboard.domain.errors import ApplyRecordError, BrocadeError
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunMode,
    WorkflowPhase,
)
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.shared import EndpointCreds, Fabric
from alletra_onboard.domain.zoning import AliasedWwpn, FabricZonePlan, ZoningPlan

HOST_WWPN = "51402EC02089CC1C"
HOST_DISP = "51:40:2e:c0:20:89:cc:1c"
ARR_WWPN = "20330002AC02D495"
ARR_DISP = "20:33:00:02:ac:02:d4:95"
PEER_WWPN = "21330002AC02D495"
PEER_DISP = "21:33:00:02:ac:02:d4:95"
SRC_WWPN = "20110002AC001234"
SRC_DISP = "20:11:00:02:ac:00:12:34"

SW_F1 = EndpointCreds(host="10.132.30.111", username="admin", password=SecretStr("pw1"))
SW_F2 = EndpointCreds(host="10.132.30.112", username="admin", password=SecretStr("pw2"))

CFGSHOW_BEFORE = """Defined configuration:
 cfg:   F2_CFG
                existing_zone
 zone:  existing_zone
                existing_h; existing_a
 alias: existing_h
                10:00:00:00:00:00:00:01
 alias: existing_a
                20:00:00:00:00:00:00:01

Effective configuration:
 cfg:   F2_CFG
 zone:  existing_zone
                10:00:00:00:00:00:00:01
                20:00:00:00:00:00:00:01
"""

CFGSHOW_AFTER = (
    CFGSHOW_BEFORE
    + """ zone:  zz_za_host_zz_za_arr
                51:40:2e:c0:20:89:cc:1c
                20:33:00:02:ac:02:d4:95
 zone:  zz_za_peer_zz_za_src
                21:33:00:02:ac:02:d4:95
                20:11:00:02:ac:00:12:34
"""
)


def _plan(*, active_cfg: str = "F2_CFG", include_peer: bool = False) -> ZoningPlan:
    fab2 = FabricZonePlan(
        fabric="F2",
        switch_host="10.132.30.112",
        active_cfg=active_cfg,
        hosts=[AliasedWwpn(wwpn=HOST_WWPN, display=HOST_DISP, role="host", fabric="F2", host_name="ELJR0NB1UV")],
        array_ports=[AliasedWwpn(wwpn=ARR_WWPN, display=ARR_DISP, role="array", fabric="F2", nsp="0:3:3", node=0)],
        pairs=[(HOST_WWPN, ARR_WWPN)],
        defined_names=["F2_CFG", "existing_zone", "existing_h", "existing_a"],
    )
    if include_peer:
        fab2.peer_ports = [AliasedWwpn(wwpn=PEER_WWPN, display=PEER_DISP, role="array", fabric="F2", nsp="1:3:3")]
        fab2.sources = [AliasedWwpn(wwpn=SRC_WWPN, display=SRC_DISP, role="array", fabric="F2", nsp="0:1:1")]
        fab2.peer_pairs = [(PEER_WWPN, SRC_WWPN)]
    return ZoningPlan(fabrics=[fab2])


class _FakeZoneWriter:
    """In-memory fake matching the BrocadeZoneWriter interface for unit tests (zero network)."""

    def __init__(
        self,
        *,
        cfgtransshow: str = "There is no outstanding zoning transaction\n",
        cfgtransshow_after_abort: str | None = None,
        cfgshow_before: str = CFGSHOW_BEFORE,
        cfgshow_after: str = CFGSHOW_AFTER,
        fail_on: str | None = None,
    ) -> None:
        self._trans = cfgtransshow
        self._trans_after_abort = cfgtransshow_after_abort
        self._before = cfgshow_before
        self._after = cfgshow_after
        self._fail_on = fail_on
        self.open_tx_on_fail = False
        self.fail_readback = False
        self.writes: list[str] = []
        self.reads: list[str] = []
        self._activated = False
        self._tx_open = False
        self._aborted = False

    def __enter__(self) -> _FakeZoneWriter:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def cfgtransshow(self) -> str:
        self.reads.append("cfgtransshow")
        if self._aborted and self._trans_after_abort is not None:
            return self._trans_after_abort
        if self._tx_open:
            return "Current transaction token is 0x1234\n"
        return self._trans

    def cfgshow(self) -> str:
        self.reads.append("cfgshow")
        if self._activated and self.fail_readback:
            raise BrocadeError("timeout reading cfgshow")
        return self._after if self._activated else self._before

    def write(self, command: str) -> str:
        self.writes.append(command)
        if self._fail_on and command.startswith(self._fail_on):
            if self.open_tx_on_fail:
                self._tx_open = True
            raise BrocadeError(f"simulated failure on {command}")
        if command == "cfgtransabort":
            self._aborted = True
            self._tx_open = False
            return "Transaction aborted\n"
        if command.startswith("cfgenable "):
            self._activated = True
            self._tx_open = False
            return "Updating flash ...\n"
        self._tx_open = True
        return ""


def _approval_with_recorder() -> tuple[Approval, list[dict[str, Any]]]:
    saved: list[dict[str, Any]] = []

    def save(model: BaseModel) -> None:
        saved.append(model.model_dump(mode="json"))

    approval = Approval(run_id="r1", purpose="zoning", switches={"odd": SW_F1, "even": SW_F2}, save_record=save)
    return approval, saved


# ------------------------------------------------------------------ build_apply_plan


def test_build_apply_plan_combines_host_and_peer_zones_and_builds_reverse_removals():
    plan = _plan(include_peer=True)
    aliases = {
        HOST_WWPN: "zz_za_host",
        ARR_WWPN: "zz_za_arr",
        PEER_WWPN: "zz_za_peer",
        SRC_WWPN: "zz_za_src",
    }
    cmds, skipped = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    peer_cmds, peer_skipped = render_peer_commands(plan, aliases)
    assert skipped == {"F2": []} and peer_skipped == {"F2": []}

    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds, peer_cmds)
    assert apply_plan.plan_id
    assert len(apply_plan.fabrics) == 1
    fab = apply_plan.fabrics[0]
    assert fab.fabric == "even" and fab.active_cfg == "F2_CFG"
    assert fab.commands == [
        f'alicreate "zz_za_host","{HOST_DISP}"',
        f'alicreate "zz_za_arr","{ARR_DISP}"',
        f'alicreate "zz_za_peer","{PEER_DISP}"',
        f'alicreate "zz_za_src","{SRC_DISP}"',
        'zonecreate "zz_za_host_zz_za_arr","zz_za_host;zz_za_arr"',
        'zonecreate "zz_za_peer_zz_za_src","zz_za_peer;zz_za_src"',
        'cfgadd "F2_CFG","zz_za_host_zz_za_arr;zz_za_peer_zz_za_src"',
        'cfgenable "F2_CFG" -f',
    ]
    assert fab.removals == [
        'cfgremove "F2_CFG","zz_za_host_zz_za_arr;zz_za_peer_zz_za_src"',
        'zonedelete "zz_za_peer_zz_za_src"',
        'zonedelete "zz_za_host_zz_za_arr"',
        'alidelete "zz_za_src"',
        'alidelete "zz_za_peer"',
        'alidelete "zz_za_arr"',
        'alidelete "zz_za_host"',
        'cfgenable "F2_CFG" -f',
    ]


def test_build_apply_plan_skips_fabric_without_active_cfg():
    plan = _plan(active_cfg="")
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    assert apply_plan.fabrics == []
    assert apply_plan.plan_id == ""


# ------------------------------------------------------------------ apply_zoning_plan


def test_apply_zoning_plan_happy_path_persists_undo_before_first_write(monkeypatch):
    plan = _plan(include_peer=True)
    aliases = {
        HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr",
        PEER_WWPN: "zz_za_peer", SRC_WWPN: "zz_za_src",
    }
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    peer_cmds, _ = render_peer_commands(plan, aliases)
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds, peer_cmds)

    approval, saved = _approval_with_recorder()
    order: list[str] = []
    writer = _FakeZoneWriter()
    orig_save = approval.save_record

    def tracking_save(model: BaseModel) -> None:
        order.append("save")
        assert orig_save is not None
        orig_save(model)

    approval.save_record = tracking_save
    orig_write = writer.write

    def tracking_write(cmd: str) -> str:
        order.append(f"write:{cmd.split()[0]}")
        return orig_write(cmd)

    monkeypatch.setattr(writer, "write", tracking_write)
    seen_objects: list[ZoningPlanObjects] = []

    def factory(_app: Approval, _fab: Fabric, objs: ZoningPlanObjects) -> _FakeZoneWriter:
        seen_objects.append(objs)
        return writer

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=factory)
    assert result.error is None
    assert len(result.fabrics) == 1
    fab_res = result.fabrics[0]
    assert fab_res.status == "applied"
    assert fab_res.verified_zones == ["zz_za_host_zz_za_arr", "zz_za_peer_zz_za_src"]
    assert fab_res.missing_zones == []
    assert fab_res.removals == apply_plan.fabrics[0].removals
    # First save happened BEFORE any write and already held the full removal set (STANDARD S5).
    assert order[0] == "save"
    assert saved[0]["fabrics"][0]["removals"] == apply_plan.fabrics[0].removals
    assert seen_objects[0].active_cfg == "F2_CFG"


def test_apply_refuses_when_open_transaction_exists():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(cfgtransshow="Current transaction token is 0x12345\n")

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    assert writer.writes == []
    assert result.error is not None and "already open" in result.error
    assert result.fabrics[0].status == "failed" and result.fabrics[0].removals == []


def test_apply_refuses_on_cfg_drift_or_existing_zone_drift():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)

    # Active cfg drifted
    approval1, _ = _approval_with_recorder()
    w1 = _FakeZoneWriter(cfgshow_before=CFGSHOW_BEFORE.replace("F2_CFG", "OTHER_CFG"))
    res1 = zoning_apply.apply_zoning_plan(approval1, apply_plan, writer_factory=lambda *_: w1)
    assert w1.writes == [] and res1.error is not None and "OTHER_CFG" in res1.error

    # Planned zone already exists
    approval2, _ = _approval_with_recorder()
    w2 = _FakeZoneWriter(cfgshow_before=CFGSHOW_AFTER)
    res2 = zoning_apply.apply_zoning_plan(approval2, apply_plan, writer_factory=lambda *_: w2)
    assert w2.writes == [] and res2.error is not None and "zz_za_host_zz_za_arr" in res2.error


def test_apply_mid_error_abort_confirmed_clears_removals():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(fail_on="zonecreate")

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    assert result.error is not None and "nothing persisted" in result.error
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.transaction_aborted is True
    assert "cfgtransabort" in writer.writes
    assert not any(c.startswith("cfgenable ") for c in writer.writes)
    assert fab_res.removals == []


def test_apply_mid_error_abort_unconfirmed_preserves_removals():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(
        fail_on="zonecreate",
        cfgtransshow_after_abort="Current transaction token is 0x999\n",
    )

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.transaction_aborted is False
    assert fab_res.removals == apply_plan.fabrics[0].removals


def test_apply_cfgenable_failure_runs_readback_and_inspect_first_guidance():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(fail_on="cfgenable", cfgshow_after=CFGSHOW_BEFORE)

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.error is not None and "Inspect the switch with cfgtransshow and cfgshow" in fab_res.error
    assert fab_res.removals == apply_plan.fabrics[0].removals
    assert writer.reads.count("cfgshow") >= 2


def test_first_write_failure_checks_cfgtransshow_and_aborts_if_open():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(fail_on="alicreate")
    writer.open_tx_on_fail = True

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.transaction_aborted is True
    assert "cfgtransabort" in writer.writes
    assert fab_res.removals == []


def test_readback_failure_after_cfgenable_checks_transaction_and_preserves_removals():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter()
    writer.fail_readback = True

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.error is not None and "Inspect the switch with cfgtransshow and cfgshow" in fab_res.error
    assert fab_res.removals == apply_plan.fabrics[0].removals
    assert writer.reads.count("cfgtransshow") >= 2


def test_missing_effective_section_fails_preflight_and_readback():
    defined_only = """Defined configuration:
 cfg:   F2_CFG
                existing_zone
 zone:  existing_zone
                existing_h; existing_a
 zone:  zz_za_host_zz_za_arr
                zz_za_host; zz_za_arr
 alias: zz_za_host
                51:40:2e:c0:20:89:cc:1c
 alias: zz_za_arr
                20:33:00:02:ac:02:d4:95
"""
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)

    # Pre-flight must refuse when no Effective configuration is active
    approval1, _ = _approval_with_recorder()
    w1 = _FakeZoneWriter(cfgshow_before=defined_only)
    res1 = zoning_apply.apply_zoning_plan(approval1, apply_plan, writer_factory=lambda *_: w1)
    assert w1.writes == [] and res1.error is not None and "No effective zoning configuration" in res1.error

    # Read-back must also fail if Effective section is missing (never fall back to Defined!)
    approval2, _ = _approval_with_recorder()
    w2 = _FakeZoneWriter(cfgshow_before=CFGSHOW_BEFORE, cfgshow_after=defined_only)
    res2 = zoning_apply.apply_zoning_plan(approval2, apply_plan, writer_factory=lambda *_: w2)
    assert res2.fabrics[0].status == "failed" and res2.error is not None and "effective cfg 'none'" in res2.error


def test_readback_fails_when_effective_zone_has_wrong_member_wwpns():
    wrong_members = (
        CFGSHOW_BEFORE
        + """ zone:  zz_za_host_zz_za_arr
                51:40:2e:c0:20:89:cc:1c
                20:99:99:99:ac:02:d4:95
"""
    )
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(cfgshow_after=wrong_members)

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    assert result.fabrics[0].status == "failed"
    assert result.fabrics[0].missing_zones == ["zz_za_host_zz_za_arr"]
    assert result.error is not None and "mismatched effective zone members" in result.error


def test_build_apply_plan_refuses_host_peer_collisions_and_dollar_aliases():
    plan = _plan(include_peer=True)
    host_cmds = {"F2": [f'alicreate "shared_a","{HOST_DISP}"', 'zonecreate "z1","shared_a;arr_a"']}
    peer_cmds = {"F2": [f'alicreate "shared_a","{PEER_DISP}"', 'zonecreate "z2","shared_a;src_a"']}
    with pytest.raises(ValueError, match="two different WWPNs"):
        zoning_apply.build_apply_plan(plan, {}, None, host_cmds, peer_cmds)

    zone_collision_host = {"F2": ['zonecreate "same_z","a1;b1"']}
    zone_collision_peer = {"F2": ['zonecreate "same_z","a2;b2"']}
    with pytest.raises(ValueError, match="two different member pairs"):
        zoning_apply.build_apply_plan(plan, {}, None, zone_collision_host, zone_collision_peer)

    dollar_cmds = {"F2": [f'alicreate "bad$name","{HOST_DISP}"', 'zonecreate "bad$name_arr","bad$name;arr"']}
    with pytest.raises(ValueError, match="cannot be applied"):
        zoning_apply.build_apply_plan(plan, {}, None, dollar_cmds)


def test_apply_record_error_on_f2_preserves_f1_applied_and_removals():
    fab1 = FabricZonePlan(
        fabric="F1", switch_host="10.132.30.111", active_cfg="F1_CFG",
        hosts=[AliasedWwpn(wwpn=HOST_WWPN, display=HOST_DISP, role="host", fabric="F1")],
        array_ports=[AliasedWwpn(wwpn=ARR_WWPN, display=ARR_DISP, role="array", fabric="F1", nsp="0:3:1")],
        pairs=[(HOST_WWPN, ARR_WWPN)], defined_names=["F1_CFG"],
    )
    fab2 = _plan().fabrics[0]
    two_fab_plan = ZoningPlan(fabrics=[fab1, fab2])
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(two_fab_plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(two_fab_plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)

    saves = {"count": 0}

    def flaky_save(_model: BaseModel) -> None:
        saves["count"] += 1
        if saves["count"] >= 3:
            raise ApplyRecordError("disk full")

    approval = Approval(
        run_id="r1", purpose="zoning", switches={"odd": SW_F1, "even": SW_F2}, save_record=flaky_save,
    )
    f1_writer = _FakeZoneWriter(
        cfgshow_before=CFGSHOW_BEFORE.replace("F2_CFG", "F1_CFG"),
        cfgshow_after=CFGSHOW_AFTER.replace("F2_CFG", "F1_CFG"),
    )
    f2_writer = _FakeZoneWriter()
    writers = {"odd": f1_writer, "even": f2_writer}

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda _a, f, _o: writers[f])
    assert result.error is not None and "disk full" in result.error
    assert result.fabrics[0].status == "applied"
    assert result.fabrics[0].removals == apply_plan.fabrics[0].removals
    assert result.fabrics[1].status == "failed"
    assert result.fabrics[1].removals == []
    assert f2_writer.writes == []


def test_apply_readback_detects_missing_zone():
    plan = _plan()
    aliases = {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"}
    cmds, _ = render_commands(plan, aliases, [(HOST_WWPN, ARR_WWPN)])
    apply_plan = zoning_apply.build_apply_plan(plan, aliases, [(HOST_WWPN, ARR_WWPN)], cmds)
    approval, _ = _approval_with_recorder()
    writer = _FakeZoneWriter(cfgshow_after=CFGSHOW_BEFORE)

    result = zoning_apply.apply_zoning_plan(approval, apply_plan, writer_factory=lambda *_: writer)
    assert result.error is not None and "did not find activated zone" in result.error
    fab_res = result.fabrics[0]
    assert fab_res.status == "failed"
    assert fab_res.missing_zones == ["zz_za_host_zz_za_arr"]
    assert fab_res.removals == apply_plan.fabrics[0].removals


# ------------------------------------------------------------------ as-built section


def test_asbuilt_adds_switch_apply_summary_only_when_applied(tmp_path):
    from docx import Document

    plan_dict = _plan().model_dump(mode="json")
    base = AsBuiltData(name="rack13", serial_no="SN1", zoning_plan=plan_dict, zoning_rendered={"commands": {"F2": ["cfgtransshow"]}})
    out_without = tmp_path / "without.docx"
    generate_asbuilt(base, out_without)
    text_without = "\n".join(p.text for p in Document(out_without).paragraphs)
    assert "Switch zoning applied" not in text_without

    base.zoning_apply = {
        "plan_id": "p1",
        "error": None,
        "fabrics": [{
            "fabric": "even",
            "switch_host": "10.132.30.112",
            "active_cfg": "F2_CFG",
            "status": "applied",
            "verified_zones": ["zz_za_host_zz_za_arr"],
            "missing_zones": [],
            "transaction_aborted": False,
            "removals": ['cfgremove "F2_CFG","zz_za_host_zz_za_arr"', 'cfgenable "F2_CFG" -f'],
        }],
    }
    out_with = tmp_path / "with.docx"
    generate_asbuilt(base, out_with)
    text_with = "\n".join(p.text for p in Document(out_with).paragraphs)
    assert "Switch zoning applied" in text_with
    assert "Switch removal command set" in text_with
    assert 'cfgremove "F2_CFG","zz_za_host_zz_za_arr"' in text_with
    assert "never writes to a switch" not in text_with

    # Merging across two applies (F1 applied + F2 failed, then F2 applied) keeps both fabrics & valid removals
    merged = AsBuiltData(
        name="rack13", serial_no="SN1", zoning_plan=plan_dict,
        zoning_rendered={"commands": {"F2": ["cfgtransshow"]}},
        zoning_applies=[
            {
                "plan_id": "p1", "error": "F2 failed",
                "fabrics": [
                    {"fabric": "odd", "switch_host": "10.132.30.111", "active_cfg": "F1_CFG", "status": "applied",
                     "verified_zones": ["z_f1"], "missing_zones": [], "transaction_aborted": False,
                     "removals": ['cfgremove "F1_CFG","z_f1"', 'zonedelete "z_f1"', 'cfgenable "F1_CFG" -f']},
                    {"fabric": "even", "switch_host": "10.132.30.112", "active_cfg": "F2_CFG", "status": "failed",
                     "verified_zones": [], "missing_zones": [], "transaction_aborted": False, "removals": []},
                ],
            },
            {
                "plan_id": "p2", "error": None,
                "fabrics": [
                    {"fabric": "even", "switch_host": "10.132.30.112", "active_cfg": "F2_CFG", "status": "applied",
                     "verified_zones": ["z_f2"], "missing_zones": [], "transaction_aborted": False,
                     "removals": ['cfgremove "F2_CFG","z_f2"', 'zonedelete "z_f2"', 'cfgenable "F2_CFG" -f']},
                ],
            },
        ],
    )
    out_merged = tmp_path / "merged.docx"
    generate_asbuilt(merged, out_merged)
    text_merged = "\n".join(p.text for p in Document(out_merged).paragraphs)
    assert 'cfgremove "F1_CFG","z_f1"' in text_merged and 'cfgenable "F1_CFG" -f' in text_merged
    assert 'cfgremove "F2_CFG","z_f2"' in text_merged and 'cfgenable "F2_CFG" -f' in text_merged


def test_interrupted_zoning_apply_recovery_names_switch_and_cfgtransshow(tmp_path):
    import json

    service, _client, run_id = _seed_run(tmp_path)
    blob = json.dumps({
        "event_type": "zoning.apply.failed",
        "after": 0,
        "payload": {"plan_id": "p1", "fabrics": [], "error": None},
    }).encode("utf-8")
    service.store.save_artifact(run_id, APPLY_RECORD_ARTIFACT, blob)
    assert service.coordinator.recover_interrupted_apply(run_id) is True
    failed = next(e for e in service.list_events(run_id) if e.event_type == "zoning.apply.failed")
    assert "cfgtransshow" in failed.message and "cfgtransabort" in failed.message
    assert "Inspect the array" not in failed.message


# ------------------------------------------------------------------ API end-to-end


def _seed_run(tmp_path) -> tuple[OnboardingService, TestClient, str]:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    item = ArrayWorkItem(
        serial_number="SN001", part_number="S0B84A", subscription_key=SecretStr("k"),
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.1.1/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.132.30.121", mask="255.255.255.0", gateway="10.132.30.1",
                              dns=["10.132.30.2"], ntp="ntp.example.com", timezone="UTC"),
        dscc_setup=DsccSetupConfig(system_name="rack13", country="India"),
    )
    intent = ProvisioningIntent(
        array=EndpointCreds(host="10.132.30.121", username="3paradm", password=SecretStr("apw")),
        vcenter=EndpointCreds(host="10.132.30.2", username="vc", password=SecretStr("vpw")),
        switch_f1=SW_F1, switch_f2=SW_F2,
    )
    run = service.create_run(
        item, mode=RunMode.CUSTOM, selected_steps=["discover", "zoning"], provisioning_intent=intent,
    )
    return service, TestClient(create_app(service)), run.run_id


def test_api_zoning_render_and_apply_requires_valid_plan_and_emits_typed_events(tmp_path, monkeypatch):
    service, raw_client, run_id = _seed_run(tmp_path)
    fake_writer = _FakeZoneWriter()
    monkeypatch.setattr(zoning_apply, "make_brocade_writer", lambda *_args: fake_writer)

    with raw_client as client:
        # Apply before render -> 409, zero writes
        assert client.post(f"/runs/{run_id}/zoning/apply", json={"approved_plan": "none"}).status_code == 409
        assert fake_writer.writes == []

        # Render returns apply_plan_id & apply_fabrics
        render = client.post("/zoning/render", json={
            "run_id": run_id,
            "plan": _plan().model_dump(mode="json"),
            "aliases": {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"},
            "selected_pairs": [[HOST_WWPN, ARR_WWPN]],
        })
        assert render.status_code == 200, render.text
        body = render.json()
        plan_id = body["apply_plan_id"]
        assert plan_id and len(body["apply_fabrics"]) == 1

        # Wrong or missing approved_plan -> 409, zero writes
        assert client.post(f"/runs/{run_id}/zoning/apply", json={"approved_plan": "wrong"}).status_code == 409
        assert client.post(f"/runs/{run_id}/zoning/apply", json={}).status_code == 409
        assert fake_writer.writes == []

        # Real approved_plan -> 200, executes and emits typed zoning.applied
        applied = client.post(f"/runs/{run_id}/zoning/apply", json={"approved_plan": plan_id})
        assert applied.status_code == 200, applied.text
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if any(e.event_type in ("zoning.applied", "zoning.apply.failed") for e in service.list_events(run_id)):
                break
            time.sleep(0.05)

        ev_types = [e.event_type for e in service.list_events(run_id)]
        assert "zoning.apply.started" in ev_types
        assert "zoning.applied" in ev_types
        applied_ev = next(e for e in service.list_events(run_id) if e.event_type == "zoning.applied")
        assert applied_ev.data["result"]["fabrics"][0]["verified_zones"] == ["zz_za_host_zz_za_arr"]

        # Plan is single-use: replaying the same approved_plan -> 409
        assert client.post(f"/runs/{run_id}/zoning/apply", json={"approved_plan": plan_id}).status_code == 409


def test_api_rejects_mismatched_switch_host_or_active_cfg_and_blocks_dollar_alias(tmp_path):
    service, raw_client, run_id = _seed_run(tmp_path)
    stored_plan = _plan()
    service.coordinator.emit(
        run_id, WorkflowPhase.STORAGE_ZONING, events.ZONING_PLAN,
        "Zoning plan ready", events.ZoningPlanData(plan=stored_plan),
    )

    with raw_client as client:
        # Forged switch_host does not match run intent -> 409
        forged_host = _plan()
        forged_host.fabrics[0].switch_host = "10.99.99.99"
        resp_host = client.post("/zoning/render", json={
            "run_id": run_id,
            "plan": forged_host.model_dump(mode="json"),
            "aliases": {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"},
            "selected_pairs": [[HOST_WWPN, ARR_WWPN]],
        })
        assert resp_host.status_code == 409

        # Forged active_cfg does not match stored zoning.plan -> 409
        forged_cfg = _plan(active_cfg="EVIL_CFG")
        resp_cfg = client.post("/zoning/render", json={
            "run_id": run_id,
            "plan": forged_cfg.model_dump(mode="json"),
            "aliases": {HOST_WWPN: "zz_za_host", ARR_WWPN: "zz_za_arr"},
            "selected_pairs": [[HOST_WWPN, ARR_WWPN]],
        })
        assert resp_cfg.status_code == 409

        # Alias with '$' is legal in FOS 8.1+ copy-paste, but blocked from direct switch apply
        resp_dollar = client.post("/zoning/render", json={
            "run_id": run_id,
            "plan": stored_plan.model_dump(mode="json"),
            "aliases": {HOST_WWPN: "zz$host", ARR_WWPN: "zz_za_arr"},
            "selected_pairs": [[HOST_WWPN, ARR_WWPN]],
        })
        assert resp_dollar.status_code == 200
        body = resp_dollar.json()
        assert body["apply_plan_id"] is None and body["apply_fabrics"] == []
        assert any("Direct switch apply is unavailable" in w for w in body["warnings"].get("apply", []))
