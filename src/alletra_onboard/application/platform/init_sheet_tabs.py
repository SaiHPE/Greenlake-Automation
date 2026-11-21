"""Pure dict-to-domain parsers for the three optional step-workflow tabs of ``Initialisation_sheet.xlsx``:
Replication (SPEC-015), Snapshots (SPEC-023), and Migration (SPEC-027).

These three tabs share the word/number/yes-no parsing rules and hold no openpyxl I/O; ``init_sheet.py``
keeps the workbook layout, schema constants, Provisioning tab, and array-port tabs. ``parse_replication_tab``
receives ``read_network`` as a lazy callback so Replication tab errors still fire before Replication
network errors.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Literal

from pydantic import SecretStr

from alletra_onboard.domain.migration import (
    MIGRATION_PROVISIONING,
    MIGRATION_TYPES,
    MigrationHostRequest,
    MigrationIntent,
    MigrationProvisioning,
    MigrationType,
    Orchestration,
)
from alletra_onboard.domain.replication import (
    RPO_MINUTES_DEFAULT,
    RPO_MINUTES_MIN,
    ProtectionRequest,
    RcipPortRequest,
    ReplicationIntent,
    ReplicationMode,
    rtt_limit_ms,
    rtt_limit_text,
)
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.snapshots import (
    ALLOWED_EVERY,
    HOURS_MAX,
    SCHEDULE_NAME_MAX,
    SnapshotIntent,
    SnapshotRequest,
    SnapshotUnit,
)

_UNSUPPORTED_REPLICATION_TYPES = ("peer persistence", "active sync", "sld", "3dc", "streaming", "app")
_REPLICATION_MODE_WORDS: dict[str, ReplicationMode] = {
    "async": "async",
    "periodic": "async",
    "asynchronous": "async",
    "asynchronous periodic": "async",
    "sync": "sync",
    "synchronous": "sync",
}

# What an operator may type for each list value; the key is the normalised text (lower case, single
# spaces, '-' and '_' read as spaces).
_MIGRATION_TYPE_WORDS: dict[str, MigrationType] = {
    "online": "online",
    "minimally disruptive": "minimally disruptive",
    "mdm": "minimally disruptive",
    "offline": "offline",
}
_MIGRATION_PROVISIONING_WORDS: dict[str, MigrationProvisioning] = {
    "thin": "thin",
    "tpvv": "thin",
    "reduce": "reduce",
}
_ORCHESTRATION_WORDS: dict[str, Orchestration] = {
    "array ui": "array UI",
    "array": "array UI",
    "dscc": "DSCC",
}

_DAY_NUMBERS = {
    name: number
    for number, full in enumerate(("sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"))
    for name in (full, full[:3])
}
_SNAPSHOT_KINDS: dict[str, Literal["set", "volume"]] = {"set": "set", "volume": "volume"}
_UNITS: dict[str, SnapshotUnit] = {
    "minute": "minutes",
    "minutes": "minutes",
    "hour": "hours",
    "hours": "hours",
    "day": "days",
    "days": "days",
}
_SCHEDULE_NAME = re.compile(rf"[A-Za-z0-9._-]{{1,{SCHEDULE_NAME_MAX}}}")
#: `help createsched` / `help removesched`: names the array keeps for itself.
_RESERVED_SCHEDULE_NAMES = ("all", "upgrade")


def _yes_no(text: str | None, *, default: bool, where: str) -> bool:
    value = (text or "").strip().lower()
    if not value:
        return default
    if value in ("yes", "y", "true", "1"):
        return True
    if value in ("no", "n", "false", "0"):
        return False
    raise ValueError(f"{where} must be 'yes' or 'no' (got '{text}').")


def _whole(text: str) -> int | None:
    """A whole number as typed or as Excel stores it ('24', 24.0); None for anything else."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return int(value) if value.is_integer() else None


def _list_word(text: str) -> str:
    return " ".join(text.strip().lower().replace("-", " ").replace("_", " ").split())


def _one_of(values: tuple[str, ...]) -> str:
    return ", ".join(values[:-1]) + " or " + values[-1]


# ------------------------------------------------------------------ Replication tab (SPEC-015)


def _parse_rtt_ms(raw_rtt: str | None) -> float | None:
    if not raw_rtt:
        return None
    try:
        rtt = float(raw_rtt)
    except ValueError as exc:
        raise ValueError(
            f"Replication tab — 'Measured round-trip time (ms)' must be a number (got '{raw_rtt}')."
        ) from exc
    if rtt < 0:
        raise ValueError("Replication tab — 'Measured round-trip time (ms)' cannot be negative.")
    return rtt


