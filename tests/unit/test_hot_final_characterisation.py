"""Characterisation tests for the final non-cloudinit, non-failover complexity hot spots (BL-65):
- application/documents/handover.py: parse_alerts
- application/documents/verification.py: _health_issues
- application/provisioning/path_verify.py: verify_paths, attach_esxi_view
- application/provisioning/peer_ports.py & peer_ports_read.py: plan_peer_ports, read_back_peer_ports
- application/documents/asbuilt.py & asbuilt_network.py: _fill_placeholders, generate_asbuilt,
  add_zoning_section, add_iscsi_network_section, add_peer_ports_section, _add_file_section,
  _add_failover_section

Each group pins real captured output from `tests/fixtures/` plus boundary and error cases with
readable literal assertions.
"""

from __future__ import annotations

from pathlib import Path

import docx
import pytest

from alletra_onboard.application.documents import handover
from alletra_onboard.application.documents.asbuilt import AsBuiltData, generate_asbuilt
from alletra_onboard.application.documents.verification import _health_issues
from alletra_onboard.application.provisioning import path_verify, peer_ports, peer_ports_read
from alletra_onboard.domain.discovery import EthernetPort
from alletra_onboard.domain.peer_ports import (
    PeerPortIntent,
    PeerPortRequest,
    PeerPortState,
    PeerPortView,
    PortParams,
)
from alletra_onboard.domain.provisioning import EsxiLun, VolumePath
from alletra_onboard.domain.unified_file import (
    NODE_RUNNING,
    ClientGroup,
    ClientRule,
    FileCapacity,
    FileNodeStatus,
    FileReport,
    FileService,
    FileShareRecord,
    FileSystemRecord,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures"
HANDOVER_FIX = FIX / "handover"
PEER_FIX = FIX / "peer_ports"
ISCSI_FIX = FIX / "iscsi_vlan"
RACK13_ARRAY = FIX / "rack13_array"


def _capture(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


def _read_doc(path: Path) -> tuple[docx.document.Document, list[str], dict[tuple[str, ...], list[list[str]]]]:
    doc = docx.Document(str(path))
    paras = [p.text for p in doc.paragraphs if p.text.strip()]
    tables: dict[tuple[str, ...], list[list[str]]] = {}
    for tbl in doc.tables:
        rows = [[c.text.strip() for c in r.cells] for r in tbl.rows]
        tables.setdefault(tuple(rows[0]), []).extend(rows[1:])
    return doc, paras, tables


# ================================================================== 1. handover.parse_alerts

def test_parse_alerts_on_vz_capture_and_wrapped_multiline_messages():
    vz = handover.parse_alerts(_capture(HANDOVER_FIX / "VZ" / "showalert_d.txt"))
    assert len(vz) == 31
    assert vz[0].severity == "Minor" and vz[0].component != ""

    wrapped = (
        "\n\n"
        "Id          : 101\n"
        "State       : New\n"
        "Severity    : Major\n"
        "Time        : 2026-11-16 12:00:00 IST\n"
        "Message Code: 0x0100001\n"
        "Type        : Test alert\n"
        "Message     : First line of message\n"
        "              continued on second line\n"
        "              and third line\n"
        "Repeat Count: Occurred 3 times, first at 2026-11-15 10:00:00 IST\n"
        "\n"
        "1 alert\n"
    )
    alerts = handover.parse_alerts(wrapped)
    assert alerts == [
        handover.Alert(
            id=101,
            state="New",
            severity="Major",
            time="2026-11-16 12:00:00 IST",
            message_code="0x0100001",
            type="Test alert",
            message="First line of message continued on second line and third line",
            first_time="2026-11-15 10:00:00 IST",
            occurrences=3,
        )
    ]


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("0 alerts\n", "no alert records"),
        ("   indented line before any key\n", "unexpected line"),
        ("Id : abc\nState : New\nSeverity : Major\nTime : 2026-11-16 00:00:00\nMessage : x\n", "numeric Id"),
        ("Id : 1\nState : New\nMessage : only two fields\n", "Severity, Time"),
        ("Id : 1\nState : New\nSeverity : Minor\nTime : 2026-11-16 00:00:00\nMessage : x\n\n2 alerts\n", "counts 2 alerts, 1 were read"),
        ("Error: not supported\n", "Error: not supported"),
    ],
)
def test_parse_alerts_rejects_malformed_and_mismatched_inputs(text: str, match: str):
    with pytest.raises(handover.UnreadableReport, match=match):
        handover.parse_alerts(text)


