# The tool verifies SAN zoning and produces a read-only zoning PLAN — it never writes to the switch

> **DEFERRAL PREMISE MEASURED AND FOUND FALSE (2026-08-04). The decision is unchanged and
> reconfirmed; the reason for waiting is not.** Two findings from live probes of 4UW0004497
> (OS 10.5.60.36):
>
> - **The BGL lab IS a real dual fabric.** Diffing the switch membership of
>   `showportdev fcfabric 0:3:1` against `0:3:2`: **28 switches on F1, 26 on F2, ZERO in common**,
>   with the `_F1`/`_F2` suffix applied consistently across all ~54. Card-port parity AGREES with the
>   switch-derived fabric (`resolve_port_fabrics` emitted no override notes). The "one big meshed
>   fabric, both declared switches see everything, the split collapses" premise recorded below does
>   not hold here. Why it was reached earlier is unresolved — possibly two switches on the same
>   fabric, or a different array — but it must be re-measured before being relied on again.
> - **Read-only SWITCH access is a hard prerequisite for PLANNING, not just for creating.**
>   `showportdev ns <n:s:p>` is **zone-filtered**: 9 lines on `0:3:1`, 8 on `0:3:2` — the array's own
>   ports plus the single host each port is *already* zoned to. None of the three vCenter ESXi hosts'
>   six WWPNs appeared. **The array is structurally blind to exactly the hosts the operator wants to
>   zone**, so the builder's dropdowns cannot be populated from array-side reads. The sheet hint
>   claiming switch access was "only needed to CREATE zones" was wrong and is fixed (a1370d9).
>
> **Consequence for the deferral.** "Build this AFTER the clean lab lands" existed because an
> *isolated* 2-switch bed was needed to make *writing* zones safe to test. With plan-only reconfirmed
> (2026-08-04 — the operator copies the commands into his own switch session; the tool never holds
> switch write credentials), that need evaporates: **reading a shared production fabric is harmless,
> and is a strictly better test** — real aliases, hundreds of existing zones, real cabling. The
> blocker is no longer a test bed but **read-only credentials for `SW6600_F23U40_F1` and
> `SW6600_F23U39_F2`**.

> **DESIGN REFINED (2026-07-04, from the SAN-team call with Panduranga). BUILD DEFERRED until a clean
> test fabric exists.** The v0.10.x plan *auto-paired* each host WWPN with every same-fabric array
> target port. That doesn't survive the field — fabric assignment must be **switch-based and
> operator-selected**, not auto. The model:
>
> - **Fabric = which switch a port is cabled to.** The operator DECLARES the two fabrics in the sheet:
>   `switch_f1` = the **odd / F1** switch, `switch_f2` = the **even / F2** switch. The tool reads each
>   switch's name server and assigns every port (host + storage) to the fabric of whichever declared
>   switch sees it. **Port-number parity** (odd `P` = 1/3 → odd, even `P` = 2/4 → even) is a
>   **cross-check**, not the source of truth; if the switch a port sits on disagrees with its parity
>   (miscabling), the tool **flags it** — it never silently guesses.
> - **Requires a REAL dual fabric.** This works only when `switch_f1` / `switch_f2` are **separate
>   fabrics**. In the lab they are one big **meshed** fabric (many switches E-port-linked, "no odd/even
>   policy"), so both declared switches see *everything* (fabric-wide `nscamshow`) and the split
>   collapses — exactly the "resolved to 5 switches, could not map to two fabrics" the tool reported.
>   In that case the tool must **say so**, not emit garbage. A customer site — and Panduranga's incoming
>   **isolated 2-switch + 1-array + 1-host** test bed — has a clean dual fabric where the split is
>   unambiguous.
> - **Two-part UI.** (1) A read-only **current-connection map** — per host WWPN, the storage port
>   WWPN(s) + `n:s:p` it is actually logged into (from `showhost` + `showport`): host WWPN ↔ storage
>   WWPN, *both sides*, "exactly what is connected to what"; an already-zoned host shows fully wired.
>   (2) An **operator-selected zoning builder** — per host WWPN a **dropdown of storage ports filtered
>   to the same fabric/parity** (a host HBA on the odd switch ⇒ only odd storage ports offered), each
>   option showing `n:s:p`, WWPN, and **label / existing use**; the operator **selects** the targets and
>   the tool emits the `alicreate / zonecreate / cfgadd / cfgenable` preview. NOT auto-all-ports. Ports
>   already zoned are pre-selected / greyed (show the delta).
> - **The RCFC hard-exclusion (v0.10.1) is DROPPED.** Keying on the `showport` Label "RCFC" wrongly
>   removed *host-serving* ports — the array's `showhost` showed hosts logged in on `0:3:4` / `1:3:4`;
>   those are **Target-mode host ports**, not the **Initiator-mode** RCFC ports the HPE guidance means.
>   With operator selection the human just doesn't pick replication ports, so the tool **shows** each
>   port's label/use and lets the operator decide instead of guessing.
> - Still **no switch writes** (read-only preview only). **Build this AFTER the clean lab lands.**

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

> Superseded in part by the **2026-07-04 refinement** at the top: fabric is **switch-declared** (not
> parity-derived), storage ports are **operator-selected** from a parity-filtered dropdown (not
> auto-all), and RCFC is **not** hard-excluded. The command format, aliases, and SIST rule below still hold.

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
even HBA → F2 / even array ports; across both nodes for redundancy). **Remote-Copy-FC and Peer ports
are excluded** — identified by the `showport` **Label** (`RCFC` / `Peer`), *not* the alias name (which
is inconsistently applied on a shared fabric). RCFC ports are Initiator-mode array↔array replication
ports, not host targets, and HPE/3PAR guidance excludes them from host zoning (they get their own
RCFC↔RCFC zones). [3parug: "Correct practice for zoning Host ports and RCFC ports"; RCFC requirements.]

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
