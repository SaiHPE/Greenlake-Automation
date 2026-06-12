from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserSessionConfig:
    cdp_url: str = "http://localhost:9222"
    headless: bool = False


class BrowserSessionLost(RuntimeError):
    pass
