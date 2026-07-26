import { Button, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { markComplete, RunEvent, RunRecord } from '../api';
import { ActivityTimeline, InlineNotification, Surface } from '../ui/primitives';
import { StepShell } from '../ui/StepShell';

interface Props {
  runId: string | null;
  run: RunRecord | null;
  events: RunEvent[];
  onRestart: () => void;
}

export function DoneStep({ runId, run, events, onRestart }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const complete = run?.status === 'succeeded';
  const created = events.filter((event) => event.event_type === 'storage.applied').length > 0;

  // Only the DSCC step used to be able to finish a run, so modes without it — provision-only and
  // verify-only — could never reach a completed state. Closing the run belongs here.
  const finish = async () => {
    if (!runId) return;
    setBusy(true);
    setError(null);
    try {
      await markComplete(runId);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <StepShell
      title="Finish"
      description="A record of what this run performed and the items handed over to other teams."
      state={complete ? 'complete' : 'action_required'}
      stateDetail={complete ? undefined : 'not closed yet'}
      error={error}
      onDismissError={() => setError(null)}
      footerNote="The run record remains on this workstation until a new run is started."
      actions={
        <>
          {!complete && runId && (
            <Button busy={busy} label="Mark run complete" onClick={finish} />
          )}
          <Button primary label="Start a new deployment" onClick={onRestart} />
        </>
      }
    >
      <InlineNotification
        tone={complete ? 'ok' : 'info'}
        title={complete ? `${run?.serial_number ?? 'The array'} is complete` : 'This run is not closed yet'}
        message={
          complete
            ? 'Everything this run was asked to do has been recorded.'
            : 'Return to any step marked Action required, or mark the run complete if there is nothing outstanding.'
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
