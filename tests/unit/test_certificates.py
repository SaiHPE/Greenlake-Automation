"""ADR 0026 — TLS certificates of on-site devices: probed and compared with the run's pin before login,
then checked on every connection. Certificates are made in the test; nothing connects anywhere."""

from __future__ import annotations

import hashlib
import ssl
from typing import ClassVar

import pytest

from alletra_onboard.adapters import device_trust
from alletra_onboard.adapters.array import wsapi_client
from alletra_onboard.adapters.array.wsapi_client import WsapiClient, WsapiError
from alletra_onboard.adapters.vcenter import vcenter_client
from alletra_onboard.adapters.vcenter.vcenter_client import VCenterClient, VCenterError
from alletra_onboard.domain.trust import DevicePin, TrustKind
from tests.unit import fake_tls

PW = "s3cret-pw"


class _Book:
    device_ca_bundle = None

    def __init__(self) -> None:
        self.pins: dict[tuple, DevicePin] = {}
        self.refused: list = []

    def pin(self, kind, host, port):
        return self.pins.get((kind, host, port))

    def first_contact(self, pin):
        return self.pins.setdefault((pin.kind, pin.host, pin.port), pin)

    def refuse(self, pin, offered):
        self.refused.append((pin, offered))


class _FakeHttp:
    """The SDK's HTTPJSONRESTClient as far as the client uses it: `_time_request` calls `self.request`."""

    def __init__(self) -> None:
        self.pinned: list[str | None] = []    # the fingerprint bound for each call

    def request(self, url, method, **kwargs):
        self.pinned.append(wsapi_client._PINNED_FINGERPRINT.get())
        return {"status": "201"}, {"key": "session"}

    def _time_request(self, url, method, **kwargs):
        return self.request(url, method, **kwargs)


class _FakeSdk:
    made: ClassVar[list[_FakeSdk]] = []

    def __init__(self, api_url, secure=False, timeout=None, suppress_ssl_warnings=False) -> None:
        self.api_url, self.secure = api_url, secure
        self.http = _FakeHttp()
        self.logins: list[tuple[str, str]] = []
        _FakeSdk.made.append(self)

    def login(self, username, password):
        self.http._time_request(f"{self.api_url}/credentials", "POST", body={"user": username})
        self.logins.append((username, password))

    def getStorageSystemInfo(self):
        self.http._time_request(f"{self.api_url}/system", "GET")
        return {"name": "array01"}

    def logout(self):
        pass


@pytest.fixture
def sdk(monkeypatch):
    _FakeSdk.made = []
    monkeypatch.setattr(wsapi_client, "HPE3ParClient", _FakeSdk)
    return _FakeSdk


@pytest.fixture
def certs(monkeypatch):
    return fake_tls.install(monkeypatch)


@pytest.fixture
def book():
    b = _Book()
    token = device_trust.bind(b)
    yield b
    device_trust.unbind(token)


def test_a_certificate_is_kept_as_pem_with_the_sha256_openssl_prints():
    der = fake_tls.self_signed_der()
    key = device_trust.tls_key(der)
    digest = hashlib.sha256(der).hexdigest().upper()
    assert key.fingerprint.replace(":", "") == digest and len(key.fingerprint) == 95
    assert key.data.startswith("-----BEGIN CERTIFICATE-----") and key.key_type == "certificate"


def test_wsapi_trusts_the_certificate_on_first_contact_and_every_call_checks_it(sdk, certs, book):
    der = fake_tls.self_signed_der()
    certs.devices[("10.0.0.5", 443)] = der
    with WsapiClient("10.0.0.5", "3paradm", PW) as client:
        assert client.system_name() == "array01"
    pin = book.pins[(TrustKind.TLS, "10.0.0.5", 443)]
    fingerprint = device_trust.tls_key(der).fingerprint
    assert (pin.device, pin.key.fingerprint) == ("array", fingerprint)
    [made] = sdk.made
    assert made.logins == [("3paradm", PW)]
    assert made.http.pinned == [fingerprint, fingerprint]     # the login and the read, each checked


