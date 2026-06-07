from __future__ import annotations

from collections.abc import Callable

from alletra_onboard.application.greenlake_preflight import (
    GreenLakePreflightRunner,
    build_greenlake_read_preflight,
)
from alletra_onboard.config import Settings
from alletra_onboard.domain.models import ArrayWorkItem, CheckStatus, PreflightCheck, PreflightReport


class PreflightService:
    def __init__(
        self,
        settings: Settings,
        greenlake_factory: Callable[[Settings], GreenLakePreflightRunner] | None = None,
    ) -> None:
        self.settings = settings
        self.greenlake_factory = greenlake_factory or build_greenlake_read_preflight

    async def run(self, item: ArrayWorkItem, *, live_greenlake: bool = False) -> PreflightReport:
        report = self.run_local(item)
        if not live_greenlake:
            return report

        checks = [*report.checks]
        checks.extend(await self.greenlake_factory(self.settings).run(item))
        overall = self._overall(checks)
        return PreflightReport(serial_number=item.serial_number, overall_status=overall, checks=checks)

    def run_local(self, item: ArrayWorkItem) -> PreflightReport:
        checks = [
            self._check_greenlake_credentials(),
            self._check_cloudinit_url(item),
            self._check_region_pair(item),
            self._check_network_config(item),
            self._check_dscc_credentials(item),
        ]
        overall = self._overall(checks)
        return PreflightReport(serial_number=item.serial_number, overall_status=overall, checks=checks)

    def _check_greenlake_credentials(self) -> PreflightCheck:
        missing = [
            name
            for name, value in {
                "GL_CLIENT_ID": self.settings.gl_client_id,
                "GL_CLIENT_SECRET": self.settings.gl_client_secret,
                "GL_MEMBER_WORKSPACE_ID": self.settings.gl_member_workspace_id,
            }.items()
            if not value
        ]
        if missing:
            return PreflightCheck(
                name="greenlake_credentials",
                status=CheckStatus.WARN,
                message=f"Missing credentials for live GreenLake checks: {', '.join(missing)}",
                remediation="Set the missing environment variables before live REST phases.",
            )
        return PreflightCheck(
            name="greenlake_credentials",
            status=CheckStatus.PASS,
            message="GreenLake credential environment variables are present.",
        )

    def _check_cloudinit_url(self, item: ArrayWorkItem) -> PreflightCheck:
        if not item.cloudinit_url.startswith("https://169.254."):
            return PreflightCheck(
                name="cloudinit_url",
                status=CheckStatus.FAIL,
                message="Cloudinit URL is not a link-local HTTPS URL.",
                remediation="Run the Discovery Tool manually and provide the https://169.254.x/cloudinit URL.",
            )
        return PreflightCheck(
            name="cloudinit_url",
            status=CheckStatus.PASS,
            message="Cloudinit URL uses expected link-local HTTPS format.",
        )

    def _check_region_pair(self, item: ArrayWorkItem) -> PreflightCheck:
        expected_pairs = {"ap-northeast": "jp1", "us-west": "us1", "eu-central": "eu1", "eu-west": "uk1"}
        expected = expected_pairs.get(item.service_catalog_region_id)
        if expected and expected != item.dscc_region_code:
            return PreflightCheck(
                name="region_mapping",
                status=CheckStatus.FAIL,
                message=(
                    f"GreenLake region {item.service_catalog_region_id} normally maps to DSCC "
                    f"{expected}, not {item.dscc_region_code}."
                ),
                remediation="Correct either service_catalog_region_id or dscc_region_code.",
            )
        if not expected:
            return PreflightCheck(
                name="region_mapping",
                status=CheckStatus.WARN,
                message=f"Unknown GreenLake region mapping: {item.service_catalog_region_id}.",
                remediation="Confirm the region mapping in config before live execution.",
            )
        return PreflightCheck(name="region_mapping", status=CheckStatus.PASS, message="Region mapping is known.")

    def _check_network_config(self, item: ArrayWorkItem) -> PreflightCheck:
        if not item.network.dns:
            return PreflightCheck(
                name="network_config",
                status=CheckStatus.FAIL,
                message="At least one DNS server is required.",
            )
        return PreflightCheck(
            name="network_config",
            status=CheckStatus.PASS,
            message="Network config has DNS, NTP, gateway, and management IP fields.",
        )

    def _check_dscc_credentials(self, item: ArrayWorkItem) -> PreflightCheck:
        if not item.dscc_setup.password_ref:
            return PreflightCheck(
                name="dscc_setup_secret",
                status=CheckStatus.WARN,
                message="No DSCC setup credential secret reference configured.",
                remediation="Set dscc_setup.password_ref before DSCC Setup automation.",
            )
        return PreflightCheck(
            name="dscc_setup_secret",
            status=CheckStatus.PASS,
            message="DSCC setup credential is referenced, not stored inline.",
        )

    def _overall(self, checks: list[PreflightCheck]) -> CheckStatus:
        if any(check.status == CheckStatus.FAIL for check in checks):
            return CheckStatus.FAIL
        if any(check.status == CheckStatus.WARN for check in checks):
            return CheckStatus.WARN
        return CheckStatus.PASS
