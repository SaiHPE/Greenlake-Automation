# ADR 0020 — Migration: the tool prepares and proves; HPE's Peer Motion imports

**Status:** accepted 2026-11-17 (owner's decision), with the changes below · **Research:**
[2026-11-16-migration-from-a-source-array.md](../research/2026-11-16-migration-from-a-source-array.md) ·
**Spec:** [SPEC-027](../specs/SPEC-027-migration-source-array.md) · **Keeps:** ADR 0001 (SSH reads are
read-only), ADR 0012 (no switch writes), ADR 0013 (one array credential per run) · **Leaves deferred:**
ADR 0014 (paired runs) · **Tracker:** BL-27

## Changes at acceptance (2026-11-17)

The owner accepted the decision with the changes a review recommended. Each is folded into the text
below.

1. **Option D added.** DSCC's public API now has migrations (storage-fleet v1alpha1). It is the likely
   future way to drive an import, and R10 progress could read it. The hand-off stays for now (§
   *Options*, D).
2. **Decision 5 is half done.** BL-46 made the read client refuse `showtarget -rescan`. Only `showrsv`
   remains, after its help has been read for options that act (LESSONS 46).
3. **The read-only account is the tool's.** Peer Motion itself needs a source account that can create
   hosts and exports (decision 1, SPEC-027 R1).
4. **The first live pair is E18U31 and the lab's HPE 3PAR 20850 R2**, so 3PAR is the first family to
   parse (§ *Consequences*, SPEC-027 §4).
5. **Open questions narrowed** (research §10): Q3 likely answered by the API, Q5 keeps W1, Q7 no longer
   needed, Q8 yes. Q1, Q2, Q4 and Q6 stay open.
6. **Must confirm before slice 1 is called done:**
   - `showversion -a -b` on the 3PAR: release, MU and patches.
   - Who owns E18U31's peer ports. The VZ fabric capture (`tests/fixtures/vz_fabric/`) has a zone
     `Pandu_*` pairing them with another array. Ask before using them (LESSONS 35).
   - A SPOCK edition of the Peer Motion matrix that covers destination 10.5.60.
   - The role Peer Motion's source account needs, and the persona of the host it creates there.
   - Whether a Peer Motion licence is needed on the source.

## Context

SCOPE areas 2 and 3 name "discover source array information" and "migration peer setup and zoning".
The customer case is a B10000 replacing a 3PAR, Primera or Alletra 9000, with the data moved by HPE's
Peer Motion over FC peer ports.

HPE supports that move from two places only: the B10000's own UI and DSCC (Peer Motion support matrix,
*Supported UI* column). DSCC's Block Storage API has no migration resource; its storage-fleet API, still
alpha, has one (option D). The destination CLI has the primitives (`admitvv`, `importvv`), but using
them means writes on **both** arrays: on the source, a host for the peer ports and exports to it, later
the removal of the production host's exports; on the destination, admit and import. The source is the
customer's production array, often an older OS of another product family the tool has never written
to. A failed import is a host outage (the field back-out plan budgets 4 to 5 hours).

Replication already showed how the tool handles a second array: the peer is a step credential on the
one-array run (SPEC-015), not a second run (ADR 0014, deferred).

## Decision

**The tool reads the source, checks readiness against HPE's support matrix, designs the peer zoning and
the host zoning as command sets, hands the import to Peer Motion in the B10000 UI or DSCC, then reads the
result and documents it. It never writes to the source array and never starts, pauses or cuts over an
import.**

1. **The source is a read-only step credential.** Supplied on the workbook's *Migration* tab, held by
   the run like the replication peer and the switches, used only through `ArrayCliClient` (the read
   allowlist). No WSAPI session is opened to the source and no write client is ever built with its
   credential, so no write path exists. This account is the tool's. Peer Motion uses its own source
   account, which the operator types into the B10000 UI or DSCC; that one must be able to create hosts
   and exports on the source. The tool never asks for it.
2. **One array per run stands.** The run's array, and its one array credential (ADR 0013), is the
   destination B10000. A Migration tab naming the run's own array is refused. Nothing is configured on
   the source, so there is no second run to pair and ADR 0014 stays deferred.
3. **Zoning is a command set** (ADR 0012): peer zones (one source host port to one destination peer
   port per zone) and host zones to the destination, rendered in FOS order. Zone removal after the
   import is a later, separate command set.
4. **Peer ports are BL-26's** (SPEC-025). This decision reads them; it does not configure them.
5. **The read client becomes exact.** Done for `showtarget`: BL-46 refuses `-rescan`, and the Tcl
   quoting characters that could smuggle it past the check. Remaining: `showrsv` joins the read
   allowlist only after `help showrsv`, captured on each family it will run on, has been read for
   options that act. Any such option goes into `_ACTION_OPTIONS`, and the test includes the allowed name
   with that option (LESSONS 46).

