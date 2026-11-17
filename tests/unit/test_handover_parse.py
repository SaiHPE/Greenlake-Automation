"""SPEC-026 R4 to R7 parsers, pinned to the read-only captures taken by lab/handover_capture.py
(tests/fixtures/handover/README.md): rack13-ARCUS (HPE Alletra Storage MP B10230, OS 10.6.0) on
2026-11-16, and D22U27 (OS 10.5.0), E18U31 (OS 10.5.60) and VZ (OS 10.5.51) on 2026-11-17.

Every value asserted here is printed in those files. rack13 was idle on its host ports and had nine
New alerts: the alert table, an idle baseline and an empty Remote Copy report. The OS 10.5.x captures
add a long alert list (D22U27, 525), the array's words for no alert (E18U31), host I/O (D22U27, and
E18U31 on its iSCSI ports), Remote Copy group rows (VZ) and the corrected CPU and port forms.
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alletra_onboard.application.documents import handover as h
from alletra_onboard.application.documents.asbuilt_parse import parse_checkhealth
from alletra_onboard.application.documents.verification import _health_issues

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
RACK13 = FIXTURES / "handover" / "rack13"
D22U27 = FIXTURES / "handover" / "D22U27"   # OS 10.5.0, 525 alerts, host I/O on FC
E18U31 = FIXTURES / "handover" / "E18U31"   # OS 10.5.60, no alert, host I/O on iSCSI
VZ = FIXTURES / "handover" / "VZ"           # OS 10.5.51, 31 alerts, two Remote Copy groups
OS_10_5 = (D22U27, E18U31, VZ)


def _capture(name: str, folder: Path = RACK13) -> str:
    """A capture without its '# command' header line: what the SSH client returns."""
    text = (folder / name).read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


def _summary(name: str, folder: Path = RACK13) -> h.SrSummary:
    return h.parse_srstat_summary(_capture(name, folder), name)


# ---- showalert -d -----------------------------------------------------------------------------------

def test_showalert_d_reads_every_alert_in_the_arrays_words():
    alerts = h.parse_alerts(_capture("showalert_d.txt"))
    assert [a.id for a in alerts] == [27, 28, 31, 34, 36, 37, 38, 39, 40]
    assert {a.state for a in alerts} == {"New"}
    assert Counter(a.severity for a in alerts) == {"Major": 3, "Critical": 2, "Informational": 2, "Degraded": 2}
    switch = next(a for a in alerts if a.id == 31)
    assert switch == h.Alert(
        id=31, state="New", severity="Critical", time="2026-11-11 23:23:04 IST", message_code="0x0b90007",
        type="The configuration of switch is not synchronized",
        message="Switch sw1 Running/startup_config mismatched.", component="hw_switch:sw1",
    )
    sfp = next(a for a in alerts if a.id == 38)
    assert sfp.message == "Port 1:4:2, SFP Degraded (Unqualified, check for unsupported SFP or cable)"
    assert sfp.component == "sw_port:1:4:2,hw_sfp"


def test_alert_time_is_the_latest_occurrence_and_the_repeat_line_gives_the_first():
    """LESSONS 24: the alert's own Time moved to the capture minute; it first happened five days earlier."""
    alerts = {a.id: a for a in h.parse_alerts(_capture("showalert_d.txt"))}
    cloud = alerts[40]
    assert cloud.time == "2026-11-16 23:25:20 IST"
    assert cloud.local_time == datetime(2026, 11, 16, 23, 25, 20)
    assert (cloud.occurrences, cloud.first_time) == (240, "2026-11-11 23:54:31 IST")
    assert cloud.first_seen_local == datetime(2026, 11, 11, 23, 54, 31)
    assert all(a.first_seen == a.time and a.occurrences == 1 for i, a in alerts.items() if i != 40)
    oldest = min(alerts.values(), key=lambda a: a.first_seen_local)
    assert (oldest.id, oldest.first_seen) == (27, "2026-11-11 23:22:51 IST")


def test_plain_showalert_agrees_but_hides_the_first_occurrence():
    """Why the tool reads -d: without it alert 40 looks as if it first happened during the run."""
    detailed = h.parse_alerts(_capture("showalert_d.txt"))
    plain = h.parse_alerts(_capture("showalert.txt"))
    keys = ("id", "state", "severity", "time", "message_code", "type", "message")
    assert [[getattr(a, k) for k in keys] for a in plain] == [[getattr(a, k) for k in keys] for a in detailed]
    assert plain[-1].first_seen == "2026-11-16 23:25:20 IST" and plain[-1].component == ""


def test_checkhealth_alert_rows_are_the_same_alerts_without_time_or_severity():
    alerts = h.parse_alerts(_capture("showalert_d.txt"))
    _summary_rows, detail = parse_checkhealth(_capture("checkhealth_svc_detail.txt"))
    alert_rows = [(ident, text) for component, ident, text, _res in detail if component == "Alert"]
    assert alert_rows == [(a.component, a.message) for a in alerts]


def test_alert_count_must_match_the_arrays_own_count():
    text = _capture("showalert_d.txt")
    last = text.index("Id          : 40")
    with pytest.raises(h.UnreadableReport, match="counts 9 alerts, 8 were read"):
        h.parse_alerts(text[:last] + "9 alerts\n")


def test_a_refusal_or_another_report_is_never_read_as_no_alerts():
    with pytest.raises(h.UnreadableReport, match="Error: Invalid option -x"):
        h.parse_alerts("Error: Invalid option -x\n")
    with pytest.raises(h.UnreadableReport, match="printed nothing"):
        h.parse_alerts("")
    with pytest.raises(h.UnreadableReport):
        h.parse_alerts(_capture("srstatvv_24h.txt"))
    with pytest.raises(h.UnreadableReport):
        h.parse_alerts(_capture("help_showalert.txt"))


