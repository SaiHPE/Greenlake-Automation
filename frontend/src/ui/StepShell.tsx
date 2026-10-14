import { Box, Button, CheckBox, Collapsible, Footer, Heading, Notification, Paragraph, ResponsiveContext, Text } from 'grommet';
import { FormDown, FormUp } from 'grommet-icons';
import { ReactNode, useContext, useState } from 'react';
import { createPortal } from 'react-dom';
import { StatusLine } from './blocks';
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
 *
 * `actions` (a node) and `footerNote` are the pre-redesign footer; steps move to `primary` /
 * `buttons` / `confirmation` one at a time.
 */
export function StepShell({
  title,
  description,
  state,
  stateDetail,
  stateLabel,
  gate,
  error,
  onDismissError,
  footerNote,
  actions,
  primary,
  buttons = [],
  confirmation,
  guidance,
  guideOpen: guideInitiallyOpen = true,
  top,
  children,
}: {
  title: string;
  description?: ReactNode;
  /** Overrides the status derived from the run; used by the steps that frame a run rather than run in it. */
  state?: StepState;
  stateDetail?: string;
  stateLabel?: string;
  gate?: { title: string; message: ReactNode } | null;
  error?: string | null;
  onDismissError?: () => void;
  showActivity?: boolean;
  activityEmpty?: string;
  footerNote?: ReactNode;
  actions?: ReactNode;
  primary?: FooterAction;
  buttons?: FooterAction[];
  confirmation?: Confirmation;
  guidance?: ReactNode;
  guideOpen?: boolean;
  top?: ReactNode;
  children?: ReactNode;
}) {
  const { step, run, events, position, footerHost } = useStepContext();
  const derived = useStepState(step, run, events);
  const effective = state ?? derived.state;
  const size = useContext(ResponsiveContext);
  const stacked = size !== 'large' && size !== 'xlarge';
  const padX = stacked ? 'medium' : 'large';
  const [showGuide, setShowGuide] = useState(false);
  const [guideOpen, setGuideOpen] = useState(guideInitiallyOpen);
  const [blockedMessage, setBlockedMessage] = useState<string | undefined>();

  const primaryBlocked = confirmation && !confirmation.checked ? `Tick the box first: ${confirmation.label}` : primary?.blocked;
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
  const hasFooter = Boolean(actions || primary || buttons.length || confirmation);

  const footer = hasFooter ? (
    <Box background="background-front" border={{ side: 'top', color: 'border-weak' }} flex={false}>
      {shownMessage && (
        <Box pad={{ horizontal: padX, top: 'small' }}>
          <Notification status="warning" message={shownMessage} onClose={() => setBlockedMessage(undefined)} />
        </Box>
      )}
      {confirmation && (
        <Box direction="row" justify="end" pad={{ horizontal: padX, top: 'small' }}>
          <CheckBox
            checked={confirmation.checked}
            onChange={(e) => {
              confirmation.onChange(e.target.checked);
              if (e.target.checked) setBlockedMessage(undefined);
            }}
            label={<Text size="small">{confirmation.label}</Text>}
          />
        </Box>
      )}
      <Footer justify="end" gap="medium" pad={{ horizontal: padX, vertical: 'small' }}>
        {footerNote && (
          <Box flex>
            <Text size="small" color="text-weak">
              {footerNote}
            </Text>
          </Box>
        )}
        <Box direction="row" gap="small" align="center" justify="end" flex={false} wrap>
          {actions}
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
            <StatusIndicator state={effective} detail={stateDetail} label={stateLabel} size="medium" />
          </Box>
        </Box>

        {guidance && stacked && (
          <Box flex={false}>
            <Button plain onClick={() => setShowGuide((v) => !v)} aria-expanded={showGuide}>
              <Box direction="row" gap="xsmall" align="center">
                {showGuide ? <FormUp /> : <FormDown />}
                <Text size="small" weight={500}>
                  About this step
                </Text>
              </Box>
            </Button>
            <Collapsible open={showGuide}>
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
        {error && (
          <StatusLine state="failed" title="This step could not run" onClose={onDismissError}>
            {error}
          </StatusLine>
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
