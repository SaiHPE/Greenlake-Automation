from __future__ import annotations

import base64
import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from alletra_onboard.adapters.persistence.secrets import KEY_FILE_NAME, SecretBox
from alletra_onboard.domain.models import ArrayWorkItem, RunEvent, RunRecord
from alletra_onboard.domain.provisioning import ProvisioningIntent
from alletra_onboard.domain.trust import DevicePin

# How many runs keep their step artifacts. Runs stay in the database; only their cached artifacts
# are pruned, so an old run reopened after this can simply re-run discovery.
ARTIFACT_RETENTION_RUNS = 20

# An uploaded sheet nobody turned into a run holds every password of the sheet; it does not wait forever.
PENDING_SHEET_TTL = timedelta(hours=24)

# The schema, one entry per version, in order: entry N brings a database from version N-1 to N and is
# recorded in `PRAGMA user_version`. Never edit an entry that has shipped; add the next one.
# Version 1 is the schema as it stood before versions were recorded, so every statement is
# IF NOT EXISTS: a database from then (user_version 0) becomes version 1 without any other change.
MIGRATIONS: tuple[tuple[str, ...], ...] = (
    (
        """
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            serial_number TEXT NOT NULL,
            status TEXT NOT NULL,
            current_phase TEXT NOT NULL,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS run_events (
            event_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            phase TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS work_items (
            run_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS provisioning_intents (
            run_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """,
        # A complete sheet uploaded but not yet turned into a run (the operator hasn't picked a mode).
        # Held server-side so device passwords never round-trip to the browser; popped when the mode
        # is chosen, purged after PENDING_SHEET_TTL. Durable so an upload survives a server restart.
        """
        CREATE TABLE IF NOT EXISTS pending_sheets (
            token TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """,
        # Step artifacts (discovery report / provisioning-plan marker / as-built docx), durable so a
        # server restart mid-engagement doesn't force re-running discovery (ADR 0011, C7). No secrets:
        # these are read results, not credentials.
        """
        CREATE TABLE IF NOT EXISTS run_artifacts (
            run_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            payload BLOB NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (run_id, kind)
        )
        """,
        # SPEC-019: every command a client sent for a run, in order, with its (capped, redacted) output.
        """
        CREATE TABLE IF NOT EXISTS run_commands (
            run_id TEXT NOT NULL,
            seq INTEGER NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (run_id, seq)
        )
        """,
        # ADR 0026: the SSH host key or TLS certificate each on-site device presented on the run's
        # first contact. Kept with the run, like its credentials (ADR 0013); a new run starts empty.
        # A table of its own, not the run record: steps write back whole stale RunRecords.
        """
        CREATE TABLE IF NOT EXISTS run_device_pins (
            run_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (run_id, kind, host, port)
        )
        """,
    ),
)
SCHEMA_VERSION = len(MIGRATIONS)

# Where the secrets sit in a stored payload ("*" = every row of a list). Only these are encrypted
# (ADR 0027); the rest stays readable.
_WORK_ITEM_SECRETS = (("subscription_key",), ("dscc_setup", "password"))
_INTENT_SECRETS = (
    ("array", "password"),
    ("vcenter", "password"),
    ("switch_f1", "password"),
    ("switch_f2", "password"),
    ("declared_hosts", "*", "password"),
    ("replication", "peer", "password"),
    ("migration", "source", "password"),
)


class StateDatabaseTooNewError(RuntimeError):
    def __init__(self, path: Path, found: int, known: int) -> None:
        super().__init__(
            f"The run history in {path} was saved by a newer version of this tool (format {found}; "
            f"this version reads up to format {known}). Start the newer version, or move that file "
            "aside to start with an empty run history."
        )


