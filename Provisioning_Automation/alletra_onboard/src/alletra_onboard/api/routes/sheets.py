"""Work-item CSV and initialisation workbook intake routes."""

from __future__ import annotations

import base64
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import ValidationError

from alletra_onboard.api.schemas import (
    CsvParseRequest,
    InitSheetComposeRequest,
    InitSheetComposeResponse,
    InitSheetUploadRequest,
    InitSheetUploadResponse,
)
from alletra_onboard.application.platform.configuring import update_gl_credentials
from alletra_onboard.application.platform.init_sheet import (
    build_template_bytes,
    compose_workbook_bytes,
    parse_upload,
    parse_workbook_bytes,
)
from alletra_onboard.application.platform.intake import csv_template, load_work_items_csv_text
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import load_settings
from alletra_onboard.domain.models import RunMode

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


async def work_item_template() -> PlainTextResponse:
    return PlainTextResponse(
        csv_template(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="arrays.csv"'},
    )


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


async def init_sheet_template() -> Response:
    # The Initialization accelerator ships an onboarding-only sheet (no Provisioning tab).
    return Response(
        content=build_template_bytes(init_only=load_settings().init_only),
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": 'attachment; filename="Initialisation_sheet.xlsx"'},
    )


async def init_sheet_compose(request: InitSheetComposeRequest) -> InitSheetComposeResponse:
    # SPEC-006 R3: the session runner's sheets. Nothing is held server-side; the caller uploads
    # the result through /init-sheet/upload like any operator sheet.
    try:
        base = base64.b64decode(request.base_b64) if request.base_b64 else None
        content = compose_workbook_bytes(
            base=base, init=request.init, targets=request.targets,
            volumes=request.volumes, hostsets=request.hostsets, hosts=request.hosts,
            replication=request.replication, migration=request.migration, snapshots=request.snapshots,
            iscsi_network=request.iscsi_network, peer_ports=request.peer_ports,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return InitSheetComposeResponse(content_b64=base64.b64encode(content).decode("ascii"))


def build_sheets_router(service: OnboardingService, env_path: Path) -> APIRouter:
    router = APIRouter()
    router.get("/work-items/template", response_class=PlainTextResponse)(work_item_template)
    router.post("/work-items/parse")(parse_work_items)
    router.get("/init-sheet/template")(init_sheet_template)
    router.post("/init-sheet/compose", response_model=InitSheetComposeResponse)(init_sheet_compose)

    @router.post("/init-sheet/upload", response_model=InitSheetUploadResponse)
    async def init_sheet_upload(request: InitSheetUploadRequest) -> InitSheetUploadResponse:
        # The sheet is COMPLETE intake, uploaded before a mode is chosen (ADR 0005 revision): save
        # GreenLake creds and HOLD the parsed sheet server-side. No run yet — picking a mode (POST
        # /runs/from-sheet) mints it. Device passwords never leave the server. Only a problem in what
        # initialising the array needs refuses the upload; a problem in another tab is listed and stops
        # only a run whose steps use that tab (owner, 2026-11-19).
        # The init-only accelerator validates ONBOARDING fields only (no Provisioning tab).
        try:
            raw = base64.b64decode(request.content_b64, validate=True)
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=422, detail="Upload was not valid base64") from exc
        problems: list[str] = []
        try:
            if load_settings().init_only:
                parsed = parse_workbook_bytes(raw, mode=RunMode.FULL_ONBOARDING)
            else:
                parsed, problems = parse_upload(raw)
        except Exception as exc:
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
        token = service.stash_pending_sheet(parsed.work_item, parsed.provisioning_intent, raw if problems else None)
        data = parsed.work_item.model_dump(mode="json")
        data["subscription_key"] = parsed.work_item.subscription_key.get_secret_value()
        data["dscc_setup"].pop("password", None)  # never echo the admin password to the UI
        targets: dict[str, str] = {}
        ports: list[str] = []
        snapshot_rows: list[str] = []
        if parsed.provisioning_intent is not None:
            intent = parsed.provisioning_intent
            for key, ep in (("array", intent.array), ("vcenter", intent.vcenter),
                            ("switch_f1", intent.switch_f1), ("switch_f2", intent.switch_f2)):
                targets[f"{key}_host"], targets[f"{key}_user"] = ep.host, ep.username
            if intent.replication is not None:
                targets["peer_host"], targets["peer_user"] = intent.replication.peer.host, intent.replication.peer.username
                ports = [f"{'this array' if r.side == 'A' else 'peer'} {r.nsp} {r.ip}" for r in intent.replication.network]
            if intent.snapshots is not None:
                snapshot_rows = [f"{r.source}: {r.summary(named=True)}" for r in intent.snapshots.requests]
        return InitSheetUploadResponse(
            token=token, work_item=data, credentials_saved=credentials_saved, targets=targets, replication_ports=ports,
            snapshot_rows=snapshot_rows, problems=problems,
        )

    return router
