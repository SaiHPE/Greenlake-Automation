"""Launch a CDP-enabled Chrome/Edge for the operator to attach the wizards to.

Components B (cloudinit) and C (DSCC) attach over CDP to a browser the operator drives.
Doing that by hand (``Start-Process chrome --remote-debugging-port=...``) is fiddly and
easy to get wrong, so this gives one primitive — usable from the CLI today and the
frontend later — that finds the browser, starts it with remote debugging on a persistent
profile (so the GreenLake SSO session survives across steps), and returns the CDP URL.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import structlog

from alletra_onboard.domain.errors import BrowserError

_log = structlog.get_logger(__name__)

try:
    from playwright.async_api import Error as _PlaywrightError
    from playwright.async_api import TimeoutError as _PlaywrightTimeoutError
    from playwright.async_api import async_playwright

    PlaywrightError: type[Exception] = _PlaywrightError
    PlaywrightTimeoutError: type[Exception] = _PlaywrightTimeoutError
except ImportError:  # pragma: no cover - browser deps optional until B/C run.
    async_playwright = None

    class _FallbackPlaywrightError(Exception):
        pass

    class _FallbackPlaywrightTimeoutError(_FallbackPlaywrightError):
        pass

    PlaywrightError = _FallbackPlaywrightError
    PlaywrightTimeoutError = _FallbackPlaywrightTimeoutError


def ensure_localhost_no_proxy() -> None:
    """Add localhost to NO_PROXY so the CDP connection isn't routed through a lab proxy."""
    existing = os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or ""
    hosts = [h.strip() for h in existing.split(",") if h.strip()]
    for host in ("localhost", "127.0.0.1"):
        if host not in hosts:
            hosts.append(host)
    value = ",".join(hosts)
    os.environ["NO_PROXY"] = value
    os.environ["no_proxy"] = value


async def save_screenshot(artifact_dir: Path | None, page: Any, filename: str, label: str) -> None:
    """Capture a full-page diagnostic screenshot; a failed capture logs and never hides the original error."""
    if not artifact_dir or page is None:
        return
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(artifact_dir / filename), full_page=True)
    except (PlaywrightError, OSError) as exc:
        _log.debug("browser_screenshot_failed", label=label, error=str(exc))

# Chrome first (what the wizards were validated against), Edge as a fallback.
_BROWSER_CANDIDATES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


def find_browser() -> str | None:
    """Return the path to a Chromium-based browser, or None if none is found."""
    for candidate in _BROWSER_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    return shutil.which("chrome") or shutil.which("msedge") or shutil.which("chromium")


def channel_for_executable(exe: str | None) -> str | None:
    """Map a browser exe path to the Playwright launch *channel* ('chrome' / 'msedge'), or None
    (use Playwright's own bundled Chromium) when it's neither a branded Chrome nor Edge. Pure."""
    if not exe:
        return None
    name = os.path.basename(exe).lower()
    if "msedge" in name or "edge" in name:
        return "msedge"
    if "chrome" in name:
        return "chrome"
    return None


def preferred_channel() -> str | None:
    """The Playwright launch channel to drive an ALREADY-INSTALLED browser, so the tool needs no
    bundled/downloaded Chromium: 'chrome' or 'msedge' when one is found (Chrome preferred, Edge
    fallback), else None to fall back to Playwright's bundled Chromium.

    ``ALLETRA_BROWSER_CHANNEL`` overrides the auto-detection: 'chrome'/'msedge' force that channel;
    'chromium' forces the bundled build (None); anything else / unset = auto-detect. This is what
    lets the slim build run on a locked-down box that can't reach the Playwright browser CDN —
    almost every Windows host already has Edge (and often Chrome).
    """
    override = (os.environ.get("ALLETRA_BROWSER_CHANNEL") or "").strip().lower()
    if override in ("chrome", "msedge"):
        return override
    if override == "chromium":
        return None
    return channel_for_executable(find_browser())


def default_profile_dir() -> str:
    base = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "."
    return str(Path(base) / "alletra-cdp")


# Chrome ignores the HTTPS_PROXY env var (it uses the Windows system proxy), so behind a lab
# proxy the DSCC SSO token exchange hangs at "Authenticating…". We pass the proxy explicitly.
# localhost/127.0.0.1 must bypass it (the CDP endpoint + local API) and BOTH link-local families
# must bypass it — the array's cloudinit wizard answers on 169.254.x.x or on fe80:: (the Discovery
# Tool reports whichever it found), and a proxy has no route to an address that only means anything
# on this cable. Everything else — incl. data.cloud.hpe.com — goes via the proxy.
DEFAULT_PROXY_BYPASS = "localhost;127.0.0.1;169.254.*;[fe80::]/10;[::1]"


def resolve_browser_proxy(explicit: str | None) -> str | None:
    """An explicit proxy wins; otherwise fall back to the HTTPS_PROXY/HTTP_PROXY env var."""
    if explicit:
        return explicit
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        value = os.environ.get(var)
        if value:
            return value
    return None


def debug_browser_args(
    exe: str,
    port: int,
    profile_dir: str,
    url: str | None,
    proxy: str | None = None,
    proxy_bypass: str | None = None,
) -> list[str]:
    """Build the launch argv (pure, so it's unit-testable without launching anything)."""
    args = [exe, f"--remote-debugging-port={port}", f"--user-data-dir={profile_dir}", "--no-first-run"]
    if proxy:
        args.append(f"--proxy-server={proxy}")
        args.append(f"--proxy-bypass-list={proxy_bypass or DEFAULT_PROXY_BYPASS}")
    if url:
        args.append(url)
    return args


def launch_debug_browser(
    port: int = 9222,
    profile_dir: str | None = None,
    url: str | None = None,
    proxy: str | None = None,
    proxy_bypass: str | None = None,
    auto_proxy: bool = True,
) -> dict[str, str]:
    """Launch a detached CDP browser. Returns {cdp_url, profile_dir, executable, proxy}.

    proxy: explicit proxy URL. If None and auto_proxy, fall back to the HTTPS_PROXY env var
    (already set on the jump box) so the launched browser can reach DSCC through the lab proxy.
    """
    exe = find_browser()
    if not exe:
        raise BrowserError(
            "No Chrome/Edge found. Install Google Chrome, or pass an explicit path. "
            "Searched: " + ", ".join(c for c in _BROWSER_CANDIDATES if c)
        )
    if proxy is None and auto_proxy:
        proxy = resolve_browser_proxy(None)
    profile = profile_dir or default_profile_dir()
    Path(profile).mkdir(parents=True, exist_ok=True)
    args = debug_browser_args(exe, port, profile, url, proxy=proxy, proxy_bypass=proxy_bypass)

    creationflags = 0
    if sys.platform == "win32":
        # Detach so the browser outlives the CLI process.
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen(args, creationflags=creationflags, close_fds=True)
    return {"cdp_url": f"http://localhost:{port}", "profile_dir": profile, "executable": exe, "proxy": proxy or ""}
