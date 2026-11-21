"""Network and fabric connectivity sections of the as-built document:
- SAN zoning designed in this run (SPEC-002 / SPEC-012)
- iSCSI network VLAN-tagged addresses and switch handoff (SPEC-024 R7)
- Peer ports for migration (SPEC-025 R9)

Kept apart from ``asbuilt.py`` following the pattern of ``asbuilt_replication.py`` and
``asbuilt_snapshots.py``. Pure document rendering over read-only data in ``AsBuiltData``; no I/O.
"""

from __future__ import annotations

import ipaddress

from alletra_onboard.application.documents.asbuilt_docx import (
    add_h1,
    add_mono,
    add_para,
    add_table,
    read_failed,
)
from alletra_onboard.application.documents.asbuilt_model import AsBuiltData
from alletra_onboard.application.provisioning.discovery import parse_iscsi_vlans
from alletra_onboard.application.provisioning.iscsi_network import (
    GATEWAY_WINDOW,
    gateway_window,
    gw_line,
    switch_handoff_for,
)
from alletra_onboard.application.provisioning.peer_ports_read import (
    parse_showport_par,
    parse_showport_peer,
    parse_showport_ports,
)
from alletra_onboard.domain.array_parse import parse_showport_roles
from alletra_onboard.domain.network import IscsiVlanAction, IscsiVlanInterface, IscsiVlanRequest

# ------------------------------------------------------------------ SPEC-002: SAN zoning


def _zoning_check_text(report: dict, *, check_only: bool) -> str:
    """What the zoning check found, host by host. The check's gate list (`zoned_hosts`) also holds iSCSI
    hosts logged in on the array, which need no zone and are on no fabric: they are named apart, so the
    document never calls one zoned (live 2026-11-17: *Zoned on both fabrics: zz_is_eljr*, an iSCSI host)."""
    iscsi: dict[str, list[str]] = report.get("iscsi_hosts") or {}
    fc_zoned = [h for h in report.get("zoned_hosts", []) if h not in iscsi]
    unverified = report.get("unverified_hosts", [])
    logged_in = [f"{h} (logged in on {', '.join(ports)})" for h, ports in sorted(iscsi.items()) if ports]
    waiting = sorted(h for h, ports in iscsi.items() if not ports)
    parts = []
    if fc_zoned or unverified or report.get("expected") or not iscsi:
        if check_only:
            parts.append("Zoned on both fabrics: " + (", ".join(fc_zoned) or "none") + ".")
        else:
            parts.append(f"zoned on both fabrics — {', '.join(fc_zoned)}." if fc_zoned else "no host zoned on both fabrics.")
    if logged_in:
        parts.append("iSCSI, no zoning needed: " + ", ".join(logged_in) + ".")
    if waiting:
        parts.append("iSCSI, not logged in on the array yet, so nothing is exported to it: " + ", ".join(waiting) + ".")
    if unverified:
        parts.append(f"Not seen by the array on either fabric: {', '.join(unverified)}." if check_only
                     else f"Not verified — {', '.join(unverified)}.")
    return " ".join(parts)


def _fabric_heading(fab: dict) -> str:
    name = fab.get("fabric", "")
    bits = [f"{name} — switch {fab.get('switch_host', '')} {fab.get('switch_name', '')}".rstrip()]
    if fab.get("fabric_name"):
        bits.append(f"fabric {fab['fabric_name']}")
    if fab.get("active_cfg"):
        bits.append(f"active cfg {fab['active_cfg']}")
    if fab.get("switch_count"):
        bits.append(f"{fab['switch_count']} switch(es) in fabric")
    return " · ".join(bits)


