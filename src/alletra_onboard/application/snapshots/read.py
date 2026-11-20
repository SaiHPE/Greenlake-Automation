"""SPEC-023 R3 — read one array's snapshots and snapshot schedules (read-only).

`read_array` makes every read the step needs: `showversion`, `showdate`, `showsched` and `showcpg` over
the read-only SSH client (ADR 0001), `GET /volumes`, `/volumesets` and `/system` over WSAPI.

Schedules are read with `showsched` because WSAPI has none: `GET /api/v1/schedules` answers HTTP 501,
code 9, "unsupported operation for the resource" (rack13-ARCUS, OS 10.6.0, 2026-11-16).

Pinned to `tests/fixtures/rc_pair/*/showsched.txt` (seven schedules, OS 10.5, 2026-10-07),
`tests/fixtures/rack13_snap/` (no schedules, no snapshots, OS 10.6.0, 2026-11-16; `showsched_one.txt`,
one schedule in the OS 10.6.0 layout, 2026-11-17) and the OS 10.5
captures of 2026-11-17: `d22u27_snap/` (seven schedules, 105 snapshots), `vz_snap/` (a suspended
schedule, 66 snapshots) and `e18u31_snap/` (no schedule, three snapshots).
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli, make_wsapi
from alletra_onboard.application.replication.read import parse_showcpg_free, parse_showversion
from alletra_onboard.domain.errors import ArrayCliError, DeviceError
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.snapshots import ArraySchedule, SnapshotArrayView

#: The snapshot columns of `showvv`, as `lab/snap_capture.py` asked for them.
SHOWVV_SNAPCOLS = (
    "showvv -showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime"
)

# `showsched` columns by header word, because two layouts are real. OS 10.5 (D22U27, E18U31, VZ):
# `SchedName File/Command Interval Min Hour DOM Month DOW CreatedBy Status Alert NextRunTime`. OS 10.6.0
# (rack13-ARCUS, 2026-11-17) adds `Id` before SchedName and `Rebal` before NextRunTime; neither is kept.
# Every column is one token except the command (it has spaces) and NextRunTime: "2026-10-07 20:00:00
# IST" on an active schedule, "--" on a suspended one (VZ, OS 10.5.51), kept as printed.
_SCHED_COLUMNS = {
    "SchedName": "name", "File/Command": "command", "Interval": "interval", "Min": "minute",
    "Hour": "hour", "DOM": "dom", "Month": "month", "DOW": "dow", "CreatedBy": "created_by",
    "Status": "status", "Alert": "alert", "NextRunTime": "next_run",
}
_SCHED_CELL = {
    "command": r"(?P<command>\S.*?)",
    "next_run": r"(?P<next_run>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \S+|\S+)",
}
_RULE = re.compile(r"^\s*-{4,}")
_DATE = re.compile(r"^\d{4}-\d\d-\d\d$")
_EMPTY = ("-", "--", "---")

# createsv options that take a value (`help createsv`, OS 10.5.x and 10.6.0); every other option is
# a flag.
_CREATESV_VALUE_OPTIONS = {"-exp", "-retain", "-addtoset", "-comment", "-i"}


def _sched_row_pattern(header: list[str]) -> re.Pattern[str] | None:
    """The row pattern for a `showsched` header, or None when the header lacks a column the
    schedule needs or repeats one."""
    if len(set(header)) != len(header) or not set(_SCHED_COLUMNS) <= set(header):
        return None
    cells = []
    for column in header:
        field = _SCHED_COLUMNS.get(column)
        cells.append(_SCHED_CELL.get(field, rf"(?P<{field}>\S+)") if field else r"\S+")
    return re.compile(r"^" + r"\s+".join(cells) + r"\s*$")


def _sched_table(text: str) -> list[ArraySchedule] | None:
    """The rows under `showsched`'s header, up to the rule. None when there is no header with every
    column, or when a row under it does not read: a layout this code has not seen must not read as
    "no schedule"."""
    pattern: re.Pattern[str] | None = None
    out: list[ArraySchedule] = []
    for line in (text or "").splitlines():
        if pattern is None:
            tokens = line.split()
            if "SchedName" in tokens[:2] and "File/Command" in tokens:
                pattern = _sched_row_pattern(tokens)
                if pattern is None:
                    return None
            continue
        if _RULE.match(line):
            return out
        if not line.strip():
            continue
        m = pattern.match(line.strip())
        if m is None:
            return None
        out.append(ArraySchedule(**m.groupdict()))
    return out if pattern is not None else None


def parse_showsched(text: str) -> list[ArraySchedule]:
    """`showsched` -> one schedule per row. "No scheduled tasks listed" (and no output, or anything
    that is not its table) is []; `showsched_readable` tells the two apart."""
    return _sched_table(text) or []


def showsched_readable(text: str) -> bool:
    """`showsched` printed its table and every row of it reads, or said it has none ("No scheduled
    tasks listed"). An error, or anything else, is not a read: parse_showsched would make it an empty
    list, which would read as "no schedule"."""
    t = text or ""
    return "No scheduled tasks listed" in t or _sched_table(t) is not None


def parse_createsv(command: str) -> dict:
    """A scheduled `createsv` line -> {read_only, expire, retain, add_to_set, pattern, source}.
    Times stay as the array prints them (`56h`, `1440m`); an option that is absent is "" (False for
    read_only). Anything other than a createsv command gives {}."""
    try:
        tokens = shlex.split(command or "")
    except ValueError:
        tokens = (command or "").split()
    if tokens[:1] != ["createsv"]:
        return {}
    options: dict[str, str] = {}
    flags: set[str] = set()
    positional: list[str] = []
    i = 1
    while i < len(tokens):
        token = tokens[i]
        if token in _CREATESV_VALUE_OPTIONS and i + 1 < len(tokens):
            options[token] = tokens[i + 1]
            i += 2
            continue
        if token.startswith("-"):
            flags.add(token)
        else:
            positional.append(token)
        i += 1
    return {
        "read_only": "-ro" in flags,
        "expire": options.get("-exp", ""),
        "retain": options.get("-retain", ""),
        "add_to_set": options.get("-addtoset", ""),
        "pattern": positional[0] if positional else "",
        "source": positional[1] if len(positional) > 1 else "",
    }


def parse_showvv_snapcols(text: str) -> list[dict[str, str]]:
    """`showvv -showcols …` with time columns (SHOWVV_SNAPCOLS) -> one dict per volume, keyed by the
    header. A time is three tokens ("2026-10-29 14:32:34 IST") and "--" when there is none; "-",
    "--" and "---" read as "". A row whose tokens do not fill the header is dropped. "no vv listed"
    is []."""
    header: list[str] = []
    rows: list[dict[str, str]] = []
    for line in (text or "").splitlines():
        tokens = line.split()
        if not header:
            if tokens[:2] == ["Id", "Name"]:
                header = tokens
            continue
        if _RULE.match(line):
            break
        row = _snapcols_row(header, tokens)
        if row is not None:
            rows.append(row)
    return rows


def _snapcols_row(header: list[str], tokens: list[str]) -> dict[str, str] | None:
    row: dict[str, str] = {}
    i = 0
    for column in header:
        if i >= len(tokens):
            return None
        if column.endswith("Time") and _DATE.match(tokens[i]) and i + 2 < len(tokens):
            row[column] = " ".join(tokens[i:i + 3])
            i += 3
        else:
            row[column] = "" if tokens[i] in _EMPTY else tokens[i]
            i += 1
    return row if i == len(tokens) else None


_SHOWDATE_ROW = re.compile(r"^\s*\d+\s+\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\s+(?P<zone>\S.*?)\s*$")


def parse_showdate_zone(text: str) -> str:
    """`showdate` -> the array's time zone as it prints it: "IST (Asia/Calcutta)". Both
    Asia/Calcutta (D22U27, E18U31) and Asia/Kolkata (VZ, rack13-ARCUS) occur; nothing compares it with a
    fixed name. "" when no node row reads."""
    for line in (text or "").splitlines():
        m = _SHOWDATE_ROW.match(line)
        if m:
            return m.group("zone")
    return ""


def read_array(
    creds: EndpointCreds, *, wsapi_factory: Callable = make_wsapi, array_cli_factory: Callable = make_array_cli,
    progress: Callable[[str], None] | None = None,
) -> SnapshotArrayView:
    """One SSH session and one WSAPI session, read-only. A failed login or read is the view's
    `read_error`: the plan is never built from half a read."""
    view = SnapshotArrayView(host=creds.host)
    say = progress or (lambda _m: None)
    try:
        with array_cli_factory(creds) as cli:
            say(f"Reading {creds.host}: version, time zone, snapshot schedules, CPGs…")
            view.os_version = parse_showversion(cli.run("showversion"))
            view.time_zone = parse_showdate_zone(cli.run("showdate"))
            sched = cli.run("showsched")
            if not showsched_readable(sched):
                first = next((ln.strip() for ln in sched.splitlines() if ln.strip()), "nothing")
                raise ArrayCliError(f"showsched did not list the schedules; it answered: {first}")
            view.schedules = parse_showsched(sched)
            view.cpg_free_mib = parse_showcpg_free(cli.run("showcpg"))
        with wsapi_factory(creds) as wsapi:
            say(f"Reading {creds.host}: volumes, volume sets and their snapshots…")
            system = wsapi.system_info()
            view.name = str(system.get("name") or "")
            view.time_zone = view.time_zone or str(system.get("timeZone") or "")
            seconds = (system.get("parameters") or {}).get("VVRetentionTimeMax")
            view.retention_max_hours = int(seconds) // 3600 if isinstance(seconds, int | float) else 0
            view.volumes = wsapi.volumes()
            view.vvsets = wsapi.volume_sets()
    except DeviceError as exc:  # the step reports it; the operator fixes access and reads again
        view.read_error = f"Could not read {creds.host}: {exc}"
    return view
