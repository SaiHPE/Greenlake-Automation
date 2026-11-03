"""Read-only GreenLake readiness check — shared by `onboard check` and the API's /config/check.

Verifies auth works and reports which regions have a PROVISIONED Data Services instance
(the prerequisite for the assign step). No writes.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from alletra_onboard.application.onboarding.clients import make_greenlake, missing_credentials
from alletra_onboard.application.platform.tls import is_tls_trust_error, tls_trust_guidance
from alletra_onboard.config import Settings


class ProvisionSummary(BaseModel):
    region: str
    status: str
    service_manager_id: str
    is_data_services: bool


class GreenLakeCheckReport(BaseModel):
    ok: bool
    ready: bool = False  # a PROVISIONED Data Services exists somewhere
    error: str | None = None
    missing_credentials: list[str] = Field(default_factory=list)
    provisions: list[ProvisionSummary] = Field(default_factory=list)
    # The check failed before the credentials were ever evaluated: the TLS certificate could not be
    # verified. Reporting that as "credentials rejected" sends the operator to re-check a client
    # secret that was never sent — the failure reported live from an HPE laptop.
    tls_trust_failure: bool = False


async def greenlake_check(settings: Settings) -> GreenLakeCheckReport:
    missing = missing_credentials(settings)
    if missing:
        return GreenLakeCheckReport(ok=False, missing_credentials=missing, error="credentials not configured")

    clients = make_greenlake(settings)
    try:
        regions = await clients.service_catalog.per_region_service_managers()
        ds_ids = {
            sm.get("id")
            for region in regions
            for sm in region.get("serviceManagers", [])
            if "data service" in str(sm.get("name", "")).lower()
        }
        response = await clients.http.request(
            "GET", "/service-catalog/v1/service-manager-provisions", bucket="service_catalog_read"
        )
        raw = response.json().get("items", [])
    except Exception as exc:  # noqa: BLE001 - operator-facing health check reports, not crashes.
        if is_tls_trust_error(exc):
            return GreenLakeCheckReport(
                ok=False,
                tls_trust_failure=True,
                error=tls_trust_guidance("the HPE GreenLake API") + f" [{type(exc).__name__}: {str(exc)[:160]}]",
            )
        return GreenLakeCheckReport(ok=False, error=f"{type(exc).__name__}: {str(exc)[:200]}")

    provisions = [
        ProvisionSummary(
            region=str(p.get("region")),
            status=str(p.get("provisionStatus")),
            service_manager_id=(p.get("serviceManager") or {}).get("id") or "",
            is_data_services=((p.get("serviceManager") or {}).get("id") in ds_ids),
        )
        for p in raw
    ]
    ready = any(p.is_data_services and p.status == "PROVISIONED" for p in provisions)
    return GreenLakeCheckReport(ok=True, ready=ready, provisions=provisions)
