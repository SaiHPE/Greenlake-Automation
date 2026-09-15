"""SPEC-006: the runner ships to Windows PowerShell 5.1, which reads a BOM-less script as ANSI.
Live 2026-09-14 (rc.14): a UTF-8 em dash decoded to `â€”`, and 0x94 is a smart quote that closed the
string early - 'Unexpected token' at line 69 before the first prompt. Pure ASCII cannot do that."""

from pathlib import Path

RUNNER = Path(__file__).resolve().parents[2] / "scripts" / "session.ps1"


def test_session_runner_is_pure_ascii():
    text = RUNNER.read_bytes()
    bad = sorted({b for b in text if b > 127})
    assert not bad, f"non-ASCII bytes in session.ps1: {[hex(b) for b in bad]} - PS 5.1 reads them as ANSI"


def test_session_runner_never_writes_outside_the_tool():
    # R7: only the app's API, WSAPI GETs, and the tool's own removal lines over SSH.
    text = RUNNER.read_text(encoding="ascii")
    for forbidden in ("zonecreate", "cfgsave", "cfgenable", "createvv", "createvlun", "createhost"):
        assert forbidden not in text


def test_runner_acceptance_pattern_catches_the_polite_refusals_of_s12():
    """S-12 (2026-09-14): the array refused `removehost` and `removevv -f` for objects still in a set,
    with no 'Error' in the text, and the rc.15 check passed. The pattern in session.ps1 must flag the
    exact lines the array wrote (tests/fixtures/rack13_array/cleanup_refused_s12.txt)."""
    import re

    script = RUNNER.read_text(encoding="ascii")
    m = re.search(r"\$_ -match '([^']+)'", script)
    assert m, "acceptance pattern not found in session.ps1"
    pattern = re.compile(m.group(1))
    transcript = (Path(__file__).resolve().parents[1] / "fixtures" / "rack13_array" / "cleanup_refused_s12.txt").read_text()
    flagged = [line for line in transcript.splitlines() if pattern.search(line)]
    assert len(flagged) == 3
    assert all("member of" in line for line in flagged)
    assert not any(line.startswith("rack13arcus cli% Issuing removevlun") for line in flagged)
