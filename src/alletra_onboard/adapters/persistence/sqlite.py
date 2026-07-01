from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from alletra_onboard.domain.models import ArrayWorkItem, RunEvent, RunRecord
from alletra_onboard.domain.storage import ProvisioningIntent


class SqliteRunStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL;")
            connection.execute("PRAGMA busy_timeout=5000;")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    serial_number TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_phase TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS run_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS work_items (
                    run_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS provisioning_intents (
                    run_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
            # A complete sheet uploaded but not yet turned into a run (the operator hasn't picked a
            # mode). Held server-side so device passwords never round-trip to the browser; popped when
            # the mode is chosen. Durable so an upload survives a browser refresh / server restart.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_sheets (
                    token TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

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
                (run_id, _work_item_json(item)),
            )

    def get_work_item(self, run_id: str) -> ArrayWorkItem | None:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM work_items WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        return ArrayWorkItem.model_validate(json.loads(row[0]))

    def save_provisioning_intent(self, run_id: str, intent: ProvisioningIntent) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO provisioning_intents (run_id, payload) VALUES (?, ?)
                ON CONFLICT(run_id) DO UPDATE SET payload = excluded.payload
                """,
                (run_id, _provisioning_intent_json(intent)),
            )

    def get_provisioning_intent(self, run_id: str) -> ProvisioningIntent | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM provisioning_intents WHERE run_id = ?", (run_id,)
            ).fetchone()
        if row is None:
            return None
        return ProvisioningIntent.model_validate(json.loads(row[0]))

    def save_pending_sheet(
        self, token: str, item: ArrayWorkItem, intent: ProvisioningIntent | None
    ) -> None:
        """Hold a parsed-but-not-yet-run sheet under an opaque token (secrets preserved, same as the
        work-item / intent serializers). The row lives in the gitignored state DB only."""
        payload = json.dumps(
            {
                "work_item": json.loads(_work_item_json(item)),
                "provisioning_intent": json.loads(_provisioning_intent_json(intent)) if intent else None,
            }
        )
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO pending_sheets (token, payload, created_at) VALUES (?, ?, ?)
                ON CONFLICT(token) DO UPDATE SET payload = excluded.payload, created_at = excluded.created_at
                """,
                (token, payload, datetime.now(timezone.utc).isoformat()),
            )

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
        item = ArrayWorkItem.model_validate(data["work_item"])
        intent = (
            ProvisioningIntent.model_validate(data["provisioning_intent"])
            if data.get("provisioning_intent")
            else None
        )
        return item, intent

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path, timeout=5)


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
    return json.dumps(data)
