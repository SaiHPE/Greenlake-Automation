# ADR 0029 — Where device-text parsers live

**Status:** accepted 2026-11-20 · **Issue:** BL-65 ·
**Relates to:** [ADR 0028](0028-one-engineering-standard-enforced-by-the-gate.md) (STANDARD T1, L3, B1)

## Context

STANDARD T1 says device output is parsed into typed values "where it enters". It does not say in
which module the parser is written. The boundaries step moved some parsers of array CLI output into
`domain/array_parse.py`: exactly the ones whose import closed a cycle between two contexts. The rest
stayed in `application/*/read.py`, `provisioning/discovery.py` and `documents/asbuilt_parse.py`. A
parser's home therefore depended on whether the import linter had complained, and the move left
copies behind: two functions that split an `n:s:p`, two that blank an unset cell, the same `n:s:p`
pattern compiled in six modules, and a test for a CLI error line sitting in `domain/errors.py`.

Two rules already limit the choice. Application code may not import an adapter module (L3), and a
step context may not import another context's plan or apply (B1). So a parser that two contexts
need can only live in `domain`.

## Decision

1. A parser is a pure function: device text in, a typed value out, no I/O.
2. **A parser, or a helper of one, that more than one context uses lives in
   `domain/array_parse.py`.** That includes the shared pieces: `NSP`, `nsp_parts`, `blank_unset`,
   `table_lines` and `answered_error`.
3. **A parser that one context uses stays in that context's read module**, beside the read that
   calls it. It moves to `domain/array_parse.py` the day a second context needs it; it is never
   copied.
4. A parser only one adapter uses (a host's `multipath -ll`, a WSAPI body) stays in that adapter,
   which returns the domain model.

## Consequences

- STANDARD T1 gains one sentence that states rule 2 and 3.
- `answered_error` moved from `domain/errors.py`; the copies of the `n:s:p` and unset-cell helpers
  in `provisioning/discovery.py` and `replication/read.py` are deleted, and the pattern is compiled
  once.
- The parsers still in the read modules are where this rule puts them. They are not debt.
- Not fixed here: `parse_showsys` returns a plain dictionary inside the type-strict package, which
  T1 does not want.
- No new check. Placement is judgement, as T1 is; L3 and B1 already refuse the cross-context import
  that would tempt a copy.
