import { Box, Button, CheckBox, Notification, Spinner, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, startProvision } from '../api';
import { EventLog, Section, StatusTag } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

export function GreenLakeStep({ runId, run, events, onDone }: Props) {
  const [dryRun, setDryRun] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const running = run?.status === 'running';
  const readyForCloudinit = run?.status === 'ready' && run?.current_phase === 'CLOUDINIT_CONNECT';
  const failed = run?.status === 'retryable_failure' || run?.status === 'terminal_failure';
  const glEvents = events.filter((e) => e.phase.startsWith('GL_') || e.phase === 'PREFLIGHT');

  const start = async () => {
    setError(null);
    try {
      await startProvision(runId, dryRun);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <Box gap="medium">
      <Section title="Register the array in GreenLake">
        <Text size="small">
          Runs the GreenLake REST automation: discover the Data Services instance, add the subscription,
          register the device, assign it to Data Services, and apply the subscription. A subscription-apply
          warning is non-fatal — registration + assignment is what unblocks the array.
        </Text>
        <Box direction="row" gap="medium" align="center">
          <Button primary disabled={running} label={running ? 'Running…' : 'Run GreenLake automation'} onClick={start} />
          <CheckBox label="Dry run (preview, no writes)" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} disabled={running} />
          {running && <Spinner />}
          <StatusTag status={run?.status} />
        </Box>
      </Section>

      {error && <Notification status="critical" title="Could not start" message={error} onClose={() => setError(null)} />}
      {failed && (
        <Notification
          status="critical"
          title="GreenLake provisioning failed"
          message="See the log below — fix the cause (credentials, part number, subscription key) and run again."
        />
      )}
      {run?.warnings?.length ? (
        <Notification status="warning" title="Warnings" message={run.warnings.join(' • ')} />
      ) : null}

      <Section title="Progress">
        <EventLog events={glEvents} emptyText="Click Run to start — phases stream here live." />
      </Section>

      {readyForCloudinit && (
        <Notification status="normal" title="GreenLake registration complete" message="The array can now connect via the Cloud Connectivity Wizard." />
      )}
      <Button primary label="Continue → Cloud Connectivity" disabled={!readyForCloudinit} onClick={onDone} alignSelf="start" />
    </Box>
  );
}
