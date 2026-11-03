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


def set_env_values(path: Path, updates: dict[str, str | None]) -> None:
    """Upsert KEY=VALUE lines IN PLACE, preserving comments, blank lines, and other keys.

    Replaces an existing key's line where it is, appends new keys at the end. Empty/None update
    values are ignored (the existing value is kept) so a blank field never wipes a saved secret.
    """
    effective = {key: value for key, value in updates.items() if value}
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out: list[str] = []
    written: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in effective:
                out.append(f"{key}={effective[key]}")
                written.add(key)
                continue
        out.append(line)  # preserve comments / blanks / untouched keys verbatim
    for key, value in effective.items():
        if key not in written:
            out.append(f"{key}={value}")
    content = "\n".join(out)
    path.write_text(content + "\n" if content else "", encoding="utf-8")


def update_gl_credentials(path: Path, values: dict[str, str | None]) -> None:
    """Merge the provided GL_* values (None/empty = keep existing) into the .env, in place."""
    set_env_values(path, {key: values.get(key) for key in GL_ENV_KEYS})


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
