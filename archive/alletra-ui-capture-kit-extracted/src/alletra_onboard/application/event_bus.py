from __future__ import annotations

from collections import defaultdict

from alletra_onboard.domain.models import RunEvent


class InMemoryEventBus:
    def __init__(self) -> None:
        self._events: dict[str, list[RunEvent]] = defaultdict(list)

    async def publish(self, event: RunEvent) -> None:
        self._events[event.run_id].append(event)

    def list_events(self, run_id: str) -> list[RunEvent]:
        return list(self._events[run_id])
