"""GreenLake client factory — the seam between the onboarding context and adapters/greenlake/*
(mirrors provisioning/clients.py). Application code composes clients HERE, never from the adapter
classes directly. This is also the slot where the ADR-0006 cloud control plane (a DSCC provisioning
client) would plug in when it is built — deliberately not abstracted further until then.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from alletra_onboard.adapters.browser.cloudinit_wizard import CloudinitWizardAdapter
from alletra_onboard.adapters.browser.debug_browser import launch_debug_browser
from alletra_onboard.adapters.browser.dscc_setup import DsccSetupAdapter
from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials
from alletra_onboard.adapters.greenlake.devices import DevicesClient
from alletra_onboard.adapters.greenlake.http_client import GreenLakeHttpClient
from alletra_onboard.adapters.greenlake.service_catalog import ServiceCatalogClient
from alletra_onboard.adapters.greenlake.subscriptions import SubscriptionsClient
from alletra_onboard.config import Settings


@dataclass
class GreenLakeClients:
    token_provider: OAuthClientCredentials
    http: GreenLakeHttpClient
    devices: DevicesClient
    subscriptions: SubscriptionsClient
    service_catalog: ServiceCatalogClient


def missing_credentials(settings: Settings) -> list[str]:
    return [
        name
        for name, value in {
            "GL_CLIENT_ID": settings.gl_client_id,
            "GL_CLIENT_SECRET": settings.gl_client_secret,
            "GL_TOKEN_URL": settings.gl_token_url,
        }.items()
        if not value
    ]


def make_greenlake(settings: Settings) -> GreenLakeClients:
    token_provider = OAuthClientCredentials(
        settings.gl_token_url,
        settings.gl_client_id or "",
        settings.gl_client_secret or "",
    )
    http = GreenLakeHttpClient(settings.gl_base_url, token_provider)
    return GreenLakeClients(
        token_provider=token_provider,
        http=http,
        devices=DevicesClient(http),
        subscriptions=SubscriptionsClient(http),
        service_catalog=ServiceCatalogClient(http),
    )


def default_cloudinit_factory(settings: Settings, on_status: Callable[[str], None]) -> Any:
    # Launch mode: the product flow opens its own browser at the pasted cloudinit URL.
    return CloudinitWizardAdapter(
        headless=settings.browser_headless,
        cdp_url=None,
        artifact_dir=settings.artifact_dir,
        on_status=on_status,
    )


def default_dscc_factory(settings: Settings, cdp_url: str) -> Any:
    return DsccSetupAdapter(cdp_url=cdp_url, artifact_dir=settings.artifact_dir)


__all__ = [
    "GreenLakeClients",
    "default_cloudinit_factory",
    "default_dscc_factory",
    "launch_debug_browser",
    "make_greenlake",
    "missing_credentials",
]
