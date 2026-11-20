"""Platform client seam — wraps system adapters (net probe, clock, discovery tool) for the
platform context and entrypoints (STANDARD L3, L5)."""

from __future__ import annotations

from alletra_onboard.adapters.system.clock import clock_status, sync_clock
from alletra_onboard.adapters.system.discovery_tool import launch_discovery_tool
from alletra_onboard.adapters.system.net_probe import probe_tcp, probe_via_proxy

__all__ = [
    "clock_status",
    "launch_discovery_tool",
    "probe_tcp",
    "probe_via_proxy",
    "sync_clock",
]
