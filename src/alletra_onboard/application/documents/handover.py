"""Read what the array says about itself at handover: alerts, capacity and System Reporter summaries.

SPEC-026 R3 to R10. Pure functions over the text one command returns (the client's output, with no
command line on top). No I/O; nothing here sends a command. Pinned to real output in
``tests/fixtures/handover/``: rack13-ARCUS on OS 10.6.0 (2026-11-16), and D22U27 (10.5.0), E18U31
(10.5.60) and VZ (10.5.51) on 2026-11-17.

A text that is not the report a parser reads (the array refused the command, or printed a layout we
have not seen) raises ``UnreadableReport``. The caller records it as a failed read (SPEC-026 R8); it
is never read as an empty list or as zeros (LESSONS 3, 27, 39).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta

from alletra_onboard.domain.replication import PortRole

MIB_PER_TIB = 1024 * 1024

# SPEC-026 R6: below this many IO/s, summed over the host ports' averages, the window was idle.
IDLE_IOPS = 10
# SPEC-026 R4: the array's own Major alert "disconnected from Data Services Cloud Console".
CLOUD_ALERT_CODE = "0x060000a"
# SPEC-026 R4: listed in full and raised as as-built warnings; every other severity is grouped.
FULL_SEVERITIES = ("Major", "Critical", "Fatal")

#: SPEC-026 R3: AsBuiltData field -> the read exactly as the tool sends it, in the order it runs.
READS: tuple[tuple[str, str], ...] = (
    ("showalert_d", "showalert -d"),
    ("showsys_space", "showsys -space"),
    ("srstatcpu", "srstatcpu -hires -btsecs -24h -groupby NODE -summary min,avg,5%,95%,max,per_group"),
    ("srstatport", ("srstatport -hires -btsecs -24h -port_type host,iscsi -groupby PORT_N,PORT_S,PORT_P "
                    "-summary avg,95%,max,per_group")),
    ("srstatvv", "srstatvv -hires -btsecs -24h -summary avg,95%,max"),
)
ALERTS, SPACE, CPU, PORTS, VOLUMES = (cmd for _attr, cmd in READS)

PERFORMANCE_NOTE = "These figures are the load seen in this window, not what the array can do."
IDLE_NOTE = "The array carried almost no host I/O in this window: an idle baseline for later comparison."
_CLOUD_NOT_READ = "The tool did not read HPE's cloud view of this array (cloud connection, call-home)."


class UnreadableReport(ValueError):
    """The text is not the report this parser reads. The message carries the array's own first line."""


# The array's refusal words on the first line, as lab/handover_capture.py judges them (LESSONS 39).
_REFUSAL = re.compile(r"^(error\b|invalid\b|unknown\b|usage\b)|command not found|not (running|licensed|supported)",
                      re.IGNORECASE)


def _first_line(text: str) -> str:
    return next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "")


def _refuse_if_refused(text: str, what: str) -> None:
    first = _first_line(text)
    if not first:
        raise UnreadableReport(f"{what}: the array printed nothing")
    if _REFUSAL.search(first):
        raise UnreadableReport(f"{what}: {first}")


def _number(text: str) -> float | None:
    """A figure as the array printed it, or None for its words for nothing (``-``) or a bound (``>25``)."""
    try:
        return float(text)
    except ValueError:
        return None


# ---- showalert / showalert -d ----------------------------------------------------------------------

_ALERT_TIME = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b")
_REPEAT = re.compile(r"Occurred (\d+) times?, first at (.+?)\s*$")
_ALERT_COUNT = re.compile(r"^(\d+) alerts?$")
# An array with no alert prints this one line, for showalert and showalert -d alike (E18U31, OS 10.5.60,
# 2026-11-17). Matched whole: any other words are not read as "no alerts".
_NO_ALERTS = re.compile(r"^no alerts$", re.IGNORECASE)


