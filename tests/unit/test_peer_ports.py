"""SPEC-025 (BL-26) — peer ports for migration, set up by the tool.

Two kinds of test live here:

* Guards on today's behaviour (no marker). They pass now and pin the facts the design stands on: the
  Remote Copy write client and the read client refuse every `controlport` form a peer port needs, host
  zoning never offers a peer FC port, and `showhost -d` names the login that makes a port busy.
* The feature (strict xfail, see docs/workpackets/BL-26.md). Each turns green, and must lose its marker,
  when the work-packet step that builds it lands.

Captures used (real output; the 2026-11-17 ones have two names replaced, see the fixture README):
rack13-ARCUS `peer_ports/rack13/` (OS 10.6.0, 2026-11-16, lab/peer_port_capture.py: every read the
peer-port section makes, taken at one moment, no port in peer mode); the same script on 2026-11-17 on
E18U31 `peer_ports/E18U31/` (OS 10.5.60, FC peer ports 0:3:2 and 1:3:2), D22U27 `peer_ports/D22U27/`
(OS 10.5.0) and VZ `peer_ports/VZ/` (OS 10.5.51), neither with a peer port; rack13-ARCUS
`rcip_pair/before/alletra/showport.txt` (2026-11-03) with `rack13_array/showhost_d.txt` and
`showvlun_a.txt` (2026-09-13: same array, an earlier day, when 0:3:3 still served a host); D22U27
`rc_pair/D22U27/showport.txt` (2026-10-07) with `d22u27_iscsi/showhost_d.txt` (2026-10-26); E18U31
`rc_pair/E18U31/showport.txt` (2026-10-07, the same peer ports); the Primera
`rcip_pair/before/primera/showport.txt` (2026-11-03).
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
PEER_FIX = FIX / "peer_ports"
RACK13 = PEER_FIX / "rack13"          # lab/peer_port_capture.py, 2026-11-16 23:20 IST, read-only
E18U31 = PEER_FIX / "E18U31"          # the same script, 2026-11-17, read-only: two FC ports in peer mode
D22U27 = PEER_FIX / "D22U27"          # 2026-11-17, OS 10.5.0, no peer port
VZ = PEER_FIX / "VZ"                  # 2026-11-17, OS 10.5.51, no peer port
E18U31_SHOWPORT_PAR = E18U31 / "showport_par.txt"
E18U31_SHOWPORT_PEER = E18U31 / "showport_peer.txt"
E18U31_WSAPI_PORTS = E18U31 / "wsapi_ports.json"

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


def test_the_peer_ports_tab_parses_into_the_intent():
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    assert _sheet(ROWS) == PeerPortIntent(ports=[
        PeerPortRequest(nsp="0:3:2", source_wwpns=["20310002AC02AC38"]),
        PeerPortRequest(nsp="1:3:2", source_wwpns=["21310002AC02AC38"]),
    ])


def test_a_workbook_without_the_tab_has_no_peer_ports():
    assert _sheet(None) is None


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


def test_a_port_on_the_peer_ports_and_the_replication_network_tab_has_two_roles():
    from alletra_onboard.application.platform import init_sheet
    from alletra_onboard.domain.models import RunMode

    network = [{"array": "this", "port": "0:4:4", "ip": "10.93.18.11", "netmask": "255.255.254.0"},
               {"array": "this", "port": "1:4:4", "ip": "10.93.18.13", "netmask": "255.255.254.0"},
               {"array": "peer", "port": "0:1:1", "ip": "10.93.18.19", "netmask": "255.255.254.0"},
               {"array": "peer", "port": "1:1:1", "ip": "10.93.18.20", "netmask": "255.255.254.0"}]
    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D2K014S", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[], peer_ports=[{"port": "0:4:4"}, ROWS[1]],
        replication={"fields": {"peer_host": "10.64.154.190", "peer_user": "3paradm", "peer_password": "pw"},
                     "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}], "network": network})
    with pytest.raises(ValueError, match=re.escape(
            "Peer ports tab — port 0:4:4 is also on the Replication network tab; a port has one role.")):
        init_sheet.parse_workbook_bytes(data, mode=RunMode.CUSTOM, selected_steps=["ports", "replicate"])


def test_the_template_has_the_peer_ports_tab_and_an_upload_with_only_peer_ports_parses():
    """A workbook may ask only for peer ports: Volumes and Host sets empty, as for replicate-only."""
    import io

    from openpyxl import load_workbook

    from alletra_onboard.application.platform import init_sheet

    ws = load_workbook(io.BytesIO(init_sheet.build_template_bytes()))[init_sheet.PEER_PORTS_SHEET_NAME]
    header = next(r for r in ws.iter_rows() if any(c.value == "Port (N:S:P) *" for c in r))
    assert [c.value for c in header][:2] == ["Port (N:S:P) *", "Source array ports to zone (WWPNs)"]
    assert ws.cell(row=header[0].row + 1, column=1).number_format == "@"
    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D2K014S", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[], peer_ports=ROWS)
    from alletra_onboard.domain.models import RunMode

    # even with Provision storage selected: the run guard refuses that step later (nothing to provision)
    intent = init_sheet.parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY).provisioning_intent
    assert [p.nsp for p in intent.peer_ports.ports] == ["0:3:2", "1:3:2"] and intent.volumes == []


# ------------------------------------------------------------------ R2: the read

def test_e18u31_peer_ports_read_with_their_own_node_wwn():
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    ports = parse_showport_ports(_text(E18U31_SHOWPORT))
    p = ports["0:3:2"]
    assert (p.mode, p.state, p.type, p.protocol) == ("initiator", "ready", "peer", "FC")
    assert (p.node_wwn, p.port_wwn) == ("2FF70202AC02DEF2", "20320202AC02DEF2")
    assert ports["0:3:1"].node_wwn == "2FF70002AC02DEF2"      # a host port of the same array


def test_the_primeras_partner_and_failover_state_are_read():
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    p = parse_showport_ports(_text(PRIMERA_SHOWPORT))["0:3:1"]
    assert (p.partner, p.failover_state) == ("1:3:1", "failed_over")


def test_showport_par_gives_the_connection_mode_to_restore():
    """rack13's `showport -par` before any change: what the removal set puts back on a free FC port.
    Layout (OS 10.6.0, the same as the CLI help's example): N:S:P Connmode ConnType CfgRate MaxRate
    Class2 UniqNodeWwn VCN IntCoal TMWO, one row per FC, NVMe and iSCSI port, none for IP ports."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_par

    params = parse_showport_par(_text(RACK13 / "showport_par.txt"))
    assert (params["0:3:2"].connmode, params["0:3:2"].conntype) == ("host", "point")
    assert params["0:3:1"].connmode == "host"
    fc = [f"{n}:3:{p}" for n in (0, 1) for p in (1, 2, 3, 4)]
    assert {(params[n].connmode, params[n].conntype) for n in fc} == {("host", "point")}
    assert (params["0:1:1"].connmode, params["0:1:1"].conntype) == ("disk", "point")     # NVMe drive port
    assert (params["0:4:1"].connmode, params["0:4:1"].conntype) == ("host", "eth")       # iSCSI
    assert len(params) == 20 and "0:4:3" not in params and "0:5:1" not in params        # IP ports: none


def test_output_that_is_not_showport_par_reads_as_nothing():
    """A wrong answer must not be read as a mode to restore: the plan then blocks on a missing read."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_par

    assert parse_showport_par(_text(RACK13 / "showport.txt")) == {}
    assert parse_showport_par(_text(RACK13 / "showport_c.txt")) == {}


def test_showport_par_reads_a_peer_port_as_peer_point():
    """E18U31 (OS 10.5.60, 2026-11-17): the peer ports read `peer point`, the value a removal set
    restores FROM; every other FC port reads `host point`, the value it restores TO."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_par

    params = parse_showport_par(_text(E18U31_SHOWPORT_PAR))
    assert (params["0:3:2"].connmode, params["0:3:2"].conntype) == ("peer", "point")
    assert (params["1:3:2"].connmode, params["1:3:2"].conntype) == ("peer", "point")
    assert params["0:3:1"].connmode == "host"
    others = [f"{n}:3:{p}" for n in (0, 1) for p in (1, 3, 4)]
    assert {(params[n].connmode, params[n].conntype) for n in others} == {("host", "point")}
    assert len(params) == 20 and "0:4:3" not in params        # the IP ports in mode peer: no row


@pytest.mark.parametrize("folder, rows", [(RACK13, 20), (E18U31, 20), (D22U27, 16), (VZ, 12)],
                         ids=["rack13", "E18U31", "D22U27", "VZ"])
def test_showport_par_has_one_layout_on_10_5_and_10_6(folder, rows):
    """The same header on OS 10.5.0 (D22U27), 10.5.51 (VZ), 10.5.60 (E18U31) and 10.6.0 (rack13); a row
    per FC, NVMe and iSCSI port, none for an IP port. D22U27 has no iSCSI port, VZ no NVMe drive port."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_par

    text = _text(folder / "showport_par.txt")
    assert text.splitlines()[1].split() == [
        "N:S:P", "Connmode", "ConnType", "CfgRate", "MaxRate", "Class2", "UniqNodeWwn", "VCN", "IntCoal", "TMWO"]
    params = parse_showport_par(text)
    assert len(params) == rows
    assert {p.conntype for p in params.values() if p.connmode == "host"} <= {"point", "eth"}


def test_showport_c_says_where_a_mode_change_is_allowed():
    """rack13: every FC port on the slot-3 cards is `allowed`; the NVMe drive ports and the iSCSI and IP
    ports are `prohibited`. 0:4:1 lists two hosts, the second on a line with no N:S:P."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_c

    change = parse_showport_c(_text(RACK13 / "showport_c.txt"))
    assert len(change) == 24
    assert {change[f"{n}:3:{p}"] for n in (0, 1) for p in (1, 2, 3, 4)} == {"allowed"}
    assert change["0:1:1"] == change["0:4:1"] == change["0:4:3"] == "prohibited"


@pytest.mark.parametrize("folder", [RACK13, D22U27, VZ], ids=["rack13", "D22U27", "VZ"])
def test_showport_peer_on_an_array_without_peer_ports_is_empty(folder):
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_peer

    text = _text(folder / "showport_peer.txt")
    assert "There is no specified port information." in text
    assert parse_showport_peer(text) == []


def test_showport_peer_reads_the_layout_the_cli_help_shows():
    """The only listing of a peer port the array has printed for us is the example in its own help
    (`help showport`, rack13, OS 10.6.0). A peer port's WWNs carry 0202 where host ports carry 0002."""
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_peer

    help_text = _text(RACK13 / "help_showport.txt")
    example = help_text.split("cli% showport -peer", 1)[1].split("cli%", 1)[0]
    rows = parse_showport_peer(example)
    assert [(r.nsp, r.mode, r.state, r.node_wwn, r.port_wwn) for r in rows] == [
        ("0:5:1", "initiator", "ready", "2FF70202AC000007", "20510202AC000007")]


def test_showport_peer_lists_e18u31_peer_ports():
    """The array's own listing (OS 10.5.60) adds a VPI column the help's example lacks. It names this
    array's peer ports with their own WWNs, the same as `showport`, never the source array they reach."""
    from alletra_onboard.application.provisioning.peer_ports import (
        parse_showport_peer,
        parse_showport_ports,
    )

    text = _text(E18U31_SHOWPORT_PEER)
    assert text.splitlines()[1].split()[-2:] == ["Rate", "VPI"]
    rows = {r.nsp: r for r in parse_showport_peer(text)}
    assert rows["0:3:2"].port_wwn == "20320202AC02DEF2" and rows["1:3:2"].port_wwn == "21320202AC02DEF2"
    assert sorted(rows) == ["0:3:2", "1:3:2"]
    assert {(r.mode, r.state, r.node_wwn) for r in rows.values()} == {("initiator", "ready", "2FF70202AC02DEF2")}
    ports = parse_showport_ports(_text(E18U31 / "showport.txt"))
    assert all((ports[n].node_wwn, ports[n].port_wwn) == (r.node_wwn, r.port_wwn) for n, r in rows.items())
    assert "AC07E528" not in text                     # the source array (seen in showport -c, below)


def test_e18u31_peer_ports_show_the_source_array_only_as_a_device():
    """What 2026-11-17 shows about the far end: nothing logs in to a peer port (`showhost -d`); the
    source array's node WWN is the port's Device in `showport -c` and `device` in GET /ports, and
    `showportdev ns` names it (an HPE 3PAR 20850, its 0:3:2 and 1:3:2 in host mode, WWNs 0002)."""
    import json

    from alletra_onboard.application.provisioning.peer_ports import parse_showport_c

    view = _now(E18U31)
    assert not view.logins.get("0:3:2") and not view.logins.get("1:3:2")
    assert parse_showport_c(_text(E18U31 / "showport_c.txt"))["0:3:2"] == "allowed"
    c_row = next(ln.split() for ln in _text(E18U31 / "showport_c.txt").splitlines() if ln.startswith("0:3:2 "))
    assert c_row[:3] == ["0:3:2", "initiator", "2FF70002AC07E528"]
    wsapi = {f"{m['portPos']['node']}:{m['portPos']['slot']}:{m['portPos']['cardPort']}": m
             for m in json.loads(_text(E18U31_WSAPI_PORTS))["members"]}
    assert wsapi["0:3:2"]["device"] == wsapi["1:3:2"]["device"] == ["2FF70002AC07E528"]
    assert "2FF70002AC07E528 20320002AC07E528" in _text(E18U31 / "showportdev_ns_032.txt")
    assert "2FF70002AC07E528 21320002AC07E528" in _text(E18U31 / "showportdev_ns_132.txt")


def test_a_peer_port_carries_0202_wwns_where_a_host_mode_port_carries_0002():
    """The WWN question (SPEC-025 §6.2), as far as captures answer it. E18U31's peer ports carry node
    WWN 2FF70202… and port WWN 2032 0202… / 2132 0202…; every FC port in host mode, on E18U31 and on
    the three arrays with no peer port, carries 0002 there. A peer port has no NVMe virtual port (the
    0102 WWNs). No capture has the same port before and after a change: that stays for the live run."""
    import json

    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    for folder in (RACK13, E18U31, D22U27, VZ):
        for nsp, p in parse_showport_ports(_text(folder / "showport.txt")).items():
            if not p.is_fc:
                continue
            marker = "0202" if p.type == "peer" else "0002"
            assert p.node_wwn[4:8] == p.port_wwn[4:8] == marker, (folder.name, nsp)
            node, slot, port = nsp.split(":")
            assert p.port_wwn[:4] == f"2{node}{slot}{port}", (folder.name, nsp)
    virtual = {f"{m['portPos']['node']}:{m['portPos']['slot']}:{m['portPos']['cardPort']}":
               [v["portWWN"] for v in m.get("virtualPorts") or []]
               for m in json.loads(_text(E18U31_WSAPI_PORTS))["members"] if m.get("protocol") == 1}
    assert virtual["0:3:2"] == virtual["1:3:2"] == []
    assert virtual["0:3:3"] == ["20330102ADF2DEF2"]


def _now(folder: Path):
    """An array as one lab/peer_port_capture.py run saw it: every read the section makes."""
    from alletra_onboard.application.provisioning.peer_ports import build_view

    return build_view(
        _text(folder / "showport.txt"), showhost_d=_text(folder / "showhost_d.txt"),
        showvlun_a=_text(folder / "showvlun_a.txt"), showport_par=_text(folder / "showport_par.txt"),
        showport_c=_text(folder / "showport_c.txt"), showport_peer=_text(folder / "showport_peer.txt"))


def _rack13_now():
    """rack13-ARCUS as one capture saw it (2026-11-16): every read the section makes."""
    return _now(RACK13)


def test_rack13_free_fc_ports_are_the_six_with_nothing_on_them():
    """SPEC-025 R3's candidate rule on the 2026-11-16 capture: FC, Type free, no login, no export.
    0:3:4 and 1:3:3 serve an unclaimed ESXi HBA; the four slot-3 ports 1 and 2 have no link."""
    from alletra_onboard.application.provisioning.peer_ports import free_fc_ports

    view = _rack13_now()
    assert free_fc_ports(view) == ["0:3:1", "0:3:2", "0:3:3", "1:3:1", "1:3:2", "1:3:4"]
    assert view.logins["0:3:4"] == view.logins["1:3:3"] == ["an unnamed initiator 10005CED8C5312A9"]
    assert view.exports == {"0:4:1": ["test_vme_shared_4"], "1:4:1": ["test_vme_shared_4"]}
    assert [n for n in ("0:3:1", "0:3:2", "1:3:1", "1:3:2") if view.ports[n].state == "loss_sync"] == [
        "0:3:1", "0:3:2", "1:3:1", "1:3:2"]
    assert view.peer_listing == [] and not any(p.type == "peer" for p in view.ports.values())


def test_the_free_port_rule_never_offers_a_peer_port():
    """E18U31 (2026-11-17), read through `read_view` as the step reads it. The peer ports have no login
    and no export, yet they are Type `peer`, not `free`: no candidate. Nor are the IP ports in mode
    `peer` (Type free, protocol IP). Only 0:3:3 and 1:3:3, free with no link, are offered."""
    from alletra_onboard.application.provisioning.peer_ports import (
        free_fc_ports,
        is_free_fc_port,
        read_view,
    )

    view = read_view(_creds(), array_cli_factory=lambda c: _ReadCli(folder=E18U31))
    assert not view.read_error
    assert free_fc_ports(view) == ["0:3:3", "1:3:3"]
    for nsp in ("0:3:2", "1:3:2"):
        p = view.ports[nsp]
        assert (p.mode, p.state, p.type, p.protocol) == ("initiator", "ready", "peer", "FC")
        assert not view.logins.get(nsp) and not view.exports.get(nsp)
        assert not is_free_fc_port(view, nsp)
    assert not is_free_fc_port(view, "0:4:3") and view.ports["0:4:3"].mode == "peer"
    assert [r.nsp for r in view.peer_listing] == ["0:3:2", "1:3:2"]


@pytest.mark.parametrize("folder, free, busy", [
    # D22U27, OS 10.5.0: 1:3:2 is labelled Peer_port and 0:3:1 `peer port`, both Type host with logins
    (D22U27, ["0:3:2", "0:3:3", "1:3:3"], {"1:3:2": ["an unnamed initiator 1000040973C52799"]}),
    # VZ, OS 10.5.51: the slot-3 ports 1 and 2 serve the three CRV hosts; 3 and 4 have no link
    (VZ, ["0:3:3", "0:3:4", "1:3:3", "1:3:4"],
     {"0:3:2": ["CRV_VZ_DL360G11D24U25", "CRV_VZ_DL360G11D24U26", "CRV_VZ_DL360G11D24U27"]}),
], ids=["D22U27", "VZ"])
def test_free_fc_ports_on_the_arrays_without_a_peer_port(folder, free, busy):
    from alletra_onboard.application.provisioning.peer_ports import free_fc_ports

    view = _now(folder)
    assert free_fc_ports(view) == free
    for nsp, who in busy.items():
        assert sorted(view.logins[nsp]) == who
    assert view.peer_listing == [] and not any(p.type == "peer" for p in view.ports.values())
    assert {p.connmode for n, p in view.params.items() if view.ports[n].is_fc} == {"host"}


def test_a_peer_label_on_a_host_port_reads_as_a_host_port():
    """D22U27 on 2026-11-17, as on 2026-10-07: three FC ports whose Label says peer are Type host,
    Connmode host, with hosts logged in (LESSONS 42)."""
    view = _now(D22U27)
    labelled = {n: p for n, p in view.ports.items() if "peer" in p.label.lower()}
    assert {n: p.label for n, p in labelled.items()} == {
        "0:3:1": "peer port", "1:3:1": "peer 1:3:1", "1:3:2": "Peer_port"}
    for nsp, p in labelled.items():
        assert (p.mode, p.type, view.params[nsp].connmode) == ("target", "host", "host")
        assert view.logins[nsp]


@pytest.mark.parametrize("reads", ["showhost", "showvlun"])
def test_a_free_type_alone_never_makes_a_candidate(reads):
    """Type says what is attached NOW: rack13 0:3:3 is `free` on 2026-11-16 though it served
    10.132.30.136 on 2026-09-13. Read with that day's logins, or its exports, it is busy either way."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, is_free_fc_port

    other = {"showhost": {"showhost_d": _text(RACK13_SHOWHOST)},
             "showvlun": {"showvlun_a": _text(RACK13_SHOWVLUN)}}[reads]
    view = build_view(_text(RACK13 / "showport.txt"), **other)
    assert view.ports["0:3:3"].type == "free"
    assert not is_free_fc_port(view, "0:3:3") and not is_free_fc_port(view, "1:3:4")
    assert is_free_fc_port(view, "0:3:2")
    if reads == "showhost":
        assert {"10.132.30.136", "an unnamed initiator 10005CBA2CFF6BD0"} <= set(view.logins["0:3:3"])
    else:
        assert view.exports["0:3:3"] == ["zz_t2_vol01", "zz_t2_vol02", "zz_t2_vol03"]


def test_a_failed_over_partner_or_a_prohibited_mode_change_is_no_candidate():
    """The Primera's free 0:3:1 and 0:3:3 have partners that took over their paths. No FC port on rack13
    is `prohibited`, so that case is a model input on top of the capture."""
    from alletra_onboard.application.provisioning.peer_ports import (
        build_view,
        free_fc_ports,
        is_free_fc_port,
    )

    assert free_fc_ports(build_view(_text(PRIMERA_SHOWPORT))) == ["0:3:2", "0:3:4", "1:3:2", "1:3:4"]
    view = _rack13_now()
    view.mode_change["0:3:3"] = "prohibited"
    assert not is_free_fc_port(view, "0:3:3")


def test_wsapi_and_the_cli_read_every_rack13_port_alike():
    """GET /ports mapped to the CLI's words equals `showport` and `showport -par`, all 28 ports
    (mode 2 target / 3 initiator / 4 peer; type 1 host / 2 disk / 3 free / -1 cluster; connectionMode
    1 disk / 2 host; connectionType 2 point / 99 eth; linkState 12 link_idle_for_reset)."""
    import json

    from alletra_onboard.adapters.array.wsapi_client import parse_port_states
    from alletra_onboard.application.provisioning.peer_ports import (
        parse_showport_par,
        parse_showport_ports,
    )

    states, params = parse_port_states(json.loads(_text(RACK13 / "wsapi_ports.json")))
    assert states == parse_showport_ports(_text(RACK13 / "showport.txt"))
    assert params == parse_showport_par(_text(RACK13 / "showport_par.txt"))
    assert len(states) == 28 and states["0:3:3"].type == "free" and states["0:3:4"].type == "host"


def test_wsapi_reads_an_fc_peer_port_like_showport():
    """E18U31, OS 10.5.60, WSAPI 1.15.60 (2026-11-17): an FC peer port is mode 3 (initiator), type 6
    (peer), connectionMode 4 (peer), connectionType 2 (point). python-3parclient's type 6 is confirmed."""
    import json

    from alletra_onboard.adapters.array.wsapi_client import parse_port_states
    from alletra_onboard.application.provisioning.peer_ports import parse_showport_ports

    body = json.loads(_text(E18U31_WSAPI_PORTS))
    states, params = parse_port_states(body)
    assert states["0:3:2"] == parse_showport_ports(_text(E18U31_SHOWPORT))["0:3:2"]     # 2026-10-07
    now = parse_showport_ports(_text(E18U31 / "showport.txt"))                          # same moment
    assert states["0:3:2"] == now["0:3:2"] and states["1:3:2"] == now["1:3:2"]
    assert params["0:3:2"].connmode == "peer"
    assert (params["1:3:2"].connmode, params["1:3:2"].conntype) == ("peer", "point")
    raw = next(m for m in body["members"] if m["portPos"] == {"node": 0, "slot": 3, "cardPort": 2})
    assert (raw["mode"], raw["type"], raw["connectionMode"], raw["connectionType"]) == (3, 6, 4, 2)


@pytest.mark.parametrize("folder, left_out", [
    (E18U31, ["0:4:3", "0:4:4", "1:4:3", "1:4:4"]),                     # IP, mode peer, Type free
    (D22U27, ["0:4:1", "0:4:2", "0:4:4", "1:4:1", "1:4:2", "1:4:4"]),   # IP, Type file or free
    (VZ, []),
], ids=["E18U31", "D22U27", "VZ"])
def test_wsapi_and_the_cli_read_the_10_5_arrays_alike(folder, left_out):
    """2026-11-17: every port GET /ports lists equals `showport`, and its params `showport -par`, on
    OS 10.5.60, 10.5.0 and 10.5.51. Type 7 is `rcip` (D22U27, VZ). On 10.5 GET /ports leaves out the IP
    ports of Type free or file (rack13 on 10.6.0 lists them): a WSAPI read is not the full port list."""
    import json

    from alletra_onboard.adapters.array.wsapi_client import parse_port_states
    from alletra_onboard.application.provisioning.peer_ports import (
        parse_showport_par,
        parse_showport_ports,
    )

    states, params = parse_port_states(json.loads(_text(folder / "wsapi_ports.json")))
    cli = parse_showport_ports(_text(folder / "showport.txt"))
    assert sorted(set(cli) - set(states)) == left_out and set(states) <= set(cli)
    assert {n: cli[n] for n in states} == states
    assert params == parse_showport_par(_text(folder / "showport_par.txt"))
    assert all(cli[n].protocol == "IP" and cli[n].type in ("free", "file") for n in left_out)


class _ReadCli:
    """Serves a capture folder (rack13 unless told) by command, through the read client's own
    allowlist check."""

    def __init__(self, fail: str = "", answer: dict[str, str] | None = None, folder: Path = RACK13) -> None:
        self.sent: list[str] = []
        self.fail, self.answer, self.folder = fail, answer or {}, folder

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        assert refusal(command) is None, command
        self.sent.append(command)
        if command == self.fail:
            raise RuntimeError("channel closed")
        if command in self.answer:
            return self.answer[command]
        return _text(self.folder / (command.replace(" -", "_").replace(" ", "_") + ".txt"))


def _creds():
    from pydantic import SecretStr

    from alletra_onboard.domain.shared import EndpointCreds

    return EndpointCreds(host=A_HOST, username="3paradm", password=SecretStr("pw"))


def test_read_view_reads_rack13_with_show_commands_only():
    from alletra_onboard.application.provisioning.peer_ports import READS, read_view

    cli = _ReadCli()
    view = read_view(_creds(), array_cli_factory=lambda c: cli)
    assert cli.sent == list(READS) and not view.read_error
    assert view.host == A_HOST
    assert view.model_copy(update={"host": ""}) == _rack13_now()


@pytest.mark.parametrize("fail, answer, why", [
    ("showhost -d", None, "channel closed"),
    ("", {"showvlun -a": "Error: busy\n"}, "'showvlun -a' answered: Error: busy"),
])
def test_a_failed_required_read_leaves_no_half_view(fail, answer, why):
    """Without the logins or the exports a busy port would look free."""
    from alletra_onboard.application.provisioning.peer_ports import read_view

    view = read_view(_creds(), array_cli_factory=lambda c: _ReadCli(fail, answer))
    assert why in view.read_error and not view.ports


def test_an_optional_read_that_fails_is_left_out():
    from alletra_onboard.application.provisioning.peer_ports import read_view

    view = read_view(_creds(), array_cli_factory=lambda c: _ReadCli("showport -peer", {"showport -c": "Error: x"}))
    assert not view.read_error and view.mode_change == {} and len(view.params) == 20


# ------------------------------------------------------------------ R3: the plan

def _rack13_view():
    from alletra_onboard.application.provisioning.peer_ports import build_view

    # The plan tests keep the 2026-11-03 showport and the 2026-09-13 logins, the days 0:3:3 served a host.
    # `showport -par` is from 2026-11-16 (rack13's first): host/point on every slot-3 FC port.
    return build_view(_text(RACK13_SHOWPORT), showhost_d=_text(RACK13_SHOWHOST), showvlun_a=_text(RACK13_SHOWVLUN),
                      showport_par=_text(RACK13 / "showport_par.txt"))


def _intent(*nsps):
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    return PeerPortIntent(ports=[PeerPortRequest(nsp=n) for n in nsps])


def _by_port(plan):
    return {a.nsp: a for a in plan.actions}


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


def test_a_port_that_serves_hosts_is_a_conflict_named_by_its_host():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:3:3", "1:3:2"), _rack13_view()))["0:3:3"]
    assert act.state == "conflict" and not act.commands
    assert "serves hosts" in act.reason and "10.132.30.136" in act.reason


def test_an_ip_port_is_not_a_peer_port_candidate():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:4:3", "1:3:2"), _rack13_view()))["0:4:3"]
    assert act.state == "conflict" and "is not a Fibre Channel port" in act.reason


def test_a_port_not_on_the_array_is_a_conflict():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:9:1", "1:3:2"), _rack13_view()))["0:9:1"]
    assert act.state == "conflict" and "is not on this array" in act.reason


def test_a_peer_label_on_a_host_port_never_makes_it_a_peer_port():
    """D22U27 1:3:2 is labelled `Peer_port`, Type host, with a login (LESSONS 42): a conflict, and with
    0:3:2 the only candidate the plan has one node and blocks."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    view = build_view(_text(D22U27_SHOWPORT), showhost_d=_text(D22U27_SHOWHOST))
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    act = _by_port(plan)["1:3:2"]
    assert act.state == "conflict" and "serves hosts" in act.reason and "1000040973C52799" in act.reason
    assert any("pairs across nodes" in b for b in plan.blockers)


def test_ports_already_in_peer_mode_exist_and_need_nothing():
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(E18U31_SHOWPORT)))
    assert [a.state for a in plan.actions] == ["exists", "exists"]
    assert not plan.blockers and not any(a.commands for a in plan.actions)


def test_a_persistent_port_partner_that_failed_over_is_a_conflict():
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    act = _by_port(plan_peer_ports(_intent("0:3:1", "1:3:4"), build_view(_text(PRIMERA_SHOWPORT))))["0:3:1"]
    assert act.state == "conflict" and "failover partner of 1:3:1" in act.reason


def test_a_create_without_the_previous_connection_mode_is_blocked():
    """No `showport -par` read means no removal set; the plan must not offer a change it cannot undo."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(RACK13_SHOWPORT)))
    assert any("showport -par" in b for b in plan.blockers)


def test_a_free_port_still_in_an_effective_zone_gets_a_note_and_without_a_switch_read_the_note_says_so():
    """rack13 on 2026-11-16: 0:3:3 and 1:3:4 are free, ready and linked, the live run's candidates. The F2
    switch's effective configuration (`rack13_fabric/F2_cfgshow.txt`, training fabric 2026-09-12) still
    zoned both to hosts then. The array cannot see zones; only the switch read can say so."""
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports
    from alletra_onboard.application.provisioning.zoning import parse_active_zones

    zones, _cfg = parse_active_zones(_text(FIX / "rack13_fabric" / "F2_cfgshow.txt"))
    plan = plan_peer_ports(_intent("0:3:3", "1:3:4"), _rack13_now(), zones={"the F2 switch": zones})
    assert [a.state for a in plan.actions] == ["create", "create"] and not plan.blockers
    note = next(n for n in plan.notes if n.startswith("0:3:3 (20330002AC02D495) is still in zones "))
    assert "arcus__windows137_zone1" in note and "Vmware_Alletra" in note and note.endswith(
        "on the F2 switch: a host that is switched off may use this port. Ask the SAN team before setting it.")
    assert any(n.startswith("1:3:4 (21340002AC02D495) is still in zones ") for n in plan.notes)
    assert not any("one fabric" in n or "both on the" in n for n in plan.notes)      # 3 odd, 4 even: two fabrics

    unchecked = plan_peer_ports(_intent("0:3:3", "1:3:4"), _rack13_now())
    assert "The zones on 0:3:3's WWPN were not checked (no switch read): ask the SAN team before setting it." in unchecked.notes


def test_two_peer_ports_on_one_fabric_by_port_number_is_a_note_not_a_blocker():
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), _rack13_now())
    assert not plan.blockers
    assert ("0:3:2 and 1:3:2 are both on the even fabric (F2) by port number; a fabric failure stops the migration."
            in plan.notes)


