"""The gate's own behaviour: scripts/fitness.py run on a throwaway repository, as scripts/check.py runs it,
and what scripts/check.py makes of two versions of the lists."""

import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
CHECK = runpy.run_path(str(SCRIPTS / "check.py"))
# Written in two parts so that this file holds no suppression comment of its own.
TYPE_IGNORE = "# type" + ": ignore[arg-type]"
ESLINT_DISABLE = "// eslint" + "-disable-next-line no-console"


@pytest.fixture
def app(tmp_path):
    """An app folder in a new git repository. fitness.py measures the folder it sits in, so it gets a copy."""
    app = tmp_path / "app"
    for folder in ("scripts", "quality", "src", "docs"):
        (app / folder).mkdir(parents=True)
    shutil.copy(SCRIPTS / "fitness.py", app / "scripts")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return app


def fitness(app, *args):
    proc = subprocess.run([sys.executable, "scripts/fitness.py", *args], cwd=app, capture_output=True, text=True,
                          check=False)
    return proc.returncode, proc.stdout


def list_violations(app, text):
    (app / "quality" / "ceilings.toml").write_text(text, encoding="utf-8")


def listed(app):
    return (app / "quality" / "ceilings.toml").read_text(encoding="utf-8")


def swallowing(app, times, function="read"):
    """A module whose one function swallows every error `times` times (STANDARD E2)."""
    body = "    with suppress(Exception):\n        pass\n" * times or "    pass\n"
    (app / "src" / "reader.py").write_text(f"from contextlib import suppress\n\n\ndef {function}():\n{body}",
                                           encoding="utf-8")


def test_a_violation_that_is_not_listed_fails_as_new(app):
    swallowing(app, 1)

    code, out = fitness(app, "suppress")

    assert code == 1
    assert "NEW   [suppress-exception] src/reader.py :: read = 1" in out


def test_a_listed_violation_passes_until_it_gets_worse(app):
    list_violations(app, '[suppress-exception]\n"src/reader.py :: read" = 1\n')
    swallowing(app, 1)
    assert fitness(app, "suppress")[0] == 0

    swallowing(app, 2)
    code, out = fitness(app, "suppress")

    assert code == 1
    assert "WORSE [suppress-exception] src/reader.py :: read = 2, its ceiling is 1" in out


def test_a_listed_violation_that_is_gone_fails_as_stale_until_tighten_drops_it(app):
    list_violations(app, '[suppress-exception]\n"src/reader.py :: read" = 1\n')
    swallowing(app, 0)

    code, out = fitness(app, "suppress")
    assert code == 1
    assert "STALE [suppress-exception] src/reader.py :: read" in out

    fitness(app, "--tighten", "suppress")
    assert "src/reader.py" not in listed(app)
    assert fitness(app, "suppress")[0] == 0


def test_tighten_lowers_a_ceiling_and_never_lists_a_new_violation(app):
    list_violations(app, '[suppress-exception]\n"src/reader.py :: read" = 3\n')
    swallowing(app, 2)
    (app / "src" / "other.py").write_text("from contextlib import suppress\nwith suppress(Exception):\n    pass\n",
                                          encoding="utf-8")

    fitness(app, "--tighten", "suppress")

    assert '"src/reader.py :: read" = 2' in listed(app)
    assert "other.py" not in listed(app)


def test_a_known_violation_added_or_raised_has_grown_and_a_lowered_one_has_not():
    before = {"quality/ceilings.toml": '[complexity]\n"a.py :: f :: C901" = 12\n"a.py :: g :: C901" = 14\n',
              "pyproject.toml": '[[tool.importlinter.contracts]]\nid = "L5"\nignore_imports = ["api -> store"]\n'}
    now = {"quality/ceilings.toml": '[complexity]\n"a.py :: f :: C901" = 13\n"a.py :: g :: C901" = 11\n'
                                    '"a.py :: h :: C901" = 11\n',
           "pyproject.toml": '[[tool.importlinter.contracts]]\nid = "L5"\n'
                             'ignore_imports = ["api -> store", "api -> ssh"]\n'}

    assert CHECK["grown"](now.get, before.get) == [
        "L5: api -> ssh", "complexity: a.py :: f :: C901", "complexity: a.py :: h :: C901"]


def test_move_renames_the_entry_of_renamed_code_keeps_its_number_and_is_not_growth(app):
    before = '[suppress-exception]\n"src/reader.py :: read" = 2\n'
    list_violations(app, before)
    swallowing(app, 2, function="read_all")
    assert fitness(app, "suppress")[0] == 1

    code, _out = fitness(app, "--move", "src/reader.py :: read", "src/reader.py :: read_all")

    assert code == 0
    assert '"src/reader.py :: read_all" = 2' in listed(app)
    assert fitness(app, "suppress")[0] == 0
    assert CHECK["grown"]({"quality/ceilings.toml": listed(app)}.get, {"quality/ceilings.toml": before}.get) == []


def test_move_refuses_code_that_got_worse_on_the_way(app):
    before = '[suppress-exception]\n"src/reader.py :: read" = 1\n'
    list_violations(app, before)
    swallowing(app, 2, function="read_all")

    code, out = fitness(app, "--move", "src/reader.py :: read", "src/reader.py :: read_all")

    assert code == 1
    assert "src/reader.py :: read_all is 2 today and src/reader.py :: read is listed at 1" in out
    assert listed(app) == before


