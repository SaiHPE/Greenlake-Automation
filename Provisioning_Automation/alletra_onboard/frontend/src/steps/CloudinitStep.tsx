import { Box, Button, Notification, Spinner, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, startCloudinit } from '../api';
import { EventLog, Instructions, Section, StatusTag } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  defaultUrl: string;
  onDone: () => void;
}

export function CloudinitStep({ runId, run, events, defaultUrl, onDone }: Props) {
  const [url, setUrl] = useState(defaultUrl);
  const [error, setError] = useState<string | null>(null);

  const stepEvents = events.filter((e) => e.phase === 'CLOUDINIT_CONNECT');
  const running = run?.status === 'running' && run?.current_phase === 'CLOUDINIT_CONNECT';
  const reviewReady = stepEvents.some((e) => e.event_type === 'operator.review_ready');
  const connected = run?.current_phase === 'DSCC_SETUP_SYSTEM' && run?.status === 'ready';
  const failed =
    run?.current_phase === 'CLOUDINIT_CONNECT' &&
    (run?.status === 'retryable_failure' || run?.status === 'terminal_failure');
  const validUrl = url.trim().startsWith('https://169.254.');

  const start = async () => {
    setError(null);
    try {
      await startCloudinit(runId, url.trim());
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <Box gap="medium">
      <Section title="Get the wizard URL from the Discovery Tool">
        <Instructions
          items={[
            <>Open the <b>HPE Storage Discovery Tool</b> on this jump box.</>,
            <>Search for the array&apos;s serial number ({run?.serial_number ?? '…'}).</>,
            <>Copy the wizard link — it looks like <b>https://169.254.x.x/cloudinit</b> (it changes every boot).</>,
            <>Paste it below and click <b>Launch &amp; Fill</b>. A browser opens and the form fills itself.</>,
          ]}
        />
        <Box direction="row" gap="small" align="center" width="large">
          <TextInput placeholder="https://169.254.x.x/cloudinit" value={url} onChange={(e) => setUrl(e.target.value)} />
          <Button primary disabled={!validUrl || running} label={running ? 'Filling…' : 'Launch & Fill'} onClick={start} />
          {running && <Spinner />}
          <StatusTag status={run?.current_phase === 'CLOUDINIT_CONNECT' ? run?.status : undefined} />
        </Box>
        {!validUrl && url.trim() !== '' && (
          <Text size="small" color="status-critical">
            The wizard URL must start with https://169.254.
          </Text>
        )}
      </Section>

      {error && <Notification status="critical" title="Could not start" message={error} onClose={() => setError(null)} />}

      {reviewReady && !connected && (
        <Notification
          status="warning"
          title="Action needed: review and Submit in the wizard browser"
          message="The wizard is filled and stopped at Review. Check the values (especially the Network section), then click Submit yourself. This page updates automatically when the array connects."
        />
      )}
      {failed && (
        <Notification
          status="critical"
          title="The wizard run did not complete"
          message="Check the screenshot in .alletra_onboard/artifacts, fix the cause, and Launch & Fill again."
        />
      )}
      {connected && (
        <Notification status="normal" title="Array connected to HPE GreenLake" message="Cloud connectivity is done — continue to DSCC Setup." />
      )}

      <Section title="Progress">
        <EventLog events={stepEvents} emptyText="Paste the URL and click Launch & Fill to start." />
      </Section>

      <Button primary label="Continue → DSCC Setup" disabled={!connected} onClick={onDone} alignSelf="start" />
    </Box>
  );
}
