from pydantic import SecretStr

from alletra_onboard.adapters.browser.cloudinit_wizard import CloudinitWizardAdapter
from alletra_onboard.adapters.browser.locators import CLOUDINIT
from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus, DsccSetupConfig, NetworkConfig


def _item(cloudinit_url: str) -> ArrayWorkItem:
    return ArrayWorkItem(
        serial_number="SGHD45FF0Y",
        part_number="S0B84A",
        subscription_key=SecretStr("key"),
        service_catalog_region_id="ap-northeast",
        dscc_region_code="jp1",
        cloudinit_url=cloudinit_url,
        network=NetworkConfig(
            mgmt_ipv4="10.64.154.225",
            mask="255.255.248.0",
            gateway="10.64.159.254",
            dns=["10.203.96.10", "10.203.96.9"],
            ntp="ntp1",
            timezone="Asia/Kolkata",
        ),
        dscc_setup=DsccSetupConfig(system_name="b10k", country="India"),
    )


async def test_non_link_local_url_is_terminal():
    # Guarded before any browser launch — a non-link-local URL is a config error.
    result = await CloudinitWizardAdapter(headless=True).run(_item("https://10.0.0.1/cloudinit"), run_id="r1")
    assert result == BrowserResultStatus.FAILED_TERMINAL


def test_locators_cover_every_wizard_field():
    for key in (
        "get_started", "eula_accept_input", "next", "mgmt_ip", "netmask", "gateway",
        "dns_inputs", "proxy_server", "proxy_port", "ntp",
        "time_region_select", "time_zone_select", "submit",
    ):
        assert CLOUDINIT.get(key)
