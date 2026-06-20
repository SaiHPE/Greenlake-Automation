"""Frozen entry point for the packaged .exe — boots the operator web app.

PyInstaller needs a real script (not the ``onboard`` console-script). This mirrors ``onboard ui``:
it starts uvicorn in-process and opens the browser. When frozen it runs from the .exe's own folder
so local state (.env, state DB, artifacts) lives next to the executable.

Two build flavours share this script (see alletra_onboard.spec):
  * bundled   — Chromium is shipped inside the .exe; the runtime hook points Playwright at it.
  * slim      — no Chromium; ``ensure_chromium()`` downloads it on first run via the bundled
                Node driver (the same proxy the tool already uses for GreenLake/DSCC).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def ensure_chromium() -> None:
    """Make sure a Chromium is available. No-op for the bundled build or once downloaded."""
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as pw:
            executable = pw.chromium.executable_path
        if executable and os.path.exists(executable):
            return  # bundled, or already downloaded to the user cache
    except Exception:  # noqa: BLE001 - fall through and try to install
        pass

    print("First run: downloading the Chromium browser (~150 MB, one time)…", flush=True)
    try:
        import subprocess

        from playwright._impl._driver import compute_driver_executable, get_driver_env

        node, cli = compute_driver_executable()
        subprocess.run([node, cli, "install", "chromium"], env=get_driver_env(), check=True)
        print("Browser ready.", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(
            f"Could not download Chromium automatically ({exc}).\n"
            "If this site blocks the Playwright browser CDN, use the offline build "
            "(alletra-onboard-offline-win64.zip), which ships Chromium inside.",
            flush=True,
        )


def selftest() -> int:
    """Launch Chromium headless to prove Playwright works inside the frozen .exe."""
    import asyncio

    if getattr(sys, "frozen", False):
        ensure_chromium()

    from playwright.async_api import async_playwright

    async def go() -> str:
        async with async_playwright() as pw:
            # channel="chromium" uses the FULL Chromium binary (what production launches headed),
            # in new-headless mode so the selftest needs no desktop and no headless-shell.
            browser = await pw.chromium.launch(headless=True, channel="chromium")
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
