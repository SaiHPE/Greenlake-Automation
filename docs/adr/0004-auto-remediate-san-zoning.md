# The tool auto-remediates SAN zoning: discover → report → confirm → create (additive-only)

For FC provisioning, SAN zoning is the prerequisite that lets a host actually *see* a LUN. Rather than
only verifying it, the tool takes it end-to-end: it **discovers** the current zoning across **both
Brocade fabrics** (odd / F1 and even / F2), **reports** the current status and the remediations needed
by the cabling best practice, and — on **explicit operator confirmation** — **creates the missing
zones itself** (`alicreate` → `zonecreate` → `cfgadd` → `cfgenable` → `cfgsave`). It then re-verifies.

**Best-practice rule (fixed, not customer-specified):** *odd port → odd switch, even port → even
switch.* Array ports with `P` (the port in `N:S:P`) = 1,3 belong on Switch 1 / F1; `P` = 2,4 on
Switch 2 / F2. Host HBA port 1 → odd fabric, HBA port 2 → even fabric. The tool computes this expected
set from the discovered array ports + host WWPNs.

**Inputs:** the customer provides — in the Initialisation sheet — all IPs/creds (array, vCenter, **both
switches**) and the **HBA**, *not* the individual ports. The tool discovers the ports/WWPNs (array via
`showport`/`showinventory`, host via vCenter).

## Non-negotiable safety constraints

The fabric is **shared production** — the live `cfgshow` showed *hundreds* of unrelated zones (XP,
3PAR, Primera, other customers' hosts) in the **same active config**, and `cfgenable` re-activates that
*whole* config. Therefore:

- **Additive-only.** The tool reads the active config first, computes **only the delta** for the target
  hosts, and `cfgadd`s its zones. It **never** creates/replaces a config or removes an existing zone.
- **Preview + confirm, always.** It shows the exact per-switch commands it will run; the operator
  confirms; only then does it execute and `cfgsave`. No silent writes — this is the highest-risk write
  in the tool.
- **Re-verify after.** Confirm via `cfgshow` (the zone is in the active config) **and** the array's
  `showportdev ns` (the host's WWPNs now log in on the target ports).

## Considered options

- **Verify-only** (the earlier decision) — rejected: the engagement wants the tool to *fix* zoning so
  provisioning is end-to-end, not hand it back to the SAN team.
- **Fully automatic, no confirm** — rejected: a silent or wrong `cfgenable` on a shared fabric can take
  down unrelated production hosts.
- **Generate a script for the SAN team to run** — folded in: the *preview* is exactly that script, but
  shown and then executed on confirm, so it's one transparent flow rather than a hand-off.

## Consequences

- Both switch SSH IPs + credentials become required sheet inputs; **Brocade FOS for v1** (Cisco's
  `device-alias` / `zoneset` model is a later, separate adapter).
- *Physical* cabling (HBA → switch, array port → switch) remains a customer prerequisite — the tool
  can't cable; it only configures zones for ports that are physically cabled and logged into the fabric.
- The tool must parse `cfgshow` / `alishow` / `nsshow`, and own a careful additive `cfgadd`/`cfgenable`
  path with strong guardrails. This is the riskiest module — it warrants the most testing.
