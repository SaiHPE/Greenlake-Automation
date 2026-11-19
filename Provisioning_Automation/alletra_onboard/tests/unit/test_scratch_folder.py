"""Tests run in a scratch folder, never the app folder: the sheet upload writes `.env` relative to the
working directory, and a test run once replaced a developer's GreenLake credentials with test values."""

from __future__ import annotations

from pathlib import Path

APP = Path(__file__).resolve().parents[2]


def test_a_test_never_runs_in_the_app_folder():
    assert Path.cwd().resolve() != APP
    assert not (Path.cwd() / "pyproject.toml").exists()
