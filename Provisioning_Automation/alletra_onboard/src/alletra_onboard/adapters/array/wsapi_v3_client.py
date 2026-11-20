"""WSAPI v3 read client for the Alletra MP B10000's file side (ADR 0021, SPEC-028 R1).

`https://<array>/api/v3`, logged in with the run's one array credential (ADR 0013). It reads only:
`get()`, plus the session login and logout. There is no post, put, patch or delete method, and the
one place a request is built refuses any other call. A write needs ADR 0021's write-plane amendment.

What both captures (`tests/fixtures/unified_file/`) showed and this client copies:

- **The session.** `POST /api/v3/credentials` answers 201 with a body `key` and three cookies
  (`sessionToken`, `hpeWsapiSentryLineage`, `hpeWsapiSentryUsername`). Every GET sends the key as
  `X-HP3PAR-WSAPI-SessionKey` *and* the cookies, as both captures did: which one the array needs is
  not yet narrowed. The session is always deleted (`DELETE /api/v3/credentials/<key>`), also when a
  read fails or raises: the context manager's exit runs it.
- **`Content-Type: application/json` on every request, GETs included.** OS 10.5.x answers a GET
  without it with 400 `MISSING_MEDIA_TYPE_HEADER`.
- **Any HTTP answer is an answer** (lesson 27). A 400, 401 or 404 comes back as a `V3Answer`; only a
  request that got no answer (connection, TLS, timeout) raises `WsapiV3Error`.

The certificate is checked as for the v1 client (ADR 0026): against the customer's device CA bundle
when one is set, otherwise against the run's pin, before the password is sent and on every connection.
A direct route around the jump box proxy, as the v1 client does.
Every call goes to the command log; the password, the session key and the cookies never do.
"""

from __future__ import annotations

import json
import ssl
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.domain.errors import (
    WsapiV3Error,
    WsapiV3LoginRefused,
    WsapiV3TrustError,
)

API_ROOT = "/api/v3"
_CREDENTIALS = f"{API_ROOT}/credentials"
_JSON = "application/json"


@dataclass(frozen=True)
class V3Answer:
    """One HTTP answer: its status and its body, parsed as JSON when it is JSON, else the text."""

    status: int
    body: Any


