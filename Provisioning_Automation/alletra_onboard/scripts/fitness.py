"""The checks of docs/STANDARD.md that no tool does on its own. scripts/check.py runs them.

    .venv/bin/python scripts/fitness.py              every section
    .venv/bin/python scripts/fitness.py complexity   one section (or several)
    .venv/bin/python scripts/fitness.py --tighten    lower each ceiling to today's value and drop the
                                                     entries whose violation is gone; never adds, never raises

Today's known violations are listed in quality/ceilings.toml, one line each, keyed by file and
function, never by line. A section fails on a violation that is not listed (NEW), on a listed one
that got worse (WORSE) and on a listed one that is gone (STALE). Sections:

  lint        ruff, every rule but the four below, counted per function (STANDARD L6, T3, C1, E1, E2)
  complexity  ruff C901, PLR0913, PLR0912, PLR0915: the function's own number is its ceiling (M1)
  pyright     type errors per file: `standard` on src, `strict` on domain (T2; pyrightconfig.json)
  vulture     dead Python code at 80% confidence in src (M3)
  knip        dead frontend code: unused files, exports, types and dependencies (M3)
  files       a source file over 500 lines may not grow (M2)
  suppress    `suppress(Exception)` per function (E2)
  docs        every code path a document names exists (C2); Markdown only in today's folders (C3)
  lessons     a lesson numbered above 49 names a test or a lint rule that exists (C4)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
CEILINGS = APP / "quality" / "ceilings.toml"
SEP = " :: "
MODULE = "<module>"

# key -> (value, where to look). The key goes in ceilings.toml; `where` is only printed.
Found = dict[str, tuple[int, str]]


class ToolError(Exception):
    """A tool could not run, or printed something this script does not understand."""


@dataclass
class Report:
    listed: int = 0
    new: list[str] = field(default_factory=list)
    worse: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    lower: int = 0

    def add(self, other: Report) -> None:
        self.listed += other.listed
        self.new += other.new
        self.worse += other.worse
        self.stale += other.stale
        self.lower += other.lower

    @property
    def failed(self) -> bool:
        return bool(self.new or self.worse or self.stale)


@dataclass(frozen=True)
class Table:
    """One table of ceilings.toml: how it is measured and what its messages say."""

    name: str
    comment: str
    measure: Callable[[], Found]
    new: Callable[[str], str]      # key -> the rule a new entry breaks and what to do
    worse: str                     # the rule a higher number breaks


def run(cmd: list[str], cwd: Path = APP, ok: tuple[int, ...] = (0,)) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if proc.returncode not in ok:
        raise ToolError(f"`{' '.join(cmd[:4])} ...` ended with {proc.returncode}: "
                        f"{(proc.stderr or proc.stdout).strip()[-600:]}")
    return proc.stdout


def rel(path: str | Path) -> str:
    return Path(path).resolve().relative_to(APP).as_posix()


# ---- which function a line belongs to ----

@cache
def _scopes(path: Path) -> tuple[tuple[int, int, str], ...]:
    """(first line, last line, qualified name) of every function and class in the file."""
    out: list[tuple[int, int, str]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                name = f"{prefix}{child.name}"
                first = min([child.lineno, *(d.lineno for d in child.decorator_list)])
                out.append((first, child.end_lineno or child.lineno, name))
                walk(child, name + ".")
            else:
                walk(child, prefix)

    try:
        walk(ast.parse(path.read_text(encoding="utf-8")), "")
    except SyntaxError:
        return ()
    return tuple(out)


def scope_at(path: Path, row: int) -> str:
    """The innermost function or class that holds the line; `<module>` outside all of them."""
    best = (0, 0, MODULE)
    for first, last, name in _scopes(path):
        if first <= row <= last and first >= best[0]:
            best = (first, last, name)
    return best[2]


# ---- ruff: lint and complexity ----

NUMERIC = ("C901", "PLR0913", "PLR0912", "PLR0915")
NUMBER = re.compile(r"\((\d+) > \d+\)")
LINT_RULES = (
    (("BLE001",), "STANDARD E1: catch DeviceError or something narrower; `except Exception` belongs only "
                  "at the coordinator's step boundary and in the API's error mapping."),
    (("S110", "S112"), "STANDARD E2: no silent swallowing. Handle the error or let it reach the step boundary."),
    (("PLC0415",), "STANDARD L6: import at the top of the file; an import inside a function hides a cycle."),
    (("PGH003", "RUF100"), "STANDARD T3: name the rule code in a `type: ignore` or `noqa`, and delete one "
                           "that suppresses nothing."),
    (("ERA001", "FIX", "TD"), "STANDARD C1: delete commented-out code; a TODO becomes an issue, not a comment."),
)


@cache
def _ruff() -> tuple[tuple[str, str, int, str], ...]:
    """(path, rule, row, message) of every ruff finding in the app folder."""
    out = run([sys.executable, "-m", "ruff", "check", ".", "--output-format", "json", "--no-cache"], ok=(0, 1))
    return tuple((rel(item["filename"]), item["code"] or "syntax", item["location"]["row"], item["message"])
                 for item in json.loads(out))


def measure_complexity() -> Found:
    found: Found = {}
    for path, rule, row, message in _ruff():
        if rule not in NUMERIC:
            continue
        number = NUMBER.search(message)
        if not number:
            raise ToolError(f"ruff {rule} printed no number: {message!r}. Update NUMBER in scripts/fitness.py.")
        key = SEP.join((path, scope_at(APP / path, row), rule))
        if int(number.group(1)) > found.get(key, (0, ""))[0]:
            found[key] = (int(number.group(1)), f"line {row}")
    return found


def measure_lint() -> Found:
    found: Found = {}
    for path, rule, row, _message in _ruff():
        if rule in NUMERIC:
            continue
        key = SEP.join((path, scope_at(APP / path, row), rule))
        count, where = found.get(key, (0, f"line {row}"))
        found[key] = (count + 1, where)
    return found


def lint_guidance(key: str) -> str:
    rule = key.rsplit(SEP, 1)[-1]
    for codes, text in LINT_RULES:
        if rule.startswith(codes):
            return text
    return f"ruff {rule}: fix it (`ruff check` shows the line and `ruff rule {rule}` explains it)."


# ---- pyright ----

def node_tool(name: str) -> str:
    """A tool `npm ci` installed in frontend/node_modules (pinned in frontend/package-lock.json)."""
    found = shutil.which(name, path=str(APP / "frontend" / "node_modules" / ".bin"))
    if not found:
        raise ToolError(f"{name} is not installed: run `npm ci` in frontend/.")
    return found


def measure_pyright() -> Found:
    out = run([node_tool("pyright"), "-p", "pyrightconfig.json", "--pythonpath", sys.executable, "--outputjson"],
              ok=(0, 1))
    found: Found = {}
    for item in json.loads(out)["generalDiagnostics"]:
        if item["severity"] != "error":
            continue
        path = rel(item["file"])
        count, where = found.get(path, (0, ""))
        if count < PYRIGHT_SHOWN:
            where += f"\n        line {item['range']['start']['line'] + 1}: {item['message'].splitlines()[0]}"
        found[path] = (count + 1, where)
    return {path: (count, f"its first errors:{where}\n       ") for path, (count, where) in found.items()}


PYRIGHT_SHOWN = 5


# ---- vulture and knip: dead code ----

VULTURE_LINE = re.compile(r"^(?P<path>.+?):(?P<row>\d+): (?P<what>.+) \(\d+% confidence(?:, \d+ lines?)?\)$")


def measure_vulture() -> Found:
    out = run([sys.executable, "-m", "vulture", "src", "--min-confidence", "80"], ok=(0, 3))
    found: Found = {}
    for line in out.splitlines():
        match = VULTURE_LINE.match(line.strip())
        if not match:
            raise ToolError(f"vulture printed a line this script cannot read: {line!r}")
        key = SEP.join((Path(match["path"]).as_posix(), match["what"]))
        count, where = found.get(key, (0, f"line {match['row']}"))
        found[key] = (count + 1, where)
    return found


def measure_knip() -> Found:
    out = run([node_tool("knip"), "--reporter", "json", "--no-progress"], cwd=APP / "frontend", ok=(0, 1))
    found: Found = {}
    for issue in json.loads(out)["issues"]:
        for kind, items in issue.items():
            if not isinstance(items, list):
                continue
            for item in items:
                key = SEP.join((f"frontend/{issue['file']}", kind, item["name"]))
                count, where = found.get(key, (0, f"line {item['line']}" if "line" in item else "the whole file"))
                found[key] = (count + 1, where)
    return found


DEAD_CODE = ("STANDARD M3: no dead code. Delete it if nothing reaches it (prove that first: LESSONS 18), "
             "or use it.")


# ---- the repository's files, as git sees them ----

@cache
def repo_root() -> Path:
    return Path(run(["git", "rev-parse", "--show-toplevel"]).strip())


@cache
def repo_files() -> tuple[str, ...]:
    """Every file that is committed or would be (tracked, or new and not ignored), from the repo root."""
    out = run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=repo_root())
    return tuple(sorted(name for name in out.split("\0") if name and (repo_root() / name).is_file()))


@cache
def app_prefix() -> str:
    return APP.relative_to(repo_root()).as_posix() + "/"


def app_files(*suffixes: str) -> list[str]:
    """Paths from the app folder of the repository's files that end with one of the suffixes."""
    return [name[len(app_prefix()):] for name in repo_files()
            if name.startswith(app_prefix()) and name.endswith(suffixes)]


