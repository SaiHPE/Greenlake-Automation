"""Snapshot and snapshot-schedule routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404, start_step
from alletra_onboard.api.schemas import RunResponse, SnapshotApplyRequest, SnapshotsResponse
from alletra_onboard.application.service import OnboardingService, RunNotFoundError


def build_snapshots_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.get("/runs/{run_id}/snapshots", response_model=SnapshotsResponse)
    async def snapshots_tab(run_id: str) -> SnapshotsResponse:
        # SPEC-023 R10: what the workbook asks for, in words, and whether the plan last shown is still held.
        get_run_or_404(service, run_id)
        try:
            return SnapshotsResponse(**service.get_snapshots(run_id))
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="this run has no provisioning sheet") from exc

    @router.post("/runs/{run_id}/snapshots/preview", response_model=RunResponse)
    async def run_snapshots_preview(run_id: str) -> RunResponse:
        # SPEC-023 R3/R4, read-only: showsched, showdate, showcpg over SSH; volumes, sets, /system over WSAPI.
        return start_step(service, run_id, lambda: service.start_snapshots_preview(run_id))

    @router.post("/runs/{run_id}/snapshots/apply", response_model=RunResponse)
    async def run_snapshots_apply(run_id: str, request: SnapshotApplyRequest | None = None) -> RunResponse:
        # SPEC-023 R5/R6: the snapshots now over WSAPI, then the schedules: only the held plan, named by
        # the id the operator ticked.
        req = request or SnapshotApplyRequest()
        return start_step(service, run_id, lambda: service.start_snapshots_apply(run_id, approved_plan=req.approved_plan))

    @router.post("/runs/{run_id}/snapshots/verify", response_model=RunResponse)
    async def run_snapshots_verify(run_id: str) -> RunResponse:
        # SPEC-023 R7, read-only: the snapshots now and each schedule, read back.
        return start_step(service, run_id, lambda: service.start_snapshots_verify(run_id))

    return router
