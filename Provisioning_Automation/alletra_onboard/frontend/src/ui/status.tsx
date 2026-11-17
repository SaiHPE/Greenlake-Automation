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

/** A row's result: the word drawn, and the state that gives it its icon and colour. */
export interface ResultWord {
  state: StepState;
  label: string;
}

/**
 * The words a table row says about one thing (SPEC-030 R9), drawn with StatusIndicator. Step maps point
 * here; no step keeps its own words or icons for these.
 */
export const RESULT = {
  // a check (prerequisites, readiness, link); a failover step uses passed, failed and skipped
  passed: { state: 'complete', label: 'Passed' },
  review: { state: 'action_required', label: 'Review' },
  failed: { state: 'failed', label: 'Failed' },
  not_checked: { state: 'not_started', label: 'Not checked' },
  // an endpoint; a port
  reachable: { state: 'complete', label: 'Reachable' },
  blocked: { state: 'failed', label: 'Blocked' },
  ready: { state: 'complete', label: 'Ready' },
  // a host on a fabric (Not zoned waits, grey, while a command set is with the SAN team)
  zoned: { state: 'complete', label: 'Zoned' },
  not_zoned: { state: 'failed', label: 'Not zoned' },
  partly_zoned: { state: 'action_required', label: 'Partly zoned' },
  not_on_fabric: { state: 'not_started', label: 'Not on fabric' },
  // a plan row (in a write's result, Already there is grey: the object was left alone)
  create: { state: 'not_started', label: 'Create' },
  update: { state: 'action_required', label: 'Update' },
  already_there: { state: 'complete', label: 'Already there' },
  conflict: { state: 'failed', label: 'Conflict' },
  // a write
  created: { state: 'complete', label: 'Created' },
  updated: { state: 'complete', label: 'Updated' },
  skipped: { state: 'not_started', label: 'Skipped' },
  // paths: No path is a report, never a gate, so amber, not red
  live: { state: 'complete', label: 'Live' },
  partial: { state: 'action_required', label: 'Partial' },
  no_path: { state: 'action_required', label: 'No path' },
  // a Remote Copy group
  replicating: { state: 'complete', label: 'Replicating' },
  syncing: { state: 'running', label: 'Initial sync in progress' },
  not_replicating: { state: 'failed', label: 'Not replicating' },
  // a setting
  matches: { state: 'complete', label: 'Matches' },
  differs: { state: 'action_required', label: 'Differs' },
  not_readable: { state: 'not_started', label: 'Not readable' },
} satisfies Record<string, ResultWord>;

/** An empty table cell (Design System tables): `--`, read as "No value". */
export function NoValue() {
  return (
    <Text size="small" color="text-weak" a11yTitle="No value">
      --
    </Text>
  );
}

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
