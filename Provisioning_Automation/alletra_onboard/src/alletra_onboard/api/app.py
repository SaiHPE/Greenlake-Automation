from __future__ import annotations

from fastapi import FastAPI, HTTPException

from alletra_onboard.api.schemas import (
    CreateRunRequest,
    CreateRunResponse,
    HealthResponse,
    PreflightRequest,
    PreflightResponse,
    RunListResponse,
)
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.application.run_service import RunService
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.config import load_settings


def create_app() -> FastAPI:
    settings = load_settings()
    store = SqliteRunStore(settings.state_database_path)
    store.initialize()
    runs = RunService(store)
    preflight_service = PreflightService(settings)
    app = FastAPI(title="Alletra Onboard", version="0.1.0")

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse()

    @app.post("/runs", response_model=CreateRunResponse)
    async def create_run(request: CreateRunRequest) -> CreateRunResponse:
        return CreateRunResponse(run=runs.create_run(request.serial_number))

    @app.get("/runs", response_model=RunListResponse)
    async def list_runs() -> RunListResponse:
        return RunListResponse(runs=store.list_runs())

    @app.post("/preflight", response_model=PreflightResponse)
    async def preflight(request: PreflightRequest) -> PreflightResponse:
        return PreflightResponse(report=preflight_service.run_local(request.work_item))

    @app.get("/runs/{run_id}", response_model=CreateRunResponse)
    async def get_run(run_id: str) -> CreateRunResponse:
        run = store.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run not found")
        return CreateRunResponse(run=run)

    return app


app = create_app()
