"""Domain error hierarchy for device and cloud adapter failures (STANDARD E1, L3).

Adapters raise subclasses of `DeviceError`; application code catches these domain errors without
importing adapter modules or transport libraries.
"""

from __future__ import annotations

from typing import Any


class DeviceError(RuntimeError):
    """Base error for failures talking to an array, switch, host, vCenter or cloud API."""


class ArrayCliError(DeviceError):
    """Couldn't connect, authenticate, or run a command on the array over SSH."""


class WsapiError(DeviceError):
    """Couldn't reach, authenticate to, or drive WSAPI v1 on the array."""


class WsapiNotReady(WsapiError):
    """The array's WSAPI is reachable but not serving (503 'services not ready') — retry later."""


class WsapiV3Error(DeviceError):
    """The request got no answer from the array: connection refused, TLS failure or timeout. The only
    failure that means the file API is not there (lesson 27)."""


class WsapiV3TrustError(WsapiV3Error):
    """The array presented a certificate the run does not trust (or the device CA bundle refused it),
    so nothing was sent. Its message is the sentence for the operator."""


class WsapiV3LoginRefused(DeviceError):
    """The array answered the login but gave no session (a 4xx or 5xx, or no `key`)."""

    def __init__(self, answer: Any) -> None:
        status = getattr(answer, "status", "unknown")
        super().__init__(f"the array answered the login with HTTP {status}")
        self.answer: Any = answer


class GreenLakeError(DeviceError):
    """A GreenLake REST or OAuth API call failed."""


class GreenLakeAsyncOperationError(GreenLakeError):
    """A polled GreenLake async-operation reached a terminal failure state."""


class GreenLakeHttpError(GreenLakeError):
    """An HTTP 4xx/5xx answer from GreenLake, translated out of httpx at the adapter edge."""

    def __init__(self, status_code: int, method: str, path: str, body_detail: str = "") -> None:
        self.status_code = status_code
        self.method = method
        self.path = path
        self.body_detail = body_detail
        base = f"HTTP {status_code} from {method} {path}"
        super().__init__(f"{base} — {body_detail}" if body_detail else base)

    @property
    def short_detail(self) -> str:
        return f"HTTP {self.status_code} from {self.method} {self.path}"


def answered_error(text: str) -> bool:
    """Whether an array CLI answer reported an error line."""
    return any(line.strip().lower().startswith("error") for line in text.splitlines())
