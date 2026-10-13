/**
 * The proposed app shell and its building blocks, for the redesign mockups only. Nothing here is
 * used by the app; when a mockup is agreed, these become the real components.
 *
 * Draft 3 follows the HPE Design System as published in its docs source (design-system.hpe.design,
 * repo grommet/hpe-design-system): the wizard template (header, step identifier, footer, cancellation
 * layer), PageHeader for the pages that are not steps, inline Notification for the one line of status,
 * semantic headings, right-aligned footer actions with one primary, no disabled gate buttons, empty
 * states instead of grey notes, t-shirt sizes only. docs/UX-GUIDELINES.md lists the rules and the few
 * places we knowingly differ.
 */
import {
  Box,
  Button,
  CheckBox,
  Collapsible,
  Footer,
  Header,
  Heading,
  Layer,
  Menu,
  Nav,
  Notification,
  PageHeader,
  Paragraph,
  ResponsiveContext,
  Spinner,
  Text,
} from 'grommet';
import { Apps, Clock, Close, FormDown, FormUp, LinkPrevious, Radial, Terminal, Time } from 'grommet-icons';
import { createContext, ReactNode, useContext, useState } from 'react';
import { HpeElement } from '../src/ui/AppChrome';
import { StatusIcon, StepState } from '../src/ui/status';

/**
 * The step vocabulary plus one word the app lacks today: `waiting`, for a step that waits on someone
 * else (the SAN team applying zones, the network team opening a port). It is drawn calm and grey, with a
 * clock: not the operator's problem right now, unlike orange `action_required`.
 */
export type RunState = StepState | 'waiting';

export function StateIcon({ state, size = 'small' }: { state: RunState; size?: string }) {
  if (state === 'waiting') return <Clock size={size} color="icon-weak" a11yTitle="Waiting on others" />;
  if (state === 'not_started') return <Radial size={size} color="icon-weak" a11yTitle="Not started" />;
  return <StatusIcon state={state} size={size} />;
}

/** Status indicator: icon (shape) + colour + words. The Design System asks for three of the four. */
export function StateLabel({ state, label, size = 'small' }: { state: RunState; label: string; size?: 'small' | 'medium' }) {
  return (
    <Box direction="row" gap="xsmall" align="center" flex={false}>
      <StateIcon state={state} size={size} />
      <Text size={size} weight={500}>{label}</Text>
    </Box>
  );
}

// ------------------------------------------------------------------ note markers

export const NotesContext = createContext(false);

/** A numbered marker that ties a spot on the screen to note N in the side panel. */
export function Mark({ n }: { n: number }) {
  if (!useContext(NotesContext)) return null;
  return (
    <Box
      as="span"
      round="full"
      background="decorative-purple"
      pad={{ horizontal: 'xsmall' }}
      align="center"
      justify="center"
      flex={false}
      aria-label={`Note ${n}`}
      margin={{ left: 'xsmall' }}
      style={{ display: 'inline-flex', verticalAlign: 'middle', minWidth: '1.4em', lineHeight: '1.4em' }}
    >
      <Text size="xsmall" weight="bold" color="text-onStrong">{n}</Text>
    </Box>
  );
}

// ------------------------------------------------------------------ the frame

export interface RailStep {
  key: string;
  label: string;
  state: RunState;
  result?: string;
}
export interface RailGroup {
  stage: string;
  steps: RailStep[];
}
export interface RunSummary {
  array: string;
  serial: string;
  mode: string;
  state: RunState;
  stateLabel: string;
}

export function StepIcon({ state }: { state: RunState }) {
  return <StateIcon state={state} />;
}

/** What the frame knows and the step page needs: the run, and the step before this one. */
const FrameContext = createContext<{ run?: RunSummary; previous?: RailStep }>({});