@dataclass(frozen=True)
class Alert:
    """One alert as ``showalert`` prints it. Every word is the array's own."""

    id: int
    state: str            # New, Acknowledged, Fixed
    severity: str         # seen: Critical, Major, Minor, Degraded, Informational
    time: str             # as printed, e.g. "2026-11-16 23:25:20 IST": the LATEST occurrence
    message_code: str
    type: str
    message: str
    component: str = ""   # -d only
    first_time: str = ""  # -d only, from "Repeat Count: Occurred N times, first at <time>"
    occurrences: int = 1  # -d only

    @property
    def first_seen(self) -> str:
        """When the alert first happened: the repeat line's time, else the alert's own time."""
        return self.first_time or self.time

    @property
    def local_time(self) -> datetime | None:
        """``time`` on the array's clock (naive; the zone is the abbreviation the array printed)."""
        return _local(self.time)

    @property
    def first_seen_local(self) -> datetime | None:
        return _local(self.first_seen)


def _local(text: str) -> datetime | None:
    m = _ALERT_TIME.match(text or "")
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") if m else None


def parse_alerts(text: str) -> list[Alert]:
    """``showalert`` or ``showalert -d`` into alerts, in the order the array printed them.

    Records are ``Key : Value`` blocks separated by blank lines, closed by an ``N alerts`` line; the
    count must match. The array prints them by ``Time`` (latest occurrence), oldest first, not by Id.
    An array with no alert prints only ``no alerts``; anything else raises.
    """
    _refuse_if_refused(text, "showalert")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) == 1 and _NO_ALERTS.match(lines[0]):
        return []
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    last_key = ""
    footer: int | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            if current:
                blocks.append(current)
                current, last_key = {}, ""
            continue
        m = _ALERT_COUNT.match(line.strip())
        if m and not current:
            footer = int(m.group(1))
            continue
        key, sep, value = line.partition(":")
        if sep and key.strip() and not key.startswith(" "):
            last_key = key.strip()
            current[last_key] = value.strip()
        elif last_key:  # a wrapped message line
            current[last_key] = f"{current[last_key]} {line.strip()}"
        else:
            raise UnreadableReport(f"showalert: unexpected line {line.strip()!r}")
    if current:
        blocks.append(current)

    if not blocks:
        raise UnreadableReport(f"showalert: no alert records; the array says: {_first_line(text)}")

    alerts = [_alert(block) for block in blocks]
    if footer is not None and footer != len(alerts):
        raise UnreadableReport(f"showalert: the array counts {footer} alerts, {len(alerts)} were read")
    return alerts


def _alert(block: dict[str, str]) -> Alert:
    missing = [k for k in ("Id", "State", "Severity", "Time", "Message") if not block.get(k)]
    if missing or not block["Id"].isdigit():
        raise UnreadableReport(f"showalert: an alert without {', '.join(missing) or 'a numeric Id'}")
    first_time, occurrences = "", 1
    repeat = _REPEAT.search(block.get("Repeat Count", ""))
    if repeat:
        occurrences, first_time = int(repeat.group(1)), repeat.group(2)
    return Alert(
        id=int(block["Id"]),
        state=block["State"],
        severity=block["Severity"],
        time=block["Time"],
        message_code=block.get("Message Code", ""),
        type=block.get("Type", ""),
        message=block["Message"],
        component=block.get("Component", ""),
        first_time=first_time,
        occurrences=occurrences,
    )


# ---- showsys -space --------------------------------------------------------------------------------

_SPACE_SECTION = re.compile(r"^-+\s*(.+?)\s*-+$")
_UNIT = re.compile(r"\s*\((\w+)\)$")


@dataclass(frozen=True)
class SpaceFigure:
    """One ``Key : value`` line of ``showsys -space``, placed by its indent under its parents."""

    section: str             # "Raw Capacity", "Usable Capacity", "Efficiency"
    unit: str                # "MiB" for the capacity sections, "" for Efficiency (ratios)
    path: tuple[str, ...]    # ("Total", "Usable", "Allocated")
    text: str                # the array's own figure: "540672", "8.46", ">25"

    @property
    def number(self) -> float | None:
        return _number(self.text)


