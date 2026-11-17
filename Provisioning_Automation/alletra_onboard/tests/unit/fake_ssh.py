"""An offline paramiko: the real `SSHClient.connect` (its host-key check is what ADR 0026 relies on), over a
fake transport that presents a key generated in the test and records each password it is given.

No socket is opened: `connect` gets a placeholder `sock` and a `transport_factory`, both of which
paramiko accepts for exactly this.
"""

from __future__ import annotations

from types import SimpleNamespace

import paramiko


class FakeTransport:
    """The part of paramiko.Transport that SSHClient.connect and its password login use."""

    gss_kex_used = False

    def __init__(self, host: str, server_key, logins: list) -> None:
        self.host, self.server_key, self.logins = host, server_key, logins
        self.gss_host = host
        self._options = SimpleNamespace(key_types=["ssh-ed25519", "ecdsa-sha2-nistp256", "ssh-rsa"])
        self.active = True

    def use_compression(self, compress=False) -> None:
        pass

    def set_gss_host(self, gss_host, trust_dns=True, gssapi_requested=True) -> None:
        self.gss_host = gss_host

    def get_security_options(self):
        return self._options

    def start_client(self, event=None, timeout=None) -> None:
        pass

    def get_remote_server_key(self):
        return self.server_key

    def auth_password(self, username, password, event=None, fallback=True):
        self.logins.append((self.host, username, password))
        return []

    def is_active(self) -> bool:
        return self.active

    def close(self) -> None:
        self.active = False


class OfflineSsh:
    """`devices[host]` is the key that host presents; `logins` lists every (host, user, password) sent."""

    def __init__(self) -> None:
        self.devices: dict[str, object] = {}
        self.logins: list[tuple[str, str, str]] = []

    def client_class(self):
        devices, logins = self.devices, self.logins

        class OfflineSSHClient(paramiko.SSHClient):
            def connect(self, hostname, port=22, **kwargs):
                key = devices[hostname]
                kwargs.update(sock=object(), transport_factory=lambda sock, **_: FakeTransport(hostname, key, logins))
                return super().connect(hostname, port=port, **kwargs)

        return OfflineSSHClient


def install(monkeypatch) -> OfflineSsh:
    offline = OfflineSsh()
    monkeypatch.setattr(paramiko, "SSHClient", offline.client_class())
    return offline


def new_key():
    return paramiko.ECDSAKey.generate()
