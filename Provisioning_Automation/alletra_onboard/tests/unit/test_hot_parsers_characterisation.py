"""Characterisation tests for the four parser/planner/verifier hot spots (BL-65):
- application/provisioning/zoning.py: parse_active_zones, build_report
- application/replication/read.py: parse_showrcopy
- application/provisioning/iscsi_network.py: _action, plan_iscsi_vlans
- application/replication/verify.py: verify

Each group exercises real captured device output from `tests/fixtures/` plus explicit edge cases
(truncated lines, prose answers, dropped columns, empty fields, boundary values) with readable
literal assertions.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import SecretStr

from alletra_onboard.application.provisioning import iscsi_network, zoning
from alletra_onboard.application.replication import read as rc_read
from alletra_onboard.application.replication import verify as rc_verify
from alletra_onboard.domain.array_parse import parse_showport_roles
from alletra_onboard.domain.discovery import ArrayHost, ArrayPort, DiscoveryReport, HostHba
from alletra_onboard.domain.network import (
    IscsiPortAddress,
    IscsiVlanInterface,
    IscsiVlanRequest,
    PortNetworkView,
)
from alletra_onboard.domain.provisioning import (
    DeclaredHost,
    HostSetRequest,
    ProvisioningIntent,
    VolumeRequest,
)
from alletra_onboard.domain.replication import (
    PortRole,
    ProtectionRequest,
    RcGroup,
    RcGroupDetail,
    RcGroupVolume,
    RcipPort,
    RcLink,
    RcTarget,
    ReplicationAction,
    ReplicationArrayView,
    ReplicationIntent,
    ReplicationPlan,
)
from alletra_onboard.domain.shared import EndpointCreds

FIX = Path(__file__).resolve().parents[1] / "fixtures"
RACK13_FABRIC = FIX / "rack13_fabric"
VZ_FABRIC = FIX / "vz_fabric"
RC_PAIR = FIX / "rc_pair"
RCIP_PAIR = FIX / "rcip_pair"
ISCSI_VLAN = FIX / "iscsi_vlan"


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="3paradm", password=SecretStr("pw"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ================================================================== 1. zoning.parse_active_zones

def test_parse_active_zones_on_real_rack13_and_vz_captures():
    f1_zones, f1_cfg = zoning.parse_active_zones(_text(RACK13_FABRIC / "F1_cfgshow.txt"))
    assert f1_cfg == "mycfg"
    assert sorted(f1_zones) == [
        "kiranzone1", "msarep1", "msarep2", "myzone",
        "primera_vmware_1", "primera_vmware_2", "rcfc1", "rcfc2",
    ]
    assert f1_zones["kiranzone1"] == {"10005CED8C5312A9", "20340002AC02D495", "21330002AC02D495"}
    assert f1_zones["myzone"] == {
        "100008F1EAC03DF7", "10008C7CFF65F321", "20340002AC02D495", "207000C0FF1DA851",
    }

    f2_zones, f2_cfg = zoning.parse_active_zones(_text(RACK13_FABRIC / "F2_cfgshow.txt"))
    assert f2_cfg == "jul2prabhu"
    assert len(f2_zones) == 13
    assert "Zone1" not in f2_zones  # defined-only zone excluded when effective section has zones
    assert f2_zones["Vmware_Alletra"] == {"10005CED8C5312A8", "20330002AC02D495", "21340002AC02D495"}

    no_eff_zones, no_eff_cfg = zoning.parse_active_zones(
        _text(RACK13_FABRIC / "F1_cfgactvshow_no_effective_2026-09-28.txt")
    )
    assert (no_eff_zones, no_eff_cfg) == ({}, None)

    vz1_zones, vz1_cfg = zoning.parse_active_zones(_text(VZ_FABRIC / "F1_cfgactvshow.txt"))
    assert vz1_cfg == "F1_CFG" and len(vz1_zones) == 773
    assert vz1_zones["AIX_94503PAR"] == {"20310002AC07E52C", "21310002AC07E52C", "10000000C998B266"}

    vz2_zones, vz2_cfg = zoning.parse_active_zones(_text(VZ_FABRIC / "F2_cfgactvshow.txt"))
    assert vz2_cfg == "F2_CFG" and len(vz2_zones) == 604


def test_parse_active_zones_defined_fallback_aliases_and_edge_cases():
    defined_only = """
DEFINED CONFIGURATION:
 cfg:\tFIRST_CFG\tz_a
 cfg:\tSECOND_CFG\tz_b
 zone:\tz_a\tali_host; ali_arr; unknown_alias
\t\t50:00:00:00:00:00:00:01; not_a_wwpn
 alias:\tali_host
\t\t10:00:00:00:c9:00:00:01; bad_token
\t\t10:00:00:00:c9:00:00:02
 alias:\tali_arr\t20:31:00:02:ac:02:f6:29