def test_parse_alerts_no_alerts_is_case_insensitive_and_accepts_missing_footer():
    assert handover.parse_alerts("  NO ALERTS  \n\n") == []
    no_footer = (
        "Id : 7\nState : New\nSeverity : Minor\n"
        "Time : 2026-11-16 01:02:03 UTC\n"
        "Message : First line\n"
        "  Nested: still part of message\n"
    )
    alerts = handover.parse_alerts(no_footer)
    assert len(alerts) == 1
    assert alerts[0].id == 7
    assert alerts[0].message == "First line Nested: still part of message"
    with pytest.raises(handover.UnreadableReport, match="unexpected line"):
        handover.parse_alerts("  IndentedKey: value before any field\n")


# ================================================================== 2. verification._health_issues

def test_health_issues_on_e18u31_and_vz_captures():
    e18 = _health_issues(_capture(HANDOVER_FIX / "E18U31" / "checkhealth_svc_detail.txt"))
    assert [(i.component, i.qty, len(i.details)) for i in e18] == [
        ("File", 4, 4),
        ("Network", 1, 2),
        ("Network", 1, 2),
        ("Port", 2, 2),
        ("Security", 1, 1),
    ]
    assert e18[0].details[0].identifier == "node:0"
    assert e18[0].details[0].resolution == "Manual"

    vz = _health_issues(_capture(HANDOVER_FIX / "VZ" / "checkhealth_svc_detail.txt"))
    assert len(vz) == 14 and sum(i.qty for i in vz) == 96
    rc_rows = [i for i in vz if i.component == "RC"]
    assert len(rc_rows) == 5 and all(len(i.details) == len(rc_rows[0].details) for i in rc_rows)


def test_health_issues_handles_edge_cases_and_malformed_lines():
    text = (
        "Checking alert\n"
        "Component ---Summary Description--- Qty\n"
        "Checking should be ignored 1\n"
        "123 numeric component ignored 2\n"
        "Short 1\n"
        "Port Bad qty notdigit\n"
        "Port Degraded SFP 2\n"
        "----------------------------------------\n"
        "  1 total 2\n"
        "Stray line between tables 99\n"
        "\n"
        "Component --Identifier-- --Detailed Description-- Resolution\n"
        "Port short\n"
        "Port three tokens\n"
        "Port port:0:1:1 SFP degraded Manual\n"
        "------------------------------------------------------------\n"
        "Port port:0:1:2 ignored after detail separator Manual\n"
    )
    issues = _health_issues(text)
    assert len(issues) == 1
    assert issues[0].component == "Port" and issues[0].summary == "Degraded SFP" and issues[0].qty == 2
    assert [(d.identifier, d.description, d.resolution) for d in issues[0].details] == [
        ("port:0:1:1", "SFP degraded", "Manual")
    ]
    assert _health_issues("Checking alert\nThe system is healthy.\n") == []


# ================================================================== 3. path_verify

def test_verify_paths_covers_iscsi_mixed_dead_vols_wwpn_alias_and_empty():
    assert path_verify.verify_paths({}, []).notes == ["No exports to verify."]

    paths = [
        # iSCSI dual-node live host
        VolumePath(lun=0, volume="v1", host="iscsi_ok", host_wwpn="iqn.1", port="0:4:1", status="active", protocol="iscsi"),
        VolumePath(lun=0, volume="v1", host="iscsi_ok", host_wwpn="iqn.1", port="1:4:1", status="nonopt", protocol="iscsi"),
        # iSCSI single-node partial host
        VolumePath(lun=0, volume="v2", host="iscsi_one", host_wwpn="iqn.2", port="0:4:1", status="active", protocol="iscsi"),
        # Mixed FC (single fabric) + iSCSI, WWPN-matched under another array host name, plus a dead volume
        VolumePath(lun=1, volume="v3", host="ARRAY_OBJ", host_wwpn="1000000000000001", port="0:3:1", status="active", protocol="fc"),
        VolumePath(lun=1, volume="v3", host="ARRAY_OBJ", host_wwpn="1000000000000001", port="0:4:1", status="active", protocol="iscsi"),
        # Non-live status ignored
        VolumePath(lun=2, volume="v4", host="off_host", host_wwpn="1000000000000002", port="0:3:2", status="standby", protocol="fc"),
    ]
    expected = {
        "iscsi_ok": {"v1"},
        "iscsi_one": {"v2"},
        "mixed_host": {"v3", "v3_dead"},
        "off_host": {"v4"},
        "empty_host": set(),
    }
    report = path_verify.verify_paths(
        expected,
        paths,
        wwpns_by_host={"mixed_host": {"1000000000000001"}},
    )
    by_host = {h.host: h for h in report.hosts}

    assert by_host["iscsi_ok"].verdict == "live"
    assert by_host["iscsi_ok"].detail == "1 LUN(s) · 1 initiator(s) · 2 path(s) per LUN · iSCSI on 0:4:1, 1:4:1 · both nodes"

    assert by_host["iscsi_one"].verdict == "partial"
    assert by_host["iscsi_one"].detail == (
        "1 LUN(s) · 1 initiator(s) · 1 path(s) per LUN · iSCSI on 0:4:1 · node 0 only — no path through the other node"
    )

    assert by_host["mixed_host"].verdict == "partial"
    assert by_host["mixed_host"].detail == (
        "1 LUN(s) · 1 HBA(s) · 2 path(s) per LUN · odd fabric only — missing the even fabric (single fabric); "
        "also iSCSI on 0:4:1; exported but no path yet: v3_dead [array host object: ARRAY_OBJ]"
    )

    assert by_host["off_host"].verdict == "no_path"
    assert by_host["off_host"].detail == (
        "0 live paths for 1 exported volume(s) — the host is off or not zoned; each activates once it is on and zoned"
    )

    assert by_host["empty_host"].verdict == "no_path"
    assert by_host["empty_host"].detail == "0 live paths, and nothing is exported to this host"


