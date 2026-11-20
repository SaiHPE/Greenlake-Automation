"""Generate frontend/generated/api.ts from FastAPI's OpenAPI schema, or check that it is current.

    .venv/bin/python scripts/api_types.py          # regenerate and write frontend/generated/api.ts
    .venv/bin/python scripts/api_types.py --check  # exit 1 if the committed file differs
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

from alletra_onboard.api.app import create_app

APP = Path(__file__).resolve().parents[1]
FRONTEND = APP / "frontend"
SPEC_PATH = FRONTEND / "node_modules" / ".cache" / "openapi.json"
OUT_REL = "generated/api.ts"


def build_spec() -> dict[str, Any]:
    return create_app(cast(Any, object())).openapi()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="check that generated/api.ts is up to date")
    args = parser.parse_args()

    npm = shutil.which("npm")
    if not npm:
        print("npm not found: install Node 20.19 or newer", file=sys.stderr)
        return 1

    spec = build_spec()
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(json.dumps(spec, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [npm, "exec", "--no", "--", "openapi-typescript", str(SPEC_PATH), "-o", OUT_REL]
    if args.check:
        cmd.append("--check")
    proc = subprocess.run(cmd, cwd=FRONTEND, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        out = (proc.stdout + proc.stderr).strip()
        if out:
            print(out, file=sys.stderr)
        return proc.returncode
    schemas = len(spec.get("components", {}).get("schemas", {}))
    print(f"api-types: {schemas} schemas, generated/api.ts current" if args.check else f"api-types: wrote {OUT_REL} ({schemas} schemas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
