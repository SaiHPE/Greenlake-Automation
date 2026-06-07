#!/usr/bin/env python3
"""
HPE GreenLake Developer Portal - Full Documentation Scraper
============================================================
Scrapes the entire HPE GreenLake API documentation from:
https://developer.greenlake.hpe.com/

Uses the llms.txt index to discover all documentation pages,
then fetches each page's raw markdown content via the .md endpoint.

Output Structure:
  webscraper/
    scraped_docs/
      greenlake/
        services/
          <service-name>/
            *.md
        guides/
          *.md
        ...
    index.json          - Full index of all scraped pages
    scrape_report.md    - Summary report of the scrape
"""

import os
import sys
import io
import json
import time
import hashlib
import re
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# Configuration
# =============================================================================
BASE_URL = "https://developer.greenlake.hpe.com"
LLMS_TXT_URL = f"{BASE_URL}/llms.txt"
OUTPUT_DIR = Path(__file__).parent / "scraped_docs"
INDEX_FILE = Path(__file__).parent / "index.json"
REPORT_FILE = Path(__file__).parent / "scrape_report.md"

MAX_WORKERS = 5  # Concurrent download threads (be respectful)
REQUEST_DELAY = 0.3  # Seconds between requests per thread
REQUEST_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3
USER_AGENT = "HPE-GreenLake-DocScraper/1.0 (Internal Documentation Reference)"


# =============================================================================
# URL Discovery
# =============================================================================
def fetch_url(url, timeout=REQUEST_TIMEOUT):
    """Fetch a URL and return its content as string."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"  [!] Retry {attempt+1}/{MAX_RETRIES} for {url}: {e}")
                time.sleep(wait)
            else:
                raise


def parse_llms_txt(content):
    """Parse the llms.txt file to extract all documentation URLs."""
    urls = []
    for line in content.splitlines():
        line = line.strip()
        # Match markdown link pattern: [title](url)
        match = re.search(r'\[([^\]]+)\]\((https://[^\)]+\.md)\)', line)
        if match:
            title = match.group(1)
            url = match.group(2)
            urls.append({"title": title, "url": url})
    return urls


def discover_additional_urls():
    """
    Discover additional documentation pages not in llms.txt.
    These are known documentation entry points and guides.
    """
    additional = [
        # Main pages (without .md - these serve rendered HTML)
        {"title": "Services & Integrations Overview", "url": f"{BASE_URL}/docs/greenlake/services/overview.md"},
        {"title": "API Versioning Guide", "url": f"{BASE_URL}/docs/greenlake/guides.md"},
        {"title": "MCP Server Documentation", "url": f"{BASE_URL}/docs/greenlake/mcp-server/public.md"},
    ]
    return additional


# =============================================================================
# Content Fetching & Processing
# =============================================================================
def url_to_filepath(url):
    """Convert a URL to a local file path under scraped_docs/."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    # Remove leading /docs/ to avoid redundant nesting
    if path.startswith("/docs/"):
        path = path[len("/docs/"):]
    elif path.startswith("/"):
        path = path[1:]

    # Ensure it ends with .md
    if not path.endswith(".md"):
        path = path.rstrip("/") + ".md"

    return OUTPUT_DIR / path


