"""Verification, as-built document and run completion routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from alletra_onboard.api.routes.common import get_run_or_404, start_step
from alletra_onboard.api.schemas import AsBuiltStepRequest, RunResponse, VerifyStepRequest
from alletra_onboard.application.service import OnboardingService


def build_documents_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs/{run_id}/verify", response_model=RunResponse)
    async def run_verify(run_id: str, request: VerifyStepRequest) -> RunResponse:
        # Post-init read-only SSH verification of the array config. Password is used for the SSH
        # session only — never stored. Never changes the run's COMPLETE/SUCCEEDED status.
        return start_step(
            service,
            run_id,
            lambda: service.start_verify(run_id, username=request.username, password=request.password),
        )

    @router.post("/runs/{run_id}/asbuilt", response_model=RunResponse)
    async def run_asbuilt(run_id: str, request: AsBuiltStepRequest) -> RunResponse:
        # Read-only: SSH the array (show*/checkhealth/showinventory -csvtable) and build the as-built
        # .docx. Password is used for the SSH session only. Download it from /asbuilt/download.
        return start_step(
            service,
            run_id,
            lambda: service.start_asbuilt(
                run_id, username=request.username, password=request.password,
                customer=request.customer, site=request.site,
                application_workload=request.application_workload, purpose=request.purpose,
            ),
        )

    @router.get("/runs/{run_id}/asbuilt/download")
    async def download_asbuilt(run_id: str) -> Response:
        run = get_run_or_404(service, run_id)
        data = service.get_asbuilt(run_id)
        if data is None:
            raise HTTPException(status_code=404, detail="No as-built generated yet — run the as-built step first.")
        serial = run.serial_number  # from the run, so a run whose credentials cannot be read still downloads
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="as-built-{serial}.docx"'},
        )

    @router.post("/runs/{run_id}/complete", response_model=RunResponse)
    async def complete_run(run_id: str) -> RunResponse:
        get_run_or_404(service, run_id)
        return RunResponse(run=service.mark_complete(run_id))

    return router
