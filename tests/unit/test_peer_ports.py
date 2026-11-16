"""SPEC-025 (BL-26) — peer ports for migration, set up by the tool.

Two kinds of test live here:

* Guards on today's behaviour (no marker). They pass now and pin the facts the design stands on: the
  Remote Copy write client and the read client refuse every `controlport` form a peer port needs, host
  zoning never offers a peer FC port, and `showhost -d` names the login that makes a port busy.
* The feature (strict xfail, see docs/workpackets/BL-26.md). Each turns green, and must lose its marker,
  when the work-packet step that builds it lands.

Captures used (real output, never edited): rack13-ARCUS `rcip_pair/before/alletra/showport.txt`
(2026-11-03) with `rack13_array/showhost_d.txt` and `showvlun_a.txt` (2026-09-13: same array, an earlier
day); D22U27 `rc_pair/D22U27/showport.txt` (2026-10-07) with `d22u27_iscsi/showhost_d.txt` (2026-10-26);
E18U31 `rc_pair/E18U31/showport.txt` (2026-10-07, the only array with FC peer ports); the Primera
`rcip_pair/before/primera/showport.txt` (2026-11-03). What was never captured (`showport -par`) is given
as model objects, not as invented array text.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from alletra_onboard.adapters.array.cli_client import refusal
from alletra_onboard.adapters.array.rc_cli_client import rc_write_refusal
from alletra_onboard.application.provisioning.discovery import (
    UNCLAIMED_HOST,
    parse_ports,
    parse_showhost,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures"
RACK13_SHOWPORT = FIX / "rcip_pair" / "before" / "alletra" / "showport.txt"
RACK13_SHOWHOST = FIX / "rack13_array" / "showhost_d.txt"
RACK13_SHOWVLUN = FIX / "rack13_array" / "showvlun_a.txt"
D22U27_SHOWPORT = FIX / "rc_pair" / "D22U27" / "showport.txt"
D22U27_SHOWHOST = FIX / "d22u27_iscsi" / "showhost_d.txt"
E18U31_SHOWPORT = FIX / "rc_pair" / "E18U31" / "showport.txt"
PRIMERA_SHOWPORT = FIX / "rcip_pair" / "before" / "primera" / "showport.txt"
# Owed by lab/peer_port_capture.py (not yet run): the files the parser tests expect.
PEER_FIX = FIX / "peer_ports"
E18U31_SHOWPORT_PAR = PEER_FIX / "E18U31" / "showport_par.txt"

NOT_BUILT = pytest.mark.xfail(reason="BL-26: not built yet, see docs/workpackets/BL-26.md", strict=True)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------------ guards: today's behaviour (pass now)

@pytest.mark.parametrize("command", [
    "controlport offline 0:3:2",
    "controlport config peer -ct point -f 0:3:2",
    "controlport rst 0:3:2",
])
def test_neither_existing_client_may_change_a_port_mode(command):
    """ADR 0015 §1 keeps `offline` and `config` off the Remote Copy client; ADR 0001 keeps the read client
    to show commands. A peer port therefore needs ADR 0018's own client, never a wider existing one."""
    assert rc_write_refusal(command)
    assert refusal(command)


def test_host_zoning_never_offers_a_peer_fc_port():
    """E18U31's peer ports (initiator, Type peer) are not host targets; discovery leaves them out."""
    nsps = {p.label for p in parse_ports(_text(E18U31_SHOWPORT), {})}
    assert "0:3:2" not in nsps and "1:3:2" not in nsps
    assert {"0:3:1", "0:3:4", "1:3:1", "1:3:4"} <= nsps


def test_showhost_names_the_unclaimed_login_that_makes_d22u27_1_3_2_busy():
    hosts = {h.name: h for h in parse_showhost(_text(D22U27_SHOWHOST))}
    assert "1:3:2" in hosts[UNCLAIMED_HOST].wwpns["1000040973C52799"]


# ------------------------------------------------------------------ R1: the sheet

A_HOST = "10.132.30.121"


def _sheet(rows):
    from alletra_onboard.application.platform import init_sheet
    from alletra_onboard.domain.models import RunMode

    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D2K014S", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[], peer_ports=rows)
    parsed = init_sheet.parse_workbook_bytes(data, mode=RunMode.CUSTOM, selected_steps=["ports"])
    return parsed.provisioning_intent.peer_ports