@dataclass(frozen=True)
class Space:
    """``showsys -space`` as the array printed it, line by line."""

    figures: tuple[SpaceFigure, ...]

    def get(self, section: str, *path: str) -> SpaceFigure | None:
        return next((f for f in self.figures if f.section == section and f.path == path), None)

    def mib(self, section: str, *path: str) -> int | None:
        figure = self.get(section, *path)
        number = figure.number if figure and figure.unit == "MiB" else None
        return None if number is None else int(number)

    # The lines SPEC-026 R5 names, as found on OS 10.6.0. Raw figures match showsys's own
    # TotalCap / AllocCap / FreeCap columns.
    @property
    def raw_total_mib(self) -> int | None:
        return self.mib("Raw Capacity", "Total")

    @property
    def raw_allocated_mib(self) -> int | None:
        return self.mib("Raw Capacity", "Total", "Usable", "Allocated")

    @property
    def raw_free_mib(self) -> int | None:
        return self.mib("Raw Capacity", "Total", "Usable", "Free")

    @property
    def usable_total_mib(self) -> int | None:
        return self.mib("Usable Capacity", "Total")

    @property
    def usable_used_mib(self) -> int | None:
        return self.mib("Usable Capacity", "Total", "Used")

    @property
    def usable_free_mib(self) -> int | None:
        return self.mib("Usable Capacity", "Total", "Free")

    @property
    def reduction(self) -> str:
        """The data reduction ratio as printed (``8.46``), or "" when the array does not print one."""
        figure = self.get("Efficiency", "Reduction")
        return figure.text if figure else ""


def tib(mib: int) -> float:
    """MiB to TiB with one decimal, the way the as-built writes capacity (SPEC-026 R5)."""
    return round(mib / MIB_PER_TIB, 1)


def parse_space(text: str) -> Space:
    """``showsys -space``: ``---- <section> (MiB) ----`` headings, then ``Key : value`` lines whose
    indent (two spaces a level) places them under the line above."""
    _refuse_if_refused(text, "showsys -space")
    figures: list[SpaceFigure] = []
    section = unit = ""
    stack: list[tuple[int, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        heading = _SPACE_SECTION.match(line.strip())
        if heading:
            name = heading.group(1)
            m = _UNIT.search(name)
            section, unit = (name[: m.start()].strip(), m.group(1)) if m else (name, "")
            stack = []
            continue
        key, sep, value = line.partition(":")
        if not sep or not section:
            raise UnreadableReport(f"showsys -space: unexpected line {line.strip()!r}")
        indent = len(key) - len(key.lstrip())
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, key.strip()))
        figures.append(SpaceFigure(section=section, unit=unit, path=tuple(k for _, k in stack),
                                   text=value.strip()))
    if not figures:
        raise UnreadableReport(f"showsys -space: no capacity lines; the array says: {_first_line(text)}")
    return Space(figures=tuple(figures))


# ---- System Reporter summaries (srstatcpu / srstatport / srstatvv / srstatrcvv -summary) ----------

_WINDOW = re.compile(r"^(Start|End) Time:\s*(.*?)\s*\((\d+)\)\s*$")
_STAT = re.compile(r"^(Avg|Min|Max|\d+(?:\.\d+)?%)$")
_GROUPBY = re.compile(r"^[A-Z][A-Z0-9_]*$")
# A last column System Reporter fills with words, not a figure: it takes the rest of the row. srstatrcvv's
# RPO prints "-", "0" or a date and time with a space in it ("2026-07-20 13:11:32", VZ, OS 10.5.51).
_TEXT_LAST_COLUMNS = frozenset({"RPO"})


@dataclass(frozen=True)
class SummaryRow:
    """One summary line: a statistic for one group, every column as the array printed it."""

    stat: str                  # "avg", "min", "max" or a percentile such as "95%"
    group: tuple[str, ...]     # the -groupby values in order; () without -groupby
    values: dict[str, str]     # column name -> figure as printed

    def number(self, column: str) -> float | None:
        return _number(self.values.get(column, ""))


@dataclass(frozen=True)
class SrSummary:
    """A System Reporter ``-summary`` report. ``end`` is None when System Reporter printed epoch 0:
    it had no sample in the window."""

    start_text: str
    end_text: str
    start: datetime | None     # UTC, from the epoch System Reporter prints in brackets
    end: datetime | None
    groupby: tuple[str, ...]
    columns: tuple[str, ...]   # metric columns, named "<group heading> <column>" where there is one
    rows: tuple[SummaryRow, ...]

    def groups(self) -> list[tuple[str, ...]]:
        seen: list[tuple[str, ...]] = []
        for row in self.rows:
            if row.group not in seen:
                seen.append(row.group)
        return seen

    def row(self, stat: str, group: tuple[str, ...] = ()) -> SummaryRow | None:
        return next((r for r in self.rows if r.stat == stat and r.group == group), None)