class WsapiV3Client:
    def __init__(self, host: str, username: str, password: str, *, port: int = 443,
                 timeout: float = 60.0, connect_timeout: float = 15.0) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.base_url = f"https://{host}" + ("" if port == 443 else f":{port}")
        self.timeout = httpx.Timeout(timeout, connect=connect_timeout)
        self._http: httpx.Client | None = None
        self._key = ""
        self._cookies: list[str] = []   # "name=value", as the login set them

    # ------------------------------------------------------------------ session

    def login(self) -> V3Answer:
        """Open the session. Raises `WsapiV3Error` when the array does not answer and
        `WsapiV3LoginRefused` when it answers without a session."""
        self.logout()
        device_trust.bypass_proxy_for(self.host)
        self._http = httpx.Client(base_url=self.base_url, verify=self._tls_context(), timeout=self.timeout)
        try:
            answer, headers = self._send("POST", _CREDENTIALS,
                                         body={"user": self.username, "password": self.password})
        except WsapiV3Error:
            self._close_http()
            raise
        key = answer.body.get("key") if isinstance(answer.body, dict) else None
        if answer.status not in (200, 201) or not isinstance(key, str) or not key:
            self._close_http()
            raise WsapiV3LoginRefused(answer)
        self._key = key
        self._cookies = [c.split(";", 1)[0].strip() for c in headers.get_list("set-cookie")]
        return answer

    def _tls_context(self) -> ssl.SSLContext:
        """The customer's device CA bundle when set (full check, no fallback); otherwise the certificate is
        read and compared with the run's pin before the password is sent, and on every connection after."""
        try:
            bundle = device_trust.device_ca_bundle()
            if bundle:
                return ssl.create_default_context(cafile=bundle)
            trusted = device_trust.check_tls(self.host, self.port, device="array",
                                             timeout=self.timeout.connect or 15.0)
            return device_trust.pinned_context(self.host, self.port, device="array", trusted=trusted)
        except device_trust.DeviceTrustError as exc:
            raise WsapiV3TrustError(str(exc)) from exc
        except Exception as exc:
            raise WsapiV3Error(f"no answer from {self.host} ({type(exc).__name__}: {exc})") from exc

    def logout(self) -> None:
        """Delete the session and close the connection. Safe to call twice, and never raises: a
        session that cannot be deleted times out on the array."""
        try:
            if self._http is not None and self._key:
                self._send("DELETE", f"{_CREDENTIALS}/{self._key}")
        except Exception:  # recorded in the command log by _send; nothing to undo
            pass
        finally:
            self._key, self._cookies = "", []
            self._close_http()

    def __enter__(self) -> WsapiV3Client:
        self.login()
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.logout()

    # ------------------------------------------------------------------ reads

    def get(self, path: str, *, withhold: Callable[[V3Answer], str] | None = None) -> V3Answer:
        """`GET /api/v3<path>`, e.g. `get("/fileservice")`. Any HTTP status is returned; only no
        answer raises (`WsapiV3Error`). `withhold(answer)`, when given, says why the answer's body
        must stay out of the command log (another array's records, ADR 0021 item 1), or "" to log it;
        the call and its status are logged either way."""
        if self._http is None or not self._key:
            raise WsapiV3Error("no session: log in before reading")
        answer, _headers = self._send("GET", API_ROOT + path, withhold=withhold)
        return answer

    # ------------------------------------------------------------------ the one request builder

    def _allowed(self, method: str, path: str) -> bool:
        if method == "GET":
            return path.startswith(API_ROOT + "/") and not path.startswith(_CREDENTIALS)
        if method == "POST":
            return path == _CREDENTIALS
        if method == "DELETE":
            return bool(self._key) and path == f"{_CREDENTIALS}/{self._key}"
        return False

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": _JSON, "Content-Type": _JSON}
        if self._key:
            headers["X-HP3PAR-WSAPI-SessionKey"] = self._key
        if self._cookies:
            headers["Cookie"] = "; ".join(self._cookies)
        return headers

    def _secrets(self) -> list[str]:
        return [self.password, self._key, *(c.partition("=")[2] for c in self._cookies)]

    def _send(self, method: str, path: str, *, body: dict | None = None,
              withhold: Callable[[V3Answer], str] | None = None) -> tuple[V3Answer, httpx.Headers]:
        if not self._allowed(method, path) or self._http is None:
            raise ValueError(f"refused: {method} {path}; this client only reads")
        login = method == "POST"
        shown = f"{_CREDENTIALS}/********" if method == "DELETE" else path
        command = f"{method} {shown}" + (" {user, password: ********}" if login else "")
        secrets = self._secrets()
        started = time.monotonic()
        # The client keeps no cookie jar of its own: the session goes out as the headers above only.
        self._http.cookies.clear()
        try:
            resp = self._http.request(method, path, headers=self._headers(),
                                      content=None if body is None else json.dumps(body))
        except device_trust.DeviceTrustError as exc:
            command_log.record(target=self.host, transport="wsapi", command=command, started=started,
                               ok=False, result="refused: the certificate is not the one the run trusts",
                               secrets=secrets)
            raise WsapiV3TrustError(str(exc)) from exc
        except httpx.HTTPError as exc:
            command_log.record(target=self.host, transport="wsapi", command=command, started=started,
                               ok=False, result=f"no answer: {type(exc).__name__}: {exc}", secrets=secrets)
            raise WsapiV3Error(f"{method} {shown}: no answer from {self.host} ({type(exc).__name__}: {exc})") from exc
        try:
            parsed: Any = resp.json()
        except ValueError:
            parsed = resp.text
        answer = V3Answer(status=resp.status_code, body=parsed)
        ok = 200 <= resp.status_code < 300
        output: Any = parsed
        if login and ok:
            output = "(session key withheld)"
        elif withhold is not None:
            output = withhold(answer) or parsed
        command_log.record(
            target=self.host, transport="wsapi", command=command, started=started, ok=ok,
            result=f"HTTP {resp.status_code}", output=output, secrets=secrets,
        )
        return answer, resp.headers

    def _close_http(self) -> None:
        if self._http is not None:
            try:
                self._http.close()
            except Exception:
                pass
            self._http = None
