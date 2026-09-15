"""SPEC-008 R1/R2 — one array credential per run (ADR 0013).

The run resolves its array credential from the sheet: the Provisioning tab's array admin, else the
DSCC system credential, else none. Verify and As-built use it unless the request overrides it; with
neither, the step refuses with a sentence the UI shows. The password never reaches an event."""

import asyncio
import json

import pytest
from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.documents.steps import DocumentSteps
from alletra_onboard.application.runs.coordinator import RunCoordinator, StepPreconditionError
from alletra_onboard.application.runs.event_bus import InMemoryEventBus
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import (
    ArrayWorkItem,
    DsccSetupConfig,
    NetworkConfig,
    RunMode,
    VerificationReport,
)
from alletra_onboard.domain.provisioning import ProvisioningIntent, VolumeRequest
from alletra_onboard.domain.shared import EndpointCreds


def _item(dscc_password: str | None = None) -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y", part_number="S0B84A", subscription_key=SecretStr("K"),
        service_catalog_region_id="ap-northeast", dscc_region_code="jp1",
        cloudinit_url="https://169.254.239.27/cloudinit",
        network=NetworkConfig(mgmt_ipv4="10.132.30.121", mask="255.255.248.0", gateway="10.132.30.1",
                              dns=["10.203.96.10"], ntp="ntp.example.com", timezone="Asia/Kolkata"),
        dscc_setup=DsccSetupConfig(system_name="rack13arcus", country="India",
                                   password=SecretStr(dscc_password) if dscc_password else None),
    )


def _intent(host="10.132.30.121", user="3paradm", password="sheet-pw") -> ProvisioningIntent:
    creds = lambda h, u, p: EndpointCreds(host=h, username=u, password=SecretStr(p))  # noqa: E731
    return ProvisioningIntent(
        array=creds(host, user, password), vcenter=creds("vc", "a", "b"),
        switch_f1=creds("f1", "a", "b"), switch_f2=creds("f2", "a", "b"),
        volumes=[VolumeRequest(name="vol01", size_gib=1)],
    )


def _coord(tmp_path) -> RunCoordinator:
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    return RunCoordinator(Settings(), store, InMemoryEventBus())


# ------------------------------------------------------------------ R1: resolution

def test_provisioning_tab_credential_wins(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(dscc_password="setup-pw"), mode=RunMode.PROVISION_ONLY,
                           provisioning_intent=_intent(user="storageadmin", password="sheet-pw"))
    cred = coord.array_credential(run.run_id)
    assert cred.available and cred.source == "provisioning"
    assert cred.username == "storageadmin" and cred.host == "10.132.30.121"
    assert cred.secret.get_secret_value() == "sheet-pw"
    # the public view never carries the secret
    assert "secret" not in cred.public().model_dump() and "password" not in json.dumps(cred.public().model_dump())


def test_dscc_system_credential_when_no_provisioning_tab(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(dscc_password="setup-pw"))
    cred = coord.array_credential(run.run_id)
    assert cred.available and cred.source == "dscc_setup"
    assert cred.username == "3paradm" and cred.secret.get_secret_value() == "setup-pw" and cred.host == "10.132.30.121"


def test_no_credential_when_the_sheet_gave_none(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(), mode=RunMode.VERIFY_ONLY)
    cred = coord.array_credential(run.run_id)
    assert not cred.available and cred.source == "none" and cred.secret is None


# ------------------------------------------------------------------ R2: the steps use it

def _verify_with(coord, run_id, *, username=None, password=None):
    seen: list[tuple[str, str]] = []

    def fake_verify(item, u, p):
        seen.append((u, p))
        return VerificationReport(reachable=True)

    steps = DocumentSteps(coord, verify_fn=fake_verify)
    coro = steps._run_verify(coord.get_run(run_id), coord.get_work_item(run_id),
                             *steps.resolve_credential(run_id, username, password))
    asyncio.run(coro)
    return seen


def test_verify_uses_the_runs_credential_by_default(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(), mode=RunMode.PROVISION_ONLY, provisioning_intent=_intent())
    assert _verify_with(coord, run.run_id) == [("3paradm", "sheet-pw")]
    # and the credential is in no event
    for ev in coord.list_events(run.run_id):
        assert "sheet-pw" not in json.dumps(ev.model_dump(mode="json"))


def test_an_explicit_credential_overrides_the_runs(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(), mode=RunMode.PROVISION_ONLY, provisioning_intent=_intent())
    assert _verify_with(coord, run.run_id, username="other", password="rotated") == [("other", "rotated")]


def test_no_credential_anywhere_is_a_precondition_error_with_the_operator_sentence(tmp_path):
    coord = _coord(tmp_path)
    run = coord.create_run(_item(), mode=RunMode.VERIFY_ONLY)
    steps = DocumentSteps(coord, verify_fn=lambda *a: VerificationReport(reachable=True))
    with pytest.raises(StepPreconditionError) as exc:
        steps.resolve_credential(run.run_id, None, None)
    assert "holds no array credential" in str(exc.value)
    # a username without a password is not a credential either
    with pytest.raises(StepPreconditionError):
        steps.resolve_credential(run.run_id, "3paradm", None)
