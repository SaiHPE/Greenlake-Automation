"""FastAPI backend for the operator frontend.

Exposes the onboarding flow the UI drives:

    POST /config            store GreenLake credentials      GET /config       masked values
    POST /config/check      live GreenLake readiness check
    GET  /work-items/template                                POST /work-items/parse
    POST /runs              create a run from a work item    GET /runs, /runs/{id}
    POST /runs/{id}/provision | /cloudinit | /dscc | /complete      (the A -> B -> C steps)
    GET  /runs/{id}/events  stored timeline                  GET /runs/{id}/stream   live SSE
    POST /browser/launch    CDP debug Chrome for the attach-mode wizards

Steps run as background tasks (see OnboardingService); the UI follows along via SSE.
When frontend/dist exists it is served at / (the packaged single-host product).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from alletra_onboard.adapters.browser.debug_browser import launch_debug_browser
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.adapters.system.clock import ClockStatus, ClockSyncResult, clock_status, sync_clock
from alletra_onboard.api.schemas import (
    BrowserLaunchRequest,
    BrowserLaunchResponse,
    CheckResponse,
    CloudinitStepRequest,
    ConfigStatusResponse,
    ConfigureRequest,
    CreateRunRequest,
    DsccStepRequest,
    EventListResponse,
    HealthResponse,
    PreflightRequest,
    PreflightResponse,
    ProvisionStepRequest,
    RunDetailResponse,
    RunListResponse,
    RunResponse,
)
from alletra_onboard.application.configuring import masked_gl_credentials, update_gl_credentials
from alletra_onboard.application.event_bus import InMemoryEventBus
from alletra_onboard.application.health import greenlake_check
from alletra_onboard.application.intake import csv_template, load_work_items_csv_text
from alletra_onboard.application.onboarding_service import (
    OnboardingService,
    RunBusyError,
    RunNotFoundError,
)
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.config import load_settings

SSE_HEARTBEAT_S = 15.0


class CsvParseRequest(BaseModel):
    csv_text: str


def create_app(service: OnboardingService | None = None) -> FastAPI:
    settings = load_settings()
    if service is None:
        store = SqliteRunStore(settings.state_database_path)
        store.initialize()
        service = OnboardingService(settings, store, InMemoryEventBus())
    env_path = Path(".env")

    app = FastAPI(title="Alletra Onboard", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # vite dev server
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def _get_run_or_404(run_id: str):
        try:
            return service.get_run(run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    # ------------------------------------------------------------------ health + config

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/config", response_model=ConfigStatusResponse)
    async def get_config() -> ConfigStatusResponse:
        values = masked_gl_credentials(env_path)
        configured = bool(values.get("GL_CLIENT_ID")) and bool(values.get("GL_CLIENT_SECRET"))
        return ConfigStatusResponse(configured=configured, values=values)

    @app.post("/config", response_model=ConfigStatusResponse)
    async def set_config(request: ConfigureRequest) -> ConfigStatusResponse:
        update_gl_credentials(
            env_path,
            {
                "GL_CLIENT_ID": request.gl_client_id,
                "GL_CLIENT_SECRET": request.gl_client_secret,
                "GL_TOKEN_URL": request.gl_token_url,
                "GL_BASE_URL": request.gl_base_url,
                "GL_MEMBER_WORKSPACE_ID": request.gl_member_workspace_id,
            },
        )
        return await get_config()

    @app.post("/config/check", response_model=CheckResponse)
    async def config_check() -> CheckResponse:
        # Re-load settings so credentials saved a moment ago are picked up.
        return CheckResponse(report=await greenlake_check(load_settings()))

    # ------------------------------------------------------------------ work items

    @app.get("/work-items/template", response_class=PlainTextResponse)
    async def work_item_template() -> PlainTextResponse:
        return PlainTextResponse(
            csv_template(),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="arrays.csv"'},
        )

    @app.post("/work-items/parse")
    async def parse_work_items(request: CsvParseRequest) -> dict:
        try:
            items = load_work_items_csv_text(request.csv_text)
        except (ValidationError, KeyError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f"CSV did not parse: {exc}") from exc

        def unmasked(item) -> dict:
            # The values came from the client's own uploaded file; masking them here would
            # break the upload -> editable form -> POST /runs round-trip. Localhost-only API.
            data = item.model_dump(mode="json")
            data["subscription_key"] = item.subscription_key.get_secret_value()
            data["dscc_setup"].pop("password", None)  # never echo a password to the UI
            return data

        return {"work_items": [unmasked(item) for item in items]}

    # ------------------------------------------------------------------ runs + steps

    @app.post("/runs", response_model=RunResponse)
    async def create_run(request: CreateRunRequest) -> RunResponse:
        return RunResponse(run=service.create_run(request.work_item))

    @app.get("/runs", response_model=RunListResponse)
    async def list_runs() -> RunListResponse:
        return RunListResponse(runs=service.list_runs())

    @app.get("/runs/{run_id}", response_model=RunDetailResponse)
    async def get_run(run_id: str) -> RunDetailResponse:
        run = _get_run_or_404(run_id)
        try:
            item = service.get_work_item(run_id)
        except RunNotFoundError:
            item = None
        return RunDetailResponse(run=run, work_item=item)

    def _start_step(run_id: str, start) -> RunResponse:
        _get_run_or_404(run_id)
        try:
            return RunResponse(run=start())
        except RunBusyError as exc:
            raise HTTPException(status_code=409, detail="a step is already running for this run") from exc

    @app.post("/runs/{run_id}/provision", response_model=RunResponse)
    async def run_provision(run_id: str, request: ProvisionStepRequest) -> RunResponse:
        return _start_step(run_id, lambda: service.start_provision(run_id, dry_run=request.dry_run))

    @app.post("/runs/{run_id}/cloudinit", response_model=RunResponse)
    async def run_cloudinit(run_id: str, request: CloudinitStepRequest) -> RunResponse:
        return _start_step(
            run_id,
            lambda: service.start_cloudinit(
                run_id, cloudinit_url=request.cloudinit_url, auto_submit=request.auto_submit
            ),
        )

    @app.post("/runs/{run_id}/dscc", response_model=RunResponse)
    async def run_dscc(run_id: str, request: DsccStepRequest) -> RunResponse:
        return _start_step(run_id, lambda: service.start_dscc(run_id, cdp_url=request.cdp_url))

    @app.post("/runs/{run_id}/complete", response_model=RunResponse)
    async def complete_run(run_id: str) -> RunResponse:
        _get_run_or_404(run_id)
        return RunResponse(run=service.mark_complete(run_id))

    # ------------------------------------------------------------------ events

    @app.get("/runs/{run_id}/events", response_model=EventListResponse)
    async def list_events(run_id: str) -> EventListResponse:
        _get_run_or_404(run_id)
        return EventListResponse(events=service.list_events(run_id))

    @app.get("/runs/{run_id}/stream")
    async def stream_events(run_id: str) -> StreamingResponse:
        _get_run_or_404(run_id)
        queue = service.events.subscribe(run_id)

        async def generate():
            try:
                while True:
                    try:
                        event = await asyncio.wait_for(queue.get(), timeout=SSE_HEARTBEAT_S)
                    except asyncio.TimeoutError:
                        yield ": heartbeat\n\n"  # keeps proxies/browsers from closing the stream
                        continue
                    yield f"data: {event.model_dump_json()}\n\n"
            finally:
                service.events.unsubscribe(run_id, queue)

        return StreamingResponse(generate(), media_type="text/event-stream")

    # ------------------------------------------------------------------ browser + preflight

    @app.post("/browser/launch", response_model=BrowserLaunchResponse)
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

    @app.get("/system/clock", response_model=ClockStatus)
    async def get_clock(url: str | None = None) -> ClockStatus:
        return await clock_status(url)

    @app.post("/system/clock/sync", response_model=ClockSyncResult)
    async def post_clock_sync(url: str | None = None) -> ClockSyncResult:
        try:
            return await sync_clock(url)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (RuntimeError, OSError) as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/preflight", response_model=PreflightResponse)
    async def preflight(request: PreflightRequest) -> PreflightResponse:
        # Fresh settings so credentials entered in Configure after startup are honored.
        report = await PreflightService(load_settings()).run(request.work_item, live_greenlake=request.live_greenlake)
        return PreflightResponse(report=report)

    # Serve the built frontend when present (single-host product mode). Look in the working
    # directory first, then relative to the package root (editable install layout).
    for dist in (Path("frontend/dist"), Path(__file__).resolve().parents[3] / "frontend" / "dist"):
        if dist.is_dir():
            app.mount("/", StaticFiles(directory=str(dist), html=True), name="ui")
            break

    return app


app = create_app()