function RailRow({ step, current, onSelect, icon }: { step: RailStep; current: boolean; onSelect?: () => void; icon?: ReactNode }) {
  return (
    <Box
      direction="row"
      gap="small"
      align="start"
      pad={{ vertical: 'xsmall', horizontal: 'small' }}
      round="xsmall"
      background={current ? 'background-selected-primary' : undefined}
      onClick={onSelect}
      hoverIndicator={onSelect ? 'background-hover' : undefined}
      aria-current={current ? 'step' : undefined}
      flex={false}
    >
      <Box pad={{ top: 'xxsmall' }} flex={false}>
        {icon ?? <StepIcon state={step.state} />}
      </Box>
      <Box>
        <Text size="small" weight={current ? 'bold' : 500} color={step.state === 'not_started' && !current ? 'text-weak' : 'text-strong'}>
          {step.label}
        </Text>
        {step.result && <Text size="xsmall" color="text-weak">{step.result}</Text>}
      </Box>
    </Box>
  );
}

/**
 * App header (Design System "app header": brand element + application name on the left, linking
 * home) over an optional step rail and the page. The rail is ours, not the Design System's: the
 * steps are operator-gated and revisitable, and the rail is the only place that shows which steps
 * the chosen mode includes.
 */
export function AppFrame({
  run,
  groups,
  current = '',
  onSelect,
  railNote,
  right,
  children,
}: {
  run?: RunSummary;
  groups?: RailGroup[];
  current?: string;
  onSelect?: (key: string) => void;
  railNote?: string;
  right?: ReactNode;
  children: ReactNode;
}) {
  const size = useContext(ResponsiveContext);
  const narrow = size === 'small' || size === 'xsmall';
  const flat = (groups ?? []).flatMap((g) => g.steps);
  const at = flat.findIndex((s) => s.key === current);
  const previous = at > 0 ? flat[at - 1] : undefined;
  return (
    <FrameContext.Provider value={{ run, previous }}>
      <Box fill background="background-back">
        <Header
          pad={{ horizontal: 'medium', vertical: 'small' }}
          background="background-front"
          border={{ side: 'bottom', color: 'border-weak' }}
          flex={false}
        >
          <Button plain a11yTitle="HPE Alletra Storage MP onboarding: go to your runs" onClick={() => undefined}>
            <Box direction="row" gap="small" align="center">
              <HpeElement width={36} />
              <Box direction="row" gap="xsmall" align="baseline" wrap>
                <Text weight="bold" color="text-strong">HPE Alletra Storage MP</Text>
                <Text color="text-strong">onboarding</Text>
              </Box>
            </Box>
          </Button>
          <Box direction="row" gap="medium" align="center">
            {run && (
              <Box direction="row" gap="small" align="center">
                <Text size="small" weight="bold" color="text-strong">{run.array}</Text>
                <Text size="small" color="text-weak">{run.serial} · {run.mode}</Text>
                <StateLabel state={run.state} label={run.stateLabel} />
              </Box>
            )}
            {right}
            <Menu label="Runs" items={[{ label: 'All runs' }, { label: 'Start a new run' }]} dropAlign={{ top: 'bottom', right: 'right' }} />
          </Box>
        </Header>
        <Box direction="row" flex overflow="hidden">
          {groups && !narrow && (
            <Nav
              aria-label="Steps of this run"
              width={{ min: 'small', max: 'medium' }}
              basis="1/6"
              flex={false}
              background="background-front"
              border={{ side: 'right', color: 'border-weak' }}
              pad={{ vertical: 'small', horizontal: 'xsmall' }}
              overflow="auto"
              gap="small"
            >
              {run && (
                <RailRow
                  step={{ key: 'overview', label: 'Run overview', state: 'complete', result: 'Every step on one page' }}
                  icon={<Apps size="small" />}
                  current={current === 'overview'}
                  onSelect={onSelect ? () => onSelect('overview') : undefined}
                />
              )}
              {groups.map((g) => (
                <Box key={g.stage} gap="xxsmall" flex={false}>
                  <Text size="small" weight={500} color="text-weak" margin={{ left: 'small', top: 'xsmall' }}>
                    {g.stage}
                  </Text>
                  {g.steps.map((s) => (
                    <RailRow key={s.key} step={s} current={s.key === current} onSelect={onSelect ? () => onSelect(s.key) : undefined} />
                  ))}
                </Box>
              ))}
              {railNote && (
                <Box pad="small" margin={{ top: 'xsmall' }} background="background-contrast" round="xsmall" flex={false}>
                  <Text size="xsmall" color="text-weak">{railNote}</Text>
                </Box>
              )}
            </Nav>
          )}
          <Box flex overflow="hidden">{children}</Box>
        </Box>
      </Box>
    </FrameContext.Provider>
  );
}

