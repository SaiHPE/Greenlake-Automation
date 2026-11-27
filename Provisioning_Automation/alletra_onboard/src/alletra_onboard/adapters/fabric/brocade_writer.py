"""Write-scoped SSH client for opt-in Brocade Fabric OS SAN zoning apply (ADR 0033, following ADR 0025).

The read-only `BrocadeClient` (`adapters/fabric/brocade_client.py`) keeps `ALLOWED_READ` and zero
write verbs. This separate subclass adds `write()` for exactly five prompt-free FOS v9.2.0b1 forms
(CLI help captured on rack13 switches 2026-11-27; live-verified on rack13 switches 2026-11-27 via `lab/zoning_apply_lab.py` (21/0)),
scoped to the exact aliases, zones and active cfg of one approved `ZoningPlanObjects`:

    alicreate "<alias>","<wwpn>"
    zonecreate "<zone>","<m1>;<m2>"
    cfgadd "<cfg>","<z1>[;<z2>...]"
    cfgenable "<cfg>" -f
    cfgtransabort

`read()` keeps `ALLOWED_READ`, so pre-flight `cfgtransshow` / `cfgshow` and post-apply `cfgshow`
read-back run over the same session. Zero stdin writes and zero PTY allocation.
"""

from __future__ import annotations

import time
from typing import Any

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.domain.approval import Approval, require_approval
from alletra_onboard.domain.errors import BrocadeError, BrocadeRefused
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.shared import Fabric
from alletra_onboard.domain.zoning_commands import (
    BROCADE_WRITE_FORMS,
    zoning_object_refusal,
    zoning_write_refusal,
)

__all__ = [
    "BROCADE_WRITE_FORMS",
    "BrocadeZoneWriter",
    "zoning_object_refusal",
    "zoning_write_refusal",
]

_CFGENABLE_ERROR_MARKERS: tuple[str, ...] = (
    "error:",
    "usage:",
    "invalid ",
    "failed",
    "not found",
    "does not exist",
    "not permitted",
    "permission denied",
    "cannot ",
    "unable to ",
    "do you want to",
    "transaction",
)

_ABORT_ERROR_MARKERS: tuple[str, ...] = (
    "error:",
    "usage:",
    "invalid ",
    "failed",
    "not permitted",
    "permission denied",
    "cannot ",
    "unable to ",
)


def _strip_cfgenable_cfg(command: str, line: str) -> str:
    """Remove only the quoted cfg name from `cfgenable` output before scanning for error words."""
    if not command.startswith('cfgenable "'):
        return line
    cfg = command.split('"', 2)[1]
    return line.replace(f'"{cfg}"', '""') if cfg else line


def _fos_write_error(command: str, output: str) -> str | None:
    """Detect FOS write errors even when the switch returns exit status 0.

    `alicreate`, `zonecreate` and `cfgadd` print nothing on success in FOS, so any non-empty output
    is treated as a failure. `cfgenable -f` prints progress lines (e.g. "Updating flash ...") and
    is verified by strict post-apply `cfgshow` Effective read-back. `cfgtransabort` may print
    "There is no outstanding zoning transaction" or "Transaction aborted" and is confirmed via
    `cfgtransshow`.
    """
    lines = [raw.strip() for raw in output.splitlines() if raw.strip()]
    if not lines:
        return None
    if command.startswith(("alicreate ", "zonecreate ", "cfgadd ")):
        return lines[0]
    markers = _ABORT_ERROR_MARKERS if command == "cfgtransabort" else _CFGENABLE_ERROR_MARKERS
    for line in lines:
        low = _strip_cfgenable_cfg(command, line).lower()
        if any(marker in low for marker in markers):
            return line
    return None


class BrocadeZoneWriter(BrocadeClient):
    """Reads like `BrocadeClient`; writes only the five exact FOS forms above on the approved plan's objects."""

    def __init__(
        self,
        approval: Approval,
        fabric: Fabric,
        objects: ZoningPlanObjects,
        **kwargs: Any,
    ) -> None:
        live = require_approval(approval)
        creds = live.switch_creds_for("zoning", fabric)
        super().__init__(creds.host, creds.username, creds.password.get_secret_value(), **kwargs)
        self._approval = live
        self._objects = objects

    def write_refusal(self, command: str) -> str | None:
        """Why `write` refuses `command` on this client, or None when it may run."""
        return zoning_write_refusal(command) or zoning_object_refusal(command, self._objects)

    def write(self, command: str) -> str:
        started = time.monotonic()
        if self._approval.spent:
            why = "refused: this approval has already been used"
            command_log.record(target=self.host, transport="fos", command=command, started=started, ok=False,
                               result=why, secrets=[self.password], write=True)
            self._approval.require_live()
        if why := self.write_refusal(command):
            command_log.record(target=self.host, transport="fos", command=command, started=started, ok=False,
                               result=why, secrets=[self.password], write=True)
            raise BrocadeRefused(why)
        try:
            status, out = self._exec_status(command)
        except BrocadeError as exc:
            command_log.record(target=self.host, transport="fos", command=command, started=started, ok=False,
                               result=str(exc), secrets=[self.password], write=True)
            raise
        err = _fos_write_error(command, out)
        if status != 0 or err is not None:
            detail = err or f"exit {status}"
            command_log.record(target=self.host, transport="fos", command=command, started=started, ok=False,
                               result=detail, output=out, secrets=[self.password], write=True)
            raise BrocadeError(f"'{command}' failed on {self.host}: {detail}")
        command_log.record(target=self.host, transport="fos", command=command, started=started, ok=True,
                           result=f"exit {status}", output=out, secrets=[self.password], write=True)
        return out

    def __enter__(self) -> BrocadeZoneWriter:
        self.connect()
        return self
