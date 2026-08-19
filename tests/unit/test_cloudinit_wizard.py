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


async def test_placeholder_url_is_terminal():
    # 169.254.0.0 is the work item's placeholder (no per-boot URL set) — never a real host.
    result = await CloudinitWizardAdapter(headless=True).run(_item("https://169.254.0.0/cloudinit"), run_id="r1")
    assert result == BrowserResultStatus.FAILED_TERMINAL


async def test_ipv6_link_local_url_is_accepted_by_the_adapter(monkeypatch):
    """REGRESSION (reported live, array CZ2D2K014S): the adapter carried its OWN IPv4-only copy of
    the link-local rule — `startswith("https://169.254.")` — so it returned FAILED_TERMINAL for the
    IPv6 address the HPE Discovery Tool produced, even after the validator, preflight, UI and proxy
    had all been taught to accept it. The rule now has one implementation (domain/cloudinit_url).

    Asserted by getting PAST the guard: with Playwright absent the adapter answers
    WAITING_FOR_OPERATOR, which is only reachable once the URL has been accepted.
    """
    from alletra_onboard.adapters.browser import cloudinit_wizard as cw

    monkeypatch.setattr(cw, "async_playwright", None)
    for url in (
        "https://[fe80::6095:14a0:b25d:fcb0]/cloudinit",     # exactly what the tool reported
        "https://[fe80::1%25eth0]/cloudinit",                 # RFC 6874 zone form
        "https://169.254.239.27/cloudinit",                   # IPv4 still works
    ):
        result = await cw.CloudinitWizardAdapter(headless=True).run(_item(url), run_id="r1")
        assert result == BrowserResultStatus.WAITING_FOR_OPERATOR, url


async def test_routable_ipv6_is_still_terminal(monkeypatch):
    """The wizard is unauthenticated — accepting IPv6 must not mean accepting any IPv6."""
    from alletra_onboard.adapters.browser import cloudinit_wizard as cw

    monkeypatch.setattr(cw, "async_playwright", None)
    result = await cw.CloudinitWizardAdapter(headless=True).run(
        _item("https://[2001:db8::1]/cloudinit"), run_id="r1")
    assert result == BrowserResultStatus.FAILED_TERMINAL


def test_browser_proxy_bypass_covers_both_link_local_families():
    """MEASURED on the jump box: an HTTPS GET to the array's fe80:: wizard returned 502 Bad Gateway
    — the corporate proxy answering, because IPv6 link-local was not in the bypass list. Chromium
    would have done the same, so the wizard was unreachable even with a valid address."""
    from alletra_onboard.adapters.browser.debug_browser import DEFAULT_PROXY_BYPASS

    assert "169.254.*" in DEFAULT_PROXY_BYPASS
    assert "fe80::" in DEFAULT_PROXY_BYPASS


def test_locators_cover_every_wizard_field():
    for key in (
        "get_started", "eula_accept_input", "next", "mgmt_ip", "netmask", "gateway",
        "dns_inputs", "proxy_server", "proxy_port", "ntp",
        "time_region_select", "time_zone_select", "back", "submit",
    ):
        assert CLOUDINIT.get(key)


def _net() -> NetworkConfig:
    return NetworkConfig(
        mgmt_ipv4="10.64.154.225",
        mask="255.255.248.0",
        gateway="10.64.159.254",
        dns=["10.203.96.10"],
        ntp="ntp1",
        timezone="Asia/Kolkata",
    )


async def _review_ok_for(body: str) -> bool:
    adapter = CloudinitWizardAdapter(headless=True)

    async def fake_body_text(_page):
        return body

    adapter._body_text = fake_body_text  # type: ignore[method-assign]
    return await adapter._review_network_ok(None, _net())


async def test_review_guard_accepts_matching_values():
    # Real Review layout: label line then value line. "DNS server IP address 1" must NOT be
    # mistaken for "IP address".
    body = (
        "Review\nNetwork\nIP address:\n10.64.154.225\nNetmask:\n255.255.248.0\n"
        "Gateway:\n10.64.159.254\nDNS server IP address 1:\n10.203.96.10\n"
    )
    assert await _review_ok_for(body) is True


async def test_review_guard_rejects_decayed_link_local_values():
    # The wizard reverted the boxes to the array's link-local default — must NOT pass the guard.
    body = (
        "Review\nNetwork\nIP address:\n169.254.184.89\nNetmask:\n255.255.0.0\n"
        "Gateway:\n169.254.0.0\n"
    )
    assert await _review_ok_for(body) is False


