"""The write-scoped SSH client for snapshot schedules (ADR 0016, following ADR 0025, BL-21).

WSAPI has no schedule resource (`GET /api/v1/schedules` answers HTTP 501, code 9, on all four lab
arrays), so a schedule is written with the array's own `createsched`, and only through this client.
It is a separate class from the read-only `ArrayCliClient` (ADR 0001), which stays the default for
every read, and from ADR 0015's `ArrayRcCliClient`. `write()` runs exactly ONE form:

    createsched -f "createsv -f [-ro] -exp <1..43800>h @vvname@.@y@@m@@d@@H@@M@@S@ <set:name|volume>" "<min> <hour> * * <dow>" <name>

A schedule is a command the array will run later, as often as the cron says, with nobody watching, so
the command inside the quotes is checked as an exact form of its own, never only the first word. `"`
is let through only at the form's four fixed positions; every other character on the shared forbidden
list (`\\ [ ] { } $ ;` among them) is refused inside the quotes as well as outside. No lock (`-retain`),
no other `createsv` or `createsched` option, no `rcgroup:` source. `-f` on both: without it
`createsched` can stop for a confirmation the SSH session cannot give, and `createsv` asks one for
`-retain`.

The form is pinned to `help createsched` and `help createsv` on rack13-ARCUS (OS 10.6.0, 2026-11-16),
D22U27, E18U31 and VZ (OS 10.5.0, 10.5.60, 10.5.51, 2026-11-17). The client is built only inside the
apply of an approved snapshot plan, with the (schedule name, source) pairs of that plan's create rows
(ADR 0025 condition 3); one built without them writes nothing. `run()` keeps the read allowlist, so the
apply reads `showsched` back through the same session.
"""

from __future__ import annotations

import re
import time
from typing import Any

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.array.cli_client import _FORBIDDEN_CHARS, ArrayCliClient
from alletra_onboard.domain.errors import ArrayCliError, answered_error
from alletra_onboard.domain.plan_objects import SnapPlanObjects

#: `help createsv`: -exp takes 1 minute to 1825 days; the form takes whole hours, 1 to 43800.
EXPIRE_HOURS_MAX = 43800
#: `help removesched` (every OS) and `help createsched` (OS 10.5): at most 31 characters.
NAME_MAX = 31
#: `help createsched`: names the array keeps for itself.
RESERVED_NAMES = frozenset({"all", "upgrade"})
SCHEDULE_PATTERN = "@vvname@.@y@@m@@d@@H@@M@@S@"

# Never a leading '-': the name is the last word of the command, where `-run_once` would read as an option.
_NAME = rf"[A-Za-z0-9._][A-Za-z0-9._-]{{0,{NAME_MAX - 1}}}"
_VOLUME = r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,254}"
_FIELD = r"[0-9*][0-9,*]*"

# The one form: the quotes at four fixed positions, nothing outside them but -f and the name.
SNAP_WRITE_FORMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("createsched", re.compile(rf'^createsched -f "(?P<inner>[^"]*)" "(?P<cron>[^"]*)" (?P<name>{_NAME})$')),
)
# The command inside the first pair of quotes, as an exact form of its own.
_CREATESV = re.compile(
    rf"^createsv -f(?P<ro> -ro)? -exp (?P<exp>[1-9][0-9]{{0,4}})h {re.escape(SCHEDULE_PATTERN)} "
    rf"(?P<source>set:{_VOLUME}|{_VOLUME})$"
)
# `<min> <hour> * * <dow>`: no day of month, no month, digits, commas and * only.
_CRON = re.compile(rf"^(?P<minute>{_FIELD}) (?P<hour>{_FIELD}) \* \* (?P<dow>{_FIELD})$")
_CRON_RANGES = {"minute": 59, "hour": 23, "dow": 6}

