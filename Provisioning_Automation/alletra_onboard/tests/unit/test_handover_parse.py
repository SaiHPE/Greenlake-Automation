"""SPEC-026 R4, R5 and R10 parsers, pinned to the read-only captures taken by lab/handover_capture.py
(tests/fixtures/handover/README.md): rack13-ARCUS (HPE Alletra Storage MP B10230, OS 10.6.0) on
2026-11-16, and D22U27 (OS 10.5.0), E18U31 (OS 10.5.60) and VZ (OS 10.5.51) on 2026-11-17.

Every value asserted here is printed in those files. rack13 had nine New alerts; the OS 10.5.x captures
add a long alert list (D22U27, 525) and the array's words for no alert (E18U31). Performance (System
Reporter) left the as-built on 2026-11-19 at the owner's request; its captures stay in the fixtures.
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


def _capture(name: str, folder: Path = RACK13) -> str:
    """A capture without its '# command' header line: what the SSH client returns."""
    text = (folder / name).read_text(encoding="utf-8")
    return text.split("\n", 1)[1] if text.startswith("#") else text


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


# ---- At handover: the three reads together ----------------------------------------------------------

# The moment each capture's showdate was printed, in UTC: what the as-built step records as the read time.
READ_AT = {
    RACK13: datetime(2026, 11, 16, 17, 57, 23, tzinfo=UTC),
    D22U27: datetime(2026, 11, 16, 18, 33, 14, tzinfo=UTC),
    E18U31: datetime(2026, 11, 16, 18, 34, 36, tzinfo=UTC),
    VZ: datetime(2026, 11, 16, 18, 38, 54, tzinfo=UTC),
}


def _reads(folder: Path, *, errors: dict | None = None, run_created_at=None, **texts: str) -> h.HandoverReads:
    """The three reads of one capture folder, as the as-built step would have them."""
    files = {h.CLOCK: "showdate.txt", h.ALERTS: "showalert_d.txt", h.SPACE: "showsys_space.txt"}
    captured = {cmd: _capture(name, folder) for cmd, name in files.items()}
    captured.update(texts)
    return h.read_handover(captured, errors or {}, run_created_at=run_created_at, read_at=READ_AT[folder])


def test_the_as_built_reads_no_performance():
    """2026-11-19, the owner's decision: performance removed from the as-built. No System Reporter read."""
    assert [cmd for _attr, cmd in h.READS] == ["showdate", "showalert -d", "showsys -space"]


@pytest.mark.parametrize("folder, clock", [
    (RACK13, datetime(2026, 11, 16, 23, 27, 23)), (D22U27, datetime(2026, 11, 17, 0, 3, 14)),
    (E18U31, datetime(2026, 11, 17, 0, 4, 36)), (VZ, datetime(2026, 11, 17, 0, 8, 54)),
])
def test_showdate_gives_the_first_nodes_time_on_the_arrays_clock(folder, clock):
    assert h.parse_showdate(_capture("showdate.txt", folder)) == clock


@pytest.mark.parametrize("folder", [RACK13, D22U27, E18U31, VZ])
def test_the_arrays_utc_offset_comes_from_its_clock_and_the_read(folder):
    """Every lab array is in India: +05:30, from showdate against the read's moment, without reading the
    zone's abbreviation or name (ADR 0019 change 5)."""
    reads = _reads(folder)
    assert reads.offset == timedelta(hours=5, minutes=30)
    assert h.offset_text(reads.offset) == "UTC+05:30"


def test_the_offset_is_the_nearest_quarter_hour():
    """An array clock a few minutes off, or a read that took seconds, still gives the zone's offset."""
    clock = datetime(2026, 11, 16, 23, 27, 23)
    read = datetime(2026, 11, 16, 17, 57, 23, tzinfo=UTC)
    for skew in (-7, -3, 0, 3, 7):
        assert h.utc_offset(clock, read + timedelta(minutes=skew)) == timedelta(hours=5, minutes=30)
    assert h.utc_offset(datetime(2026, 11, 16, 12, 0), datetime(2026, 11, 16, 17, 0, tzinfo=UTC)) == timedelta(hours=-5)
    assert h.offset_text(h.utc_offset(datetime(2026, 11, 16, 23, 45), datetime(2026, 11, 16, 18, 0, tzinfo=UTC))) == "UTC+05:45"


