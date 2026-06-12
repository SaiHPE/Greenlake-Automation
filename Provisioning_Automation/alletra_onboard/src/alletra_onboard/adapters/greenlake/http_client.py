from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from alletra_onboard.domain.policies import RateBudget, TokenBucket

# Async-operation status vocabulary (Devices/Subscriptions async-operations).
TERMINAL_OK = {"SUCCEEDED", "SUCCESS", "OK", "COMPLETE", "COMPLETED", "DONE"}
TERMINAL_FAIL = {"FAILED", "FAILURE", "ERROR", "TIMEDOUT", "TIMEOUT", "PAUSED", "CANCELLED"}
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class GreenLakeAsyncOperationError(RuntimeError):
    """A polled GreenLake async-operation reached a terminal failure state."""


def default_rate_buckets() -> dict[str, TokenBucket]:
    """Named rate budgets from AUTOMATION_PLAN section 2 / 7.

    request() falls back to the ``default`` bucket for any unlisted name, so adding a
    new call site never crashes; it just shares the default budget until tuned here.
    """
    budgets = {
        "default": RateBudget("default", capacity=60, refill_seconds=60),
        "device_add": RateBudget("device_add", capacity=25, refill_seconds=60),
        "device_patch": RateBudget("device_patch", capacity=20, refill_seconds=60),
        "device_read": RateBudget("device_read", capacity=60, refill_seconds=60),
        "device_async_poll": RateBudget("device_async_poll", capacity=90, refill_seconds=60),
        "subscription_add": RateBudget("subscription_add", capacity=4, refill_seconds=60),
        "subscription_read": RateBudget("subscription_read", capacity=30, refill_seconds=60),
        "subscription_async_poll": RateBudget("subscription_async_poll", capacity=30, refill_seconds=60),
        "service_catalog_read": RateBudget("service_catalog_read", capacity=60, refill_seconds=60),
    }
    return {name: TokenBucket(budget) for name, budget in budgets.items()}


class GreenLakeHttpClient:
    def __init__(
        self,
        base_url: str,
        token_provider,
        buckets: dict[str, TokenBucket] | None = None,
        *,
        max_retries: int = 4,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token_provider = token_provider
        self.buckets = buckets or default_rate_buckets()
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def _bucket(self, name: str) -> TokenBucket:
        return self.buckets.get(name, self.buckets["default"])

    async def request(self, method: str, path: str, *, bucket: str = "default", **kwargs: Any) -> httpx.Response:
        base_headers = dict(kwargs.pop("headers", {}))
        attempt = 0
        while True:
            await self._bucket(bucket).acquire()
            token = await self.token_provider.token()
            headers = {**base_headers, "Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
                response = await client.request(method, path, headers=headers, **kwargs)
            if response.status_code in RETRYABLE_STATUS and attempt < self.max_retries:
                attempt += 1
                await asyncio.sleep(_retry_delay(response, attempt))
                continue
            response.raise_for_status()
            return response

    async def poll_async(
        self,
        location: str,
        *,
        bucket: str = "device_async_poll",
        max_wait_seconds: float = 900.0,
        default_interval: float = 5.0,
    ) -> dict[str, Any]:
        """Poll a 202 Location async-operation resource until a terminal state.

        Honors ``suggestedPollingIntervalSeconds`` when the payload provides it. Returns
        the final payload on success; raises GreenLakeAsyncOperationError on terminal
        failure and TimeoutError if the operation does not settle within the budget.
        """
        deadline = time.monotonic() + max_wait_seconds
        while True:
            payload = (await self.request("GET", location, bucket=bucket)).json()
            status = str(payload.get("status") or payload.get("state") or "").upper()
            if status in TERMINAL_OK:
                return payload
            if status in TERMINAL_FAIL:
                raise GreenLakeAsyncOperationError(
                    f"Async operation {location} ended in {status}: {_async_error_detail(payload)}"
                )
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Async operation {location} did not finish within {max_wait_seconds:.0f}s")
            interval = float(payload.get("suggestedPollingIntervalSeconds") or default_interval)
            await asyncio.sleep(max(1.0, min(interval, 30.0)))


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), 30.0)
        except ValueError:
            pass
    return min(0.5 * (2 ** (attempt - 1)), 16.0)


def _async_error_detail(payload: dict[str, Any]) -> str:
    for key in ("error", "message", "detail", "failureReason", "errorDetails"):
        value = payload.get(key)
        if value:
            return str(value)
    return "no error detail in async-operation payload"
