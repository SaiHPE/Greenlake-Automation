"""ADR 0026 — trust on first contact: the pin store, the one helper that records, compares and refuses,
the run binding, and the re-trust action. Fakes only; nothing connects anywhere."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from alletra_onboard.adapters import device_trust
from alletra_onboard.adapters.device_trust import DeviceTrustError
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.api.app import create_app
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.application.service import OnboardingService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    WorkflowPhase,
)
from alletra_onboard.domain.trust import DeviceKey, DevicePin, TrustKind

KEY_A = DeviceKey(kind=TrustKind.SSH, key_type="ssh-ed25519", data="AAAAC3NzaC1lZDI1NTE5AAAAIA==",
                  fingerprint="SHA256:firstkeyfirstkeyfirstkeyfirstkeyfirstkey0")
KEY_B = DeviceKey(kind=TrustKind.SSH, key_type="ssh-rsa", data="AAAAB3NzaC1yc2EAAAADAQAB",
                  fingerprint="SHA256:otherkeyotherkeyotherkeyotherkeyotherkey0")


class _Book:
    """The TrustBook contract in memory, for the helper alone."""

    device_ca_bundle = None

    def __init__(self) -> None:
        self.pins: dict[tuple, DevicePin] = {}
        self.refused: list[tuple[DevicePin, DeviceKey]] = []

    def pin(self, kind, host, port):
        return self.pins.get((kind, host, port))

    def first_contact(self, pin):
        return self.pins.setdefault((pin.kind, pin.host, pin.port), pin)

    def refuse(self, pin, offered):
        self.refused.append((pin, offered))


@pytest.fixture
def book():
    b = _Book()
    token = device_trust.bind(b)
    yield b
    device_trust.unbind(token)


def _service(tmp_path) -> OnboardingService:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    return OnboardingService(Settings(), store, InMemoryEventBus())


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y", part_number="S0B84A", subscription_key="KEY123",
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.0.0.5", mask="255.255.255.0", gateway="10.0.0.1",
                              dns=["10.0.0.2"], ntp="ntp.example.com", timezone="UTC"),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India"),
    )


# ------------------------------------------------------------------ the helper: record, compare, refuse

def test_with_no_run_bound_nothing_is_compared_or_recorded():
    assert device_trust.current() is None
    assert device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A) is KEY_A


def test_first_contact_records_the_key(book):
    assert device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A).same_as(KEY_A)
    pin = book.pins[(TrustKind.SSH, "10.0.0.5", 22)]
    assert (pin.device, pin.key.fingerprint, pin.how) == ("array", KEY_A.fingerprint, "first_contact")


def test_the_same_key_goes_through_and_nothing_is_refused(book):
    device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A)
    device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A.model_copy())
    assert book.refused == []


def test_a_different_key_is_refused_naming_the_device_and_both_fingerprints(book):
    device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A)
    with pytest.raises(DeviceTrustError) as caught:
        device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_B)
    text = str(caught.value)
    assert text.startswith("The array at 10.0.0.5 presented a different SSH host key from the one this run trusted.")
    assert KEY_A.fingerprint in text and KEY_B.fingerprint in text
    assert "The password was not sent." in text and "Trusted devices" in text
    [(pin, offered)] = book.refused
    assert pin.key.same_as(KEY_A) and offered.same_as(KEY_B)


def test_pins_are_per_address_port_and_kind(book):
    device_trust.check(TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A)
    device_trust.check(TrustKind.SSH, "10.0.0.5", 2222, "array", KEY_B)    # another port: its own first contact
    device_trust.check(TrustKind.SSH, "10.0.0.6", 22, "array", KEY_B)      # the peer
    assert len(book.pins) == 3 and book.refused == []


# ------------------------------------------------------------------ the pin store

def test_the_store_keeps_the_first_pin_when_two_contacts_race(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    first = DevicePin(kind=TrustKind.SSH, host="10.0.0.5", port=22, device="array", key=KEY_A)
    assert store.add_device_pin("run-1", first) == first
    assert store.add_device_pin("run-1", first.model_copy(update={"key": KEY_B})) == first
    assert store.get_device_pin("run-1", TrustKind.SSH, "10.0.0.5", 22) == first
    assert store.get_device_pin("run-2", TrustKind.SSH, "10.0.0.5", 22) is None   # a new run starts empty
    assert store.list_device_pins("run-1") == [first]


# ------------------------------------------------------------------ the run binding

async def test_a_step_records_first_contact_as_a_run_event(tmp_path):
    service = _service(tmp_path)
    run = service.create_run(_item())
    coord = service.coordinator

    async def step():
        coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "step.started", "Verifying…")
        await asyncio.to_thread(device_trust.check, TrustKind.SSH, "10.0.0.5", 22, "array", KEY_A)
        coord.emit(run.run_id, WorkflowPhase.CONFIG_VERIFY, "verify.completed", "Verified")

    coord.spawn(run.run_id, step())
    await coord.wait(run.run_id)
    await asyncio.sleep(0)   # the worker thread's event is handed to the loop
    [pin] = service.trusted_devices(run.run_id)
    assert (pin.host, pin.fingerprint, pin.how) == ("10.0.0.5", KEY_A.fingerprint, "first_contact")
    trusted = [e for e in service.list_events(run.run_id) if e.event_type == "device.trusted"]
    assert len(trusted) == 1 and trusted[0].phase == WorkflowPhase.CONFIG_VERIFY
    assert KEY_A.fingerprint in trusted[0].message and "on first contact" in trusted[0].message
    assert device_trust.current() is None   # bound for the step only


async def test_a_refusal_blocks_the_step_even_when_the_step_carried_on(tmp_path):
    service = _service(tmp_path)
    run = service.create_run(_item())
    coord = service.coordinator
    coord.store.add_device_pin(run.run_id, DevicePin(kind=TrustKind.SSH, host="10.0.0.9", port=22,
                                                     device="Linux host", key=KEY_A))

    async def step():   # like discovery: one host's failure becomes a note and the step completes
        coord.emit(run.run_id, WorkflowPhase.STORAGE_DISCOVER, "discover.started", "Discovering…")
        try:
            await asyncio.to_thread(device_trust.check, TrustKind.SSH, "10.0.0.9", 22, "Linux host", KEY_B)
        except DeviceTrustError:
            pass
        coord.emit(run.run_id, WorkflowPhase.STORAGE_DISCOVER, "discover.completed", "Discovered")

    coord.spawn(run.run_id, step())
    await coord.wait(run.run_id)
    last = service.list_events(run.run_id)[-1]
    assert (last.event_type, last.phase) == ("device.trust_failed", WorkflowPhase.STORAGE_DISCOVER)
    assert "The Linux host at 10.0.0.9" in last.message and KEY_B.fingerprint in last.message
    [pin] = service.trusted_devices(run.run_id)
    assert (pin.fingerprint, pin.refused_fingerprint) == (KEY_A.fingerprint, KEY_B.fingerprint)


# ------------------------------------------------------------------ the re-trust action (API)

def test_the_run_lists_its_devices_and_retrust_is_a_separate_logged_action(tmp_path):
    service = _service(tmp_path)
    run = service.create_run(_item())
    client = TestClient(create_app(service))
    base = f"/runs/{run.run_id}/trust"
    body = {"kind": "ssh", "host": "10.0.0.5", "port": 22, "fingerprint": KEY_B.fingerprint}

    assert client.get(base).json() == {"devices": [], "device_ca_bundle": None}
    assert client.post(f"{base}/retrust", json=body).status_code == 404       # never reached

    pin = DevicePin(kind=TrustKind.SSH, host="10.0.0.5", port=22, device="array", key=KEY_A)
    service.coordinator.store.add_device_pin(run.run_id, pin)
    nothing = client.post(f"{base}/retrust", json=body)
    assert nothing.status_code == 409 and "nothing to trust again" in nothing.json()["detail"]

    service.coordinator.store.save_device_pin(run.run_id, pin.model_copy(update={"refused": KEY_B}))
    [listed] = client.get(base).json()["devices"]
    assert (listed["fingerprint"], listed["refused_fingerprint"]) == (KEY_A.fingerprint, KEY_B.fingerprint)
    assert "data" not in listed   # fingerprints only

    stale = client.post(f"{base}/retrust", json=dict(body, fingerprint="SHA256:somethingelse"))
    assert stale.status_code == 409 and "compare the fingerprint again" in stale.json()["detail"]

    done = client.post(f"{base}/retrust", json=body)
    assert done.status_code == 200
    device = done.json()["device"]
    assert (device["fingerprint"], device["how"], device["previous_fingerprint"], device["refused_fingerprint"]) == (
        KEY_B.fingerprint, "retrusted", KEY_A.fingerprint, None)
    [event] = [e for e in service.list_events(run.run_id) if e.event_type == "device.retrusted"]
    assert (event.data["was"], event.data["now"]) == (KEY_A.fingerprint, KEY_B.fingerprint)
    assert KEY_A.fingerprint in event.message and KEY_B.fingerprint in event.message
