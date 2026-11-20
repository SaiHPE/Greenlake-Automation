"""The pre-pull-request check. Run it before you push; paste its last block into the pull request.

    .venv/bin/python scripts/check.py          (Windows: .venv\\Scripts\\python scripts\\check.py)
    .venv/bin/python scripts/check.py --quick  (skips the test suite, for a fast re-check)

There is no CI on github.hpe.com (Actions is off for this repo), so this script is the gate the
reviewer relies on. It checks, against the branch point with origin/main:
  tests      pytest, the whole suite
  deps       the dependency rules of docs/STANDARD.md 3.1 to 3.3 (import-linter; the contracts are
             in pyproject.toml and quality/imports-type-only.toml)
  lint       ruff (the version pinned in pyproject.toml), every rule but the four of `complexity`;
             today's offenders are listed per function in quality/ceilings.toml (scripts/fitness.py)
  complexity ruff C901, PLR0913, PLR0912, PLR0915 per function, each with today's number as its
             ceiling in quality/ceilings.toml
  fitness    scripts/fitness.py: a long source file may not grow, no suppress(Exception),
             a file may not gain a suppression comment (`type: ignore`, `noqa`, `eslint-disable`),
             every code path a document names exists, Markdown only in today's folders, a new
             lesson names the test or lint rule that catches its defect
  vulture    dead Python code at 80% confidence; today's findings are listed in quality/ceilings.toml
  pyright    backend type errors per file (pyright from frontend/node_modules, pyrightconfig.json):
             a file may not gain errors, and a file with none stays clean
  api-types  frontend/generated/api.ts matches FastAPI's OpenAPI schema (scripts/api_types.py --check)
  types      the frontend TypeScript check (npm run typecheck)
  mockups    the design mockups' TypeScript check (tsc -p mockups --noEmit)
  ui-lint    eslint on frontend/src (npm run lint); today's violations are eslint's own list,
             frontend/eslint-suppressions.json
  knip       dead frontend code: unused files, exports, types and dependencies, listed like vulture's
  ui-tests   the frontend unit tests (npm test: vitest, no browser)
  config     what the gate measures is not changed: its two scripts, the settings of ruff, pyright,
             eslint, tsc and knip, the npm scripts, and the import contracts (deleting an
             ignore_imports line is a fix, not a change). ALLOW_CONFIG=1 turns the failure into a
             warning; that is the owner's call, with an ADR
  dist       frontend/dist is not changed: it is built from frontend/src after each merge
  secrets    no token, private key or lab password in the lines this branch adds
  lists      no known violation is added to a list, or raised: the lists only go down. Every such
             key is printed. ALLOW_LISTS=1 turns the failure into a warning; that is the owner's
             call (a new check that brings its list), and the pull request says why
  ignored    files under src/, tests/ or frontend/src/ that .gitignore hides (a warning)

A FAIL line names the rule of docs/STANDARD.md it breaks and what to do. The last line is the time
the whole check took.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
REPO = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=APP, capture_output=True, text=True,
                           check=True).stdout.strip())
APP_REL = APP.relative_to(REPO).as_posix()
DIST = f"{APP_REL}/frontend/dist/"
TOKEN = re.compile(r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gh[osu]_[A-Za-z0-9]{30,}"
                   r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")
# A capture keeps what the device printed, its contact block included: an address in a fixture is a
# colleague's or a customer's. Captures use lab-user@example.com instead.
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net")
FIXTURES = f"{APP_REL}/tests/fixtures/"
IMPORT_CONFIGS = ("pyproject.toml", "quality/imports-type-only.toml")
# Files that decide, whole, what the gate measures. gate_settings() adds the parts of pyproject.toml,
# frontend/package.json and the import contracts that do.
GATE_FILES = ("scripts/check.py", "scripts/fitness.py", "scripts/api_types.py", "pyrightconfig.json",
              "frontend/eslint.config.js", "frontend/tsconfig.json")
LINT_IMPORTS = "import sys; from importlinter.cli import lint_imports_command; sys.exit(lint_imports_command())"
FITNESS_LINE = r"^fitness\["   # the last line scripts/fitness.py prints: listed, new, worse, stale
LISTED = "each NEW, WORSE and STALE line above names the rule and says what to do"
# name, command for this Python, the output line to show, what a failure breaks and what to do
PYTHON_STEPS = (
    # --no-cache: with two config files the cache serves the second import graph stale, so a new
    # violation of L3 or L6 passed (seen with import-linter 2.17, grimp 3.20). Uncached takes under a second.
    ("deps", ["-c", LINT_IMPORTS, "pyproject.toml", "quality/imports-type-only.toml", "--no-logo", "--no-cache"],
     r"^Contracts: |^No matches for ignored import",
     ("STANDARD S2, L1 to L6, B1 (import-linter): an import breaks a dependency rule; the contract above "
      "says which and what to do. `No matches for ignored import` means a listed violation is gone: "
      "delete its ignore_imports line")),
    ("lint", ["scripts/fitness.py", "lint"], FITNESS_LINE, f"STANDARD L6, T3, C1, E1, E2 (ruff): {LISTED}"),
    ("complexity", ["scripts/fitness.py", "complexity"], FITNESS_LINE,
     ("STANDARD M1 (ruff C901, PLR0913, PLR0912, PLR0915): a new function stays within the limits and a "
      "listed one may not get worse; see the lines above")),
    ("fitness", ["scripts/fitness.py", "files", "suppress", "suppressions", "docs", "lessons"], FITNESS_LINE,
     f"STANDARD M2, E2, T3, C2, C3, C4 (scripts/fitness.py): {LISTED}"),
    ("vulture", ["scripts/fitness.py", "vulture"], FITNESS_LINE,
     "STANDARD M3 (vulture): new dead code; delete it or use it, as the lines above say"),
)
# name, npm arguments (or a fitness.py section), the package it needs, the output line to show, the rule
FRONTEND_STEPS = (
    ("pyright", ["scripts/fitness.py", "pyright"], "pyright", FITNESS_LINE,
     ("STANDARD T2 (pyright): a file may not gain type errors; the lines above name the file and its "
      "first errors")),
    ("api-types", ["scripts/api_types.py", "--check"], "openapi-typescript", r"^api-types:",
     ("STANDARD T4: frontend/generated/api.ts is not what the backend's schema generates. Run "
      "`.venv/bin/python scripts/api_types.py` and commit the file. Never edit it by hand. "
      "If it still differs, your fastapi or pydantic is not the dev extra's version.")),
    ("types", ["run", "-s", "typecheck"], "typescript", "",
     "the frontend does not type-check (tsc): fix the errors above"),
    ("mockups", ["exec", "--no", "--", "tsc", "-p", "mockups", "--noEmit"], "typescript", "",
     "the design mockups do not type-check (tsc -p mockups): fix the errors above"),
    ("ui-lint", ["run", "-s", "lint"], "eslint", r"problems? \(|suppressions left",
     ("STANDARD T3, T4, F1, F2, F3 (eslint): fix the errors above; do not add to "
      "frontend/eslint-suppressions.json. If it says suppressions are left, a listed violation is gone: "
      "delete its entry with `npx eslint src --prune-suppressions` in frontend/")),
    ("knip", ["scripts/fitness.py", "knip"], "knip", FITNESS_LINE,
     ("STANDARD M3 (knip): a new unused file, export, type or dependency in the frontend; delete it or "
      "use it, as the lines above say")),
    ("ui-tests", ["run", "-s", "test"], "vitest", r"^\s*Tests\s", "fix the failing frontend tests above"),
)
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


def tool_env() -> dict[str, str]:
    """The tools check this checkout's source, also in a worktree that shares another one's venv."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(APP / "src"), env.get("PYTHONPATH", "")) if p)
    return env


