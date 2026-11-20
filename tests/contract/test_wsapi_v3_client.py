"""ADR 0021 / SPEC-028 R1: the WSAPI v3 read client, against the array's own answers.

The login answer is replayed from the D22U27 capture (`tests/fixtures/unified_file/d22u27/`): the
capture's headers with test values where it redacted the session, so the stub sends what the array
sends (three cookies, a body `key`), never a hand-written guess (LESSONS 28, 29). The reads replay the
captured bodies."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
import respx

from alletra_onboard.adapters import command_log, device_trust
from alletra_onboard.adapters.array.wsapi_v3_client import (
    V3Answer,
    WsapiV3Client,
    WsapiV3Error,
    WsapiV3LoginRefused,
    WsapiV3TrustError,
)
from tests.unit import fake_tls
from tests.unit.test_device_trust import _Book

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "unified_file" / "d22u27"
HOST = "10.64.122.99"
BASE = f"https://{HOST}/api/v3"
PW = "zz-array-password"
KEY = "0-zz-session-key-0123456789abcdef"
COOKIES = {"sessionToken": "zz-cookie-token", "hpeWsapiSentryLineage": "zz-cookie-lineage",
           "hpeWsapiSentryUsername": "zz-cookie-user"}


def _captured(name: str) -> dict:
    return json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))


def _login_answer() -> httpx.Response:
    """The captured 201, with test values where the capture redacted the session."""
    captured = _captured("wsapi_v3_login")
    headers = []
    for name, value in captured["headers"]:
        if name == "Set-Cookie":
            cookie = value.split("=", 1)[0]
            value = value.replace("<redacted>", COOKIES[cookie])
        elif name == "Location":
            value = value.replace("<redacted>", KEY)
        if name not in ("Content-Length", "Transfer-Encoding", "Connection"):
            headers.append((name, value))
    body = {"key": KEY, "sessionId": "zz-session-id", "username": "3paradm", "arrayPrivileges": []}
    assert set(body) == set(captured["body"])
    return httpx.Response(captured["status"], headers=headers, json=body)


def _replay(name: str) -> httpx.Response:
    captured = _captured(name)
    return httpx.Response(captured["status"], json=captured["body"])


@pytest.fixture(autouse=True)
def certificates(monkeypatch):
    # ADR 0026: the client reads the array's certificate before login; a made-up one stands in for it
    certs = fake_tls.install(monkeypatch)
    certs.devices[(HOST, 443)] = fake_tls.self_signed_der("array")
    return certs


@pytest.fixture(autouse=True)
def _proxy_env(monkeypatch):
    # The client adds the array to NO_PROXY, as the v1 client does; put the variables back after.
    for var in ("NO_PROXY", "no_proxy"):
        monkeypatch.setenv(var, "")


@pytest.fixture
def recorded():
    got: list[dict] = []
    token = command_log.bind(got.append)
    yield got
    command_log.unbind(token)


@pytest.fixture
def array():
    with respx.mock(base_url=BASE, assert_all_called=False) as mock:
        mock.post("/credentials", name="login").mock(return_value=_login_answer())
        mock.delete(f"/credentials/{KEY}", name="logout").mock(return_value=httpx.Response(200))
        for resource in ("fileservice", "filesystems", "filesharesettings", "fileshares"):
            mock.get(f"/{resource}", name=resource).mock(return_value=_replay(f"wsapi_v3_{resource}"))
        yield mock


def _client() -> WsapiV3Client:
    return WsapiV3Client(HOST, "3paradm", PW)


def test_login_sends_the_user_and_password_as_json(array):
    with _client():
        pass
    request = array["login"].calls.last.request
    assert json.loads(request.content) == {"user": "3paradm", "password": PW}
    assert request.headers["Content-Type"] == "application/json"
    assert "X-HP3PAR-WSAPI-SessionKey" not in request.headers


def test_every_get_carries_the_key_header_all_three_cookies_and_content_type(array):
    with _client() as v3:
        for resource in ("fileservice", "filesystems", "filesharesettings", "fileshares"):
            assert v3.get(f"/{resource}").status == 200
    for resource in ("fileservice", "filesystems", "filesharesettings", "fileshares"):
        request = array[resource].calls.last.request
        assert request.headers["X-HP3PAR-WSAPI-SessionKey"] == KEY
        # OS 10.5.x answers a GET without it with 400 MISSING_MEDIA_TYPE_HEADER.
        assert request.headers["Content-Type"] == "application/json"
        sent = dict(c.split("=", 1) for c in request.headers["Cookie"].split("; "))
        assert sent == COOKIES


def test_the_session_is_deleted_by_its_key_when_the_reads_are_done(array):
    with _client() as v3:
        v3.get("/fileservice")
    assert array["logout"].call_count == 1
    assert array["logout"].calls.last.request.headers["X-HP3PAR-WSAPI-SessionKey"] == KEY


def test_the_session_is_deleted_when_a_read_raises(array):
    with pytest.raises(RuntimeError, match="parser failed"), _client() as v3:
        v3.get("/fileservice")
        raise RuntimeError("parser failed")
    assert array["logout"].call_count == 1


def test_the_session_is_deleted_when_a_read_gets_no_answer(array):
    array["filesystems"].mock(side_effect=httpx.ConnectError("connection reset"))
    with pytest.raises(WsapiV3Error, match="no answer"), _client() as v3:
        v3.get("/filesystems")
    assert array["logout"].call_count == 1


@pytest.mark.parametrize("status, key", [
    (400, "MISSING_MEDIA_TYPE_HEADER"), (401, "INVALID_SESSION_KEY"), (404, "NON_EXISTENT_RESOURCE"),
])
def test_an_http_error_with_a_json_body_is_an_answer_not_a_failure(array, status, key):
    """Lesson 27: the array answered in its own protocol. The 400's body is the one 10.5.x sent."""
    array["filesystems"].mock(return_value=httpx.Response(status, json={"message": {"key": key}}))
    with _client() as v3:
        answer = v3.get("/filesystems")
    assert answer == V3Answer(status=status, body={"message": {"key": key}})


