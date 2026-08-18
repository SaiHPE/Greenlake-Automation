"""Proxy resolution — use the environment's proxy the way the browser does, never hardcode one.

The *effective proxy* for an outbound URL is (highest precedence first): a manual override the operator
set, else an explicit ``HTTPS_PROXY`` env var, else the OS **system proxy** auto-detected per-URL
(WinINET static + PAC/WPAD, resolved via WinHTTP — exactly what the browser does), else none (direct).
On-prem targets (localhost, the cloudinit link-local, the array/vCenter/switch IPs) are bypassed so
their traffic never tunnels out. No proxy host is ever hardcoded. See docs/adr/0008.
"""

from __future__ import annotations

import ctypes
import fnmatch
import ipaddress
import os
import sys
from urllib.parse import urlparse
from urllib.request import getproxies_registry

_IS_WINDOWS = sys.platform == "win32"

# Reached DIRECTLY, never via the proxy. Extended per-run with the array/vCenter/switch IPs.
# BOTH link-local families: the array's setup wizard may only be reachable on IPv6 (the Discovery
# Tool reports whichever it found), and sending link-local traffic to a corporate proxy cannot work
# — the proxy has no route to an address that is only meaningful on this cable.
DEFAULT_BYPASS: tuple[str, ...] = ("localhost", "127.0.0.1", "169.254.*", "fe80:*", "::1")


#: The operator's "there is no proxy here" answer. A non-empty sentinel ON PURPOSE: an empty
#: override means "auto-detect", and `set_env_values` deliberately ignores empty values (so a blank
#: field can never wipe a saved secret) — so blanking the field could never persist a *decision* to
#: go direct. Saving this does. Matches the existing BROWSER_PROXY=direct:// convention.
DIRECT = "direct://"
_DIRECT_WORDS = frozenset({"direct", "direct://", "none", "no", "off", "-"})


def is_direct(value: str | None) -> bool:
    """Does this override mean "force a direct connection, ignore any detected proxy"?"""
    return (value or "").strip().lower() in _DIRECT_WORDS


def normalize_proxy(value: str | None) -> str | None:
    """A proxy spec (``host:port``, ``user:pass@host:port``, or a full URL) -> ``http://…``.

    Returns None for: empty, a direct sentinel, and — the case that bit us — anything that does not
    resolve to a real HOST. Windows' own registry yields ``'http://'`` when ProxyEnable is set with
    an empty ProxyServer entry (urllib's getproxies_registry prefixes the bare protocol), and the
    old passthrough published that host-less string into HTTPS_PROXY and reported it to the operator
    as "detected system proxy http://" — an unusable proxy that broke every outbound cloud call and
    could not be removed from the UI. A proxy URL with no hostname is not a proxy.
    """
    if not value:
        return None
    value = value.strip()
    if not value or is_direct(value):
        return None
    candidate = value if "://" in value else f"http://{value}"
    try:
        if not urlparse(candidate).hostname:
            return None
    except ValueError:  # malformed (e.g. a bad IPv6 literal)
        return None
    return candidate


def _first_proxy(proxy_list: str | None) -> str | None:
    """WinHTTP/WinINET proxy strings are ``host:port`` | ``http=h:p;https=h:p`` | ``h1:p1 h2:p2``.
    Return the first https (else unlabelled) ``host:port`` as an ``http://…`` URL."""
    if not proxy_list:
        return None
    entries = [e for e in proxy_list.replace(";", " ").split() if e]
    https = [e.split("=", 1)[1] for e in entries if e.lower().startswith("https=")]
    plain = [e for e in entries if "=" not in e]
    picks = https or plain or [e.split("=", 1)[-1] for e in entries]
    return normalize_proxy(picks[0]) if picks else None


def is_bypassed(host: str | None, bypass: list[str]) -> bool:
    """Should `host` be reached directly (not via the proxy)? Matches exact, glob (169.254.*), CIDR."""
    if not host:
        return True
    host = host.strip().lower().strip("[]")
    # An IPv6 zone ("fe80::1%eth0") is a local interface selector, not part of the address — strip
    # it so CIDR entries still match. Glob entries match either form.
    bare = host.split("%", 1)[0]
    for raw in bypass:
        entry = (raw or "").strip().lower().strip("[]")
        if not entry:
            continue
        if entry in (host, bare) or ("*" in entry and fnmatch.fnmatch(host, entry)):
            return True
        if "/" in entry:
            try:
                if ipaddress.ip_address(bare) in ipaddress.ip_network(entry.strip("[]"), strict=False):
                    return True
            except ValueError:
                pass
    return False


# --------------------------------------------------------------- Windows system-proxy (WinHTTP)