class SqliteRunStore:
    def __init__(self, database_path: Path, key_path: Path | None = None) -> None:
        self.database_path = database_path
        # The key lives with the database it protects (ADR 0027), never inside it.
        self.secrets = SecretBox(key_path or database_path.parent / KEY_FILE_NAME)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path, timeout=5, isolation_level=None)) as connection:
            connection.execute("PRAGMA journal_mode=WAL;")
            connection.execute("PRAGMA busy_timeout=5000;")
            _migrate(connection, self.database_path)
        with self._connect() as connection:
            _purge_expired_pending_sheets(connection)

    def upsert_run(self, run: RunRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (run_id, serial_number, status, current_phase, payload, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = excluded.status,
                    current_phase = excluded.current_phase,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    run.run_id,
                    run.serial_number,
                    run.status.value,
                    run.current_phase.value,
                    run.model_dump_json(),
                    run.updated_at.isoformat(),
                ),
            )

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return RunRecord.model_validate(json.loads(row[0]))

    def list_runs(self) -> list[RunRecord]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload FROM runs ORDER BY updated_at DESC").fetchall()
        return [RunRecord.model_validate(json.loads(row[0])) for row in rows]

    def append_event(self, event: RunEvent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO run_events (event_id, run_id, phase, event_type, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.run_id,
                    event.phase.value,
                    event.event_type,
                    event.model_dump_json(),
                    event.created_at.isoformat(),
                ),
            )

    def list_events(self, run_id: str) -> list[RunEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM run_events WHERE run_id = ? ORDER BY created_at ASC",
                (run_id,),
            ).fetchall()
        return [RunEvent.model_validate(json.loads(row[0])) for row in rows]

    def save_work_item(self, run_id: str, item: ArrayWorkItem) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO work_items (run_id, payload) VALUES (?, ?)
                ON CONFLICT(run_id) DO UPDATE SET payload = excluded.payload
                """,
                (run_id, json.dumps(self._sealed(json.loads(_work_item_json(item)), _WORK_ITEM_SECRETS))),
            )

    def get_work_item(self, run_id: str) -> ArrayWorkItem | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM work_items WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return self._work_item(json.loads(row[0]))

    def save_provisioning_intent(self, run_id: str, intent: ProvisioningIntent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO provisioning_intents (run_id, payload) VALUES (?, ?)
                ON CONFLICT(run_id) DO UPDATE SET payload = excluded.payload
                """,
                (run_id, json.dumps(self._sealed(json.loads(_provisioning_intent_json(intent)), _INTENT_SECRETS))),
            )

    def get_provisioning_intent(self, run_id: str) -> ProvisioningIntent | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM provisioning_intents WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return self._intent(json.loads(row[0]))

    def save_pending_sheet(
        self, token: str, item: ArrayWorkItem, intent: ProvisioningIntent | None, workbook: bytes | None = None
    ) -> None:
        """Hold a parsed-but-not-yet-run sheet under an opaque token (secrets preserved and encrypted, as
        for a run). The row lives in the gitignored state DB only, for at most PENDING_SHEET_TTL.
        `workbook`: the uploaded file, kept only when the upload listed problems, to check it again for
        the chosen steps; it holds every password of the sheet, so it is encrypted whole."""
        data: dict[str, Any] = {
            "work_item": self._sealed(json.loads(_work_item_json(item)), _WORK_ITEM_SECRETS),
            "provisioning_intent": (
                self._sealed(json.loads(_provisioning_intent_json(intent)), _INTENT_SECRETS) if intent else None
            ),
        }
        if workbook is not None:
            data["workbook_b64"] = self.secrets.seal(base64.b64encode(workbook).decode("ascii"))
        payload = json.dumps(data)
        with self._connect() as connection:
            _purge_expired_pending_sheets(connection)
            connection.execute(
                """
                INSERT INTO pending_sheets (token, payload, created_at) VALUES (?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET payload = excluded.payload, created_at = excluded.created_at
                """,
                (token, payload, datetime.now(UTC).isoformat()),
            )

    def pending_sheet_workbook(self, token: str) -> bytes | None:
        """The uploaded file held with a pending sheet, without using the hold up; None when none was kept."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM pending_sheets WHERE token = ?", (token,)
            ).fetchone()
        workbook = self.secrets.open(json.loads(row[0]).get("workbook_b64")) if row else None
        return base64.b64decode(workbook) if workbook else None

    def pop_pending_sheet(
        self, token: str
    ) -> tuple[ArrayWorkItem, ProvisioningIntent | None] | None:
        """Fetch AND delete a pending sheet (single-use — one upload mints one run)."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM pending_sheets WHERE token = ?", (token,)
            ).fetchone()
            if row is None:
                return None
            connection.execute("DELETE FROM pending_sheets WHERE token = ?", (token,))
        data = json.loads(row[0])
        item = self._work_item(data["work_item"])
        intent = self._intent(data["provisioning_intent"]) if data.get("provisioning_intent") else None
        return item, intent

    def save_artifact(self, run_id: str, kind: str, payload: bytes) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO run_artifacts (run_id, kind, payload, updated_at) VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id, kind) DO UPDATE SET
                    payload = excluded.payload, updated_at = excluded.updated_at
                """,
                (run_id, kind, payload, datetime.now(UTC).isoformat()),
            )
            # Artifacts include the generated as-built document, hundreds of KB per run, and nothing
            # else ever deletes them. Keep the recent runs — enough to resume anything in flight —
            # and drop the rest, so a long-lived workstation's state file cannot grow without bound.
            # An in-flight apply record stays until recovered or closed (STANDARD S5).
            connection.execute(
                """
                DELETE FROM run_artifacts
                 WHERE kind != 'apply_in_progress'
                   AND run_id NOT IN (SELECT run_id FROM runs ORDER BY updated_at DESC LIMIT ?)
                """,
                (ARTIFACT_RETENTION_RUNS,),
            )

    def load_artifact(self, run_id: str, kind: str) -> bytes | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM run_artifacts WHERE run_id = ? AND kind = ?", (run_id, kind)
            ).fetchone()
        return None if row is None else bytes(row[0])

    def append_command(self, run_id: str, entry: dict) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COALESCE(MAX(seq), 0) FROM run_commands WHERE run_id = ?", (run_id,)).fetchone()
            seq = int(row[0]) + 1
            connection.execute("INSERT INTO run_commands (run_id, seq, payload) VALUES (?, ?, ?)",
                               (run_id, seq, json.dumps(dict(entry, seq=seq))))
            if seq == 1:
                # same retention as the artifacts: outputs are up to 64 KB each
                connection.execute(
                    "DELETE FROM run_commands WHERE run_id != ? AND run_id NOT IN "
                    "(SELECT run_id FROM runs ORDER BY updated_at DESC LIMIT ?)",
                    (run_id, ARTIFACT_RETENTION_RUNS),
                )
        return seq

    def list_commands(self, run_id: str, since: int = 0) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM run_commands WHERE run_id = ? AND seq > ? ORDER BY seq", (run_id, since)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def get_device_pin(self, run_id: str, kind: str, host: str, port: int) -> DevicePin | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM run_device_pins WHERE run_id = ? AND kind = ? AND host = ? AND port = ?",
                (run_id, str(kind), host, port),
            ).fetchone()
        return None if row is None else DevicePin.model_validate_json(row[0])

    def list_device_pins(self, run_id: str) -> list[DevicePin]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM run_device_pins WHERE run_id = ? ORDER BY host, port, kind", (run_id,)
            ).fetchall()
        return [DevicePin.model_validate_json(r[0]) for r in rows]

    def add_device_pin(self, run_id: str, pin: DevicePin) -> DevicePin:
        """Record a first contact unless the device already has a pin, and return the pin that holds:
        two reads reaching the same device at once must not each trust what they saw."""
        with self._connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO run_device_pins (run_id, kind, host, port, payload) VALUES (?, ?, ?, ?, ?)",
                (run_id, str(pin.kind), pin.host, pin.port, pin.model_dump_json()),
            )
            row = connection.execute(
                "SELECT payload FROM run_device_pins WHERE run_id = ? AND kind = ? AND host = ? AND port = ?",
                (run_id, str(pin.kind), pin.host, pin.port),
            ).fetchone()
        return DevicePin.model_validate_json(row[0])

    def save_device_pin(self, run_id: str, pin: DevicePin) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO run_device_pins (run_id, kind, host, port, payload) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(run_id, kind, host, port) DO UPDATE SET payload = excluded.payload
                """,
                (run_id, str(pin.kind), pin.host, pin.port, pin.model_dump_json()),
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path, timeout=5)

    def _sealed(self, data: dict, paths: tuple[tuple[str, ...], ...]) -> dict:
        for path in paths:
            _map_at(data, path, lambda value: self.secrets.seal(value) if isinstance(value, str) else value)
        return data

    def _opened(self, data: dict, paths: tuple[tuple[str, ...], ...]) -> dict:
        for path in paths:
            _map_at(data, path, self.secrets.open)
        return data

    def _work_item(self, data: dict) -> ArrayWorkItem:
        return ArrayWorkItem.model_validate(self._opened(data, _WORK_ITEM_SECRETS))

    def _intent(self, data: dict) -> ProvisioningIntent:
        return ProvisioningIntent.model_validate(self._opened(data, _INTENT_SECRETS))


