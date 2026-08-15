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
import base64
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from alletra_onboard.adapters.browser.debug_browser import launch_debug_browser
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.adapters.system.clock import ClockStatus, ClockSyncResult, clock_status, sync_clock
from alletra_onboard.adapters.system.discovery_tool import launch_discovery_tool
from alletra_onboard.api.schemas import (
    AsBuiltStepRequest,
    BrowserLaunchRequest,
    BrowserLaunchResponse,
    CheckResponse,
    CloudinitStepRequest,
    ConfigStatusResponse,
    ConfigureRequest,
    ConnectivityResponse,
    ConnectivityResultItem,
    CreateRunRequest,
    DiscoveryToolResponse,
    DsccStepRequest,
    FirewallRule,
    FirewallRulesResponse,
    InitSheetUploadRequest,
    InitSheetUploadResponse,
    VerifyStepRequest,
    EventListResponse,
    HealthResponse,
    PreflightRequest,
    PreflightResponse,
    ProvisionStepRequest,
    ProxySaveRequest,
    ProxyStatusResponse,
    RunDetailResponse,
    RunFromSheetRequest,
    RunListResponse,
    RunResponse,
)
from alletra_onboard.application.platform.configuring import (
    masked_gl_credentials,
    set_env_values,
    update_gl_credentials,
)
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.onboarding.health import greenlake_check
from alletra_onboard.application.platform.init_sheet import build_template_bytes, parse_workbook_bytes
from alletra_onboard.application.platform.proxy import ProxyResolver, apply_proxy_env, detect_system_proxy
from alletra_onboard.domain.models import RunMode
from alletra_onboard.domain.provisioning import (
    PreflightReport,
    ProvisioningBuilder,
    ProvisioningComposition,
    ProvisioningObjects,
)
from alletra_onboard.domain.workflow import STEP_REGISTRY, mode_steps
from alletra_onboard.domain.zoning import ZoningPlan
from alletra_onboard.application.provisioning.zoning_plan import render_commands


def _wsapi_capability() -> dict:
    """Whether this build (frozen or not) actually imported the 3PAR SDK — and if not, WHY."""
    from alletra_onboard.adapters.array.wsapi_client import HPE3ParClient, SDK_IMPORT_ERROR

    return {"wsapi_sdk": HPE3ParClient is not None, "wsapi_sdk_error": SDK_IMPORT_ERROR}
from alletra_onboard import __version__
from alletra_onboard.application.platform.intake import csv_template, load_work_items_csv_text
from alletra_onboard.application.service import (
    OnboardingService,
    PendingSheetNotFoundError,
    RunBusyError,
    RunNotFoundError,
    StepPreconditionError,
)
from alletra_onboard.application.platform import prereqs
from alletra_onboard.application.onboarding.preflight_service import PreflightService
from alletra_onboard.config import load_settings

SSE_HEARTBEAT_S = 15.0


class CsvParseRequest(BaseModel):
    csv_text: str


class ZoningRenderRequest(BaseModel):
    """Render the read-only zoning command preview: the plan the UI already holds (from the
    zoning.plan event), the operator's alias names, and the operator's SELECTED pairs. Pure and
    stateless — rendering lives in the backend so the frontend never mirrors the command grammar
    (a hand-synced mirror of render_commands drifted once already)."""

    plan: ZoningPlan
    aliases: dict[str, str] = {}
    selected_pairs: list[tuple[str, str]] = []


class ZoningRenderResponse(BaseModel):
    commands: dict[str, list[str]]


