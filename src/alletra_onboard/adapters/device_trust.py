"""Trust on first contact for on-site devices (ADR 0026): the one place every SSH and TLS client asks.

A run binds its pins for the length of a step, the way it binds the command log. Before a client
sends a password it hands over what the device presented, and `check()` decides: on the run's first
contact the key is recorded, the same key goes through, and a different key is refused with a
sentence that names the device and both fingerprints. Nothing is sent to a refused device. A pin whose
stored key does not decode (only a damaged `state.db` holds one) is refused the same way, with its own
sentence, so the operator can trust the device again from the run overview.

With no run bound (the lab scripts, the command line) there is nothing to compare with and nothing to
record; the client goes on with what it saw, and keeps it for the rest of its own session.
"""

from __future__ import annotations

import base64
import hashlib
import os
import socket
import ssl
from contextvars import ContextVar, Token
from typing import Protocol

from alletra_onboard.domain.trust import (
    DeviceKey,
    DevicePin,
    TrustKind,
    key_readable,
    mismatch_message,
    refusal_message,
)

try:
    import paramiko
except ImportError:  # pragma: no cover - bundled in the .exe; optional for non-SSH runs
    paramiko = None


class TrustBook(Protocol):
    """One run's pins as the clients see them. The run coordinator implements it."""

    device_ca_bundle: str | None

    def pin(self, kind: TrustKind, host: str, port: int) -> DevicePin | None: ...

    def first_contact(self, pin: DevicePin) -> DevicePin:
        """Record `pin` unless the device already has one; return the pin that holds."""
        ...

    def refuse(self, pin: DevicePin, offered: DeviceKey) -> None:
        """Note that the device presented `offered` instead of `pin.key` and was refused."""
        ...


class DeviceTrustError(Exception):
    """A device presented a key or certificate other than the one the run trusts; nothing was sent."""

    def __init__(self, message: str, *, pin: DevicePin | None = None, offered: DeviceKey | None = None) -> None:
        super().__init__(message)
        self.pin = pin
        self.offered = offered


_book: ContextVar[TrustBook | None] = ContextVar("alletra_device_trust", default=None)


def bind(book: TrustBook | None) -> Token:
    return _book.set(book)


def unbind(token: Token) -> None:
    _book.reset(token)


def current() -> TrustBook | None:
    return _book.get()


DEVICE_CA_BUNDLE_VAR = "ALLETRA_DEVICE_CA_BUNDLE"


def device_ca_bundle() -> str | None:
    """The customer's device CA bundle, when one is set (the run's setting; with no run, the environment).
    Set, it replaces first-contact trust for the TLS devices, and a path that cannot be read stops the
    connection instead of falling back to first-contact trust. SSH has no CA here: it is always pinned."""
    book = current()
    path = ((book.device_ca_bundle if book is not None else os.environ.get(DEVICE_CA_BUNDLE_VAR)) or "").strip()
    if not path:
        return None
    if not os.path.isfile(path):
        raise DeviceTrustError(
            f"The device CA bundle set in {DEVICE_CA_BUNDLE_VAR} ({path}) cannot be read, so the tool did not "
            "connect. Correct the path, or remove the setting to trust devices on first contact, then restart "
            "the app."
        )
    return path


def ca_bundle_refusal(device: str, host: str, bundle: str, detail: str = "") -> str:
    """The sentence for a TLS device the customer's CA bundle does not vouch for."""
    name = device if device == "vCenter" else f"The {device}"
    reason = f" ({detail.strip()[:160]})" if detail.strip() else ""
    return (f"{name} at {host} presented a certificate that the device CA bundle at {bundle} does not vouch "
            f"for, or that does not name {host}{reason}. The password was not sent. Ask the customer for the "
            f"certificate authority that signed it, or remove {DEVICE_CA_BUNDLE_VAR} to trust devices on first "
            "contact.")


def check(kind: TrustKind, host: str, port: int, device: str, offered: DeviceKey) -> DeviceKey:
    """Record on first contact, let the same key through, refuse a different one. Returns the key the
    connection may go on with."""
    book = current()
    if book is None:
        return offered
    pin = book.pin(kind, host, port)
    if pin is None:
        pin = book.first_contact(DevicePin(kind=kind, host=host, port=port, device=device, key=offered))
    if key_readable(pin.key) and pin.key.same_as(offered):
        return pin.key
    book.refuse(pin, offered)
    raise DeviceTrustError(refusal_message(pin, offered), pin=pin, offered=offered)


# ------------------------------------------------------------------ SSH


def ssh_key(key) -> DeviceKey:
    """A paramiko key as the run keeps it: type, base64 public key, `SHA256:` fingerprint."""
    return DeviceKey(kind=TrustKind.SSH, key_type=key.get_name(), data=key.get_base64(), fingerprint=key.fingerprint)


def _known_hosts_name(host: str, port: int) -> str:
    # the name paramiko looks the key up under
    return host if port == 22 else f"[{host}]:{port}"


class FirstContactPolicy(paramiko.MissingHostKeyPolicy if paramiko is not None else object):
    """Called by paramiko only when no key is known for the host: the run's first contact, or a pin
    whose key does not decode. The key goes through `check()`: recorded on first contact, refused when
    another read pinned a different key meanwhile or the pin cannot be read."""

    def __init__(self, host: str, port: int, device: str) -> None:
        self.host, self.port, self.device = host, port, device

    def missing_host_key(self, client, hostname, key) -> None:
        check(TrustKind.SSH, self.host, self.port, self.device, ssh_key(key))
        client.get_host_keys().add(hostname, key.get_name(), key)