def test_the_printed_command_set_and_removal_set_before_the_paste():
    """R4/R5, first slice: the commands in sheet order, and the undo, last port first, before any paste."""
    from alletra_onboard.application.provisioning.peer_ports import (
        command_set_text,
        plan_peer_ports,
        planned_removals,
        removal_set_text,
    )

    plan = plan_peer_ports(_intent("0:3:3", "1:3:4"), _rack13_now())
    assert command_set_text(plan, "rack13-ARCUS").splitlines()[1:] == [
        "# 0:3:3", "controlport offline 0:3:3", "controlport config peer -ct point -f 0:3:3",
        "# 1:3:4", "controlport offline 1:3:4", "controlport config peer -ct point -f 1:3:4"]
    assert planned_removals(plan) == [
        "controlport offline 1:3:4", "controlport config host -ct point -f 1:3:4", "controlport rst 1:3:4",
        "controlport offline 0:3:3", "controlport config host -ct point -f 0:3:3", "controlport rst 0:3:3"]
    assert removal_set_text(planned_removals(plan), "rack13-ARCUS").startswith(
        "# Undo the peer ports this run set on rack13-ARCUS. Remove the SAN team's peer-port zones")


# ------------------------------------------------------------------ R4/R5: read after the paste, apply, removal set

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