# ---- showsys -space ---------------------------------------------------------------------------------

def test_showsys_space_capacity():
    space = h.parse_space(_capture("showsys_space.txt"))
    assert (space.raw_total_mib, space.raw_allocated_mib, space.raw_free_mib) == (21958656, 540672, 18957312)
    assert (space.usable_total_mib, space.usable_used_mib, space.usable_free_mib) == (15174810, 90039, 15084771)
    assert space.reduction == "8.46"
    assert [h.tib(m) for m in (space.raw_total_mib, space.usable_total_mib, space.usable_used_mib,
                               space.usable_free_mib)] == [20.9, 14.5, 0.1, 14.4]
    # Same key names in different places: the indent and the section tell them apart.
    assert space.get("Raw Capacity", "Total", "System", "Metadata").text == "473088"
    assert space.get("Usable Capacity", "Total", "Used", "Metadata").text == "7735"
    efficiency = space.get("Efficiency", "Total")
    assert (efficiency.unit, efficiency.text, efficiency.number) == ("", ">25", None)
    assert space.mib("Efficiency", "Reduction") is None  # a ratio, never read as MiB


def test_raw_space_matches_the_showsys_columns():
    space = h.parse_space(_capture("showsys_space.txt"))
    header, row = _capture("showsys.txt").splitlines()[1:3]
    assert header.split()[-4:] == ["TotalCap", "AllocCap", "FreeCap", "FailedCap"]
    total, alloc, free, _failed = (int(v) for v in row.split()[-4:])
    assert (space.raw_total_mib, space.raw_allocated_mib, space.raw_free_mib) == (total, alloc, free)


def test_space_refusal_raises():
    with pytest.raises(h.UnreadableReport, match="Error: Invalid option"):
        h.parse_space("Error: Invalid option -spaced\n")


# ---- System Reporter summaries ----------------------------------------------------------------------

def test_cpu_summary_per_node_and_its_window():
    summary = _summary("srstatcpu_24h.txt")
    assert summary.start_text == "2026-11-15 23:28:34 IST"
    assert summary.start == datetime(2026, 11, 15, 17, 58, 34, tzinfo=UTC)
    assert summary.end == datetime(2026, 11, 16, 17, 55, tzinfo=UTC)  # the last 5-minute sample
    assert summary.groupby == ("NODE",)
    assert summary.columns == ("User%", "Sys%", "Idle%", "Intr/s", "CtxtSw/s")
    # The array prints Avg, Max, then the percentile, whatever order the command asked for.
    assert [r.stat for r in summary.rows] == ["avg", "avg", "max", "max", "95%", "95%"]
    nodes = {n.node: n for n in h.cpu_by_node(summary)}
    assert list(nodes) == ["0", "1"]
    assert nodes["0"].stats == {
        "avg": h.CpuFigures(7.3, 0.5, 92.2),
        "max": h.CpuFigures(10.0, 1.0, 92.5),
        "95%": h.CpuFigures(7.40, 0.60, 92.40),
    }
    assert (nodes["0"].busy_avg, nodes["1"].busy_avg) == (7.8, 7.5)


def test_cpu_max_row_is_per_column_so_the_busiest_sample_is_unknown():
    """Node 1's Max row has Idle% 92.8, above its average: the most idle sample, not the busiest.
    The R3 form asks for no min or 5% row, so busy max and busy 95% stay unknown, never guessed."""
    node1 = {n.node: n for n in h.cpu_by_node(_summary("srstatcpu_24h.txt"))}["1"]
    assert node1.stats["max"].idle_pct > node1.stats["avg"].idle_pct
    assert node1.stats["max"].user_pct == 11.2
    assert node1.busy_max is None and node1.busy_p95 is None


def test_host_ports_summary_per_port():
    summary = _summary("srstatport_24h.txt")
    assert summary.groupby == ("PORT_N", "PORT_S", "PORT_P")
    assert summary.columns[:3] == ("IO/s Rd", "IO/s Wr", "IO/s Tot")
    assert summary.columns[-2:] == ("QLen", "AvgBusy%")
    assert "Svct ms Tot" in summary.columns and "KBytes/s Tot" in summary.columns
    ports = h.ports_by_port(summary)
    assert [p.name for p in ports] == ["0:3:4", "0:4:1", "1:3:3", "1:4:1"]
    zero = h.IoFigures(0.0, 0.0, 0.0)  # printed by the array as 0.0 / 0.000, not missing
    assert all(p.stats == {"avg": zero, "max": zero, "95%": zero} for p in ports)


def test_volumes_summary_for_the_whole_array():
    summary = _summary("srstatvv_24h.txt")
    assert summary.groupby == ()
    load = h.volumes_total(summary)
    assert load.stats == {
        "avg": h.IoFigures(27.6, 167.8, 0.230),
        "max": h.IoFigures(104.9, 2351.0, 0.268),
        "95%": h.IoFigures(30.76, 186.78, 0.260),
    }


def test_an_idle_array_still_shows_volume_io_while_its_host_ports_are_zero():
    """SPEC-026 R6 as proposed would call rack13 busy: the volumes carry about 28 IO/s of the array's
    own I/O with no host I/O at all. The spec now says which figure decides "idle"."""
    volumes = h.volumes_total(_summary("srstatvv_24h.txt"))
    ports = h.ports_by_port(_summary("srstatport_24h.txt"))
    assert volumes.stats["avg"].iops > 10
    assert sum(p.stats["avg"].iops for p in ports) == 0.0


