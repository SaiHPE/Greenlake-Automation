"""Read-only default client factories: build an adapter from EndpointCreds (STANDARD S2, L3).
Injectable so services can be unit-tested with fakes. Every writer factory lives in its own
protected module (`runs/writer_clients.py`, `replication/clients.py`, `snapshots/clients.py`)."""

from __future__ import annotations

from alletra_onboard.adapters.array.cli_client import ArrayCliClient
from alletra_onboard.adapters.array.wsapi_client import (
    SDK_IMPORT_ERROR,
    HPE3ParClient,
    WsapiReader,
)
from alletra_onboard.adapters.array.wsapi_v3_client import WsapiV3Client
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.adapters.hosts.linux_ssh import LinuxHostClient, read_linux_host
from alletra_onboard.adapters.hosts.windows_winrm import WindowsHostClient, read_windows_host
from alletra_onboard.adapters.vcenter.vcenter_client import VCenterClient
from alletra_onboard.domain.shared import EndpointCreds


def wsapi_capability() -> dict[str, object]:
    """Whether this build (frozen or not) imported the 3PAR SDK — and if not, why."""
    return {"wsapi_sdk": HPE3ParClient is not None, "wsapi_sdk_error": SDK_IMPORT_ERROR}


def make_wsapi(creds: EndpointCreds) -> WsapiReader:
    return WsapiReader(creds.host, creds.username, creds.password.get_secret_value())


def make_wsapi_v3(creds: EndpointCreds) -> WsapiV3Client:
    # ADR 0021: the array's file side over WSAPI v3, GET only. Opened by `with`, which logs in.
    return WsapiV3Client(creds.host, creds.username, creds.password.get_secret_value())


def make_array_cli(creds: EndpointCreds) -> ArrayCliClient:
    # Read-only SSH to the array (showport / showportdev ns) — used for switch-free zoning verify.
    return ArrayCliClient(creds.host, creds.username, creds.password.get_secret_value())


def make_vcenter(creds: EndpointCreds) -> VCenterClient:
    return VCenterClient(creds.host, creds.username, creds.password.get_secret_value())


def make_brocade(creds: EndpointCreds) -> BrocadeClient:
    return BrocadeClient(creds.host, creds.username, creds.password.get_secret_value())


def make_linux_host(creds: EndpointCreds) -> LinuxHostClient:
    return LinuxHostClient(creds.host, creds.username, creds.password.get_secret_value())


def make_windows_host(creds: EndpointCreds) -> WindowsHostClient:
    return WindowsHostClient(creds.host, creds.username, creds.password.get_secret_value())


__all__ = [
    "make_array_cli",
    "make_brocade",
    "make_linux_host",
    "make_vcenter",
    "make_windows_host",
    "make_wsapi",
    "make_wsapi_v3",
    "read_linux_host",
    "read_windows_host",
    "wsapi_capability",
]
