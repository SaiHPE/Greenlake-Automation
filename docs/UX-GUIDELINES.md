# UX guidelines: what the HPE Design System requires of this app

Second extraction, 2026-10-13. Source: the Design System's own documentation source
(github.com/grommet/hpe-design-system, `apps/docs/src/pages`: 20 foundation pages, 25 templates,
49 component pages, 11 design-token pages, plus the example code the pages render), and the HPE
Brand Central plugin references (`colour.md`, `typography.md`, `voice-and-tone.md`,
`design-system.md`). The first extraction (2026-07-25, a browser read of design-system.hpe.design)
is in git history at e3d662e6. Rules below are the Design System's. **Our call** lines record
where this app knowingly differs and why. Draft 3 of the redesign mockups (`frontend/mockups`,
BL-43) implements these.

## 1. Brand and identity

- The HPE element (the green rectangle) sits top left, always with the company and product name.
  Product names exactly as HPE publishes them: **HPE Alletra Storage MP**. Never pluralised or
  possessive. "HPE" is the company.
- An app outside the HPE GreenLake shell uses an **app header**: brand element plus
  application name on the left, linking to the app's landing page; navigation and account
  actions on the right. The HPE GreenLake badge is retired.
- Brand Central's palette is for Office and print. **Web and app UI use the Design System
  tokens only**; never blend the two.
- Font: the theme's (HPE Graphik on the web; the installed theme still says Metric). Take it from
  the theme, never hardcode.

## 2. Colour

- Semantic tokens only: `background.*`, `text.*`, `icon.*`, `border.*`. Names say target, role,
  state and scale (`color.background.selected.primary`). No hex in app code.
- Colour pairing is a rule: text and icons on a `strong`/`xstrong` background use the `onStrong`
  variants; on a status background use that status's `on` variant.
- Status colours (`ok`, `warning`, `critical`, `info`, `unknown`) are for status and nothing else.
  Never colour alone: pair with icon and words.
- Pick **Basic** or **Layered** backgrounds and use it app wide. Layered: page on
  `background-back`, surfaces on `background-front`, a fixed header on `background-front`;
  `background-contrast` for a secondary panel or a wizard bar.
  - **Our call: Layered.** Borders (`border-weak`) only where a surface boundary is otherwise
    ambiguous.
- Interaction states (hover, focus, active) come from the tokens. If two application states apply
  (readonly and selected), style by the higher one.

## 3. Typography

- rem units; all values from the type scale, never mixed (a `large` size with a `small` line height
  is wrong).
- **One h1 per page**; h2 for sections; h3 for subsections; needing h4 to h6 means the page should be
  split. No skipped levels. **Level and size are independent**: pick the level for structure, then
  the size token for the look; never demote a heading to make it smaller.
- Paragraphs keep their `maxWidth` (about 80 characters) for readability.
- Sentence case everywhere: titles, headings, buttons, labels. Tabs are the one exception (Title
  Case, one or two words).
  - **Our call:** step titles are h1 at the `small` size (1.75rem) and section titles h2/h3 at a
    small size taken from the text scale; the theme's h2 (1.5rem) is too large inside a step.

## 4. Status, state and notifications

- A **status indicator** has four elements: colour, icon, shape, words. **At least three must be
  present** (WCAG 2.1). Icons `size="small"` in tables and lists.
- **State** is the stage of a process; **status** is its condition. **Never write "health" in the
  UI; write "status".** In tables, status and state are separate columns unless they are one to one.
- **Inline notification**: next to the content it is about. Page level: directly under the page
  header, same width as it. Section level: above that section or above the action it concerns
  (form errors above the submit button). Status icon + optional title (page summaries only) +
  message + up to two links + close (never on critical). **No buttons inside.** Not sticky.
  Messages wrap, never truncate. Statuses: normal, warning, critical, info, unknown.
- **Toast**: low attention, no action needed, one at a time, 8 seconds, three lines, no links or
  buttons, never for "in progress", never while a modal or wizard is open. Not a primary channel.
- **Global notification**: directly under the global header, system conditions only (outage,
  expiring subscription), one at a time, 192 characters, critical ones not dismissible.
- **Busy button** (`busy` then `success`) only for actions of a couple of seconds. Longer work:
  show progress elsewhere and let the user leave; notify when done. **Spinner** for anything over
  about 300 ms, **one per page**, with `message={{ start, end }}` for screen readers. **Skeleton**
  only while fetching content, never for an operation that will succeed or fail.
- **Empty state** (no data yet, nothing matched, or an error stopped the load): heading (required,
  at the heading level of its place), description (medium text), icon (optional, `xlarge`), at most
  two actions and two links. Placed top left in HPE cloud services, or centred, or in the content
  area. Error empty states use the alert icon and warning colour, no blame, no jargon.
- Content: words the user knows, no internal jargon, no run-on sentences, "please" rarely, "Error"
  only for screen readers.

