"""The write-scoped SSH client for Remote Copy links and targets (ADR 0015, BL-41).

Layers 1–2 of replication (RCIP addresses, the Remote Copy service, targets and links) have no WSAPI
call, so they go over SSH, and only through this client. It is a separate class from the read-only
`ArrayCliClient` (ADR 0001), which stays the default for every read. `write()` runs exactly the
commands below, each checked for its whole shape, not only its first word; `run()` keeps the read
allowlist so the client can read back what it changed. The service constructs it only inside the
apply of a plan the operator approved.

Command forms are the arrays' own (`help controlport`, `help creatercopytarget`, … captured
2026-11-03 on rack13-ARCUS OS 10.5.55 and PRIMERA630R11U22 OS 4.6.20). `controlport` asks
"Are you sure…?" without `-f`, and an SSH exec has no terminal to answer it, so `-f` is required.
Nothing here can remove a group, stop Remote Copy, change a port's role, or touch a non-RCIP port.
"""

from __future__ import annotations

import ipaddress
import re
import time

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array.cli_client import (
    _FORBIDDEN_CHARS,
    ArrayCliClient,
    ArrayCliError,
)

_NSP = r"\d{1,2}:\d{1,2}:\d{1,2}"
_IPV4 = r"(?:\d{1,3}\.){3}\d{1,3}"
# Target names: the array's own name rules are wider, the tool names targets after the other array.
_TARGET = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,30}"
_LINK = rf"{_NSP}:{_IPV4}"

RC_WRITE_FORMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("startrcopy", re.compile(r"^startrcopy$")),
    ("controlport rcip addr", re.compile(rf"^controlport rcip addr -f (?P<ip>{_IPV4}) (?P<mask>{_IPV4}|\d{{1,2}}) {_NSP}$")),
    ("controlport rcip gw", re.compile(rf"^controlport rcip gw -f (?P<ip>{_IPV4}) {_NSP}$")),
    ("controlport rcip ping", re.compile(rf"^controlport rcip ping (?:-c (?:[1-9]|10) )?(?P<ip>{_IPV4}) {_NSP}$")),
    ("creatercopytarget", re.compile(rf"^creatercopytarget {_TARGET} IP {_LINK}(?: {_LINK})*$")),
    ("admitrcopylink", re.compile(rf"^admitrcopylink {_TARGET} {_LINK}(?: {_LINK})*$")),
    ("dismissrcopylink", re.compile(rf"^dismissrcopylink {_TARGET} {_LINK}(?: {_LINK})*$")),
    ("removercopytarget", re.compile(rf"^removercopytarget {_TARGET}$")),
)


def _valid_ipv4(text: str) -> bool:
    try:
        ipaddress.IPv4Address(text)
        return True
    except ValueError:
        return False


def rc_write_refusal(command: str) -> str | None:
    """Why `ArrayRcCliClient.write` would refuse `command`, or None when it may run."""
    if any(ch in command for ch in _FORBIDDEN_CHARS):
        return "refused: command contains a forbidden shell metacharacter"
    for _name, form in RC_WRITE_FORMS:
        m = form.match(command)
        if not m:
            continue
        addresses = re.findall(_IPV4, command)
        if not all(_valid_ipv4(a) for a in addresses):
            return "refused: not a valid IPv4 address in " + command
        mask = m.groupdict().get("mask")
        if mask is not None and "." not in mask and not 1 <= int(mask) <= 32:
            return "refused: prefix length must be 1 to 32"
        if mask is not None and "." in mask:
            bits = int(ipaddress.IPv4Address(mask))
            if bits == 0 or (bits | (bits - 1)) & 0xFFFFFFFF != 0xFFFFFFFF:
                return f"refused: '{mask}' is not a netmask"
        return None
    return ("refused: only the Remote Copy link and target commands may run here (startrcopy, "
            "controlport rcip addr|gw|ping, creatercopytarget … IP, admitrcopylink, dismissrcopylink, "
            "removercopytarget without -cleargroups)")


def answered_error(text: str) -> bool:
    """The array's refusal: a line starting with 'Error', or a failed confirmation."""
    return any(line.strip().lower().startswith("error") for line in text.splitlines())


class ArrayRcCliClient(ArrayCliClient):
    """Reads like `ArrayCliClient`; writes only the Remote Copy link and target commands above."""

    def write(self, command: str, timeout: float | None = None) -> str:
        if self._client is None:
            raise ArrayCliError("not connected")
        started = time.monotonic()
        why = rc_write_refusal(command)
        if why:
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=why, secrets=[self.password], write=True)
            raise ArrayCliError(why)
        try:
            text = self._exec(command, timeout)
        except ArrayCliError as exc:
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=str(exc), secrets=[self.password], write=True)
            raise
        failed = answered_error(text)
        first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
        command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=not failed,
                           result=first if failed else (first or "ok"), output=text,
                           secrets=[self.password], write=True)
        return text

    def __enter__(self) -> ArrayRcCliClient:
        self.connect()
        return self