def test_attach_esxi_view_covers_not_checked_uneven_active_and_degraded_precedence():
    report = path_verify.verify_paths({"esx_empty": set(), "esx_uneven": {"v1", "v2"}, "esx_dead": {"v1"}}, [])
    luns = [
        EsxiLun(host_name="esx_uneven", naa="naa.aaaa", paths_total=4, paths_active=2, paths_dead=0, adapters=["vmhba1", "vmhba2"]),
        EsxiLun(host_name="esx_uneven", naa="naa.bbbb", paths_total=4, paths_active=4, paths_dead=0, adapters=["vmhba2"]),
        EsxiLun(host_name="esx_dead", naa="naa.aaaa", paths_total=2, paths_active=1, paths_dead=2, adapters=[]),
    ]
    path_verify.attach_esxi_view(
        report,
        {"esx_empty": set(), "esx_uneven": {"v1", "v2"}, "esx_dead": {"v1"}},
        luns,
        {"v1": "AAAA", "v2": "BBBB"},
        {"esx_empty", "esx_uneven", "esx_dead"},
    )
    by_host = {h.host: h for h in report.hosts}
    assert by_host["esx_empty"].esxi_state == "not_checked"
    assert by_host["esx_empty"].esxi_note == "ESXi view: nothing exported to this host"
    assert by_host["esx_uneven"].esxi_state == "ok"
    assert by_host["esx_uneven"].esxi_note == "ESXi sees 2 volume(s) · 2–4 active of 4 path(s) per LUN · vmhba1, vmhba2"
    assert by_host["esx_dead"].esxi_state == "degraded"
    assert by_host["esx_dead"].esxi_note == "ESXi sees 1 volume(s) · 1 active of 2 path(s) per LUN — 2 dead path(s)"


# ================================================================== 4. peer_ports

def _rack13_peer_view() -> PeerPortView:
    r = PEER_FIX / "rack13"
    return peer_ports_read.build_view(
        _capture(r / "showport.txt"),
        showhost_d=_capture(r / "showhost_d.txt"),
        showvlun_a=_capture(r / "showvlun_a.txt"),
        showport_par=_capture(r / "showport_par.txt"),
        showport_c=_capture(r / "showport_c.txt"),
        showport_peer=_capture(r / "showport_peer.txt"),
    )


