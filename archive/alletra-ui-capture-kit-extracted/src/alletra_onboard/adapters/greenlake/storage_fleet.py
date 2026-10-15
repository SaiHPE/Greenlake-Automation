from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient


class StorageFleetClient:
    def __init__(self, http: "GreenLakeHttpClient") -> None:
        self.http = http

    async def list_b10000_systems(self) -> dict:
        response = await self.http.request("GET", "/storage-fleet/v1alpha1/devtype4-storage-systems")
        return response.json()