# ---- M2: a long file may not grow ----

LONG = 500


def measure_file_lines() -> Found:
    found: Found = {}
    for path in app_files(".py", ".ts", ".tsx"):
        if not path.startswith(("src/", "frontend/src/")) or path.endswith((".test.ts", ".test.tsx")):
            continue
        lines = len((APP / path).read_text(encoding="utf-8").splitlines())
        if lines > LONG:
            found[path] = (lines, f"{lines} lines")
    return found


# ---- E2: no contextlib.suppress(Exception) ----

def measure_suppress() -> Found:
    found: Found = {}
    for path in app_files(".py"):
        if not path.startswith(("src/", "tests/")):
            continue
        try:
            tree = ast.parse((APP / path).read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            broad = any(isinstance(arg, ast.Name) and arg.id in ("Exception", "BaseException") for arg in node.args)
            if name == "suppress" and broad:
                key = SEP.join((path, scope_at(APP / path, node.lineno)))
                count, where = found.get(key, (0, f"line {node.lineno}"))
                found[key] = (count + 1, where)
    return found


# ---- C2: a document names only code that exists ----

CODE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".mjs", ".ps1", ".sh", ".cmd", ".toml", ".spec", ".md", ".html")
SPAN = re.compile(r"`([^`\n]+)`")
PATH_TOKEN = re.compile(r"^[A-Za-z0-9_.\-/*]+$")
# What the app, a build or a developer's machine makes: named in documents, never in the repository.
NOT_IN_THE_REPO = (".venv", "node_modules", "dist/", "build/", "AlletraOnboard", ".alletra_onboard",
                   "~", "/", "http", "$", "%")
