from __future__ import annotations

import asyncio
from collections import defaultdict

from alletra_onboard.domain.models import RunEvent


class InMemoryEventBus:
    """Per-run event history + live fan-out to subscribers (the API's SSE stream).

    publish() is async (EventSink protocol); publish_sync() exists for sync call sites like the
    provisioning progress callback. Both append to history and push to every live subscriber
    queue without blocking (queues are unbounded).
    """

    def __init__(self) -> None:
        self._events: dict[str, list[RunEvent]] = defaultdict(list)
        self._subscribers: dict[str, list[asyncio.Queue[RunEvent]]] = defaultdict(list)

    async def publish(self, event: RunEvent) -> None:
        self.publish_sync(event)

    def publish_sync(self, event: RunEvent) -> None:
        self._events[event.run_id].append(event)
        for queue in list(self._subscribers[event.run_id]):
            queue.put_nowait(event)

    def list_events(self, run_id: str) -> list[RunEvent]:
        return list(self._events[run_id])

    def subscribe(self, run_id: str) -> asyncio.Queue[RunEvent]:
        queue: asyncio.Queue[RunEvent] = asyncio.Queue()
        self._subscribers[run_id].append(queue)
        return queue

    def unsubscribe(self, run_id: str, queue: asyncio.Queue[RunEvent]) -> None:
        try:
            self._subscribers[run_id].remove(queue)
        except ValueError:
            pass
