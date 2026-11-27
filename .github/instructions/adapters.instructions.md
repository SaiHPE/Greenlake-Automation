---
applyTo: "Provisioning_Automation/alletra_onboard/src/alletra_onboard/adapters/**"
---
# Adapters (arrays, switches, vCenter, hosts, GreenLake, browser)

- An adapter talks to one outside system and nothing else; the domain never imports it.
- Array SSH commands must be in `ALLOWED_COMMANDS` (`adapters/array/cli_client.py`); switch commands
  in the Brocade client's allowlist. Adding one needs a unit test and a sentence in the pull request.
  Writes go through WSAPI after the operator approves a plan. Every SSH write follows ADR 0025 (exact
  forms, approved apply only, the plan's objects only, undo first, read-back after, no prompts). Today
  there are two SSH write clients: ADR 0015's `ArrayRcCliClient` (`RC_WRITE_FORMS` in
  `adapters/array/rc_cli_client.py`) and ADR 0016's `ArraySnapCliClient` (`SNAP_WRITE_FORMS` in
  `adapters/array/snap_cli_client.py`: one `createsched -f` form, the command inside its quotes checked
  as a form of its own). A new form needs a test pinned to the array's own help or a live answer, and a
  new kind of write needs its own ADR. Brocade switch reads stay strictly read-only in
  `adapters/fabric/brocade_client.py`; opt-in Brocade FOS zoning apply uses the separate
  `BrocadeZoneWriter` (`adapters/fabric/brocade_writer.py`, ADR 0033) under ADR 0025.
- Every command sent to a device is recorded with `command_log.record(...)`, with the client's
  secrets passed in so they are redacted.
- Parse real output: capture it read-only on the lab, scrub it (no passwords, no customer data),
  save it under `tests/fixtures/`, and pin the parser to it with a test before relying on it.
- GreenLake payload helpers import `GreenLakeHttpClient` under `TYPE_CHECKING` only, so contract
  tests run without `httpx`.
- Browser selectors live in `adapters/browser/locators.py`: role, label or visible text, never CSS.
