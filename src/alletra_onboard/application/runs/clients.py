"""Runs context client seam — read-only array SSH client, command log and device trust context
bindings, and local terminal launcher (STANDARD L3, L4, B1)."""

from __future__ import annotations

from alletra_onboard.adapters.array.cli_client import ArrayCliClient
from alletra_onboard.adapters.array.cli_client import refusal as command_refusal
from alletra_onboard.adapters.command_log import bind as bind_command_log
from alletra_onboard.adapters.command_log import record as record_command
from alletra_onboard.adapters.command_log import unbind as unbind_command_log
from alletra_onboard.adapters.device_trust import bind as bind_device_trust
from alletra_onboard.adapters.device_trust import unbind as unbind_device_trust
from alletra_onboard.adapters.system.terminal import launch_terminal
from alletra_onboard.domain.shared import EndpointCreds


def make_array_cli(creds: EndpointCreds) -> ArrayCliClient:
    return ArrayCliClient(creds.host, creds.username, creds.password.get_secret_value())


__all__ = [
    "bind_command_log",
    "bind_device_trust",
    "command_refusal",
    "launch_terminal",
    "make_array_cli",
    "record_command",
    "unbind_command_log",
    "unbind_device_trust",
]