def test_remote_copy_summary_with_no_group_is_empty_and_says_so():
    """rack13 has no Remote Copy group: System Reporter prints the header and an End Time of epoch 0."""
    summary = _summary("srstatrcvv_24h.txt")
    assert summary.groupby == ("GROUP_NAME",)
    assert summary.columns == ("IO/s Lcl", "IO/s Rmt", "KBytes/sec Lcl", "KBytes/sec Rmt",
                               "Svct(ms) Lcl", "Svct(ms) Rmt", "IOSz KB Lcl", "RPO")
    assert summary.rows == ()
    assert summary.start == datetime(2026, 11, 15, 17, 58, 39, tzinfo=UTC)
    assert summary.end is None and summary.end_text == "1970-01-01 05:30:00 IST"
    assert h.rc_by_group(summary) == []


@pytest.mark.parametrize("name, folder", [
    ("srstatcpu.txt", RACK13), ("srstatport.txt", RACK13), ("srstatvv.txt", RACK13),
    ("srstatrcvv.txt", RACK13), ("D22U27/srstatrcvv_hourly.txt", FIXTURES / "rc_pair"),
])
def test_a_time_series_report_is_not_read_as_a_summary(name, folder):
    """The plain forms print one row per sample; read as a summary the all-zero hourly capture would
    look like an idle array. It is refused instead."""
    with pytest.raises(h.UnreadableReport, match="not a System Reporter summary"):
        h.parse_srstat_summary(_capture(name, folder), name)


def test_a_refused_or_misshapen_summary_raises():
    with pytest.raises(h.UnreadableReport, match="Error: Invalid option -port_tipe"):
        h.parse_srstat_summary("Error: Invalid option -port_tipe\n", "srstatport")
    with pytest.raises(h.UnreadableReport, match="a summary line we cannot read"):
        h.parse_srstat_summary(_capture("srstatcpu_24h.txt") + "    Avg    2   7.3\n", "srstatcpu")
    with pytest.raises(h.UnreadableReport, match="expected groups NODE"):
        h.cpu_by_node(_summary("srstatvv_24h.txt"))


# ---- checkhealth -svc -detail on OS 10.6.0 (the existing parsers) -----------------------------------

def test_asbuilt_checkhealth_tables_read_os_10_6():
    summary, detail = parse_checkhealth(_capture("checkhealth_svc_detail.txt"))
    assert len(summary) == 10 and sum(int(q) for _c, _d, q in summary) == 40  # "10 total 40"
    assert summary[0] == ("Alert", "New alerts", "9")
    assert ("PD", "PDs that are degraded", "12") in summary
    assert ("Security", "System with remote root access enabled", "1") in summary
    assert len(detail) == 40  # "40 total"
    assert detail[0] == ("Alert", "sw_ilo:0", "Unable to register ssh key for iLO on Node 0", "Manual")
    assert ("Cage", "cage:41", "Firmware is not current", "Auto") in detail
    assert not any("autofix" in " ".join(row) for row in summary + detail)


def test_verify_checkhealth_issues_read_os_10_6():
    issues = _health_issues(_capture("checkhealth_svc_detail.txt"))
    assert [i.component for i in issues] == ["Alert", "Cage", "Cage", "iLO", "PD", "Port", "Security",
                                             "Switch", "Switch", "vlun"]
    assert sum(i.qty for i in issues) == 40
    by_component = {i.component: i for i in issues}
    assert len(by_component["Alert"].details) == 9
    assert len(by_component["PD"].details) == 12
    assert [d.identifier for d in by_component["Port"].details] == ["port:0:4:2", "port:1:4:2"]


# ---- OS 10.5.x: D22U27, E18U31, VZ (2026-11-17) -----------------------------------------------------

@pytest.mark.parametrize("name", ["showalert.txt", "showalert_d.txt"])
def test_an_array_with_no_alert_gives_an_empty_list(name):
    """E18U31 (OS 10.5.60) prints one line for both forms. It is read as no alerts, never as an error."""
    text = _capture(name, E18U31)
    assert text == "no alerts\n"
    assert h.parse_alerts(text) == []


@pytest.mark.parametrize("text", ["no alerts found\n", "no alerts\nId          : 1\n", "No alerts on node 0\n"])
def test_only_the_arrays_exact_words_mean_no_alerts(text):
    with pytest.raises(h.UnreadableReport):
        h.parse_alerts(text)


def test_a_long_alert_list_is_read_in_full():
    """D22U27 (OS 10.5.0): 525 New alerts, 4201 lines plain and 5255 with -d, all read and counted."""
    detailed = h.parse_alerts(_capture("showalert_d.txt", D22U27))
    plain = h.parse_alerts(_capture("showalert.txt", D22U27))
    assert len(detailed) == len(plain) == len({a.id for a in detailed}) == 525
    assert {a.state for a in detailed} == {"New"}
    assert Counter(a.severity for a in detailed) == {"Minor": 521, "Major": 4}
    assert Counter(a.type for a in detailed)["Task failed"] == 521
    keys = ("id", "state", "severity", "time", "message_code", "type", "message")
    assert [[getattr(a, k) for k in keys] for a in plain] == [[getattr(a, k) for k in keys] for a in detailed]
    assert sum(1 for a in detailed if a.first_time) == 4
    assert all(a.component for a in detailed) and not any(a.component for a in plain)


