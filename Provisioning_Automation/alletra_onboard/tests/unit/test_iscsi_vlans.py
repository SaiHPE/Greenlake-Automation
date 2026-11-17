"""SPEC-024 — VLAN-tagged iSCSI addresses on the array's ports (BL-25). The read side is built.

Every test marked `xfail(strict=True)` describes behaviour the spec asks for and fails today; it turns
green, and must then lose its marker, when the step of docs/workpackets/BL-25.md that names it is built.
The plan tests stand on E18U31's real captures (tests/fixtures/rc_pair/E18U31/, 2026-10-07): its
`showport` roles, the iSCSI ports' base addresses from `showport -iscsi`, its RCIP addresses and its
management address from `shownet`. The parser tests stand on the captures in
tests/fixtures/iscsi_vlan/: rack13-ARCUS (OS 10.6.0, 2026-11-16) and, from 2026-11-17, D22U27 (OS
10.5.0, no iSCSI port), VZ (OS 10.5.51, four offline iSCSI ports) and E18U31 (OS 10.5.60, four ready
iSCSI ports, MTU 9000). None of those has a tagged interface; `tagged/` (rack13-ARCUS, 2026-11-17) holds
VLAN 2999 on 0:4:2, set for the live confirmation and removed again. Sheet addresses use the
documentation range 192.0.2.0/24.
"""

from __future__ import annotations

import io
import json
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
VLAN_FIX = FIX / "iscsi_vlan"          # lab/iscsi_vlan_capture.py output, one folder per array
RACK13 = VLAN_FIX / "rack13"           # rack13-ARCUS, OS 10.6.0, 2026-11-16: no tagged interface
D22U27 = VLAN_FIX / "D22U27"           # AlletraMP_D22U27, OS 10.5.0, 2026-11-17: no iSCSI port at all
VZ = VLAN_FIX / "VZ"                   # MPB10K-D24U21-VZ, OS 10.5.51, 2026-11-17: four iSCSI ports, all offline
E18U31_NOW = VLAN_FIX / "E18U31"       # E18U31, now named DHCI_B10K, OS 10.5.60, 2026-11-17: four ready, MTU 9000
OS_10_5 = {"10.5.0": D22U27, "10.5.51": VZ, "10.5.60": E18U31_NOW}
TAGGED = VLAN_FIX / "tagged"           # rack13-ARCUS, OS 10.6.0, 2026-11-17: VLAN 2999 on 0:4:2 (no untagged address)

