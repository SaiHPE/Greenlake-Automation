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
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

import httpx
from pydantic import BaseModel

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


async def _server_utc(preferred: str | None = None) -> tuple[datetime, str]:
    """Return (UTC now, source URL used), trying candidates until one yields a Date header.
    trust_env (default) makes httpx use HTTPS_PROXY, so this works behind the lab proxy."""
    last = "no time sources tried"
    for url in _candidates(preferred):
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url)
            date = resp.headers.get("date")
            if date:
                return parsedate_to_datetime(date).astimezone(UTC), url
            last = f"no Date header from {url}"
        except Exception as exc:  # noqa: BLE001 - try the next source
            last = f"{type(exc).__name__} from {url}: {str(exc)[:80]}"
    raise RuntimeError(last)


async def clock_status(url: str | None = None) -> ClockStatus:
    local = datetime.now(UTC)
    try:
        server, source = await _server_utc(url)
    except Exception as exc:  # noqa: BLE001 - status must never raise; the UI just won't warn.
        return ClockStatus(
            in_sync=True,
            skew_seconds=None,
            local_utc=local.isoformat(),
            server_utc=None,
            is_admin=is_elevated(),
            source=url or "(none reachable)",
            error=f"{type(exc).__name__}: {str(exc)[:200]}",
        )
    skew = (local - server).total_seconds()
    return ClockStatus(
        in_sync=abs(skew) <= IN_SYNC_THRESHOLD_S,
        skew_seconds=skew,
        local_utc=local.isoformat(),
        server_utc=server.isoformat(),
        is_admin=is_elevated(),
        source=source,
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
    before = datetime.now(UTC)
    server, source = await _server_utc(url)
    skew = (before - server).total_seconds()
    changed = abs(skew) > IN_SYNC_THRESHOLD_S
    if changed:
        _set_system_utc(server)
    after = datetime.now(UTC)
    return ClockSyncResult(
        changed=changed,
        skew_seconds_before=skew,
        local_utc_before=before.isoformat(),
        local_utc_after=after.isoformat(),
        server_utc=server.isoformat(),
        source=source,
    )
