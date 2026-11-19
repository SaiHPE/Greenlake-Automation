"""Correct the Windows system clock so token auth doesn't fail on clock skew.

DSCC sign-in fails with "iat is in the future" when the host clock has drifted. NTP can't be
relied on (UDP/123 is firewalled in locked environments and proxies don't carry NTP), so this
reads the authoritative ``Date`` header from an HTTPS endpoint — through the same proxy
everything else uses (httpx honors HTTPS_PROXY) — and sets the clock from it via the Win32
``SetSystemTime`` (which takes UTC, so there's no timezone math). Works on any Windows host —
jump box or laptop — wherever the app already has HTTPS egress. Setting the clock needs
Administrator; reading the status does not.
"""

from __future__ import annotations

import ctypes
import sys
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import NamedTuple

import httpx
from pydantic import BaseModel

from alletra_onboard.application.platform.tls import ssl_context

# Tried in order; the caller's preferred source (e.g. the DSCC console, known reachable in
# context) is tried first, then these fall-backs, so the check works wherever the host has
# HTTPS egress — not just where one specific host is reachable.
TIME_SOURCES = ("https://www.hpe.com", "https://www.microsoft.com", "https://www.cloudflare.com")
IN_SYNC_THRESHOLD_S = 5.0
ERROR_PRIVILEGE_NOT_HELD = 1314


class ClockStatus(BaseModel):
    in_sync: bool
    skew_seconds: float | None  # local - server (positive = clock ahead); None if unreachable
    local_utc: str
    server_utc: str | None
    is_admin: bool
    source: str
    error: str | None = None


class ClockSyncResult(BaseModel):
    changed: bool
    skew_seconds_before: float
    local_utc_before: str
    local_utc_after: str
    server_utc: str
    source: str


def is_elevated() -> bool:
    """True if the current process can set the clock (Administrator on Windows)."""
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # noqa: BLE001
        return False


def _candidates(preferred: str | None) -> list[str]:
    ordered = [preferred] if preferred else []
    ordered += [s for s in TIME_SOURCES if s != preferred]
    return ordered


def _now() -> datetime:
    return datetime.now(UTC)


class _Reading(NamedTuple):
    server: datetime     # the source's Date header
    local: datetime      # this clock at the midpoint of that request
    source: str

    @property
    def skew(self) -> float:
        return (self.local - self.server).total_seconds()


async def _server_utc(preferred: str | None = None) -> _Reading:
    """The first candidate that answers with a Date header, and the local time to compare it with.
    The local time is taken per attempt, at the midpoint of that request: a slow or failed source
    before it (10 s timeout) must not count as skew. trust_env (default) makes httpx use HTTPS_PROXY,
    so this works behind the lab proxy."""
    last = "no time sources tried"
    for url in _candidates(preferred):
        try:
            t0 = _now()
            async with httpx.AsyncClient(
                timeout=10.0, follow_redirects=True, verify=ssl_context()
            ) as client:
                resp = await client.get(url)
            t1 = _now()
            date = resp.headers.get("date")
            if date:
                return _Reading(parsedate_to_datetime(date).astimezone(UTC), t0 + (t1 - t0) / 2, url)
            last = f"no Date header from {url}"
        except Exception as exc:  # noqa: BLE001 - try the next source
            last = f"{type(exc).__name__} from {url}: {str(exc)[:80]}"
    raise RuntimeError(last)


async def clock_status(url: str | None = None) -> ClockStatus:
    try:
        reading = await _server_utc(url)
    except Exception as exc:  # noqa: BLE001 - status must never raise; the UI just won't warn.
        return ClockStatus(
            in_sync=True,
            skew_seconds=None,
            local_utc=_now().isoformat(),
            server_utc=None,
            is_admin=is_elevated(),
            source=url or "(none reachable)",
            error=f"{type(exc).__name__}: {str(exc)[:200]}",
        )
    skew = reading.skew
    return ClockStatus(
        in_sync=abs(skew) <= IN_SYNC_THRESHOLD_S,
        skew_seconds=skew,
        local_utc=reading.local.isoformat(),
        server_utc=reading.server.isoformat(),
        is_admin=is_elevated(),
        source=reading.source,
    )


def _set_system_utc(when: datetime) -> None:
    if sys.platform != "win32":
        raise RuntimeError("System clock sync is only supported on Windows.")
    import ctypes.wintypes as wt

    class SYSTEMTIME(ctypes.Structure):
        _fields_ = [
            ("wYear", wt.WORD),
            ("wMonth", wt.WORD),
            ("wDayOfWeek", wt.WORD),
            ("wDay", wt.WORD),
            ("wHour", wt.WORD),
            ("wMinute", wt.WORD),
            ("wSecond", wt.WORD),
            ("wMilliseconds", wt.WORD),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    st = SYSTEMTIME(
        when.year, when.month, when.isoweekday() % 7, when.day,
        when.hour, when.minute, when.second, when.microsecond // 1000,
    )
    if not kernel32.SetSystemTime(ctypes.byref(st)):  # SetSystemTime takes UTC
        err = ctypes.get_last_error()
        if err == ERROR_PRIVILEGE_NOT_HELD:
            raise PermissionError("Setting the clock needs Administrator — run the app as Administrator.")
        raise OSError(f"SetSystemTime failed (WinError {err}).")


async def sync_clock(url: str | None = None) -> ClockSyncResult:
    """Set the system clock from the HTTPS time source if it has drifted past the threshold."""
    reading = await _server_utc(url)
    skew = reading.skew
    changed = abs(skew) > IN_SYNC_THRESHOLD_S
    if changed:
        # the Date header plus half the round trip, plus the time since that request
        _set_system_utc(_now() - timedelta(seconds=skew))
    after = _now()
    return ClockSyncResult(
        changed=changed,
        skew_seconds_before=skew,
        local_utc_before=reading.local.isoformat(),
        local_utc_after=after.isoformat(),
        server_utc=reading.server.isoformat(),
        source=reading.source,
    )