def test_a_different_wsapi_certificate_stops_before_the_password_is_sent(sdk, certs, book):
    old, new = fake_tls.self_signed_der(), fake_tls.self_signed_der()
    certs.devices[("10.0.0.5", 443)] = old
    WsapiClient("10.0.0.5", "3paradm", PW).connect()
    certs.devices[("10.0.0.5", 443)] = new
    with pytest.raises(WsapiError) as caught:
        WsapiClient("10.0.0.5", "3paradm", PW).connect()
    text = str(caught.value)
    assert text.startswith("The array at 10.0.0.5 presented a different certificate from the one this run trusted.")
    assert device_trust.tls_key(old).fingerprint in text and device_trust.tls_key(new).fingerprint in text
    assert "The password was not sent." in text
    assert len(sdk.made) == 1                                  # no SDK client, so no login, for the second
    [(pin, offered)] = book.refused
    assert (pin.key.fingerprint, offered.fingerprint) == (device_trust.tls_key(old).fingerprint,
                                                          device_trust.tls_key(new).fingerprint)


def test_a_certificate_that_changes_after_login_is_named_and_recorded(sdk, certs, book):
    from hpe3parclient import exceptions as hpe_exc

    old, new = fake_tls.self_signed_der(), fake_tls.self_signed_der()
    certs.devices[("10.0.0.5", 443)] = old
    client = WsapiClient("10.0.0.5", "3paradm", PW)
    client.connect()
    certs.devices[("10.0.0.5", 443)] = new          # what urllib3's fingerprint check met mid-session
    err = client._translate(hpe_exc.SSLCertFailed("SSL Certificate Verification Failed."), where="getHosts")
    assert "presented a different certificate" in str(err) and device_trust.tls_key(new).fingerprint in str(err)
    assert len(book.refused) == 1


def test_with_no_run_bound_the_client_still_checks_its_own_session(sdk, certs):
    der = fake_tls.self_signed_der()
    certs.devices[("10.0.0.5", 443)] = der
    WsapiClient("10.0.0.5", "3paradm", PW).connect()
    assert sdk.made[0].http.pinned == [device_trust.tls_key(der).fingerprint]


# ------------------------------------------------------------------ the SDK's transport

def test_the_sdk_sends_its_requests_through_the_pinned_stand_in():
    from hpe3parclient import http as sdk_http

    assert isinstance(sdk_http.requests, wsapi_client._PinnedRequests)
    assert sdk_http.requests.exceptions.SSLError is __import__("requests").exceptions.SSLError


def test_a_pinned_call_goes_through_a_session_that_asserts_the_fingerprint():
    calls: list = []

    class _Session:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def mount(self, prefix, adapter):
            calls.append(("mount", prefix, adapter.poolmanager.connection_pool_kw.get("assert_fingerprint")))

        def request(self, method, url, **kwargs):
            calls.append(("session", method, url, kwargs["verify"]))
            return "answer"

    class _Requests:
        Session = _Session

        @staticmethod
        def request(method, url, **kwargs):
            calls.append(("plain", method, url))
            return "plain answer"

    stand_in = wsapi_client._PinnedRequests(_Requests)
    assert stand_in.request("GET", "https://10.0.0.5/api/v1/system", verify=False) == "plain answer"
    token = wsapi_client._PINNED_FINGERPRINT.set("AB:CD")
    try:
        assert stand_in.request("GET", "https://10.0.0.5/api/v1/system", verify=False) == "answer"
    finally:
        wsapi_client._PINNED_FINGERPRINT.reset(token)
    assert calls == [("plain", "GET", "https://10.0.0.5/api/v1/system"), ("mount", "https://", "AB:CD"),
                     ("session", "GET", "https://10.0.0.5/api/v1/system", False)]


# ------------------------------------------------------------------ vCenter

class _FakeTls:
    def __init__(self, der: bytes) -> None:
        self.der, self.closed = der, False

    def getpeercert(self, binary_form=False):
        return self.der

    def close(self) -> None:
        self.closed = True


