import httpx
import pytest
import respx

from alletra_onboard.adapters.greenlake.devices import DevicesClient
from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient
from alletra_onboard.adapters.greenlake.service_catalog import ServiceCatalogClient
from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient
from alletra_onboard.application.provisioning import (
    DONE,
    SKIPPED,
    WOULD_DO,
    GreenLakeProvisioningService,
)
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, WorkflowPhase

BASE = "https://global.api.greenlake.hpe.com"


class StaticToken:
    async def token(self) -> str:
        return "jwt"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    async def _sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _sleep)
    monkeypatch.setattr("alletra_onboard.application.provisioning.asyncio.sleep", _sleep)


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y",
        part_number="R7C75-63004",
        subscription_key="KEY123",
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(
            mgmt_ipv4="10.64.154.225",
            mask="255.255.248.0",
            gateway="10.64.159.254",
            dns=["10.203.96.10"],
            ntp="ntp1",
            timezone="Asia/Tokyo",
        ),
        dscc_setup=DsccSetupConfig(system_name="b10k", country="JP"),
    )


def _service(device_state_timeout: float = 5.0) -> GreenLakeProvisioningService:
    http = GreenLakeHttpClient(BASE, StaticToken())
    return GreenLakeProvisioningService(
        http=http,
        devices=DevicesClient(http),
        subscriptions=SubscriptionsClient(http),
        service_catalog=ServiceCatalogClient(http),
        device_state_timeout=device_state_timeout,
    )


def _provisions():
    return httpx.Response(
        200,
        json={"items": [{"serviceManager": {"id": "svc-1"}, "region": "ap-northeast", "provisionStatus": "PROVISIONED"}]},
    )


def _phase(result, phase):
    return next(p for p in result.phases if p.phase == phase)


@respx.mock
async def test_full_provision_happy_path_registers_assigns_and_verifies():
    respx.get(f"{BASE}/service-catalog/v1/service-manager-provisions").mock(return_value=_provisions())

    # Subscription: absent, then present after add.
    respx.get(f"{BASE}/subscriptions/v1/subscriptions").mock(
        side_effect=[httpx.Response(200, json={"items": []}), httpx.Response(200, json={"items": [{"id": "sub-1"}]})]
    )
    respx.post(f"{BASE}/subscriptions/v1/subscriptions").mock(
        return_value=httpx.Response(202, headers={"Location": f"{BASE}/subscriptions/v1/async-operations/sub-op"})
    )
    respx.get(f"{BASE}/subscriptions/v1/async-operations/sub-op").mock(
        return_value=httpx.Response(200, json={"status": "SUCCEEDED"})
    )

    # Device: absent, then present after add.
    respx.get(f"{BASE}/devices/v1/devices").mock(
        side_effect=[httpx.Response(200, json={"items": []}), httpx.Response(200, json={"items": [{"id": "dev-1"}]})]
    )
    respx.post(f"{BASE}/devices/v1/devices").mock(
        return_value=httpx.Response(202, headers={"Location": f"{BASE}/devices/v1/async-operations/add-op"})
    )
    # Two PATCHes: assign then apply.
    respx.patch(f"{BASE}/devices/v1/devices").mock(
        side_effect=[
            httpx.Response(202, headers={"Location": f"{BASE}/devices/v1/async-operations/assign-op"}),
            httpx.Response(202, headers={"Location": f"{BASE}/devices/v1/async-operations/apply-op"}),
        ]
    )
    for op in ("add-op", "assign-op", "apply-op"):
        respx.get(f"{BASE}/devices/v1/async-operations/{op}").mock(
            return_value=httpx.Response(200, json={"status": "SUCCEEDED"})
        )

    assigned = {
        "id": "dev-1",
        "assignedState": "ASSIGNED_TO_SERVICE",
        "application": {"id": "svc-1"},
        "region": "ap-northeast",
    }
    respx.get(f"{BASE}/devices/v1/devices/dev-1").mock(
        side_effect=[
            httpx.Response(200, json={"id": "dev-1", "assignedState": "UNASSIGNED"}),  # _assign check
            httpx.Response(200, json=assigned),  # _wait_for_device_state
            httpx.Response(200, json={**assigned, "subscription": []}),  # _apply check
            httpx.Response(200, json={**assigned, "subscription": [{"id": "sub-1"}]}),  # _verify
        ]
    )

    result = await _service().provision(_item())

    assert result.succeeded is True
    assert (result.device_id, result.subscription_id, result.service_manager_id) == ("dev-1", "sub-1", "svc-1")
    assert result.assigned_state == "ASSIGNED_TO_SERVICE"
    assert _phase(result, WorkflowPhase.GL_REGISTER_DEVICE).status == DONE
    assert _phase(result, WorkflowPhase.GL_ASSIGN_APPLICATION).status == DONE
    assert _phase(result, WorkflowPhase.GL_VERIFY_DEVICE).status == DONE