def _migrate(connection: sqlite3.Connection, path: Path) -> None:
    """Bring the database to SCHEMA_VERSION in one transaction; refuse one written by a newer version."""
    found = connection.execute("PRAGMA user_version").fetchone()[0]
    if found > SCHEMA_VERSION:
        raise StateDatabaseTooNewError(path, found, SCHEMA_VERSION)
    if found == SCHEMA_VERSION:
        return
    connection.execute("BEGIN IMMEDIATE")
    try:
        found = connection.execute("PRAGMA user_version").fetchone()[0]  # another process may have won
        if found > SCHEMA_VERSION:
            raise StateDatabaseTooNewError(path, found, SCHEMA_VERSION)
        for statements in MIGRATIONS[found:]:
            for statement in statements:
                connection.execute(statement)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        connection.execute("COMMIT")
    except BaseException:
        connection.execute("ROLLBACK")
        raise


def _purge_expired_pending_sheets(connection: sqlite3.Connection) -> None:
    cutoff = datetime.now(UTC) - PENDING_SHEET_TTL
    expired = []
    for token, created_at in connection.execute("SELECT token, created_at FROM pending_sheets"):
        try:
            created = datetime.fromisoformat(created_at)
        except (TypeError, ValueError):
            created = None
        if created is None or created.tzinfo is None or created < cutoff:
            expired.append((token,))
    connection.executemany("DELETE FROM pending_sheets WHERE token = ?", expired)


