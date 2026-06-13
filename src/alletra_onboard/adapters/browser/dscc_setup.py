"""Component C — drive the DSCC "Set Up System" wizard (Playwright, ATTACH only).

DSCC needs a live GreenLake SSO session, so this adapter never logs in: it attaches over
CDP to a Chrome the operator already authenticated, finds the DSCC tab, and drives the
"HPE Alletra Setup Wizard". The whole wizard renders inside an IFRAME
(``data-test-id="setup-iframe"``), so every locator is scoped to that frame.

    Welcome -> Network Domain -> Time -> Attributes(Proxy, Support Contact) -> System -> Review

It fills each step and **STOPS at "Review and Finalize" — it never clicks Submit** (the
operator reviews + finalizes; finalize may also need the GreenLake subscription). It never
touches the blueprint checkbox. DNS / NTP / timezone / proxy carry over from cloudinit, so
those screens are mostly confirm-and-continue; the genuinely new input is Support Contact,
the System name/country, and the System credential (secret).

Selectors live in ``locators.DSCC``. The Create-Secret modal fields were not captured open,
so those locators are best-effort (label/name based) and flagged for first-run verification.
"""

from __future__ import annotations

import os
from pathlib import Path

from alletra_onboard.adapters.browser.locators import DSCC
from alletra_onboard.domain.models import ArrayWorkItem, BrowserResultStatus, DsccSetupConfig, NetworkConfig

try:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    from playwright.async_api import async_playwright
except ImportError:  # pragma: no cover - browser deps optional until B/C run.
    async_playwright = None

    class PlaywrightTimeoutError(Exception):
        pass


STEP_TIMEOUT_MS = 30_000
DSCC_HOST_HINT = "data.cloud.hpe.com"


class DsccSetupError(Exception):
    """Operator-actionable problem (e.g. a required secret is missing)."""


