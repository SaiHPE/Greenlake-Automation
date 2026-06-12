from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient


def add_subscription_payload(subscription_key: str) -> dict:
    return {"subscriptions": [{"key": subscription_key}]}


class SubscriptionsClient:
    def __init__(self, http: "GreenLakeHttpClient") -> None:
        self.http = http

    async def add_subscription(self, subscription_key: str) -> str | None:
        response = await self.http.request(
            "POST",
            "/subscriptions/v1/subscriptions",
            bucket="subscription_add",
            json=add_subscription_payload(subscription_key),
        )
        return response.headers.get("Location")

    async def find_by_key(self, subscription_key: str) -> dict | None:
        response = await self.http.request(
            "GET",
            "/subscriptions/v1/subscriptions",
            bucket="subscription_read",
            params={"filter": f"key eq '{subscription_key}'"},
        )
        items = response.json().get("items", [])
        return items[0] if items else None
