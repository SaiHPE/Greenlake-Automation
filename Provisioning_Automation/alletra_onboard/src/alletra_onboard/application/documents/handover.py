"""Read what the array says about itself at handover: alerts, capacity and System Reporter summaries.

SPEC-026 R4 to R7. Pure functions over the text one command returns (the client's output, with no
command line on top). No I/O; nothing here sends a command. Pinned to real output in
``tests/fixtures/handover/``: rack13-ARCUS on OS 10.6.0 (2026-11-16), and D22U27 (10.5.0), E18U31
(10.5.60) and VZ (10.5.51) on 2026-11-17.

A text that is not the report a parser reads (the array refused the command, or printed a layout we
have not seen) raises ``UnreadableReport``. The caller records it as a failed read (SPEC-026 R8); it
is never read as an empty list or as zeros (LESSONS 3, 27, 39).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

MIB_PER_TIB = 1024 * 1024


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
