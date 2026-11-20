"""Read-only ESXi FC HBA discovery via vCenter (pyVmomi).

Enumerates each ESXi host's Fibre Channel HBAs — their port WWPNs and the host OS/build — so the
provisioning flow can build host definitions and zoning from the real environment instead of asking
the operator to type WWPNs. Strictly read-only: it connects, reads the inventory, and disconnects.

pyVmomi has no single call every read goes through, so the command log gets one record per login and
per inventory read, named by the properties it reads.
"""

from __future__ import annotations

import ssl
import time
from collections.abc import Callable

try:
    from pyVim.connect import Disconnect, SmartConnect
    from pyVmomi import vim
except Exception:  # bundled in the .exe; optional otherwise
    SmartConnect = None
    Disconnect = None
    vim = None

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.domain.discovery import HostHba, HostIdentity
from alletra_onboard.domain.provisioning import EsxiLun
from alletra_onboard.domain.shared import normalize_wwpn


class VCenterError(Exception):
    """Couldn't reach, authenticate to, or read inventory from vCenter."""


LOGIN = "login {user, password: ********}"
READ_FC_HBAS = "read HostSystem config.storageDevice.hostBusAdapter (FC ports)"
READ_IDENTITIES = "read HostSystem hardware.systemInfo, config.storageDevice.hostBusAdapter (serial, iSCSI names)"
READ_LUNS = "read HostSystem config.storageDevice.scsiLun, multipathInfo (LUNs and paths)"


def _fault_text(exc: Exception) -> str:
    # D-11 (S-3, 2026-09-17): str() of a vim fault is its whole property dump; `.msg` is the sentence.
    return str(getattr(exc, "msg", "") or exc).strip()[:200]


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


def _serial_number(esxi) -> str:
    """`hardware.systemInfo.serialNumber` (vSphere 6.7+), else the SerialNumberTag / ServiceTag entry
    of `otherIdentifyingInfo` that older builds carry instead. Duck-typed for tests."""
    info = getattr(getattr(esxi, "hardware", None), "systemInfo", None)
    serial = str(getattr(info, "serialNumber", "") or "").strip()
    if serial:
        return serial
    other = getattr(getattr(getattr(esxi, "summary", None), "hardware", None), "otherIdentifyingInfo", None) or []
    for tag in ("SerialNumberTag", "ServiceTag"):
        for entry in other:
            key = getattr(getattr(entry, "identifierType", None), "key", "")
            value = str(getattr(entry, "identifierValue", "") or "").strip()
            if key == tag and value:
                return value
    return ""


