from __future__ import annotations

import functools
import operator
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, create_model

from alletra_onboard.application.onboarding.health import GreenLakeCheckReport
from alletra_onboard.domain.events import EVENT_TYPES
from alletra_onboard.domain.models import (
    ArrayCredentialInfo,
    ArrayWorkItem,
    PreflightReport,
    RunEvent,
    RunMode,
    RunRecord,
)
from alletra_onboard.domain.network import IscsiVlanRequest
from alletra_onboard.domain.peer_ports import PeerPortIntent
from alletra_onboard.domain.trust import DevicePinInfo, TrustKind
from alletra_onboard.domain.zoning import ZoningPlan


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""   # SPEC-006 R1: the session report names the build it tested


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
    mode: RunMode = RunMode.FULL_ONBOARDING
    selected_steps: list[str] = Field(default_factory=list)


class RunResponse(BaseModel):
    run: RunRecord


class ArrayPortsResponse(BaseModel):
    """The Array ports step's inputs: the sheet's iSCSI network rows and Peer ports rows, and whether each
    plan the page last showed is still held (a new read, a sheet change or a restart withdraws it, LESSONS 6)."""

    iscsi_network: list[IscsiVlanRequest] = Field(default_factory=list)
    iscsi_plan_held: bool = False
    peer_ports: PeerPortIntent | None = None
    peer_plan_held: bool = False


class RunDetailResponse(BaseModel):
    run: RunRecord
    # SecretStr fields serialize masked ('**********') — safe to return to the UI.
    work_item: ArrayWorkItem | None = None
    # ADR 0013 / SPEC-008 R3: whether the run holds an array credential, and whose — never the password.
    array_credential: ArrayCredentialInfo | None = None


class RunListResponse(BaseModel):
    runs: list[RunRecord]


class EventListResponse(BaseModel):
    events: list[RunEvent]


def run_event_list() -> type[BaseModel]:
    """What /runs/{id}/events returns and each frame of /runs/{id}/stream carries: the stored event
    with `data` typed by `event_type`. Documentation only; stored events are served as they are."""
    by_data: dict[type[BaseModel], list[str]] = {}
    for event in EVENT_TYPES.values():
        by_data.setdefault(event.data, []).append(event.name)
    lit: Any = Literal
    ann: Any = Annotated
    lst: Any = list
    variants: list[Any] = []
    for data, names in by_data.items():
        fields: dict[str, Any] = {
            "event_type": (lit[tuple(names)], ...),
            "data": (data, ...),
        }
        variants.append(create_model(f"{data.__name__.removesuffix('Data')}Event", __base__=RunEvent, **fields))
    event_union: Any = functools.reduce(operator.or_, variants)
    item_type: Any = ann[event_union, Field(discriminator="event_type")]
    list_fields: dict[str, Any] = {"events": (lst[item_type], ...)}
    return create_model("RunEventList", **list_fields)


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


class VerifyStepRequest(BaseModel):
    # SPEC-008 R2 (ADR 0013): both optional — given together they override the run's own array credential.
    username: str | None = Field(default=None, description="Array admin username override (e.g. 3paradm).")
    password: str | None = Field(default=None, description="Array admin password override — used for this SSH session only.")


class AsBuiltStepRequest(BaseModel):
    username: str | None = Field(default=None, description="Array admin username override (e.g. 3paradm).")
    password: str | None = Field(default=None, description="Array admin password override — used for this SSH session only.")
    customer: str = Field(default="", description="Customer name for the as-built cover page (overrides the sheet value).")
    site: str = Field(default="", description="Deployment site/location (optional; the array doesn't store it).")
    application_workload: str = Field(default="", description="Application/workload the array serves, e.g. 'VMware vSphere cluster' (overrides the sheet value).")
    purpose: str = Field(default="", description="Why block storage is used here, e.g. 'primary datastore for the vault zone' (overrides the sheet value).")


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


# ------------------------------------------------------------------ initialisation sheet

class InitSheetUploadRequest(BaseModel):
    # The sheet is COMPLETE intake, uploaded BEFORE a mode is chosen (ADR 0005 revision), so no
    # mode/steps here — the upload validates the full superset and holds the sheet server-side.
    content_b64: str = Field(description="Base64-encoded Initialisation_sheet.xlsx contents.")


