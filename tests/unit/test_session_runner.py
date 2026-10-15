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
    """R7: only the app's API, WSAPI GETs, and the tool's own removal lines over SSH to the ARRAY.
    From rc.24 the runner asserts on the rendered zoning command set (SPEC-010), so the FOS words may
    appear in comparisons - but never on a line that runs or writes a command, and the only `ssh` is the
    array cleanup fed from the tool's removal file."""
    text = RUNNER.read_text(encoding="ascii")
    lines = text.splitlines()
    ssh_lines = [line for line in lines if "cmd /c" in line and "ssh " in line]
    assert len(ssh_lines) == 1 and "$ArrayUser@$ArrayHost" in ssh_lines[0] and "$cmdFile" in ssh_lines[0]
    for forbidden in ("zonecreate", "alicreate", "cfgsave", "cfgenable", "createvv", "createvlun", "createhost"):
        for line in lines:
            if forbidden in line:
                assert "ssh " not in line and "WriteAllText" not in line and "cmdFile" not in line, line
    # the runner never calls a switch host: the only hosts it opens a connection to are the app and the array
    assert "switch_f1" not in text and "prov_sw1_host" not in text


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


def test_runner_compiles_its_tls_callback_the_way_5_1_accepts():
    """Probe on the jump box, 2026-09-15: `#pragma warning disable SYSLIB0014` makes 5.1's compiler fail
    ("Warning as Error: Invalid number") and the runner silently fell back to the script-block callback
    (rc.17, rc.18). `-IgnoreWarnings` without the pragma compiled. Pin the working form."""
    text = RUNNER.read_text(encoding="ascii")
    assert "#pragma" not in text
    assert "Add-Type -IgnoreWarnings -TypeDefinition" in text
    assert "TLS callback: $($script:TlsCallback)" in text  # the fallback is visible in the report, not only on the console


def test_runner_asserts_the_rc19_to_rc23_changes_the_api_exposes():
    """rc.24: the register's closed rows became assertions where the scenarios already produce the evidence."""
    text = RUNNER.read_text(encoding="ascii")
    for needle in (
        "array_credential",                      # SPEC-008 R1-R3
        "1 volume is not presented by this plan", # SPEC-008 R5 (P-19)
        "identified", "in_run", "/storage/preflight", "object name\\(s\\) free",  # SPEC-009
        "/zoning/plan", "/zoning/render", "cfgtransshow", "try 'bad_name_1'",      # SPEC-010
        "'exact', 'contains', 'includes'", "details",                              # SPEC-011
        "\\u00b7 persona", "pageBreakBefore",                                      # SPEC-012 R1, R3
        "Still needs eyes",                                                        # the screenshot list
    ):
        assert needle in text, needle
