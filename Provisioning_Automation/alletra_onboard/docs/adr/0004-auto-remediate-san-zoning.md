# The tool verifies SAN zoning and produces a read-only zoning PLAN — it never writes to the switch

> **DECISION REVISED (2026-07-03): NO SWITCH WRITES — verify + read-only zoning PLAN.** This ADR
> originally had the tool CREATE the missing zones on operator confirmation
> (`alicreate → zonecreate → cfgadd → cfgenable`). That is **superseded**: the tool now **verifies**
> zoning and **produces the exact zoning as a read-only plan** — the host-WWPN ↔ array-port-WWPN pairs
> per fabric, the correct aliases, and the copy-paste command sequence (with the *resolved* active cfg
> name) — for the **SAN team to apply by hand**. It **never writes to the switch**. Why the flip:
> - The active config is **shared production**, verified live on the customer fabric (FOS v9.0.1e1):
>   `F1_CFG` / `F2_CFG` carry **hundreds** of other teams' zones (3PAR / Primera / Alletra / Nimble /
>   Synergy / StoreOnce / dozens of hosts), and `cfgenable` re-activates the *whole* config. The SAN
>   team owns this fabric; the customer's standing rule is that the tool makes **no switch writes**.
> - The write path can't be safely tested in the lab; a correct **preview** can — and it *is* one of
>   this ADR's own "considered options" ("generate a script for the SAN team"), now chosen rather than
>   folded into auto-execute.
> - **The plan needs a read-only switch read, structurally** (not for writing): a host that isn't zoned
>   yet is **invisible to the array** — FC name-server *queries* are zone-filtered (soft zoning, FC-GS),
>   which is the very basis of the array-side verify below. But a cabled, powered host **FLOGIs and
>   registers in the fabric name server regardless of zoning**, so the switch admin name server
>   (`nsshow` = local, `nscamshow` = fabric-wide) shows it *and* its fabric. So the zoning step reads
>   the switch **read-only** (`nsshow`/`nscamshow` → the host-WWPN→fabric map; `alishow` → the array
>   ports' existing aliases) and writes nothing. [Broadcom FOS Command Ref `nsShow`/`nsCamShow`; FCIA
>   *Zoning Fundamentals*; Cisco *Managing FLOGI, Name Server, FDMI, RSCN* — soft zoning filters NS
>   discovery, it does not block FLOGI/registration. Verified live: the switch NS lists 408 online
>   initiators incl. real Emulex/QLogic host HBAs; the array's `showportdev ns` shows only zoned ones.]
> - **Per-WWPN data sources:** **vCenter** = the host's *complete* HBA WWPN set (authoritative — the
>   array only knows *already-zoned* WWPNs); **array** (`showhost`) = what's already zoned (logged in);
>   **switch NS** = the fabric of an unzoned-but-**online** WWPN. The delta = the plan. An **offline**
>   host WWPN is in none of them → the tool says *"cable + power the host, then re-run"*, never guesses.
>
> The `BrocadeClient` write path (`ALLOWED_WRITE`, `apply()`) and the "Apply remediation to switches"
> button are **removed** — only the read allowlist remains. Everything below is retained as the
> historical rationale for the additive `cfgadd → cfgenable` sequence, which now appears only as the
> **preview text** the SAN team runs.

> **Revision (2026-07-03): verification reads `showhost -d`, not `showportdev ns`.** The raw fabric
> name server (`showportdev ns`) also lists the array's own peer ports and *other* storage arrays, so
> inferring "hosts" from it can mistake a storage port for an ESXi host (and it line-wraps). The array's
> curated host view — **`showhost -d`** (Id · Name · Persona · WWN · Port · IP) — lists only real hosts
> and the array ports each WWPN is logged into, so it can't confuse storage for a host. Discovery now
> reads `showport` + `showport -iscsi` (all FC + iSCSI ports, any state) + `showhost -d`; zoning verify
> computes over that. Calibrated against a live Primera A630 (OS 4.5.24). Everything below stands.