def _parse_replication_mode(raw_mode: str | None, where: str) -> ReplicationMode:
    mode_text = (raw_mode or "async").strip().lower()
    mode = _REPLICATION_MODE_WORDS.get(mode_text)
    if mode is None:
        unsupported = any(t in mode_text for t in _UNSUPPORTED_REPLICATION_TYPES)
        raise ValueError(
            f"{where}: Mode must be 'async' or 'sync' (got '{raw_mode}')"
            + ("; Peer Persistence, Active Sync, SLD and 3DC are not supported in this version." if unsupported else ".")
        )
    return mode


def _parse_rpo_minutes(raw_rpo: str | None, where: str) -> int:
    raw = (raw_rpo or "").strip()
    if not raw:
        return RPO_MINUTES_DEFAULT
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            f"{where}: RPO must be a whole number of minutes, {RPO_MINUTES_MIN} or more (got '{raw}')."
        ) from exc
    if not value.is_integer() or value < RPO_MINUTES_MIN:
        raise ValueError(f"{where}: RPO must be a whole number of minutes, {RPO_MINUTES_MIN} or more (got '{raw}').")
    return int(value)


def _parse_protection_row(row: dict[str, str], *, rtt: float | None, where: str) -> ProtectionRequest:
    mode = _parse_replication_mode(row.get("mode"), where)
    rpo = _parse_rpo_minutes(row.get("rpo_minutes"), where) if mode == "async" else None
    # SPEC-020: a blank RTT is fine here — the Replication step measures it (checkrclink), or over Fibre
    # Channel asks for it (SPEC-031 R6). The sheet does not know the transport yet: it refuses only what RCIP,
    # the looser limit, refuses, and the step holds a Fibre Channel pair to its own.
    if rtt is not None and rtt > rtt_limit_ms("IP", mode):
        raise ValueError(
            f"{where}: the measured round-trip time is {rtt:g} ms; {rtt_limit_text('IP', mode)} "
            "(HPE Support Matrix)."
        )
    peer_cpg = (row.get("peer_cpg") or "").strip()
    if not peer_cpg:
        raise ValueError(f"{where}: Peer CPG is required (the CPG on the peer array for the secondary volumes).")
    return ProtectionRequest(
        vvset=row["vvset"],
        mode=mode,
        rpo_minutes=rpo,
        peer_cpg=peer_cpg,
        peer_vvset=(row.get("peer_vvset") or "").strip(),
        auto_synchronize=_yes_no(row.get("auto_synchronize"), default=True, where=f"{where}: Auto synchronize"),
        auto_recover=_yes_no(row.get("auto_recover"), default=True, where=f"{where}: Auto recover"),
    )


def parse_replication_tab(
    fields: dict[str, str],
    rows: list[dict[str, str]],
    *,
    required_fields: Sequence[tuple[str, str]],
    read_network: Callable[[], list[RcipPortRequest]],
) -> ReplicationIntent | None:
    """Validate and build a ``ReplicationIntent`` from the Replication tab's key/value fields and
    Protection rows (SPEC-015 R1/R2). Returns ``None`` when the tab is blank."""
    if not any(fields.get(key) for key, _ in required_fields) and not rows:
        return None
    missing = [label for key, label in required_fields if not fields.get(key)]
    if missing:
        raise ValueError("Replication tab — missing required fields: " + ", ".join(sorted(missing)))
    if not rows:
        raise ValueError("Replication tab — add at least one volume set to protect (a Volume set and a Peer CPG).")

    rtt = _parse_rtt_ms(fields.get("rtt_ms"))
    # A set not on the Volumes tab is an EXISTING set: the Replication preview reads the array and
    # refuses it there if it is missing or empty (plan.check).
    protections: list[ProtectionRequest] = []
    seen: set[str] = set()
    for row in rows:
        vvset = row["vvset"]
        where = f"Replication tab — row '{vvset}'"
        if vvset in seen:
            raise ValueError(f"{where} appears twice; one row per volume set.")
        seen.add(vvset)
        protections.append(_parse_protection_row(row, rtt=rtt, where=where))

    # Called lazily here so Replication tab errors surface before Replication network errors.
    network = read_network()
    return ReplicationIntent(
        peer=EndpointCreds(
            host=fields["peer_host"],
            username=fields["peer_user"],
            password=SecretStr(fields["peer_password"]),
        ),
        rtt_ms=rtt,
        protections=protections,
        failover_test=_yes_no(
            fields.get("failover_test"), default=True, where="Replication tab — 'Run the failover test'",
        ),
        failover_group=(fields.get("failover_group") or "").strip(),
        network=network,
    )