def _headings(line: str) -> list[tuple[int, int, str]]:
    """The dashed group headings above the column names, as (start, end, label).

    ``-----Svct ms-----`` and ``IOSz KB`` hold one space inside; a heading ends where a token ends
    in a dash, so ``-IO/s-- -KBytes/sec-`` is two."""
    spans: list[list] = []
    for m in re.finditer(r"\S+", line):
        if spans and m.start() == spans[-1][1] + 1 and not spans[-1][2].endswith("-"):
            spans[-1][1], spans[-1][2] = m.end(), f"{spans[-1][2]} {m.group()}"
        else:
            spans.append([m.start(), m.end(), m.group()])
    return [(s, e, text.strip("-").strip()) for s, e, text in spans]


def parse_srstat_summary(text: str, command: str = "srstat") -> SrSummary:
    """Any ``srstat* -summary ...`` report: the window lines, one ``Summary`` header line (with the
    group headings above it, when the report has them) and one row per statistic and group.

    The array prints the statistics in its own order (Avg, Max, Min, then the percentiles group by
    group, on OS 10.5.x and 10.6.0), whatever order the command asked for. A time-series report (no
    ``Summary`` header) raises.
    """
    _refuse_if_refused(text, command)
    lines = [ln.rstrip() for ln in text.splitlines()]
    window: dict[str, tuple[str, int]] = {}
    header_at = -1
    for i, line in enumerate(lines):
        m = _WINDOW.match(line.strip())
        if m:
            window[m.group(1)] = (m.group(2), int(m.group(3)))
        elif line.split()[:1] == ["Summary"]:
            header_at = i
            break
    if header_at < 0:
        raise UnreadableReport(f"{command}: not a System Reporter summary; the array says: {_first_line(text)}")

    header = lines[header_at]
    above = lines[header_at - 1] if header_at > 0 else ""
    headings = [] if (not above.strip() or _WINDOW.match(above.strip())) else _headings(above)
    tokens = list(re.finditer(r"\S+", header))[1:]

    def heading_of(token: re.Match[str]) -> str:
        return next((label for s, e, label in headings if s < token.end() and token.start() < e), "")

    # The -groupby names (NODE, PORT_N, GROUP_NAME) come first, in capitals and under no heading.
    groupby: list[str] = []
    while tokens and _GROUPBY.match(tokens[0].group()) and not heading_of(tokens[0]):
        groupby.append(tokens.pop(0).group())
    columns = [f"{heading_of(t)} {t.group()}" if heading_of(t) else t.group() for t in tokens]

    rows: list[SummaryRow] = []
    width = 1 + len(groupby) + len(columns)
    for line in lines[header_at + 1:]:
        parts = line.split()
        if not parts or set(line.strip()) <= {"-"}:
            continue
        if len(parts) > width and columns and columns[-1] in _TEXT_LAST_COLUMNS:
            parts = [*parts[:width - 1], " ".join(parts[width - 1:])]
        if not _STAT.match(parts[0]) or len(parts) != width:
            raise UnreadableReport(f"{command}: a summary line we cannot read: {line.strip()!r}")
        rows.append(SummaryRow(stat=parts[0].lower(), group=tuple(parts[1:1 + len(groupby)]),
                               values=dict(zip(columns, parts[1 + len(groupby):], strict=True))))

    start_text, start_epoch = window.get("Start", ("", 0))
    end_text, end_epoch = window.get("End", ("", 0))
    return SrSummary(
        start_text=start_text, end_text=end_text,
        start=datetime.fromtimestamp(start_epoch, UTC) if start_epoch else None,
        end=datetime.fromtimestamp(end_epoch, UTC) if end_epoch else None,
        groupby=tuple(groupby), columns=tuple(columns), rows=tuple(rows),
    )


def _require(summary: SrSummary, groupby: tuple[str, ...], columns: tuple[str, ...], what: str) -> None:
    missing = [c for c in columns if c not in summary.columns]
    if summary.groupby != groupby or missing:
        raise UnreadableReport(f"{what}: expected groups {', '.join(groupby) or 'none'} and columns "
                               f"{', '.join(columns)}; the array printed groups "
                               f"{', '.join(summary.groupby) or 'none'} and columns {', '.join(summary.columns)}")


