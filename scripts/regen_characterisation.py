"""Regenerate the capture-only characterisation golden JSON files under
`tests/fixtures/characterisation/`.

Deliberately run by hand when an intentional behaviour change updates captured outputs:

    .venv/bin/python scripts/regen_characterisation.py

Never invoked by `scripts/check.py` or pytest. Writes indented JSON (one item per line) so every
capture diff is directly reviewable.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]

_TARGETS = (
    ("tests.unit.test_discovery_differential", "compute_discovery_captures"),
    ("tests.unit.test_zoning_plan_characterisation", "compute_zoning_captures"),
    ("tests.unit.test_provisioning_characterisation", "compute_provisioning_captures"),
)


def main() -> None:
    for entry in (str(APP / "src"), str(APP)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    for mod_name, fn_name in _TARGETS:
        mod = importlib.import_module(mod_name)
        path: Path = mod.GOLDEN
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(getattr(mod, fn_name)(), indent=2, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(APP)} ({len(text):,} bytes)")


if __name__ == "__main__":
    main()