FORM_TEXT = (f'createsched -f "createsv -f [-ro] -exp <n>h {SCHEDULE_PATTERN} <set:name|volume>" '
             '"<min> <hour> * * <dow>" <name>')
UNBOUND = "refused: this client was not built from an approved snapshot plan, so it writes nothing"


def _cron_refusal(cron: str) -> str | None:
    m = _CRON.match(cron)
    if m is None:
        return "refused: the schedule must run at '<min> <hour> * * <dow>', with digits, commas and * only"
    for field, top in _CRON_RANGES.items():
        for value in m.group(field).split(","):
            if value != "*" and (not value.isdigit() or int(value) > top):
                return f"refused: '{m.group(field)}' is not a {field} the array schedules (0 to {top})"
    return None


def _inner_refusal(inner: str) -> str | None:
    m = _CREATESV.match(inner)
    if m is None:
        if " -retain " in f" {inner} ":
            return "refused: a lock (-retain) is not allowed: a locked snapshot cannot be removed until the lock ends"
        return f"refused: the schedule may run only 'createsv -f [-ro] -exp <n>h {SCHEDULE_PATTERN} <set:name|volume>'"
    if not 1 <= int(m.group("exp")) <= EXPIRE_HOURS_MAX:
        return f"refused: -exp must be 1 to {EXPIRE_HOURS_MAX} hours"
    return None


def _form_match(command: str) -> re.Match[str] | None:
    for _name, form in SNAP_WRITE_FORMS:
        m = form.match(command)
        if m:
            return m
    return None


def snap_write_refusal(command: str) -> str | None:
    """Why `ArraySnapCliClient.write` would refuse the shape of `command`, or None when it is the one form."""
    if any(ch in command for ch in _FORBIDDEN_CHARS - {'"'}):
        return "refused: command contains a forbidden shell or Tcl character"
    m = _form_match(command)
    if m is None:
        return f"refused: only {FORM_TEXT} may run here"
    if m.group("name").lower() in RESERVED_NAMES:
        return f"refused: '{m.group('name')}' is a name the array keeps for itself"
    return _inner_refusal(m.group("inner")) or _cron_refusal(m.group("cron"))


def schedule_target(command: str) -> tuple[str, str] | None:
    """(schedule name, source_ref) of a well-formed command, else None."""
    if snap_write_refusal(command) is not None:
        return None
    m = _form_match(command)
    inner = _CREATESV.match(m.group("inner")) if m else None
    return (m.group("name"), inner.group("source")) if m and inner else None


def snap_object_refusal(command: str, objects: SnapPlanObjects) -> str | None:
    """Why `ArraySnapCliClient.write` would refuse a well-formed `command` for naming a schedule or a source
    the approved plan does not create, or None when the pair is one of the plan's."""
    target = schedule_target(command)
    if target is None:
        return snap_write_refusal(command)
    if target not in objects.schedules:
        name, source = target
        return f"refused: schedule {name} on {source} is not in the approved plan"
    return None


class ArraySnapCliClient(ArrayCliClient):
    """Reads like `ArrayCliClient`; writes only the one schedule form above, and only the schedules of the
    plan it was built with. Built without them, it refuses every write."""

    def __init__(self, host: str, username: str, password: str, *, objects: SnapPlanObjects | None = None,
                 **kwargs: Any) -> None:
        super().__init__(host, username, password, **kwargs)
        self._objects = objects

    @property
    def objects(self) -> SnapPlanObjects | None:
        return self._objects

    def write_refusal(self, command: str) -> str | None:
        """Why `write` would refuse `command` on this client, or None when it may run."""
        if self._objects is None:
            return UNBOUND
        return snap_write_refusal(command) or snap_object_refusal(command, self._objects)

    def write(self, command: str, timeout: float | None = None) -> str:
        if self._client is None:
            raise ArrayCliError("not connected")
        started = time.monotonic()
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

    def __enter__(self) -> ArraySnapCliClient:
        self.connect()
        return self
