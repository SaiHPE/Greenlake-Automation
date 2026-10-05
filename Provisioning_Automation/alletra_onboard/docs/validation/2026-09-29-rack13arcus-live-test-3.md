# Live validation: SPEC-014 hosts + zoning designer, rack13arcus, 2026-09-28/29

Third live record on rack13arcus, run from the rack13 jump box (`ELJR0NB1UV`, 10.132.30.137), which
pulls the `jumpbox-test` branch from github.com and runs the app from source (`.venv\Scripts\onboard.exe ui`).

**Outcome: the provisioning track still passes end to end after the SPEC-014 and bug-sweep changes
(session runner 60/60, then 59/1 where the 1 was the runner, fixed). SPEC-014's lookups, the vCenter
identity read and the Windows read over WinRM are live. Four zoning-designer changes were seen live
the same day they were built. Found live and fixed: installer-default host names taken as
identities. Still owed: the Linux read over SSH (no login), S-9, SPEC-013 *Visible*.**

## Environment

As [2026-09-12](2026-09-12-rack13arcus-live-test-2.md), except: F1 (`SAN6700R13U38`) had **no
effective zoning configuration** on 2026-09-28 (default zone *No Access*); with the lab owner's
agreement `rack13_F1_cfg` was created and enabled with the two zones for `.136` HBA 2 (kept; fixtures
`tests/fixtures/rack13_fabric/F1_cfgactvshow_no_effective_2026-09-28.txt`, `F1_defzone_show_2026-09-28.txt`).
F2 cfg `jul2prabhu`. Sheet `Initialisation_sheet_rack13arcus_spec014.xlsx`, mode *Provision storage only*.

## 2026-09-28

| Time | Build | What | Result | Evidence |
|---|---|---|---|---|
| 16:59 | v0.16.0 + SPEC-014 slices | `session.ps1` (SPEC-006, S-15) | **60 PASS / 0 FAIL** | [evidence-2026-09-28-s15-report.md](evidence-2026-09-28-s15-report.md) |
| day | same | `spec014.ps1` run 1 | 36/1/3 — the WinRM login refused a bare `administrator` (domain-joined host) | [evidence-2026-09-28-spec014-rack13-report.md](evidence-2026-09-28-spec014-rack13-report.md) |
| day | 1cfa22e, 9999bbc | `spec014.ps1` run 2 with `ELJR0NB1UV\Administrator` | **40 PASS / 0 FAIL / 2 SKIP** (Linux: no host) | [evidence-2026-09-28-spec014-rack13-run2-report.md](evidence-2026-09-28-spec014-rack13-run2-report.md) |
| 21:55 | a0cbb04 | `session.ps1` after the bug sweeps | **59 PASS / 1 FAIL** — the FAIL was the runner reading ssh's *Permission denied, please try again* (a mistyped password, retried) as CLI error text; the array's own reads passed: no `zz_s6_` left, counts at baseline 9/4/64/22/45. Runner fixed (dde5ed5). | operator transcript |

SPEC-014 facts read live: `10.132.30.47` serial `CN763604C4` and iSCSI IQN from vCenter; the VME host
`HPE_VM_7f21bf6bf27da180152ea344` found on the array by name and by short name (IQN
`iqn.2024-12.com.hpe:vmenode3:42802`); Windows `ELJR0NB1UV` serial `SGH640WFT7`, FC WWPNs
`51402EC02089CC1C` / `…CC1E`, IQN, *MPIO Installed; 3PARdata VV claimed by MSDSM*; a typed WWPN
`1000000000000001` blocks the plan; no password in any run detail or event.

Code reviews the same day (no live defect behind them) fixed the host-join and zoning defects listed
in SPEC-014's and SPEC-010's addenda — e083406, 486dfa8, ffdf900, a0cbb04 (LESSONS 41).

## 2026-09-29 — zoning designer (read-only; nothing pasted)

Run `7de0e3c0`, *Build zoning plan* re-read both switches each time.

| Item | Build | Seen | Verdict |
|---|---|---|---|
| BL-01 nothing pre-ticked | 0a71a96 | Panel text *"Nothing is ticked for you…"*; *Names* says *Select a pair above*; *Generate command set (0 new zones)* disabled; operator's own ticks → *(2 new zones)* / *(3 new zones)* | pass |
| Command set | same | F1: `alicreate` ×2 for the new host aliases, array-port aliases reused, `zonecreate` ×2, `cfgadd "rack13_F1_cfg"`; F2: new alias for `0:3:3` (none on F2), `cfgadd "jul2prabhu"`; `cfgsave` / `cfgenable` in block 3 | correct |
| BL-08 found | 0a71a96 | Two HBA ports (`10:00:5c:ed:8c:53:12:a3` F1, `…:a2` F2) named `localhost.localdomain` from the name server — see *Defect* | fixed c199a29 |
| BL-08 fixed | c199a29 | Same ports shown by WWPN; alias `host_12a3_hba1` | pass |
| BL-04 A | c199a29 | Host alias `CZ2D2K014S_N1S3P3` (array port 1:3:3's alias) → *Not included: … already exists on the switch for another device*; no `zonecreate` | pass |
| BL-04 B | c199a29 | `host_cc1e_hba1` for `cc:1e` and `12:a3` → first pair rendered; second *Not included: … is also the name chosen for host 51:40:2e:c0:20:89:cc:1e* | pass |
| BL-09 | 11ff0e1 | Same two cases red in the names panel before the click (*Already on the switch for another device* / *Same name as …* on both ports), counter *"N selected pair(s) have a missing, invalid or clashing name"*, Generate disabled; corrected name → *Valid*, enabled | pass |

## Defect found live

**Installer-default host names were identities (BL-08).** The name server's `HN:` field is what the
HBA driver advertises; an unconfigured Linux install advertises `localhost.localdomain`. The captured
fabrics hold 29 WWPNs under `localhost.bgl1.global.tslabs.hpecorp.net`, 7 under
`localhost.localdomain`, 4 under `localhost`, 3 `smartstart` across two adapters. The provisioning
host union groups initiators by name, so choosing that "host" as a set member would have created one
array host carrying many servers' HBAs. Fixed: those names leave the port unnamed. Two tests had
pinned the placeholder as a name (LESSONS 42).

## Owed

- Linux / HPE VME read over SSH (SPEC-014 R4) — needs a login (TRACKER BL-10).
- S-9 iSCSI export (BL-11); SPEC-013 *Visible* after a rescan (BL-12).
- Zone-name clash and > 64 checks — **seen live 2026-10-05** (fresh install from `jumpbox-test`): host
  alias `rack13` + array alias `F1_cfg` → *zone rack13_F1_cfg already exists on the switch* (FOS shares
  one namespace for alias/zone/cfg); a 50-character host alias → *… is 68 characters — FOS allows 64*;
  Generate disabled in both. Nothing pasted.
- As-built provisioned sections, page-by-page review (S-8).
