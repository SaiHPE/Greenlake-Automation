# Phase 3 implementation plan — UX redesign

**Status: awaiting approval. No implementation begins until this plan and the mockups are signed off.**

| | |
|---|---|
| Branch | `feat/ux-redesign` |
| Design reference | [`docs/ux/mockups.html`](mockups.html) — 15 screens, professional register |
| Rules reference | [`docs/UX-GUIDELINES.md`](../UX-GUIDELINES.md) — HPE Design System requirements + documented divergences |
| Governing decision | ADR 0011 — frozen API contract; frontend verification = `tsc` + build + one scripted manual pass |
| Out of scope | Backend changes of any kind; API contract changes; zone creation; new features |

---

## 1. Objective

Re-implement the operator interface to match the approved mockups exactly: one status vocabulary,
one progress model, the Design System's wizard anatomy, layered surfaces, professional copy, and
the corrected brand treatment. The backend (184 tests, merged to `main`) is not touched.

## 2. Workstream A — foundation components (build once, reuse everywhere)

Each component's contract is defined by the mockups; no invention during implementation.

| Component | Replaces | Definition of done |
|---|---|---|
| `AppHeader` | current sidebar brand block | HPE Element top-left + service name; run identity, mode, run status right-aligned. GreenLake badge removed. |
| `StepRail` | flat numbered list in `App.tsx` | Steps grouped by lifecycle stage (Prepare / Initialize / Provision / Document); per-step status indicator; one-line result hint; current-step marker. Driven by the served registry. |
| `WizardBar` | — (new) | Sticky; Previous step (left, hidden on first step), Cancel run (right). Cancel opens the double-confirmation layer. |
| `PageIdentifier` | ad-hoc `Heading` per step | "Step X of Y", title, description, status indicator. X of Y computed from the built step list. |
| `StatusIndicator` | `StatusTag` + ~43 ad-hoc `Notification`s | The five states (Not started / Running / Action required / Complete / Failed) rendered as colour + icon + shape + text (WCAG 3-of-4). Single source for icons. |
| `InlineNotification` | per-step `Notification` usage | Four severities on status-tint surfaces; the "Action required" operator-gate variant with instruction copy. |
| `WizardFooter` | per-step button rows | Context note left; secondary + primary actions far right; consistent width across steps. |
| `useStepState(run, events, stepKey)` | 6 divergent status derivations, 2 progress models | One hook mapping run status + step events to the five-state vocabulary. Ends the `run.status`-vs-event-derived split (Verify/As-built steps included). |
| `CredentialsFields` | duplicated forms in Verify + As-built | Username/password fields with the "used for this operation only; never stored" help text. |
| `ActivityTimeline` | `EventLog` + 8 hand-rolled filters | Phase-filtered timeline with status-coloured markers and tabular timestamps. |
| Theme pass | ~16 hard-coded pixel widths, 3 concurrent spinners | T-shirt sizing throughout; `text.medium` body with 30em reading width; at most one spinner per screen; skeletons for loading states. |

## 3. Workstream B — screen migrations

Screens are migrated one per commit, lowest-risk first, each rebuilt on the Workstream A
components to match its mockup. Order:

1. Prerequisites  2. Initialisation sheet  3. Mode (Selector pattern)  4. Verify configuration
5. As-built document  6. Finish  7. GreenLake registration  8. Cloud Connectivity (operator gate)
9. DSCC setup (operator gate)  10. Discovery  11. SAN zoning  12. Provisioning builder
13. Provisioning plan & create

Rationale: 1–6 are forms/read-only views (low risk); 7–9 carry the gate pattern; 10–13 are the
data-dense screens and land last, on proven components.

## 4. Workstream C — terminology

Applied with each screen migration; the authoritative glossary is the mockup copy. Key renames:

| Current | Approved |
|---|---|
| Needs you / waiting for operator | **Action required** |
| Verify config & health | **Verify configuration** (the Design System prohibits "health" in UI copy) |
| Done | **Complete** |
| differs / difference | **Mismatch / discrepancy** |
| Confirm & create | **Create storage objects** |
| Start over | **Cancel run** (with double confirmation: Keep run / Discard run) |
| ad-hoc button labels | verb + noun throughout (Re-run discovery, Confirm submission, Regenerate, Dry run) |

The `init-only` build profile's relabelling ("Initialization") is preserved.

## 5. Verification and acceptance

- **Per commit:** `tsc --noEmit` and `vite build` pass; backend suite untouched and green (no
  backend files modified in this phase).
- **API contract:** no endpoint, schema, or event-type changes. `useStepState` consumes existing
  statuses and events only.
- **Final acceptance:** one scripted manual pass per mode (Full onboarding / Provision only /
  Both / Verify only / Custom), walking every screen against its mockup — layout, status
  transitions, gate banners, copy. The checklist will be committed as `docs/ux/CHECKLIST.md`
  and executed once, per ADR 0011.
- **Accessibility spot-checks:** focus ring visible on all interactive elements; heading levels
  sequential; status never conveyed by colour alone; spinner announcements present.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Grommet parity with mockups (sticky wizard bar, table summary footer) | Mockups use only patterns Grommet/`grommet-theme-hpe` support; any true gap is resolved toward the Design System, recorded in UX-GUIDELINES.md. |
| Typeface (site prescribes HPE Graphik; installed theme still ships Metric) | Take the font from the theme package; do not hardcode. Revisit when the theme updates. |
| Regression without frontend tests | Accepted in ADR 0011: small commits, `tsc`/build gates, single final manual pass. |
| Copy drift during implementation | Mockup text is copied verbatim, not retyped from memory. |

## 7. Approval gates

1. Mockup review (all 15 screens, including States & patterns and the Design spec) — **pending**.
2. This plan — **pending**.
3. Implementation begins only after both are approved; any change requested in review is applied
   to the mockups first, then this plan, then code.