// ------------------------------------------------------------------ pages that are not steps

/**
 * Home, the run overview and the hand-over page use the Design System PageHeader: h1 title, optional
 * subtitle, a link to the parent page on child pages only, page-level actions right-aligned. Buttons
 * that act on the page go here; buttons that act on a table go next to that table.
 */
export function PlainPage({
  title,
  subtitle,
  parent,
  actions,
  children,
}: {
  title: string;
  subtitle?: string | JSX.Element;
  parent?: { label: string; onClick?: () => void };
  actions?: JSX.Element;
  children: ReactNode;
}) {
  return (
    <Box fill overflow="auto">
      <Box pad={{ horizontal: 'large', bottom: 'large' }} flex={false} gap="medium">
        <PageHeader
          title={title}
          subtitle={subtitle}
          parent={parent ? <Button plain label={parent.label} icon={<LinkPrevious />} onClick={parent.onClick} /> : undefined}
          actions={actions}
          size="small"
          pad={{ vertical: 'medium' }}
        />
        {children}
      </Box>
    </Box>
  );
}

// ------------------------------------------------------------------ one step page

/**
 * A footer action. No `disabled`: the Design System says not to gate a step with a greyed button but
 * to leave it active and say, on click, what is still missing. `blocked` is that sentence.
 */
export interface Action {
  label: string;
  onClick?: () => void;
  busy?: boolean;
  blocked?: string;
  /** A call to action that supports the primary. Everything else is a default button. */
  secondary?: boolean;
}