def test_the_read_after_the_paste_finds_the_peer_ports_and_keeps_their_undo():
    """First slice (ADR 0018 accepted, write deferred): a consultant pastes the printed command set; the
    tool reads the array again and judges it as the apply will judge its read-back. Each restore ends
    with `rst`, so a port left offline comes back (ADR 0018 *Risks*)."""
    from alletra_onboard.application.provisioning.peer_ports import (
        plan_peer_ports,
        read_back_peer_ports,
    )

    view = _rack13_view()
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    result = read_back_peer_ports(plan, before=view, after=_after(view, "0:3:2", "1:3:2"))
    assert result.error is None and result.changed == ["0:3:2", "1:3:2"]
    assert result.removals == [
        "controlport offline 1:3:2", "controlport config host -ct point -f 1:3:2", "controlport rst 1:3:2",
        "controlport offline 0:3:2", "controlport config host -ct point -f 0:3:2", "controlport rst 0:3:2",
    ]


def test_the_read_after_a_paste_that_stopped_after_offline_gives_rst_only_and_says_so():
    """R5: 1:3:4 was taken offline, its `config` never landed: it is held offline in its old mode, and
    only `controlport rst` brings it back (the help's way). A read with nothing changed is no paste."""
    from alletra_onboard.application.provisioning.peer_ports import (
        changed_since,
        plan_peer_ports,
        read_back_peer_ports,
    )

    view = _rack13_now()
    plan = plan_peer_ports(_intent("0:3:3", "1:3:4"), view)
    assert not changed_since(plan, view, view.model_copy(deep=True))
    after = _after(view, "0:3:3")
    after.ports["1:3:4"] = after.ports["1:3:4"].model_copy(update={"state": "offline"})
    assert changed_since(plan, view, after)
    result = read_back_peer_ports(plan, before=view, after=after)
    assert result.changed == ["0:3:3"]
    assert result.error == "1:3:4 did not come back as a peer port (Type free, state offline)."
    assert result.removals == ["controlport rst 1:3:4", "controlport offline 0:3:3",
                               "controlport config host -ct point -f 0:3:3", "controlport rst 0:3:3"]
    assert result.sentences[0] == "0:3:3 is now a peer port (port WWPN 20330002AC02D495)."


