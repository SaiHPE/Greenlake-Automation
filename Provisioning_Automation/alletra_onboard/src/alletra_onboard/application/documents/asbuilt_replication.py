"""SPEC-018 — the as-built's Replication section, placed after *Provisioning performed* only when the
run's workbook has a Replication tab.

Everything about the arrays is read when the document is made (`AsBuiltData.replication_primary`,
`AsBuiltData.replication_peer`, `AsBuiltData.replication_details`), never copied from the plan.
Kept apart from asbuilt.py, which calls `add_replication_section`; `documents/steps.py` calls
`rc_group_names` to know which groups to read with `showrcopy -d`.
"""

from __future__ import annotations

from typing import NamedTuple

from alletra_onboard.application.documents.asbuilt_docx import (
    add_h1,
    add_mono,
    add_para,
    add_table,
    format_when,
)
from alletra_onboard.application.documents.asbuilt_model import AsBuiltData
from alletra_onboard.application.replication.link_check import PING_COUNT
from alletra_onboard.application.replication.plan_check import find_partnership
from alletra_onboard.application.replication.verify import peer_group_name
from alletra_onboard.domain.replication import (
    RTT_LIMIT_MS,
    ReplicationArrayView,
    rtt_limit_ms,
    rtt_limit_text,
)

_RC_OUTCOME_LABEL = {"created": "Done", "exists": "Already existed", "failed": "Failed", "skipped": "Skipped"}
_RC_KIND_LABEL = {
    "group": "Remote Copy group", "peer_vvset": "Peer volume set", "test_volume": "Test volume",
    "test_vvset": "Test volume set", "volume_admit": "Volume admitted", "start": "Group started",
    "policy": "Policies and period", "rcip_port": "Replication port", "rc_service": "Remote Copy service",
    "target": "Remote Copy target", "ping": "Ping between the ports", "links": "Links Up",
}


class _RcSide(NamedTuple):
    view: ReplicationArrayView | None
    name: str
    err: str


def _rc_view(view: ReplicationArrayView | None, name_fallback: str) -> _RcSide:
    """One array's read-back view, display name and read error (or '') for the replication section."""
    if view is None:
        return _RcSide(None, name_fallback, "not read")
    err = view.read_error or ""
    return _RcSide(None if err else view, view.name or view.host or name_fallback, err)


def _rc_group_rows(data: AsBuiltData) -> list[dict]:
    """The groups this run configured: from the apply's outcomes when it ran; without an apply, only the
    groups the plan found already in place (a planned-but-not-created group is not on the array)."""
    if data.replication_result:
        names = [o.get("name") for o in data.replication_result.get("outcomes", [])
                 if o.get("kind") == "group" and o.get("status") in ("created", "exists")]
    elif data.replication_plan:
        names = [a.get("name") for a in data.replication_plan.get("actions", [])
                 if a.get("kind") == "group" and a.get("state") == "exists"]
    else:
        names = []
    detail = {a.get("name"): a.get("detail") or {} for a in (data.replication_plan or {}).get("actions", []) if a.get("kind") == "group"}
    return [{"name": n, **detail.get(n, {})} for n in dict.fromkeys(n for n in names if n)]


def rc_group_names(data: AsBuiltData) -> list[str]:
    """The Remote Copy groups this run configured, in the section's order."""
    return [row["name"] for row in _rc_group_rows(data)]


def _rc_peer_set(peer, peer_group) -> str:
    """The peer volume set holding exactly the peer group's volumes (the array's own RCP_ sets aside)."""
    if peer is None or peer_group is None or not peer_group.volumes:
        return ""
    want = set(peer_group.volume_names)
    return next((name for name, members in peer.vvsets.items() if set(members) == want and not name.startswith("RCP_")), "")


def _rc_rpo_text(row: dict, tab: dict, period_read: str = "") -> str:
    """'RPO 10 min (period 5m)' for a periodic group, 'sync (every write)' otherwise. The period comes
    from the array when it was read; the RPO is the workbook's number for that volume set."""
    period = row.get("period_seconds")
    if not period and not period_read:
        return "sync (every write)"
    rpo = next((r.get("rpo_minutes") for r in tab.get("rows", []) if r.get("vvset") == row.get("vvset")), None)
    if not rpo and period:
        rpo = period * 2 // 60
    shown = period_read or (f"{period // 60}m" if period else "?")
    return (f"RPO {rpo} min " if rpo else "") + f"(period {shown})"


def _cell(value: str) -> str:
    return "—" if value in ("", "NA", "-") else value


def _with_id(name: str, number: int | None) -> str:
    return _cell(name) + (f" ({number})" if number is not None else "")