"""
    zones, cfg = zoning.parse_active_zones(defined_only)
    assert cfg == "FIRST_CFG"  # first defined cfg wins when no effective section exists
    assert zones == {
        "z_a": {
            "10000000C9000001", "10000000C9000002",
            "20310002AC02F629", "5000000000000001",
        }
    }

    # Empty, prose, continuation before entity, and empty entity headers
    assert zoning.parse_active_zones("") == ({}, None)
    assert zoning.parse_active_zones("orphan line before any section\ncfg:\nzone:\nalias:\n") == ({"": set()}, "")

    # Effective section present with cfg name but NO effective zones falls back to defined zones,
    # while keeping effective_cfg over defined_cfg. A section header also terminates an in-progress
    # continuation so a stray WWPN after it is not appended to the previous defined zone.
    mixed = """
Defined configuration:
 cfg: DEF_CFG z1
 zone: z1 10:00:00:00:00:00:00:0a

Effective configuration:
\t\t10:00:00:00:00:00:00:ff
 cfg: EFF_CFG
"""
    assert zoning.parse_active_zones(mixed) == ({"z1": {"100000000000000A"}}, "EFF_CFG")


# ================================================================== 2. zoning.build_report

def _fc_ports() -> list[ArrayPort]:
    return [
        ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC02F629", link_state="ready", fabric="even"),
        ArrayPort(node=1, slot=3, card_port=2, protocol="fc", wwpn="21320002AC02F629", link_state="ready", fabric="even"),
    ]


def _prov_intent(*, declared=None, host_sets=None) -> ProvisioningIntent:
    return ProvisioningIntent(
        array=_creds("10.0.0.5"), vcenter=_creds("vc"),
        switch_f1=_creds("sw-f1"), switch_f2=_creds("sw-f2"),
        declared_hosts=declared or [],
        host_sets=host_sets or [],
    )


def test_build_report_without_fc_ports_handles_iscsi_only_and_fc_error():
    iqn = "iqn.1994-05.com.redhat:node1"
    iscsi_host = DeclaredHost(name="lin1", os="linux", iqn=iqn)
    disc_logged = DiscoveryReport(
        array_ports=[],
        array_hosts=[ArrayHost(name="lin1", persona="Generic-ALUA", iqns={iqn: ["0:4:1", "1:4:1"]})],
    )
    ok = zoning.build_report(_prov_intent(declared=[iscsi_host]), disc_logged)
    assert ok.error is None and ok.proper is True
    assert ok.iscsi_hosts == {"lin1": ["0:4:1", "1:4:1"]}
    assert ok.zoned_hosts == ["lin1"]
    assert ok.notes == ["lin1: iSCSI, logged in on 0:4:1, 1:4:1 — no zoning needed; exports allowed."]

    disc_missing = DiscoveryReport(array_ports=[], array_hosts=[])
    waiting = zoning.build_report(_prov_intent(declared=[iscsi_host]), disc_missing)
    assert waiting.error is None and waiting.proper is False
    assert waiting.iscsi_hosts == {"lin1": []}
    assert waiting.notes == ["lin1: iSCSI, IQN not logged in on the array — exports to it are held back."]

    # No FC ports and no iSCSI hosts -> error
    empty = zoning.build_report(_prov_intent(), disc_missing)
    assert empty.proper is False
    assert empty.error is not None and "no array FC target ports" in empty.error

    # Both FC and iSCSI hosts with no FC ports -> iSCSI still judged, error still set
    both_intent = _prov_intent(declared=[
        iscsi_host,
        DeclaredHost(name="fc1", os="linux", wwpns=["1000000000000001"]),
    ])
    both = zoning.build_report(both_intent, disc_logged)
    assert both.error is not None and both.proper is False and both.iscsi_hosts == {"lin1": ["0:4:1", "1:4:1"]}


def test_build_report_array_only_fallback_and_unclaimed_logins():
    # No vCenter, no declared hosts, no zoning plan: falls back to named array hosts logged in on FC ports.
    disc = DiscoveryReport(
        array_ports=_fc_ports(),
        array_hosts=[
            ArrayHost(name="", wwpns={"1000000000000099": ["0:3:1"]}),  # unclaimed -> skipped by fallback
            ArrayHost(name="offline_h", wwpns={"1000000000000088": []}),  # not logged in -> skipped
            ArrayHost(name="srv.01", wwpns={"1000000000000001": ["0:3:1"], "1000000000000002": ["0:3:2"]}),
        ],
    )
    report = zoning.build_report(_prov_intent(), disc)
    assert report.proper is True
    assert report.zoned_hosts == ["srv.01"]
    assert [(z.name, z.fabric, z.present, z.host_wwpn) for z in report.expected] == [
        ("srv_01_odd", "odd", True, "1000000000000001"),
        ("srv_01_even", "even", True, "1000000000000002"),
    ]
    assert report.notes == ["No vCenter host list — verifying the hosts the array reports as logged in (showhost)."]


def test_build_report_mixed_fc_states_unclaimed_union_and_remediations():
    # Unclaimed login on array still satisfies a vCenter host's WWPN.
    # h_even_only is missing odd; h_odd_only is missing even; h_dark is unverified; h_iscsi is iSCSI.
    iqn = "iqn.1994-05.com.redhat:lin2"
    disc = DiscoveryReport(
        array_ports=_fc_ports(),
        array_hosts=[
            ArrayHost(name="", wwpns={"1000000000000001": ["0:3:1"], "1000000000000002": ["0:3:2"]}),
            ArrayHost(name="other_team", wwpns={"10000000000000AA": ["0:3:1"]}),  # not in host_set -> ignored
            ArrayHost(name="h_even_only", wwpns={"1000000000000012": ["1:3:2"]}),
            ArrayHost(name="h_odd_only", wwpns={"1000000000000021": ["1:3:1"]}),
            ArrayHost(name="lin2", iqns={iqn: ["0:4:1"]}),
        ],
        host_hbas=[
            HostHba(host_name="h_ok", wwpn="1000000000000001"),
            HostHba(host_name="h_ok", wwpn="1000000000000002"),
            HostHba(host_name="h_even_only", wwpn="1000000000000011"),
            HostHba(host_name="h_even_only", wwpn="1000000000000012"),
            HostHba(host_name="h_odd_only", wwpn="1000000000000021"),
            HostHba(host_name="h_odd_only", wwpn="1000000000000022"),
            HostHba(host_name="h_dark", wwpn="1000000000000031"),
        ],
    )
    intent = _prov_intent(
        declared=[DeclaredHost(name="lin2", os="linux", iqn=iqn)],
        host_sets=[HostSetRequest(name="hs1", members=["h_ok"])],
    )
    report = zoning.build_report(intent, disc)
    assert report.proper is False
    assert report.zoned_hosts == ["h_ok", "lin2"]
    assert report.unverified_hosts == ["h_dark"]
    assert "other_team" not in {z.name.rsplit("_", 1)[0] for z in report.expected}
    assert "h_even_only: zoned on one fabric only — missing odd/F1." in report.notes
    assert "h_odd_only: zoned on one fabric only — missing even/F2." in report.notes
    assert [(r.fabric, r.switch_host, len(r.commands)) for r in report.remediations] == [
        ("odd", "sw-f1", 4),
        ("even", "sw-f2", 4),
    ]
    assert report.remediations[0].commands == [
        'zonecreate "h_even_only_629","10:00:00:00:00:00:00:11;20:31:00:02:ac:02:f6:29"',
        'zonecreate "h_even_only_629","10:00:00:00:00:00:00:11;21:31:00:02:ac:02:f6:29"',
        'cfgadd "<active_cfg>","h_even_only_629;h_even_only_629"',
        'cfgenable "<active_cfg>"',
    ]


def test_build_report_deduplicates_sorted_array_ports_and_picks_first_host_wwpn():
    # Duplicate array WWPNs on odd in reverse order -> sorted & de-duplicated in ExpectedZone.array_wwpn.
    # Two logged-in host WWPNs on odd -> lexicographically first WWPN chosen for ExpectedZone.host_wwpn.
    ports = [
        ArrayPort(node=1, slot=3, card_port=1, protocol="fc", wwpn="21310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=2, slot=3, card_port=1, protocol="fc", wwpn="20310002AC02F629", link_state="ready", fabric="odd"),
        ArrayPort(node=0, slot=3, card_port=2, protocol="fc", wwpn="20320002AC02F629", link_state="ready", fabric="even"),
    ]
    disc = DiscoveryReport(
        array_ports=ports,
        array_hosts=[
            ArrayHost(name="h1", wwpns={
                "100000000000000B": ["0:3:1"],
                "100000000000000A": ["1:3:1"],
                "100000000000000C": ["0:3:2"],
            }),
        ],
        host_hbas=[
            HostHba(host_name="h1", wwpn="100000000000000B"),
            HostHba(host_name="h1", wwpn="100000000000000A"),
            HostHba(host_name="h1", wwpn="100000000000000C"),
        ],
    )
    report = zoning.build_report(_prov_intent(), disc)
    odd = next(z for z in report.expected if z.fabric == "odd")
    assert odd.host_wwpn == "100000000000000A"
    assert odd.array_wwpn == "20310002AC02F629, 21310002AC02F629"


# ================================================================== 3. replication/read.parse_showrcopy

def test_parse_showrcopy_on_real_primera_vz_and_unconfigured_captures():
    # Prose answer on unconfigured array
    assert rc_read.parse_showrcopy(_text(RCIP_PAIR / "before" / "alletra" / "showrcopy.txt")) == {
        "status": "", "health": "", "targets": [], "links": [], "groups": [],
    }

    # Primera capture with failed FC target, Down outbound / Up inbound links, 5 Stopped Sync groups
    prim = rc_read.parse_showrcopy(_text(RCIP_PAIR / "before" / "primera" / "showrcopy.txt"))
    assert (prim["status"], prim["health"]) == ("Started", "Normal")
    assert prim["targets"] == [
        RcTarget(name="rack13-ARCUS_PRIMERA", id=28, type="FC", status="failed",
                 options="2FF70002AC02D495", policy="mirror_config"),
    ]
    assert len(prim["links"]) == 4
    assert [l.status for l in prim["links"]] == ["Down", "Down", "Up", "Up"]
    assert [g.name for g in prim["groups"]] == [
        "Mike1_vv", "NVMe_VV.r185493", "Rudiyanto_vv.r185493",
        "Sync_Repl_VV.r185493", "testfailvv.r185493",
    ]
    assert prim["groups"][1].volumes == [
        RcGroupVolume(local_name="NVMe_VV.0.r", local_id=51807, remote_name="NVMe_VV.0",
                      remote_id=1083, sync_status="Stopped", last_sync="2026-10-19 08:09:50 IST"),
        RcGroupVolume(local_name="NVMe_VV.1.r", local_id=51806, remote_name="NVMe_VV.1",
                      remote_id=1084, sync_status="Stopped", last_sync="2026-10-19 08:09:50 IST"),
    ]

    # VZ targets and links subsets with leading comment line
    vz_t = rc_read.parse_showrcopy(_text(RC_PAIR / "second_target" / "VZ_showrcopy_targets.txt"))
    assert vz_t["targets"] == [
        RcTarget(name="MPB10K-E24U21-LZ", id=1, type="IP", status="failed", options="", policy="mirror_config"),
    ]
    vz_l = rc_read.parse_showrcopy(_text(RC_PAIR / "second_target" / "VZ_showrcopy_links.txt"))
    assert len(vz_l["links"]) == 8 and sum(1 for l in vz_l["links"] if l.inbound) == 4


def test_parse_showrcopy_edge_cases_truncated_rows_errors_and_progress():
    text = """
