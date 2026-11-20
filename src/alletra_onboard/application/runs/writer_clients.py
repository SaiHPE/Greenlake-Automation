"""WSAPI writer factory (STANDARD S2, S3): only the four apply modules may import this module."""

from __future__ import annotations

from alletra_onboard.adapters.array.wsapi_writer import WsapiWriter
from alletra_onboard.domain.approval import Approval, Purpose, Side, require_approval


def make_wsapi_writer(approval: Approval, purpose: Purpose, side: Side) -> WsapiWriter:
    live = require_approval(approval)
    creds = live.creds_for(purpose, side)
    return WsapiWriter(creds.host, creds.username, creds.password.get_secret_value(), approval=live)


__all__ = ["WsapiWriter", "make_wsapi_writer"]
