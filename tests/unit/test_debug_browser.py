from alletra_onboard.adapters.browser.debug_browser import (
    DEFAULT_PROXY_BYPASS,
    channel_for_executable,
    debug_browser_args,
    find_browser,
    preferred_channel,
    resolve_browser_proxy,
)


def test_debug_browser_args_builds_cdp_flags():
    args = debug_browser_args("chrome.exe", 9222, r"C:\tmp\prof", "https://example.com")
    assert args[0] == "chrome.exe"
    assert "--remote-debugging-port=9222" in args
    assert r"--user-data-dir=C:\tmp\prof" in args
    assert args[-1] == "https://example.com"
    # no proxy unless asked
    assert not any(a.startswith("--proxy-server") for a in args)


def test_debug_browser_args_without_url():
    args = debug_browser_args("chrome.exe", 9333, "/tmp/p", None)
    assert "--remote-debugging-port=9333" in args
    assert not any(a.startswith("http") for a in args)


def test_debug_browser_args_with_proxy_adds_bypass():
    args = debug_browser_args("chrome.exe", 9222, "/tmp/p", "https://x", proxy="http://proxy:8080")
    assert "--proxy-server=http://proxy:8080" in args
    assert f"--proxy-bypass-list={DEFAULT_PROXY_BYPASS}" in args
    # the URL still comes last
    assert args[-1] == "https://x"


def test_resolve_browser_proxy_prefers_explicit_then_env(monkeypatch):
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    assert resolve_browser_proxy(None) is None
    assert resolve_browser_proxy("http://explicit:3128") == "http://explicit:3128"
    monkeypatch.setenv("HTTPS_PROXY", "http://env:8080")
    assert resolve_browser_proxy(None) == "http://env:8080"


def test_find_browser_returns_str_or_none():
    # Must not raise regardless of what's installed on the test host.
    result = find_browser()
    assert result is None or isinstance(result, str)


def test_channel_for_executable_maps_branded_browsers():
    assert channel_for_executable(r"C:\Program Files\Google\Chrome\Application\chrome.exe") == "chrome"
    assert channel_for_executable(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") == "msedge"
    assert channel_for_executable("/usr/bin/google-chrome") == "chrome"
    assert channel_for_executable("/usr/lib/chromium/chromium") is None  # bare chromium -> bundled
    assert channel_for_executable(None) is None


def test_preferred_channel_env_override_wins(monkeypatch):
    monkeypatch.setenv("ALLETRA_BROWSER_CHANNEL", "msedge")
    assert preferred_channel() == "msedge"
    monkeypatch.setenv("ALLETRA_BROWSER_CHANNEL", "chrome")
    assert preferred_channel() == "chrome"
    # 'chromium' forces the bundled build (None), regardless of what's installed
    monkeypatch.setenv("ALLETRA_BROWSER_CHANNEL", "chromium")
    assert preferred_channel() is None


def test_preferred_channel_autodetect_is_str_or_none(monkeypatch):
    monkeypatch.delenv("ALLETRA_BROWSER_CHANNEL", raising=False)
    result = preferred_channel()
    assert result in (None, "chrome", "msedge")
