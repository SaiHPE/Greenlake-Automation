from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx


class OAuthClientCredentials:
    def __init__(self, token_url: str, client_id: str, client_secret: str) -> None:
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._expires_at = datetime.min.replace(tzinfo=UTC)

    async def token(self) -> str:
        if self._access_token and datetime.now(UTC) < self._expires_at - timedelta(seconds=30):
            return self._access_token
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.token_url,
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
        self._access_token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 900))
        self._expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        return self._access_token