/** A tick the operator must give before the primary action runs; it sits in the footer next to the button. */
export interface Confirmation {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

/** The Design System's double confirmation before leaving a wizard with work in it. */
function CancelLayer({ title, run, onClose }: { title: string; run: boolean; onClose: () => void }) {
  return (
    <Layer position="center" onClickOutside={onClose} onEsc={onClose}>
      <Box pad="large" gap="medium" width="large">
        <Box gap="xxsmall">
          <Heading level={2} margin="none" size="small">{run ? 'Cancel this run?' : 'Start over?'}</Heading>
          <Text color="text-strong">{title}</Text>
        </Box>
        <Text>
          {run
            ? 'The run and its results stay in your runs, marked cancelled. Nothing is changed on the array, vCenter or the switches.'
            : 'The uploaded workbook and your choices on these three screens are forgotten.'}
        </Text>
        <Box as="footer" direction="row" gap="small" justify="end">
          <Button label="No, stay" secondary onClick={onClose} />
          <Button label={run ? 'Yes, cancel the run' : 'Yes, start over'} primary onClick={onClose} />
        </Box>
      </Box>
    </Layer>
  );
}

export function StepPage({
  stepLabel,
  first = false,
  runExists = true,
  title,
  description,
  state,
  stateLabel,
  primary,
  actions = [],
  confirmation,
  guidance,
  guideOpen: guideInitiallyOpen = true,
  top,
  activity,
  children,
}: {
  stepLabel?: string;
  first?: boolean;
  runExists?: boolean;
  title: string;
  description?: string;
  state?: RunState;
  stateLabel?: string;
  primary?: Action;
  actions?: Action[];
  confirmation?: Confirmation;
  guidance?: ReactNode;
  guideOpen?: boolean;
  top?: ReactNode;
  activity?: { last: string; events: number; commands: number };
  children: ReactNode;
}) {
  const size = useContext(ResponsiveContext);
  const { run, previous } = useContext(FrameContext);
  const stacked = size !== 'large' && size !== 'xlarge';
  const compact = size === 'small' || size === 'xsmall';
  const [showGuide, setShowGuide] = useState(false);
  const [guideOpen, setGuideOpen] = useState(guideInitiallyOpen);
  const [cancelling, setCancelling] = useState(false);
  const [blockedMessage, setBlockedMessage] = useState<string | undefined>();
  const flow = run ? `${run.mode} on ${run.array}` : 'Prepare a run';

  // what stops the primary right now: the untied confirmation first, then the action's own reason
  const primaryBlocked = confirmation && !confirmation.checked ? `Tick the box first: ${confirmation.label}` : primary?.blocked;
  const press = (a: Action, blocked = a.blocked) => () => {
    if (blocked) setBlockedMessage(blocked);
    else {
      setBlockedMessage(undefined);
      a.onClick?.();
    }
  };
  const shownMessage = blockedMessage && (blockedMessage === primaryBlocked || actions.some((a) => a.blocked === blockedMessage)) ? blockedMessage : undefined;

  return (
    <Box fill>
      {/* wizard header (Design System wizard template): previous step left, the flow in the middle, Cancel right */}
      <Header background="background-contrast" pad={{ horizontal: 'medium', vertical: 'xsmall' }} responsive={false} flex={false}>
        <Box direction="row" flex>
          {!first && previous && <Button icon={<LinkPrevious />} label={compact ? undefined : previous.label} a11yTitle={`Previous step: ${previous.label}`} size="small" />}
        </Box>
        <Text size="small" weight={500} color="text-strong" truncate>{flow}</Text>
        <Box direction="row" flex justify="end">
          <Button icon={<Close />} label={compact ? undefined : runExists ? 'Cancel run' : 'Start over'} reverse size="small" onClick={() => setCancelling(true)} />
        </Box>
      </Header>
      {cancelling && <CancelLayer title={flow} run={runExists} onClose={() => setCancelling(false)} />}

      <Box flex overflow="auto">
        <Box pad={{ horizontal: 'large', top: 'medium', bottom: 'large' }} flex={false} gap="medium">
          {/* step identifier: "Step X of Y", the h1, one paragraph */}
          <Box direction="row" justify="between" align="start" gap="medium" flex={false}>
            <Box gap="xxsmall">
              {stepLabel && <Text size="small" color="text-weak">{stepLabel}</Text>}
              <Heading level={1} size="small" margin="none">{title}</Heading>
              {description && <Paragraph margin="none">{description}</Paragraph>}
            </Box>
            {state && (
              <Box direction="row" gap="medium" align="center" flex={false} pad={{ top: stepLabel ? 'medium' : 'none' }}>
                {!stacked && guidance && !guideOpen && (
                  <Button size="small" label="About this step" onClick={() => setGuideOpen(true)} />
                )}
                <StateLabel state={state} label={stateLabel ?? ''} size="medium" />
              </Box>
            )}
          </Box>
          {stacked && guidance && (
            <Box flex={false}>
              <Button plain onClick={() => setShowGuide((v) => !v)} aria-expanded={showGuide}>
                <Box direction="row" gap="xsmall" align="center">
                  {showGuide ? <FormUp /> : <FormDown />}
                  <Text size="small" weight={500}>About this step</Text>
                </Box>
              </Button>
              <Collapsible open={showGuide}>
                <Box background="background-contrast" round="small" pad="medium" margin={{ top: 'small' }}>{guidance}</Box>
              </Collapsible>
            </Box>
          )}
          {top}
          <Box direction="row" gap="large" align="start" flex={false}>
            {/* screens pass Boxes, never fragments: Grommet's gap counts a fragment as one child */}
            <Box flex gap="medium" style={{ minWidth: 0 }}>{children}</Box>
            {!stacked && guidance && guideOpen && (
              <Box
                as="aside"
                aria-label="About this step"
                width={{ min: 'xsmall', max: 'medium' }}
                basis="1/3"
                flex={false}
                alignSelf="start"
                background="background-contrast"
                round="small"
                pad="medium"
                gap="medium"
              >
                <Box direction="row" justify="between" align="center">
                  <Text weight={500} color="text-strong">About this step</Text>
                  <Button size="small" label="Hide" onClick={() => setGuideOpen(false)} />
                </Box>
                {guidance}
              </Box>
            )}
          </Box>
        </Box>
      </Box>

      {(primary || actions.length > 0) && (
        <Box background="background-front" border={{ side: 'top', color: 'border-weak' }} flex={false}>
          {shownMessage && (
            <Box pad={{ horizontal: 'large', top: 'small' }}>
              <Notification status="warning" message={shownMessage} onClose={() => setBlockedMessage(undefined)} />
            </Box>
          )}
          {/* step footer: everything right-aligned, default buttons, then secondary, then the one primary */}
          <Footer justify="end" gap="small" pad={{ horizontal: 'large', vertical: 'small' }}>
            {confirmation && (
              <Box flex direction="row" justify="end">
                <CheckBox
                  checked={confirmation.checked}
                  onChange={(e) => { confirmation.onChange(e.target.checked); if (e.target.checked) setBlockedMessage(undefined); }}
                  label={<Text size="small">{confirmation.label}</Text>}
                />
              </Box>
            )}
            <Box direction="row" gap="small" flex={false} wrap justify="end">
              {[...actions].sort((a, b) => Number(!!a.secondary) - Number(!!b.secondary)).map((a) => (
                <Button key={a.label} secondary={a.secondary} label={a.label} onClick={press(a)} busy={a.busy} />
              ))}
              {primary && <Button primary label={primary.label} onClick={press(primary, primaryBlocked)} busy={primary.busy} />}
            </Box>
          </Footer>
        </Box>
      )}
      {activity && <ActivityBar {...activity} />}
    </Box>
  );
}

/** The activity list and the console, folded into one line at the bottom until asked for. */
export function ActivityBar({ last, events, commands }: { last: string; events: number; commands: number }) {
  return (
    <Box
      direction="row"
      justify="between"
      align="center"
      gap="small"
      pad={{ horizontal: 'large', vertical: 'xsmall' }}
      background="background-contrast"
      border={{ side: 'top', color: 'border-weak' }}
      flex={false}
    >
      <Box direction="row" gap="xsmall" align="center">
        <Time size="small" color="icon-weak" aria-hidden />
        <Text size="small" color="text-weak">{last}</Text>
      </Box>
      <Box direction="row" gap="small" flex={false}>
        <Button size="small" label={`Activity (${events})`} />
        <Button size="small" icon={<Terminal size="small" />} label={`Console (${commands} commands)`} />
      </Box>
    </Box>
  );
}

// ------------------------------------------------------------------ content blocks

const STATUS: Record<RunState, 'normal' | 'warning' | 'critical' | 'info' | 'unknown'> = {
  complete: 'normal',
  action_required: 'warning',
  failed: 'critical',
  running: 'info',
  not_started: 'unknown',
  waiting: 'unknown',
};

/**
 * One sentence saying what happened, as the Design System's inline notification, under the page
 * header. Status icon + colour + words. No buttons inside; up to two links.
 */
export function StatusLine({
  state,
  children,
  time,
  links,
}: {
  state: RunState;
  children: ReactNode;
  time?: string;
  links?: { label: string; onClick?: () => void }[];
}) {
  const icon =
    state === 'running' ? <Spinner size="xsmall" message={{ start: 'Working', end: 'Finished' }} /> : state === 'waiting' ? <Clock color="icon-weak" /> : undefined;
  return (
    <Box flex={false}>
      <Notification
        status={STATUS[state]}
        icon={icon}
        message={
          <Box direction="row" gap="medium" align="start" justify="between">
            <Text>{children}</Text>
            {time && <Text size="small" color="text-weak" style={{ whiteSpace: 'nowrap' }}>{time}</Text>}
          </Box>
        }
        actions={links?.map((l) => ({ label: l.label, onClick: l.onClick, href: l.onClick ? undefined : '#' }))}
      />
    </Box>
  );
}

/**
 * The Design System's empty state for a step that has not run: a heading that says the status, one
 * sentence on how to move on. The action is the footer's primary, so it is not repeated here.
 */
export function EmptyState({ icon, title, children }: { icon?: ReactNode; title: ReactNode; children?: ReactNode }) {
  return (
    <Box direction="row" gap="medium" align="start" pad={{ vertical: 'small' }} flex={false}>
      {icon && <Box flex={false}>{icon}</Box>}
      <Box gap="xsmall">
        <Heading level={2} size="small" margin="none">{title}</Heading>
        {children && <Paragraph margin="none">{children}</Paragraph>}
      </Box>
    </Box>
  );
}

/** A surface with a heading: the Design System separates sections by background, not by borders alone. */
export function Panel({ title, right, level = 2, children }: { title?: ReactNode; right?: ReactNode; level?: 2 | 3; children: ReactNode }) {
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
      {(title || right) && (
        <Box direction="row" justify="between" align="center" gap="small">
          {title && <Heading level={level} size="xsmall" weight={500} margin="none">{title}</Heading>}
          {right}
        </Box>
      )}
      {children}
    </Box>
  );
}

