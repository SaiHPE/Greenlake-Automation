from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - operator guidance path.
    print(
        "Playwright is not installed. From Provisioning_Automation/alletra_onboard run:\n"
        "  python -m pip install -e .[dev]\n"
        "  python -m playwright install chromium",
        file=sys.stderr,
    )
    raise SystemExit(2)


ALLOWED_CDP_HOSTS = {"localhost", "127.0.0.1", "::1"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture DSCC Setup UI screenshots, HTML, text, and locator candidates over CDP."
    )
    parser.add_argument(
        "--region",
        default="jp1",
        help="DSCC region code, for example jp1, us1, eu1, or uk1.",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Optional DSCC URL to open. Defaults to https://console-{region}.data.cloud.hpe.com.",
    )
    parser.add_argument(
        "--cdp-url",
        default="http://localhost:9222",
        help="Chrome/Edge CDP URL. Must be bound to localhost.",
    )
    parser.add_argument(
        "--out",
        default=".alletra_onboard/ui-captures/dscc",
        help="Output directory for captured artifacts.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=90000,
        help="Navigation timeout in milliseconds.",
    )
    parser.add_argument(
        "--no-navigate",
        action="store_true",
        help="Do not navigate; capture the DSCC tab you already have open (use once you're on the wizard).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not is_local_cdp_url(args.cdp_url):
        print("Refusing to connect to a non-local CDP endpoint.", file=sys.stderr)
        print("Start Chrome/Edge with remote debugging bound to localhost only.", file=sys.stderr)
        return 2

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_url = args.url or f"https://console-{args.region}.data.cloud.hpe.com"
    print_safety_notice(output_dir, args.cdp_url, target_url)

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(args.cdp_url)
        if not browser.contexts:
            print("No browser context was available from CDP. Open Chrome/Edge first, then retry.", file=sys.stderr)
            return 2

        page = pick_page(browser, target_url)
        if page is None:
            print("No open tab found in the attached browser. Open a DSCC tab, then retry.", file=sys.stderr)
            return 2

        if not args.no_navigate:
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
            except PlaywrightTimeoutError:
                print("Navigation timed out. Capturing the current browser state if available.")

        if looks_like_login(page.url):
            print("The current page looks like a login/SSO page.")
            print("Log in manually in the attached browser, then capture the DSCC shell screen.")

        capture_index = 1
        safe_capture(page, output_dir, capture_index, "initial")
        capture_index += 1

        while True:
            print()
            print("Use the attached browser to move to the next DSCC Setup screen.")
            label = input("Capture label, Enter for auto name, or q to quit: ").strip()
            if label.lower() in {"q", "quit", "exit"}:
                break
            if not label:
                label = f"screen-{capture_index}"
            safe_capture(page, output_dir, capture_index, label)
            capture_index += 1

        # Do not close the operator's attached Chrome/Edge session. Let process exit drop CDP only.

    print(f"Capture complete. Artifacts are under: {output_dir.resolve()}")
    return 0


def pick_page(browser: Any, target_url: str) -> Any:
    """Prefer a tab already on the DSCC host (data.cloud.hpe.com); else the last real tab."""
    pages = [p for ctx in browser.contexts for p in ctx.pages]
    host = urlparse(target_url).hostname or ""
    base = host.split(".", 1)[-1] if "." in host else host  # data.cloud.hpe.com
    for page in pages:
        if base and base in (urlparse(page.url).hostname or ""):
            try:
                page.bring_to_front()
            except Exception:  # noqa: BLE001
                pass
            return page
    real = [p for p in pages if p.url and not p.url.startswith(("about:", "edge:", "chrome:"))]
    if real:
        return real[-1]
    if pages:
        return pages[-1]
    return browser.contexts[0].new_page() if browser.contexts else None


def print_safety_notice(output_dir: Path, cdp_url: str, target_url: str) -> None:
    print("DSCC UI capture helper")
    print(f"CDP URL: {cdp_url}")
    print(f"Target URL: {target_url}")
    print(f"Output directory: {output_dir.resolve()}")
    print("This attaches to an already-open, already-authenticated Chrome/Edge session.")
    print("This does not collect passwords, MFA codes, cookies, local storage, or API tokens directly.")
    print("It saves screenshots, sanitized HTML, visible text, and locator candidates.")
    print("Do not capture screens with visible passwords, MFA codes, real subscription keys, or customer secrets.")
    print()


def safe_capture(page: Any, output_dir: Path, index: int, label: str) -> None:
    """Capture one screen; never let a single bad screen crash the whole session."""
    try:
        capture_snapshot(page, output_dir, index, label)
    except Exception as exc:  # noqa: BLE001 - capture must survive odd page states.
        print(f"WARNING: capture of {label!r} hit an error and was partially skipped: {exc}")


def capture_snapshot(page: Any, output_dir: Path, index: int, label: str) -> None:
    name = f"{index:02d}-{slug(label)}"
    # The screenshot is page-level (it already shows iframe content visually).
    page.screenshot(path=str(output_dir / f"{name}.png"), full_page=True)
    _dump_document(page, output_dir, name, label, page.url, screenshot=f"{name}.png")

    # The DSCC Setup wizard renders inside a micro-app IFRAME (data-test-id="setup-iframe",
    # name="micro-app-setup"), so the real form fields are NOT in the top document — they live
    # in a child frame. Dump every http(s) child frame so locators are actually captured.
    frames = [f for f in page.frames if f is not page.main_frame and str(f.url).startswith("http")]
    for i, frame in enumerate(frames, start=1):
        try:
            _dump_document(frame, output_dir, f"{name}.frame{i}", f"{label} (frame {i})", frame.url)
        except Exception as exc:  # noqa: BLE001 - one odd frame must not abort the capture.
            print(f"  WARNING: frame {i} ({str(frame.url)[:60]}) skipped: {exc}")
    print(f"Saved {name}: screenshot + top document + {len(frames)} frame document(s)")


def _dump_document(
    target: Any, output_dir: Path, name: str, label: str, url: str, screenshot: str | None = None
) -> None:
    """Dump HTML + visible text + control candidates for one document (a page OR a frame)."""
    html_path = output_dir / f"{name}.html"
    text_path = output_dir / f"{name}.txt"
    controls_path = output_dir / f"{name}.controls.json"
    metadata_path = output_dir / f"{name}.metadata.json"

    html_path.write_text(sanitized_html(target), encoding="utf-8")
    text_path.write_text(visible_text(target), encoding="utf-8")
    write_json(controls_path, control_candidates(target))
    files = {"html": html_path.name, "text": text_path.name, "controls": controls_path.name}
    if screenshot:
        files["screenshot"] = screenshot
    write_json(
        metadata_path,
        {
            "captured_at": datetime.now(UTC).isoformat(),
            "label": label,
            "url": url,
            "login_like_url": looks_like_login(url),
            "files": files,
        },
    )


def sanitized_html(page: Any) -> str:
    return page.evaluate(
        """
        () => {
            const clone = document.documentElement.cloneNode(true);
            clone.querySelectorAll('script').forEach((element) => element.remove());
            clone.querySelectorAll('input, textarea').forEach((element) => {
                element.setAttribute('value', '');
                element.textContent = '';
                const type = (element.getAttribute('type') || '').toLowerCase();
                if (type === 'password' || type === 'hidden') {
                    element.setAttribute('value', '<redacted>');
                }
            });
            return '<!doctype html>\\n' + clone.outerHTML;
        }
        """
    )


def visible_text(page: Any) -> str:
    return page.evaluate("() => document.body ? document.body.innerText : ''")


def control_candidates(page: Any) -> list[dict[str, Any]]:
    return page.evaluate(
        """
        () => Array.from(document.querySelectorAll(
            'button,a,input,textarea,select,label,h1,h2,h3,h4,[role],[aria-label],[placeholder]'
        )).slice(0, 900).map((element) => {
            const rect = element.getBoundingClientRect();
            const tag = element.tagName.toLowerCase();
            const type = element.getAttribute('type') || '';
            const href = element.getAttribute('href') || '';
            return {
                tag,
                type,
                role: element.getAttribute('role') || '',
                text: (element.innerText || element.textContent || '').trim().slice(0, 300),
                ariaLabel: element.getAttribute('aria-label') || '',
                labelFor: element.getAttribute('for') || '',
                name: element.getAttribute('name') || '',
                id: element.id || '',
                dataTestId: element.getAttribute('data-test-id') || '',
                placeholder: element.getAttribute('placeholder') || '',
                title: element.getAttribute('title') || '',
                href: href.split('?')[0],
                visible: rect.width > 0 && rect.height > 0,
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height)
            };
        })
        """
    )


def is_local_cdp_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and parsed.hostname in ALLOWED_CDP_HOSTS


def looks_like_login(url: str) -> bool:
    lowered = url.lower()
    return any(marker in lowered for marker in ("login", "signin", "sso", "oauth", "authorize"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return normalized or "screen"


if __name__ == "__main__":
    raise SystemExit(main())
