# SAN Zoning step — UI/UX redesign plan

**Status:** proposed 2026-09-12 from the rack13arcus live test of v0.16.0-rc.5 and an external
evidence pass (sources at the end). **Phases 0–2 implemented the same day** (backend union + zone
names + fabric identity + FOS validation + `cfgsave`; frontend panels A–F) — **built, pending live
run** (`docs/validation/2026-09-12-rack13arcus-live-test-2.md`). Phase 3 (per-HBA method) is open. Scope is the **zoning step only** — `ZoningStep.tsx`,
`ZoningPlanView.tsx`, the zoning-context models in `domain/zoning.py`, `application/provisioning/
zoning_plan.py`, and the `POST /zoning/render` endpoint. Nothing else in the app changes: the step
registry, `StepShell`, `useStepState`, the SSE event names (`zoning.plan`, `zoning.previewed`,
`zoning.proper`), the provisioning gate (`zoned_hosts`), and ADR 0012 (**no switch writes**) all stay.

## 1. Why — what the live test showed

The zoning *data* was right on every check against raw `nsshow` / `nscamshow` / `cfgshow` /
`showhost -d` output. The *presentation* made an expert operator doubt it. Findings, in the words
of the operator where possible:

| # | Finding | Kind |
|---|---|---|
| Z1 | "F1 — 10.132.30.111" read as a host; "10.132.30.136" not labelled as a host; WWPN not labelled as the host's HBA port. Nothing on the screen names what anything is. | Labels |
| Z2 | "(zoned)" doesn't say zoned **to this host**, nor **by which zone**. Operator asked "zoned to which host? how do I infer that?" The zone name (`kiranzone1`) is in the `cfgshow` the tool already reads. | Information |
| Z3 | Alias boxes appear for WWPNs that need no action (`.136`, fully zoned), inviting input that does nothing. | Noise |
| Z4 | No legend for grey tick (exists) vs green tick (you selected). | Status |
| Z5 | Alias name `arcus_esx86-hba1` accepted without validation; FOS ≤8.0.1 rejects `-`. | Validation |
| Z6 | "Current zoning" (read) and "design new zones" (build) are one undifferentiated view. | IA |
| Z7 | After the SAN team applies, the operator has no obvious "re-check and watch the boxes turn grey" loop. | Flow |
| Z8 | **Hosts not in vCenter never reach the plan.** `cc:1e` (Windows `.137`), `12:a3`, `12:a2` are live unzoned initiators on the declared switches and are invisible in this step when vCenter answers. Declared (Hosts-tab) hosts are not consulted either. | **Design defect** |
| Z9 | Hosts placed via `nscamshow` (remote switch) show no hint that they sit on another switch in the fabric (`.86` on `SAN1624ZR12U40`). Operator could not tell why it was offered on F2. | Information |
| Z10 | WWPNs shown without the decode an expert does in their head (`20:34:00:02:ac:…` = array node 0 slot 3 port 4). | Readability |

Z8 is a backend change and blocks the customer-shaped test (mixed Windows/Linux + vCenter estate).
Everything else is presentation and can ship without touching the command grammar.

## 2. Principles the redesign keeps (do not relitigate)

1. **The tool never writes to a switch** (ADR 0012). The deliverable is a command set; `cfgenable`
   is shown apart from the paste block.
2. **Commands are rendered by the backend** (`POST /zoning/render`) — one grammar implementation.
   The UI never assembles `alicreate`/`zonecreate` strings.
3. **The UI renders from the event stream**, not from step return values (`useStepState`).
4. **Existing pairs are never recreated**; the delta is the only output.
5. **Status = colour + icon + shape + text, at least three of four** (DS status rule). Never "health".
6. **Brocade FOS only**; the UI says so (ADR 0004 scope note).
7. **Fabric placement comes from the switch name servers** (local `nsshow` + fabric-wide
   `nscamshow`); "already zoned" comes from the array's logins (`showhost -d`) cross-checked with the
   effective cfg. Both stay; the UI just explains them.

## 3. Vocabulary (exact strings)

