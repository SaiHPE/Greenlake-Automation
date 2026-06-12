from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient


@dataclass(frozen=True)
class ServiceProvision:
    service_manager_id: str
    region: str
    provision_status: str
    resource_uri: str | None = None


def parse_service_manager_provision(item: dict) -> ServiceProvision:
    service_manager = item.get("serviceManager") or {}
    return ServiceProvision(
        service_manager_id=service_manager["id"],
        region=item["region"],
        provision_status=item["provisionStatus"],
        resource_uri=item.get("resourceUri"),
    )


class ServiceCatalogClient:
    def __init__(self, http: "GreenLakeHttpClient") -> None:
        self.http = http

    async def per_region_service_managers(self) -> list[dict]:
        response = await self.http.request(
            "GET",
            "/service-catalog/v1/per-region-service-managers",
            bucket="service_catalog_read",
        )
        return response.json().get("items", [])

    async def service_manager_provisions(self, region: str) -> list[ServiceProvision]:
        response = await self.http.request(
            "GET",
            "/service-catalog/v1/service-manager-provisions",
            bucket="service_catalog_read",
            params={"filter": f"status eq 'PROVISIONED' and region eq '{region}'"},
        )
        return [parse_service_manager_provision(item) for item in response.json().get("items", [])]
