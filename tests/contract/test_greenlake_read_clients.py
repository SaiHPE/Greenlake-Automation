from alletra_onboard.adapters.greenlake.devices import DevicesClient
from alletra_onboard.adapters.greenlake.service_catalog import ServiceCatalogClient
from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def json(self) -> dict:
        return self.payload


class RecordingHttp:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls: list[dict] = []

    async def request(self, method: str, path: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": method, "path": path, **kwargs})
        return FakeResponse(self.payload)


async def test_device_find_by_serial_uses_read_filter():
    http = RecordingHttp({"items": [{"id": "dev-123"}]})
    result = await DevicesClient(http).find_by_serial("SGHD44LQLS")

    assert result == {"id": "dev-123"}
    assert http.calls == [
        {
            "method": "GET",
            "path": "/devices/v1/devices",
            "bucket": "device_read",
            "params": {"filter": "serialNumber eq 'SGHD44LQLS'"},
        }
    ]


async def test_subscription_find_by_key_uses_read_filter():
    http = RecordingHttp({"items": [{"id": "sub-123"}]})
    result = await SubscriptionsClient(http).find_by_key("secret-key")

    assert result == {"id": "sub-123"}
    assert http.calls == [
        {
            "method": "GET",
            "path": "/subscriptions/v1/subscriptions",
            "bucket": "subscription_read",
            "params": {"filter": "key eq 'secret-key'"},
        }
    ]


async def test_service_catalog_provisions_filter_client_side_by_region_and_status():
    # The endpoint 400s on server-side status/combined filters, so the client fetches
    # unfiltered and filters in Python: only PROVISIONED items in the target region.
    http = RecordingHttp(
        {
            "items": [
                {"serviceManager": {"id": "svc-123"}, "region": "ap-northeast", "provisionStatus": "PROVISIONED"},
                {"serviceManager": {"id": "svc-other"}, "region": "us-west", "provisionStatus": "PROVISIONED"},
                {"serviceManager": {"id": "svc-unprov"}, "region": "ap-northeast", "provisionStatus": "UNPROVISIONED"},
            ]
        }
    )
    result = await ServiceCatalogClient(http).service_manager_provisions("ap-northeast")

    assert [provision.service_manager_id for provision in result] == ["svc-123"]
    assert http.calls == [
        {
            "method": "GET",
            "path": "/service-catalog/v1/service-manager-provisions",
            "bucket": "service_catalog_read",
        }
    ]