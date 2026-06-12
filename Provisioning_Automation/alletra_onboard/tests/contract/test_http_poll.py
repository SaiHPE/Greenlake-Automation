import httpx
import pytest
import respx

from alletra_onboard.adapters.greenlake.http_client import (
    GreenLakeAsyncOperationError,
    GreenLakeHttpClient,
)


class StaticToken:
    async def token(self) -> str:
        return "jwt"


@respx.mock
async def test_poll_async_returns_payload_on_terminal_success(monkeypatch):
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-1"
    respx.get(op).mock(
        side_effect=[
            httpx.Response(200, json={"status": "RUNNING", "suggestedPollingIntervalSeconds": 1}),
            httpx.Response(200, json={"status": "SUCCEEDED", "id": "op-1"}),
        ]
    )
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    payload = await http.poll_async(op)

    assert payload["status"] == "SUCCEEDED"


@respx.mock
async def test_poll_async_raises_on_terminal_failure(monkeypatch):
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-2"
    respx.get(op).mock(return_value=httpx.Response(200, json={"status": "FAILED", "message": "bad part number"}))
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    with pytest.raises(GreenLakeAsyncOperationError) as exc:
        await http.poll_async(op)

    assert "bad part number" in str(exc.value)


@respx.mock
async def test_request_retries_on_429_then_succeeds(monkeypatch):
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    route = respx.get("https://api.example/devices/v1/devices").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"items": []}),
        ]
    )
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    response = await http.request("GET", "/devices/v1/devices", bucket="device_read")

    assert response.status_code == 200
    assert route.call_count == 2
