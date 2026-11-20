"""Snapshot-schedule SSH writer factory (STANDARD S2, ADR 0016): only snapshots.apply may import this."""

from __future__ import annotations

from alletra_onboard.adapters.array.snap_cli_client import ArraySnapCliClient
from alletra_onboard.domain.plan_objects import SnapPlanObjects
from alletra_onboard.domain.shared import EndpointCreds


def make_snap_writer(creds: EndpointCreds, objects: SnapPlanObjects) -> ArraySnapCliClient:
    return ArraySnapCliClient(creds.host, creds.username, creds.password.get_secret_value(), objects=objects)


__all__ = ["make_snap_writer"]
