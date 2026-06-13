import { Box, Button, Notification, Text } from 'grommet';
import { RunEvent, RunRecord } from '../api';
import { EventLog, Section } from '../components';

interface Props {
  run: RunRecord | null;
  events: RunEvent[];
  onRestart: () => void;
}

export function DoneStep({ run, events, onRestart }: Props) {
  return (
    <Box gap="medium">
      <Notification
        status="normal"
        title={`Array ${run?.serial_number ?? ''} onboarding complete`}
        message="Registered in GreenLake, connected via the Cloud Connectivity Wizard, and set up in DSCC."
      />
      {run?.warnings?.length ? (
        <Notification status="warning" title="Warnings recorded during the run" message={run.warnings.join(' • ')} />
      ) : null}
      <Section title="Full run timeline">
        <EventLog events={events} />
      </Section>
      <Text size="small" color="text-weak">
        Failure screenshots (if any) are under .alletra_onboard/artifacts.
      </Text>
      <Button primary label="Onboard another array" onClick={onRestart} alignSelf="start" />
    </Box>
  );
}
