# The refactor deepens bounded contexts behind a frozen API contract; the UX redesign is decoupled and comes after

With v0.12.0 shipped the platform is feature-complete except SAN zoning — after zoning lands, scope
freezes (see SCOPE.md). Before that last feature, two efforts run on `refactor/bounded-contexts`: a
structural refactor of the organically-grown backend, and a ground-up UX redesign on the HPE design
system (design-system.hpe.design). This ADR fixes how the two relate, what the refactor's honest
mandate is, and what safety net each side runs on. Evidence base: a full-tree scan on 2026-07-24
(`onboarding_service.py` 733 lines / 44 methods / 11 step pairs; `domain/storage.py` 26 models across
four contexts; 6 dead modules; the step registry mirrored by hand in `frontend/src/modes.ts` plus three
more hand-synced frontend surfaces; ~43 hand-rolled notification panels and two coexisting progress
models in the step components).

**Decision:** the refactor and the redesign are **decoupled behind the frozen HTTP API contract**
(`api/app.py` + `schemas.py` ↔ `frontend/src/api.ts`) and sequenced **refactor first**: (0) dead-code
deletion; (1) backend deepening — the orchestrator god-object becomes a thin run coordinator + four
per-context step services (onboarding, discovery/zoning, provisioning, documents), `domain/storage.py`
splits per context, `application/` reorganizes into context packages, the GreenLake cluster gets the
factory seam every other adapter already has; (2) the **step registry is served** to the frontend
(extending `GET /app/profile`) — the only deliberate contract change — killing the `modes.ts` mirror;
(3) the UX redesign builds a shared StepShell + a single run-progress model, then restyles on stock
`grommet-theme-hpe`; (4) zoning lands on the finished structure. Backend safety is the existing test
suite (182 green after phase 0): every move is small → tests green → commit. Frontend safety is
`tsc --noEmit` + the typed client + **one scripted manual click-through per mode at the very end** —
deliberately **no** frontend test infrastructure is built.

## Why this ADR

**The honest mandate is not future velocity.** Refactoring pays off over future changes, and exactly
one feature remains. The real drivers are (a) zoning must land cleanly — it is the one place the
god-object and the duplicated registry would bite again — and (b) now-or-never: this is the last time
the whole codebase is loaded in one head; the bounded-context cleanup is accepted *as polish* with
eyes open, not sold as ROI.

**Why decouple, and why refactor-first.** Mixing a UI rewrite and a backend restructure in one branch
makes every breakage ambiguous. The frozen contract makes the efforts independent — except the served
registry, which touches both sides; doing it *before* the redesign means the new UI is built on the
unified registry rather than rewired under it afterwards. Refactor-first also means the one expensive
manual verification pass happens once, against the final shape of everything.

**Why no frontend tests.** The redesign is one-time (scope freezes after zoning), so a Playwright
suite would be built for a single run and then rot — the classic infra-you-won't-reuse waste. The
accepted trade-off: regression safety on the UI is a disciplined checklist, not automation. If the
frontend ever re-enters sustained churn, revisit this (characterization smoke tests against a mocked
SSE backend would be the shape).

**What is deliberately NOT done now:** the ADR-0006 cloud control plane (the GreenLake seam only marks
the slot where a DSCC client would go — no speculative abstraction), zone creation (ADR 0004, still
deferred-not-abandoned), and any API contract change beyond the served registry.
