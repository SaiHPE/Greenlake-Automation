import sys
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime

import httpx
import pytest
import respx

from alletra_onboard.adapters.system import clock
from alletra_onboard.adapters.system.clock import (
    TIME_SOURCES,
    _set_system_utc,
    clock_status,
    is_elevated,
    sync_clock,
)

TRUE_UTC = datetime(2026, 11, 19, 9, 0, 0, tzinfo=UTC)


class FakeClock:
    """This host's clock, `ahead` seconds off the true time; requests move it on by their duration."""

    def __init__(self, ahead: float = 0.0):
        self.true = TRUE_UTC
        self.ahead = timedelta(seconds=ahead)

    def now(self) -> datetime:
        return self.true + self.ahead

    def wait(self, seconds: float) -> None:
        self.true += timedelta(seconds=seconds)


def _slow_first_source(fake: FakeClock) -> None:
    """The preferred source times out after 10 s; the first fall-back answers in 0.4 s with the true time."""
    def timeout(_request):
        fake.wait(10.0)
        raise httpx.ConnectTimeout("timed out")

    def answer(_request):
        fake.wait(0.2)
        date = format_datetime(fake.true, usegmt=True)    # the server stamps its reply mid-way
        fake.wait(0.2)
        return httpx.Response(200, headers={"Date": date})

    respx.get("https://slow.test/").mock(side_effect=timeout)
    respx.get(TIME_SOURCES[0]).mock(side_effect=answer)


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


@respx.mock
async def test_a_slow_first_source_is_not_skew(monkeypatch):
    # BL-63: the local time was taken before the 10 s timeout and read as 10 s of skew
    fake = FakeClock(ahead=0.0)
    monkeypatch.setattr(clock, "_now", fake.now)
    _slow_first_source(fake)
    status = await clock_status("https://slow.test/")
    assert status.source == TIME_SOURCES[0]
    assert status.in_sync is True
    assert abs(status.skew_seconds) < 1.0


@respx.mock
async def test_a_real_skew_behind_a_slow_first_source_is_still_reported(monkeypatch):
    fake = FakeClock(ahead=60.0)
    monkeypatch.setattr(clock, "_now", fake.now)
    _slow_first_source(fake)
    status = await clock_status("https://slow.test/")
    assert status.in_sync is False
    assert 59.0 < status.skew_seconds < 61.0


@respx.mock
async def test_sync_sets_the_source_time_plus_half_the_round_trip(monkeypatch):
    fake = FakeClock(ahead=-30.0)
    monkeypatch.setattr(clock, "_now", fake.now)
    _slow_first_source(fake)
    set_to: list[datetime] = []
    monkeypatch.setattr(clock, "_set_system_utc", set_to.append)
    result = await sync_clock("https://slow.test/")
    assert result.changed is True and result.source == TIME_SOURCES[0]
    assert -31.0 < result.skew_seconds_before < -29.0
    # set to the true time of the moment it is set, within the Date header's one second
    assert len(set_to) == 1 and abs((set_to[0] - fake.true).total_seconds()) < 1.0


@respx.mock
async def test_sync_leaves_a_right_clock_alone_behind_a_slow_first_source(monkeypatch):
    fake = FakeClock(ahead=0.0)
    monkeypatch.setattr(clock, "_now", fake.now)
    _slow_first_source(fake)
    set_to: list[datetime] = []
    monkeypatch.setattr(clock, "_set_system_utc", set_to.append)
    result = await sync_clock("https://slow.test/")
    assert result.changed is False and set_to == []


def test_set_system_utc_rejects_non_windows(monkeypatch):
    # Guard: forcing non-Windows makes it raise BEFORE any SetSystemTime call, so this test
    # can never change the host clock.
    monkeypatch.setattr(sys, "platform", "linux")
    with pytest.raises(RuntimeError):
        _set_system_utc(datetime.now(UTC))


def test_is_elevated_returns_bool():
    assert isinstance(is_elevated(), bool)


@respx.mock
async def test_bad_date_header_falls_through_to_next_time_source():
    respx.get("https://bad-date.test/").mock(return_value=httpx.Response(200, headers={"Date": "not-a-date"}))
    respx.get(TIME_SOURCES[0]).mock(
        return_value=httpx.Response(200, headers={"Date": "Sat, 13 Jun 2026 04:47:16 GMT"})
    )
    status = await clock_status("https://bad-date.test/")
    assert status.source == TIME_SOURCES[0] and status.error is None
