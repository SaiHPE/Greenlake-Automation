---
applyTo: "Provisioning_Automation/alletra_onboard/tests/**"
---
# Tests

- No live calls: GreenLake, arrays, vCenter and switches are faked or replayed from
  `tests/fixtures/` captures. A test that needs the network is a lab script, not a test.
- Fixtures are real captured output, scrubbed before commit: no passwords, tokens, customer names
  or customer addresses. Lab addresses are fine. Say in the fixture folder's README where and when
  it was captured.
- `.gitignore` hides `*.json`, `*.txt` and similar everywhere except `tests/fixtures/`; if a new
  fixture type is ignored, add an exception for `tests/fixtures/` only.
- Never loosen an assertion to make a test pass. If behaviour changed on purpose, say so in the
  test and the pull request.
- Run the suite with `scripts/check.py` (or `python -m pytest -q`) from the app folder.
