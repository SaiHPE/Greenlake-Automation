from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlsplit

import httpx

from alletra_onboard.adapters import command_log
from alletra_onboard.adapters.tls import ssl_context
from alletra_onboard.domain.errors import GreenLakeHttpError


class OAuthClientCredentials:
    """OAuth2 client-credentials token provider for HPE GreenLake personal API clients.

    Per the GreenLake "Generating an access token" docs, the client id and secret are
    posted in the form body (application/x-www-form-urlencoded) to the workspace token
    URL, e.g. https://global.api.greenlake.hpe.com/authorization/v2/oauth2/<tid>/token.
    GreenLake platform tokens are valid ~15 minutes, so the cache refreshes early.
    """

    def __init__(self, token_url: str, client_id: str, client_secret: str) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._expires_at = datetime.min.replace(tzinfo=UTC)

    async def token(self) -> str:
        if self._access_token and datetime.now(UTC) < self._expires_at - timedelta(seconds=60):
            return self._access_token
        started = time.monotonic()
        try:
            # verify against the OS trust store + certifi, so a corporate TLS-inspection root that the
            # browser already trusts does not fail here as a bogus "credentials rejected".
            async with httpx.AsyncClient(timeout=30, verify=ssl_context()) as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
        except Exception as exc:
            self._record(started, ok=False, result=type(exc).__name__)
            raise
        self._record(started, ok=response.is_success, result=f"HTTP {response.status_code}",
                     output="(token withheld)" if response.is_success else "")
        if response.is_error:
            raise GreenLakeHttpError(
                response.status_code,
                response.request.method,
                response.request.url.path,
            )
        payload = response.json()
        self._access_token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 900))
        self._expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        return self._access_token

    def _record(self, started: float, *, ok: bool, result: str, output: str = "") -> None:
        """The token request: its path, never the form body (the client secret) or the answer (the token)."""
        url = urlsplit(self.token_url)
        command_log.record(
            target=url.hostname or self.token_url, transport="greenlake",
            command=f"POST {url.path} (client credentials withheld)", started=started, ok=ok,
            result=result, output=output, secrets=[self.client_secret, self._access_token or ""],
        )
