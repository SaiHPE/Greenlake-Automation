# Live validation: zoning + provisioning, rack13arcus (BGL), 2026-08-31

First end-to-end run of the SAN zoning and storage provisioning steps **driven by the operator in
the shipped application UI** against real hardware, rather than by scripts from a workspace. Purpose
was to decide whether the tool is fit to cut over to production use.

**Outcome: the chain works. Three defects were found that produce wrong answers, and one capability
was found that no document in the repository authorises.** See [ADR 0012](../adr/0012-no-switch-writes-the-tool-emits-a-command-set.md).

## Environment

| | |
|---|---|
| Array | Alletra MP B10000 `rack13arcus`, `10.132.30.121`, serial CZ2D2K014S, user `3paradm` |
| CPG | `SSD_r6` |
| Fabric F1 | `10.132.30.111`, active cfg `mycfg` |
| Fabric F2 | `10.132.30.112` `SAN6700R13U40`, active cfg `jul2prabhu`, **13 zones, shared production fabric** |
| vCenter | `10.132.26.124` |
| Hosts seen | `.136` (2 HBAs, both fabrics), `.47` (2 HBAs, both offline), `.86` (1 online on F2, 1 offline) |
| Mode | Provision storage only |

**The array is cross-cabled.** F1 carries array ports `0:3:4` + `1:3:3`; F2 carries `0:3:3` + `1:3:4`.
Card-port parity ties in *both* fabrics, so parity-based fabric assignment would be wrong on both.
The switch-derived resolution of ADR 0009 got it right, which is its second validation against
genuinely non-standard cabling.

## What was driven, and what the hardware said

### Zoning

The plan read both switches, showed `10.132.30.136` as already zoned on all four pairs (pre-ticked
and locked, excluded from the command set), and offered `10.132.30.86` `51:40:2e:c0:20:89:cc:38`
against `0:3:3` and `1:3:4` on F2. One pair was selected, aliases named `zz_test_h86` /
`zz_test_a0303`, and the zone was created on the switch **by the application**.

Confirmed by hand on `10.132.30.112` afterwards:

- `zz_test_h86_zz_test_a0303` present in the **Defined** configuration of `jul2prabhu`, built from
  both new aliases.
- **Effective** configuration unchanged: still the same 13 zones, ours absent. Defined held exactly
  one zone more than Effective and it was ours. Nothing pre-existing was modified, and the other
  configurations on that switch (`CFG1`, `cfg1`, `cfg3`, `cfg_haji`, `jul2`) were untouched.
- `cfgtransshow` reported no outstanding transaction, so `cfgsave` committed and left no fabric lock.
  This was the failure mode most worth catching: FOS `cfgsave` prompts interactively and defaults to
  no, which would have exited cleanly while silently discarding everything.

### Provisioning

Composition: host-set `zz_test_hs` with member `.136`; export `zz_test_vol01` → host set, auto LUN.
Plan built, authorised, applied. Result: **4 created, 0 already existed.**

Confirmed by hand on the array:

```
showhost -d
 16 10.132.30.136  VMware  10005CED8C5312A8  0:3:3 / 1:3:4
 16 10.132.30.136  VMware  10005CED8C5312A9  1:3:3 / 0:3:4

showvv zz_test_vol01
 27 zz_test_vol01  tdvv  v2  Yes  ...  1024 MiB

showvlun -a
  0 zz_test_vol01  10.132.30.136  ...A8  0:3:3  host set  active  10
  0 zz_test_vol01  10.132.30.136  ...A9  0:3:4  host set  active  10
  0 zz_test_vol01  10.132.30.136  ...A9  1:3:3  host set  nonopt  11
  0 zz_test_vol01  10.132.30.136  ...A8  1:3:4  host set  nonopt  11
```

- Persona **VMware**. Every other host on that array, including the iSCSI `HPE_VM_*` hosts and
  `Node1/2/3`, is Generic-ALUA. The persona-by-name lookup resolved correctly through the real client.
- `tdvv` + compression v2 + dedup Yes is what a **reduce** volume looks like from the CLI, so the
  `{"reduce": true}` body landed correctly.
- Type `host set` confirms the set-level export, not a host-level one.
- Four paths over two HBAs and two nodes, `active` on node 0 and `nonopt` on node 1: textbook ALUA.
  A8 sits on F2, A9 on F1, so the redundancy is genuine and crosses both fabrics.
- Tier-2 path verification reported `10.132.30.136` **Live, 2 HBA(s) on both fabrics**.

**Negative control.** `51402EC02089CC38` (`.86`) appears nowhere in `showhost -d`. Its zone was
written to the defined configuration only, so it is not active, so that host has not logged into the
array. Had it appeared, something would have activated a configuration that nothing should have.