def test_the_read_after_the_paste_names_another_port_that_changed():
    from alletra_onboard.application.provisioning.peer_ports import (
        plan_peer_ports,
        read_back_peer_ports,
    )

    view = _rack13_now()
    plan = plan_peer_ports(_intent("0:3:3", "1:3:4"), view)
    after = _after(view, "0:3:3", "1:3:4")
    after.ports["0:3:4"] = after.ports["0:3:4"].model_copy(update={"mode": "initiator"})
    result = read_back_peer_ports(plan, before=view, after=after)
    assert result.changed == ["0:3:3", "1:3:4"]
    assert result.error == "0:3:4 changed as well (mode target, now initiator): check the array before going on."


def test_verify_says_a_peer_port_without_a_link_needs_its_cable():
    from alletra_onboard.application.provisioning.peer_ports import verify_peer_ports

    view = _after(_rack13_now(), "0:3:2", "1:3:2")
    view.ports["0:3:2"] = view.ports["0:3:2"].model_copy(update={"state": "loss_sync"})
    checks = verify_peer_ports(_intent("0:3:2", "1:3:2"), view)
    assert [(c.ok, c.sentence) for c in checks] == [
        (False, "0:3:2 is a peer port but its link is loss_sync: check the cable and the switch port."),
        (True, "1:3:2 is a peer port, link ready.")]


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