def _add_rc_group_detail(doc, data: AsBuiltData, row: dict, a_name: str, warnings: list[str]) -> None:
    """BL-64: every volume in one group and the group's settings, from `showrcopy -d groups <group>` read
    on this array when the document was made."""
    g = row["name"]
    detail = (data.replication_details or {}).get(g)
    if detail is None:
        err = (data.replication_details_errors or {}).get(g)
        if err:
            add_para(doc, f"{g}: its settings and volumes could not be read (showrcopy -d): {err}")
            warnings.append(f"The settings and volumes of Remote Copy group {g} could not be read ({err}); "
                            "the replication section lists its volumes without them.")
        return
    add_para(doc, f"{g}: every volume and the group's settings", bold=True)
    add_para(doc, f"As {a_name} reports them (showrcopy -d groups {g}) when this document was generated. ID: the "
                  "array's own number. Iterations correlate each volume with its snapshots and the peer's copy.")
    settings = [
        ["Target", _cell(detail.target)], ["Mode", _cell(detail.mode)],
        ["RPO / period", _rc_rpo_text(row, data.replication_tab or {}, detail.period)],
        ["Policies", ", ".join(detail.options) or "—"], ["Role here", _cell(detail.role)],
        ["Status", _cell(detail.status)], ["Group ID", "—" if detail.id is None else str(detail.id)],
        ["CPG for the volumes here", _cell(detail.local_user_cpg)],
        ["CPG for the volumes on the peer", _cell(detail.remote_user_cpg)],
    ]
    if detail.local_snap_cpg or detail.remote_snap_cpg:
        settings += [["Snapshot CPG here", _cell(detail.local_snap_cpg)],
                     ["Snapshot CPG on the peer", _cell(detail.remote_snap_cpg)]]
    settings += [["Last sync of the group", _cell(detail.last_sync)], ["Volumes", str(len(detail.volumes))]]
    add_table(doc, ["Setting", "Value"], settings, widths=[0.35, 0.65])
    add_table(doc, ["Volume here (ID)", "Volume on peer (ID)", "Sync status", "Last sync", "Resync snapshot",
                    "Sync snapshot", "Iterations: volume / resync / sync", "Volume set here / on peer"],
              [[_with_id(v.local_name, v.local_id), _with_id(v.remote_name, v.remote_id), _cell(v.sync_status),
                _cell(v.last_sync), _cell(v.resync_snapshot), _cell(v.sync_snapshot),
                " / ".join(_cell(x) for x in (v.volume_iteration, v.resync_iteration, v.sync_iteration)),
                f"{_cell(v.local_set)} / {_cell(v.remote_set)}"] for v in detail.volumes],
              widths=[0.15, 0.15, 0.09, 0.14, 0.13, 0.09, 0.13, 0.12])


def _rc_rtt_verdict(data: AsBuiltData, over: list[str], what: str) -> str:
    if not over:
        return "within HPE's limit."
    accepted = any("accepted it and chose to continue" in n for n in (data.replication_result or {}).get("notes", []))
    if accepted:
        return f"over HPE's limit for {'/'.join(over)} — the operator accepted the {what} and continued."
    return f"over HPE's limit for {'/'.join(over)}."


def _add_link_check(doc, data: AsBuiltData) -> None:
    """SPEC-020 R6: what `checkrclink` measured, the limit for each configured mode, and whether the
    operator accepted a latency over it (the apply's note says so)."""
    check = data.link_check or {}
    add_para(doc, "Link check", bold=True)
    results = check.get("results", [])
    measured = [r for r in results if r.get("status") == "measured" and r.get("latency_ms") is not None]
    modes = check.get("modes", [])
    limits = "; ".join(rtt_limit_text("IP", m) for m in modes if m in RTT_LIMIT_MS["IP"])
    if check.get("error") or not measured:
        add_para(doc, f"The latency between the arrays was not measured: {check.get('error') or 'no link could be tested'}.")
        return
    worst = max(r["latency_ms"] for r in measured)
    over = [m for m in modes if worst > rtt_limit_ms("IP", m)]
    verdict = _rc_rtt_verdict(data, over, "measured latency")
    add_para(doc, f"Measured with checkrclink on {check.get('at', '')} (test length {check.get('duration_s', '')} s, stopped "
                  f"once the latency was printed): worst latency {worst:g} ms on {len(measured)} link(s); {limits}. "
                  f"The latency is {verdict}")
    rows = []
    by_ping = False
    for r in results:
        pair = r.get("pair", {})
        link = f"A {pair.get('nsp_a', '')} ({pair.get('ip_a', '')}) → B {pair.get('nsp_b', '')} ({pair.get('ip_b', '')})"
        if r.get("status") == "measured":
            lost = r.get("pings_lost_pct")
            ping = (r.get("detail") or "").startswith("Measured with ping")
            by_ping = by_ping or ping
            rows.append([link, f"{r.get('latency_ms'):g} ms" + (" (ping)" if ping else ""), f"{lost:g} %" if lost is not None else "—"])
        else:
            rows.append([link, "not measured", r.get("detail") or "—"])
    add_table(doc, ["Link", "Latency", "Pings lost"], rows, widths=[0.56, 0.18, 0.26])
    if by_ping:
        add_para(doc, "(ping): the array's link test printed its latency line with no number on that link, so the tool "
                      f"measured the average round trip with {PING_COUNT} pings from the same port to the same address.")
    for line in check.get("unchecked", []):
        add_para(doc, f"Not checked: {line}")


