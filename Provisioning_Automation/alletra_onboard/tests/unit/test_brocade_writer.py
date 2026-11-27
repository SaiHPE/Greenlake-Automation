"""Unit tests for the opt-in Brocade FOS write-scoped SSH client (ADR 0033, ADR 0025)."""

from __future__ import annotations

from typing import Any, cast

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.fabric.brocade_client import ALLOWED_READ, BrocadeClient
from alletra_onboard.adapters.fabric.brocade_writer import (
    BrocadeZoneWriter,
    zoning_object_refusal,
    zoning_write_refusal,
)
from alletra_onboard.domain.approval import Approval, ApprovalError
from alletra_onboard.domain.errors import BrocadeError, BrocadeRefused
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.shared import EndpointCreds

SW_F1 = EndpointCreds(host="10.132.30.111", username="admin", password=SecretStr("sw-secret-1"))
SW_F2 = EndpointCreds(host="10.132.30.112", username="admin", password=SecretStr("sw-secret-2"))

OBJECTS = ZoningPlanObjects(
    active_cfg="F2_CFG",
    aliases=(
        ("zz_za_host", "51402EC02089CC1C"),
        ("zz_za_arr", "20330002AC02D495"),
    ),
    zones=(
        ("zz_za_host_zz_za_arr", "zz_za_host", "zz_za_arr"),
        ("zz_za_peer_zz_za_src", "zz_za_peer", "zz_za_src"),
    ),
)


def _zoning_approval(*, spent: bool = False) -> Approval:
    return Approval(run_id="r1", purpose="zoning", switches={"even": SW_F2}, spent=spent)


class _StubWriter(BrocadeZoneWriter):
    """BrocadeZoneWriter with `_exec_status` stubbed so no network connection is opened."""

    def __init__(self, approval: Approval, objects: ZoningPlanObjects, responses: dict[str, tuple[int, str]]) -> None:
        super().__init__(approval, "even", objects)
        self._responses = responses
        self.sent: list[str] = []

    def _exec_status(self, command: str) -> tuple[int, str]:
        self.sent.append(command)
        return self._responses.get(command, (0, ""))


# ------------------------------------------------------------------ exact forms & refusals


@pytest.mark.parametrize("command", [
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c"',
    'alicreate "zz_za_arr","20:33:00:02:ac:02:d4:95"',
    'zonecreate "zz_za_host_zz_za_arr","zz_za_host;zz_za_arr"',
    'cfgadd "F2_CFG","zz_za_host_zz_za_arr"',
    'cfgadd "F2_CFG","zz_za_host_zz_za_arr;zz_za_peer_zz_za_src"',
    'cfgenable "F2_CFG" -f',
    "cfgtransabort",
])
def test_allowed_exact_forms_and_plan_objects_pass(command: str):
    assert zoning_write_refusal(command) is None
    assert zoning_object_refusal(command, OBJECTS) is None


@pytest.mark.parametrize("bad_command", [
    # shell metacharacters & semicolon outside member list
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c"; cfgclear',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c" | cat',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c" && id',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c" `id`',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c" $(id)',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c"\ncfgclear',
    'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c" > /tmp/x',
    "alicreate 'zz_za_host','51:40:2e:c0:20:89:cc:1c'",
    "cfgtransabort; cfgclear",
    "cfgtransabort --force",
    # malformed WWPN / names / missing -f
    'alicreate "zz_za_host","51:40:2E:C0:20:89:CC:1C"',
    'alicreate "zz_za_host","51402ec02089cc1c"',
    'alicreate "bad name","51:40:2e:c0:20:89:cc:1c"',
    'zonecreate "zz_za_host_zz_za_arr","zz_za_host"',
    'zonecreate "zz_za_host_zz_za_arr","zz_za_host;zz_za_arr;third"',
    'cfgadd "F2_CFG","zz_za_host_zz_za_arr;;zz_za_peer_zz_za_src"',
    'cfgadd "F2_CFG","zz_za_host_zz_za_arr;zz_za_host_zz_za_arr"',
    'cfgenable "F2_CFG"',
    "cfgenable F2_CFG -f",
    # forbidden / destructive verbs
    "cfgsave",
    "cfgsave -f",
    'cfgdelete "F2_CFG"',
    "cfgclear",
    "cfgdisable",
    'zonedelete "zz_za_host_zz_za_arr"',
    'alidelete "zz_za_host"',
    'cfgremove "F2_CFG","zz_za_host_zz_za_arr"',
])
def test_disallowed_forms_are_refused(bad_command: str):
    assert zoning_write_refusal(bad_command) is not None