def test_an_alert_from_last_year_looks_new_without_its_repeat_line():
    """LESSONS 24 on D22U27: alert 10's Time is 13 minutes before the capture; it first happened almost
    eleven months earlier. Only -d says so, and it is the oldest alert by first occurrence, not by Time."""
    alerts = {a.id: a for a in h.parse_alerts(_capture("showalert_d.txt", D22U27))}
    cloud = alerts[10]
    assert (cloud.severity, cloud.component) == ("Major", "sw_wsapi")
    assert cloud.type == "Disconnected from Data Services Cloud Console for a prolonged period of time"
    assert cloud.time == "2026-11-16 23:50:26 IST"
    assert (cloud.occurrences, cloud.first_time) == (2285, "2025-12-26 21:11:20 IST")
    assert min(alerts.values(), key=lambda a: a.first_seen_local) is cloud
    assert min(alerts.values(), key=lambda a: a.local_time).time == "2026-09-30 20:00:00 IST"
    plain = {a.id: a for a in h.parse_alerts(_capture("showalert.txt", D22U27))}
    assert plain[10].first_seen == "2026-11-16 23:50:26 IST"


@pytest.mark.parametrize("folder", [RACK13, D22U27, VZ])
def test_the_array_prints_alerts_by_latest_time_not_by_id(folder):
    alerts = h.parse_alerts(_capture("showalert_d.txt", folder))
    assert [a.local_time for a in alerts] == sorted(a.local_time for a in alerts)


def test_vz_alerts_and_their_order():
    alerts = h.parse_alerts(_capture("showalert_d.txt", VZ))
    assert len(alerts) == 31 and {a.state for a in alerts} == {"New"}
    assert Counter(a.severity for a in alerts) == {"Minor": 18, "Major": 8, "Degraded": 4, "Informational": 1}
    assert sum(1 for a in alerts if a.first_time) == 12
    # By latest Time, so the alerts still repeating since June (cloud connection, Remote Copy links and
    # target: ids 11 to 21) come last.
    assert [a.id for a in alerts][-7:] == [42, 11, 13, 12, 14, 15, 21]
    link = next(a for a in alerts if a.id == 12)
    assert link.message == "Remote Copy Link 1(MPB10K-E24U21-LZ_0_4_3) Failed (Down Due To Send Error Or Missing Heartbeat)"
    assert (link.occurrences, link.first_time) == (881, "2026-06-24 10:57:57 IST")


@pytest.mark.parametrize("folder, alerts", [(D22U27, 525), (VZ, 31)])
def test_checkhealth_alert_rows_are_the_same_alerts_on_os_10_5(folder, alerts):
    parsed = h.parse_alerts(_capture("showalert_d.txt", folder))
    summary, detail = parse_checkhealth(_capture("checkhealth_svc_detail.txt", folder))
    assert summary[0] == ("Alert", "New alerts", str(alerts))
    assert [(ident, text) for component, ident, text, _res in detail if component == "Alert"] == \
        [(a.component, a.message) for a in parsed]


@pytest.mark.parametrize("folder, rows, total", [(D22U27, 13, 565), (E18U31, 5, 9), (VZ, 14, 96)])
def test_checkhealth_tables_read_os_10_5(folder, rows, total):
    summary, detail = parse_checkhealth(_capture("checkhealth_svc_detail.txt", folder))
    assert len(summary) == rows and sum(int(q) for _c, _d, q in summary) == total == len(detail)
    assert sum(i.qty for i in _health_issues(_capture("checkhealth_svc_detail.txt", folder))) == total


def test_no_alert_and_no_checkhealth_alert_row_agree():
    summary, detail = parse_checkhealth(_capture("checkhealth_svc_detail.txt", E18U31))
    assert not any(c == "Alert" for c, _d, _q in summary) and not any(row[0] == "Alert" for row in detail)


@pytest.mark.parametrize("folder, raw, usable, reduction", [
    (D22U27, (29278208, 947899, 24457541), (19890325, 1381934, 18508391), "1.05"),
    (E18U31, (29278208, 106859, 25006741), (19517890, 89049, 19428841), "1.69"),
    (VZ, (43929600, 696198, 37244026), (29547910, 599314, 28948596), ">25"),
])
def test_showsys_space_on_os_10_5(folder, raw, usable, reduction):
    space = h.parse_space(_capture("showsys_space.txt", folder))
    assert (space.raw_total_mib, space.raw_allocated_mib, space.raw_free_mib) == raw
    assert (space.usable_total_mib, space.usable_used_mib, space.usable_free_mib) == usable
    assert space.reduction == reduction
    total, alloc, free, _failed = (int(v) for v in _capture("showsys.txt", folder).splitlines()[2].split()[-4:])
    assert raw == (total, alloc, free)


def test_os_10_5_space_has_a_third_level_under_raw_free():
    """OS 10.5.x prints VV Preallocated, CPG Preallocated and Unallocated under Raw > Usable > Free;
    OS 10.6.0 does not. The indent places them; the figures the as-built uses are unchanged."""
    space = h.parse_space(_capture("showsys_space.txt", D22U27))
    assert space.get("Raw Capacity", "Total", "Usable", "Free", "Unallocated").text == "22013952"
    assert h.parse_space(_capture("showsys_space.txt")).get("Raw Capacity", "Total", "Usable", "Free",
                                                             "Unallocated") is None
    vz = h.parse_space(_capture("showsys_space.txt", VZ))
    dedup = vz.get("Efficiency", "Dedup")
    assert (dedup.text, dedup.number) == ("-", None)