def _add_typed_latency(doc, data: AsBuiltData) -> None:
    """SPEC-031 R6/R7: over Fibre Channel the latency is the round-trip time the engineer typed on the
    Replication tab, held to the FC limit; the document says it was typed, not measured."""
    tab = data.replication_tab or {}
    rtt = tab.get("rtt_ms")
    modes = sorted({r.get("mode") for r in tab.get("rows", []) if r.get("mode")}) or ["async"]
    add_para(doc, "Round-trip time", bold=True)
    if rtt is None:
        add_para(doc, "The arrays replicate over Fibre Channel and no round-trip time was typed on the Replication tab. "
                      "The tool cannot measure Fibre Channel links yet, so the latency between the arrays is not recorded.")
        return
    over = [m for m in modes if rtt > rtt_limit_ms("FC", m)]
    verdict = _rc_rtt_verdict(data, over, "typed time")
    limits = "; ".join(rtt_limit_text("FC", m) for m in modes)
    add_para(doc, f"Typed by the engineer on the Replication tab, not measured: {rtt:g} ms. The tool cannot measure Fibre "
                  f"Channel links yet. {limits[0].upper() + limits[1:]}. The typed time is {verdict}")


def _rc_partner_row(label: str, side: _RcSide, transport: str) -> list[str]:
    view = side.view
    if view is None:
        return [label, "could not be read" if side.err else "—", "—", "—", "—"]
    rc = f"{view.rc_status}{', ' + view.rc_health if view.rc_health else ''}" or "—"
    if transport == "FC":
        fc = {t.name for t in view.targets if t.is_fc}
        ports = "; ".join(f"{link.nsp} → {link.address}" for link in view.links if link.target in fc) or "none"
    else:
        ports = "; ".join(f"{p.nsp} {p.ip}" for p in view.rcip_ports) or "none configured"
    return [label, view.serial or "—", view.os_version or "—", rc, ports]


def _add_rc_partnership(doc, data: AsBuiltData, a: _RcSide, b: _RcSide) -> str:
    add_para(doc, "Partner array", bold=True)
    partnership = find_partnership(a.view, b.view) if a.view is not None and b.view is not None else None
    # SPEC-031 R7: the replication ports are RCIP addresses, or over Fibre Channel each FC link (port → peer WWN)
    transport = (partnership.transport if partnership is not None
                 else ((data.replication_report or {}).get("partnership") or {}).get("transport", "IP"))
    add_table(doc, ["Array", "Serial", "OS", "Remote Copy", "Replication ports"],
              [_rc_partner_row("This array: " + a.name, a, transport),
               _rc_partner_row("Peer: " + b.name, b, transport)],
              widths=[0.26, 0.14, 0.10, 0.16, 0.34])
    if partnership is None or a.view is None or b.view is None:
        add_para(doc, "No Remote Copy partnership between the two arrays could be confirmed when this document was "
                      "generated" + (" (one side was not readable)." if a.err or b.err else "."))
        return transport
    link_rows = [
        [side.name, t.name, t.policy or "—", f"{link.nsp} → {link.address}", link.status]
        for side in (a, b) if side.view is not None
        for t in side.view.targets
        for link in side.view.links
        if link.target == t.name and not link.inbound
    ]
    add_para(doc, f"Partnered: {a.name} → {b.name} via target '{partnership.target_on_primary}' "
                  f"({partnership.links_primary_up}/{partnership.links_primary_total} links Up); "
                  f"{b.name} → {a.name} via target '{partnership.target_on_peer}' "
                  f"({partnership.links_peer_up}/{partnership.links_peer_total} links Up). "
                  + ("Over Fibre Channel, found by port WWN." if partnership.transport == "FC"
                     else "Over RCIP, found by link address."))
    add_table(doc, ["Array", "Target", "Policy",
                    "Link (port → peer port WWN)" if partnership.transport == "FC" else "Link (port → peer address)",
                    "Status"], link_rows, widths=[0.22, 0.22, 0.16, 0.28, 0.12])
    return transport


