# Provisioning is driven by discovery, not a fully-specified sheet

The storage-provisioning automation (host / volume / LUN / snapshot / replication / DR) must work on
**any** customer environment, not just the calibration lab. To guarantee that, the **Initialisation
sheet carries only the customer's intent + reach** — IPs, credentials, and what to create (volume
names/sizes, target hosts/cluster, replication target, protocol). **Every environment fact is
discovered at run time**: array target-port WWPNs, the CPG list, existing hosts/volumes/VLUNs, host
HBA WWPNs, available personas, the `naa`↔VV mapping, multipath state. Nothing environment-specific is
hardcoded, and the operator is never asked to type a fact the tool can read.

## Considered options

- **Sheet specifies everything** (WWPNs, CPG, target ports, LUN IDs) — rejected: it overfits to one
  environment, is wrong on every other one, and makes the customer hand-type facts they'll mistype.
  This is exactly the "overfit to the calibration lab" failure we must avoid.
- **Discover everything; sheet = intent + reach** — chosen. The live lab proved every fact is
  readable (`show*` + esxcli, and the array's fabric nameserver even exposes host HBAs/OS).
- **Hybrid (discover, but allow pinning)** — adopted only as an *override*: the operator may pin a
  choice (e.g. force a specific CPG) when discovery is ambiguous, but the default is discovery.

## Consequences

- **Discovery is a hard dependency**: the tool needs read access (SSH and/or WSAPI) to the array and
  hosts before it can provision; a preflight gathers facts first.
- **The tool makes choices** the operator must be able to **review and override** (e.g. auto-picking
  a CPG, or auto LUN IDs) — so a dry-run/preview that shows the discovered facts + the planned
  actions is required before any write.
- **Parsers must stay tolerant and be calibrated per OS version** (CLI text varies); the lab is a
  calibration reference, not a template. WSAPI's structured JSON is preferred where it covers the
  operation (see ADR 0003, transport).
- **Idempotency is required**: discovery will routinely find objects already present (the lab is
  fully provisioned), so create operations must treat `EXISTENT_*` as a warning, not a failure.
- The sheet grows by a small **"Provisioning intent"** section only — not a dump of every field.
