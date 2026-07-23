from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.domain.storage import (
    EndpointCreds,
    ProvisioningIntent,
    normalize_wwpn,
    wwpn_colons,
)


def test_normalize_wwpn_strips_separators_and_uppercases():
    # ESXi colon/lowercase and array no-colon/uppercase normalize to the same canonical form.
    assert normalize_wwpn("10:00:5c:ed:a1:b2:c3:d4") == "10005CEDA1B2C3D4"
    assert normalize_wwpn("10005ceda1b2c3d4") == "10005CEDA1B2C3D4"
    assert normalize_wwpn("20:31:00:02:ac:02:b8:8e") == "20310002AC02B88E"


def test_wwpn_colons_round_trips():
    assert wwpn_colons("20310002AC02B88E") == "20:31:00:02:ac:02:b8:8e"


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("pw-" + host))


def test_from_simple_expands_prefix_count_into_heterogeneous_volumes():
    single = ProvisioningIntent.from_simple(
        array=_creds("a"), vcenter=_creds("v"), switch_f1=_creds("f1"), switch_f2=_creds("f2"),
        host_set_name="HS", name_prefix="V", size_gib=10,
    )
    assert [v.name for v in single.volumes] == ["V"]
    assert single.host_sets[0].name == "HS" and single.host_sets[0].members == []  # empty => all hosts

    many = ProvisioningIntent.from_simple(
        array=_creds("a"), vcenter=_creds("v"), switch_f1=_creds("f1"), switch_f2=_creds("f2"),
        host_set_name="HS", name_prefix="CRV_Prod", size_gib=10, count=3, provisioning_type="reduce",
    )
    assert [v.name for v in many.volumes] == ["CRV_Prod01", "CRV_Prod02", "CRV_Prod03"]
    assert all(v.provisioning_type == "reduce" and v.size_mib == 10240 for v in many.volumes)


def _intent() -> ProvisioningIntent:
    return ProvisioningIntent.from_simple(
        host_set_name="HS",
        array=_creds("10.0.0.5"),
        vcenter=_creds("vc"),
        switch_f1=_creds("sw1"),
        switch_f2=_creds("sw2"),
        name_prefix="V", size_gib=100, count=2,
    )


def test_provisioning_intent_persists_with_secrets(tmp_path):
    store = SqliteRunStore(tmp_path / "state.db")
    store.initialize()
    store.save_provisioning_intent("run1", _intent())

    loaded = store.get_provisioning_intent("run1")
    assert loaded is not None
    # passwords must survive the round-trip (model_dump_json would mask them to '**********')
    assert loaded.array.password.get_secret_value() == "pw-10.0.0.5"
    assert loaded.switch_f2.password.get_secret_value() == "pw-sw2"
    assert [v.name for v in loaded.volumes] == ["V01", "V02"]
    assert store.get_provisioning_intent("missing") is None
