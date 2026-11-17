"""ADR 0026: one run's device pins, bound for a step so every SSH and TLS client checks against them.

The coordinator builds a `RunTrustBook` for each spawned step and each route that reads a device,
binds it (like the command log), and calls `finish()` on the event loop when the step ends: a device
that was refused during a step blocks it, whatever the step did with the client's error. A route
(the console, the storage readiness check) answers with the refusal itself; its book only notes it
on the run.
"""

from __future__ import annotations

import asyncio
import threading
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from alletra_onboard.domain.trust import (
    DeviceKey,
    DevicePin,
    DevicePinInfo,
    TrustKind,
    mismatch_message,
    trusted_message,
)

if TYPE_CHECKING:
    from alletra_onboard.application.runs.coordinator import RunCoordinator


class RunTrustBook:
    """The `adapters.device_trust.TrustBook` of one run. Its methods run on worker threads; the
    events they emit are handed to the event loop."""

    def __init__(self, coord: RunCoordinator, run_id: str, *, device_ca_bundle: str | None = None,
                 step: bool = True) -> None:
        self._coord = coord
        self.run_id = run_id
        self.device_ca_bundle = device_ca_bundle
        self._step = step
        self._loop = asyncio.get_running_loop()
        self._loop_thread = threading.get_ident()
        self._lock = threading.Lock()
        self._refused: dict[tuple[str, str, int], tuple[DevicePin, DeviceKey]] = {}

    def pin(self, kind: TrustKind, host: str, port: int) -> DevicePin | None:
        return self._coord.store.get_device_pin(self.run_id, kind, host, port)

    def first_contact(self, pin: DevicePin) -> DevicePin:
        held = self._coord.store.add_device_pin(self.run_id, pin)
        if held == pin:   # this contact recorded it; a concurrent one would hold its own
            self._emit("device.trusted", trusted_message(held), {"device": DevicePinInfo.of(held).model_dump(mode="json")})
        return held

    def refuse(self, pin: DevicePin, offered: DeviceKey) -> None:
        self._coord.store.save_device_pin(
            self.run_id, pin.model_copy(update={"refused": offered, "refused_at": datetime.now(UTC)}))
        with self._lock:
            self._refused[(str(pin.kind), pin.host, pin.port)] = (pin, offered)

    @property
    def refusals(self) -> list[tuple[DevicePin, DeviceKey]]:
        with self._lock:
            return list(self._refused.values())

    def finish(self) -> None:
        """On the event loop, after the step: one failure event per refused device, in the step's phase,
        so the step shows as stopped even when its code carried on without that device. After a route,
        a note on the run instead: the route's own answer already carried the refusal."""
        event_type = "device.trust_failed" if self._step else "device.refused"
        for pin, offered in self.refusals:
            stored = self._coord.store.get_device_pin(self.run_id, pin.kind, pin.host, pin.port) or pin
            self._coord.emit(
                self.run_id, self._phase(), event_type,
                mismatch_message(pin, offered), data={"device": DevicePinInfo.of(stored).model_dump(mode="json")},
            )

    def _phase(self):
        if self._step:
            return self._coord.step_phase(self.run_id)
        return self._coord.get_run(self.run_id).current_phase

    def _emit(self, event_type: str, message: str, data: dict) -> None:
        phase = self._phase()
        if threading.get_ident() == self._loop_thread:
            self._coord.emit(self.run_id, phase, event_type, message, data)
        else:
            self._loop.call_soon_threadsafe(self._coord.emit, self.run_id, phase, event_type, message, data)
