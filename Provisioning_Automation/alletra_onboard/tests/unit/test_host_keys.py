"""ADR 0026 — SSH host keys are trusted on first contact and pinned for the run. Every SSH client goes
through `device_trust.open_ssh`; paramiko's own host-key check runs, over an offline transport."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters import device_trust
from alletra_onboard.adapters.array.cli_client import ArrayCliClient, ArrayCliError
from alletra_onboard.adapters.array.rc_cli_client import ArrayRcCliClient, RcPlanObjects
from alletra_onboard.adapters.fabric.brocade_client import BrocadeClient, BrocadeError
from alletra_onboard.adapters.hosts.linux_ssh import LinuxHostClient, LinuxHostError
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.documents.verification import verify
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig
from alletra_onboard.domain.trust import DevicePin, TrustKind
from tests.unit import fake_ssh

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


@pytest.fixture
def ssh(monkeypatch):
    return fake_ssh.install(monkeypatch)


@pytest.fixture
def book():
    b = _Book()
    token = device_trust.bind(b)
    yield b
    device_trust.unbind(token)


def _connect(client) -> None:
    client.connect()
    client.close()


def test_the_array_key_is_trusted_on_first_contact_and_the_password_goes_after_it(ssh, book):
    key = fake_ssh.new_key()
    ssh.devices["10.0.0.5"] = key
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    pin = book.pins[(TrustKind.SSH, "10.0.0.5", 22)]
    assert (pin.device, pin.key.key_type, pin.key.fingerprint) == ("array", key.get_name(), key.fingerprint)
    assert pin.key.data == key.get_base64()          # the key itself: paramiko needs it to compare
    assert ssh.logins == [("10.0.0.5", "3paradm", PW)]


def test_the_same_key_on_a_later_connection_is_compared_by_paramiko_and_accepted(ssh, book):
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    assert len(ssh.logins) == 2 and book.refused == []


def test_a_different_key_stops_the_connection_before_the_password_is_sent(ssh, book):
    old, new = fake_ssh.new_key(), fake_ssh.new_key()
    ssh.devices["10.0.0.5"] = old
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    ssh.devices["10.0.0.5"] = new
    with pytest.raises(ArrayCliError) as caught:
        ArrayCliClient("10.0.0.5", "3paradm", PW).connect()
    text = str(caught.value)
    assert text.startswith("The array at 10.0.0.5 presented a different SSH host key")
    assert old.fingerprint in text and new.fingerprint in text and "The password was not sent." in text
    assert ssh.logins == [("10.0.0.5", "3paradm", PW)]       # only the first, trusted, login
    [(pin, offered)] = book.refused
    assert (pin.key.fingerprint, offered.fingerprint) == (old.fingerprint, new.fingerprint)


def test_a_different_key_type_is_a_different_key(ssh, book):
    import paramiko

    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    ssh.devices["10.0.0.5"] = paramiko.RSAKey.generate(1024)
    with pytest.raises(ArrayCliError, match="presented a different SSH host key"):
        ArrayCliClient("10.0.0.5", "3paradm", PW).connect()
    assert len(ssh.logins) == 1


def test_a_port_other_than_22_is_pinned_under_its_own_name(ssh, book):
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW, port=2222))
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW, port=2222))
    assert list(book.pins) == [(TrustKind.SSH, "10.0.0.5", 2222)] and book.refused == []


def test_the_remote_copy_write_client_connects_like_the_read_client(ssh, book):
    ssh.devices["10.0.0.6"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.6", "3paradm", PW))
    ssh.devices["10.0.0.6"] = fake_ssh.new_key()
    with pytest.raises(ArrayCliError, match="presented a different SSH host key"):
        ArrayRcCliClient("10.0.0.6", "3paradm", PW, objects=RcPlanObjects()).connect()
    assert len(ssh.logins) == 1


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y", part_number="S0B84A", subscription_key="KEY123",
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.0.0.5", mask="255.255.255.0", gateway="10.0.0.1",
                              dns=["10.0.0.2"], ntp="ntp.example.com", timezone="UTC"),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India", password=SecretStr(PW)),
    )


def test_verification_builds_its_own_client_and_still_gets_the_run_pins(ssh, book):
    item = _item()
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    report = verify(item, "3paradm", PW)
    assert not report.reachable and "presented a different SSH host key" in (report.error or "")
    assert len(ssh.logins) == 1


def test_with_no_run_bound_the_client_connects_as_before(ssh):
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    _connect(ArrayCliClient("10.0.0.5", "3paradm", PW))     # nothing kept between clients without a run
    assert len(ssh.logins) == 2


async def test_the_console_reads_with_the_run_pins_and_a_refusal_is_on_the_run(ssh, tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    service = OnboardingService(Settings(), store, InMemoryEventBus())
    run = service.create_run(_item())
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    await service.console.run(run.run_id, "showsys")          # first contact (the fake runs no command)
    [pin] = service.trusted_devices(run.run_id)
    ssh.devices["10.0.0.5"] = fake_ssh.new_key()
    answer = await service.console.run(run.run_id, "showsys")
    assert not answer["ok"] and "presented a different SSH host key" in answer["output"]
    assert len(ssh.logins) == 1
    # the console answered with the refusal; the run notes it without marking a step stopped
    assert service.list_events(run.run_id)[-1].event_type == "device.refused"
    assert service.trusted_devices(run.run_id)[0].refused_fingerprint not in (None, pin.fingerprint)


def test_an_old_switch_ssh_rsa_key_pins_like_any_other(ssh, book):
    import paramiko

    key = paramiko.RSAKey.generate(1024)     # old FOS offers only ssh-rsa (LESSONS 43)
    ssh.devices["10.0.1.2"] = key
    _connect(BrocadeClient("10.0.1.2", "admin", PW))
    _connect(BrocadeClient("10.0.1.2", "admin", PW))
    pin = book.pins[(TrustKind.SSH, "10.0.1.2", 22)]
    assert (pin.device, pin.key.key_type, pin.key.fingerprint) == ("switch", "ssh-rsa", key.fingerprint)
    ssh.devices["10.0.1.2"] = paramiko.RSAKey.generate(1024)
    with pytest.raises(BrocadeError) as caught:
        BrocadeClient("10.0.1.2", "admin", PW).connect()
    assert str(caught.value).startswith("The switch at 10.0.1.2 presented a different SSH host key")
    assert len(ssh.logins) == 2


def test_a_linux_host_key_change_stops_before_the_password(ssh, book):
    ssh.devices["10.0.2.7"] = fake_ssh.new_key()
    _connect(LinuxHostClient("10.0.2.7", "root", PW))
    ssh.devices["10.0.2.7"] = fake_ssh.new_key()
    with pytest.raises(LinuxHostError) as caught:
        LinuxHostClient("10.0.2.7", "root", PW).connect()
    assert str(caught.value).startswith("The Linux host at 10.0.2.7 presented a different SSH host key")
    assert "The password was not sent." in str(caught.value)
    assert ssh.logins == [("10.0.2.7", "root", PW)]