def quiet(name: str) -> str:
    """What to show for a step that printed nothing."""
    if name != "ui-lint":
        return "no errors"
    listed = sum(entry["count"] for rules in json.loads(on_disk("frontend/eslint-suppressions.json") or "{}").values()
                 for entry in rules.values())
    return f"{listed} listed, 0 new, 0 stale"


def run_step(name: str, cmd: list[str], cwd: Path, summary_line: str = "", rule: str = "") -> None:
    """Runs one step. `summary_line`, a regex, picks the output line to show instead of the last one.
    `rule` names the STANDARD rule a failure breaks and what to do about it."""
    started = time.monotonic()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, env=tool_env())
    tail = [line for line in (proc.stdout + proc.stderr).strip().splitlines() if line.strip()]
    picked = [line.strip() for line in tail if summary_line and re.search(summary_line, line)]
    summary = picked[-1] if picked else tail[-1] if tail else quiet(name)
    if proc.returncode == 0:
        record(name, "PASS", f"{summary} ({time.monotonic() - started:.0f} s)")
    else:
        print("\n".join(tail[-40:]))
        record(name, "FAIL", f"{summary} ({time.monotonic() - started:.0f} s). {rule}".rstrip(" ."))


def known_violations(text_of) -> dict[str, int]:
    """Every violation the gate's lists hold, with its number: quality/ceilings.toml, the import
    contracts' ignore_imports and eslint's suppressions."""
    out: dict[str, int] = {}
    for table, entries in tomllib.loads(text_of("quality/ceilings.toml") or "").items():
        if table == "moves":
            continue
        for key, value in entries.items():
            out.update({f"{table}: {key}": value} if isinstance(value, int)
                       else {f"{table}: {item}": 1 for item in value})
    for config in IMPORT_CONFIGS:
        contracts = tomllib.loads(text_of(config) or "").get("tool", {}).get("importlinter", {}).get("contracts", [])
        out.update({f"{contract['id']}: {line}": 1 for contract in contracts
                    for line in contract.get("ignore_imports", [])})
    for path, rules in json.loads(text_of("frontend/eslint-suppressions.json") or "{}").items():
        out.update({f"eslint: {path} :: {rule}": entry["count"] for rule, entry in rules.items()})
    return out