| Concept | Show as | Never |
|---|---|---|
| Fabric card header | **Fabric F1 (odd)** · switch `10.132.30.111` `SAN6700R13U38` · fabric `Training_Lab_Rack12` · active cfg **`mycfg`** | "F1 — 10.132.30.111 (cfg mycfg)" |
| A host | **Host** `10.132.30.136` · ESXi 8.0.2 · from vCenter | bare IP |
| A host's adapter | **HBA port** `10:00:5c:ed:8c:53:12:a9` | "WWPN" alone, "adapter" |
| An array port | **Array port 0:3:4** (node 0) `20:34:00:02:ac:02:d4:95` | WWPN alone |
| Pair already effective | **Zoned** · zone `kiranzone1` | "(zoned)" |
| Pair operator selected | **New zone** | green tick alone |
| Pair possible, not selected | **Not zoned** | empty box alone |
| Host adapter in no fabric NS | **Not on either fabric** — check cable/power | "Offline" |
| Host adapter on a remote switch | **on `SAN1624ZR12U40` (10.132.30.62)** via ISL | nothing |
| Host identity source | from vCenter / from sheet (Hosts tab) / from fabric name server / array login only | "switch" |
| Array port with non-host Type | ⚠ Type `rcfc` — array does not report this as host-serving | — |
| Config sections | Effective / Defined (FOS terms) | "active", "current" (mixed) |

## 4. Information architecture — five panels, one step

The step keeps its `StepShell` (title, description, actions, gate, activity). Inside, top to bottom:

