"""Capture the Alletra MP Cloud Connectivity Wizard (cloudinit) UI for locator authoring.

Run this ON THE JUMP SERVER (the only host that can reach the array's link-local IP).
It launches its own Chromium, lets you step through the wizard manually, and at each
screen saves everything needed to later write robust Playwright locators:

    <NN>-<label>.png             full-page screenshot
    <NN>-<label>.html            sanitized HTML (input values blanked, secrets redacted)
    <NN>-<label>.txt             visible text
    <NN>-<label>.controls.json   locator candidates (incl. shadow DOM, iframes,
                                 data-testid/data-*, <select> options, computed labels)
    <NN>-<label>.aria.json       accessibility tree snapshot (best source for get_by_role)
    <NN>-<label>.metadata.json   url, title, frame list, counts
    manifest.json                running index of every captured screen

No package imports — only Playwright is required:
    python -m pip install playwright
    python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - operator guidance path.
    print(
        "Playwright is not installed. Run:\n"
        "  python -m pip install playwright\n"
        "  python -m playwright install chromium",
        file=sys.stderr,
    )
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# Shared DOM harvester (kept inline so this script is standalone/portable).
# Pierces open shadow roots; run per-frame from Python for iframe coverage.
# ---------------------------------------------------------------------------

HARVEST_JS = r"""
() => {
  const SELECTORS = 'button,a,input,textarea,select,label,h1,h2,h3,h4,h5,'
    + '[role],[aria-label],[placeholder],[data-testid],[contenteditable="true"]';
  const out = [];
  const seenRoots = new Set();
  function computedLabel(el){
    try{
      const aria = el.getAttribute('aria-label'); if(aria) return aria.trim();
      const lb = el.getAttribute('aria-labelledby');
      if(lb){
        const root = el.getRootNode();
        const t = lb.split(/\s+/).map(id => {
          const n = (root && root.getElementById ? root.getElementById(id) : null)
                    || document.getElementById(id);
          return n ? (n.innerText || n.textContent || '') : '';
        }).join(' ').trim();
        if(t) return t;
      }
      if(el.id){
        const root = el.getRootNode();
        const lab = root && root.querySelector
          ? root.querySelector('label[for="' + CSS.escape(el.id) + '"]') : null;
        if(lab) return (lab.innerText || lab.textContent || '').trim();
      }
      const wrap = el.closest ? el.closest('label') : null;
      if(wrap) return (wrap.innerText || wrap.textContent || '').trim();
      const ph = el.getAttribute('placeholder'); if(ph) return ph.trim();
    }catch(e){}
    return '';
  }
  function dataAttrs(el){
    const d = {};
    try{ for(const a of el.attributes){ if(a.name.indexOf('data-') === 0) d[a.name] = a.value; } }catch(e){}
    return d;
  }
  function options(el){
    try{
      if(el.tagName === 'SELECT'){
        return Array.from(el.options).map(o => ({
          value: o.value, text: (o.textContent || '').trim(), selected: o.selected
        }));
      }
    }catch(e){}
    return undefined;
  }
  function rec(el){
    let rect = {}; try{ rect = el.getBoundingClientRect(); }catch(e){}
    const tag = el.tagName ? el.tagName.toLowerCase() : '';
    const get = n => { try{ return el.getAttribute(n) || ''; }catch(e){ return ''; } };
    return {
      tag, type: get('type'), role: get('role'),
      text: (el.innerText || el.textContent || '').trim().slice(0, 300),
      label: computedLabel(el), ariaLabel: get('aria-label'),
      name: get('name'), id: el.id || '', testid: get('data-testid'),
      placeholder: get('placeholder'), title: get('title'),
      href: (get('href') || '').split('?')[0],
      data: dataAttrs(el), options: options(el),
      disabled: !!el.disabled,
      visible: rect.width > 0 && rect.height > 0,
      x: Math.round(rect.x || 0), y: Math.round(rect.y || 0),
      width: Math.round(rect.width || 0), height: Math.round(rect.height || 0)
    };
  }
  function walk(root, depth){
    if(!root || depth > 8 || seenRoots.has(root)) return;
    seenRoots.add(root);
    let all; try{ all = root.querySelectorAll('*'); }catch(e){ return; }
    for(const el of all){
      try{ if(el.matches && el.matches(SELECTORS)) out.push(rec(el)); }catch(e){}
      if(el.shadowRoot) walk(el.shadowRoot, depth + 1);
      if(out.length > 2000) return;
    }
  }
  walk(document, 0);
  return out.slice(0, 2000);
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture cloudinit UI screenshots, HTML, text, accessibility tree, and locator candidates."
    )
    parser.add_argument("--url", required=True, help="Cloudinit URL, e.g. https://169.254.239.27/cloudinit.")
    parser.add_argument("--out", default=".alletra_onboard/ui-captures/cloudinit", help="Output directory.")
    parser.add_argument("--headless", action="store_true", help="Run headless (leave OFF for capture work).")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Navigation timeout in milliseconds.")
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
            settle(page)
        except PlaywrightTimeoutError:
            print("Navigation timed out. Capturing the current browser state if available.")

        capture_index = 1
        safe_capture(page, output_dir, capture_index, "initial")
        capture_index += 1

        while True:
            print()
            print("Tip: open every dropdown (timezone/region/country) BEFORE capturing so its options are recorded.")
            print("Use the browser window to move to the next cloudinit screen.")
            label = input("Capture label, Enter for auto name, or q to quit: ").strip()
            if label.lower() in {"q", "quit", "exit"}:
                break
            if not label:
                label = f"screen-{capture_index}"
            safe_capture(page, output_dir, capture_index, label)
            capture_index += 1

        context.close()
        browser.close()

    print(f"Capture complete. Artifacts are under: {output_dir.resolve()}")
    return 0