class InitSheetComposeRequest(BaseModel):
    """SPEC-006 R3: a filled sheet from JSON, so a script never writes xlsx. `base_b64` is the
    operator's working sheet (credentials and init fields come from it); a row table given REPLACES
    that tab's rows; one not given is left alone."""

    base_b64: str | None = None
    init: dict[str, str] = Field(default_factory=dict)
    targets: dict[str, str] = Field(default_factory=dict)
    volumes: list[dict[str, str]] | None = None
    hostsets: list[dict[str, str]] | None = None
    hosts: list[dict[str, str]] | None = None
    # SPEC-015 R6: {"fields": {peer_host, peer_user, peer_password, rtt_ms, …}, "rows": [{vvset, mode, …}]}
    replication: dict | None = None
    # SPEC-027 R1: {"fields": {source_host, source_user, source_password, orchestration}, "rows": [{host, type, cpg, provisioning}]}
    migration: dict | None = None
    # SPEC-023 R1: the Snapshots tab's rows, [{source, kind, snapshot_now, every, unit, …}]
    snapshots: list[dict[str, str]] | None = None
    # SPEC-024 R1: the iSCSI network tab's rows, [{port, vlan, ip, netmask, gateway}]
    iscsi_network: list[dict[str, str]] | None = None
    # SPEC-025 R1: the Peer ports tab's rows, [{port, source_wwpns}]
    peer_ports: list[dict[str, str]] | None = None


class InitSheetComposeResponse(BaseModel):
    content_b64: str
    filename: str = "Initialisation_sheet.xlsx"


class InitSheetUploadResponse(BaseModel):
    # A single-use token for the held sheet; the run is minted later from this token + the chosen mode.
    token: str
    # The parsed work item for review (subscription_key shown; admin password / device passwords never echoed).
    work_item: dict
    credentials_saved: bool = True
    # SPEC-006 R1: the Provisioning tab's endpoints WITHOUT passwords (host + username per device), so a
    # script driving the API learns the array from the sheet rather than from a parameter.
    targets: dict[str, str] = Field(default_factory=dict)
    # SPEC-021 R1: the Replication network tab's rows, one line each ("this array 0:4:4 10.93.18.11"), for review.
    replication_ports: list[str] = Field(default_factory=list)
    # SPEC-023 R9: the Snapshots tab's rows, one line each, with the schedule a row asks for named
    # ("zz_sn_vvs: Snapshot now · schedule zz_sn_vvs_snap, every 4 hours …"), so the review can say the
    # tab is filled when the chosen mode lacks the step.
    snapshot_rows: list[str] = Field(default_factory=list)
    # Problems in tabs that initialising the array does not use, one sentence each (the sentence that
    # refuses a run whose steps use that tab). Empty for a sheet with none.
    problems: list[str] = Field(default_factory=list)


class RunFromSheetRequest(BaseModel):
    token: str = Field(description="The token returned by /init-sheet/upload for the held sheet.")
    mode: RunMode = Field(default=RunMode.FULL_ONBOARDING, description="The operator-selected slice.")
    selected_steps: list[str] = Field(
        default_factory=list,
        description="Explicit step keys when mode is CUSTOM (else derived from the mode).",
    )


# ------------------------------------------------------------------ preflight

class PreflightRequest(BaseModel):
    work_item: ArrayWorkItem
    live_greenlake: bool = False


class PreflightResponse(BaseModel):
    report: PreflightReport


# ------------------------------------------------------------------ prerequisites

class FirewallRule(BaseModel):
    fqdn: str
    port: str
    initiator: str
    purpose: str


class FirewallRulesResponse(BaseModel):
    region: str
    rules: list[FirewallRule]


class ConnectivityResultItem(BaseModel):
    host: str
    port: int
    reachable: bool
    detail: str
    via: str = ""  # the proxy the test tunnelled through ("" = tested directly)


class ConnectivityResponse(BaseModel):
    region: str
    results: list[ConnectivityResultItem]
    all_reachable: bool
    proxy: str | None = None  # the effective proxy these were tested through (None = direct)


class ProxyStatusResponse(BaseModel):
    detected: str | None = None   # the OS's OWN system proxy (WinINET/PAC/registry), if any
    manual: str | None = None     # the operator's manual override, if set
    effective: str | None = None  # what the tool will actually use (None = direct)
    source: str = "direct"        # "manual" | "system" | "direct"
    # True when the operator explicitly chose to ignore any detected proxy (saved "direct://").
    # Distinct from source == "direct" meaning "nothing was detected".
    forced_direct: bool = False


