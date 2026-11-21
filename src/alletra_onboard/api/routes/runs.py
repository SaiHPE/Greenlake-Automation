"""Run creation, listing and detail routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404
from alletra_onboard.api.schemas import (
    CreateRunRequest,
    RunDetailResponse,
    RunFromSheetRequest,
    RunListResponse,
    RunResponse,
)
from alletra_onboard.application.service import (
    OnboardingService,
    PendingSheetNotFoundError,
    RunNotFoundError,
)
from alletra_onboard.domain.ports import StoredCredentialsUnreadableError


def build_runs_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs", response_model=RunResponse)
    async def create_run(request: CreateRunRequest) -> RunResponse:
        return RunResponse(
            run=service.create_run(
                request.work_item, mode=request.mode, selected_steps=request.selected_steps
            )
        )

    @router.post("/runs/from-sheet", response_model=RunResponse)
    async def create_run_from_sheet(request: RunFromSheetRequest) -> RunResponse:
        # The operator picked a mode for a previously-uploaded complete sheet -> mint the run now.
        try:
            run = service.create_run_from_pending(
                request.token, mode=request.mode, selected_steps=request.selected_steps
            )
        except PendingSheetNotFoundError as exc:
            raise HTTPException(
                status_code=410,
                detail="This uploaded sheet is no longer held — re-upload the Initialisation sheet.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return RunResponse(run=run)

    @router.get("/runs", response_model=RunListResponse)
    async def list_runs() -> RunListResponse:
        return RunListResponse(runs=service.list_runs())

    @router.get("/runs/{run_id}", response_model=RunDetailResponse)
    async def get_run(run_id: str) -> RunDetailResponse:
        run = get_run_or_404(service, run_id)
        # A run whose stored credentials cannot be read still opens; its steps say why they refuse.
        try:
            item = service.get_work_item(run_id)
        except (RunNotFoundError, StoredCredentialsUnreadableError):
            item = None
        try:
            credential = service.array_credential_info(run_id)
        except (RunNotFoundError, StoredCredentialsUnreadableError):
            credential = None
        return RunDetailResponse(run=run, work_item=item, array_credential=credential)

    return router