@dataclass(frozen=True)
class CpuFigures:
    user_pct: float | None
    sys_pct: float | None
    idle_pct: float | None


@dataclass(frozen=True)
class CpuNode:
    """One controller node's CPU over the window, per statistic as printed.

    System Reporter summarises each column on its own: the ``max`` row's Idle% is the most idle
    sample, not the busiest. Busy is 100 - Idle%, so the busiest sample needs the ``min`` Idle% and
    the 95th percentile of busy needs the 5th percentile of Idle%. Without them those are None.
    """

    node: str
    stats: dict[str, CpuFigures]

    def _busy(self, stat: str) -> float | None:
        figures = self.stats.get(stat)
        idle = figures.idle_pct if figures else None
        return None if idle is None else round(100 - idle, 1)

    @property
    def busy_avg(self) -> float | None:
        return self._busy("avg")

    @property
    def busy_p95(self) -> float | None:
        return self._busy("5%")

    @property
    def busy_max(self) -> float | None:
        return self._busy("min")


def cpu_by_node(summary: SrSummary) -> list[CpuNode]:
    """``srstatcpu -groupby NODE -summary ...,per_group``: one entry per node."""
    _require(summary, ("NODE",), ("User%", "Sys%", "Idle%"), "srstatcpu")
    return [
        CpuNode(node=group[0], stats={
            r.stat: CpuFigures(r.number("User%"), r.number("Sys%"), r.number("Idle%"))
            for r in summary.rows if r.group == group
        })
        for group in summary.groups()
    ]


@dataclass(frozen=True)
class IoFigures:
    """Total (read + write) I/O for one statistic. KBytes/s as printed; MB/s is the renderer's."""

    iops: float | None
    kbytes_s: float | None
    svct_ms: float | None


@dataclass(frozen=True)
class IoLoad:
    """One port's, or the whole array's volumes', I/O over the window, per statistic."""

    name: str                       # "0:3:4" for a port; "" for all volumes together
    stats: dict[str, IoFigures]


_IO_COLUMNS = ("IO/s Tot", "KBytes/s Tot", "Svct ms Tot")


def _io(row: SummaryRow) -> IoFigures:
    return IoFigures(row.number("IO/s Tot"), row.number("KBytes/s Tot"), row.number("Svct ms Tot"))


def ports_by_port(summary: SrSummary) -> list[IoLoad]:
    """``srstatport -groupby PORT_N,PORT_S,PORT_P -summary ...,per_group``: one entry per port."""
    _require(summary, ("PORT_N", "PORT_S", "PORT_P"), _IO_COLUMNS, "srstatport")
    return [IoLoad(name=":".join(group), stats={r.stat: _io(r) for r in summary.rows if r.group == group})
            for group in summary.groups()]


def volumes_total(summary: SrSummary) -> IoLoad | None:
    """``srstatvv -summary ...`` with no -groupby: all volumes together, or None with no rows."""
    _require(summary, (), _IO_COLUMNS, "srstatvv")
    return IoLoad(name="", stats={r.stat: _io(r) for r in summary.rows}) if summary.rows else None


@dataclass(frozen=True)
class RcFigures:
    lcl_iops: float | None
    rmt_iops: float | None
    lcl_svct_ms: float | None
    rmt_svct_ms: float | None
    rpo: str                        # as System Reporter prints it: "-", "0" or a date and time (SPEC-026 R7)


@dataclass(frozen=True)
class RcGroupLoad:
    group: str
    stats: dict[str, RcFigures]


_RC_COLUMNS = ("IO/s Lcl", "IO/s Rmt", "Svct(ms) Lcl", "Svct(ms) Rmt", "RPO")


def rc_by_group(summary: SrSummary) -> list[RcGroupLoad]:
    """``srstatrcvv -groupby GROUP_NAME -summary ...,per_group``: one entry per Remote Copy group."""
    _require(summary, ("GROUP_NAME",), _RC_COLUMNS, "srstatrcvv")
    return [
        RcGroupLoad(group=group[0], stats={
            r.stat: RcFigures(r.number("IO/s Lcl"), r.number("IO/s Rmt"), r.number("Svct(ms) Lcl"),
                              r.number("Svct(ms) Rmt"), r.values["RPO"])
            for r in summary.rows if r.group == group
        })
        for group in summary.groups()
    ]