## 5. Buttons and labels

- **Primary**: the key action on the page, **once**. Most pages are for looking, not acting; many
  have no primary at all. **Secondary**: a call to action that supports the primary or stands alone,
  never navigation. **Default**: everything else, the majority. **Toolbar** (`kind="toolbar"`): when
  a button sits in a row with search, filter and an actions menu.
- **Cancel is always a default button**, never emphasised.
- **Alignment**: wizards, confirmation and dialog modals and notifications are **right-aligned**;
  side drawers, forms and filters are **left-aligned**. Right-aligned sets read default, secondary,
  **primary at the outer edge**. Left-aligned sets start with the primary.
- **No disabled buttons to gate a step.** Leave the button active and say, on click, what is still
  missing. A button that does not apply is not shown at all.
- Labels: **verb + noun** for the primary ("Apply filters", "Create run"); later buttons may drop
  the noun ("Reset"). The label matches the destination or the result. No contractions, no
  colloquialisms. "Add" associates an existing object; "New" opens a blank template; "Create"
  submits and makes the object. Icon-only buttons carry an `a11yTitle`; toggle buttons show the
  current state in the icon and say what the click does.
- Buttons act on the same page; **anchors navigate**. On `small` and `xsmall` screens buttons fill
  the width and groups stack; labels never wrap, truncate or shrink.

## 6. The wizard (our steps)

Anatomy from the Design System template and its example code:

