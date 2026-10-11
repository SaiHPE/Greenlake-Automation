"""Dependency pins that protect field behaviour, not just the build."""

from __future__ import annotations

import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_paramiko_stays_below_4_so_old_fos_switches_can_still_be_read():
    """BL-40: FOS 7.0.2c offers only SHA-1 kex and ssh-rsa/ssh-dss, which paramiko 4/5 removed."""
    deps = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["dependencies"]
    paramiko = [d.replace(" ", "") for d in deps if d.lower().startswith("paramiko")]
    assert paramiko == ["paramiko>=3.4.0,<4"]
