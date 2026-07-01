# The tool auto-remediates SAN zoning: discover → report → confirm → create (additive-only)

> **Revision (2026-06-30, validated against the live LZ array): VERIFICATION IS ARRAY-SIDE — no
> switch login.** The fabric name server is zoning-filtered, so each array FC target port's
> `showportdev ns` *is* its effective zoning, and the array names each host. So the tool verifies
> zoning **read-only from the array** (`showport` + `showportdev ns`), cross-references the **expected
> hosts** (from vCenter discovery), and flags any expected host seen on neither fabric as
> **unverified** ("not zoned OR offline" — the array can't distinguish the two). The Brocade switch
> is **not** a prerequisite for verification; its IPs/creds are needed **only** to *create* missing
> zones (remediation). Remediation writes are additionally **frozen** behind
> `provisioning_writes_enabled` until validated against live hardware. The switch-side `cfgshow`
> parser is retained for an optional config-hygiene audit. The rest of this ADR (the odd/even rule,
> additive-only, `cfgenable`-not-`cfgsave`, preview+confirm) stands unchanged for the remediation path.

For FC provisioning, SAN zoning is the prerequisite that lets a host actually *see* a LUN. The tool
**verifies** the current zoning (array-side, read-only — see the revision above), **reports** the
status and the remediations needed by the cabling best practice, and — on **explicit operator
confirmation**, and only once writes are unfrozen — **creates the missing zones itself**
(`alicreate` → `zonecreate` → `cfgadd` → `cfgenable`) on the switch. It then re-verifies.

> **Activation discipline (verified by deep research, 2026-06-26).** The apply step is **`cfgenable`**,
> not `cfgsave`. `cfgenable` activates the change on the running fabric *and* persists it to nonvolatile
> memory on all switches. **`cfgsave` alone only commits the *Defined* config — it does NOT activate,
> and explicitly leaves the *Effective* and *Defined* configurations inconsistent**, which can produce
> divergent zoning on a zone merge or HA failover. So the tool must drive `cfgadd → cfgenable` and must
> never use `cfgsave`-alone as the "apply" step. [Broadcom FOS Administration Guide; FOS `cfgSave` cmd
> reference — 3-vote confirmed.]

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
  confirms; only then does it execute and `cfgenable` (the activation step — see the activation
  discipline note above). No silent writes — this is the highest-risk write in the tool.
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
