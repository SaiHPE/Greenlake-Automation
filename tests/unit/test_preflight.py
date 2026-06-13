from pydantic import SecretStr

from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, CheckStatus, DsccSetupConfig, NetworkConfig


def _item(**overrides):
    data = {
        "serial_number": "SGHD44LQLS",
        "part_number": "S0B84A",
        "subscription_key": SecretStr("secret"),
        "service_catalog_region_id": "ap-northeast",
        "dscc_region_code": "jp1",
        "cloudinit_url": "https://169.254.239.27/cloudinit",
        "network": NetworkConfig(
            mgmt_ipv4="10.64.122.140",
            mask="255.255.255.0",
            gateway="10.64.122.1",
            dns=["10.0.0.10"],
            ntp="ntp.example.com",
            timezone="Asia/Kolkata",
        ),
        "dscc_setup": DsccSetupConfig(
            system_name="array01",
            country="India",
            password="env:DSCC_SETUP_PASSWORD",
        ),
    }
    data.update(overrides)
    return ArrayWorkItem(**data)


def test_preflight_fails_bad_cloudinit_url():
    service = PreflightService(Settings())
    report = service.run_local(_item(cloudinit_url="https://10.0.0.1/cloudinit"))
    assert report.overall_status == CheckStatus.FAIL
    assert any(check.name == "cloudinit_url" and check.status == CheckStatus.FAIL for check in report.checks)


def test_preflight_warns_missing_credentials_not_fail():
    service = PreflightService(Settings())
    report = service.run_local(_item())
    assert any(check.name == "greenlake_credentials" and check.status == CheckStatus.WARN for check in report.checks)