/**
 * A section that opens on demand, after the Design System's collapsible child object: the whole
 * header is the control, the label is a heading, FormDown closed and FormUp open, the summary may
 * truncate.
 */
export function Section({
  title,
  summary,
  right,
  level = 2,
  open: openInitially = false,
  children,
}: {
  title: ReactNode;
  summary?: ReactNode;
  right?: ReactNode;
  level?: 2 | 3;
  open?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(openInitially);
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
      <Box
        direction="row"
        gap="small"
        align="center"
        pad={{ horizontal: 'medium', vertical: 'xsmall' }}
        onClick={() => setOpen((v) => !v)}
        hoverIndicator="background-hover"
        round="small"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen((v) => !v); } }}
        aria-expanded={open}
        aria-label={open ? 'Hide detail' : 'Show detail'}
      >
        {open ? <FormUp /> : <FormDown />}
        <Box flex direction="row" gap="small" align="baseline" wrap>
          <Heading level={level} size="xsmall" weight={500} margin="none">{title}</Heading>
          {summary && <Text size="small" color="text-weak" truncate>{summary}</Text>}
        </Box>
        {right}
      </Box>
      <Collapsible open={open}>
        <Box pad={{ horizontal: 'medium', bottom: 'medium' }} gap="small">{children}</Box>
      </Collapsible>
    </Box>
  );
}

