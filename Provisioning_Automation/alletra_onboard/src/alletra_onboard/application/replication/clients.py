"""Remote Copy SSH writer factory (STANDARD S2, ADR 0015): only partnership_apply may import this."""

from __future__ import annotations

from alletra_onboard.adapters.array.rc_cli_client import ArrayRcCliClient
from alletra_onboard.domain.plan_objects import RcPlanObjects
from alletra_onboard.domain.shared import EndpointCreds


def make_rc_writer(creds: EndpointCreds, objects: RcPlanObjects) -> ArrayRcCliClient:
    return ArrayRcCliClient(creds.host, creds.username, creds.password.get_secret_value(), objects=objects)


__all__ = ["make_rc_writer"]