> **Revision (2026-06-30, validated against the live LZ array): VERIFICATION IS ARRAY-SIDE — no
> switch login.** The fabric name server is zoning-filtered, so each array FC target port's
> `showportdev ns` *is* its effective zoning, and the array names each host. So the tool verifies
> zoning **read-only from the array** (`showport` + `showportdev ns`), cross-references the **expected
> hosts** (from vCenter discovery), and flags any expected host seen on neither fabric as
> **unverified** ("not zoned OR offline" — the array can't distinguish the two). The Brocade switch
> is **not** a prerequisite for verification; its IPs/creds are needed **only** to *create* missing
> zones (remediation), which is gated behind preview + explicit operator confirmation (the global
> write-freeze was removed once verification was validated against live hardware — preview+confirm is
> the gate). The switch-side `cfgshow` parser is retained for an optional config-hygiene audit. The
> rest of this ADR (the odd/even rule, additive-only, `cfgenable`-not-`cfgsave`, preview+confirm)
> stands unchanged for the remediation path.

For FC provisioning, SAN zoning is the prerequisite that lets a host actually *see* a LUN. The tool
**verifies** the current zoning (array-side, read-only — see the revision above), **reports** the
status and the remediations needed by the cabling best practice, and — on **explicit operator
confirmation** — **creates the missing zones itself**
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

## The zoning plan — method (the SAN team's house standard, 2026-07-03)

The read-only plan follows the SAN team's own method (field transcript + zoning worksheet from
Panduranga). The tool is an **assisted command builder**, not an auto-generator: it discovers
everything it can *know*, and the operator types the alias *names* (which encode physical facts the
tool can't discover — site, rack, U-location).

**What the tool knows (pre-filled in the interface):**
- each host's HBA WWPNs (vCenter) + **which fabric each is on** (switch name server, `nsshow` local +
  `nscamshow` fabric-wide — the array can't tell us, because its NS queries are zone-filtered);
- the array's **target ports online per fabric** (Panduranga's *"how many storage ports"* = every array
  target port online on that host's fabric);
- the **existing alias(es)** for any WWPN (`alishow`) — a WWPN can have *many* on this shared fabric, so
  the tool keeps the whole list and prefers the convention-matching one;
- the **active cfg** per fabric (`cfgshow` **Effective** block → `F1_CFG` / `F2_CFG`);
- the **SIST pairing** by the odd/even rule.

**What the operator types (the interface's editable cells):** the alias NAME for any WWPN that doesn't
already have one:
- host HBA port → `<Site>_<Device>_<Rack>_<ULoc>_HBA_<n>_Port_<n>` (e.g. `EPC1-ESX-01_R109U17_HBA_1_Port_2`)
- array port    → `<Site>_<STGDevice>_<Rack><ULoc>_N<node>S<slot>P<port>` (e.g. `EPC2-STG-01_R619U14_N0S3P1`)

An existing alias is shown and **reused**, never re-created.

**Zoning is single-initiator-single-target** — one host HBA port ↔ one array port per zone. Each host
HBA port on fabric F is zoned to every array target port online on F (odd HBA → F1 / odd array ports;
even HBA → F2 / even array ports; across both nodes for redundancy).

**Generated command sequence (read-only preview, per fabric), assembled from the operator-edited
aliases + the discovered pairing:**
```
alicreate "<host_alias>","<host_wwpn>"       # only for aliases that do not already exist
alicreate "<array_alias>","<array_wwpn>"
zonecreate "<host_alias>_<array_alias>","<host_alias>;<array_alias>"   # one per SIST pair
cfgadd "F1_CFG","<zone1>;<zone2>;…"
cfgenable F1_CFG
```
The tool **never runs these** — it produces the script for the SAN team. An **offline** host WWPN (not
in either fabric NS) can't be placed → the plan says *"cable + power the host, then re-run"*, never
guesses. Built by `application/storage/zoning_plan.py`.