## Consequences

- The tool owns the parts that fail most in the field and cost least to get right: version and patch
  gaps, a missing peer link, a zone on the wrong fabric, a cluster too large for an online move, a
  volume in a Remote Copy group. HPE's tool owns the import and its own checks.
- The operator types the import into the UI or DSCC by hand, from the facts the step shows. That is one
  more screen, and it is where the operator decides.
- Parsers for the source run on 3PAR, Primera and Alletra 9000 output, pinned to captures from each.
  **3PAR comes first.** The lab's HPE 3PAR 20850 R2 (4UW0002142) is already visible on both FC peer
  ports of E18U31 (DHCI_B10K, OS 10.5.60): `showportdev ns` on 0:3:2 and 1:3:2 lists it, captured
  2026-11-17 for BL-26. So the first live read needs no peer-port setup, no cabling and no switch paste,
  and R8's visibility (the source seen on both peer ports) can be proven with no write.
- That pair is not expected to import. The 3PAR's fabric name, fw:3313, suggests 3.3.1 MU3; the matrix
  minimum is 3.3.1 MU5 with P141, P173 and P180. This is an inference until `showversion -a -b`
  confirms it. The first live run proves the read and a version blocker, not an import.
- A real import later needs a source inside the matrix. The VZ fabric's name servers list candidates:
  a 3PAR 8400 at fw:3321 (3.3.2 MU1 by the same reading), a 3PAR 7400c at fw:3315 (3.3.1 MU5), several
  Alletra 9060s (fw:9410 to fw:9570) and Primera A650s (fw:4530, fw:4650). Each needs its owner's
  consent, a peer zone and its patches checked. The Primera 630 (4.6.20) on rack13 is the second
  family to parse.
- If the owner later wants the tool to drive the import, option D is the likely way: its own
  amendment, after the hand-off path has run live. The tool would still build no write client for the
  source; Peer Motion does the source-side work with its own account, as it does from the UI.

## Options

- **A. Hand the import to Peer Motion in the B10000 UI or DSCC.** Chosen (the decision above).
- **B. The tool runs `admitvv` / `importvv`.** Rejected: needs source-side writes and bypasses the
  supported orchestration; the blast radius is the customer's data path.
- **C. Drive DSCC's migration wizard with Playwright.** Rejected: no captured wizard, no stable
  selectors, and the DSCC browser is attach-only with the operator signed in (ADR 0006).
- **D. Drive Peer Motion through DSCC's storage-fleet API.** Added 2026-11-17; kept for later, not
  rejected. Source: storage-fleet v1alpha1, spec version 1.4.0,
  `developer.greenlake.hpe.com/_bundle/docs/greenlake/services/storage-fleet/public/openapi/storage-fleet-public-v1alpha1/storage-fleet-api.yaml`,
  read 2026-11-17 (not in the repository's offline mirror). Paths are under
  `/storage-fleet/v1alpha1/devtype4-storage-systems/{systemId}`:
  - `POST …/migration-partners` adds the source: address, user, password, family
    `3PAR/PRIMERA/ALLETRA-9K`, protocol `FC` or `iSCSI`.
  - `GET …/migration-partners/{id}/hosts`, `/host-sets`, `/volumes`, `/volume-sets`, `/vluns`,
    `/ports`, `/remotecopy-groups` read the source as Peer Motion sees it. `GET
    …/migration-partners/{id}` shows its connection state, peer hosts and peer-link pairs (up to 4).
  - `POST …/migration-partners/{id}/migrations` starts an import: hosts or `set:<hostset>`, CPG,
    `tpvv` or `reduce`, minimally disruptive (`isMdmRequired`), pause before the data transfer
    (`pauseMigration`). It also takes `removeSourceVolume`. `POST …/migrations/{id}/actions` resumes,
    reverts or retries.
  - `GET …/migrations` (per partner or per system) gives status, percent complete, current step and a
    host persona (described for Nimble sources only).

  Why not now: the API is alpha; it needs a DSCC API client with write rights on storage-fleet, and the
  tool has none (it uses the GreenLake platform API and an attached DSCC browser); whether our workspace
  is entitled to it is unknown (ADR 0006: entitlements are the gate); and the source password would go
  to DSCC from the tool. A read-only use for R10 progress can come first, as its own decision.
- *A paired run for the source (ADR 0014).* Rejected: nothing is provisioned on the source; pairing
  would add the A/B machinery for a read.
- *Leave everything to the operator.* Rejected: discovery of the source and the peer zoning are scope
  items, and the zoning command set is the pattern that already works (G-1).
