"""GreenLake configuration and jump-box prerequisite routes."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from alletra_onboard.api.schemas import (
    CheckResponse,
    ConfigStatusResponse,
    ConfigureRequest,
    ConnectivityResponse,
    ConnectivityResultItem,
    FirewallRule,
    FirewallRulesResponse,
    ProxySaveRequest,
    ProxyStatusResponse,
)
from alletra_onboard.application.onboarding.health import greenlake_check
from alletra_onboard.application.platform import prereqs
from alletra_onboard.application.platform.configuring import (
    masked_gl_credentials,
    set_env_values,
    update_gl_credentials,
)
from alletra_onboard.application.platform.proxy import (
    DIRECT,
    ProxyResolver,
    apply_proxy_env,
    is_direct,
    normalize_proxy,
    os_system_proxy,
)
from alletra_onboard.config import load_settings


async def config_check() -> CheckResponse:
    # Re-load settings so credentials saved a moment ago are picked up.
    return CheckResponse(report=await greenlake_check(load_settings()))


async def prereq_firewall(region: str = "jp1") -> FirewallRulesResponse:
    rules = [
        FirewallRule(fqdn=fqdn, port=port, initiator=initiator, purpose=purpose)
        for fqdn, port, initiator, purpose in prereqs.rules_for(region)
    ]
    return FirewallRulesResponse(region=region, rules=rules)


async def prereq_firewall_txt(region: str = "jp1") -> PlainTextResponse:
    return PlainTextResponse(
        prereqs.firewall_text(region),
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="alletra-firewall-requirements.txt"'},
    )


async def prereq_connectivity(region: str = "jp1") -> ConnectivityResponse:
    # Reachability to the HPE endpoints via the SAME path the tool uses: through the effective
    # proxy (auto-detected system proxy or the manual override) if any, else direct.
    manual = load_settings().alletra_proxy
    results = await prereqs.check_connectivity(region, manual_proxy=manual)
    items = [
        ConnectivityResultItem(host=r.host, port=r.port, reachable=r.reachable, detail=r.detail, via=r.via)
        for r in results
    ]
    effective = ProxyResolver(manual).for_url("https://common.cloud.hpe.com")
    return ConnectivityResponse(
        region=region, results=items, all_reachable=all(i.reachable for i in items), proxy=effective
    )


async def prereq_proxy_status() -> ProxyStatusResponse:
    manual = load_settings().alletra_proxy or None
    # os_system_proxy, NOT detect_system_proxy: the latter reads the HTTPS_PROXY env that
    # apply_proxy_env publishes, so it would report our own override back as "detected".
    detected = os_system_proxy("https://common.cloud.hpe.com")
    effective = ProxyResolver(manual).for_url("https://common.cloud.hpe.com")
    forced = is_direct(manual)
    source = "direct" if forced or not effective else ("manual" if normalize_proxy(manual) else "system")
    return ProxyStatusResponse(
        detected=detected, manual=manual, effective=effective, source=source, forced_direct=forced,
    )


def build_prereqs_router(env_path: Path) -> APIRouter:
    router = APIRouter()

    @router.get("/config", response_model=ConfigStatusResponse)
    async def get_config() -> ConfigStatusResponse:
        values = masked_gl_credentials(env_path)
        configured = bool(values.get("GL_CLIENT_ID")) and bool(values.get("GL_CLIENT_SECRET"))
        return ConfigStatusResponse(configured=configured, values=values)

    @router.post("/config", response_model=ConfigStatusResponse)
    async def set_config(request: ConfigureRequest) -> ConfigStatusResponse:
        update_gl_credentials(
            env_path,
            {
                "GL_CLIENT_ID": request.gl_client_id,
                "GL_CLIENT_SECRET": request.gl_client_secret,
                "GL_TOKEN_URL": request.gl_token_url,
                "GL_BASE_URL": request.gl_base_url,
                "GL_MEMBER_WORKSPACE_ID": request.gl_member_workspace_id,
            },
        )
        return await get_config()

    router.post("/config/check", response_model=CheckResponse)(config_check)
    router.get("/prereqs/firewall", response_model=FirewallRulesResponse)(prereq_firewall)
    router.get("/prereqs/firewall.txt", response_class=PlainTextResponse)(prereq_firewall_txt)
    router.get("/prereqs/connectivity", response_model=ConnectivityResponse)(prereq_connectivity)
    router.get("/prereqs/proxy", response_model=ProxyStatusResponse)(prereq_proxy_status)

    @router.post("/prereqs/proxy", response_model=ProxyStatusResponse)
    async def prereq_proxy_save(request: ProxySaveRequest) -> ProxyStatusResponse:
        # os.environ is the source of truth for the running process (pydantic reads it); .env persists
        # a set across restarts. Then re-publish the effective proxy for httpx + browser.
        value = (request.proxy or "").strip()
        # Normalize a direct request to the canonical sentinel so what persists is unambiguous, and
        # so it is NON-EMPTY: set_env_values ignores empty values (it must never wipe a saved
        # secret), which is precisely why blanking the field could not persist "go direct".
        if is_direct(value):
            value = DIRECT
        os.environ["ALLETRA_PROXY"] = value
        if value:
            set_env_values(env_path, {"ALLETRA_PROXY": value})
        apply_proxy_env(value or None)
        return await prereq_proxy_status()

    return router