def test_plan_peer_ports_notes_for_same_fabric_link_and_switch_zones():
    view = _rack13_peer_view()
    intent = PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:1"), PeerPortRequest(nsp="1:3:1")])
    zones = {
        "SW1": None,
        "SW2": {
            "z_a": {"20310002AC02D495"},
            "z_b": {"20310002AC02D495"},
            "z_c": {"21310002AC02D495"},
        },
    }
    plan = peer_ports.plan_peer_ports(intent, view, zones=zones)
    assert plan.blockers == []
    assert [a.state for a in plan.actions] == ["create", "create"]
    assert plan.notes == [
        "0:3:1 and 1:3:1 are both on the odd fabric (F1) by port number; a fabric failure stops the migration.",
        peer_ports.OFFLINE_ASKS,
        "0:3:1's link is loss_sync (no cable or no switch port): it can be set, but zones will not work until it is cabled.",
        "The zones on 0:3:1's WWPN were not checked on SW1 (it could not be read): ask the SAN team before setting it.",
        "0:3:1 (20310002AC02D495) is still in zones z_a, z_b on SW2: a host that is switched off may use this port. Ask the SAN team before setting it.",
        "1:3:1's link is loss_sync (no cable or no switch port): it can be set, but zones will not work until it is cabled.",
        "The zones on 1:3:1's WWPN were not checked on SW1 (it could not be read): ask the SAN team before setting it.",
        "1:3:1 (21310002AC02D495) is still in zone z_c on SW2: a host that is switched off may use this port. Ask the SAN team before setting it.",
    ]

    # zones=None produces no-switch-read note; single-node usable triggers pairs blocker
    one_node = peer_ports.plan_peer_ports(PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:1")]), view, zones=None)
    assert one_node.blockers == [
        (
            "Peer ports go in pairs across nodes: name at least one port on each of two nodes "
            "(got 0:3:1 only on node 0), so the migration keeps a path when a node restarts."
        ),
    ]
    assert one_node.notes == [
        peer_ports.OFFLINE_ASKS,
        "0:3:1's link is loss_sync (no cable or no switch port): it can be set, but zones will not work until it is cabled.",
        "The zones on 0:3:1's WWPN were not checked (no switch read): ask the SAN team before setting it.",
    ]


def test_plan_and_read_back_peer_ports_pin_wwpn_guard_exists_only_and_par_edges():
    # Empty port_wwn must not match even if "" appears in zone members; all-exists plan omits OFFLINE_ASKS
    empty_wwpn_view = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="target", state="ready", type="free", protocol="FC", port_wwn=""),
            "1:3:1": PeerPortState(nsp="1:3:1", mode="initiator", state="ready", type="peer", protocol="FC", port_wwn="21310002AC02D495"),
        },
        params={
            "0:3:1": PortParams(nsp="0:3:1", connmode="host", conntype="point", intcoal="enabled"),
            "1:3:1": PortParams(nsp="1:3:1", connmode="peer", conntype="point", intcoal="enabled"),
        },
    )
    mixed_plan = peer_ports.plan_peer_ports(
        PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:1"), PeerPortRequest(nsp="1:3:1")]),
        empty_wwpn_view,
        zones={"SW1": {"ghost": {""}}},
    )
    assert mixed_plan.notes == [
        "0:3:1 and 1:3:1 are both on the odd fabric (F1) by port number; a fabric failure stops the migration.",
        peer_ports.OFFLINE_ASKS,
    ]
    exists_only = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="initiator", state="ready", type="peer", protocol="FC"),
            "1:3:2": PeerPortState(nsp="1:3:2", mode="initiator", state="ready", type="peer", protocol="FC"),
        },
        params={
            "0:3:1": PortParams(nsp="0:3:1", connmode="peer", conntype="point"),
            "1:3:2": PortParams(nsp="1:3:2", connmode="peer", conntype="point"),
        },
    )
    exists_plan = peer_ports.plan_peer_ports(
        PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:1"), PeerPortRequest(nsp="1:3:2")]),
        exists_only,
        zones=None,
    )
    assert exists_plan.blockers == [] and exists_plan.notes == []

    # Peer mode with conntype="loop" fails read-back and keeps full undo; missing -par row keeps same-mode check
    after_loop = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="initiator", state="ready", type="peer", protocol="FC"),
            "1:3:1": empty_wwpn_view.ports["1:3:1"],
        },
        params={"0:3:1": PortParams(nsp="0:3:1", connmode="peer", conntype="loop")},
    )
    res_loop = peer_ports.read_back_peer_ports(mixed_plan, before=empty_wwpn_view, after=after_loop)
    assert res_loop.changed == []
    assert res_loop.sentences == ["0:3:1 did not come back as a peer port (Type peer, state ready)."]
    assert res_loop.removals == [
        "controlport offline 0:3:1",
        "controlport config host -ct point -f 0:3:1",
        "controlport rst -f 0:3:1",
        "controlport intcoal enable -f 0:3:1",
    ]
    after_no_par = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="target", state="ready", type="free", protocol="FC"),
            "1:3:1": empty_wwpn_view.ports["1:3:1"],
        },
        params={},
    )
    res_no_par = peer_ports.read_back_peer_ports(mixed_plan, before=empty_wwpn_view, after=after_no_par)
    assert res_no_par.changed == [] and res_no_par.removals == []


