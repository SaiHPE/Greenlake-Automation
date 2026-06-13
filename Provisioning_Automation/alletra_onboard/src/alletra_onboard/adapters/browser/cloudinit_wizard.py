"""Component B — drive the on-array HPE Cloud Connectivity Wizard (Playwright).

Launches its own Chromium, navigates to the array's ``https://169.254.x.x/cloudinit``
(self-signed cert handled via ``ignore_https_errors``), and drives the wizard. No auth.
The operator supplies the cloudinit URL (from the HPE Discovery Tool); the frontend will
pass it the same way. Steps mirror the live capture:

    Welcome -> EULA(1) -> Network(2) -> Proxy(3) -> Time(4) -> Review(5) -> Submit

then it polls the page text until the array reports connected. Register + assign in
GreenLake (Component A) must already be done, or the progress screen fails with fail-prov.

Selectors live in ``locators.CLOUDINIT`` (HPE exposes stable name / data-test-id hooks).
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from alletra_onboard.adapters.browser.locators import CLOUDINIT, CLOUDINIT_TEXT
from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus, NetworkConfig

try:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    from playwright.async_api import async_playwright
except ImportError:  # pragma: no cover - browser deps optional until B/C run.
    async_playwright = None

    class PlaywrightTimeoutError(Exception):
        pass


STEP_TIMEOUT_MS = 30_000
CONNECT_TIMEOUT_S = 300.0


class CloudinitWizardAdapter:
    def __init__(self, headless: bool = False, artifact_dir: str | Path | None = None) -> None:
        self.headless = headless
        self.artifact_dir = Path(artifact_dir) if artifact_dir else None

    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus:
        if not item.cloudinit_url.startswith("https://169.254."):
            return BrowserResultStatus.FAILED_TERMINAL
        if async_playwright is None:
            return BrowserResultStatus.WAITING_FOR_OPERATOR  # playwright not installed

        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.launch(
                    headless=self.headless,
                    args=[] if self.headless else ["--start-maximized"],
                )
            except Exception:  # noqa: BLE001 - chromium missing: run `playwright install chromium`.
                return BrowserResultStatus.WAITING_FOR_OPERATOR

            context = await browser.new_context(
                ignore_https_errors=True,  # the array serves a self-signed cert
                no_viewport=not self.headless,
            )
            page = await context.new_page()
            page.set_default_timeout(STEP_TIMEOUT_MS)
            try:
                await page.goto(item.cloudinit_url, wait_until="domcontentloaded")
                if await self._page_has_any(page, CLOUDINIT_TEXT["success"]):
                    return BrowserResultStatus.ALREADY_DONE
                await self._welcome(page)
                await self._eula(page)
                await self._network(page, item.network)
                await self._proxy(page, item.network)
                await self._time(page, item.network)
                await page.get_by_role("button", name=CLOUDINIT["submit"], exact=True).click()
                return await self._await_result(page, run_id)
            except PlaywrightTimeoutError:
                await self._dump(page, run_id, "timeout")
                return BrowserResultStatus.FAILED_RETRYABLE
            finally:
                await context.close()
                await browser.close()

    # ------------------------------------------------------------------ screens

    async def _welcome(self, page) -> None:
        get_started = page.get_by_role("button", name=CLOUDINIT["get_started"])
        try:
            await get_started.wait_for(timeout=5_000)
        except PlaywrightTimeoutError:
            return  # already past the welcome screen
        await get_started.click()

    async def _eula(self, page) -> None:
        accept = page.locator(CLOUDINIT["eula_accept_input"])
        await accept.wait_for()
        await self._scroll_eula_to_end(page)  # accept is enabled only after scrolling to the end
        if not await accept.is_checked():
            await page.get_by_text(CLOUDINIT["eula_accept_label"], exact=False).click()
        await self._next(page)

    async def _network(self, page, net: NetworkConfig) -> None:
        await page.locator(CLOUDINIT["mgmt_ip"]).wait_for()
        await self._fill(page, CLOUDINIT["mgmt_ip"], net.mgmt_ipv4)
        await self._fill(page, CLOUDINIT["netmask"], net.mask)
        await self._fill(page, CLOUDINIT["gateway"], net.gateway)
        for selector, value in zip(CLOUDINIT["dns_inputs"], net.dns):
            await self._fill(page, selector, value)
        await self._next(page)

    async def _proxy(self, page, net: NetworkConfig) -> None:
        if net.proxy_host:
            await page.get_by_text(CLOUDINIT["proxy_http_option"], exact=True).click()
            await self._fill(page, CLOUDINIT["proxy_server"], net.proxy_host)
            if net.proxy_port is not None:
                await self._fill(page, CLOUDINIT["proxy_port"], str(net.proxy_port))
        else:
            await page.get_by_text(CLOUDINIT["proxy_none_option"], exact=True).click()
        await self._next(page)

    async def _time(self, page, net: NetworkConfig) -> None:
        await self._fill(page, CLOUDINIT["ntp"], net.ntp)
        region = net.timezone.split("/", 1)[0]
        await self._select(page, CLOUDINIT["time_region_select"], re.compile(rf"^{re.escape(region)}$"))
        await self._select(page, CLOUDINIT["time_zone_select"], re.compile(rf"^{re.escape(net.timezone)}\b"))
        await self._next(page)

    # ------------------------------------------------------------------ helpers

    async def _next(self, page) -> None:
        await page.locator(CLOUDINIT["next"]).click()

    async def _fill(self, page, selector: str, value: str) -> None:
        field = page.locator(selector)
        await field.wait_for()
        await field.fill(value)

    async def _select(self, page, trigger_selector: str, option_pattern: re.Pattern[str]) -> None:
        # Grommet Select: click the (readonly) value box to open the drop, then click the option.
        await page.locator(trigger_selector).click()
        await page.get_by_role("option", name=option_pattern).first.click()

    async def _scroll_eula_to_end(self, page) -> None:
        await page.evaluate(
            """() => {
                for (const el of document.querySelectorAll('div, section')) {
                    if (el.scrollHeight > el.clientHeight + 20
                        && /End User License Agreement/i.test(el.textContent || '')) {
                        el.scrollTop = el.scrollHeight;
                    }
                }
            }"""
        )

    async def _await_result(self, page, run_id: str) -> BrowserResultStatus:
        deadline = time.monotonic() + CONNECT_TIMEOUT_S
        while time.monotonic() < deadline:
            text = (await self._body_text(page)).lower()
            if any(sig in text for sig in CLOUDINIT_TEXT["success"]):
                return BrowserResultStatus.SUCCEEDED
            if any(sig in text for sig in CLOUDINIT_TEXT["fail_prov"]):
                await self._dump(page, run_id, "fail-prov")
                return BrowserResultStatus.FAILED_RETRYABLE
            await page.wait_for_timeout(3_000)
        await self._dump(page, run_id, "connect-timeout")
        return BrowserResultStatus.FAILED_RETRYABLE

    async def _body_text(self, page) -> str:
        try:
            return await page.inner_text("body")
        except Exception:  # noqa: BLE001
            return ""

    async def _page_has_any(self, page, signals) -> bool:
        text = (await self._body_text(page)).lower()
        return any(signal in text for signal in signals)

    async def _dump(self, page, run_id: str, label: str) -> None:
        if not self.artifact_dir:
            return
        try:
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(self.artifact_dir / f"cloudinit-{run_id}-{label}.png"), full_page=True)
        except Exception:  # noqa: BLE001
            pass