NOT_BUILT = pytest.mark.xfail(reason="BL-25: not built yet, see docs/workpackets/BL-25.md", strict=True)
NO_STARRED_ROW = pytest.mark.xfail(
    reason="BL-25: needs showport -iscsi with a '*' after an address, from a port that has an untagged address "
           "and a VLAN address; the tagged capture of 2026-11-17 (tests/fixtures/iscsi_vlan/tagged/) put the VLAN "
           "on 0:4:2, which had no untagged address, and printed no '*'",
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


@pytest.mark.parametrize("cmd", [
    "controliscsiport addr 192.0.2.11 255.255.255.0 -vlan 120 -f 0:4:1",
    "controliscsiport gw 192.0.2.1 -vlan 120 -f 0:4:1",
    "controliscsiport delete -vlan 120 -f 0:4:1",
])
def test_no_client_the_tool_has_takes_an_iscsi_vlan_form(cmd):
    """ADR 0017: the first slice prints these lines and sends none. When the apply is built, the forms
    go on ADR 0025's one array-port write client, never on the Remote Copy write client."""
    from alletra_onboard.adapters.array.rc_cli_client import rc_write_refusal

    assert cli_client.refusal(cmd) is not None
    assert rc_write_refusal(cmd) is not None


def test_a_workbook_without_the_iscsi_network_tab_parses_as_today():
    intent = _intent(None)
    assert getattr(intent, "iscsi_network", []) == []


# ------------------------------------------------------------------ R1: the sheet

def test_the_iscsi_network_tab_parses_into_the_intent():
    from alletra_onboard.domain.network import IscsiVlanRequest

    assert _intent(ROWS).iscsi_network == [
        IscsiVlanRequest(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0", gateway="192.0.2.1"),
        IscsiVlanRequest(nsp="1:4:1", vlan_id=120, ip="192.0.2.12", netmask="255.255.255.0", gateway="192.0.2.1"),
    ]
    assert _intent([]).iscsi_network == []


def test_a_port_excel_stored_as_a_time_reads_back_as_n_s_p():
    """Excel turns 0:4:1 typed in a General cell into a time; the tab reads it back as the port."""
    import datetime

    wb = load_workbook(io.BytesIO(_workbook(ROWS)))
    ws = wb["iSCSI network"]
    ws.cell(row=3, column=1).value = datetime.time(0, 4, 1)
    out = io.BytesIO()
    wb.save(out)
    intent = init_sheet.parse_workbook_bytes(out.getvalue(), mode=RunMode.PROVISION_ONLY).provisioning_intent
    assert [r.nsp for r in intent.iscsi_network] == ["0:4:1", "1:4:1"]


def test_a_filled_row_with_no_port_is_refused_not_dropped():
    with pytest.raises(ValueError, match=re.escape("iSCSI network tab — row ' VLAN 120': missing Port (N:S:P).")):
        _intent([{**ROWS[0], "port": ""}, ROWS[1]])


def test_compose_writes_the_iscsi_network_tab():
    data = init_sheet.compose_workbook_bytes(
        base=_workbook(None), iscsi_network=[{"port": "0:4:1", "vlan": "120", "ip": "192.0.2.11",
                                              "netmask": "255.255.255.0"}])
    intent = init_sheet.parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY).provisioning_intent
    assert [(r.nsp, r.vlan_id, r.ip, r.gateway) for r in intent.iscsi_network] == [("0:4:1", 120, "192.0.2.11", "")]


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


def test_the_template_has_the_iscsi_network_tab_with_the_port_column_as_text():
    ws = load_workbook(io.BytesIO(init_sheet.build_template_bytes()))[init_sheet.ISCSI_NETWORK_SHEET_NAME]
    header = next(r for r in ws.iter_rows() if any(c.value == "Port (N:S:P) *" for c in r))
    assert [c.value for c in header][:5] == HEADER
    assert ws.cell(row=header[0].row + 1, column=1).number_format == "@"


# ------------------------------------------------------------------ R2: the parsers

def test_showport_iscsi_gives_mask_gateway_and_the_peer_flag_from_the_e18u31_capture():
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi

    ports = {p.nsp: p for p in parse_showport_iscsi((E18U31 / "showport_iscsi.txt").read_text())}
    assert set(ports) == {"0:4:1", "0:4:2", "1:4:1", "1:4:2"}
    assert (ports["0:4:1"].ip, ports["0:4:1"].netmask, ports["0:4:1"].gateway) == ("10.30.14.1", "255.255.255.0", "10.30.14.254")
    assert not any(p.peer_enabled for p in ports.values())       # Peer_Enabled N on all four
    # The other array answers in prose when it has no iSCSI port (D22U27, 2026-10-26).
    assert parse_showport_iscsi((FIX / "d22u27_iscsi" / "showport_iscsi.txt").read_text()) == []


# The older `... STGT VLAN` layout, from the real `showport -iscsi` in test_storage_services.py.
_OLDER_LAYOUT = """N:S:P State   IPAddr        Netmask/PrefixLen Gateway       TPGT  MTU   Rate iSNS_Addr iSNS_Port STGT VLAN
0:4:1 ready   10.55.234.221 255.255.248.0     10.55.239.254   41 1500 10Gbps 0.0.0.0        3205   41 Y
0:4:2 offline 0.0.0.0       0.0.0.0           0.0.0.0         42  n/a    n/a 0.0.0.0        3205   42 Y"""


def test_showport_iscsi_reads_rack13_unset_ports_and_the_older_layout():
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi
    from alletra_onboard.domain.network import IscsiPortAddress

    assert parse_showport_iscsi((RACK13 / "showport_iscsi.txt").read_text()) == [
        IscsiPortAddress(nsp="0:4:1", ip="10.93.18.10", netmask="255.255.254.0", gateway="10.93.18.1", vlans="1"),
        IscsiPortAddress(nsp="0:4:2", vlans="0"),                 # offline, 0.0.0.0 everywhere: not set
        IscsiPortAddress(nsp="1:4:1", ip="10.93.18.12", netmask="255.255.254.0", gateway="10.93.18.1", vlans="1"),
        IscsiPortAddress(nsp="1:4:2", vlans="0"),
    ]
    older = parse_showport_iscsi(_OLDER_LAYOUT)
    assert [(p.nsp, p.ip, p.gateway, p.vlans, p.peer_enabled) for p in older] == [
        ("0:4:1", "10.55.234.221", "10.55.239.254", "Y", False), ("0:4:2", "", "", "Y", False)]
    # `help showport` NOTES: "IP address denoted with * ... has more than one IP address configured
    # with VLANs". The star is a marker, not part of the address.
    starred = (RACK13 / "showport_iscsi.txt").read_text().replace("10.93.18.10 ", "10.93.18.10* ", 1)
    assert parse_showport_iscsi(starred)[0].ip == "10.93.18.10"
    assert "than one IP address configured with VLANs." in (RACK13 / "help_showport.txt").read_text()


def test_showport_iscsi_refuses_a_layout_it_does_not_know():
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi

    rows = (RACK13 / "showport_iscsi.txt").read_text().splitlines()
    with pytest.raises(ValueError, match="before its header"):
        parse_showport_iscsi("\n".join(r for r in rows if not r.startswith("N:S:P")))
    with pytest.raises(ValueError, match="no Gateway column"):
        parse_showport_iscsi("\n".join(r.replace("Gateway", "Gw") for r in rows))


def test_showport_iscsivlans_parses_the_lab_capture():
    """Pinned to rack13-ARCUS's own output (OS 10.6.0, 2026-11-16). It lists each port's untagged
    address as a row with VLAN `untagged`, the same values `showport -iscsi` gives as the base
    address, and no row for a port with no address. Those rows are not VLAN interfaces."""
    from alletra_onboard.application.provisioning.discovery import (
        parse_iscsi_vlans,
        parse_showport_iscsi,
    )

    text = (RACK13 / "showport_iscsivlans.txt").read_text()
    assert text.splitlines()[1].split() == [
        "N:S:P", "VLAN", "IPAddr", "Netmask/PrefixLen", "Gateway", "MTU", "TPGT", "STGT", "iSNS_Addr", "iSNS_Port"]
    assert parse_iscsi_vlans(text) == []
    untagged = [ln.split() for ln in text.splitlines() if " untagged " in ln]
    base = {p.nsp: p for p in parse_showport_iscsi((RACK13 / "showport_iscsi.txt").read_text()) if p.ip}
    assert [(r[0], r[2], r[3], r[4]) for r in untagged] == [
        (p.nsp, p.ip, p.netmask, p.gateway) for p in base.values()]
    assert (RACK13 / "help_controliscsiport.txt").is_file()
    with pytest.raises(ValueError, match="neither a tag"):
        parse_iscsi_vlans(text.replace(" untagged ", " tagged   ", 1))


def _release(folder: Path) -> str:
    """The capture's own `showversion`: `Release version 10.5.60` -> "10.5.60"."""
    line = next(ln for ln in (folder / "showversion.txt").read_text().splitlines() if ln.startswith("Release version"))
    return line.split()[-1]


def test_each_capture_is_the_release_its_folder_is_filed_under():
    assert _release(RACK13) == "10.6.0"
    for release, folder in OS_10_5.items():
        assert _release(folder) == release, folder.name


def test_an_array_with_no_iscsi_port_answers_both_iscsi_views_in_prose():
    """D22U27 (OS 10.5.0, 2026-11-17): slot 4 carries file and RCIP ports, no iSCSI port. The two
    iSCSI views answer in two different sentences; both read as nothing."""
    from alletra_onboard.application.provisioning.discovery import (
        parse_iscsi_vlans,
        parse_showport_iscsi,
    )

    roles, _wwn = parse_showport_roles((D22U27 / "showport.txt").read_text())
    assert len(roles) == 24 and not [r for r in roles.values() if r.protocol == "iSCSI"]
    iscsi = (D22U27 / "showport_iscsi.txt").read_text()
    vlans = (D22U27 / "showport_iscsivlans.txt").read_text()
    assert iscsi.splitlines()[1:] == ["There is no specified port information."]
    assert vlans.splitlines()[1:] == ["no ports listed"]
    assert parse_showport_iscsi(iscsi) == [] and parse_iscsi_vlans(vlans) == []
    # No iSCSI port, so no per-port iSCSIVlans GET; OS 10.5.0's GET /ports has no iSCSIVlans field.
    ports = json.loads((D22U27 / "wsapi" / "ports.json").read_text())["members"]
    assert not [m for m in ports if m["protocol"] == 2] and not any("iSCSIVlans" in m for m in ports)
    assert not list((D22U27 / "wsapi").glob("ports_*_iscsivlans.json"))


def test_offline_iscsi_ports_have_no_address_and_no_iscsivlans_row():
    """VZ (OS 10.5.51, 2026-11-17): four iSCSI ports, all `target offline free iSCSI`, no address.
    `showport -iscsivlans` then answers `no ports listed`, the words D22U27 uses with no iSCSI port
    at all: the view lists addresses, not ports, so only `showport` says which iSCSI ports exist."""
    from alletra_onboard.adapters.array.wsapi_client import parse_iscsi_vlans_wsapi
    from alletra_onboard.application.provisioning.discovery import (
        parse_iscsi_vlans,
        parse_showport_iscsi,
    )
    from alletra_onboard.domain.network import IscsiPortAddress

    nsps = ("0:4:1", "0:4:2", "1:4:1", "1:4:2")
    roles, _wwn = parse_showport_roles((VZ / "showport.txt").read_text())
    assert {r.nsp: f"{r.mode} {r.state} {r.type} {r.protocol}" for r in roles.values() if r.protocol == "iSCSI"} == \
        dict.fromkeys(nsps, "target offline free iSCSI")
    assert parse_showport_iscsi((VZ / "showport_iscsi.txt").read_text()) == [
        IscsiPortAddress(nsp=nsp, vlans="0") for nsp in nsps]          # 0.0.0.0 everywhere: not set
    vlans = (VZ / "showport_iscsivlans.txt").read_text()
    assert vlans.splitlines()[1:] == ["no ports listed"] and parse_iscsi_vlans(vlans) == []
    for nsp in nsps:
        body = json.loads((VZ / "wsapi" / f"ports_{nsp.replace(':', '_')}_iscsivlans.json").read_text())
        assert sorted(body) == ["iSCSIVlans", "links", "total"] and body["total"] == 0
        assert parse_iscsi_vlans_wsapi(nsp, body) == []
    ports = json.loads((VZ / "wsapi" / "ports.json").read_text())["members"]
    info = [m["iSCSIPortInfo"] for m in ports if m["protocol"] == 2]
    assert len(info) == 4 and all((i["IPAddr"], i["vlan"], i["mtu"]) == ("0.0.0.0", 0, 1500) for i in info)
    assert not any("iSCSIVlans" in m for m in ports)               # OS 10.5.51's GET /ports has no such field


def test_a_second_array_with_ready_ports_mtu_9000_and_no_gateway():
    """E18U31 (serial CZ2D3209YV, now named DHCI_B10K, OS 10.5.60, 2026-11-17): four ready iSCSI
    ports on two /24 networks, one per port number, no gateway, MTU 9000, three lab hosts logged in
    on every port. `showport -iscsivlans` has rack13-ARCUS's layout (OS 10.6.0) and lists the four
    untagged addresses; no tagged row."""
    from alletra_onboard.application.provisioning.discovery import (
        parse_iscsi_vlans,
        parse_showport_iscsi,
    )
    from alletra_onboard.domain.network import IscsiPortAddress

    assert "DHCI_B10K" in (E18U31_NOW / "showsys.txt").read_text()
    assert "CZ2D3209YV" in (E18U31_NOW / "showsys.txt").read_text()       # the same array as rc_pair/E18U31
    roles, _wwn = parse_showport_roles((E18U31_NOW / "showport.txt").read_text())
    nsps = ("0:4:1", "0:4:2", "1:4:1", "1:4:2")
    assert [f"{roles[n].mode} {roles[n].state} {roles[n].type} {roles[n].protocol}" for n in nsps] == \
        ["target ready host iSCSI"] * 4
    assert parse_showport_iscsi((E18U31_NOW / "showport_iscsi.txt").read_text()) == [   # Gateway 0.0.0.0: none
        IscsiPortAddress(nsp="0:4:1", ip="10.1.1.2", netmask="255.255.255.0", vlans="1"),
        IscsiPortAddress(nsp="0:4:2", ip="20.1.1.2", netmask="255.255.255.0", vlans="1"),
        IscsiPortAddress(nsp="1:4:1", ip="10.1.1.3", netmask="255.255.255.0", vlans="1"),
        IscsiPortAddress(nsp="1:4:2", ip="20.1.1.3", netmask="255.255.255.0", vlans="1"),
    ]
    text = (E18U31_NOW / "showport_iscsivlans.txt").read_text()
    assert text.splitlines()[1].split() == (RACK13 / "showport_iscsivlans.txt").read_text().splitlines()[1].split()
    assert parse_iscsi_vlans(text) == []
    untagged = [ln.split() for ln in text.splitlines() if " untagged " in ln]
    assert [(r[0], r[2], r[4], r[5]) for r in untagged] == [         # N:S:P, IPAddr, Gateway, MTU
        ("0:4:1", "10.1.1.2", "0.0.0.0", "9000"), ("0:4:2", "20.1.1.2", "0.0.0.0", "9000"),
        ("1:4:1", "10.1.1.3", "0.0.0.0", "9000"), ("1:4:2", "20.1.1.3", "0.0.0.0", "9000")]
    logins = [ln.split() for ln in (E18U31_NOW / "showhost_d.txt").read_text().splitlines() if " iqn." in ln]
    assert all(sum(1 for r in logins if r[4] == nsp) == 3 for nsp in nsps)


def test_a_tagged_row_of_showport_iscsivlans_parses():
    """Edit the expected values to what the capture shows; never write the capture to fit this test."""
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans

    vlans = parse_iscsi_vlans((TAGGED / "showport_iscsivlans.txt").read_text())
    assert vlans
    assert all(re.fullmatch(r"\d+:\d+:\d+", v.nsp) and 1 <= v.vlan_id <= 4094 and v.ip and v.netmask for v in vlans)
    assert [(v.nsp, v.vlan_id, v.ip, v.netmask, v.gateway, v.mtu) for v in vlans] == [
        ("0:4:2", 2999, "192.0.2.10", "255.255.255.0", "", "1500")]


def test_wsapi_iscsivlans_answer_has_its_own_envelope_and_leaves_out_the_untagged_address():
    """rack13-ARCUS (OS 10.6.0) answered GET /ports/<n:s:p>/iSCSIVlans/ on all four iSCSI ports.
    0:4:1 and 1:4:1 carry an untagged address and the answer is still empty; `GET /ports` says
    `iSCSIPortInfo.vlan` 0 and carries `iSCSIVlans: []` on every port. OS 10.5.60 differs (below)."""
    from alletra_onboard.adapters.array.wsapi_client import parse_iscsi_vlans_wsapi

    for nsp in ("0:4:1", "0:4:2", "1:4:1", "1:4:2"):
        body = json.loads((RACK13 / "wsapi" / f"ports_{nsp.replace(':', '_')}_iscsivlans.json").read_text())
        assert sorted(body) == ["iSCSIVlans", "links", "total"]        # not the {"members": ...} envelope
        assert parse_iscsi_vlans_wsapi(nsp, body) == []
    ports = json.loads((RACK13 / "wsapi" / "ports.json").read_text())["members"]
    iscsi = [m for m in ports if m["protocol"] == 2]
    assert len(iscsi) == 4 and all(m["iSCSIPortInfo"]["vlan"] == 0 for m in iscsi)
    assert all(m["iSCSIVlans"] == [] for m in ports)
    with pytest.raises(ValueError, match="no iSCSIVlans list"):
        parse_iscsi_vlans_wsapi("0:4:1", {"members": [], "total": 0})
    with pytest.raises(ValueError, match="no vlanTag"):          # a field this code has not seen
        parse_iscsi_vlans_wsapi("0:4:1", {"iSCSIVlans": [{"IPAddr": "192.0.2.11", "netmask": "255.255.255.0"}]})


def test_wsapi_on_os_10_5_60_lists_the_untagged_address_as_vlan_tag_0_and_the_parser_leaves_it_out():
    """E18U31 (OS 10.5.60, 2026-11-17), unlike rack13-ARCUS (OS 10.6.0), answers GET
    /ports/<n:s:p>/iSCSIVlans/ with the port's untagged address as one record with `vlanTag` 0, and
    GET /ports carries the same record in each iSCSI port's `iSCSIVlans`. Tag 0 is the untagged
    address, not a VLAN interface. These are the first real records in hand: their field names are
    the ones the parser reads."""
    from alletra_onboard.adapters.array.wsapi_client import parse_iscsi_vlans_wsapi
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi
    from alletra_onboard.domain.network import IscsiVlanInterface

    base = {p.nsp: p for p in parse_showport_iscsi((E18U31_NOW / "showport_iscsi.txt").read_text())}
    ports = {"{node}:{slot}:{cardPort}".format(**m["portPos"]): m
             for m in json.loads((E18U31_NOW / "wsapi" / "ports.json").read_text())["members"]}
    for nsp, port in base.items():
        body = json.loads((E18U31_NOW / "wsapi" / f"ports_{nsp.replace(':', '_')}_iscsivlans.json").read_text())
        assert sorted(body) == ["iSCSIVlans", "links", "total"] and body["total"] == 1
        (rec,) = body["iSCSIVlans"]
        assert sorted(rec) == ["IPAddr", "gateway", "iSNSAddr", "iSNSPort", "mtu", "netmask", "stgt", "tpgt", "vlanTag"]
        assert (rec["vlanTag"], rec["IPAddr"], rec["netmask"], rec["gateway"], rec["mtu"]) == \
            (0, port.ip, port.netmask, "0.0.0.0", 9000)
        assert parse_iscsi_vlans_wsapi(nsp, body) == []
        assert ports[nsp]["iSCSIVlans"] == [rec] and ports[nsp]["iSCSIPortInfo"]["vlan"] == 0
    assert all(m["iSCSIVlans"] == [] for nsp, m in ports.items() if nsp not in base)
    # The real 1:4:2 record with a tag put in maps field by field. Tagged values are still owed.
    real = json.loads((E18U31_NOW / "wsapi" / "ports_1_4_2_iscsivlans.json").read_text())["iSCSIVlans"][0]
    assert parse_iscsi_vlans_wsapi("1:4:2", {"iSCSIVlans": [{**real, "vlanTag": 120}]}) == [
        IscsiVlanInterface(nsp="1:4:2", vlan_id=120, ip="20.1.1.3", netmask="255.255.255.0", mtu="9000")]
    with pytest.raises(ValueError, match="vlanTag 4095"):
        parse_iscsi_vlans_wsapi("1:4:2", {"iSCSIVlans": [{**real, "vlanTag": 4095}]})


@NO_STARRED_ROW
def test_discovery_reads_a_starred_iscsi_address_without_its_star():
    """`help showport`: an address shown with `*` has more addresses configured with VLANs beside it.
    Discovery's address column (`parse_iscsi_ips`) keeps the star today, so once a port carries a VLAN
    it would show `10.93.18.10*`. ADR 0017's live confirmation captures such a row; fix the parser on
    it before the apply. Edit the expectation to what the capture shows, never the capture."""
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_ips

    text = (TAGGED / "showport_iscsi.txt").read_text()
    assert "*" in text
    ips = parse_iscsi_ips(text)
    assert ips and not any("*" in ip for ip in ips.values())


def test_a_tagged_wsapi_iscsivlans_record_parses():
    """The record's field names are seen on E18U31's untagged record (OS 10.5.60); this pins a tagged one."""
    from alletra_onboard.adapters.array.wsapi_client import parse_iscsi_vlans_wsapi

    found = []
    for path in sorted((TAGGED / "wsapi").glob("ports_*_iscsivlans.json")):
        nsp = ":".join(path.name.split("_")[1:4])
        found += parse_iscsi_vlans_wsapi(nsp, json.loads(path.read_text()))
    assert found and all(1 <= v.vlan_id <= 4094 and v.ip and v.netmask for v in found)
    assert [(v.nsp, v.vlan_id, v.ip, v.netmask) for v in found] == [("0:4:2", 2999, "192.0.2.10", "255.255.255.0")]


_VLAN_FORMS = (
    "controliscsiport addr <IP_address> <netmask|prefix_len> [-vlan <vlan_tag>] [-f] <node:slot:port>",
    "controliscsiport gw <gw_address> [-vlan <vlan_tag>] [-f] <node:slot:port>",
    "controliscsiport delete [-vlan <vlan_tag>] [-f] <node:slot:port>",
)


def test_the_array_help_names_the_vlan_add_gateway_and_delete_forms():
    """The forms R3 prints and R5's removal set uses, as rack13-ARCUS's help gives them. `delete`
    without `-vlan` removes the port's untagged address (the help's own example), so a removal line
    must always carry `-vlan`."""
    text = (RACK13 / "help_controliscsiport.txt").read_text()
    forms = [ln.strip() for ln in text.splitlines()]
    assert all(form in forms for form in _VLAN_FORMS)
    assert "For other commands, the VLAN tag is in the range [1-4094]." in forms
    assert "cli% controliscsiport delete -f 1:1:1" in forms and "iSCSI port configuration is deleted:" in text


@pytest.mark.parametrize("release", sorted(OS_10_5))
def test_os_10_5_help_gives_the_same_vlan_add_gateway_and_delete_forms(release):
    """OS 10.5.0, 10.5.51 and 10.5.60 print one and the same `help controliscsiport`, and its address,
    gateway and delete forms take `-vlan` exactly as on 10.6.0: R3's and R5's lines hold on both.
    10.5 words the range "(1 to 4094)" and lacks 10.6.0's initiator range and `-skip_rescan`."""
    text = (OS_10_5[release] / "help_controliscsiport.txt").read_text()
    forms = [ln.strip() for ln in text.splitlines()]
    assert all(form in forms for form in _VLAN_FORMS)
    assert "Indicates the VLAN tag number (1 to 4094)." in forms
    assert "For other commands, the VLAN tag is in the range [1-4094]." not in forms
    assert "cli% controliscsiport delete -f 1:1:1" in forms and "iSCSI port configuration is deleted:" in text
    assert text == (D22U27 / "help_controliscsiport.txt").read_text()


@pytest.mark.parametrize("folder, forms_with_vlan", [
    (RACK13, ["add", "addr", "delete", "gw", "mtu", "state"]),     # OS 10.6.0
    (D22U27, []), (VZ, []), (E18U31_NOW, []),                       # OS 10.5.0, 10.5.51, 10.5.60
])
def test_controlport_rcip_takes_vlan_on_os_10_6_only(folder, forms_with_vlan):
    """SPEC-024 §2 leaves RCIP VLANs out of scope; this pins which OS could carry them."""
    lines = [ln.strip() for ln in (folder / "help_controlport.txt").read_text().splitlines()]
    rcip = [ln for ln in lines if ln.startswith("controlport rcip ")]
    assert {"add", "addr", "delete", "gw"} <= {ln.split()[2] for ln in rcip}
    assert sorted({ln.split()[2] for ln in rcip if "[-vlan <vlan_tag>]" in ln}) == forms_with_vlan


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


def test_one_vlan_on_an_iscsi_port_of_each_node_is_planned_as_two_adds():
    plan = _plan([_req(), _req("1:4:1", ip="192.0.2.12")])
    assert [(a.nsp, a.vlan_id, a.state) for a in plan.actions] == [("0:4:1", 120, "create"), ("1:4:1", 120, "create")]
    assert plan.blockers == [] and plan.notes == []
    # The CLI lines are printed, the array's own forms, each with -vlan: without it they would change
    # the port's untagged address and cut off the hosts logged in on it (ADR 0017).
    assert [a.cli.splitlines() for a in plan.actions] == [
        ["controliscsiport addr 192.0.2.11 255.255.255.0 -vlan 120 -f 0:4:1",
         "controliscsiport gw 192.0.2.1 -vlan 120 -f 0:4:1"],
        ["controliscsiport addr 192.0.2.12 255.255.255.0 -vlan 120 -f 1:4:1",
         "controliscsiport gw 192.0.2.1 -vlan 120 -f 1:4:1"],
    ]
    (no_gateway,) = _plan([_req(gw="")]).actions
    assert no_gateway.cli == "controliscsiport addr 192.0.2.11 255.255.255.0 -vlan 120 -f 0:4:1"


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


def test_a_port_the_array_does_not_have_is_a_conflict():
    (action,) = _plan([_req("2:4:1")]).actions
    assert action.state == "conflict" and action.reason == "AlletraMP_E18U31 has no port 2:4:1 (showport)."


def test_a_peer_enabled_iscsi_port_is_a_conflict():
    (action,) = _plan([_req()], _view(peer_enabled=("0:4:1",))).actions
    assert action.state == "conflict" and "is a peer-enabled iSCSI port" in action.reason


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


@pytest.mark.parametrize("ip, mask, where", [
    ("10.30.14.2", "255.255.255.0", "iSCSI port 0:4:2"),         # E18U31's own iSCSI address
    ("10.54.154.192", "255.255.248.0", "RCIP port 0:4:3"),
    ("10.64.154.190", "255.255.248.0", "management"),
])
def test_an_address_already_in_use_on_the_array_is_a_conflict(ip, mask, where):
    (action,) = _plan([_req("1:4:2", ip=ip, mask=mask, gw="")]).actions
    assert action.state == "conflict" and action.reason == f"{ip} is already in use on AlletraMP_E18U31: {where}."


def test_a_vlan_in_the_ports_own_untagged_network_is_a_conflict():
    (action,) = _plan([_req(ip="10.30.14.50", gw="")]).actions
    assert action.state == "conflict"
    assert action.reason.startswith("10.30.14.0/24 is already the network of iSCSI port 0:4:1 on AlletraMP_E18U31")


def test_a_vlan_on_one_node_only_is_a_note_not_a_blocker():
    plan = _plan([_req(), _req("0:4:2", ip="192.0.2.12")])
    assert plan.blockers == []
    assert any("VLAN 120 is only on node 0" in n for n in plan.notes)


def test_the_switch_side_is_a_sentence_per_port_for_the_network_team_never_a_command():
    from alletra_onboard.domain.network import IscsiVlanInterface

    there = IscsiVlanInterface(nsp="0:4:1", vlan_id=130, ip="198.51.100.11", netmask="255.255.255.0")
    plan = _plan([_req(), _req("1:4:1", ip="192.0.2.12")], _view(vlans=[there]))
    # The native VLAN stays: the hosts already logged in use the port's untagged address.
    keep = "keep the untagged (native) VLAN as it is."
    assert plan.switch_handoff == [
        f"Switch port cabled to AlletraMP_E18U31 0:4:1: carry VLAN 120, 130 tagged (802.1Q); {keep}",
        f"Switch port cabled to AlletraMP_E18U31 1:4:1: carry VLAN 120 tagged (802.1Q); {keep}",
    ]


# ------------------------------------------------------------------ R5: the removal set

def test_the_removal_set_undoes_every_write_this_apply_sent_last_first():
    """ADR 0025: the removal line is written before the write is sent, so a write that failed after
    the send (address set, gateway refused) keeps its line. An interface that existed never has one.
    Every line carries -vlan: `controliscsiport delete -f <port>` deletes the port's whole configuration."""
    from alletra_onboard.application.provisioning.iscsi_network import removal_lines
    from alletra_onboard.domain.network import IscsiVlanOutcome

    lines = removal_lines([
        IscsiVlanOutcome(nsp="0:4:1", vlan_id=120, status="created"),
        IscsiVlanOutcome(nsp="0:4:2", vlan_id=120, status="exists"),
        IscsiVlanOutcome(nsp="1:4:1", vlan_id=120, status="created"),
        IscsiVlanOutcome(nsp="1:4:2", vlan_id=120, status="failed"),
    ])
    assert lines == [
        "controliscsiport delete -vlan 120 -f 1:4:2",
        "controliscsiport delete -vlan 120 -f 1:4:1",
        "controliscsiport delete -vlan 120 -f 0:4:1",
    ]


# ------------------------------------------------------------------ R2: the read, over a fake CLI

_READS = {
    "showsys": "showsys.txt", "showport": "showport.txt", "showport -iscsi": "showport_iscsi.txt",
    "showport -iscsivlans": "showport_iscsivlans.txt", "showport -rcip": "showport_rcip.txt",
    "showport -file": "showport_file.txt", "shownet": "shownet.txt",
}


class _CaptureCli:
    """Answers each read with the capture's own file; refuses anything the read client would."""

    def __init__(self, folder: Path, override: dict[str, str] | None = None):
        self.folder, self.override, self.commands = folder, override or {}, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def run(self, command: str) -> str:
        assert cli_client.refusal(command) is None, command
        self.commands.append(command)
        if command in self.override:
            return self.override[command]
        return (self.folder / _READS[command]).read_text()


def _read(folder: Path, override: dict[str, str] | None = None):
    from alletra_onboard.application.provisioning.iscsi_network import read_port_network
    from alletra_onboard.domain.shared import EndpointCreds

    cli = _CaptureCli(folder, override)
    view = read_port_network(EndpointCreds(host="192.0.2.99", username="u", password="p"),
                             array_cli_factory=lambda _creds: cli)
    return view, cli.commands


@pytest.mark.parametrize("folder, name, mgmt, others", [
    (RACK13, "rack13-ARCUS", ("10.132.30.121", "255.255.240.0"), {}),
    (D22U27, "AlletraMP_D22U27", ("10.64.122.99", "255.255.248.0"), {
        "10.54.122.92": "RCIP port 0:4:3", "10.54.122.93": "RCIP port 1:4:3",
        "10.54.90.70": "file port 0:4:1", "10.54.90.71": "file port 0:4:2",
        "10.54.90.73": "file port 1:4:1", "10.54.90.74": "file port 1:4:2"}),
    (VZ, "MPB10K-D24U21-VZ", ("10.64.122.140", "255.255.248.0"), {
        "10.222.1.5": "RCIP port 0:4:3", "10.222.1.6": "RCIP port 0:4:4",
        "10.222.1.7": "RCIP port 1:4:3", "10.222.1.8": "RCIP port 1:4:4"}),
    (E18U31_NOW, "DHCI_B10K", ("10.64.154.190", "255.255.248.0"), {}),
])
def test_the_read_builds_the_view_from_each_capture_in_one_read_only_session(folder, name, mgmt, others):
    from alletra_onboard.application.provisioning.discovery import parse_showport_iscsi

    view, commands = _read(folder)
    assert sorted(commands) == sorted(_READS)                    # each once, no write, no showhost -d
    assert (view.name, (view.mgmt_ip, view.mgmt_netmask)) == (name, mgmt)
    assert view.roles == parse_showport_roles((folder / "showport.txt").read_text())[0]
    assert view.iscsi_ports == parse_showport_iscsi((folder / "showport_iscsi.txt").read_text())
    assert view.vlans == [] and view.other_addresses == others


def test_a_read_the_array_refused_fails_the_read_instead_of_reading_as_nothing_there():
    with pytest.raises(ValueError, match="showport -iscsivlans` answered: Error"):
        _read(RACK13, {"showport -iscsivlans": "Error: Invalid option -iscsivlans\n"})


def test_the_plan_on_rack13_adds_on_a_ready_and_an_offline_port_and_says_the_offline_one_waits_for_its_link():
    view, _ = _read(RACK13)
    plan = _plan([_req("0:4:1"), _req("1:4:2", ip="192.0.2.12"), _req("1:4:1", vlan=130, ip="10.93.19.50", mask="255.255.254.0", gw="")], view)
    assert [(a.nsp, a.state) for a in plan.actions] == [("0:4:1", "create"), ("1:4:2", "create"), ("1:4:1", "conflict")]
    assert plan.actions[2].reason == ("10.93.18.0/23 is already the network of iSCSI port 1:4:1 on rack13-ARCUS; "
                                      "a VLAN needs a network of its own.")
    assert plan.notes == ["VLAN 130 is only on node 1. If that node stops, hosts on VLAN 130 lose every path.",
                          "1:4:2 is offline: the address is set, but no host reaches it until the link is up."]
    assert [s.split(":")[0] for s in plan.switch_handoff] == ["Switch port cabled to rack13-ARCUS 0", "Switch port cabled to rack13-ARCUS 1"]


def test_a_vlan_only_address_is_not_read_as_the_ports_untagged_address():
    """Live on rack13-ARCUS, 2026-11-17 (`tagged/`): with VLAN 2999 the only address on 0:4:2, `showport
    -iscsi` prints 192.0.2.10 in 0:4:2's base columns, no `*`. Only `showport -iscsivlans` says it is
    tagged (no `untagged` row for 0:4:2). Read as untagged, a second VLAN in 192.0.2.0/24 on that port was
    refused as the port's own network, and the address was named as the port's base address."""
    view, _ = _read(TAGGED)
    base = {p.nsp: p.ip for p in view.iscsi_ports}
    assert base == {"0:4:1": "10.93.18.10", "0:4:2": "", "1:4:1": "10.93.18.12", "1:4:2": ""}
    assert [(v.nsp, v.vlan_id, v.ip) for v in view.vlans] == [("0:4:2", 2999, "192.0.2.10")]

    plan = _plan([_req("0:4:2", vlan=3000, ip="192.0.2.20", gw=""), _req("1:4:2", vlan=3000, ip="192.0.2.10", gw="")], view)
    assert [(a.nsp, a.state) for a in plan.actions] == [("0:4:2", "create"), ("1:4:2", "conflict")]
    assert plan.actions[1].reason == "192.0.2.10 is already in use on rack13-ARCUS: iSCSI port 0:4:2 VLAN 2999."


def test_a_conflict_row_keeps_the_switch_sentence_for_the_vlan_already_on_its_port():
    """Live on rack13-ARCUS, 2026-11-17 (`tagged/`): VLAN 2999 was on 0:4:2 without its gateway, so the row
    became a conflict and the plan dropped the network team's sentence. R3 asks for one per port with a
    planned or existing VLAN; the as-built printed it."""
    view, _ = _read(TAGGED)
    plan = _plan([_req("0:4:2", vlan=2999, ip="192.0.2.10", gw="192.0.2.1"), _req("1:4:1", vlan=7, ip="10.93.18.12", gw="")],
                 view)
    assert [a.state for a in plan.actions] == ["conflict", "conflict"]
    assert plan.switch_handoff == [
        "Switch port cabled to rack13-ARCUS 0:4:2: carry VLAN 2999 tagged (802.1Q); keep the untagged (native) VLAN as it is."]


def test_the_plan_on_d22u27_refuses_its_file_ports_and_on_vz_names_the_rcip_addresses():
    view, _ = _read(D22U27)
    (action,) = _plan([_req("0:4:1")], view).actions
    assert action.reason == ("AlletraMP_D22U27 0:4:1 is not an iSCSI port: showport lists it as target ready file IP. "
                             "The tool never changes a port's role.")
    view, _ = _read(VZ)
    (action,) = _plan([_req("0:4:1", ip="10.222.1.7", mask="255.255.255.0", gw="")], view).actions
    assert action.reason == "10.222.1.7 is already in use on MPB10K-D24U21-VZ: RCIP port 1:4:3."


def test_a_sheet_row_without_a_gateway_matches_an_interface_that_has_one_but_a_different_gateway_does_not():
    from alletra_onboard.domain.network import IscsiVlanInterface

    there = IscsiVlanInterface(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="24", gateway="192.0.2.1")
    assert [a.state for a in _plan([_req(gw="")], _view(vlans=[there])).actions] == ["exists"]
    (action,) = _plan([_req(gw="192.0.2.254")], _view(vlans=[there])).actions
    assert action.state == "conflict" and "(gateway 192.0.2.1); the sheet says 192.0.2.11 255.255.255.0 (gateway 192.0.2.254)" in action.reason


# ------------------------------------------------------------------ R8: the step

def test_the_array_ports_step_sits_between_discovery_and_san_zoning():
    from alletra_onboard.domain.workflow import STEP_REGISTRY

    keys = [s.key for s in STEP_REGISTRY]
    assert keys.index("discover") < keys.index("ports") < keys.index("zoning")
    assert next(s for s in STEP_REGISTRY if s.key == "ports").label == "Array ports"


# ------------------------------------------------------------------ R8: the step service (preview only)

def _service_run(tmp_path, rows):
    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.application.service import OnboardingService
    from alletra_onboard.config import Settings

    parsed = init_sheet.parse_workbook_bytes(_workbook(rows), mode=RunMode.PROVISION_ONLY)
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(parsed.work_item, mode=RunMode.PROVISION_ONLY, provisioning_intent=parsed.provisioning_intent)
    return service, run


def _events(service, run, kind):
    return [e for e in service.list_events(run.run_id) if e.event_type == kind]


async def test_with_no_iscsi_rows_the_step_reads_nothing_and_is_complete(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import iscsi_network

    monkeypatch.setattr(iscsi_network, "read_port_network", lambda *a, **k: pytest.fail("read the array"))
    service, run = _service_run(tmp_path, None)
    before = service.get_run(run.run_id)
    service.start_ports_preview(run.run_id)
    await service.wait(run.run_id)
    (event,) = _events(service, run, "ports.completed")
    # BL-26 added the peer-port section to the step: the sentence names both tabs (changed on purpose).
    assert event.message == "The sheet asks for no iSCSI VLANs and no peer ports. Nothing to set up here."
    after = service.get_run(run.run_id)
    assert (after.status, after.current_phase) == (before.status, before.current_phase)


async def test_the_preview_reads_the_array_plans_and_holds_the_plan_until_a_new_read(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import iscsi_network
    from alletra_onboard.domain.models import RunStatus, WorkflowPhase

    view, _ = _read(RACK13)
    reads = iter([view, RuntimeError("SSH connection refused")])

    def read(creds):
        answer = next(reads)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(iscsi_network, "read_port_network", read)
    service, run = _service_run(tmp_path, ROWS)
    service.start_ports_preview(run.run_id)
    await service.wait(run.run_id)
    (event,) = _events(service, run, "ports.previewed")
    assert event.message == "Read rack13-ARCUS: plan ready, 2 to add, 0 conflict(s), 0 already there."
    assert event.phase == WorkflowPhase.STORAGE_PORTS
    assert service.get_run(run.run_id).status == RunStatus.WAITING_FOR_OPERATOR
    plan = event.data["iscsi"]["plan"]
    assert [a["cli"].splitlines()[0] for a in plan["actions"]] == [
        "controliscsiport addr 192.0.2.11 255.255.255.0 -vlan 120 -f 0:4:1",
        "controliscsiport addr 192.0.2.12 255.255.255.0 -vlan 120 -f 1:4:1"]
    assert service.get_ports(run.run_id)["iscsi_plan_held"] is True
    assert "password" not in str(event.data)

    service.start_ports_preview(run.run_id)            # a new read withdraws the plan, even when it fails
    await service.wait(run.run_id)
    (failed,) = _events(service, run, "ports.preview.failed")
    assert failed.message.startswith("Could not read 10.64.154.190: SSH connection refused.")
    assert service.get_run(run.run_id).status == RunStatus.RETRYABLE_FAILURE
    assert service.get_ports(run.run_id)["iscsi_plan_held"] is False


async def test_when_every_row_is_already_there_the_step_is_complete(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import iscsi_network
    from alletra_onboard.domain.models import RunStatus
    from alletra_onboard.domain.network import IscsiVlanInterface

    view, _ = _read(RACK13)
    view.vlans = [IscsiVlanInterface(nsp=r["port"], vlan_id=120, ip=r["ip"], netmask=r["netmask"], gateway=r["gateway"])
                  for r in ROWS]
    monkeypatch.setattr(iscsi_network, "read_port_network", lambda creds: view)
    service, run = _service_run(tmp_path, ROWS)
    service.start_ports_preview(run.run_id)
    await service.wait(run.run_id)
    (event,) = _events(service, run, "ports.completed")
    assert event.message == "Read rack13-ARCUS: all 2 iSCSI address(es) the sheet asks for are on the array."
    assert service.get_run(run.run_id).status == RunStatus.READY


# ------------------------------------------------------------------ R6: Verify, R7: the as-built

def _tagged_e18u31(tag="120", ip="192.0.2.11"):
    """E18U31's own `showport -iscsivlans` (OS 10.5.60) with one row turned into a tagged interface.
    Derived here, not captured: no lab port carries a tagged interface yet (the live confirmation
    captures one into tests/fixtures/iscsi_vlan/tagged/)."""
    text = (E18U31_NOW / "showport_iscsivlans.txt").read_text()
    row = next(ln for ln in text.splitlines() if ln.startswith("0:4:1 "))
    tagged = row.replace("untagged", tag.rjust(len("untagged")), 1).replace("10.1.1.2", ip.ljust(len("10.1.1.2")), 1)
    return text.replace(row, row + "\n" + tagged, 1)


def test_verify_says_present_missing_or_different_for_each_sheet_row():
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans
    from alletra_onboard.application.provisioning.iscsi_network import verify_iscsi_vlans

    vlans = parse_iscsi_vlans(_tagged_e18u31())
    assert [(v.nsp, v.vlan_id, v.ip, v.mtu) for v in vlans] == [("0:4:1", 120, "192.0.2.11", "9000")]
    checks = verify_iscsi_vlans([_req(gw=""), _req("1:4:1", ip="192.0.2.12")], vlans)
    assert [(c.nsp, c.status) for c in checks] == [("0:4:1", "present"), ("1:4:1", "missing")]
    (check,) = verify_iscsi_vlans([_req(ip="192.0.2.50", gw="192.0.2.1")], vlans)
    assert check.status == "different"
    assert check.differences == ["address: 192.0.2.11 on the array, 192.0.2.50 on the sheet",
                                 "gateway: none on the array, 192.0.2.1 on the sheet"]


async def test_the_verify_step_compares_the_sheets_iscsi_rows_read_only(tmp_path):
    from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans
    from alletra_onboard.domain.models import VerificationReport

    service, run = _service_run(tmp_path, ROWS)
    service.documents._verify_fn = lambda item, username, password: VerificationReport(reachable=True)
    seen = []
    service.documents._read_iscsi_vlans = lambda creds: (seen.append(creds.host), parse_iscsi_vlans(_tagged_e18u31()))[1]
    service.start_verify(run.run_id)
    await service.wait(run.run_id)
    (event,) = _events(service, run, "verify.completed")
    assert seen == ["10.64.154.190"] and event.message.endswith("iSCSI VLAN addresses: 0 of 2 present.")
    statuses = [(c["nsp"], c["status"]) for c in event.data["report"]["iscsi_vlans"]]
    assert statuses == [("0:4:1", "different"), ("1:4:1", "missing")]       # the sheet gives gateway 192.0.2.1

    def refused(creds):
        raise RuntimeError("connection reset")

    service.documents._read_iscsi_vlans = refused
    service.start_verify(run.run_id)
    await service.wait(run.run_id)
    event = _events(service, run, "verify.completed")[-1]
    assert event.data["report"]["iscsi_vlans_error"] == "`showport -iscsivlans` could not be read: connection reset"


async def test_verify_reads_no_iscsi_vlans_when_the_sheet_has_none(tmp_path):
    from alletra_onboard.domain.models import VerificationReport

    service, run = _service_run(tmp_path, None)
    service.documents._verify_fn = lambda item, username, password: VerificationReport(reachable=True)
    service.documents._read_iscsi_vlans = lambda creds: pytest.fail("read showport -iscsivlans")
    service.start_verify(run.run_id)
    await service.wait(run.run_id)
    (event,) = _events(service, run, "verify.completed")
    assert event.data["report"]["iscsi_vlans"] == [] and "iSCSI" not in event.message


def test_the_as_built_lists_every_vlan_interface_with_its_port_state_and_the_switch_sentence(tmp_path):
    import docx
    from docx.oxml.ns import qn

    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt

    data = AsBuiltData(
        name="DHCI_B10K", showport=(E18U31_NOW / "showport.txt").read_text(), showport_iscsivlans=_tagged_e18u31(),
        iscsi_network_rows=[_req(gw="").model_dump(), _req("1:4:1", ip="192.0.2.12", gw="").model_dump()],
        iscsi_set_up_in_run=[("0:4:1", 120)],
    )
    out, warnings = generate_asbuilt(data, tmp_path / "asbuilt.docx")
    doc = docx.Document(str(out))
    text = "".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))
    assert "iSCSI network" in [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
    table = next([[c.text.strip() for c in r.cells] for r in t.rows] for t in doc.tables
                 if [c.text.strip() for c in t.rows[0].cells][:2] == ["Port", "VLAN"])
    assert table[1:] == [["0:4:1", "120", "192.0.2.11/24", "—", "9000", "ready", "By this run"]]
    assert "Asked for on the sheet but not on the array: 1:4:1 VLAN 120 (192.0.2.12)." in text
    assert ("Switch port cabled to DHCI_B10K 0:4:1: carry VLAN 120 tagged (802.1Q); keep the untagged (native) "
            "VLAN as it is.") in text
    assert not [w for w in warnings if "iscsivlans" in w]


def test_the_as_built_names_a_failed_iscsivlans_read_and_the_run_records_take_the_plans_adds():
    from types import SimpleNamespace

    from alletra_onboard.application.documents import steps as st
    from alletra_onboard.application.documents.asbuilt import AsBuiltData

    plan = {"actions": [{"nsp": "0:4:1", "vlan_id": 120, "state": "create"}, {"nsp": "1:4:1", "vlan_id": 120, "state": "exists"}]}
    events = [SimpleNamespace(event_type="ports.previewed", data={"iscsi": {"plan": plan}}, created_at="t1"),
              SimpleNamespace(event_type="ports.completed", data={"iscsi": None}, created_at="t2")]
    coord = SimpleNamespace(list_events=lambda run_id: events, list_commands=lambda run_id, since=0: [])
    data = AsBuiltData()
    st.DocumentSteps(coord=coord)._run_records("r1", data)
    assert data.iscsi_set_up_in_run == [("0:4:1", 120)]
    assert ("showport_iscsivlans", "showport -iscsivlans") in st.DocumentSteps._ASBUILT_LISTINGS


@pytest.mark.parametrize("over, why", [
    ({"read_errors": {"showport -iscsivlans": "TimeoutError: no answer"}}, "TimeoutError: no answer"),
    ({"showport_iscsivlans": "Error: Invalid option -iscsivlans"}, "Error: Invalid option -iscsivlans"),
    ({"showport_iscsivlans": _tagged_e18u31(tag="9999")}, "neither a tag from 1 to 4094 nor untagged"),
])
def test_the_as_built_names_an_iscsivlans_read_it_could_not_use_even_without_sheet_rows(tmp_path, over, why):
    """Without the read the document cannot know whether the array has an interface, so it says so."""
    import docx

    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt

    data = AsBuiltData(name="DHCI_B10K", showport=(E18U31_NOW / "showport.txt").read_text())
    for key, value in over.items():
        setattr(data, key, value)
    out, warnings = generate_asbuilt(data, tmp_path / "asbuilt.docx")
    doc = docx.Document(str(out))
    assert "iSCSI network" in [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
    assert any("showport -iscsivlans" in w and why in w for w in warnings)
