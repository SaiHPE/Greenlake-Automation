"""The words the UI lab scripts press and read stay in the source (SPEC-030 R10, ADR 0023 change 3).

`lab/ui_live_lab.py`, `lab/ui_provision_lab.py` and `lab/failed_apply_lab.py` drive the screens in a
browser: they press buttons by name and look for text on the page. This test reads them with `ast`,
takes every literal they press, fill or look for, and finds each one in `frontend/src`, or where the
few made elsewhere are made (`ELSEWHERE`). A miss names the literal, the script and its line. Object
names and commands built from a script's own constants are skipped.

Its limit: it proves the words are still in the source, not that they are drawn in the state a script
reads them (a closed section renders nothing). The screenshots and the lab run check that.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from alletra_onboard.domain.workflow import STEP_REGISTRY

APP = Path(__file__).resolve().parents[2]
LAB = APP / "lab"
FRONTEND = APP / "frontend" / "src"
SCRIPTS = ("failed_apply_lab.py", "ui_live_lab.py", "ui_provision_lab.py")

# Read by a script but made elsewhere, or built from parts: what to find instead, where, and why.
ELSEWHERE: dict[str, tuple[str, str, str]] = {
    "Stopped while creating volume set": (
        "Stopped while creating", "src/alletra_onboard/application/provisioning/storage_provision.py",
        "the apply's own error: the backend makes it from the object's kind and name"),
    "The console runs the tool's read-only commands": (
        "The console runs the tool's read-only commands", "src/alletra_onboard/application/runs/console.py",
        "the console's refusal: the backend sends it and the page shows it as it comes"),
    "%d created": (
        "} created", "frontend/src/steps/ProvisionStep.tsx",
        "the status line after a create counts the objects: `${created} created`"),
    "%d objects were created before it stopped": (
        "created before it stopped", "frontend/src/steps/ProvisionStep.tsx",
        "the failed-apply status line counts the objects and says object or objects"),
}
# The rail labels of the run's steps are the step registry's (AGENTS rule 5), served by /app/profile;
# the steps that frame a run (Prerequisites, ..., Finish, Run overview) are `label`s in the frontend.
REGISTRY_LABELS = {step.label.lower() for step in STEP_REGISTRY}


@dataclass(frozen=True)
class Word:
    text: str
    script: str
    line: int
    how: str
    case: bool = False      # the script compares case-sensitively
    rail: bool = False      # a rail label, clicked in the nav

    def where(self) -> str:
        return f"lab/{self.script}:{self.line}, {self.how}"


def _flat(text: str) -> str:
    return " ".join(text.split())


def _constants(tree: ast.Module) -> dict[str, str]:
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            out.update({t.id: node.value.value for t in node.targets if isinstance(t, ast.Name)})
    return out


def _string(node: ast.AST | None, consts: dict[str, str]) -> str | None:
    """A literal, a module-level string constant (`consts`), or the fixed text a string is built from
    ("%d created" % n, "Stopped while creating volume " + VOL2)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return consts.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mod, ast.Add)) and isinstance(node.left, ast.Constant):
        return node.left.value if isinstance(node.left.value, str) else None
    return None


def _regex_words(pattern: str) -> str:
    """The fixed words a pattern starts with: `^Continue to ` is "Continue to", `Console \\(\\d+ command`
    is "Console (", `^Run$` is "Run"."""
    out, i = [], 1 if pattern.startswith("^") else 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            nxt = pattern[i + 1:i + 2]
            if not nxt or nxt.isalnum():
                break
            out.append(nxt)
            i += 2
            continue
        if c in ".^$*+?{}[]|()":
            break
        out.append(c)
        i += 1
    return "".join(out)