# ---- At handover: the five reads together (SPEC-026 R4, R6, R8, R10) -------------------------------

def utc_offset(*summaries: SrSummary | None) -> timedelta | None:
    """The array's UTC offset, from the first System Reporter summary given that has a window: its
    ``Start Time`` line prints the local time and the epoch (``2026-11-16 00:05:18 IST (1794767718)``
    is +05:30). Never from the zone's abbreviation and never through ``zoneinfo``: the exe ships no
    ``tzdata`` (ADR 0019 change 5)."""
    for summary in summaries:
        local = _local(summary.start_text) if summary is not None else None
        if local is None or summary.start is None:
            continue
        seconds = (local - summary.start.replace(tzinfo=None)).total_seconds()
        return timedelta(minutes=round(seconds / 60))
    return None


def offset_text(offset: timedelta) -> str:
    """``UTC+05:30``."""
    minutes = round(offset.total_seconds() / 60)
    sign = "-" if minutes < 0 else "+"
    return f"UTC{sign}{abs(minutes) // 60:02d}:{abs(minutes) % 60:02d}"


def _utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def before_run(alert: Alert, offset: timedelta | None, run_created_at: datetime | None) -> bool | None:
    """Whether the alert FIRST happened before the run was created (its ``Time`` is the latest
    occurrence). None, unknown, without the array's offset or the run's creation time."""
    first = alert.first_seen_local
    if first is None or offset is None or run_created_at is None:
        return None
    return (first - offset).replace(tzinfo=UTC) < _utc(run_created_at)


def is_full(alert: Alert) -> bool:
    """Major, Critical or Fatal: listed in full and raised as an as-built warning."""
    return alert.severity.lower() in {s.lower() for s in FULL_SEVERITIES}


def cloud_alert(alerts: Iterable[Alert]) -> Alert | None:
    """The New alert saying the array is disconnected from Data Services Cloud Console, or None."""
    return next((a for a in alerts if a.message_code.lower() == CLOUD_ALERT_CODE and a.state.lower() == "new"), None)


def oldest(alerts: Iterable[Alert]) -> Alert | None:
    """The alert that first happened earliest (by its first occurrence, not its ``Time``)."""
    dated = [a for a in alerts if a.first_seen_local is not None]
    return min(dated, key=lambda a: a.first_seen_local) if dated else None


def _newest_first(alerts: Iterable[Alert]) -> list[Alert]:
    return sorted(alerts, key=lambda a: (a.local_time or datetime.min, a.id), reverse=True)


@dataclass(frozen=True)
class AlertGroup:
    """Alerts below Major that share a message code and a severity, newest first."""

    severity: str
    message_code: str
    alerts: tuple[Alert, ...]

    @property
    def count(self) -> int:
        return len(self.alerts)

    @property
    def first_seen(self) -> str:
        first = oldest(self.alerts)
        return first.first_seen if first else self.alerts[-1].first_seen

    @property
    def latest(self) -> str:
        return self.alerts[0].time

    @property
    def sample(self) -> str:
        return self.alerts[0].message


def alert_table(alerts: Iterable[Alert]) -> tuple[list[Alert], list[AlertGroup]]:
    """SPEC-026 R4: Major, Critical and Fatal alerts in full, newest first; the rest grouped by
    severity and message code, the group with the newest occurrence first."""
    alerts = list(alerts)
    full = _newest_first(a for a in alerts if is_full(a))
    grouped: dict[tuple[str, str], list[Alert]] = {}
    for alert in alerts:
        if not is_full(alert):
            grouped.setdefault((alert.severity, alert.message_code), []).append(alert)
    groups = [AlertGroup(severity, code, tuple(_newest_first(members))) for (severity, code), members in grouped.items()]
    groups.sort(key=lambda g: (g.alerts[0].local_time or datetime.min, g.alerts[0].id), reverse=True)
    return full, groups