# ------------------------------------------------------------------ Snapshots tab (SPEC-023)


def _parse_snapshot_period(
    every_text: str, unit_text: str, *, snapshot_now: bool, where: str,
) -> tuple[int | None, SnapshotUnit | None]:
    if not snapshot_now and not every_text and not unit_text:
        raise ValueError(f"{where} asks for nothing: set Snapshot now to yes, or fill Every and Unit.")
    if bool(every_text) != bool(unit_text):
        raise ValueError(f"{where}: Every and Unit go together; fill both or neither.")
    if not every_text:
        return None, None
    every, unit = _whole(every_text), _UNITS.get(unit_text.lower())
    if every is None or unit is None or every not in ALLOWED_EVERY[unit]:
        raise ValueError(
            f"{where}: every {every if every is not None else every_text} {unit_text} is not a period the "
            "array schedules; use 15, 20 or 30 minutes, 1, 2, 3, 4, 6, 8 or 12 hours, or 1 day."
        )
    return every, unit


def _parse_snapshot_start_hour(raw_hour: str | None, unit: SnapshotUnit | None, where: str) -> int:
    hour_text = (raw_hour or "").strip()
    if unit == "minutes" and hour_text:
        raise ValueError(f"{where}: Start hour applies to hours and days; leave it blank for a schedule in minutes.")
    if not hour_text or unit is None:
        return 0
    parsed_hour = _whole(hour_text)
    if parsed_hour is None or not 0 <= parsed_hour <= 23:
        raise ValueError(f"{where}: Start hour must be a whole number from 0 to 23 (got '{hour_text}').")
    return parsed_hour


def _parse_snapshot_days(raw_days: str | None, unit: SnapshotUnit | None, where: str) -> list[int]:
    days_text = (raw_days or "").strip()
    if days_text and unit is None:
        raise ValueError(f"{where}: Days applies to a schedule; fill Every and Unit, or leave Days blank.")
    days: set[int] = set()
    for item in (d.strip().lower() for d in days_text.split(",")):
        if not item:
            continue
        if item not in _DAY_NUMBERS:
            raise ValueError(
                f"{where}: Days must be day names separated by commas, such as mon, tue (got '{days_text}')."
            )
        days.add(_DAY_NUMBERS[item])
    return sorted(days)


def _parse_snapshot_retention(raw_expire: str | None, raw_retain: str | None, where: str) -> tuple[int, int | None]:
    expire = _whole((raw_expire or "").strip())
    if expire is None or not 1 <= expire <= HOURS_MAX:
        raise ValueError(f"{where}: Keep for must be a whole number of hours from 1 to {HOURS_MAX}.")
    retain_text = (raw_retain or "").strip()
    if not retain_text:
        return expire, None
    retain = _whole(retain_text)
    if retain is None or not 1 <= retain <= HOURS_MAX:
        raise ValueError(f"{where}: Lock for must be a whole number of hours from 1 to {HOURS_MAX}, or blank.")
    if retain > expire:
        raise ValueError(f"{where}: Lock for cannot be longer than Keep for; the array refuses it.")
    return expire, retain


def _parse_snapshot_schedule_name(raw_name: str | None, where: str) -> str:
    schedule_name = (raw_name or "").strip()
    if schedule_name and not _SCHEDULE_NAME.fullmatch(schedule_name):
        raise ValueError(
            f"{where}: Schedule name may use letters, digits, '.', '_' and '-' only, up to {SCHEDULE_NAME_MAX} characters."
        )
    if schedule_name.startswith("-"):
        raise ValueError(f"{where}: Schedule name cannot start with '-'; the array would read it as an option.")
    if schedule_name.lower() in _RESERVED_SCHEDULE_NAMES:
        raise ValueError(f"{where}: Schedule name '{schedule_name}' is kept by the array for itself; choose another.")
    return schedule_name


