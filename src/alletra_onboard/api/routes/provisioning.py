"""Block storage provisioning routes: preflight, builder, preview, apply and path verify."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404, start_step
from alletra_onboard.api.schemas import RunResponse, StorageApplyRequest
from alletra_onboard.application.service import (
    OnboardingService,
    RunBusyError,
    StepPreconditionError,
)
from alletra_onboard.domain.provisioning import (
    PreflightReport,
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningObjects,
)


async def _recorded_read[T](
    service: OnboardingService, run_id: str, read: Callable[[str], T]
) -> T:
    get_run_or_404(service, run_id)
    try:
        with service.coordinator.recording(run_id):
            return await asyncio.to_thread(read, run_id)
    except StepPreconditionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


def build_provisioning_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.get("/runs/{run_id}/storage/preflight", response_model=PreflightReport)
    async def storage_preflight(run_id: str) -> PreflightReport:
        # Read-only readiness of the array + vCenter the sheet points at, so a missing prerequisite is
        # named BEFORE discovery runs instead of surfacing as a failed step. Makes no writes.
        return await _recorded_read(service, run_id, service.get_storage_preflight)

    @router.get("/runs/{run_id}/storage/objects", response_model=ProvisioningObjects)
    async def storage_objects(run_id: str) -> ProvisioningObjects:
        # The dropdown palette (existing array objects + to-be-created + discovered hosts). Reads the
        # array over WSAPI, so run it off the event loop.
        return await _recorded_read(service, run_id, service.get_storage_objects)

    @router.post("/runs/{run_id}/storage/builder", response_model=ProvisioningComposition)
    async def storage_builder(run_id: str, request: ProvisioningBuilder) -> ProvisioningComposition:
        # Save the operator-composed host-set membership + VV-set membership + exports onto the intent.
        get_run_or_404(service, run_id)
        try:
            return service.set_provisioning_builder(run_id, request)
        except (RunBusyError, StepPreconditionError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/runs/{run_id}/storage/preview", response_model=RunResponse)
    async def run_storage_preview(run_id: str) -> RunResponse:
        return start_step(service, run_id, lambda: service.start_storage_preview(run_id))

    @router.post("/runs/{run_id}/storage/apply", response_model=RunResponse)
    async def run_storage_apply(run_id: str, request: StorageApplyRequest | None = None) -> RunResponse:
        # Creates host/volumes/exports on the array: only the held plan, named by the id the operator ticked.
        req = request or StorageApplyRequest()
        return start_step(service, run_id, lambda: service.start_storage_apply(run_id, approved_plan=req.approved_plan))

    @router.post("/runs/{run_id}/storage/verify-paths", response_model=RunResponse)
    async def run_storage_verify_paths(run_id: str) -> RunResponse:
        # Tier-2, read-only: reads showvlun -a and reports per-host path liveness. Never gates.
        return start_step(service, run_id, lambda: service.start_path_verify(run_id))

    return router
