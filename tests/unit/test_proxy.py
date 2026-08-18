"""Proxy resolution — parsing, bypass, precedence, and env application (no live system proxy needed)."""

from __future__ import annotations

import os

from alletra_onboard.application.platform.proxy import (
    DIRECT,
    ProxyResolver,
    _first_proxy,
    apply_proxy_env,
    is_bypassed,
    is_direct,
    normalize_proxy,
)


def test_normalize_proxy():
    assert normalize_proxy("host:3128") == "http://host:3128"
    assert normalize_proxy("http://h:8080") == "http://h:8080"
    assert normalize_proxy("user:pass@h:8080") == "http://user:pass@h:8080"
    assert normalize_proxy("") is None
    assert normalize_proxy(None) is None


def test_normalize_proxy_rejects_a_url_with_no_host():
    """REPORTED FROM THE UI: "In use: detected system proxy http://" with no way to remove it.

    Windows' registry yields exactly that when ProxyEnable is set with an empty ProxyServer entry
    (urllib's getproxies_registry prefixes the bare protocol -> 'http://'). The old passthrough
    ("://" in value -> return as-is) then published that host-less string into HTTPS_PROXY, which
    breaks every outbound call, and showed it to the operator as the detected system proxy.
    """
    assert normalize_proxy("http://") is None
    assert normalize_proxy("https://") is None
    assert normalize_proxy("://") is None
    assert normalize_proxy("   ") is None
    assert normalize_proxy("http:// ") is None


def test_direct_sentinel_is_recognised_and_normalises_to_no_proxy():
    for word in ("direct", "direct://", "DIRECT", "none", "off", "no", "-", "  direct  "):
        assert is_direct(word), word
        assert normalize_proxy(word) is None          # a decision, not a proxy address
    assert not is_direct("proxy.corp:3128")
    assert not is_direct("")                          # empty means AUTO-DETECT, not direct
    assert not is_direct(None)


def test_registry_garbage_never_reaches_the_env(monkeypatch):
    """The full path from a broken OS setting to the process env: 'http://' must resolve to direct."""
    from alletra_onboard.application.platform import proxy as mod

    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(mod, "_win_system_proxy", lambda url: None)
    monkeypatch.setattr(mod, "getproxies_registry", lambda: {"https": "http://"})
    monkeypatch.setattr(mod, "_IS_WINDOWS", True)
    assert mod.os_system_proxy("https://common.cloud.hpe.com") is None
    assert apply_proxy_env(None) is None
    assert "HTTPS_PROXY" not in os.environ


def test_first_proxy_parses_winhttp_strings():
    assert _first_proxy("http=p:8080;https=sec:8443") == "http://sec:8443"  # prefer https
    assert _first_proxy("proxy.corp:3128") == "http://proxy.corp:3128"
    assert _first_proxy("h1:1 h2:2") == "http://h1:1"                       # first of a space list
    assert _first_proxy("") is None
    assert _first_proxy(None) is None


def test_is_bypassed_exact_glob_and_cidr():
    bypass = ["localhost", "127.0.0.1", "169.254.*", "10.65.234.220", "10.0.0.0/8"]
    assert is_bypassed("localhost", bypass)
    assert is_bypassed("169.254.1.2", bypass)          # glob
    assert is_bypassed("10.65.234.220", bypass)        # exact IP
    assert is_bypassed("10.1.2.3", bypass)             # CIDR
    assert not is_bypassed("common.cloud.hpe.com", bypass)


def test_resolver_manual_wins_and_bypasses(monkeypatch):
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("https_proxy", raising=False)
    r = ProxyResolver(manual="mp:3128", bypass=["10.65.234.220"])
    assert r.for_url("https://common.cloud.hpe.com") == "http://mp:3128"
    assert r.for_url("https://10.65.234.220") is None     # on-prem array -> direct
    assert r.for_url("http://localhost:8765") is None
    assert r.for_url("https://169.254.1.2/cloudinit") is None


def test_resolver_uses_env_when_no_manual(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://envproxy:8080")
    assert ProxyResolver().for_url("https://common.cloud.hpe.com") == "http://envproxy:8080"


def test_apply_proxy_env_publishes_manual_and_bypass(monkeypatch):
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "NO_PROXY", "no_proxy"):
        monkeypatch.delenv(var, raising=False)
    proxy = apply_proxy_env("mp:3128", extra_bypass=["10.65.234.220"])
    assert proxy == "http://mp:3128"
    assert os.environ["HTTPS_PROXY"] == "http://mp:3128"
    assert "10.65.234.220" in os.environ["NO_PROXY"] and "169.254.*" in os.environ["NO_PROXY"]


