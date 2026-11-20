"""WSAPI write/read client for the Alletra MP B10000 — wraps the official python-3parclient.

Drives provisioning over WSAPI v1 (https://<array>:443/api/v1), the verified-correct endpoint for
the B10000 (see ADR 0003 + the deep-research findings in the runbook). Design points baked in here:

- **python-3parclient >= 4.2.14** (pinned in pyproject) — earlier versions POST to /credentials
  instead of /api/v1/credentials and fail to authenticate to the B10000.
- **Readiness gate**: login() is the gate. A degraded/initialising array returns 503 (code 68,
  "system services required for operation are not ready"); we surface that as a clear, retry-later
  error instead of half-provisioning.
- **Idempotency**: every create is lookup-before-create (getHosts-derived WWN ownership) or catches the array's
  HTTPConflict so a re-run reports "exists" rather than failing — EXISTENT_HOST / EXISTENT_SV
  (volume; NOT EXISTENT_VV) / EXISTENT_VLUN, and EXISTENT_PATH (a WWN already on another host) which
  is a real conflict we do NOT swallow.
- **Proxy bypass**: the array is on the internal mgmt network; routing its 443 through the jump-box
  proxy is what caused TLS handshake timeouts (see probe_wsapi.py). We add the host to NO_PROXY so
  python-3parclient's `requests` calls go direct.
- **Self-signed TLS, pinned** (ADR 0026): the SDK's own chain check stays off, because a certificate
  the array made for itself cannot pass one. Before login the certificate is read and compared with the
  run's pin (recorded on first contact), and every connection the SDK opens after that checks the same
  SHA-256 (`_pin_calls`), so a device that answers in the array's place never gets the password or the
  session key.

The client is synchronous; callers drive it via asyncio.to_thread (the SDK pulls in eventlet but we
never monkey-patch, so it stays dormant).
"""

from __future__ import annotations

import time
from contextvars import ContextVar

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.domain.errors import WsapiError, WsapiNotReady

try:
    from hpe3parclient import exceptions as hpe_exc
    from hpe3parclient import http as sdk_http
    from hpe3parclient.client import HPE3ParClient

    SDK_IMPORT_ERROR: str | None = None
except Exception as _exc:  # import may pull eventlet; keep import errors non-fatal at module load
    HPE3ParClient = None
    hpe_exc = None
    sdk_http = None
    # Keep the REASON. A frozen build that fails this import degrades silently until WSAPI is first
    # touched (v0.14.0-rc.1 shipped that way), and "not available" without the cause forces a
    # diagnose-by-rebuild loop. Served via /app/profile capabilities and appended to the error.
    SDK_IMPORT_ERROR = f"{type(_exc).__name__}: {_exc}"

from alletra_onboard.domain.discovery import ArrayPort
from alletra_onboard.domain.network import IscsiVlanInterface
from alletra_onboard.domain.peer_ports import PeerPortState, PortParams
from alletra_onboard.domain.provisioning import ArrayHostRecord, VlunTemplate
from alletra_onboard.domain.replication import (
    DR_ACTION_FAILOVER,
    DR_ACTION_RECOVER,
    DR_ACTION_RESTORE,
)
from alletra_onboard.domain.shared import ArrayVolumeRecord, normalize_wwpn

# A request that got no answer, known by its type. socket.timeout is TimeoutError.
_TIMEOUT_TYPES: tuple[type[BaseException], ...] = (TimeoutError,)
_DR_ACTION = {DR_ACTION_FAILOVER: "failover", DR_ACTION_RECOVER: "recover", DR_ACTION_RESTORE: "restore"}
if hpe_exc is not None:
    _TIMEOUT_TYPES += (hpe_exc.Timeout,)
try:
    import requests
    from requests.adapters import HTTPAdapter

    _TIMEOUT_TYPES += (requests.exceptions.Timeout,)
except ImportError:
    requests = None
    HTTPAdapter = object

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


# WSAPI port enums -> the CLI (`showport`) vocabulary that ArrayPort documents. Only values we have
# actually observed are mapped; anything else falls through as its own string rather than being
# guessed at or dropped.
#
# PROVEN by running both interfaces against the same array (4UW0004497, OS 10.5.60.36) and matching
# them port for port: the six ports `showport` calls `target` are exactly the six the WSAPI reports
# as mode=2, the two it calls `initiator` are exactly mode=3, and every port it calls `ready` is
# linkState=4. The IP/peer ports (`peer`, protocol IP) come back as protocol=4/mode=4 and are
# filtered out before this mapping applies.
#
# The rest was matched the same way on rack13-ARCUS (CZ2D2K014S, OS 10.6.0, 2026-11-16): `GET /ports`
# against `showport` and `showport -par`, all 28 ports (tests/fixtures/peer_ports/rack13/). linkState 12
# is the cluster ports' `link_idle_for_reset`; type -1 is `cluster`; connectionType 99 is the iSCSI
# ports' `eth`.
#
# The FC peer port, matched the same way on E18U31 (DHCI_B10K, OS 10.5.60, 2026-11-17,
# tests/fixtures/peer_ports/E18U31/): 0:3:2 and 1:3:2, `initiator` and Type `peer` in `showport`,
# `peer point` in `showport -par`, are mode 3, type 6, connectionMode 4. Type 7 is the `rcip` IP ports
# of D22U27 (OS 10.5.0) and VZ (OS 10.5.51). python-3parclient also names type 5 rcfc and 8 iscsi;
# no capture has shown either, so they stay unmapped.
_PORT_LINK_STATE: dict[object, str] = {4: "ready", 5: "loss_sync", 10: "offline", 12: "link_idle_for_reset"}
_PORT_MODE: dict[object, str] = {1: "suspended", 2: "target", 3: "initiator", 4: "peer"}
_PORT_TYPE: dict[object, str] = {1: "host", 2: "disk", 3: "free", 6: "peer", 7: "rcip", -1: "cluster"}
_PORT_PROTOCOL: dict[object, str] = {1: "FC", 2: "iSCSI", 4: "IP", 6: "NVMe"}
_PORT_CONN_MODE: dict[object, str] = {1: "disk", 2: "host", 4: "peer"}
_PORT_CONN_TYPE: dict[object, str] = {2: "point", 99: "eth"}

