"""WSAPI write/read client for the Alletra MP B10000 — wraps the official python-3parclient.

Drives provisioning over WSAPI v1 (https://<array>:443/api/v1), the verified-correct endpoint for
the B10000 (see ADR 0003 + the deep-research findings in the runbook). Design points baked in here:

- **python-3parclient >= 4.2.14** (pinned in pyproject) — earlier versions POST to /credentials
  instead of /api/v1/credentials and fail to authenticate to the B10000.
- **Readiness gate**: login() is the gate. A degraded/initialising array returns 503 (code 68,
  "system services required for operation are not ready"); we surface that as a clear, retry-later
  error instead of half-provisioning.
- **Idempotency**: every create is lookup-before-create (findHost) or catches the array's
  HTTPConflict so a re-run reports "exists" rather than failing — EXISTENT_HOST / EXISTENT_SV
  (volume; NOT EXISTENT_VV) / EXISTENT_VLUN, and EXISTENT_PATH (a WWN already on another host) which
  is a real conflict we do NOT swallow.
- **Proxy bypass**: the array is on the internal mgmt network; routing its 443 through the jump-box
  proxy is what caused TLS handshake timeouts (see probe_wsapi.py). We add the host to NO_PROXY so
  python-3parclient's `requests` calls go direct.
- **Self-signed TLS**: secure=False.

The client is synchronous; callers drive it via asyncio.to_thread (the SDK pulls in eventlet but we
never monkey-patch, so it stays dormant).
"""

from __future__ import annotations

import os

try:
    from hpe3parclient import exceptions as hpe_exc
    from hpe3parclient.client import HPE3ParClient
except Exception:  # noqa: BLE001 - import may pull eventlet; keep import errors non-fatal at module load
    HPE3ParClient = None
    hpe_exc = None

from alletra_onboard.domain.shared import normalize_wwpn
from alletra_onboard.domain.discovery import ArrayPort

# WSAPI host-persona ids, resolved by NAME. The values are hpe3parclient's HOST_PERSONA_* constants —
# the array's WSAPI persona enum: VMware=8, WindowsServer=11, Generic-ALUA=2. Verified 2026-07-22 against
# the SDK constants AND a live Alletra MP (GET /hosts reported persona 8 for its VMware ESXi hosts). This
# is the WSAPI enum, NOT the CLI `showhost -listpersona` numbering where VMware=11 — passing the CLI number
# to createHost would create ESXi hosts with the *Windows* persona (11 == WindowsServer here). Resolving by
# name means the two numberings can never be confused again.
_WSAPI_PERSONA: dict[str, int] = (
    {
        "VMware": HPE3ParClient.HOST_PERSONA_VMWARE,
        "WindowsServer": HPE3ParClient.HOST_PERSONA_WINDOWS_SERVER,
        "Generic-ALUA": HPE3ParClient.HOST_PERSONA_GENERIC_ALUA,
    }
    if HPE3ParClient is not None
    else {"VMware": 8, "WindowsServer": 11, "Generic-ALUA": 2}  # SDK absent in this build: verified values
)


# WSAPI port enums -> the CLI (`showport`) vocabulary that ArrayPort documents. Only the values we
# have actually observed are mapped; anything else falls through as its own string rather than being
# guessed at or dropped. Observed live on 4UW0004497 (OS 10.5.60.36): every FC port reported
# linkState=4 while the CLI calls those ports ready, and the host-serving ports reported mode=2
# against mode=3 on the two ports the array does not present to hosts.
_PORT_LINK_STATE: dict[object, str] = {4: "ready", 5: "loss_sync", 10: "offline"}
_PORT_MODE: dict[object, str] = {1: "suspended", 2: "target", 3: "initiator", 4: "peer"}


class WsapiError(Exception):
    """Couldn't reach, authenticate to, or drive WSAPI on the array."""


class WsapiNotReady(WsapiError):
    """The array's WSAPI is reachable but not serving (503 'services not ready') — retry later."""


def _bypass_proxy_for(host: str) -> None:
    """Ensure requests (the SDK transport) talks to the array directly, not via HTTP(S)_PROXY."""
    for var in ("NO_PROXY", "no_proxy"):
        current = os.environ.get(var, "")
        hosts = {h.strip() for h in current.split(",") if h.strip()}
        if host not in hosts:
            hosts.add(host)
            os.environ[var] = ",".join(sorted(hosts))


