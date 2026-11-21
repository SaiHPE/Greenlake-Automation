"""Remote Copy replication and failover-test routes."""

from __future__ import annotations

from fastapi import APIRouter

from alletra_onboard.api.routes.common import start_step
from alletra_onboard.api.schemas import (
    FailoverTestRequest,
    LinkCheckRequest,
    ReplicationApplyRequest,
    RunResponse,
)
from alletra_onboard.application.service import OnboardingService


def build_replication_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs/{run_id}/replication/preview", response_model=RunResponse)
    async def run_replication_preview(run_id: str) -> RunResponse:
        # SPEC-016 R1-R3, read-only: both arrays over SSH, the partnership, the exists/create/conflict plan.
        return start_step(service, run_id, lambda: service.start_replication_preview(run_id))

    @router.post("/runs/{run_id}/replication/link-check", response_model=RunResponse)
    async def run_replication_link_check(run_id: str, request: LinkCheckRequest | None = None) -> RunResponse:
        # SPEC-020 R2: checkrclink server on B, client on A, read until the latency, stop both. No config change.
        req = request or LinkCheckRequest()
        return start_step(service, run_id, lambda: service.start_link_check(run_id, duration_s=req.duration_s))

    @router.post("/runs/{run_id}/replication/apply", response_model=RunResponse)
    async def run_replication_apply(run_id: str, request: ReplicationApplyRequest | None = None) -> RunResponse:
        # SPEC-016 R4/R7: creates Remote Copy groups over WSAPI: only the held plan, named by the id the operator ticked.
        # SPEC-020 R4: on RCIP the link must have been checked; over the limit needs accept_latency.
        req = request or ReplicationApplyRequest()
        return start_step(
            service,
            run_id,
            lambda: service.start_replication_apply(
                run_id, approved_plan=req.approved_plan, accept_latency=req.accept_latency
            ),
        )

    @router.post("/runs/{run_id}/replication/verify", response_model=RunResponse)
    async def run_replication_verify(run_id: str) -> RunResponse:
        # SPEC-016 R6, read-only: showrcopy on both arrays, one verdict per planned group.
        return start_step(service, run_id, lambda: service.start_replication_verify(run_id))

    @router.post("/runs/{run_id}/replication/failover-test", response_model=RunResponse)
    async def run_failover_test(run_id: str, request: FailoverTestRequest | None = None) -> RunResponse:
        # SPEC-017: stop -> failover -> recover -> wait -> restore on one group over WSAPI's DR action;
        # requires authorised=True (R4). Role changes on two arrays: never implicit.
        req = request or FailoverTestRequest()
        return start_step(
            service,
            run_id,
            lambda: service.start_failover_test(
                run_id, group=req.group, confirm=req.confirm, authorised=req.authorised,
            ),
        )

    return router