# ------------------------------------------------------------------ ADR 0018: the array-port client (deferred)

APPROVED = {("0:3:2", "peer"), ("1:3:2", "peer")}


@NOT_BUILT
@pytest.mark.parametrize("command, allowed", [
    ("controlport offline 0:3:2", True),
    ("controlport config peer -ct point -f 0:3:2", True),
    ("controlport rst 0:3:2", True),
    ("controlport offline 0:3:3", False),                          # not an approved port
    ("controlport config host -ct point -f 0:3:2", False),         # restores are pasted, never run
    ("controlport config rcfc -ct point -f 0:3:2", False),         # approved for peer, not rcfc
    ("controlport config peer -virt_ports 8 0:3:2", False),
    ("controlport config peer -ct point -f 0:3:2 1:3:2", False),   # one port per command
    ("controlport rst -m initiator 0:3:2", False),
    ("controlport offline 0:3:2; showport", False),
    ("controlport offline {0:3:2}", False),                        # Tcl quoting (ADR 0025 condition 1)
    ("controlport rcip addr -f 10.0.0.1 255.255.255.0 0:4:4", False),
])
def test_the_port_client_runs_only_the_approved_mode_on_approved_ports(command, allowed):
    """The array-port client of ADR 0025 condition 7 is built from the plan's (port, mode) pairs. Its mode
    family is `peer` or `rcfc`; `config rcfc` comes with ADR 0024 part B and its own live capture."""
    from alletra_onboard.adapters.array.port_cli_client import port_write_refusal

    assert (port_write_refusal(command, approved=APPROVED) is None) is allowed


