import io

import pytest
from openpyxl import load_workbook

from alletra_onboard.application.init_sheet import (
    SECTIONS,
    build_template_bytes,
    parse_workbook_bytes,
)


def _fill(values: dict[str, str]) -> bytes:
    """Take the blank template and fill the Value column for the given field keys."""
    label_to_key = {label: key for _, fields in SECTIONS for key, label, _, _ in fields}
    wb = load_workbook(io.BytesIO(build_template_bytes()))
    ws = wb.active
    for row in ws.iter_rows(min_row=2):
        label = row[0].value
        if label is None:
            continue
        key = label_to_key.get(str(label).strip().removesuffix("*").strip())
        if key and key in values:
            row[1].value = values[key]
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


_COMPLETE = {
    "gl_client_id": "client-123",
    "gl_client_secret": "secret-xyz",
    "gl_token_url": "https://global.api.greenlake.hpe.com/authorization/v2/oauth2/tenant/token",
    "serial_number": "SGHD45FF0Y",
    "part_number": "S0B84A",
    "subscription_key": "YHHDKEY1234567890",
    "service_catalog_region_id": "ap-northeast",
    "dscc_region_code": "jp1",
    "mgmt_ipv4": "10.64.154.225",
    "mask": "255.255.248.0",
    "gateway": "10.64.159.254",
    "dns1": "10.203.96.10",
    "dns2": "10.203.96.9",
    "ntp": "ntp1.example.net",
    "timezone": "Asia/Kolkata",
    "proxy_host": "proxy.example.net",
    "proxy_port": "8080",
    "contact_first_name": "Jane",
    "contact_last_name": "Doe",
    "contact_language": "English",
    "contact_company": "HPE",
    "contact_phone": "8000000000",
    "contact_email": "jane.doe@example.com",
    "dscc_system_name": "MPB10K-TEST",
    "dscc_country": "India",
    "secret_name": "b10000-admin",
    "secret_username": "3paradm",
}


def test_template_is_a_valid_xlsx_with_every_field():
    wb = load_workbook(io.BytesIO(build_template_bytes()))
    labels = {str(row[0].value).strip().removesuffix("*").strip() for row in wb.active.iter_rows(min_row=2) if row[0].value}
    for _, fields in SECTIONS:
        for _, label, _, _ in fields:
            assert label in labels


def test_round_trip_parses_creds_and_work_item():
    parsed = parse_workbook_bytes(_fill(_COMPLETE))
    assert parsed.gl_client_id == "client-123"
    assert parsed.gl_client_secret == "secret-xyz"
    assert parsed.gl_token_url.endswith("/token")

    item = parsed.work_item
    assert item.serial_number == "SGHD45FF0Y"
    assert item.part_number == "S0B84A"
    assert item.subscription_key.get_secret_value() == "YHHDKEY1234567890"
    assert item.network.mgmt_ipv4 == "10.64.154.225"
    assert item.network.dns == ["10.203.96.10", "10.203.96.9"]
    assert item.network.proxy_port == 8080
    # the admin password is NOT in the sheet — the operator types it in the DSCC wizard
    assert item.dscc_setup.password is None
    assert item.dscc_setup.system_name == "MPB10K-TEST"


def test_missing_required_field_is_reported():
    incomplete = dict(_COMPLETE)
    del incomplete["gl_client_secret"]
    del incomplete["mgmt_ipv4"]
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_fill(incomplete))
    assert "API Client Secret" in str(exc.value)
    assert "IP address" in str(exc.value)
