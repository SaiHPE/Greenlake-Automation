from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunEvent,
    RunRecord,
    WorkflowPhase,
)


def _item():
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y",
        part_number="S0B84A",
        subscription_key=SecretStr("REALKEY123"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(
            mgmt_ipv4="10.64.154.225",
            mask="255.255.248.0",
            gateway="10.64.159.254",
            dns=["10.203.96.10"],
            ntp="ntp.example.com",
            timezone="Asia/Kolkata",
        ),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India", password="3pardata"),
    )


def test_artifacts_are_pruned_to_the_recent_runs(tmp_path):
    """The as-built document is large and nothing else deletes it, so retention has to be bounded."""
    from alletra_onboard.adapters.persistence.sqlite import ARTIFACT_RETENTION_RUNS

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()

    runs = []
    for index in range(ARTIFACT_RETENTION_RUNS + 5):
        run = RunRecord(serial_number=f"SGH{index:04d}")
        store.upsert_run(run)
        store.save_artifact(run.run_id, "asbuilt_docx", b"PK-payload")
        runs.append(run)

    assert store.load_artifact(runs[-1].run_id, "asbuilt_docx") == b"PK-payload"
    assert store.load_artifact(runs[0].run_id, "asbuilt_docx") is None
    # The run itself survives; only its cached artifact is dropped, so it can be re-read on demand.
    assert store.get_run(runs[0].run_id) is not None


def test_work_item_round_trip_preserves_secrets(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    store.save_work_item("run-1", _item())

    loaded = store.get_work_item("run-1")
    assert loaded is not None
    # SecretStr round-trip must NOT mask to '**********' (that's the model_dump_json default).
    assert loaded.subscription_key.get_secret_value() == "REALKEY123"
    assert loaded.dscc_setup.password is not None
    assert loaded.dscc_setup.password.get_secret_value() == "3pardata"


def test_get_work_item_missing_returns_none(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    assert store.get_work_item("nope") is None


def test_list_events_in_order(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    run = RunRecord(serial_number="SGHD45FF0Y")
    store.upsert_run(run)
    for index in range(3):
        store.append_event(
            RunEvent(
                run_id=run.run_id,
                phase=WorkflowPhase.PREFLIGHT,
                event_type="test",
                message=f"event {index}",
            )
        )
    events = store.list_events(run.run_id)
    assert [e.message for e in events] == ["event 0", "event 1", "event 2"]
    assert store.list_events("other-run") == []


def test_a_stored_run_with_a_retired_status_still_loads_as_idle(tmp_path):
    """`cancel_requested`, `cancelled` and `skipped` were removed from RunStatus; no release set them,
    but a row carrying one must not make the list of runs fail."""
    import json
    import sqlite3

    from alletra_onboard.domain.models import RunStatus

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    for status in ("cancel_requested", "cancelled", "skipped"):
        run = RunRecord(serial_number=f"SGH-{status}")
        store.upsert_run(run)
        payload = json.loads(run.model_dump_json())
        payload["status"] = status
        with sqlite3.connect(tmp_path / "state.db") as connection:
            connection.execute(
                "UPDATE runs SET status = ?, payload = ? WHERE run_id = ?",
                (status, json.dumps(payload), run.run_id),
            )
        loaded = store.get_run(run.run_id)
        assert loaded is not None and loaded.status is RunStatus.READY

    assert {r.status for r in store.list_runs()} == {RunStatus.READY}
