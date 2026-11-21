"""Discovery, array ports and SAN zoning routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404, start_step
from alletra_onboard.api.schemas import (
    ArrayPortsResponse,
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


def build_discovery_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs/{run_id}/discover", response_model=RunResponse)
    async def run_discover(run_id: str) -> RunResponse:
        return start_step(service, run_id, lambda: service.start_discover(run_id))

    @router.get("/runs/{run_id}/ports", response_model=ArrayPortsResponse)
    async def array_ports(run_id: str) -> ArrayPortsResponse:
        get_run_or_404(service, run_id)
        try:
            return ArrayPortsResponse(**service.get_ports(run_id))
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="this run has no provisioning sheet") from exc

    @router.post("/runs/{run_id}/ports/preview", response_model=RunResponse)
    async def run_ports_preview(run_id: str) -> RunResponse:
        # SPEC-024 R2/R3, read-only: the array's ports, iSCSI addresses and VLANs, and the plan for the
        # sheet's iSCSI network tab. Its CLI lines are printed for the engineer; nothing is sent.
        return start_step(service, run_id, lambda: service.start_ports_preview(run_id))

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
