"""Read-only SSH discovery of a Linux host the sheet lists (SPEC-014 R4).

Runs a FIXED set of read commands, addressed by key — the client cannot run anything else. Nothing
is written; `sudo -n` is tried only for the two reads that need root and fails fast without a prompt.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

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
    # World-readable: "live" while the dm-multipath kernel module is loaded; absent when it is not
    # (and on a kernel with dm-multipath built in, which the major distributions do not ship).
    "dm_multipath": "cat /sys/module/dm_multipath/initstate",
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


# A map's first line: `mpatha (360002ac…) dm-2 3PARdata,VV`, or the WWID alone when there is no alias.
_MP_DEVICE = re.compile(r"^(?P<name>\S+)(?:\s+\([^)]+\))?\s+dm-\d+\s+(?P<vendor>[^,]+),")
# A path line: `  |- 7:0:0:1  sdb  8:16   active ready running` (dm state, checker state, device state).
_MP_PATH = re.compile(r"\d+:\d+:\d+:\d+\s+\S+\s+\d+:\d+\s+(\S+)\s+(\S+)\s+(\S+)")
_ALLETRA_VENDOR = "3PARdata"   # Alletra MP, Alletra 9000, Primera and 3PAR all report this vendor


@dataclass(frozen=True)
class MultipathDevice:
    name: str                          # the alias (mpatha), or the WWID when there is none
    paths: tuple[str, ...]             # "active ready running", one per path

    @property
    def failed(self) -> int:
        """Paths that are not carrying I/O. `ghost` is a standby path (ALUA), not a failure."""
        return sum(1 for p in self.paths if p.split()[:2] not in (["active", "ready"], ["active", "ghost"]))


def parse_multipath(text: str) -> list[MultipathDevice]:
    """The Alletra/3PAR devices in `multipath -ll` output, with their paths; other vendors are skipped."""
    found: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    for line in (text or "").splitlines():
        if head := _MP_DEVICE.match(line):
            current = None
            if head.group("vendor").strip() == _ALLETRA_VENDOR:
                current = []
                found.append((head.group("name"), current))
        elif current is not None and (path := _MP_PATH.search(line)):
            current.append(" ".join(path.groups()))
    return [MultipathDevice(name, tuple(paths)) for name, paths in found]


def _n(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def multipath_summary(devices: list[MultipathDevice], *, listed: bool, module_loaded: bool) -> tuple[str, str]:
    """(state, the one-line sentence shown after "multipath:").

    `listed`: `multipath -ll` ran (as root, or through sudo). `module_loaded`: dm-multipath is loaded.
    State is ok | uneven | degraded | none | not_set_up | not_permitted."""
    if not devices:
        if not module_loaded:
            return "not_set_up", ("not set up on this server (the dm-multipath module is not loaded). "
                                  "Set up multipath before volumes are presented.")
        if not listed:
            return "not_permitted", ("not read: it needs root, or sudo without a password. "
                                     "Use a root login on the Hosts tab to see it.")
        return "none", "set up, no Alletra/3PAR devices yet. They appear once volumes are presented and the host rescans."
    counts = Counter(len(d.paths) for d in devices)
    usual = max(counts, key=lambda c: (counts[c], c))
    odd = [d for d in devices if len(d.paths) != usual]
    sentence = f"{_n(len(devices), 'Alletra/3PAR device')}, {_n(usual, 'path')}" + (" each" if len(devices) > 1 else "")
    if odd:
        sentence += " except " + ", ".join(f"{d.name} ({_n(len(d.paths), 'path')})" for d in odd)
    failed = [d for d in devices if d.failed]
    if failed:
        sentence += f"; {_n(sum(d.failed for d in failed), 'path')} failed on " + ", ".join(d.name for d in failed)
    if failed or odd:
        return "degraded" if failed else "uneven", sentence + ". Check the zoning and cabling."
    return "ok", sentence + ", all active"


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

    def run(self, key: str) -> tuple[int, str]:
        """Run the fixed command named `key`: (exit status, stdout); -1 when it could not run.
        stderr is not content."""
        if self._client is None:
            raise LinuxHostError("not connected")
        command = COMMANDS[key]
        try:
            _in, stdout, _err = self._client.exec_command(command, timeout=self.exec_timeout)
            out = stdout.read().decode("utf-8", "replace")
            return stdout.channel.recv_exit_status(), out
        except Exception:  # noqa: BLE001 - one unreadable file must not sink the host read
            return -1, ""

    def read(self, key: str) -> str:
        """stdout of the fixed command named `key`, or '' when it failed."""
        status, out = self.run(key)
        return out if status == 0 else ""

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001 - closing a dead session
                pass
            self._client = None

    def __enter__(self) -> LinuxHostClient:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def read_linux_host(client, host_name: str, address: str) -> HostRead:
    """Every SPEC-014 R4 fact from a connected client (anything with `read(key) -> str` and
    `run(key) -> (exit status, stdout)`)."""
    read = HostRead(host_name=host_name, address=address, method="ssh", os="linux")
    read.hostname = client.read("hostname").strip()
    read.os_text = parse_os_release(client.read("os"))
    read.serial_number = parse_serial(client.read("serial")) or parse_serial(client.read("serial_sudo"))
    if not read.serial_number:
        read.notes.append("serial number not readable (needs root, or sudo without a password)")
    read.wwpns = parse_fc_port_names(client.read("fc"))
    read.iqns = parse_initiator_name(client.read("iqn"))
    # `multipath` refuses a non-root user ("need to be root", exit 1), and may not be on that user's
    # PATH (exit 127); `sudo -n` runs it as root when sudo needs no password. Exit 0 means it listed.
    status, mp = client.run("multipath")
    if status != 0:
        status, mp = client.run("multipath_sudo")
    devices = parse_multipath(mp) if status == 0 else []
    loaded = bool(devices) or client.read("dm_multipath").strip() == "live"
    read.multipath_state, read.multipath = multipath_summary(devices, listed=status == 0, module_loaded=loaded)
    if read.multipath_state == "not_permitted":
        read.notes.append("multipath not readable (needs root, or sudo without a password)")
    return read
