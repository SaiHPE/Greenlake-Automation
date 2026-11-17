"""Device trust (ADR 0026): what an on-site device presented, and the pin a run keeps for it.

Cloud endpoints (GreenLake, DSCC) are checked against certificate authorities and never appear here.
On-site devices (the array and its Remote Copy peer, vCenter, the Brocade switches, Linux hosts) ship
with self-signed certificates and SSH keys nobody recorded, so a run trusts each one the first time it
reaches it and keeps what it saw. A later difference stops the step before the password is sent.

The sentences the operator reads live here too, so every client says the same thing.
"""

from __future__ import annotations

import base64
import binascii
import ssl
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

DEFAULT_PORTS = {"ssh": 22, "tls": 443}


class TrustKind(StrEnum):
    SSH = "ssh"
    TLS = "tls"


class DeviceKey(BaseModel):
    """What a device presented.

    SSH: the host key type (`ssh-ed25519`), the public key in base64 as `known_hosts` holds it, and the
    `SHA256:` fingerprint `ssh-keygen -l` prints. TLS: `certificate`, the leaf certificate in PEM, and
    its SHA-256 as colon-separated hex, as `openssl x509 -fingerprint -sha256` prints it.
    """

    kind: TrustKind
    key_type: str
    data: str
    fingerprint: str

    def same_as(self, other: DeviceKey) -> bool:
        return self.kind == other.kind and self.fingerprint == other.fingerprint


class DevicePin(BaseModel):
    """The key a run trusts for one device address, port and kind. Lives with the run (ADR 0013)."""

    kind: TrustKind
    host: str
    port: int
    device: str                      # what the tool calls it: "array", "switch", "vCenter", "Linux host"
    key: DeviceKey
    trusted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    how: Literal["first_contact", "retrusted"] = "first_contact"
    previous: DeviceKey | None = None        # the key a re-trust replaced
    refused: DeviceKey | None = None         # a different key the device presented since; nothing was sent
    refused_at: datetime | None = None


class DevicePinInfo(BaseModel):
    """What the run overview and the as-built show: no key material, only what a person compares."""

    kind: TrustKind
    host: str
    port: int
    device: str
    key_type: str
    fingerprint: str
    trusted_at: datetime
    how: str
    previous_fingerprint: str | None = None
    refused_key_type: str | None = None
    refused_fingerprint: str | None = None
    refused_at: datetime | None = None

    @classmethod
    def of(cls, pin: DevicePin) -> DevicePinInfo:
        return cls(
            kind=pin.kind, host=pin.host, port=pin.port, device=pin.device, key_type=pin.key.key_type,
            fingerprint=pin.key.fingerprint, trusted_at=pin.trusted_at, how=pin.how,
            previous_fingerprint=pin.previous.fingerprint if pin.previous else None,
            refused_key_type=pin.refused.key_type if pin.refused else None,
            refused_fingerprint=pin.refused.fingerprint if pin.refused else None,
            refused_at=pin.refused_at,
        )


def address(kind: TrustKind | str, host: str, port: int) -> str:
    """`10.0.0.5`, or `10.0.0.5:2222` when the port is not the usual one for the kind."""
    return host if DEFAULT_PORTS.get(str(kind)) == port else f"{host}:{port}"


def describe(key: DeviceKey) -> str:
    """`SSH host key SHA256:… (ssh-ed25519)` or `certificate SHA-256 AB:CD:…`."""
    if key.kind == TrustKind.SSH:
        return f"SSH host key {key.fingerprint} ({key.key_type})"
    return f"certificate SHA-256 {key.fingerprint}"


def _what(kind: TrustKind | str) -> str:
    return "SSH host key" if str(kind) == TrustKind.SSH else "certificate"


def _the(device: str) -> str:
    """`the array`, `the Linux host`, but `vCenter`: a product name takes no article."""
    return device if device == "vCenter" else f"the {device}"


