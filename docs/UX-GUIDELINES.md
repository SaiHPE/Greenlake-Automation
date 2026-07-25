# UX guidelines — what the HPE Design System requires of this app

Scraped from **design-system.hpe.design** (2026-07-25, client-rendered SPA — read via a real browser)
and cross-checked against the **`hpe-design-tokens`** package the frontend already installs. This is
the reference the Phase-3 redesign implements against (ADR 0011). Rules below are the design
system's; **Our call** lines record where we deliberately diverge and why.

## 1. Brand & identity

- **The HPE GreenLake badge is RETIRED** — the DS says it "should not be added to any new material"
  pending the GreenLake rebrand. **Our current header shows an "HPE GreenLake" lockup — it must go.**
- Use the **HPE element** (the green rectangle, `grommet-icons`/`@hpe-design/icons-grommet` `Hpe`)
  plus the service name. HPE green = the **`decorative.brand`** token (`#01a982`) and is for the brand
  mark — *not* for primary buttons.
- **Font: HPE Graphik** (Light / Regular / Medium / Semibold / Bold). Note: the installed
  `hpe-design-tokens` still emits `'Metric', Arial, sans-serif` — the theme package is a version
  behind the site's guidance. Take the font from the theme; don't hardcode.

## 2. Color

- Never use raw hex — use **semantic tokens** (`color.background.*`, `color.text.*`, `color.icon.*`,
  `color.border.*`). Semantic names say *when/where* to apply.
- **Color pairing is a hard rule:** a role background pairs with its `on[Role]` text/icon
  (`background-critical` → `text-onCritical`); any `strong` background pairs with `onStrong`.
  Primary buttons are `background.primary-strong` (`#008567`) + `text.onPrimaryStrong`.
- **Pick Basic or Layered backgrounds and use it app-wide** — never mix per page.
  Philosophy: *"distinguish content sections with color, avoid excessive borders"*; prefer contrast
  backgrounds over borders in dense layouts to cut visual noise.
  - **Our call: Layered** (`background-back` app → `background-front` surfaces), borders only where
    a surface boundary is genuinely ambiguous.

## 3. Status — the rule that shapes this whole app

- A status indicator is built from four elements — **color, icon, shape, content** — and
  **at least three of the four must be present** to meet WCAG 2.1. Color alone is never enough.
- **Never write "health" in the UI. Always "status."** (DS: users don't share our internal
  vocabulary.) **Our step "Verify config & health" must be relabelled.**
- Distinguish **state** (the stage of a process) from **status** (the condition of that state).
- Status content: familiar words not internal jargon, short, no run-on sentences, don't lean on
  "please".

## 4. Notifications

- **Inline** — near the content it relates to; for feedback on a user's action and significant task
  status updates. **This is our per-step pattern** (the operator gate, step results).
- **Global** — top-of-interface, system-generated, high attention (outage, expiring subscription).
  Critical global notifications are **not dismissible**. Not for task completion.
- **Toast** — low-severity, no action needed, temporary.
- Anatomy: status icon + message + optional anchor to detail + close (except critical).

## 5. Wizard (our app *is* one)

DS anatomy:
- **Wizard header**, full width and **sticky**: wizard title; **Previous step** button on the left
  (all steps except the first); **Cancel** on the right.
- **Step identifier**: step title (required), **"Step X of Y"** summary, optional step description.
- **Step footer**: the **primary Next/Finish button, aligned far right**; footer width consistent
  across steps so the button never moves.
- **Cancel opens a double-confirmation modal.**
- Validation happens **within each step**, before advancing.
- DS says a wizard "should always appear as a fullscreen modal".

**Our calls (deliberate divergences, documented so they aren't mistaken for drift):**
- **Not a modal** — the wizard *is* the whole application; there is no page behind it to return to.
- **Keep the step rail.** DS's linear wizard assumes forward-only progress; our steps are
  operator-gated, revisitable and mode-selected, and the rail is the only affordance showing which
  steps a mode includes and where the run stands. We **add "Step X of Y"** so DS progress guidance is
  still met, and group rail items by lifecycle stage.
- **Cancel = "Start over"**, which discards a run → it gets the DS double confirmation.

## 6. Buttons & labels

- Label with **verb + noun** ("Apply filters", "Create device"). Never generic ("Yes", "OK", "Submit"
  where a specific verb exists). The label must match what happens.
- **Add / New / Create are not synonyms:** *Add* associates an existing object; *New* opens a blank
  template; **Create** submits input and creates the object instance. (Our provisioning apply is a
  **Create**.)
- Double-confirmation dialogs: title leads with the action ("Discard *Add application*?"), footer
  actions right-aligned with the primary on the right, and the button verb matches the title.
- Forms place submit/cancel at the **bottom left of the form**; a **wizard's** primary action goes
  **far right in the wizard footer**. (Ours is a wizard.)

## 7. Layout

- Building blocks: **App container → Global header/footer → Page → PageContent**. `Page` sets max
  width/padding/alignment; kinds are **wide / narrow / full**.
- Breakpoints: xsmall ≤576 · small 577–768 · medium 769–1080 · large 1081–1439 · xlarge ≥1440.
- Use **t-shirt tokens** for container sizes, radii, border widths and spacing — **no ad-hoc pixel
  widths**. (Our current UI hard-codes ~16 px widths — all must go.)

## 8. Components

- **DataTable**: controls (search/filter/actions) live **above** the table; concise column headers;
  optional **footer for summary counts/aggregations**. Use it for all tabular data — never hand-built
  rows.
- **Card**: *contained, independent, individual, summarized* — for at-a-glance summary content. Not a
  generic section wrapper; plain surfaces are correct for step content.
- **Tag**: metadata for identify/organize/filter — **not** a status display. Highlight tags are only
  for temporary notes ("New").
- **Spinner**: only for waits >~300 ms, and **avoid multiple spinners on one page** (ours currently
  renders up to three).
- **Icons**: semantic names; pair abstract icons with labels; if an icon always needs a label, use
  text alone. Library is moving to `@hpe-design/icons-grommet`.

## 9. Voice & tone

- Values: open, courageous, inspired. Content is **active, positive, objective, fact-based, plain
  English**, at roughly a **US grade-7 reading level**; sentence case.
- Design says *how*; content says *why*. Keep messages short; no jargon, no run-ons.
- Empty states must say what's missing, why, and the way forward.

## 10. Accessibility

- Status never by color alone (§3). Correct semantic heading order (no level skipping — style with
  heading tokens, not by picking a bigger heading level). Spinners announce start/end to screen
  readers. Focus ring: `#004233`, 2 px, 2 px offset.
