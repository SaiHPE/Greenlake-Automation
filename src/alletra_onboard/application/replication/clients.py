"""Remote Copy SSH writer factory (STANDARD S2, S3, ADR 0015): only partnership_apply may import this."""

from __future__ import annotations

from typing import TYPE_CHECKING

from alletra_onboard.adapters.array import rc_cli_client as _rc_cli_client
from alletra_onboard.domain.approval import Approval, Side, require_approval
from alletra_onboard.domain.plan_objects import RcPlanObjects

if TYPE_CHECKING:
    from alletra_onboard.adapters.array.rc_cli_client import ArrayRcCliClient


def make_rc_writer(approval: Approval, side: Side, objects: RcPlanObjects) -> ArrayRcCliClient:
    live = require_approval(approval)
    creds = live.creds_for("rc_partnership", side)
    return _rc_cli_client.ArrayRcCliClient(
        creds.host, creds.username, creds.password.get_secret_value(), objects=objects, approval=live,
    )


__all__ = ["make_rc_writer"]