# comment line
Remote Copy System Information
Status: Stopped
Unrelated: ignored

Target Information
Name ID Type Status Options Policy
short 1 IP
t_four bad_id IP ready
t_five 2 FC ready -
Error: transient warning

Link Information
Target Node Address Status
short 0:4:3 10.0.0.1
t_five 0:4:3 10.0.0.1 Up -
t_four 1:4:3 10.0.0.2 Down

Group Information
orphan_before_header t_five Started Primary Sync
LocalVV ID RemoteVV ID SyncStatus LastSyncTime
orphan_vol 1 orphan_vol 2 Synced NA

Name Target Status Role Mode Options
  LocalVV ID RemoteVV ID SyncStatus LastSyncTime
  skipped_vol 1 skipped_vol 2 Synced NA

Name Target Status Role Mode Options

   
g_trunc t_five Started Primary
Name Target Status Role Mode Options
g_ok t_five Started Primary Periodic Last-Sync 2026-10-09 23:39:23 IST, Period 5m, auto_recover, , over_per_alert
  LocalVV ID RemoteVV ID SyncStatus LastSyncTime
  short_v 1 short_v 2
  v1 10 v1 20 Syncing (42%) 2026-10-09 23:40:00 IST
  v2 -- v2 xx Synced (notpct) NA