def alerts_verdict(alerts: list[Alert]) -> str:
    """The sentence above the alert table, with the cloud sentence when the array reports one."""
    if not alerts:
        return "No new alerts."
    first = oldest(alerts)
    if len(alerts) == 1:
        text = "1 new alert" + (f"; it first occurred on {first.first_seen}" if first else "")
    else:
        text = f"{len(alerts)} new alerts" + (f"; the oldest first occurred on {first.first_seen}" if first else "")
    text += ". Alerts record an event, not the current state: compare each with checkhealth before acting."
    cloud = cloud_alert(alerts)
    if cloud is not None:
        text += f" The array reports it is disconnected from Data Services Cloud Console (alert {cloud.id})."
    return text


def cloud_line(alerts: list[Alert] | None) -> str:
    """SPEC-026 R9: the section's last line. ``alerts`` is None when they could not be read."""
    if alerts is None:
        return f"Cloud connection: unknown, the alerts could not be read. {_CLOUD_NOT_READ}"
    cloud = cloud_alert(alerts)
    if cloud is None:
        return f"Cloud connection: the array has no New alert about it. {_CLOUD_NOT_READ}"
    return ("Cloud connection: the array reports it is disconnected from Data Services Cloud Console "
            f'(alert {cloud.id}: "{cloud.message}"). The tool did not read HPE\'s cloud view of this array (call-home).')


@dataclass(frozen=True)
class PortRow:
    """A host port in the performance table, with its protocol as ``showport`` prints it."""

    load: IoLoad
    protocol: str


def _carried_io(load: IoLoad) -> bool:
    return any((figures.iops or 0) > 0 for figures in load.stats.values())


def _state_words(role: PortRole | None) -> str:
    if role is None:
        return "not listed by showport"
    if role.type.lower() == "free":
        return "not configured"
    return {"offline": "offline", "loss_sync": "with no link"}.get(role.state.lower(), f"in state {role.state}")


def split_ports(loads: list[IoLoad], roles: Mapping[str, PortRole]) -> tuple[list[PortRow], list[str]]:
    """SPEC-026 R6: the ports ``showport`` reports ``ready``, for the table; every other port System
    Reporter printed, named in one line per kind (``4 iSCSI ports not configured, no I/O: 0:4:1, …``),
    never dropped. Without ``showport`` states every port is listed and one line says why."""
    if not roles:
        why = "The ports' states could not be read from showport, so every port System Reporter printed is listed."
        return [PortRow(load, "") for load in loads], [why] if loads else []
    ready: list[PortRow] = []
    others: dict[tuple[str, str, str], list[str]] = {}
    for load in loads:
        role = roles.get(load.name)
        if role is not None and role.state.lower() == "ready":
            ready.append(PortRow(load, role.protocol))
            continue
        key = (role.protocol if role else "", _state_words(role), "with I/O" if _carried_io(load) else "no I/O")
        others.setdefault(key, []).append(load.name)
    lines = []
    for (protocol, words, io), names in others.items():
        noun = "port" if len(names) == 1 else "ports"
        lines.append(f"{len(names)} {protocol + ' ' if protocol else ''}{noun} {words}, {io}: {', '.join(names)}.")
    return ready, lines


@dataclass
class HandoverReads:
    """The five reads parsed. A read that failed, or printed something its parser cannot read, is in
    ``errors`` (command -> the array's words) and its value is None: never an empty list or a zero."""

    read_at: datetime | None = None
    run_created_at: datetime | None = None
    alerts: list[Alert] | None = None
    space: Space | None = None
    cpu: SrSummary | None = None
    cpu_nodes: list[CpuNode] | None = None
    ports: SrSummary | None = None
    port_loads: list[IoLoad] | None = None
    volumes: SrSummary | None = None
    volume_load: IoLoad | None = None
    roles: dict[str, PortRole] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def offset(self) -> timedelta | None:
        return utc_offset(self.cpu, self.ports, self.volumes)

    @property
    def window(self) -> SrSummary | None:
        """The first System Reporter summary that parsed: its Start and End Time are the window."""
        return next((s for s in (self.cpu, self.ports, self.volumes) if s is not None), None)

    @property
    def host_iops_avg(self) -> float | None:
        """SPEC-026 R6: the host ports' average IO/s summed, every port printed (ready or not). None, not
        known, when the report was not read or printed no port: no sample is not an idle window."""
        if not self.port_loads:
            return None
        figures = [p.stats["avg"].iops if "avg" in p.stats else None for p in self.port_loads]
        return None if None in figures else round(sum(figures), 1)

    @property
    def idle(self) -> bool | None:
        iops = self.host_iops_avg
        return None if iops is None else iops < IDLE_IOPS