@pytest.mark.parametrize("folder, busy", [
    (D22U27, {"0": (3.5, 3.5, 6.0), "1": (4.2, 4.3, 5.8)}),
    (E18U31, {"0": (3.9, 3.9, 5.5), "1": (3.7, 3.8, 6.3)}),
    (VZ, {"0": (7.2, 7.2, 10.2), "1": (6.7, 6.7, 11.0)}),
])
def test_corrected_cpu_form_gives_the_busiest_sample_and_95_percent_busy(folder, busy):
    """srstatcpu ... -summary min,avg,5%,95%,max,per_group answered on all three. Busy average, 95% and
    busiest are 100 minus Idle% avg, 5% and min; the old form leaves the last two unknown."""
    summary = _summary("srstatcpu_24h_v2.txt", folder)
    assert [r.stat for r in summary.rows] == ["avg", "avg", "max", "max", "min", "min", "5%", "95%", "5%", "95%"]
    nodes = {n.node: n for n in h.cpu_by_node(summary)}
    assert {k: (n.busy_avg, n.busy_p95, n.busy_max) for k, n in nodes.items()} == busy
    old = {n.node: n for n in h.cpu_by_node(_summary("srstatcpu_24h.txt", folder))}
    assert all(old[k].busy_max is None and old[k].busy_p95 is None for k in old)
    for k, node in nodes.items():  # the rows both forms print are the same figures
        assert {s: node.stats[s] for s in ("avg", "max", "95%")} == old[k].stats


def test_cpu_min_and_5_percent_rows_on_d22u27():
    node0 = {n.node: n for n in h.cpu_by_node(_summary("srstatcpu_24h_v2.txt", D22U27))}["0"]
    assert node0.stats["min"] == h.CpuFigures(3.3, 0.1, 94.0)
    assert node0.stats["5%"] == h.CpuFigures(3.30, 0.10, 96.50)


IDLE_IOPS = h.IDLE_IOPS  # SPEC-026 R6


def _avg_iops(ports: list[h.IoLoad]) -> dict[str, float]:
    return {p.name: p.stats["avg"].iops for p in ports}


def test_host_and_iscsi_form_adds_the_iscsi_ports_and_changes_the_idle_verdict():
    """E18U31: -port_type host lists its four FC host ports (2.7 IO/s together, below IDLE_IOPS = 10);
    host,iscsi adds its four ready iSCSI ports (0:4:1, 0:4:2, 1:4:1, 1:4:2), which carry most of its
    host I/O: 26.3 IO/s together. SPEC-026 §2a correction 3, confirmed."""
    fc = h.ports_by_port(_summary("srstatport_24h.txt", E18U31))
    both = h.ports_by_port(_summary("srstatport_24h_v2.txt", E18U31))
    assert [p.name for p in fc] == ["0:3:1", "0:3:4", "1:3:1", "1:3:4"]
    assert [p.name for p in both] == ["0:3:1", "0:3:4", "0:4:1", "0:4:2", "1:3:1", "1:3:4", "1:4:1", "1:4:2"]
    iscsi = {k: v for k, v in _avg_iops(both).items() if k not in _avg_iops(fc)}
    assert iscsi == {"0:4:1": 10.7, "0:4:2": 10.7, "1:4:1": 1.1, "1:4:2": 1.1}
    fc_only, with_iscsi = round(sum(_avg_iops(fc).values()), 1), round(sum(_avg_iops(both).values()), 1)
    assert (fc_only, with_iscsi) == (2.7, 26.3)
    assert fc_only < IDLE_IOPS < with_iscsi
    fc_rows = {p.name: p.stats for p in fc}
    assert all(p.stats == fc_rows[p.name] for p in both if p.name in fc_rows)


def test_iscsi_ports_with_no_host_print_zero_rows():
    """VZ: the iscsi type lists every iSCSI port, configured or not; its four are offline and print 0.0."""
    fc = h.ports_by_port(_summary("srstatport_24h.txt", VZ))
    both = h.ports_by_port(_summary("srstatport_24h_v2.txt", VZ))
    zero = h.IoFigures(0.0, 0.0, 0.0)
    added = [p for p in both if p.name not in {q.name for q in fc}]
    assert [p.name for p in added] == ["0:4:1", "0:4:2", "1:4:1", "1:4:2"]
    assert all(p.stats == {"avg": zero, "max": zero, "95%": zero} for p in added)
    assert round(sum(_avg_iops(both).values()), 1) == round(sum(_avg_iops(fc).values()), 1) == 0.9


def test_an_array_with_host_io_on_fc():
    """D22U27 has no iSCSI port, so both forms print the same five FC host ports, 44.2 IO/s together:
    the first capture above IDLE_IOPS. Its volumes average 96.0 IO/s."""
    fc = h.ports_by_port(_summary("srstatport_24h.txt", D22U27))
    both = h.ports_by_port(_summary("srstatport_24h_v2.txt", D22U27))
    assert [p.name for p in fc] == ["0:3:1", "0:3:4", "1:3:1", "1:3:2", "1:3:4"]
    assert [(p.name, p.stats) for p in both] == [(p.name, p.stats) for p in fc]
    host_io = round(sum(_avg_iops(fc).values()), 1)
    assert host_io == 44.2 and host_io > IDLE_IOPS
    assert fc[2].stats["max"] == h.IoFigures(23.2, 309.8, 0.475)
    assert h.volumes_total(_summary("srstatvv_24h.txt", D22U27)).stats["avg"] == h.IoFigures(96.0, 1986.8, 0.320)


