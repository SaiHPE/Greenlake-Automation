"""WSAPI writer factory (STANDARD S2, S3): only the four apply modules may import this module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from alletra_onboard.adapters.array import wsapi_writer as _wsapi_writer
from alletra_onboard.domain.approval import Approval, Purpose, Side, require_approval

if TYPE_CHECKING:
    from alletra_onboard.adapters.array.wsapi_writer import WsapiWriter


def make_wsapi_writer(approval: Approval, purpose: Purpose, side: Side) -> WsapiWriter:
    live = require_approval(approval)
    creds = live.creds_for(purpose, side)
    return _wsapi_writer.WsapiWriter(
        creds.host, creds.username, creds.password.get_secret_value(), approval=live,
    )


__all__ = ["make_wsapi_writer"]