Group Information
  stray_after_second_section 1 stray 2 Synced NA
Name Target Status Role Mode Options
g_second t_five Started Primary Sync
  LocalVV ID RemoteVV ID SyncStatus LastSyncTime
  v3 30 v3 40 Synced NA
"""
    rc = rc_read.parse_showrcopy(text)
    assert (rc["status"], rc["health"]) == ("Stopped", "")
    assert rc["targets"] == [
        RcTarget(name="t_four", id=None, type="IP", status="ready", options="", policy=""),
        RcTarget(name="t_five", id=2, type="FC", status="ready", options="", policy=""),
    ]
    assert rc["links"] == [
        RcLink(target="t_five", nsp="0:4:3", address="10.0.0.1", status="Up"),
        RcLink(target="t_four", nsp="1:4:3", address="10.0.0.2", status="Down"),
    ]
    assert [g.name for g in rc["groups"]] == ["g_ok", "g_second"]
    g = rc["groups"][0]
    assert (g.name, g.period, g.last_sync, g.options) == (
        "g_ok", "5m", "2026-10-09 23:39:23 IST", ["auto_recover", "over_per_alert"],
    )
    assert g.volumes == [
        RcGroupVolume(local_name="v1", local_id=10, remote_name="v1", remote_id=20,
                      sync_status="Syncing", sync_progress="42%", last_sync="2026-10-09 23:40:00 IST"),
        RcGroupVolume(local_name="v2", local_id=None, remote_name="v2", remote_id=None,
                      sync_status="Synced", sync_progress="", last_sync="(notpct) NA"),
    ]
    assert rc["groups"][1].volumes == [
        RcGroupVolume(local_name="v3", local_id=30, remote_name="v3", remote_id=40,
                      sync_status="Synced", sync_progress="", last_sync="NA"),
    ]


# ================================================================== 4. iscsi_network.plan_iscsi_vlans & _action

def _e18_view(*, vlans=None, sessions=None, mgmt_ip="10.64.154.190", mgmt_mask="255.255.248.0") -> PortNetworkView:
    roles, _ = parse_showport_roles(_text(RC_PAIR / "E18U31" / "showport.txt"))
    # Add an offline iSCSI host port and a second node port for edge-case coverage
    roles["0:4:9"] = PortRole(nsp="0:4:9", mode="target", state="offline", type="free", protocol="iSCSI")
    iscsi = [
        IscsiPortAddress(nsp="0:4:1", ip="10.30.14.1", netmask="255.255.255.0", gateway="10.30.14.254"),
        IscsiPortAddress(nsp="0:4:2", ip="10.30.14.2", netmask="255.255.255.0", gateway="10.30.14.254", peer_enabled=True),
        IscsiPortAddress(nsp="1:4:1", ip="10.30.14.3", netmask="255.255.255.0", gateway="10.30.14.254"),
        IscsiPortAddress(nsp="0:4:9", ip="", netmask="", gateway=""),
    ]
    return PortNetworkView(
        name="AlletraMP_E18U31", mgmt_ip=mgmt_ip, mgmt_netmask=mgmt_mask,
        roles=roles, iscsi_ports=iscsi, vlans=list(vlans or []),
        other_addresses={"10.54.154.192": "RCIP port 0:4:3"},
        sessions=dict(sessions or {}),
    )


def test_plan_iscsi_vlans_rule_precedence_and_all_conflict_cases():
    existing = [
        IscsiVlanInterface(nsp="0:4:1", vlan_id=100, ip="192.0.2.10", netmask="24", gateway=""),
        IscsiVlanInterface(nsp="1:4:1", vlan_id=200, ip="198.51.100.10", netmask="255.255.255.0", gateway="198.51.100.1"),
    ]
    view = _e18_view(vlans=existing, sessions={"0:4:1": 2})
    reqs = [
        # 1. Missing port
        IscsiVlanRequest(nsp="9:9:9", vlan_id=10, ip="203.0.113.1", netmask="255.255.255.0"),
        # 2. Wrong protocol (FC)
        IscsiVlanRequest(nsp="0:3:1", vlan_id=10, ip="203.0.113.2", netmask="255.255.255.0"),
        # 3. Peer-enabled iSCSI port
        IscsiVlanRequest(nsp="0:4:2", vlan_id=10, ip="203.0.113.3", netmask="255.255.255.0"),
        # 4a. Existing VLAN matching prefix len ("24" == "255.255.255.0"), gateway unset on array
        IscsiVlanRequest(nsp="0:4:1", vlan_id=100, ip="192.0.2.10", netmask="255.255.255.0", gateway="192.0.2.1"),
        # 4b. Existing VLAN with differing gateway (both set) -> conflict, keeps switch handoff via view.vlans
        IscsiVlanRequest(nsp="1:4:1", vlan_id=200, ip="198.51.100.10", netmask="255.255.255.0", gateway="198.51.100.254"),
        # 5. IP already used on another VLAN
        IscsiVlanRequest(nsp="0:4:9", vlan_id=300, ip="192.0.2.10", netmask="255.255.255.0"),
        # 6. Network matches management subnet
        IscsiVlanRequest(nsp="0:4:9", vlan_id=301, ip="10.64.154.200", netmask="255.255.248.0"),
        # 7. Two creates on the same offline port -> offline note deduplicated once
        IscsiVlanRequest(nsp="0:4:9", vlan_id=302, ip="203.0.113.10", netmask="255.255.255.0", gateway="203.0.113.1"),
        IscsiVlanRequest(nsp="0:4:9", vlan_id=303, ip="203.0.113.130", netmask="255.255.255.128"),
    ]
    plan = iscsi_network.plan_iscsi_vlans(reqs, view)
    assert [a.state for a in plan.actions] == [
        "conflict", "conflict", "conflict", "exists", "conflict", "conflict", "conflict", "create", "create",
    ]
    assert plan.actions[3].reason == (
        "192.0.2.10 24 already set; gateway 192.0.2.1 not set yet (a change window's job)"
    )
    assert plan.actions[4].reason == (
        "AlletraMP_E18U31 1:4:1 already has VLAN 200 with 198.51.100.10 255.255.255.0 "
        "(gateway 198.51.100.1); the sheet says 198.51.100.10 255.255.255.0 "
        "(gateway 198.51.100.254). The tool never changes an address it did not set."
    )
    assert plan.actions[5].reason == "192.0.2.10 is already in use on AlletraMP_E18U31: iSCSI port 0:4:1 VLAN 100."
    assert plan.actions[6].reason == (
        "10.64.152.0/21 is already the network of management on AlletraMP_E18U31; a VLAN needs a network of its own."
    )
    assert plan.removal_lines == [
        "controliscsiport delete -vlan 303 -f 0:4:9",
        "controliscsiport delete -vlan 302 -f 0:4:9",
    ]
    assert plan.notes.count(
        "0:4:9 is offline: the address is set, but no host reaches it until the link is up."
    ) == 1
    assert plan.gateway_window == [
        "controlport offline 0:4:1",
        "controliscsiport gw 192.0.2.1 -vlan 100 -f 0:4:1",
        "controlport rst -f 0:4:1",
        "controlport offline 0:4:9",
        "controliscsiport gw 203.0.113.1 -vlan 302 -f 0:4:9",
        "controlport rst -f 0:4:9",
    ]
    assert plan.gateway_notes[1:] == [
        "0:4:1 carries 2 iSCSI sessions now (showhost -d): all of them stop while the port is offline.",
        "0:4:9: its iSCSI sessions were not read. Check `showhost -d` before the change window.",
    ]
    # Conflict port 1:4:1 keeps its switch_handoff line because view.vlans has VLAN 200 on 1:4:1;
    # conflict ports 9:9:9, 0:3:1, 0:4:2 have no existing VLANs so they do not appear.
    assert plan.switch_handoff == [
        "Switch port cabled to AlletraMP_E18U31 0:4:1: carry VLAN 100 tagged (802.1Q); keep the untagged (native) VLAN as it is.",
        "Switch port cabled to AlletraMP_E18U31 0:4:9: carry VLAN 302, 303 tagged (802.1Q); keep the untagged (native) VLAN as it is.",
        "Switch port cabled to AlletraMP_E18U31 1:4:1: carry VLAN 200 tagged (802.1Q); keep the untagged (native) VLAN as it is.",
    ]


def test_plan_iscsi_vlans_on_vz_and_tagged_captures():
    vz_roles, _ = parse_showport_roles(_text(ISCSI_VLAN / "VZ" / "showport.txt"))
    vz_view = PortNetworkView(name="MPB10K-D24U21-VZ", roles=vz_roles)
    plan = iscsi_network.plan_iscsi_vlans(
        [
            IscsiVlanRequest(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0"),
            IscsiVlanRequest(nsp="1:4:1", vlan_id=120, ip="192.0.2.12", netmask="255.255.255.0"),
        ],
        vz_view,
    )
    assert [a.state for a in plan.actions] == ["create", "create"]
    assert plan.blockers == []
    assert plan.notes == [
        "0:4:1 is offline: the address is set, but no host reaches it until the link is up.",
        "1:4:1 is offline: the address is set, but no host reaches it until the link is up.",
    ]

    # Existing VLAN whose gateway is already set to the requested gateway gets no gateway_cli.
    with_gw = _e18_view(vlans=[
        IscsiVlanInterface(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0", gateway="192.0.2.1"),
    ])
    done = iscsi_network.plan_iscsi_vlans(
        [IscsiVlanRequest(nsp="0:4:1", vlan_id=120, ip="192.0.2.11", netmask="255.255.255.0", gateway="192.0.2.1")],
        with_gw,
    )
    assert done.actions[0].state == "exists"
    assert done.actions[0].gateway_cli == ""
    assert done.actions[0].reason == "192.0.2.11 255.255.255.0 already set"
    assert done.gateway_window == [] and done.gateway_notes == []


# ================================================================== 5. replication/verify.verify

def _rc_prov(*, with_replication: bool = True) -> ProvisioningIntent:
    intent = ProvisioningIntent(
        array=_creds("10.64.122.99"), vcenter=_creds("vc"),
        switch_f1=_creds(""), switch_f2=_creds(""),
        volumes=[VolumeRequest(name="v1", size_gib=10, cpg="SSD_r6", vvset="vvs_a")],
    )
    if with_replication:
        intent.replication = ReplicationIntent(
            peer=_creds("10.64.154.190"),
            protections=[ProtectionRequest(vvset="vvs_a", peer_cpg="SSD_r6", mode="async", rpo_minutes=15)],
        )
    return intent


def test_verify_no_replication_tab_and_read_error_precedence():
    out_none = rc_verify.verify(_rc_prov(with_replication=False), ReplicationPlan())
    assert out_none.error == "this run has no Replication tab"

    a_err = ReplicationArrayView(host="a", read_error="A failed")
    b_err = ReplicationArrayView(host="b", read_error="B failed")
    reads = iter([a_err, b_err])
    out_ab = rc_verify.verify(_rc_prov(), ReplicationPlan(), read_fn=lambda c, progress=None: next(reads))
    assert out_ab.error == "A failed"

    reads2 = iter([ReplicationArrayView(host="a"), b_err])
    out_b = rc_verify.verify(_rc_prov(), ReplicationPlan(), read_fn=lambda c, progress=None: next(reads2))
    assert out_b.error == "B failed"


def test_verify_no_partnership_edge_verdicts_peer_vvset_and_rcp_notes():
    a = ReplicationArrayView(
        host="a", name="ArrA", system_id=100, rc_status="Started",
        groups=[
            RcGroup(name="g_rep", target="T1", status="Started", role="Primary", mode="Sync",
                    volumes=[RcGroupVolume(local_name="v1", remote_name="v1", sync_status="Synced", last_sync="NA")]),
            RcGroup(name="g_empty", target="T1", status="Started", role="Primary", mode="Sync", volumes=[]),
            RcGroup(name="g_notsynced", target="T1", status="Started", role="Primary", mode="Periodic",
                    volumes=[RcGroupVolume(local_name="v2", remote_name="v2", sync_status="NotSynced", last_sync="NA")]),
        ],
        vvsets={f"RCP_g{i}": [] for i in range(1, 8)},  # 7 RCP_ sets -> truncated at 6 with ellipsis
    )
    b = ReplicationArrayView(
        host="b", name="ArrB", system_id=200, rc_status="Started",
        groups=[
            RcGroup(name="g_rep.r100", target="T1", status="Started", role="Secondary", mode="Sync",
                    volumes=[RcGroupVolume(local_name="v1", remote_name="v1", sync_status="Synced", last_sync="NA")]),
            RcGroup(name="g_empty.r100", target="T1", status="Started", role="Secondary", mode="Sync", volumes=[]),
            RcGroup(name="g_notsynced.r100", target="T1", status="Started", role="Secondary", mode="Periodic",
                    volumes=[RcGroupVolume(local_name="v2", remote_name="v2", sync_status="NotSynced", last_sync="NA")]),
        ],
        vvsets={},  # missing peer_vvset for g_rep
    )
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="test_volume", name="ignored_vol", state="create"),
        ReplicationAction(kind="group", name="g_conflict", state="conflict", detail={"mode": "sync"}),
        ReplicationAction(kind="group", name="g_rep", state="exists", detail={"mode": "async", "period_seconds": 600, "peer_vvset": "missing_set"}),
        ReplicationAction(kind="group", name="g_empty", state="create", detail={"mode": "sync"}),
        ReplicationAction(kind="group", name="g_notsynced", state="create", detail={"mode": "async", "vvset": "vvs_a", "period_seconds": 300}),
        ReplicationAction(kind="group", name="g_missing_on_a", state="create", detail={"mode": "async", "period_seconds": 300}),
    ])
    detail_calls: list[list[str]] = []

    def fake_detail(_creds, names, progress=None):
        detail_calls.append(list(names))
        return (
            {
                "g_rep": RcGroupDetail(name="g_rep", mode="Sync"),
                "g_notsynced": RcGroupDetail(name="g_notsynced", mode="Periodic"),
            },
            {"g_empty": "group timeout"},
        )

    reads = iter([a, b])
    out = rc_verify.verify(_rc_prov(), plan, read_fn=lambda c, progress=None: next(reads), detail_fn=fake_detail)
    assert out.links_ok is False
    assert out.links_detail == "no partnership found between the two arrays"
    assert detail_calls == [["g_rep", "g_empty", "g_notsynced"]]
    assert [(g.group, g.verdict, g.detail) for g in out.groups] == [
        ("g_rep", "replicating",
         "Started · Primary here, Secondary on the peer · Sync · expected async · 1 volume(s) Synced · peer set missing_set missing"),
        ("g_empty", "not_replicating",
         "Started · Primary here, Secondary on the peer · Sync · volumes: none"),
        ("g_notsynced", "syncing",
         "Started · Primary here, Secondary on the peer · Periodic · initial sync in progress (0 of 1 volumes Synced)"),
        ("g_missing_on_a", "not_replicating", "not on this array"),
    ]
    assert out.groups[0].config is not None and out.groups[0].config.rpo_minutes == 20  # exists async group: 2x planned period
    assert out.groups[2].config is not None and out.groups[2].config.rpo_minutes == 15  # from intent.protections
    assert out.notes == [
        "The settings and volumes of g_empty could not be read (showrcopy -d): group timeout",
        "The array keeps its own VV set per group (RCP_g1, RCP_g2, RCP_g3, RCP_g4, RCP_g5, RCP_g6…); expected, and removed with the group.",
    ]


def test_verify_filters_partnership_to_used_targets_only():
    # Two targets in partnership: T_ok has 2/2 links Up, T_bad has 1/2 links Up.
    # When plan only uses T_ok, links_ok is True and links_detail names T_ok only.
    a = ReplicationArrayView(
        host="a", name="ArrA", system_id=1,
        rcip_ports=[
            RcipPort(nsp="0:4:3", ip="10.0.1.1"), RcipPort(nsp="1:4:3", ip="10.0.1.2"),
            RcipPort(nsp="0:4:4", ip="10.0.2.1"), RcipPort(nsp="1:4:4", ip="10.0.2.2"),
        ],
        targets=[
            RcTarget(name="T_ok", id=1, type="IP", status="ready"),
            RcTarget(name="T_bad", id=2, type="IP", status="ready"),
        ],
        links=[
            RcLink(target="T_ok", nsp="0:4:3", address="10.0.1.11", status="Up"),
            RcLink(target="T_ok", nsp="1:4:3", address="10.0.1.12", status="Up"),
            RcLink(target="T_bad", nsp="0:4:4", address="10.0.2.11", status="Up"),
            RcLink(target="T_bad", nsp="1:4:4", address="10.0.2.12", status="Down"),
        ],
    )
    b = ReplicationArrayView(
        host="b", name="ArrB", system_id=2,
        rcip_ports=[
            RcipPort(nsp="0:4:3", ip="10.0.1.11"), RcipPort(nsp="1:4:3", ip="10.0.1.12"),
            RcipPort(nsp="0:4:4", ip="10.0.2.11"), RcipPort(nsp="1:4:4", ip="10.0.2.12"),
        ],
        targets=[
            RcTarget(name="T_ok_b", id=1, type="IP", status="ready"),
            RcTarget(name="T_bad_b", id=2, type="IP", status="ready"),
        ],
        links=[
            RcLink(target="T_ok_b", nsp="0:4:3", address="10.0.1.1", status="Up"),
            RcLink(target="T_ok_b", nsp="1:4:3", address="10.0.1.2", status="Up"),
            RcLink(target="T_bad_b", nsp="0:4:4", address="10.0.2.1", status="Up"),
            RcLink(target="T_bad_b", nsp="1:4:4", address="10.0.2.2", status="Up"),
        ],
    )
    plan = ReplicationPlan(actions=[
        ReplicationAction(kind="group", name="g1", state="create", detail={"target": "T_ok", "mode": "sync"}),
    ])
    reads = iter([a, b])
    out = rc_verify.verify(_rc_prov(), plan, read_fn=lambda c, progress=None: next(reads))
    assert out.links_ok is True
    assert out.links_detail == (
        "ArrA → ArrB via 'T_ok' 2/2 links Up · ArrB → ArrA via 'T_ok_b' 2/2 links Up"
    )

    # A used target with 1/2 links Up on local side and 2/2 on peer fails the >= 2 threshold.
    plan_bad_local = ReplicationPlan(actions=[
        ReplicationAction(kind="group", name="g1", state="create", detail={"target": "T_bad", "mode": "sync"}),
    ])
    reads_bad_local = iter([a, b])
    out_bad_local = rc_verify.verify(_rc_prov(), plan_bad_local, read_fn=lambda c, progress=None: next(reads_bad_local))
    assert out_bad_local.links_ok is False
    assert out_bad_local.links_detail == (
        "ArrA → ArrB via 'T_bad' 1/2 links Up · ArrB → ArrA via 'T_bad_b' 2/2 links Up"
    )

    # Mirror: 2/2 links Up on local side and 1/2 on peer also fails the >= 2 threshold.
    b_degraded = b.model_copy(update={"links": [
        RcLink(target="T_ok_b", nsp="0:4:3", address="10.0.1.1", status="Up"),
        RcLink(target="T_ok_b", nsp="1:4:3", address="10.0.1.2", status="Down"),
    ]})
    reads_bad_peer = iter([a, b_degraded])
    out_bad_peer = rc_verify.verify(_rc_prov(), plan, read_fn=lambda c, progress=None: next(reads_bad_peer))
    assert out_bad_peer.links_ok is False
    assert out_bad_peer.links_detail == (
        "ArrA → ArrB via 'T_ok' 2/2 links Up · ArrB → ArrA via 'T_ok_b' 1/2 links Up"
    )