def _rc_configured_tables(
    a: _RcSide, b: _RcSide, groups: list[dict], tab: dict,
) -> tuple[list[list[str]], list[list[str]]]:
    group_rows: list[list[str]] = []
    volume_rows: list[list[str]] = []
    for row in groups:
        g = row["name"]
        ag = a.view.group(g) if a.view is not None else None
        bg = b.view.group(peer_group_name(g, a.view)) if (a.view is not None and b.view is not None) else None
        if ag is None:
            state = "could not be read" if a.err else "not on the array now"
            group_rows.append([g, row.get("mode", "—"), _rc_rpo_text(row, tab), "—", state, "—", "—", row.get("peer_vvset") or "—"])
            continue
        period = _rc_rpo_text(row, tab, ag.period)
        peer_role = bg.role if bg else ("could not be read" if b.err else "not found on the peer")
        peer_set = row.get("peer_vvset") or _rc_peer_set(b.view, bg) or "—"
        if b.view is not None and peer_set != "—":
            members = b.view.vvsets.get(peer_set)
            peer_set += " (missing on the peer)" if members is None else f" ({len(members)} volume(s))"
        synced = sum(1 for v in ag.volumes if v.sync_status.lower() == "synced")
        status = f"{ag.status} · {synced}/{len(ag.volumes)} Synced" + (f" · last sync {ag.last_sync}" if ag.last_sync and ag.last_sync != "NA" else "")
        group_rows.append([g, ag.mode, period, ", ".join(ag.options) or "—", ag.role, peer_role, status, peer_set])
        for v in ag.volumes:
            size = a.view.volume_size_mib.get(v.local_name) if a.view is not None else None
            volume_rows.append([g, v.local_name, f"{size / 1024:g}" if size else "—", v.remote_name or "—",
                                v.sync_status or "—", v.last_sync if v.last_sync and v.last_sync != "NA" else "—"])
    return group_rows, volume_rows


def _add_rc_configured_groups(doc, data: AsBuiltData, a: _RcSide, b: _RcSide, warnings: list[str]) -> list[dict]:
    add_para(doc, "Remote Copy groups configured by this run", bold=True)
    groups = _rc_group_rows(data)
    planned_new = [act for act in (data.replication_plan or {}).get("actions", []) if act.get("kind") == "group" and act.get("state") == "create"]
    if not data.replication_result and not data.replication_plan:
        add_para(doc, "The replication step was not run in this run.")
    elif not data.replication_result and planned_new:
        add_para(doc, "A replication plan was built but not applied.")
    elif data.replication_result and not groups:
        add_para(doc, "The apply created no Remote Copy group.")
    if not groups:
        return groups
    suffix = (f" On the peer each group's name carries the suffix .r{a.view.system_id} (this array's system ID)."
              if a.view is not None and a.view.system_id is not None else "")
    if data.replication_result:
        when = f" at {format_when(data.replication_applied_at)}" if data.replication_applied_at else ""
        add_para(doc, f"Configured over WSAPI{when}. Roles and states are as read now.{suffix}")
    else:
        add_para(doc, "Already in place when this run read the arrays (configured by an earlier run); this run made no "
                      f"replication change. Roles and states are as read now.{suffix}")
    group_rows, volume_rows = _rc_configured_tables(a, b, groups, data.replication_tab or {})
    add_table(doc, ["Group", "Mode", "RPO / period", "Policies", "Role here", "Role on peer", "Status", "Peer volume set"],
              group_rows, widths=[0.14, 0.08, 0.14, 0.16, 0.09, 0.10, 0.17, 0.12])
    details = data.replication_details or {}
    # a group whose showrcopy -d was read gets its own table below; the others keep the short list
    volume_rows = [r for r in volume_rows if r[0] not in details]
    if volume_rows:
        add_table(doc, ["Group", "Volume here", "Size (GiB)", "Volume on peer", "Sync status", "Last sync"],
                  volume_rows, widths=[0.18, 0.20, 0.10, 0.20, 0.12, 0.20])
    for row in groups:
        _add_rc_group_detail(doc, data, row, a.name, warnings)
    return groups