def _fabric_pair_rows(
    fab: dict,
    aliases: dict[str, str],
    delivered: set[tuple[str, ...]],
) -> list[list[str]]:
    by_wwpn = {w["wwpn"]: w for w in fab.get("hosts", []) + fab.get("array_ports", [])}
    zoned = {tuple(p) for p in fab.get("already_zoned", [])}
    zone_names = fab.get("zone_names", {})

    def alias(wwpn: str) -> str:
        return aliases.get(wwpn) or by_wwpn.get(wwpn, {}).get("suggested_alias") or "—"

    rows: list[list[str]] = []
    for h, a in (tuple(p) for p in fab.get("pairs", [])):
        host, port = by_wwpn.get(h, {}), by_wwpn.get(a, {})
        if (h, a) in zoned:
            status = "already zoned"
        elif (h, a) in delivered:
            status = "command set delivered"
        else:
            status = "not selected"
        rows.append([
            host.get("host_name") or "—", host.get("display", h), alias(h),
            port.get("nsp", "—"), port.get("display", a), alias(a),
            ", ".join(zone_names.get(f"{h}|{a}", [])) or "—", status,
        ])
    return rows


def _add_fabric_zoning(
    doc,
    fab: dict,
    aliases: dict[str, str],
    delivered: set[tuple[str, ...]],
    commands: dict[str, list[str]],
) -> None:
    add_para(doc, _fabric_heading(fab), bold=True)
    rows = _fabric_pair_rows(fab, aliases, delivered)
    if rows:
        add_table(doc, ["Host", "HBA WWPN", "Alias", "Array port", "Array WWPN", "Alias", "Zone(s)", "Status"], rows,
                  widths=[0.14, 0.16, 0.12, 0.08, 0.16, 0.12, 0.12, 0.10])
    else:
        add_para(doc, "No host HBA on this fabric needed a zone to this array.")
    name = fab.get("fabric", "")
    if commands.get(name):
        add_para(doc, "Delivered to the SAN team for application; confirm against the fabric before relying on it.")
        add_mono(doc, commands[name])


def add_zoning_section(doc, data: AsBuiltData) -> None:
    add_h1(doc, "SAN zoning designed in this run")
    plan = data.zoning_plan
    report = data.zoning_report
    if not plan and not report:
        add_para(doc, "This run did not include the SAN zoning step.")
        return
    if not plan:
        # The check ran (array-side) but no plan was built: say what the check found, plainly.
        add_para(doc, "The zoning check ran against the array's logins; no zoning plan was built and no "
                      "command set was generated in this run.")
        add_para(doc, _zoning_check_text(report or {}, check_only=True))
        return
    rendered = data.zoning_rendered or {}
    aliases: dict[str, str] = rendered.get("aliases") or {}
    delivered = {tuple(p) for p in rendered.get("selected_pairs") or []}
    commands: dict[str, list[str]] = rendered.get("commands") or {}
    add_para(doc, "The tool designs zones and hands the SAN team a command set; it never writes to a switch. "
                  "Rows marked 'already zoned' were found in the fabric's effective configuration.")
    for fab in plan.get("fabrics", []):
        _add_fabric_zoning(doc, fab, aliases, delivered, commands)
    if plan.get("offline_hosts"):
        add_para(doc, "On no fabric (cable and power first): " + ", ".join(plan["offline_hosts"]))
    if not rendered:
        add_para(doc, "No command set was generated in this run.")
    if report:
        add_para(doc, "Zoning check on the array: " + _zoning_check_text(report, check_only=False))
    else:
        add_para(doc, "The zoning check was not run.")


# ------------------------------------------------------------------ SPEC-024 R7: iSCSI network


def _prefix(mask: str) -> str:
    try:
        return str(ipaddress.ip_network(f"0.0.0.0/{mask}").prefixlen)
    except ValueError:
        return mask


def _read_iscsi_vlans(raw_answer: str) -> tuple[list[IscsiVlanInterface], str]:
    answer = raw_answer.strip()
    if answer.lower().startswith("error"):
        return [], answer.splitlines()[0]
    try:
        return parse_iscsi_vlans(answer), ""
    except ValueError as exc:
        return [], str(exc)