def test_read_back_peer_ports_covers_changed_missing_offline_mode_and_unplanned_drift():
    before = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="target", state="loss_sync", type="free", protocol="FC", port_wwn="20310002AC02D495"),
            "1:3:1": PeerPortState(nsp="1:3:1", mode="target", state="loss_sync", type="free", protocol="FC", port_wwn="21310002AC02D495"),
            "0:3:3": PeerPortState(nsp="0:3:3", mode="target", state="ready", type="host", protocol="FC"),
            "1:3:3": PeerPortState(nsp="1:3:3", mode="target", state="ready", type="host", protocol="FC"),
            "0:3:4": PeerPortState(nsp="0:3:4", mode="target", state="ready", type="host", protocol="FC"),
        },
        params={
            "0:3:1": PortParams(nsp="0:3:1", connmode="host", conntype="point", intcoal="enabled"),
            "1:3:1": PortParams(nsp="1:3:1", connmode="host", conntype="point", intcoal="enabled"),
        },
    )
    plan = peer_ports.plan_peer_ports(
        PeerPortIntent(ports=[PeerPortRequest(nsp="0:3:1"), PeerPortRequest(nsp="1:3:1")]), before
    )

    # Case A: 0:3:1 succeeded, 1:3:1 stuck offline in old mode; 0:3:3 missing, 1:3:3 mode changed, 0:3:4 type changed
    after_a = PeerPortView(
        ports={
            "0:3:1": PeerPortState(nsp="0:3:1", mode="initiator", state="ready", type="peer", protocol="FC", port_wwn="20310002AC02D495"),
            "1:3:1": PeerPortState(nsp="1:3:1", mode="target", state="offline", type="free", protocol="FC"),
            "1:3:3": PeerPortState(nsp="1:3:3", mode="initiator", state="ready", type="host", protocol="FC"),
            "0:3:4": PeerPortState(nsp="0:3:4", mode="target", state="ready", type="free", protocol="FC"),
        },
        params={
            "0:3:1": PortParams(nsp="0:3:1", connmode="peer", conntype="point", intcoal="disabled"),
            "1:3:1": PortParams(nsp="1:3:1", connmode="host", conntype="point", intcoal="enabled"),
        },
    )
    res_a = peer_ports.read_back_peer_ports(plan, before=before, after=after_a)
    assert res_a.changed == ["0:3:1"]
    assert res_a.sentences == [
        "0:3:1 is now a peer port (port WWPN 20310002AC02D495).",
        "1:3:1 did not come back as a peer port (Type free, state offline).",
        "0:3:3 is not in showport any more: check the array before going on.",
        "1:3:3 changed as well (mode target, now initiator): check the array before going on.",
        "0:3:4 changed as well (Type host, now free): check the array before going on.",
    ]
    assert res_a.removals == [
        "controlport rst -f 1:3:1",
        "controlport offline 0:3:1",
        "controlport config host -ct point -f 0:3:1",
        "controlport rst -f 0:3:1",
        "controlport intcoal enable -f 0:3:1",
    ]

    # Case B: 0:3:1 missing from showport, 1:3:1 changed to wrong mode (loop)
    after_b = PeerPortView(
        ports={
            "1:3:1": PeerPortState(nsp="1:3:1", mode="target", state="loss_sync", type="free", protocol="FC"),
            "0:3:3": before.ports["0:3:3"],
            "1:3:3": before.ports["1:3:3"],
            "0:3:4": before.ports["0:3:4"],
        },
        params={"1:3:1": PortParams(nsp="1:3:1", connmode="host", conntype="loop")},
    )
    res_b = peer_ports.read_back_peer_ports(plan, before=before, after=after_b)
    assert res_b.changed == []
    assert "0:3:1 is not in showport any more: check the array before going on." in res_b.sentences
    assert "1:3:1 did not come back as a peer port (Type free, state loss_sync)." in res_b.sentences
    assert res_b.removals[-2:] == ["controlport intcoal enable -f 1:3:1", "controlport intcoal enable -f 0:3:1"]


# ================================================================== 5. asbuilt.py

