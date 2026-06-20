"""Launch the HPE Storage Discovery Tool (native Windows app) for the operator.

The Cloud Connectivity step needs the array's link-local ``https://169.254.x.x/cloudinit`` URL,
which the operator reads off the Discovery Tool. We ship the tool *inside* the package (and the
packaged .exe) so the operator never has to find/download it: the bundled copy is launched after
its SHA256 is verified. If the bundle is missing we fall back to searching the Desktop.

Resolution order: ``DISCOVERY_TOOL_PATH`` (explicit) → the verified bundled copy → the Desktop(s).
``DISCOVERY_TOOL_DIR`` adds a Desktop search location; ``DISCOVERY_TOOL_BUNDLED_DIR`` overrides
where the bundled copy lives (also how the frozen .exe points at its extracted data dir).
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

DISCOVERY_GLOB = "*Discovery Tool*.exe"


def _bundled_dir() -> Path:
    """Where the bundled Discovery Tool ships: alongside the package, or inside the frozen .exe."""
    override = os.environ.get("DISCOVERY_TOOL_BUNDLED_DIR")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):  # PyInstaller: data lands under sys._MEIPASS
        return Path(getattr(sys, "_MEIPASS", ".")) / "tools" / "discovery"
    return Path(__file__).resolve().parents[4] / "tools" / "discovery"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify(exe: Path) -> bool:
    """True if the sidecar ``<exe>.sha256`` matches (or there is no sidecar to check against)."""
    sidecar = exe.with_name(exe.name + ".sha256")
    if not sidecar.is_file():
        return True  # nothing to verify against — allow it
    try:
        expected = sidecar.read_text(encoding="utf-8").split()[0].strip().lower()
    except OSError:
        return False
    return bool(expected) and _sha256(exe).lower() == expected


def _bundled_tool() -> Path | None:
    directory = _bundled_dir()
    if not directory.is_dir():
        return None
    exes = sorted(p for p in directory.glob(DISCOVERY_GLOB) if p.suffix.lower() == ".exe")
    for exe in reversed(exes):  # highest version first; only return a verified one
        if _verify(exe):
            return exe
    return None


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
    """Locate the Discovery Tool: explicit path → verified bundled copy → newest match on a Desktop."""
    exact = os.environ.get("DISCOVERY_TOOL_PATH")
    if exact and Path(exact).is_file():
        return Path(exact)
    bundled = _bundled_tool()
    if bundled is not None:
        return bundled
    for directory in _search_dirs():
        if not directory.is_dir():
            continue
        exes = sorted(p for p in directory.glob(DISCOVERY_GLOB) if p.suffix.lower() == ".exe")
        if exes:
            return exes[-1]
    return None


def launch_discovery_tool() -> dict:
    """Find and launch the Discovery Tool. Returns a structured result (never raises)."""
    searched = [str(_bundled_dir())] + [str(directory) for directory in _search_dirs()]
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
            "error": "Could not find a verified 'HPE Discovery Tool*.exe'. It ships with the app; "
            "if missing, put it on the Desktop or set DISCOVERY_TOOL_PATH in .env.",
        }
    try:
        os.startfile(str(exe))  # type: ignore[attr-defined]  # noqa: S606 - open like a double-click
    except OSError as exc:
        return {"launched": False, "path": str(exe), "searched": searched, "error": f"Found it but could not launch: {exc}"}
    return {"launched": True, "path": str(exe), "searched": searched, "error": None}