if _IS_WINDOWS:
    from ctypes import wintypes

    # The WinHTTP out-strings below are GlobalAlloc'd by WinHTTP and we must GlobalFree them. They are
    # declared as raw c_void_p (NOT LPWSTR) on purpose: ctypes auto-converts an LPWSTR field to a
    # Python str on access, which LOSES the original pointer — then freeing the auto-converted str's
    # address (ctypes.cast on a str returns a pointer INTO the Python object) corrupts the process heap
    # (STATUS_HEAP_CORRUPTION, 0xC0000374). Keeping the raw pointer lets us read it with wstring_at and
    # GlobalFree the exact address WinHTTP gave us. See docs/adr/0008.
    class _IE_PROXY_CONFIG(ctypes.Structure):
        _fields_ = [
            ("fAutoDetect", wintypes.BOOL),
            ("lpszAutoConfigUrl", ctypes.c_void_p),
            ("lpszProxy", ctypes.c_void_p),
            ("lpszProxyBypass", ctypes.c_void_p),
        ]

    class _AUTOPROXY_OPTIONS(ctypes.Structure):
        _fields_ = [
            ("dwFlags", wintypes.DWORD),
            ("dwAutoDetectFlags", wintypes.DWORD),
            ("lpszAutoConfigUrl", wintypes.LPCWSTR),
            ("lpvReserved", ctypes.c_void_p),
            ("dwReserved", wintypes.DWORD),
            ("fAutoLogonIfChallenged", wintypes.BOOL),
        ]

    class _PROXY_INFO(ctypes.Structure):
        _fields_ = [
            ("dwAccessType", wintypes.DWORD),
            ("lpszProxy", ctypes.c_void_p),        # WinHTTP GlobalAlloc'd — raw ptr, see note above
            ("lpszProxyBypass", ctypes.c_void_p),
        ]

    _AUTO_DETECT = 0x00000001
    _CONFIG_URL = 0x00000002
    _DETECT_DHCP = 0x00000001
    _DETECT_DNS_A = 0x00000002
    _ACCESS_NO_PROXY = 1

    def _winhttp():
        wh = ctypes.WinDLL("winhttp")
        wh.WinHttpGetIEProxyConfigForCurrentUser.argtypes = [ctypes.POINTER(_IE_PROXY_CONFIG)]
        wh.WinHttpGetIEProxyConfigForCurrentUser.restype = wintypes.BOOL
        wh.WinHttpOpen.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        wh.WinHttpOpen.restype = ctypes.c_void_p
        wh.WinHttpGetProxyForUrl.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(_AUTOPROXY_OPTIONS), ctypes.POINTER(_PROXY_INFO)]
        wh.WinHttpGetProxyForUrl.restype = wintypes.BOOL
        wh.WinHttpCloseHandle.argtypes = [ctypes.c_void_p]
        wh.WinHttpCloseHandle.restype = wintypes.BOOL
        return wh

    def _wstr(ptr) -> str | None:
        """Copy a wide string from a raw pointer (int address or None) to a Python str, WITHOUT taking
        ownership of the pointer (so the caller can still GlobalFree the original)."""
        return ctypes.wstring_at(ptr) if ptr else None

    def _win_system_proxy(url: str) -> str | None:
        """Per-URL system proxy via WinHTTP: WinINET static, else PAC/WPAD — as the browser resolves it."""
        try:
            wh = _winhttp()
        except Exception:  # noqa: BLE001 - winhttp unavailable
            return None
        cfg = _IE_PROXY_CONFIG()
        static: str | None = None
        auto_detect = True
        pac_url: str | None = None
        try:
            if wh.WinHttpGetIEProxyConfigForCurrentUser(ctypes.byref(cfg)):
                static = _first_proxy(_wstr(cfg.lpszProxy))
                auto_detect = bool(cfg.fAutoDetect)
                pac_url = _wstr(cfg.lpszAutoConfigUrl)
        except Exception:  # noqa: BLE001
            pass
        finally:
            _global_free(cfg.lpszAutoConfigUrl, cfg.lpszProxy, cfg.lpszProxyBypass)

        resolved = _win_proxy_for_url(wh, url, auto_detect, pac_url) if (auto_detect or pac_url) else None
        return resolved or static

    def _win_proxy_for_url(wh, url: str, auto_detect: bool, pac_url: str | None) -> str | None:
        session = wh.WinHttpOpen("alletra-onboard", _ACCESS_NO_PROXY, None, None, 0)
        if not session:
            return None
        try:
            opts = _AUTOPROXY_OPTIONS()
            opts.fAutoLogonIfChallenged = True
            if pac_url:
                opts.dwFlags |= _CONFIG_URL
                opts.lpszAutoConfigUrl = pac_url
            if auto_detect:
                opts.dwFlags |= _AUTO_DETECT
                opts.dwAutoDetectFlags = _DETECT_DHCP | _DETECT_DNS_A
            info = _PROXY_INFO()
            try:
                ok = wh.WinHttpGetProxyForUrl(session, url, ctypes.byref(opts), ctypes.byref(info))
            except Exception:  # noqa: BLE001
                return None
            if not ok:
                return None
            try:
                return _first_proxy(_wstr(info.lpszProxy))
            finally:
                _global_free(info.lpszProxy, info.lpszProxyBypass)
        finally:
            wh.WinHttpCloseHandle(session)

    def _global_free(*ptrs) -> None:
        """GlobalFree each raw WinHTTP pointer (a c_void_p field reads back as an int address, or None).
        NEVER pass a Python str here — freeing a str's address corrupts the heap (see the struct note)."""
        k32 = ctypes.WinDLL("kernel32")
        k32.GlobalFree.argtypes = [ctypes.c_void_p]
        k32.GlobalFree.restype = ctypes.c_void_p
        for value in ptrs:
            if value:
                try:
                    k32.GlobalFree(value)  # value is the real WinHTTP address (int), not a Python object
                except Exception:  # noqa: BLE001
                    pass