@pytest.mark.parametrize("out_of_plan", [
    'alicreate "other_host","51:40:2e:c0:20:89:cc:1c"',
    'alicreate "zz_za_host","10:00:00:00:00:00:00:99"',
    'zonecreate "other_zone","zz_za_host;zz_za_arr"',
    'zonecreate "zz_za_host_zz_za_arr","zz_za_arr;zz_za_host"',
    'cfgadd "OTHER_CFG","zz_za_host_zz_za_arr"',
    'cfgadd "F2_CFG","other_zone"',
    'cfgadd "F2_CFG","zz_za_host_zz_za_arr;other_zone"',
    'cfgenable "OTHER_CFG" -f',
])
def test_well_formed_commands_outside_approved_plan_are_refused(out_of_plan: str):
    assert zoning_write_refusal(out_of_plan) is None
    assert zoning_object_refusal(out_of_plan, OBJECTS) is not None


def test_cfgenable_refused_when_plan_has_zero_zones():
    empty_objects = ZoningPlanObjects(active_cfg="F2_CFG", aliases=(), zones=())
    assert zoning_write_refusal('cfgenable "F2_CFG" -f') is None
    assert zoning_object_refusal('cfgenable "F2_CFG" -f', empty_objects) is not None


def test_non_empty_output_on_additive_verbs_and_cfgenable_prompt_fail():
    ali_cmd = 'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c"'
    cfg_cmd = 'cfgenable "F2_CFG" -f'
    writer = _StubWriter(
        _zoning_approval(),
        OBJECTS,
        {
            ali_cmd: (0, "unexpected warning banner\n"),
            cfg_cmd: (0, "Do you want to enable 'F2_CFG' (yes, y, no, n): [no] \n"),
        },
    )
    with pytest.raises(BrocadeError, match="unexpected warning banner"):
        writer.write(ali_cmd)
    with pytest.raises(BrocadeError, match="Do you want to enable"):
        writer.write(cfg_cmd)


def test_cfgenable_with_transaction_in_cfg_name_does_not_false_fail():
    objs = ZoningPlanObjects(
        active_cfg="test_transaction_cfg",
        aliases=OBJECTS.aliases,
        zones=OBJECTS.zones,
    )
    cmd = 'cfgenable "test_transaction_cfg" -f'
    writer = _StubWriter(
        _zoning_approval(),
        objs,
        {cmd: (0, 'Updating flash ...\nZone configuration "test_transaction_cfg" has been enabled.\n')},
    )
    assert "has been enabled" in writer.write(cmd)


# ------------------------------------------------------------------ approval gating


def test_constructor_requires_live_zoning_approval_for_fabric():
    with pytest.raises(ApprovalError):
        BrocadeZoneWriter(cast(Any, None), "even", OBJECTS)
    with pytest.raises(ApprovalError):
        BrocadeZoneWriter(_zoning_approval(spent=True), "even", OBJECTS)
    wrong_purpose = Approval(run_id="r1", purpose="storage", switches={"even": SW_F2})
    with pytest.raises(ApprovalError):
        BrocadeZoneWriter(wrong_purpose, "even", OBJECTS)
    only_f1 = Approval(run_id="r1", purpose="zoning", switches={"odd": SW_F1})
    with pytest.raises(ApprovalError):
        BrocadeZoneWriter(only_f1, "even", OBJECTS)


