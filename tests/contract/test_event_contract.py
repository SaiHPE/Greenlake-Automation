"""Contract tests for the run-event registry and its OpenAPI schema (STANDARD T4)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.events import EVENT_TYPES, NoData, _event
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunEvent,
    WorkflowPhase,
)


def _service(tmp_path) -> OnboardingService:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    return OnboardingService(Settings(), store, InMemoryEventBus())


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y", part_number="S0B84A", subscription_key="KEY123",
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.0.0.5", mask="255.255.255.0", gateway="10.0.0.1",
                              dns=["10.0.0.2"], ntp="ntp.example.com", timezone="UTC"),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )


def test_schema_names_every_event_type(tmp_path):
    """The OpenAPI schema for /runs/{id}/events documents every registered event type in its discriminator."""
    spec = create_app(_service(tmp_path)).openapi()
    ref = spec["paths"]["/runs/{run_id}/events"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    assert ref == "#/components/schemas/RunEventList"
    items = spec["components"]["schemas"]["RunEventList"]["properties"]["events"]["items"]
    mapping = items["discriminator"]["mapping"]
    assert set(mapping) == set(EVENT_TYPES)
    assert len(items["oneOf"]) == len({entry.data for entry in EVENT_TYPES.values()})


def test_stored_events_are_served_as_stored(tmp_path):
    """Old or unknown stored events must be returned unchanged with 200, never validated or filled with defaults."""
    service = _service(tmp_path)
    run = service.create_run(_item())
    legacy = RunEvent(
        run_id=run.run_id,
        phase=WorkflowPhase.STORAGE_PROVISION,
        event_type="storage.apply.failed",
        message="Legacy failure with empty payload",
        data={},
    )
    retired = RunEvent(
        run_id=run.run_id,
        phase=WorkflowPhase.COMPLETE,
        event_type="retired.unknown.event",
        message="Retired event from an older release",
        data={"old_key": "kept"},
    )
    service.store.append_event(legacy)
    service.store.append_event(retired)

    client = TestClient(create_app(service))
    resp = client.get(f"/runs/{run.run_id}/events")
    assert resp.status_code == 200
    by_type = {ev["event_type"]: ev for ev in resp.json()["events"]}
    assert by_type["storage.apply.failed"]["data"] == {}
    assert by_type["retired.unknown.event"]["data"] == {"old_key": "kept"}


def test_duplicate_event_type_is_refused():
    with pytest.raises(ValueError, match="duplicate event type"):
        _event("step.started", NoData)


def test_no_data_forbids_extra_fields():
    with pytest.raises(ValidationError):
        NoData.model_validate({"unexpected": True})
