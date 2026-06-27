from pydantic import SecretStr

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.domain.storage import (
    EndpointCreds,
    ProvisioningIntent,
    VolumeSpec,
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


def test_volume_spec_names():
    assert VolumeSpec(name_prefix="V", size_gib=10).names() == ["V"]
    assert VolumeSpec(name_prefix="CRV_Prod", size_gib=10, count=3).names() == [
        "CRV_Prod01", "CRV_Prod02", "CRV_Prod03",
    ]


def _creds(host: str) -> EndpointCreds:
    return EndpointCreds(host=host, username="u", password=SecretStr("pw-" + host))


def _intent() -> ProvisioningIntent:
    creds = _creds
    return ProvisioningIntent(
        host_set_name="HS",
        array=creds("10.0.0.5"),
        vcenter=creds("vc"),
        switch_f1=creds("sw1"),
        switch_f2=creds("sw2"),
        volume=VolumeSpec(name_prefix="V", size_gib=100, count=2),
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
    assert loaded.volume.names() == ["V01", "V02"]
    assert store.get_provisioning_intent("missing") is None
