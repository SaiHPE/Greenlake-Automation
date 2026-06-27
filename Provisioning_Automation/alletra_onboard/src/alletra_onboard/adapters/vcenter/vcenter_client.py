"""Read-only ESXi FC HBA discovery via vCenter (pyVmomi).

Enumerates each ESXi host's Fibre Channel HBAs — their port WWPNs and the host OS/build — so the
provisioning flow can build host definitions and zoning from the real environment instead of asking
the operator to type WWPNs. Strictly read-only: it connects, reads the inventory, and disconnects.
"""

from __future__ import annotations

import ssl

try:
    from pyVim.connect import Disconnect, SmartConnect
    from pyVmomi import vim
except Exception:  # noqa: BLE001 - bundled in the .exe; optional otherwise
    SmartConnect = None
    Disconnect = None
    vim = None

from alletra_onboard.domain.storage import HostHba, normalize_wwpn


class VCenterError(Exception):
    """Couldn't reach, authenticate to, or read inventory from vCenter."""


def _wwpn_hex(port_wwn: int) -> str:
    """A pyVmomi HBA portWorldWideName is a 64-bit int; render it as a 16-hex WWPN."""
    return normalize_wwpn(f"{int(port_wwn) & 0xFFFFFFFFFFFFFFFF:016x}")


class VCenterClient:
    def __init__(self, host: str, username: str, password: str, port: int = 443, timeout: float = 30.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self._si = None

    def connect(self) -> None:
        if SmartConnect is None:
            raise VCenterError("pyVmomi is not available in this build.")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # vCenter self-signed cert in the lab
        try:
            self._si = SmartConnect(
                host=self.host, user=self.username, pwd=self.password,
                port=self.port, sslContext=ctx, connectionPoolTimeout=int(self.timeout),
            )
        except Exception as exc:  # noqa: BLE001 - auth / socket / TLS
            raise VCenterError(
                f"Could not connect to vCenter {self.host}: {type(exc).__name__}: {str(exc)[:200]}"
            ) from exc

    def close(self) -> None:
        if self._si is not None:
            try:
                Disconnect(self._si)
            except Exception:  # noqa: BLE001
                pass
            self._si = None

    def __enter__(self) -> "VCenterClient":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def host_fc_hbas(self) -> list[HostHba]:
        """One HostHba per ESXi FC HBA port (WWPN + host name + ESXi version)."""
        if self._si is None:
            raise VCenterError("not connected")
        content = self._si.RetrieveContent()
        view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        hbas: list[HostHba] = []
        try:
            for esxi in view.view:
                os_version = self._os_string(esxi)
                adapters = getattr(getattr(esxi.config, "storageDevice", None), "hostBusAdapter", []) or []
                for hba in adapters:
                    if isinstance(hba, vim.host.FibreChannelHba):
                        hbas.append(
                            HostHba(
                                host_name=esxi.name,
                                wwpn=_wwpn_hex(hba.portWorldWideName),
                                model=getattr(hba, "model", None),
                                os=os_version,
                            )
                        )
        finally:
            try:
                view.Destroy()
            except Exception:  # noqa: BLE001
                pass
        return hbas

    @staticmethod
    def _os_string(esxi) -> str | None:
        product = getattr(getattr(esxi.config, "product", None), "fullName", None)
        if product:
            return product
        summary = getattr(getattr(esxi, "summary", None), "config", None)
        return getattr(getattr(summary, "product", None), "fullName", None)
