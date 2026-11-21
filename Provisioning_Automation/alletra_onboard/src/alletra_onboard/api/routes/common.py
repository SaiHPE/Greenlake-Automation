"""Shared HTTP lookup, step-start error mapping and SSE streaming helpers for route modules."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Protocol

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from alletra_onboard.api.schemas import RunResponse
from alletra_onboard.application.service import (
    OnboardingService,
    RunBusyError,
    RunNotFoundError,
    StepPreconditionError,
)
from alletra_onboard.domain.models import RunRecord

SSE_HEARTBEAT_S = 15.0


class RunStreamBus[T](Protocol):
    """InMemoryEventBus and ConsoleBus both expose per-run subscribe/unsubscribe queues."""

    def subscribe(self, run_id: str) -> asyncio.Queue[T]: ...

    def unsubscribe(self, run_id: str, queue: asyncio.Queue[T]) -> None: ...


def get_run_or_404(service: OnboardingService, run_id: str) -> RunRecord:
    try:
        return service.get_run(run_id)
    except RunNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


def start_step(
    service: OnboardingService, run_id: str, start: Callable[[], RunRecord]
) -> RunResponse:
    get_run_or_404(service, run_id)
    try:
        return RunResponse(run=start())
    except (RunBusyError, StepPreconditionError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RunNotFoundError as exc:
        # e.g. a provisioning step on a run that has no provisioning intent
        raise HTTPException(status_code=404, detail=str(exc) or "not found") from exc


def sse_stream[T](
    bus: RunStreamBus[T],
    run_id: str,
    serialize: Callable[[T], str],
) -> StreamingResponse:
    queue = bus.subscribe(run_id)

    async def generate():
        try:
            while True:
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=SSE_HEARTBEAT_S)
                except TimeoutError:
                    yield ": heartbeat\n\n"  # keeps proxies/browsers from closing the stream
                    continue
                yield f"data: {serialize(item)}\n\n"
        finally:
            bus.unsubscribe(run_id, queue)

    return StreamingResponse(generate(), media_type="text/event-stream")
