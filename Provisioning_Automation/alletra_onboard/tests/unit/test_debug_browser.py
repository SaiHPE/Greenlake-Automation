from alletra_onboard.adapters.browser.debug_browser import debug_browser_args, find_browser


def test_debug_browser_args_builds_cdp_flags():
    args = debug_browser_args("chrome.exe", 9222, r"C:\tmp\prof", "https://example.com")
    assert args[0] == "chrome.exe"
    assert "--remote-debugging-port=9222" in args
    assert r"--user-data-dir=C:\tmp\prof" in args
    assert args[-1] == "https://example.com"


def test_debug_browser_args_without_url():
    args = debug_browser_args("chrome.exe", 9333, "/tmp/p", None)
    assert "--remote-debugging-port=9333" in args
    assert not any(a.startswith("http") for a in args)


def test_find_browser_returns_str_or_none():
    # Must not raise regardless of what's installed on the test host.
    result = find_browser()
    assert result is None or isinstance(result, str)
