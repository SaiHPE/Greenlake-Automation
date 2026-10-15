#!/usr/bin/env python3
"""
HPE GreenLake Developer Portal - Full Documentation Scraper
============================================================
Scrapes the entire HPE GreenLake API documentation from:
https://developer.greenlake.hpe.com/

Recursively crawls all internal markdown pages, downloads all visual assets,
and grabs the raw OpenAPI specification files (.yaml and .json).

Output Structure:
  webscraper/
    scraped_docs/
      greenlake/
        services/
          <service-name>/
            *.md
            *.yaml
            *.json
        guides/
          *.md
        assets/
          *.png
          *.jpg
          ...
    index.json          - Full index of all scraped pages
    scrape_report.md    - Summary report of the scrape
"""

import os
import sys
import json
import time
import hashlib
import re
import urllib.request
import urllib.error
import urllib.parse
import queue
import threading
import shutil
from datetime import datetime, timezone
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================
BASE_URL = "https://developer.greenlake.hpe.com"
LLMS_TXT_URL = f"{BASE_URL}/llms.txt"
OUTPUT_DIR = Path(__file__).parent / "scraped_docs"
INDEX_FILE = Path(__file__).parent / "index.json"
REPORT_FILE = Path(__file__).parent / "scrape_report.md"
ROOT_DOCS_DIR = Path(__file__).parent.parent / "docs and plans" / "greenlake_api_docs"

MAX_WORKERS = 10  # Concurrent download threads
REQUEST_DELAY = 0.1  # Seconds between requests per thread to be respectful
REQUEST_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3
USER_AGENT = "HPE-GreenLake-DocScraper/2.0 (Internal Documentation Reference)"