def test_no_answer_at_the_login_raises_and_nothing_else_is_sent(array):
    array["login"].mock(side_effect=httpx.ConnectTimeout("timed out"))
    with pytest.raises(WsapiV3Error, match="no answer"), _client():
        pass
    assert array["logout"].call_count == 0


def test_a_refused_login_is_an_answer_with_no_session(array):
    array["login"].mock(return_value=httpx.Response(401, json={"code": 5, "desc": "invalid username or password"}))
    with pytest.raises(WsapiV3LoginRefused) as refused, _client():
        pass
    assert refused.value.status == 401
    assert array["logout"].call_count == 0


def test_the_client_has_no_write_method_and_refuses_one_built_by_hand(array):
    for name in ("post", "put", "patch", "delete"):
        assert not hasattr(WsapiV3Client, name)
    with _client() as v3:
        for method, path in (("POST", "/api/v3/filesystems"), ("PUT", "/api/v3/fileservice"),
                             ("PATCH", "/api/v3/fileshares/x"), ("DELETE", "/api/v3/fileshares/x"),
                             ("DELETE", "/api/v3/credentials/another-key"), ("GET", "/api/v1/volumes"),
                             ("GET", f"/api/v3/credentials/{KEY}")):
            with pytest.raises(ValueError, match="refused"):
                v3._send(method, path)
    assert [c.request.method for c in array.calls] == ["POST", "DELETE"]


def test_a_read_needs_a_session():
    with pytest.raises(WsapiV3Error, match="no session"):
        _client().get("/fileservice")


def test_each_call_is_recorded_with_method_path_and_status(array, recorded):
    array["filesystems"].mock(return_value=httpx.Response(401, json={"message": {"key": "INVALID_SESSION_KEY"}}))
    with _client() as v3:
        v3.get("/fileservice")
        v3.get("/filesystems")
    login, service, systems, logout = recorded
    assert (login["command"], login["result"], login["ok"], login["write"]) == (
        "POST /api/v3/credentials {user, password: ********}", "HTTP 201", True, False)
    assert login["output"] == "(session key withheld)"
    assert (service["command"], service["result"], service["ok"], service["transport"]) == (
        "GET /api/v3/fileservice", "HTTP 200", True, "wsapi")
    assert '"arraySerialNumber": "CZ2D320BT1"' in service["output"]
    assert (systems["command"], systems["result"], systems["ok"]) == ("GET /api/v3/filesystems", "HTTP 401", False)
    assert (logout["command"], logout["result"], logout["write"]) == (
        "DELETE /api/v3/credentials/********", "HTTP 200", False)
    assert {e["target"] for e in recorded} == {HOST}


def test_the_password_key_and_cookie_values_never_reach_the_log(array, recorded):
    echo = {"members": {}, "echo": [PW, KEY, *COOKIES.values()]}
    array["fileshares"].mock(return_value=httpx.Response(200, json=echo))
    with _client() as v3:
        v3.get("/fileshares")
    array["fileshares"].mock(side_effect=httpx.ConnectError(f"reset after {KEY}"))
    with pytest.raises(WsapiV3Error), _client() as v3:
        v3.get("/fileshares")
    text = json.dumps(recorded)
    for secret in (PW, KEY, *COOKIES.values()):
        assert secret not in text
    assert command_log.REDACTED in recorded[1]["output"]


def test_a_body_the_caller_withholds_is_not_logged_but_the_call_is(array, recorded):
    with _client() as v3:
        answer = v3.get("/fileshares", withhold=lambda a: "(not recorded: another array)")
    assert answer.body["arraySerialNumber"] == "CZ2D320BT1"        # the caller still gets the answer
    shares = [e for e in recorded if e["command"] == "GET /api/v3/fileshares"]
    assert [(e["result"], e["output"]) for e in shares] == [("HTTP 200", "(not recorded: another array)")]


def test_another_arrays_shares_never_reach_the_command_log(array, recorded):
    """ADR 0021 item 1: none of another array's read is shown or stored, and the command log is both."""
    from alletra_onboard.application.unified_file.read import OTHER_ARRAY, read_file_report
    from tests.unit.test_unified_file_read import CapturedCli, _ports

    other = _captured("wsapi_v3_fileshares")
    other["body"]["arraySerialNumber"] = "CZ2D2K014S"
    array["fileshares"].mock(return_value=httpx.Response(200, json=other["body"]))
    report = read_file_report(CapturedCli("d22u27"), _client(), "10.5.0", _ports("d22u27"))
    assert report.notes == [OTHER_ARRAY.format(found="CZ2D2K014S", expected="CZ2D320BT1")]
    assert report.shares == [] and array["logout"].call_count == 1
    logged = json.dumps(recorded)
    for name in ("share01", "Lab_test", "/file/fs01/share01"):
        assert name not in logged
    assert "GET /api/v3/fileshares" in [e["command"] for e in recorded]


def test_a_certificate_other_than_the_one_the_run_trusts_stops_the_login_before_the_password(array, certificates):
    book = _Book()
    token = device_trust.bind(book)
    try:
        with _client():
            pass
        certificates.devices[(HOST, 443)] = fake_tls.self_signed_der("someone-else")
        with pytest.raises(WsapiV3TrustError) as caught:
            _client().login()
    finally:
        device_trust.unbind(token)
    assert array["login"].call_count == 1
    assert "presented a different" in str(caught.value) and "The password was not sent." in str(caught.value)
