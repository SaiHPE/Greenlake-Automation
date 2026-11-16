# rack13arcus WSAPI captures — 2026-09-13 12:33 (S-0)

Raw `GET /api/v1/{hosts,hostsets,volumes,volumesets,vluns}` responses from CZ2D2K014S (OS 10.5.55,
WSAPI 1.x), captured read-only from the jump box with the S-0 script while `zz_t2_*` was present.

What they settled (SPEC-001 §6):

- A host-set **template** is reported with `hostname: "set:<hostset>"`, `type: 5`, `active: false`.
  The **active paths** of that export are separate records with `hostname` = the *member host*,
  `type: 5`, `active: true`, plus `remoteName`/`portPos`. So templates are the `active == false`
  records, taken as-is — never "type 5 ⇒ prefix set:" (that would invent `set:<hostname>`).
- `provisioningType`: 1 full (`admin`), 2 tpvv (`zz_t2_vol01`), 3 snp (snapshots, `copyOf` set),
  6 tdvv (`zz_t2_vol02`, created with `{"reduce": true}`), 7 dds (`.shared.*`).
- `FCPaths` lists one entry per (WWN, port) — the same WWN appears once per array port it is logged
  in on, so host WWNs must be de-duplicated.

Pinned by tests/unit/test_plan_truth.py.