def test_write_refusal_logs_and_sends_nothing():
    records: list[dict] = []
    token = command_log.bind(records.append)
    try:
        writer = _StubWriter(_zoning_approval(), OBJECTS, {})
        with pytest.raises(BrocadeRefused):
            writer.write("cfgsave")
        with pytest.raises(BrocadeRefused):
            writer.write('cfgenable "OTHER_CFG" -f')
    finally:
        command_log.unbind(token)
    assert writer.sent == []
    assert len(records) == 2
    assert all(r["transport"] == "fos" and r["write"] is True and r["ok"] is False for r in records)


def test_spent_approval_refuses_further_writes():
    approval = _zoning_approval()
    writer = _StubWriter(approval, OBJECTS, {})
    approval.spent = True
    records: list[dict] = []
    token = command_log.bind(records.append)
    try:
        with pytest.raises(ApprovalError):
            writer.write('cfgenable "F2_CFG" -f')
    finally:
        command_log.unbind(token)
    assert writer.sent == []
    assert len(records) == 1 and records[0]["write"] is True and records[0]["ok"] is False


def test_write_succeeds_and_detects_exit_or_fos_error_lines():
    ok_cmd = 'cfgenable "F2_CFG" -f'
    err_cmd = 'alicreate "zz_za_host","51:40:2e:c0:20:89:cc:1c"'
    writer = _StubWriter(
        _zoning_approval(),
        OBJECTS,
        {
            ok_cmd: (0, 'Updating flash ...\nZone configuration "F2_CFG" has been enabled.\n'),
            "cfgtransabort": (0, "There is no outstanding zoning transaction\n"),
            err_cmd: (0, 'Error: "zz_za_host" already exists.\n'),
            'zonecreate "zz_za_host_zz_za_arr","zz_za_host;zz_za_arr"': (1, "failed to create zone"),
        },
    )
    records: list[dict] = []
    token = command_log.bind(records.append)
    try:
        assert "Updating flash" in writer.write(ok_cmd)
        assert "no outstanding" in writer.write("cfgtransabort").lower()
        with pytest.raises(BrocadeError, match="already exists"):
            writer.write(err_cmd)
        with pytest.raises(BrocadeError, match="failed to create zone"):
            writer.write('zonecreate "zz_za_host_zz_za_arr","zz_za_host;zz_za_arr"')
    finally:
        command_log.unbind(token)
    assert [r["ok"] for r in records] == [True, True, False, False]
    assert all(r["write"] is True and r["transport"] == "fos" for r in records)


def test_cfgenable_strip_only_replaces_quoted_cfg_name():
    objs = ZoningPlanObjects(
        active_cfg="fail",
        aliases=(("zz_za_host", "51402ec02089cc1c"), ("zz_za_arr", "20330002ac02d495")),
        zones=(("zz_za_host_zz_za_arr", "zz_za_host", "zz_za_arr"),),
    )
    cmd = 'cfgenable "fail" -f'
    writer = _StubWriter(_zoning_approval(), objs, {cmd: (0, "Commit failed\n")})
    with pytest.raises(BrocadeError, match="Commit failed"):
        writer.write(cmd)
    ok_writer = _StubWriter(
        _zoning_approval(),
        objs,
        {cmd: (0, 'Zone configuration "fail" has been enabled.\n')},
    )
    assert "enabled" in ok_writer.write(cmd)


# ------------------------------------------------------------------ read-only BrocadeClient invariant


def test_read_only_brocade_client_still_has_no_write_surface():
    client = BrocadeClient("10.132.30.112", "admin", "pw")
    assert not hasattr(client, "write")
    for verb in ("alicreate", "zonecreate", "cfgadd", "cfgenable", "cfgsave", "cfgtransabort", "cfgclear"):
        assert verb not in ALLOWED_READ
        with pytest.raises(BrocadeRefused):
            client.read(verb)