class _FakeVim:
    """SmartConnect as far as trust goes: pyVmomi opens its connections with the context it is given
    (version lookup, then login) and only then sends the account."""

    def __init__(self, monkeypatch, certs: fake_tls.Certificates) -> None:
        self.certs = certs
        self.logins: list[tuple[str, str]] = []
        monkeypatch.setattr(vcenter_client, "SmartConnect", self.smart_connect)

        def handshake(context, sock, server_hostname=None, **kwargs):   # the TLS layer, offline
            return _FakeTls(certs.devices[(server_hostname, 443)])

        monkeypatch.setattr(ssl.SSLContext, "wrap_socket", handshake)

    def smart_connect(self, *, host, user, pwd, port, sslContext, **kwargs):
        for _ in ("/sdk/vimServiceVersions.xml", "/sdk"):
            sslContext.wrap_socket(object(), server_hostname=host)
        self.logins.append((user, pwd))
        return object()


def test_vcenter_trusts_its_certificate_on_first_contact_and_checks_every_connection(monkeypatch, certs, book):
    vim = _FakeVim(monkeypatch, certs)
    der = fake_tls.self_signed_der("vcenter")
    certs.devices[("10.0.0.20", 443)] = der
    VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    pin = book.pins[(TrustKind.TLS, "10.0.0.20", 443)]
    assert (pin.device, pin.key.fingerprint) == ("vCenter", device_trust.tls_key(der).fingerprint)
    assert pin.key.data.startswith("-----BEGIN CERTIFICATE-----")      # the PEM, as pyVmomi would need it
    assert vim.logins == [("administrator@vsphere.local", PW)]


def test_a_different_vcenter_certificate_stops_before_the_account_is_sent(monkeypatch, certs, book):
    vim = _FakeVim(monkeypatch, certs)
    certs.devices[("10.0.0.20", 443)] = fake_tls.self_signed_der("vcenter")
    VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    certs.devices[("10.0.0.20", 443)] = fake_tls.self_signed_der("impostor")
    with pytest.raises(VCenterError) as caught:
        VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    assert str(caught.value).startswith("vCenter at 10.0.0.20 presented a different certificate")
    assert len(vim.logins) == 1 and len(book.refused) == 1


def test_a_vcenter_certificate_swapped_after_the_probe_is_caught_on_the_connection(monkeypatch, certs, book):
    vim = _FakeVim(monkeypatch, certs)
    trusted = fake_tls.self_signed_der("vcenter")
    certs.devices[("10.0.0.20", 443)] = trusted
    probe = certs.probe

    def probe_then_swap(host, port, timeout):
        der = probe(host, port, timeout)
        certs.devices[(host, port)] = fake_tls.self_signed_der("impostor")
        return der

    monkeypatch.setattr(device_trust, "probe_tls", probe_then_swap)
    with pytest.raises(VCenterError, match="presented a different certificate"):
        VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    assert vim.logins == [] and len(book.refused) == 1


# ------------------------------------------------------------------ the customer's device CA bundle

@pytest.fixture
def bundle(tmp_path, book):
    path = tmp_path / "device-ca.pem"
    path.write_text(ssl.DER_cert_to_PEM_cert(fake_tls.self_signed_der("customer CA")))
    book.device_ca_bundle = str(path)
    return str(path)


def test_with_a_device_ca_bundle_wsapi_makes_the_full_check_and_pins_nothing(sdk, certs, book, bundle):
    WsapiClient("10.0.0.5", "3paradm", PW).connect()
    [made] = sdk.made
    assert made.secure == bundle and made.http.pinned == [None]     # requests checks chain and name
    assert certs.probes == [] and book.pins == {}
    assert made.logins == [("3paradm", PW)]


def test_a_certificate_the_bundle_does_not_vouch_for_never_falls_back_to_first_contact(sdk, certs, book, bundle):
    from hpe3parclient import exceptions as hpe_exc

    client = WsapiClient("10.0.0.5", "3paradm", PW)
    client.connect()
    err = client._translate(hpe_exc.SSLCertFailed("SSL Certificate Verification Failed."), where="login")
    assert str(err).startswith(f"The array at 10.0.0.5 presented a certificate that the device CA bundle at {bundle}")
    assert "The password was not sent." in str(err)
    assert certs.probes == [] and book.pins == {} and book.refused == []


