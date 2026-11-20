"""Open a new local terminal window running a command (SPEC-019 R5, STANDARD L4)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def launch_terminal(argv: list[str]) -> None:
    """Open a new terminal window with `argv` in it; no password is passed (R5)."""
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", "", "cmd", "/k", *argv])
        return
    if sys.platform == "darwin":
        script = " ".join(argv).replace('"', '\\"')
        subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{script}"'])
        return
    term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal")
    if term is None:
        raise RuntimeError("no terminal program found")
    subprocess.Popen([term, "--", *argv])