def key_readable(key: DeviceKey) -> bool:
    """Whether a stored key still decodes: an SSH key's base64 holds a blob that names its own type, a
    certificate's PEM holds DER. Only a damaged run state (`state.db`) holds one that does not."""
    try:
        if key.kind == TrustKind.SSH:
            blob = base64.b64decode(key.data, validate=True)
            size = int.from_bytes(blob[:4], "big")
            return blob[4:4 + size] == key.key_type.encode()
        return bool(ssl.PEM_cert_to_DER_cert(key.data))
    except (binascii.Error, ValueError, TypeError):
        return False


#: How the operator trusts a device again, in every sentence that asks for it.
RETRUST_STEPS = ("compare the new fingerprint with the device's own console, then trust it again on the run "
                 "overview, under Trusted devices")


def _sentence_start(text: str) -> str:
    return f"T{text[1:]}" if text.startswith("the ") else text


def _presented(key: DeviceKey) -> str:
    return f"{key.fingerprint}{f' ({key.key_type})' if key.kind == TrustKind.SSH else ''}"


def trusted_message(pin: DevicePin) -> str:
    return (f"Trusted {_the(pin.device)} at {address(pin.kind, pin.host, pin.port)} on first contact: "
            f"{describe(pin.key)}. Compare it with the device's own console if you want to be sure.")


def mismatch_message(pin: DevicePin, offered: DeviceKey) -> str:
    """Names the device and both fingerprints, says nothing was sent, and says what to do next."""
    device = _sentence_start(_the(pin.device))
    where = address(pin.kind, pin.host, pin.port)
    return (
        f"{device} at {where} presented a different {_what(pin.kind)} from the one "
        f"this run trusted. Trusted: {_presented(pin.key)}. Presented now: {_presented(offered)}. "
        f"The password was not sent. If the device was replaced or reset on purpose, {RETRUST_STEPS}. "
        "If nobody changed it, stop and ask the customer's network team."
    )


def unreadable_message(pin: DevicePin, offered: DeviceKey) -> str:
    """The run's stored key does not decode, so nothing could be compared and nothing was sent."""
    device = _the(pin.device)
    whose = "vCenter's" if device == "vCenter" else f"{device}'s"
    return (
        f"This run's record of {whose} {_what(pin.kind)} at {address(pin.kind, pin.host, pin.port)} cannot "
        f"be read, so it could not be compared with the one {device} presented now: {_presented(offered)}. "
        "Nothing was sent to the device, not even the password. Only a damaged run state can cause this. "
        f"To go on, {RETRUST_STEPS}."
    )


def refusal_message(pin: DevicePin, offered: DeviceKey) -> str:
    """Why a device was refused: the run's record of its key cannot be read, or it presented another."""
    return mismatch_message(pin, offered) if key_readable(pin.key) else unreadable_message(pin, offered)


def retrusted_message(pin: DevicePin) -> str:
    was = pin.previous.fingerprint if pin.previous else "none"
    return (f"Trusted the new {_what(pin.kind)} of {_the(pin.device)} at "
            f"{address(pin.kind, pin.host, pin.port)}, at the operator's request. "
            f"Was: {was}. Now: {pin.key.fingerprint}.")


def retrust(pin: DevicePin, fingerprint: str) -> DevicePin:
    """The pin after the operator accepts the key the device last presented. `fingerprint` is the one
    they compared; if the device has presented anything else since, the re-trust is refused."""
    if pin.refused is None:
        raise ValueError(f"{address(pin.kind, pin.host, pin.port)} has not presented a different "
                         f"{_what(pin.kind)}, so there is nothing to trust again.")
    if pin.refused.fingerprint != fingerprint.strip():
        raise ValueError("The device presented a different key since this page was loaded. Reload, compare "
                         "the fingerprint again, then trust it.")
    return pin.model_copy(update={
        "key": pin.refused, "previous": pin.key, "how": "retrusted", "trusted_at": datetime.now(UTC),
        "refused": None, "refused_at": None,
    })
