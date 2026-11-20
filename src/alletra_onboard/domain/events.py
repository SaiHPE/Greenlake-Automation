"""Registry of run event types and their typed payloads (STANDARD T1, T4).

One table of every `event_type` the backend emits and the pydantic model of its `data`.
`RunCoordinator.emit` takes an `EventType[D]` and a `D`, so pyright checks every emit site.
The OpenAPI schema documents `/runs/{id}/events` as a discriminated union built from this
registry; `RunEvent.data` stays a dict in SQLite and on the bus so stored runs open unchanged.

Evolution rule: a field added to a payload gets a default; a field or event type is never
renamed or given a new meaning (a new meaning gets a new event type).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from alletra_onboard.domain.discovery import DiscoveryReport
from alletra_onboard.domain.models import VerificationReport
from alletra_onboard.domain.network import IscsiNetworkPlan, IscsiVlanRequest, PortNetworkView
from alletra_onboard.domain.peer_ports import (
    PeerPortPlan,
    PeerPortRequest,
    PeerPortResult,
    PeerPortView,
)
from alletra_onboard.domain.provisioning import (
    PathVerification,
    ProvisioningPlan,
    ProvisioningResult,
)
from alletra_onboard.domain.replication import (
    FailoverRecord,
    LinkCheck,
    ReplicationPlan,
    ReplicationReport,
    ReplicationResult,
    ReplicationVerification,
)
from alletra_onboard.domain.snapshots import (
    ArraySchedule,
    SnapshotPlan,
    SnapshotResult,
    SnapshotVerification,
)
from alletra_onboard.domain.trust import DevicePinInfo, TrustKind
from alletra_onboard.domain.zoning import ZoningPlan, ZoningReport


# `dump(payload: D)` puts `D` in a contravariant position alongside `data: type[D]` (covariant),
# so PEP 695 infers `D` as invariant and pyright rejects a wrong payload model at emit sites.
@dataclass(frozen=True)
class EventType[D: BaseModel]:
    name: str
    data: type[D]

    def dump(self, payload: D) -> dict[str, Any]:
        return payload.model_dump(mode="json")


EVENT_TYPES: dict[str, EventType[Any]] = {}


def _event[D: BaseModel](name: str, data: type[D]) -> EventType[D]:
    if name in EVENT_TYPES:
        raise ValueError(f"duplicate event type: {name}")
    entry = EventType(name, data)
    EVENT_TYPES[name] = entry
    return entry


class NoData(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _plain(name: str) -> EventType[NoData]:
    return _event(name, NoData)


class VerifyData(BaseModel):
    report: VerificationReport


class HandoverStatus(BaseModel):
    """SPEC-026 R10: the ``handover`` field of ``asbuilt.generated``. None means not known, never zero."""

    read_at: str | None
    alerts_new: int | None
    alerts_major: int | None  # Major, Critical or Fatal
    oldest_alert: str | None  # the oldest first occurrence, as the array printed it
    cloud_alert: int | None  # the id of the alert saying the array is disconnected from Data Services Cloud Console
    read_errors: dict[str, str]


class AsBuiltData(BaseModel):
    serial: str
    name: str
    customer: str
    size: int
    warnings: list[str]
    handover: HandoverStatus | None = None


class DiscoveryData(BaseModel):
    report: DiscoveryReport


class ZoningCheckData(BaseModel):
    report: ZoningReport


class ZoningPlanData(BaseModel):
    plan: ZoningPlan


class ZoningRenderedData(BaseModel):
    commands: dict[str, list[str]]
    skipped: dict[str, list[str]]
    aliases: dict[str, str]
    selected_pairs: list[tuple[str, str]]
    peer_commands: dict[str, list[str]] = Field(default_factory=dict)


class IscsiSection(BaseModel):
    requests: list[IscsiVlanRequest]
    error: str | None = None
    view: PortNetworkView | None = None
    plan: IscsiNetworkPlan | None = None
    commands_text: str = ""
    removals_text: str = ""
    gateway_text: str = ""


class PeerSection(BaseModel):
    requests: list[PeerPortRequest]
    error: str | None = None
    view: PeerPortView | None = None
    plan: PeerPortPlan | None = None
    result: PeerPortResult | None = None
    removals: list[str] = Field(default_factory=list)
    zones_checked: bool = False
    commands_text: str = ""
    removals_text: str = ""
    result_removals_text: str = ""


class PortsData(BaseModel):
    iscsi: IscsiSection | None = None
    peer: PeerSection | None = None


class StoragePlanData(BaseModel):
    plan: ProvisioningPlan


class StorageResultData(BaseModel):
    result: ProvisioningResult


class PathsData(BaseModel):
    verification: PathVerification


class ReplicationPlanData(BaseModel):
    report: ReplicationReport
    plan: ReplicationPlan


class LinkCheckData(BaseModel):
    link_check: LinkCheck


class ReplicationResultData(BaseModel):
    result: ReplicationResult


class ReplicationVerifyData(BaseModel):
    verification: ReplicationVerification


class FailoverStartData(BaseModel):
    group: str


class FailoverData(BaseModel):
    record: FailoverRecord


class SnapshotArraySummary(BaseModel):
    host: str
    name: str
    os_version: str
    time_zone: str
    retention_max_hours: int
    schedules: list[ArraySchedule]


class SnapshotPlanData(BaseModel):
    array: SnapshotArraySummary
    plan: SnapshotPlan


class SnapshotResultData(BaseModel):
    result: SnapshotResult


class SnapshotVerifyData(BaseModel):
    verification: SnapshotVerification


class DeviceData(BaseModel):
    device: DevicePinInfo


class RetrustData(BaseModel):
    kind: TrustKind
    host: str
    port: int
    device: str
    was: str
    now: str


RUN_CREATED = _plain("run.created")
RUN_COMPLETED = _plain("run.completed")
STEP_STARTED = _plain("step.started")
STEP_COMPLETED = _plain("step.completed")
STEP_FAILED = _plain("step.failed")
STEP_STALLED = _plain("step.stalled")
STEP_CRASHED = _plain("step.crashed")
PHASE_PROGRESS = _plain("phase.progress")
OPERATOR_CREDENTIALS_READY = _plain("operator.credentials_ready")
OPERATOR_REVIEW_READY = _plain("operator.review_ready")
VERIFY_COMPLETED = _event("verify.completed", VerifyData)
VERIFY_FAILED = _plain("verify.failed")
ASBUILT_STARTED = _plain("asbuilt.started")
ASBUILT_GENERATED = _event("asbuilt.generated", AsBuiltData)
ASBUILT_FAILED = _plain("asbuilt.failed")
DISCOVER_COMPLETED = _event("discover.completed", DiscoveryData)
ZONING_PREVIEWED = _event("zoning.previewed", ZoningCheckData)
ZONING_PROPER = _event("zoning.proper", ZoningCheckData)
ZONING_PLAN = _event("zoning.plan", ZoningPlanData)
ZONING_RENDERED = _event("zoning.rendered", ZoningRenderedData)
PORTS_PREVIEWED = _event("ports.previewed", PortsData)
PORTS_PREVIEW_FAILED = _event("ports.preview.failed", PortsData)
PORTS_COMPLETED = _event("ports.completed", PortsData)
STORAGE_PREVIEWED = _event("storage.previewed", StoragePlanData)
STORAGE_PREVIEW_FAILED = _event("storage.preview.failed", StoragePlanData)
STORAGE_APPLY_STARTED = _plain("storage.apply.started")
STORAGE_APPLIED = _event("storage.applied", StorageResultData)
STORAGE_APPLY_FAILED = _event("storage.apply.failed", StorageResultData)
STORAGE_PATHS_CHECKING = _plain("storage.paths.checking")
STORAGE_PATHS_VERIFIED = _event("storage.paths.verified", PathsData)
STORAGE_PATHS_FAILED = _event("storage.paths.failed", PathsData)
REPLICATION_PREVIEWED = _event("replication.previewed", ReplicationPlanData)
REPLICATION_PREVIEW_FAILED = _event("replication.preview.failed", ReplicationPlanData)
REPLICATION_LINK_CHECK_STARTED = _plain("replication.link_check.started")
REPLICATION_LINK_CHECKED = _event("replication.link_checked", LinkCheckData)
REPLICATION_LINK_CHECK_FAILED = _event("replication.link_check.failed", LinkCheckData)
REPLICATION_APPLY_STARTED = _plain("replication.apply.started")
REPLICATION_APPLIED = _event("replication.applied", ReplicationResultData)
REPLICATION_APPLY_FAILED = _event("replication.apply.failed", ReplicationResultData)
REPLICATION_VERIFY_STARTED = _plain("replication.verify.started")
REPLICATION_VERIFIED = _event("replication.verified", ReplicationVerifyData)
REPLICATION_VERIFY_FAILED = _event("replication.verify.failed", ReplicationVerifyData)
FAILOVER_STARTED = _event("failover.started", FailoverStartData)
FAILOVER_COMPLETED = _event("failover.completed", FailoverData)
FAILOVER_FAILED = _event("failover.failed", FailoverData)
SNAPSHOTS_PREVIEWED = _event("snapshots.previewed", SnapshotPlanData)
SNAPSHOTS_PREVIEW_FAILED = _event("snapshots.preview.failed", SnapshotPlanData)
SNAPSHOTS_APPLY_STARTED = _plain("snapshots.apply.started")
SNAPSHOTS_APPLIED = _event("snapshots.applied", SnapshotResultData)
SNAPSHOTS_APPLY_FAILED = _event("snapshots.apply.failed", SnapshotResultData)
SNAPSHOTS_VERIFY_STARTED = _plain("snapshots.verify.started")
SNAPSHOTS_VERIFIED = _event("snapshots.verified", SnapshotVerifyData)
SNAPSHOTS_VERIFY_FAILED = _event("snapshots.verify.failed", SnapshotVerifyData)
DEVICE_TRUSTED = _event("device.trusted", DeviceData)
DEVICE_TRUST_FAILED = _event("device.trust_failed", DeviceData)
DEVICE_REFUSED = _event("device.refused", DeviceData)
DEVICE_RETRUSTED = _event("device.retrusted", RetrustData)