def test_remote_copy_rows_per_group_with_the_rpo_as_printed():
    """VZ has two Remote Copy groups. RPO prints "-", "0" or a date and time with a space in it."""
    summary = _summary("srstatrcvv_24h.txt", VZ)
    assert summary.start == datetime(2026, 11, 15, 18, 39, 31, tzinfo=UTC)
    assert summary.end == datetime(2026, 11, 16, 18, 30, tzinfo=UTC)
    groups = {g.group: g for g in h.rc_by_group(summary)}
    assert list(groups) == ["LZ_RcopyGroup1.r194089", "Recover_back"]
    assert groups["LZ_RcopyGroup1.r194089"].stats == {
        "avg": h.RcFigures(7.2, 0.0, 0.08, 0.0, "-"),
        "max": h.RcFigures(185.3, 0.0, 0.87, 0.0, "0"),
    }
    assert groups["Recover_back"].stats == {
        "avg": h.RcFigures(0.0, 0.0, 0.0, 0.0, "2026-07-20 13:11:32"),
        "max": h.RcFigures(0.0, 0.0, 0.0, 0.0, "2026-07-20 13:11:32"),
    }


def test_only_a_words_column_may_hold_a_space():
    with pytest.raises(h.UnreadableReport, match="a summary line we cannot read"):
        h.parse_srstat_summary(_capture("srstatcpu_24h_v2.txt", VZ) + "    Avg    2 6.7 0.4 92.8 1.0 2.0 3.0\n",
                               "srstatcpu")


@pytest.mark.parametrize("folder", [D22U27, E18U31])
def test_remote_copy_summary_with_no_sample_on_os_10_5(folder):
    """D22U27's six groups are not started (its checkhealth says so); E18U31 prints no group row either.
    Both print epoch 0 as End: no sample, not a time."""
    summary = _summary("srstatrcvv_24h.txt", folder)
    assert summary.rows == () and summary.end is None and h.rc_by_group(summary) == []


@pytest.mark.parametrize("folder", OS_10_5)
@pytest.mark.parametrize("name", ["srstatcpu.txt", "srstatport.txt", "srstatvv.txt", "srstatrcvv.txt"])
def test_os_10_5_time_series_reports_are_not_read_as_summaries(folder, name):
    with pytest.raises(h.UnreadableReport, match="not a System Reporter summary"):
        h.parse_srstat_summary(_capture(name, folder), name)


# ---- At handover: the five reads together (work packet step 4) --------------------------------------

PEER_PORTS = FIXTURES / "peer_ports"   # showport from the same lab arrays (BL-26, 2026-11-16 and 17)
V2 = {RACK13: ("srstatcpu_24h.txt", "srstatport_24h.txt")}   # rack13 has no corrected forms


def _reads(folder: Path, *, showport: str = "", errors: dict | None = None, run_created_at=None,
           ports: str | None = None, **texts: str) -> h.HandoverReads:
    """The five reads of one capture folder, as the as-built step would have them."""
    cpu, port = V2.get(folder, ("srstatcpu_24h_v2.txt", "srstatport_24h_v2.txt"))
    files = {h.ALERTS: "showalert_d.txt", h.SPACE: "showsys_space.txt", h.CPU: cpu, h.PORTS: ports or port,
             h.VOLUMES: "srstatvv_24h.txt"}
    captured = {cmd: _capture(name, folder) for cmd, name in files.items()}
    captured.update(texts)
    return h.read_handover(captured, errors or {}, showport=showport, run_created_at=run_created_at,
                           read_at=datetime(2026, 11, 16, 18, 0, tzinfo=UTC))


@pytest.mark.parametrize("folder, name", [
    (RACK13, "srstatcpu_24h.txt"), (RACK13, "srstatvv_24h.txt"), (RACK13, "srstatrcvv_24h.txt"),
    (D22U27, "srstatcpu_24h_v2.txt"), (E18U31, "srstatport_24h_v2.txt"), (VZ, "srstatvv_24h.txt"),
])
def test_the_arrays_utc_offset_comes_from_a_start_time_line(folder, name):
    """Every lab array is in India: +05:30, from the local time and the epoch on one line, without
    reading the zone's name (ADR 0019 change 5). An empty Remote Copy report still has a Start Time."""
    offset = h.utc_offset(_summary(name, folder))
    assert offset == timedelta(hours=5, minutes=30)
    assert h.offset_text(offset) == "UTC+05:30"


def test_no_system_reporter_read_means_no_offset():
    assert h.utc_offset(None, None, None) is None
    reads = _reads(RACK13, errors={h.CPU: "refused", h.PORTS: "refused", h.VOLUMES: "refused"})
    assert reads.offset is None and reads.window is None


def test_the_first_summary_that_parsed_gives_the_offset_and_the_window():
    reads = _reads(VZ, errors={h.CPU: "ArrayCliError: refused"})
    assert reads.window is reads.ports
    assert reads.offset == timedelta(hours=5, minutes=30)


def test_before_this_run_uses_the_first_occurrence_and_the_arrays_offset():
    """rack13: alert 27 first happened 2026-11-11 23:22:51 IST (17:52:51 UTC), alert 40 at 23:54:31 IST
    (18:24:31 UTC) though its Time is the capture minute. A run created at 18:00 UTC that day sits
    between them."""
    alerts = {a.id: a for a in h.parse_alerts(_capture("showalert_d.txt"))}
    offset = timedelta(hours=5, minutes=30)
    created = datetime(2026, 11, 11, 18, 0, tzinfo=UTC)
    assert h.before_run(alerts[27], offset, created) is True
    assert h.before_run(alerts[40], offset, created) is False
    assert h.before_run(alerts[40], offset, datetime(2026, 11, 16, 17, 0, tzinfo=UTC)) is True
    assert h.before_run(alerts[40], None, created) is None            # no System Reporter read: unknown
    assert h.before_run(alerts[40], offset, None) is None


