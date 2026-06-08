from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture cloudinit UI screenshots, HTML, text, and locator candidates."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Cloudinit URL, for example https://169.254.239.27/cloudinit.",
    )
    parser.add_argument(
        "--out",
        default=".alletra_onboard/ui-captures/cloudinit",
        help="Output directory for captured artifacts.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chromium headless. For capture work, leave this off.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=60000,
        help="Navigation timeout in milliseconds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.url.startswith("https://169.254."):
        print("Refusing to capture cloudinit from a non-link-local HTTPS URL.", file=sys.stderr)
        print("Expected a URL like https://169.254.x.x/cloudinit.", file=sys.stderr)
        return 2

    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    print_safety_notice(output_dir)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
        page = context.new_page()

        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        except PlaywrightTimeoutError:
            print("Navigation timed out. Capturing the current browser state if available.")

        capture_index = 1
        capture_snapshot(page, output_dir, capture_index, "initial")
        capture_index += 1

        while True:
            print()
            print("Use the browser window to move to the next cloudinit screen.")
            label = input("Capture label, Enter for auto name, or q to quit: ").strip()
            if label.lower() in {"q", "quit", "exit"}:
                break
            if not label:
                label = f"screen-{capture_index}"
            capture_snapshot(page, output_dir, capture_index, label)
            capture_index += 1

        context.close()
        browser.close()

    print(f"Capture complete. Artifacts are under: {output_dir.resolve()}")
    return 0


def print_safety_notice(output_dir: Path) -> None:
    print("Cloudinit UI capture helper")
    print(f"Output directory: {output_dir.resolve()}")
    print("This saves screenshots, sanitized HTML, visible text, and locator candidates.")
    print("Do not enter real passwords, MFA codes, real subscription keys, or customer secrets before capturing.")
    print("HTML/control metadata blanks input values, but screenshots capture whatever is visible on screen.")
    print()


def capture_snapshot(page: Any, output_dir: Path, index: int, label: str) -> None:
    name = f"{index:02d}-{slug(label)}"
    screenshot_path = output_dir / f"{name}.png"
    html_path = output_dir / f"{name}.html"
    text_path = output_dir / f"{name}.txt"
    controls_path = output_dir / f"{name}.controls.json"
    metadata_path = output_dir / f"{name}.metadata.json"

    page.screenshot(path=str(screenshot_path), full_page=True)
    html_path.write_text(sanitized_html(page), encoding="utf-8")
    text_path.write_text(visible_text(page), encoding="utf-8")
    write_json(controls_path, control_candidates(page))
    write_json(
        metadata_path,
        {
            "captured_at": datetime.now(UTC).isoformat(),
            "label": label,
            "url": page.url,
            "title": safe_title(page),
            "files": {
                "screenshot": screenshot_path.name,
                "html": html_path.name,
                "text": text_path.name,
                "controls": controls_path.name,
            },
        },
    )
    print(f"Saved {name}: screenshot, HTML, visible text, controls, metadata")


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
            return '<!doctype html>\n' + clone.outerHTML;
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
        )).slice(0, 700).map((element) => {
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


def safe_title(page: Any) -> str:
    try:
        return page.title()
    except Exception:  # noqa: BLE001 - capture should continue even on odd browser states.
        return ""


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def slug(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return normalized or "screen"


if __name__ == "__main__":
    raise SystemExit(main())
