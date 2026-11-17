"""SPEC-027 R1/R2 — the Migration tab: parsed only when filled, one sentence per refused rule, compose
support, and the source password kept by the store but never shown. Back-compat: a workbook without the
tab parses exactly as before."""

import io
import json

import pytest
from openpyxl import load_workbook

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore, _provisioning_intent_json
from alletra_onboard.application.platform.init_sheet import (
    MIGRATION_HOST_COLUMNS,
    MIGRATION_SECTIONS,
    MIGRATION_SHEET_NAME,
    build_template_bytes,
    compose_workbook_bytes,
    parse_workbook_bytes,
)
from alletra_onboard.domain.models import RunMode

_INIT = {"serial_number": "CZ2D3209YV", "mgmt_ipv4": "10.64.154.190"}
_TARGETS = {
    "prov_array_host": "10.64.154.190", "prov_array_user": "3paradm", "prov_array_password": "pw",
    "prov_vcenter_host": "vc.example.net", "prov_vcenter_user": "administrator@vsphere.local", "prov_vcenter_password": "vpw",
}
_VOLUMES = [{"name": "zz_mig_vol01", "size_gib": "1", "vvset": "zz_mig_vvs"}]
_HOSTSETS = [{"name": "zz_mig_hs", "members": "esx1"}]
_SOURCE = {"source_host": "192.0.2.10", "source_user": "lab-reader", "source_password": "=src pw "}
_ROW = {"host": "lab-host-01", "cpg": "SSD_r6"}


def _sheet(*, fields=None, rows=None, volumes=None, hostsets=None, replication=None) -> bytes:
    """A workbook with the Initialisation and Provisioning tabs filled and the Migration tab as given."""
    migration = None if fields is None and rows is None else {"fields": fields or {}, "rows": rows}
    return compose_workbook_bytes(
        base=None, init=_INIT, targets=_TARGETS,
        volumes=_VOLUMES if volumes is None else volumes, hostsets=_HOSTSETS if hostsets is None else hostsets,
        replication=replication, migration=migration,
    )


def _parse(data: bytes):
    return parse_workbook_bytes(data, mode=RunMode.PROVISION_ONLY)


def _without_migration_tab(data: bytes) -> bytes:
    wb = load_workbook(io.BytesIO(data))
    del wb[MIGRATION_SHEET_NAME]
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def _with_secrets(intent) -> dict:
    """The intent as the store keeps it: model_dump masks every password, so compare them in the clear."""
    return json.loads(_provisioning_intent_json(intent))


# ------------------------------------------------------------------ template + back-compat

def test_the_template_has_the_migration_tab_and_the_initialisation_accelerator_does_not():
    wb = load_workbook(io.BytesIO(build_template_bytes()))
    assert MIGRATION_SHEET_NAME in wb.sheetnames
    texts = {str(c.value).strip().removesuffix("*").strip() for row in wb[MIGRATION_SHEET_NAME].iter_rows() for c in row if c.value}
    for _, fields in MIGRATION_SECTIONS:
        for _, label, _, _ in fields:
            assert label in texts
    for _, label, _ in MIGRATION_HOST_COLUMNS:
        assert label in texts
    assert MIGRATION_SHEET_NAME not in load_workbook(io.BytesIO(build_template_bytes(init_only=True))).sheetnames


@pytest.mark.parametrize("data", [
    pytest.param(lambda: _sheet(), id="provisioning"),
    pytest.param(lambda: _sheet(replication={"fields": {"peer_host": "10.64.122.99", "peer_user": "3paradm", "peer_password": "p"},
                                             "rows": [{"vvset": "zz_mig_vvs", "peer_cpg": "SSD_r6"}]}), id="replication"),
    pytest.param(lambda: _sheet(volumes=[], hostsets=[],
                                replication={"fields": {"peer_host": "10.64.122.99", "peer_user": "3paradm", "peer_password": "p"},
                                             "rows": [{"vvset": "existing_set", "peer_cpg": "SSD_r6"}]}), id="replicate-only"),
])
def test_a_workbook_from_before_the_tab_parses_unchanged(data):
    with_blank_tab = data()
    older = _without_migration_tab(with_blank_tab)
    before = _parse(older).provisioning_intent
    after = _parse(with_blank_tab).provisioning_intent
    assert before.migration is None and after.migration is None
    assert _with_secrets(before) == _with_secrets(after)


def test_an_onboarding_only_workbook_is_untouched():
    data = compose_workbook_bytes(base=build_template_bytes(init_only=True), init=_INIT)
    assert parse_workbook_bytes(data, mode=RunMode.VERIFY_ONLY).provisioning_intent is None


# ------------------------------------------------------------------ R1: the tab, parsed

def test_the_tab_parses_into_an_intent_with_defaults_filled():
    mig = _parse(_sheet(fields=_SOURCE, rows=[_ROW])).provisioning_intent.migration
    assert (mig.source.host, mig.source.username) == ("192.0.2.10", "lab-reader")
    assert mig.source.password.get_secret_value() == "=src pw "       # verbatim, '=' and spaces kept
    assert mig.orchestration == "array UI"
    [h] = mig.hosts
    assert (h.host, h.type, h.cpg, h.provisioning) == ("lab-host-01", "online", "SSD_r6", "thin")


