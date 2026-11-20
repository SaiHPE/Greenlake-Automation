"""Snapshot-schedule SSH writer factory (STANDARD S2, S3, ADR 0016): only snapshots.apply may import this."""

from __future__ import annotations

from typing import TYPE_CHECKING

from alletra_onboard.adapters.array import snap_cli_client as _snap_cli_client
from alletra_onboard.domain.approval import Approval, require_approval
from alletra_onboard.domain.plan_objects import SnapPlanObjects

if TYPE_CHECKING:
    from alletra_onboard.adapters.array.snap_cli_client import ArraySnapCliClient


def make_snap_writer(approval: Approval, objects: SnapPlanObjects) -> ArraySnapCliClient:
    live = require_approval(approval)
    creds = live.creds_for("snapshots", "A")
    return _snap_cli_client.ArraySnapCliClient(
        creds.host, creds.username, creds.password.get_secret_value(), objects=objects, approval=live,
    )


__all__ = ["make_snap_writer"]
