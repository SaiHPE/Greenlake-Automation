"""Snapshot-context models (SPEC-023): what the Snapshots tab asks for, what the array holds for
snapshots and schedules, and the plan. No I/O.

A row asks for a snapshot now (over WSAPI, `<volume>.initial` per member) and a schedule (the array's
own `createsched`, ADR 0016). Names, the cron and the command lines are derived here and nowhere else
(LESSONS 19): the plan, apply, verify and the as-built all read them from these functions.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Literal

from pydantic import BaseModel, Field

from alletra_onboard.domain.shared import ArrayVolumeRecord, RemovalItem

SnapshotUnit = Literal["minutes", "hours", "days"]

#: The periods a row may ask for: DSCC's schedule periods (reference mirror,
#: `volume-sets/devicetype4createprotectionpolicy.md`) without the month, so a tool-made schedule is
#: one DSCC could also express (SPEC-023 R1).
ALLOWED_EVERY: dict[str, tuple[int, ...]] = {"minutes": (15, 20, 30), "hours": (1, 2, 3, 4, 6, 8, 12), "days": (1,)}
#: `help createsv` (OS 10.6.0 on rack13-ARCUS, 2026-11-16; OS 10.5.0, 10.5.51 and 10.5.60 on the lab
#: arrays, 2026-11-17): `-exp` and `-retain` take 1 minute to 1825 days. 1825 days is 43800 hours.
HOURS_MAX = 43800
#: `help removesched` takes at most 31 characters on every OS captured, and so does `help createsched`
#: on OS 10.5. On 10.6.0 `createsched` allows 127: a longer name could be created and never removed
#: by name.
SCHEDULE_NAME_MAX = 31
#: `help createsv`: at most 2048 virtual copies per volume (ADR 0016 decision 3).
SNAPSHOTS_PER_VOLUME_MAX = 2048
#: The name each scheduled snapshot gets: `<volume>.YYMMDDHHMMSS` (`test999.261116080000`, D22U27).
SCHEDULE_PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"
#: What the pattern adds to a member's name: a dot and twelve digits.
SCHEDULE_SUFFIX_LEN = 13
#: The snapshot taken now is `<volume>.initial`: a fixed name, so a rerun finds it (LESSONS 37).
NOW_SUFFIX = ".initial"
#: Snapshot names: 31 characters up to OS 10.4.0, 248 from 10.4.2 (DSCC's limit on B10000; the CLI
#: on 10.5 and 10.6 takes 255, the plan keeps the stricter).
SNAPSHOT_NAME_MAX_OLD = 31
SNAPSHOT_NAME_MAX = 248
_LONG_NAMES_FROM = (10, 4, 2)

#: SPEC-023 R2: a run with the Snapshots step from a workbook without the tab (HTTP 422).
SNAPSHOTS_TAB_NEEDED = (
    "The Snapshots step needs the 'Snapshots' tab (the volume sets or volumes to snapshot), and this "
    "workbook has none filled in."
)


def derive_schedule_name(source: str) -> str:
    """`<source>_snap`, shortened with a stable 4-hex suffix when that would exceed 31 characters
    (the suffix is a hash of the full source name, so the same source always derives the same name)."""
    name = f"{source}_snap"
    if len(name) <= SCHEDULE_NAME_MAX:
        return name
    tag = hashlib.sha1(source.encode("utf-8")).hexdigest()[:4]
    keep = SCHEDULE_NAME_MAX - len("_snap") - len(tag) - 1
    return f"{source[:keep]}_{tag}_snap"


def schedule_cron(every: int, unit: SnapshotUnit, at_hour: int = 0, days: list[int] | None = None) -> str:
    """The five cron fields the array runs the schedule on (SPEC-023 R4), in the array's local time.
    Minutes: on the minutes of every hour. Hours: from the start hour, stepping by N, round the clock
    and sorted (`*` when N is 1). A day: at the start hour. Days of week: `*`, or 0-6 with 0 = Sunday."""
    dow = ",".join(str(d) for d in sorted(set(days))) if days else "*"
    if unit == "minutes":
        return f"{','.join(str(m) for m in range(0, 60, every))} * * * {dow}"
    if unit == "hours":
        hours = "*" if every == 1 else ",".join(str(h) for h in sorted({(at_hour + k * every) % 24 for k in range(24 // every)}))
        return f"0 {hours} * * {dow}"
    return f"0 {at_hour} * * {dow}"


#: The range of each cron field: minute, hour, day of month, month, day of week (0 = Sunday).
_CRON_RANGES = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
_UNIT_MINUTES = {"minutes": 1, "hours": 60, "days": 1440}
DAY_NAMES = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


def cron_field_values(text: str, lo: int, hi: int) -> frozenset[int] | None:
    """One cron field as the numbers it stands for: `*`, `5`, `00`, `0,4,8`, `1-5`, `*/15`. None when it
    does not read (an `@hourly` row, an interval schedule's `-`)."""
    values: set[int] = set()
    for part in text.split(","):
        base, _, step_text = part.partition("/")
        try:
            step = int(step_text) if step_text else 1
            if base == "*":
                first, last = lo, hi
            elif "-" in base:
                first, last = (int(x) for x in base.split("-", 1))
            else:
                first = last = int(base)
        except ValueError:
            return None
        if step < 1 or first < lo or last > hi or first > last:
            return None
        values.update(range(first, last + 1, step))
    return frozenset(values)


def cron_values(cron: str) -> tuple[frozenset[int], ...] | None:
    """The five fields of a cron as numbers, or None when one does not read."""
    fields = cron.split()
    if len(fields) != 5:
        return None
    out = tuple(cron_field_values(f, lo, hi) for f, (lo, hi) in zip(fields, _CRON_RANGES, strict=True))
    return None if any(v is None for v in out) else out  # type: ignore[return-value]


def same_cron(a: str, b: str) -> bool:
    """Two crons run at the same times: compared as numbers, so `00` is `0` (D22U27 prints both)."""
    va, vb = cron_values(a), cron_values(b)
    return va is not None and va == vb


def same_command(a: str, b: str) -> bool:
    return " ".join(a.split()) == " ".join(b.split())


def period_minutes(every: int, unit: SnapshotUnit) -> int:
    return every * _UNIT_MINUTES[unit]


def snapshot_name_max(os_version: str) -> int:
    """The longest snapshot name the array's OS takes. An OS version that does not read is held to
    the older, stricter limit."""
    try:
        version = tuple(int(part) for part in os_version.strip().split(".")[:3])
    except ValueError:
        return SNAPSHOT_NAME_MAX_OLD
    if not version:
        return SNAPSHOT_NAME_MAX_OLD
    return SNAPSHOT_NAME_MAX if version >= _LONG_NAMES_FROM else SNAPSHOT_NAME_MAX_OLD


def now_snapshot_name(member: str) -> str:
    """The snapshot taken now of one member volume."""
    return f"{member}{NOW_SUFFIX}"


def is_scheduled_snapshot_name(member: str, name: str) -> bool:
    """A name the schedule's pattern gives a snapshot of `member`: `<member>.` and twelve digits. Remote
    Copy's own snapshots of the same member (`rcpy.41.269.5`) never match (ADR 0016 decision 5)."""
    return re.fullmatch(rf"{re.escape(member)}\.\d{{12}}", name) is not None


class SnapshotRequest(BaseModel):
    """One row of the Snapshots tab: a volume set (or a volume), a snapshot now, a schedule, or both."""

    source: str
    kind: Literal["set", "volume"] = "set"
    snapshot_now: bool = False
    every: int | None = None
    unit: SnapshotUnit | None = None
    at_hour: int = 0
    days: list[int] = Field(default_factory=list[int])   # 0 = Sunday … 6 = Saturday; empty = every day
    expire_hours: int
    retain_hours: int | None = None
    read_only: bool = True
    schedule_name: str = ""

    @property
    def source_ref(self) -> str:
        """The CLI and WSAPI source token: `set:<set>` or the volume name."""
        return f"set:{self.source}" if self.kind == "set" else self.source

    @property
    def name(self) -> str:
        """The schedule's name: the one on the tab, else derived from the source."""
        return self.schedule_name or derive_schedule_name(self.source)

    @property
    def has_schedule(self) -> bool:
        return self.every is not None and self.unit is not None

    @property
    def cron(self) -> str:
        """The schedule's cron, or "" when the row asks for no schedule."""
        if not self.has_schedule:
            return ""
        return schedule_cron(self.every, self.unit, self.at_hour, self.days)  # type: ignore[arg-type]

    @property
    def kept_alive(self) -> int:
        """The most snapshots the schedule keeps alive at once: Keep for over the period, rounded up.
        Days of the week are not subtracted, so the count is never low (SPEC-023 R4)."""
        if not self.has_schedule:
            return 0
        return math.ceil(self.expire_hours * 60 / period_minutes(self.every, self.unit))  # type: ignore[arg-type]

    def schedule_words(self) -> str:
        """The schedule in words: "every 4 hours from 00:00, every day, kept 24 hours, read-only"."""
        if not self.has_schedule:
            return ""
        unit = self.unit.removesuffix("s") if self.every == 1 else self.unit  # type: ignore[union-attr]
        when = f"every {self.every} {unit}" if self.every != 1 else f"every {unit}"
        if self.unit == "hours" and self.every != 1:
            when += f" from {self.at_hour:02d}:00"
        elif self.unit == "days":
            when += f" at {self.at_hour:02d}:00"
        days = ", ".join(DAY_NAMES[d] for d in sorted(set(self.days))) if self.days else "every day"
        mode = "read-only" if self.read_only else "read-write"
        return f"{when}, {days}, kept {self.expire_hours} hours, {mode}"

    def summary(self, *, named: bool = False) -> str:
        """The row in words, for the step page: "Snapshot now · every 4 hours from 00:00, every day, kept
        24 hours, read-only". `named` puts the schedule's name first, for the sheet review, which has no
        column for it: "Snapshot now · schedule zz_sn_vvs_snap, every 4 hours …"."""
        mode = "read-only" if self.read_only else "read-write"
        if self.has_schedule:
            rest = f"schedule {self.name}, {self.schedule_words()}" if named else self.schedule_words()
        else:
            rest = f"kept {self.expire_hours} hours, {mode}"
        return " · ".join(part for part in ("Snapshot now" if self.snapshot_now else "", rest) if part)

    def createsv_command(self) -> str:
        """The command the schedule runs. The domain renders a lock (`-retain`); the plan refuses a row
        that asks for one in the first slice (ADR 0016 decision 2)."""
        parts = ["createsv", "-f"]
        if self.read_only:
            parts.append("-ro")
        parts.append(f"-exp {self.expire_hours}h")
        if self.retain_hours:
            parts.append(f"-retain {self.retain_hours}h")
        parts += [SCHEDULE_PATTERN, self.source_ref]
        return " ".join(parts)

    def createsched_command(self) -> str:
        """The one form ADR 0016 allows: `createsched -f "<createsv>" "<cron>" <name>`."""
        return f'createsched -f "{self.createsv_command()}" "{self.cron}" {self.name}'

    def now_command(self) -> str:
        """The CLI line the snapshot now over WSAPI equals (SPEC-023 R4 table, row 1)."""
        target = (f"@vvname@{NOW_SUFFIX} set:{self.source}" if self.kind == "set"
                  else f"{now_snapshot_name(self.source)} {self.source}")
        return f"createsv{' -ro' if self.read_only else ''} -exp {self.expire_hours}h {target}"


class SnapshotIntent(BaseModel):
    """The Snapshots tab, parsed: one request per row."""

    requests: list[SnapshotRequest] = Field(default_factory=list[SnapshotRequest])


class ArraySchedule(BaseModel):
    """One row of `showsched`, as printed. Cron fields stay text (`00` and `0` both occur)."""

    name: str
    command: str
    interval: str
    minute: str
    hour: str
    dom: str
    month: str
    dow: str
    created_by: str
    status: str
    alert: str
    next_run: str

    @property
    def cron(self) -> str:
        return f"{self.minute} {self.hour} {self.dom} {self.month} {self.dow}"


class SnapshotArrayView(BaseModel):
    """Everything the Snapshots step read from the run's array, read-only (SPEC-023 R3)."""

    host: str = ""
    name: str = ""
    os_version: str = ""
    time_zone: str = ""                     # as the array prints it: Asia/Calcutta and Asia/Kolkata both occur
    volumes: list[ArrayVolumeRecord] = Field(default_factory=list[ArrayVolumeRecord])
    vvsets: dict[str, list[str]] = Field(default_factory=dict)
    schedules: list[ArraySchedule] = Field(default_factory=list[ArraySchedule])
    cpg_free_mib: dict[str, int] = Field(default_factory=dict)
    retention_max_hours: int = 0            # GET /system VVRetentionTimeMax / 3600; the lock's cap, once allowed
    read_error: str = ""

    def volume(self, name: str) -> ArrayVolumeRecord | None:
        return next((v for v in self.volumes if v.name == name), None)

    def schedule(self, name: str) -> ArraySchedule | None:
        return next((s for s in self.schedules if s.name == name), None)


class SnapshotAction(BaseModel):
    """One planned write: the snapshot now of one row (every member at once), or its schedule."""

    kind: Literal["snapshot", "schedule"]
    name: str
    source: str
    state: Literal["create", "exists", "conflict"]
    reason: str = ""
    members: list[str] = Field(default_factory=list)
    cli: str = ""                # the CLI line the write equals
    call: str = ""               # the call it makes, as text (WSAPI, or the write client over SSH)


class SnapshotPlan(BaseModel):
    actions: list[SnapshotAction] = Field(default_factory=list[SnapshotAction])
    notes: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    error: str | None = None
    # Set when the step holds the plan for approval; the apply must quote it back (BL-52).
    plan_id: str = ""


class SnapshotOutcome(BaseModel):
    kind: Literal["snapshot", "schedule"]
    name: str
    source: str
    status: Literal["created", "exists", "skipped", "failed"]
    detail: str = ""


class SnapshotResult(BaseModel):
    """What one apply did (SPEC-023 R5) and the lines that undo it (R6), in REMOVAL_ORDER."""

    outcomes: list[SnapshotOutcome] = Field(default_factory=list[SnapshotOutcome])
    removals: list[RemovalItem] = Field(default_factory=list[RemovalItem])
    removal_notes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    schedules_created: list[str] = Field(default_factory=list)
    started_at: str = ""            # ISO 8601, when the apply began: a schedule's snapshots are counted from it
    error: str | None = None


SnapshotVerdict = Literal["scheduled", "taking", "not_scheduled", "none"]


class SnapshotRowCheck(BaseModel):
    """SPEC-023 R7, one row: the snapshot now as read, and the schedule's verdict."""

    source: str
    schedule: str = ""
    verdict: SnapshotVerdict = "none"     # none: the row asks for no schedule
    detail: str = ""
    next_run: str = ""
    taken: int = 0
    now_ok: bool | None = None            # None: the row asks for no snapshot now
    now_detail: str = ""


class SnapshotVerification(BaseModel):
    rows: list[SnapshotRowCheck] = Field(default_factory=list[SnapshotRowCheck])
    notes: list[str] = Field(default_factory=list)
    error: str | None = None