def on_disk(path: str) -> str:
    return (APP / path).read_text(encoding="utf-8") if (APP / path).is_file() else ""


def run_tools(quick: bool) -> None:
    if quick:
        record("tests", "SKIP", "--quick")
    else:
        run_step("tests", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], APP,
                 r"\d+ (passed|failed)",
                 "STANDARD X1 to X3: fix the failing tests above; never loosen an assertion to pass")
    for name, cmd, summary_line, rule in PYTHON_STEPS:
        run_step(name, [sys.executable, *cmd], APP, summary_line, rule)

    npm = shutil.which("npm")
    frontend = APP / "frontend"
    for name, cmd, needs, summary_line, rule in FRONTEND_STEPS:
        if not npm:
            record(name, "FAIL", "npm not found: install Node 20.19 or newer")
        elif not (frontend / "node_modules").is_dir():
            record(name, "FAIL", "run `npm ci` in frontend/ first")
        elif not (frontend / "node_modules" / needs).is_dir():
            record(name, "FAIL", f"{needs} is not installed: run `npm ci` in frontend/")
        elif cmd[0].startswith("scripts/"):
            run_step(name, [sys.executable, *cmd], APP, summary_line, rule)
        else:
            run_step(name, [npm, *cmd], frontend, summary_line, rule)


def grown(now_text_of, before_text_of) -> list[str]:
    """The known violations listed now that were not listed before, or had a lower number. A key that
    `fitness.py --move` recorded is compared with its old key, when that key is gone and no other
    key claims it."""
    now, before = known_violations(now_text_of), known_violations(before_text_of)
    moves = tomllib.loads(now_text_of("quality/ceilings.toml") or "").get("moves", {})

    def ceiling(listed: str) -> int:
        table, _, key = listed.partition(": ")
        old = f"{table}: {moves.get(key)}"
        moved = old not in now and list(moves.values()).count(moves.get(key)) == 1
        return before.get(listed, before.get(old, 0) if moved else 0)

    return sorted(key for key, value in now.items() if value > ceiling(key))


def at(base: str):
    """Reads a file of the app folder as it was at the branch point."""
    return lambda path: git("show", f"{base}:{APP_REL}/{path}")


def check_lists(base: str) -> None:
    keys = grown(on_disk, at(base)) if at(base)("quality/ceilings.toml") else []
    count = f"{len(keys)} known violation(s) added or raised since the branch point"
    if not keys:
        record("lists", "PASS", "no known violation added or raised")
    elif os.environ.get("ALLOW_LISTS") == "1":
        record("lists", "WARN", f"{count}, let through by ALLOW_LISTS=1: say why in the pull request")
    else:
        print("\n".join(f"  grown: {key}" for key in keys))
        record("lists", "FAIL", f"{count}, each printed above. STANDARD rule 3: the lists only go down. Fix the "
               f"code and take the line back out. ALLOW_LISTS=1 lets it through; that is the owner's call")