# ------------------------------------------------------------------ R6: verify

def test_verify_reads_e18u31_peer_ports_as_ready():
    from alletra_onboard.application.provisioning.peer_ports import build_view, verify_peer_ports

    checks = verify_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(E18U31_SHOWPORT)))
    assert all(c.ok for c in checks)
    assert checks[0].sentence == "0:3:2 is a peer port, link ready."


def test_verify_says_a_free_port_is_not_a_peer_port():
    from alletra_onboard.application.provisioning.peer_ports import build_view, verify_peer_ports

    checks = verify_peer_ports(_intent("0:3:2", "1:3:2"), build_view(_text(RACK13_SHOWPORT)))
    assert not checks[0].ok and checks[0].sentence == "0:3:2 is not a peer port (Type free)."


def _service_run(tmp_path, rows, steps=("ports", "verify")):
    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.application.platform import init_sheet
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.application.service import OnboardingService
    from alletra_onboard.config import Settings
    from alletra_onboard.domain.models import RunMode

    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D3209YV", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[], peer_ports=rows)
    parsed = init_sheet.parse_workbook_bytes(data, mode=RunMode.CUSTOM, selected_steps=list(steps))
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(parsed.work_item, mode=RunMode.CUSTOM, selected_steps=list(steps),
                             provisioning_intent=parsed.provisioning_intent)
    return service, run


async def test_the_verify_step_reads_the_planned_peer_ports_read_only(tmp_path):
    from alletra_onboard.application.provisioning.peer_ports import read_view
    from alletra_onboard.domain.models import VerificationReport

    service, run = _service_run(tmp_path, ROWS)
    service.documents._verify_fn = lambda item, username, password: VerificationReport(reachable=True)
    service.documents._read_peer_ports = lambda creds: read_view(creds, array_cli_factory=lambda c: _ReadCli(folder=E18U31))
    service.start_verify(run.run_id)
    await service.wait(run.run_id)
    event = next(e for e in service.list_events(run.run_id) if e.event_type == "verify.completed")
    assert event.message.endswith("Peer ports: 2 of 2 ready.")
    assert [c["sentence"] for c in event.data["report"]["peer_ports"]] == [
        "0:3:2 is a peer port, link ready.", "1:3:2 is a peer port, link ready."]

    service.documents._read_peer_ports = lambda creds: read_view(
        creds, array_cli_factory=lambda c: _ReadCli("showhost -d", folder=E18U31))
    service.start_verify(run.run_id)
    await service.wait(run.run_id)
    event = [e for e in service.list_events(run.run_id) if e.event_type == "verify.completed"][-1]
    assert "channel closed" in event.data["report"]["peer_ports_error"]


async def test_the_array_ports_step_plans_the_peer_ports_then_judges_the_read_after_the_paste(tmp_path, monkeypatch):
    """R4/R8, first slice, through the step service: a read and a plan with the commands and their undo;
    the consultant pastes; the next read is judged against the read the plan was made from, and the zoning
    plan then takes the peer WWPNs from it."""
    import json

    from alletra_onboard.application.provisioning import peer_ports
    from alletra_onboard.application.provisioning.steps import ACTIVE_ZONES_ARTIFACT
    from alletra_onboard.domain.models import RunStatus

    before = _rack13_now()
    reads = iter([before, _after(before, "0:3:2", "1:3:2")])
    monkeypatch.setattr(peer_ports, "read_view", lambda creds: next(reads))
    service, run = _service_run(tmp_path, ROWS)
    service.store.save_artifact(run.run_id, ACTIVE_ZONES_ARTIFACT,
                                json.dumps({"the F2 switch sw-f2": {"old_zone": ["20320002AC02D495"]}}).encode())

    service.start_ports_preview(run.run_id)
    await service.wait(run.run_id)
    (event,) = [e for e in service.list_events(run.run_id) if e.event_type == "ports.previewed"]
    assert event.message == "Read 10.132.30.121: plan ready, peer ports: 2 to set, 0 already peer, 0 conflict(s)."
    peer = event.data["peer"]
    assert [a["state"] for a in peer["plan"]["actions"]] == ["create", "create"] and peer["result"] is None
    assert peer["removals"][:2] == ["controlport offline 1:3:2", "controlport config host -ct point -f 1:3:2"]
    assert "0:3:2 (20320002AC02D495) is still in zone old_zone on the F2 switch sw-f2" in " ".join(peer["plan"]["notes"])
    assert event.data["iscsi"] is None and service.get_ports(run.run_id)["peer_plan_held"] is True
    assert service.get_run(run.run_id).status == RunStatus.WAITING_FOR_OPERATOR

    service.start_ports_preview(run.run_id)                # the consultant pasted; read the array again
    await service.wait(run.run_id)
    (done,) = [e for e in service.list_events(run.run_id) if e.event_type == "ports.completed"]
    assert done.message == "Read 10.132.30.121: all 2 peer port(s) the sheet asks for are in peer mode."
    result = done.data["peer"]["result"]
    assert result["changed"] == ["0:3:2", "1:3:2"] and result["error"] is None
    assert result["sentences"][0] == "0:3:2 is now a peer port (port WWPN 20320002AC02D495)."
    pairs, nsps = service.discovery_zoning._peer_zone_input(run.run_id, service.get_provisioning_intent(run.run_id))
    assert pairs == [("20320002AC02D495", "20310002AC02AC38"), ("21320002AC02D495", "21310002AC02AC38")]
    assert nsps == {"20320002AC02D495": "0:3:2", "21320002AC02D495": "1:3:2"}


async def test_after_a_partial_paste_each_port_keeps_its_undo_from_the_read_that_first_planned_it(tmp_path, monkeypatch):
    """The first paste sets 0:3:2 only; the second sets 1:3:2. Every later read is judged against the
    first read that planned each port, so 0:3:2's restore never drops out of the removal set."""
    from alletra_onboard.application.provisioning import peer_ports

    before = _rack13_now()
    reads = iter([before, _after(before, "0:3:2"), _after(before, "0:3:2", "1:3:2"), _after(before, "0:3:2", "1:3:2")])
    monkeypatch.setattr(peer_ports, "read_view", lambda creds: next(reads))
    service, run = _service_run(tmp_path, ROWS)
    results = []
    for _ in range(4):
        service.start_ports_preview(run.run_id)
        await service.wait(run.run_id)
        last = [e for e in service.list_events(run.run_id) if e.event_type.startswith("ports.")][-1]
        results.append(last.data["peer"]["result"])
    assert results[0] is None
    assert results[1]["changed"] == ["0:3:2"] and "1:3:2 did not come back as a peer port" in results[1]["error"]
    both = ["controlport offline 1:3:2", "controlport config host -ct point -f 1:3:2", "controlport rst 1:3:2",
            "controlport offline 0:3:2", "controlport config host -ct point -f 0:3:2", "controlport rst 0:3:2"]
    for result in results[2:]:                              # the read after the second paste, and a second look
        assert result["changed"] == ["0:3:2", "1:3:2"] and result["error"] is None and result["removals"] == both


