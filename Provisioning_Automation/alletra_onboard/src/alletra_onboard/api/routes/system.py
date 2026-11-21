"""Jump-box browser, Discovery Tool, clock and work-item preflight routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from alletra_onboard.api.schemas import (
    BrowserLaunchRequest,
    BrowserLaunchResponse,
    DiscoveryToolResponse,
    PreflightRequest,
    PreflightResponse,
)
from alletra_onboard.application.onboarding.clients import launch_debug_browser
from alletra_onboard.application.onboarding.preflight_service import PreflightService
from alletra_onboard.application.platform import clients as platform_clients
from alletra_onboard.config import Settings, load_settings
from alletra_onboard.domain.models import ClockStatus, ClockSyncResult


async def discovery_launch() -> DiscoveryToolResponse:
    # Runs on the jump box; opens the on-Desktop HPE Discovery Tool .exe for the operator.
    return DiscoveryToolResponse(**platform_clients.launch_discovery_tool())


async def get_clock(url: str | None = None) -> ClockStatus:
    return await platform_clients.clock_status(url)


async def post_clock_sync(url: str | None = None) -> ClockSyncResult:
    try:
        return await platform_clients.sync_clock(url)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


async def preflight(request: PreflightRequest) -> PreflightResponse:
    # Fresh settings so credentials entered in Configure after startup are honored.
    report = await PreflightService(load_settings()).run(request.work_item, live_greenlake=request.live_greenlake)
    return PreflightResponse(report=report)


def build_system_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.post("/browser/launch", response_model=BrowserLaunchResponse)
    async def browser_launch(request: BrowserLaunchRequest) -> BrowserLaunchResponse:
        try:
            info = launch_debug_browser(
                port=request.port,
                url=request.url,
                proxy=request.proxy or settings.browser_proxy,
                proxy_bypass=settings.browser_proxy_bypass,
                auto_proxy=not request.no_proxy,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return BrowserLaunchResponse(**info)

    router.post("/tools/discovery/launch", response_model=DiscoveryToolResponse)(discovery_launch)
    router.get("/system/clock", response_model=ClockStatus)(get_clock)
    router.post("/system/clock/sync", response_model=ClockSyncResult)(post_clock_sync)
    router.post("/preflight", response_model=PreflightResponse)(preflight)

    return router
