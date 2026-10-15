#!/usr/bin/env python3
import json
from pathlib import Path
import urllib.parse

# Define paths
WORKSPACE_ROOT = Path(__file__).parent.parent
INDEX_FILE = Path(__file__).parent / "index.json"
OUTPUT_LLMS_TXT = WORKSPACE_ROOT / "docs and plans" / "greenlake_api_docs" / "llms.txt"

def main():
    if not INDEX_FILE.exists():
        print(f"Error: {INDEX_FILE} not found!")
        return

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    files = data.get("files", [])
    success_files = [f for f in files if f.get("status") == "success"]

    # Group by category/service
    categories = {}
    for f in success_files:
        filepath_raw = f.get("filepath", "")
        # Normalise path separators to forward slashes
        filepath = Path(filepath_raw).as_posix()
        
        # Normalise path relative to greenlake_api_docs
        if filepath.startswith("scraped_docs/"):
            rel_path = filepath[len("scraped_docs/"):]
        else:
            rel_path = filepath
            
        parts = rel_path.split("/")
        if len(parts) > 1:
            if parts[0] == "greenlake":
                if parts[1] == "services" and len(parts) > 2:
                    category = f"Service: {parts[2]}"
                else:
                    category = f"Category: {parts[1]}"
            else:
                category = f"Category: {parts[0]}"
        else:
            category = "General"

        if category not in categories:
            categories[category] = []
        categories[category].append((f.get("title", ""), rel_path, f.get("url", "")))

    # Generate Markdown Content
    content = []
    content.append("# HPE GreenLake API Documentation - Local AI Agent Index Map")
    content.append("This file is a map designed for AI agents and developers to quickly locate and ingest documentation, raw OpenAPI specification files, and visual assets.")
    content.append("\n## Workspace Location")
    # URL-encode spaces in the workspace root path for markdown link validity
    encoded_root = urllib.parse.quote(WORKSPACE_ROOT.as_posix())
    content.append(f"- **Local docs directory:** [greenlake_api_docs](file:///{encoded_root}/docs%20and%20plans/greenlake_api_docs)")
    content.append(f"- **Total indexed files:** {len(success_files)}")

    content.append("\n## Index by Service and Category")

    for cat in sorted(categories.keys()):
        content.append(f"\n### {cat}")
        for title, rel_path, url in sorted(categories[cat], key=lambda x: x[1]):
            # URL-encode rel_path for the Markdown link URL
            encoded_rel = urllib.parse.quote(rel_path)
            file_url = f"file:///{WORKSPACE_ROOT.as_posix()}/docs and plans/greenlake_api_docs/{encoded_rel}"
            
            # Format file name or title
            display_title = title if title else Path(rel_path).name
            if rel_path.endswith((".yaml", ".yml")):
                file_type = " [OpenAPI Spec]"
            elif rel_path.endswith((".png", ".jpg", ".jpeg", ".svg")):
                file_type = " [Visual Asset]"
            elif rel_path.endswith(".json"):
                file_type = " [Metadata JSON]"
            else:
                file_type = ""
                
            content.append(f"- [{display_title}{file_type}]({file_url})")
            if url:
                content.append(f"  - *Remote source:* {url}")

    # Write output
    OUTPUT_LLMS_TXT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_LLMS_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    print(f"Successfully generated AI Agent Index Map at {OUTPUT_LLMS_TXT}")

if __name__ == "__main__":
    main()
