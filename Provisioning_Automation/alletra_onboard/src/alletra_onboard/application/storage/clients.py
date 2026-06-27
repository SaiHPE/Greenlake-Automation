"""Default client factories: build an adapter from EndpointCreds. Injectable so services can be
unit-tested with fakes (the live clients need an array / vCenter / switches)."""

from __future__ import annotations

from alletra_onboard.adapters.array.wsapi_client import WsapiClient
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.adapters.vcenter.vcenter_client import VCenterClient
from alletra_onboard.domain.storage import EndpointCreds


def make_wsapi(creds: EndpointCreds) -> WsapiClient:
    return WsapiClient(creds.host, creds.username, creds.password.get_secret_value())


def make_vcenter(creds: EndpointCreds) -> VCenterClient:
    return VCenterClient(creds.host, creds.username, creds.password.get_secret_value())


def make_brocade(creds: EndpointCreds) -> BrocadeClient:
    return BrocadeClient(creds.host, creds.username, creds.password.get_secret_value())
