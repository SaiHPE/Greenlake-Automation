# The tool never writes to a SAN switch — it emits the command set and a consultant applies it

**Status:** accepted, 2026-09-02. Reaffirms [ADR 0004](0004-auto-remediate-san-zoning.md); removes
the write path that shipped against it in v0.14.0 and v0.15.0.

> **REVISED the same day: the gate moved from the RUN to the EXPORT.** As first written this ADR
> said provisioning "unlocks per host on verified zoning", implemented as a refusal of the whole
> apply until at least one host verified. Looking up the iSCSI case showed that is the wrong
> operation to gate.
>
> HPE's documented order is **register first**. `createhost -persona 15 "Hera" -iscsi
> "iqn.1991-05.com.microsoft:hera.lionetti.lab"` takes an IQN the array has never seen, and the VME
> guidance is explicit that *"if the host has never established an iSCSI session, the IQN may not
> appear automatically"* and should be registered beforehand. The earlier deep research had already
> found that host creation is not gated on zoning by the API either, so our gate was refusing a
> legitimate order of operations on **both** transports. It only became obvious via iSCSI.
>
> So hosts, host sets, volumes and VV sets are always created. Only the **export** waits, on whether
> the array can reach the target: logged in on both fabrics for FC, an active session for iSCSI once
> that transport is built. Creating a host object for a server that is not cabled yet is harmless and
> reversible; an export to a host that cannot reach the array is the thing that reports "created" and
> is silently dead, which is the property the gate existed to protect.
>
> A **host-set** export needs only ONE reachable member. Exporting to the set is HPE's practice for a
> cluster and the remaining members pick the LUN up as they come online. It is held back only when no
> member can reach the array. Sources: the ESXi Implementation Guide (which also states that
> exporting one VLUN over both iSCSI and FC is unsupported) and the HPE VME iSCSI guidance.

**Decision.** The application has no ability to write to a fibre-channel switch. `BrocadeClient`
keeps `ALLOWED_READ` and nothing else. The zoning step's deliverable is the **command set**: the
exact, correctly-ordered `alicreate` / `zonecreate` / `cfgadd` / `cfgenable` text for the operator's
fabric, which a consultant reviews and applies by hand. Provisioning unlocks **per host** on
verified zoning, not on a global flag.

## Why this ADR exists

ADR 0004 decided the tool never writes to the switch. `CONTEXT.md` says the same thing in the
glossary entry for **Zoning plan**. Neither was ever amended.

A write path shipped anyway. It was built on a verbal mandate recorded on 2026-08-15 in a docstring
(`zoning_stage.py:2`, "2026-08-15 write-path mandate") and in the assistant's memory, and nowhere
else. `ALLOWED_WRITE` returned to `brocade_client.py:47`, ADR 0004 line 98 still asserting it had
been removed. `POST /runs/{id}/zoning/stage` was added with no feature flag.

On 2026-08-31 the operator drove that path against a live production fabric
(`10.132.30.112`, cfg `jul2prabhu`, 13 effective zones) and it created a zone and two aliases and
ran `cfgsave`. On 2026-09-02, reviewing that same session, **the operator stated the tool had not
written anything — that he had copy-pasted the commands himself.** He had not; his SSH transcript
contains only `cfgshow`, `cfgtransshow` and `alishow`. The zone was there because the application
put it there.

That is the finding this ADR records. The operator's belief matched every document in the
repository. Only the code disagreed, and the code is what ran.

## Decision drivers

**Multi-vendor risk is the operator's stated reason and it is the strongest one.** Only Brocade FOS
has ever been tested. Cisco MDS uses different objects and different syntax (`device-alias`,
`zone name`, `zoneset activate`). Shipping a write adapter per vendor means owning a
destructive-capable, under-tested code path for every fabric family a customer might have. Emitting
text does not remove the vendor problem — the tool still has to print the right dialect — but it
changes the blast radius from *a wrong command executes on a production fabric* to *a wrong command
is read by a consultant before it executes*.

**The `cfgsave`-alone contradiction disappears.** ADR 0004 lines 130-136, three-vote confirmed
against the Broadcom FOS Administration Guide, forbid `cfgsave`-alone as an apply step because it
leaves the Defined and Effective configurations inconsistent, which can diverge on a zone merge or
HA failover. `zoning_stage.py:118` did exactly that, deliberately, as the price of never activating,
and mitigated it with an "Activation pending" banner. Removing the write path removes the need for
that trade entirely: the consultant runs `cfgadd` and `cfgenable` together in a maintenance window,
which is what the guidance actually wants, and the fabric never sits divergent.

**Staging was a weak gate and the live run proved it.** `ZONING_OK = ("verified-proper", "staged")`
let a staged-but-unactivated zone unlock provisioning. On 2026-08-31 host `10.132.30.86` was staged,
the gate opened, and path verification then reported `no_path` for it — correctly, because staging
into a defined configuration is not activation and that host still had no route to the array. The
gate said proceed for a host that could not see the storage.

## Consequences

**Removed.** `BrocadeClient.write`, `cfgsave_defined`, `cfgtransabort`, `ALLOWED_WRITE`; the
`zoning_stage` module; `POST /runs/{id}/zoning/stage`; the Stage button and its result panel; the
`ZoningStageResult` / `FabricStageResult` models and the `zoning.staged` event.

**The command set becomes the product, not a warm-up.** It must be copyable in one action, ordered
so a consultant can paste it straight through, and it must visually separate `cfgenable` from the
additive commands. The 2026-08-31 UI rendered `cfgenable jul2prabhu` in the same monospace block,
weight and colour as the four commands that executed, which invites pasting the activation line
along with the rest.

**The gate becomes per host.** Provisioning proceeds for hosts verified zoned on both fabrics and
excludes the others with a named reason each. A partially-racked cluster is the normal case: on
2026-08-31, `.136` was properly zoned and provisionable while `.47` and `.86` were not, and a global
gate would have blocked the whole run. This also scopes the path-verification target set to the
hosts actually in the provisioning intent, which fixes a separate defect where hosts in no export
row were reported as "exported-but-no-path".

**We lose a proven capability.** The write path worked, additively, on a shared production fabric,
with a transaction guard that refused to stack on another admin's open transaction and a read-back
verification. That is real engineering being deleted. It is deleted because the risk is owned by the
customer's SAN team, not by this tool, and because no document in this repository ever authorised it.

**Cleanup owed from the live test.** `zz_test_h86_zz_test_a0303` and aliases `zz_test_h86` /
`zz_test_a0303` remain in the defined configuration of `jul2prabhu` on `10.132.30.112`. Removal is
manual: `cfgremove` → `zonedelete` → `alidelete` ×2 → `cfgsave`. The disclosure to the SAN team must
say the tool created them, not that an engineer pasted them.

## Considered and rejected

**Keep the code behind a default-off flag.** Preserves the capability for a customer who asks for
it. Rejected: an ungated flag is precisely how this shipped in the first place, and a flag that
exists will eventually be set by someone who has not read this ADR.

**Fix the UI so Stage is unmistakable.** Treats the 2026-08-31 run as a success and keeps the
capability. Rejected on the multi-vendor argument above, and because it leaves the tool holding
destructive access it has no documented authority to hold.
