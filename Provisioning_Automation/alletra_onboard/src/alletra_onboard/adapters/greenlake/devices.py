from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient


def storage_device_payload(serial_number: str, part_number: str, tags: dict[str, str] | None = None) -> dict[str, Any]:
    # POST /devices/v2beta1/devices flat schema: serialNumber + deviceType + partNumber
    # (partNumber required for STORAGE). The v1 `{storage:[...]}` form requires
    # compute/network arrays too and 400s for a storage-only add.
    payload: dict[str, Any] = {
        "serialNumber": serial_number,
        "deviceType": "STORAGE",
        "partNumber": part_number,
    }
    if tags:
        payload["tags"] = tags
    return payload


def assign_application_payload(service_manager_id: str, region: str) -> dict[str, Any]:
    return {"application": {"id": service_manager_id}, "region": region}


def apply_subscription_payload(subscription_id: str) -> dict[str, Any]:
    return {"subscription": [{"id": subscription_id}]}


class DevicesClient:
    def __init__(self, http: "GreenLakeHttpClient") -> None:
        self.http = http

    async def add_storage_device(
        self, serial_number: str, part_number: str, tags: dict[str, str], *, dry_run: bool = False
    ) -> str | None:
        # dry_run=True asks GreenLake to validate the payload without creating the device
        # (the endpoint's documented `dry-run` query param). Used by `provision --dry-run`.
        params = {"dry-run": "true"} if dry_run else None
        response = await self.http.request(
            "POST",
            "/devices/v2beta1/devices",
            bucket="device_add",
            params=params,
            json=storage_device_payload(serial_number, part_number, tags),
        )
        return response.headers.get("Location")

    async def find_by_serial(self, serial_number: str) -> dict | None:
        response = await self.http.request(
            "GET",
            "/devices/v1/devices",
            bucket="device_read",
            params={"filter": f"serialNumber eq '{serial_number}'"},
        )
        items = response.json().get("items", [])
        return items[0] if items else None

    async def get(self, device_id: str) -> dict:
        response = await self.http.request("GET", f"/devices/v1/devices/{device_id}", bucket="device_read")
        return response.json()

    async def assign_application(self, device_id: str, service_manager_id: str, region: str) -> str | None:
        response = await self.http.request(
            "PATCH",
            f"/devices/v1/devices?id={device_id}",
            bucket="device_patch",
            headers={"Content-Type": "application/merge-patch+json"},
            json=assign_application_payload(service_manager_id, region),
        )
        return response.headers.get("Location")

    async def apply_subscription(self, device_id: str, subscription_id: str) -> str | None:
        response = await self.http.request(
            "PATCH",
            f"/devices/v1/devices?id={device_id}",
            bucket="device_patch",
            headers={"Content-Type": "application/merge-patch+json"},
            json=apply_subscription_payload(subscription_id),
        )
        return response.headers.get("Location")