def _map_at(data: Any, path: tuple[str, ...], change) -> None:
    """Replace the value at `path` in a JSON tree with change(value), when the path is there."""
    head, rest = path[0], path[1:]
    children: list[tuple[Any, Any]]
    if head == "*":
        children = list(enumerate(data)) if isinstance(data, list) else []
    else:
        children = [(head, data[head])] if isinstance(data, dict) and head in data else []
    for key, child in children:
        if rest:
            _map_at(child, rest, change)
        else:
            data[key] = change(child)


def _work_item_json(item: ArrayWorkItem) -> str:
    """Serialize a work item PRESERVING secrets (model_dump_json masks SecretStr to '********',
    which would corrupt the round-trip). The DB lives in the gitignored .alletra_onboard dir."""
    data = item.model_dump(mode="json")
    data["subscription_key"] = item.subscription_key.get_secret_value()
    if item.dscc_setup.password is not None:
        data["dscc_setup"]["password"] = item.dscc_setup.password.get_secret_value()
    return json.dumps(data)


def _provisioning_intent_json(intent: ProvisioningIntent) -> str:
    """Serialize a provisioning intent PRESERVING the device passwords (same masking caveat as the
    work item — the customer-supplied creds must round-trip for the WSAPI/SSH/vCenter clients)."""
    data = intent.model_dump(mode="json")
    for endpoint in ("array", "vcenter", "switch_f1", "switch_f2"):
        data[endpoint]["password"] = getattr(intent, endpoint).password.get_secret_value()
    for row, host in zip(data.get("declared_hosts", []), intent.declared_hosts):
        row["password"] = host.password.get_secret_value() if host.password is not None else None
    if intent.replication is not None:
        data["replication"]["peer"]["password"] = intent.replication.peer.password.get_secret_value()
    if intent.migration is not None:
        data["migration"]["source"]["password"] = intent.migration.source.password.get_secret_value()
    return json.dumps(data)
