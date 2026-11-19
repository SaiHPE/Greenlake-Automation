"""Dependency pins that protect field behaviour, not just the build."""

from __future__ import annotations

import ast
import importlib.util
import tomllib
from pathlib import Path

APP = Path(__file__).resolve().parents[2]
PYPROJECT = APP / "pyproject.toml"
SPEC = APP / "alletra_onboard.spec"


def _strings(node: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _sets_hiddenimports(node: ast.AST) -> bool:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AugAssign) else []
    return any(isinstance(target, ast.Name) and target.id == "hiddenimports" for target in targets)


def _spec_names() -> tuple[set[str], set[str]]:
    """What the PyInstaller spec names as literals: (modules it collects or hides, paths it reads)."""
    modules: set[str] = set()
    paths: set[str] = set()
    for node in ast.walk(ast.parse(SPEC.read_text(encoding="utf-8"))):
        called = node.func.id if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) else ""
        if called in ("collect_submodules", "collect_data_files"):
            modules.update(_strings(node.args[0]))
        elif called in ("Tree", "Analysis"):
            paths.update(_strings(node.args[0]))
            paths.update(s for keyword in node.keywords if keyword.arg in ("pathex", "runtime_hooks")
                         for s in _strings(keyword.value))
        elif _sets_hiddenimports(node):
            modules.update(s for part in ast.walk(node.value) if isinstance(part, ast.List) for s in _strings(part))
    return modules, paths


def test_every_module_and_path_the_packaging_spec_names_exists():
    """STANDARD X3 (LESSONS 16): a module that moved, or a dependency that was dropped, breaks the
    packaged .exe without failing any other test. v0.14.0-rc.1 shipped without the WSAPI SDK that way."""
    modules, paths = _spec_names()
    assert {"alletra_onboard", "uvicorn", "hpe3parclient"} <= modules, "the spec is no longer read correctly"
    assert {"packaging/app_main.py", "src", "frontend/dist"} <= paths, "the spec is no longer read correctly"
    missing_modules = sorted(name for name in modules if importlib.util.find_spec(name) is None)
    missing_paths = sorted(path for path in paths if not (APP / path).exists())
    assert not missing_modules, (
        f"alletra_onboard.spec names modules that cannot be imported: {missing_modules}. "
        "Fix the name in the spec, or add the package to pyproject.toml.")
    assert not missing_paths, (
        f"alletra_onboard.spec names paths that do not exist: {missing_paths}. "
        "Fix the path in the spec in the same change that moved the file.")


def test_paramiko_stays_below_4_so_old_fos_switches_can_still_be_read():
    """BL-40: FOS 7.0.2c offers only SHA-1 kex and ssh-rsa/ssh-dss, which paramiko 4/5 removed."""
    deps = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["dependencies"]
    paramiko = [d.replace(" ", "") for d in deps if d.lower().startswith("paramiko")]
    assert paramiko == ["paramiko>=3.4.0,<4"], (
        "paramiko must stay below 4: FOS 7.x switches need SHA-1 kex / ssh-rsa / ssh-dss (BL-40, LESSONS 43). "
        "The Dependabot SHA-1 alert on 3.x was accepted on purpose; do not bump the pin to clear it.")
