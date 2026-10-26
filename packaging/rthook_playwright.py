"""PyInstaller runtime hook: pin where Playwright looks for browsers.

Set PLAYWRIGHT_BROWSERS_PATH explicitly for BOTH builds — if it is left unset, a frozen app
resolves browsers to a path *inside* the bundle (…/playwright/driver/.local-browsers), which is
wrong for the slim build (read-only, and not where first-run install lands).

  * offline build — Chromium is bundled under <bundle>/ms-playwright; point there.
  * slim build    — point at the per-user cache %LOCALAPPDATA%\\ms-playwright, where
                    app_main.ensure_chromium() downloads it on first run and it persists.

setdefault so an explicit override still wins.
"""

import os
import sys

if hasattr(sys, "_MEIPASS"):
    _bundled = os.path.join(sys._MEIPASS, "ms-playwright")
    if os.path.isdir(_bundled):
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", _bundled)
    else:
        _local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.join(_local, "ms-playwright"))