def _add_rc_apply_record(doc, data: AsBuiltData, a_name: str, b_name: str) -> None:
    result = data.replication_result
    if not result:
        return
    applies = data.replication_applies or [{"plan": data.replication_plan, "result": result}]
    calls = [(where, cli) for x in applies for _seq, where, cli in sorted(
        ((c.get("seq", 0), c.get("where", "A"), c.get("cli", "")) for act in (x.get("plan") or {}).get("actions", [])
         for c in act.get("calls", [])), key=lambda t: t[0])]
    if calls:
        add_para(doc, "What was run, in order", bold=True)
        add_para(doc, "Each call the tool made, shown as the array CLI command (a WSAPI call as the command it is "
                      "equivalent to). A = this array, B = the peer.")
        add_mono(doc, [f"{where}  {cli}" for where, cli in calls])
    outcomes = [o for x in applies for o in (x.get("result") or {}).get("outcomes", [])]
    if outcomes:
        add_para(doc, "What each array reported", bold=True)
        add_table(doc, ["Kind", "Name", "On", "Result", "Detail"],
                  [[str(_RC_KIND_LABEL.get(o.get("kind", ""), o.get("kind", ""))), str(o.get("name", "")),
                    str(o.get("where", "A")), str(_RC_OUTCOME_LABEL.get(o.get("status", ""), o.get("status", ""))),
                    str(o.get("detail") or "—")] for o in outcomes],
                  widths=[0.18, 0.22, 0.06, 0.14, 0.40])
    if result.get("error"):
        add_para(doc, f"Replication stopped with an error: {result['error']}")
    add_para(doc, "To remove what this run created", bold=True)
    rem_a = data.replication_removals_a or result.get("removals_a") or []
    rem_b = data.replication_removals_b or result.get("removals_b") or []
    if rem_a or rem_b:
        add_para(doc, "Paste the A block on this array first, then the B block on the peer. Depending on the "
                      "peer, the array may already have removed a peer volume set or a secondary volume, so a "
                      "B line may answer 'does not exist'. "
                      "Objects that existed before the run are not listed. The tool never runs these.")
        lines = []
        if rem_a:
            lines += [f"# ---- A: {a_name}", *rem_a]
        if rem_b:
            lines += [f"# ---- B: {b_name}", *rem_b]
        add_mono(doc, lines)
    else:
        add_para(doc, "Nothing — this run created no replication objects.")


def add_replication_section(doc, data: AsBuiltData, warnings: list[str]) -> None:
    tab = data.replication_tab or {}
    add_h1(doc, "Replication configured in this run")
    a = _rc_view(data.replication_primary, data.name or "this array")
    b = _rc_view(data.replication_peer, tab.get("peer_host", "the peer array"))
    rows = tab.get("rows", [])
    add_para(doc, f"The workbook's Replication tab asked for {len(rows)} volume set(s) to be replicated to "
                  f"{b.name}. Everything below was read from both arrays when this document was generated; "
                  "nothing is copied from the plan.")
    if a.err:
        add_para(doc, f"{a.name} could not be read for this section: {a.err}")
        warnings.append(f"The replication section could not read this array ({a.err}); its states are missing.")
    if b.err:
        add_para(doc, f"The peer array could not be read for this section: {b.err}. Its columns below say so.")
        warnings.append(f"The replication section could not read the peer array ({b.err}); the peer's columns are empty.")

    # -- partner array and partnership
    transport = _add_rc_partnership(doc, data, a, b)

    # -- SPEC-020 R6: the measured latency; SPEC-031 R6: over Fibre Channel, the typed one
    if transport == "FC":
        _add_typed_latency(doc, data)
    elif data.link_check:
        _add_link_check(doc, data)

    # -- groups configured by this run
    groups = _add_rc_configured_groups(doc, data, a, b, warnings)

    # -- groups the run did not create
    add_para(doc, "Replication already present", bold=True)
    ours = {row["name"] for row in groups}
    others = [g for g in (a.view.groups if a.view is not None else []) if g.name not in ours]
    if a.view is None:
        add_para(doc, "Not known: this array could not be read.")
    elif not others:
        add_para(doc, f"No other Remote Copy groups are on {a.name}.")
    else:
        add_para(doc, "Groups on this array that this run did not configure. Listed for the record; not changed by the tool.")
        add_table(doc, ["Group", "Target", "Mode", "Role here", "Status", "Volumes"],
                  [[g.name, g.target, g.mode + (f" every {g.period}" if g.period else ""), g.role, g.status, str(len(g.volumes))] for g in others],
                  widths=[0.28, 0.22, 0.14, 0.10, 0.12, 0.14])

    # -- what was run and how to undo it
    _add_rc_apply_record(doc, data, a.name, b.name)
