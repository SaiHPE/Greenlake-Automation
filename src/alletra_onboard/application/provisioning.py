"""Component A — GreenLake REST provisioning orchestrator.

Runs the per-array pipeline from AUTOMATION_PLAN section 3:

    discover -> add subscription -> register device -> assign application
             -> apply subscription -> verify

Every write is GET-guarded for idempotency, and every 202+Location response is polled
to a terminal state. ``dry_run`` performs all the read/guard calls (safe GETs) but skips
every POST/PATCH, so it prints a faithful preview of exactly what the live run would do.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials
from alletra_onboard.adapters.greenlake.devices import DevicesClient
from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient
from alletra_onboard.adapters.greenlake.service_catalog import ServiceCatalogClient
from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, WorkflowPhase
from alletra_onboard.domain.policies import redact

ASSIGNED_STATE_TARGET = "ASSIGNED_TO_SERVICE"

# Phase outcome statuses.
DONE = "done"
SKIPPED = "skipped"
WOULD_DO = "would-do"  # dry-run: a write the live run would perform
FAILED = "failed"


@dataclass
class PhaseOutcome:
    phase: WorkflowPhase
    status: str
    detail: str


@dataclass
class ProvisionResult:
    serial: str
    succeeded: bool = False
    dry_run: bool = False
    phases: list[PhaseOutcome] = field(default_factory=list)
    device_id: str | None = None
    subscription_id: str | None = None
    service_manager_id: str | None = None
    region: str | None = None
    assigned_state: str | None = None
    error: str | None = None


class GreenLakeProvisioningService:
    def __init__(
        self,
        *,
        http: GreenLakeHttpClient,
        devices: DevicesClient,
        subscriptions: SubscriptionsClient,
        service_catalog: ServiceCatalogClient,
        progress: Callable[[WorkflowPhase, str], None] | None = None,
        device_state_timeout: float = 300.0,
    ) -> None:
        self.http = http
        self.devices = devices
        self.subscriptions = subscriptions
        self.service_catalog = service_catalog
        self._progress = progress or (lambda phase, message: None)
        self.device_state_timeout = device_state_timeout

    async def provision(self, item: ArrayWorkItem, *, dry_run: bool = False) -> ProvisionResult:
        result = ProvisionResult(serial=item.serial_number, dry_run=dry_run)
        try:
            await self._discover(item, result)
            await self._add_subscription(item, result, dry_run=dry_run)
            await self._register_device(item, result, dry_run=dry_run)
            await self._assign_application(result, dry_run=dry_run)
            await self._apply_subscription(result, dry_run=dry_run)
            await self._verify(result, dry_run=dry_run)
            result.succeeded = not dry_run and all(p.status != FAILED for p in result.phases)
        except Exception as exc:  # noqa: BLE001 - operator-facing pipeline must report, not crash.
            detail = _exception_detail(exc)
            phase = _current_phase(result)
            result.error = detail
            result.phases.append(PhaseOutcome(phase, FAILED, detail))
            self._progress(phase, f"FAILED: {detail}")
        return result

    # ------------------------------------------------------------------ phases

    async def _discover(self, item: ArrayWorkItem, result: ProvisionResult) -> None:
        phase = WorkflowPhase.GL_DISCOVER_SERVICE
        provisions = await self.service_catalog.service_manager_provisions(item.service_catalog_region_id)
        if not provisions:
            raise ProvisioningError(
                f"No PROVISIONED Data Services service-manager found in region "
                f"{item.service_catalog_region_id}. Add the Data Services service to this "
                f"workspace and deploy it to the region (GreenLake UI: Manage Workspace -> "
                f"Services), or correct service_catalog_region_id. Until a service is "
                f"provisioned, the device cannot be assigned to an application instance."
            )
        provision = provisions[0]
        result.service_manager_id = provision.service_manager_id
        result.region = provision.region
        detail = f"service-manager {provision.service_manager_id} in {provision.region}"
        if len(provisions) > 1:
            detail += f" ({len(provisions)} provisions; using the first)"
        self._record(result, phase, DONE, detail)

    async def _add_subscription(self, item: ArrayWorkItem, result: ProvisionResult, *, dry_run: bool) -> None:
        phase = WorkflowPhase.GL_ADD_SUBSCRIPTION
        key = item.subscription_key.get_secret_value()
        existing = await self.subscriptions.find_by_key(key)
        if existing:
            result.subscription_id = _res_id(existing)
            self._record(result, phase, SKIPPED, f"subscription already present as {result.subscription_id}")
            return
        if dry_run:
            self._record(result, phase, WOULD_DO, "would add subscription, then poll until active")
            return
        location = await self.subscriptions.add_subscription(key)
        if location:
            await self.http.poll_async(location, bucket="subscription_async_poll")
        added = await self.subscriptions.find_by_key(key)
        if not added:
            raise ProvisioningError("Subscription add completed but the key is still not queryable.")
        result.subscription_id = _res_id(added)
        self._record(result, phase, DONE, f"subscription added as {result.subscription_id}")

    async def _register_device(self, item: ArrayWorkItem, result: ProvisionResult, *, dry_run: bool) -> None:
        phase = WorkflowPhase.GL_REGISTER_DEVICE
        existing = await self.devices.find_by_serial(item.serial_number)
        if existing:
            result.device_id = _res_id(existing)
            self._record(result, phase, SKIPPED, f"device already registered as {result.device_id}")
            return
        if dry_run:
            # Validate the device payload against GreenLake (dry-run=true) without creating it.
            await self.devices.add_storage_device(item.serial_number, item.part_number, item.tags, dry_run=True)
            self._record(
                result, phase, WOULD_DO,
                f"device payload validated by API (dry-run); would register serial={item.serial_number}",
            )
            return
        location = await self.devices.add_storage_device(item.serial_number, item.part_number, item.tags)
        if location:
            await self.http.poll_async(location, bucket="device_async_poll")
        added = await self.devices.find_by_serial(item.serial_number)
        if not added:
            raise ProvisioningError("Device add completed but the serial is still not in inventory.")
        result.device_id = _res_id(added)
        self._record(result, phase, DONE, f"device registered as {result.device_id}")

    async def _assign_application(self, result: ProvisionResult, *, dry_run: bool) -> None:
        phase = WorkflowPhase.GL_ASSIGN_APPLICATION
        if result.service_manager_id is None:
            return
        if result.device_id is None:
            # Only reachable in dry-run before a real registration exists.
            self._record(result, phase, WOULD_DO, "would assign application after the device is registered")
            return
        device = await self.devices.get(result.device_id)
        if _application_id(device) == result.service_manager_id and _device_region(device) == result.region:
            result.assigned_state = _assigned_state(device)
            self._record(result, phase, SKIPPED, "device already assigned to this application/region")
            return
        if dry_run:
            self._record(result, phase, WOULD_DO, f"would assign application {result.service_manager_id} / {result.region}")
            return
        location = await self.devices.assign_application(result.device_id, result.service_manager_id, result.region or "")
        if location:
            await self.http.poll_async(location, bucket="device_async_poll")
        device = await self._wait_for_device_state(result.device_id, ASSIGNED_STATE_TARGET)
        result.assigned_state = _assigned_state(device)
        self._record(result, phase, DONE, f"assignedState={result.assigned_state}")

    async def _apply_subscription(self, result: ProvisionResult, *, dry_run: bool) -> None:
        phase = WorkflowPhase.GL_APPLY_SUBSCRIPTION
        if result.device_id is None or result.subscription_id is None:
            if dry_run:
                self._record(result, phase, WOULD_DO, "would apply subscription after device + subscription exist")
            return
        device = await self.devices.get(result.device_id)
        if result.subscription_id in _subscription_ids(device):
            self._record(result, phase, SKIPPED, "subscription already applied to the device")
            return
        if dry_run:
            self._record(result, phase, WOULD_DO, f"would apply subscription {result.subscription_id}")
            return
        location = await self.devices.apply_subscription(result.device_id, result.subscription_id)
        if location:
            await self.http.poll_async(location, bucket="device_async_poll")
        self._record(result, phase, DONE, f"subscription {result.subscription_id} applied")

    async def _verify(self, result: ProvisionResult, *, dry_run: bool) -> None:
        phase = WorkflowPhase.GL_VERIFY_DEVICE
        if dry_run:
            self._record(result, phase, WOULD_DO, "would verify assignedState == ASSIGNED_TO_SERVICE + subscription")
            return
        if result.device_id is None:
            raise ProvisioningError("Cannot verify: no device id resolved.")
        device = await self.devices.get(result.device_id)
        result.assigned_state = _assigned_state(device)
        problems = []
        if result.assigned_state != ASSIGNED_STATE_TARGET:
            problems.append(f"assignedState={result.assigned_state!r} (expected {ASSIGNED_STATE_TARGET})")
        if not _application_id(device):
            problems.append("application.id is empty")
        if not _subscription_ids(device):
            problems.append("no subscription on device")
        if problems:
            raise ProvisioningError("Verification failed: " + "; ".join(problems))
        self._record(result, phase, DONE, "assignedState=ASSIGNED_TO_SERVICE, application + subscription present")

    # ----------------------------------------------------------------- helpers

    async def _wait_for_device_state(self, device_id: str, target_state: str) -> dict[str, Any]:
        deadline = time.monotonic() + self.device_state_timeout
        device: dict[str, Any] = {}
        while True:
            device = await self.devices.get(device_id)
            if _assigned_state(device) == target_state:
                return device
            if time.monotonic() >= deadline:
                return device
            await asyncio.sleep(5.0)

    def _record(self, result: ProvisionResult, phase: WorkflowPhase, status: str, detail: str) -> None:
        result.phases.append(PhaseOutcome(phase, status, detail))
        self._progress(phase, f"{status}: {detail}")


class ProvisioningError(RuntimeError):
    """A provisioning phase failed in a way the operator must act on."""


def missing_credentials(settings: Settings) -> list[str]:
    return [
        name
        for name, value in {
            "GL_CLIENT_ID": settings.gl_client_id,
            "GL_CLIENT_SECRET": settings.gl_client_secret,
            "GL_TOKEN_URL": settings.gl_token_url,
        }.items()
        if not value
    ]


def build_provisioning_service(
    settings: Settings,
    *,
    progress: Callable[[WorkflowPhase, str], None] | None = None,
) -> GreenLakeProvisioningService:
    token_provider = OAuthClientCredentials(
        settings.gl_token_url,
        settings.gl_client_id or "",
        settings.gl_client_secret or "",
    )
    http = GreenLakeHttpClient(settings.gl_base_url, token_provider)
    return GreenLakeProvisioningService(
        http=http,
        devices=DevicesClient(http),
        subscriptions=SubscriptionsClient(http),
        service_catalog=ServiceCatalogClient(http),
        progress=progress,
    )


def _record_phases_have(result: ProvisionResult, phase: WorkflowPhase) -> bool:
    return any(p.phase == phase for p in result.phases)


def _current_phase(result: ProvisionResult) -> WorkflowPhase:
    order = [
        WorkflowPhase.GL_DISCOVER_SERVICE,
        WorkflowPhase.GL_ADD_SUBSCRIPTION,
        WorkflowPhase.GL_REGISTER_DEVICE,
        WorkflowPhase.GL_ASSIGN_APPLICATION,
        WorkflowPhase.GL_APPLY_SUBSCRIPTION,
        WorkflowPhase.GL_VERIFY_DEVICE,
    ]
    for phase in order:
        if not _record_phases_have(result, phase):
            return phase
    return WorkflowPhase.GL_VERIFY_DEVICE


def _exception_detail(exc: Exception) -> str:
    import httpx

    if isinstance(exc, httpx.HTTPStatusError):
        base = f"HTTP {exc.response.status_code} from {exc.request.method} {exc.request.url.path}"
        body = _greenlake_error_text(exc.response)
        return f"{base} — {body}" if body else base
    return redact(str(exc) or exc.__class__.__name__)


def _greenlake_error_text(response: Any) -> str:
    """Pull the human-readable message + field issues out of a GreenLake error body."""
    try:
        data = response.json()
    except Exception:  # noqa: BLE001 - error bodies are not always JSON.
        return redact((response.text or "").strip()[:300])
    if not isinstance(data, dict):
        return ""
    parts: list[str] = []
    if data.get("message"):
        parts.append(str(data["message"]))
    if data.get("errorCode"):
        parts.append(f"[{data['errorCode']}]")
    for detail in data.get("badRequestErrorDetails") or []:
        issues = detail.get("issues") if isinstance(detail, dict) else None
        for issue in issues or []:
            if not isinstance(issue, dict):
                continue
            description = issue.get("description") or issue.get("subject")
            source = issue.get("source")
            if description:
                parts.append(f"{source + ': ' if source else ''}{description}")
    return redact("; ".join(parts))[:500]


def _res_id(value: dict[str, Any]) -> str:
    return str(value.get("id") or value.get("resourceId") or value.get("deviceId") or "unknown")


def _application_id(device: dict[str, Any]) -> str | None:
    application = device.get("application") or {}
    return application.get("id") if isinstance(application, dict) else None


def _device_region(device: dict[str, Any]) -> str | None:
    return device.get("region")


def _assigned_state(device: dict[str, Any]) -> str | None:
    return device.get("assignedState")


def _subscription_ids(device: dict[str, Any]) -> list[str]:
    subscriptions = device.get("subscription") or []
    if isinstance(subscriptions, dict):
        subscriptions = [subscriptions]
    return [str(s.get("id")) for s in subscriptions if isinstance(s, dict) and s.get("id")]
