# ADR 0030 — The gate fails where it only warned, and measures what could be slipped past it

**Status:** accepted 2026-11-20 (owner's request after the audit of the first refactor steps) ·
**Issue:** BL-65 · **Relates to:** ADR 0028 (the standard and the gate)

## Context

ADR 0028 made `scripts/check.py` the judge of a change, so that "good" is a check and not an
agent's opinion. An audit of the first refactor steps (PR #50, PR #51 and the branches built on
them) looked for ways a change could pass the gate without meeting the rule behind it. It found
several, and the refactor had already used some of them. STANDARD rule 4 says a rule change needs an
ADR; this is the one for the changes that close them.

## Decision

Each row is one weakness the audit named and what the gate does now.

| What | Before | Now |
|---|---|---|
| A list that grows (rule 3) | A branch that added an entry to a list, or raised a number, got a warning. "Only go down" was a request. | `lists` fails and prints every key. `ALLOW_LISTS=1` turns it into a warning: the owner's call, for a new check that brings its list. |
| Code that moves or is renamed | It showed as one new violation and one stale entry. The file's header said to move the line by hand; the message said never to add a line. Splitting a listed file was the easy way out, and PR #51 took it. | `scripts/fitness.py --move OLD NEW` renames the entry and keeps its number. It refuses code that is worse at its new key. The move is recorded in `[moves]`, and `lists` compares a moved entry with its old key, so it is not growth. An old key counts for one new key only. |
| Settings nobody watched (rule 4) | A branch could add a ruff `ignore` or `per-file-ignores` line, loosen `pyrightconfig.json`, switch off an eslint rule, add a knip `ignore`, widen an import contract or edit the gate's own scripts. None of it showed in any list. | `config` fails when a branch changes `scripts/check.py`, `scripts/fitness.py`, `[tool.ruff]`, `pyrightconfig.json`, `frontend/eslint.config.js`, `frontend/tsconfig.json`, the npm scripts or the knip block of `frontend/package.json`, or an import contract (deleting an `ignore_imports` line is a fix and passes). `ALLOW_CONFIG=1` turns it into a warning, for a change that comes with its ADR. |
| Inline suppressions (T3) | `# type: ignore[code]`, `# noqa: CODE` and `eslint-disable-next-line rule` are legal under T3 and were counted nowhere. A type error or lint finding could be hidden one comment at a time. | A new table, `[suppressions]`, counts the lines with `type: ignore`, `noqa`, `pyright:`, `eslint-disable` or `@ts-expect-error` per file in `src`, `tests` and `frontend/src`. It is seeded with today's counts and works like the other lists: a file may not gain one. |
| A document that names code that is gone (C2) | A function named after its file (the LLD named `ssl_context` in an application module after it had moved to an adapter) passed whenever the file existed, whatever it defined. A path with a line number (`http_client.py:86`) was skipped. Only `AGENTS.md`, the READMEs, `CONTEXT.md` and `docs/design` were read. | The file is parsed and must define the name (the syntax tree for Python, a whole-word search for TypeScript). A line number is cut off and the path checked. `docs/STANDARD.md` and the ADRs from 0028 on are read too. |
| A lesson and its check (C4) | C4 promised a `No check:` form the gate did not know, so a lesson about how we work could not be written. Any ruff code that happened to be on (444 of them) counted as "the rule that catches it". | A lesson with `No check:` and a reason passes. Any other lesson after 49 names a test id that exists, a ruff rule that `pyproject.toml` selects, an import contract id, or an eslint rule set to error. |
| `eslint-disable` and its rule code (T3) | T3 said an `eslint-disable` needs its rule code and named `ban-ts-comment` as the check. That rule reads `@ts-` comments only, so nothing checked it. | The claim is dropped from T3. ESLint itself has no rule for it. A rule written in `frontend/eslint.config.js` was tried: a bare `eslint-disable` switches that rule off too, so it saw only the `-next-line` form. The plugin that does this is not installed, and a dependency is not added for it. What holds instead is stricter: the suppressions count refuses every new `eslint-disable`, with or without a rule code. |
| When a listed function is fixed (M1) | "It is fixed when it is next changed for any reason." Nothing checked that, and the typing work rightly edited some twenty listed functions without restructuring them. The rule was false as written. | M1 says what is checked and what is asked. Checked: a listed function may not get worse. Asked of the author and the reviewer: a change to what a listed function does brings it within the limits in the same change. An edit that leaves its behaviour alone (types, a rename, an import) does not count. |
| How a long file is measured (M2) | In lines, with no limit on line length (2,420 lines are over 100 characters). Joining two lines made room for a new one: the typing branch added imports to `init_sheet.py` and `discovery.py` and each came out one line shorter. | In non-blank characters. "Long" is over 18,000 of them: 500 lines at this code's average of 36 to a line. The unit changed, so `[file-lines]` is replaced by `[file-size]`, seeded with today's counts. Two files of under 500 long lines are now listed (`documents/steps.py`, `domain/provisioning.py`); three of just over 500 short lines no longer are (`ProvisionStep.tsx`, `DiscoveryStep.tsx`, `documents/handover.py`). |

## Consequences

- A branch that needs `ALLOW_LISTS=1` or `ALLOW_CONFIG=1` shows a WARN line in the block pasted
  into the pull request, so the reviewer sees that a list grew or a setting changed, and asks why.
  The branch that made these changes needed both.
- The gate's two scripts are linted by the gate (ruff, like `src/`) and `tests/unit/test_gate.py`
  runs `fitness.py` on a throwaway repository. A change to the gate now has to pass both.
- ADRs 0001 to 0027 are not read by the document check. Read today they name 24 paths that are not in
  the repository: files of other projects (`paramiko`'s, the 3PAR client's), files that were planned
  and never built, and files that have since moved. Listing them would add 24 lines that only a
  rewrite of history could clear. From 0028 on an ADR is checked, and when code it names moves, the
  change that moves it corrects the path in the ADR. The two dead paths in ADR 0028 and one in the LLD
  are listed in `quality/ceilings.toml`.
- Two `eslint-disable` comments exist today, both with their rule. Rewriting one of them without its
  rule would keep the count and pass. Review has to see that; the gate does not.
- A branch cut before this change was measured in lines. One that kept a long file's line count by
  joining lines is worse in characters when it meets this change; the typing branch is, in eight
  files. That is the rule working. The owner decides whether the code shrinks or the ceiling is
  seeded once more.

## Not changed

- `fitness.py --seed` can still write a table that was deleted. It no longer gets past the gate:
  the re-seeded entries are compared with the branch point by `lists`.
- Pyright counts errors per file, so one error can replace another, and the count depends on the
  installed packages. Pyright does not read the gate's two scripts.
- The `suppress(Exception)` check matches the bare name only, not an alias of it.
- `docs/DEVELOPER-HANDBOOK.html` is not read by the document check.
