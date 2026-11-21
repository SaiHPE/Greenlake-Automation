"""Contract tests for the run-event registry and its OpenAPI schema (STANDARD T4)."""

from __future__ import annotations

import asyncio
import base64
import json
import time

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import ValidationError

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.api.schemas import (
    ConsoleCommandResponse,
    ConsoleLogResponse,
    ConsoleTargetsResponse,
    ConsoleTerminalResponse,
    InitSheetUploadResponse,
    InitSheetUploadResult,
    RunDetailResponse,
    app_profile_model,
)
from alletra_onboard.application.platform.init_sheet import compose_workbook_bytes
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


def test_schema_names_are_unambiguous_and_snapshot_state_is_narrow(tmp_path):
    """The events payload is named AsBuiltResultData so it never clashes with the documents asbuilt
    AsBuiltData dataclass; PlainEvent replaces placeholder NoEvent; SnapshotAction.state matches only
    the three states the snapshot planner emits; and documented-only routes name their models."""
    spec = create_app(_service(tmp_path)).openapi()
    schemas = spec["components"]["schemas"]
    assert "AsBuiltData" not in schemas
    assert "AsBuiltResultData" in schemas
    assert "NoEvent" not in schemas
    assert "PlainEvent" in schemas
    assert schemas["SnapshotAction"]["properties"]["state"]["enum"] == ["create", "exists", "conflict"]
    expected_refs = (
        ("/app/profile", "get", "AppProfile"),
        ("/init-sheet/upload", "post", "InitSheetUploadResult"),
        ("/runs/{run_id}", "get", "RunDetailResponse"),
        ("/runs/{run_id}/console/log", "get", "ConsoleLogResponse"),
        ("/runs/{run_id}/console/targets", "get", "ConsoleTargetsResponse"),
        ("/runs/{run_id}/console", "post", "ConsoleCommandResponse"),
        ("/runs/{run_id}/console/terminal", "post", "ConsoleTerminalResponse"),
    )
    for path, method, schema in expected_refs:
        ref = spec["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        assert ref == f"#/components/schemas/{schema}"
    assert "text/plain" in spec["paths"]["/runs/{run_id}/console/log"]["get"]["responses"]["200"]["content"]


_SHEET_INIT = {
    "gl_client_id": "client-123",
    "gl_client_secret": "secret-xyz",
    "gl_token_url": "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/t/token",
    "serial_number": "SGHD45FF0Y",
    "part_number": "S0B84A",
    "subscription_key": "YHHDKEY123",
    "service_catalog_region_id": "ap-northeast",
    "dscc_region_code": "jp1",
    "mgmt_ipv4": "10.64.154.225",
    "mask": "255.255.248.0",
    "gateway": "10.64.159.254",
    "dns1": "10.203.96.10",
    "ntp": "ntp1.example.net",
    "timezone": "Asia/Kolkata",
    "proxy_host": "proxy.example.com",
    "proxy_port": "8080",
    "contact_first_name": "Jane",
    "contact_last_name": "Doe",
    "contact_language": "English",
    "contact_company": "HPE",
    "contact_phone": "8000000000",
    "contact_email": "jane@example.com",
    "dscc_system_name": "MPB10K-TEST",
    "dscc_country": "India",
    "secret_name": "b10000-admin",
    "secret_username": "3paradm",
}
_SHEET_TARGETS = {
    "prov_array_host": "10.64.154.225",
    "prov_array_user": "3paradm",
    "prov_array_password": "arraypw",
    "prov_vcenter_host": "vc.example.com",
    "prov_vcenter_user": "administrator@vsphere.local",
    "prov_vcenter_password": "vcpw",
}


def _iter_routes(routes):
    for route in routes:
        if isinstance(route, APIRoute):
            yield route
        elif hasattr(route, "original_router"):
            yield from _iter_routes(route.original_router.routes)


def _route_for(app, path: str, method: str) -> APIRoute:
    for route in _iter_routes(app.routes):
        if route.path == path and method in route.methods:
            return route
    raise AssertionError(f"route not found: {method} {path}")


def _assert_strict(resp, model) -> dict:
    assert resp.status_code == 200, resp.text
    parsed = model.model_validate_json(resp.content, strict=True)
    body = resp.json()
    assert json.loads(parsed.model_dump_json()) == body
    return body


@pytest.mark.parametrize(("profile", "mode"), [("full", "BOTH"), ("init-only", "FULL_ONBOARDING")])
def test_documented_only_routes_match_real_responses_in_both_profiles(tmp_path, monkeypatch, profile, mode):
    """Documentation-only OpenAPI models must strictly validate and round-trip the real wire JSON
    in both build profiles, while /app/profile and /init-sheet/upload keep their runtime serialisation."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ALLETRA_PROFILE", profile)
    service = _service(tmp_path)
    service.console.launcher = lambda _argv: None
    app = create_app(service)
    client = TestClient(app)

    # Documentation only: never add/change response_model on the initialisation track or console routes.
    assert _route_for(app, "/app/profile", "GET").response_model is dict
    assert _route_for(app, "/init-sheet/upload", "POST").response_model is InitSheetUploadResponse
    assert _route_for(app, "/runs/{run_id}/console/log", "GET").response_model is None

    # 1. GET /app/profile
    _assert_strict(client.get("/app/profile"), app_profile_model())

    # 2. POST /init-sheet/upload (with proxy_host/proxy_port populated)
    tpl = client.get("/init-sheet/template").content
    filled = compose_workbook_bytes(
        base=tpl,
        init=_SHEET_INIT,
        targets=_SHEET_TARGETS if profile == "full" else None,
        volumes=[{"name": "CRV_Prod01", "size_gib": "1024"}] if profile == "full" else None,
        hostsets=[{"name": "CRVLZ_Hostset"}] if profile == "full" else None,
    )
    upload_body = _assert_strict(
        client.post("/init-sheet/upload", json={"content_b64": base64.b64encode(filled).decode("ascii")}),
        InitSheetUploadResult,
    )
    assert upload_body["work_item"]["network"]["proxy_host"] == "proxy.example.com"
    assert upload_body["work_item"]["network"]["proxy_port"] == 8080
    assert "password" not in upload_body["work_item"]["dscc_setup"]

    # 3. POST /runs/from-sheet + GET /runs/{run_id}
    run_resp = client.post("/runs/from-sheet", json={"token": upload_body["token"], "mode": mode})
    assert run_resp.status_code == 200, run_resp.text
    run_id = run_resp.json()["run"]["run_id"]
    _assert_strict(client.get(f"/runs/{run_id}"), RunDetailResponse)

    # 4. Console routes: real command_log.record inside coordinator.recording, zero live devices.
    async def _record_one() -> None:
        with service.coordinator.recording(run_id):
            command_log.record(
                target="10.64.154.225", transport="ssh", command="showversion",
                started=time.monotonic(), ok=True, result="ok", output="Release version 10.6.0",
            )

    asyncio.run(_record_one())
    log_body = _assert_strict(client.get(f"/runs/{run_id}/console/log"), ConsoleLogResponse)
    assert len(log_body["commands"]) == 1
    _assert_strict(client.get(f"/runs/{run_id}/console/targets"), ConsoleTargetsResponse)
    if profile == "full":
        cmd_body = _assert_strict(
            client.post(f"/runs/{run_id}/console", json={"command": "removevv -f fake", "target": "array"}),
            ConsoleCommandResponse,
        )
        assert cmd_body["refused"] is True
        term_body = _assert_strict(
            client.post(f"/runs/{run_id}/console/terminal", json={"target": "array"}),
            ConsoleTerminalResponse,
        )
        assert term_body["launched"] is True
