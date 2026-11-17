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


@NOT_BUILT
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