def test_no_clock_means_no_offset():
    assert h.utc_offset(None, READ_AT[RACK13]) is None
    reads = _reads(RACK13, errors={h.CLOCK: "ArrayCliError: timed out"})
    assert reads.clock is None and reads.offset is None
    with pytest.raises(h.UnreadableReport, match="Error: Invalid option"):
        h.parse_showdate("Error: Invalid option -x\n")
    with pytest.raises(h.UnreadableReport, match="no node time"):
        h.parse_showdate("Node Date\n")


def test_before_this_run_uses_the_first_occurrence_and_the_arrays_offset():
    """rack13: alert 27 first happened 2026-11-11 23:22:51 IST (17:52:51 UTC), alert 40 at 23:54:31 IST
    (18:24:31 UTC) though its Time is the capture minute. A run created at 18:00 UTC that day sits
    between them."""
    alerts = {a.id: a for a in h.parse_alerts(_capture("showalert_d.txt"))}
    offset = _reads(RACK13).offset
    created = datetime(2026, 11, 11, 18, 0, tzinfo=UTC)
    assert h.before_run(alerts[27], offset, created) is True
    assert h.before_run(alerts[40], offset, created) is False
    assert h.before_run(alerts[40], offset, datetime(2026, 11, 16, 17, 0, tzinfo=UTC)) is True
    assert h.before_run(alerts[40], None, created) is None            # the clock not read: unknown
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


def test_a_refused_or_unreadable_read_is_an_error_and_the_others_still_parse():
    reads = _reads(VZ, errors={h.CLOCK: "ArrayCliError: refused"}, **{h.SPACE: "Error: Invalid option -space\n"})
    assert reads.errors == {h.CLOCK: "ArrayCliError: refused", h.SPACE: "Error: Invalid option -space"}
    assert reads.clock is reads.space is None
    assert len(reads.alerts) == 31
    reads = _reads(VZ, **{h.ALERTS: ""})
    assert reads.errors == {h.ALERTS: "the array printed nothing"} and reads.alerts is None


@pytest.mark.parametrize("folder, expected", [
    (RACK13, {"alerts_new": 9, "alerts_major": 5, "oldest_alert": "2026-11-11 23:22:51 IST", "cloud_alert": 40}),
    (D22U27, {"alerts_new": 525, "alerts_major": 4, "oldest_alert": "2025-12-26 21:11:20 IST", "cloud_alert": 10}),
    (E18U31, {"alerts_new": 0, "alerts_major": 0, "oldest_alert": None, "cloud_alert": None}),
    (VZ, {"alerts_new": 31, "alerts_major": 8, "cloud_alert": 11}),
])
def test_summarise_gives_the_event_fields(folder, expected):
    """SPEC-026 R10. No performance field since 2026-11-19 (the owner's decision)."""
    summary = h.summarise(_reads(folder)).as_event()
    assert set(summary) == {"read_at", "alerts_new", "alerts_major", "oldest_alert", "cloud_alert", "read_errors"}
    assert summary["read_at"] == READ_AT[folder].isoformat() and summary["read_errors"] == {}
    assert {k: summary[k] for k in expected} == expected


def test_summarise_says_unknown_for_every_read_that_failed():
    failed = {cmd: "ArrayCliError: timed out" for cmd in (h.CLOCK, h.ALERTS, h.SPACE)}
    summary = h.summarise(_reads(D22U27, errors=failed))
    assert (summary.alerts_new, summary.alerts_major, summary.oldest_alert, summary.cloud_alert) == (None, None, None, None)
    assert summary.read_errors == failed
