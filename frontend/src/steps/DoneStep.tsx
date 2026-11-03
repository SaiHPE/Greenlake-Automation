import { Box, Button, Heading, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { markComplete, RunEvent, RunRecord } from '../api';
import { DocList, Section, StatusLine } from '../ui/blocks';
import { ActivityTimeline, NotesList } from '../ui/primitives';
import { PlainPage, runDocuments, when } from '../ui/RunPages';

interface Props {
  runId: string | null;
  run: RunRecord | null;
  events: RunEvent[];
  modeLabel: string;
  onRestart: () => void;
  onHome: () => void;
}

/** The end of the run, as a hand-over page: what was done, the files, and what is still open. */
export function DoneStep({ runId, run, events, modeLabel, onRestart, onHome }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const complete = run?.status === 'succeeded';
  const created = events.filter((event) => event.event_type === 'storage.applied').length > 0;
  const started = events.find((e) => e.event_type === 'run.created');
  const last = events[events.length - 1];

  // Only the DSCC step used to be able to finish a run, so modes without it (provision-only and
  // verify-only) could never reach a completed state. Closing the run belongs here.
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

  const subtitle = [
    run?.serial_number,
    modeLabel,
    started ? `started ${when(started.created_at)}` : '',
    last ? `last activity ${when(last.created_at)}` : '',
  ].filter(Boolean).join(' · ');

  return (
    <PlainPage
      title={complete ? 'Done' : 'Finish'}
      subtitle={subtitle}
      parent={{ label: 'Your runs', onClick: onHome }}
      actions={
        <Box direction="row" gap="small" wrap justify="end">
          {complete ? (
            <Button primary label="Start a new run" onClick={onRestart} />
          ) : (
            <>
              <Button label="Start a new run" onClick={onRestart} />
              {runId && <Button primary busy={busy} label="Mark run complete" onClick={finish} />}
            </>
          )}
        </Box>
      }
    >
      {error && (
        <StatusLine state="failed" title="The run could not be marked complete" onClose={() => setError(null)}>
          {error}
        </StatusLine>
      )}
      <StatusLine
        state={complete ? 'complete' : 'action_required'}
        title={complete ? `${run?.serial_number ?? 'The array'} is complete` : 'This run is not closed yet'}
      >
        {complete
          ? 'Everything this run was asked to do is recorded. The run stays in Your runs with its documents.'
          : 'Go back to any step marked Action required, or mark the run complete if nothing is outstanding.'}
      </StatusLine>

      {run?.warnings?.length ? (
        <StatusLine state="action_required" title="Warnings recorded during this run">
          <NotesList notes={run.warnings} />
        </StatusLine>
      ) : null}

      {runId && (
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">
            Hand-over package
          </Heading>
          <DocList items={runDocuments(runId, run, events)} label="Documents of this run" />
        </Box>
      )}

      <Section title="Summary" summary={`${run?.serial_number ?? '--'} · ${modeLabel}`} open>
        <NameValueList nameProps={{ width: 'small' }}>
          <NameValuePair name="Array">
            <Text>{run?.serial_number ?? '--'}</Text>
          </NameValuePair>
          <NameValuePair name="Mode">
            <Text>{modeLabel || '--'}</Text>
          </NameValuePair>
          <NameValuePair name="Storage provisioned">
            <Text>{created ? 'Yes' : 'Not in this run'}</Text>
          </NameValuePair>
        </NameValueList>
      </Section>

      <Section title="Run timeline" summary={`${events.length} event${events.length === 1 ? '' : 's'}, in order`}>
        <ActivityTimeline events={events} />
      </Section>

      <Text size="small" color="text-weak">
        The run record stays on this workstation. Diagnostic screenshots, if any were captured, are stored under
        .alletra_onboard/artifacts.
      </Text>
    </PlainPage>
  );
}