def print_safety_notice(output_dir: Path) -> None:
    print("Cloudinit UI capture helper")
    print(f"Output directory: {output_dir.resolve()}")
    print("Saves screenshots, sanitized HTML, visible text, accessibility tree, and locator candidates.")
    print("Do NOT enter real passwords, MFA codes, real subscription keys, or customer secrets before capturing.")
    print("HTML/control metadata blanks input values, but screenshots capture whatever is visible on screen.")
    print()


def settle(page: Any, ms: int = 1500) -> None:
    try:
        page.wait_for_timeout(ms)
    except Exception:  # noqa: BLE001
        pass


def safe_capture(page: Any, output_dir: Path, index: int, label: str) -> None:
    """Capture one screen; never let a single bad screen crash the session."""
    try:
        capture_snapshot(page, output_dir, index, label)
    except Exception as exc:  # noqa: BLE001 - capture must survive odd page states.
        print(f"WARNING: capture of {label!r} hit an error and was partially skipped: {exc}")


def capture_snapshot(page: Any, output_dir: Path, index: int, label: str) -> None:
    name = f"{index:02d}-{slug(label)}"
    screenshot_path = output_dir / f"{name}.png"
    html_path = output_dir / f"{name}.html"
    text_path = output_dir / f"{name}.txt"
    controls_path = output_dir / f"{name}.controls.json"
    aria_path = output_dir / f"{name}.aria.json"
    metadata_path = output_dir / f"{name}.metadata.json"

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:  # noqa: BLE001 - some states block full_page; fall back to viewport.
        page.screenshot(path=str(screenshot_path))

    html_path.write_text(sanitized_html(page), encoding="utf-8")
    text_path.write_text(visible_text(page), encoding="utf-8")
    controls = harvest_controls(page)
    write_json(controls_path, controls)
    write_json(aria_path, aria_snapshot(page))

    frames = [f.url for f in page.frames]
    metadata = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "url": page.url,
        "title": safe_title(page),
        "frame_count": len(frames),
        "frames": frames,
        "control_count": len(controls),
        "files": {
            "screenshot": screenshot_path.name,
            "html": html_path.name,
            "text": text_path.name,
            "controls": controls_path.name,
            "aria": aria_path.name,
        },
    }
    write_json(metadata_path, metadata)
    append_manifest(output_dir, metadata)
    print(f"Saved {name}: screenshot, HTML, text, {len(controls)} controls, aria tree, metadata")


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


def harvest_controls(page: Any) -> list[dict[str, Any]]:
    """Run the harvester in every frame (covers cross-origin iframes); tag each by frame URL."""
    results: list[dict[str, Any]] = []
    for frame in page.frames:
        try:
            items = frame.evaluate(HARVEST_JS)
        except Exception as exc:  # noqa: BLE001 - a frame may be detached/cross-origin-restricted.
            results.append({"_frame_error": str(exc), "frame": frame.url})
            continue
        for item in items:
            item["frame"] = frame.url
        results.extend(items)
    return results


def aria_snapshot(page: Any) -> Any:
    try:
        return page.accessibility.snapshot(interesting_only=False)
    except Exception as exc:  # noqa: BLE001
        return {"_aria_error": str(exc)}


def append_manifest(output_dir: Path, metadata: dict[str, Any]) -> None:
    manifest_path = output_dir / "manifest.json"
    entries: list[dict[str, Any]] = []
    if manifest_path.exists():
        try:
            entries = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            entries = []
    entries.append(
        {
            "label": metadata["label"],
            "url": metadata["url"],
            "title": metadata["title"],
            "control_count": metadata["control_count"],
            "frame_count": metadata["frame_count"],
            "files": metadata["files"],
            "captured_at": metadata["captured_at"],
        }
    )
    write_json(manifest_path, entries)


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
