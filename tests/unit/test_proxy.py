"""Proxy resolution — parsing, bypass, precedence, and env application (no live system proxy needed)."""

from __future__ import annotations

import os

from alletra_onboard.application.proxy import (
    ProxyResolver,
    _first_proxy,
    apply_proxy_env,
    is_bypassed,
    normalize_proxy,
)


def test_normalize_proxy():
    assert normalize_proxy("host:3128") == "http://host:3128"
    assert normalize_proxy("http://h:8080") == "http://h:8080"
    assert normalize_proxy("user:pass@h:8080") == "http://user:pass@h:8080"
    assert normalize_proxy("") is None
    assert normalize_proxy(None) is None


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