# WSAPI persona id -> name (the inverse of _WSAPI_PERSONA) for reading hosts back.
_PERSONA_NAME: dict[int, str] = {v: k for k, v in _WSAPI_PERSONA.items()}

# WSAPI volume `provisioningType` enum. 6 (TDVV) is what a `{"reduce": True}` create reads back as on
# the Alletra MP (observed live, see ensure_volume) — so 6 IS "reduce" in this tool's vocabulary.
_PROVISIONING_TYPE: dict[object, str] = {1: "full", 2: "tpvv", 3: "snp", 4: "peer", 5: "unknown", 6: "reduce", 7: "dds"}

# WSAPI VLUN `type` enum value for a host-set export (kept for readers of the records; the parser
# below does not need it — see parse_vlun_templates).
_VLUN_TYPE_HOST_SET = 5


def parse_hosts(body: object) -> list[ArrayHostRecord]:
    """getHosts -> records. Persona by name (unknown ids pass through as their number); FC WWNs
    de-duplicated — `FCPaths` carries one entry per (WWN, array port), so a dual-fabric HBA appears
    twice (rack13arcus capture, 2026-09-13). iSCSI names come from `iSCSIPaths[].name`, de-duplicated
    case-insensitively (rack13arcus 2026-09-13, D22U27 2026-10-26)."""
    out: list[ArrayHostRecord] = []
    for m in _members(body):
        name = m.get("name", "")
        if not name:
            continue
        persona_id = m.get("persona")
        wwns: list[str] = []
        for p in m.get("FCPaths") or []:
            w = normalize_wwpn(str(p.get("wwn", "")))
            if len(w) == 16 and w not in wwns:
                wwns.append(w)
        out.append(ArrayHostRecord(
            name=name,
            persona=_PERSONA_NAME.get(persona_id, str(persona_id) if persona_id is not None else ""),
            wwns=wwns,
            iqns=_iscsi_names(m),
            id=int(m["id"]) if str(m.get("id", "")).isdigit() else None,
        ))
    return out


def _word(table: dict[object, str], value: object) -> str:
    return table.get(value, "" if value is None else str(value))


def parse_port_states(body: object) -> tuple[dict[str, PeerPortState], dict[str, PortParams]]:
    """getPorts -> ({n:s:p: state}, {n:s:p: params}) in the words `showport` and `showport -par`
    print, so a WSAPI read and a CLI read of one array compare equal (rack13-ARCUS, 2026-11-16). An
    unknown enum value passes through as its number. WWNs are kept for FC ports only: for an NVMe
    port the WSAPI puts its IP address in `nodeWWN`. A port without `connectionMode` (the IP ports)
    has no params, as `showport -par` lists none for it. On OS 10.5 (E18U31, D22U27, 2026-11-17)
    `GET /ports` leaves out the IP ports of Type `free` and `file`, so it is not a full port list there;
    OS 10.6.0 (rack13) lists every port."""
    states: dict[str, PeerPortState] = {}
    params: dict[str, PortParams] = {}
    for m in _members(body):
        pos = m.get("portPos") or {}
        if not pos:
            continue
        nsp = f"{pos.get('node')}:{pos.get('slot')}:{pos.get('cardPort')}"
        protocol = _word(_PORT_PROTOCOL, m.get("protocol"))
        fc = protocol == "FC"
        states[nsp] = PeerPortState(
            nsp=nsp,
            mode=_word(_PORT_MODE, m.get("mode")),
            state=_word(_PORT_LINK_STATE, m.get("linkState")),
            type=_word(_PORT_TYPE, m.get("type")),
            protocol=protocol,
            node_wwn=normalize_wwpn(str(m.get("nodeWWN") or "")) if fc else "",
            port_wwn=normalize_wwpn(str(m.get("portWWN") or "")) if fc else "",
            label=str(m.get("label") or ""),
        )
        if m.get("connectionMode") is not None:
            params[nsp] = PortParams(nsp=nsp, connmode=_word(_PORT_CONN_MODE, m.get("connectionMode")),
                                     conntype=_word(_PORT_CONN_TYPE, m.get("connectionType")))
    return states, params


def _iscsi_names(host: dict) -> list[str]:
    out: list[str] = []
    for p in host.get("iSCSIPaths") or []:
        iqn = str(p.get("name", "")).strip()
        if iqn and iqn.lower() not in {i.lower() for i in out}:
            out.append(iqn)
    return out


def parse_volumes(body: object) -> list[ArrayVolumeRecord]:
    out: list[ArrayVolumeRecord] = []
    for m in _members(body):
        name = m.get("name", "")
        if not name:
            continue
        out.append(ArrayVolumeRecord(
            name=name,
            size_mib=int(m.get("sizeMiB") or 0),
            cpg=str(m.get("userCPG") or ""),
            provisioning_type=_PROVISIONING_TYPE.get(m.get("provisioningType"), "unknown"),
            id=int(m["id"]) if str(m.get("id", "")).isdigit() else None,
            wwn=str(m.get("wwn") or "").upper(),
            copy_of=str(m.get("copyOf") or ""),
            read_only=bool(m.get("readOnly")),
            created=str(m.get("creationTime8601") or ""),
            expires=str(m.get("expirationTime8601") or ""),
        ))
    return out


