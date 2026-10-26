"""SPEC-019 R3/R5: the read-only console prompt and the Open terminal launcher.

The prompt runs one command through the array's read-only SSH client (ADR 0001 allowlist) with the
credential the run already holds (ADR 0013). It is recorded like any read the tool makes. Nothing here
can reach a write path.
"""

from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array.cli_client import ArrayCliError, refusal
from alletra_onboard.application.provisioning.clients import make_array_cli
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.domain.shared import EndpointCreds

REFUSED = ("The console runs the tool's read-only commands (show…, checkhealth). Changes go through a plan "
           "you approve, or through your own SSH session — Open terminal.")
_SAFE_HOST = re.compile(r"[A-Za-z0-9.:-]{1,253}")
_SAFE_USER = re.compile(r"[A-Za-z0-9._-]{1,64}")


class ConsoleService:
    def __init__(self, coordinator: RunCoordinator, *, cli_factory: Callable = make_array_cli,
                 launcher: Callable[[list[str]], None] | None = None) -> None:
        self.coord = coordinator
        self.cli_factory = cli_factory
        self.launcher = launcher or _launch

    def targets(self, run_id: str) -> dict[str, str]:
        """target key -> 'user@host' for the arrays this run may read."""
        out = {}
        cred = self.coord.array_credential(run_id)
        if cred.available:
            out["array"] = f"{cred.username}@{cred.host}"
        peer = self._peer(run_id)
        if peer is not None:
            out["peer"] = f"{peer.username}@{peer.host}"
        return out

    def _peer(self, run_id: str) -> EndpointCreds | None:
        try:
            intent = self.coord.get_provisioning_intent(run_id)
        except Exception:  # noqa: BLE001 - a run without the provisioning tabs has no peer
            return None
        rep = getattr(intent, "replication", None)
        return rep.peer if rep is not None else None

    def _creds(self, run_id: str, target: str) -> EndpointCreds:
        if target == "peer":
            peer = self._peer(run_id)
            if peer is None:
                raise StepPreconditionError("This run has no Replication tab, so there is no peer array to read.")
            return peer
        cred = self.coord.array_credential(run_id)
        if not cred.available or cred.secret is None:
            raise StepPreconditionError("This run holds no array credential (Provisioning tab or DSCC setup).")
        return EndpointCreds(host=cred.host, username=cred.username, password=cred.secret)

    async def run(self, run_id: str, command: str, target: str = "array") -> dict:
        self.coord.get_run(run_id)
        command = " ".join(command.split())
        creds = self._creds(run_id, target)
        with self.coord.recording(run_id):
            why = refusal(command)
            if why:
                command_log.record(target=creds.host, transport="ssh", command=command, started=time.monotonic(),
                                   ok=False, result=f"{why} (console)")
                return {"ok": False, "refused": True, "output": REFUSED, "target": creds.host}

            def read() -> str:
                with self.cli_factory(creds) as cli:
                    return cli.run(command)

            try:
                text = await asyncio.to_thread(read)
            except ArrayCliError as exc:
                return {"ok": False, "refused": False, "output": str(exc), "target": creds.host}
        return {"ok": True, "refused": False, "output": text, "target": creds.host}

    def open_terminal(self, run_id: str, target: str = "array") -> dict:
        creds = self._creds(run_id, target)
        line = f"ssh {creds.username}@{creds.host}"
        # both go onto a shell command line in a new window
        if not (_SAFE_HOST.fullmatch(creds.host) and _SAFE_USER.fullmatch(creds.username)):
            return {"launched": False, "command": line, "error": "The sheet's host or account name has characters a terminal "
                                                                "command line cannot take safely; open SSH yourself."}
        try:
            self.launcher(["ssh", f"{creds.username}@{creds.host}"])
        except Exception as exc:  # noqa: BLE001
            return {"launched": False, "command": line, "error": f"Could not open a terminal ({exc}). Run: {line}"}
        return {"launched": True, "command": line, "error": None}


def console_text(entries: list[dict]) -> str:
    """R4's line form, for Download .txt and the runner's evidence folder."""
    lines = []
    for e in entries:
        at = (e.get("at") or "")[11:19]
        lines.append(f"{at}  {e.get('target', '')} ({e.get('transport', '')})  {e.get('command', '')}  "
                     f"{e.get('duration_s', 0)}s  {e.get('result', '')}")
        out = (e.get("output") or "").rstrip()
        if out:
            lines.extend("    " + line for line in out.splitlines())
    return "\n".join(lines) + "\n"


def _launch(argv: list[str]) -> None:
    """A new terminal window with `argv` in it; no password is passed (R5)."""
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