/** Finished parts of a step, one compact line each, with the part's own "do it again" on the right. */
export function DoneList({ items }: { items: { text: string; again?: string; detail?: ReactNode }[] }) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
      {items.map((it, i) => (
        <Box key={i} border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined}>
          <Box direction="row" gap="small" align="center" pad={{ horizontal: 'medium', vertical: 'xsmall' }}>
            <StatusIcon state="complete" />
            <Box flex direction="row" gap="small" align="center">
              <Text size="small" color="text-strong">{it.text}</Text>
              {it.detail && (
                <Button plain onClick={() => setOpen(open === i ? null : i)} aria-expanded={open === i}>
                  <Text size="small" color="text-anchor">{open === i ? 'Hide detail' : 'Show detail'}</Text>
                </Button>
              )}
            </Box>
            {it.again && <Button size="small" label={it.again} />}
          </Box>
          {it.detail && <Collapsible open={open === i}><Box pad={{ horizontal: 'medium', bottom: 'small' }}>{it.detail}</Box></Collapsible>}
        </Box>
      ))}
    </Box>
  );
}

/**
 * Files a run produces, as the Design System's list pattern: one row per file with its icon, name,
 * detail and action. Replaces rows of buttons, which wrap unevenly.
 */
export interface DocItem {
  icon: ReactNode;
  name: string;
  detail: string;
  action?: string;
  /** Not there yet: the row says so in words instead of showing a greyed button. */
  pending?: string;
}

