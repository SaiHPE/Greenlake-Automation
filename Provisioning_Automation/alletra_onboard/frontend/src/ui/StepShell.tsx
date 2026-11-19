import { Box, Button, CheckBox, Collapsible, Footer, Heading, Notification, Paragraph, ResponsiveContext, Text } from 'grommet';
import { FormDown, FormUp } from 'grommet-icons';
import { ReactNode, useContext, useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Section, StatusLine, StatusLink } from './blocks';
import { NotesList } from './primitives';
import { StatusIndicator, StepState } from './status';
import { useStepContext } from './StepContext';
import { useStepState } from './useStepState';

/**
 * A footer action. There is no `disabled`: the Design System says not to gate a step with a greyed
 * button but to leave it active and say, on click, what is missing. `blocked` is that sentence.
 */
export interface FooterAction {
  label: string;
  onClick?: () => void;
  busy?: boolean;
  blocked?: string;
  /** A call to action that supports the primary. Everything else is a default button. */
  secondary?: boolean;
  href?: string;
  download?: string;
}

/** A tick the operator must give before the primary runs; it sits in the footer next to the button. */
export interface Confirmation {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

/** The one status line under the step's header (SPEC-030 R2): a title, one sentence, a time, two links. */
export interface StepStatus {
  state: StepState;
  title?: string;
  message?: ReactNode;
  time?: string;
  links?: StatusLink[];
}

// SPEC-030 R8: About this step starts closed; opening it is kept for the browser session.
const ABOUT_KEY = 'alletra.about';
function aboutWasOpened(): boolean {
  try {
    return sessionStorage.getItem(ABOUT_KEY) === 'open';
  } catch {
    return false;
  }
}
function rememberAbout(open: boolean) {
  try {
    if (open) sessionStorage.setItem(ABOUT_KEY, 'open');
    else sessionStorage.removeItem(ABOUT_KEY);
  } catch {
    // storage refused: the choice lasts until the next step
  }
}

function ActionButton({ action, primary, onPress }: { action: FooterAction; primary?: boolean; onPress: () => void }) {
  if (action.href) {
    return <Button as="a" href={action.href} download={action.download} label={action.label} primary={primary} secondary={action.secondary} />;
  }
  return <Button label={action.label} primary={primary} secondary={action.secondary} busy={action.busy} onClick={onPress} />;
}

/**
 * The chrome every step wears (Design System wizard template): "Step X of Y", the h1, one paragraph
 * and the status on the right; the step's content, with "About this step" beside it on wide screens;
 * a footer pinned under the page with the step's actions right-aligned and the one primary last.
 */
export function StepShell({
  title,
  description,
  state,
  stateLabel,
  gate,
  error,
  onDismissError,
  status,
  notes = [],
  staleNotice,
  primary,
  buttons = [],
  confirmation,
  confirmations,
  guidance,
  top,
  children,
}: {
  title: string;
  description?: ReactNode;
  /** Overrides the status derived from the run; used by the steps that frame a run rather than run in it. */
  state?: StepState;
  stateLabel?: string;
  gate?: { title: string; message: ReactNode } | null;
  error?: string | null;
  onDismissError?: () => void;
  /** The one status line under the header; `error` replaces it while shown. */
  status?: StepStatus;
  /** Every other notice, one per line, folded under the status line as "N notes". */
  notes?: ReactNode[];
  /** A stale discovery stays a visible warning under the status line on the steps that act on it (LESSONS 8). */
  staleNotice?: ReactNode;
  primary?: FooterAction;
  buttons?: FooterAction[];
  confirmation?: Confirmation;
  /** Ticks the primary needs, in the order they are drawn (Replication: the latency, then the plan). */
  confirmations?: Confirmation[];
  guidance?: ReactNode;
  top?: ReactNode;
  children?: ReactNode;
}) {
  const { step, run, events, position, footerHost } = useStepContext();
  const derived = useStepState(step, run, events);
  const effective = state ?? derived.state;
  const size = useContext(ResponsiveContext);
  const stacked = size !== 'large' && size !== 'xlarge';
  const padX = stacked ? 'medium' : 'large';
  const [guideOpen, setGuideOpenState] = useState(aboutWasOpened);
  const setGuideOpen = (open: boolean) => {
    setGuideOpenState(open);
    rememberAbout(open);
  };
  const [blockedMessage, setBlockedMessage] = useState<string | undefined>();

  // a step that passes both keeps every tick; the blocked message names the first one not ticked
  const ticks = [...(confirmations ?? []), ...(confirmation ? [confirmation] : [])];
  const unticked = ticks.find((tick) => !tick.checked);
  const primaryBlocked = unticked ? `Tick the box first: ${unticked.label}` : primary?.blocked;
  const press = (action: FooterAction, blocked = action.blocked) => () => {
    if (blocked) {
      setBlockedMessage(blocked);
      return;
    }
    setBlockedMessage(undefined);
    action.onClick?.();
  };
  // a message stays only while the reason it was shown still holds
  const shownMessage =
    blockedMessage && (blockedMessage === primaryBlocked || buttons.some((b) => b.blocked === blockedMessage)) ? blockedMessage : undefined;
  const ordered = [...buttons].sort((a, b) => Number(!!a.secondary) - Number(!!b.secondary));
  const hasFooter = Boolean(primary || buttons.length || ticks.length);
  useEffect(() => {
    if (import.meta.env.DEV && buttons.length > 2) {
      console.warn(`${title}: ${buttons.length} footer buttons beside the primary; SPEC-030 R4 allows two.`);
    }
  }, [buttons.length, title]);

  const tickBoxes = ticks.map((tick) => (
    <CheckBox
      key={tick.label}
      checked={tick.checked}
      onChange={(e) => {
        tick.onChange(e.target.checked);
        if (e.target.checked) setBlockedMessage(undefined);
      }}
      label={<Text size="small">{tick.label}</Text>}
    />
  ));

  const footer = hasFooter ? (
    <Box background="background-front" border={{ side: 'top', color: 'border-weak' }} flex={false}>
      {shownMessage && (
        <Box pad={{ horizontal: padX, top: 'small' }}>
          <Notification status="warning" message={shownMessage} onClose={() => setBlockedMessage(undefined)} />
        </Box>
      )}
      {/* below large the ticks stack above the buttons; at large they share the buttons' row, on the left */}
      {stacked && tickBoxes.length > 0 && (
        <Box align="end" gap="xsmall" pad={{ horizontal: padX, top: 'small' }}>
          {tickBoxes}
        </Box>
      )}
      <Footer justify="end" gap="medium" pad={{ horizontal: padX, vertical: 'small' }} wrap>
        {!stacked && tickBoxes.length > 0 && (
          <Box flex width={{ min: 'small' }} align="end" gap="xsmall">
            {tickBoxes}
          </Box>
        )}
        <Box direction="row" gap="small" align="center" justify="end" flex={false} wrap>
          {ordered.map((b) => (
            <ActionButton key={b.label} action={b} onPress={press(b)} />
          ))}
          {primary && <ActionButton action={primary} primary onPress={press(primary, primaryBlocked)} />}
        </Box>
      </Footer>
    </Box>
  ) : null;

  const aboutPanel = guidance && !stacked && guideOpen && (
    <Box
      as="aside"
      aria-label="About this step"
      width={{ min: 'small', max: 'medium' }}
      basis="1/3"
      flex={false}
      alignSelf="start"
      background="background-contrast"
      round="small"
      pad="medium"
      gap="medium"
    >
      <Box direction="row" justify="between" align="center">
        <Text weight={500} color="text-strong">
          About this step
        </Text>
        <Button size="small" label="Hide" onClick={() => setGuideOpen(false)} />
      </Box>
      {guidance}
    </Box>
  );

  return (
    <>
      <Box gap="medium" flex={false}>
        <Box direction="row" justify="between" align="start" gap="medium" flex={false}>
          <Box gap="xxsmall">
            {position.label !== '' && (
              <Text size="small" color="text-weak">
                {position.label ?? `Step ${position.index} of ${position.total}`}
              </Text>
            )}
            <Heading level={1} size="small" margin="none">
              {title}
            </Heading>
            {description && <Paragraph margin="none">{description}</Paragraph>}
          </Box>
          <Box direction="row" gap="medium" align="center" flex={false} pad={{ top: 'medium' }}>
            {guidance && !stacked && !guideOpen && <Button size="small" label="About this step" onClick={() => setGuideOpen(true)} />}
            <StatusIndicator state={effective} label={stateLabel} size="medium" />
          </Box>
        </Box>

        {guidance && stacked && (
          <Box flex={false}>
            <Button plain onClick={() => setGuideOpen(!guideOpen)} aria-expanded={guideOpen}>
              <Box direction="row" gap="xsmall" align="center">
                {guideOpen ? <FormUp /> : <FormDown />}
                <Text size="small" weight={500}>
                  About this step
                </Text>
              </Box>
            </Button>
            <Collapsible open={guideOpen}>
              <Box background="background-contrast" round="small" pad="medium" margin={{ top: 'small' }}>
                {guidance}
              </Box>
            </Collapsible>
          </Box>
        )}

        {top}

        {gate && (
          <StatusLine state="action_required" title={gate.title}>
            {gate.message}
          </StatusLine>
        )}
        {error ? (
          <Box role="alert" flex={false}>
            <StatusLine state="failed" title="This step could not run" onClose={onDismissError}>
              {error}
            </StatusLine>
          </Box>
        ) : (
          status && (
            <Box role="status" aria-live="polite" flex={false}>
              <StatusLine state={status.state} title={status.title} time={status.time} links={status.links}>
                {status.message}
              </StatusLine>
            </Box>
          )
        )}
        {staleNotice}
        {notes.length > 0 && (
          <Section title={`${notes.length} note${notes.length === 1 ? '' : 's'}`}>
            <NotesList notes={notes} />
          </Section>
        )}

        <Box direction="row" gap="large" align="start" flex={false}>
          {/* children are Boxes: Grommet's gap counts a fragment as one child */}
          <Box flex gap="medium" style={{ minWidth: 0 }}>
            {children}
          </Box>
          {aboutPanel}
        </Box>
      </Box>
      {footer && (footerHost ? createPortal(footer, footerHost) : footer)}
    </>
  );
}
