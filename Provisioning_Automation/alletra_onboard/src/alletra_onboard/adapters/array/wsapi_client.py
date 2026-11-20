"""Read-only WSAPI v1 client for the Alletra MP B10000 — wraps the official python-3parclient.

Drives reads over WSAPI v1 (https://<array>:443/api/v1), the verified-correct endpoint for
the B10000 (see ADR 0003 + the deep-research findings in the runbook). Mutating calls live in
`wsapi_writer.py` (`WsapiWriter`), which extends `WsapiReader` and is imported only by
`application/runs/writer_clients.py` (STANDARD S2). Design points baked in here:

- **python-3parclient >= 4.2.14** (pinned in pyproject) — earlier versions POST to /credentials
  instead of /api/v1/credentials and fail to authenticate to the B10000.
- **Readiness gate**: login() is the gate. A degraded/initialising array returns 503 (code 68,
  "system services required for operation are not ready"); we surface that as a clear, retry-later
  error instead of half-provisioning.
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
from typing import Any, cast

import structlog

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.adapters.array.wsapi_parse import (
    _PORT_LINK_STATE,
    _PORT_MODE,
    _members,
    _names,
    _word,
    parse_hosts,
    parse_sets,
    parse_vlun_templates,
    parse_volumes,
)
from alletra_onboard.domain.discovery import ArrayPort
from alletra_onboard.domain.errors import WsapiError, WsapiNotReady
from alletra_onboard.domain.provisioning import ArrayHostRecord, VlunTemplate
from alletra_onboard.domain.shared import ArrayVolumeRecord, normalize_wwpn

_log = structlog.get_logger(__name__)

try:
    from hpe3parclient import exceptions as hpe_exc
    from hpe3parclient import http as sdk_http
    from hpe3parclient.client import HPE3ParClient

    SDK_IMPORT_ERROR: str | None = None
except (ImportError, OSError, RuntimeError, AttributeError) as _exc:  # import may pull eventlet
    HPE3ParClient = None
    hpe_exc = None
    sdk_http = None
    # Keep the REASON. A frozen build that fails this import degrades silently until WSAPI is first
    # touched (v0.14.0-rc.1 shipped that way), and "not available" without the cause forces a
    # diagnose-by-rebuild loop. Served via /app/profile capabilities and appended to the error.
    SDK_IMPORT_ERROR = f"{type(_exc).__name__}: {_exc}"

# A request that got no answer, known by its type. socket.timeout is TimeoutError.
_ExcTypes = tuple[type[BaseException], ...]
_TIMEOUT_TYPES: _ExcTypes = (TimeoutError,)
_HTTP_NOT_FOUND: _ExcTypes = ()
_LOGOUT_ERRORS: _ExcTypes = (OSError, RuntimeError)
if hpe_exc is not None:
    _TIMEOUT_TYPES += (hpe_exc.Timeout,)
    _HTTP_NOT_FOUND = (hpe_exc.HTTPNotFound,)
    _LOGOUT_ERRORS += (hpe_exc.ClientException,)
try:
    import requests
    from requests.adapters import HTTPAdapter as _RequestsHTTPAdapter

    _TIMEOUT_TYPES += (requests.exceptions.Timeout,)
    _LOGOUT_ERRORS += (requests.RequestException,)
except ImportError:
    requests = None
    _RequestsHTTPAdapter = None

# ADR 0026. The SDK opens a new connection for every call (it calls the module-level `requests.request`),
# so a probe before login covers only that moment. A pinned client binds its certificate's SHA-256 for
# each call it makes, and the stand-in for `requests` inside the SDK sends that call through a session
# whose connections check it (urllib3's assert_fingerprint, which urllib3 checks with verification off).
_PINNED_FINGERPRINT: ContextVar[str | None] = ContextVar("alletra_wsapi_fingerprint", default=None)


if _RequestsHTTPAdapter is not None:

    class _FingerprintAdapter(_RequestsHTTPAdapter):
        def __init__(self, fingerprint: str) -> None:
            self._fingerprint = fingerprint      # read by init_poolmanager, which HTTPAdapter.__init__ calls
            super().__init__()

        def init_poolmanager(self, connections: int, maxsize: int, block: bool = False, **pool_kwargs: object) -> None:
            pool_kwargs["assert_fingerprint"] = self._fingerprint
            super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)


class _PinnedRequests:
    """Stands in for the `requests` module inside `hpe3parclient.http`; everything else passes through."""

    def __init__(self, real: Any) -> None:
        self._real = real

    def __getattr__(self, name: str) -> Any:
        return getattr(self._real, name)

    def request(self, method: str, url: str, **kwargs: object) -> Any:
        fingerprint = _PINNED_FINGERPRINT.get()
        if fingerprint is None:
            return self._real.request(method, url, **kwargs)
        if _RequestsHTTPAdapter is None:
            raise WsapiError(
                "Certificate pinning requires requests.adapters.HTTPAdapter; refusing to send an unpinned request."
            )
        with self._real.Session() as session:
            session.mount("https://", _FingerprintAdapter(fingerprint))
            return session.request(method=method, url=url, **kwargs)


def _install_pinned_transport() -> None:
    if sdk_http is not None and not isinstance(sdk_http.requests, _PinnedRequests):
        sdk_http.requests = _PinnedRequests(sdk_http.requests)


if HPE3ParClient is not None:
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


_DESCRIBE_ERRORS = (AttributeError, TypeError, ValueError, LookupError)


def _safe_str(exc: BaseException) -> str:
    """``str(exc)`` without trusting the exception to be describable.

    MEASURED against a wedged WSAPI: ``str()`` on hpe3parclient's own ``Timeout`` RAISES —
    its ``__str__`` reads a ``.message`` attribute that no longer exists on modern Python — so
    this translator crashed with ``AttributeError`` and the operator saw that instead of "the
    array did not respond". Describing a failure must never fail.
    """
    try:
        text = str(exc)
    except _DESCRIBE_ERRORS:  # broken __str__ on SDK Timeout
        text = ""
    if not text:
        # Its args may still carry the detail. Only use them when there ARE any: repr(()) is
        # the string "''", which is truthy and would mask the type-name fallback below.
        try:
            args = exc.args
            text = "; ".join(str(a) for a in args) if args else ""
        except _DESCRIBE_ERRORS:
            text = ""
    return text or f"{type(exc).__name__} (no detail available)"


def _record_calls(client, host: str, api_url: str, password: str) -> None:
    """SPEC-019 R1: every HTTP call the SDK makes goes through `http._time_request(url, method, **kw)`."""
    http = getattr(client, "http", None)
    inner = getattr(http, "_time_request", None)
    if http is None or inner is None:
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
        common: dict[str, Any] = {
            "target": host, "transport": "wsapi", "command": command,
            "started": started, "secrets": [password], "write": write,
        }
        try:
            resp, out = inner(url, method, **kwargs)
        except Exception as exc:
            status = getattr(exc, "http_status", None) or getattr(exc, "code", None) or type(exc).__name__
            command_log.record(**common, ok=False, result=f"HTTP {status}: {_safe_str(exc)}")
            raise
        status = getattr(resp, "status_code", None) or getattr(resp, "status", None) or ""
        command_log.record(**common, ok=True, result=f"HTTP {status}".strip(),
                           output="(session key withheld)" if login else out)
        return resp, out

    http._time_request = timed


_READ_WHAT: dict[str, str] = {
    "getStorageSystemInfo": "array system info",
    "getCPGs": "array CPGs",
    "getPorts": "array ports",
    "getHosts": "array hosts",
    "getHostSets": "array host sets",
    "getVolumes": "array volumes",
    "getVolumeSets": "array volume sets",
    "getVLUNs": "array VLUNs",
    "getRemoteCopyGroups": "Remote Copy groups",
}


class WsapiReader:
    def __init__(self, host: str, username: str, password: str, port: int = 443, timeout: float = 30.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.api_url = f"https://{host}:{port}/api/v1"
        self.timeout = timeout
        self._client: Any = None
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
            # requests accepts a CA bundle path as `verify` (the SDK forwards `secure` to `verify`).
            # TRUST-OFF: a certificate the array made for itself cannot pass a chain check, so the SDK's
            # is off; every connection this client opens checks the pinned SHA-256 instead (_pin_calls).
            kw: dict[str, Any] = (
                {"secure": cast(Any, self._ca_bundle)}
                if trusted is None
                else {"secure": False, "suppress_ssl_warnings": True}
            )
            client = HPE3ParClient(self.api_url, timeout=self.timeout, **kw)
            if trusted is not None:
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
            except _LOGOUT_ERRORS as exc:
                _log.debug("wsapi_logout_failed", host=self.host, error=_safe_str(exc))
            self._client = None

    def __enter__(self) -> WsapiReader:
        self.connect()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    # ------------------------------------------------------------------ reads

    def _read(self, method: str, *args: Any) -> Any:
        try:
            return getattr(self._require(), method)(*args)
        except WsapiError:
            raise
        except Exception as exc:
            raise self._translate(exc, where=f"read the {_READ_WHAT[method]}") from exc

    def system_name(self) -> str:
        return self.system_info().get("name", "")

    def system_info(self) -> dict:
        """GET /system as the array returns it: name, timeZone, `parameters` (VVRetentionTimeMax, …)."""
        info = self._read("getStorageSystemInfo")
        return info if isinstance(info, dict) else {}

    def cpg_names(self) -> list[str]:
        return _names(self._read("getCPGs"))

    def cpg_free_mib(self) -> dict[str, int]:
        """CPG name -> free capacity in MiB, for the readiness preflight. `freeSpaceMiB` is what the
        array reports; a CPG missing the field reads as 0 rather than dropping out of the map."""
        return {
            m.get("name", ""): int(m.get("freeSpaceMiB") or 0)
            for m in _members(self._read("getCPGs"))
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
        for member in _members(self._read("getPorts")):
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
                    link_state=_word(_PORT_LINK_STATE, member.get("linkState")),
                    mode=_word(_PORT_MODE, member.get("mode")),
                    fabric="odd" if card_port % 2 == 1 else "even",
                )
            )
        return ports

    def host_names(self) -> list[str]:
        return _names(self._read("getHosts"))

    def host_set_names(self) -> list[str]:
        return _names(self._read("getHostSets"))

    def volume_names(self) -> list[str]:
        return _names(self._read("getVolumes"))

    def volume_set_names(self) -> list[str]:
        return _names(self._read("getVolumeSets"))

    # Record reads for the plan (SPEC-001 §4): one GET each, parsed by the module-level parsers.

    def hosts(self) -> list[ArrayHostRecord]:
        return parse_hosts(self._read("getHosts"))

    def host_sets(self) -> dict[str, list[str]]:
        return parse_sets(self._read("getHostSets"))

    def volumes(self) -> list[ArrayVolumeRecord]:
        return parse_volumes(self._read("getVolumes"))

    def volume_sets(self) -> dict[str, list[str]]:
        return parse_sets(self._read("getVolumeSets"))

    def vlun_templates(self) -> list[VlunTemplate]:
        return parse_vlun_templates(self._read("getVLUNs"))

    def wwn_owners(self) -> dict[str, str]:
        """{normalized FC WWN: owning host name} for EVERY host on the array, from one getHosts()
        read. This exists because the SDK's findHost() is a TRAP: it does not query — it runs
        `createhost` over the SDK's OWN SSH channel (which this client never configures), so on
        this client it always raised, the broad except returned None, and every WWN looked
        unowned. PROVEN LIVE 2026-08-15: ensure_host re-added an already-present WWN, the array
        answered EXISTENT_PATH, and the conflict-swallow reported 'exists' while the new WWN was
        silently dropped. Ownership is now computed from the array's own host list — no SSH, no
        probe-host creation, one round trip."""
        return {wwn: h.name for h in self.hosts() for wwn in h.wwns}

    def iqn_owners(self) -> dict[str, str]:
        """{lower-case iSCSI name: owning host name} for every host on the array, from one getHosts()
        read — for the same reason as wwn_owners (never the SDK's findHost)."""
        return {iqn.lower(): h.name for h in self.hosts() for iqn in h.iqns}

    def find_host_by_wwn(self, wwn: str) -> str | None:
        """Return the name of the host owning this FC WWN, or None. Backed by wwn_owners(), never
        by the SDK's findHost (see wwn_owners for why)."""
        return self.wwn_owners().get(normalize_wwpn(wwn))

    # ------------------------------------------------------------------ Remote Copy group reads (SPEC-016)
    # The `/remotecopygroups` resource, confirmed on WSAPI 1.15 (B10000, OS 10.5.0, both lab
    # arrays): group records carry `role` 1/2, `targets[].mode` 1 sync / 2 periodic,
    # `targets[].policies.{autoRecover,autoSynchronize,…}`, `targets[].syncPeriod`,
    # `remoteGroupName`, `volumes[].remoteVolumes[].syncStatus` (tests/fixtures/rc_pair/README.md).

    def remote_copy_groups(self) -> list[dict]:
        return _members(self._read("getRemoteCopyGroups"))

    def remote_copy_group(self, name: str) -> dict | None:
        try:
            body = self._require().getRemoteCopyGroup(name)
            return body if isinstance(body, dict) else None
        except _HTTP_NOT_FOUND:
            return None
        except WsapiError:
            raise
        except Exception as exc:
            raise self._translate(exc, where=f"read Remote Copy group {name}") from exc

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
        except _DESCRIBE_ERRORS:  # describing a failure must never fail
            return ""
        return "" if code in (None, "") else str(code)

    _safe_str = staticmethod(_safe_str)

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
        except OSError as exc:  # the array went away as well; the sentence below still holds
            _log.debug("wsapi_cert_reprobe_failed", host=self.host, error=str(exc))
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
            http_status = getattr(exc, "http_status", None)
            if http_status:
                facts.append(f"HTTP {http_status}")
            if exc.get_code() not in (None, ""):
                facts.append(f"code {exc.get_code()}")
            # Rarely sent, but str(exc) carried them, so they stay.
            for label, value in (("ref", exc.get_ref()), ("debug1", getattr(exc, "_debug1", None)),
                                 ("debug2", getattr(exc, "_debug2", None))):
                if value:
                    facts.append(f"{label} {value}")
        except _DESCRIBE_ERRORS:  # describing a failure must never fail
            return ""
        return f"{desc} ({', '.join(facts)[:200]})" if facts else desc
