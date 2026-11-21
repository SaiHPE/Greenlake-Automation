"""On-site device trust (ADR 0026) routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import get_run_or_404
from alletra_onboard.api.schemas import RetrustRequest, RetrustResponse, TrustedDevicesResponse
from alletra_onboard.application.service import (
    DevicePinNotFoundError,
    OnboardingService,
    StepPreconditionError,
)


def build_trust_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.get("/runs/{run_id}/trust", response_model=TrustedDevicesResponse)
    async def trusted_devices(run_id: str) -> TrustedDevicesResponse:
        # The key or certificate each on-site device presented on this run's first contact: fingerprints only.
        get_run_or_404(service, run_id)
        return TrustedDevicesResponse(devices=service.trusted_devices(run_id), device_ca_bundle=service.device_ca_bundle())

    @router.post("/runs/{run_id}/trust/retrust", response_model=RetrustResponse)
    async def retrust_device(run_id: str, request: RetrustRequest) -> RetrustResponse:
        # A separate, logged action on the run (never a button on the error): trust the key the device
        # presented when it was refused, named by the fingerprint the operator compared.
        get_run_or_404(service, run_id)
        try:
            device = service.retrust_device(run_id, kind=request.kind, host=request.host, port=request.port,
                                            fingerprint=request.fingerprint)
        except DevicePinNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return RetrustResponse(device=device)

    return router
