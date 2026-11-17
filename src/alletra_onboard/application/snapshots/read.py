"""SPEC-023 R3 — read one array's snapshots and snapshot schedules (read-only).

`read_array` makes every read the step needs: `showversion`, `showdate`, `showsched` and `showcpg` over
the read-only SSH client (ADR 0001), `GET /volumes`, `/volumesets` and `/system` over WSAPI.

Schedules are read with `showsched` because WSAPI has none: `GET /api/v1/schedules` answers HTTP 501,
code 9, "unsupported operation for the resource" (rack13-ARCUS, OS 10.6.0, 2026-11-16).

Pinned to `tests/fixtures/rc_pair/*/showsched.txt` (seven schedules, OS 10.5, 2026-10-07),
`tests/fixtures/rack13_snap/` (no schedules, no snapshots, OS 10.6.0, 2026-11-16) and the OS 10.5
captures of 2026-11-17: `d22u27_snap/` (seven schedules, 105 snapshots), `vz_snap/` (a suspended
schedule, 66 snapshots) and `e18u31_snap/` (no schedule, three snapshots).
"""

from __future__ import annotations

import re
import shlex
from collections.abc import Callable

from alletra_onboard.application.provisioning.clients import make_array_cli, make_wsapi
from alletra_onboard.application.replication.read import parse_showcpg_free, parse_showversion
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.snapshots import ArraySchedule, SnapshotArrayView

#: The snapshot columns of `showvv`, as `lab/snap_capture.py` asked for them.
SHOWVV_SNAPCOLS = (
    "showvv -showcols Id,Name,Prov,Type,CopyOf,Rd,CPG,CreationTime,ExpirationTime,RetentionEndTime"
)

# Name, then the command (it has spaces), then nine single-token columns (Interval, Min, Hour, DOM,
# Month, DOW, CreatedBy, Status, Alert), then NextRunTime: "2026-10-07 20:00:00 IST" on an active
# schedule. A suspended one prints "--" (VZ, OS 10.5.51, 2026-11-17); it is kept as printed rather
# than shifting every other column.
_SCHED_ROW = re.compile(
    r"^(?P<name>\S+)\s+(?P<command>\S.*?)"
    r"\s+(?P<interval>\S+)\s+(?P<minute>\S+)\s+(?P<hour>\S+)\s+(?P<dom>\S+)\s+(?P<month>\S+)"
    r"\s+(?P<dow>\S+)\s+(?P<created_by>\S+)\s+(?P<status>\S+)\s+(?P<alert>\S+)"
    r"\s+(?P<next_run>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \S+|\S+)\s*$"
)
_RULE = re.compile(r"^\s*-{4,}")
_DATE = re.compile(r"^\d{4}-\d\d-\d\d$")
_EMPTY = ("-", "--", "---")

# createsv options that take a value (`help createsv`, OS 10.5.x and 10.6.0); every other option is
# a flag.
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


def showsched_readable(text: str) -> bool:
    """`showsched` printed its table, or said it has none ("No scheduled tasks listed"). An error, or
    anything else, is not a read: parse_showsched would make it an empty list, which would read as "no
    schedule"."""
    t = text or ""
    return "No scheduled tasks listed" in t or any(line.split()[:1] == ["SchedName"] for line in t.splitlines())


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
                raise RuntimeError(f"showsched did not list the schedules; it answered: {first}")
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
    except Exception as exc:  # noqa: BLE001 - the step reports it; the operator fixes access and reads again
        view.read_error = f"Could not read {creds.host}: {exc}"
    return view