def gate_settings(text_of) -> dict[str, object]:
    """What decides what the gate measures, by name. The ignore_imports lists are left out: deleting
    a line there is a fix, and `lists` fails a line that is added."""
    out: dict[str, object] = {path: text_of(path) or "" for path in GATE_FILES}
    out["pyproject.toml [tool.ruff]"] = tomllib.loads(text_of("pyproject.toml") or "").get("tool", {}).get("ruff")
    package = json.loads(text_of("frontend/package.json") or "{}")
    out["frontend/package.json scripts"] = package.get("scripts")
    out["frontend/package.json knip"] = package.get("knip")
    for config in IMPORT_CONFIGS:
        linter = tomllib.loads(text_of(config) or "").get("tool", {}).get("importlinter", {})
        contracts = [{key: value for key, value in contract.items() if key != "ignore_imports"}
                     for contract in linter.get("contracts", [])]
        out[f"{config} [tool.importlinter]"] = {**linter, "contracts": contracts}
    return out


def changed_settings(now_text_of, before_text_of) -> list[str]:
    now, before = gate_settings(now_text_of), gate_settings(before_text_of)
    return sorted(name for name in now if now[name] != before[name])


def check_config(base: str) -> None:
    names = ", ".join(changed_settings(on_disk, at(base)))
    if not names:
        record("config", "PASS", "the gate's scripts and the tools' settings are unchanged")
    elif os.environ.get("ALLOW_CONFIG") == "1":
        record("config", "WARN", f"changed since the branch point: {names}. Let through by ALLOW_CONFIG=1: name "
               f"the ADR in the pull request")
    else:
        record("config", "FAIL", f"changed since the branch point: {names}. STANDARD rule 4: what the gate "
               f"measures changes with an ADR, not inside another change. Take the change back out. "
               f"ALLOW_CONFIG=1 lets it through; that is the owner's call")


def check_dist(base: str, changed: list[str]) -> None:
    dist = [f for f in changed if f.startswith(DIST)]
    if dist and os.environ.get("ALLOW_DIST") != "1":
        record("dist", "FAIL", f"{len(dist)} file(s) under frontend/dist changed. It is rebuilt after merge; "
               f"drop them: git checkout {base[:10]} -- {DIST}")
    else:
        record("dist", "PASS", "frontend/dist untouched")


def check_secrets(base: str, changed: list[str]) -> None:
    secrets = lab_passwords()
    leaks, people = [], []
    for path, line in added_lines(base):
        if TOKEN.search(line) or any(pw in line for pw in secrets):
            leaks.append(path)
        if path.startswith(FIXTURES) and any(m.group(0).rsplit("@", 1)[1].lower() not in PLACEHOLDER_DOMAINS
                                             for m in EMAIL.finditer(line)):
            people.append(path)
    if leaks or people:
        found = (["a token, key or lab password is in: " + ", ".join(sorted(set(leaks)))] if leaks else []) + (
            ["a real email address is in: " + ", ".join(sorted(set(people))) + " (use lab-user@example.com)"]
            if people else [])
        record("secrets", "FAIL", "; ".join(found))
    else:
        record("secrets", "PASS", f"{len(changed)} changed file(s) scanned")


def check_ignored() -> None:
    ignored = [f for f in git("ls-files", "--others", "--ignored", "--exclude-standard", "--",
                              f"{APP_REL}/src", f"{APP_REL}/tests", f"{APP_REL}/frontend/src").split()
               if "__pycache__" not in f and not f.endswith((".pyc", ".DS_Store", "Thumbs.db"))]
    if ignored:
        record("ignored", "WARN", "hidden by .gitignore, not committed: " + ", ".join(ignored[:5])
               + (" ..." if len(ignored) > 5 else ""))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="skip the test suite")
    args = parser.parse_args()

    started = time.monotonic()
    base = base_ref()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    head = git("log", "-1", "--format=%h %s").strip()
    print(f"Checking {branch} @ {head}\n  against {base[:10]} (branch point with origin/main)\n")

    run_tools(args.quick)
    check_lists(base)
    check_config(base)
    changed = changed_files(base)
    check_dist(base, changed)
    check_secrets(base, changed)
    check_ignored()

    failed = [name for name, status, _ in RESULTS if status == "FAIL"]
    print("\n---- paste this into the pull request ----")
    print(f"check.py on {branch} @ {head.split()[0] if head else '?'}: "
          f"{'FAIL (' + ', '.join(failed) + ')' if failed else 'PASS'}")
    for name, status, detail in RESULTS:
        print(f"  {status:<4} {name}{' - ' + detail if detail else ''}")
    print(f"  took {time.monotonic() - started:.0f} s")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