def parse_sets(body: object) -> dict[str, list[str]]:
    """getHostSets / getVolumeSets -> {name: members}. A set with no `setmembers` is present and empty."""
    return {m["name"]: list(m.get("setmembers") or []) for m in _members(body) if m.get("name")}


def parse_vlun_templates(body: object) -> list[VlunTemplate]:
    """getVLUNs -> the presentation templates: (volume, target, lun), target exactly as the array
    names it (`set:<hostset>` for a host-set export, a bare host name otherwise).

    PINNED to the rack13arcus capture (tests/fixtures/rack13_wsapi/vluns.json, 2026-09-13): the
    array returns two kinds of record. Templates have `active: false` and carry the target as
    written (`hostname: "set:zz_t2_hs"`, `type: 5`). Active paths have `active: true` and carry the
    MEMBER host (`hostname: "10.132.30.136"`, still `type: 5`) plus `remoteName` / `portPos`. So a
    template is an inactive record taken as-is — never "type 5 ⇒ prefix set:", which the first
    draft did from the documentation and which would have invented `set:10.132.30.136` from every
    active path. Records with no `active` field (unknown firmware) are kept, de-duplicated."""
    seen: dict[tuple[str, str, int], VlunTemplate] = {}
    for m in _members(body):
        if m.get("active") is True:
            continue
        volume, target, lun = m.get("volumeName"), m.get("hostname"), m.get("lun")
        if not volume or not target or lun is None:
            continue
        key = (str(volume), str(target), int(lun))
        if key not in seen:
            seen[key] = VlunTemplate(volume=key[0], target=key[1], lun=key[2])
    return list(seen.values())


def parse_iscsi_vlans_wsapi(nsp: str, body: object) -> list[IscsiVlanInterface]:
    """`GET /ports/<n:s:p>/iSCSIVlans/` -> the port's VLAN-tagged addresses.

    PINNED to tests/fixtures/iscsi_vlan/: the answer is `{"iSCSIVlans": [...], "total": N, "links":
    [...]}`, not the `members` envelope of the other collections, so `_members` would read every
    answer as empty. Whether the untagged address is in the list depends on the OS: rack13-ARCUS
    (OS 10.6.0, 2026-11-16) left it out, E18U31 (OS 10.5.60, 2026-11-17) lists it as a record with
    `vlanTag` 0. Tag 0 is the port's base address, not a VLAN interface, so it is left out here as
    `parse_iscsi_vlans` leaves out the CLI's `untagged` row.

    The field names are those of E18U31's real untagged records (`IPAddr`, `netmask`, `gateway`,
    `vlanTag`, `mtu`, `stgt`, `tpgt`, `iSNSAddr`, `iSNSPort`); no tagged record is captured yet. A
    record without `vlanTag`, `IPAddr` or `netmask`, or with a tag outside 0 to 4094, is refused
    rather than read as blanks (LESSONS 28)."""
    if not isinstance(body, dict) or "iSCSIVlans" not in body:
        raise ValueError(f"WSAPI iSCSIVlans answer for {nsp} has no iSCSIVlans list: {str(body)[:200]}")
    out: list[IscsiVlanInterface] = []
    for rec in body["iSCSIVlans"] or []:
        missing = [k for k in ("vlanTag", "IPAddr", "netmask") if not isinstance(rec, dict) or k not in rec]
        if missing:
            raise ValueError(f"WSAPI iSCSIVlans record for {nsp} has no {', '.join(missing)}: {str(rec)[:200]}")
        tag = str(rec["vlanTag"])
        if not (tag.isdigit() and int(tag) <= 4094):
            raise ValueError(f"WSAPI iSCSIVlans record for {nsp} has vlanTag {tag}, "
                             "neither a tag from 1 to 4094 nor 0 (untagged)")
        if int(tag) == 0:
            continue
        gateway = str(rec.get("gateway") or "")
        out.append(IscsiVlanInterface(
            nsp=nsp, vlan_id=int(tag), ip=str(rec["IPAddr"]), netmask=str(rec["netmask"]),
            gateway="" if gateway == "0.0.0.0" else gateway, mtu=str(rec.get("mtu") or ""),
        ))
    return out


# ADR 0026. The SDK opens a new connection for every call (it calls the module-level `requests.request`),
# so a probe before login covers only that moment. A pinned client binds its certificate's SHA-256 for
# each call it makes, and the stand-in for `requests` inside the SDK sends that call through a session
# whose connections check it (urllib3's assert_fingerprint, which urllib3 checks with verification off).
_PINNED_FINGERPRINT: ContextVar[str | None] = ContextVar("alletra_wsapi_fingerprint", default=None)


class _FingerprintAdapter(HTTPAdapter):
    def __init__(self, fingerprint: str) -> None:
        self._fingerprint = fingerprint      # read by init_poolmanager, which HTTPAdapter.__init__ calls
        super().__init__()

    def init_poolmanager(self, *args, **kwargs) -> None:
        kwargs["assert_fingerprint"] = self._fingerprint
        super().init_poolmanager(*args, **kwargs)


class _PinnedRequests:
    """Stands in for the `requests` module inside `hpe3parclient.http`; everything else passes through."""

    def __init__(self, real) -> None:
        self._real = real

    def __getattr__(self, name: str):
        return getattr(self._real, name)

    def request(self, method, url, **kwargs):
        fingerprint = _PINNED_FINGERPRINT.get()
        if fingerprint is None:
            return self._real.request(method, url, **kwargs)
        with self._real.Session() as session:
            session.mount("https://", _FingerprintAdapter(fingerprint))
            return session.request(method=method, url=url, **kwargs)


def _install_pinned_transport() -> None:
    if sdk_http is not None and not isinstance(sdk_http.requests, _PinnedRequests):
        sdk_http.requests = _PinnedRequests(sdk_http.requests)


