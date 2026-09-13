# SPEC-002 — The as-built documents the provisioned array

**Status:** implemented 2026-09-13 (rc.8; 18 acceptance tests + 1 service test green; array parsers
pinned to the rack13arcus capture) — **pending live confirmation** (S-8 of the second live
session; one CLI capture owed, §6)
**Findings closed:** G-0 (register), SCOPE area 9 as-built line; Z-2 on the way (the copied paste
block now carries its header lines)
**Owner:** documents context (`application/documents/asbuilt.py`, `asbuilt_parse.py`, `steps.py`;
`adapters/array/cli_client.py` allowlist; `api/app.py` `/zoning/render` + `service.record_zoning_render`)

## 1. Problem

The as-built reads `shownode showcage showsys shownet showversion showpd showcpg showport
showinventory checkhealth` and fills three template sections: configuration, inventory,
checkhealth. It was designed for the handover of an *initialized* array. Since v0.15 the same run
discovers hosts, designs zoning, creates hosts / sets / volumes / exports and verifies paths — and
the document says nothing about any of it. The document generated after run 2 on 2026-09-13
(1,615 lines) has no trace of the host, the three volumes, the VV-set, the host set, the three
exports or the zoning plan that run produced.

## 2. Scope

In: five new sections after *checkhealth*; the array reads that feed them; the run records that
feed them; per-read failure handling; the TOC. Out: HLD/LLD (SCOPE area 9, not started); any
change to the three existing sections; ESXi-side facts (G-3).

Two kinds of section, kept distinct in the document because they answer different questions:

- **Array sections** describe *everything on the array* — the customer receives an array, not a
  run. Source: read-only `show*`.
- **Run sections** describe *what this engagement did* — the zoning designed, the objects created,
  the paths verified. Source: the run's own events. They are the only place the word "created" may
  appear.

## 3. Requirements

**R1 — Hosts and host sets.** From `showhost -d` and `showhostset`. One row per host object: name,
persona, initiators (FC WWPNs and IQNs), array ports it is logged in on, host set(s) it belongs to.
Logins with no host object (`-- --` rows) are a separate table, *Logged in, no host object*, because
on a customer array that is the "zoned but never provisioned" list. Host sets: name → members.

**R2 — Volumes and volume sets.** From `showvv` (+ `showvv -showcols …UsrCPG…` for the CPG, see
R7), `showvvset`. Base volumes only in the main table: name, provisioning (tpvv / tdvv / full /
dds), dedup, compression, size GiB, CPG, snapshot count, VV set. System volumes (`admin`, `.srdata`,
`.mgmtdata`, `.shared.*`) and snapshots (`snp` / `vcopy`) are counted in a one-line note, not listed.
VV sets: name → members.

**R3 — Presentations.** From `showvlun -t` (the templates — what is presented to whom) with
`showvlun -a` (what is live). One row per template: LUN, volume, presented to (`set:<hs>` shown as
"host set <hs>"), active paths (count of active + non-optimised rows for that LUN + volume, and the
hosts they belong to). A template with zero active paths is stated as such — that is a presentation
nobody can see.

**R4 — SAN zoning (run section).** From the run's latest `zoning.plan` event, its latest zoning
check (`zoning.previewed` / `zoning.proper`), and its latest `zoning.rendered` event. Per fabric:
switch (name, address), fabric name, active cfg, switches in fabric; then one row per host HBA →
array port pair: host, HBA WWPN, alias, array port n:s:p, array WWPN, alias, zone name(s), status
(*already zoned* / *command set delivered* / *not selected*). The command set handed to the SAN team
is reproduced verbatim (monospace) under the sentence *"Delivered to the SAN team for application;
confirm against the fabric before relying on it."* The zoning check result (hosts zoned on both
fabrics / not verified) closes the section. No zoning event → one sentence: *This run did not
include the SAN zoning step.*

*The record R4 needs did not exist:* `/zoning/render` was pure and stateless, so the command set the
operator copied was never on the run. The request now takes an optional `run_id`; when present the
service emits `zoning.rendered` (`commands`, `skipped`, `aliases`, `selected_pairs`) without
touching the run's status. The UI passes the run id from the Generate button (an explicit click, not
a keystroke, so the event volume is one per generation).

**R5 — Provisioning record (run section).** From the latest `storage.applied` (result) with its
timestamp, and the latest `storage.paths.verified`. Table: kind, name, result (Created / Updated /
Already existed / Failed), detail (LUNs from read-back, WWNs added). Then path verification: host,
verdict, detail. No apply event → *This run did not include the provisioning step.* A `storage.previewed`
plan with no apply → *A plan was built but not applied.*

**R6 — Empty is not failed.** Every section is written. When the array has nothing, the section says
so in one sentence ("The array reports no host sets."). When a read failed, the section says that
("`showhostset` could not be read: <error>") **and** the failure is in the document's warnings list,
so the operator sees it before sending. One failing read never stops the others or the document.

**R7 — CPG per volume.** `showvv` has no CPG column. The tool also reads
`showvv -showcols Id,Name,Prov,Type,CPG,VSize_MB` and joins on name (the column is `CPG` on OS
10.5.55 — C-1; `UsrCPG` is accepted too for other releases). If that read fails, the CPG column
reads "—" and a warning names the command. Header-driven parsing: columns are located by their
header token, never by position.

**R8 — Read-only, inside the allowlist.** `showhostset` and `showvvset` are added to
`ALLOWED_COMMANDS`. Nothing else changes in the client. No write is ever issued.

**R9 — TOC.** The template's table of contents is a Word field. The document sets
`w:updateFields` so Word refreshes the TOC (and page numbers) on open; new headings appear in it.
New headings use the template's *Heading 1* style so `_start_sections_on_new_pages` and the running
header treat them like the originals.