def test_a_switch_the_zoning_plan_could_not_read_leaves_its_zones_unchecked(tmp_path):
    """A failed switch read is not a checked one: with no switch read the note says so, and with one switch
    read the other switch's zones are named as not checked."""
    import json

    from alletra_onboard.application.provisioning import zoning_plan as zp
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports
    from alletra_onboard.application.provisioning.steps import (
        ACTIVE_ZONES_ARTIFACT,
        ArrayPortsSteps,
    )
    from alletra_onboard.domain.discovery import DiscoveryReport
    from alletra_onboard.domain.provisioning import ProvisioningIntent
    from alletra_onboard.domain.shared import EndpointCreds

    def refuse(creds):
        raise ConnectionError("no route")

    creds = {k: EndpointCreds(host=k, username="u", password="p") for k in ("array", "vc", "sw-f1", "sw-f2")}
    prov = ProvisioningIntent(array=creds["array"], vcenter=creds["vc"], switch_f1=creds["sw-f1"], switch_f2=creds["sw-f2"])
    plan = zp.build_zoning_plan(prov, DiscoveryReport(), brocade_factory=refuse)
    assert plan.active_zones == {"the F1 switch sw-f1": None, "the F2 switch sw-f2": None}

    service, run = _service_run(tmp_path, ROWS)
    steps: ArrayPortsSteps = service.ports
    service.store.save_artifact(run.run_id, ACTIVE_ZONES_ARTIFACT, json.dumps(plan.active_zones).encode())
    assert steps._active_zones(run.run_id) is None
    zones = {"the F1 switch sw-f1": None, "the F2 switch sw-f2": {"z": {"20330002AC02D495"}}}
    notes = plan_peer_ports(_intent("0:3:3", "1:3:4"), _rack13_now(), zones=zones).notes
    assert ("The zones on 1:3:4's WWPN were not checked on the F1 switch sw-f1 (it could not be read): ask the SAN "
            "team before setting it.") in notes
    assert any(n.startswith("0:3:3 (20330002AC02D495) is still in zone z on the F2 switch sw-f2") for n in notes)


async def test_a_failed_peer_port_read_plans_nothing(tmp_path, monkeypatch):
    from alletra_onboard.application.provisioning import peer_ports
    from alletra_onboard.domain.peer_ports import PeerPortView

    monkeypatch.setattr(peer_ports, "read_view",
                        lambda creds: PeerPortView(host=creds.host, read_error=f"Could not read {creds.host}: timed out"))
    service, run = _service_run(tmp_path, ROWS)
    service.start_ports_preview(run.run_id)
    await service.wait(run.run_id)
    (event,) = [e for e in service.list_events(run.run_id) if e.event_type == "ports.preview.failed"]
    assert event.message == ("Could not read 10.132.30.121: timed out. Nothing was planned for the peer ports. "
                             "Read the array again.")
    assert "plan" not in event.data["peer"] and service.get_ports(run.run_id)["peer_plan_held"] is False


# ------------------------------------------------------------------ R7: zoning

def test_peer_zones_use_the_wwpn_read_after_the_change():
    """E18U31's peer ports carry 2032 0202… where its host ports carry 2031 0002…; the zone takes the
    port WWN from the view it is given (the read-back), never from the read before the apply."""
    from alletra_onboard.application.provisioning.peer_ports import build_view, peer_zone_pairs
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest

    intent = PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:2", source_wwpns=["20310002AC02AC38"]),
                                   PeerPortRequest(nsp="1:3:2", source_wwpns=["21310002AC02AC38"])])
    pairs = peer_zone_pairs(intent, build_view(_text(E18U31_SHOWPORT)))
    assert pairs == [("20320202AC02DEF2", "20310002AC02AC38"), ("21320202AC02DEF2", "21310002AC02AC38")]


# The source array behind E18U31's peer ports (showportdev_ns_032/132.txt, 2026-11-17): an HPE 3PAR 20850,
# serial 4UW0002142, its 0:3:2 and 1:3:2 in host mode. The switch answers below are written for the test,
# in the layout of tests/unit/test_zoning_plan.py; the WWPNs are the arrays' own.
_SRC_032, _SRC_132 = "20320002AC07E528", "21320002AC07E528"


def _ns_entry(wwpn: str, kind: str, symb: str) -> str:
    colons = ":".join(wwpn[i:i + 2] for i in range(0, 16, 2)).lower()
    return f""" N    020{wwpn[2]}00;   3;{colons};2f:f7:00:02:ac:07:e5:28; 0x0
    PortSymb: [10] "{symb}"
    Device type: Physical {kind}
"""


class _Switch:
    def __init__(self, ns: str, alis: str, cfg: str):
        self.ns, self.alis, self.cfg = ns, alis, cfg

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def nsshow(self):
        return self.ns

    def nscamshow(self):
        return ""

    def alishow(self):
        return self.alis

    def cfgshow(self):
        return self.cfg


def _peer_zoning_plan():
    from alletra_onboard.application.provisioning import zoning_plan as zp
    from alletra_onboard.application.provisioning.peer_ports import build_view, peer_zone_pairs
    from alletra_onboard.domain.discovery import ArrayPort, DiscoveryReport
    from alletra_onboard.domain.peer_ports import PeerPortIntent, PeerPortRequest
    from alletra_onboard.domain.provisioning import ProvisioningIntent
    from alletra_onboard.domain.shared import EndpointCreds

    view = build_view(_text(E18U31 / "showport.txt"))
    intent = PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:2", source_wwpns=[_SRC_032]),
                                   PeerPortRequest(nsp="1:3:2", source_wwpns=[_SRC_132])])
    pairs = peer_zone_pairs(intent, view)
    nsps = {view.ports[n].port_wwn: n for n in ("0:3:2", "1:3:2")}
    f2_ns = (_ns_entry("20340002AC02DEF2", "Target", "CZ2D3209YV - 0:3:4 - x")
             + _ns_entry("20320202AC02DEF2", "Initiator", "peer") + _ns_entry("21320202AC02DEF2", "Initiator", "peer")
             + _ns_entry(_SRC_032, "Target", "4UW0002142 - 0:3:2 - HPE") + _ns_entry(_SRC_132, "Target", "4UW0002142 - 1:3:2 - HPE"))
    switches = {"sw-f1": _Switch("", "", "Effective configuration:\n cfg:\tF1_CFG\n"),
                "sw-f2": _Switch(f2_ns, " alias:\tsrc3par_032\n\t\t20:32:00:02:ac:07:e5:28\n",
                                 "Effective configuration:\n cfg:\tF2_CFG\n")}
    creds = {k: EndpointCreds(host=k, username="u", password="p") for k in ("array", "vc", "sw-f1", "sw-f2")}
    prov = ProvisioningIntent(array=creds["array"], vcenter=creds["vc"], switch_f1=creds["sw-f1"], switch_f2=creds["sw-f2"])
    discovery = DiscoveryReport(array_ports=[
        ArrayPort(node=0, slot=3, card_port=4, protocol="fc", wwpn="20340002AC02DEF2", link_state="ready")])
    return zp.build_zoning_plan(prov, discovery, brocade_factory=lambda c: switches[c.host],
                                peer_pairs=pairs, peer_nsps=nsps)