def _words(exc: UnreadableReport) -> str:
    """The parser's message without its leading command name: what the array printed, or why it was not read."""
    message = str(exc)
    return message.split(": ", 1)[1] if ": " in message else message


def read_handover(texts: Mapping[str, str], read_errors: Mapping[str, str], *, showport: str = "",
                  read_at: datetime | None = None, run_created_at: datetime | None = None) -> HandoverReads:
    """Parse each of the five reads (``texts`` keyed by command). One that is in ``read_errors``, or
    that its parser refuses, lands in ``errors``; the others still parse (SPEC-026 R8)."""
    # The one reader of a port's role (LESSONS 41). Imported here: its module brings the array clients.
    from alletra_onboard.application.replication.read import parse_showport_roles

    reads = HandoverReads(read_at=read_at, run_created_at=run_created_at, roles=parse_showport_roles(showport)[0])

    def attempt(command: str, parse):
        if command in read_errors:
            reads.errors[command] = read_errors[command]
            return None
        try:
            return parse(texts.get(command) or "")
        except UnreadableReport as exc:
            reads.errors[command] = _words(exc)
            return None

    def summary(name: str, per):
        def parse(text: str):
            parsed = parse_srstat_summary(text, name)
            return parsed, per(parsed)
        return parse

    reads.alerts = attempt(ALERTS, parse_alerts)
    reads.space = attempt(SPACE, parse_space)
    reads.cpu, reads.cpu_nodes = attempt(CPU, summary("srstatcpu", cpu_by_node)) or (None, None)
    reads.ports, reads.port_loads = attempt(PORTS, summary("srstatport", ports_by_port)) or (None, None)
    reads.volumes, reads.volume_load = attempt(VOLUMES, summary("srstatvv", volumes_total)) or (None, None)
    return reads


def read_from(data) -> HandoverReads:
    """The five reads as an ``AsBuiltData`` carries them (duck-typed: ``asbuilt.py`` imports this module)."""
    return read_handover({cmd: getattr(data, attr, "") for attr, cmd in READS}, data.read_errors,
                         showport=data.showport, read_at=data.handover_read_at, run_created_at=data.run_created_at)


@dataclass(frozen=True)
class HandoverSummary:
    """SPEC-026 R10: the ``handover`` field of the ``asbuilt.generated`` event. None means not known
    (the read failed), never zero."""

    read_at: str | None
    window_from: str | None
    window_to: str | None
    alerts_new: int | None
    alerts_major: int | None
    oldest_alert: str | None          # the oldest first occurrence, as the array printed it
    cloud_alert: int | None           # the id of the New 0x060000a alert
    cpu_max_pct: float | None         # the busiest sample of any node
    iops_avg: float | None            # the host ports' average IO/s, summed
    idle: bool | None
    read_errors: dict[str, str]

    def as_event(self) -> dict:
        return asdict(self)


def _iso(moment: datetime | None) -> str | None:
    return _utc(moment).isoformat() if moment is not None else None


def summarise(reads: HandoverReads) -> HandoverSummary:
    alerts = reads.alerts
    window = reads.window
    busiest = [n.busy_max for n in reads.cpu_nodes or [] if n.busy_max is not None]
    first = oldest(alerts) if alerts else None
    cloud = cloud_alert(alerts) if alerts else None
    return HandoverSummary(
        read_at=_iso(reads.read_at),
        window_from=_iso(window.start) if window else None,
        window_to=_iso(window.end) if window else None,
        alerts_new=None if alerts is None else len(alerts),
        alerts_major=None if alerts is None else sum(1 for a in alerts if is_full(a)),
        oldest_alert=first.first_seen if first else None,
        cloud_alert=cloud.id if cloud else None,
        cpu_max_pct=max(busiest) if busiest else None,
        iops_avg=reads.host_iops_avg,
        idle=reads.idle,
        read_errors=dict(reads.errors),
    )