def test_asbuilt_split_placeholders_and_missing_headings_warning(tmp_path):
    tpl = tmp_path / "split.docx"
    d = docx.Document()
    p = d.add_paragraph()
    p.add_run("Hello <Cust")
    p.add_run("omer Name> at <Site ")
    p.add_run("Location> and <Unknown Tag>")
    hdr = d.sections[0].header.paragraphs[0]
    hdr.add_run("<Customer")
    hdr.add_run("Name>")
    d.save(str(tpl))

    out, warnings = generate_asbuilt(AsBuiltData(customer="Contoso", site="BLR"), tmp_path / "out.docx", template=tpl)
    doc = docx.Document(str(out))
    assert doc.paragraphs[0].text == "Hello Contoso at BLR and <Unknown Tag>"
    assert doc.sections[0].header.paragraphs[0].text == "Contoso"
    assert warnings == [
        "No 'Inventory' heading was found in the template, so the hardware inventory is NOT in this document.",
        "No 'checkhealth' heading was found in the template, so the health report is NOT in this document.",
        (
            "Placeholders are still unfilled and will be visible to the customer: <Unknown Tag>. "
            "Fill them in the workbook (or the As-built step) and regenerate, or edit the document before sending."
        ),
    ]


def test_asbuilt_zoning_iscsi_peer_ports_file_and_failover_sections(tmp_path):
    data = AsBuiltData(
        customer="Contoso",
        site="BLR",
        application_workload="vSphere",
        purpose="block",
        name="rack13",
        showport=_capture(ISCSI_FIX / "tagged" / "showport.txt"),
        showport_iscsivlans=_capture(ISCSI_FIX / "tagged" / "showport_iscsivlans.txt"),
        showport_par=_capture(PEER_FIX / "E18U31" / "showport_par.txt"),
        showport_peer=_capture(PEER_FIX / "E18U31" / "showport_peer.txt"),
        iscsi_network_rows=[
            {"nsp": "0:4:2", "vlan_id": 2999, "ip": "192.0.2.10", "netmask": "255.255.255.0", "gateway": "192.0.2.1"},
            {"nsp": "1:4:2", "vlan_id": 2999, "ip": "192.0.2.11", "netmask": "255.255.255.0"},
        ],
        iscsi_set_up_in_run=[("0:4:2", 2999)],
        peer_ports_rows=[
            {"nsp": "0:3:2", "source_wwpns": ["20310002AC02AC38"]},
            {"nsp": "9:9:9", "source_wwpns": []},
        ],
        peer_ports_plan={
            "actions": [{"nsp": "0:3:2", "state": "create", "commands": ["controlport offline 0:3:2"]}]
        },
        peer_ports_result={
            "changed": ["0:3:2"],
            "sentences": ["0:3:2 is now a peer port."],
            "removals": ["controlport offline 0:3:2", "controlport config host -ct point -f 0:3:2"],
        },
        zoning_plan={
            "fabrics": [
                {
                    "fabric": "F1",
                    "switch_host": "10.0.0.10",
                    "switch_name": "SW1",
                    "fabric_name": "FabA",
                    "active_cfg": "CFG1",
                    "switch_count": 2,
                    "hosts": [{"wwpn": "1000000000000001", "host_name": "esx1", "display": "10:00:00:00:00:00:00:01", "suggested_alias": "h_esx1"}],
                    "array_ports": [
                        {"wwpn": "20310002AC02D495", "nsp": "0:3:1", "display": "20:31:00:02:ac:02:d4:95", "suggested_alias": "a_031"},
                        {"wwpn": "20320002AC02D495", "nsp": "0:3:2", "display": "20:32:00:02:ac:02:d4:95"},
                        {"wwpn": "20330002AC02D495", "nsp": "0:3:3", "display": "20:33:00:02:ac:02:d4:95"},
                    ],
                    "pairs": [
                        ["1000000000000001", "20310002AC02D495"],
                        ["1000000000000001", "20320002AC02D495"],
                        ["1000000000000001", "20330002AC02D495"],
                    ],
                    "already_zoned": [["1000000000000001", "20310002AC02D495"]],
                    "zone_names": {"1000000000000001|20310002AC02D495": ["z1"]},
                },
                {"fabric": "F2", "switch_host": "10.0.0.11", "pairs": []},
            ],
            "offline_hosts": ["esx_off"],
        },
        zoning_rendered={
            "aliases": {"20320002AC02D495": "custom_032"},
            "selected_pairs": [["1000000000000001", "20320002AC02D495"]],
            "commands": {"F1": ["zonecreate \"z2\", \"h_esx1; custom_032\""]},
            "peer_commands": {"F1": ["zonecreate \"peer_z\", \"a; b\""]},
        },
        zoning_report={"zoned_hosts": ["esx1"], "unverified_hosts": ["esx_off"]},
        file_ports=[
            EthernetPort(
                node=0,
                slot=4,
                card_port=1,
                role="file",
                address="10.0.0.2",
                prefix_len="24",
                link="up",
                link_state="ready",
            )
        ],
        file_report=FileReport(
            service=FileService(
                uid="fs-svc-1",
                enabled=True,
                nodes=[
                    FileNodeStatus(node=0, status=NODE_RUNNING),
                    FileNodeStatus(node=1, status="stopped"),
                ],
                capacity=FileCapacity(total=2 * 1024 * 1024, used=512 * 1024, available=1536 * 1024),
            ),
            file_systems=[
                FileSystemRecord(
                    uid="fs-1",
                    name="fs1",
                    size_mib=102400,
                    reduce=True,
                    share_count=1,
                    owner_node=0,
                    state="STATE_NORMAL",
                )
            ],
            shares=[
                FileShareRecord(
                    uid="sh-1",
                    name="sh1",
                    file_system="fs1",
                    client_group="cg1",
                    host_ip="",
                    mount_path="/fs1/sh1",
                    protocols=[],
                    state="STATE_NORMAL",
                )
            ],
            client_groups=[
                ClientGroup(
                    uid="cg-1",
                    name="cg1",
                    state="STATE_NORMAL",
                    clients=[ClientRule(address="10.0.0.5", access="rw", options="no_root_squash")],
                )
            ],
        ),
        replication_tab={"peer_host": "10.0.0.2", "rows": []},
        failover_record={
            "result": "failed",
            "failed_step": 3,
            "mode": "async",
            "group": "g1",
            "peer_group": "g1.r1",
            "primary_array": "A1",
            "peer_array": "A2",
            "started_at": "2026-11-16T10:00:00Z",
            "ended_at": "2026-11-16T10:05:00Z",
            "time_to_failover_s": 12.5,
            "time_to_synced_s": 30,
            "data_loss_bound": "2026-11-16 09:59:00 IST",
            "error": "recover timed out",
            "observed_state": "Primary-Rev/Stopped",
            "recovery_action": "setrcopygroup recover g1",
            "steps": [
                {
                    "seq": 1,
                    "title": "Stop",
                    "where": "P",
                    "cli": "stoprcopygroup g1",
                    "started_at": "2026-11-16T10:00:00Z",
                    "seconds": 2.5,
                    "primary": {"role": "Primary", "status": "Stopped", "synced": 1, "volumes": 1, "last_sync": "NA"},
                    "peer": {"present": False},
                    "outcome": "ok",
                },
            ],
        },
    )
    out, warnings = generate_asbuilt(data, tmp_path / "full.docx")
    _doc, paras, tables = _read_doc(out)
    assert warnings == [
        "The replication section could not read this array (not read); its states are missing.",
        "The replication section could not read the peer array (not read); the peer's columns are empty.",
    ]

    # Zoning table statuses & aliases
    assert tables[("Host", "HBA WWPN", "Alias", "Array port", "Array WWPN", "Alias", "Zone(s)", "Status")] == [
        ["esx1", "10:00:00:00:00:00:00:01", "h_esx1", "0:3:1", "20:31:00:02:ac:02:d4:95", "a_031", "z1", "already zoned"],
        ["esx1", "10:00:00:00:00:00:00:01", "h_esx1", "0:3:2", "20:32:00:02:ac:02:d4:95", "custom_032", "—", "command set delivered"],
        ["esx1", "10:00:00:00:00:00:00:01", "h_esx1", "0:3:3", "20:33:00:02:ac:02:d4:95", "—", "—", "not selected"],
    ]
    assert "F1 — switch 10.0.0.10 SW1 · fabric FabA · active cfg CFG1 · 2 switch(es) in fabric" in paras
    assert "No host HBA on this fabric needed a zone to this array." in paras
    assert "On no fabric (cable and power first): esx_off" in paras

    # iSCSI network section: VLAN table, absent row, pending gateway
    assert tables[("Port", "VLAN", "Address", "Gateway", "MTU", "Port state", "Set up")] == [
        ["0:4:2", "2999", "192.0.2.10/24", "—", "1500", "ready", "By this run"],
    ]
    assert "Asked for on the sheet but not on the array: 1:4:2 VLAN 2999 (192.0.2.11)." in paras
    assert "Gateways for a change window" in paras

    # Peer ports section: port present + missing, showport -peer table, commands, zones, removals
    assert tables[("Port", "Type", "Connection", "State", "Node WWN", "Port WWN", "Source ports to zone")] == [
        ["0:3:2", "free", "peer, point", "loss_sync", "2FF70002AC02D495", "20320002AC02D495", "20310002AC02AC38"],
        ["9:9:9", "not on the array", "—", "—", "—", "—", "—"],
    ]
    assert len(tables[("Port", "Mode", "State", "Node WWN", "Port WWN")]) == 2

    # File section: partial nodes running, share with no host_ip / empty protocols
    assert "File service: on, running on 1 of 2 nodes. Capacity for file: 2.0 TiB, 512 GiB used, 1.5 TiB available." in paras
    assert tables[("Share", "File system", "Client group", "Clients", "Mount", "Protocol", "State")] == [
        ["sh1", "fs1", "cg1", "10.0.0.5 rw no_root_squash", "/fs1/sh1", "—", "normal"],
    ]

    # Failover section: failed with step, timing, async data loss bound, recovery action
    assert "Result: Failed at step 3." in paras
    assert "Measured: the peer took over (Primary-Rev) 12.5 s after the failover was issued; every volume was Synced again 30 s after the recover." in paras
    assert "Stopped: recover timed out" in paras
    assert "Observed when it stopped: Primary-Rev/Stopped" in paras
    assert tables[("#", "Step", "On", "Command (CLI equivalent)", "Started", "Took", "P after", "S after", "Outcome")] == [
        ["1", "Stop", "P", "stoprcopygroup g1", "2026-11-16 10:00 UTC", "2.5 s", "Primary/Stopped · 1/1 Synced", "not on the array", "OK"],
    ]