@pytest.mark.parametrize("folder, alert_id", [(RACK13, 40), (D22U27, 10), (VZ, 11), (E18U31, None)])
def test_the_cloud_alert_is_the_arrays_own(folder, alert_id):
    alerts = h.parse_alerts(_capture("showalert_d.txt", folder))
    cloud = h.cloud_alert(alerts)
    assert (cloud.id if cloud else None) == alert_id
    if cloud:
        assert cloud.severity == "Major" and cloud.message_code == "0x060000a"
        assert "disconnected from Data Services Cloud Console" in cloud.message


@pytest.mark.parametrize("folder, full, groups", [(RACK13, 5, 2), (D22U27, 4, 1), (VZ, 8, 3), (E18U31, 0, 0)])
def test_alert_table_lists_major_and_worse_in_full_and_groups_the_rest(folder, full, groups):
    """SPEC-026 §4: rack13 5 rows in full and 2 groups, D22U27 4 and 1, VZ 8 and 3."""
    alerts = h.parse_alerts(_capture("showalert_d.txt", folder))
    rows, grouped = h.alert_table(alerts)
    assert (len(rows), len(grouped)) == (full, groups)
    assert {a.severity for a in rows} <= {"Major", "Critical", "Fatal"}
    assert len(rows) + sum(g.count for g in grouped) == len(alerts)       # none dropped
    assert [a.local_time for a in rows] == sorted((a.local_time for a in rows), reverse=True)


def test_rack13_alert_groups():
    rows, groups = h.alert_table(h.parse_alerts(_capture("showalert_d.txt")))
    assert [a.id for a in rows] == [40, 34, 31, 28, 27]          # newest Time first; 27 and 28 share theirs
    assert [(g.severity, g.message_code, g.count, [a.id for a in g.alerts]) for g in groups] == [
        ("Degraded", "0x02900de", 2, [39, 38]), ("Informational", "0x02d0003", 2, [37, 36])]
    degraded = groups[0]
    assert (degraded.first_seen, degraded.latest) == ("2026-11-11 23:24:01 IST", "2026-11-11 23:24:37 IST")


def test_d22u27_groups_521_task_failures_in_one_row():
    rows, groups = h.alert_table(h.parse_alerts(_capture("showalert_d.txt", D22U27)))
    assert {a.severity for a in rows} == {"Major"}
    (tasks,) = groups
    assert (tasks.severity, tasks.message_code, tasks.count) == ("Minor", "0x00e000a", 521)
    assert tasks.first_seen == "2026-09-30 20:00:00 IST"                 # the earliest of the 521
    assert tasks.latest == tasks.alerts[0].time and tasks.sample == tasks.alerts[0].message
    assert tasks.alerts[0].local_time == max(a.local_time for a in tasks.alerts)


def test_alerts_verdict_and_the_cloud_sentence():
    rack13 = h.parse_alerts(_capture("showalert_d.txt"))
    assert h.alerts_verdict(rack13) == (
        "9 new alerts; the oldest first occurred on 2026-11-11 23:22:51 IST. Alerts record an event, not the "
        "current state: compare each with checkhealth before acting. The array reports it is disconnected "
        "from Data Services Cloud Console (alert 40).")
    assert h.alerts_verdict([]) == "No new alerts."
    no_cloud = [a for a in rack13 if a.id != 40]
    assert "Data Services Cloud Console" not in h.alerts_verdict(no_cloud)
    assert h.alerts_verdict(no_cloud[:1]).startswith("1 new alert; it first occurred on 2026-11-11 23:22:51 IST.")


def test_the_three_cloud_lines():
    rack13 = h.parse_alerts(_capture("showalert_d.txt"))
    assert h.cloud_line(rack13) == (
        'Cloud connection: the array reports it is disconnected from Data Services Cloud Console (alert 40: '
        '"Storage system has been disconnected from Data Services Cloud Console for more than 7200 minutes."). '
        "The tool did not read HPE's cloud view of this array (call-home).")
    assert h.cloud_line([]) == ("Cloud connection: the array has no New alert about it. The tool did not read "
                                "HPE's cloud view of this array (cloud connection, call-home).")
    assert h.cloud_line(None) == ("Cloud connection: unknown, the alerts could not be read. The tool did not "
                                  "read HPE's cloud view of this array (cloud connection, call-home).")


def test_ports_showport_does_not_report_ready_are_named_in_one_line():
    """VZ (SPEC-026 §2a item 9): its four iSCSI ports are offline with type free in showport and print
    all-zero rows. They leave the table and are named, never dropped."""
    loads = h.ports_by_port(_summary("srstatport_24h_v2.txt", VZ))
    roles = _roles(PEER_PORTS / "VZ" / "showport.txt")
    rows, lines = h.split_ports(loads, roles)
    assert [(r.load.name, r.protocol) for r in rows] == [("0:3:1", "FC"), ("0:3:2", "FC"), ("1:3:1", "FC"), ("1:3:2", "FC")]
    assert lines == ["4 iSCSI ports not configured, no I/O: 0:4:1, 0:4:2, 1:4:1, 1:4:2."]


@pytest.mark.parametrize("folder, showport", [
    (E18U31, FIXTURES / "rc_pair" / "E18U31" / "showport.txt"),
    (E18U31, PEER_PORTS / "E18U31" / "showport.txt"),
    (D22U27, PEER_PORTS / "D22U27" / "showport.txt"),
])
def test_ready_ports_all_stay_in_the_table(folder, showport):
    """E18U31's four iSCSI ports are ready and carry most of its host I/O; D22U27's five FC ports are ready."""
    loads = h.ports_by_port(_summary("srstatport_24h_v2.txt", folder))
    rows, lines = h.split_ports(loads, _roles(showport))
    assert [r.load.name for r in rows] == [p.name for p in loads] and lines == []