def test_forced_direct_overrides_a_detected_proxy_and_clears_the_env(monkeypatch):
    """The operator's "there is no proxy here" must beat detection AND erase what we published.

    The second half is the other reason removal appeared not to work: apply_proxy_env only ever
    SET the vars, so a previously-published (or externally `setx`-ed) value kept routing traffic
    after the operator asked for a direct connection.
    """
    from alletra_onboard.application.platform import proxy as mod

    monkeypatch.setattr(mod, "_win_system_proxy", lambda url: "http://detected:8080")
    monkeypatch.setenv("HTTPS_PROXY", "http://stale:9999")
    monkeypatch.setenv("http_proxy", "http://stale:9999")

    r = ProxyResolver(manual=DIRECT)
    assert r.force_direct and r.for_url("https://common.cloud.hpe.com") is None

    assert apply_proxy_env(DIRECT) is None
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        assert var not in os.environ, f"{var} survived a forced-direct apply"
    # ...while an empty override still means AUTO-DETECT, which finds the system proxy again.
    assert apply_proxy_env(None) == "http://detected:8080"
    assert os.environ["HTTPS_PROXY"] == "http://detected:8080"


def test_status_reporting_never_echoes_the_override_as_detected(monkeypatch):
    """`detected` must be the machine's setting; os_system_proxy ignores the env we publish."""
    from alletra_onboard.application.platform import proxy as mod

    monkeypatch.setattr(mod, "_win_system_proxy", lambda url: None)
    monkeypatch.setattr(mod, "getproxies_registry", lambda: {})
    monkeypatch.setenv("HTTPS_PROXY", "http://our-own-override:3128")
    assert mod.os_system_proxy("https://common.cloud.hpe.com") is None       # not the echo
    assert mod.detect_system_proxy("https://common.cloud.hpe.com") == "http://our-own-override:3128"


# --------------- regression: v0.9.0 heap-corruption crash on a box WITH a system proxy ---------------

def test_winhttp_out_strings_are_raw_pointers_not_lpwstr():
    """The WinHTTP out-string struct fields MUST be raw ``c_void_p``, never ``LPWSTR``.

    As ``LPWSTR`` they auto-convert to a Python ``str`` on access, so the real GlobalAlloc'd pointer is
    lost; ``GlobalFree`` then runs on a pointer INTO a Python object and corrupts the process heap
    (STATUS_HEAP_CORRUPTION / 0xC0000374). This only triggers on a machine that actually HAS a system
    proxy (so the strings are non-null) — which is why every unit + CI selftest passed while the
    packaged app crashed at launch on the proxied customer box. Deterministic guard against a revert.
    """
    import ctypes

    from alletra_onboard.application.platform import proxy

    if not proxy._IS_WINDOWS:  # the structs only exist on the packaged Windows target
        return
    ie = dict(proxy._IE_PROXY_CONFIG._fields_)
    pi = dict(proxy._PROXY_INFO._fields_)
    for field in ("lpszAutoConfigUrl", "lpszProxy", "lpszProxyBypass"):
        assert ie[field] is ctypes.c_void_p, f"_IE_PROXY_CONFIG.{field} must be c_void_p (raw pointer)"
    for field in ("lpszProxy", "lpszProxyBypass"):
        assert pi[field] is ctypes.c_void_p, f"_PROXY_INFO.{field} must be c_void_p (raw pointer)"


def test_win_system_proxy_reads_then_frees_a_real_pointer(monkeypatch):
    """End-to-end: read the WinHTTP string via a raw pointer and GlobalFree that exact pointer — with a
    genuine GlobalAlloc'd wide string, so a regression to the bad free would corrupt the heap here."""
    import ctypes

    from alletra_onboard.application.platform import proxy

    if not proxy._IS_WINDOWS:
        return
    k32 = ctypes.WinDLL("kernel32")
    k32.GlobalAlloc.restype = ctypes.c_void_p
    k32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]

    def galloc_wstr(s: str) -> int:
        raw = ctypes.create_unicode_buffer(s)
        ptr = k32.GlobalAlloc(0x0040, ctypes.sizeof(raw))  # GPTR = fixed + zero-init
        ctypes.memmove(ptr, raw, ctypes.sizeof(raw))
        return ptr

    class FakeWH:
        def WinHttpGetIEProxyConfigForCurrentUser(self, ref):
            cfg = ctypes.cast(ref, ctypes.POINTER(proxy._IE_PROXY_CONFIG)).contents
            cfg.fAutoDetect = False
            cfg.lpszAutoConfigUrl = None
            cfg.lpszProxy = galloc_wstr("1.2.3.4:8080")
            cfg.lpszProxyBypass = None
            return 1

    monkeypatch.setattr(proxy, "_winhttp", lambda: FakeWH())
    assert proxy._win_system_proxy("https://common.cloud.hpe.com") == "http://1.2.3.4:8080"