def create_app(service: OnboardingService | None = None) -> FastAPI:
    settings = load_settings()
    # Publish the effective proxy (manual override, else the auto-detected system proxy) to the process
    # env so httpx (GreenLake/clock) and the launched browser go through it — like the browser. ADR 0008.
    apply_proxy_env(settings.alletra_proxy)
    if service is None:
        store = SqliteRunStore(settings.state_database_path)
        store.initialize()
        service = OnboardingService(settings, store, InMemoryEventBus())
    env_path = Path(".env")

    app = FastAPI(title="Alletra Onboard", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # vite dev server
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _ui_cache_policy(request, call_next):
        # Every release serves from the same origin (127.0.0.1:8765), and without a policy the
        # browser caches index.html AND the old hashed bundle it references — so after an upgrade
        # the operator keeps seeing the previous interface until a hard refresh (seen live on the
        # v0.13.0 candidates). index.html must always be revalidated; the hashed assets it names
        # are immutable and can be cached forever.
        response = await call_next(request)
        path = request.url.path
        if path in ("/", "/index.html"):
            response.headers["Cache-Control"] = "no-cache"
        elif path.startswith("/assets/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    def _get_run_or_404(run_id: str):
        try:
            return service.get_run(run_id)
        except RunNotFoundError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    # ------------------------------------------------------------------ health + config

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/app/profile")
    async def app_profile() -> dict:
        # The UI reads this to brand itself + restrict the mode chooser: "full" shows all modes;
        # "init-only" (the Alletra MP Initialization accelerator) shows Initialization only.
        # It ALSO serves the step registry + mode presets — the single source of truth the wizard
        # renders from (ADR 0011 Phase 2; kills the hand-synced frontend mirror).
        settings = load_settings()
        return {
            "profile": settings.alletra_profile,
            "init_only": settings.init_only,
            "title": settings.app_title,
            "steps": [
                {"key": s.key, "label": s.label, "kind": s.kind, "phase": s.phase.value}
                for s in STEP_REGISTRY
            ],
            "modes": {mode.value: list(keys) for mode, keys in mode_steps().items()},
            # Optional-dependency capabilities of THIS build. wsapi_client imports the 3PAR SDK in
            # a guarded try/except, so a frozen build that failed to bundle it degrades silently to
            # "python-3parclient is not available in this build" the first time WSAPI is touched —
            # which is how every exe before v0.14.0-rc.2 shipped without anyone noticing (the
            # preflight was the first packaged feature to call WSAPI). Reporting it here makes a
            # packaging regression visible on ANY build with one request, no array needed.
            "capabilities": _wsapi_capability(),
        }

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

    # ------------------------------------------------------------------ prerequisites

    @app.get("/prereqs/firewall", response_model=FirewallRulesResponse)
    async def prereq_firewall(region: str = "jp1") -> FirewallRulesResponse:
        rules = [
            FirewallRule(fqdn=fqdn, port=port, initiator=initiator, purpose=purpose)
            for fqdn, port, initiator, purpose in prereqs.rules_for(region)
        ]
        return FirewallRulesResponse(region=region, rules=rules)

    @app.get("/prereqs/firewall.txt", response_class=PlainTextResponse)
    async def prereq_firewall_txt(region: str = "jp1") -> PlainTextResponse:
        return PlainTextResponse(
            prereqs.firewall_text(region),
            media_type="text/plain",
            headers={"Content-Disposition": 'attachment; filename="alletra-firewall-requirements.txt"'},
        )

    @app.get("/prereqs/connectivity", response_model=ConnectivityResponse)
    async def prereq_connectivity(region: str = "jp1") -> ConnectivityResponse:
        # Reachability to the HPE endpoints via the SAME path the tool uses: through the effective
        # proxy (auto-detected system proxy or the manual override) if any, else direct.
        manual = load_settings().alletra_proxy
        results = await prereqs.check_connectivity(region, manual_proxy=manual)
        items = [
            ConnectivityResultItem(host=r.host, port=r.port, reachable=r.reachable, detail=r.detail, via=r.via)
            for r in results
        ]
        effective = ProxyResolver(manual).for_url("https://common.cloud.hpe.com")
        return ConnectivityResponse(
            region=region, results=items, all_reachable=all(i.reachable for i in items), proxy=effective
        )

    @app.get("/prereqs/proxy", response_model=ProxyStatusResponse)
    async def prereq_proxy_status() -> ProxyStatusResponse:
        manual = load_settings().alletra_proxy or None
        detected = detect_system_proxy("https://common.cloud.hpe.com")
        effective = ProxyResolver(manual).for_url("https://common.cloud.hpe.com")
        source = "manual" if manual else ("system" if detected else "direct")
        return ProxyStatusResponse(detected=detected, manual=manual, effective=effective, source=source)

    @app.post("/prereqs/proxy", response_model=ProxyStatusResponse)
    async def prereq_proxy_save(request: ProxySaveRequest) -> ProxyStatusResponse:
        # os.environ is the source of truth for the running process (pydantic reads it); .env persists
        # a set across restarts. Then re-publish the effective proxy for httpx + browser.
        value = (request.proxy or "").strip()
        os.environ["ALLETRA_PROXY"] = value
        if value:
            set_env_values(env_path, {"ALLETRA_PROXY": value})
        apply_proxy_env(value or None)
        return await prereq_proxy_status()

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

    # ------------------------------------------------------------------ initialisation sheet

    XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    @app.get("/init-sheet/template")
    async def init_sheet_template() -> Response:
        # The Initialization accelerator ships an onboarding-only sheet (no Provisioning tab).
        return Response(
            content=build_template_bytes(init_only=load_settings().init_only),
            media_type=XLSX_MEDIA,
            headers={"Content-Disposition": 'attachment; filename="Initialisation_sheet.xlsx"'},
        )

    @app.post("/init-sheet/upload", response_model=InitSheetUploadResponse)
    async def init_sheet_upload(request: InitSheetUploadRequest) -> InitSheetUploadResponse:
        # The sheet is COMPLETE intake, uploaded before a mode is chosen (ADR 0005 revision): validate
        # the full superset, save GreenLake creds, and HOLD the parsed sheet server-side. No run yet —
        # picking a mode (POST /runs/from-sheet) mints it. Device passwords never leave the server.
        # The init-only accelerator validates ONBOARDING fields only (no Provisioning tab).
        try:
            raw = base64.b64decode(request.content_b64, validate=True)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="Upload was not valid base64") from exc
        try:
            if load_settings().init_only:
                parsed = parse_workbook_bytes(raw, mode=RunMode.FULL_ONBOARDING)
            else:
                parsed = parse_workbook_bytes(raw, complete=True)
        except Exception as exc:  # noqa: BLE001 - bad xlsx / missing fields -> a clear 422
            raise HTTPException(status_code=422, detail=f"Initialisation sheet did not parse: {exc}") from exc

        # Workspace API credentials from the sheet land in the gitignored .env (no manual typing).
        credentials_saved = bool(parsed.gl_client_id and parsed.gl_client_secret)
        if credentials_saved:
            update_gl_credentials(
                env_path,
                {
                    "GL_CLIENT_ID": parsed.gl_client_id,
                    "GL_CLIENT_SECRET": parsed.gl_client_secret,
                    "GL_TOKEN_URL": parsed.gl_token_url,
                },
            )
        token = service.stash_pending_sheet(parsed.work_item, parsed.provisioning_intent)
        data = parsed.work_item.model_dump(mode="json")
        data["subscription_key"] = parsed.work_item.subscription_key.get_secret_value()
        data["dscc_setup"].pop("password", None)  # never echo the admin password to the UI
        return InitSheetUploadResponse(token=token, work_item=data, credentials_saved=credentials_saved)

    # ------------------------------------------------------------------ runs + steps

    @app.post("/runs", response_model=RunResponse)
    async def create_run(request: CreateRunRequest) -> RunResponse:
        return RunResponse(
            run=service.create_run(
                request.work_item, mode=request.mode, selected_steps=request.selected_steps
            )
        )

    @app.post("/runs/from-sheet", response_model=RunResponse)
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
        return RunResponse(run=run)

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
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except RunNotFoundError as exc:
            # e.g. a provisioning step on a run that has no provisioning intent
            raise HTTPException(status_code=404, detail=str(exc) or "not found") from exc

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

    @app.post("/runs/{run_id}/verify", response_model=RunResponse)
    async def run_verify(run_id: str, request: VerifyStepRequest) -> RunResponse:
        # Post-init read-only SSH verification of the array config. Password is used for the SSH
        # session only — never stored. Never changes the run's COMPLETE/SUCCEEDED status.
        return _start_step(
            run_id,
            lambda: service.start_verify(run_id, username=request.username, password=request.password),
        )

    @app.post("/runs/{run_id}/asbuilt", response_model=RunResponse)
    async def run_asbuilt(run_id: str, request: AsBuiltStepRequest) -> RunResponse:
        # Read-only: SSH the array (show*/checkhealth/showinventory -csvtable) and build the as-built
        # .docx. Password is used for the SSH session only. Download it from /asbuilt/download.
        return _start_step(
            run_id,
            lambda: service.start_asbuilt(
                run_id, username=request.username, password=request.password,
                customer=request.customer, site=request.site,
            ),
        )

    @app.get("/runs/{run_id}/asbuilt/download")
    async def download_asbuilt(run_id: str) -> Response:
        _get_run_or_404(run_id)
        data = service.get_asbuilt(run_id)
        if data is None:
            raise HTTPException(status_code=404, detail="No as-built generated yet — run the as-built step first.")
        serial = service.get_work_item(run_id).serial_number
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="as-built-{serial}.docx"'},
        )

    @app.post("/runs/{run_id}/complete", response_model=RunResponse)
    async def complete_run(run_id: str) -> RunResponse:
        _get_run_or_404(run_id)
        return RunResponse(run=service.mark_complete(run_id))

    # ------------------------------------------------------------------ storage provisioning (Phase 2)

    @app.post("/runs/{run_id}/discover", response_model=RunResponse)
    async def run_discover(run_id: str) -> RunResponse:
        return _start_step(run_id, lambda: service.start_discover(run_id))

    @app.post("/runs/{run_id}/zoning/preview", response_model=RunResponse)
    async def run_zoning_preview(run_id: str) -> RunResponse:
        return _start_step(run_id, lambda: service.start_zoning_preview(run_id))

    @app.post("/runs/{run_id}/zoning/plan", response_model=RunResponse)
    async def run_zoning_plan(run_id: str) -> RunResponse:
        # Read-only: reads both fabric switches to build the zoning plan; makes NO switch writes.
        return _start_step(run_id, lambda: service.start_zoning_plan(run_id))

    @app.post("/zoning/render", response_model=ZoningRenderResponse)
    async def zoning_render(request: ZoningRenderRequest) -> ZoningRenderResponse:
        # Pure + stateless: assemble the read-only command preview from the plan + the operator's
        # aliases and selected pairs. The tool never RUNS these commands (ADR 0004) — this is the
        # script the SAN team applies by hand.
        return ZoningRenderResponse(
            commands=render_commands(request.plan, request.aliases, request.selected_pairs)
        )

    @app.get("/runs/{run_id}/storage/preflight", response_model=PreflightReport)
    async def storage_preflight(run_id: str) -> PreflightReport:
        # Read-only readiness of the array + vCenter the sheet points at, so a missing prerequisite is
        # named BEFORE discovery runs instead of surfacing as a failed step. Makes no writes.
        _get_run_or_404(run_id)
        try:
            return await asyncio.to_thread(service.get_storage_preflight, run_id)
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/runs/{run_id}/storage/objects", response_model=ProvisioningObjects)
    async def storage_objects(run_id: str) -> ProvisioningObjects:
        # The dropdown palette (existing array objects + to-be-created + discovered hosts). Reads the
        # array over WSAPI, so run it off the event loop.
        _get_run_or_404(run_id)
        try:
            return await asyncio.to_thread(service.get_storage_objects, run_id)
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/runs/{run_id}/storage/builder", response_model=ProvisioningComposition)
    async def storage_builder(run_id: str, request: ProvisioningBuilder) -> ProvisioningComposition:
        # Save the operator-composed host-set membership + VV-set membership + exports onto the intent.
        _get_run_or_404(run_id)
        try:
            return service.set_provisioning_builder(run_id, request)
        except StepPreconditionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/runs/{run_id}/storage/preview", response_model=RunResponse)
    async def run_storage_preview(run_id: str) -> RunResponse:
        return _start_step(run_id, lambda: service.start_storage_preview(run_id))

    @app.post("/runs/{run_id}/storage/apply", response_model=RunResponse)
    async def run_storage_apply(run_id: str) -> RunResponse:
        # Creates host/volumes/exports on the array — the UI must preview + confirm first.
        return _start_step(run_id, lambda: service.start_storage_apply(run_id))

    @app.post("/runs/{run_id}/storage/verify-paths", response_model=RunResponse)
    async def run_storage_verify_paths(run_id: str) -> RunResponse:
        # Tier-2, read-only: reads showvlun -a and reports per-host path liveness. Never gates.
        return _start_step(run_id, lambda: service.start_path_verify(run_id))

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

    @app.post("/tools/discovery/launch", response_model=DiscoveryToolResponse)
    async def discovery_launch() -> DiscoveryToolResponse:
        # Runs on the jump box; opens the on-Desktop HPE Discovery Tool .exe for the operator.
        return DiscoveryToolResponse(**launch_discovery_tool())

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

    # Serve the built frontend when present (single-host product mode). Frozen .exe first
    # (PyInstaller extracts data under sys._MEIPASS), then the working directory, then the
    # package root (editable install layout).
    dist_candidates = [Path("frontend/dist"), Path(__file__).resolve().parents[3] / "frontend" / "dist"]
    if getattr(sys, "frozen", False):
        dist_candidates.insert(0, Path(getattr(sys, "_MEIPASS", ".")) / "frontend" / "dist")
    for dist in dist_candidates:
        if dist.is_dir():
            app.mount("/", StaticFiles(directory=str(dist), html=True), name="ui")
            break

    return app


app = create_app()
