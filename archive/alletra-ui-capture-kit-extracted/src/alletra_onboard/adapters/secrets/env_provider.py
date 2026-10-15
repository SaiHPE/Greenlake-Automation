from __future__ import annotations

import os


class EnvSecretProvider:
    def get(self, reference: str) -> str | None:
        if reference.startswith("env:"):
            return os.getenv(reference.removeprefix("env:"))
        return os.getenv(reference)