```
┌ SAN zoning ─────────────────────────────────────────────────────────── Step 5 of 8 ┐
│ Read-only against the array and both Brocade switches. Produces a command set your  │
│ SAN team applies. This tool never writes to a switch.            [Re-check] [Plan]  │
├─ A. Fabrics ─────────────────────────────────────────────────────────────────────────┤
│ Fabric F1 (odd)  switch 10.132.30.111 SAN6700R13U38 · Training_Lab_Rack12 (2 sw)    │
│   active cfg mycfg · array ports here: 0:3:4 (node 0) · 1:3:3 (node 1)              │
│ Fabric F2 (even) switch 10.132.30.112 SAN6700R13U40 · Training_Lab_Rack11 (2 sw)    │
│   active cfg jul2prabhu · array ports here: 0:3:3 (node 0) · 1:3:4 (node 1)         │
│ ⓘ Non-standard cabling: 0:3:4 and 0:3:3 attach opposite to card-port parity —       │
│   fabric taken from the switch (ADR 0009).                                          │
├─ B. Current zoning (what the array can reach today) ────────────── [Export .txt] ───┤
│ Host              HBA port            Fabric  Array ports        Zone        Status  │
│ 10.132.30.136     10:00:…:12:a9       F1      0:3:4, 1:3:3       kiranzone1  ● Zoned │
│  ESXi · vCenter   10:00:…:12:a8       F2      0:3:3, 1:3:4       Vmware_All… ● Zoned │
│ arcus-win137      51:40:…:cc:1c       F2      0:3:3, 1:3:4       arcus__win… ● Zoned │
│  Windows · sheet  51:40:…:cc:1e       F1      —                  —           ▲ Not zoned│
│ 10.132.30.86      51:40:…:cc:38       F2 (on SAN1624ZR12U40)  —  —           ▲ Not zoned│
│  ESXi · vCenter   51:40:…:cc:3a       —       —                  —           ○ Not on fabric│
│ (unnamed)         10:00:…:12:a3       F1      —                  —           ▲ Not zoned│
│ 3 of 5 hosts zoned on both fabrics · 2 HBA ports need zones · 1 not on any fabric    │
│ ☐ Show only hosts that need zones                                                    │
├─ C. Design new zones ─────────────────────────────────────────────────────────────────┤
│ Method: (•) One zone per HBA port × array port (SIST)  ( ) One zone per HBA port (1:N) │
│ Fabric F1 · cfg mycfg                                                                │
│  arcus-win137 · HBA port 51:40:…:cc:1e                                               │
│    node 0: [✓ New] 0:3:4        node 1: [✓ New] 1:3:3        ← recommended: one per node│
│  (unnamed) · HBA port 10:00:…:12:a3                        [Name this host…]         │
│    node 0: [ ] 0:3:4            node 1: [ ] 1:3:3                                    │
│ Fabric F2 · cfg jul2prabhu                                                           │
│  10.132.30.86 · HBA port 51:40:…:cc:38 · on SAN1624ZR12U40 via ISL                   │
│    node 0: [✓ New] 0:3:3        node 1: [✓ New] 1:3:4                                │
│  arcus-win137 · HBA port 51:40:…:cc:1c   ● Zoned 0:3:3, 1:3:4 (arcus__windows137_zone2)│
├─ D. Names for the new zones ─────────────────────────────────────────────────────────┤
│ Only WWPNs that take part in a new zone are listed. Existing aliases are reused.     │
│ Fabric F1                                                                            │
│  HBA port  arcus-win137  51:40:…:cc:1e   alias [arcus_win137_hba2        ] ✓ valid   │
│  Array port 0:3:4        20:34:…:d4:95   alias [rack13arcus_N0S3P4        ] ✓ valid   │
│  Array port 1:3:3        21:33:…:d4:95   alias [rack13arcus_N1S3P3        ] ✓ valid   │
│  → zones: arcus_win137_hba2_rack13arcus_N0S3P4 · arcus_win137_hba2_rack13arcus_N1S3P3 │
│ Fabric F2                                                                            │
│  HBA port  10.132.30.86  51:40:…:cc:38   alias [arcus_esx86-hba1] ✗ '-' needs FOS ≥8.1│
│  …                                                                                   │
│                                              [Generate command set (4 new zones)]    │
├─ E. Command set — give to your SAN team ─────────────────────────────────────────────┤
│ Fabric F1 · 10.132.30.111 · cfg mycfg                     [Copy] [Download F1.txt]   │
│ ┃ alicreate "arcus_win137_hba2","51:40:2e:c0:20:89:cc:1e"                            │
│ ┃ …                                                                                  │
│ ┃ cfgadd "mycfg","…;…"                                                               │
│ Additive only. Creates nothing that exists; removes nothing.                        │
│ ▌Then, separately — activation (SAN team, in a window)                               │
│ ▌ cfgtransshow      ← must report no outstanding transaction first                   │
│ ▌ cfgsave                                                                            │
│ ▌ cfgenable mycfg                                                                    │
│ Fabric F2 · …                                                                        │
├─ F. After the SAN team applies ──────────────────────────────────────────────────────┤
│ [Re-check zoning]  Reads the array's logins again. Newly zoned pairs move to Zoned.  │
│ Last check 17:02 · since then: +2 logins (arcus-win137 on 0:3:4, 1:3:3)              │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

Panel by panel:

**A. Fabrics** — one card per declared switch. Shows the switch name and fabric name (from
`switchshow`/`fabricshow`), how many switches are in the fabric, the active cfg, and which array
ports attach here with their **node**. Cabling notes from discovery (parity mismatch, single fabric,
overlap) render here as an inline info notification — today they are computed and dropped.

**B. Current zoning** — a read-only `DataTable`, one row per **HBA port**, grouped under its host
(host name in the primary column with source and OS beneath). Columns: HBA port WWPN · Fabric (with
"on `<remote switch>`" when placed via `nscamshow`) · Array ports it is logged into · Zone name(s)
from the effective cfg · Status. Status uses the DS four-element rule. Footer summary in one
sentence. **Export .txt** produces the same table as plain text — the artefact a SAN team wants
before they touch anything. The filter "show only hosts that need zones" is the default when any
exist.

**C. Design new zones** — only HBA ports with at least one unzoned pair on a fabric. Array ports
are grouped **by node** so "one port per node" (the redundancy rule) is visible, and that pattern is
**pre-selected** as the recommendation (operator can untick). Already-zoned pairs render as a status
line, not as disabled checkboxes. An unnamed initiator (array login / NS only) gets a "Name this
host" affordance that writes the name into the plan (not the sheet) so the alias suggestion and zone
names are readable. Method toggle: SIST (today's grammar) or per-HBA 1:N (HPE's stated preference
for coexistence with other HPE arrays — see sources); the toggle changes only how the backend
renders `zonecreate`.

**D. Names** — lists **only** WWPNs participating in a selected new zone. Each field is pre-filled:
an existing alias for that WWPN on that switch (reused, no `alicreate`), else a suggestion from the
convention `<host>_hba<n>` / `<array system>_N<n>S<s>P<p>`. Inline validation against FOS rules
(start with a letter, `[A-Za-z0-9_]`, ≤64; `-`/`$`/`^`/leading digit flagged "needs every switch on
FOS ≥ 8.1.0"). The resulting zone names are previewed live so the operator sees what will land in
`cfgshow` before generating.

**E. Command set** — per fabric, a DS code block (Prism theme, `wrapLongLines`, `tabIndex=0`),
**Copy** and **Download `<fabric>_<switch>_<date>.txt`** (header comment: fabric, switch, cfg, run
id, generated-at, operator note "additive only"). Activation is a separate bordered block, as now,
extended with the FOS-recommended preamble/sequence: `cfgtransshow` → paste → `cfgsave` →
`cfgenable <cfg>`, with the sentence "cfgenable replaces the effective configuration fabric-wide;
run it in a window".

**F. After apply** — the loop the operator described. **Re-check zoning** is the existing
`/zoning/preview` (array `showhost -d`); the panel shows what changed since the last check and the
provisioning gate updates from the same `zoned_hosts` it uses today.

## 5. Status indicators (DS: ≥3 of colour · icon · shape · text)

| State | Colour | Icon | Text |
|---|---|---|---|
| Zoned (effective) | status-ok | StatusGood (circle-check) | Zoned · `<zone>` |
| New zone (selected) | brand | Add (circle-plus) | New zone |
| Not zoned (on fabric, unzoned) | status-warning | StatusWarning (triangle) | Not zoned |
| Not on either fabric | status-unknown | StatusUnknown (circle-dash) | Not on fabric |
| Caution (non-host Type port) | status-warning | Alert | ⚠ Type `<type>` |

## 6. WWPN readability

- Monospace, lower-case, colon-grouped, **wrap not truncate** (DS DataTable rule for long numeric).
- Role tag before every WWPN: "HBA port" or "Array port n:s:p (node N)".
- Array WWPN decode on hover/`a11yTitle`: `2N:SP:00:02:AC:<sysid>` → "array node N slot S port P".
- Initiator/target role from the NS `Device type` / FC4 features, never from the OUI (OUI shown as a
  secondary hint only: QLogic `51:40:2e`, HPE `5c:ed:8c`, Emulex `10:00:00:00:c9`).

## 7. Backend changes (zoning context only, all additive)

| Change | Where | Why |
|---|---|---|
| **Host list = union** of vCenter HBAs, declared hosts (Hosts tab), local-NS physical initiators, array unclaimed logins; each tagged `host_source`; grouped into one host when a source ties WWPNs together | `zoning_plan.build_zoning_plan` | Z8 — customer estates are mixed; today's fallback triggers only when vCenter returns nothing |
| `already_zoned` → carry the **zone name(s)** from effective `cfgshow` per pair | `FabricZonePlan.zone_names: dict[str, list[str]]` (key `host|array`) | Z2 |
| `FabricZonePlan.fabric_name`, `switch_name`, `switch_count`, per-host `placed_on_switch` | from `switchshow`/`fabricshow`/`nscamshow` "Switch entry for" | A, Z9 |
| `AliasedWwpn.node` for array ports (parse from `nsp`) | domain | node grouping in C |
| Alias suggestion when none exists: `<host>_hba<n>` / `<system>_N<n>S<s>P<p>` | `_suggest_alias` | D pre-fill |
| FOS name validation in `render_commands`; invalid → `skipped` with the rule violated | `render_commands` | Z5 |
| Activation block gains `cfgtransshow` (comment) and `cfgsave` before `cfgenable` | `render_commands` | FOS reference: cfgsave commits; cfgenable separate |
| Optional `method: "sist" \| "per_hba"` on `/zoning/render` | endpoint + renderer | C method toggle; default `sist` keeps today's output byte-identical |
| Discovery cabling notes surfaced on the plan | `ZoningPlan.notes` already exists — copy discovery's fabric notes in | A |

No change to `ZoningReport`, the preview step, the provisioning gate, `steps.py` event names, the
sheet, or any other step. Existing unit tests keep passing; new fixtures come from
`script-logs/rack13_precheck_20260912_152028.utf8.txt` and `rack13_nscam_20260912_172824.txt`
(two-switch fabrics, remote-switch initiator, NPIV targets, alias-free F1, dead zone member).

## 8. Frontend component plan

Keep `ZoningStep.tsx` as the orchestrator (events → `report`, `plan`; actions; gate). Replace
`ZoningPlanView.tsx` with:

| Component | Panel | Notes |
|---|---|---|
| `FabricOverview` | A | pure render of `plan.fabrics[*]` + notes |
| `CurrentZoningTable` | B | Grommet `DataTable` grouped by host; export builds text client-side from the same data |
| `ZoneDesigner` | C | selection state; pre-selects one-port-per-node for unzoned HBA ports; method toggle |
| `AliasReview` | D | derives participants from selection; validation mirrors backend rules (backend stays authoritative) |
| `CommandSetPanel` | E | reuses today's `CommandSet` split; adds Download and Prism code block |
| `RecheckBar` | F | calls `zoningPreview`; diff of `report.expected` vs previous |

`api.ts` types gain optional fields only. `useStepState`, `StepShell`, `status.tsx`,
`primitives.tsx` unchanged.

## 9. Phasing

| Phase | Content | Backend? | Exit test |
|---|---|---|---|
| **0 — words** | Labels/vocabulary of §3, legend, hide alias rows for fully-zoned hosts, FOS validation client-side, activation block gains `cfgtransshow`/`cfgsave` text | none | Operator reads the screen without asking what a row is |
| **1 — truth** | Host-source union (Z8), zone names, remote-switch placement, cabling notes on the plan | yes (§7 rows 1–3, 9) | `cc:1e` appears on F1 with `0:3:4`/`1:3:3`; `.136` shows `kiranzone1`; `.86` shows `SAN1624ZR12U40` |
| **2 — flow** | Panels B/C/D/E/F as designed; export; re-check diff; alias suggestions | yes (§7 rows 4–7) | Phase 3 of the lab plan run end to end through the UI: design → paste → `cfgenable` → re-check turns pairs Zoned |
| **3 — method** | per-HBA 1:N rendering; peer-zone research | yes (§7 row 8) | golden tests for both grammars; SIST output unchanged |

Phase 0 can ship in the next rc without a live run (text only). Phase 1 needs the rack13 live test
repeated (it changes what the plan contains). Phase 2 is the one to design on mockups first
(LESSONS 22) — update `docs/ux/mockups.html` before implementing.

## 10. Acceptance criteria (from the 2026-09-12 lab)

1. F1 card names switch `SAN6700R13U38`, fabric `Training_Lab_Rack12`, cfg `mycfg`, ports `0:3:4`
   (node 0) and `1:3:3` (node 1); shows the non-standard-cabling note.
2. Current zoning lists `10.132.30.136` twice (one row per HBA port) as **Zoned · kiranzone1** (F1)
   and **Zoned · <F2 zone>**; `arcus-win137` `cc:1c` Zoned, `cc:1e` **Not zoned**; `.86` `cc:38`
   Not zoned "on SAN1624ZR12U40"; `cc:3a`, `.47` ×2 **Not on fabric**; `12:a3`, `12:a2` as unnamed
   Not zoned.
3. Designer offers `cc:1e` → `0:3:4`, `1:3:3` only, pre-selected; offers nothing for `.136`.
4. Alias `arcus_esx86-hba1` is flagged; `arcus_esx86_hba1` passes; existing alias reuse produces no
   `alicreate`.
5. For the same selection and names as today, the F2 command set is **byte-identical** to the one
   generated 2026-09-12 (golden test), with the activation block now `cfgsave` + `cfgenable`.
6. Nothing is selected → no commands for that fabric; no request touches a switch write path
   (`cfgshow`/`cfgtransshow` before/after identical).
7. Re-check after a manual `cfgenable` moves the pair to Zoned and unlocks the host in provisioning.

## 11. Non-goals

Switch writes (ADR 0012). Cisco MDS (ADR 0004 scope). SANnav/Web Tools integration. Editing or
deleting existing zones. Changing the sheet or any other step.

## 12. Sources

HPE (host implementation guides, B10000): zoning by HBA "one initiator to multiple targets per zone"
recommended and required for coexistence; SIST also supported; WWN or Smart SAN zoning recommended;
verify with `showhost` — sd00003478 (AIX), sd00003479 (HP-UX), sd00002431 (SLES), sd00002430 (target
port limits). SAN Design Reference Guide sd00001803: "Alletra MP zoning best practices", "Zoning by
HBA", "Single initiator–single target Zoning" (titles verified; body to be read for ports-per-fabric).
Broadcom FOS 9.2.x: `zoneCreate`/`aliCreate` naming rules (letter/digit start, `[A-Za-z0-9_-$^]`,
case-sensitive, 64 chars; `-$^`/leading digit need FOS ≥ 8.1.0 fabric-wide), `cfgSave` commits the
transaction, `cfgEnable` builds and commits, `cfgTransShow` for open transactions; "Single HBA"
zoning recommended; WWN identification for security; peer zones recommended where available; naming
example `SRV_…`/`ZNE_…`. Cisco NDFC 12.2 zoning UI: Status online/offline, Zoned By, Type host/
storage, "View unzoned end devices", activation diff, pending vs effective DB, config-file export
for CLI paste. IBM SAN zoning best practices: zone by initiator, WWPN never WWNN, four paths per
volume. HPE Design System (design-system.hpe.design): DataTable (status = shape+colour+content,
wrap long numerics, `--` empty cells), status indicator (≥3 of 4), notification (inline near content,
never "health"), wizard (summary before submit), forms (labels, help text, inline errors), code
blocks (Prism theme, wrap long lines). Local evidence: `script-logs/rack13_precheck_20260912_152028
.utf8.txt`, `script-logs/rack13_nscam_20260912_172824.txt`, operator screenshots 2026-09-12.
