import { Box, Button, CheckBox, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, startProvision } from '../api';
import { InlineNotification, Surface } from '../ui/primitives';
import { StepShell } from '../ui/StepShell';
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
  const { step } = useStepContext();

  const running = run?.status === 'running';
  // Derived from this step's own outcome, not from the phase of whichever step happens to follow —
  // in a custom run there may not be one, which used to leave the operator with no way forward.
  const { state } = useStepState(step, run, events);
  const registered = state === 'complete';
  const resources = events.find((event) => event.event_type === 'step.completed' && event.phase.startsWith('GL_'));

  const start = async () => {
    setError(null);
    try {
      await startProvision(runId, dryRun);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <StepShell
      title="GreenLake registration"
      description="Registers the array in HPE GreenLake, assigns it to Data Services and applies the subscription."
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Start the registration and each phase will be recorded here."
      footerNote="Each write is idempotency-checked; re-running is safe."
      actions={
        <>
          <CheckBox
            label="Dry run (no writes)"
            checked={dryRun}
            onChange={(event) => setDryRun(event.target.checked)}
            disabled={running}
          />
          {registered ? (
            <Button primary label="Continue" onClick={onDone} />
          ) : (
            <Button primary busy={running} label={running ? 'Registering' : 'Register the array'} onClick={start} />
          )}
        </>
      }
    >
      {run?.warnings?.length ? (
        <InlineNotification
          tone="warning"
          title="Registration completed with warnings"
          message={run.warnings.join(' · ')}
        />
      ) : null}

      {registered && (
        <InlineNotification
          tone="ok"
          title="The array is registered and assigned to Data Services"
          message="It can now be connected to HPE GreenLake from the array console."
        />
      )}

      {resources && (
        <Surface title="Created resources">
          <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'medium' }}>
            <NameValuePair name="Device">
              <Text>{run?.serial_number ?? '—'}</Text>
            </NameValuePair>
            <NameValuePair name="Region">
              <Text>{String(resources.data?.region ?? 'As configured in the workbook')}</Text>
            </NameValuePair>
          </NameValueList>
        </Surface>
      )}

      <Box flex={false}>
        <Text size="small" color="text-weak">
          A subscription-apply warning is not fatal; registration and assignment are what release the array.
        </Text>
      </Box>
    </StepShell>
  );
}
