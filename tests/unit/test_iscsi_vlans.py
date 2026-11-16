"""SPEC-024 — VLAN-tagged iSCSI addresses on the array's ports (BL-25). NOT BUILT YET.

Every test marked `xfail(strict=True)` describes behaviour the spec asks for and fails today; it turns
green, and must then lose its marker, when the step of docs/workpackets/BL-25.md that names it is built.
The plan tests stand on E18U31's real captures (tests/fixtures/rc_pair/E18U31/, 2026-10-07): its
`showport` roles, the iSCSI ports' base addresses from `showport -iscsi`, its RCIP addresses and its
management address from `shownet`. Sheet addresses use the documentation range 192.0.2.0/24.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest
from openpyxl import load_workbook

from alletra_onboard.adapters.array import cli_client
from alletra_onboard.application.platform import init_sheet
from alletra_onboard.application.replication.read import parse_showport_roles
from alletra_onboard.domain.models import RunMode

FIX = Path(__file__).resolve().parents[1] / "fixtures"
E18U31 = FIX / "rc_pair" / "E18U31"
VLAN_FIX = FIX / "iscsi_vlan"          # filled by lab/iscsi_vlan_capture.py; not captured yet

NOT_BUILT = pytest.mark.xfail(reason="BL-25: not built yet, see docs/workpackets/BL-25.md", strict=True)
NOT_CAPTURED = pytest.mark.xfail(
    reason="BL-25: needs lab/iscsi_vlan_capture.py output in tests/fixtures/iscsi_vlan/, see docs/workpackets/BL-25.md",
    strict=True)

HEADER = ["Port (N:S:P) *", "VLAN ID *", "iSCSI address *", "Netmask *", "Gateway (optional)"]
ROWS = [
    {"port": "0:4:1", "vlan": "120", "ip": "192.0.2.11", "netmask": "255.255.255.0", "gateway": "192.0.2.1"},
    {"port": "1:4:1", "vlan": "120", "ip": "192.0.2.12", "netmask": "255.255.255.0", "gateway": "192.0.2.1"},
]
_KEYS = ["port", "vlan", "ip", "netmask", "gateway"]


def _workbook(rows: list[dict] | None) -> bytes:
    """A provisioning workbook as the template writes it, plus (when rows is not None) an 'iSCSI network'
    tab laid out the way SPEC-024 R1 says the template will write it: intro line, header, rows."""
    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D3209YV", "mgmt_ipv4": "10.64.154.190"},
        targets={"prov_array_host": "10.64.154.190", "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[{"name": "zz_vl_vol01", "size_gib": "1"}], hostsets=[{"name": "zz_vl_hs"}], hosts=[])
    if rows is None:
        return data
    wb = load_workbook(io.BytesIO(data))
    if "iSCSI network" in wb.sheetnames:          # once the template writes the tab, refill it
        del wb["iSCSI network"]
    ws = wb.create_sheet("iSCSI network")
    ws.append(["Fill this only when the tool should add VLAN-tagged iSCSI addresses to this array's iSCSI ports."])
    ws.append(HEADER)
    for r in rows:
        ws.append([r.get(k, "") for k in _KEYS])
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def _intent(rows: list[dict] | None):
    return init_sheet.parse_workbook_bytes(_workbook(rows), mode=RunMode.PROVISION_ONLY).provisioning_intent


# ------------------------------------------------------------------ what holds today (no marker)

def test_the_read_allowlist_already_takes_every_read_the_spec_needs():
    """SPEC-024 R2 needs no read allowlist change: each read's base word is already allowed."""
    for cmd in ("showport", "showport -iscsi", "showport -iscsivlans", "showport -rcip", "showport -file",
                "shownet", "showhost -d"):
        assert cli_client.refusal(cmd) is None, cmd


def test_the_read_client_still_refuses_an_iscsi_port_write():
    assert cli_client.refusal("controliscsiport delete -f 0:4:1") is not None


def test_a_workbook_without_the_iscsi_network_tab_parses_as_today():
    intent = _intent(None)
    assert getattr(intent, "iscsi_network", []) == []


# ------------------------------------------------------------------ R1: the sheet

