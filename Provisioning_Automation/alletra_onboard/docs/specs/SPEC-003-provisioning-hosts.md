# SPEC-003 — Provisioning sees every host the run knows

**Status:** implemented 2026-09-13 (rc.8; 10 acceptance tests green, existing provisioning tests
unchanged) — **pending live confirmation** (S-4 of the second live session: `.136 + .86` in one host
set; a sheet-declared Windows host in a set)
**Findings closed:** P-2, P-3
**Owner:** provisioning context (`application/provisioning/hosts.py` new, `storage_provision.py`,
`steps.py`; `domain/provisioning.py`; `frontend/src/steps/ProvisioningBuilderView.tsx`)

## 1. Problem

The provisioning host list is `discovery.host_hbas` — vCenter only. On 2026-09-13 the Compose
dropdown offered `.136 / .47 / .86`; `arcus-win137` (declared on the sheet) and
`localhost.localdomain` (seen on the fabric) — both of which the **zoning** step lists since rc.6 —
could not be put in a host set or given an export (P-2). The same dropdown offered eleven iSCSI-only
array hosts (`HPE_VM_*`, `grp3_vmenode*`) at the same weight as the FC hosts the run is about,
with no hint that this tool neither zones nor path-verifies iSCSI (P-3).

## 2. Scope

In: one host union for provisioning (plan, apply, path-verification targets, the Compose
dropdown), with source, transport and persona per host; the dropdown label and order. Out: iSCSI
host *creation* over WSAPI (the client takes FC WWNs only — a separate spec when G-4's iSCSI export
is scheduled); any change to the zoning step's own union (it stays inline in `zoning_plan.py`,
live-proven rc.6/rc.7).

## 3. Requirements

**R1 — One union, in trust order for the name.** `union_hosts(discovery, declared_hosts,
zoning_plan)` returns provisionable hosts from: vCenter (`discovery.host_hbas`), the sheet's Hosts
tab (`intent.declared_hosts`), the array's own host objects (`discovery.array_hosts`, never the
unclaimed row), and the fabric name servers as the zoning plan recorded them (`fabrics[].hosts`
with `host_source == "switch"`, when a zoning plan exists). The first source to name an initiator
wins; a later source only adds initiators or fills a blank OS. Hosts are keyed by name; an
initiator already claimed by another name is not re-claimed (the array is the arbiter, and
`ensure_host` refuses a WWN that belongs to another host anyway). A name left with **no**
initiator of its own — typically a sheet row that re-types a WWPN vCenter already attributes — is
dropped from the union with a note naming the owner, never planned as an empty host.

**R2 — Each host carries what provisioning needs.** `name`, `source` (`vcenter | sheet | array |
switch`), `wwpns` (normalised), `iqns`, `os`, `persona` (vCenter/switch/sheet → `persona_for_os`;
array → the persona the array already has), `transport` (`fc | iscsi | both | none`).

**R3 — Nameless initiators are counted, not offered.** Array unclaimed logins and fabric
initiators with no name cannot be created (a host object needs a name). They do not appear in the
list; the plan carries one note: *"N initiator(s) logged in with no host name — name them on the
sheet's Hosts tab to provision them."*

**R4 — Plan, apply and path verification use the same union.** `_selected_hosts`,
`_persona_by_host`, `exported_volumes_by_host`, `host_briefs` all derive from `union_hosts`. The
steps layer passes the latest `zoning.plan` payload (from the run's events) to all of them, so what
the operator was offered is what apply creates and what the verifier checks.

**R5 — Transport is visible, never a silent peer.** `DiscoveredHostBrief` gains `source`,
`transport`, `persona`, `fc_capable`. In the Compose dropdown FC-capable hosts come first, labelled
`name — status · source`; iSCSI-only hosts follow, labelled `name — iSCSI only · not zoned or
path-verified by this tool`. They remain selectable (a mixed-transport set is legal on the array).
When a composed host set contains one, the plan carries a note naming it.

**R6 — Nothing is created for a host with no FC initiator.** An iSCSI-only host is planned only
when it already exists on the array (it joins a set; nothing is created). One that does not exist
yet is not planned and is named in a note: the WSAPI client registers FC WWNs only, and a host
object created without its IQN would be a lie of omission.

**R7 — Existing behaviour holds.** With vCenter as the only source, the list, personas, selected
hosts and exports are exactly what they were (the existing tests in `test_storage_services.py`
pass unchanged).

## 4. Data contract

```python
class ProvisionableHost(BaseModel):          # domain/provisioning.py
    name: str
    source: Literal["vcenter", "sheet", "array", "switch"]
    wwpns: list[str] = []                    # normalised
    iqns: list[str] = []
    os: str = ""
    persona: str = "VMware"
    @property transport -> "fc" | "iscsi" | "both" | "none"

class DiscoveredHostBrief(BaseModel):        # + fields
    source: str = ""
    transport: str = "fc"
    persona: str = ""
    fc_capable: bool = True

def union_hosts(discovery, declared_hosts, zoning_plan=None) -> tuple[OrderedDict[str, ProvisionableHost], list[str]]
    # (hosts by name, notes)  — application/provisioning/hosts.py
```

`build_plan / apply_plan / exported_volumes_by_host / host_briefs` gain `zoning_plan: dict | None =
None` (the `zoning.plan` event payload, JSON-shaped, like SPEC-002's run records).

## 5. Acceptance tests (`tests/unit/test_provisioning_hosts.py`)

| Test | Requirement |
|---|---|
| `test_union_orders_sources_vcenter_sheet_array_switch` | R1, R2 |
| `test_union_first_name_wins_and_later_sources_only_add` | R1 |
| `test_union_never_offers_nameless_initiators_but_counts_them` | R3 |
| `test_union_array_host_keeps_its_persona_and_transport` | R2 |
| `test_union_switch_hosts_come_from_the_zoning_plan_payload` | R1, R4 |
| `test_plan_and_apply_create_a_sheet_declared_windows_host` (the `arcus-win137` case) | R4 |
| `test_plan_notes_an_iscsi_only_member_of_an_fc_set` | R5 |
| `test_briefs_carry_source_transport_and_put_iscsi_last` | R5 |
| `test_path_verification_targets_include_non_vcenter_hosts` | R4 |
| `test_vcenter_only_behaviour_is_unchanged` | R7 |

## 6. Live confirmation owed

**S-4** (cluster `.136 + .86`) and a sheet-declared host (`arcus-win137`, WWPN `…cc:1c`) in a host
set → plan shows it with source `sheet`, persona `WindowsServer`; apply creates it; the as-built
lists it. The switch-sourced `localhost.localdomain` appears in the dropdown once the zoning plan
has been built in the same run.
