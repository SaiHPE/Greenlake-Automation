from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, SecretStr, field_validator


class WorkflowPhase(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    PREFLIGHT = "PREFLIGHT"
    GL_DISCOVER_SERVICE = "GL_DISCOVER_SERVICE"
    GL_ADD_SUBSCRIPTION = "GL_ADD_SUBSCRIPTION"
    GL_REGISTER_DEVICE = "GL_REGISTER_DEVICE"
    GL_ASSIGN_APPLICATION = "GL_ASSIGN_APPLICATION"
    GL_APPLY_SUBSCRIPTION = "GL_APPLY_SUBSCRIPTION"
    GL_VERIFY_DEVICE = "GL_VERIFY_DEVICE"
    CLOUDINIT_CONNECT = "CLOUDINIT_CONNECT"
    DSCC_SETUP_SYSTEM = "DSCC_SETUP_SYSTEM"
    STORAGE_FLEET_VERIFY = "STORAGE_FLEET_VERIFY"
    CONFIG_VERIFY = "CONFIG_VERIFY"
    COMPLETE = "COMPLETE"


class RunStatus(StrEnum):
    NOT_STARTED = "not_started"
    READY = "ready"
    RUNNING = "running"
    WAITING_FOR_OPERATOR = "waiting_for_operator"
    RETRYABLE_FAILURE = "retryable_failure"
    TERMINAL_FAILURE = "terminal_failure"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    SKIPPED = "skipped"


class BrowserResultStatus(StrEnum):
    ALREADY_DONE = "already_done"
    SUCCEEDED = "succeeded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    WAITING_FOR_OPERATOR = "waiting_for_operator"


class CheckStatus(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


class NetworkConfig(BaseModel):
    mgmt_ipv4: str
    mask: str
    gateway: str
    dns: list[str] = Field(default_factory=list)
    ntp: str
    timezone: str
    proxy_host: str | None = None
    proxy_port: int | None = None
    proxy_username: str | None = None
    proxy_password_ref: str | None = None


class DsccSetupConfig(BaseModel):
    # System step
    system_name: str
    country: str
    # System Credentials (the array admin secret DSCC stores; reused if present, else created)
    credential_name: str = "b10000-admin"
    username: str = "3paradm"
    password: SecretStr | None = None
    # Attributes -> Support Contact step
    contact_first_name: str | None = None
    contact_last_name: str | None = None
    contact_language: str = "English"
    contact_company: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    # Review -> blueprint (left off by default; revisit later)
    blueprint_name: str | None = None
    apply_blueprint: bool = False


class ArrayWorkItem(BaseModel):
    serial_number: str
    part_number: str
    subscription_key: SecretStr
    service_catalog_region_id: str
    dscc_region_code: str
    cloudinit_url: str
    network: NetworkConfig
    dscc_setup: DsccSetupConfig
    tags: dict[str, str] = Field(default_factory=dict)
    support_contact: dict[str, Any] = Field(default_factory=dict)
    storage_fleet_enabled: bool = False

    @field_validator("serial_number", "part_number", "service_catalog_region_id", "dscc_region_code")
    @classmethod
    def non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be empty")
        return value


class ExternalResources(BaseModel):
    device_id: str | None = None
    subscription_id: str | None = None
    service_manager_id: str | None = None
    service_catalog_region_id: str | None = None
    active_async_operation_id: str | None = None
    storage_fleet_system_id: str | None = None


class RunEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    phase: WorkflowPhase
    event_type: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RunRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    serial_number: str
    status: RunStatus = RunStatus.NOT_STARTED
    current_phase: WorkflowPhase = WorkflowPhase.NOT_STARTED
    resources: ExternalResources = Field(default_factory=ExternalResources)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PhaseResult(BaseModel):
    status: RunStatus
    message: str
    resources: ExternalResources = Field(default_factory=ExternalResources)
    warnings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class PreflightCheck(BaseModel):
    name: str
    status: CheckStatus
    message: str
    remediation: str | None = None


class PreflightReport(BaseModel):
    serial_number: str
    overall_status: CheckStatus
    checks: list[PreflightCheck]

    @property
    def passed(self) -> bool:
        return self.overall_status in {CheckStatus.PASS, CheckStatus.WARN}


class FieldCheckStatus(StrEnum):
    PASS = "pass"
    MISMATCH = "mismatch"
    NOT_READABLE = "not_readable"  # the array didn't expose this value (or the parser missed it)


class FieldCheck(BaseModel):
    """One configured value compared against what the array actually reports."""

    field: str
    expected: str
    actual: str | None = None
    status: FieldCheckStatus
    critical: bool = False  # network + system name — a mismatch here is prominent


class HealthIssue(BaseModel):
    """One row from `checkhealth -svc -detail` — a component the array reports a problem on."""

    component: str  # e.g. Alert, Cage, CDM, iLO, RC, Security
    summary: str    # the Summary Description text
    qty: int        # how many of this issue


class VerificationReport(BaseModel):
    """Result of the post-init SSH verification (see docs/adr/0001) — config + array health."""

    reachable: bool  # could we SSH in + run the show commands at all?
    error: str | None = None
    checks: list[FieldCheck] = Field(default_factory=list)
    health_issues: list[HealthIssue] = Field(default_factory=list)  # from checkhealth -svc -detail
    raw: dict[str, str] = Field(default_factory=dict)  # raw show* output, for operator review/calibration

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.status == FieldCheckStatus.PASS)

    @property
    def mismatches(self) -> int:
        return sum(1 for c in self.checks if c.status == FieldCheckStatus.MISMATCH)

    @property
    def health_total(self) -> int:
        return sum(i.qty for i in self.health_issues)
