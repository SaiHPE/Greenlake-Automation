"""The pre-pull-request check. Run it before you push; paste its last block into the pull request.

    .venv/bin/python scripts/check.py          (Windows: .venv\\Scripts\\python scripts\\check.py)
    .venv/bin/python scripts/check.py --quick  (skips the test suite, for a fast re-check)

There is no CI on github.hpe.com (Actions is off for this repo), so this script is the gate the
reviewer relies on. It checks, against the branch point with origin/main:
  tests      pytest, the whole suite
  lint       ruff (the version pinned in pyproject.toml)
  types      the frontend TypeScript check (npm run typecheck)
  dist       frontend/dist is not changed: it is built from frontend/src after each merge
  secrets    no token, private key or lab password in the lines this branch adds
  ignored    files under src/, tests/ or frontend/src/ that .gitignore hides (a warning)
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
REPO = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=APP, capture_output=True, text=True,
                           check=True).stdout.strip())
APP_REL = APP.relative_to(REPO).as_posix()
DIST = f"{APP_REL}/frontend/dist/"
TOKEN = re.compile(r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gh[osu]_[A-Za-z0-9]{30,}"
                   r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")
RESULTS: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> None:
    RESULTS.append((name, status, detail))
    print(f"  {status:<4} {name}{' - ' + detail if detail else ''}", flush=True)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=False).stdout


def base_ref() -> str:
    for ref in ("origin/main", "main"):
        if git("rev-parse", "--verify", "-q", ref).strip():
            return git("merge-base", "HEAD", ref).strip() or ref
    return "HEAD"


def changed_files(base: str) -> list[str]:
    """Everything this branch changes: commits since the branch point, staged and unstaged edits."""
    names = set(git("diff", "--name-only", base).split()) | set(git("diff", "--name-only", "--cached").split())
    return sorted(names)


def added_lines(base: str) -> list[tuple[str, str]]:
    out, path = [], ""
    for line in git("diff", "-U0", "--no-color", base).splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else ""
        elif line.startswith("+") and path:
            out.append((path, line[1:]))
    return out


def lab_passwords() -> list[str]:
    """The developer's own lab passwords from the app's .env, so they are caught without being written here."""
    env = APP / ".env"
    found = []
    if env.is_file():
        for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() in ("LAB_ARRAY_PW", "LAB_DEFAULT_PW") and len(value.strip()) >= 4:
                found.append(value.strip())
    return found


def run_step(name: str, cmd: list[str], cwd: Path) -> None:
    started = time.monotonic()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    tail = [line for line in (proc.stdout + proc.stderr).strip().splitlines() if line.strip()]
    summary = tail[-1] if tail else "no errors"
    if proc.returncode == 0:
        record(name, "PASS", f"{summary} ({time.monotonic() - started:.0f} s)")
    else:
        print("\n".join(tail[-25:]))
        record(name, "FAIL", summary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="skip the test suite")
    args = parser.parse_args()

    base = base_ref()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    head = git("log", "-1", "--format=%h %s").strip()
    print(f"Checking {branch} @ {head}\n  against {base[:10]} (branch point with origin/main)\n")

    if args.quick:
        record("tests", "SKIP", "--quick")
    else:
        run_step("tests", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], APP)
    run_step("lint", [sys.executable, "-m", "ruff", "check", "."], APP)

    npm = shutil.which("npm")
    if not npm:
        record("types", "FAIL", "npm not found: install Node 20")
    elif not (APP / "frontend" / "node_modules").is_dir():
        record("types", "FAIL", "run `npm ci` in frontend/ first")
    else:
        run_step("types", [npm, "run", "-s", "typecheck"], APP / "frontend")

    changed = changed_files(base)
    dist = [f for f in changed if f.startswith(DIST)]
    if dist and os.environ.get("ALLOW_DIST") != "1":
        record("dist", "FAIL", f"{len(dist)} file(s) under frontend/dist changed. It is rebuilt after merge; "
               f"drop them: git checkout {base[:10]} -- {DIST}")
    else:
        record("dist", "PASS", "frontend/dist untouched")

    secrets = lab_passwords()
    leaks = []
    for path, line in added_lines(base):
        if TOKEN.search(line) or any(pw in line for pw in secrets):
            leaks.append(path)
    if leaks:
        record("secrets", "FAIL", "a token, key or lab password is in: " + ", ".join(sorted(set(leaks))))
    else:
        record("secrets", "PASS", f"{len(changed)} changed file(s) scanned")

    ignored = [f for f in git("ls-files", "--others", "--ignored", "--exclude-standard", "--",
                                f"{APP_REL}/src", f"{APP_REL}/tests", f"{APP_REL}/frontend/src").split()
               if "__pycache__" not in f and not f.endswith((".pyc", ".DS_Store", "Thumbs.db"))]
    if ignored:
        record("ignored", "WARN", "hidden by .gitignore, not committed: " + ", ".join(ignored[:5])
               + (" ..." if len(ignored) > 5 else ""))

    failed = [name for name, status, _ in RESULTS if status == "FAIL"]
    print("\n---- paste this into the pull request ----")
    print(f"check.py on {branch} @ {head.split()[0] if head else '?'}: "
          f"{'FAIL (' + ', '.join(failed) + ')' if failed else 'PASS'}")
    for name, status, detail in RESULTS:
        print(f"  {status:<4} {name}{' - ' + detail if detail else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