**R10 — Parsers pinned to real output.** `tests/fixtures/rack13_array/` (rack13arcus, 2026-09-13
00:07, after run 2) pins `showhost -d`, `showvv`, `showvvset`, `showhostset`, `showvlun -t`,
`showvlun -a`. The `-showcols` form of `showvv` is the one read without a capture (§6).

## 4. Data contract

```python
@dataclass
class AsBuiltData:
    ...existing fields...
    # array sections — raw text, parsed by the renderer like inventory/checkhealth
    showhost_d: str = ""
    showhostset: str = ""
    showvv: str = ""
    showvv_cpg: str = ""       # showvv -showcols …UsrCPG…
    showvvset: str = ""
    showvlun_t: str = ""
    showvlun_a: str = ""
    read_errors: dict[str, str] = field(default_factory=dict)   # command -> error text (R6)
    # run sections — the events' payloads as dicts (already JSON-shaped), None when the step did not run
    zoning_plan: dict | None = None
    zoning_report: dict | None = None
    zoning_rendered: dict | None = None      # {commands, skipped, aliases, selected_pairs}
    provisioning_plan: dict | None = None
    provisioning_result: dict | None = None
    provisioning_applied_at: str = ""
    path_verification: dict | None = None
```

New parsers in `asbuilt_parse.py`, all header-driven:

| function | input | returns |
|---|---|---|
| `parse_showvv(text)` | `showvv` or `showvv -showcols …` | `[dict]` one per row, keys = header tokens (`Name`, `Prov`, `Type`, `VSize(MiB)`/`VSize_MB`, `UsrCPG`, …); snapshots included with `Type == "vcopy"` and `CopyOf` |
| `parse_cli_sets(text)` | `showhostset` / `showvvset` | `OrderedDict[name, [members]]`; continuation lines are members; `--` = empty; "No … listed" = `{}` |
| `parse_showvlun_templates_cli(text)` | `showvlun -t` | `[VlunTemplate]` (domain model from SPEC-001; `set:` kept) |

Reused: `provisioning.discovery.parse_showhost` (hosts, unclaimed logins),
`provisioning.path_verify.parse_showvlun_active` (active paths).

`DocumentSteps._run_records(run_id)` reads `coord.list_events(run_id)` once and returns the latest
payload per event type; `_collect_asbuilt` runs each command inside its own try/except, recording
`read_errors[cmd]` (R6) — a connection/login failure still raises, as before.

## 5. Acceptance tests (`tests/unit/test_asbuilt_provisioned.py`)

| Test | Requirement |
|---|---|
| `test_parse_showvv_pins_the_capture` (51 rows; `zz_t2_vol02` tdvv dedup 1024 MiB; snapshots carry CopyOf) | R2, R10 |
| `test_parse_showvv_showcols_is_header_driven` | R7 |
| `test_parse_cli_sets_pins_hostset_and_vvset_captures` (6 host sets, 9 VV sets, `test.Snapset` empty, "No vv set listed" → {}) | R1, R2, R10 |
| `test_parse_showvlun_templates_cli_pins_the_capture` (3 templates, `set:zz_t2_hs`, type "host set") | R3, R10 |
| `test_hosts_section_lists_hosts_sets_and_unclaimed_logins` | R1 |
| `test_volumes_section_hides_system_and_snapshot_volumes_but_counts_them` | R2 |
| `test_presentations_section_joins_templates_with_active_paths` | R3 |
| `test_zoning_section_renders_the_plan_and_the_command_set` | R4 |
| `test_zoning_section_states_when_the_step_did_not_run` | R4 |
| `test_provisioning_record_renders_outcomes_timestamp_and_paths` | R5 |
| `test_provisioning_record_states_plan_without_apply` | R5 |
| `test_a_failed_read_is_named_in_the_section_and_in_the_warnings` | R6 |
| `test_an_empty_array_section_says_so_without_a_warning` | R6 |
| `test_new_sections_are_heading_1_after_checkhealth_and_toc_updates_on_open` | R9 |
| `test_collect_continues_past_a_failing_command` | R6 (steps) |
| `test_run_records_take_the_latest_event_of_each_type` | R4, R5 (steps) |
| `test_showhostset_and_showvvset_are_allowlisted_and_nothing_else_changed` | R8 |

Existing `test_asbuilt.py` / `test_asbuilt_parse.py` unchanged. Plus, in `test_onboarding_service.py`:
`test_zoning_render_is_recorded_on_the_run_without_touching_its_status` (R4's record).

## 6. Live confirmation

- **C-1 answered 2026-09-13 12:33:** `showvv -listcols` on OS 10.5.55 has `CPG`, not `UsrCPG`/`SnpCPG`
  (`-showcols …UsrCPG,SnpCPG…` → "Invalid columns specified"). The as-built now reads
  `showvv -showcols Id,Name,Prov,Type,CPG,VSize_MB`; the renderer accepts either header. Pinned by
  `tests/fixtures/rack13_array/showvv_listcols.txt`. The corrected command's output is the same
  header-driven table shape as `showvv`; capture it with S-8 for completeness.
- **S-8:** generate the as-built after S-4 (the cluster case) and review the five sections against
  `showhost -d` / `showvlun -t` on the array and the zoning command set on screen.

## 7. Non-goals and risks

- Tables are appended at the end of the body (the template's last section is checkhealth); if a
  future template puts another section after checkhealth, the new sections follow it. Acceptable.
- `w:updateFields` makes Word ask "update fields?" on first open. That prompt is the price of a
  correct TOC; the alternative (a TOC that omits five sections) is G-0 again.
- Large arrays: `showvv` on a 2,000-volume array is a long table. The document is for handover of
  what was built; a per-run filter is deliberately NOT applied (array sections show the array).
