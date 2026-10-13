/**
 * The proposed app shell and its building blocks, for the redesign mockups only. Nothing here is
 * used by the app; when a mockup is agreed, these become the real components.
 */
import { Box, Button, CheckBox, Collapsible, Heading, Menu, ResponsiveContext, Text } from 'grommet';
import { Apps, FormDown, FormNext, FormPrevious, Radial, Terminal, Time } from 'grommet-icons';
import { createContext, ReactNode, useContext, useState } from 'react';
import { HpeElement } from '../src/ui/AppChrome';
import { StatusIcon, StatusIndicator, StepState } from '../src/ui/status';

/** The medium spacing step of the HPE theme, as a CSS value. */
const GAP = '24px';

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
      width="22px"
      height="22px"
      align="center"
      justify="center"
      flex={false}
      aria-label={`Note ${n}`}
      style={{ display: 'inline-flex', verticalAlign: 'middle', marginLeft: 6 }}
    >
      <Text size="xsmall" weight="bold" color="text-onStrong">{n}</Text>
    </Box>
  );
}

// ------------------------------------------------------------------ the frame

export interface RailStep {
  key: string;
  label: string;
  state: StepState;
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
  state: StepState;
  stateLabel: string;
}

export function StepIcon({ state }: { state: StepState }) {
  // A plain empty circle for "not started": the current app's question mark reads as "unknown".
  if (state === 'not_started') return <Radial size="small" color="text-weak" a11yTitle="Not started" />;
  return <StatusIcon state={state} />;
}

const RailIcon = StepIcon;

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
      <Box pad={{ top: '2px' }} flex={false}>
        {icon ?? <RailIcon state={step.state} />}
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

export function AppFrame({
  run,
  groups,
  current,
  onSelect,
  railNote,
  children,
}: {
  run?: RunSummary;
  groups: RailGroup[];
  current: string;
  onSelect?: (key: string) => void;
  railNote?: string;
  children: ReactNode;
}) {
  const size = useContext(ResponsiveContext);
  const narrow = size === 'small' || size === 'xsmall';
  return (
    <Box fill background="background-back">
      <Box
        direction="row"
        justify="between"
        align="center"
        pad={{ horizontal: 'medium', vertical: 'small' }}
        background="background-front"
        border={{ side: 'bottom', color: 'border-weak' }}
        flex={false}
      >
        <Box direction="row" gap="small" align="center">
          <HpeElement width={36} />
          <Text weight="bold" color="text-strong">Alletra MP Onboarding</Text>
        </Box>
        <Box direction="row" gap="medium" align="center">
          {run && (
            <Box direction="row" gap="small" align="center">
              <Text size="small" weight="bold" color="text-strong">{run.array}</Text>
              <Text size="small" color="text-weak">{run.serial} · {run.mode}</Text>
              <StatusIndicator state={run.state} label={run.stateLabel} />
            </Box>
          )}
          <Menu label="Runs" items={[{ label: 'Open another run' }, { label: 'Start a new run' }]} dropAlign={{ top: 'bottom', right: 'right' }} />
        </Box>
      </Box>
      <Box direction="row" flex overflow="hidden">
        {!narrow && (
          <Box
            width="248px"
            flex={false}
            background="background-front"
            border={{ side: 'right', color: 'border-weak' }}
            pad={{ vertical: 'small', horizontal: 'small' }}
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
                <Text size="xsmall" weight="bold" color="text-weak" margin={{ left: 'small', top: 'xsmall' }}>
                  {g.stage.toUpperCase()}
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
          </Box>
        )}
        <Box flex overflow="hidden">{children}</Box>
      </Box>
    </Box>
  );
}

// ------------------------------------------------------------------ one step page

export interface Action {
  label: string;
  onClick?: () => void;
  disabled?: boolean;
  busy?: boolean;
  hint?: string;
}