export function DocList({ items }: { items: DocItem[] }) {
  return (
    <Box as="ul" margin="none" pad="none" background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
      {items.map((d, i) => (
        <Box
          as="li"
          key={d.name}
          direction="row"
          gap="small"
          align="center"
          pad={{ horizontal: 'medium', vertical: 'xsmall' }}
          border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined}
          style={{ listStyle: 'none' }}
        >
          <Box flex={false}>{d.icon}</Box>
          <Box flex>
            <Text size="small" weight={500} color={d.pending ? 'text-weak' : 'text-strong'}>{d.name}</Text>
            <Text size="xsmall" color="text-weak">{d.detail}</Text>
          </Box>
          {d.pending ? <Text size="small" color="text-weak">{d.pending}</Text> : <Button size="small" label={d.action ?? 'Download'} />}
        </Box>
      ))}
    </Box>
  );
}

/** Right-hand guidance: the explanations that used to fill the page. */
export function Guidance({ items }: { items: { title: string; body: ReactNode }[] }) {
  return (
    <Box gap="medium" flex={false}>
      {items.map((g) => (
        <Box key={g.title} gap="xxsmall" flex={false}>
          <Heading level={2} size="xsmall" weight={500} margin="none">{g.title}</Heading>
          <Text size="small">{g.body}</Text>
        </Box>
      ))}
    </Box>
  );
}

/**
 * Commands to copy: the Design System's code block, reachable by keyboard, long lines wrapped
 * rather than scrolled sideways.
 */
export function CodeBlock({ lines, a11yTitle }: { lines: string[]; a11yTitle: string }) {
  return (
    <Box as="pre" tabIndex={0} aria-label={a11yTitle} background="background-contrast" round="xsmall" pad="small" margin="none" flex={false} style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
      {lines.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
    </Box>
  );
}

/**
 * The Design System's selector: a card that is the whole choice. Container, round indicator (single
 * choice), title, description. Nothing interactive inside it, so keyboard and screen readers get one
 * control per option.
 */
export function SelectorCard({ title, checked, onSelect, children }: { title: string; checked: boolean; onSelect: () => void; children?: ReactNode }) {
  return (
    <Box
      role="radio"
      aria-checked={checked}
      tabIndex={0}
      pad="medium"
      round="small"
      background={checked ? 'background-selected-primary' : 'background-front'}
      border={{ color: checked ? 'border-selected' : 'border-weak', size: checked ? 'medium' : 'xsmall' }}
      onClick={onSelect}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(); } }}
      hoverIndicator={checked ? undefined : 'background-hover'}
      gap="xsmall"
    >
      <Box direction="row" gap="small" align="center">
        {/* the theme's radio glyph (radioButton.size 24px), drawn rather than a real input so the card is the one control */}
        <Box round="full" width="24px" height="24px" border={{ color: checked ? 'border-selected' : 'border-strong', size: 'small' }} align="center" justify="center" flex={false} aria-hidden>
          {checked && <Box round="full" width="12px" height="12px" background="background-primary-strong" />}
        </Box>
        <Text weight={500} color="text-strong">{title}</Text>
      </Box>
      {children}
    </Box>
  );
}

export const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;