@NOT_BUILT
def test_the_iscsi_network_tab_parses_into_the_intent():
    from alletra_onboard.domain.network import IscsiVlanRequest

    assert _intent(ROWS).iscsi_network == [
        IscsiVlanRequest(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0", gateway="192.0.2.1"),
        IscsiVlanRequest(nsp="1:4:1", vlan_id=120, ip="192.0.2.12", netmask="255.255.255.0", gateway="192.0.2.1"),
    ]
    assert _intent([]).iscsi_network == []


@NOT_BUILT
@pytest.mark.parametrize("rows, why", [
    ([{**ROWS[0], "ip": ""}, ROWS[1]], "missing iSCSI address"),
    ([{**ROWS[0], "port": "0-4-1"}, ROWS[1]], "Port must be N:S:P, like 0:4:1 (got '0-4-1')"),
    ([{**ROWS[0], "vlan": "0"}, ROWS[1]], "VLAN ID must be a whole number from 1 to 4094 (got '0')"),
    ([{**ROWS[0], "vlan": "4095"}, ROWS[1]], "VLAN ID must be a whole number from 1 to 4094 (got '4095')"),
    ([{**ROWS[0], "vlan": "12a"}, ROWS[1]], "VLAN ID must be a whole number from 1 to 4094 (got '12a')"),
    ([{**ROWS[0], "ip": "192.0.2.300"}, ROWS[1]], "iSCSI address '192.0.2.300' is not an IPv4 address"),
    ([{**ROWS[0], "netmask": "255.0.255.0"}, ROWS[1]], "Netmask '255.0.255.0' is not a netmask"),
    ([{**ROWS[0], "gateway": "gw1"}, ROWS[1]], "Gateway 'gw1' is not an IPv4 address"),
    ([{**ROWS[0], "gateway": "198.51.100.1"}, ROWS[1]], "Gateway 198.51.100.1 is not on the network 192.0.2.0/24 of 192.0.2.11"),
    ([{**ROWS[0], "ip": "192.0.2.255"}, ROWS[1]], "192.0.2.255 is the network or broadcast address of 192.0.2.0/24"),
    ([ROWS[0], {**ROWS[0], "ip": "192.0.2.13"}], "port 0:4:1 has VLAN 120 twice"),
    ([ROWS[0], {**ROWS[1], "ip": "192.0.2.11"}], "address 192.0.2.11 is used twice"),
    ([ROWS[0], {**ROWS[1], "ip": "198.51.100.12", "gateway": ""}],
     "VLAN 120 is on two networks: 192.0.2.0/24 on 0:4:1 and 198.51.100.0/24 on 1:4:1. One VLAN is one network"),
    ([ROWS[0], {**ROWS[1], "vlan": "130"}], "VLAN 120 and VLAN 130 are both on 192.0.2.0/24"),
])
def test_a_wrong_iscsi_network_row_is_refused_with_a_sentence(rows, why):
    with pytest.raises(ValueError, match=re.escape(why)):
        _intent(rows)


@NOT_BUILT
def test_the_template_has_the_iscsi_network_tab_with_the_port_column_as_text():
    ws = load_workbook(io.BytesIO(init_sheet.build_template_bytes()))[init_sheet.ISCSI_NETWORK_SHEET_NAME]
    header = next(r for r in ws.iter_rows() if any(c.value == "Port (N:S:P) *" for c in r))
    assert [c.value for c in header][:5] == HEADER
    assert ws.cell(row=header[0].row + 1, column=1).number_format == "@"


# ------------------------------------------------------------------ R2: the parsers

@NOT_BUILT
def test_showport_iscsi_gives_mask_gateway_and_the_peer_flag_from_the_e18u31_capture():
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi

    ports = {p.nsp: p for p in parse_showport_iscsi((E18U31 / "showport_iscsi.txt").read_text())}
    assert set(ports) == {"0:4:1", "0:4:2", "1:4:1", "1:4:2"}
    assert (ports["0:4:1"].ip, ports["0:4:1"].netmask, ports["0:4:1"].gateway) == ("10.30.14.1", "255.255.255.0", "10.30.14.254")
    assert not any(p.peer_enabled for p in ports.values())       # Peer_Enabled N on all four
    # The other array answers in prose when it has no iSCSI port (D22U27, 2026-10-26).
    assert parse_showport_iscsi((FIX / "d22u27_iscsi" / "showport_iscsi.txt").read_text()) == []


@NOT_CAPTURED
def test_showport_iscsivlans_parses_the_lab_capture():
    """Pinned to E18U31's own output once captured. Edit the expected values to what the capture shows;
    never write the capture to fit this test."""
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans

    text = (VLAN_FIX / "E18U31" / "showport_iscsivlans.txt").read_text()
    vlans = parse_iscsi_vlans(text)
    assert all(re.fullmatch(r"\d+:\d+:\d+", v.nsp) and 1 <= v.vlan_id <= 4094 for v in vlans)
    assert (VLAN_FIX / "E18U31" / "help_controliscsiport.txt").is_file()


# ------------------------------------------------------------------ R3: the plan, on E18U31's real ports

def _view(vlans=None, peer_enabled=()):
    from alletra_onboard.domain.network import IscsiPortAddress, PortNetworkView

    roles, _wwn = parse_showport_roles((E18U31 / "showport.txt").read_text())
    # From E18U31/showport_iscsi.txt (all four 255.255.255.0, gateway 10.30.14.254, Peer_Enabled N).
    iscsi = [IscsiPortAddress(nsp=nsp, ip=ip, netmask="255.255.255.0", gateway="10.30.14.254", peer_enabled=nsp in peer_enabled)
             for nsp, ip in (("0:4:1", "10.30.14.1"), ("0:4:2", "10.30.14.2"), ("1:4:1", "10.30.14.3"), ("1:4:2", "10.30.14.4"))]
    return PortNetworkView(
        name="AlletraMP_E18U31", mgmt_ip="10.64.154.190", mgmt_netmask="255.255.248.0",   # E18U31/shownet.txt
        roles=roles, iscsi_ports=iscsi, vlans=list(vlans or []),
        other_addresses={"10.54.154.192": "RCIP port 0:4:3", "10.54.154.193": "RCIP port 1:4:3"},  # showport_rcip.txt
    )


def _req(nsp="0:4:1", vlan=120, ip="192.0.2.11", mask="255.255.255.0", gw="192.0.2.1"):
    from alletra_onboard.domain.network import IscsiVlanRequest

    return IscsiVlanRequest(nsp=nsp, vlan_id=vlan, ip=ip, netmask=mask, gateway=gw)


def _plan(requests, view=None):
    from alletra_onboard.application.provisioning.iscsi_network import plan_iscsi_vlans

    return plan_iscsi_vlans(requests, view or _view())


@NOT_BUILT
def test_one_vlan_on_an_iscsi_port_of_each_node_is_planned_as_two_adds():
    plan = _plan([_req(), _req("1:4:1", ip="192.0.2.12")])
    assert [(a.nsp, a.vlan_id, a.state) for a in plan.actions] == [("0:4:1", 120, "create"), ("1:4:1", 120, "create")]
    assert plan.blockers == [] and plan.notes == []
    assert all(a.cli and "120" in a.cli and a.nsp in a.cli for a in plan.actions)   # the CLI equivalent is printed


@NOT_BUILT
@pytest.mark.parametrize("nsp, words", [
    ("0:3:1", "showport lists it as target ready host FC"),     # an FC host port
    ("0:4:3", "showport lists it as peer ready rcip IP"),       # an RCIP port
    ("0:4:4", "showport lists it as peer offline free IP"),     # a free replication port
])
def test_a_port_that_is_not_iscsi_is_a_conflict_never_a_role_change(nsp, words):
    plan = _plan([_req(nsp)])
    (action,) = plan.actions
    assert action.state == "conflict" and not action.cli
    assert f"AlletraMP_E18U31 {nsp} is not an iSCSI port: {words}. The tool never changes a port's role." == action.reason
    assert action.reason in plan.blockers


@NOT_BUILT
def test_a_port_the_array_does_not_have_is_a_conflict():
    (action,) = _plan([_req("2:4:1")]).actions
    assert action.state == "conflict" and action.reason == "AlletraMP_E18U31 has no port 2:4:1 (showport)."


@NOT_BUILT
def test_a_peer_enabled_iscsi_port_is_a_conflict():
    (action,) = _plan([_req()], _view(peer_enabled=("0:4:1",))).actions
    assert action.state == "conflict" and "is a peer-enabled iSCSI port" in action.reason


@NOT_BUILT
def test_a_vlan_already_there_with_the_same_values_exists_and_with_others_is_a_conflict():
    from alletra_onboard.domain.network import IscsiVlanInterface

    same = IscsiVlanInterface(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0", gateway="192.0.2.1")
    (action,) = _plan([_req()], _view(vlans=[same])).actions
    assert action.state == "exists" and not action.cli

    other = same.model_copy(update={"ip": "192.0.2.50"})
    (action,) = _plan([_req()], _view(vlans=[other])).actions
    assert action.state == "conflict"
    assert action.reason.startswith("AlletraMP_E18U31 0:4:1 already has VLAN 120 with 192.0.2.50 255.255.255.0")
    assert action.reason.endswith("The tool never changes an address it did not set.")


@NOT_BUILT
@pytest.mark.parametrize("ip, mask, where", [
    ("10.30.14.2", "255.255.255.0", "iSCSI port 0:4:2"),         # E18U31's own iSCSI address
    ("10.54.154.192", "255.255.248.0", "RCIP port 0:4:3"),
    ("10.64.154.190", "255.255.248.0", "management"),
])
def test_an_address_already_in_use_on_the_array_is_a_conflict(ip, mask, where):
    (action,) = _plan([_req("1:4:2", ip=ip, mask=mask, gw="")]).actions
    assert action.state == "conflict" and action.reason == f"{ip} is already in use on AlletraMP_E18U31: {where}."


@NOT_BUILT
def test_a_vlan_in_the_ports_own_untagged_network_is_a_conflict():
    (action,) = _plan([_req(ip="10.30.14.50", gw="")]).actions
    assert action.state == "conflict"
    assert action.reason.startswith("10.30.14.0/24 is already the network of iSCSI port 0:4:1 on AlletraMP_E18U31")


@NOT_BUILT
def test_a_vlan_on_one_node_only_is_a_note_not_a_blocker():
    plan = _plan([_req(), _req("0:4:2", ip="192.0.2.12")])
    assert plan.blockers == []
    assert any("VLAN 120 is only on node 0" in n for n in plan.notes)


@NOT_BUILT
def test_the_switch_side_is_a_sentence_per_port_for_the_network_team_never_a_command():
    from alletra_onboard.domain.network import IscsiVlanInterface

    there = IscsiVlanInterface(nsp="0:4:1", vlan_id=130, ip="198.51.100.11", netmask="255.255.255.0")
    plan = _plan([_req(), _req("1:4:1", ip="192.0.2.12")], _view(vlans=[there]))
    assert plan.switch_handoff == [
        "Switch port cabled to AlletraMP_E18U31 0:4:1: carry VLAN 120, 130 tagged (802.1Q).",
        "Switch port cabled to AlletraMP_E18U31 1:4:1: carry VLAN 120 tagged (802.1Q).",
    ]


# ------------------------------------------------------------------ R5: the removal set

@NOT_BUILT
def test_the_removal_set_undoes_only_what_this_apply_created_last_first():
    from alletra_onboard.application.provisioning.iscsi_network import removal_lines
    from alletra_onboard.domain.network import IscsiVlanOutcome

    lines = removal_lines([
        IscsiVlanOutcome(nsp="0:4:1", vlan_id=120, status="created"),
        IscsiVlanOutcome(nsp="0:4:2", vlan_id=120, status="exists"),
        IscsiVlanOutcome(nsp="1:4:1", vlan_id=120, status="created"),
        IscsiVlanOutcome(nsp="1:4:2", vlan_id=120, status="failed"),
    ])
    assert len(lines) == 2
    assert "1:4:1" in lines[0] and "120" in lines[0]
    assert "0:4:1" in lines[1] and "120" in lines[1]


# ------------------------------------------------------------------ R8: the step

@NOT_BUILT
def test_the_array_ports_step_sits_between_discovery_and_san_zoning():
    from alletra_onboard.domain.workflow import STEP_REGISTRY

    keys = [s.key for s in STEP_REGISTRY]
    assert keys.index("discover") < keys.index("ports") < keys.index("zoning")
    assert next(s for s in STEP_REGISTRY if s.key == "ports").label == "Array ports"
