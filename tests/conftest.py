import ipaddress
import socket

import pytest

from alletra_onboard.config import Settings


def _stays_on_this_machine(address) -> bool:
    """True for a unix socket path and for a loopback address; a host name would be looked up and dialled."""
    if not isinstance(address, tuple):
        return True
    host = address[0].decode("ascii", "replace") if isinstance(address[0], bytes) else str(address[0])
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host.split("%")[0]).is_loopback
    except ValueError:
        return False


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """STANDARD X1: a test opens no connection that leaves this machine and looks up no host name.
    The attempt raises where it is made, and the test fails at the end even when the code under test
    caught that error."""
    attempts: list[str] = []

    def guard(real):
        def guarded(sock, *args, **kwargs):
            address = args[-1] if args else None
            if sock.family != getattr(socket, "AF_UNIX", None) and not _stays_on_this_machine(address):
                attempts.append(f"{real.__name__} {address!r}")
                raise RuntimeError(f"STANDARD X1: a test tried to reach {address!r} over the network. Tests use "
                                   f"fakes and captured output: hand the code a fake client, or patch the call "
                                   f"that dials.")
            return real(sock, *args, **kwargs)
        return guarded

    for name in ("connect", "connect_ex", "sendto"):
        monkeypatch.setattr(socket.socket, name, guard(getattr(socket.socket, name)))

    real_lookup = socket.getaddrinfo

    def lookup(host, *args, **kwargs):
        name = host.decode("ascii", "replace") if isinstance(host, bytes) else host
        if name and name != "localhost":
            try:
                ipaddress.ip_address(str(name).split("%")[0])
            except ValueError:
                attempts.append(f"name lookup {name!r}")
                raise RuntimeError(f"STANDARD X1: a test tried to look up {name!r} on the network. Tests use "
                                   f"fakes and captured output: hand the code a fake client, or patch the call "
                                   f"that dials.") from None
        return real_lookup(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", lookup)
    yield
    if attempts:
        pytest.fail("STANDARD X1: this test tried to reach the network (" + "; ".join(attempts) + "). Tests use "
                    "fakes and captured output: hand the code a fake client, or patch the call that dials.",
                    pytrace=False)


@pytest.fixture(autouse=True)
def _run_in_a_scratch_folder(tmp_path, monkeypatch):
    """Every test runs in its own empty folder. The app writes `.env` (the sheet's GreenLake
    credentials) and its state folder relative to the working directory, so a test must never run
    in the app folder: it would overwrite the developer's real `.env`."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def _isolate_settings_from_dotenv(monkeypatch):
    """Keep unit tests deterministic regardless of a local operator .env.

    The CLI reads GreenLake credentials from a .env in the working directory. That file
    must not leak into tests that assert on missing/explicit credentials, so disable
    .env loading and clear any GL_* process env for the duration of each test.
    """
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    for key in (
        "GL_CLIENT_ID",
        "GL_CLIENT_SECRET",
        "GL_MEMBER_WORKSPACE_ID",
        "GL_TOKEN_URL",
        "GL_BASE_URL",
        "ALLETRA_DEVICE_CA_BUNDLE",
    ):
        monkeypatch.delenv(key, raising=False)
