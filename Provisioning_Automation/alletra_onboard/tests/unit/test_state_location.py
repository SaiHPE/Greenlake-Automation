"""X-10 (2026-09-17): run history must survive an exe-folder replacement, so frozen builds keep it
under %LOCALAPPDATA%\\AlletraOnboard — unless a store already sits beside the exe, or the operator set
the path explicitly."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_APP_MAIN = Path(__file__).resolve().parents[2] / "packaging" / "app_main.py"


@pytest.fixture
def app_main(monkeypatch):
    spec = importlib.util.spec_from_file_location("app_main_under_test", _APP_MAIN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    monkeypatch.delenv("STATE_DATABASE_PATH", raising=False)
    monkeypatch.delenv("ARTIFACT_DIR", raising=False)
    return mod


def test_state_goes_to_localappdata_when_nothing_is_beside_the_exe(app_main, tmp_path, monkeypatch):
    exe_dir = tmp_path / "AlletraOnboard"; exe_dir.mkdir()
    monkeypatch.chdir(exe_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    app_main._place_state()
    import os
    assert os.environ["STATE_DATABASE_PATH"] == str(tmp_path / "LocalAppData" / "AlletraOnboard" / "state.db")
    assert os.environ["ARTIFACT_DIR"] == str(tmp_path / "LocalAppData" / "AlletraOnboard" / "artifacts")
    assert (tmp_path / "LocalAppData" / "AlletraOnboard").is_dir()


def test_an_existing_store_beside_the_exe_is_kept(app_main, tmp_path, monkeypatch):
    exe_dir = tmp_path / "AlletraOnboard"; (exe_dir / ".alletra_onboard").mkdir(parents=True)
    (exe_dir / ".alletra_onboard" / "state.db").write_bytes(b"")
    monkeypatch.chdir(exe_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    app_main._place_state()
    import os
    assert "STATE_DATABASE_PATH" not in os.environ          # the default relative path still applies
    assert not (tmp_path / "LocalAppData").exists()


def test_an_explicit_path_wins(app_main, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("STATE_DATABASE_PATH", "D:/somewhere/state.db")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    app_main._place_state()
    import os
    assert os.environ["STATE_DATABASE_PATH"] == "D:/somewhere/state.db"
    assert not (tmp_path / "LocalAppData").exists()
