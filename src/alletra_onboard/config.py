from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")

    api_host: str = "127.0.0.1"
    api_port: int = 8765
    gl_client_id: str | None = None
    gl_client_secret: str | None = None
    gl_member_workspace_id: str | None = None
    gl_token_url: str = "https://sso.common.cloud.hpe.com/as/token.oauth2"
    gl_base_url: str = "https://global.api.greenlake.hpe.com"
    state_database_path: Path = Field(default=Path(".alletra_onboard/state.db"))
    artifact_dir: Path = Field(default=Path(".alletra_onboard/artifacts"))
    browser_cdp_url: str = "http://localhost:9222"
    browser_headless: bool = False
    # Proxy for the launched DSCC debug browser. None -> use the HTTPS_PROXY env var (the jump
    # box sets it). Set BROWSER_PROXY=direct:// in .env to force no proxy on a machine that has
    # HTTPS_PROXY set but reaches DSCC directly.
    browser_proxy: str | None = None
    browser_proxy_bypass: str = "localhost;127.0.0.1;169.254.*"
    # SAFETY FREEZE: provisioning WRITE actions (SAN zoning apply, host/volume/VLUN create) are
    # disabled until they've been validated against live hardware. Read-only discovery, zoning
    # verification, and the previews always work. Flip to true (env PROVISIONING_WRITES_ENABLED=true,
    # or set it in .env) only once the write paths are tested + signed off.
    provisioning_writes_enabled: bool = False


def load_settings() -> Settings:
    return Settings()
