"""SPEC-019 R1: one record per command a client sends to a device, delivered to the run that is
current in this context (bound by the run coordinator for the step's task and its worker threads).

Clients call `record()` after every command; with no run bound it does nothing. Output is capped and
every secret the client holds is replaced before the record leaves the client.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterable
from contextvars import ContextVar, Token
from datetime import UTC, datetime

MAX_OUTPUT_BYTES = 64 * 1024
REDACTED = "********"

Sink = Callable[[dict], None]
_sink: ContextVar[Sink | None] = ContextVar("alletra_command_sink", default=None)


def bind(sink: Sink | None) -> Token:
    return _sink.set(sink)


def unbind(token: Token) -> None:
    _sink.reset(token)


def active() -> bool:
    return _sink.get() is not None


def redact(text: str, secrets: Iterable[str]) -> str:
    for secret in secrets:
        if secret and len(secret) >= 3:
            text = text.replace(secret, REDACTED)
    return text


def cap(text: str) -> str:
    data = text.encode("utf-8", "replace")
    if len(data) <= MAX_OUTPUT_BYTES:
        return text
    cut = data[:MAX_OUTPUT_BYTES].decode("utf-8", "ignore")
    return f"{cut}\n… ({(len(data) - MAX_OUTPUT_BYTES) // 1024} KB truncated)"


def as_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, indent=1, default=str)
    except (TypeError, ValueError):
        return str(value)


def record(
    *, target: str, transport: str, command: str, started: float, ok: bool, result: str,
    output: object = "", secrets: Iterable[str] = (), write: bool = False,
) -> None:
    """`started` is a time.monotonic() reading taken before the command was sent."""
    sink = _sink.get()
    if sink is None:
        return
    secrets = [s for s in secrets if s]
    entry = {
        "at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": target,
        "transport": transport,
        "command": redact(command, secrets),
        "duration_s": round(time.monotonic() - started, 2),
        "ok": ok,
        "result": redact(result, secrets)[:300],
        "write": write,
        "output": cap(redact(as_text(output), secrets)),
    }
    try:
        sink(entry)
    except Exception:  # noqa: BLE001 - the log must never break the command it describes
        pass
