"""Read what the array says about itself at handover: its clock, alerts and capacity.

SPEC-026 R3 to R5 and R8 to R10. Pure functions over the text one command returns (the client's output,
with no command line on top). No I/O; nothing here sends a command. Pinned to real output in
``tests/fixtures/handover/``: rack13-ARCUS on OS 10.6.0 (2026-11-16), and D22U27 (10.5.0), E18U31
(10.5.60) and VZ (10.5.51) on 2026-11-17.

2026-11-19: performance removed from the as-built at the owner's request. The System Reporter reads
(``srstatcpu``, ``srstatport``, ``srstatvv``) and their parsers are gone; the array's UTC offset, which
came from a System Reporter window, now comes from ``showdate`` against the moment of the read.

A text that is not the report a parser reads (the array refused the command, or printed a layout we
have not seen) raises ``UnreadableReport``. The caller records it as a failed read (SPEC-026 R8); it
is never read as an empty list or as zeros (LESSONS 3, 27, 39).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta

MIB_PER_TIB = 1024 * 1024

# SPEC-026 R4: the array's own Major alert "disconnected from Data Services Cloud Console".
CLOUD_ALERT_CODE = "0x060000a"
# SPEC-026 R4: listed in full and raised as as-built warnings; every other severity is grouped.
FULL_SEVERITIES = ("Major", "Critical", "Fatal")
# The array's UTC offset is its clock minus the read's moment, to the nearest quarter hour: every zone's
# offset is a multiple of 15 minutes, so a clock up to 7 minutes off still gives the right one.
OFFSET_STEP_MINUTES = 15

#: SPEC-026 R3: AsBuiltData field -> the read exactly as the tool sends it, in the order it runs. The
#: clock first, as close to the read's moment as it can be.
READS: tuple[tuple[str, str], ...] = (
    ("showdate", "showdate"),
    ("showalert_d", "showalert -d"),
    ("showsys_space", "showsys -space"),
)
CLOCK, ALERTS, SPACE = (cmd for _attr, cmd in READS)

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


# ---- showdate --------------------------------------------------------------------------------------

_DATE_ROW = re.compile(r"^\d+\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b")


def parse_showdate(text: str) -> datetime:
    """``showdate``: one row per node, ``0    2026-11-16 23:27:23 IST (Asia/Kolkata)``. The first node's
    time on the array's clock (naive: the zone is only an abbreviation and a name, neither read)."""
    _refuse_if_refused(text, "showdate")
    for line in text.splitlines():
        m = _DATE_ROW.match(line.strip())
        if m:
            return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
    raise UnreadableReport(f"showdate: no node time; the array says: {_first_line(text)}")


# ---- At handover: the reads together (SPEC-026 R4, R8, R10) ---------------------------------------

def utc_offset(clock: datetime | None, read_at: datetime | None) -> timedelta | None:
    """The array's UTC offset: ``showdate``'s time minus the read's moment in UTC, to the nearest quarter
    hour (2026-11-16 23:27:23 on the array, read at 17:57:23 UTC, is +05:30). Never from the zone's
    abbreviation or name and never through ``zoneinfo``: the exe ships no ``tzdata`` (ADR 0019 change 5)."""
    if clock is None or read_at is None:
        return None
    moment = _utc(read_at).astimezone(UTC).replace(tzinfo=None)
    minutes = (clock - moment).total_seconds() / 60
    return timedelta(minutes=round(minutes / OFFSET_STEP_MINUTES) * OFFSET_STEP_MINUTES)


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


@dataclass
class HandoverReads:
    """The three reads parsed. A read that failed, or printed something its parser cannot read, is in
    ``errors`` (command -> the array's words) and its value is None: never an empty list or a zero."""

    read_at: datetime | None = None
    run_created_at: datetime | None = None
    clock: datetime | None = None       # showdate: the first node's time on the array's clock
    alerts: list[Alert] | None = None
    space: Space | None = None
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def offset(self) -> timedelta | None:
        return utc_offset(self.clock, self.read_at)


def _words(exc: UnreadableReport) -> str:
    """The parser's message without its leading command name: what the array printed, or why it was not read."""
    message = str(exc)
    return message.split(": ", 1)[1] if ": " in message else message


def read_handover(texts: Mapping[str, str], read_errors: Mapping[str, str], *,
                  read_at: datetime | None = None, run_created_at: datetime | None = None) -> HandoverReads:
    """Parse each of the three reads (``texts`` keyed by command). One that is in ``read_errors``, or
    that its parser refuses, lands in ``errors``; the others still parse (SPEC-026 R8)."""
    reads = HandoverReads(read_at=read_at, run_created_at=run_created_at)

    def attempt(command: str, parse):
        if command in read_errors:
            reads.errors[command] = read_errors[command]
            return None
        try:
            return parse(texts.get(command) or "")
        except UnreadableReport as exc:
            reads.errors[command] = _words(exc)
            return None

    reads.clock = attempt(CLOCK, parse_showdate)
    reads.alerts = attempt(ALERTS, parse_alerts)
    reads.space = attempt(SPACE, parse_space)
    return reads


def read_from(data) -> HandoverReads:
    """The three reads as an ``AsBuiltData`` carries them (duck-typed: ``asbuilt.py`` imports this module)."""
    return read_handover({cmd: getattr(data, attr, "") for attr, cmd in READS}, data.read_errors,
                         read_at=data.handover_read_at, run_created_at=data.run_created_at)


@dataclass(frozen=True)
class HandoverSummary:
    """SPEC-026 R10: the ``handover`` field of the ``asbuilt.generated`` event. None means not known
    (the read failed), never zero."""

    read_at: str | None
    alerts_new: int | None
    alerts_major: int | None
    oldest_alert: str | None          # the oldest first occurrence, as the array printed it
    cloud_alert: int | None           # the id of the New 0x060000a alert
    read_errors: dict[str, str]

    def as_event(self) -> dict:
        return asdict(self)


def _iso(moment: datetime | None) -> str | None:
    return _utc(moment).isoformat() if moment is not None else None


def summarise(reads: HandoverReads) -> HandoverSummary:
    alerts = reads.alerts
    first = oldest(alerts) if alerts else None
    cloud = cloud_alert(alerts) if alerts else None
    return HandoverSummary(
        read_at=_iso(reads.read_at),
        alerts_new=None if alerts is None else len(alerts),
        alerts_major=None if alerts is None else sum(1 for a in alerts if is_full(a)),
        oldest_alert=first.first_seen if first else None,
        cloud_alert=cloud.id if cloud else None,
        read_errors=dict(reads.errors),
    )
