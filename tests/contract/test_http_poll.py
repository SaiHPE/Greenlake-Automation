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
async def test_poll_async_reports_every_poll(monkeypatch):
    """A poll that says nothing for its 15-minute budget makes a working step look hung.

    MEASURED live during a GreenLake registration: the device add SUCCEEDED (inventory showed it
    registered and ASSIGNED_TO_SERVICE) while the operation resource never went terminal, so the
    UI sat on "Running" with no new line and the operator had to query the API to learn the truth.
    """
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-progress"
    respx.get(op).mock(
        side_effect=[
            httpx.Response(200, json={"status": "PENDING"}),
            httpx.Response(200, json={"status": "RUNNING"}),
            httpx.Response(200, json={"status": "SUCCEEDED"}),
        ]
    )
    seen: list[tuple[str, float]] = []
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    await http.poll_async(op, on_progress=lambda status, elapsed: seen.append((status, elapsed)))

    assert [s for s, _ in seen] == ["PENDING", "RUNNING"]   # terminal poll needs no progress line
    assert all(elapsed >= 0 for _, elapsed in seen)


@respx.mock
async def test_poll_async_stops_when_the_real_state_says_done(monkeypatch):
    """The operation resource describes the work; the inventory IS the work.

    This is the exact live failure: a never-terminal operation resource for a device that was
    already registered. Without the settled() escape the step waits the full budget and then fails,
    despite the work having succeeded minutes earlier.
    """
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-stuck"
    respx.get(op).mock(return_value=httpx.Response(200, json={"status": "PENDING"}))  # never settles
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    calls = {"n": 0}

    async def settled() -> bool:
        calls["n"] += 1
        return calls["n"] >= 2          # the device shows up in inventory on the second check

    payload = await http.poll_async(op, settled=settled)

    assert payload["status"] == "SETTLED_BY_STATE"
    assert payload["lastReportedStatus"] == "PENDING"


@respx.mock
async def test_poll_async_settled_check_failure_does_not_end_the_poll(monkeypatch):
    """An unreadable state check means 'not yet', never 'done' — it must not fake success."""
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-flaky"
    respx.get(op).mock(
        side_effect=[
            httpx.Response(200, json={"status": "PENDING"}),
            httpx.Response(200, json={"status": "SUCCEEDED"}),
        ]
    )
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    async def settled() -> bool:
        return False                     # the caller's own guard swallows read errors into False

    payload = await http.poll_async(op, settled=settled)
    assert payload["status"] == "SUCCEEDED"


@respx.mock
async def test_poll_async_timeout_names_the_last_status(monkeypatch):
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-timeout"
    respx.get(op).mock(return_value=httpx.Response(200, json={"status": "PENDING"}))
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    with pytest.raises(TimeoutError, match="PENDING"):
        await http.poll_async(op, max_wait_seconds=0.0)


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
async def test_poll_async_surfaces_failed_device_detail(monkeypatch):
    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr("alletra_onboard.adapters.greenlake.http_client.asyncio.sleep", _no_sleep)
    op = "https://api.example/devices/v1/async-operations/op-3"
    respx.get(op).mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "FAILED",
                "result": {
                    "failedDevices": [
                        {"serialNumber": "SGHD45FF0Y", "errorCode": "HPE_GL_ERROR_NOT_FOUND", "message": "Device not found"}
                    ]
                },
            },
        )
    )
    http = GreenLakeHttpClient("https://api.example", StaticToken())

    with pytest.raises(GreenLakeAsyncOperationError) as exc:
        await http.poll_async(op)

    message = str(exc.value)
    assert "SGHD45FF0Y" in message
    assert "Device not found" in message
    assert "HPE_GL_ERROR_NOT_FOUND" in message


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
