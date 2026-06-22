# Post-init verification reads the array's running config via SSH CLI

After the operator confirms the array is initialized, the tool verifies the **on-array config**
against the Initialisation-sheet values by logging into the array directly over **SSH** (port 22,
the array admin account) and parsing the read-only `show*` commands (`showsys`, `shownet`,
`showdns`, `showntp`, `showdate`). It never writes — it's a confidence check, not a gate, and a
config mismatch never fails the onboarding.

## Considered options

- **DSCC / GreenLake cloud API** (reuses our token) — rejected: it verifies what the cloud
  *recorded as applied*, not the array's actual state, so it can't catch "DSCC says applied but
  the array didn't take it" — the exact failure this feature exists to catch.
- **WSAPI v3 (REST, 443)** — rejected as the primary interface: HPE's own SDK confirms WSAPI is a
  *storage-provisioning* API (volumes, hosts, capacity, system identity) with **no methods for
  network / DNS / NTP / timezone** — which is most of what we configured. It also isn't guaranteed
  enabled (`startwsapi`). It could verify identity (name/serial) only, so it wasn't worth a second
  protocol; SSH reads identity too.
- **Ansible** — rejected: its HPE storage modules wrap the same WSAPI (same blind spot), and using
  Ansible merely to run SSH commands is a heavy dependency for what paramiko does directly.

## Consequences

- Adds **paramiko** (+ cryptography) as a dependency, bundled into the .exe.
- Verification parses **CLI text output**, which is brittle to OS-version formatting changes — the
  parsers are calibrated against the first live array and isolated so a format tweak is a one-line fix.
- Requires **SSH (22) reachable** from the jump box to the array's mgmt IP, and the array admin
  credentials (the DSCC System Credential). The password is supplied per-run and never stored.
- Only an allowlist of `show*` commands is ever run — the path is structurally read-only.
