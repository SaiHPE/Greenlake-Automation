"""Read-only SSH discovery of a Linux host the sheet lists (SPEC-014 R4).

Runs a FIXED set of read commands, addressed by key — the client cannot run anything else. Nothing
is written; `sudo -n` is tried only for the two reads that need root and fails fast without a prompt.
"""

from __future__ import annotations

import re
import time
from collections import Counter
from dataclasses import dataclass

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe
    paramiko = None

from alletra_onboard.adapters import command_log, device_trust
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
# A map that has lost every path prints `##,##` in place of the vendor and product.
_MP_DEVICE = re.compile(r"^(?P<name>\S+)(?:\s+\((?P<wwid>[^)]+)\))?\s+dm-\d+\s+(?P<vendor>[^,]+),")
# A path line: `  |- 7:0:0:1  sdb  8:16   active ready running` (dm state, checker state, device state).
# A path whose device is gone from sysfs prints `#:#:#:#` and `-`; the checker state may be two words.
_MP_PATH = re.compile(r"[#\d]+:[#\d]+:[#\d]+:[#\d]+\s+(?P<dev>\S+)\s+[#\d]+:[#\d]+\s+"
                      r"(?P<states>\S+\s+(?:i/o\s+\S+|\S+)\s+\S+)")
_ALLETRA_VENDOR = "3PARdata"   # Alletra MP, Alletra 9000, Primera and 3PAR all report this vendor
# The 3PAR/Alletra WWID: NAA type 6 (360002ac…) or type 5 (350002ac…), HPE 3PAR's OUI 0002ac.
_ALLETRA_WWID = re.compile(r"3[56]0002ac", re.IGNORECASE)
_NO_DEVICE = "no device: "
# Carrying I/O, or ready to: `ghost` is a standby path (ALUA), `i/o pending` a check still running.
_WORKING = re.compile(r"active\s+(?:ready|ghost|i/o\s+pending)\s")
_MOST_NAMED = 3


@dataclass(frozen=True)
class MultipathDevice:
    name: str                          # the alias (mpatha), or the WWID when there is none
    paths: tuple[str, ...]             # "active ready running", one per path; "no device: …" when it is gone
    wwid: str = ""

    @property
    def failed(self) -> int:
        """Paths that are not carrying I/O: failed, faulty, or the device gone from sysfs."""
        return sum(1 for p in self.paths if not _WORKING.match(p + " "))


def _is_alletra(vendor: str, wwid: str) -> bool:
    return vendor == _ALLETRA_VENDOR or (vendor == "##" and bool(_ALLETRA_WWID.match(wwid)))


def parse_multipath(text: str) -> list[MultipathDevice]:
    """The Alletra/3PAR devices in `multipath -ll` output, with their paths; other vendors are skipped."""
    found: list[tuple[str, str, list[str]]] = []
    current: list[str] | None = None
    for line in (text or "").splitlines():
        if head := _MP_DEVICE.match(line):
            current = None
            wwid = head.group("wwid") or head.group("name")
            if _is_alletra(head.group("vendor").strip(), wwid):
                current = []
                found.append((head.group("name"), wwid, current))
        elif current is not None and (path := _MP_PATH.search(line)):
            states = " ".join(path.group("states").split())
            current.append(_NO_DEVICE + states if path.group("dev") == "-" else states)
    return [MultipathDevice(name, tuple(paths), wwid) for name, wwid, paths in found]


def lists_maps(text: str) -> bool:
    """`multipath -ll` printed at least one map, of any vendor."""
    return any(_MP_DEVICE.match(line) for line in (text or "").splitlines())


