import { Box, Button, Heading, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { markComplete, RunEvent, RunRecord } from '../api';
import { isOf, latestOf } from '../events';
import { DocList, Section } from '../ui/blocks';
import { ActivityTimeline } from '../ui/primitives';
import { PlainPage, runDocuments, when } from '../ui/RunPages';
import { NoValue } from '../ui/status';
import { mergedRemovals, RemovalSet, RemovalSets } from '../ui/RemovalSets';

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
  // A failed apply can have made objects before it stopped (SPEC-007 R6), so both kinds of apply count.
  const applies = events
    .filter((event) => isOf(event, 'storage.applied', 'storage.apply.failed'))
    .filter((event) => !!event.data?.result);
  const created = applies.some((event) => {
    const result = event.data.result;
    return (result.removals ?? []).length > 0 || (result.outcomes ?? []).some((outcome) => outcome.status === 'created');
  });
  // The answer follows the LAST apply: a run whose apply found everything already there is provisioned.
  const lastApply = applies[applies.length - 1];
  const provisioned = !lastApply
    ? 'Not in this run'
    : lastApply.event_type === 'storage.apply.failed'
      ? created
        ? 'Partly. The last attempt stopped before it finished. Provision storage shows what was created and the commands to remove it.'
        : 'No. The last attempt stopped before it created anything. Provision storage says why.'
      : created
        ? 'Yes'
        : 'Yes. Everything was already on the array.';
  // The removal sets, as the two steps show them: every apply's undo, failed ones included (SPEC-007 R6).
  const storageResults = applies.map((event) => event.data.result);
  const storageRemovals = storageResults.flatMap((r) => r.removals ?? []);
  const storageNotes = storageResults.flatMap((r) => r.removal_notes ?? []).filter((note, i, all) => all.indexOf(note) === i);
  const replicationResults = events.flatMap((e) =>
    isOf(e, 'replication.applied', 'replication.apply.failed') && e.data?.result ? [e.data.result] : [],
  );
  const replicationRemovals = mergedRemovals(replicationResults);
  const pair = latestOf(events, 'replication.previewed')?.data?.report;
  const lines = (n: number) => `${n} line${n === 1 ? '' : 's'}`;
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
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
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
      error={error ? { title: 'The run could not be marked complete', message: error } : null}
      onDismissError={() => setError(null)}
      status={{
        state: complete ? 'complete' : 'action_required',
        title: complete ? `${run?.serial_number ?? 'The array'} is complete` : 'This run is not closed yet',
        message: complete
          ? 'Everything this run was asked to do is recorded. The run stays in Your runs with its documents.'
          : 'Go back to any step marked Action required, or mark the run complete if nothing is outstanding.',
      }}
      // warnings recorded during the run are notes under the status line (SPEC-030 R2)
      notes={run?.warnings ?? []}
    >

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
            {run?.serial_number ? <Text>{run.serial_number}</Text> : <NoValue />}
          </NameValuePair>
          <NameValuePair name="Mode">
            {modeLabel ? <Text>{modeLabel}</Text> : <NoValue />}
          </NameValuePair>
          <NameValuePair name="Storage provisioned">
            <Text>{provisioned}</Text>
          </NameValuePair>
        </NameValueList>
      </Section>

      {runId && storageResults.length > 0 && (
        <Section
          title="Provision storage: removal command set"
          summary={`${lines(new Set(storageRemovals.map((r) => r.command)).size)} that undo what this run created on ${run?.serial_number ?? 'the array'}`}
        >
          <RemovalSet removals={storageRemovals} notes={storageNotes} runId={runId} serial={run?.serial_number} />
        </Section>
      )}

      {runId && replicationResults.length > 0 && (
        <Section
          title="Replication: removal command set"
          summary={`${lines(replicationRemovals.removals_a.length)} for ${pair?.primary.name || 'array A'}, then ${lines(replicationRemovals.removals_b.length)} for ${pair?.peer.name || 'array B'}`}
        >
          <RemovalSets result={replicationRemovals} runId={runId} a={pair?.primary.name || 'array A'} b={pair?.peer.name || 'array B'} />
        </Section>
      )}

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
