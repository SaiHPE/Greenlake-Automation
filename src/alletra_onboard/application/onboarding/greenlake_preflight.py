from __future__ import annotations

from typing import Protocol

import httpx

from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials
from alletra_onboard.adapters.greenlake.devices import DevicesClient
from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient
from alletra_onboard.adapters.greenlake.service_catalog import ServiceCatalogClient, ServiceProvision
from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, CheckStatus, PreflightCheck
from alletra_onboard.domain.policies import redact


class GreenLakePreflightRunner(Protocol):
    async def run(self, item: ArrayWorkItem) -> list[PreflightCheck]: ...


class TokenProvider(Protocol):
    async def token(self) -> str: ...


class DeviceLookup(Protocol):
    async def find_by_serial(self, serial_number: str) -> dict | None: ...


class SubscriptionLookup(Protocol):
    async def find_by_key(self, subscription_key: str) -> dict | None: ...


class ServiceCatalogLookup(Protocol):
    async def service_manager_provisions(self, region: str) -> list[ServiceProvision]: ...


class MissingGreenLakeReadPreflightService:
    def __init__(self, missing_credentials: list[str]) -> None:
        self.missing_credentials = missing_credentials

    async def run(self, item: ArrayWorkItem) -> list[PreflightCheck]:
        return [
            PreflightCheck(
                name="greenlake_live_credentials",
                status=CheckStatus.FAIL,
                message=(
                    "Live GreenLake preflight was requested, but required environment variables "
                    f"are missing: {', '.join(self.missing_credentials)}."
                ),
                remediation="Set the missing variables and rerun preflight with --live-greenlake.",
            )
        ]


class GreenLakeReadPreflightService:
    def __init__(
        self,
        token_provider: TokenProvider,
        devices: DeviceLookup,
        subscriptions: SubscriptionLookup,
        service_catalog: ServiceCatalogLookup,
    ) -> None:
        self.token_provider = token_provider
        self.devices = devices
        self.subscriptions = subscriptions
        self.service_catalog = service_catalog

    async def run(self, item: ArrayWorkItem) -> list[PreflightCheck]:
        auth_check = await self._check_auth()
        checks = [auth_check]
        if auth_check.status == CheckStatus.FAIL:
            return checks

        checks.append(await self._check_service_catalog(item))
        checks.append(await self._check_device_lookup(item))
        checks.append(await self._check_subscription_lookup(item))
        return checks

    async def _check_auth(self) -> PreflightCheck:
        try:
            await self.token_provider.token()
        except Exception as exc:  # noqa: BLE001 - operator-facing preflight should report all failures.
            return _failed_check(
                "greenlake_auth",
                "Could not fetch a GreenLake OAuth token",
                exc,
                "Check GL_CLIENT_ID, GL_CLIENT_SECRET, and service account status.",
            )
        return PreflightCheck(
            name="greenlake_auth",
            status=CheckStatus.PASS,
            message="GreenLake OAuth token fetch succeeded.",
        )

    async def _check_service_catalog(self, item: ArrayWorkItem) -> PreflightCheck:
        try:
            provisions = await self.service_catalog.service_manager_provisions(item.service_catalog_region_id)
        except Exception as exc:  # noqa: BLE001
            return _failed_check(
                "greenlake_service_catalog",
                "Could not read Service Catalog provisions",
                exc,
                "Grant read access to Service Catalog and confirm the requested region.",
            )

        if not provisions:
            return PreflightCheck(
                name="greenlake_service_catalog",
                status=CheckStatus.FAIL,
                message=(
                    "No provisioned service manager was found for GreenLake region "
                    f"{item.service_catalog_region_id}."
                ),
                remediation="Provision DSCC in the target region or correct service_catalog_region_id.",
            )

        first = provisions[0]
        suffix = "" if len(provisions) == 1 else f" ({len(provisions)} provisions found)"
        return PreflightCheck(
            name="greenlake_service_catalog",
            status=CheckStatus.PASS,
            message=(
                "Found provisioned service manager "
                f"{first.service_manager_id} for {item.service_catalog_region_id}{suffix}."
            ),
        )

    async def _check_device_lookup(self, item: ArrayWorkItem) -> PreflightCheck:
        try:
            device = await self.devices.find_by_serial(item.serial_number)
        except Exception as exc:  # noqa: BLE001
            return _failed_check(
                "greenlake_device_lookup",
                "Could not read Device Management inventory",
                exc,
                "Grant read access to Device Management and retry.",
            )

        if device is None:
            return PreflightCheck(
                name="greenlake_device_lookup",
                status=CheckStatus.PASS,
                message=f"Serial {item.serial_number} is not currently registered in GreenLake.",
            )

        return PreflightCheck(
            name="greenlake_device_lookup",
            status=CheckStatus.WARN,
            message=(
                f"Serial {item.serial_number} is already registered in GreenLake "
                f"as {_resource_id(device)}."
            ),
            remediation="Confirm this run should resume or reconcile the existing device before writes.",
        )

    async def _check_subscription_lookup(self, item: ArrayWorkItem) -> PreflightCheck:
        try:
            subscription = await self.subscriptions.find_by_key(item.subscription_key.get_secret_value())
        except Exception as exc:  # noqa: BLE001
            return _failed_check(
                "greenlake_subscription_lookup",
                "Could not read Subscription Management inventory",
                exc,
                "Grant read access to Subscription Management and retry.",
            )

        if subscription is None:
            return PreflightCheck(
                name="greenlake_subscription_lookup",
                status=CheckStatus.PASS,
                message="Subscription key is not already present; the write phase can add it.",
            )

        return PreflightCheck(
            name="greenlake_subscription_lookup",
            status=CheckStatus.PASS,
            message=f"Subscription key is already present as {_resource_id(subscription)}.",
        )


def build_greenlake_read_preflight(settings: Settings) -> GreenLakePreflightRunner:
    missing = _missing_credentials(settings)
    if missing:
        return MissingGreenLakeReadPreflightService(missing)

    token_provider = OAuthClientCredentials(
        settings.gl_token_url,
        settings.gl_client_id or "",
        settings.gl_client_secret or "",
    )
    http = GreenLakeHttpClient(settings.gl_base_url, token_provider)
    return GreenLakeReadPreflightService(
        token_provider,
        DevicesClient(http),
        SubscriptionsClient(http),
        ServiceCatalogClient(http),
    )


def _missing_credentials(settings: Settings) -> list[str]:
    return [
        name
        for name, value in {
            "GL_CLIENT_ID": settings.gl_client_id,
            "GL_CLIENT_SECRET": settings.gl_client_secret,
            "GL_MEMBER_WORKSPACE_ID": settings.gl_member_workspace_id,
        }.items()
        if not value
    ]


def _failed_check(name: str, prefix: str, exc: Exception, remediation: str) -> PreflightCheck:
    return PreflightCheck(
        name=name,
        status=CheckStatus.FAIL,
        message=f"{prefix}: {_format_exception(exc)}",
        remediation=remediation,
    )


def _format_exception(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        response = exc.response
        request = response.request
        return f"HTTP {response.status_code} from {request.method} {request.url.path}"
    return redact(str(exc) or exc.__class__.__name__)


def _resource_id(value: dict) -> str:
    return str(value.get("id") or value.get("resourceId") or value.get("deviceId") or "unknown id")