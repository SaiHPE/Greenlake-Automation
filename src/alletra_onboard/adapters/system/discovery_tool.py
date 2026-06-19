"""Launch the HPE Storage Discovery Tool (native Windows app) for the operator.

The Cloud Connectivity step needs the array's link-local ``https://169.254.x.x/cloudinit`` URL,
which the operator reads off the Discovery Tool. The tool is a standalone ``.exe`` dropped on the
Desktop, so the web app (which runs ON the jump box) can find and launch it like a double-click —
the UI offers a one-click "Open Discovery Tool" button instead of asking the operator to alt-tab
and hunt for it.

The executable name carries a version (``HPE Discovery Tool-1.1.1.33.exe``), so we glob rather
than hardcode. ``DISCOVERY_TOOL_PATH`` (full path) or ``DISCOVERY_TOOL_DIR`` (a folder to search)
override the Desktop search when the tool lives elsewhere.
"""

from __future__ import annotations

import os
from pathlib import Path

DISCOVERY_GLOB = "*Discovery Tool*.exe"


def _search_dirs() -> list[Path]:
    """Desktop locations to scan, in priority order, de-duplicated."""
    candidates: list[Path] = []
    override_dir = os.environ.get("DISCOVERY_TOOL_DIR")
    if override_dir:
        candidates.append(Path(override_dir))
    for env in ("USERPROFILE", "PUBLIC"):
        base = os.environ.get(env)
        if base:
            candidates.append(Path(base) / "Desktop")
    candidates.append(Path(r"C:\Users\Administrator\Desktop"))

    seen: set[str] = set()
    unique: list[Path] = []
    for directory in candidates:
        key = str(directory).lower()
        if key not in seen:
            seen.add(key)
            unique.append(directory)
    return unique


def find_discovery_tool() -> Path | None:
    """Locate the Discovery Tool .exe — explicit path wins, else newest match on a Desktop."""
    exact = os.environ.get("DISCOVERY_TOOL_PATH")
    if exact and Path(exact).is_file():
        return Path(exact)
    for directory in _search_dirs():
        if not directory.is_dir():
            continue
        exes = sorted(p for p in directory.glob(DISCOVERY_GLOB) if p.suffix.lower() == ".exe")
        if exes:
            return exes[-1]  # highest version by name sort
    return None


def launch_discovery_tool() -> dict:
    """Find and launch the Discovery Tool. Returns a structured result (never raises)."""
    searched = [str(directory) for directory in _search_dirs()]
    if os.name != "nt":
        return {
            "launched": False,
            "path": None,
            "searched": searched,
            "error": "Launching the Discovery Tool is only supported on Windows (run this on the jump box).",
        }
    exe = find_discovery_tool()
    if exe is None:
        return {
            "launched": False,
            "path": None,
            "searched": searched,
            "error": "Could not find 'HPE Discovery Tool*.exe'. Put it on the Desktop, or set "
            "DISCOVERY_TOOL_PATH in .env to its full path.",
        }
    try:
        os.startfile(str(exe))  # type: ignore[attr-defined]  # noqa: S606 - open like a double-click
    except OSError as exc:
        return {"launched": False, "path": str(exe), "searched": searched, "error": f"Found it but could not launch: {exc}"}
    return {"launched": True, "path": str(exe), "searched": searched, "error": None}