/** A tick the operator must give before the primary action runs; it sits in the footer next to the button. */
export interface Confirmation {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
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
  secondary = [],
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
  state?: StepState;
  stateLabel?: string;
  primary?: Action;
  secondary?: Action[];
  confirmation?: Confirmation;
  guidance?: ReactNode;
  guideOpen?: boolean;
  top?: ReactNode;
  activity?: { last: string; events: number; commands: number };
  children: ReactNode;
}) {
  const size = useContext(ResponsiveContext);
  const stacked = size !== 'large' && size !== 'xlarge';
  const [showGuide, setShowGuide] = useState(false);
  const [guideOpen, setGuideOpen] = useState(guideInitiallyOpen);
  return (
    <Box fill>
      {/* wizard header: Previous left (not on the first step), Cancel right (HPE wizard template) */}
      <Box
        direction="row"
        justify="between"
        align="center"
        pad={{ horizontal: 'medium', vertical: 'xsmall' }}
        background="background-front"
        border={{ side: 'bottom', color: 'border-weak' }}
        flex={false}
      >
        {first ? <Box /> : <Button icon={<FormPrevious />} label="Previous step" plain={false} size="small" />}
        <Button label={runExists ? 'Cancel run' : 'Start over'} size="small" />
      </Box>
      <Box flex overflow="auto">
        <Box pad={{ horizontal: 'large', top: 'small', bottom: 'large' }} flex={false} style={{ gap: GAP }}>
          <Box direction="row" justify="between" align="end" gap="medium" flex={false}>
            <Box>
              {stepLabel && <Text size="small" color="text-weak">{stepLabel}</Text>}
              <Heading level={1} size="small" margin="none">{title}</Heading>
              {description && <Text color="text-weak" margin={{ top: 'xxsmall' }}>{description}</Text>}
            </Box>
            {state && (
              <Box direction="row" gap="medium" align="center" flex={false}>
                {!stacked && guidance && !guideOpen && (
                  <Button size="small" label="About this step" onClick={() => setGuideOpen(true)} />
                )}
                <StatusIndicator state={state} label={stateLabel} size="medium" />
              </Box>
            )}
          </Box>
          {stacked && guidance && (
            <Box flex={false}>
              <Button plain onClick={() => setShowGuide((v) => !v)}>
                <Box direction="row" gap="xsmall" align="center">
                  {showGuide ? <FormDown /> : <FormNext />}
                  <Text size="small" weight={600}>About this step</Text>
                </Box>
              </Button>
              <Collapsible open={showGuide}>
                <Box background="background-contrast" round="small" pad="medium" margin={{ top: 'small' }}>{guidance}</Box>
              </Collapsible>
            </Box>
          )}
          {top}
          <Box direction="row" gap="large" align="start" flex={false}>
            {/* CSS gap, not Grommet's: Grommet counts a React fragment as one child and puts no gap inside it */}
            <Box flex style={{ minWidth: 0, gap: GAP }}>{children}</Box>
            {!stacked && guidance && guideOpen && (
              <Box width="medium" flex={false} background="background-contrast" round="small" pad="medium" gap="medium">
                <Box direction="row" justify="between" align="center">
                  <Text size="small" weight="bold" color="text-weak">ABOUT THIS STEP</Text>
                  <Button size="small" label="Hide" onClick={() => setGuideOpen(false)} />
                </Box>
                {guidance}
              </Box>
            )}
          </Box>
        </Box>
      </Box>
      {(primary || secondary.length > 0) && (
        <Box
          direction="row"
          justify="between"
          align="center"
          gap="small"
          pad={{ horizontal: 'large', vertical: 'small' }}
          background="background-front"
          border={{ side: 'top', color: 'border-weak' }}
          flex={false}
        >
          <Box direction="row" gap="small">
            {secondary.map((a) => (
              <Button key={a.label} secondary label={a.label} onClick={a.onClick} disabled={a.disabled} busy={a.busy} />
            ))}
          </Box>
          {primary && (
            <Box direction="row" gap="medium" align="center">
              {confirmation && (
                <CheckBox
                  checked={confirmation.checked}
                  onChange={(e) => confirmation.onChange(e.target.checked)}
                  label={<Text size="small">{confirmation.label}</Text>}
                />
              )}
              {!confirmation && primary.disabled && primary.hint && <Text size="small" color="text-weak">{primary.hint}</Text>}
              <Button primary label={primary.label} onClick={primary.onClick} disabled={primary.disabled} busy={primary.busy} />
            </Box>
          )}
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
      pad={{ horizontal: 'large', vertical: 'xsmall' }}
      background="background-contrast"
      border={{ side: 'top', color: 'border-weak' }}
      flex={false}
    >
      <Box direction="row" gap="xsmall" align="center">
        <Time size="small" color="text-weak" />
        <Text size="small" color="text-weak">{last}</Text>
      </Box>
      <Box direction="row" gap="small">
        <Button size="small" label={`Activity · ${events}`} />
        <Button size="small" icon={<Terminal size="small" />} label={`Console · ${commands} commands`} />
      </Box>
    </Box>
  );
}

// ------------------------------------------------------------------ content blocks

const TONE: Record<StepState, string> = {
  complete: 'background-ok',
  action_required: 'background-warning',
  failed: 'background-critical',
  running: 'background-info',
  not_started: 'background-contrast',
};

/** One sentence saying what happened, at the top of the step. */
export function StatusLine({ state, children, time }: { state: StepState; children: ReactNode; time?: string }) {
  return (
    <Box direction="row" gap="small" align="center" pad={{ horizontal: 'medium', vertical: 'small' }} round="small" background={TONE[state]} flex={false}>
      <StatusIcon state={state} size="medium" />
      <Box flex>
        <Text weight={500} color="text-strong">{children}</Text>
      </Box>
      {time && <Text size="small" color="text-weak">{time}</Text>}
    </Box>
  );
}

/** A section that opens on demand: the title and a one-line summary are always visible. */
export function Section({
  title,
  summary,
  right,
  open: openInitially = false,
  children,
}: {
  title: ReactNode;
  summary?: ReactNode;
  right?: ReactNode;
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
      >
        {open ? <FormDown /> : <FormNext />}
        <Box flex direction="row" gap="small" align="baseline" wrap>
          <Text weight={600} color="text-strong">{title}</Text>
          {summary && <Text size="small" color="text-weak">{summary}</Text>}
        </Box>
        {right}
      </Box>
      <Collapsible open={open}>
        <Box pad={{ horizontal: 'medium', bottom: 'medium' }} style={{ gap: '12px' }}>{children}</Box>
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
                <Button plain onClick={() => setOpen(open === i ? null : i)}>
                  <Text size="small" color="text-anchor">{open === i ? 'Hide' : 'Show'}</Text>
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

/** Right-hand guidance: the explanations that used to fill the page. */
export function Guidance({ items }: { items: { title: string; body: ReactNode }[] }) {
  return (
    <Box gap="medium" flex={false}>
      {items.map((g) => (
        <Box key={g.title} gap="xxsmall" flex={false}>
          <Text size="small" weight="bold" color="text-strong">{g.title}</Text>
          <Text size="small" color="text-default">{g.body}</Text>
        </Box>
      ))}
    </Box>
  );
}

export const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;
