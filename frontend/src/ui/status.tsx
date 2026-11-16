import { Box, Text } from 'grommet';
import { Clock, InProgress, Radial, StatusCritical, StatusGood, StatusWarning } from 'grommet-icons';

/**
 * The single status vocabulary for the whole application. Every step, every screen and the run
 * itself report progress in these six words; there is no second set. `waiting` is a step parked on
 * another team (the SAN team applying zones): calm and grey, unlike orange `action_required`.
 */
export type StepState = 'not_started' | 'running' | 'action_required' | 'waiting' | 'complete' | 'failed';

interface StateStyle {
  label: string;
  color: string;
  Icon: typeof StatusGood;
}

// Colour + icon + shape + text. WCAG 2.1 requires at least three of those four signals, so status is
// never carried by colour alone: each state also has its own icon silhouette and its own wording.
const STATES: Record<StepState, StateStyle> = {
  not_started: { label: 'Not started', color: 'icon-weak', Icon: Radial },
  running: { label: 'Running', color: 'status-info', Icon: InProgress },
  action_required: { label: 'Action required', color: 'status-warning', Icon: StatusWarning },
  waiting: { label: 'Waiting on others', color: 'icon-weak', Icon: Clock },
  complete: { label: 'Complete', color: 'status-ok', Icon: StatusGood },
  failed: { label: 'Failed', color: 'status-critical', Icon: StatusCritical },
};

export const stateLabel = (state: StepState) => STATES[state].label;

export function StatusIcon({ state, size = 'small' }: { state: StepState; size?: string }) {
  const { Icon, color, label } = STATES[state];
  return <Icon size={size} color={color} a11yTitle={label} />;
}

/**
 * Status as icon + words. `detail` appends a short qualifier ("Complete · 1 discrepancy") without
 * changing the state vocabulary itself.
 */
export function StatusIndicator({
  state,
  detail,
  size = 'small',
  label,
}: {
  state: StepState;
  detail?: string;
  size?: 'small' | 'medium';
  label?: string;
}) {
  const text = label ?? stateLabel(state);
  return (
    <Box direction="row" gap="xsmall" align="center" flex={false}>
      <StatusIcon state={state} size={size} />
      <Text size={size === 'medium' ? 'medium' : 'small'} weight={500}>
        {detail ? `${text} · ${detail}` : text}
      </Text>
    </Box>
  );
}
