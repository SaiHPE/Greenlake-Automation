import sys
from datetime import UTC, datetime

import httpx
import pytest
import respx

from alletra_onboard.adapters.system.clock import _set_system_utc, clock_status, is_elevated


@respx.mock
async def test_clock_status_computes_skew():
    respx.get("https://time.test/").mock(
        return_value=httpx.Response(200, headers={"Date": "Sat, 13 Jun 2026 04:47:16 GMT"})
    )
    status = await clock_status("https://time.test/")
    assert status.server_utc is not None
    assert status.skew_seconds is not None
    assert isinstance(status.is_admin, bool)


@respx.mock
async def test_clock_status_unreachable_is_graceful():
    respx.get("https://nope.test/").mock(side_effect=httpx.ConnectError("boom"))
    status = await clock_status("https://nope.test/")
    # Can't warn if the time source is unreachable — report in_sync with the error noted.
    assert status.in_sync is True
    assert status.skew_seconds is None
    assert status.error is not None


def test_set_system_utc_rejects_non_windows(monkeypatch):
    # Guard: forcing non-Windows makes it raise BEFORE any SetSystemTime call, so this test
    # can never change the host clock.
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(RuntimeError):
        _set_system_utc(datetime.now(UTC))


def test_is_elevated_returns_bool():
    assert isinstance(is_elevated(), bool)
