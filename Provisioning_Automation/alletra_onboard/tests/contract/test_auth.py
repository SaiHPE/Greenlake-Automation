import httpx
import pytest
import respx

from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials
from alletra_onboard.domain.errors import GreenLakeHttpError

TOKEN_URL = "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/tid/token"


@respx.mock
async def test_token_posts_client_credentials_in_body():
    route = respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "jwt-abc", "expires_in": 900})
    )
    provider = OAuthClientCredentials(TOKEN_URL, "cid", "shh")

    token = await provider.token()

    assert token == "jwt-abc"
    body = route.calls.last.request.content.decode()
    assert "grant_type=client_credentials" in body
    assert "client_id=cid" in body
    assert "client_secret=shh" in body


@respx.mock
async def test_token_is_cached_until_near_expiry():
    route = respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "jwt-abc", "expires_in": 900})
    )
    provider = OAuthClientCredentials(TOKEN_URL, "cid", "shh")

    await provider.token()
    await provider.token()

    assert route.call_count == 1


@respx.mock
async def test_a_redirect_from_the_token_endpoint_is_an_error():
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(302, headers={"Location": "https://login.example/sso"}))

    with pytest.raises(GreenLakeHttpError) as refused:
        await OAuthClientCredentials(TOKEN_URL, "cid", "shh").token()

    assert refused.value.status_code == 302


async def test_token_transport_error_translates_to_greenlake_error_preserving_tls_cause(monkeypatch):
    """STANDARD E1: OAuth transport errors become GreenLakeError (DeviceError) with __cause__
    intact so TLS trust inspection still detects corporate proxy certificate failures."""
    import ssl

    from alletra_onboard.adapters.tls import is_tls_trust_error
    from alletra_onboard.domain.errors import DeviceError, GreenLakeError

    tls_err = ssl.SSLCertVerificationError("[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer")

    async def _raise_tls(self, *_args, **_kwargs) -> httpx.Response:
        raise httpx.ConnectError("connection failed") from tls_err

    monkeypatch.setattr(httpx.AsyncClient, "post", _raise_tls)

    with pytest.raises(GreenLakeError) as exc_info:
        await OAuthClientCredentials(TOKEN_URL, "cid", "shh").token()

    assert isinstance(exc_info.value, DeviceError)
    assert is_tls_trust_error(exc_info.value) is True