VALID_EXTENSIONS = ('.md', '.yaml', '.yml', '.json', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.pdf', '.zip', '.txt')

# =============================================================================
# Helper Functions
# =============================================================================
def fetch_url_bytes(url, timeout=REQUEST_TIMEOUT):
    """Fetch a URL and return its content as bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise


def parse_llms_txt(content):
    """Parse the llms.txt file to extract all seed documentation URLs."""
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


def extract_links(content):
    """Extract markdown, image, and HTML links from text content."""
    links = []
    
    # 1. Match Markdown links (and image links)
    # Syntax: [label](url) or ![alt](url)
    markdown_pattern = r'!?\[([^\]]*)\]\(([^)#\s]+)\)'
    for match in re.finditer(markdown_pattern, content):
        text = match.group(1).strip()
        url = match.group(2).strip()
        links.append((text, url))
        
    # 2. Match HTML href links
    html_pattern = r'href=["\']([^"\']+)["\']'
    for match in re.finditer(html_pattern, content):
        url = match.group(1).strip()
        links.append(("", url))
        
    # 3. Match HTML src links (for images)
    src_pattern = r'src=["\']([^"\']+)["\']'
    for match in re.finditer(src_pattern, content):
        url = match.group(1).strip()
        links.append(("", url))
        
    return links


def normalise_url(url, current_url):
    """Resolve and normalise a URL relative to current_url."""
    # Resolve relative URL
    url = urllib.parse.urljoin(current_url, url)
    # Split fragment and query
    url = url.split("#")[0].split("?")[0].strip()
    
    if not url.startswith("https://developer.greenlake.hpe.com"):
        return None
        
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    
    # Exclude Gatsby framework JSON files from crawling
    if "/page-data/" in path or "app-data.json" in path or "webpack.stats.json" in path:
        return None
        
    # If path is empty, it's just the homepage
    if not path or path == "/":
        return url
        
    # Check if path has an extension
    _, ext = os.path.splitext(path)
    if not ext:
        # If it's a documentation path, append .md (Gatsby serves raw source at .md)
        if any(x in path for x in ["/docs/", "/guides/", "/community/", "/mcp-server/", "/services/", "/iam/", "/scim"]):
            path = path.rstrip("/") + ".md"
            url = parsed._replace(path=path).geturl()
            
    return url


def url_to_filepath(url):
    """Convert a URL to a local file path under scraped_docs/."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    
    # Strip leading slash
    if path.startswith("/"):
        path = path[1:]
        
    # Remove prefix /docs/ or /_bundle/docs/ to keep folder structure clean
    if path.startswith("_bundle/docs/"):
        path = path[len("_bundle/docs/"):]
    elif path.startswith("docs/"):
        path = path[len("docs/"):]
        
    # Ensure it ends with proper extension or .md if none
    _, ext = os.path.splitext(path)
    if not ext:
        path = path.rstrip("/") + ".md"
        
    return OUTPUT_DIR / path


# =============================================================================
# Gatsby page-data JSON Fetcher
# =============================================================================
def fetch_page_data_json(url):
    """Fetch the page-data JSON which contains rendered metadata."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path

    if path.endswith(".md"):
        path = path[:-3]

    page_data_url = f"{BASE_URL}/page-data{path}/data.json"
    try:
        content = fetch_url_bytes(page_data_url, timeout=15)
        return json.loads(content.decode("utf-8", errors="replace"))
    except Exception:
        return None


# =============================================================================
# Recursive Crawler
# =============================================================================
class GreenLakeCrawler:
    def __init__(self, seed_entries):
        self.visited = set()
        self.results = []
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.active_workers = 0
        self.active_workers_lock = threading.Lock()
        
        # Add initial seed entries
        for entry in seed_entries:
            self.add_to_queue(entry["url"], entry["title"])

    def add_to_queue(self, url, title=""):
        norm_url = normalise_url(url, BASE_URL)
        if not norm_url:
            return
            
        with self.lock:
            if norm_url not in self.visited:
                self.visited.add(norm_url)
                self.queue.put((norm_url, title))

    def worker(self):
        while True:
            try:
                # Retrieve next URL from queue
                url, title = self.queue.get(timeout=1.0)
            except queue.Empty:
                # If queue is empty, check if other workers are still running.
                with self.active_workers_lock:
                    if self.active_workers == 0:
                        break
                time.sleep(0.1)
                continue

            # Increment active workers
            with self.active_workers_lock:
                self.active_workers += 1

            try:
                self.process_url(url, title)
            except Exception as e:
                print(f"  [!] Unhandled exception processing {url}: {e}")
            finally:
                # Decrement active workers and mark queue task done
                with self.active_workers_lock:
                    self.active_workers -= 1
                self.queue.task_done()

    def process_url(self, url, title):
        time.sleep(REQUEST_DELAY)
        
        filepath = url_to_filepath(url)
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        _, ext = os.path.splitext(path)
        
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
            content_bytes = fetch_url_bytes(url)
            
            if not content_bytes or len(content_bytes) == 0:
                result["status"] = "empty"
                result["error"] = "Empty response"
                with self.lock:
                    self.results.append(result)
                return

            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # If it's a markdown file, we decode, parse for links, add frontmatter, and save
            if url.endswith(".md"):
                content = content_bytes.decode("utf-8", errors="replace")
                
                # Parse for recursive links
                links = extract_links(content)
                for link_text, link_url in links:
                    norm_url = normalise_url(link_url, url)
                    if norm_url:
                        parsed_norm = urllib.parse.urlparse(norm_url)
                        _, norm_ext = os.path.splitext(parsed_norm.path)
                        if norm_ext in VALID_EXTENSIONS or not norm_ext:
                            self.add_to_queue(norm_url, link_text)
                            
                # Prepend YAML frontmatter
                header = f"""---
title: "{title}"
source_url: "{url}"
scraped_at: "{datetime.now(timezone.utc).isoformat()}Z"
---

"""
                full_content = header + content
                filepath.write_text(full_content, encoding="utf-8")
                result["size_bytes"] = len(full_content.encode("utf-8"))
            else:
                # Save binary / OpenAPI specs / other files directly
                filepath.write_bytes(content_bytes)
                result["size_bytes"] = len(content_bytes)
                
            result["status"] = "success"
            result["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"
            result["checksum"] = hashlib.md5(content_bytes).hexdigest()
            
            print(f"  [OK] {title[:30]:.<32} {result['size_bytes']:>8,} bytes ({os.path.basename(path)})")
            
        except urllib.error.HTTPError as e:
            result["status"] = "http_error"
            result["error"] = f"HTTP {e.code}: {e.reason}"
            print(f"  [FAIL] {title[:30]:.<30} HTTP {e.code} ({os.path.basename(path)})")
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"  [FAIL] {title[:30]:.<30} {str(e)[:40]} ({os.path.basename(path)})")

        with self.lock:
            self.results.append(result)

    def run(self):
        threads = []
        for _ in range(MAX_WORKERS):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
            
        self.queue.join()
        for t in threads:
            t.join()


# =============================================================================
# Report Generation & File Copy
# =============================================================================
def generate_report(results, start_time, end_time):
    """Generate a markdown report of the recursive scraping results."""
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ("error", "http_error"))
    empty = sum(1 for r in results if r["status"] == "empty")
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
        elif "/assets/" in url:
            service = "assets"
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
| Total files discovered | {total} |
| Successfully scraped | {success} |
| Failed (HTTP errors) | {failed} |
| Empty responses | {empty} |
| Total data downloaded | {total_bytes:,} bytes ({total_bytes/1024/1024:.2f} MB) |

## Services Scraped ({len(services)} categories)

| Category / Service | Total Files | Status |
|--------------------|-------------|--------|
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
            report += f"- {status_icon} [{r['title'] or os.path.basename(r['filepath'])}]({r['url']}) — {size_str}"
            if r["error"]:
                report += f" — *{r['error']}*"
            report += "\n"

    failures = [r for r in results if r["status"] not in ("success",)]
    if failures:
        report += "\n## Failed Files\n\n"
        for r in failures:
            report += f"- **{r['title'] or os.path.basename(r['filepath'])}**: `{r['url']}` — {r['error'] or r['status']}\n"

    return report


def copy_to_root_docs():
    """Copy all scraped documentation to the project root docs folder."""
    print(f"\nCopying scraped documentation to {ROOT_DOCS_DIR}...")
    try:
        # Remove target directory if it exists to ensure a clean copy
        if ROOT_DOCS_DIR.exists():
            shutil.rmtree(ROOT_DOCS_DIR)
        
        # Copy scraped_docs directory
        shutil.copytree(OUTPUT_DIR, ROOT_DOCS_DIR, dirs_exist_ok=True)
        
        # Copy index.json and scrape_report.md
        shutil.copy2(INDEX_FILE, ROOT_DOCS_DIR / "index.json")
        shutil.copy2(REPORT_FILE, ROOT_DOCS_DIR / "scrape_report.md")
        
        print("  Copy completed successfully!")
    except Exception as e:
        print(f"  [!] Error copying files: {e}")


# =============================================================================
# Main Execution
# =============================================================================
def main():
    print("=" * 70)
    print("  HPE GreenLake Developer Portal - Recursive Documentation Scraper")
    print("=" * 70)
    print()

    # Step 1: Fetch llms.txt seed index
    print("[1/5] Fetching documentation seed index from llms.txt...")
    try:
        llms_content = fetch_url_bytes(LLMS_TXT_URL).decode("utf-8", errors="replace")
        seed_entries = parse_llms_txt(llms_content)
        print(f"  Found {len(seed_entries)} documentation seed pages in llms.txt")
    except Exception as e:
        print(f"  [FAIL] Failed to fetch llms.txt: {e}")
        sys.exit(1)

    # Save the raw seed list
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "_llms.txt").write_text(llms_content, encoding="utf-8")

    # Add extra seed entry points for robustness
    seed_entries.append({"title": "Services Overview", "url": f"{BASE_URL}/docs/greenlake/services/overview.md"})
    seed_entries.append({"title": "Guides Overview", "url": f"{BASE_URL}/docs/greenlake/guides.md"})

    # Step 2: Start recursive crawling
    print(f"\n[2/5] Crawling and downloading all files recursively...")
    print(f"  Using {MAX_WORKERS} concurrent threads with request delay of {REQUEST_DELAY}s")
    print("-" * 70)

    start_time = time.time()
    crawler = GreenLakeCrawler(seed_entries)
    crawler.run()
    end_time = time.time()

    print("-" * 70)
    print(f"  Crawled {len(crawler.visited)} total unique URLs.")

    # Step 3: Fetch supplementary page-data JSONs for key pages
    print(f"\n[3/5] Fetching supplementary page-data JSONs for key service pages...")
    page_data_dir = OUTPUT_DIR / "_page_data"
    page_data_dir.mkdir(parents=True, exist_ok=True)

    key_pages = [e for e in seed_entries if e["url"].endswith("/public.md") or e["url"].endswith("/overview.md")]
    pd_count = 0
    for entry in key_pages:
        try:
            time.sleep(REQUEST_DELAY)
            pd = fetch_page_data_json(entry["url"])
            if pd:
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

    # Step 4: Generate index and report
    print(f"\n[4/5] Generating index and report...")

    # Sort results
    crawler.results.sort(key=lambda r: r["url"])

    # Save index
    now_str = datetime.now(timezone.utc).isoformat() + "Z"
    index_data = {
        "scraped_at": now_str,
        "source": BASE_URL,
        "total_files": len(crawler.results),
        "successful": sum(1 for r in crawler.results if r["status"] == "success"),
        "files": crawler.results,
    }
    INDEX_FILE.write_text(json.dumps(index_data, indent=2), encoding="utf-8")
    print(f"  Index saved to: {INDEX_FILE}")

    # Generate report
    report = generate_report(crawler.results, start_time, end_time)
    report = report.encode('ascii', errors='replace').decode('ascii')
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"  Report saved to: {REPORT_FILE}")

    # Step 5: Copy files to root docs
    print(f"\n[5/5] Copying all files to project root documentation...")
    copy_to_root_docs()

    # Final summary
    success = sum(1 for r in crawler.results if r["status"] == "success")
    total_bytes = sum(r["size_bytes"] for r in crawler.results)
    print()
    print("=" * 70)
    print(f"  RECURSIVE SCRAPE COMPLETE")
    print(f"  Files: {success}/{len(crawler.results)} successful")
    print(f"  Data:  {total_bytes:,} bytes ({total_bytes/1024/1024:.2f} MB)")
    print(f"  Time:  {end_time - start_time:.1f} seconds")
    print(f"  Docs:  {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