def test_the_zoning_plan_drafts_the_peer_block_on_the_fabric_where_both_ports_are():
    plan = _peer_zoning_plan()
    f1, f2 = plan.fabrics
    assert f1.peer_pairs == [] and f2.peer_pairs == [("20320202AC02DEF2", _SRC_032), ("21320202AC02DEF2", _SRC_132)]
    assert [(p.nsp, p.proposed_alias) for p in f2.peer_ports] == [
        ("0:3:2", "CZ2D3209YV_N0S3P2_PEER"), ("1:3:2", "CZ2D3209YV_N1S3P2_PEER")]
    assert [(s.suggested_alias, s.proposed_alias) for s in f2.sources] == [("src3par_032", ""), ("", "array_4UW0002142_N1S3P2")]   # FOS: a name starts with a letter
    assert "active_zones" not in plan.model_dump(mode="json")          # kept off the event payload


def test_the_peer_block_renders_zones_named_by_the_peer_alias_and_the_source_alias():
    """The command set for the SAN team; `cfgenable` is a line of its own as for the host zones (ADR 0012)."""
    from alletra_onboard.application.provisioning.zoning_plan import render_peer_commands

    plan = _peer_zoning_plan()
    aliases = {w.wwpn: w.suggested_alias or w.proposed_alias for f in plan.fabrics for w in f.peer_ports + f.sources}
    commands, skipped = render_peer_commands(plan, aliases)
    assert skipped == {"F2": []} and "F1" not in commands
    zones = [c for c in commands["F2"] if c.startswith("zonecreate")]
    assert zones == [
        'zonecreate "CZ2D3209YV_N0S3P2_PEER_src3par_032","CZ2D3209YV_N0S3P2_PEER;src3par_032"',
        'zonecreate "CZ2D3209YV_N1S3P2_PEER_array_4UW0002142_N1S3P2","CZ2D3209YV_N1S3P2_PEER;array_4UW0002142_N1S3P2"',
    ]
    assert 'alicreate "src3par_032","20:32:00:02:ac:07:e5:28"' not in commands["F2"]     # the switch has it
    assert commands["F2"][0] == "cfgtransshow" and commands["F2"][-1] == "cfgenable F2_CFG"


# ------------------------------------------------------------------ R9: the as-built

def test_the_as_built_documents_the_peer_ports_how_they_were_set_their_zones_and_their_undo(tmp_path):
    """Built from model objects: the plan and the read after the paste on rack13's 0:3:2 and 1:3:2, and the
    array read when the document is made from E18U31's own reads (2026-11-17, its peer ports 0:3:2, 1:3:2)."""
    import docx
    from docx.oxml.ns import qn

    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt
    from alletra_onboard.application.provisioning.peer_ports import (
        plan_peer_ports,
        read_back_peer_ports,
    )

    view = _rack13_now()
    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), view)
    result = read_back_peer_ports(plan, before=view, after=_after(view, "0:3:2", "1:3:2"))
    data = AsBuiltData(
        name="DHCI_B10K", showport=_text(E18U31 / "showport.txt"), showport_par=_text(E18U31_SHOWPORT_PAR),
        showport_peer=_text(E18U31_SHOWPORT_PEER),
        peer_ports_rows=[{"nsp": "0:3:2", "source_wwpns": [_SRC_032]}, {"nsp": "1:3:2", "source_wwpns": [_SRC_132]}],
        peer_ports_plan=plan.model_dump(mode="json"), peer_ports_result=result.model_dump(mode="json"),
        zoning_rendered={"peer_commands": {"F2": ['zonecreate "a_PEER_b","a_PEER;b"', "cfgenable F2_CFG"]}},
    )
    out, warnings = generate_asbuilt(data, tmp_path / "asbuilt.docx")
    doc = docx.Document(str(out))
    text = "".join(t.text or "" for t in doc.element.body.iter(qn("w:t")))
    assert "Peer ports" in [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
    table = next([[c.text.strip() for c in r.cells] for r in t.rows] for t in doc.tables
                 if [c.text.strip() for c in t.rows[0].cells][:3] == ["Port", "Type", "Connection"])
    assert table[1] == ["0:3:2", "peer", "peer, point", "ready", "2FF70202AC02DEF2", "20320202AC02DEF2", _SRC_032]
    assert "controlport config peer -ct point -f 0:3:2" in text and "a consultant pasted them" in text
    assert 'zonecreate "a_PEER_b","a_PEER;b"' in text and "cfgenable F2_CFG" in text
    assert "controlport config host -ct point -f 1:3:2" in text
    assert not [w for w in warnings if "Peer ports" in w]


def test_the_as_built_says_printed_not_pasted_when_no_read_saw_a_port_change(tmp_path):
    import docx
    from docx.oxml.ns import qn

    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt
    from alletra_onboard.application.provisioning.peer_ports import plan_peer_ports

    plan = plan_peer_ports(_intent("0:3:2", "1:3:2"), _rack13_now())
    data = AsBuiltData(name="rack13-ARCUS", showport=_text(RACK13 / "showport.txt"), showport_par=_text(RACK13 / "showport_par.txt"),
                       peer_ports_rows=[{"nsp": "0:3:2"}, {"nsp": "1:3:2"}], peer_ports_plan=plan.model_dump(mode="json"))
    out, _ = generate_asbuilt(data, tmp_path / "asbuilt.docx")
    text = "".join(t.text or "" for t in docx.Document(str(out)).element.body.iter(qn("w:t")))
    assert "for a consultant to paste; no port change was seen on the array in this run." in text
    assert "a consultant pasted them" not in text


def test_the_run_records_keep_the_last_plan_that_set_ports_and_the_last_read_after_the_paste():
    from types import SimpleNamespace

    from alletra_onboard.application.documents import steps as st
    from alletra_onboard.application.documents.asbuilt import AsBuiltData

    setting = {"actions": [{"nsp": "0:3:2", "state": "create", "commands": ["controlport offline 0:3:2"]}]}
    done = {"actions": [{"nsp": "0:3:2", "state": "exists"}]}
    result = {"changed": ["0:3:2"], "removals": ["controlport rst 0:3:2"], "error": None, "sentences": []}
    events = [SimpleNamespace(event_type="ports.previewed", data={"peer": {"plan": setting}}, created_at="t1"),
              SimpleNamespace(event_type="ports.completed", data={"peer": {"plan": done, "result": result}}, created_at="t2")]
    data = AsBuiltData()
    coord = SimpleNamespace(list_events=lambda run_id: events, list_commands=lambda run_id, since=0: [])
    st.DocumentSteps(coord=coord)._run_records("r1", data)
    assert data.peer_ports_plan == setting and data.peer_ports_result == result
    assert ("showport_peer", "showport -peer") in st.DocumentSteps._ASBUILT_LISTINGS


def test_the_as_built_has_no_peer_ports_section_without_the_tab(tmp_path):
    import docx

    from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt

    out, _ = generate_asbuilt(AsBuiltData(name="x", showport=_text(E18U31 / "showport.txt")), tmp_path / "a.docx")
    assert "Peer ports" not in [p.text for p in docx.Document(str(out)).paragraphs if p.style.name == "Heading 1"]


# ------------------------------------------------------------------ R8: the step

def test_peer_ports_are_a_section_of_the_shared_array_ports_step():
    """SPEC-024 (BL-25) proposes the `ports` step; peer ports add a section to it, not a step of their own."""
    from alletra_onboard.domain.workflow import STEP_REGISTRY

    keys = [s.key for s in STEP_REGISTRY]
    assert keys.index("discover") < keys.index("ports") < keys.index("zoning")
    assert next(s for s in STEP_REGISTRY if s.key == "ports").kind == "provision"
    assert "peer_ports" not in keys