def identity_from_host(esxi, *, is_iscsi=lambda hba: hasattr(hba, "iScsiName")) -> HostIdentity:
    """One ESXi HostSystem -> its serial number and iSCSI initiator names."""
    adapters = getattr(getattr(getattr(esxi, "config", None), "storageDevice", None), "hostBusAdapter", None) or []
    iqns: list[str] = []
    for hba in adapters:
        if is_iscsi(hba):
            name = str(getattr(hba, "iScsiName", "") or "").strip()
            if name.lower().startswith("iqn.") and name not in iqns:
                iqns.append(name)
    return HostIdentity(host_name=esxi.name, serial_number=_serial_number(esxi), iqns=iqns)


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
        # ADR 0026: with the customer's device CA bundle, the full check (chain and name), no fallback.
        # Without one, vCenter's certificate is usually its own: read it and compare it with the run's pin
        # (recorded on first contact) before the account, often the vSphere administrator, is sent.
        bundle = None
        try:
            bundle = device_trust.device_ca_bundle()
            if bundle:
                ctx = ssl.create_default_context(cafile=bundle)
            else:
                trusted = device_trust.check_tls(self.host, self.port, device="vCenter", timeout=self.timeout)
                # pyVmomi 9.1's serverPemCert is consulted only after a verifying handshake fails, and
                # SmartConnect's version lookup connects with the context alone, so a self-signed vCenter
                # cannot be pinned through it. This context compares the pin on every connection instead.
                ctx = device_trust.pinned_context(self.host, self.port, device="vCenter", trusted=trusted)
        except device_trust.DeviceTrustError as exc:
            raise VCenterError(str(exc)) from exc
        except Exception as exc:
            raise VCenterError(f"Could not connect to vCenter {self.host}: {type(exc).__name__}: "
                               f"{str(exc).strip()[:200]}") from exc
        started = time.monotonic()
        try:
            self._si = SmartConnect(
                host=self.host, user=self.username, pwd=self.password,
                port=self.port, sslContext=ctx, connectionPoolTimeout=int(self.timeout),
            )
        except device_trust.DeviceTrustError as exc:
            raise VCenterError(str(exc)) from exc
        except ssl.SSLCertVerificationError as exc:
            if not bundle:
                raise VCenterError(f"Could not connect to vCenter {self.host}: {exc}") from exc
            raise VCenterError(device_trust.ca_bundle_refusal(
                "vCenter", self.host, bundle, getattr(exc, "verify_message", "") or str(exc))) from exc
        except Exception as exc:
            detail = _fault_text(exc)
            self._record(LOGIN, started, ok=False, result=f"{type(exc).__name__}: {detail}")
            if type(exc).__name__ == "InvalidLogin":
                raise VCenterError(
                    f"Login failed for {self.username}@{self.host} — check the vCenter username/password "
                    f"on the sheet ({detail})."
                ) from exc
            raise VCenterError(f"Could not connect to vCenter {self.host}: {type(exc).__name__}: {detail}") from exc
        self._record(LOGIN, started, ok=True, result="ok", output="(session withheld)")

    def _record(self, command: str, started: float, *, ok: bool, result: str, output: object = "") -> None:
        command_log.record(target=self.host, transport="vcenter", command=command, started=started, ok=ok,
                           result=result, output=output, secrets=[self.password])

    def _recorded_read(self, command: str, read: Callable[[], list]) -> list:
        if self._si is None:
            raise VCenterError("not connected")
        started = time.monotonic()
        try:
            found = read()
        except Exception as exc:
            self._record(command, started, ok=False, result=f"{type(exc).__name__}: {_fault_text(exc)}")
            raise
        self._record(command, started, ok=True, result=f"ok, {len(found)} found",
                     output=[item.model_dump(mode="json") for item in found])
        return found

    def close(self) -> None:
        if self._si is not None:
            try:
                Disconnect(self._si)
            except Exception:
                pass
            self._si = None

    def __enter__(self) -> VCenterClient:
        self.connect()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def host_fc_hbas(self) -> list[HostHba]:
        """One HostHba per ESXi FC HBA port (WWPN + host name + ESXi version)."""
        return self._recorded_read(READ_FC_HBAS, self._read_fc_hbas)

    def _read_fc_hbas(self) -> list[HostHba]:
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
            except Exception:
                pass
        return hbas

    def host_identities(self) -> list[HostIdentity]:
        """SPEC-014 R2: serial number + iSCSI IQNs per ESXi host. Read-only."""
        return self._recorded_read(READ_IDENTITIES, self._read_identities)

    def _read_identities(self) -> list[HostIdentity]:
        content = self._si.RetrieveContent()
        view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        out: list[HostIdentity] = []
        try:
            for esxi in view.view:
                ident = identity_from_host(esxi, is_iscsi=lambda hba: isinstance(hba, vim.host.InternetScsiHba))
                ident.os = self._os_string(esxi)
                out.append(ident)
        finally:
            try:
                view.Destroy()
            except Exception:
                pass
        return out

    def host_luns(self) -> list[EsxiLun]:
        """SPEC-013 R1: every SCSI device each ESXi host sees, with its multipath state — what
        `esxcli storage core path list` would show, read through vCenter's cached storageDevice.
        Read-only; no rescan is triggered (R4)."""
        return self._recorded_read(READ_LUNS, self._read_luns)

    def _read_luns(self) -> list[EsxiLun]:
        content = self._si.RetrieveContent()
        view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        out: list[EsxiLun] = []
        try:
            for esxi in view.view:
                out.extend(parse_storage_device(esxi.name, getattr(esxi.config, "storageDevice", None)))
        finally:
            try:
                view.Destroy()
            except Exception:
                pass
        return out

    @staticmethod
    def _os_string(esxi) -> str | None:
        product = getattr(getattr(esxi.config, "product", None), "fullName", None)
        if product:
            return product
        summary = getattr(getattr(esxi, "summary", None), "config", None)
        return getattr(getattr(summary, "product", None), "fullName", None)
