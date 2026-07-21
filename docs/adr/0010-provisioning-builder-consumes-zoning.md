# Provisioning is an interactive builder over discovered objects; it consumes zoning, it does not create it

Storage provisioning turns a customer's intent (hosts, volumes, exports) into array-side objects on the
Alletra MP B10000 and confirms the result. This ADR fixes the **scope and shape** of that flow now that
the SAN-zoning automation is **deferred** — the clean dual-fabric lab needed to build zone *creation*
safely is delayed, and the messy shared-fabric lab is what we have. It supersedes the implicit
"execute the Provisioning sheet top-to-bottom, auto-deciding everything" model in the first
`application/storage/storage_provision.py` cut.

**Decision:** provisioning does **two tiers** — **(1) array-side create** (host → host-set → volume →
VV-set → VLUN export, over WSAPI) and **(2) read-only path verification** (read `showvlun` / `showhost`
back and report, per host, which HBAs are logged in and on which fabric). It **consumes** existing
zoning (reads which host WWPN is logged into which array port); it **never creates** zones — that is a
separate, deferred (not abandoned) step. The relationship steps (set membership + presentation) are an
**operator-composed dropdown builder** over *discovered + to-be-created* objects, not an auto-executed
sheet. The ESXi-side finish (rescan → VMFS datastore, "tier 3") is **out of scope**.

## Why this ADR

Two different operations wear the word "zoning" and conflating them is what stalled the thinking:
*producing* zones (writing `zonecreate`/`cfgenable` to the switch — the risky part that needs the clean
lab) versus *consuming* zoning (reading which host WWPN is logged into which array port). Provisioning
only needs the second, and the array already exposes it read-only: `showhost -d` gives the curated
host→WWPN→port map, where an empty port list means "configured but not logged in (not zoned / offline)"
([domain/storage.py](../../src/alletra_onboard/domain/storage.py) `ArrayHost`). So provisioning is
**unblocked by the deferral** — the array-side create and the read-back verify are independent of
whether *we* can safely write zones. Only the true data path (host actually sees the LUN) needs zoning,
and that zoning is supplied by the SAN team / the existing fabric, not by this tool.

The first `storage_provision.py` cut also hardcoded choices the field needs to make: it built hosts from
*all* vCenter WWPNs blindly, dumped every host into one host-set, created N identical volumes, and always
exported each volume to `set:<hostset>` at an auto LUN. Panduranga's direction is the opposite —
**flexible, dropdown-driven, use the discovered connections** — so the shape has to change.

## Design

1. **Host WWPNs are discovered, not typed.** vCenter enumerates each ESXi host's FC HBA WWPNs + OS
   (`adapters/vcenter/vcenter_client.py`); persona is derived from the OS (VMware 11 / WindowsServer 15 /
   Generic-ALUA 2). The array side is OS-agnostic, so scoping discovery to ESXi+vCenter *now* does not
   bake ESXi into tiers 1–2; other host OSes are a later discovery source.
2. **Tier 2 = read-only path verification.** After apply, read `showvlun` + `showhost` and report per host
   "2/2 HBAs logged in — LUN live on both fabrics" or "0 paths — host off or not zoned (created; activates
   once zoned)". It **reports, never gates**: `createVLUN` succeeds regardless of login state and the
   export activates when paths appear, so a zero-path host must not fail the run. A non-blocking pre-apply
   heads-up warns before exporting to a zero-path host. "0 paths" is deliberately ambiguous (off vs
   unzoned) because the array cannot distinguish the two.
3. **Create is plural / heterogeneous.** A run creates a *list* of volumes each with its own
   name/size/type/CPG, and ≥1 host-set with *selected* members — not one `VolumeSpec` → N identical
   volumes and one all-hosts set. The Initialisation sheet is redesigned to match (it is not fixed).
4. **Relationships are an operator dropdown builder.** VV-set membership, host-set membership, and
   presentation (source `volume|vvset` × target `host|hostset` × LUN `auto|explicit`) are composed by the
   operator from dropdowns whose options are **existing array objects + the ones being created this run**.
   Selection is **manual** (no auto-ranking) — at the real scale (a cluster ≈ 7–8 picks) ranking is
   over-engineering; dropdown entries carry discovered status text so a half-zoned host isn't picked blind.
5. **Ideal subset from the messy lab.** We do not wait for clean hardware: discovery classifies every
   host by fabric + login state, and the operator selects the clean subset (on + zoned) to work with. That
   subset is the tier-2 green validation set now and the known-good seed for the zoning step later.

## Considered alternatives

- **Execute the sheet top-to-bottom, auto-deciding presentation** (the first cut) — rejected: the field
  needs vol/vvset × host/hostset flexibility with explicit LUNs, and hardcoding "each volume → host-set,
  auto LUN" can't express boot LUNs, single-host exports, or set-level presentation.
- **Create zones now so the data path works end-to-end in the lab** — rejected: writing to a shared
  production/meshed fabric is the highest-risk action in the tool and needs the clean dual-fabric lab to
  validate the odd/even split; deferred, not abandoned.
- **Auto-propose the ideal subset (rank hosts, pre-select the ready ones)** — rejected for now: at cluster
  scale the operator picks a handful by hand; ranking is weight we don't need. Status *labels* on entries
  give the safety without the ranking logic.
- **Create hosts with only the connected WWPNs** — rejected: the host record should carry the host's full
  HBA set so paths light up automatically once zoning lands; connectivity is *verified and reported*
  (tier 2), not used to filter the create.

## Consequences

- Provisioning can be **built and validated now on the messy lab**: tier-1 create and tier-2's "not zoned"
  reporting are independent of the fabric. Only a *green* tier-2 needs a host that is on **and** already
  zoned — discoverable via `showhost -d`; if none exists, one host is zoned once by hand, or the green
  branch is proved with recorded `showhost` fixtures (which also proves the ideal dual-fabric case).
- `ProvisioningIntent` is restructured (single `VolumeSpec` → list; single `host_set_name` → sets with
  selected members; explicit export rows), and `storage_provision.py` gains the tier-2 read-back.
- The tool stays **structurally read-only where it must be**: discovery and tier-2 verify use only `show*`;
  the switch is never written; the only writes are the gated WSAPI creates (preview + confirm, idempotent).
- Tier 3 (ESXi rescan + VMFS datastore) and zone *creation* remain deferred, each tracked separately.
