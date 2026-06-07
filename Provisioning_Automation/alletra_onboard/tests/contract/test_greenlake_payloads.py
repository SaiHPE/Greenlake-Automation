from alletra_onboard.adapters.greenlake.devices import (
    apply_subscription_payload,
    assign_application_payload,
    storage_device_payload,
)


def test_storage_device_payload_uses_serial_and_part_number():
    payload = storage_device_payload("SGHD44LQLS", "S0B84A")
    assert payload == {"storage": [{"serialNumber": "SGHD44LQLS", "partNumber": "S0B84A", "tags": {}}]}


def test_assignment_payload_does_not_include_subscription():
    payload = assign_application_payload("svc", "ap-northeast")
    assert payload == {"application": {"id": "svc"}, "region": "ap-northeast"}
    assert "subscription" not in payload


def test_subscription_payload_does_not_include_application():
    payload = apply_subscription_payload("sub")
    assert payload == {"subscription": [{"id": "sub"}]}
    assert "application" not in payload
