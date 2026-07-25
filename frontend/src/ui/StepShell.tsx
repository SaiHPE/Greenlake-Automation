import { Box, Heading, Text } from 'grommet';
import { ReactNode } from 'react';
import { ActionRequired, ActivityTimeline, InlineNotification, Surface } from './primitives';
import { StatusIndicator, StepState } from './status';
import { useStepContext } from './StepContext';
import { stepEvents, useStepState } from './useStepState';

/**
 * The chrome every step wears.
 *
 * Each step used to hand-roll its own heading, status wording, error banner, event filter and
 * button row — which is how the interface ended up with several spellings of the same idea. A step
 * now supplies only what is genuinely its own: its content and its actions. Position, status and
 * activity come from the run.
 *
 * Order is fixed, top to bottom: identity → operator gate → error → content → activity → actions.
 */
export function StepShell({
  title,
  description,
  state,
  stateDetail,
  gate,
  error,
  onDismissError,
  showActivity = true,
  activityEmpty,
  footerNote,
  actions,
  children,
}: {
  title: string;
  description?: ReactNode;
  /** Overrides the status derived from the run — used by the steps that frame a run rather than run in it. */
  state?: StepState;
  stateDetail?: string;
  gate?: { title: string; message: ReactNode } | null;
  error?: string | null;
  onDismissError?: () => void;
  showActivity?: boolean;
  activityEmpty?: string;
  footerNote?: ReactNode;
  actions?: ReactNode;
  children?: ReactNode;
}) {
  const { step, run, events, position } = useStepContext();
  const derived = useStepState(step, run, events);
  const effective = state ?? derived.state;
  const activity = stepEvents(step, events);

  return (
    <Box gap="medium" flex={false}>
      <Box gap="xsmall" flex={false}>
        <Text size="xsmall" color="text-weak">
          {`Step ${position.index} of ${position.total}`}
        </Text>
        <Heading level={1} margin="none">
          {title}
        </Heading>
        {description && (
          <Text color="text-weak" style={{ maxWidth: '30em' }}>
            {description}
          </Text>
        )}
        <Box pad={{ top: 'xxsmall' }} flex={false}>
          <StatusIndicator state={effective} detail={stateDetail} size="medium" />
        </Box>
      </Box>

      {gate && <ActionRequired title={gate.title} message={gate.message} />}

      {error && (
        <InlineNotification tone="critical" title="This step could not run" message={error} onClose={onDismissError} />
      )}

      {children}

      {showActivity && step && (
        <Surface title="Activity">
          <ActivityTimeline events={activity} empty={activityEmpty} />
        </Surface>
      )}

      {actions && (
        <Box
          direction="row"
          align="center"
          justify="between"
          gap="medium"
          pad={{ top: 'medium' }}
          border={{ side: 'top', color: 'border-weak' }}
          flex={false}
          wrap
        >
          <Text size="small" color="text-weak">
            {footerNote}
          </Text>
          <Box direction="row" gap="small" align="center" flex={false}>
            {actions}
          </Box>
        </Box>
      )}
    </Box>
  );
}
