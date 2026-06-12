from alletra_onboard.adapters.greenlake.devices import (
    apply_subscription_payload,
    assign_application_payload,
    storage_device_payload,
)


def test_storage_device_payload_uses_v2beta1_flat_schema():
    payload = storage_device_payload("SGHD44LQLS", "S0B84A")
    assert payload == {"serialNumber": "SGHD44LQLS", "deviceType": "STORAGE", "partNumber": "S0B84A"}


def test_storage_device_payload_includes_tags_only_when_present():
    assert "tags" not in storage_device_payload("SGHD44LQLS", "S0B84A")
    assert storage_device_payload("SGHD44LQLS", "S0B84A", {"site": "lab"})["tags"] == {"site": "lab"}


def test_assignment_payload_does_not_include_subscription():
    payload = assign_application_payload("svc", "ap-northeast")
    assert payload == {"application": {"id": "svc"}, "region": "ap-northeast"}
    assert "subscription" not in payload


def test_subscription_payload_does_not_include_application():
    payload = apply_subscription_payload("sub")
    assert payload == {"subscription": [{"id": "sub"}]}
    assert "application" not in payload
