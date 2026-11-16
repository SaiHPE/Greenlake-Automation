"""SPEC-023 R3 — read one array's snapshots and snapshot schedules (read-only).

Schedules are read with `showsched` because WSAPI has none: `GET /api/v1/schedules` answers HTTP 501,
code 9, "unsupported operation for the resource" (rack13-ARCUS, OS 10.6.0, 2026-11-16).

Pinned to `tests/fixtures/rc_pair/*/showsched.txt` (seven schedules, OS 10.5, 2026-10-07) and
`tests/fixtures/rack13_snap/` (no schedules, no snapshots, OS 10.6.0, 2026-11-16).
"""

from __future__ import annotations

import re
import shlex

from alletra_onboard.domain.snapshots import ArraySchedule

#: The snapshot columns of `showvv`, as `lab/snap_capture.py` asked for them.
SHOWVV_SNAPCOLS = (
    "showvv -showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime"
)

# Name, then the command (it has spaces), then nine single-token columns (Interval, Min, Hour, DOM,
# Month, DOW, CreatedBy, Status, Alert), then NextRunTime: "2026-10-07 20:00:00 IST" on every
# captured row. A NextRunTime that is one token (not captured yet; a suspended schedule may print
# one) is kept as it is rather than shifting every other column.
_SCHED_ROW = re.compile(
    r"^(?P<name>\S+)\s+(?P<command>\S.*?)"
    r"\s+(?P<interval>\S+)\s+(?P<minute>\S+)\s+(?P<hour>\S+)\s+(?P<dom>\S+)\s+(?P<month>\S+)"
    r"\s+(?P<dow>\S+)\s+(?P<created_by>\S+)\s+(?P<status>\S+)\s+(?P<alert>\S+)"
    r"\s+(?P<next_run>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \S+|\S+)\s*$"
)
_RULE = re.compile(r"^\s*-{4,}")
_DATE = re.compile(r"^\d{4}-\d\d-\d\d$")
_EMPTY = ("-", "--", "---")

# createsv options that take a value (`help createsv`, OS 10.6.0); every other option is a flag.
_CREATESV_VALUE_OPTIONS = {"-exp", "-retain", "-addtoset", "-comment", "-i"}


def parse_showsched(text: str) -> list[ArraySchedule]:
    """`showsched` -> one schedule per row. "No scheduled tasks listed" (and no output) is []."""
    out: list[ArraySchedule] = []
    in_table = False
    for line in (text or "").splitlines():
        if not in_table:
            in_table = line.split()[:1] == ["SchedName"]
            continue
        if _RULE.match(line):
            break
        m = _SCHED_ROW.match(line.strip())
        if m:
            out.append(ArraySchedule(**m.groupdict()))
    return out


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
