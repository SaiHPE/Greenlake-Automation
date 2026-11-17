"""Self-signed certificates made in the test, standing in for what an array or vCenter presents. Nothing
here opens a connection: tests replace `device_trust.probe_tls` with `install(...)`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from alletra_onboard.adapters import device_trust


def self_signed_der(common_name: str = "array") -> bytes:
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(UTC)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1)).sign(key, hashes.SHA256()))
    return cert.public_bytes(serialization.Encoding.DER)


class Certificates:
    """`devices[(host, port)]` is the certificate (DER) the device presents; `probes` counts the reads."""

    def __init__(self) -> None:
        self.devices: dict[tuple[str, int], bytes] = {}
        self.probes: list[tuple[str, int]] = []

    def probe(self, host: str, port: int, timeout: float) -> bytes:
        self.probes.append((host, port))
        return self.devices[(host, port)]


def install(monkeypatch) -> Certificates:
    certs = Certificates()
    monkeypatch.setattr(device_trust, "probe_tls", certs.probe)
    return certs
