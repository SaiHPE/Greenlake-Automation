"""GreenLake registration must not look hung while it is working.

MEASURED live on a jump box (array CZ2D2K014S, 2026-08-17): the device add SUCCEEDED — GreenLake
inventory showed it registered AND ASSIGNED_TO_SERVICE — but the async-operation resource never
reported a terminal status. The step sat in poll_async emitting nothing, so the UI showed "Running"
with no new line for minutes and the operator had to query the API by hand to discover the work had
already completed. These tests pin both halves of the fix: every poll reports, and the real end
state ends the wait.
"""

from __future__ import annotations

from pydantic import SecretStr

from alletra_onboard.adapters.greenlake.service_catalog import ServiceProvision
from alletra_onboard.application.onboarding.greenlake_provision import GreenLakeProvisioningService
from alletra_onboard.domain.models import ArrayWorkItem, DsccSetupConfig, NetworkConfig, WorkflowPhase

DEVICE_ID = "e7986853-a980-5a82-90a5-9240b42ec07f"
SERIAL = "CZ2D2K014S"


def _item() -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number=SERIAL,
        part_number="S0B84A",
        subscription_key=SecretStr("key-1"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(
            mgmt_ipv4="10.64.122.140", mask="255.255.255.0", gateway="10.64.122.1",
            dns=["10.0.0.10"], ntp="ntp.example.com", timezone="Asia/Kolkata",
        ),
        dscc_setup=DsccSetupConfig(system_name="array01", country="India", password="env:PW"),
    )


class NeverSettlingHttp:
    """The live failure: the operation resource stays non-terminal forever."""

    def __init__(self) -> None:
        self.polls = 0

    async def poll_async(self, location, *, bucket="device_async_poll", on_progress=None,
                         settled=None, **kwargs):
        while True:
            self.polls += 1
            if settled is not None and await settled():
                return {"status": "SETTLED_BY_STATE"}
            if on_progress is not None:
                on_progress("PENDING", float(self.polls))
            if self.polls > 50:                     # the real client would raise TimeoutError here
                raise AssertionError("poll never ended - settled() was not honoured")

    async def request(self, *a, **k):
        raise AssertionError("not used")


class Devices:
    """Inventory that lags the add by a couple of reads, then reflects it — while the operation
    resource never settles. That lag is the window in which the step must SAY it is waiting."""

    INVENTORY_LAG = 2

    def __init__(self) -> None:
        self.registered = False
        self.assigned = False
        self._lag = 0

    async def add_storage_device(self, serial, part_number, tags=None, dry_run=False):
        self.registered = True                       # the work is accepted...
        self._lag = self.INVENTORY_LAG               # ...but is not queryable for a moment
        return "https://api/devices/v1/async-operations/op-1"   # ...and the op never settles

    async def find_by_serial(self, serial):
        if not self.registered:
            return None
        if self._lag > 0:
            self._lag -= 1
            return None
        return {"id": DEVICE_ID}

    async def get(self, device_id):
        return {
            "id": DEVICE_ID,
            "assignedState": "ASSIGNED_TO_SERVICE" if self.assigned else "UNASSIGNED",
            "application": {"id": "svc-1"} if self.assigned else {},
            "region": "ap-northeast" if self.assigned else "",
            "subscription": [],
        }

    async def assign_application(self, device_id, service_manager_id, region):
        self.assigned = True
        return "https://api/devices/v1/async-operations/op-2"

    async def apply_subscription(self, device_id, subscription_id):
        return None


class Subscriptions:
    async def add_subscription(self, key):
        return None

    async def find_by_key(self, key):
        return {"id": "sub-1", "availableQuantity": 1}


class Catalog:
    async def service_manager_provisions(self, region):
        return [ServiceProvision(service_manager_id="svc-1", region="ap-northeast",
                                 provision_status="PROVISIONED")]


def _service(events: list[tuple[WorkflowPhase, str]]):
    return GreenLakeProvisioningService(
        http=NeverSettlingHttp(),
        devices=Devices(),
        subscriptions=Subscriptions(),
        service_catalog=Catalog(),
        progress=lambda phase, message: events.append((phase, message)),
        device_state_timeout=0.0,
    )


async def test_registration_completes_despite_a_never_settling_operation():
    events: list[tuple[WorkflowPhase, str]] = []
    result = await _service(events).provision(_item())

    assert result.error is None, result.error
    assert result.device_id == DEVICE_ID
    assert result.assigned_state == "ASSIGNED_TO_SERVICE"
    assert result.succeeded


async def test_every_wait_reports_progress():
    """The operator must be able to tell a working step from a hung one, from the UI alone."""
    events: list[tuple[WorkflowPhase, str]] = []
    await _service(events).provision(_item())
    messages = [m for _, m in events]

    waiting = [m for m in messages if m.startswith("waiting for")]
    assert waiting, f"no progress emitted while polling; got {messages}"
    assert any(SERIAL in m for m in waiting)          # names WHAT it is waiting for
    assert any("(" in m and "s)" in m for m in waiting)   # and for HOW LONG


async def test_the_settled_check_is_what_ends_the_wait():
    """Not a timeout, not luck: the inventory read is what releases the poll."""
    events: list[tuple[WorkflowPhase, str]] = []
    service = _service(events)
    result = await service.provision(_item())

    assert result.succeeded
    assert service.http.polls > 0                     # it really did poll a non-terminal operation