class ProxySaveRequest(BaseModel):
    # host:port (or user:pass@host:port) to force that proxy; "direct://" to force NO proxy;
    # null/"" to go back to auto-detecting the OS setting.
    proxy: str | None = None


class ConsoleRequest(BaseModel):
    """SPEC-019 R3: one read-only command on the run's array (`array`) or its Replication peer (`peer`)."""

    command: str = Field(min_length=1, max_length=400)
    target: Literal["array", "peer"] = "array"


class ConsoleTerminalRequest(BaseModel):
    target: Literal["array", "peer"] = "array"


class FailoverTestRequest(BaseModel):
    """SPEC-017 R1: blank group = the tool's own test group. A group this run did not create needs its
    name typed back in `confirm`. `authorised` must be True (the operator ticked the confirmation)."""

    group: str | None = None
    confirm: str | None = None
    authorised: bool = False


class LinkCheckRequest(BaseModel):
    """SPEC-020 R2: the client's test length; the tool stops it once the latency is printed."""

    duration_s: int = Field(default=600, ge=300, le=172800)


class StorageApplyRequest(BaseModel):
    """`approved_plan` is the `plan_id` of the plan the operator ticked, from the `storage.previewed`
    event. The server refuses the apply without it, or when it is not the plan it holds."""

    approved_plan: str | None = None


class ReplicationApplyRequest(BaseModel):
    """SPEC-020 R4: `accept_latency` is the operator's 'Continue anyway' when the measured latency is
    over HPE's limit for a mode on the tab. `approved_plan` is the `plan_id` of the plan the operator
    ticked, from the `replication.previewed` event."""

    accept_latency: bool = False
    approved_plan: str | None = None


class TrustedDevicesResponse(BaseModel):
    """ADR 0026: what this run trusts, device by device: fingerprints only, never key material. With a
    device CA bundle set, the TLS devices are checked against it instead of being trusted on first contact."""

    devices: list[DevicePinInfo]
    device_ca_bundle: str | None = None


class RetrustRequest(BaseModel):
    """The operator's re-trust of one device: `fingerprint` is the new one they compared with the
    device's own console. Refused if the device has presented anything else since."""

    kind: TrustKind
    host: str
    port: int
    fingerprint: str


class RetrustResponse(BaseModel):
    device: DevicePinInfo


class SnapshotApplyRequest(BaseModel):
    """`approved_plan` is the `plan_id` of the plan the operator ticked, from the `snapshots.previewed`
    event. The server refuses the apply without it, or when it is not the plan it holds."""

    approved_plan: str | None = None


class SnapshotRow(BaseModel):
    source: str
    kind: str
    schedule: str = ""          # the schedule's name; "" when the row asks for no schedule
    summary: str


class SnapshotsResponse(BaseModel):
    """The Snapshots step's inputs: the tab's rows in words, and the id of the plan the server holds ("" when
    none: a new read, an apply or a restart withdraws it, LESSONS 6)."""

    rows: list[SnapshotRow] = Field(default_factory=list)
    held_plan_id: str = ""


class CsvParseRequest(BaseModel):
    csv_text: str


class ZoningRenderRequest(BaseModel):
    """Render the read-only zoning command preview: the plan the UI already holds (from the
    zoning.plan event), the operator's alias names, and the operator's SELECTED pairs. Rendering
    lives in the backend so the frontend never mirrors the command grammar (a hand-synced mirror of
    render_commands drifted once already). With `run_id` the result is also recorded on the run as
    a `zoning.rendered` event — the command set handed to the SAN team is a deliverable, and the
    as-built (SPEC-002) reproduces it from that record."""

    plan: ZoningPlan
    aliases: dict[str, str] = {}
    selected_pairs: list[tuple[str, str]] = []
    run_id: str | None = None


class ZoningRenderResponse(BaseModel):
    commands: dict[str, list[str]]
    # Selected pairs that could NOT be rendered (a member has no alias name, or a name FOS would
    # reject), per fabric — surfaced so a tick that produces no command explains itself instead of
    # silently disappearing.
    skipped: dict[str, list[str]]
    # Legal-but-non-portable alias names (need FOS 8.1.0+ fabric-wide), per fabric. Advisory only.
    warnings: dict[str, list[str]] = {}
    # SPEC-025 R7: the peer-port block, its own command set per fabric (every pair the sheet asks for).
    peer_commands: dict[str, list[str]] = {}
    peer_skipped: dict[str, list[str]] = {}

