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

import os
import time
from pathlib import Path
from typing import Callable

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
REVIEW_WAIT_S = 1_800.0  # how long to keep the browser open for the operator to review + Submit


class CloudinitWizardAdapter:
    def __init__(
        self,
        headless: bool = False,
        cdp_url: str | None = None,
        artifact_dir: str | Path | None = None,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self.headless = headless
        # cdp_url set -> ATTACH to an already-open browser and drive its current cloudinit
        # tab (the operator navigated/clicked Modify themselves). None -> LAUNCH our own.
        self.cdp_url = cdp_url
        self.artifact_dir = Path(artifact_dir) if artifact_dir else None
        # Mid-run progress hook for the API/UI (e.g. "review_ready" once the wizard is filled
        # and the adapter starts waiting for the operator's Submit).
        self._on_status = on_status or (lambda message: None)

    async def run(self, item: ArrayWorkItem, run_id: str, *, auto_submit: bool = False) -> BrowserResultStatus:
        if not item.cloudinit_url.startswith("https://169.254."):
            return BrowserResultStatus.FAILED_TERMINAL
        if async_playwright is None:
            return BrowserResultStatus.WAITING_FOR_OPERATOR  # playwright not installed

        self._ensure_localhost_no_proxy()  # keep the local CDP connect off a lab proxy
        attached = self.cdp_url is not None
        async with async_playwright() as pw:
            try:
                if attached:
                    browser = await pw.chromium.connect_over_cdp(self.cdp_url)
                else:
                    browser = await pw.chromium.launch(
                        headless=self.headless,
                        args=[] if self.headless else ["--start-maximized"],
                    )
            except Exception:  # noqa: BLE001 - no browser (chromium missing, or CDP unreachable).
                return BrowserResultStatus.WAITING_FOR_OPERATOR

            context = None
            try:
                if attached:
                    page = await self._pick_open_page(browser, item.cloudinit_url)
                    if page is None:
                        return BrowserResultStatus.WAITING_FOR_OPERATOR  # no open tab to drive
                else:
                    context = await browser.new_context(
                        ignore_https_errors=True,  # the array serves a self-signed cert
                        no_viewport=not self.headless,
                    )
                    page = await context.new_page()
                    await page.goto(item.cloudinit_url, wait_until="domcontentloaded")

                page.set_default_timeout(STEP_TIMEOUT_MS)
                if await self._page_has_any(page, CLOUDINIT_TEXT["success"]):
                    return BrowserResultStatus.ALREADY_DONE  # connected; never touches Modify/Launch
                await self._welcome(page)
                await self._eula(page)
                await self._network(page, item.network)
                await self._proxy(page, item.network)
                await self._time(page, item.network)  # advancing from Time lands on the Review screen
                if auto_submit:
                    # Operator already reviewed the values in the web app; fill + submit in one
                    # motion (no idle window), but verify the Review screen first — see below.
                    return await self._guarded_submit(page, item.network, run_id)
                # Manual mode (CLI without --auto-submit): stop at Review and let the operator
                # Submit themselves. NOTE: the wizard decays the Network boxes to the array's
                # link-local default after ~10s idle, so this path can show stale values — the
                # product flow uses auto_submit, which re-verifies right before Submit.
                self._on_status("review_ready")
                return await self._wait_for_operator_submit(page, run_id)
            except PlaywrightTimeoutError:
                await self._dump(page, run_id, "timeout")
                return BrowserResultStatus.FAILED_RETRYABLE
            finally:
                if not attached:  # only close what we launched; never close the operator's browser
                    if context is not None:
                        await context.close()
                    await browser.close()

    # ------------------------------------------------------------------ screens

    async def _pick_open_page(self, browser, cloudinit_url: str):
        # The link-local IP changes per boot, so match the /cloudinit path, not the exact host.
        pages = [page for context in browser.contexts for page in context.pages]
        for page in pages:
            if "cloudinit" in (page.url or ""):
                await page.bring_to_front()
                return page
        return pages[0] if pages else None

    async def _welcome(self, page) -> None:
        get_started = page.get_by_role("button", name=CLOUDINIT["get_started"])
        try:
            await get_started.wait_for(timeout=5_000)
        except PlaywrightTimeoutError:
            return  # already past the welcome screen
        await get_started.click()

    async def _eula(self, page) -> None:
        # The real checkbox input is visually hidden (Grommet), so key off the visible label.
        label = page.get_by_text(CLOUDINIT["eula_accept_label"], exact=False)
        await label.wait_for()
        await self._scroll_eula_to_end(page)  # accept is enabled only after scrolling to the end
        await page.wait_for_timeout(500)
        accept = page.locator(CLOUDINIT["eula_accept_input"])
        if not await accept.is_checked():
            await label.click()
        await self._next(page)

    async def _network(self, page, net: NetworkConfig) -> None:
        await page.locator(CLOUDINIT["mgmt_ip"]).wait_for()
        await self._fill(page, CLOUDINIT["mgmt_ip"], net.mgmt_ipv4)
        await self._fill(page, CLOUDINIT["netmask"], net.mask)
        await self._fill(page, CLOUDINIT["gateway"], net.gateway)
        for selector, value in zip(CLOUDINIT["dns_inputs"], net.dns):
            await self._fill(page, selector, value)
        # Blur the last field, then re-read the three IP boxes. These are React-controlled and
        # are PRE-FILLED with the array's link-local default; if our typed value didn't stick in
        # React state it re-renders the old value on blur. Catch that here (fast-fail) so a wrong
        # value never reaches the Review page where the operator might submit it.
        await page.evaluate("() => document.activeElement && document.activeElement.blur()")
        for selector, value in (
            (CLOUDINIT["mgmt_ip"], net.mgmt_ipv4),
            (CLOUDINIT["netmask"], net.mask),
            (CLOUDINIT["gateway"], net.gateway),
        ):
            got = await page.locator(selector).input_value()
            if got != value:
                raise PlaywrightTimeoutError(
                    f"Network field {selector} reverted after blur: got {got!r}, wanted {value!r} "
                    "(the wizard kept its link-local default — value did not commit)."
                )
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
        region = net.timezone.split("/", 1)[0]  # "Asia/Kolkata" -> "Asia"
        await self._select(page, CLOUDINIT["time_region_select"], region, exact=True)
        await self._select(page, CLOUDINIT["time_zone_select"], net.timezone, exact=False)
        await self._next(page)

    # ------------------------------------------------------------------ Review guard + Submit

    async def _guarded_submit(self, page, net: NetworkConfig, run_id: str) -> BrowserResultStatus:
        """Verify the Review screen still shows our Network values, then Submit.

        The Network boxes start EMPTY with the array's current (link-local) config shown only as
        placeholder; if the form sits idle the typed values decay back to that default, so a blind
        Submit could apply link-local and strand the array. We re-read the Review summary, re-fill
        once if the values decayed, and REFUSE to submit if they still don't match — a wrong
        management IP is never applied, on any install.
        """
        if not await self._review_network_ok(page, net):
            self._on_status("reasserted")
            await self._reassert_network(page, net)
        if not await self._review_network_ok(page, net):
            await self._dump(page, run_id, "review-mismatch")
            self._on_status("refused")
            return BrowserResultStatus.FAILED_RETRYABLE
        self._on_status("applying")
        await page.get_by_role("button", name=CLOUDINIT["submit"], exact=True).click()
        return await self._await_result(page, run_id)

    async def _review_network_ok(self, page, net: NetworkConfig) -> bool:
        values = await self._review_network_values(page)
        return (
            values.get("ip") == net.mgmt_ipv4
            and values.get("mask") == net.mask
            and values.get("gateway") == net.gateway
        )

    async def _review_network_values(self, page) -> dict[str, str]:
        # The Review screen lists each field as a label followed by its value. inner_text usually
        # puts them on separate lines ("IP address:" then the value), but tolerate "label: value"
        # on one line too. Exact full-label match avoids catching "DNS server IP address 1".
        text = await self._body_text(page)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        labels = {"ip address": "ip", "netmask": "mask", "gateway": "gateway"}
        out: dict[str, str] = {}
        for index, line in enumerate(lines):
            lowered = line.lower()
            for label, key in labels.items():
                if lowered in (label, label + ":"):
                    if index + 1 < len(lines):
                        out[key] = lines[index + 1]
                elif lowered.startswith(label + ":"):
                    value = line.split(":", 1)[1].strip()
                    if value:
                        out[key] = value
        return out

    async def _reassert_network(self, page, net: NetworkConfig) -> None:
        # Review -> Back to the Network screen (Review/Time/Proxy/Network = 3 Backs), re-fill, and
        # walk forward again. _network re-fills + advances to Proxy; two more Continues reach Review.
        for _ in range(3):
            await self._back(page)
            await page.wait_for_timeout(300)
        await self._network(page, net)
        await self._next(page)  # Proxy -> Time
        await self._next(page)  # Time -> Review

    async def _back(self, page) -> None:
        button = page.get_by_role("button", name=CLOUDINIT["back"], exact=True).first
        await button.wait_for(state="visible")
        await button.click()

    # ------------------------------------------------------------------ helpers

    async def _next(self, page) -> None:
        # Responsive wizard: maximized -> footer "Continue" (setup-next-button); narrow viewport
        # -> header arrow (setup-next-icon). Combined CSS matches whichever the layout renders;
        # wait for it to be visible (it can be briefly disabled until the page validates).
        selector = ", ".join(CLOUDINIT["next"])
        button = page.locator(selector).first
        await button.wait_for(state="visible")
        await button.click()

    async def _fill(self, page, selector: str, value: str) -> None:
        field = page.locator(selector)
        await field.wait_for()
        await field.click()
        await field.press("Control+a")
        await field.press("Delete")  # clear any pre-filled value (e.g. the link-local default)
        # Type key-by-key (not fill()): fill() sets the DOM value but not React's controlled
        # state, so a pre-filled box keeps its old value on Review. Real keystrokes fire onChange.
        await field.press_sequentially(value, delay=20)
        got = await field.input_value()
        if got != value:
            raise PlaywrightTimeoutError(f"Field {selector} did not accept value: got {got!r}, wanted {value!r}")

    async def _select(self, page, trigger_selector: str, option_text: str, *, exact: bool) -> None:
        # Open the Grommet drop and click the option by VISIBLE TEXT (the plain options don't
        # reliably expose role=option). Long lists (timezones, ~400) are virtualized + have no
        # search box, so the target isn't in the DOM until scrolled. Park the mouse over the
        # open drop and use the native wheel to scroll the LIST (won't close it or scroll the
        # page), checking for the option each step. exact=False = substring (City).
        trigger = page.locator(trigger_selector)
        await trigger.click()
        await page.wait_for_timeout(300)
        box = await trigger.bounding_box()
        if box:  # hover ~150px below the trigger -> inside the drop that opened beneath it
            await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] + 150)
        target = page.get_by_text(option_text, exact=exact)
        for _ in range(60):
            if await target.count() > 0:
                try:
                    await target.first.scroll_into_view_if_needed(timeout=500)
                    await target.first.click(timeout=1_500)
                    return
                except Exception:  # noqa: BLE001 - may be re-virtualized; scroll more and retry
                    pass
            await page.mouse.wheel(0, 400)
            await page.wait_for_timeout(100)
        await target.first.click()

    async def _scroll_eula_to_end(self, page) -> None:
        # Scroll every scrollable container to its bottom and fire a scroll event, so the
        # "scroll to the end to accept" gate is satisfied however the EULA box is built.
        await page.evaluate(
            """() => {
                for (const el of document.querySelectorAll('*')) {
                    if (el.clientHeight > 40 && el.scrollHeight > el.clientHeight + 8) {
                        el.scrollTop = el.scrollHeight;
                        el.dispatchEvent(new Event('scroll', { bubbles: true }));
                    }
                }
            }"""
        )

    async def _wait_for_operator_submit(self, page, run_id: str) -> BrowserResultStatus:
        """Filled through Review; leave the browser open and watch for the operator's Submit."""
        deadline = time.monotonic() + REVIEW_WAIT_S
        while time.monotonic() < deadline:
            if page.is_closed():
                return BrowserResultStatus.WAITING_FOR_OPERATOR  # operator closed it / cancelled
            text = (await self._body_text(page)).lower()
            if any(sig in text for sig in CLOUDINIT_TEXT["success"]):
                return BrowserResultStatus.SUCCEEDED
            if any(sig in text for sig in CLOUDINIT_TEXT["fail_prov"]):
                await self._dump(page, run_id, "fail-prov")
                return BrowserResultStatus.FAILED_RETRYABLE
            try:
                await page.wait_for_timeout(2_000)
            except Exception:  # noqa: BLE001 - the page may close mid-wait.
                return BrowserResultStatus.WAITING_FOR_OPERATOR
        return BrowserResultStatus.WAITING_FOR_OPERATOR

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

    @staticmethod
    def _ensure_localhost_no_proxy() -> None:
        """Add localhost to NO_PROXY so the CDP connection isn't routed through a lab proxy."""
        existing = os.environ.get("NO_PROXY") or os.environ.get("no_proxy") or ""
        hosts = [h.strip() for h in existing.split(",") if h.strip()]
        for host in ("localhost", "127.0.0.1"):
            if host not in hosts:
                hosts.append(host)
        value = ",".join(hosts)
        os.environ["NO_PROXY"] = value
        os.environ["no_proxy"] = value

    async def _dump(self, page, run_id: str, label: str) -> None:
        if not self.artifact_dir:
            return
        try:
            self.artifact_dir.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(self.artifact_dir / f"cloudinit-{run_id}-{label}.png"), full_page=True)
        except Exception:  # noqa: BLE001
            pass