if HPE3ParClient is not None and requests is not None:
    _install_pinned_transport()


def _pin_calls(client, fingerprint: str) -> None:
    """Every HTTP call the SDK makes for `client` goes through `client.http.request`: bind the pin there."""
    http = client.http
    inner = http.request

    def pinned(*args, **kwargs):
        token = _PINNED_FINGERPRINT.set(fingerprint)
        try:
            return inner(*args, **kwargs)
        finally:
            _PINNED_FINGERPRINT.reset(token)

    http.request = pinned


def _record_calls(client, host: str, api_url: str, password: str) -> None:
    """SPEC-019 R1: every HTTP call the SDK makes goes through `http._time_request(url, method, **kw)`."""
    http = getattr(client, "http", None)
    inner = getattr(http, "_time_request", None)
    if inner is None:
        return

    def timed(url, method, **kwargs):
        if not command_log.active():
            return inner(url, method, **kwargs)
        path = url.removeprefix(api_url)
        login = path.startswith("/credentials")
        if login and path != "/credentials":
            path = "/credentials/********"   # logout carries the session key in the URL
        # Opening or closing a session changes nothing on the array: not a write.
        write = method != "GET" and not login
        body = kwargs.get("body")
        shown = "{user, password: ********}" if login else command_log.as_text(body).replace("\n", " ")
        command = f"{method} {path}" + ("" if body is None else f" {shown}")
        started = time.monotonic()
        try:
            resp, out = inner(url, method, **kwargs)
        except Exception as exc:
            status = getattr(exc, "http_status", None) or getattr(exc, "code", None) or type(exc).__name__
            command_log.record(target=host, transport="wsapi", command=command, started=started, ok=False,
                               result=f"HTTP {status}: {WsapiClient._safe_str(exc)}", secrets=[password],
                               write=write)
            raise
        status = getattr(resp, "status_code", None) or getattr(resp, "status", None) or ""
        command_log.record(target=host, transport="wsapi", command=command, started=started, ok=True,
                           result=f"HTTP {status}".strip(), output="(session key withheld)" if login else out,
                           secrets=[password], write=write)
        return resp, out

    http._time_request = timed


