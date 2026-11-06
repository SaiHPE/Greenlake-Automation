"""Read-only WinRM discovery of a Windows host the sheet lists (SPEC-014 R5).

Runs a FIXED set of PowerShell reads, addressed by key — the client cannot run anything else. Each
read emits JSON so the parse never depends on the host's display formatting or locale.
"""

from __future__ import annotations

import json

try:
    import winrm
    from winrm.exceptions import InvalidCredentialsError
except ImportError:  # pragma: no cover - bundled in the .exe
    winrm = None
    InvalidCredentialsError = Exception

from alletra_onboard.domain.discovery import HostRead
from alletra_onboard.domain.shared import normalize_wwpn

SCRIPTS: dict[str, str] = {
    "hostname": "$env:COMPUTERNAME",
    "os": "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version | ConvertTo-Json -Compress",
    "serial": "(Get-CimInstance Win32_BIOS).SerialNumber",
    "initiators": (
        "ConvertTo-Json -Compress -InputObject @(Get-InitiatorPort -ErrorAction SilentlyContinue | "
        "Select-Object NodeAddress,PortAddress)"
    ),
    "mpio": (
        "$f = (Get-WindowsFeature Multipath-IO -ErrorAction SilentlyContinue).InstallState; "
        "$c = @(Get-MSDSMSupportedHW -ErrorAction SilentlyContinue | Where-Object VendorId -eq '3PARdata').Count; "
        "$d = @(Get-Disk -ErrorAction SilentlyContinue | Where-Object FriendlyName -like '3PARdata*').Count; "
        "ConvertTo-Json -Compress @{feature = \"$f\"; claimed = $c; disks = $d}"
    ),
}

_NO_SERIAL = {"", "0", "none", "not specified", "to be filled by o.e.m.", "default string", "system serial number"}


class WindowsHostError(Exception):
    """Couldn't connect to or authenticate on the host."""


def _json(text: str):
    text = (text or "").strip().lstrip("\ufeff")
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


def parse_os(text: str) -> str:
    data = _json(text)
    return str(data.get("Caption") or "").strip() if isinstance(data, dict) else ""


def parse_serial(text: str) -> str:
    value = (text or "").strip()
    return "" if value.lower() in _NO_SERIAL else value


def parse_initiators(text: str) -> tuple[list[str], list[str]]:
    """`Get-InitiatorPort` -> (FC WWPNs, iSCSI IQNs). Classified by address shape, not ConnectionType:
    an FC port's PortAddress is 16 hex; an iSCSI initiator's NodeAddress is its IQN."""
    data = _json(text)
    rows = data if isinstance(data, list) else [data] if isinstance(data, dict) else []
    wwpns: list[str] = []
    iqns: list[str] = []
    for row in rows:
        node = str(row.get("NodeAddress") or "").strip()
        port = normalize_wwpn(str(row.get("PortAddress") or ""))
        if node.lower().startswith("iqn.") and node not in iqns:
            iqns.append(node)
        elif len(port) == 16 and port not in wwpns and port != "0" * 16:
            wwpns.append(port)
    return wwpns, iqns


def parse_mpio(text: str) -> str:
    data = _json(text)
    if not isinstance(data, dict):
        return ""
    feature = str(data.get("feature") or "").strip() or "state not readable"
    claimed = "3PARdata VV claimed by MSDSM" if int(data.get("claimed") or 0) else "3PARdata VV NOT claimed by MSDSM"
    return f"MPIO {feature}; {claimed}; {int(data.get('disks') or 0)} Alletra/3PAR disk(s)"


class WindowsHostClient:
    """NTLM over WinRM: HTTP 5985 (message-encrypted) first, HTTPS 5986 if 5985 is closed."""

    def __init__(self, host: str, username: str, password: str, timeout: int = 30) -> None:
        self.host, self.username, self.password, self.timeout = host, username, password, timeout
        self._session = None

    def _session_for(self, url: str):
        return winrm.Session(
            url, auth=(self.username, self.password), transport="ntlm",
            server_cert_validation="ignore",   # lab hosts carry self-signed WinRM listeners
            proxy=None,                        # never tunnel an on-prem host through the lab proxy
            read_timeout_sec=self.timeout, operation_timeout_sec=self.timeout - 10,
        )

    def connect(self) -> None:
        if winrm is None:
            raise WindowsHostError("WinRM support (pywinrm) is not available in this build.")
        last: Exception | None = None
        for url in (f"http://{self.host}:5985/wsman", f"https://{self.host}:5986/wsman"):
            session = self._session_for(url)
            try:
                session.run_ps(SCRIPTS["hostname"])
            except InvalidCredentialsError as exc:
                hint = "" if ("\\" in self.username or "@" in self.username) else (
                    " (a domain-joined server needs COMPUTERNAME\\user for a local account, or DOMAIN\\user)"
                )
                raise WindowsHostError(
                    f"login failed for {self.username}@{self.host} — check the Hosts tab login{hint}"
                ) from exc
            except Exception as exc:  # noqa: BLE001 - refused / timeout / TLS: try the next listener
                last = exc
                continue
            self._session = session
            return
        raise WindowsHostError(
            f"could not reach WinRM on {self.host} (5985/5986: {type(last).__name__}) — is WinRM enabled and "
            "the port open from the jump box?"
        )

    def read(self, key: str) -> str:
        """Run the fixed script named `key`; stdout, or '' when it failed."""
        if self._session is None:
            raise WindowsHostError("not connected")
        try:
            response = self._session.run_ps(SCRIPTS[key])
        except Exception:  # noqa: BLE001 - one failed read must not sink the host read
            return ""
        return response.std_out.decode("utf-8", "replace") if response.status_code == 0 else ""

    def close(self) -> None:
        self._session = None

    def __enter__(self) -> WindowsHostClient:
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def read_windows_host(client, host_name: str, address: str) -> HostRead:
    """Every SPEC-014 R5 fact from a connected client (anything with `read(key) -> str`)."""
    read = HostRead(host_name=host_name, address=address, method="winrm", os="windows")
    read.hostname = client.read("hostname").strip()
    read.os_text = parse_os(client.read("os"))
    read.serial_number = parse_serial(client.read("serial"))
    if not read.serial_number:
        read.notes.append("serial number not reported by Win32_BIOS")
    read.wwpns, read.iqns = parse_initiators(client.read("initiators"))
    read.multipath = parse_mpio(client.read("mpio"))
    if not read.multipath:
        read.notes.append("MPIO state not readable (needs a local administrator login)")
    return read