ROWS = [{"port": "0:3:2", "source_wwpns": "20:31:00:02:ac:02:ac:38"},
        {"port": "1:3:2", "source_wwpns": "21310002AC02AC38"}]


@NOT_BUILT
def test_the_peer_ports_tab_parses_into_the_intent():
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    assert _sheet(ROWS) == PeerPortIntent(ports=[
        PeerPortRequest(nsp="0:3:2", source_wwpns=["20310002AC02AC38"]),
        PeerPortRequest(nsp="1:3:2", source_wwpns=["21310002AC02AC38"]),
    ])


@NOT_BUILT
def test_a_workbook_without_the_tab_has_no_peer_ports():
    assert _sheet(None) is None


@NOT_BUILT
@pytest.mark.parametrize("rows, why", [
    ([{**ROWS[0], "port": "0-3-2"}, ROWS[1]], "Port must be N:S:P, like 0:3:2"),
    ([ROWS[0], ROWS[0], ROWS[1]], "port 0:3:2 is named twice"),
    ([ROWS[0]], "peer ports go in pairs across nodes"),
    ([ROWS[0], {**ROWS[1], "port": "0:3:1"}], "peer ports go in pairs across nodes"),
    ([{**ROWS[0], "source_wwpns": "zz"}, ROWS[1]], "'zz' is not a WWPN"),
])
def test_a_wrong_peer_port_row_is_refused_with_a_sentence(rows, why):
    with pytest.raises(ValueError, match=re.escape(why)):
        _sheet(rows)


# ------------------------------------------------------------------ R2: the read

@NOT_BUILT
def test_e18u31_peer_ports_read_with_their_own_node_wwn():
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    ports = parse_showport_ports(_text(E18U31_SHOWPORT))
    p = ports["0:3:2"]
    assert (p.mode, p.state, p.type, p.protocol) == ("initiator", "ready", "peer", "FC")
    assert (p.node_wwn, p.port_wwn) == ("2FF70202AC02DEF2", "20320202AC02DEF2")
    assert ports["0:3:1"].node_wwn == "2FF70002AC02DEF2"      # a host port of the same array


@NOT_BUILT
def test_the_primeras_partner_and_failover_state_are_read():
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    p = parse_showport_ports(_text(PRIMERA_SHOWPORT))["0:3:1"]
    assert (p.partner, p.failover_state) == ("1:3:1", "failed_over")


@NOT_BUILT
def test_showport_par_gives_the_connection_mode_to_restore():
    """Needs the capture: tests/fixtures/peer_ports/E18U31/showport_par.txt (lab/peer_port_capture.py)."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_par

    params = parse_showport_par(_text(E18U31_SHOWPORT_PAR))
    assert (params["0:3:2"].connmode, params["0:3:2"].conntype) == ("peer", "point")
    assert params["0:3:1"].connmode == "host"


# ------------------------------------------------------------------ R3: the plan

def _rack13_view():
    from alletra_onboard.application.provisioning.peer_ports import build_view
    from alletra_onboard.domain.peer_ports import PortParams

    view = build_view(_text(RACK13_SHOWPORT), showhost_d=_text(RACK13_SHOWHOST), showvlun_a=_text(RACK13_SHOWVLUN))
    # rack13's `showport -par` was never captured: these are model inputs, not array output.
    for nsp in ("0:3:1", "0:3:2", "1:3:1", "1:3:2", "0:3:3"):
        view.params[nsp] = PortParams(nsp=nsp, connmode="host", conntype="point")
    return view


def _intent(*nsps):
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    return PeerPortIntent(ports=[PeerPortRequest(nsp=n) for n in nsps])


def _by_port(plan):
    return {a.nsp: a for a in plan.actions}


@NOT_BUILT
def test_two_free_fc_ports_on_two_nodes_are_planned_with_their_undo():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), _rack13_view())
    acts = _by_port(plan)
    assert not plan.blockers
    for nsp in ("0:3:2", "1:3:2"):
        assert acts[nsp].state == "create"
        assert acts[nsp].commands[0] == f"controlport offline {nsp}"
        assert f"controlport config peer -ct point -f {nsp}" in acts[nsp].commands
        assert acts[nsp].undo[:2] == [f"controlport offline {nsp}", f"controlport config host -ct point -f {nsp}"]
    assert any("loss_sync" in n for n in plan.notes)          # both ports have no link on 2026-11-03


@NOT_BUILT
def test_a_port_that_serves_hosts_is_a_conflict_named_by_its_host():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:3:3", "1:3:2"), _rack13_view()))["0:3:3"]
    assert act.state == "conflict" and not act.commands
    assert "serves hosts" in act.reason and "10.132.30.136" in act.reason


@NOT_BUILT
def test_an_ip_port_is_not_a_peer_port_candidate():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:4:3", "1:3:2"), _rack13_view()))["0:4:3"]
    assert act.state == "conflict" and "is not a Fibre Channel port" in act.reason


@NOT_BUILT
def test_a_port_not_on_the_array_is_a_conflict():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:9:1", "1:3:2"), _rack13_view()))["0:9:1"]
    assert act.state == "conflict" and "is not on this array" in act.reason


@NOT_BUILT
def test_a_peer_label_on_a_host_port_never_makes_it_a_peer_port():
    """D22U27 1:3:2 is labelled `Peer_port`, Type host, with a login (LESSONS 42): a conflict, and with
    0:3:2 the only candidate the plan has one node and blocks."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    view = build_view(_text(D22U27_SHOWPORT), showhost_d=_text(D22U27_SHOWHOST))
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    act = _by_port(plan)["1:3:2"]
    assert act.state == "conflict" and "serves hosts" in act.reason and "1000040973C52799" in act.reason
    assert any("pairs across nodes" in b for b in plan.blockers)