class WsapiClient:
    def __init__(self, host: str, username: str, password: str, port: int = 443, timeout: float = 30.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.api_url = f"https://{host}:{port}/api/v1"
        self.timeout = timeout
        self._client = None
        self._ca_bundle: str | None = None

    # ------------------------------------------------------------------ lifecycle

    def connect(self) -> None:
        if HPE3ParClient is None:
            raise WsapiError(
                f"python-3parclient is not available in this build ({SDK_IMPORT_ERROR})."
            )
        device_trust.bypass_proxy_for(self.host)
        # ADR 0026: with the customer's device CA bundle the SDK makes the full check (requests takes a path
        # as `verify`), with no fallback. Without one, read the certificate and compare it with the run's
        # pin before the password goes anywhere.
        trusted = None
        try:
            self._ca_bundle = device_trust.device_ca_bundle()
            if self._ca_bundle is None:
                trusted = device_trust.check_tls(self.host, self.port, device="array", timeout=self.timeout)
        except device_trust.DeviceTrustError as exc:
            raise WsapiError(str(exc)) from exc
        except Exception as exc:
            raise self._translate(exc, where="log in to the array") from exc
        try:
            if trusted is None:
                client = HPE3ParClient(self.api_url, secure=self._ca_bundle, timeout=self.timeout)
            else:
                # TRUST-OFF: a certificate the array made for itself cannot pass a chain check, so the SDK's
                # is off; every connection this client opens checks the pinned SHA-256 instead (_pin_calls).
                client = HPE3ParClient(self.api_url, secure=False, timeout=self.timeout, suppress_ssl_warnings=True)
                _pin_calls(client, trusted.fingerprint)
            _record_calls(client, self.host, self.api_url, self.password)
            client.login(self.username, self.password)  # the readiness gate
        except Exception as exc:
            raise self._translate(exc, where="log in to the array") from exc
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.logout()
            except Exception:
                pass
            self._client = None

    def __enter__(self) -> WsapiClient:
        self.connect()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------ reads

    def system_name(self) -> str:
        info = self._require().getStorageSystemInfo()
        return info.get("name", "") if isinstance(info, dict) else ""

    def system_info(self) -> dict:
        """GET /system as the array returns it: name, timeZone, `parameters` (VVRetentionTimeMax, …)."""
        info = self._require().getStorageSystemInfo()
        return info if isinstance(info, dict) else {}

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
        except Exception:  # older firmware may differ; non-fatal for a plan preview
            return []

    def volume_names(self) -> list[str]:
        return [m.get("name", "") for m in _members(self._require().getVolumes())]

    def volume_set_names(self) -> list[str]:
        try:
            return [m.get("name", "") for m in _members(self._require().getVolumeSets())]
        except Exception:
            return []

    # Record reads for the plan (SPEC-001 §4): one GET each, parsed by the module-level parsers.

    def hosts(self) -> list[ArrayHostRecord]:
        return parse_hosts(self._require().getHosts())

    def host_sets(self) -> dict[str, list[str]]:
        return parse_sets(self._require().getHostSets())

    def volumes(self) -> list[ArrayVolumeRecord]:
        return parse_volumes(self._require().getVolumes())

    def volume_sets(self) -> dict[str, list[str]]:
        return parse_sets(self._require().getVolumeSets())

    def vlun_templates(self) -> list[VlunTemplate]:
        return parse_vlun_templates(self._require().getVLUNs())

    def wwn_owners(self) -> dict[str, str]:
        """{normalized FC WWN: owning host name} for EVERY host on the array, from one getHosts()
        read. This exists because the SDK's findHost() is a TRAP: it does not query — it runs
        `createhost` over the SDK's OWN SSH channel (which this client never configures), so on
        this client it always raised, the broad except returned None, and every WWN looked
        unowned. PROVEN LIVE 2026-08-15: ensure_host re-added an already-present WWN, the array
        answered EXISTENT_PATH, and the conflict-swallow reported 'exists' while the new WWN was
        silently dropped. Ownership is now computed from the array's own host list — no SSH, no
        probe-host creation, one round trip."""
        owners: dict[str, str] = {}
        for member in _members(self._require().getHosts()):
            name = member.get("name", "")
            for path in member.get("FCPaths") or []:
                wwn = normalize_wwpn(str(path.get("wwn", "")))
                if len(wwn) == 16 and name:
                    owners[wwn] = name
        return owners

    def iqn_owners(self) -> dict[str, str]:
        """{lower-case iSCSI name: owning host name} for every host on the array, from one getHosts()
        read — for the same reason as wwn_owners (never the SDK's findHost)."""
        return {
            iqn.lower(): member.get("name", "")
            for member in _members(self._require().getHosts()) if member.get("name")
            for iqn in _iscsi_names(member)
        }

    def find_host_by_wwn(self, wwn: str) -> str | None:
        """Return the name of the host owning this FC WWN, or None. Backed by wwn_owners(), never
        by the SDK's findHost (see wwn_owners for why)."""
        return self.wwn_owners().get(normalize_wwpn(wwn))

    # ------------------------------------------------------------------ idempotent writes

    def ensure_host(self, name: str, fc_wwns: list[str], persona: str = "VMware") -> str:
        """Create ONE host carrying all FC WWNs at the given persona NAME (default 'VMware'), resolved to
        the WSAPI persona id via `_WSAPI_PERSONA`. Returns 'created', 'updated' (the host existed but was
        missing some of these WWNs — they were added), or 'exists' (already carries every WWN). The
        persona of an existing host is never modified.

        Raises WsapiError if any WWN already belongs to a *different* host (EXISTENT_PATH) — that is a
        real conflict the operator must resolve, not something to silently adopt.
        """
        # ONE getHosts read answers both questions: who owns each WWN, and does the host exist.
        owners_map = self.wwn_owners()
        host_exists = name in set(self.host_names())
        by_norm = {w: normalize_wwpn(w) for w in fc_wwns}
        other = {owners_map[n] for n in by_norm.values() if n in owners_map and owners_map[n] != name}
        if other:
            raise WsapiError(
                f"WWN(s) for host '{name}' already belong to another host definition: {sorted(other)}. "
                "Resolve this on the array before provisioning."
            )
        missing = [w for w, n in by_norm.items() if owners_map.get(n) != name]
        if host_exists and not missing:
            return "exists"
        if not host_exists:
            # Checked here only: an existing host keeps whatever persona the array gave it (e.g. Generic).
            persona_id = _WSAPI_PERSONA.get(persona)
            if persona_id is None:
                raise WsapiError(f"unknown host persona '{persona}' (expected one of {sorted(_WSAPI_PERSONA)})")
            try:
                self._require().createHost(name, FCWwns=fc_wwns, optional={"persona": persona_id})
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create host {name}") from exc
                # EXISTENT_HOST race: someone created the name since our read — fall through and add.
        # The host object exists but lacks some of these WWNs. Reporting "exists" here would be the
        # silent single-path trap: the object looks green while the unregistered HBAs' paths never
        # light up. Reconcile by ADDing exactly the missing WWNs — never re-adding present ones
        # (the array answers EXISTENT_PATH even for a WWN already on the SAME host — proven live),
        # and never removing or adopting anyone else's.
        try:
            self._require().modifyHost(
                name,
                {"pathOperation": getattr(HPE3ParClient, "HOST_EDIT_ADD", 1), "FCWWNs": missing},
            )
            return "updated"
        except Exception as exc:
            # No conflict-swallow here: `missing` excludes WWNs already on this host, so a 409 now
            # means a real race or another owner — masking it as 'exists' is how the live bug hid.
            raise self._translate(exc, where=f"add {len(missing)} WWN(s) to host {name}") from exc

    def ensure_iscsi_host(self, name: str, iqns: list[str], persona: str = "VMware") -> str:
        """The iSCSI twin of ensure_host: ONE host carrying these iSCSI names (`createhost -iscsi`).
        Returns 'created', 'updated' (the IQNs it lacked were added) or 'exists'. The array takes an
        IQN it has never seen a session from, so this does not wait for a login.

        Raises WsapiError when an IQN belongs to a different host, or when the host of that name
        carries FC WWNs: WSAPI refuses FC and iSCSI names in one request, and this tool does not put
        both on one host (not proven on the array)."""
        if not iqns:
            raise WsapiError(f"no iSCSI name given for host '{name}'")
        members = {m.get("name", ""): m for m in _members(self._require().getHosts()) if m.get("name")}
        owners = {i.lower(): n for n, m in members.items() for i in _iscsi_names(m)}
        other = sorted({owners[i.lower()] for i in iqns if owners.get(i.lower(), name) != name})
        if other:
            raise WsapiError(
                f"iSCSI name(s) for host '{name}' already belong to another host definition: {other}. "
                "Resolve this on the array before provisioning."
            )
        existing = members.get(name)
        if existing is not None and any(p.get("wwn") for p in existing.get("FCPaths") or []):
            raise WsapiError(
                f"host '{name}' exists with FC WWNs; this tool does not add iSCSI names to an FC host. "
                "Use another host name, or add the IQN on the array."
            )
        missing = [i for i in iqns if owners.get(i.lower()) != name]
        if existing is not None and not missing:
            return "exists"
        if existing is None:
            persona_id = _WSAPI_PERSONA.get(persona)
            if persona_id is None:
                raise WsapiError(f"unknown host persona '{persona}' (expected one of {sorted(_WSAPI_PERSONA)})")
            try:
                self._require().createHost(name, iscsiNames=list(iqns), optional={"persona": persona_id})
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create iSCSI host {name}") from exc
                # EXISTENT_HOST race, as in ensure_host: add the names to the host someone just made.
        try:
            self._require().modifyHost(
                name,
                {"pathOperation": getattr(HPE3ParClient, "HOST_EDIT_ADD", 1), "iSCSINames": missing},
            )
            return "updated"
        except Exception as exc:
            raise self._translate(exc, where=f"add {len(missing)} iSCSI name(s) to host {name}") from exc

    def _existing_set_members(self, getter, name: str) -> list[str] | None:
        """The set's current members, or None if the set does not exist. Sets share ensure_host's
        reconciliation problem: exists-with-missing-members must gain them, never report 'exists'."""
        try:
            data = getter(name)
        except Exception:  # not-found raises in the SDK
            return None
        if isinstance(data, dict):
            return list(data.get("setmembers") or [])
        return list(getattr(data, "setmembers", None) or [])

    def ensure_host_set(self, name: str, members: list[str]) -> str:
        """Create the host set, or ADD any missing members to an existing one (additive only — a
        member someone else added is never removed). 'exists' means every requested member verified."""
        existing = self._existing_set_members(self._require().getHostSet, name)
        if existing is None:
            try:
                self._require().createHostSet(name, setmembers=list(members))
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create host set {name}") from exc
                existing = self._existing_set_members(self._require().getHostSet, name) or []
        missing = [m for m in members if m not in existing]
        if not missing:
            return "exists"
        try:
            self._require().modifyHostSet(
                name, action=getattr(HPE3ParClient, "SET_MEM_ADD", 1), setmembers=missing,
            )
            return "updated"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add {len(missing)} host(s) to host set {name}") from exc

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
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            # Live on rack13-ARCUS, 2026-11-16: a 1 PiB volume was refused with HTTP 400 code 28,
            # "client request contains value that is too large". The size is the one number in the body.
            if self._array_code(exc) == "28":
                size = f"{size_mib // 1024} GiB" if size_mib % 1024 == 0 else f"{size_mib} MiB"
                raise WsapiError(
                    f"the array says {size} is more than it can create in one volume. Make it smaller on the "
                    f"sheet's Volumes tab, then build the plan again. Array said: "
                    f"{self._array_reason(exc) or self._safe_str(exc)}"
                ) from exc
            raise self._translate(exc, where=f"create volume {name}") from exc

    def ensure_volume_set(self, name: str, members: list[str]) -> str:
        """Create the VV set, or ADD any missing members to an existing one (additive only)."""
        existing = self._existing_set_members(self._require().getVolumeSet, name)
        if existing is None:
            try:
                self._require().createVolumeSet(name, setmembers=list(members))
                return "created"
            except Exception as exc:
                if not self._is_conflict(exc):
                    raise self._translate(exc, where=f"create volume set {name}") from exc
                existing = self._existing_set_members(self._require().getVolumeSet, name) or []
        missing = [m for m in members if m not in existing]
        if not missing:
            return "exists"
        try:
            self._require().modifyVolumeSet(
                name, action=getattr(HPE3ParClient, "SET_MEM_ADD", 1), setmembers=missing,
            )
            return "updated"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add {len(missing)} volume(s) to volume set {name}") from exc

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
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"export {volume_name} to {host_name}") from exc

    # ------------------------------------------------------------------ snapshots (SPEC-023 R5)
    # hpe3parclient 4.5 `createSnapshot` and `createSnapshotOfVolumeSet` (read 2026-11-17, LESSONS 29):
    # plain WSAPI, no SSH. POST /volumes/<vol> and /volumesets/<set> with {action: createSnapshot,
    # parameters: {name, readOnly, expirationHours}}; a set's `name` may be a VV name pattern. Never
    # `retentionHours`: no lock in the first slice (ADR 0016 decision 2). A duplicate name is the array's
    # refusal, never "exists": the plan judged that from its read (LESSONS 29, 37). `@vvname@.initial`
    # over WSAPI is confirmed on the lab before the live run (work packet, live check 2).

    def create_snapshot(self, volume: str, name: str, *, read_only: bool, expire_hours: int) -> None:
        try:
            self._require().createSnapshot(name, volume, optional={"readOnly": read_only, "expirationHours": expire_hours})
        except Exception as exc:
            raise self._translate(exc, where=f"create snapshot {name} of volume {volume}") from exc

    def create_set_snapshot(self, vvset: str, pattern: str, *, read_only: bool, expire_hours: int) -> None:
        try:
            self._require().createSnapshotOfVolumeSet(
                pattern, vvset, optional={"readOnly": read_only, "expirationHours": expire_hours})
        except Exception as exc:
            raise self._translate(exc, where=f"create snapshots {pattern} of volume set {vvset}") from exc

    # ------------------------------------------------------------------ Remote Copy groups (SPEC-016 R4)
    # The `/remotecopygroups` resource, confirmed on WSAPI 1.15 (B10000, OS 10.5.0, both lab
    # arrays): group records carry `role` 1/2, `targets[].mode` 1 sync / 2 periodic,
    # `targets[].policies.{autoRecover,autoSynchronize,…}`, `targets[].syncPeriod`,
    # `remoteGroupName`, `volumes[].remoteVolumes[].syncStatus` (tests/fixtures/rc_pair/README.md).

    def remote_copy_groups(self) -> list[dict]:
        try:
            return _members(self._require().getRemoteCopyGroups())
        except Exception as exc:
            raise self._translate(exc, where="read the Remote Copy groups") from exc

    def remote_copy_group(self, name: str) -> dict | None:
        try:
            body = self._require().getRemoteCopyGroup(name)
            return body if isinstance(body, dict) else None
        except Exception as exc:
            if hpe_exc is not None and isinstance(exc, hpe_exc.HTTPNotFound):
                return None
            raise self._translate(exc, where=f"read Remote Copy group {name}") from exc

    def create_remote_copy_group(self, name: str, *, target: str, mode: str, peer_cpg: str, local_cpg: str = "") -> str:
        """`creatercopygroup -usr_cpg <local> <target>:<peer_cpg> <name> <target>:<sync|periodic>`."""
        targets = [{"targetName": target, "mode": 1 if mode == "sync" else 2, "userCPG": peer_cpg}]
        optional = {"localUserCPG": local_cpg} if local_cpg else None
        try:
            self._require().createRemoteCopyGroup(name, targets, optional=optional)
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"create Remote Copy group {name}") from exc

    def set_remote_copy_group(
        self, name: str, *, target: str, period_seconds: int | None, auto_recover: bool, auto_synchronize: bool,
    ) -> str:
        """`setrcopygroup period …` then `setrcopygroup pol …` — as TWO PUTs. Proven live on
        AlletraMP_D22U27 (WSAPI 1.15, 2026-10-09): one body carrying both draws HTTP 400 code 44
        "parameters cannot be present at the same time - policies, syncPeriod". Returns a note when
        the array refused `autoSynchronize` as a WSAPI field (then only `autoRecover` was set)."""
        if period_seconds:
            try:
                self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "syncPeriod": period_seconds}]})
            except Exception as exc:
                raise self._translate(exc, where=f"set the sync period of Remote Copy group {name}") from exc
        policies = {"autoRecover": auto_recover, "autoSynchronize": auto_synchronize}
        try:
            self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "policies": policies}]})
            return ""
        except Exception as exc:
            detail = self._safe_str(exc).lower()
            if "autosynchronize" not in detail and "unrecognized" not in detail:
                raise self._translate(exc, where=f"set the policies of Remote Copy group {name}") from exc
        try:
            self._require().modifyRemoteCopyGroup(name, optional={"targets": [{"targetName": target, "policies": {"autoRecover": auto_recover}}]})
        except Exception as exc:
            raise self._translate(exc, where=f"set the policies of Remote Copy group {name}") from exc
        return (f"The array did not accept 'autoSynchronize' for {name}; auto_recover and the "
                f"period were set. Set it on the array: setrcopygroup pol {'auto_synchronize' if auto_synchronize else 'no_auto_synchronize'} {name}")

    def admit_remote_copy_volume(self, group: str, volume: str, *, target: str, secondary: str | None = None) -> str:
        """`admitrcopyvv -createvv <volume> <group> <target>:<secondary>` — the secondary is auto-created."""
        targets = [{"targetName": target, "secVolumeName": secondary or volume}]
        try:
            self._require().addVolumeToRemoteCopyGroup(group, volume, targets, optional={"volumeAutoCreation": True})
            return "created"
        except Exception as exc:
            if self._is_conflict(exc):
                return "exists"
            raise self._translate(exc, where=f"add volume {volume} to Remote Copy group {group}") from exc

    def start_remote_copy_group(self, name: str) -> str:
        try:
            self._require().startRemoteCopy(name)
            return "started"
        except Exception as exc:
            if self._is_conflict(exc) or "already" in self._safe_str(exc).lower():
                return "exists"
            raise self._translate(exc, where=f"start Remote Copy group {name}") from exc

    def stop_remote_copy_group(self, name: str) -> str:
        try:
            self._require().stopRemoteCopy(name)
            return "stopped"
        except Exception as exc:
            if self._is_conflict(exc) or "already" in self._safe_str(exc).lower():
                return "exists"
            raise self._translate(exc, where=f"stop Remote Copy group {name}") from exc

    def remote_copy_dr_action(self, name: str, action: int) -> None:
        """`setrcopygroup failover|recover|restore -f <name>` as the WSAPI disaster-recovery action
        (7 / 9 / 10) on `/remotecopygroups/<name>`. Issued on the array that holds the group under
        that name; the array mirrors the role change to its partner. SPEC-017."""
        try:
            self._require().recoverRemoteCopyGroupFromDisaster(name, action)
        except Exception as exc:
            raise self._translate(exc, where=f"run {_DR_ACTION.get(action, f'action {action}')} on Remote Copy group {name}") from exc

    # ------------------------------------------------------------------ internals

    def _require(self):
        if self._client is None:
            raise WsapiError("not connected")
        return self._client

    @staticmethod
    def _is_conflict(exc: Exception) -> bool:
        return hpe_exc is not None and isinstance(exc, hpe_exc.HTTPConflict)

    @staticmethod
    def _array_code(exc: Exception) -> str:
        """The array's error code as text ("28"), or '' when the error did not come from the array."""
        if hpe_exc is None or not isinstance(exc, hpe_exc.ClientException):
            return ""
        try:
            code = exc.get_code()
        except Exception:  # describing a failure must never fail
            return ""
        return "" if code in (None, "") else str(code)

    @staticmethod
    def _safe_str(exc: BaseException) -> str:
        """``str(exc)`` without trusting the exception to be describable.

        MEASURED against a wedged WSAPI: ``str()`` on hpe3parclient's own ``Timeout`` RAISES —
        its ``__str__`` reads a ``.message`` attribute that no longer exists on modern Python — so
        this translator crashed with ``AttributeError`` and the operator saw that instead of "the
        array did not respond". Describing a failure must never fail.
        """
        try:
            text = str(exc)
        except Exception:  # the exception's own __str__ is broken
            text = ""
        if not text:
            # Its args may still carry the detail. Only use them when there ARE any: repr(()) is
            # the string "''", which is truthy and would mask the type-name fallback below.
            try:
                args = tuple(getattr(exc, "args", ()) or ())
                text = "; ".join(str(a) for a in args) if args else ""
            except Exception:
                text = ""
        return text or f"{type(exc).__name__} (no detail available)"

    def _translate(self, exc: Exception, *, where: str) -> WsapiError:
        """The error the operator reads. `where` is what the tool was doing, in plain words ("create
        volume x"): the API's call names and the word WSAPI stay off the screen (SPEC-030 R10)."""
        if hpe_exc is not None and isinstance(exc, hpe_exc.SSLCertFailed):
            if self._ca_bundle:
                return WsapiError(device_trust.ca_bundle_refusal("array", self.host, self._ca_bundle))
            return self._certificate_changed(where)
        detail = self._safe_str(exc)
        reason = self._array_reason(exc)
        # str() of a bare ClientException fails, so its description reaches these checks only
        # through the array's reason.
        lowered = f"{detail} {reason}".lower()
        # Readiness: a 503 (services not ready) on login is the documented degraded-array condition.
        status = getattr(exc, "http_status", None) or getattr(exc, "code", None)
        if status == 503 or "not ready" in lowered:
            return WsapiNotReady(
                f"The array answered but is not ready to take requests yet (while trying to {where}). This "
                "is the array's own state, not the sheet: check `checkhealth -svc -detail` on the array and "
                "try again once it is clear."
            )
        # A wedged WSAPI: the TLS connection is ACCEPTED and then nothing answers, so this looks
        # like a network fault while `showwsapi` still reports Enabled/Active. Seen live on the LZ
        # array. Name the remedy, because "timed out" sends people to check firewalls for an hour.
        if self._is_timeout(exc, lowered):
            return WsapiNotReady(
                f"The array accepted the connection but did not respond while trying to {where}. Its "
                "management service is listening yet not serving — `showwsapi` will still say "
                "Enabled/Active. Restart it on the array over SSH (`stopwsapi` then `startwsapi`), "
                "then try again."
            )
        # The GreenLake gate, hit live on a fresh B10000: every create is refused with "Array has
        # not yet completed the subscription process" until onboarding (Component A/B/C) finishes.
        # Without this translation it reads like a WSAPI defect instead of a sequencing problem.
        if "subscri" in lowered:
            return WsapiError(
                f"Could not {where}: the array has not finished its GreenLake subscription. "
                "Finish the onboarding steps (GreenLake registration → cloud connection) and try again. "
                f"The array said: {reason or detail[:200]}"
            )
        if reason:
            return WsapiError(f"Could not {where}. The array said: {reason}")
        return WsapiError(f"Could not {where}: {type(exc).__name__}: {detail[:200]}")

    def _certificate_changed(self, where: str) -> WsapiError:
        """A connection after login met a certificate other than the pinned one; the request was not
        sent. Read it again so the run records what was presented, and say so with both fingerprints."""
        try:
            device_trust.check_tls(self.host, self.port, device="array", timeout=self.timeout)
        except device_trust.DeviceTrustError as exc:
            return WsapiError(str(exc))
        except Exception:  # the array went away as well; the sentence below still holds
            pass
        return WsapiError(
            f"The array at {self.host} presented a different certificate while the tool tried to {where}, so it "
            "stopped before sending the request. Run the step again; if it stops again, the run "
            "overview shows the fingerprints under Trusted devices."
        )

    @staticmethod
    def _is_timeout(exc: Exception, text: str) -> bool:
        """True when the request got no answer. Judged by the exception's type; its text counts
        only when no HTTP status came back, because an array that refuses a request with "invalid
        timeout value" did answer, and its reason must reach the operator."""
        if isinstance(exc, _TIMEOUT_TYPES) or "timeout" in type(exc).__name__.lower():
            return True
        answered = bool(getattr(exc, "http_status", None)) or (
            # from_response() raises the bare ClientException for a status it does not map, and
            # drops the status, but the array still answered.
            hpe_exc is not None and type(exc) is hpe_exc.ClientException
        )
        return not answered and ("timed out" in text or "timeout" in text)

    @staticmethod
    def _array_reason(exc: Exception) -> str:
        """The array's reason said once, then its status and code: ``<desc> (HTTP 400, code 28)``.

        ``str()`` of an hpe3parclient error already ends with the description ("Bad request
        (HTTP 400) 28 - <desc>"), so quoting the description and then ``str(exc)`` said the reason
        twice. Empty when the error carries no description from the array. A long description (an
        HTML error page comes through whole) is cut to its first 300 characters.
        """
        if hpe_exc is None or not isinstance(exc, hpe_exc.ClientException):
            return ""
        try:
            desc = str(exc.get_description() or "")
            if not desc:
                return ""
            if len(desc) > 300:
                desc = desc[:300].rstrip() + "…"
            facts = []
            if getattr(exc, "http_status", None):
                facts.append(f"HTTP {exc.http_status}")
            if exc.get_code() not in (None, ""):
                facts.append(f"code {exc.get_code()}")
            # Rarely sent, but str(exc) carried them, so they stay.
            for label, value in (("ref", exc.get_ref()), ("debug1", getattr(exc, "_debug1", None)),
                                 ("debug2", getattr(exc, "_debug2", None))):
                if value:
                    facts.append(f"{label} {value}")
        except Exception:  # describing a failure must never fail
            return ""
        return f"{desc} ({', '.join(facts)[:200]})" if facts else desc


def _members(body) -> list[dict]:
    """python-3parclient get* returns {'total':N,'members':[...]} (or sometimes a bare list)."""
    if isinstance(body, dict):
        return body.get("members", []) or []
    if isinstance(body, list):
        return body
    return []