def _n(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def _paths(count: int) -> str:
    return "no paths" if count == 0 else _n(count, "path")


def _names(names: list[str]) -> str:
    """At most three names, then "and N more" (one fabric down can touch every device)."""
    if len(names) <= _MOST_NAMED:
        return ", ".join(names)
    return ", ".join(names[:_MOST_NAMED]) + f" and {len(names) - _MOST_NAMED} more"


def multipath_summary(devices: list[MultipathDevice], *, listed: bool, module_loaded: bool,
                      timed_out: bool = False) -> tuple[str, str]:
    """(state, the one-line sentence shown after "multipath:").

    `listed`: `multipath -ll` ran (as root, or through sudo). `module_loaded`: dm-multipath is loaded.
    `timed_out`: the command did not answer in time. State is ok | uneven | degraded | none |
    not_set_up | not_permitted | timed_out."""
    if timed_out:
        return "timed_out", "could not be read: the command timed out. Run Discovery again."
    if not devices:
        if not module_loaded:
            return "not_set_up", ("not set up on this server (the dm-multipath module is not loaded). "
                                  "Set up multipath before volumes are presented.")
        if not listed:
            return "not_permitted", ("not read: it needs root, or sudo without a password. "
                                     "Use a root login on the Hosts tab to see it.")
        return "none", "set up, no Alletra/3PAR devices yet. They appear once volumes are presented and the host rescans."
    reached = Counter(len(d.paths) for d in devices if d.paths)
    if not reached:
        sentence = f"{_n(len(devices), 'Alletra/3PAR device')} with no paths: " + _names([d.name for d in devices])
        return "degraded", sentence + ". Check the zoning and cabling."
    usual = max(reached, key=lambda c: (reached[c], c))
    odd = [d for d in devices if len(d.paths) != usual]
    sentence = f"{_n(len(devices), 'Alletra/3PAR device')}, {_n(usual, 'path')}" + (" each" if len(devices) > 1 else "")
    if odd:
        sentence += " except " + _names([f"{d.name} ({_paths(len(d.paths))})" for d in odd])
    failed = [d for d in devices if d.failed]
    if failed:
        sentence += f"; {_n(sum(d.failed for d in failed), 'path')} failed on " + _names([d.name for d in failed])
    thin = [d for d in devices if len(d.paths) <= 1]
    if failed or odd or thin:
        single = " A single path is no redundancy." if any(len(d.paths) == 1 for d in devices) else ""
        state = "degraded" if failed or thin else "uneven"
        return state, sentence + "." + single + " Check the zoning and cabling."
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
        # ADR 0026: trusted on first contact, pinned for the run.
        try:
            client = device_trust.open_ssh(self.host, self.port, device="Linux host", username=self.username,
                                           password=self.password, timeout=self.timeout)
        except device_trust.DeviceTrustError as exc:
            raise LinuxHostError(str(exc)) from exc
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
        started = time.monotonic()
        try:
            _in, stdout, _err = self._client.exec_command(command, timeout=self.exec_timeout)
            out = stdout.read().decode("utf-8", "replace")
            status = stdout.channel.recv_exit_status()
        except Exception as exc:  # noqa: BLE001 - one unreadable file must not sink the host read
            command_log.record(target=self.host, transport="host-ssh", command=command, started=started,
                               ok=False, result=type(exc).__name__, secrets=[self.password])
            return -1, ""
        command_log.record(target=self.host, transport="host-ssh", command=command, started=started,
                           ok=status == 0, result=f"exit {status}", output=out, secrets=[self.password])
        return status, out

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
    # -1 is a command that did not answer in time: sudo would only wait again.
    status, mp = client.run("multipath")
    if status not in (0, -1):
        status, mp = client.run("multipath_sudo")
    timed_out = status == -1
    devices = parse_multipath(mp) if status == 0 else []
    # A listing with maps proves the driver is there, even built into the kernel (no initstate file).
    loaded = timed_out or (status == 0 and lists_maps(mp)) or client.read("dm_multipath").strip() == "live"
    read.multipath_state, read.multipath = multipath_summary(devices, listed=status == 0, module_loaded=loaded,
                                                             timed_out=timed_out)
    if read.multipath_state == "not_permitted":
        read.notes.append("multipath not readable (needs root, or sudo without a password)")
    elif read.multipath_state == "timed_out":
        read.notes.append("multipath not read: the command timed out")
    return read