# Where a document's short path can start from, as folders from the repository root.
DOC_ROOTS = ("", "{app}", "{app}src/", "{app}src/alletra_onboard/", "{app}src/alletra_onboard/application/",
             "{app}src/alletra_onboard/adapters/", "{app}frontend/", "{app}frontend/src/", "{app}docs/",
             "{app}tests/", "{app}tests/fixtures/")


def documents() -> list[str]:
    """The documents that describe the structure, from the repository root (STANDARD C2)."""
    named = ["AGENTS.md", "README.md", app_prefix() + "CONTEXT.md", app_prefix() + "README.md"]
    design = [name for name in repo_files() if name.startswith(app_prefix() + "docs/design/") and name.endswith(".md")]
    return [name for name in named if name in repo_files()] + design


@cache
def _repo_index() -> tuple[frozenset[str], frozenset[str]]:
    """(every file and folder of the repository, every file name)."""
    paths: set[str] = set()
    for name in repo_files():
        paths.add(name)
        parts = name.split("/")
        paths.update("/".join(parts[:depth]) for depth in range(1, len(parts)))
    return frozenset(paths), frozenset(name.rsplit("/", 1)[-1] for name in repo_files())


def _is_code_path(token: str, roots: list[str]) -> bool:
    """A token is taken for a code path when it ends like a code file, ends with a slash, or starts
    with a folder that exists; `origin/main`, `SUCCEEDED/FAILED` and a bare `.ps1` are none of these."""
    if not PATH_TOKEN.match(token) or token.startswith(NOT_IN_THE_REPO) or ".." in token or "//" in token:
        return False
    if "/" not in token:
        return token.endswith(CODE_SUFFIXES) and not token.startswith(".")
    paths, _names = _repo_index()
    return (token.endswith(CODE_SUFFIXES) or token.endswith("/")
            or any((root + token.split("/")[0]) in paths for root in roots))


