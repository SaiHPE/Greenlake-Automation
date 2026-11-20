"""Documents context client seam — read-only array SSH and WSAPI v3 clients (STANDARD L3)."""

from __future__ import annotations

from alletra_onboard.adapters.array.cli_client import ArrayCliClient
from alletra_onboard.adapters.array.wsapi_v3_client import WsapiV3Client


def make_verify_cli(*, host: str, username: str, password: str) -> ArrayCliClient:
    return ArrayCliClient(host=host, username=username, password=password)


def make_verify_wsapi_v3(*, host: str, username: str, password: str) -> WsapiV3Client:
    return WsapiV3Client(host=host, username=username, password=password)
