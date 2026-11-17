# Post-init verification reads the array's running config via SSH CLI

> **Amended by [ADR 0013](0013-one-array-credential-per-run.md) (2026-09-15):** the credential rule below
> ("supplied per-run and never stored") is superseded. The run holds one array credential from the
> sheet and every step uses it; the prompt remains only for runs whose sheet supplied none.
>
> **Amended by [ADR 0015](0015-tool-configures-remote-copy-write-scoped-ssh.md) (2026-10-07, effective
> from the release that ships Remote Copy links and targets, v0.19):** the client described here stays
> read-only and stays the default. A second, write-scoped SSH client will exist for Remote Copy links
> and targets only (its own allowlist), reachable only through an operator-approved replication plan.
> Remote Copy groups and DR actions go over WSAPI, not SSH.

After the operator confirms the array is initialized, the tool verifies the **on-array config**
against the Initialisation-sheet values by logging into the array directly over **SSH** (port 22,
the array admin account) and parsing the read-only `show*` commands. It never writes — it's a
confidence check, not a gate, and a config mismatch never fails the onboarding.

Calibrated against a live B10000 (OS 10.5.51), the verified config comes from three commands:
`showsys -d` (name / serial / product number / contact), `shownet` (mgmt IP + netmask, gateway as
`Default IPv4 route`, plus the `NTP server` and `DNS server` lines), and `showdate` (timezone).
Two calibration findings: `showdns` / `showntp` do not exist on this platform (DNS/NTP are read from
`shownet`), and the DSCC "System country" is **not** stored on the array (`Location` is empty) — it's
a cloud-side attribute, so it isn't verified here.

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

## Addendum 2026-10-12 (SPEC-020)

One command that is not a `show` runs over this client: `checkrclink`, HPE's link test between two
Remote Copy ports (a test server on one array, a test client on the other). It changes no
configuration, but it starts and stops a process on the array, so it does not join the read allowlist.
It has an allowlist of its own (`run_diagnostic`: exactly `startserver`, `stopserver`, `startclient`,
`stopclient`, with the port, address and test length validated), is called only by the replication
link check, and is never reachable from the Console prompt (SPEC-019), which keeps the read allowlist.

## Addendum 2026-11-16 (BL-46)

The read allowlist checked only the command name, so an allowed command with an option that acts got
through: `showtarget -rescan` makes the peer ports rescan for targets (HPE CLI reference, showtarget).
It changes no configuration, but it is not a read, and the Console prompt could send it. The client now
also refuses known acting options per command (`_ACTION_OPTIONS` in `cli_client.py`, case-insensitive),
each with a test. Only `showtarget -rescan` is known today; another joins the list when a captured
`help` shows it.
**Live 2026-11-16** on rack13-ARCUS (OS 10.6.0, run `aa3d93c5`, `lab/failed_apply_lab.py`): typed in the
Console, `showtarget -rescan` was refused on screen and over the API, the refusal was in the command log
and nothing reached the array; `showtarget` still ran. Record: `docs/validation/2026-11-16-failed-apply-rack13.md`
(BL-45's pull request).

Tcl's quoting and substitution characters are refused too: `"` `'` `{` `}` `[` `]` `\` joined the shell
metacharacters in `_FORBIDDEN_CHARS`, with a test for each. The array CLI is built on Tcl. If it parses
an SSH exec line that way, `showvv [removevv -f zz]` runs `removevv` inside an allowed read, and
`showtarget "-rescan"`, `showtarget {-rescan}` or `showtarget \-rescan` reach the array as `-rescan`
while the option check sees a different word. No read the tool makes uses these characters, so refusing
them costs nothing. The link check and the Remote Copy write client share the same set and refuse them
as well. Whether the CLI really applies Tcl parsing to an SSH exec is not confirmed: a harmless lab
check such as `showsys [showdate]` would settle it. It has not been run.

## Addendum 2026-11-17 (SPEC-026, ADR 0019)

The read allowlist gains four commands by exact base name: `showalert` (the array's alerts) and the
System Reporter reports `srstatcpu`, `srstatport` and `srstatvv`. The as-built reads them for its
*Array status and performance at handover* section. Each only reads: `showalert` lists alerts, and an
`srstat*` report queries the System Reporter database. Every option their captured `help` offers on
OS 10.5.0, 10.5.51, 10.5.60 and 10.6.0 filters, windows, sorts or formats, and AUTHORITY is "Any role
in the system"; `tests/unit/test_cli_allowlist.py` reads those help pages and fails on an option
nobody has reviewed (LESSONS 46). The same file pins what stays off: `srstatrcvv` (until a started
Remote Copy group is captured), the live samplers `statcpu`, `statport` and `statvv` (without `-iter`
they never end), System Reporter's writes (`setsr`, `startsr`, `stopsr`, `*sralertcrit`) and the
alert writes `setalert` and `removealert`. The Console prompt uses this allowlist, so it can run the
four commands too.
