from __future__ import annotations

from pydantic import BaseModel

from alletra_onboard.domain.models import ArrayWorkItem, PreflightReport, RunRecord


class HealthResponse(BaseModel):
    status: str = "ok"


class CreateRunRequest(BaseModel):
    serial_number: str


class CreateRunResponse(BaseModel):
    run: RunRecord


class RunListResponse(BaseModel):
    runs: list[RunRecord]


class PreflightRequest(BaseModel):
    work_item: ArrayWorkItem
    live_greenlake: bool = False


class PreflightResponse(BaseModel):
    report: PreflightReport
