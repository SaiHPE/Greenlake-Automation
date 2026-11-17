"""Default client factories: build an adapter from EndpointCreds. Injectable so services can be
unit-tested with fakes (the live clients need an array / vCenter / switches)."""

from __future__ import annotations

from alletra_onboard.adapters.array.cli_client import ArrayCliClient
from alletra_onboard.adapters.array.rc_cli_client import ArrayRcCliClient, RcPlanObjects
from alletra_onboard.adapters.array.snap_cli_client import ArraySnapCliClient, SnapPlanObjects
from alletra_onboard.adapters.array.wsapi_client import WsapiClient
from alletra_onboard.adapters.array.wsapi_v3_client import WsapiV3Client
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient
from alletra_onboard.adapters.hosts.linux_ssh import LinuxHostClient
from alletra_onboard.adapters.hosts.windows_winrm import WindowsHostClient
from alletra_onboard.adapters.vcenter.vcenter_client import VCenterClient
from alletra_onboard.domain.shared import EndpointCreds


def make_wsapi(creds: EndpointCreds) -> WsapiClient:
    return WsapiClient(creds.host, creds.username, creds.password.get_secret_value())


def make_wsapi_v3(creds: EndpointCreds) -> WsapiV3Client:
    # ADR 0021: the array's file side over WSAPI v3, GET only. Opened by `with`, which logs in.
    return WsapiV3Client(creds.host, creds.username, creds.password.get_secret_value())


def make_array_cli(creds: EndpointCreds) -> ArrayCliClient:
    # Read-only SSH to the array (showport / showportdev ns) — used for switch-free zoning verify.
    return ArrayCliClient(creds.host, creds.username, creds.password.get_secret_value())


def make_rc_cli(creds: EndpointCreds, objects: RcPlanObjects) -> ArrayRcCliClient:
    # ADR 0015: the write-scoped SSH client for Remote Copy links and targets. Only the apply of an
    # approved replication plan builds one, with the ports, addresses and target that plan names on
    # this array (ADR 0025 condition 3).
    return ArrayRcCliClient(creds.host, creds.username, creds.password.get_secret_value(), objects=objects)


def make_snap_cli(creds: EndpointCreds, objects: SnapPlanObjects) -> ArraySnapCliClient:
    # ADR 0016: the write-scoped SSH client for snapshot schedules. Only the apply of an approved snapshot
    # plan builds one, with the (schedule name, source) pairs that plan creates (ADR 0025 condition 3).
    return ArraySnapCliClient(creds.host, creds.username, creds.password.get_secret_value(), objects=objects)


def make_vcenter(creds: EndpointCreds) -> VCenterClient:
    return VCenterClient(creds.host, creds.username, creds.password.get_secret_value())


def make_brocade(creds: EndpointCreds) -> BrocadeClient:
    return BrocadeClient(creds.host, creds.username, creds.password.get_secret_value())


def make_linux_host(creds: EndpointCreds) -> LinuxHostClient:
    return LinuxHostClient(creds.host, creds.username, creds.password.get_secret_value())


def make_windows_host(creds: EndpointCreds) -> WindowsHostClient:
    return WindowsHostClient(creds.host, creds.username, creds.password.get_secret_value())