def fetch_and_save_page(entry, index_lock=None):
    """Fetch a single documentation page and save it locally."""
    url = entry["url"]
    title = entry["title"]
    filepath = url_to_filepath(url)

    result = {
        "title": title,
        "url": url,
        "filepath": str(filepath.relative_to(Path(__file__).parent)),
        "status": "pending",
        "size_bytes": 0,
        "timestamp": None,
        "checksum": None,
        "error": None,
    }

    try:
        # Small delay to be respectful
        time.sleep(REQUEST_DELAY)

        content = fetch_url(url)

        if not content or len(content.strip()) < 10:
            result["status"] = "empty"
            result["error"] = "Empty or near-empty response"
            return result

        # Check if we got an HTML error page instead of markdown
        if content.strip().startswith("<!doctype") or content.strip().startswith("<html"):
            # Try to extract useful content from HTML if it's a Gatsby page-data approach
            # For .md URLs, the server should return raw markdown
            result["status"] = "html_response"
            result["error"] = "Got HTML instead of markdown - page may be JS-rendered only"
            # Still save it but note the issue
            pass

        # Create directory structure
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata header to the file
        header = f"""---
title: "{title}"
source_url: "{url}"
scraped_at: "{datetime.now(timezone.utc).isoformat()}Z"
---

"""
        full_content = header + content

        # Write the file
        filepath.write_text(full_content, encoding="utf-8")

        result["status"] = "success"
        result["size_bytes"] = len(full_content.encode("utf-8"))
        result["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"
        result["checksum"] = hashlib.md5(content.encode("utf-8")).hexdigest()

        print(f"  [OK] {title[:60]:.<62} {result['size_bytes']:>8,} bytes")

    except urllib.error.HTTPError as e:
        result["status"] = "http_error"
        result["error"] = f"HTTP {e.code}: {e.reason}"
        print(f"  [FAIL] {title[:60]:.<60} HTTP {e.code}")

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  [FAIL] {title[:60]:.<60} {str(e)[:40]}")

    return result


# =============================================================================
# Additional: Try to fetch OpenAPI/Swagger spec files
# =============================================================================
def discover_openapi_specs(doc_entries):
    """
    From the documentation entries, identify potential OpenAPI spec download URLs.
    Many HPE GreenLake services expose their OpenAPI specs as downloadable YAML/JSON.
    """
    openapi_urls = []
    seen = set()

    for entry in doc_entries:
        url = entry["url"]
        # Look for patterns like /openapi/ in the URL path
        if "/openapi/" in url:
            # Try to find the base openapi directory
            parts = url.split("/openapi/")
            if len(parts) == 2:
                base = parts[0] + "/openapi/"
                if base not in seen:
                    seen.add(base)
                    # Common spec file names
                    for spec_name in ["openapi.yaml", "openapi.json", "spec.yaml", "spec.json"]:
                        spec_url = base + spec_name
                        openapi_urls.append({
                            "title": f"OpenAPI Spec: {spec_name} from {base.split('/services/')[-1] if '/services/' in base else base}",
                            "url": spec_url,
                        })

    return openapi_urls


# =============================================================================
# Also scrape the Gatsby page-data JSON for each page
# =============================================================================
def fetch_page_data_json(url):
    """
    For Gatsby sites, try to fetch the page-data JSON which contains
    the actual rendered content and metadata.
    """
    parsed = urllib.parse.urlparse(url)
    path = parsed.path

    # Remove .md extension and construct page-data URL
    if path.endswith(".md"):
        path = path[:-3]

    # Gatsby page-data pattern
    page_data_url = f"{BASE_URL}/page-data{path}/data.json"

    try:
        content = fetch_url(page_data_url, timeout=15)
        return json.loads(content)
    except Exception:
        return None


# =============================================================================
# Report Generation
# =============================================================================
def generate_report(results, start_time, end_time):
    """Generate a markdown report of the scraping results."""
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ("error", "http_error"))
    empty = sum(1 for r in results if r["status"] == "empty")
    html_only = sum(1 for r in results if r["status"] == "html_response")
    total_bytes = sum(r["size_bytes"] for r in results)

    duration = end_time - start_time

    # Group by service
    services = {}
    for r in results:
        url = r["url"]
        if "/services/" in url:
            service = url.split("/services/")[1].split("/")[0]
        elif "/guides/" in url:
            service = "guides"
        elif "/community/" in url:
            service = "community"
        elif "/mcp-server/" in url:
            service = "mcp-server"
        elif "/iam/" in url:
            service = "iam"
        else:
            service = "other"
        if service not in services:
            services[service] = []
        services[service].append(r)

    report = f"""# HPE GreenLake API Documentation - Scrape Report

**Scraped at:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Duration:** {duration:.1f} seconds
**Source:** {BASE_URL}

## Summary

| Metric | Count |
|--------|-------|
| Total pages discovered | {total} |
| Successfully scraped | {success} |
| Failed (HTTP errors) | {failed} |
| Empty responses | {empty} |
| HTML-only (JS rendered) | {html_only} |
| Total data downloaded | {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB) |

## Services Scraped ({len(services)} services)

| Service | Pages | Status |
|---------|-------|--------|
"""
    for svc in sorted(services.keys()):
        pages = services[svc]
        ok = sum(1 for p in pages if p["status"] == "success")
        total_svc = len(pages)
        status = "OK" if ok == total_svc else f"PARTIAL {ok}/{total_svc}"
        report += f"| {svc} | {total_svc} | {status} |\n"

    report += "\n## Detailed Results\n\n"

    for svc in sorted(services.keys()):
        report += f"\n### {svc}\n\n"
        for r in sorted(services[svc], key=lambda x: x["url"]):
            status_icon = "OK" if r["status"] == "success" else "FAIL"
            size_str = f"{r['size_bytes']:,} bytes" if r["size_bytes"] > 0 else "N/A"
            report += f"- {status_icon} [{r['title']}]({r['url']}) — {size_str}"
            if r["error"]:
                report += f" — *{r['error']}*"
            report += "\n"

    # Failed pages section
    failures = [r for r in results if r["status"] not in ("success",)]
    if failures:
        report += "\n## Failed Pages\n\n"
        for r in failures:
            report += f"- **{r['title']}**: `{r['url']}` — {r['error'] or r['status']}\n"

    return report


