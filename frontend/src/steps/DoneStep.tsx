import { Button, NameValueList, NameValuePair, Text } from 'grommet';
import { RunEvent, RunRecord } from '../api';
import { ActivityTimeline, InlineNotification, Surface } from '../ui/primitives';
import { StepShell } from '../ui/StepShell';

interface Props {
  run: RunRecord | null;
  events: RunEvent[];
  onRestart: () => void;
}

export function DoneStep({ run, events, onRestart }: Props) {
  const complete = run?.status === 'succeeded';
  const created = events.filter((event) => event.event_type === 'storage.applied').length > 0;

  return (
    <StepShell
      title="Finish"
      description="A record of what this run performed and the items handed over to other teams."
      state={complete ? 'complete' : 'not_started'}
      stateDetail={complete ? undefined : 'run still in progress'}
      footerNote="The run record remains on this workstation until a new run is started."
      actions={<Button primary label="Start a new deployment" onClick={onRestart} />}
    >
      <InlineNotification
        tone={complete ? 'ok' : 'info'}
        title={complete ? `${run?.serial_number ?? 'The array'} is onboarded` : 'This run is not finished yet'}
        message={
          complete
            ? 'Registered in HPE GreenLake and configured in DSCC.'
            : 'Return to any step marked Action required to continue.'
        }
      />

      {run?.warnings?.length ? (
        <InlineNotification tone="warning" title="Warnings recorded during this run" message={run.warnings.join(' · ')} />
      ) : null}

      <Surface title="Summary">
        <NameValueList pairProps={{ direction: 'column' }}>
          <NameValuePair name="Array">
            <Text>{run?.serial_number ?? '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Mode">
            <Text>{run?.mode?.replaceAll('_', ' ').toLowerCase() ?? '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Storage provisioned">
            <Text>{created ? 'Yes' : 'Not in this run'}</Text>
          </NameValuePair>
        </NameValueList>
      </Surface>

      <Surface title="Run timeline" description="Every step this run recorded, in order.">
        <ActivityTimeline events={events} />
      </Surface>

      <Text size="small" color="text-weak">
        Diagnostic screenshots, if any were captured, are stored under .alletra_onboard/artifacts.
      </Text>
    </StepShell>
  );
}
