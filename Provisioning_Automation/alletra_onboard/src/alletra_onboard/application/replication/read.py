"""SPEC-016 R1 — read ONE array's Remote Copy state over the read-only SSH client (ADR 0001).

Every parser here is pinned to `tests/fixtures/rc_pair/` (AlletraMP_D22U27 <-> AlletraMP_E18U31,
OS 10.5.0, captured 2026-10-07). The fixtures README lists the facts each one rests on.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import structlog

from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.domain.array_parse import (
    NSP,
    blank_unset,
    parse_cli_sets,
    parse_showport_rcip,
    parse_showport_roles,
    parse_showsys,
    parse_showversion,
)
from alletra_onboard.domain.errors import DeviceError
from alletra_onboard.domain.replication import (
    RcGroup,
    RcGroupDetail,
    RcGroupVolume,
    RcLink,
    RcTarget,
    RcTransport,
    RcVolumeDetail,
    ReplicationArrayView,
)
from alletra_onboard.domain.shared import EndpointCreds

_log = structlog.get_logger(__name__)


def _int(text: str) -> int | None:
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def parse_showrctransport_rcip(text: str) -> list[RcTransport]:
    """`showrctransport -rcip`: N:S:P State HwAddr IPAddress PeerIPAddress Netmask/PrefixLen Gateway MTU Rate Duplex."""
    out: list[RcTransport] = []
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) < 6 or not NSP.match(p[0]):
            continue
        out.append(RcTransport(
            nsp=p[0], state=p[1], ip=blank_unset(p[3]), peer_ip=blank_unset(p[4]), netmask=blank_unset(p[5]),
            gateway=blank_unset(p[6]) if len(p) > 6 else "",
        ))
    return out


def parse_showrcopy(text: str) -> dict:
    """`showrcopy` (or any of its `targets` / `links` / `groups` subsets) -> {status, health, targets,
    links, groups}.

    Sections are titled "Remote Copy System Information" (Status: Started, Normal), "Target
    Information", "Link Information", "Group Information". Each group is a block: a `Name Target
    Status Role Mode Options` header, the group row (Options may be absent), a `LocalVV ID RemoteVV
    ID SyncStatus LastSyncTime` header, then one row per volume. The capture shows a whitespace-only
    line between a wrapped header and its group row, so blank lines never end a block — only the
    next header or section does. A missing group prints an "Error: group matching … does not exist"
    line on stderr (kept in the fixture) and an empty Group Information section."""
    status = health = ""
    targets: list[RcTarget] = []
    links: list[RcLink] = []
    groups: list[RcGroup] = []
    section = ""
    expect_group_row = in_volumes = False
    current: RcGroup | None = None

    for raw in (text or "").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("Remote Copy System Information"):
            section = "system"
            continue
        if stripped.startswith("Target Information"):
            section, current = "targets", None
            continue
        if stripped.startswith("Link Information"):
            section, current = "links", None
            continue
        if stripped.startswith("Group Information"):
            section, current = "groups", None
            continue
        if stripped.startswith("Error:"):
            continue
        tokens = stripped.split()
        if section == "system":
            if stripped.startswith("Status:"):
                parts = [s.strip() for s in stripped[len("Status:"):].split(",")]
                status, health = parts[0], (parts[1] if len(parts) > 1 else "")
            continue
        if section == "targets":
            if tokens[0] == "Name" or len(tokens) < 4:
                continue
            targets.append(RcTarget(
                name=tokens[0], id=_int(tokens[1]), type=tokens[2], status=tokens[3],
                options=blank_unset(tokens[4]) if len(tokens) > 4 else "",
                policy=tokens[5] if len(tokens) > 5 else "",
            ))
            continue
        if section == "links":
            if tokens[0] == "Target" or len(tokens) < 4:
                continue
            links.append(RcLink(target=tokens[0], nsp=tokens[1], address=tokens[2], status=tokens[3]))
            continue
        if section == "groups":
            if tokens[:5] == ["Name", "Target", "Status", "Role", "Mode"]:
                expect_group_row, in_volumes, current = True, False, None
                continue
            if tokens[0] == "LocalVV":
                expect_group_row, in_volumes = False, True
                continue
            if expect_group_row and len(tokens) >= 5:
                options, period, last_sync = _group_options(" ".join(tokens[5:]))
                current = RcGroup(
                    name=tokens[0], target=tokens[1], status=tokens[2], role=tokens[3], mode=tokens[4],
                    options=options, period=period, last_sync=last_sync,
                )
                groups.append(current)
                expect_group_row = False
                continue
            if in_volumes and current is not None and len(tokens) >= 5:
                rest = tokens[5:]
                progress = ""
                if rest and re.fullmatch(r"\(\d+%\)", rest[0]):
                    # live 2026-10-10: a volume syncing shows "Syncing (100%)" in the SyncStatus column
                    progress, rest = rest[0].strip("()"), rest[1:]
                current.volumes.append(RcGroupVolume(
                    local_name=tokens[0], local_id=_int(tokens[1]), remote_name=tokens[2],
                    remote_id=_int(tokens[3]), sync_status=tokens[4], sync_progress=progress,
                    last_sync=" ".join(rest),
                ))
    return {"status": status, "health": health, "targets": targets, "links": links, "groups": groups}


def _group_options(text: str) -> tuple[list[str], str, str]:
    """A group's Options column -> (policies, period, last sync). Periodic rows carry spaces in it (live
    2026-10-09 23:39): "Last-Sync 2026-10-09 23:39:23 IST, Period 5m,auto_recover,over_per_alert,auto_synchronize";
    a secondary prints "Period 5m,auto_recover,..." without the Last-Sync part (Primera OS 4.6.20, 2026-11-19)."""
    options, period, last_sync = [], "", ""
    for part in (p.strip() for p in text.split(",")):
        if part.startswith("Last-Sync "):
            last_sync = part[len("Last-Sync "):].strip()
        elif part.startswith("Period "):
            period = part[len("Period "):].strip()
        elif part:
            options.append(part)
    return options, period, last_sync


def _header(line: str) -> list[tuple[int, str]]:
    """A table header as (start column, name). The volume header names two columns ID: the one after
    LocalVV is LocalID, the one after RemoteVV RemoteID."""
    columns: list[tuple[int, str]] = []
    for m in re.finditer(r"\S+", line):
        name = m.group()
        if name == "ID" and columns and columns[-1][1] in ("LocalVV", "RemoteVV"):
            name = columns[-1][1][:-2] + "ID"
        columns.append((m.start(), name))
    return columns


def _cells(line: str, columns: list[tuple[int, str]]) -> dict[str, str]:
    """A row cut by its header. A word belongs to the last column that starts at or before its LAST
    character: names and words are left-aligned under their heading, IDs right-aligned and may start
    left of it ("  demo_rc_vol01 51913" under "  LocalVV        ID"). A word with a space in it (a time,
    the periodic Options) is joined back. A column with nothing under it is ""."""
    cells: dict[str, list[str]] = {name: [] for _start, name in columns}
    for m in re.finditer(r"\S+", line):
        last = m.end() - 1
        name = next((n for start, n in reversed(columns) if start <= last), columns[0][1])
        cells[name].append(m.group())
    return {name: " ".join(words) for name, words in cells.items()}


def parse_showrcopy_detail(text: str) -> list[RcGroupDetail]:
    """`showrcopy -d groups <group>` (or a whole `showrcopy -d`) -> every group block: the group's row
    and one row per volume, every column the array prints. Columns are found by their header, so the
    Primera's LocalSnapCpg / RmSnapCpg and a volume header without LocalSet / RemoteSet (a secondary on
    OS 4.6.20) read the same way. Pinned to `tests/fixtures/rc_pair/` (OS 10.5.0, sync and periodic) and
    `tests/fixtures/rcip_pair/showrcopy_d/` (OS 10.6.0 and Primera OS 4.6.20, periodic). The Target and
    Link sections are skipped; a missing group prints an Error line and no block."""
    groups: list[RcGroupDetail] = []
    section = ""
    group_columns: list[tuple[int, str]] = []
    volume_columns: list[tuple[int, str]] = []
    expect_group_row = False
    current: RcGroupDetail | None = None
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "Error:")):
            continue
        if stripped.endswith("Information") and not raw.startswith(" "):
            section, current, expect_group_row = stripped, None, False
            continue
        if section != "Group Information":
            continue
        words = stripped.split()
        if words[0] == "Name" and "Target" in words and "Mode" in words:
            group_columns, expect_group_row, current = _header(line), True, None
            continue
        if words[0] == "LocalVV":
            volume_columns = _header(line)
            continue
        if expect_group_row:
            row = _cells(line, group_columns)
            options, period, last_sync = _group_options(row.get("Options", ""))
            current = RcGroupDetail(
                name=row.get("Name", ""), id=_int(row.get("ID", "")), target=row.get("Target", ""),
                status=row.get("Status", ""), role=row.get("Role", ""), mode=row.get("Mode", ""),
                local_user_cpg=row.get("LocalUserCpg", ""), local_snap_cpg=row.get("LocalSnapCpg", ""),
                remote_user_cpg=row.get("RmUserCpg", ""), remote_snap_cpg=row.get("RmSnapCpg", ""),
                options=options, period=period, last_sync=last_sync,
            )
            groups.append(current)
            expect_group_row = False
            continue
        if current is not None and volume_columns:
            row = _cells(line, volume_columns)
            current.volumes.append(RcVolumeDetail(
                local_name=row.get("LocalVV", ""), local_id=_int(row.get("LocalID", "")),
                remote_name=row.get("RemoteVV", ""), remote_id=_int(row.get("RemoteID", "")),
                sync_status=row.get("SyncStatus", ""), resync_snapshot=row.get("Resync_ss", ""),
                sync_snapshot=row.get("Sync_ss", ""), volume_iteration=row.get("VV_iter", ""),
                resync_iteration=row.get("R_iter", ""), sync_iteration=row.get("S_iter", ""),
                last_sync=row.get("LastSyncTime", ""), local_set=row.get("LocalSet", ""),
                remote_set=row.get("RemoteSet", ""),
            ))
    return groups


def group_detail_command(group: str) -> str:
    """The one form the tool sends: `-d` only changes what is shown (the array's help: "Displays more
    detailed configuration information"), `groups <name>` limits it to one group."""
    return f"showrcopy -d groups {group}"


def read_group_details(
    creds: EndpointCreds, groups: list[str], *, array_cli_factory: Callable = make_array_cli,
    progress: Callable[[str], None] | None = None,
) -> tuple[dict[str, RcGroupDetail], dict[str, str]]:
    """One SSH session, read-only: `showrcopy -d groups <group>` for each group -> ({group: detail},
    {group: why it is missing}). A failed login is every group's reason; the caller notes it and goes on."""
    details: dict[str, RcGroupDetail] = {}
    errors: dict[str, str] = {}
    try:
        with array_cli_factory(creds) as cli:
            if progress:
                progress(f"Reading {creds.host}: each group's settings and volumes (showrcopy -d)…")
            for group in groups:
                try:
                    text = cli.run(group_detail_command(group))
                except DeviceError as exc:  # one group's read costs that group only
                    errors[group] = str(exc)
                    continue
                found = next((g for g in parse_showrcopy_detail(text) if g.name == group), None)
                if found is None:
                    first = next((ln.strip() for ln in text.splitlines() if ln.strip().startswith("Error")), "")
                    errors[group] = first or "the array printed no block for it"
                else:
                    details[group] = found
    except DeviceError as exc:  # a report, never a gate
        errors = {group: f"Could not read {creds.host}: {exc}" for group in groups if group not in details}
    return details, errors


def parse_showcpg_free(text: str) -> dict[str, int]:
    """`showcpg` -> {cpg: free MiB}. Columns Id Name Warn% VVs TPVVs TDVVs Used Free Total; the
    `total` footer row has no Id."""
    out: dict[str, int] = {}
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) >= 9 and p[0].isdigit() and p[1] != "total":
            free = _int(p[-2])
            if free is not None:
                out[p[1]] = free
    return out


def parse_showvv_sizes(text: str) -> dict[str, int]:
    """`showvv -showcols Name,VSize_MB` (an Id column is tolerated) -> {volume: MiB}; the rule and
    `total` footer rows are skipped."""
    out: dict[str, int] = {}
    for line in (text or "").splitlines():
        p = line.split()
        if p and p[0].isdigit():       # a leading Id column, if the caller asked for one
            p = p[1:]
        if len(p) < 2 or p[0] in ("Name", "total") or p[0].startswith("-") or not p[-1].isdigit():
            continue
        out[p[0]] = int(p[-1])
    return out


_SHOWDATE_ROW = re.compile(r"^\s*\d+\s+(?P<when>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s+(?P<zone>\S.*?)\s*$")


def parse_showdate(text: str) -> tuple[datetime | None, str]:
    """`showdate` -> (the first node's local time, naive; its zone as printed: "IST (Asia/Kolkata)").
    (None, "") when no node row reads."""
    for line in (text or "").splitlines():
        m = _SHOWDATE_ROW.match(line)
        if m:
            return datetime.strptime(m.group("when"), "%Y-%m-%d %H:%M:%S"), m.group("zone")
    return None, ""


def utc_offset_minutes(array_local: datetime, utc_now: datetime) -> int:
    """The array's local time minus UTC, to the quarter hour (every zone's offset is a multiple of 15
    minutes, so a clock a few minutes off still gives the right one). Needs no time zone database:
    the Windows jump box has none."""
    minutes = (array_local - utc_now.astimezone(UTC).replace(tzinfo=None)).total_seconds() / 60
    return round(minutes / 15) * 15


def array_time(iso_utc: str, view: ReplicationArrayView) -> str:
    """A UTC timestamp in the array's local time with its zone, as the array writes its own times
    ("2026-10-10 15:50:40 IST"); in UTC when its `showdate` did not read."""
    when = datetime.fromisoformat(iso_utc).astimezone(UTC)
    if view.utc_offset_minutes is None:
        return when.strftime("%Y-%m-%d %H:%M:%S UTC")
    local = when.replace(tzinfo=None) + timedelta(minutes=view.utc_offset_minutes)
    hours, minutes = divmod(abs(view.utc_offset_minutes), 60)
    zone = view.time_zone.split()[0] if view.time_zone else \
        f"UTC{'-' if view.utc_offset_minutes < 0 else '+'}{hours:02d}:{minutes:02d}"
    return f"{local:%Y-%m-%d %H:%M:%S} {zone}"


def read_array(
    creds: EndpointCreds, *, array_cli_factory: Callable = make_array_cli,
    progress: Callable[[str], None] | None = None,
) -> ReplicationArrayView:
    """One SSH session, read-only, every `show*` the step needs. A failed login or connection is
    the view's `read_error`; a failed individual read leaves that part empty (and is noted)."""
    view = ReplicationArrayView(host=creds.host)

    def _p(message: str) -> None:
        if progress:
            progress(message)

    try:
        with array_cli_factory(creds) as cli:
            _p(f"Reading {creds.host}: system, RCIP ports, Remote Copy…")
            sysinfo = parse_showsys(cli.run("showsys"))
            view.name, view.serial, view.system_id = sysinfo.get("name", ""), sysinfo.get("serial", ""), sysinfo.get("id")
            view.os_version = parse_showversion(cli.run("showversion"))
            view.ports, view.fc_node_wwn = parse_showport_roles(cli.run("showport"))
            view.rcip_ports = parse_showport_rcip(cli.run("showport -rcip"))
            view.transports = parse_showrctransport_rcip(cli.run("showrctransport -rcip"))
            rc = parse_showrcopy(cli.run("showrcopy"))
            view.rc_status, view.rc_health = rc["status"], rc["health"]
            view.targets, view.links, view.groups = rc["targets"], rc["links"], rc["groups"]
            view.cpg_free_mib = parse_showcpg_free(cli.run("showcpg"))
            view.vvsets = dict(parse_cli_sets(cli.run("showvvset")))
            view.volume_size_mib = parse_showvv_sizes(cli.run("showvv -showcols Name,VSize_MB"))
            try:
                # the zone the array writes its times in (a group's last sync): only for showing times
                local, view.time_zone = parse_showdate(cli.run("showdate"))
                if local is not None:
                    view.utc_offset_minutes = utc_offset_minutes(local, datetime.now(UTC))
            except (DeviceError, OSError, ValueError) as exc:  # times are then shown in UTC
                _log.debug("showdate_read_failed", host=creds.host, error=str(exc))
    except DeviceError as exc:  # the step reports, the operator fixes the sheet
        view.read_error = f"Could not read {creds.host}: {exc}"
    return view
