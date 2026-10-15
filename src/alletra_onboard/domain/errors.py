from __future__ import annotations

from enum import StrEnum


class ErrorCategory(StrEnum):
    CONFIG = "CONFIG"
    AUTH = "AUTH"
    GREENLAKE_CONTRACT = "GREENLAKE_CONTRACT"
    GREENLAKE_STATE = "GREENLAKE_STATE"
    RATE_LIMIT = "RATE_LIMIT"
    BROWSER_SELECTOR = "BROWSER_SELECTOR"
    PHYSICAL = "PHYSICAL"
    PROPAGATION = "PROPAGATION"


class OnboardError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        category: ErrorCategory,
        retryable: bool = False,
        remediation: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.category = category
        self.retryable = retryable
        self.remediation = remediation