def _parse_snapshot_row(row: dict[str, str], where: str) -> SnapshotRequest:
    kind = _SNAPSHOT_KINDS.get((row.get("kind") or "set").strip().lower())
    if kind is None:
        raise ValueError(f"{where}: Kind must be 'set' or 'volume' (got '{row.get('kind')}').")
    every_text, unit_text = (row.get("every") or "").strip(), (row.get("unit") or "").strip()
    snapshot_now = _yes_no(row.get("snapshot_now"), default=False, where=f"{where}: Snapshot now")
    every, unit = _parse_snapshot_period(every_text, unit_text, snapshot_now=snapshot_now, where=where)
    at_hour = _parse_snapshot_start_hour(row.get("at_hour"), unit, where)
    days = _parse_snapshot_days(row.get("days"), unit, where)
    expire, retain = _parse_snapshot_retention(row.get("expire_hours"), row.get("retain_hours"), where)
    schedule_name = _parse_snapshot_schedule_name(row.get("schedule_name"), where)
    read_only = _yes_no(row.get("read_only"), default=True, where=f"{where}: Read-only")
    return SnapshotRequest(
        source=row["source"],
        kind=kind,
        snapshot_now=snapshot_now,
        every=every,
        unit=unit,
        at_hour=at_hour,
        days=days,
        expire_hours=expire,
        retain_hours=retain,
        read_only=read_only,
        schedule_name=schedule_name,
    )


def parse_snapshots_rows(rows: list[dict[str, str]]) -> SnapshotIntent:
    """Validate and build a ``SnapshotIntent`` from the Snapshots tab's rows (SPEC-023 R1/R2).
    Each row is checked in R2's order and the first rule it breaks is raised, one sentence each."""
    requests: list[SnapshotRequest] = []
    seen: set[str] = set()
    names: set[str] = set()
    for row in rows:
        source = row["source"]
        where = f"Snapshots tab — row '{source}'"
        if source in seen:
            raise ValueError(f"{where} appears twice; one row per volume set or volume.")
        seen.add(source)
        request = _parse_snapshot_row(row, where)
        if request.has_schedule:
            if request.name in names:
                raise ValueError(f"{where}: schedule name '{request.name}' is used by two rows.")
            names.add(request.name)
        requests.append(request)
    return SnapshotIntent(requests=requests)


# ------------------------------------------------------------------ Migration tab (SPEC-027)


def _parse_migration_source(fields: dict[str, str]) -> EndpointCreds:
    if not fields.get("source_host", "").strip():
        raise ValueError("Migration tab — enter the source array's management address (the array the data moves from).")
    if not fields.get("source_user", "").strip():
        raise ValueError("Migration tab — enter a user for the source array; a read-only account is enough.")
    if not fields.get("source_password"):
        raise ValueError("Migration tab — enter the password of the source array's user.")
    return EndpointCreds(
        host=fields["source_host"].strip(),
        username=fields["source_user"].strip(),
        password=SecretStr(fields["source_password"]),
    )


def _parse_migration_host_row(row: dict[str, str], where: str) -> MigrationHostRequest:
    kind = _MIGRATION_TYPE_WORDS.get(_list_word(row.get("type") or "online"))
    if kind is None:
        raise ValueError(f"{where}: Migration type must be {_one_of(MIGRATION_TYPES)} (got '{row['type']}').")
    provisioning = _MIGRATION_PROVISIONING_WORDS.get(_list_word(row.get("provisioning") or "thin"))
    if provisioning is None:
        raise ValueError(
            f"{where}: Provisioning must be {_one_of(MIGRATION_PROVISIONING)} (got '{row['provisioning']}')."
        )
    cpg = (row.get("cpg") or "").strip()
    if not cpg:
        raise ValueError(f"{where}: enter the destination CPG, the CPG on this array that receives its volumes.")
    return MigrationHostRequest(host=row["host"], type=kind, cpg=cpg, provisioning=provisioning)


def parse_migration_tab(fields: dict[str, str], rows: list[dict[str, str]]) -> MigrationIntent | None:
    """Validate and build a ``MigrationIntent`` from the Migration tab's fields and host rows
    (SPEC-027 R1). Returns ``None`` when the tab is blank."""
    if not fields and not rows:
        return None
    source = _parse_migration_source(fields)
    orchestration = _ORCHESTRATION_WORDS.get(_list_word(fields.get("orchestration") or "array UI"))
    if orchestration is None:
        raise ValueError(
            f"Migration tab — 'Where the import runs' must be 'array UI' or 'DSCC' (got '{fields['orchestration']}')."
        )
    if not rows:
        raise ValueError(
            "Migration tab — add at least one host to migrate: its name on the source array and a destination CPG."
        )
    hosts: list[MigrationHostRequest] = []
    seen: set[str] = set()
    for row in rows:
        name = row["host"]
        where = f"Migration tab — host '{name}'"
        if name in seen:
            raise ValueError(f"{where} appears twice; one row per host.")
        seen.add(name)
        hosts.append(_parse_migration_host_row(row, where))
    return MigrationIntent(source=source, orchestration=orchestration, hosts=hosts)