- **Wizard header**, full width, `background-contrast`: **previous step** button on the left
  (LinkPrevious icon plus the previous step's title; on all steps but the first), the **wizard
  title** in the middle, **Cancel** on the right (Close icon, `reverse`). Cancel opens a
  **double confirmation** (centre Layer: h2, the wizard title, one sentence on what is lost,
  right-aligned "No, stay" (secondary) then "Yes, exit" (primary)).
- **Step identifier**: `Step X of Y` (text), the step title as **h1**, one paragraph.
- **Content** in one column, or two when guidance is needed: the guidance column is a
  `background-contrast` panel, `round="medium"`, width between `xsmall` and `medium`, top aligned.
- **Step footer**: `Footer`, top border, `justify="end"`, the one primary **Next**/**Finish** at
  the far right. Footer width constant across steps so the button never moves.
- Validate within the step before advancing. `Page kind="narrow"` for a wizard.
- Review step: a `NameValueList` showing **every** pair, empty ones as `--` with
  `a11yTitle="No value"`.

**Our calls** (kept from draft 2, now documented against the template):

- **Not a modal and not narrow.** The wizard is the whole app; a run's steps carry tables that
  need the width. The rail on the left is ours: the steps are operator-gated, revisitable and
  chosen by mode, and the rail is the only place that shows which steps a run has and where it
  stands. We keep `Step X of Y` so the Design System's progress cue is still met.
- The wizard title is the flow: "Provision, then replicate on AlletraMP_D22U27", or "Prepare a run"
  before a run exists. Cancel reads "Cancel run" (or "Start over" before a run) so it cannot be
  read as "cancel this click".
- Other footer actions sit left of the primary, right-aligned as the Design System orders them.
  A tick the operator must give before the primary sits in the footer next to the button; pressing
  the button before the tick shows a warning notification above the footer saying so.
- The guidance panel can be hidden ("About this step" brings it back); below `large` it folds
  under the title.

## 7. Pages that are not steps

- **PageHeader**: title always **h1**, unique under its parent, sentence case, left-aligned, wraps.
  Subtitle optional, one line of high-priority metadata only (no dumping page metadata there).
  **Parent link** (ascending navigation, LinkPrevious icon, the parent's exact name) **required on
  every child page, forbidden on top-level pages**; one per page. **Page-level actions
  right-aligned**, verb + noun, never table or list CRUD (those go in a toolbar above the data);
  actions collapse into an overflow menu as width shrinks, the primary never does.
- `Page` kinds: **wide** (1536px max; dashboards, tables, lists), **narrow** (768px; wizards,
  forms, settings), **full** (charts, maps). Minimum content width 336px. Page padding by
  breakpoint: 12 / 24 / 24 / 48 / 48 px (xsmall to xlarge).
- Breakpoints: xsmall ≤576, small 577–768, medium 769–1080, large 1081–1439, xlarge ≥1440.
- Dashboards: abbreviated numbers, less detail, fewer colours, fewer larger items.
  - **Our pages:** Home (top level, no parent; primary "Start a new run"), Run overview (parent
    "Your runs"; primary "Continue at <step>"), Done (parent "Your runs"; primary "Download the
    hand-over package", default "Start another run on this array").

## 8. Lists, tables, cards, name-value lists

- **List** when scanning matters or space is short, or when the item can be chosen from the list
  content alone; **DataTable** for finding, narrowing, browsing or assembling records. Lists are
  easier to navigate than tables; prefer them for simple sets.
- List rows: consistent layout, icon or image to aid scanning, dividers or enough space, logical
  order, **wrap rather than truncate** (long names must stay tellable apart). Either the whole row is
  selectable or it holds clickable controls, never both. An action menu per row only when the action
  is simple and its result is visible in the row. Long lists: sticky header, one scrollbar, search
  and filter, avoid pagination. Each list has an `aria-label` saying what and how many.
- DataTable: controls in a toolbar above (search, filter, Manage columns, then the Actions menu
  right-aligned); let the data set the height; about 20 records a page; numeric columns
  `align: 'end'`; never truncate headings, numbers or statuses; truncated text gets a tip; empty
  cell `--` with `a11yTitle="No value"`; status cells are icon + colour + words.
- **Card**: contained, independent, individual, summarised. For scannable summaries you drill
  into, not a generic section wrapper. Left-aligned text, real heading for the title, hover only
  when the whole card is one action, groups of cards are lists (`ul`/`li`).
- **NameValueList** for metadata: names bold or values bold, never both; name never larger than
  value; names `small` width, values `medium`; a heading groups several lists; empty pairs shown on
  review and edit screens, omitted on public profiles.
- **Selector** (a card that is the choice): container, round indicator for single choice, title
  required, description optional, **nothing interactive inside** (one control per option; Space or
  Enter selects).
- **Collapsible child object** (our sections): the whole header is the control (click, Enter,
  Space), the label is a heading, FormDown closed / FormUp open, summary may truncate, top and
  bottom `border-weak`, aria-label "Show detail" / "Hide detail".

## 9. Forms, dialogs, popovers

- Ask only what is needed; defaults filled; progressive disclosure; sentence-case labels; helpful
  placeholder that is not the label; required marked with an asterisk the colour of the label (not
  red; none on sign-in forms); errors inline in red, a summary notification above the submit button;
  encode input; no restrictions on names (spaces, punctuation, unicode allowed).
- Form buttons bottom left; wizard buttons footer right.
- **Double confirmation** for any layer with unsaved changes or an irreversible action: title
  states what is discarded, subtitle clarifies, footer right-aligned "Cancel" then the primary;
  click-outside dismissal only when nothing can be lost.
- Layer titles are h2; the primary verb matches the title verb; side drawer
  `position="right" full="vertical"`; announce open and close.
- Popover for optional contextual help only (icon-only trigger with `a11yTitle`, small text, no
  crucial content, Esc closes, focus trapped).
- Menus hold actions, never value selection; group with dividers, most frequent first, the
  destructive action alone at the end with a double confirmation.
- Code blocks: keyboard reachable (`tabIndex=0`), long lines wrap, vertical scroll inside the block
  if long, no horizontal scroll.

## 10. Layout and spacing

- **T-shirt tokens only**: sizes (`xxsmall` 48 … `xlarge` 1152, `xxlarge` 1536), spacing
  (`xxsmall` 3, `xsmall` 6, `small` 12, `medium` 24, `large` 48, `xlarge` 96), radii, borders.
  No ad-hoc pixels. Tokens step down one size at the `small` breakpoint.
- Base scale 24/16. Grid for layouts: container-driven (page regions, fixed/flex/fluid columns)
  or content-driven (dialogs sized by their content); nested grids for complex regions. Order
  content by priority so it reads right at every width and in a screen reader.
- Omit the `size` prop when it is medium.

## 11. Date and time

- Store UTC, show the user's locale formatting. Relative times for recent events ("Just now", "5
  min ago", "Today, 19:31"), absolute with timezone when precision matters, both in notifications.
- Right-align relative times in a column; zero-pad in lists; abbreviate consistently.

## 12. Icons

- Semantic names; **abstract icons always with a label**; if an icon always needs the label, use the
  words alone. Status icons are reserved for status. Icon height matches the text size. Decorative
  icons `aria-hidden`; meaningful ones carry an `a11yTitle`.

## 13. Voice and tone

- Active, positive, objective, fact-based, plain English at about a US grade-7 reading level.
  "You" for the reader, "we" for HPE. Present tense. Short sentences, one idea each. Specific
  rather than vague; no "thus" or "hence"; no hype words; US spelling for global material.
- Empty states and failures say what is missing or what stopped, why, and the way out.
- Design says *how*; content says *why*. Headings front-load the meaning in the first three words.
  - **Our call:** the product's own term "Initialisation sheet" keeps its spelling.

## 14. Accessibility

- Status never by colour alone. Headings in order. Every input in a `FormField` with `htmlFor`
  and `name`. Tab order logical; no arrow keys needed to reach things. Spinners and modal layers
  announce themselves. Lists and navigation regions labelled. Focus ring from the theme
  (`#292d3a` light). Nothing interactive nested inside something interactive.