## Crossed to proven-live

Previously built-but-unproven, now confirmed on hardware through the shipped UI:

- The zoning step driven end to end in the app, including the delta against the effective
  configuration on a fabric with 13 live zones.
- Full `apply_plan` through the **real client**. Prior tier-1 proof (2026-07-23, VZ) used standalone
  scripts that mirrored the request shapes; this was the packaged product.
- Tier-2 path verification returning a `live` verdict against real hardware.
- By implication, this build's executable carries a working WSAPI SDK, since the writes went over WSAPI.

Still unproven: as-built document through the UI, GreenLake registration (component A).

## Defects found

**1. Unclaimed logins were discarded, so a zoned host reported as unzoned.** `parse_showhost`
skipped any row whose first field was not a digit. `showhost -d` prints a WWPN with no Host record as
`-- -- -- <wwpn> <n:s:p>`, so those rows were dropped and their WWPNs never reached the fabric
lookup. The verify called `10.132.30.136` "not zoned on either fabric" while the zoning plan showed
it fully zoned — the plan was right. This is the normal state of a freshly zoned server, so on a
greenfield array every host would have been mislabelled. Fixed in `80d002d`, regression tests pinned
to this array's real rows. Glossary term added: **Unclaimed login**.

**2. Path verification asserts an export exists without checking.** The `no_path` detail hardcodes
"(export exists; it activates once the host is on + zoned)". Clicking **Verify paths** before the
plan is applied — the button has no guard — printed that sentence for a volume that did not exist.

**3. Path verification claims "exported-but-no-path" for hosts in no export row.** `dead_vols` is
computed as intent-volumes minus live-volumes for every host in the target set, and the target set is
every vCenter host rather than the hosts in the provisioning intent. `.47` and `.86` were reported
as having an export of `zz_test_vol01`, which was only ever destined for `zz_test_hs`, whose sole
member is `.136`.

**4. `cfgenable` is rendered identically to the commands that execute.** Same monospace block, weight
and colour. The backend refuses to run it (two independent guards), but the display invites a human
to paste it. This contributed directly to finding 6.

**5. The provisioning gate accepted intent instead of completion.** `ZONING_OK` included `"staged"`,
so a staged-but-unactivated zone unlocked provisioning for `.86` — a host that then correctly
reported `no_path`. Replaced by a per-host gate on verified zoning (ADR 0012).

**6. The tool has switch write access that no document authorises.** Found on 2026-09-02 while
reviewing this run. ADR 0004 and `CONTEXT.md` both state the tool never writes to a switch; a write
path shipped in v0.14.0/v0.15.0 on a mandate recorded only in a docstring. **The operator, reviewing
this session, stated he had pasted the commands himself.** He had not — his transcript contains only
read commands. See ADR 0012 and LESSONS 30-32.

## Defect status, 2026-09-02

All six are now closed in code. None of the fixes has been driven through the app against hardware.

| # | Defect | Fixed in |
|---|---|---|
| 1 | Unclaimed logins discarded, so a zoned host reported unzoned | `80d002d` |
| 2 | Path verify asserts "export exists" without checking | `aada08c` |
| 3 | "exported-but-no-path" for hosts in no export row | `aada08c` |
| 4 | `cfgenable` rendered identically to executed commands | `ca32a62` |
| 5 | Gate accepted intent (staged) instead of completion | `ca32a62`, revised in `2908382` |
| 6 | Switch write access no document authorises | `ca32a62` |

Found and fixed in the same window, none of them from this run's list, all by reading real output
rather than by a test failing: the array persona ignored as an OS signal (nine hosts reported
"Unidentified" while the array said VMware and WindowsServer); every iSCSI initiator in an unclaimed
row given the first one's IP; colliding IQN-derived host names rendered as duplicate rows; host
objects with no adapters dropped silently; the RCIP "unset" gateway marker reaching the UI as a
literal `-`.

## Owed

- **Cleanup, manual.** Array: `removevlun -f zz_test_vol01 0 set:zz_test_hs` → `removevv -f
  zz_test_vol01` → `removehostset -f zz_test_hs` → `removehost -f 10.132.30.136`. Switch
  `10.132.30.112`: `cfgremove "jul2prabhu","zz_test_h86_zz_test_a0303"` → `zonedelete` → `alidelete`
  ×2 → `cfgsave`. No `cfgenable`.
- **Disclosure to the SAN team** must state that the onboarding tool logged into F2 with the sheet
  credentials and created the zone, not that an engineer pasted it.
- **A run of the current build against hardware.** Everything since this test is verified against
  captured command output, not driven through the application. That is the same gap this run existed
  to close: on 2026-08-31 the zoning parser was correct and the step still gave the wrong answer.
