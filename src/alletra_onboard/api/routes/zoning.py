"""SAN zoning routes (read-only checks, switch-read plan, and copy-paste command set)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import start_step
from alletra_onboard.api.schemas import (
    RunResponse,
    ZoningRenderRequest,
    ZoningRenderResponse,
)
from alletra_onboard.application.provisioning.zoning_plan import (
    alias_name_warnings,
    render_commands,
    render_peer_commands,
)
from alletra_onboard.application.service import OnboardingService, RunNotFoundError


def build_zoning_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs/{run_id}/zoning/preview", response_model=RunResponse)
    async def run_zoning_preview(run_id: str) -> RunResponse:
        return start_step(service, run_id, lambda: service.start_zoning_preview(run_id))

    @router.post("/runs/{run_id}/zoning/plan", response_model=RunResponse)
    async def run_zoning_plan(run_id: str) -> RunResponse:
        # Read-only: reads both fabric switches to build the zoning plan; makes NO switch writes.
        return start_step(service, run_id, lambda: service.start_zoning_plan(run_id))

    # POST /runs/{run_id}/zoning/stage was removed on 2026-09-02 (ADR 0012). It wrote zones to the
    # switch; the tool no longer has that capability at any layer. /zoning/render is the whole
    # zoning output now.

    @router.post("/zoning/render", response_model=ZoningRenderResponse)
    async def zoning_render(request: ZoningRenderRequest) -> ZoningRenderResponse:
        # Assemble the command set from the plan + the operator's aliases and selected pairs. The
        # tool never RUNS these commands (ADR 0004, ADR 0012) — this is the script the SAN team
        # applies by hand, and it is the deliverable, not a rehearsal.
        commands, skipped = render_commands(request.plan, request.aliases, request.selected_pairs)
        peer_commands, peer_skipped = render_peer_commands(request.plan, request.aliases)
        if request.run_id:
            try:
                service.record_zoning_render(
                    request.run_id, commands=commands, skipped=skipped,
                    aliases=request.aliases, selected_pairs=request.selected_pairs,
                    peer_commands=peer_commands,
                )
            except RunNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
        return ZoningRenderResponse(
            commands=commands, skipped=skipped,
            warnings=alias_name_warnings(request.plan, request.aliases),
            peer_commands=peer_commands, peer_skipped=peer_skipped,
        )

    return router
