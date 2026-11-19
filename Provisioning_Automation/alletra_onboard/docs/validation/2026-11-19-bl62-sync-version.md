# Live validation: sync refused for the arrays' OS versions before any write (BL-62), 2026-11-19

Run from the developer's Mac on the HPE VPN, the app from source on `debt/d-bl62-sync-version` on
127.0.0.1:8783 with a fresh state database, driven by `lab/rcip_tool_lab.py` under the lab lock. Pair:
rack13-ARCUS (CZ2D2K014S, 10.132.30.121, **OS 10.6.0**) → PRIMERA630R11U22 (SGH339NK4C, 10.132.30.28,
**OS 4.6.20**), from the starting point with no partnership.

**Outcome: a sync row is refused at the first read with one sentence, the apply is refused and the run
sends no write to either array; async over the same pair still passes end to end (38/0). The demo pair
was READY before and after.**

## What the rule is built from

| Evidence | Where |
|---|---|
| The array's refusal, 2026-11-18 (rehearsal 2): *RC sync/AA configurations are not supported with target PRIMERA630R11U22 running 4.x / 9.x. (HTTP 400, code 29)*, after the partnership was set up and the link check passed (0.021 ms) | `~/Documents/alletra-demo/rcip_tool/05-apply-2.json`, `report.txt` (17/1) |
| rack13 on 10.6.0 | `tests/fixtures/rack13_snap/showversion.txt` (2026-11-16); preview 1's `os_version` in the same evidence |
| The same pair ran sync on 2026-11-03 with rack13 on **10.5.55** (25/0) | [2026-11-03-rcip-partnership.md](2026-11-03-rcip-partnership.md); `tests/fixtures/rcip_pair/before/{alletra,primera}/showversion.txt` |
| 10.5.0 ↔ 10.5.0 sync, live 2026-10-09 | `tests/fixtures/rc_pair/{D22U27,E18U31}/showversion.txt` |
| What the research notes and Support Matrix summaries say about sync to an older family | nothing (`docs/research/2026-09-19…`, `2026-10-07…`, `2026-11-17-rcfc.md`) |

So the plan blocks a sync group to create when this array is on release 10.6 and the peer on 4.x or 9.x
(the two the message names); 10.5.x stays allowed. SPEC-016 R2 has the rule and what it leaves out.

## The runs (IST)

| Run | Script | Result |
|---|---|---|
| `768dcfe1` sync | `rcip_tool_lab.py` as on `main` | **8 PASS, 2 FAIL**, the two expected: *preview 1: no group yet, no blocker* (the plan now carries the blocker) and *stopped: partnership plan has blockers*. The pair was back at the start. |
| `b8ffa408` sync | adjusted (BL-62 path) | **12 PASS, 0 FAIL**. Versions read 10.6.0 / 4.6.20; preview 1 planned the partnership rows as before and one blocker: *rack13-ARCUS (OS 10.6.0) refuses sync replication to PRIMERA630R11U22 (OS 4.6.20), as it does to any Primera 4.x array, so the sync row for volume set 'zz_rc_vvs' cannot be configured: set Mode to async (periodic) on the Replication tab for this pair.* Apply 1: HTTP 409 *the plan has findings that must be resolved first*. The run's console log holds 18 commands, all reads (`showsys`, `showversion`, `showport`, `showport -rcip`, `showrctransport -rcip`, `showrcopy`, `showcpg`, `showvvset`, `showvv` on each array), no write. |
| `9ae5db09` async | adjusted, `RCIP_MODE=async` | **38 PASS, 0 FAIL**: partnership set up (8 steps, links Up), link check 0.02 ms, both groups created (12 writes), Periodic 5 min, verify replicating with `showrcopy -d`, failover 6.8 s and back 6.6 s, as-built, removal set pasted, pair back at the start. |

In both sync runs the only objects made on an array were the script's own `zz_rc_vol01` and `zz_rc_vvs` on
rack13 (made before the run, removed by the script at the end), as in every run of this script.

`demo_prep.py check` and `demo_objects.py check` from the main checkout: all READY before (20:41) and after
(20:49); `demo_rc_vol01` / `demo_rc_vvs` on rack13 untouched.
