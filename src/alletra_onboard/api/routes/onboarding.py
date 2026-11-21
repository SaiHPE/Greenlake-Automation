"""Onboarding step routes: GreenLake registration, Cloud Connectivity and DSCC setup."""

from __future__ import annotations

from functools import partial

from fastapi import APIRouter

from alletra_onboard.api.routes.common import start_step
from alletra_onboard.api.schemas import (
    CloudinitStepRequest,
    DsccStepRequest,
    ProvisionStepRequest,
    RunResponse,
)
from alletra_onboard.application.service import OnboardingService


def build_onboarding_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()
    _start_step = partial(start_step, service)

    @router.post("/runs/{run_id}/provision", response_model=RunResponse)
    async def run_provision(run_id: str, request: ProvisionStepRequest) -> RunResponse:
        """GreenLake device registration (the `greenlake` step): register, assign, subscribe.

        Not storage provisioning; that is `/runs/{id}/storage/preview` and `/storage/apply`. The
        path predates the storage steps. It is documented rather than renamed so the UI, and any
        script written against it, keep working.
        """
        return _start_step(run_id, lambda: service.start_provision(run_id, dry_run=request.dry_run))

    @router.post("/runs/{run_id}/cloudinit", response_model=RunResponse)
    async def run_cloudinit(run_id: str, request: CloudinitStepRequest) -> RunResponse:
        return _start_step(
            run_id,
            lambda: service.start_cloudinit(
                run_id, cloudinit_url=request.cloudinit_url, auto_submit=request.auto_submit
            ),
        )

    @router.post("/runs/{run_id}/dscc", response_model=RunResponse)
    async def run_dscc(run_id: str, request: DsccStepRequest) -> RunResponse:
        return _start_step(run_id, lambda: service.start_dscc(run_id, cdp_url=request.cdp_url))

    return router
