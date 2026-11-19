"""BL-65: the state database's schema version, its secrets at rest (ADR 0027) and the expiry of
uploaded sheets nobody turned into a run."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import (
    SCHEMA_VERSION,
    SqliteRunStore,
    StateDatabaseTooNewError,
)
from alletra_onboard.api.app import create_app
from alletra_onboard.application.runs.coordinator import RunCoordinator
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.migration import MigrationIntent
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunEvent,
    RunRecord,
    WorkflowPhase,
)
from alletra_onboard.domain.ports import CREDENTIALS_UNREADABLE, StoredCredentialsUnreadableError
from alletra_onboard.domain.provisioning import DeclaredHost, ProvisioningIntent, VolumeRequest
from alletra_onboard.domain.replication import ReplicationIntent
from alletra_onboard.domain.shared import EndpointCreds
from alletra_onboard.domain.trust import DeviceKey, DevicePin, TrustKind

SECRETS = {
    "subscription": "SUBKEY-7f3a91",
    "dscc": "dscc-pw-a81",
    "array": "array-pw-b52",
    "vcenter": "vc-pw-c63",
    "f1": "f1-pw-d74",
    "f2": "f2-pw-e85",
    "host": "host-pw-f96",
    "peer": "peer-pw-0a7",
    "source": "src-pw-1b8",
}
WORKBOOK = b"PK\x03\x04 a workbook holding wb-pw-2c9"

# The schema exactly as the store created it before versions were recorded (main @ 8f89125c).
V0_SCHEMA = (
    ("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, serial_number TEXT NOT NULL, status TEXT NOT NULL,"
     " current_phase TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"),
    ("CREATE TABLE IF NOT EXISTS run_events (event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, phase TEXT NOT NULL,"
     " event_type TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)"),
    "CREATE TABLE IF NOT EXISTS work_items (run_id TEXT PRIMARY KEY, payload TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS provisioning_intents (run_id TEXT PRIMARY KEY, payload TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS pending_sheets (token TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)",
    ("CREATE TABLE IF NOT EXISTS run_artifacts (run_id TEXT NOT NULL, kind TEXT NOT NULL, payload BLOB NOT NULL,"
     " updated_at TEXT NOT NULL, PRIMARY KEY (run_id, kind))"),
    ("CREATE TABLE IF NOT EXISTS run_commands (run_id TEXT NOT NULL, seq INTEGER NOT NULL, payload TEXT NOT NULL,"
     " PRIMARY KEY (run_id, seq))"),
    ("CREATE TABLE IF NOT EXISTS run_device_pins (run_id TEXT NOT NULL, kind TEXT NOT NULL, host TEXT NOT NULL,"
     " port INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY (run_id, kind, host, port))"),
)
TABLES = {"runs", "run_events", "work_items", "provisioning_intents", "pending_sheets", "run_artifacts",
          "run_commands", "run_device_pins"}


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y", part_number="S0B84A", subscription_key=SecretStr(SECRETS["subscription"]),
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.132.30.121", mask="255.255.248.0", gateway="10.132.30.1",
                              dns=["10.203.96.10"], ntp="ntp.example.com", timezone="Asia/Kolkata"),
        dscc_setup=DsccSetupConfig(system_name="rack13arcus", country="India", password=SecretStr(SECRETS["dscc"])),
    )


def _intent() -> ProvisioningIntent:
    def creds(host: str, secret: str) -> EndpointCreds:
        return EndpointCreds(host=host, username="admin", password=SecretStr(SECRETS[secret]))

    return ProvisioningIntent(
        array=creds("10.132.30.121", "array"), vcenter=creds("vc.lab", "vcenter"),
        switch_f1=creds("10.0.0.1", "f1"), switch_f2=creds("10.0.0.2", "f2"),
        volumes=[VolumeRequest(name="vol01", size_gib=1)],
        declared_hosts=[DeclaredHost(name="rhel01", os="linux", address="10.132.30.140", username="root",
                                     password=SecretStr(SECRETS["host"])),
                        DeclaredHost(name="esx01", os="esxi")],
        replication=ReplicationIntent(peer=creds("10.132.30.122", "peer")),
        migration=MigrationIntent(source=creds("10.132.30.123", "source")),
    )


def _revealed(model) -> dict:
    """A model dump with every SecretStr in the clear, to compare what was stored with what loads."""
    def walk(value):
        if isinstance(value, SecretStr):
            return value.get_secret_value()
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        if isinstance(value, list | tuple):
            return [walk(v) for v in value]
        return value
    return walk(model.model_dump())


def _plain_json(model) -> str:
    """The row as the store wrote it before ADR 0027: every secret in clear JSON."""
    return json.dumps(_revealed(model), default=str)


def _raw(db) -> str:
    with sqlite3.connect(db) as connection:
        rows = [str(row) for table in TABLES for row in connection.execute(f"SELECT * FROM {table}")]
    return "\n".join(rows)


def _user_version(db) -> int:
    with sqlite3.connect(db) as connection:
        return connection.execute("PRAGMA user_version").fetchone()[0]


def _store(tmp_path, **kwargs) -> SqliteRunStore:
    store = SqliteRunStore(tmp_path / "state.db", **kwargs)
    store.initialize()
    return store


# ------------------------------------------------------------------ schema version


def test_a_fresh_database_is_created_at_the_current_version(tmp_path):
    _store(tmp_path)
    assert SCHEMA_VERSION == 1
    assert _user_version(tmp_path / "state.db") == SCHEMA_VERSION
    with sqlite3.connect(tmp_path / "state.db") as connection:
        names = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert TABLES <= names


def _v0_database(db, run, event, pin) -> None:
    """A state.db as the store left it before versions: user_version 0, secrets in clear JSON."""
    now = datetime.now(UTC).isoformat()
    with sqlite3.connect(db) as c:
        for statement in V0_SCHEMA:
            c.execute(statement)
        c.execute("INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)", (run.run_id, run.serial_number, run.status.value,
                  run.current_phase.value, run.model_dump_json(), run.updated_at.isoformat()))
        c.execute("INSERT INTO run_events VALUES (?, ?, ?, ?, ?, ?)", (event.event_id, run.run_id, event.phase.value,
                  event.event_type, event.model_dump_json(), event.created_at.isoformat()))
        c.execute("INSERT INTO work_items VALUES (?, ?)", (run.run_id, _plain_json(_item())))
        c.execute("INSERT INTO provisioning_intents VALUES (?, ?)", (run.run_id, _plain_json(_intent())))
        sheet = {"work_item": json.loads(_plain_json(_item())), "provisioning_intent": json.loads(_plain_json(_intent())),
                 "workbook_b64": base64.b64encode(WORKBOOK).decode("ascii")}
        c.execute("INSERT INTO pending_sheets VALUES (?, ?, ?)", ("tok", json.dumps(sheet), now))
        c.execute("INSERT INTO run_artifacts VALUES (?, ?, ?, ?)", (run.run_id, "asbuilt_docx", b"PK-docx", now))
        c.execute("INSERT INTO run_commands VALUES (?, ?, ?)", (run.run_id, 1, json.dumps({"seq": 1, "command": "showsys"})))
        c.execute("INSERT INTO run_device_pins VALUES (?, ?, ?, ?, ?)",
                  (run.run_id, pin.kind.value, pin.host, pin.port, pin.model_dump_json()))


def test_a_database_from_before_versions_opens_as_version_1_and_every_row_loads_as_before(tmp_path):
    db = tmp_path / "state.db"
    run = RunRecord(serial_number="SGHD45FF0Y")
    event = RunEvent(run_id=run.run_id, phase=WorkflowPhase.PREFLIGHT, event_type="run.created", message="m")
    pin = DevicePin(kind=TrustKind.SSH, host="10.132.30.121", port=22, device="array",
                    key=DeviceKey(kind=TrustKind.SSH, key_type="ssh-ed25519", data="AAAA", fingerprint="SHA256:x"))
    _v0_database(db, run, event, pin)
    before = _raw(db)
    assert _user_version(db) == 0

    store = _store(tmp_path)

    assert _user_version(db) == 1
    assert _raw(db) == before                                   # recognised, not rewritten
    assert store.get_run(run.run_id) == run
    assert store.list_runs() == [run]
    assert store.list_events(run.run_id) == [event]
    assert store.load_artifact(run.run_id, "asbuilt_docx") == b"PK-docx"
    assert store.list_commands(run.run_id) == [{"seq": 1, "command": "showsys"}]
    assert store.list_device_pins(run.run_id) == [pin]
    assert _revealed(store.get_work_item(run.run_id)) == _revealed(_item())
    assert _revealed(store.get_provisioning_intent(run.run_id)) == _revealed(_intent())
    assert store.pending_sheet_workbook("tok") == WORKBOOK
    item, intent = store.pop_pending_sheet("tok")
    assert _revealed(item) == _revealed(_item()) and _revealed(intent) == _revealed(_intent())
    assert not (tmp_path / "secrets.key").exists()             # reading old rows needs no key


def test_a_database_from_before_a_table_existed_gains_it(tmp_path):
    db = tmp_path / "state.db"
    with sqlite3.connect(db) as connection:
        connection.execute(V0_SCHEMA[0])
    _store(tmp_path)
    with sqlite3.connect(db) as connection:
        names = {r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert TABLES <= names and _user_version(db) == 1


def test_a_database_from_a_newer_version_is_refused_and_left_alone(tmp_path):
    db = tmp_path / "state.db"
    _store(tmp_path)
    with sqlite3.connect(db) as connection:
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
    with pytest.raises(StateDatabaseTooNewError, match="saved by a newer version of this tool"):
        SqliteRunStore(db).initialize()
    assert _user_version(db) == SCHEMA_VERSION + 1


# ------------------------------------------------------------------ secrets at rest (ADR 0027)


def test_secrets_are_encrypted_at_rest_and_the_rest_stays_readable(tmp_path):
    store = _store(tmp_path)
    store.save_work_item("r1", _item())
    store.save_provisioning_intent("r1", _intent())
    store.save_pending_sheet("tok", _item(), _intent(), WORKBOOK)

    raw = _raw(tmp_path / "state.db")
    for secret in [*SECRETS.values(), "wb-pw-2c9", base64.b64encode(WORKBOOK).decode("ascii")]:
        assert secret not in raw
    assert "SGHD45FF0Y" in raw and "10.132.30.140" in raw and "rhel01" in raw   # support can still read these
    assert '"fernet"' in raw

    assert _revealed(store.get_work_item("r1")) == _revealed(_item())
    assert _revealed(store.get_provisioning_intent("r1")) == _revealed(_intent())
    assert store.pending_sheet_workbook("tok") == WORKBOOK
    item, intent = store.pop_pending_sheet("tok")
    assert _revealed(item) == _revealed(_item()) and _revealed(intent) == _revealed(_intent())


def test_the_key_file_sits_next_to_the_database_and_only_its_owner_reads_it(tmp_path):
    store = _store(tmp_path)
    store.save_work_item("r1", _item())
    key = tmp_path / "secrets.key"
    assert key.is_file()
    if os.name == "posix":
        assert key.stat().st_mode & 0o777 == 0o600
    assert key.read_bytes().strip() not in _raw(tmp_path / "state.db").encode()


def test_an_old_plain_value_is_read_and_encrypted_on_the_next_save(tmp_path):
    store = _store(tmp_path)
    with sqlite3.connect(tmp_path / "state.db") as connection:
        connection.execute("INSERT INTO work_items VALUES (?, ?)", ("r1", _plain_json(_item())))
    item = store.get_work_item("r1")
    assert item.subscription_key.get_secret_value() == SECRETS["subscription"]
    store.save_work_item("r1", item)
    assert SECRETS["subscription"] not in _raw(tmp_path / "state.db")
    assert store.get_work_item("r1").subscription_key.get_secret_value() == SECRETS["subscription"]


@pytest.mark.parametrize("damage", ["key missing", "key of another installation"])
def test_secrets_that_cannot_be_decrypted_say_so_in_one_sentence(tmp_path, damage):
    store = _store(tmp_path)
    store.save_work_item("r1", _item())
    store.save_provisioning_intent("r1", _intent())
    store.save_pending_sheet("tok", _item(), _intent(), WORKBOOK)
    (tmp_path / "secrets.key").unlink()
    if damage == "key of another installation":
        other = SqliteRunStore(tmp_path / "other" / "state.db")
        other.initialize()
        other.save_work_item("x", _item())
        (tmp_path / "other" / "secrets.key").rename(tmp_path / "secrets.key")

    moved = SqliteRunStore(tmp_path / "state.db")
    for read in (lambda: moved.get_work_item("r1"), lambda: moved.get_provisioning_intent("r1"),
                 lambda: moved.pending_sheet_workbook("tok"), lambda: moved.pop_pending_sheet("tok")):
        with pytest.raises(StoredCredentialsUnreadableError) as caught:
            read()
        assert str(caught.value) == CREDENTIALS_UNREADABLE
    assert moved.get_run("r1") is None and moved.list_runs() == []      # what holds no secret still reads


def _unreadable_run(tmp_path) -> str:
    store = _store(tmp_path)
    coord = RunCoordinator(Settings(), store, InMemoryEventBus())
    run = coord.create_run(_item())
    (tmp_path / "secrets.key").unlink()
    return run.run_id


def test_the_api_opens_such_a_run_and_its_steps_answer_with_the_sentence(tmp_path):
    run_id = _unreadable_run(tmp_path)
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    client = TestClient(create_app(OnboardingService(Settings(), store, InMemoryEventBus())))

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["run"]["run_id"] == run_id and detail.json()["work_item"] is None

    store.save_artifact(run_id, "asbuilt_docx", b"PK-docx")
    assert client.get(f"/runs/{run_id}/asbuilt/download").status_code == 200

    store.save_pending_sheet("tok", _item(), None)
    (tmp_path / "secrets.key").unlink()
    refused = TestClient(create_app(OnboardingService(Settings(), SqliteRunStore(tmp_path / "state.db"),
                                                      InMemoryEventBus()))).post("/runs/from-sheet", json={"token": "tok"})
    assert refused.status_code == 409 and refused.json()["detail"] == CREDENTIALS_UNREADABLE


async def test_a_step_that_meets_it_records_the_sentence_alone(tmp_path):
    run_id = _unreadable_run(tmp_path)
    coord = RunCoordinator(Settings(), SqliteRunStore(tmp_path / "state.db"), InMemoryEventBus())

    async def step():
        await asyncio.to_thread(coord.get_work_item, run_id)

    coord.spawn(run_id, step())
    await coord.wait(run_id)
    assert coord.list_events(run_id)[-1].message == CREDENTIALS_UNREADABLE


# ------------------------------------------------------------------ pending sheets expire


def _age(db, token: str, hours: float) -> None:
    with sqlite3.connect(db) as connection:
        connection.execute("UPDATE pending_sheets SET created_at = ? WHERE token = ?",
                           ((datetime.now(UTC) - timedelta(hours=hours)).isoformat(), token))


def _tokens(db) -> set[str]:
    with sqlite3.connect(db) as connection:
        return {r[0] for r in connection.execute("SELECT token FROM pending_sheets")}


def test_uploaded_sheets_older_than_a_day_are_purged_on_startup_and_on_each_upload(tmp_path):
    db = tmp_path / "state.db"
    store = _store(tmp_path)
    for token in ("old", "recent"):
        store.save_pending_sheet(token, _item(), _intent(), WORKBOOK)
    _age(db, "old", 25)
    _age(db, "recent", 23)

    _store(tmp_path)                                            # startup
    assert _tokens(db) == {"recent"}

    _age(db, "recent", 24.5)
    store.save_pending_sheet("new", _item(), None)              # an upload
    assert _tokens(db) == {"new"}
    assert store.pop_pending_sheet("recent") is None