def _add_pending_iscsi_gateways(doc, rows: list[dict], vlans: list[IscsiVlanInterface]) -> None:
    # ADR 0017, amended 2026-11-17: the tool adds the address without its gateway; a gateway the sheet gives
    # and the array does not have yet is the change window's, printed here with its lines.
    gateways: dict[tuple[object, object], str] = {(v.nsp, v.vlan_id): v.gateway for v in vlans}
    pending = []
    for row in rows:
        key = (row.get("nsp"), row.get("vlan_id"))
        if row.get("gateway") and key in gateways and not gateways[key]:
            req = IscsiVlanRequest.model_validate(row)
            pending.append(IscsiVlanAction(nsp=req.nsp, vlan_id=req.vlan_id, state="exists", gateway_cli=gw_line(req)))
    if not pending:
        return
    add_para(doc, "Gateways for a change window", bold=True)
    add_para(doc, "The sheet gives a gateway for "
                  + ", ".join(f"{a.nsp} VLAN {a.vlan_id}" for a in pending)
                  + f", and the array has none. {GATEWAY_WINDOW} The lines, kept for that window:")
    add_mono(doc, gateway_window(pending))


def _add_iscsi_vlan_table(doc, name: str, data: AsBuiltData, vlans: list[IscsiVlanInterface]) -> None:
    if not vlans:
        add_para(doc, f"{name} has no VLAN-tagged iSCSI address.")
        return
    roles, _wwn = parse_showport_roles(data.showport)
    add_para(doc, f"The VLAN-tagged iSCSI addresses on {name}'s iSCSI ports when this document was made. Each port's "
                  "untagged address is not listed here; it stays as it was.")
    set_up = {(nsp, vlan) for nsp, vlan in data.iscsi_set_up_in_run}
    add_table(doc, ["Port", "VLAN", "Address", "Gateway", "MTU", "Port state", "Set up"],
              [[v.nsp, str(v.vlan_id), f"{v.ip}/{_prefix(v.netmask)}", v.gateway or "—", v.mtu or "—",
                roles[v.nsp].state if v.nsp in roles else "—",
                "By this run" if (v.nsp, v.vlan_id) in set_up else "Already there"] for v in vlans])


