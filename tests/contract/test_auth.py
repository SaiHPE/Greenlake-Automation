import httpx
import respx

from alletra_onboard.adapters.greenlake.auth import OAuthClientCredentials

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
