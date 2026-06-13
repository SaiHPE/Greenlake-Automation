from fastapi.testclient import TestClient
from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.event_bus import InMemoryEventBus
from alletra_onboard.application.intake import csv_template
from alletra_onboard.application.onboarding_service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig


def _client(tmp_path) -> TestClient:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    return TestClient(create_app(service))


def _work_item_payload() -> dict:
    item = ArrayWorkItem(
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
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )
    payload = item.model_dump(mode="json")
    payload["subscription_key"] = "REALKEY123"  # model_dump masks; the client sends the real key
    return payload


def test_health(tmp_path):
    assert _client(tmp_path).get("/health").json() == {"status": "ok"}


def test_create_get_and_list_runs_masks_secret(tmp_path):
    client = _client(tmp_path)
    created = client.post("/runs", json={"work_item": _work_item_payload()})
    assert created.status_code == 200
    run_id = created.json()["run"]["run_id"]

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["run"]["serial_number"] == "SGHD45FF0Y"
    # the API must never echo the subscription key
    assert "REALKEY123" not in detail.text

    assert any(r["run_id"] == run_id for r in client.get("/runs").json()["runs"])
    events = client.get(f"/runs/{run_id}/events").json()["events"]
    assert events and events[0]["event_type"] == "run.created"


def test_run_not_found_is_404(tmp_path):
    client = _client(tmp_path)
    assert client.get("/runs/nope").status_code == 404
    assert client.post("/runs/nope/provision", json={}).status_code == 404


def test_mark_complete(tmp_path):
    client = _client(tmp_path)
    run_id = client.post("/runs", json={"work_item": _work_item_payload()}).json()["run"]["run_id"]
    done = client.post(f"/runs/{run_id}/complete")
    assert done.json()["run"]["status"] == "succeeded"


def test_template_and_parse_round_trip(tmp_path):
    client = _client(tmp_path)
    template = client.get("/work-items/template")
    assert template.status_code == 200
    assert template.text == csv_template()

    parsed = client.post("/work-items/parse", json={"csv_text": template.text})
    assert parsed.status_code == 200
    items = parsed.json()["work_items"]
    assert len(items) == 1 and items[0]["serial_number"] == "SGHD00EXAMPLE"

    bad = client.post("/work-items/parse", json={"csv_text": "not,a,real\nheader,row,x"})
    assert bad.status_code == 422


def test_config_roundtrip_masks_secret(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the API writes .env in the working directory
    client = _client(tmp_path)
    saved = client.post(
        "/config",
        json={"gl_client_id": "abc", "gl_client_secret": "supersecret", "gl_token_url": "https://t"},
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["configured"] is True
    assert body["values"]["GL_CLIENT_ID"] == "abc"
    assert body["values"]["GL_CLIENT_SECRET"] == "****"
    assert "supersecret" not in saved.text
