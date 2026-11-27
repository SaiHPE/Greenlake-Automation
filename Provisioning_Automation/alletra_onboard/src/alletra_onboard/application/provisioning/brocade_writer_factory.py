"""Brocade FOS zoning SSH writer factory (STANDARD S2, S3, ADR 0033): only provisioning.zoning_apply may import this."""

from __future__ import annotations

from typing import TYPE_CHECKING

from alletra_onboard.adapters.fabric import brocade_writer as _brocade_writer
from alletra_onboard.domain.approval import Approval, require_approval
from alletra_onboard.domain.plan_objects import ZoningPlanObjects
from alletra_onboard.domain.shared import Fabric

if TYPE_CHECKING:
    from alletra_onboard.adapters.fabric.brocade_writer import BrocadeZoneWriter


def make_brocade_writer(
    approval: Approval,
    fabric: Fabric,
    objects: ZoningPlanObjects,
) -> BrocadeZoneWriter:
    live = require_approval(approval)
    return _brocade_writer.BrocadeZoneWriter(live, fabric, objects)


__all__ = ["make_brocade_writer"]