def test_an_old_key_claimed_by_two_new_keys_is_growth():
    before = {"quality/ceilings.toml": '[complexity]\n"a.py :: f :: C901" = 30\n'}
    now = {"quality/ceilings.toml": '[complexity]\n"a.py :: g :: C901" = 15\n"a.py :: h :: C901" = 15\n'
                                    '[moves]\n"a.py :: g :: C901" = "a.py :: f :: C901"\n'
                                    '"a.py :: h :: C901" = "a.py :: f :: C901"\n'}

    assert CHECK["grown"](now.get, before.get) == ["complexity: a.py :: g :: C901", "complexity: a.py :: h :: C901"]


def test_a_file_may_not_gain_a_suppression_comment(app):
    list_violations(app, '[suppressions]\n"src/reader.py" = 1\n')
    (app / "src" / "reader.py").write_text(f"x: int = read()  {TYPE_IGNORE}\n", encoding="utf-8")
    assert fitness(app, "suppressions")[0] == 0

    (app / "src" / "reader.py").write_text(f"x: int = read()  {TYPE_IGNORE}\n" * 2, encoding="utf-8")
    (app / "frontend" / "src").mkdir(parents=True)
    (app / "frontend" / "src" / "page.ts").write_text(f"{ESLINT_DISABLE}\nconsole.log(1);\n", encoding="utf-8")
    code, out = fitness(app, "suppressions")

    assert code == 1
    assert "WORSE [suppressions] src/reader.py = 2, its ceiling is 1" in out
    assert "NEW   [suppressions] frontend/src/page.ts = 1" in out


def test_a_changed_tool_setting_is_named_and_a_deleted_ignore_imports_line_is_not():
    contract = '[[tool.importlinter.contracts]]\nid = "L5"\nforbidden_modules = ["adapters"]\n'
    before = {"pyproject.toml": '[tool.ruff.lint]\nignore = []\n' + contract + 'ignore_imports = ["a -> b"]\n',
              "frontend/package.json": '{"scripts": {"lint": "eslint src"}, "knip": {"ignore": ["dist/**"]}}'}
    fixed = {**before, "pyproject.toml": '[tool.ruff.lint]\nignore = []\n' + contract}
    loosened = {"pyproject.toml": '[tool.ruff.lint]\nignore = ["BLE001"]\n' + contract.replace("adapters", "nothing"),
                "frontend/package.json": '{"scripts": {"lint": "true"}, "knip": {"ignore": ["dist/**", "src/**"]}}'}

    assert CHECK["changed_settings"](fixed.get, before.get) == []
    assert CHECK["changed_settings"](loosened.get, before.get) == [
        "frontend/package.json knip", "frontend/package.json scripts", "pyproject.toml [tool.importlinter]",
        "pyproject.toml [tool.ruff]"]


def test_a_document_names_only_a_file_that_exists_and_a_name_the_file_defines(app):
    list_violations(app, '[markdown-folders]\nfolders = ["app"]\n')
    (app / "src" / "tls.py").write_text("def ssl_context():\n    return None\n", encoding="utf-8")
    (app / "README.md").write_text("TLS comes from `src/tls.ssl_context()` (`src/tls.py:1`).\n", encoding="utf-8")
    assert fitness(app, "docs")[0] == 0

    (app / "src" / "tls.py").write_text("def tls_context():\n    return None\n", encoding="utf-8")
    (app / "README.md").write_text("TLS comes from `src/tls.ssl_context()` (`src/gone.py:1-9`).\n", encoding="utf-8")
    code, out = fitness(app, "docs")

    assert code == 1
    assert "NEW   [doc-paths] app/README.md :: src/tls.ssl_context = 1" in out
    assert "NEW   [doc-paths] app/README.md :: src/gone.py = 1" in out


def test_a_new_lesson_names_a_check_that_exists_or_says_why_it_has_none(app):
    (app / "pyproject.toml").write_text('[tool.ruff.lint]\nextend-select = ["BLE001"]\n', encoding="utf-8")
    (app / "tests").mkdir()
    (app / "tests" / "test_http.py").write_text("def test_a_redirect_raises():\n    pass\n", encoding="utf-8")
    lessons = app / "docs" / "LESSONS.md"
    lessons.write_text("**50. A redirect is not a success.** `tests/test_http.py::test_a_redirect_raises`.\n\n"
                       "**51. A broad catch hid the cause.** `BLE001` refuses it now.\n\n"
                       "**52. Ask before a lab run.** No check: this is about how we work, not about code.\n",
                       encoding="utf-8")
    assert fitness(app, "lessons")[0] == 0

    lessons.write_text("**50. A redirect is not a success.** `tests/test_http.py::test_that_is_gone`.\n\n"
                       "**51. A broad catch hid the cause.** `E501` is a ruff rule, and not one we select.\n\n"
                       "**52. Ask before a lab run.** No check:\n", encoding="utf-8")
    code, out = fitness(app, "lessons")

    assert code == 1
    assert "lesson 50 names a test that does not exist: tests/test_http.py::test_that_is_gone" in out
    assert "lesson 51 names no test and no lint rule the configuration selects" in out
    assert "lesson 52 names no test and no lint rule the configuration selects" in out


def test_a_long_file_may_not_grow_and_joining_lines_does_not_hide_the_growth(app):
    list_violations(app, '[file-size]\n"src/big.py" = 21000\n')
    (app / "src" / "big.py").write_text("a = 1\n" * 7000, encoding="utf-8")
    assert fitness(app, "files")[0] == 0

    (app / "src" / "big.py").write_text("a = 1; a = 1; b = 2\n" + "a = 1\n" * 6998, encoding="utf-8")
    code, out = fitness(app, "files")

    assert code == 1
    assert "WORSE [file-size] src/big.py = 21005, its ceiling is 21000" in out