def test_asbuilt_iscsi_unreadable_and_peer_ports_warning_and_file_empty_edges(tmp_path):
    data = AsBuiltData(
        customer="Contoso",
        site="BLR",
        application_workload="vSphere",
        purpose="block",
        showport_iscsivlans="Error: Invalid option -iscsivlans\n",
        peer_ports_rows=[{"nsp": "0:3:1"}],
        peer_ports_result={"error": "0:3:1 stayed free"},
        file_ports=[],
        file_report=FileReport(service=FileService(uid="fs-svc-off", enabled=False, nodes=[]), file_systems=[], shares=[]),
        zoning_report={"iscsi_hosts": {"lin1": ["0:4:1"], "lin2": []}, "zoned_hosts": ["lin1"], "unverified_hosts": ["fc1"]},
    )
    out, warnings = generate_asbuilt(data, tmp_path / "edges.docx")
    _doc, paras, _tables = _read_doc(out)
    assert "`showport -iscsivlans` could not be read: Error: Invalid option -iscsivlans" in paras
    assert warnings == [
        "`showport -iscsivlans` could not be read (Error: Invalid option -iscsivlans); the iSCSI network section is empty.",
        "Peer ports: the read after the paste did not match the plan: 0:3:1 stayed free",
    ]
    assert "File service: off." in paras
    assert "The array has no File ports." in paras
    assert "The array has no file systems." in paras
    assert "The array has no shares." in paras
    assert (
        "Zoned on both fabrics: none. iSCSI, no zoning needed: lin1 (logged in on 0:4:1). "
        "iSCSI, not logged in on the array yet, so nothing is exported to it: lin2. "
        "Not seen by the array on either fabric: fc1."
    ) in paras


def test_asbuilt_file_service_not_read_lists_only_ports_and_skips_file_systems(tmp_path):
    data = AsBuiltData(
        customer="Contoso",
        site="BLR",
        application_workload="vSphere",
        purpose="block",
        file_ports=[EthernetPort(node=0, slot=4, card_port=1, role="file", address="10.0.0.2", prefix_len="24", link="up", link_state="ready")],
        file_report=FileReport(
            service=None,
            notes=[],
            file_systems=[FileSystemRecord(uid="f1", name="fs1", size_mib=1024, reduce=False, share_count=0, owner_node=0, state="STATE_NORMAL")],
            shares=[],
        ),
    )
    out, warnings = generate_asbuilt(data, tmp_path / "file_not_read.docx")
    _doc, paras, tables = _read_doc(out)
    assert warnings == ["The File service section lists only the File ports: the file service was not read"]
    assert ("Port", "Address", "Gateway", "VLAN", "MTU", "Link") in tables
    assert "File systems" not in paras and "Shares" not in paras
