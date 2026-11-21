"""FastAPI backend for the operator frontend.

Exposes the onboarding flow the UI drives:

    POST /config            store GreenLake credentials      GET /config       masked values
    POST /config/check      live GreenLake readiness check
    GET  /work-items/template                                POST /work-items/parse
    POST /runs              create a run from a work item    GET /runs, /runs/{id}
    POST /runs/{id}/provision | /cloudinit | /dscc | /complete      (the A -> B -> C steps;
                            /provision is GreenLake device registration, not storage provisioning)
    GET  /runs/{id}/events  stored timeline                  GET /runs/{id}/stream   live SSE
    GET  /runs/{id}/trust   devices the run trusts           POST /runs/{id}/trust/retrust
    POST /browser/launch    CDP debug Chrome for the attach-mode wizards

Steps run as background tasks (see OnboardingService); the UI follows along via SSE.
When frontend/dist exists it is served at / (the packaged single-host product).
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from alletra_onboard import __version__
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.routes.console import build_console_router
from alletra_onboard.api.routes.discovery import build_discovery_router
from alletra_onboard.api.routes.documents import build_documents_router
from alletra_onboard.api.routes.events import build_events_router
from alletra_onboard.api.routes.onboarding import build_onboarding_router
from alletra_onboard.api.routes.prereqs import build_prereqs_router
from alletra_onboard.api.routes.provisioning import build_provisioning_router
from alletra_onboard.api.routes.replication import build_replication_router
from alletra_onboard.api.routes.runs import build_runs_router
from alletra_onboard.api.routes.sheets import build_sheets_router
from alletra_onboard.api.routes.snapshots import build_snapshots_router
from alletra_onboard.api.routes.system import build_system_router
from alletra_onboard.api.routes.trust import build_trust_router
from alletra_onboard.api.routes.zoning import build_zoning_router
from alletra_onboard.api.schemas import HealthResponse, app_profile_model
from alletra_onboard.application.platform.proxy import apply_proxy_env
from alletra_onboard.application.provisioning.clients import wsapi_capability
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import load_settings
from alletra_onboard.domain.ports import StoredCredentialsUnreadableError
from alletra_onboard.domain.workflow import NOT_BUILT_STEPS, STEP_REGISTRY, mode_steps


async def _ui_cache_policy(request: Request, call_next):
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


async def _credentials_unreadable(_request: Request, exc: Exception) -> JSONResponse:
    # ADR 0027: the run's secrets were encrypted with a key this installation does not hold.
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def health() -> HealthResponse:
    return HealthResponse(version=__version__)


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
        # `unavailable` is the sentence for a step whose work is not built yet ("" otherwise): the
        # mode chooser greys out every mode that includes it, and minting such a run is refused.
        "steps": [
            {"key": s.key, "label": s.label, "kind": s.kind, "phase": s.phase.value,
             "unavailable": NOT_BUILT_STEPS.get(s.key, "")}
            for s in STEP_REGISTRY
        ],
        "modes": {mode.value: list(keys) for mode, keys in mode_steps().items()},
        # Optional-dependency capabilities of THIS build. wsapi_client imports the 3PAR SDK in
        # a guarded try/except, so a frozen build that failed to bundle it degrades silently to
        # "python-3parclient is not available in this build" the first time WSAPI is touched —
        # which is how every exe before v0.14.0-rc.2 shipped without anyone noticing (the
        # preflight was the first packaged feature to call WSAPI). Reporting it here makes a
        # packaging regression visible on ANY build with one request, no array needed.
        "capabilities": wsapi_capability(),
    }


def _mount_frontend(app: FastAPI) -> None:
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
    app.middleware("http")(_ui_cache_policy)
    app.add_exception_handler(StoredCredentialsUnreadableError, _credentials_unreadable)

    app.get("/health", response_model=HealthResponse)(health)
    app.get("/app/profile", responses={200: {"model": app_profile_model()}})(app_profile)

    for router in (
        build_prereqs_router(env_path),
        build_sheets_router(service, env_path),
        build_runs_router(service),
        build_onboarding_router(service),
        build_documents_router(service),
        build_discovery_router(service),
        build_zoning_router(service),
        build_provisioning_router(service),
        build_replication_router(service),
        build_snapshots_router(service),
        build_trust_router(service),
        build_events_router(service),
        build_console_router(service),
        build_system_router(settings),
    ):
        app.include_router(router)

    _mount_frontend(app)
    return app


app = create_app()
