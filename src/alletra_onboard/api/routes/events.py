"""Run event history and SSE stream routes."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from alletra_onboard.api.routes.common import get_run_or_404, sse_stream
from alletra_onboard.api.schemas import EventListResponse, run_event_list
from alletra_onboard.application.service import OnboardingService


def build_events_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.get("/runs/{run_id}/events", response_model=EventListResponse,
                responses={200: {"model": run_event_list()}})
    async def list_events(run_id: str) -> EventListResponse:
        get_run_or_404(service, run_id)
        return EventListResponse(events=service.list_events(run_id))

    @router.get("/runs/{run_id}/stream")
    async def stream_events(run_id: str) -> StreamingResponse:
        get_run_or_404(service, run_id)
        return sse_stream(service.events, run_id, lambda event: event.model_dump_json())

    return router
