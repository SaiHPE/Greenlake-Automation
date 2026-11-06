"""SPEC-021 — RCIP ports and the partnership set up by the tool. Plan and apply are pinned to the lab
pair as it was before the manual setup on 2026-11-03 (tests/fixtures/rcip_pair/before/) and to the
answers that setup got (tests/fixtures/rcip_pair/rcip_setup_commands_2026-11-03.log)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import SecretStr

from alletra_onboard.application.platform import init_sheet
from alletra_onboard.application.replication import partnership
from alletra_onboard.application.replication.plan import build_plan, check
from alletra_onboard.application.replication.read import parse_showport_roles, read_array
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.replication import ProtectionRequest, RcipPortRequest, ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "rcip_pair"
A_HOST, B_HOST = "10.132.30.121", "10.132.30.28"
LIVE = (FIX / "rcip_setup_commands_2026-11-03.log").read_text(encoding="utf-8")


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


class _ReadCli:
    """Serves the before-captures by command; what was not captured reads as empty."""

    def __init__(self, array: str, overrides: dict[str, str] | None = None) -> None:
        self.array, self.overrides = array, overrides or {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def run(self, command: str, timeout=None) -> str:
        if command in self.overrides:
            return self.overrides[command]
        path = FIX / "before" / self.array / (command.replace(" -", "_").replace(" ", "_") + ".txt")
        return path.read_text(encoding="utf-8") if path.exists() else ""


def _views(a_over=None, b_over=None):
    a = read_array(_creds(A_HOST), array_cli_factory=lambda c: _ReadCli("alletra", a_over))
    b = read_array(_creds(B_HOST), array_cli_factory=lambda c: _ReadCli("primera", b_over))
    return a, b


NETWORK = [
    RcipPortRequest(side="A", nsp="0:4:4", ip="10.93.18.11", netmask="255.255.254.0"),
    RcipPortRequest(side="A", nsp="1:4:4", ip="10.93.18.13", netmask="255.255.254.0"),
    RcipPortRequest(side="B", nsp="0:1:1", ip="10.93.18.19", netmask="255.255.254.0"),
    RcipPortRequest(side="B", nsp="1:1:1", ip="10.93.18.20", netmask="255.255.254.0"),
]


def _intent(network=None) -> ReplicationIntent:
    return ReplicationIntent(peer=_creds(B_HOST), failover_test=False, network=NETWORK if network is None else network,
                             protections=[ProtectionRequest(vvset="zz_rc_vvs", peer_cpg="SSD_r6", mode="sync", rpo_minutes=None)])


def _prov(intent: ReplicationIntent) -> ProvisioningIntent:
    return ProvisioningIntent(array=_creds(A_HOST), vcenter=_creds("vc"), switch_f1=_creds(""), switch_f2=_creds(""),
                              replication=intent)


# ------------------------------------------------------------------ R2: the read

def test_showport_roles_read_both_arrays_as_they_were():
    a_roles, a_wwn = parse_showport_roles((FIX / "before" / "alletra" / "showport.txt").read_text())
    b_roles, b_wwn = parse_showport_roles((FIX / "before" / "primera" / "showport.txt").read_text())
    assert a_wwn == "2FF70002AC02D495" and b_wwn == "2FF70002AC02AC38"
    assert a_roles["0:4:4"].rcip_capable and a_roles["1:4:4"].rcip_capable           # peer offline free IP
    assert not a_roles["0:4:1"].rcip_capable and a_roles["0:4:1"].protocol == "iSCSI"  # live hosts on it
    assert b_roles["0:1:1"].rcip_capable and b_roles["0:1:1"].type == "rcip"            # Primera: the 10-column form


# ------------------------------------------------------------------ R3: the plan

def _plan(network=None, a_over=None, b_over=None):
    a, b = _views(a_over, b_over)
    intent = _intent(network)
    return build_plan(check(a, b, intent), intent, _prov(intent))


def _by(plan):
    return {(x.kind, x.where, x.name): x for x in plan.actions}


def test_the_lab_pair_plans_two_addresses_remote_copy_and_two_targets_and_no_group():
    plan = _plan()
    by = _by(plan)
    assert [(k, w, n, x.state) for (k, w, n), x in by.items()] == [
        ("rcip_port", "A", "0:4:4", "create"), ("rcip_port", "A", "1:4:4", "create"),
        ("rcip_port", "B", "0:1:1", "exists"), ("rcip_port", "B", "1:1:1", "exists"),
        ("rc_service", "A", "Remote Copy", "create"), ("rc_service", "B", "Remote Copy", "exists"),
        ("target", "A", "PRIMERA630R11U22", "create"), ("target", "B", "rack13-ARCUS", "create"),
    ]
    calls = [c.cli for c in sorted((c for x in plan.actions for c in x.calls), key=lambda c: c.seq)]
    # exactly what the manual setup ran (rcip_setup_commands_2026-11-03.log), in the same order
    assert calls == [
        "controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4",
        "controlport rcip addr -f 10.93.18.13 255.255.254.0 1:4:4",
        "startrcopy",
        "creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20",
        "creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13",
    ]
    for cli in calls:
        assert f"$ {cli}\n" in LIVE
    assert plan.sets_up_partnership and not [x for x in plan.actions if x.kind == "group"]
    assert any("Remote Copy groups are planned after it" in n for n in plan.notes)
    assert not any("No Remote Copy partnership" in b for b in plan.blockers)
    assert not any("Remote Copy is not started" in b for b in plan.blockers)


def test_the_primeras_old_fc_target_for_the_alletra_blocks_the_plan():
    plan = _plan()
    stale = [b for b in plan.blockers if "over Fibre Channel" in b]
    assert stale == [(
        "PRIMERA630R11U22 already has target 'rack13-ARCUS_PRIMERA' for rack13-ARCUS over Fibre Channel (status failed). "
        "The arrays keep one partnership per pair, so an IP target beside it does not work. Remove it on "
        "PRIMERA630R11U22 first: `removercopytarget -cleargroups -f rack13-ARCUS_PRIMERA` (this also removes the groups "
        "on that target; their volumes stay). Save `showrcopy -d groups` before."
    )]


def _without_fc_target():
    text = (FIX / "before" / "primera" / "showrcopy.txt").read_text()
    lines = [ln for ln in text.splitlines() if "rack13-ARCUS_PRIMERA" not in ln]
    return {"showrcopy": "\n".join(lines) + "\n"}


# The run's volume set, made on the Alletra before the run (lab/rcip_pair_lab.py does the same).
WITH_SET = {"showvvset": "Id Name Members\n 90 zz_rc_vvs zz_rc_vol01\n"}


def test_once_the_fc_target_is_gone_the_plan_has_no_blocker():
    plan = _plan(a_over=WITH_SET, b_over=_without_fc_target())
    assert plan.blockers == [] and plan.sets_up_partnership


def test_mixed_sync_and_async_rows_are_refused_before_the_partnership_is_set_up():
    """The partnership the tool sets up has one target, and a target carries one mode: refuse at the
    first read, before any write, not after the ports and targets exist."""
    a, b = _views(WITH_SET, _without_fc_target())
    intent = _intent()
    intent.protections.append(ProtectionRequest(vvset="zz_rc_vvs2", peer_cpg="SSD_r6", mode="async", rpo_minutes=10))
    plan = build_plan(check(a, b, intent), intent, _prov(intent))
    assert [x for x in plan.blockers if "mixes sync and async rows" in x] == [(
        "The Replication tab mixes sync and async rows, and the partnership the tool sets up between rack13-ARCUS and "
        "PRIMERA630R11U22 has one target; every group on one target must replicate in the same mode (HPE Support "
        "Matrix). Make all rows one mode, or set up a second target over spare RCIP ports on the arrays first.")]


def test_the_primeras_showsys_with_its_clusterled_column_gives_its_name():
    _a, b = _views()
    assert (b.name, b.serial, b.system_id) == ("PRIMERA630R11U22", "SGH339NK4C", 0x2AC38)


def test_a_live_iscsi_port_on_the_sheet_is_a_conflict_never_a_role_change():
    network = [RcipPortRequest(side="A", nsp="0:4:1", ip="10.93.18.14", netmask="255.255.254.0"), *NETWORK]
    plan = _plan(network, b_over=_without_fc_target())
    port = _by(plan)[("rcip_port", "A", "0:4:1")]
    assert port.state == "conflict" and port.calls == []
    assert port.reason == ("rack13-ARCUS 0:4:1 is not a free replication port: showport lists it as target ready host "
                           "iSCSI. The tool never changes a port's role.")
    assert port.reason in plan.blockers


def test_an_address_already_on_the_port_is_kept_and_a_different_one_is_a_conflict():
    network = [*NETWORK[:3], RcipPortRequest(side="B", nsp="1:1:1", ip="10.93.18.29", netmask="255.255.254.0")]
    port = _by(_plan(network, b_over=_without_fc_target()))[("rcip_port", "B", "1:1:1")]
    assert port.state == "conflict" and "already has RCIP address 10.93.18.20 255.255.254.0" in port.reason


def test_after_the_setup_the_partnership_reads_as_existing_and_the_groups_are_planned():
    """The arrays as the manual setup left them (same commands the tool sends): every partnership row
    'exists', and the plan goes on to the groups as SPEC-016 plans them."""
    after_a = {
        "showrcopy": "\nRemote Copy System Information\nStatus: Started, Normal\n\nTarget Information\n\n"
                     "Name             ID Type Status Options Policy\nPRIMERA630R11U22  1 IP   ready  -       mirror_config\n\n"
                     "Link Information\n\nTarget           Node  Address     Status Options\n"
                     "PRIMERA630R11U22 0:4:4 10.93.18.19 Up     -\nPRIMERA630R11U22 1:4:4 10.93.18.20 Up     -\n"
                     "receive          0:4:4 10.93.18.11 Up     -\nreceive          1:4:4 10.93.18.13 Up     -\n",
        "showport -rcip": "N:S:P State ---HwAddr--- IPAddr Netmask/PrefixLen Gateway MTU Rate Duplex AutoNeg\n"
                          "0:4:4 ready 40A6B7D7D1EB 10.93.18.11 255.255.254.0 - 1500 10Gbps Full Yes\n"
                          "1:4:4 ready 40A6B7D7C5C3 10.93.18.13 255.255.254.0 - 1500 10Gbps Full Yes\n",
        "showvvset": "Id Name Members\n 90 zz_rc_vvs zz_rc_vol01\n",
    }
    after_b = {
        "showrcopy": "\nRemote Copy System Information\nStatus: Started, Normal\n\nTarget Information\n\n"
                     "Name                 ID Type Status Options          Policy\n"
                     "rack13-ARCUS         29 IP   ready  -                mirror_config\n\n"
                     "Link Information\n\nTarget               Node  Address          Status Options\n"
                     "rack13-ARCUS         0:1:1 10.93.18.11      Up     -\nrack13-ARCUS         1:1:1 10.93.18.13      Up     -\n"
                     "receive              0:1:1 10.93.18.19      Up     -\nreceive              1:1:1 10.93.18.20      Up     -\n",
    }
    plan = _plan(a_over=after_a, b_over=after_b)
    by = _by(plan)
    assert all(x.state == "exists" for x in plan.actions if x.kind in ("rcip_port", "rc_service", "target"))
    assert not plan.sets_up_partnership
    assert by[("group", "A", "zz_rc_vvs_rcg")].state == "create"
    assert plan.blockers == []


# ------------------------------------------------------------------ R4/R5: apply and its removal set

class _RcCli:
    """The two arrays as the apply sees them, answering as they did live on 2026-11-03."""

    def __init__(self, side: str, state: dict, log: list, *, ping_loss: bool = False, refuse: str = "",
                 gw_ignored: bool = False) -> None:
        self.side, self.state, self.log, self.ping_loss, self.refuse, self.gw_ignored = side, state, log, ping_loss, refuse, gw_ignored

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def write(self, command: str) -> str:
        self.log.append((self.side, command))
        s = self.state[self.side]
        if self.refuse and command.startswith(self.refuse):
            return "Error: simulated refusal\n"
        p = command.split()
        if command.startswith("controlport rcip addr"):
            s["rcip"][p[-1]] = (p[-3], p[-2])
            return "Remote Copy interface change successful.\n"
        if command.startswith("controlport rcip gw"):
            if not self.gw_ignored:
                s.setdefault("gw", {})[p[-1]] = p[-2]
            return "Remote Copy interface change successful.\n"
        if command.startswith("controlport rcip ping"):
            return ("3 packets transmitted, 0 received, +1 errors, 100% packet loss, time 2075ms\n" if self.ping_loss
                    else "3 packets transmitted, 3 received, 0% packet loss, time 2035ms\n")
        if command == "startrcopy":
            s["rc"] = "Started"
            return "\n"
        if command.startswith("creatercopytarget"):
            s["targets"][p[1]] = [lk.rsplit(":", 1) for lk in p[3:]]
            return "\n"
        raise AssertionError(command)

    def run(self, command: str, timeout=None) -> str:
        s = self.state[self.side]
        if command == "showport -rcip":
            return "N:S:P State HwAddr IPAddr Netmask Gateway MTU Rate\n" + "".join(
                f"{n} ready 00 {ip} {mask} {s.get('gw', {}).get(n, '-')} 1500 10Gbps\n" for n, (ip, mask) in s["rcip"].items())
        if command in ("showrcopy", "showrcopy targets", "showrcopy links"):
            if not s["rc"]:
                return "Remote Copy is not configured on this system.\n"
            text = f"\nRemote Copy System Information\nStatus: {s['rc']}, Normal\n\nTarget Information\n\nName ID Type Status Options Policy\n"
            text += "".join(f"{t} 1 IP ready - mirror_config\n" for t in s["targets"])
            text += "\nLink Information\n\nTarget Node Address Status Options\n"
            text += "".join(f"{t} {nsp} {addr} Up -\n" for t, links in s["targets"].items() for nsp, addr in links)
            return text
        raise AssertionError(command)


def _apply(plan, **kw):
    state = {"A": {"rcip": {}, "rc": "", "targets": {}},
             "B": {"rcip": {"0:1:1": ("10.93.18.19", "255.255.254.0"), "1:1:1": ("10.93.18.20", "255.255.254.0")},
                   "rc": "Started", "targets": {}}}
    log: list = []
    hosts = {A_HOST: "A", B_HOST: "B"}
    result = partnership.apply_partnership(
        plan, _prov(_intent()), sleep=lambda s: None,
        rc_cli_factory=lambda creds: _RcCli(hosts[creds.host], state, log, **kw))
    return result, log, state


def test_apply_sends_the_live_commands_in_order_and_the_removal_set_undoes_exactly_them():
    plan = _plan(b_over=_without_fc_target())
    result, log, _state = _apply(plan)
    assert result.error is None
    assert log == [
        ("A", "controlport rcip addr -f 10.93.18.11 255.255.254.0 0:4:4"),
        ("A", "controlport rcip addr -f 10.93.18.13 255.255.254.0 1:4:4"),
        ("A", "controlport rcip ping -c 3 10.93.18.19 0:4:4"),
        ("A", "controlport rcip ping -c 3 10.93.18.20 1:4:4"),
        ("A", "startrcopy"),
        ("A", "creatercopytarget PRIMERA630R11U22 IP 0:4:4:10.93.18.19 1:4:4:10.93.18.20"),
        ("B", "creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13"),
    ]
    assert result.removals_a == [
        "removercopytarget PRIMERA630R11U22",
        "stoprcopy -f -stopgroups -clear",                  # Remote Copy was not configured on A before
        "controlport rcip delete -f 0:4:4",
        "controlport rcip delete -f 1:4:4",
    ]
    assert result.removals_b == ["removercopytarget rack13-ARCUS"]   # the Primera's ports and Remote Copy were there
    assert [o.kind for o in result.outcomes] == ["rcip_port", "rcip_port", "ping", "ping", "rc_service", "target", "target", "links"]


def test_a_ping_with_loss_stops_after_the_addresses_and_removes_only_them():
    plan = _plan(b_over=_without_fc_target())
    result, log, _ = _apply(plan, ping_loss=True)
    assert result.error.startswith("Stopped after 2 step(s): ping from 0:4:4 to 10.93.18.19: 3 packets transmitted, 0 received")
    assert [c for _, c in log if not c.startswith("controlport rcip")] == []
    assert result.removals_a == ["controlport rcip delete -f 0:4:4", "controlport rcip delete -f 1:4:4"]
    assert result.removals_b == []


def test_a_refused_target_stops_and_names_the_arrays_words():
    plan = _plan(b_over=_without_fc_target())
    result, _, _ = _apply(plan, refuse="creatercopytarget rack13-ARCUS")
    assert "the peer refused `creatercopytarget rack13-ARCUS IP 0:1:1:10.93.18.11 1:1:1:10.93.18.13`: Error: simulated refusal" in result.error
    assert result.removals_a[0] == "removercopytarget PRIMERA630R11U22"
    assert result.removals_b == ["removercopytarget rack13-ARCUS"]      # written before the command, in case it half-worked


# This array's ports on a /28 with the lab router as gateway, so the peer's addresses are reached through
# it (probe 2026-11-06: 10.93.18.1 forwards; a gateway that is not a router loses every ping).
ROUTED = [RcipPortRequest(side="A", nsp="0:4:4", ip="10.93.18.11", netmask="255.255.255.240", gateway="10.93.18.1"),
          RcipPortRequest(side="A", nsp="1:4:4", ip="10.93.18.13", netmask="255.255.255.240", gateway="10.93.18.1"),
          *NETWORK[2:]]


def test_a_gateway_row_is_written_after_the_address_and_read_back():
    plan = _plan(ROUTED, a_over=WITH_SET, b_over=_without_fc_target())
    assert plan.blockers == []
    assert not any("gets gateway" in n for n in plan.notes)          # the peer is off this array's subnet: no warning
    result, log, state = _apply(plan)
    assert result.error is None
    assert [c for side, c in log if side == "A"][:4] == [
        "controlport rcip addr -f 10.93.18.11 255.255.255.240 0:4:4", "controlport rcip gw -f 10.93.18.1 0:4:4",
        "controlport rcip addr -f 10.93.18.13 255.255.255.240 1:4:4", "controlport rcip gw -f 10.93.18.1 1:4:4"]
    assert result.outcomes[0].detail == "10.93.18.11 255.255.255.240, gateway 10.93.18.1, ready"
    assert state["A"]["gw"] == {"0:4:4": "10.93.18.1", "1:4:4": "10.93.18.1"}
    assert "controlport rcip delete -f 0:4:4" in result.removals_a          # the delete takes the gateway with it


def test_a_gateway_the_array_did_not_take_stops_before_the_ping():
    plan = _plan(ROUTED, a_over=WITH_SET, b_over=_without_fc_target())
    result, log, _ = _apply(plan, gw_ignored=True)
    assert "after setting it, showport -rcip shows gateway none on 0:4:4, not 10.93.18.1" in result.error
    assert not any("ping" in c for _, c in log)
    assert result.removals_a == ["controlport rcip delete -f 0:4:4"]


# ------------------------------------------------------------------ R1: the sheet

def _sheet(network_rows):
    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D2K014S", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[],
        replication={"fields": {"peer_host": B_HOST, "peer_user": "3paradm", "peer_password": "pw"},
                     "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}], "network": network_rows})
    return init_sheet.parse_workbook_bytes(data, mode=RunMode.CUSTOM, selected_steps=["replicate"]).provisioning_intent.replication


ROWS = [{"array": "this", "port": "0:4:4", "ip": "10.93.18.11", "netmask": "255.255.254.0"},
        {"array": "this", "port": "1:4:4", "ip": "10.93.18.13", "netmask": "255.255.254.0"},
        {"array": "peer", "port": "0:1:1", "ip": "10.93.18.19", "netmask": "255.255.254.0"},
        {"array": "peer", "port": "1:1:1", "ip": "10.93.18.20", "netmask": "255.255.254.0"}]


def test_the_network_tab_parses_into_the_intent():
    assert _sheet(ROWS).network == NETWORK
    assert _sheet([]).network == []


@pytest.mark.parametrize("rows, why", [
    ([{**ROWS[0], "array": "primary"}, *ROWS[1:]], "Array must be 'this' or 'peer'"),
    ([{**ROWS[0], "port": "0-4-4"}, *ROWS[1:]], "Port must be N:S:P"),
    ([{**ROWS[0], "port": "00:04:04"}, *ROWS[1:]], "Port must be N:S:P"),
    ([{**ROWS[0], "ip": "10.93.18.300"}, *ROWS[1:]], "is not an IPv4 address"),
    ([{**ROWS[0], "netmask": "255.0.255.0"}, *ROWS[1:]], "is not a netmask"),
    ([{**ROWS[0], "netmask": "0.0.0.255"}, *ROWS[1:]], "is not a netmask"),           # a host mask
    ([{**ROWS[0], "netmask": "0"}, *ROWS[1:]], "is not a netmask"),
    ([*ROWS, {**ROWS[0], "ip": "10.93.18.12"}], "port 0:4:4 is named twice"),
    ([*ROWS[:3], {**ROWS[3], "ip": "10.93.18.11"}], "address 10.93.18.11 is used twice"),
    ([ROWS[0], ROWS[1], ROWS[2]], "no partner on the other array's same node: this 1:4:4"),
    ([ROWS[0], ROWS[2]], "needs at least 2 links"),
])
def test_a_wrong_network_row_is_refused_with_a_sentence(rows, why):
    with pytest.raises(ValueError, match=re.escape(why)):
        _sheet(rows)


def test_a_port_excel_turned_into_a_time_reads_back_as_n_s_p():
    """Excel stores 0:4:4 typed in a General cell as a time; the template's Port column is text, and an
    older or retyped sheet's time cells are read back as the port."""
    import datetime
    import io

    from openpyxl import load_workbook

    data = init_sheet.compose_workbook_bytes(
        base=None, init={"serial_number": "CZ2D2K014S", "mgmt_ipv4": A_HOST},
        targets={"prov_array_host": A_HOST, "prov_array_user": "3paradm", "prov_array_password": "pw",
                 "prov_vcenter_host": "vc", "prov_vcenter_user": "u", "prov_vcenter_password": "p"},
        volumes=[], hostsets=[], hosts=[],
        replication={"fields": {"peer_host": B_HOST, "peer_user": "3paradm", "peer_password": "pw"},
                     "rows": [{"vvset": "zz_rc_vvs", "peer_cpg": "SSD_r6", "mode": "sync"}], "network": ROWS})
    wb = load_workbook(io.BytesIO(data))
    ws = wb[init_sheet.REPLICATION_NETWORK_SHEET_NAME]
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and re.fullmatch(r"\d:\d:\d", cell.value):
                n, s, p = (int(x) for x in cell.value.split(":"))
                cell.value = datetime.time(n, s, p)
    out = io.BytesIO()
    wb.save(out)
    intent = init_sheet.parse_workbook_bytes(out.getvalue(), mode=RunMode.CUSTOM, selected_steps=["replicate"])
    assert intent.provisioning_intent.replication.network == NETWORK


def test_the_template_keeps_the_port_column_as_text():
    import io

    from openpyxl import load_workbook

    ws = load_workbook(io.BytesIO(init_sheet.build_template_bytes()))[init_sheet.REPLICATION_NETWORK_SHEET_NAME]
    header = next(r for r in ws.iter_rows() if any(c.value == "Port (N:S:P) *" for c in r))
    assert ws.cell(row=header[0].row + 1, column=2).number_format == "@"


def test_one_pair_is_a_blocker_in_the_plan_too():
    plan = _plan([NETWORK[0], NETWORK[2]], a_over=WITH_SET, b_over=_without_fc_target())
    assert any("needs at least 2 pairs of ports" in b for b in plan.blockers)
