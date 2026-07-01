"""Frozen entry point for the packaged .exe — boots the operator web app.

PyInstaller needs a real script (not the ``onboard`` console-script). This mirrors ``onboard ui``:
it starts uvicorn in-process and opens the browser. When frozen it runs from the .exe's own folder
so local state (.env, state DB, artifacts) lives next to the executable.

Browser strategy (the wizards + selftest): prefer an already-installed Chrome/Edge via Playwright's
``channel`` (no download), and only fall back to a bundled/downloaded Chromium when no branded
browser is present. Two build flavours share this script (see alletra_onboard.spec):
  * bundled — Chromium is shipped inside the .exe; the runtime hook points Playwright at it (used
              when no Chrome/Edge is installed).
  * slim    — no Chromium; if a Chrome/Edge is installed it is driven directly, else
              ``ensure_chromium()`` downloads Chromium on first run via the bundled Node driver
              (needs the Playwright CDN — a locked-down box should use the offline build).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _place_vcredist(executable: str | None) -> None:
    """Copy the bundled MSVC runtime DLLs next to chrome.exe so Chromium runs even on a box without
    the VC++ Redistributable installed. No-op when not frozen, or already present."""
    if not (getattr(sys, "frozen", False) and executable):
        return
    source = os.path.join(sys._MEIPASS, "vcredist")  # type: ignore[attr-defined]
    if not os.path.isdir(source):
        return
    import shutil

    target_dir = os.path.dirname(executable)  # ...\chrome-win64
    for dll in os.listdir(source):
        target = os.path.join(target_dir, dll)
        if not os.path.exists(target):
            try:
                shutil.copy2(os.path.join(source, dll), target)
            except OSError:
                pass


def ensure_chromium() -> None:
    """Make sure a browser is available for the wizards + selftest.

    Prefer an already-installed Chrome/Edge (channel mode) — nothing to download or place. Only a
    slim build on a box with NO branded browser falls through to downloading Playwright's Chromium
    (which needs the CDN); a locked-down box should use the offline build instead.
    """
    from alletra_onboard.adapters.browser.debug_browser import preferred_channel

    if preferred_channel():
        return  # an installed Chrome/Edge will be driven directly

    from playwright.sync_api import sync_playwright

    def _executable() -> str | None:
        try:
            with sync_playwright() as pw:
                return pw.chromium.executable_path
        except Exception:  # noqa: BLE001
            return None

    executable = _executable()
    if not (executable and os.path.exists(executable)):
        print("First run: downloading the Chromium browser (~150 MB, one time)…", flush=True)
        try:
            import subprocess

            from playwright._impl._driver import compute_driver_executable, get_driver_env

            node, cli = compute_driver_executable()
            subprocess.run([node, cli, "install", "chromium"], env=get_driver_env(), check=True)
            print("Browser ready.", flush=True)
            executable = _executable()
        except Exception as exc:  # noqa: BLE001
            print(
                f"Could not download Chromium automatically ({exc}).\n"
                "If this site blocks the Playwright browser CDN, use the offline build "
                "(alletra-onboard-offline-win64.zip), which ships Chromium inside.",
                flush=True,
            )
    _place_vcredist(executable)


def selftest() -> int:
    """Launch Chromium headless to prove Playwright works inside the frozen .exe."""
    import asyncio

    if getattr(sys, "frozen", False):
        ensure_chromium()

    from playwright.async_api import async_playwright

    async def go() -> str:
        from alletra_onboard.adapters.browser.debug_browser import preferred_channel

        async with async_playwright() as pw:
            # Drive the installed Chrome/Edge if present (what production now prefers); otherwise
            # channel="chromium" uses the FULL bundled Chromium. Headless new-mode either way, so
            # the selftest needs no desktop and no headless-shell.
            browser = await pw.chromium.launch(headless=True, channel=preferred_channel() or "chromium")
            try:
                page = await browser.new_page()
                await page.goto("about:blank")
                return browser.version
            finally:
                await browser.close()

    try:
        version = asyncio.run(go())
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        print(f"SELFTEST FAIL: {type(exc).__name__}: {message}")
        if "side-by-side" in message.lower() or "0xc000007b" in message.lower():
            print(
                "Hint: Chromium can't start — install the Microsoft Visual C++ Redistributable "
                "(x64) from https://aka.ms/vs/17/release/vc_redist.x64.exe, then retry."
            )
        return 1
    print(f"SELFTEST OK: launched Chromium {version}")
    return 0


def _force_utf8() -> None:
    # The frozen console is cp1252; Playwright error text (box-drawing chars) crashes prints.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            pass


def main() -> None:
    _force_utf8()
    if "selftest" in sys.argv[1:]:
        sys.exit(selftest())

    if getattr(sys, "frozen", False):
        # Keep .env / state / artifacts beside the .exe, not in System32 (double-click cwd).
        os.chdir(Path(sys.executable).resolve().parent)
        ensure_chromium()

    import uvicorn

    from alletra_onboard.api.app import app as fastapi_app
    from alletra_onboard.config import load_settings

    settings = load_settings()
    address = f"http://{settings.api_host}:{settings.api_port}"
    print(f"Alletra Onboard — serving the web app at {address}")
    print("Leave this window open. Close it (or press Ctrl+C) to stop.")

    import threading
    import webbrowser

    threading.Timer(1.5, lambda: webbrowser.open(address)).start()
    uvicorn.run(fastapi_app, host=settings.api_host, port=settings.api_port, log_level="info")


if __name__ == "__main__":
    main()
