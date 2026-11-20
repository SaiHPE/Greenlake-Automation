"""WSAPI writer factory (STANDARD S2): only the four apply modules may import this module."""

from __future__ import annotations

from alletra_onboard.adapters.array.wsapi_writer import WsapiWriter
from alletra_onboard.domain.shared import EndpointCreds


def make_wsapi_writer(creds: EndpointCreds) -> WsapiWriter:
    return WsapiWriter(creds.host, creds.username, creds.password.get_secret_value())


__all__ = ["make_wsapi_writer"]
