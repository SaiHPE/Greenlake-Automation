---
applyTo: "Provisioning_Automation/alletra_onboard/src/alletra_onboard/adapters/**"
---
# Adapters (arrays, switches, vCenter, hosts, GreenLake, browser)

- An adapter talks to one outside system and nothing else; the domain never imports it.
- Array SSH commands must be in `ALLOWED_COMMANDS` (`adapters/array/cli_client.py`); switch commands
  in the Brocade client's allowlist. Adding one needs a unit test and a sentence in the pull request.
  Writes go through WSAPI after the operator approves a plan, or the Remote Copy write client
  (ADR 0015). Never a switch write (ADR 0012).
- Every command sent to a device is recorded with `command_log.record(...)`, with the client's
  secrets passed in so they are redacted.
- Parse real output: capture it read-only on the lab, scrub it (no passwords, no customer data),
  save it under `tests/fixtures/`, and pin the parser to it with a test before relying on it.
- GreenLake payload helpers import `GreenLakeHttpClient` under `TYPE_CHECKING` only, so contract
  tests run without `httpx`.
- Browser selectors live in `adapters/browser/locators.py`: role, label or visible text, never CSS.
