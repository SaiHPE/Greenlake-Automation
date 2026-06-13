"""GreenLake credential storage in a local gitignored .env — shared by the CLI and the API.

The frontend's Configure screen and `onboard configure` both write the same five keys, so the
read/write/mask helpers live here rather than in the CLI module.
"""

from __future__ import annotations

from pathlib import Path

GL_ENV_KEYS = (
    "GL_CLIENT_ID",
    "GL_CLIENT_SECRET",
    "GL_TOKEN_URL",
    "GL_BASE_URL",
    "GL_MEMBER_WORKSPACE_ID",
)


def read_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def write_env(path: Path, data: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in data.items() if value != ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_gl_credentials(path: Path, values: dict[str, str | None]) -> None:
    """Merge the provided GL_* values (None/empty = keep existing) into the .env."""
    current = read_env(path)
    for key in GL_ENV_KEYS:
        value = values.get(key)
        if value:
            current[key] = value
    write_env(path, current)


def masked_gl_credentials(path: Path) -> dict[str, str]:
    """Current GL_* values with the secret masked — safe to return over the API / print."""
    current = read_env(path)
    out: dict[str, str] = {}
    for key in GL_ENV_KEYS:
        value = current.get(key, "")
        if key == "GL_CLIENT_SECRET":
            out[key] = "****" if value else ""
        else:
            out[key] = value
    return out