@respx.mock
async def test_idempotent_rerun_skips_all_writes():
    respx.get(f"{BASE}/service-catalog/v1/service-manager-provisions").mock(return_value=_provisions())
    respx.get(f"{BASE}/subscriptions/v1/subscriptions").mock(
        return_value=httpx.Response(200, json={"items": [{"id": "sub-1"}]})
    )
    respx.get(f"{BASE}/devices/v1/devices").mock(
        return_value=httpx.Response(200, json={"items": [{"id": "dev-1"}]})
    )
    respx.get(f"{BASE}/devices/v1/devices/dev-1").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "dev-1",
                "assignedState": "ASSIGNED_TO_SERVICE",
                "application": {"id": "svc-1"},
                "region": "ap-northeast",
                "subscription": [{"id": "sub-1"}],
            },
        )
    )
    post_device = respx.post(f"{BASE}/devices/v1/devices").mock(return_value=httpx.Response(202))
    patch_device = respx.patch(f"{BASE}/devices/v1/devices").mock(return_value=httpx.Response(202))
    post_sub = respx.post(f"{BASE}/subscriptions/v1/subscriptions").mock(return_value=httpx.Response(202))

    result = await _service().provision(_item())

    assert result.succeeded is True
    assert _phase(result, WorkflowPhase.GL_REGISTER_DEVICE).status == SKIPPED
    assert _phase(result, WorkflowPhase.GL_ASSIGN_APPLICATION).status == SKIPPED
    assert _phase(result, WorkflowPhase.GL_APPLY_SUBSCRIPTION).status == SKIPPED
    assert post_device.call_count == 0
    assert patch_device.call_count == 0
    assert post_sub.call_count == 0


@respx.mock
async def test_dry_run_makes_no_writes_and_previews_all_phases():
    respx.get(f"{BASE}/service-catalog/v1/service-manager-provisions").mock(return_value=_provisions())
    respx.get(f"{BASE}/subscriptions/v1/subscriptions").mock(return_value=httpx.Response(200, json={"items": []}))
    respx.get(f"{BASE}/devices/v1/devices").mock(return_value=httpx.Response(200, json={"items": []}))
    post_device = respx.post(f"{BASE}/devices/v1/devices").mock(return_value=httpx.Response(202))
    patch_device = respx.patch(f"{BASE}/devices/v1/devices").mock(return_value=httpx.Response(202))
    post_sub = respx.post(f"{BASE}/subscriptions/v1/subscriptions").mock(return_value=httpx.Response(202))

    result = await _service().provision(_item(), dry_run=True)

    assert result.succeeded is False  # dry-run never claims success
    assert _phase(result, WorkflowPhase.GL_ADD_SUBSCRIPTION).status == WOULD_DO
    assert _phase(result, WorkflowPhase.GL_REGISTER_DEVICE).status == WOULD_DO
    assert _phase(result, WorkflowPhase.GL_ASSIGN_APPLICATION).status == WOULD_DO
    assert _phase(result, WorkflowPhase.GL_APPLY_SUBSCRIPTION).status == WOULD_DO
    assert _phase(result, WorkflowPhase.GL_VERIFY_DEVICE).status == WOULD_DO
    assert post_device.call_count == 0
    assert patch_device.call_count == 0
    assert post_sub.call_count == 0


@respx.mock
async def test_discover_with_no_provision_fails_clearly():
    respx.get(f"{BASE}/service-catalog/v1/service-manager-provisions").mock(
        return_value=httpx.Response(200, json={"items": []})
    )

    result = await _service().provision(_item())

    assert result.succeeded is False
    assert result.error is not None
    assert "No PROVISIONED" in result.error