class DsccSetupAdapter:
    def __init__(self, cdp_url: str | None = None, artifact_dir: str | Path | None = None) -> None:
        # DSCC is attach-only — it needs the operator's authenticated GreenLake session.
        self.cdp_url = cdp_url
        self.artifact_dir = Path(artifact_dir) if artifact_dir else None

    async def run(self, item: ArrayWorkItem, run_id: str) -> BrowserResultStatus:
        # WAITING_FOR_OPERATOR is reserved for the genuine operator gate (stopped at the System
        # credential). Anything that prevented attaching is FAILED_RETRYABLE so callers (CLI/UI)
        # can show "fix the browser and retry" instead of a false "filled" message.
        if not item.dscc_region_code:
            return BrowserResultStatus.FAILED_TERMINAL
        if async_playwright is None:
            return BrowserResultStatus.FAILED_RETRYABLE  # playwright not installed
        if not self.cdp_url:
            return BrowserResultStatus.FAILED_RETRYABLE  # DSCC must attach to a logged-in browser

        self._ensure_localhost_no_proxy()
        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.connect_over_cdp(self.cdp_url)
            except Exception:  # noqa: BLE001 - CDP unreachable / no debug browser.
                return BrowserResultStatus.FAILED_RETRYABLE

            try:
                page = await self._pick_open_page(browser)
                if page is None:
                    return BrowserResultStatus.FAILED_RETRYABLE  # no DSCC tab to drive
                page.set_default_timeout(STEP_TIMEOUT_MS)

                frame = page.frame_locator(DSCC["iframe"])
                await frame.locator(DSCC["continue"]).first.wait_for(state="visible")

                await self._welcome(frame)
                await self._network_domain(frame, item.network)
                await self._time(frame, item.network)
                await self._proxy(frame, item.network)
                await self._support_contact(frame, item.dscc_setup)
                await self._system(frame, item.dscc_setup)

                # STOP on the System screen with everything filled EXCEPT the credential. The
                # operator picks/creates the system secret (sensitive, and not reliably scriptable),
                # then clicks Continue -> reviews -> Submits. Confirm we're on System and return.
                await frame.locator(DSCC["credentials_select"]).wait_for(state="visible")
                return BrowserResultStatus.WAITING_FOR_OPERATOR
            except DsccSetupError:
                # Bad/missing work-item input (e.g. no contact name) — fix the data, then re-run.
                await self._dump(page, run_id, "operator-action")
                return BrowserResultStatus.FAILED_TERMINAL
            except PlaywrightTimeoutError:
                await self._dump(page, run_id, "timeout")
                return BrowserResultStatus.FAILED_RETRYABLE
            # Never close the operator's attached browser.

    # ------------------------------------------------------------------ screens

    async def _pick_open_page(self, browser):
        pages = [page for context in browser.contexts for page in context.pages]
        for page in pages:
            if DSCC_HOST_HINT in (page.url or ""):
                await page.bring_to_front()
                return page
        return pages[0] if pages else None

    async def _welcome(self, frame) -> None:
        # Welcome has only the "Get Started" footer button; click it to enter the wizard.
        await self._continue(frame)

    async def _network_domain(self, frame, net: NetworkConfig) -> None:
        # DNS carries over from cloudinit, but fill from config to guarantee correctness.
        inputs = DSCC["dns_inputs"]
        for index, value in enumerate(net.dns):
            if index >= len(inputs):
                await frame.locator(DSCC["dns_add"]).click()  # need another row
            selector = inputs[min(index, len(inputs) - 1)]
            await self._fill(frame, selector, value)
        await self._continue(frame)

    async def _time(self, frame, net: NetworkConfig) -> None:
        await self._fill(frame, DSCC["ntp_inputs"][0], net.ntp)
        # Region/city (timezone) carry over from cloudinit. Try to confirm them, but treat the
        # search-select as best-effort here — if it's already inherited we must not break it.
        region = net.timezone.split("/", 1)[0]
        await self._maybe_select(frame, DSCC["time_region_select"], region, region, exact=True)
        await self._maybe_select(frame, DSCC["time_city_select"], net.timezone, net.timezone, exact=False)
        await self._continue(frame)

    async def _proxy(self, frame, net: NetworkConfig) -> None:
        # Server/port are read-only value-text (inherited from cloudinit); only the type is set.
        # The radio is Grommet-styled (often a hidden input), and HTTP is usually already selected
        # from cloudinit, so this is best-effort: check() no-ops if it's already set.
        radio = DSCC["proxy_http_radio"] if net.proxy_host else DSCC["proxy_none_radio"]
        target = frame.locator(radio)
        try:
            if await target.count():
                await target.check()
        except PlaywrightTimeoutError:
            pass  # inherited selection stands
        await self._continue(frame)

    async def _support_contact(self, frame, cfg: DsccSetupConfig) -> None:
        missing = [
            name
            for name, value in (("contact_first_name", cfg.contact_first_name), ("contact_last_name", cfg.contact_last_name))
            if not value
        ]
        if missing:
            raise DsccSetupError(f"Support Contact requires {', '.join(missing)} in arrays.csv.")
        await self._fill(frame, DSCC["sc_first"], cfg.contact_first_name)
        await self._fill(frame, DSCC["sc_last"], cfg.contact_last_name)
        await self._select(frame, DSCC["sc_country_select"], cfg.country, cfg.country, exact=True)
        await self._select(frame, DSCC["sc_language_select"], cfg.contact_language, cfg.contact_language, exact=True)
        if cfg.contact_company:
            await self._fill(frame, DSCC["sc_company"], cfg.contact_company)
        if cfg.contact_phone:
            await self._fill(frame, DSCC["sc_phone"], cfg.contact_phone)
        if cfg.contact_email:
            await self._fill(frame, DSCC["sc_email"], cfg.contact_email)
        await self._continue(frame)

    async def _system(self, frame, cfg: DsccSetupConfig) -> None:
        # Fill system name + country only. The System Credentials secret is left to the operator
        # (it's sensitive and the Create-Secret modal is not reliably scriptable), so we stop here.
        await self._fill(frame, DSCC["system_name"], cfg.system_name)
        await self._select(frame, DSCC["system_country_select"], cfg.country, cfg.country, exact=True)

    # ------------------------------------------------------------------ helpers

    async def _continue(self, frame) -> None:
        await frame.locator(DSCC["continue"]).click()

    async def _fill(self, frame, selector: str, value: str) -> None:
        field = frame.locator(selector)
        await field.wait_for(state="visible")
        await field.click()
        await field.press("Control+a")
        await field.press("Delete")
        await field.press_sequentially(value, delay=20)  # key-by-key so React commits (see cloudinit)
        got = await field.input_value()
        if got != value:
            raise PlaywrightTimeoutError(f"Field {selector} did not accept value: got {got!r}, wanted {value!r}")

    async def _select(self, frame, trigger: str, search_text: str, option_text: str, *, exact: bool) -> None:
        # Grommet v2 searchable select: click trigger -> type in the search box -> click the option.
        await frame.locator(trigger).click()
        search = frame.locator(DSCC["select_search"]).first
        await search.wait_for(state="visible")
        await search.fill("")
        await search.press_sequentially(search_text, delay=20)
        await frame.get_by_role("option", name=option_text, exact=exact).first.click()

    async def _maybe_select(self, frame, trigger: str, search_text: str, option_text: str, *, exact: bool) -> None:
        """Select only if not already set (timezone is inherited from cloudinit; don't clobber it)."""
        loc = frame.locator(trigger)
        if not await loc.count():
            return
        current = (await loc.input_value()).strip()
        if current and option_text.lower() in current.lower():
            return
        try:
            await self._select(frame, trigger, search_text, option_text, exact=exact)
        except PlaywrightTimeoutError:
            pass  # inherited value stands; first-run verification will tell us if this matters

    @staticmethod
    def _ensure_localhost_no_proxy() -> None:
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
            await page.screenshot(path=str(self.artifact_dir / f"dscc-{run_id}-{label}.png"), full_page=True)
        except Exception:  # noqa: BLE001
            pass