def test_explicit_values_and_their_natural_spellings_are_honoured():
    rows = [
        {"host": "h1", "type": "Minimally-Disruptive", "cpg": "SSD_r6", "provisioning": "Reduce"},
        {"host": "h2", "type": "MDM", "cpg": "SSD_r6", "provisioning": "tpvv"},
        {"host": "h3", "type": "OFFLINE", "cpg": "FC_r6"},
    ]
    mig = _parse(_sheet(fields={**_SOURCE, "orchestration": "dscc"}, rows=rows)).provisioning_intent.migration
    assert mig.orchestration == "DSCC"
    assert [(h.host, h.type, h.cpg, h.provisioning) for h in mig.hosts] == [
        ("h1", "minimally disruptive", "SSD_r6", "reduce"),
        ("h2", "minimally disruptive", "SSD_r6", "thin"),
        ("h3", "offline", "FC_r6", "thin"),
    ]


def test_a_migration_only_workbook_may_leave_volumes_and_host_sets_empty():
    intent = _parse(_sheet(fields=_SOURCE, rows=[_ROW], volumes=[], hostsets=[])).provisioning_intent
    assert intent.volumes == [] and intent.host_sets == []
    assert [h.host for h in intent.migration.hosts] == ["lab-host-01"]
    with pytest.raises(ValueError, match="add at least one volume.*fill the Migration tab"):
        _parse(_sheet(volumes=[], hostsets=[]))


# ------------------------------------------------------------------ R1: one sentence per refusal

@pytest.mark.parametrize("fields, rows, expected", [
    ({k: v for k, v in _SOURCE.items() if k != "source_host"}, [_ROW],
     r"^Migration tab — enter the source array's management address \(the array the data moves from\)\.$"),
    ({k: v for k, v in _SOURCE.items() if k != "source_user"}, [_ROW],
     r"^Migration tab — enter a user for the source array; a read-only account is enough\.$"),
    ({k: v for k, v in _SOURCE.items() if k != "source_password"}, [_ROW],
     r"^Migration tab — enter the password of the source array's user\.$"),
    ({**_SOURCE, "orchestration": "the cloud"}, [_ROW],
     r"^Migration tab — 'Where the import runs' must be 'array UI' or 'DSCC' \(got 'the cloud'\)\.$"),
    (_SOURCE, [], r"^Migration tab — add at least one host to migrate: its name on the source array and a destination CPG\.$"),
    (_SOURCE, [_ROW, {**_ROW, "cpg": "FC_r6"}], r"^Migration tab — host 'lab-host-01' appears twice; one row per host\.$"),
    (_SOURCE, [{**_ROW, "type": "live"}],
     r"^Migration tab — host 'lab-host-01': Migration type must be online, minimally disruptive or offline \(got 'live'\)\.$"),
    (_SOURCE, [{**_ROW, "provisioning": "thick"}],
     r"^Migration tab — host 'lab-host-01': Provisioning must be thin or reduce \(got 'thick'\)\.$"),
    (_SOURCE, [{"host": "lab-host-01"}],
     r"^Migration tab — host 'lab-host-01': enter the destination CPG, the CPG on this array that receives its volumes\.$"),
    ({**_SOURCE, "source_host": "10.64.154.190"}, [_ROW],
     (r"^Migration tab — the source array \(10\.64\.154\.190\) is this run's own array\. This run's array is the destination: "
      r"enter the address of the array the data moves from\.$")),
])
def test_each_refusal_is_one_sentence(fields, rows, expected):
    with pytest.raises(ValueError, match=expected):
        _parse(_sheet(fields=fields, rows=rows))


# ------------------------------------------------------------------ R3: the Migration step needs the tab

@pytest.mark.parametrize("mode, steps", [(RunMode.MIGRATE, None), (RunMode.CUSTOM, ["migrate", "asbuilt"])])
def test_a_run_with_the_migration_step_needs_the_tab(mode, steps):
    with pytest.raises(ValueError, match=r"^The Migration step needs the 'Migration' tab \(the source array and the hosts "
                                         r"to migrate\), and this workbook has none filled in\.$"):
        parse_workbook_bytes(_sheet(), mode=mode, selected_steps=steps)
    intent = parse_workbook_bytes(_sheet(fields=_SOURCE, rows=[_ROW]), mode=mode, selected_steps=steps).provisioning_intent
    assert intent.migration.source.host == "192.0.2.10"


# ------------------------------------------------------------------ compose onto an older workbook

def test_compose_adds_the_tab_to_a_base_workbook_that_predates_it_and_replaces_rows():
    older = _without_migration_tab(_sheet())
    first = compose_workbook_bytes(base=older, migration={"fields": _SOURCE, "rows": [_ROW, {"host": "h2", "cpg": "SSD_r6"}]})
    second = compose_workbook_bytes(base=first, migration={"rows": [{"host": "h3", "cpg": "FC_r6", "type": "offline"}]})
    mig = _parse(second).provisioning_intent.migration
    assert mig.source.host == "192.0.2.10"                            # fields kept from the first compose
    assert [(h.host, h.type) for h in mig.hosts] == [("h3", "offline")]  # rows REPLACED, not appended


# ------------------------------------------------------------------ R2: the source password

def test_the_store_keeps_the_source_password_and_no_dump_shows_it(tmp_path):
    intent = _parse(_sheet(fields=_SOURCE, rows=[_ROW])).provisioning_intent
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    store.save_provisioning_intent("run1", intent)
    loaded = store.get_provisioning_intent("run1")
    assert loaded.migration.source.password.get_secret_value() == "=src pw "
    assert loaded.migration.hosts == intent.migration.hosts
    for shown in (loaded.model_dump_json(), str(loaded.model_dump()), repr(loaded), str(loaded.migration)):
        assert "=src pw " not in shown

    store.save_pending_sheet("tok", _parse(_sheet()).work_item, intent)
    _item, held = store.pop_pending_sheet("tok")
    assert held.migration.source.password.get_secret_value() == "=src pw "