def test_a_port_that_is_not_ready_but_carried_io_says_so():
    loads = h.ports_by_port(_summary("srstatport_24h_v2.txt", E18U31))
    roles = _roles(PEER_PORTS / "E18U31" / "showport.txt")
    roles["0:4:1"] = roles["0:4:1"].model_copy(update={"state": "loss_sync"})
    del roles["1:4:2"]
    rows, lines = h.split_ports(loads, roles)
    assert "0:4:1" not in [r.load.name for r in rows]
    assert lines == ["1 iSCSI port with no link, with I/O: 0:4:1.", "1 port not listed by showport, with I/O: 1:4:2."]


def test_without_port_states_every_port_is_listed_and_the_line_says_why():
    loads = h.ports_by_port(_summary("srstatport_24h_v2.txt", VZ))
    rows, lines = h.split_ports(loads, {})
    assert len(rows) == 8 and lines == [
        "The ports' states could not be read from showport, so every port System Reporter printed is listed."]


@pytest.mark.parametrize("folder, ports, iops, idle", [
    (RACK13, None, 0.0, True),
    (VZ, None, 0.9, True),
    (E18U31, "srstatport_24h.txt", 2.7, True),          # FC only: the first form called it idle
    (E18U31, None, 26.3, False),                        # with its iSCSI ports: not idle
    (D22U27, None, 44.2, False),
])
def test_idle_is_the_host_ports_summed_average_below_idle_iops(folder, ports, iops, idle):
    reads = _reads(folder, ports=ports)
    assert (reads.host_iops_avg, reads.idle) == (iops, idle)


def test_idle_is_unknown_when_the_ports_could_not_be_read():
    reads = _reads(RACK13, errors={h.PORTS: "ArrayCliError: refused"})
    assert reads.host_iops_avg is None and reads.idle is None


def test_idle_is_unknown_when_the_port_report_has_no_row():
    """A report with no port (no host port, or no sample in the window) is not an idle baseline."""
    text = _capture("srstatport_24h_v2.txt", VZ)
    header_only = text[:text.index("\n", text.index("Summary")) + 1]
    reads = _reads(VZ, **{h.PORTS: header_only})
    assert reads.port_loads == [] and "srstatport" not in " ".join(reads.errors)
    assert reads.host_iops_avg is None and reads.idle is None
    assert (h.summarise(reads).iops_avg, h.summarise(reads).idle) == (None, None)


def test_a_refused_or_unreadable_read_is_an_error_and_the_others_still_parse():
    reads = _reads(VZ, errors={h.CPU: "ArrayCliError: refused: 'srstatcpu' is not a read-only show command"},
                   **{h.SPACE: "Error: Invalid option -space\n", h.VOLUMES: ""})
    assert reads.errors == {
        h.CPU: "ArrayCliError: refused: 'srstatcpu' is not a read-only show command",
        h.SPACE: "Error: Invalid option -space",
        h.VOLUMES: "the array printed nothing",
    }
    assert reads.cpu is reads.cpu_nodes is reads.space is reads.volumes is reads.volume_load is None
    assert len(reads.alerts) == 31 and len(reads.port_loads) == 8


@pytest.mark.parametrize("folder, expected", [
    (RACK13, {"alerts_new": 9, "alerts_major": 5, "oldest_alert": "2026-11-11 23:22:51 IST", "cloud_alert": 40,
              "cpu_max_pct": None, "iops_avg": 0.0, "idle": True,
              "window_from": "2026-11-15T17:58:34+00:00", "window_to": "2026-11-16T17:55:00+00:00"}),
    (D22U27, {"alerts_new": 525, "alerts_major": 4, "oldest_alert": "2025-12-26 21:11:20 IST", "cloud_alert": 10,
              "cpu_max_pct": 6.0, "iops_avg": 44.2, "idle": False}),
    (E18U31, {"alerts_new": 0, "alerts_major": 0, "oldest_alert": None, "cloud_alert": None,
              "cpu_max_pct": 6.3, "iops_avg": 26.3, "idle": False}),
    (VZ, {"alerts_new": 31, "alerts_major": 8, "cloud_alert": 11, "cpu_max_pct": 11.0, "iops_avg": 0.9, "idle": True}),
])
def test_summarise_gives_the_event_fields(folder, expected):
    """SPEC-026 R10. rack13 was captured with the first CPU form: its busiest sample is unknown, not 0."""
    summary = h.summarise(_reads(folder)).as_event()
    assert set(summary) == {"read_at", "window_from", "window_to", "alerts_new", "alerts_major", "oldest_alert",
                            "cloud_alert", "cpu_max_pct", "iops_avg", "idle", "read_errors"}
    assert summary["read_at"] == "2026-11-16T18:00:00+00:00" and summary["read_errors"] == {}
    assert {k: summary[k] for k in expected} == expected


def test_summarise_says_unknown_for_every_read_that_failed():
    failed = {cmd: "ArrayCliError: timed out" for cmd in (h.ALERTS, h.CPU, h.PORTS, h.VOLUMES)}
    summary = h.summarise(_reads(D22U27, errors=failed))
    assert (summary.alerts_new, summary.alerts_major, summary.cloud_alert, summary.cpu_max_pct, summary.iops_avg,
            summary.idle, summary.window_from) == (None, None, None, None, None, None, None)
    assert summary.read_errors == failed


def _roles(path: Path) -> dict:
    from alletra_onboard.application.replication.read import parse_showport_roles

    return parse_showport_roles(_capture(path.name, path.parent))[0]
