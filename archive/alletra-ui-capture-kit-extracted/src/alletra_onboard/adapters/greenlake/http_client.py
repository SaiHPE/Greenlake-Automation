from __future__ import annotations

from typing import Any

import httpx

from alletra_onboard.domain.policies import RateBudget, TokenBucket


class GreenLakeHttpClient:
    def __init__(self, base_url: str, token_provider, buckets: dict[str, TokenBucket] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token_provider = token_provider
        self.buckets = buckets or {
            "default": TokenBucket(RateBudget("default", capacity=60, refill_seconds=60)),
        }

    async def request(self, method: str, path: str, *, bucket: str = "default", **kwargs: Any) -> httpx.Response:
        await self.buckets.get(bucket, self.buckets["default"]).acquire()
        token = await self.token_provider.token()
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:
            response = await client.request(method, path, headers=headers, **kwargs)
        response.raise_for_status()
        return response

    async def poll_location(self, location: str, *, bucket: str = "default") -> dict[str, Any]:
        response = await self.request("GET", location, bucket=bucket)
        return response.json()