def test_a_device_ca_bundle_that_cannot_be_read_stops_the_connection(sdk, certs, book, tmp_path):
    book.device_ca_bundle = str(tmp_path / "missing.pem")
    with pytest.raises(WsapiError, match="device CA bundle set in ALLETRA_DEVICE_CA_BUNDLE .* cannot be read"):
        WsapiClient("10.0.0.5", "3paradm", PW).connect()
    assert sdk.made == [] and certs.probes == []


def test_with_no_run_bound_the_bundle_comes_from_the_environment(sdk, certs, monkeypatch, tmp_path):
    path = tmp_path / "device-ca.pem"
    path.write_text(ssl.DER_cert_to_PEM_cert(fake_tls.self_signed_der("customer CA")))
    monkeypatch.setenv("ALLETRA_DEVICE_CA_BUNDLE", str(path))
    WsapiClient("10.0.0.5", "3paradm", PW).connect()
    assert sdk.made[0].secure == str(path) and certs.probes == []


def test_with_a_device_ca_bundle_vcenter_is_checked_against_it(monkeypatch, certs, book, bundle):
    seen: dict = {}

    def smart_connect(*, sslContext, **kwargs):
        seen["ctx"] = sslContext
        return object()

    monkeypatch.setattr(vcenter_client, "SmartConnect", smart_connect)
    VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    ctx = seen["ctx"]
    assert ctx.verify_mode == ssl.CERT_REQUIRED and ctx.check_hostname
    assert certs.probes == [] and book.pins == {}


def test_a_vcenter_certificate_the_bundle_refuses_is_named(monkeypatch, certs, book, bundle):
    def smart_connect(**kwargs):
        raise ssl.SSLCertVerificationError(1, "certificate verify failed: self-signed certificate")

    monkeypatch.setattr(vcenter_client, "SmartConnect", smart_connect)
    with pytest.raises(VCenterError) as caught:
        VCenterClient("10.0.0.20", "administrator@vsphere.local", PW).connect()
    assert str(caught.value).startswith(f"vCenter at 10.0.0.20 presented a certificate that the device CA bundle at {bundle}")


@pytest.mark.parametrize("with_bundle", [False, True])
def test_winrm_over_https_validates_against_the_bundle_only_when_one_is_set(monkeypatch, book, tmp_path, with_bundle):
    from alletra_onboard.adapters.hosts import windows_winrm

    seen: list[dict] = []

    class FakeSession:
        def __init__(self, url, auth, **kwargs):
            seen.append(dict(kwargs, url=url))

        def run_ps(self, script):
            raise ConnectionRefusedError("closed")      # neither listener answers: both are tried

    if with_bundle:
        path = tmp_path / "device-ca.pem"
        path.write_text(ssl.DER_cert_to_PEM_cert(fake_tls.self_signed_der("customer CA")))
        book.device_ca_bundle = str(path)
    monkeypatch.setattr(windows_winrm, "winrm", type("W", (), {"Session": FakeSession}))
    with pytest.raises(windows_winrm.WindowsHostError):
        windows_winrm.WindowsHostClient("10.0.3.4", "administrator", PW).connect()
    assert [s["transport"] for s in seen] == ["ntlm", "ntlm"]
    if with_bundle:
        assert all((s["server_cert_validation"], s["ca_trust_path"]) == ("validate", book.device_ca_bundle) for s in seen)
    else:
        assert all(s["server_cert_validation"] == "ignore" and "ca_trust_path" not in s for s in seen)


def test_the_run_says_which_device_ca_bundle_it_uses(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient

    from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
    from alletra_onboard.api.app import create_app
    from alletra_onboard.application.runs.event_bus import InMemoryEventBus
    from alletra_onboard.application.service import OnboardingService
    from alletra_onboard.config import Settings
    from tests.unit.test_device_trust import _item

    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_item())
    monkeypatch.setenv("ALLETRA_DEVICE_CA_BUNDLE", "C:/certs/customer-devices.pem")
    body = TestClient(create_app(service)).get(f"/runs/{run.run_id}/trust").json()
    assert body == {"devices": [], "device_ca_bundle": "C:/certs/customer-devices.pem"}
