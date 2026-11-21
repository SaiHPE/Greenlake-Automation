"""Discovery and array ports routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404, start_step
from alletra_onboard.api.schemas import ArrayPortsResponse, RunResponse
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

    return router