async def test_review_guard_handles_label_value_on_one_line():
    body = "IP address: 10.64.154.225\nNetmask: 255.255.248.0\nGateway: 10.64.159.254\n"
    assert await _review_ok_for(body) is True


class _FakePage:
    """Just enough page for the initializing wait: body text per poll, no real sleeping."""

    def __init__(self, bodies: list[str]) -> None:
        self._bodies = bodies
        self._index = 0

    def next_body(self) -> str:
        body = self._bodies[min(self._index, len(self._bodies) - 1)]
        self._index += 1
        return body

    async def wait_for_timeout(self, _ms: int) -> None:
        return None


def _adapter_with_page(bodies: list[str]) -> tuple[CloudinitWizardAdapter, _FakePage, list[str]]:
    statuses: list[str] = []
    adapter = CloudinitWizardAdapter(headless=True, on_status=statuses.append)
    page = _FakePage(bodies)

    async def fake_body_text(_page):
        return page.next_body()

    adapter._body_text = fake_body_text  # type: ignore[method-assign]
    return adapter, page, statuses


async def test_wizard_ready_immediately_when_not_initializing():
    adapter, page, statuses = _adapter_with_page(["Welcome\nGet Started"])
    assert await adapter._await_wizard_ready(page, "r1") is True
    assert statuses == []  # no noise when the wizard is already up


async def test_wizard_waits_out_the_initializing_state():
    # Seen live 2026-07: the array shows "Initializing your system..." for minutes on first boot.
    # The adapter previously fell through to the EULA locator and failed generically in ~40s.
    bodies = ["Initializing your system..."] * 3 + ["Welcome\nGet Started"]
    adapter, page, statuses = _adapter_with_page(bodies)
    assert await adapter._await_wizard_ready(page, "r1") is True
    assert any(status.startswith("initializing") for status in statuses)  # liveness was reported


async def test_wizard_initializing_timeout_reports_a_specific_error(monkeypatch):
    from alletra_onboard.adapters.browser import cloudinit_wizard as module

    monkeypatch.setattr(module, "INIT_WAIT_S", 0.0)  # expire immediately
    adapter, page, statuses = _adapter_with_page(["Initializing your system..."])
    assert await adapter._await_wizard_ready(page, "r1") is False
    assert any(status.startswith("error:") and "initializing" in status.lower() for status in statuses)


async def test_wizard_waits_through_the_blank_page_before_the_spinner():
    # The live rc.2 failure: at goto time the SPA has rendered NOTHING, so "no spinner text" is
    # also true of a blank page — waiting for the spinner's absence concluded ready instantly and
    # the run timed out on the EULA locator 41 seconds later. The wait must demand positive proof
    # of a wizard screen: blank -> blank -> spinner -> Welcome must succeed.
    bodies = ["", "", "Initializing your system...", "Initializing your system...", "Welcome\nGet Started"]
    adapter, page, statuses = _adapter_with_page(bodies)
    assert await adapter._await_wizard_ready(page, "r1") is True
    assert page._index >= len(bodies)  # it genuinely polled through every state


async def test_wizard_ready_when_the_eula_screen_renders_directly():
    # The Modify path opens on the EULA screen with no Welcome — that is proof enough.
    adapter, page, statuses = _adapter_with_page(["I have read and accept the agreement"])
    assert await adapter._await_wizard_ready(page, "r1") is True


async def test_wizard_ready_passes_terminal_screens_to_the_normal_flow():
    # An already-connected array renders its success page; the wait must hand it back, not stall.
    adapter, page, statuses = _adapter_with_page(["Your system is now connected"])
    assert await adapter._await_wizard_ready(page, "r1") is True


async def test_wizard_unknown_page_timeout_reports_what_it_shows(monkeypatch):
    from alletra_onboard.adapters.browser import cloudinit_wizard as module

    monkeypatch.setattr(module, "INIT_WAIT_S", 0.0)
    adapter, page, statuses = _adapter_with_page(["Some entirely different HPE page"])
    assert await adapter._await_wizard_ready(page, "r1") is False
    # The error names what the page actually says, so an unfamiliar state identifies itself.
    assert any("some entirely different hpe page" in status.lower() for status in statuses)
