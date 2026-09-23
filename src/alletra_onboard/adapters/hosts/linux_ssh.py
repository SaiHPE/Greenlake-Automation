"""Read-only SSH discovery of a Linux host the sheet lists (SPEC-014 R4).

Runs a FIXED set of read commands, addressed by key — the client cannot run anything else. Nothing
is written; `sudo -n` is tried only for the two reads that need root and fails fast without a prompt.
"""

from __future__ import annotations

import re

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

from alletra_onboard.domain.discovery import HostRead
from alletra_onboard.domain.shared import normalize_wwpn

COMMANDS: dict[str, str] = {
    "hostname": "hostname",
    "os": "cat /etc/os-release",
    "serial": "cat /sys/class/dmi/id/product_serial",
    "serial_sudo": "sudo -n cat /sys/class/dmi/id/product_serial",
    "fc": "cat /sys/class/fc_host/host*/port_name",
    "iqn": "cat /etc/iscsi/initiatorname.iscsi",
    "multipath": "multipath -ll",
    "multipath_sudo": "sudo -n multipath -ll",
}

_NO_SERIAL = {"", "0", "none", "not specified", "to be filled by o.e.m.", "default string", "system serial number"}


class LinuxHostError(Exception):
    """Couldn't connect to or authenticate on the host."""


def parse_os_release(text: str) -> str:
    fields = {k: v.strip().strip('"') for k, _, v in (line.partition("=") for line in (text or "").splitlines()) if v}
    return fields.get("PRETTY_NAME") or " ".join(x for x in (fields.get("NAME"), fields.get("VERSION_ID")) if x)


def parse_serial(text: str) -> str:
    value = (text or "").strip().splitlines()[0].strip() if (text or "").strip() else ""
    return "" if value.lower() in _NO_SERIAL or "permission denied" in value.lower() else value


def parse_fc_port_names(text: str) -> list[str]:
    """`/sys/class/fc_host/host*/port_name` -> ['10000090FA8B1234', ...]; each line is `0x<16 hex>`."""
    out: list[str] = []
    for line in (text or "").splitlines():
        m = re.fullmatch(r"\s*(?:0x)?([0-9a-fA-F]{16})\s*", line)
        if m and (w := normalize_wwpn(m.group(1))) not in out and w != "0" * 16:
            out.append(w)
    return out


def parse_initiator_name(text: str) -> list[str]:
    out: list[str] = []
    for line in (text or "").splitlines():
        key, _, value = line.strip().partition("=")
        if key == "InitiatorName" and value.strip().lower().startswith("iqn.") and value.strip() not in out:
            out.append(value.strip())
    return out


_MP_DEVICE = re.compile(r"^(?:\S+\s+)?\(?(?:[0-9a-fA-F]{33}|\S+)\)?\s+dm-\d+\s+(\S+)")
_MP_PATH = re.compile(r"\d+:\d+:\d+:\d+\s+\S+\s+\d+:\d+\s+(\w+)\s+(\w+)")


def parse_multipath(text: str) -> str:
    """`multipath -ll` -> '2 Alletra/3PAR device(s), 4 path(s) each (all active)' or ''."""
    devices: list[list[str]] = []
    vendor_ok = False
    for line in (text or "").splitlines():
        head = _MP_DEVICE.match(line)
        if head:
            vendor_ok = "3PARdata" in head.group(1)
            if vendor_ok:
                devices.append([])
            continue
        path = _MP_PATH.search(line)
        if path and vendor_ok and devices:
            devices[-1].append(f"{path.group(1)} {path.group(2)}")
    if not devices:
        return ""
    counts = sorted({len(d) for d in devices})
    bad = sum(1 for d in devices for p in d if not p.startswith("active ready"))
    each = f"{counts[0]} path(s) each" if len(counts) == 1 else f"{counts[0]}–{counts[-1]} path(s)"
    return f"{len(devices)} Alletra/3PAR device(s), {each}" + (f", {bad} path(s) not active" if bad else " (all active)")


class LinuxHostClient:
    def __init__(self, host: str, username: str, password: str, port: int = 22,
                 timeout: float = 10.0, exec_timeout: float = 20.0) -> None:
        self.host, self.username, self.password, self.port = host, username, password, port
        self.timeout, self.exec_timeout = timeout, exec_timeout
        self._client = None

    def connect(self) -> None:
        if paramiko is None:
            raise LinuxHostError("SSH support (paramiko) is not available in this build.")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.host, port=self.port, username=self.username, password=self.password,
                           timeout=self.timeout, allow_agent=False, look_for_keys=False)
        except paramiko.AuthenticationException as exc:
            raise LinuxHostError(f"login failed for {self.username}@{self.host} — check the Hosts tab login") from exc
        except Exception as exc:
            raise LinuxHostError(f"could not reach {self.host}:{self.port} over SSH ({type(exc).__name__})") from exc
        self._client = client

    def read(self, key: str) -> str:
        """Run the fixed command named `key`; stdout, or '' when it failed (stderr is not content)."""
        if self._client is None:
            raise LinuxHostError("not connected")
        command = COMMANDS[key]
        try:
            _in, stdout, _err = self._client.exec_command(command, timeout=self.exec_timeout)
            out = stdout.read().decode("utf-8", "replace")
            return out if stdout.channel.recv_exit_status() == 0 else ""
        except Exception:  # noqa: BLE001 - one unreadable file must not sink the host read
            return ""

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001, S110 - closing a dead session
                pass
            self._client = None

    def __enter__(self) -> LinuxHostClient:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def read_linux_host(client, host_name: str, address: str) -> HostRead:
    """Every SPEC-014 R4 fact from a connected client (anything with `read(key) -> str`)."""
    read = HostRead(host_name=host_name, address=address, method="ssh", os="linux")
    read.hostname = client.read("hostname").strip()
    read.os_text = parse_os_release(client.read("os"))
    read.serial_number = parse_serial(client.read("serial")) or parse_serial(client.read("serial_sudo"))
    if not read.serial_number:
        read.notes.append("serial number not readable (needs root, or sudo without a password)")
    read.wwpns = parse_fc_port_names(client.read("fc"))
    read.iqns = parse_initiator_name(client.read("iqn"))
    mp = client.read("multipath") or client.read("multipath_sudo")
    read.multipath = parse_multipath(mp) or ("no Alletra/3PAR devices" if mp.strip() else "")
    if not mp.strip():
        read.notes.append("multipath not readable (needs root, or multipath-tools not installed)")
    return read