def open_ssh(host: str, port: int, *, device: str, username: str, password: str, timeout: float):
    """A logged-in paramiko client, opened only after the host key passed the run's pin.

    The pinned key is preloaded, so paramiko itself compares it and raises `BadHostKeyException` on a
    difference. paramiko checks the host key before it authenticates, so a refused device never gets
    the password. Every SSH client in the tool connects through here.
    """
    client = paramiko.SSHClient()
    book = current()
    pin = book.pin(TrustKind.SSH, host, port) if book is not None else None
    stored = _stored_ssh_key(pin) if pin is not None else None
    if stored is not None:
        client.get_host_keys().add(_known_hosts_name(host, port), pin.key.key_type, stored)
    else:
        pin = None    # nothing preloaded: the policy meets the key, and `check()` compares it with the pin
    client.set_missing_host_key_policy(FirstContactPolicy(host, port, device))
    try:
        client.connect(host, port=port, username=username, password=password, timeout=timeout,
                       allow_agent=False, look_for_keys=False)
    except paramiko.BadHostKeyException as exc:
        client.close()
        if book is None or pin is None:
            raise
        offered = ssh_key(exc.key)
        book.refuse(pin, offered)
        raise DeviceTrustError(mismatch_message(pin, offered), pin=pin, offered=offered) from exc
    except BaseException:
        client.close()
        raise
    return client


def _stored_ssh_key(pin: DevicePin):
    """The pinned key as paramiko compares it, or None when the run's record of it cannot be read."""
    if not key_readable(pin.key):
        return None
    try:
        return paramiko.PKey.from_type_string(pin.key.key_type, base64.b64decode(pin.key.data))
    except (ValueError, paramiko.SSHException):
        return None


# ------------------------------------------------------------------ TLS


def tls_key(der: bytes) -> DeviceKey:
    """A leaf certificate as the run keeps it: PEM, and its SHA-256 in the colon hex
    `openssl x509 -fingerprint -sha256` prints (urllib3's assert_fingerprint takes the same form)."""
    digest = hashlib.sha256(der).hexdigest().upper()
    return DeviceKey(kind=TrustKind.TLS, key_type="certificate", data=ssl.DER_cert_to_PEM_cert(der),
                     fingerprint=":".join(digest[i:i + 2] for i in range(0, len(digest), 2)))


def probe_tls(host: str, port: int, timeout: float) -> bytes:
    """The device's leaf certificate (DER), from a TLS handshake that sends nothing after it. Direct to
    the device: on-site devices are never reached through the proxy (ADR 0008)."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # TRUST-OFF: this handshake only reads the certificate so it can be compared with the run's pin
    # before anything is sent; nothing goes over this connection.
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=timeout) as raw, \
            context.wrap_socket(raw, server_hostname=host) as tls:
        der = tls.getpeercert(binary_form=True)
    if not der:
        raise ssl.SSLError(f"{host}:{port} presented no certificate")
    return der


def check_tls(host: str, port: int, *, device: str, timeout: float = 15.0) -> DeviceKey:
    """Probe and compare, before any login: the certificate the connection may go on with (the run's
    pin; with no run bound, what the device presented now)."""
    return check(TrustKind.TLS, host, port, device, tls_key(probe_tls(host, port, timeout)))


class _PinnedContext(ssl.SSLContext):
    """Compares the certificate of every TLS connection made with it, right after the handshake and
    before the caller can send anything (set up by `pinned_context`)."""

    _pin: tuple[str, int, str, DeviceKey]

    def wrap_socket(self, sock, *args, **kwargs):
        tls = super().wrap_socket(sock, *args, **kwargs)
        try:
            if not kwargs.get("do_handshake_on_connect", True):
                tls.do_handshake()
            self._compare(tls.getpeercert(binary_form=True))
        except BaseException:
            tls.close()
            raise
        return tls

    def _compare(self, der: bytes | None) -> None:
        host, port, device, trusted = self._pin
        if not der:
            raise DeviceTrustError(f"{host}:{port} presented no certificate, so the tool sent nothing.")
        offered = tls_key(der)
        if offered.same_as(trusted):
            return
        if current() is not None:
            check(TrustKind.TLS, host, port, device, offered)   # refused unless the run trusts it now
            return
        pin = DevicePin(kind=TrustKind.TLS, host=host, port=port, device=device, key=trusted)
        raise DeviceTrustError(mismatch_message(pin, offered), pin=pin, offered=offered)


def pinned_context(host: str, port: int, *, device: str, trusted: DeviceKey) -> ssl.SSLContext:
    """An SSL context for a client library that opens its own connections (pyVmomi): no chain check,
    which a device-made certificate cannot pass, and the trusted certificate compared on every one."""
    context = _PinnedContext(ssl.PROTOCOL_TLS_CLIENT)
    # TRUST-OFF: the chain and name checks are off because a certificate the device made for itself
    # cannot pass them; every handshake is compared with the run's pinned certificate instead.
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context._pin = (host, port, device, trusted)
    return context


def bypass_proxy_for(host: str) -> None:
    """Ensure HTTP clients (requests/httpx) talk to an on-site array directly, not via HTTP(S)_PROXY."""
    for var in ("NO_PROXY", "no_proxy"):
        current_val = os.environ.get(var, "")
        hosts = {h.strip() for h in current_val.split(",") if h.strip()}
        if host not in hosts:
            hosts.add(host)
            os.environ[var] = ",".join(sorted(hosts))
