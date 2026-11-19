# ADR 0028 — One engineering standard, enforced by the gate

**Status:** accepted 2026-11-19 (owner's request: "the best architecture, HLD, LLD, free of technical
debt, a golden standard to follow") · **Issue:** BL-65 ·
**Relates to:** ADR 0011 (contexts), ADR 0025 (SSH writes), ADR 0026, ADR 0027

## Context

The code grew feature by feature, much of it written by agents. A measurement on main `f95fbdbd`
(2026-11-19) found:

- The documented layering did not hold. Application modules imported adapters in 13 places, and
  three adapters imported the application layer (`platform/tls`).
- Workflow packages imported each other in cycles: provisioning↔replication, replication↔documents,
  provisioning↔snapshots, runs↔provisioning. There was also a domain cycle, snapshots→provisioning.
- Every reader of the array could call any of the 14 WSAPI write methods. The failover test started
  without an approval token.
- Pyright reported 147 errors, and 49 functions were over a complexity of 10 (the worst, 91).
  The code held 127 `noqa: BLE001` and 20 `type: ignore`.
- The structure was described in four places, which disagreed: `ARCHITECTURE.md`, `HLD.md`,
  `LLD.md` and `AGENTS.md`.

Nothing checked any of these rules, so each new change could copy whichever example it found.

Refactoring to "clean code" without a reference would only swap one agent's taste for another's. The
owner asked for a standard with a source behind each rule, so that a later change can be measured
against it.

## Decision

1. **`docs/STANDARD.md` is the reference.** Each rule names its published source (Saltzer and
   Schroeder; Cockburn; Percival and Gregory; Evans; Ousterhout; King; McCabe; Ford et al.; Tan;
   arc42/C4/Nygard; react.dev). Each rule also names the check that enforces it, or says it is
   judgement.
2. **The checks run in `scripts/check.py`.** Each tool keeps its own list of today's violations. The
   list only shrinks. An entry is keyed by file and symbol, never by line. The gate fails on a new
   violation, on a listed function that got worse, and on a stale entry.
3. **The order of work is risk first** (STANDARD.md section 5). Every change preserves behaviour and
   is checked live where it touches a device.

## How the standard was reviewed

A first draft was critiqued independently by three models (Claude Fable 5.2, GPT 6.2 Astra and
Gemini 4 Carbon). All three were given the same brief and the same measurements.

| Change from the draft | Raised by | Why |
|---|---|---|
| Dropped "application reaches every device through a Protocol, wired in a bootstrap module" | all three | Adds about 400 lines of one-implementation interfaces. Tests already inject fakes through factories. A Protocol does not stop a fake drifting from the vendor (LESSONS 28 and 29). It also made the write-client check unprovable. |
| Least privilege added as its own section (reader and writer classes, writers built only from an approval, undo stored before the write returns) | Astra, Fable, Carbon | The real gap was power, not import direction. The as-built could have called a write, and the failover test starts with no approval. |
| Independent contexts replaced by a declared order of workflow packages | all three | They share one model and one vocabulary, and verify and the as-built must read live state (SPEC-018 R3). Independence would have forced copies or stale reports. |
| File-length and parameter limits replaced by ruff's defaults with per-function ceilings, and "a file over 500 lines may not grow" | Fable, Carbon, Astra | The draft's numbers had no source. Ousterhout argues against length limits. McCabe and NIST give 10. |
| Native tool baselines keyed by symbol instead of a custom comparator keyed by line | Fable, Astra, Carbon | Line keys churn on every edit. A count alone lets one fix pay for an unrelated regression. |
| Broad catches confined to two modules, with a `DeviceError` family | Fable, Carbon | A per-folder allowance switched the check off where most catches are. S110 was ignored globally. |
| Typed run events before generating TypeScript types | Carbon, Astra | Most hand-written frontend types describe event payloads, which are `dict[str, Any]` in the backend today. |
| No retro-fitted lesson checks; no feature-map file; a `lab_script` field on each step instead | all three | It avoids a third tracker. A script's existence is not a live run. |
| Build-profile and PyInstaller-spec checks added | Carbon, Astra | Moving modules can break the init-only build and the packaged exe without failing a test (LESSONS 16). |

Kept although one reviewer argued against it: arc42 headings and C4 diagrams for the HLD. Gemini
Carbon called them duplicates of `ARCHITECTURE.md`. The owner asked for a proper HLD and LLD, so
`ARCHITECTURE.md` is the one removed.

## Consequences

- The gate is stricter from the day this lands. Today's violations are listed, so it stays green.
- A refactor counts as done when its entries leave the lists, the tests pass unchanged, and the live
  checks pass. An agent's opinion that the code is cleaner does not count.
- `AGENTS.md` gets shorter. Where a rule is now a check, it points to the check.
