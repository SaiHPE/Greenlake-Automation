import io

import pytest
from openpyxl import load_workbook

from alletra_onboard.application.init_sheet import (
    PROVISIONING_SECTIONS,
    PROVISIONING_SHEET_NAME,
    SECTIONS,
    build_template_bytes,
    parse_workbook_bytes,
)
from alletra_onboard.domain.models import RunMode

_PROV_COMPLETE = {
    "prov_array_host": "10.64.122.140", "prov_array_user": "3paradm", "prov_array_password": "pw",
    "prov_vcenter_host": "vc.example.net", "prov_vcenter_user": "administrator@vsphere.local", "prov_vcenter_password": "vpw",
    "prov_sw1_host": "10.0.0.1", "prov_sw1_user": "admin", "prov_sw1_password": "s1",
    "prov_sw2_host": "10.0.0.2", "prov_sw2_user": "admin", "prov_sw2_password": "s2",
    "prov_host_set": "CRVLZ_Hostset", "prov_cpg": "SSD_r6", "prov_type": "tpvv",
    "prov_vol_prefix": "CRV_LZ_Prod", "prov_vol_size_gib": "1024", "prov_vol_count": "3",
}


def _fill_tabs(init_values: dict[str, str], prov_values: dict[str, str] | None = None) -> bytes:
    """Fill the Initialisation tab and (optionally) the Provisioning tab of the template."""
    init_l2k = {label: key for _, fields in SECTIONS for key, label, _, _ in fields}
    prov_l2k = {label: key for _, fields in PROVISIONING_SECTIONS for key, label, _, _ in fields}
    wb = load_workbook(io.BytesIO(build_template_bytes()))

    def fill(ws, label_to_key, vals):
        for row in ws.iter_rows(min_row=2):
            if row[0].value is None:
                continue
            key = label_to_key.get(str(row[0].value).strip().removesuffix("*").strip())
            if key and key in vals:
                row[1].value = vals[key]

    fill(wb["Initialisation"], init_l2k, init_values)
    if prov_values is not None:
        fill(wb[PROVISIONING_SHEET_NAME], prov_l2k, prov_values)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


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


def test_verify_only_sheet_needs_just_serial_and_ip():
    # A sparse sheet (no GreenLake creds, no DSCC contact) parses fine for a verify-only run.
    sparse = {"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.154.225"}
    parsed = parse_workbook_bytes(_fill(sparse), mode=RunMode.VERIFY_ONLY)
    assert parsed.work_item.serial_number == "SGHD45FF0Y"
    assert parsed.work_item.network.mgmt_ipv4 == "10.64.154.225"
    assert parsed.gl_client_id == ""  # not required, not present


def test_verify_only_still_requires_the_array_ip():
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(_fill({"serial_number": "SGHD45FF0Y"}), mode=RunMode.VERIFY_ONLY)
    assert "IP address" in str(exc.value)


def test_provision_only_parses_the_provisioning_tab_not_greenlake():
    parsed = parse_workbook_bytes(
        _fill_tabs({"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.122.140"}, _PROV_COMPLETE),
        mode=RunMode.PROVISION_ONLY,
    )
    assert parsed.gl_client_id == ""  # GreenLake creds not required for provisioning
    intent = parsed.provisioning_intent
    assert intent is not None
    assert intent.host_set_name == "CRVLZ_Hostset"
    assert intent.array.host == "10.64.122.140"
    assert intent.array.password.get_secret_value() == "pw"
    assert intent.switch_f1.host == "10.0.0.1" and intent.switch_f2.host == "10.0.0.2"
    assert intent.volume.names() == ["CRV_LZ_Prod01", "CRV_LZ_Prod02", "CRV_LZ_Prod03"]
    assert intent.provisioning_type == "tpvv" and intent.cpg == "SSD_r6"


def test_provision_only_reports_missing_provisioning_fields():
    incomplete = dict(_PROV_COMPLETE)
    del incomplete["prov_array_password"]
    with pytest.raises(ValueError) as exc:
        parse_workbook_bytes(
            _fill_tabs({"serial_number": "SGHD45FF0Y", "mgmt_ipv4": "10.64.122.140"}, incomplete),
            mode=RunMode.PROVISION_ONLY,
        )
    assert "Provisioning tab" in str(exc.value)
    assert "Array admin password" in str(exc.value)


def test_full_mode_ignores_the_provisioning_tab():
    # No provisioning step selected -> the Provisioning tab is not parsed at all.
    parsed = parse_workbook_bytes(_fill_tabs(_COMPLETE))  # default FULL_ONBOARDING, no prov values
    assert parsed.provisioning_intent is None
