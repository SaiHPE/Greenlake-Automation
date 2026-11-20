import { Box, CheckBox, NameValueList, NameValuePair, Text } from 'grommet';
import { Cloud } from 'grommet-icons';
import { useState } from 'react';
import { RunEvent, RunRecord, startProvision } from '../api';
import { EmptyState, Guidance, Panel } from '../ui/blocks';
import { StepShell, StepStatus } from '../ui/StepShell';
import { useStepContext } from '../ui/StepContext';
import { useStepState } from '../ui/useStepState';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

export function GreenLakeStep({ runId, run, events, onDone }: Props) {
  const [dryRun, setDryRun] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { step, nextTitle } = useStepContext();

  const running = run?.status === 'running';
  // Derived from this step's own outcome, not from the phase of whichever step happens to follow:
  // in a custom run there may not be one, which used to leave the operator with no way forward.
  const { state } = useStepState(step, run, events);
  const registered = state === 'complete';
  const resources = events.find((event) => event.event_type === 'step.completed' && event.phase.startsWith('GL_'));

  // one status: running > registered; the subscription warnings are notes
  const status: StepStatus | undefined = running
    ? { state: 'running', title: 'Registering the array in HPE GreenLake', message: 'Each phase appears in Activity, below.' }
    : registered
      ? {
          state: 'complete',
          title: 'Registered and assigned to Data Services',
          message: 'The array can now be connected to HPE GreenLake from the array console.',
        }
      : undefined;

  const start = async () => {
    setError(null);
    try {
      await startProvision(runId, dryRun);
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  };

  return (
    <StepShell
      title="GreenLake registration"
      description="Registers the array in HPE GreenLake, assigns it to Data Services and applies the subscription."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      notes={run?.warnings ?? []}
      primary={
        registered
          ? { label: nextTitle ? `Continue to ${nextTitle}` : 'Continue', onClick: onDone }
          : { label: running ? 'Registering' : dryRun ? 'Check without writing' : 'Register the array', busy: running, onClick: start }
      }
      guidance={
        <Guidance
          items={[
            { title: 'Safe to run again', body: 'Each write is checked against HPE GreenLake first. Running the step again skips what is already done.' },
            { title: 'Dry run', body: 'Reads HPE GreenLake and reports what registration would do, without writing anything.' },
            { title: 'Subscription warnings', body: 'A warning while applying the subscription is not fatal. Registration and assignment are what release the array.' },
          ]}
        />
      }
    >
      {!registered && !running && (
        <Box gap="small" flex={false}>
          <EmptyState icon={<Cloud size="large" color="icon-weak" />} title="Not registered yet">
            Register the array adds the device, assigns it to Data Services in the workbook&apos;s region, and applies the subscription.
          </EmptyState>
          <CheckBox label="Dry run: check without writing" checked={dryRun} onChange={(event) => setDryRun(event.target.checked)} />
        </Box>
      )}

      {resources && (
        <Panel title="Created resources">
          <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'medium' }}>
            <NameValuePair name="Device">
              <Text>{run?.serial_number ?? '--'}</Text>
            </NameValuePair>
            <NameValuePair name="Region">
              <Text>As configured in the workbook</Text>
            </NameValuePair>
          </NameValueList>
        </Panel>
      )}
    </StepShell>
  );
}