def _regex(node: ast.AST) -> tuple[str, bool] | None:
    """`re.compile("<constant>"[, re.I])`: its fixed words and whether it ignores case."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "compile"):
        return None
    if not node.args or not (isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
        return None     # built from a variable (`press(label)`): the caller's literal is collected instead
    flags = ast.unparse(node.args[1]) if len(node.args) > 1 else ""
    return _regex_words(node.args[0].value), "re.I" in flags or "IGNORECASE" in flags


def _callee(call: ast.Call) -> tuple[str, str]:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id, ""
    if isinstance(func, ast.Attribute):
        return func.attr, func.value.id if isinstance(func.value, ast.Name) else ""
    return "", ""


def collect(script: str) -> list[Word]:
    tree = ast.parse((LAB / script).read_text(encoding="utf-8"))
    consts = _constants(tree)
    words: list[Word] = []

    def add(node, how, *, case=False, rail=False, line=None, named=False):
        # a name given to press or page_ok is an object the script makes (HOST, VOL); only a sentence
        # the script keeps in a constant and looks for `in text` (REFUSED_START) is read through its name
        text = _string(node, consts if named else {})
        if text and _flat(text):
            words.append(Word(_flat(text), script, line or node.lineno, how, case, rail))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "STEP_PAGES" for t in node.targets):
            for row in node.value.elts:
                label, phrase = row.elts
                add(label, "STEP_PAGES rail label", rail=True)
                for p in phrase.elts if isinstance(phrase, ast.Tuple) else [phrase]:
                    add(p, "STEP_PAGES phrase")
        elif isinstance(node, ast.Compare) and isinstance(node.ops[0], ast.In) and isinstance(node.comparators[0], ast.Name):
            if node.comparators[0].id == "text":
                add(node.left, "`in text`", case=True, named=True)
        elif isinstance(node, ast.Call):
            name, receiver = _callee(node)
            if name == "press" and node.args:
                add(node.args[0], "press", case=True)
            elif name == "until" and node.args:
                add(node.args[0], "until")
            elif name == "page_ok":
                for p in node.args[2:]:
                    add(p, "page_ok")
            elif name == "look" and len(node.args) > 1:
                phrase = node.args[1]
                for p in phrase.elts if isinstance(phrase, ast.Tuple) else [phrase]:
                    add(p, "look")
            elif name in ("get_by_text", "get_by_label") and node.args:
                exact = any(k.arg == "exact" and ast.unparse(k.value) == "True" for k in node.keywords)
                pattern = _regex(node.args[0])
                if pattern:
                    words.append(Word(_flat(pattern[0]), script, node.lineno, f"{name} pattern", not pattern[1], receiver == "rail"))
                else:
                    add(node.args[0], name, case=exact, rail=receiver == "rail")
            for k in node.keywords:
                if k.arg == "has_text":
                    add(k.value, "has_text", line=node.lineno)
                elif k.arg == "name" and name == "get_by_role":
                    pattern = _regex(k.value)
                    if pattern:
                        words.append(Word(_flat(pattern[0]), script, node.lineno, "get_by_role name", not pattern[1]))
                    else:
                        add(k.value, "get_by_role name", case=True, line=node.lineno)
    return [w for w in words if w.text]


def _source(where: Path) -> str:
    files = [where] if where.is_file() else sorted(p for p in where.rglob("*") if p.suffix in (".ts", ".tsx", ".py"))
    return "\n".join(p.read_text(encoding="utf-8") for p in files)


FRONTEND_TEXT = _source(FRONTEND)


def _contains(haystack: str, needle: str, case: bool) -> bool:
    haystack, needle = _flat(haystack), _flat(needle)
    return needle in haystack if case else needle.lower() in haystack.lower()


def missing(word: Word) -> str | None:
    """Why the word is not found, or None when it is."""
    if word.rail:
        if word.text.lower() in REGISTRY_LABELS:
            return None
        label = r"label\s*[:=]\s*['\"]" + re.escape(word.text) + r"['\"]"
        if re.search(label, FRONTEND_TEXT, re.IGNORECASE):
            return None
        return f"'{word.text}' ({word.where()}) is neither a step registry label nor a rail `label` in frontend/src"
    if word.text in ELSEWHERE:
        find, where, _why = ELSEWHERE[word.text]
        if _contains(_source(APP / where), find, case=True):
            return None
        return f"'{word.text}' ({word.where()}): '{find}' is not in {where}"
    if _contains(FRONTEND_TEXT, word.text, word.case):
        return None
    return f"'{word.text}' ({word.where()}) is not in frontend/src"


ALL = [w for script in SCRIPTS for w in collect(script)]


def test_every_word_the_lab_scripts_press_or_read_is_in_the_source():
    misses = [why for why in map(missing, ALL) if why]
    assert not misses, "frozen UI words gone from the source (SPEC-030 R10):\n  " + "\n  ".join(misses)


def test_the_reader_finds_the_words_spec_030_freezes():
    """If a script changes how it presses or reads, the reader must still see the frozen words, or
    the test above passes on nothing."""
    frozen = {
        "Build plan", "Rebuild plan", "Create storage objects", "Verify paths", "Continue with", "Continue to",
        "I have reviewed this plan", "Undo what this run created", "Activity", "Console (", "Run",
        "Read-only command", "Runs", "Your runs", "Run overview", "Finish", "Checked by this tool",
        "Initialisation sheet", "What do you want to do", "Fibre Channel port", "the array can reach", "Fabrics",
        "No host is zoned", "plan", "Read both arrays", "sequence", "Configuration", "Cover details",
        "Documents and logs", "Hand-over package", "Start a new run", "discover", "No plan yet",
        "Review the plan, then approve creation", "Review the plan", "Tick the box first", "%d created",
        "What the array answered", "Verify the paths next", "read back", "Creation reported an error",
        "%d objects were created before it stopped", "Removal command set", "Stopped while creating volume set",
        "The console runs the tool's read-only commands",
    }
    assert frozen <= {w.text for w in ALL}, sorted(frozen - {w.text for w in ALL})
    rails = {w.text.lower() for w in ALL if w.rail}
    assert {"prerequisites", "san zoning", "provision storage", "as-built document", "run overview"} <= rails


def _drives_a_browser(path: Path) -> bool:
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else (
            [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
        if any(n == "playwright" or n.startswith("playwright.") for n in names):
            return True
    return False


def test_every_lab_script_that_drives_the_browser_is_read_here():
    """A new browser script under lab/ joins SCRIPTS on purpose, so its words are frozen too."""
    drivers = sorted(p.relative_to(LAB).as_posix() for p in LAB.rglob("*.py") if _drives_a_browser(p))
    assert drivers == sorted(SCRIPTS), f"lab scripts that import Playwright: {drivers}; read here: {sorted(SCRIPTS)}"


def test_the_link_check_is_called_check_rc_link_on_the_page_and_in_the_runners():
    """The owner's name for the link check (2026-11-19, after the customer demo): *Check RC link* and
    *Check RC link again* on the Replication page, never *Check the link*. The runners that check the
    apply's refusal look for the backend's own words."""
    page = (FRONTEND / "steps" / "ReplicationStep.tsx").read_text(encoding="utf-8")
    assert "'Check RC link'" in page and "'Check RC link again'" in page
    assert "check the link" not in FRONTEND_TEXT.lower()
    refusal = "Check RC link first"
    assert refusal in (APP / "src" / "alletra_onboard" / "application" / "replication" / "steps.py").read_text(encoding="utf-8")
    for script in ("rc_link_lab.py", "rc_preset_lab.py", "rcip_tool_lab.py"):
        text = (LAB / script).read_text(encoding="utf-8")
        assert refusal in text and "Check the link" not in text, script
