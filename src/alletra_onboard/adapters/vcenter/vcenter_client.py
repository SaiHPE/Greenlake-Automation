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

from alletra_onboard.domain.shared import normalize_wwpn
from alletra_onboard.domain.discovery import HostHba
from alletra_onboard.domain.provisioning import EsxiLun


class VCenterError(Exception):
    """Couldn't reach, authenticate to, or read inventory from vCenter."""


def _wwpn_hex(port_wwn: int) -> str:
    """A pyVmomi HBA portWorldWideName is a 64-bit int; render it as a 16-hex WWPN."""
    return normalize_wwpn(f"{int(port_wwn) & 0xFFFFFFFFFFFFFFFF:016x}")


def parse_storage_device(host_name: str, storage_device) -> list[EsxiLun]:
    """HostStorageDeviceInfo -> [EsxiLun]. Duck-typed over pyVmomi objects (or any fake with the same
    attributes) so the join can be tested without pyVmomi: `scsiLun[]` (key, canonicalName,
    operationalState), `multipathInfo.lun[]` (lun = scsiLun key, path[] with pathState + adapter key),
    `hostBusAdapter[]` (key -> device, e.g. vmhba1)."""
    if storage_device is None:
        return []
    adapters = {getattr(a, "key", ""): getattr(a, "device", "") for a in (getattr(storage_device, "hostBusAdapter", None) or [])}
    luns: dict[str, EsxiLun] = {}
    for lun in getattr(storage_device, "scsiLun", None) or []:
        name = str(getattr(lun, "canonicalName", "") or "").lower()
        if not name.startswith("naa."):
            continue
        states = list(getattr(lun, "operationalState", None) or [])
        luns[str(getattr(lun, "key", ""))] = EsxiLun(
            host_name=host_name, naa=name, operational_state=str(states[0]) if states else "",
        )
    mp = getattr(storage_device, "multipathInfo", None)
    for entry in (getattr(mp, "lun", None) or []) if mp is not None else []:
        rec = luns.get(str(getattr(entry, "lun", "")))
        if rec is None:
            continue
        for path in getattr(entry, "path", None) or []:
            rec.paths_total += 1
            state = str(getattr(path, "pathState", "") or "").lower()
            if state == "active":
                rec.paths_active += 1
            elif state == "dead":
                rec.paths_dead += 1
            key = str(getattr(path, "adapter", "") or "")
            vmhba = adapters.get(key) or (key.rsplit("-", 1)[-1] if key else "")
            if vmhba and vmhba not in rec.adapters:
                rec.adapters.append(vmhba)
    return list(luns.values())


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
            # D-11 (S-3, 2026-09-17): str() of a vim fault is its whole property dump; `.msg` is the sentence.
            detail = str(getattr(exc, "msg", "") or exc).strip()[:200]
            if type(exc).__name__ == "InvalidLogin":
                raise VCenterError(
                    f"Login failed for {self.username}@{self.host} — check the vCenter username/password "
                    f"on the sheet ({detail})."
                ) from exc
            raise VCenterError(f"Could not connect to vCenter {self.host}: {type(exc).__name__}: {detail}") from exc

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
        # One physical port can surface as SEVERAL adapter objects — a CNA reports the same
        # portWorldWideName through more than one vmhba. Measured live on the VZ ESXi 8.0.3 hosts:
        # 12 adapters for 6 real ports, every WWPN listed twice. The WWPN is the identity that
        # matters for zoning and host creation, so keep the first sighting of each (host, wwpn);
        # otherwise every count and every per-HBA note the operator sees is silently doubled.
        seen: set[tuple[str, str]] = set()
        try:
            for esxi in view.view:
                os_version = self._os_string(esxi)
                adapters = getattr(getattr(esxi.config, "storageDevice", None), "hostBusAdapter", []) or []
                for hba in adapters:
                    if isinstance(hba, vim.host.FibreChannelHba):
                        wwpn = _wwpn_hex(hba.portWorldWideName)
                        if (esxi.name, wwpn) in seen:
                            continue
                        seen.add((esxi.name, wwpn))
                        hbas.append(
                            HostHba(
                                host_name=esxi.name,
                                wwpn=wwpn,
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

    def host_luns(self) -> list[EsxiLun]:
        """SPEC-013 R1: every SCSI device each ESXi host sees, with its multipath state — what
        `esxcli storage core path list` would show, read through vCenter's cached storageDevice.
        Read-only; no rescan is triggered (R4)."""
        if self._si is None:
            raise VCenterError("not connected")
        content = self._si.RetrieveContent()
        view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        out: list[EsxiLun] = []
        try:
            for esxi in view.view:
                out.extend(parse_storage_device(esxi.name, getattr(esxi.config, "storageDevice", None)))
        finally:
            try:
                view.Destroy()
            except Exception:  # noqa: BLE001
                pass
        return out

    @staticmethod
    def _os_string(esxi) -> str | None:
        product = getattr(getattr(esxi.config, "product", None), "fullName", None)
        if product:
            return product
        summary = getattr(getattr(esxi, "summary", None), "config", None)
        return getattr(getattr(summary, "product", None), "fullName", None)