def add_iscsi_network_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-024 R7: when the array has a VLAN-tagged iSCSI address or the sheet asks for one: every
    interface on every iSCSI port with the port's state (showport -iscsivlans has no State column),
    whether this run set it up, then the sentences for the network team."""
    command = "showport -iscsivlans"
    rows = data.iscsi_network_rows
    vlans, unreadable = _read_iscsi_vlans(data.showport_iscsivlans)
    # A read that failed cannot say the array has no interface, so the section names the failure.
    if not vlans and not rows and not unreadable and command not in data.read_errors:
        return
    add_h1(doc, "iSCSI network")
    if read_failed(doc, data.read_errors, command, warnings):
        return
    if unreadable:
        add_para(doc, f"`{command}` could not be read: {unreadable}")
        warnings.append(f"`{command}` could not be read ({unreadable}); the iSCSI network section is empty.")
        return
    name = data.name or data.serial_no or "the array"
    _add_iscsi_vlan_table(doc, name, data, vlans)
    there = {(v.nsp, v.vlan_id) for v in vlans}
    absent = [r for r in rows if (r.get("nsp"), r.get("vlan_id")) not in there]
    if absent:
        add_para(doc, "Asked for on the sheet but not on the array: "
                      + ", ".join(f"{r.get('nsp')} VLAN {r.get('vlan_id')} ({r.get('ip')})" for r in absent) + ".")
    _add_pending_iscsi_gateways(doc, rows, vlans)
    sentences = switch_handoff_for(name, vlans)
    if sentences:
        add_para(doc, "For the network team", bold=True)
        add_para(doc, "The tool does not change any switch. Each switch port cabled to these array ports carries the "
                      "VLANs tagged and keeps its native VLAN for the untagged address:")
        add_mono(doc, sentences)


# ------------------------------------------------------------------ SPEC-025 R9: Peer ports


def _peer_port_rows(data: AsBuiltData) -> list[list[str]]:
    ports = parse_showport_ports(data.showport)
    params = parse_showport_par(data.showport_par)
    rows: list[list[str]] = []
    for req in data.peer_ports_rows:
        nsp = req.get("nsp", "")
        p, par = ports.get(nsp), params.get(nsp)
        rows.append([
            nsp, p.type if p else "not on the array", f"{par.connmode}, {par.conntype}" if par else "—",
            p.state if p else "—", p.node_wwn if p and p.node_wwn else "—", p.port_wwn if p and p.port_wwn else "—",
            ", ".join(req.get("source_wwpns") or []) or "—",
        ])
    return rows


def _add_peer_port_commands(doc, plan: dict, result: dict, warnings: list[str]) -> None:
    add_para(doc, "How they were set", bold=True)
    creates = [a for a in plan.get("actions") or [] if a.get("state") == "create"]
    if creates and result.get("changed"):
        add_para(doc, "The tool printed these commands and a consultant pasted them on the array's CLI; the tool does "
                      "not run them. The read after the paste checked each port and every other port.")
        add_mono(doc, [line for a in creates for line in [f"# {a.get('nsp', '')}", *(a.get("commands") or [])]])
    elif creates:
        add_para(doc, "The tool printed these commands for a consultant to paste; no port change was seen on the array "
                      "in this run.")
        add_mono(doc, [line for a in creates for line in [f"# {a.get('nsp', '')}", *(a.get("commands") or [])]])
    else:
        add_para(doc, "No port was set in this run: every port the sheet names was already in peer mode, or no plan "
                      "had a port to set.")
    if result.get("sentences"):
        add_mono(doc, list(result["sentences"]))
    if result.get("error"):
        warnings.append(f"Peer ports: the read after the paste did not match the plan: {result['error']}")


def _add_peer_port_zones(doc, data: AsBuiltData) -> None:
    add_para(doc, "Peer-port zones designed in this run", bold=True)
    zones = (data.zoning_rendered or {}).get("peer_commands") or {}
    if any(zones.values()):
        add_para(doc, "The command set given to the SAN team; the tool never writes to a switch.")
        for fabric, commands in sorted(zones.items()):
            if commands:
                add_mono(doc, [f"# {fabric}", *commands])
    else:
        add_para(doc, "No peer-port zone command set was generated in this run.")


def _add_peer_port_removals(doc, result: dict) -> None:
    add_para(doc, "To remove the peer ports", bold=True)
    removals = result.get("removals") or []
    if removals:
        add_para(doc, "Puts each port this run set back in the mode it had, last port first. Remove the SAN team's "
                      "peer-port zones and any migration that uses these ports first. The tool never runs these.")
        add_mono(doc, removals)
    else:
        add_para(doc, "Nothing: the tool saw no port change in this run.")


def add_peer_ports_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    """SPEC-025 R9, when the sheet has the Peer ports tab: each port as the array reads it now (mode,
    connection, state, WWNs), the array's own peer-port listing, the commands and who ran them, the
    peer-port zones designed in the run, and the removal set."""
    if not data.peer_ports_rows:
        return
    add_h1(doc, "Peer ports")
    name = data.name or data.serial_no or "the array"
    add_para(doc, f"The Fibre Channel ports of {name} named on the sheet's Peer ports tab, as the array reads them when "
                  "this document was made. A peer port logs in to the fabric as an initiator so a data migration can "
                  "read the source array through it.")
    add_table(doc, ["Port", "Type", "Connection", "State", "Node WWN", "Port WWN", "Source ports to zone"],
              _peer_port_rows(data))
    listed = parse_showport_peer(data.showport_peer)
    if listed:
        add_para(doc, "The array's own list of its peer ports (showport -peer)", bold=True)
        add_table(doc, ["Port", "Mode", "State", "Node WWN", "Port WWN"],
                  [[r.nsp, r.mode, r.state, r.node_wwn or "—", r.port_wwn or "—"] for r in listed])
    result = data.peer_ports_result or {}
    _add_peer_port_commands(doc, data.peer_ports_plan or {}, result, warnings)
    _add_peer_port_zones(doc, data)
    _add_peer_port_removals(doc, result)