# =============================================================================
# Main Execution
# =============================================================================
def main():
    print("=" * 70)
    print("  HPE GreenLake Developer Portal - Full Documentation Scraper")
    print("=" * 70)
    print()

    # Step 1: Fetch llms.txt index
    print("[1/5] Fetching documentation index from llms.txt...")
    try:
        llms_content = fetch_url(LLMS_TXT_URL)
        entries = parse_llms_txt(llms_content)
        print(f"  Found {len(entries)} documentation pages in llms.txt")
        sys.stdout.flush()
    except Exception as e:
        print(f"  [FAIL] Failed to fetch llms.txt: {e}")
        sys.exit(1)

    # Save the raw llms.txt
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "_llms.txt").write_text(llms_content, encoding="utf-8")

    # Step 2: Deduplicate URLs
    print("\n[2/5] Deduplicating URLs...")
    seen_urls = set()
    unique_entries = []
    for entry in entries:
        if entry["url"] not in seen_urls:
            seen_urls.add(entry["url"])
            unique_entries.append(entry)
    print(f"  {len(unique_entries)} unique pages to scrape (removed {len(entries) - len(unique_entries)} duplicates)")

    # Step 3: Fetch all pages
    print(f"\n[3/5] Scraping {len(unique_entries)} documentation pages...")
    print(f"  Using {MAX_WORKERS} concurrent workers with {REQUEST_DELAY}s delay")
    print("-" * 70)

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_and_save_page, entry): entry
            for entry in unique_entries
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    end_time = time.time()
    print("-" * 70)

    # Step 4: Try to also fetch page-data JSONs for key pages
    print(f"\n[4/5] Fetching supplementary page-data JSONs for key service pages...")
    page_data_dir = OUTPUT_DIR / "_page_data"
    page_data_dir.mkdir(parents=True, exist_ok=True)

    # Identify key service overview pages
    key_pages = [e for e in unique_entries if e["url"].endswith("/public.md") or e["url"].endswith("/overview.md")]
    pd_count = 0
    for entry in key_pages:
        try:
            time.sleep(REQUEST_DELAY)
            pd = fetch_page_data_json(entry["url"])
            if pd:
                # Save page-data JSON
                url_path = urllib.parse.urlparse(entry["url"]).path
                if url_path.endswith(".md"):
                    url_path = url_path[:-3]
                safe_name = url_path.replace("/", "_").strip("_") + ".json"
                (page_data_dir / safe_name).write_text(
                    json.dumps(pd, indent=2), encoding="utf-8"
                )
                pd_count += 1
        except Exception:
            pass
    print(f"  Fetched {pd_count} page-data JSONs")

    # Step 5: Generate index and report
    print(f"\n[5/5] Generating index and report...")

    # Sort results by URL for consistent output
    results.sort(key=lambda r: r["url"])

    # Save index
    now_str = datetime.now(timezone.utc).isoformat() + "Z"
    index_data = {
        "scraped_at": now_str,
        "source": BASE_URL,
        "total_pages": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "pages": results,
    }
    INDEX_FILE.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print(f"  Index saved to: {INDEX_FILE}")

    # Generate report
    report = generate_report(results, start_time, end_time)
    # Replace any remaining Unicode in report for Windows compat
    report = report.encode('ascii', errors='replace').decode('ascii')
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"  Report saved to: {REPORT_FILE}")

    # Final summary
    success = sum(1 for r in results if r["status"] == "success")
    total_bytes = sum(r["size_bytes"] for r in results)
    print()
    print("=" * 70)
    print(f"  SCRAPE COMPLETE")
    print(f"  Pages: {success}/{len(results)} successful")
    print(f"  Data:  {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB)")
    print(f"  Time:  {end_time - start_time:.1f} seconds")
    print(f"  Docs:  {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
