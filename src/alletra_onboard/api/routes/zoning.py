"""SAN zoning routes (read-only checks, switch-read plan, copy-paste command set, and opt-in Brocade apply)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.routes.common import start_step
from alletra_onboard.api.schemas import (
    RunResponse,
    ZoningApplyRequest,
    ZoningRenderRequest,
    ZoningRenderResponse,
)
from alletra_onboard.application.provisioning.zoning_apply import build_apply_plan
from alletra_onboard.application.provisioning.zoning_plan import (
    alias_name_warnings,
    render_commands,
    render_peer_commands,
)
from alletra_onboard.application.service import (
    OnboardingService,
    RunNotFoundError,
    StepPreconditionError,
)
from alletra_onboard.domain.zoning import ZoningApplyPlan


def _try_build_apply_plan(
    request: ZoningRenderRequest,
    commands: dict[str, list[str]],
    peer_commands: dict[str, list[str]],
) -> tuple[ZoningApplyPlan, str | None]:
    try:
        return build_apply_plan(
            request.plan, request.aliases, request.selected_pairs, commands, peer_commands,
        ), None
    except ValueError as exc:
        return ZoningApplyPlan(), str(exc)


def build_zoning_router(service: OnboardingService) -> APIRouter:
    router = APIRouter()

    @router.post("/runs/{run_id}/zoning/preview", response_model=RunResponse)
    async def run_zoning_preview(run_id: str) -> RunResponse:
        return start_step(service, run_id, lambda: service.start_zoning_preview(run_id))

    @router.post("/runs/{run_id}/zoning/plan", response_model=RunResponse)
    async def run_zoning_plan(run_id: str) -> RunResponse:
        # Read-only: reads both fabric switches to build the zoning plan; makes NO switch writes.
        return start_step(service, run_id, lambda: service.start_zoning_plan(run_id))

    @router.post("/runs/{run_id}/zoning/apply", response_model=RunResponse)
    async def run_zoning_apply(run_id: str, request: ZoningApplyRequest | None = None) -> RunResponse:
        # ADR 0033: opt-in Brocade FOS zoning apply; requires the held plan_id the operator ticked.
        req = request or ZoningApplyRequest()
        return start_step(service, run_id, lambda: service.start_zoning_apply(run_id, approved_plan=req.approved_plan))

    @router.post("/zoning/render", response_model=ZoningRenderResponse)
    async def zoning_render(request: ZoningRenderRequest) -> ZoningRenderResponse:
        # Assemble the copy-paste command set (default deliverable) and, for a run, cache the
        # opt-in Brocade apply plan (ADR 0033).
        commands, skipped = render_commands(request.plan, request.aliases, request.selected_pairs)
        peer_commands, peer_skipped = render_peer_commands(request.plan, request.aliases)
        warnings = alias_name_warnings(request.plan, request.aliases)
        apply_plan, apply_err = _try_build_apply_plan(request, commands, peer_commands)
        if apply_err:
            warnings.setdefault("apply", []).append(
                f"Direct switch apply is unavailable for this selection: {apply_err}"
            )
        apply_plan_id: str | None = None
        apply_fabrics = []
        if request.run_id:
            try:
                service.hold_zoning_apply_plan(request.run_id, apply_plan)
                service.record_zoning_render(
                    request.run_id, commands=commands, skipped=skipped,
                    aliases=request.aliases, selected_pairs=request.selected_pairs,
                    peer_commands=peer_commands,
                )
            except RunNotFoundError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            except StepPreconditionError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            apply_plan_id = apply_plan.plan_id or None
            apply_fabrics = apply_plan.fabrics
        return ZoningRenderResponse(
            commands=commands, skipped=skipped, warnings=warnings,
            peer_commands=peer_commands, peer_skipped=peer_skipped,
            apply_plan_id=apply_plan_id, apply_fabrics=apply_fabrics,
        )

    return router
