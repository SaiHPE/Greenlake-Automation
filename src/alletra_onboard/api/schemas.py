from __future__ import annotations

from pydantic import BaseModel, Field

from alletra_onboard.application.health import GreenLakeCheckReport
from alletra_onboard.domain.models import ArrayWorkItem, PreflightReport, RunEvent, RunRecord


class HealthResponse(BaseModel):
    status: str = "ok"


# ------------------------------------------------------------------ config

class ConfigureRequest(BaseModel):
    gl_client_id: str | None = None
    gl_client_secret: str | None = None
    gl_token_url: str | None = None
    gl_base_url: str | None = None
    gl_member_workspace_id: str | None = None


class ConfigStatusResponse(BaseModel):
    configured: bool
    values: dict[str, str]  # GL_* keys, secret masked


class CheckResponse(BaseModel):
    report: GreenLakeCheckReport


# ------------------------------------------------------------------ runs

class CreateRunRequest(BaseModel):
    work_item: ArrayWorkItem


class RunResponse(BaseModel):
    run: RunRecord


class RunDetailResponse(BaseModel):
    run: RunRecord
    # SecretStr fields serialize masked ('**********') — safe to return to the UI.
    work_item: ArrayWorkItem | None = None


class RunListResponse(BaseModel):
    runs: list[RunRecord]


class EventListResponse(BaseModel):
    events: list[RunEvent]


# ------------------------------------------------------------------ steps

class ProvisionStepRequest(BaseModel):
    dry_run: bool = False


class CloudinitStepRequest(BaseModel):
    cloudinit_url: str | None = Field(
        default=None,
        description="Fresh https://169.254.x.x/cloudinit URL from the Discovery Tool; "
        "overrides the work item's stored value (the link-local IP changes per boot).",
    )
    auto_submit: bool = Field(
        default=True,
        description="Product flow: the operator reviews the values in the web app, then the "
        "automation fills + Submits in one motion (the on-array wizard decays typed Network "
        "values on idle). A guard re-verifies the Review screen and refuses to submit a wrong IP.",
    )


class DsccStepRequest(BaseModel):
    cdp_url: str = Field(
        default="http://localhost:9222",
        description="CDP URL of the operator's logged-in debug Chrome (see /browser/launch).",
    )


# ------------------------------------------------------------------ browser

class BrowserLaunchRequest(BaseModel):
    port: int = 9222
    url: str | None = None  # e.g. the DSCC console URL or a cloudinit URL
    proxy: str | None = None  # override; default applies BROWSER_PROXY / HTTPS_PROXY
    no_proxy: bool = False  # force a direct connection


class BrowserLaunchResponse(BaseModel):
    cdp_url: str
    profile_dir: str
    executable: str
    proxy: str = ""


class DiscoveryToolResponse(BaseModel):
    launched: bool
    path: str | None = None
    searched: list[str] = []
    error: str | None = None


# ------------------------------------------------------------------ preflight (existing)

class PreflightRequest(BaseModel):
    work_item: ArrayWorkItem
    live_greenlake: bool = False


class PreflightResponse(BaseModel):
    report: PreflightReport