else:  # pragma: no cover - the packaged app is Windows-only
    def _win_system_proxy(url: str) -> str | None:
        return None


def os_system_proxy(url: str) -> str | None:
    """The OS's OWN system proxy for `url` (WinINET static + PAC/WPAD, else the registry), ignoring
    the ``HTTPS_PROXY`` env this module publishes. Reporting "detected" must never echo back the
    value we ourselves exported, or a manual override shows up as the machine's own setting."""
    win = _win_system_proxy(url)
    if win:
        return win
    return normalize_proxy(getproxies_registry().get("https")) if _IS_WINDOWS else None


def detect_system_proxy(url: str) -> str | None:
    """The system proxy for `url`: explicit HTTPS_PROXY env, else the OS's own configuration."""
    env = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if env:
        return normalize_proxy(env)
    return os_system_proxy(url)


class ProxyResolver:
    """Resolves the effective proxy for a URL: forced-direct > manual override > system proxy >
    direct; on-prem targets always bypassed."""

    def __init__(self, manual: str | None = None, bypass: list[str] | None = None) -> None:
        self.force_direct = is_direct(manual)
        self.manual = normalize_proxy(manual)
        self.bypass = list(DEFAULT_BYPASS) + [b for b in (bypass or []) if b]

    def for_url(self, url: str) -> str | None:
        host = urlparse(url).hostname
        if is_bypassed(host, self.bypass):
            return None
        if self.force_direct:
            return None
        return self.manual or detect_system_proxy(url)


_CLOUD_PROBE_URL = "https://common.cloud.hpe.com"


def apply_proxy_env(
    manual: str | None = None,
    *,
    cloud_url: str = _CLOUD_PROBE_URL,
    extra_bypass: list[str] | None = None,
) -> str | None:
    """Resolve the effective *cloud* proxy (manual override, else system proxy) and publish it to the
    process env — HTTPS_PROXY / HTTP_PROXY + NO_PROXY — so httpx (trust_env) and the launched browser
    go through it, and on-prem targets bypass it. Returns the proxy URL (or None = direct). Called at
    startup and whenever the operator saves a manual proxy; cheap enough but not per-request."""
    resolver = ProxyResolver(manual, list(extra_bypass or []))
    # Resolve from the override + the OS's own system proxy — NOT via detect_system_proxy, which
    # reads the HTTPS_PROXY env we manage here (that would echo a stale value back on every call).
    proxy = None if resolver.force_direct else (resolver.manual or os_system_proxy(cloud_url))
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        if proxy:
            os.environ[var] = proxy
        else:
            # CLEAR, don't just skip. Leaving a previously-published (or externally `setx`-ed) value
            # in place is why "remove the proxy" appeared to do nothing: the operator forced direct,
            # the app stopped setting the var, and the stale one kept routing every request.
            os.environ.pop(var, None)
    # NO_PROXY is consumed by third-party libraries, and httpx parses each entry as a URL: an IPv6
    # pattern like "fe80:*" is read as host "fe80" port "*" and raises InvalidURL for EVERY client
    # constructed in the process (proven: httpx.Client(trust_env=True) fails outright). Since
    # apply_proxy_env runs at startup, publishing one would break every cloud call in the product.
    # So export only colon-free entries; link-local bypass is enforced where it actually matters —
    # ProxyResolver.for_url (our own calls) and the browser's --proxy-bypass-list (Chrome syntax).
    no_proxy = ",".join(entry for entry in resolver.bypass if ":" not in entry)
    os.environ["NO_PROXY"] = no_proxy
    os.environ["no_proxy"] = no_proxy
    return proxy