@NOT_BUILT
def test_ports_already_in_peer_mode_exist_and_need_nothing():
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(E18U31_SHOWPORT)))
    assert [a.state for a in plan.actions] == ["exists", "exists"]
    assert not plan.blockers and not any(a.commands for a in plan.actions)


@NOT_BUILT
def test_a_persistent_port_partner_that_failed_over_is_a_conflict():
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:3:1", "1:3:4"), build_view(_text(PRIMERA_SHOWPORT))))["0:3:1"]
    assert act.state == "conflict" and "failover partner of 1:3:1" in act.reason


@NOT_BUILT
def test_a_create_without_the_previous_connection_mode_is_blocked():
    """No `showport -par` read means no removal set; the plan must not offer a change it cannot undo."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(RACK13_SHOWPORT)))
    assert any("showport -par" in b for b in plan.blockers)


# ------------------------------------------------------------------ R4/R5: apply and the removal set

class _Writer:
    """A fake port write client: records commands; answers '' unless told to refuse one."""

    def __init__(self, refuse: str = "") -> None:
        self.sent: list[str] = []
        self.refuse = refuse

    def write(self, command: str, timeout=None) -> str:
        self.sent.append(command)
        return "Error: refused by the fake" if command == self.refuse else ""


def _after(view, *peer_nsps):
    """The read-back as model objects: the planned ports now Type peer (no capture of this exists)."""
    from alletra_onboard.domain.peer_ports import PortParams

    out = view.model_copy(deep=True)
    for nsp in peer_nsps:
        out.ports[nsp] = out.ports[nsp].model_copy(update={"type": "peer", "mode": "initiator", "state": "ready"})
        out.params[nsp] = PortParams(nsp=nsp, connmode="peer", conntype="point")
    return out


@NOT_BUILT
def test_apply_sends_offline_then_config_per_port_and_undoes_exactly_them():
    from alletra_onboard.application.provisioning.peer_ports import (
        apply_peer_ports,
        plan_peer_ports,
    )

    view = _rack13_view()
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    writer = _Writer()
    result = apply_peer_ports(plan, writer=writer, read=lambda: _after(view, "0:3:2", "1:3:2"))
    assert result.error is None and result.changed == ["0:3:2", "1:3:2"]
    assert writer.sent[:2] == ["controlport offline 0:3:2", "controlport config peer -ct point -f 0:3:2"]
    assert result.removals[:2] == ["controlport offline 1:3:2", "controlport config host -ct point -f 1:3:2"]


@NOT_BUILT
def test_a_refused_config_stops_and_the_removal_set_names_only_what_changed():
    from alletra_onboard.application.provisioning.peer_ports import (
        apply_peer_ports,
        plan_peer_ports,
    )

    view = _rack13_view()
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    writer = _Writer(refuse="controlport config peer -ct point -f 1:3:2")
    result = apply_peer_ports(plan, writer=writer, read=lambda: _after(view, "0:3:2"))
    assert result.error and "1:3:2" in result.error
    assert result.changed == ["0:3:2"]
    # 0:3:2 is restored; 1:3:2 was only taken offline, so it is only brought back (help: "Issue
    # controlport rst to bring the port back online"), never re-configured.
    assert "controlport config host -ct point -f 0:3:2" in result.removals
    assert "controlport rst 1:3:2" in result.removals
    assert not any(r.startswith("controlport config") and r.endswith("1:3:2") for r in result.removals)


@NOT_BUILT
def test_another_port_changing_mode_stops_the_apply():
    """The CLI help warns a mode change can move a partner port; the read-back compares every port."""
    from alletra_onboard.application.provisioning.peer_ports import (
        apply_peer_ports,
        plan_peer_ports,
    )

    view = _rack13_view()
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)

    def read():
        after = _after(view, "0:3:2")
        after.ports["0:3:1"] = after.ports["0:3:1"].model_copy(update={"mode": "initiator"})
        return after

    result = apply_peer_ports(plan, writer=_Writer(), read=read)
    assert result.error and "0:3:1" in result.error


# ------------------------------------------------------------------ ADR 0018: the port-scoped client

@NOT_BUILT
@pytest.mark.parametrize("command, allowed", [
    ("controlport offline 0:3:2", True),
    ("controlport config peer -ct point -f 0:3:2", True),
    ("controlport rst 0:3:2", True),
    ("controlport offline 0:3:3", False),                          # not an approved port
    ("controlport config host -ct point -f 0:3:2", False),         # restores are pasted, never run
    ("controlport config peer -virt_ports 8 0:3:2", False),
    ("controlport config peer -ct point -f 0:3:2 1:3:2", False),   # one port per command
    ("controlport rst -m initiator 0:3:2", False),
    ("controlport offline 0:3:2; showport", False),
    ("controlport rcip addr -f 10.0.0.1 255.255.255.0 0:4:4", False),
])
def test_the_port_client_runs_only_the_peer_forms_on_approved_ports(command, allowed):
    from alletra_onboard.adapters.array.port_cli_client import port_write_refusal

    assert (port_write_refusal(command, approved={"0:3:2", "1:3:2"}) is None) is allowed


# ------------------------------------------------------------------ R6: verify

@NOT_BUILT
def test_verify_reads_e18u31_peer_ports_as_ready():
    from alletra_onboard.application.provisioning.peer_ports import build_view, verify_peer_ports

    checks = verify_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(E18U31_SHOWPORT)))
    assert all(c.ok for c in checks)
    assert checks[0].sentence == "0:3:2 is a peer port, link ready."


@NOT_BUILT
def test_verify_says_a_free_port_is_not_a_peer_port():
    from alletra_onboard.application.provisioning.peer_ports import build_view, verify_peer_ports

    checks = verify_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(RACK13_SHOWPORT)))
    assert not checks[0].ok and checks[0].sentence == "0:3:2 is not a peer port (Type free)."


# ------------------------------------------------------------------ R7: zoning

@NOT_BUILT
def test_peer_zones_use_the_wwpn_read_after_the_change():
    """E18U31's peer ports carry 2032 0202… where its host ports carry 2031 0002…; the zone takes the
    port WWN from the view it is given (the read-back), never from the read before the apply."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, peer_zone_pairs
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    intent = PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:2", source_wwpns=["20310002AC02AC38"]),
                                   PeerPortRequest(nsp="1:3:2", source_wwpns=["21310002AC02AC38"])])
    pairs = peer_zone_pairs(intent, build_view(_text(E18U31_SHOWPORT)))
    assert pairs == [("20320202AC02DEF2", "20310002AC02AC38"), ("21320202AC02DEF2", "21310002AC02AC38")]


# ------------------------------------------------------------------ R8: the step

@NOT_BUILT
def test_peer_ports_are_a_section_of_the_shared_array_ports_step():
    """SPEC-024 (BL-25) proposes the `ports` step; peer ports add a section to it, not a step of their own."""
    from alletra_onboard.domain.workflow import STEP_REGISTRY

    keys = [s.key for s in STEP_REGISTRY]
    assert keys.index("discover") < keys.index("ports") < keys.index("zoning")
    assert next(s for s in STEP_REGISTRY if s.key == "ports").kind == "provision"
    assert "peer_ports" not in keys
