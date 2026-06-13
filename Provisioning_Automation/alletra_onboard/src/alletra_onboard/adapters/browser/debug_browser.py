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


def default_profile_dir() -> str:
    base = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "."
    return str(Path(base) / "alletra-cdp")


def debug_browser_args(exe: str, port: int, profile_dir: str, url: str | None) -> list[str]:
    """Build the launch argv (pure, so it's unit-testable without launching anything)."""
    args = [exe, f"--remote-debugging-port={port}", f"--user-data-dir={profile_dir}", "--no-first-run"]
    if url:
        args.append(url)
    return args


def launch_debug_browser(
    port: int = 9222, profile_dir: str | None = None, url: str | None = None
) -> dict[str, str]:
    """Launch a detached CDP browser. Returns {cdp_url, profile_dir, executable}."""
    exe = find_browser()
    if not exe:
        raise RuntimeError(
            "No Chrome/Edge found. Install Google Chrome, or pass an explicit path. "
            "Searched: " + ", ".join(c for c in _BROWSER_CANDIDATES if c)
        )
    profile = profile_dir or default_profile_dir()
    Path(profile).mkdir(parents=True, exist_ok=True)
    args = debug_browser_args(exe, port, profile, url)

    creationflags = 0
    if sys.platform == "win32":
        # Detach so the browser outlives the CLI process.
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen(args, creationflags=creationflags, close_fds=True)
    return {"cdp_url": f"http://localhost:{port}", "profile_dir": profile, "executable": exe}