def _resolves(token: str, roots: list[str]) -> bool:
    paths, names = _repo_index()
    token = token.rstrip("/")
    if "*" in token:
        pattern = re.compile("(?:" + "|".join(re.escape(root) for root in roots) + "|.*/)"
                             + re.escape(token).replace(r"\*", "[^/]*") + "$")
        return any(pattern.match(path) for path in paths)
    if any((root + token) in paths for root in roots) or ("/" not in token and token in names):
        return True
    # `platform/tls.ssl_context` names a function in platform/tls.py
    folder, _, last = token.rpartition("/")
    return bool(folder) and "." in last and any(f"{root}{folder}/{last.split('.')[0]}.py" in paths for root in roots)


def doc_paths(doc: str) -> dict[str, int]:
    """The code paths a document names in backticks, outside code blocks, each with its first line."""
    roots = [root.format(app=app_prefix()) for root in DOC_ROOTS] + [doc.rsplit("/", 1)[0] + "/" if "/" in doc else ""]
    named: dict[str, int] = {}
    fenced = False
    for row, line in enumerate((repo_root() / doc).read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if fenced:
            continue
        for span in SPAN.findall(line):
            for word in span.replace("\\", "/").split():
                token = word.split("::")[0].strip("()[],;:'\"").rstrip(".").removeprefix("./")
                if _is_code_path(token, roots) and not _resolves(token, roots):
                    named.setdefault(token, row)
    return named


def measure_doc_paths() -> Found:
    return {SEP.join((doc, token)): (1, f"line {row}") for doc in documents() for token, row in doc_paths(doc).items()}


# ---- C3: Markdown lives in the folders that exist today ----

def _markdown_folder(name: str) -> str:
    return name.rsplit("/", 1)[0] if "/" in name else "."


def _listed_as(folder: str, listed: list[str]) -> str | None:
    """The entry that allows Markdown in the folder: the folder itself, or a `tree/**` above it."""
    if folder in listed:
        return folder
    return next((entry for entry in listed if entry.endswith("/**") and (folder + "/").startswith(entry[:-2])), None)


def markdown_folders_used(listed: list[str]) -> set[str]:
    return {entry for name in repo_files() if name.endswith(".md")
            if (entry := _listed_as(_markdown_folder(name), listed))}


def check_markdown_folders(ceilings: dict) -> Report:
    listed: list[str] = ceilings.get("markdown-folders", {}).get("folders", [])
    report = Report(listed=len(listed))
    for name in repo_files():
        if name.endswith(".md") and not _listed_as(_markdown_folder(name), listed):
            report.new.append(f"NEW   [markdown-folders] {name}. STANDARD C3: Markdown lives in the folders that "
                              f"have it today. Put the file in one of them; a new folder is the owner's call.")
    for entry in sorted(set(listed) - markdown_folders_used(listed)):
        report.stale.append(f"STALE [markdown-folders] {entry}: listed, and it holds no Markdown now. Delete it "
                            f"from quality/ceilings.toml.")
    return report


def markdown_folders_today() -> list[str]:
    """Used once, by --seed. A tree of captures or mirrored pages is listed as one entry."""
    trees = ["archive/**", "reference/**", app_prefix() + "tests/fixtures/**"]
    return sorted({_listed_as(_markdown_folder(name), trees) or _markdown_folder(name)
                   for name in repo_files() if name.endswith(".md")})


# ---- C4: a lesson names the check that now catches its defect ----

LESSON = re.compile(r"^\*\*(\d+)\. ")
OLD_LESSONS = 49
RUFF_CODE = re.compile(r"^[A-Z]{1,4}\d{3,4}$")


@cache
def _check_ids() -> frozenset[str]:
    """Rule ids the gate knows: ruff rules that are on, import contracts, eslint rules in the config."""
    ids = set(re.findall(r"\(([A-Z]+\d+)\)", run([sys.executable, "-m", "ruff", "check", "--show-settings",
                                                  "src/alletra_onboard/__init__.py"]).split("linter.rules.should_fix")[0]))
    for config in ("pyproject.toml", "quality/imports-type-only.toml"):
        with (APP / config).open("rb") as handle:
            ids.update(contract["id"] for contract in tomllib.load(handle)["tool"]["importlinter"]["contracts"])
    eslint = APP / "frontend" / "eslint.config.js"
    if eslint.is_file():
        ids.update(re.findall(r"""["']([@a-z][a-z0-9/-]+)["']\s*:""", eslint.read_text(encoding="utf-8")))
    return frozenset(ids)


def _test_exists(test_id: str) -> bool:
    path, _, name = test_id.partition("::")
    file = next((root / path for root in (APP, repo_root()) if (root / path).is_file()), None)
    if file is None or not name:
        return False
    if file.suffix != ".py":
        return name in file.read_text(encoding="utf-8")
    return name.replace("::", ".") in {scope for _first, _last, scope in _scopes(file)}


def check_lessons(_ceilings: dict) -> Report:
    report = Report()
    text = (APP / "docs" / "LESSONS.md").read_text(encoding="utf-8").splitlines()
    starts = [(row, int(match.group(1))) for row, line in enumerate(text) if (match := LESSON.match(line))]
    for index, (row, number) in enumerate(starts):
        if number <= OLD_LESSONS:
            continue
        end = starts[index + 1][0] if index + 1 < len(starts) else len(text)
        body = "\n".join(line for line in text[row:end] if not line.startswith("## "))
        tokens = [token.strip() for token in SPAN.findall(body)]
        tests = [token for token in tokens if "::" in token]
        broken = [token for token in tests if not _test_exists(token)]
        rules = [token for token in tokens if token in _check_ids()]
        if broken:
            report.new.append(f"NEW   [lessons] lesson {number} names a test that does not exist: "
                              f"{', '.join(broken)}. STANDARD C4: write the id as `tests/unit/test_x.py::test_name`.")
        elif not tests and not rules:
            report.new.append(f"NEW   [lessons] lesson {number} names no test and no lint rule. STANDARD C4: a new "
                              f"lesson lands with the check that now catches its defect, named in backticks: a "
                              f"test id (`tests/unit/test_x.py::test_name`), a ruff rule (`BLE001`), an import "
                              f"contract id (`L3-clients-only`) or an eslint rule.")
    return report

TABLES: dict[str, Table] = {table.name: table for table in (
    Table("complexity",
          "STANDARD M1. `file :: function :: rule` = the function's number today: C901 complexity (limit 10),\n"
          "PLR0913 parameters (5), PLR0912 branches (12), PLR0915 statements (50). A listed function may not\n"
          "get worse; it is fixed when it is next changed for any reason.",
          measure_complexity,
          lambda key: "STANDARD M1: a function stays within complexity 10, 5 parameters, 12 branches and 50 "
                      "statements. Simplify it: a table, or a helper that hides a decision.",
          "STANDARD M1: a listed function may not get worse. Bring it back to its ceiling or lower."),
    Table("lint",
          "Every other ruff rule. `file :: function :: rule` = how many times the function breaks the rule.\n"
          "BLE001 is E1, S110 and S112 are E2, PLC0415 is L6, PGH003 and RUF100 are T3, ERA001, FIX and TD are C1.",
          measure_lint,
          lint_guidance,
          "The function breaks the rule more often than it did. Take the new one out."),
    Table("pyright",
          "STANDARD T2. `file` = its pyright errors today (`standard` on src, `strict` on src/alletra_onboard/domain;\n"
          "pyrightconfig.json). The count depends on the packages installed: use the dev extra's versions.",
          measure_pyright,
          lambda key: "STANDARD T2: the backend type-checks, and a file with no errors stays that way. Fix the "
                      "types (frontend/node_modules/.bin/pyright -p pyrightconfig.json lists them).",
          "STANDARD T2: a listed file may not gain type errors. Fix the new ones "
          "(frontend/node_modules/.bin/pyright -p pyrightconfig.json lists them)."),
    Table("vulture",
          "STANDARD M3. `file :: finding` = how often vulture reports it at 80% confidence in src. A finding is\n"
          "a lead, not proof: delete code only after showing that nothing reaches it (LESSONS 18).",
          measure_vulture,
          lambda key: DEAD_CODE,
          DEAD_CODE),
    Table("knip",
          "STANDARD M3. `file :: kind :: name` = one knip finding in the frontend (unused file, export, type\n"
          "or dependency). A finding is a lead, not proof, like vulture's.",
          measure_knip,
          lambda key: DEAD_CODE,
          DEAD_CODE),
    Table("file-lines",
          "STANDARD M2. `file` = its lines today, for a source file over 500 lines (src and frontend/src, tests\n"
          "left out). The file may not grow. Splitting it only to get under a number is not a fix: a split\n"
          "hides a decision, removes duplication or makes behaviour testable on its own.",
          measure_file_lines,
          lambda key: f"STANDARD M2: a file over {LONG} lines may not grow, and this one just crossed it. Put the "
                      f"new code where its decision lives, in a module of its own if it has one.",
          f"STANDARD M2: a file over {LONG} lines may not grow. Put the new code in the module it belongs to, or "
          f"take as many lines out as you add."),
    Table("suppress-exception",
          "STANDARD E2. `file :: function` = its `suppress(Exception)` and `suppress(BaseException)` calls today.",
          measure_suppress,
          lambda key: "STANDARD E2: no silent swallowing. Name the error the call can raise in `suppress(...)`, "
                      "or handle it.",
          "STANDARD E2: no silent swallowing. Name the error the call can raise in `suppress(...)`, or handle it."),
    Table("doc-paths",
          "STANDARD C2. `document :: path` = a code path the document names in backticks that is not in the\n"
          "repository. The documents are AGENTS.md, README.md, the app's CONTEXT.md and README.md and docs/design.",
          measure_doc_paths,
          lambda key: "STANDARD C2: a document names only code that exists. Correct the path in the document, in "
                      "the change that moved or removed the file.",
          "STANDARD C2: a document names only code that exists."),
)}

# Tables that hold a list, not ceilings: name -> comment.
EXTRA_TABLES: dict[str, str] = {
    "markdown-folders": "STANDARD C3. The folders that hold Markdown today, from the repository root (`.` is the\n"
                        "root, `folder/**` a whole tree of captures or mirrored pages). A Markdown file\n"
                        "anywhere else fails. Adding a folder here is the owner's call.",
}

# section name -> the tables it compares, and the checks that keep no ceilings
SECTIONS: dict[str, tuple[tuple[str, ...], tuple[Callable[[dict], Report], ...]]] = {
    "lint": (("lint",), ()),
    "complexity": (("complexity",), ()),
    "pyright": (("pyright",), ()),
    "vulture": (("vulture",), ()),
    "knip": (("knip",), ()),
    "files": (("file-lines",), ()),
    "suppress": (("suppress-exception",), ()),
    "docs": (("doc-paths",), (check_markdown_folders,)),
    "lessons": ((), (check_lessons,)),
}


# ---- ceilings.toml ----

def load_ceilings() -> dict:
    if not CEILINGS.is_file():
        return {}
    with CEILINGS.open("rb") as handle:
        return tomllib.load(handle)


def _quote(key: str) -> str:
    return '"' + key.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_ceilings(ceilings: dict) -> None:
    """The header comment is kept as it is; every table is written again, sorted."""
    header = []
    if CEILINGS.is_file():
        for line in CEILINGS.read_text(encoding="utf-8").splitlines():
            if line.startswith("["):
                break
            header.append(line)
    out = "\n".join(header).rstrip() + "\n"
    for name, table in TABLES.items():
        if name not in ceilings:
            continue
        out += f"\n[{name}]\n" + "".join(f"# {line}\n" for line in table.comment.splitlines())
        out += "".join(f"{_quote(key)} = {value}\n" for key, value in sorted(ceilings[name].items()))
    for name, lists in EXTRA_TABLES.items():
        if name in ceilings:
            out += f"\n[{name}]\n" + "".join(f"# {line}\n" for line in lists.splitlines())
            for key, values in ceilings[name].items():
                out += f"{key} = [\n" + "".join(f"  {_quote(value)},\n" for value in sorted(values)) + "]\n"
    CEILINGS.write_text(out, encoding="utf-8")


def compare(table: Table, listed: dict[str, int], found: Found) -> Report:
    report = Report(listed=len(listed))
    for key, (value, where) in sorted(found.items()):
        if key not in listed:
            report.new.append(f"NEW   [{table.name}] {key} = {value} ({where}). {table.new(key)} "
                              f"Do not add it to quality/ceilings.toml.")
        elif value > listed[key]:
            report.worse.append(f"WORSE [{table.name}] {key} = {value}, its ceiling is {listed[key]} ({where}). "
                                f"{table.worse}")
        elif value < listed[key]:
            report.lower += 1
    for key in sorted(set(listed) - set(found)):
        report.stale.append(f"STALE [{table.name}] {key}: listed, and its violation is gone. Delete its line "
                            f"from quality/ceilings.toml (or run scripts/fitness.py --tighten).")
    return report


def tighten(ceilings: dict, sections: list[str], seed: bool) -> int:
    changed = 0
    for name in (table for section in sections for table in SECTIONS[section][0]):
        found = TABLES[name].measure()
        if name not in ceilings:
            if seed:
                ceilings[name] = {key: value for key, (value, _where) in found.items()}
                changed += len(found)
            continue
        table = ceilings[name]
        for key in list(table):
            today = found.get(key, (0, ""))[0]
            if today == 0:
                del table[key]
                changed += 1
            elif today < table[key]:
                table[key] = today
                changed += 1
    if "docs" in sections:
        if "markdown-folders" in ceilings:
            folders = ceilings["markdown-folders"]["folders"]
            kept = [entry for entry in folders if entry in markdown_folders_used(folders)]
            changed += len(folders) - len(kept)
            ceilings["markdown-folders"]["folders"] = kept
        elif seed:
            ceilings["markdown-folders"] = {"folders": markdown_folders_today()}
            changed += len(ceilings["markdown-folders"]["folders"])
    write_ceilings(ceilings)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sections", nargs="*", metavar="section", help=", ".join(SECTIONS))
    parser.add_argument("--tighten", action="store_true",
                        help="lower ceilings to today's values and drop entries whose violation is gone")
    parser.add_argument("--seed", action="store_true",
                        help="write today's violations for a table the file does not have yet (used once, "
                             "when a check is introduced)")
    args = parser.parse_args()
    unknown = [name for name in args.sections if name not in SECTIONS]
    if unknown:
        parser.error(f"no section named {', '.join(unknown)}; the sections are {', '.join(SECTIONS)}")
    names = args.sections or list(SECTIONS)
    label = f"fitness[{', '.join(names)}]"
    ceilings = load_ceilings()
    try:
        if args.tighten or args.seed:
            changed = tighten(ceilings, names, args.seed)
            print(f"{label}: {changed} entr{'y' if changed == 1 else 'ies'} changed in quality/ceilings.toml")
            return 0
        total = Report()
        for name in names:
            tables, checks = SECTIONS[name]
            for table in tables:
                total.add(compare(TABLES[table], ceilings.get(table, {}), TABLES[table].measure()))
            for check in checks:
                total.add(check(ceilings))
    except ToolError as exc:
        print(f"{label}: could not run. {exc}")
        return 1
    for line in total.new + total.worse + total.stale:
        print(line)
    print(f"{label}: {total.listed} listed, {len(total.new)} new, {len(total.worse)} worse, "
          f"{len(total.stale)} stale" + (f" ({total.lower} can be lowered: --tighten)" if total.lower else ""))
    return 1 if total.failed else 0


if __name__ == "__main__":
    sys.exit(main())
