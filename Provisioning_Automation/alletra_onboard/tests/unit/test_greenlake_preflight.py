from pydantic import SecretStr

from alletra_onboard.adapters.greenlake.service_catalog import ServiceProvision
from alletra_onboard.application.greenlake_preflight import (
    GreenLakeReadPreflightService,
    build_greenlake_read_preflight,
)
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, CheckStatus, DsccSetupConfig, NetworkConfig, PreflightCheck


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


class FakeTokenProvider:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def token(self) -> str:
        if self.error:
            raise self.error
        return "token"


class FakeDevices:
    def __init__(self, device: dict | None = None) -> None:
        self.device = device

    async def find_by_serial(self, serial_number: str) -> dict | None:
        return self.device


class FakeSubscriptions:
    def __init__(self, subscription: dict | None = None) -> None:
        self.subscription = subscription

    async def find_by_key(self, subscription_key: str) -> dict | None:
        return self.subscription


class FakeServiceCatalog:
    def __init__(self, provisions: list[ServiceProvision]) -> None:
        self.provisions = provisions

    async def service_manager_provisions(self, region: str) -> list[ServiceProvision]:
        return self.provisions


class FakeGreenLakeRunner:
    async def run(self, item: ArrayWorkItem) -> list[PreflightCheck]:
        return [
            PreflightCheck(
                name="greenlake_auth",
                status=CheckStatus.PASS,
                message="fake live check",
            )
        ]


async def test_live_greenlake_preflight_passes_read_checks():
    service = GreenLakeReadPreflightService(
        FakeTokenProvider(),
        FakeDevices(),
        FakeSubscriptions({"id": "sub-123"}),
        FakeServiceCatalog(
            [
                ServiceProvision(
                    service_manager_id="svc-123",
                    region="ap-northeast",
                    provision_status="PROVISIONED",
                )
            ]
        ),
    )

    checks = await service.run(_item())

    by_name = {check.name: check for check in checks}
    assert by_name["greenlake_auth"].status == CheckStatus.PASS
    assert by_name["greenlake_service_catalog"].status == CheckStatus.PASS
    assert by_name["greenlake_device_lookup"].status == CheckStatus.PASS
    assert by_name["greenlake_subscription_lookup"].status == CheckStatus.PASS


async def test_live_greenlake_preflight_stops_and_redacts_auth_failure():
    service = GreenLakeReadPreflightService(
        FakeTokenProvider(RuntimeError("client_secret=super-secret")),
        FakeDevices(),
        FakeSubscriptions(),
        FakeServiceCatalog([]),
    )

    checks = await service.run(_item())

    assert len(checks) == 1
    assert checks[0].name == "greenlake_auth"
    assert checks[0].status == CheckStatus.FAIL
    assert "<redacted>" in checks[0].message
    assert "super-secret" not in checks[0].message


async def test_build_greenlake_preflight_fails_when_credentials_are_missing():
    runner = build_greenlake_read_preflight(Settings())

    checks = await runner.run(_item())

    assert checks[0].name == "greenlake_live_credentials"
    assert checks[0].status == CheckStatus.FAIL
    assert "GL_CLIENT_ID" in checks[0].message


async def test_preflight_service_merges_local_and_live_checks():
    service = PreflightService(
        Settings(
            gl_client_id="client",
            gl_client_secret="secret",
            gl_member_workspace_id="workspace",
        ),
        greenlake_factory=lambda settings: FakeGreenLakeRunner(),
    )

    report = await service.run(_item(), live_greenlake=True)

    assert report.overall_status == CheckStatus.PASS
    assert any(check.name == "greenlake_auth" for check in report.checks)
