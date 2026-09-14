# SPEC-007 — The tool writes the removal script for what it created

**Status:** implemented 2026-09-14 (rc.14) — **pending live** (the next session's cleanup runs the
tool's own set instead of a hand-written one)
**Findings closed:** G-5
**Owner:** provisioning context (`storage_provision.py`, `domain/provisioning.py`),
`ProvisionStep.tsx`, `documents/asbuilt.py`

## 1. Problem

Three cleanups in two days were hand-written from memory against a shared array — fourteen
commands the last time, in dependency order, with LUN numbers copied off a screenshot. The tool
knows every object it created (each `storage.applied` result), it knows the LUNs the array assigned
(the R8 read-back), and it already hands the SAN team a copy-paste command set rather than writing
to the switch (ADR 0012). The undo for a half-failed apply, and the cleanup after a test, are the
same document; nobody should have to compose it by hand.

## 2. Requirements

**R1 — Only what this apply created.** Removal items are derived from outcomes with status
`created`. Objects that `exists` or were `updated` are never in the set: they were someone's before
this run, and removing them would remove another team's object. `updated` objects are named in a
note (*"Not reverted — members or WWNs were added to: …"*).

**R2 — Exports by diff, not by status.** Export removals are the VLUN templates present after apply
that were not present before (`after − before`, both reads apply already makes), one
`removevlun -f <volume> <lun> <target>` each. This is exact for a set export completed member by
member (only the new member's LUN) and can never name a pre-existing LUN.

**R3 — Dependency order, always.** The list itself — `ProvisioningResult.removals`, the `storage.applied`
event, every render of it — is in the order exports → VV sets → volumes → host sets → hosts, whatever
order the outcomes came in, so the block can be pasted top to bottom by anything that reads it
(S-12 found the runner pasting the raw list host-before-set). One command
per object (`removevv -f` per volume, not one line of five — a failure names the object).

**R4 — Never executed by the tool.** The set is text: `ProvisioningResult.removals` (structured,
so records can be unioned) and a rendered block. The UI shows it under the Result with a header the
paste carries (`# Removal of what run <id> created on <array> — <time>` / `# Review before pasting.
The tool never runs these.`), *Copy* and *Download .txt*. The as-built's provisioning record
includes the block under *To remove what this run created*, unioned across every apply in the run.

**R5 — Empty is stated.** An apply that created nothing renders *"Nothing to remove — this apply
created nothing."*

## 3. Data contract

```python
class RemovalItem(BaseModel):
    kind: ActionKind            # vlun | vvset | volume | hostset | host
    name: str                   # the object (for vlun: "<volume> LUN <n> → <target>")
    command: str                # the CLI line, `-f` where the CLI prompts

class ProvisioningResult(BaseModel):
    ...
    removals: list[RemovalItem]
    removal_notes: list[str]    # R1's "not reverted" note

def render_removal_commands(items: list[RemovalItem]) -> list[str]   # R3 order, de-duplicated
```

## 4. Acceptance (`tests/unit/test_removal_set.py`)

`test_removal_covers_only_what_this_apply_created_in_dependency_order`,
`test_export_removals_come_from_the_template_diff_not_the_status`,
`test_updated_objects_are_not_reverted_but_named`,
`test_render_orders_by_kind_and_dedups_across_two_applies`,
`test_nothing_created_means_an_empty_set`,
`test_the_second_session_cleanup_would_have_been_generated` (pinned to the 2026-09-14 apply: the
same fourteen lines the operator typed, in the same order).
