from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass


SECRET_PATTERNS = (
    re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"(client_secret\s*[=:]\s*)[^\s&]+", re.IGNORECASE),
    re.compile(r"(subscription[_ -]?key\s*[=:]\s*)[^\s&]+", re.IGNORECASE),
)


def redact(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(r"\1<redacted>", redacted)
    return redacted


@dataclass(slots=True)
class RateBudget:
    name: str
    capacity: int
    refill_seconds: float


class TokenBucket:
    def __init__(self, budget: RateBudget) -> None:
        self.budget = budget
        self._tokens = float(budget.capacity)
        self._updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1:
                    self._tokens -= 1
                    return
                wait_seconds = min(self.budget.refill_seconds / self.budget.capacity, 1.0)
            await asyncio.sleep(wait_seconds)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._updated_at
        refill_rate = self.budget.capacity / self.budget.refill_seconds
        self._tokens = min(self.budget.capacity, self._tokens + elapsed * refill_rate)
        self._updated_at = now
