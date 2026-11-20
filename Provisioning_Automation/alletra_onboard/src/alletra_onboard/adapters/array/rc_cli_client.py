"""The write-scoped SSH client for Remote Copy links and targets (ADR 0015, BL-41).

Layers 1–2 of replication (RCIP addresses, the Remote Copy service, targets and links) have no WSAPI
call, so they go over SSH, and only through this client. It is a separate class from the read-only
`ArrayCliClient` (ADR 0001), which stays the default for every read. `write()` runs exactly the
commands below, each checked for its whole shape, not only its first word, and only on the ports,
addresses and targets of the approved plan it was built with (ADR 0025 condition 3); `run()` keeps the
read allowlist so the client can read back what it changed. The service constructs it only inside the
apply of a plan the operator approved; a client built without the plan's objects writes nothing.

Command forms are the arrays' own (`help controlport`, `help creatercopytarget`, … captured
2026-11-03 on rack13-ARCUS OS 10.5.55 and PRIMERA630R11U22 OS 4.6.20). `controlport` asks
"Are you sure…?" without `-f`, and an SSH exec has no terminal to answer it, so `-f` is required.
Nothing here can remove a group, stop Remote Copy, change a port's role, or touch a non-RCIP port.
"""

from __future__ import annotations

import ipaddress
import re
import time
from typing import Any

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array.cli_client import _FORBIDDEN_CHARS, ArrayCliClient
from alletra_onboard.domain.approval import Approval, require_approval
from alletra_onboard.domain.array_parse import answered_error
from alletra_onboard.domain.errors import ArrayCliError
from alletra_onboard.domain.plan_objects import RcPlanObjects

_NSP = r"\d{1,2}:\d{1,2}:\d{1,2}"
_IPV4 = r"(?:\d{1,3}\.){3}\d{1,3}"
# Target names: the array's own name rules are wider, the tool names targets after the other array.
_TARGET = r"[A-Za-z0-9][A-Za-z0-9_.-]{0,30}"
_LINK = rf"{_NSP}:{_IPV4}"

# The named groups say what each command acts on: `nsp` a port of this array, `addr` an address set on
# it (RCIP address or gateway), `peer` the other array's address, `links` `<N:S:P>:<peer>` pairs,
# `target` a Remote Copy target. `rc_object_refusal` checks them against the approved plan.
RC_WRITE_FORMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("startrcopy", re.compile(r"^startrcopy$")),
    ("controlport rcip addr", re.compile(
        rf"^controlport rcip addr -f (?P<addr>{_IPV4}) (?P<mask>{_IPV4}|\d{{1,2}}) (?P<nsp>{_NSP})$")),
    ("controlport rcip gw", re.compile(rf"^controlport rcip gw -f (?P<addr>{_IPV4}) (?P<nsp>{_NSP})$")),
    ("controlport rcip ping", re.compile(
        rf"^controlport rcip ping (?:-c (?:[1-9]|10) )?(?P<peer>{_IPV4}) (?P<nsp>{_NSP})$")),
    ("creatercopytarget", re.compile(rf"^creatercopytarget (?P<target>{_TARGET}) IP (?P<links>{_LINK}(?: {_LINK})*)$")),
)
# BL-51: admitrcopylink, dismissrcopylink and removercopytarget were allowed and never sent; the
# removal set names removercopytarget as text the operator pastes. A form joins here with the code
# that sends it.

UNBOUND = "refused: this client was not built from an approved replication plan, so it writes nothing"


def _valid_ipv4(text: str) -> bool:
    try:
        ipaddress.IPv4Address(text)
        return True
    except ValueError:
        return False


def _form_match(command: str) -> re.Match[str] | None:
    for _name, form in RC_WRITE_FORMS:
        m = form.match(command)
        if m:
            return m
    return None


def rc_write_refusal(command: str) -> str | None:
    """Why `ArrayRcCliClient.write` would refuse the shape of `command`, or None when it is well formed."""
    if any(ch in command for ch in _FORBIDDEN_CHARS):
        return "refused: command contains a forbidden shell metacharacter"
    m = _form_match(command)
    if m is None:
        return ("refused: only the Remote Copy link and target commands may run here (startrcopy, "
                "controlport rcip addr|gw|ping, creatercopytarget … IP)")
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


def rc_object_refusal(command: str, objects: RcPlanObjects) -> str | None:
    """Why `ArrayRcCliClient.write` would refuse a well-formed `command` for naming a port, address or
    target the approved plan does not name on this array, or None when every one is in the plan."""
    m = _form_match(command)
    if m is None:
        return rc_write_refusal(command)
    named = m.groupdict()
    ports = [named["nsp"]] if named.get("nsp") else []
    peers = [named["peer"]] if named.get("peer") else []
    for link in (named.get("links") or "").split():
        nsp, peer = link.rsplit(":", 1)
        ports.append(nsp)
        peers.append(peer)
    for nsp in ports:
        if nsp not in objects.ports:
            return f"refused: port {nsp} is not in the approved plan"
    addr = named.get("addr")
    if addr and addr not in objects.addresses:
        return f"refused: address {addr} is not one the approved plan sets on this array"
    for peer in peers:
        if peer not in objects.peer_addresses:
            return f"refused: peer address {peer} is not in the approved plan"
    target = named.get("target")
    if target and target not in objects.targets:
        return f"refused: target {target} is not in the approved plan"
    return None


class ArrayRcCliClient(ArrayCliClient):
    """Reads like `ArrayCliClient`; writes only the Remote Copy link and target commands above, and only
    on the objects of the plan it was built with. Built without them, it refuses every write."""

    def __init__(self, host: str, username: str, password: str, *, approval: Approval,
                 objects: RcPlanObjects | None = None, **kwargs: Any) -> None:
        super().__init__(host, username, password, **kwargs)
        self._objects = objects
        self._approval = require_approval(approval)

    @property
    def objects(self) -> RcPlanObjects | None:
        return self._objects

    def write_refusal(self, command: str) -> str | None:
        """Why `write` would refuse `command` on this client, or None when it may run."""
        if self._objects is None:
            return UNBOUND
        return rc_write_refusal(command) or rc_object_refusal(command, self._objects)

    def write(self, command: str, timeout: float | None = None) -> str:
        started = time.monotonic()
        if self._approval.spent:
            why = "refused: this approval has already been used"
            command_log.record(target=self.host, transport="ssh", command=command, started=started, ok=False,
                               result=why, secrets=[self.password], write=True)
            self._approval.require_live()
        if self._client is None:
            raise ArrayCliError("not connected")
        why = self.write_refusal(command)
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
