"""Read-only operator console, command log and SSE stream routes (SPEC-019)."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse

from alletra_onboard.api.routes.common import get_run_or_404, sse_stream
from alletra_onboard.api.schemas import ConsoleRequest, ConsoleTerminalRequest
from alletra_onboard.application.runs.console import console_text
from alletra_onboard.application.service import OnboardingService, StepPreconditionError


def build_console_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.get("/runs/{run_id}/console/log")
    async def console_log(run_id: str, since: int = 0, format: str = "json") -> Response:
        get_run_or_404(service, run_id)
        entries = service.coordinator.list_commands(run_id, since)
        if format == "txt":
            return Response(content=console_text(entries), media_type="text/plain; charset=utf-8",
                            headers={"Content-Disposition": f'attachment; filename="commands-{run_id[:8]}.txt"'})
        return JSONResponse({"commands": entries})

    @router.get("/runs/{run_id}/console/targets")
    async def console_targets(run_id: str) -> dict:
        get_run_or_404(service, run_id)
        return {"targets": service.console.targets(run_id)}

    @router.post("/runs/{run_id}/console")
    async def console_run(run_id: str, request: ConsoleRequest) -> dict:
        # SPEC-019 R3: read-only allowlist only, with the run's own credential; refusals are answered, not raised
        get_run_or_404(service, run_id)
        try:
            return await service.console.run(run_id, request.command, request.target)
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/runs/{run_id}/console/terminal")
    async def console_terminal(run_id: str, request: ConsoleTerminalRequest) -> dict:
        get_run_or_404(service, run_id)
        try:
            return service.console.open_terminal(run_id, request.target)
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/runs/{run_id}/console/stream")
    async def console_stream(run_id: str) -> StreamingResponse:
        get_run_or_404(service, run_id)
        return sse_stream(service.coordinator.console, run_id, json.dumps)

    return router