class WsapiClient:
    def __init__(self, host: str, username: str, password: str, port: int = 443, timeout: float = 30.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.api_url = f"https://{host}:{port}/api/v1"
        self.timeout = timeout
        self._client = None

    # ------------------------------------------------------------------ lifecycle

    def connect(self) -> None:
        if HPE3ParClient is None:
            raise WsapiError("python-3parclient is not available in this build.")
        _bypass_proxy_for(self.host)
        try:
            client = HPE3ParClient(self.api_url, secure=False, timeout=self.timeout, suppress_ssl_warnings=True)
            client.login(self.username, self.password)  # the readiness gate
        except Exception as exc:  # noqa: BLE001
            raise self._translate(exc, where="login") from exc
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.logout()
            except Exception:  # noqa: BLE001
                pass
            self._client = None

    def __enter__(self) -> "WsapiClient":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------ reads

    def system_name(self) -> str:
        info = self._require().getStorageSystemInfo()
        return info.get("name", "") if isinstance(info, dict) else ""

    def cpg_names(self) -> list[str]:
        body = self._require().getCPGs()
        return [m.get("name", "") for m in _members(body)]

    def cpg_free_mib(self) -> dict[str, int]:
        """CPG name -> free capacity in MiB, for the readiness preflight. `freeSpaceMiB` is what the
        array reports; a CPG missing the field reads as 0 rather than dropping out of the map."""
        return {
            m.get("name", ""): int(m.get("freeSpaceMiB") or 0)
            for m in _members(self._require().getCPGs())
            if m.get("name")
        }

    def array_fc_ports(self) -> list[ArrayPort]:
        """Every FC port with its WWPN, link state and role, fabric assigned by card-port parity.

        The WSAPI reports linkState and mode as integers while the CLI (`showport`) reports words,
        and ArrayPort is shared by both paths — so map the enums back to the CLI's vocabulary here
        rather than leaking "4" into a field documented as "ready". Unknown values pass through as
        their own string instead of being silently dropped.
        """
        ports: list[ArrayPort] = []
        for member in _members(self._require().getPorts()):
            if member.get("protocol") not in (1, None):  # 1 = FC
                continue
            wwn = member.get("portWWN")
            pos = member.get("portPos") or {}
            if not wwn or not pos:
                continue
            card_port = int(pos.get("cardPort", 0))
            ports.append(
                ArrayPort(
                    node=int(pos.get("node", 0)),
                    slot=int(pos.get("slot", 0)),
                    card_port=card_port,
                    wwpn=normalize_wwpn(str(wwn)),
                    link_state=_PORT_LINK_STATE.get(member.get("linkState"), str(member.get("linkState", ""))),
                    mode=_PORT_MODE.get(member.get("mode"), str(member.get("mode", ""))),
                    fabric="odd" if card_port % 2 == 1 else "even",
                )
            )
        return ports

    def host_names(self) -> list[str]:
        return [m.get("name", "") for m in _members(self._require().getHosts())]

    def host_set_names(self) -> list[str]:
        try:
            return [m.get("name", "") for m in _members(self._require().getHostSets())]
        except Exception:  # noqa: BLE001 - older firmware may differ; non-fatal for a plan preview
            return []

    def volume_names(self) -> list[str]:
        return [m.get("name", "") for m in _members(self._require().getVolumes())]

    def volume_set_names(self) -> list[str]:
        try:
            return [m.get("name", "") for m in _members(self._require().getVolumeSets())]
        except Exception:  # noqa: BLE001
            return []

    def find_host_by_wwn(self, wwn: str) -> str | None:
        """Return the name of the host owning this FC WWN, or None (lookup-before-create primitive)."""
        try:
            host = self._require().findHost(wwn=wwn)
        except Exception:  # noqa: BLE001 - findHost raises if not found in some versions
            return None
        if isinstance(host, str):
            return host or None
        if isinstance(host, dict):
            return host.get("name")
        return host or None

    # ------------------------------------------------------------------ writes (idempotent)

    def ensure_host(self, name: str, fc_wwns: list[str], persona: str = "VMware") -> str:
        """Create ONE host carrying all FC WWNs at the given persona NAME (default 'VMware'), resolved to
        the WSAPI persona id via `_WSAPI_PERSONA`. Returns 'created' or 'exists'. An existing host is never
        modified — its persona is left as-is.

        Raises WsapiError if any WWN already belongs to a *different* host (EXISTENT_PATH) — that is a
        real conflict the operator must resolve, not something to silently adopt.
        """
        persona_id = _WSAPI_PERSONA.get(persona)
        if persona_id is None:
            raise WsapiError(f"unknown host persona '{persona}' (expected one of {sorted(_WSAPI_PERSONA)})")
        owners = {self.find_host_by_wwn(w) for w in fc_wwns}
        owners.discard(None)
        if owners == {name}:
            return "exists"
        other = owners - {name}
        if other:
            raise WsapiError(
                f"WWN(s) for host '{name}' already belong to another host definition: {sorted(other)}. "
                "Resolve this on the array before provisioning."
            )
        try:
            self._require().createHost(name, FCWwns=fc_wwns, optional={"persona": persona_id})
            return "created"
        except Exception as exc:  # noqa: BLE001
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"createHost {name}") from exc

    def ensure_host_set(self, name: str, members: list[str]) -> str:
        try:
            self._require().createHostSet(name, setmembers=members)
            return "created"
        except Exception as exc:  # noqa: BLE001
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"createHostSet {name}") from exc

    def ensure_volume(self, name: str, cpg: str, size_mib: int, provisioning_type: str) -> str:
        # Data reduction is ONE flag on the Alletra MP WSAPI: `reduce`. The legacy 3PAR pair
        # {"tdvv": True, "compression": True} is rejected outright -- proven live on a B10000
        # (WSAPI 1.15.60 / OS 10.5.60.36): `tdvv` returns code 78 "one of the parameters is
        # required: tpvv,reduce", and `compression` returns code 42 "unrecognized name" in ANY
        # body. `{"reduce": True}` alone is accepted and reads back provisioningType=6 with
        # deduplication on -- so do not "restore" the compression flag; the array has no such field.
        optional = {"reduce": True} if provisioning_type == "reduce" else {"tpvv": True}
        try:
            self._require().createVolume(name, cpg, size_mib, optional=optional)
            return "created"
        except Exception as exc:  # noqa: BLE001 - EXISTENT_SV on a re-run
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"createVolume {name}") from exc

    def ensure_volume_set(self, name: str, members: list[str]) -> str:
        try:
            self._require().createVolumeSet(name, setmembers=members)
            return "created"
        except Exception as exc:  # noqa: BLE001
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"createVolumeSet {name}") from exc

    def ensure_vlun(self, volume_name: str, host_name: str, lun: int | None = None) -> str:
        """Export a source to a target as a VLUN. ``volume_name`` is a bare volume or ``set:<vvset>``;
        ``host_name`` is a bare host or ``set:<hostset>``. ``lun=None`` lets the array auto-assign;
        an explicit ``lun`` presents at that number. Returns 'created' or 'exists' (idempotent)."""
        try:
            if lun is None:
                self._require().createVLUN(volume_name, hostname=host_name, auto=True)
            else:
                self._require().createVLUN(volume_name, lun=lun, hostname=host_name, auto=False)
            return "created"
        except Exception as exc:  # noqa: BLE001 - EXISTENT_VLUN on a re-run
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"createVLUN {volume_name}->{host_name}") from exc

    # ------------------------------------------------------------------ internals

    def _require(self):
        if self._client is None:
            raise WsapiError("not connected")
        return self._client

    @staticmethod
    def _is_conflict(exc: Exception) -> bool:
        return hpe_exc is not None and isinstance(exc, hpe_exc.HTTPConflict)

    def _translate(self, exc: Exception, *, where: str) -> WsapiError:
        # Readiness: a 503 (services not ready) on login is the documented degraded-array condition.
        status = getattr(exc, "http_status", None) or getattr(exc, "code", None)
        if status == 503 or "not ready" in str(exc).lower():
            return WsapiNotReady(
                f"The array's WSAPI is reachable but not ready (during {where}). This tracks array "
                "health, not config — check `checkhealth -svc -detail` and retry once it clears."
            )
        desc = ""
        if hpe_exc is not None and isinstance(exc, hpe_exc.ClientException):
            try:
                desc = exc.get_description() or ""
            except Exception:  # noqa: BLE001
                desc = ""
        return WsapiError(f"WSAPI {where} failed: {desc or type(exc).__name__}: {str(exc)[:200]}")


def _members(body) -> list[dict]:
    """python-3parclient get* returns {'total':N,'members':[...]} (or sometimes a bare list)."""
    if isinstance(body, dict):
        return body.get("members", []) or []
    if isinstance(body, list):
        return body
    return []
