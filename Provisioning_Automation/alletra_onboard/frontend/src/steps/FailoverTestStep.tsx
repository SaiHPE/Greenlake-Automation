import { Box, DataTable, FormField, ResponsiveContext, Select, Text, TextInput } from 'grommet';
import { useContext, useState } from 'react';
import {
  FailoverOutcome,
  FailoverRecord,
  FailoverStepRecord,
  ReplicationReport,
  ReplicationResult,
  RunEvent,
  RunRecord,
  failoverTest,
} from '../api';
import { CodeBlock, Guidance, Panel, StatusLine } from '../ui/blocks';
import { InlineNotification } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const TEST_GROUP = 'zz_rc_test_rcg';
const OTHER = 'Another group…';
const mono = { fontFamily: 'Consolas, Menlo, monospace' } as const;

const OUTCOME: Record<FailoverOutcome, { state: StepState; label: string }> = {
  pending: { state: 'not_started', label: '--' },
  ok: { state: 'complete', label: 'OK' },
  failed: { state: 'failed', label: 'Failed' },
  skipped: { state: 'not_started', label: 'Skipped' },
};

/** The R2 table before anything has run: the seven steps the test will take. */
const SEQUENCE: Array<Pick<FailoverStepRecord, 'seq' | 'title' | 'where' | 'expected'>> = [
  { seq: 0, title: 'Read both arrays', where: '-', expected: 'Primary/Started on P, Secondary/Started on S, every volume Synced' },
  { seq: 1, title: 'Stop the group', where: 'P', expected: 'Stopped on both arrays' },
  { seq: 2, title: 'Fail over to the peer', where: 'S', expected: 'Primary-Rev on S; Primary/Stopped on P' },
  { seq: 3, title: 'The peer’s volumes are now read/write', where: '-', expected: 'recorded, not written to' },
  { seq: 4, title: 'Recover', where: 'S', expected: 'Primary-Rev/Started on S; Secondary-Rev on P; syncing back to P' },
  { seq: 5, title: 'Wait until Synced', where: '-', expected: 'every volume Synced (up to 15 min)' },
  { seq: 6, title: 'Restore the natural direction', where: 'S', expected: 'Primary/Started on P; Secondary/Started on S; Synced' },
];

function latest<T>(events: RunEvent[], types: string[], key: string): T | null {
  const event = [...events].reverse().find((item) => types.includes(item.event_type));
  return (event?.data?.[key] as T) ?? null;
}

function sideText(side: FailoverSideLike | null): string {
  if (!side) return '--';
  if (!side.present) return 'not on the array';
  const bits = [`${side.role}/${side.status}`, `${side.synced}/${side.volumes} Synced`];
  if (side.last_sync && side.last_sync !== 'NA') bits.push(`last sync ${side.last_sync}`);
  return bits.join(' · ');
}
type FailoverSideLike = { present: boolean; role: string; status: string; synced: number; volumes: number; last_sync: string };

function when(iso: string): string {
  if (!iso) return '--';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleTimeString();
}

export function FailoverTestStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const wide = useContext(ResponsiveContext) === 'large' || useContext(ResponsiveContext) === 'xlarge';
  const [error, setError] = useState<string | null>(null);
  // started_at of a passed test the operator chose to run again
  const [again, setAgain] = useState<string | null>(null);
  const [authorised, setAuthorised] = useState(false);
  const [choice, setChoice] = useState<string>(TEST_GROUP);
  const [typed, setTyped] = useState('');
  const running = run?.status === 'running';

  const report = latest<ReplicationReport>(events, ['replication.previewed'], 'report');
  const result = latest<ReplicationResult>(events, ['replication.applied', 'replication.apply.failed'], 'result');
  const record = latest<FailoverRecord>(events, ['failover.completed', 'failover.failed'], 'record');
  const lastStart = events.map((e) => e.event_type).lastIndexOf('failover.started');
  const lastEnd = Math.max(...['failover.completed', 'failover.failed'].map((t) => events.map((e) => e.event_type).lastIndexOf(t)));
  const testing = running && lastStart > lastEnd;
  const aName = report?.primary.name || 'this array';
  const bName = report?.peer.name || 'the peer';

  // R1: offered by default: the tool's test group and the groups this run created. Anything else is typed.
  const created = result?.groups_created ?? [];
  const onArray = new Set((report?.primary.groups ?? []).map((g) => g.name));
  const offered = [TEST_GROUP, ...created.filter((g) => g !== TEST_GROUP)];
  const options = [...offered, OTHER];
  const other = choice === OTHER;
  const group = other ? typed.trim() : choice;
  // groups this run created were made after the read, so their absence from it says nothing
  const knownMissing = group && onArray.size > 0 && !onArray.has(group) && !created.includes(group);

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const rows: FailoverStepRecord[] = record && !testing
    ? record.steps
    : SEQUENCE.map((s) => ({ ...s, action: '', cli: '', started_at: '', ended_at: '', seconds: null, primary: null, peer: null, outcome: 'pending', detail: '' }));

  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const passed = !testing && record?.result === 'passed' && record.started_at !== again;
  const shown = testing ? null : record;
  const runTest: FooterAction = {
    label: record ? 'Run the failover test again' : 'Run failover test',
    busy: running,
    onClick: passed
      ? () => setAgain(record?.started_at ?? '')
      : call(async () => {
          await failoverTest(runId, group, other ? typed.trim() : null);
          setAuthorised(false);
        }),
    blocked: !group
      ? 'Choose the group to test first.'
      : other && !typed.trim()
        ? "Type the group's name to confirm it first."
        : undefined,
  };
  const skip: FooterAction = { label: record?.result === 'passed' ? next : `${next} without the failover test`, onClick: onDone };
  const primary = passed ? { label: next, onClick: onDone } : testing ? undefined : runTest;
  // A test already passed: running it again goes back to choosing the group and authorising, never straight to the arrays.
  const buttons = passed ? [runTest] : testing ? [] : [skip];

  const columns = [
    { property: 'seq', header: '#', render: (s: FailoverStepRecord) => <Text size="small">{s.seq}</Text> },
    {
      property: 'title',
      header: 'Step',
      render: (s: FailoverStepRecord) => (
        <Box>
          <Text size="small">{s.title}</Text>
          {s.cli && <Text size="xsmall" color="text-weak" style={mono}>{s.cli}</Text>}
        </Box>
      ),
    },
    ...(wide
      ? [
          { property: 'where', header: 'On', render: (s: FailoverStepRecord) => <Text size="small">{s.where}</Text> },
          { property: 'expected', header: 'Expected after', render: (s: FailoverStepRecord) => <Text size="small" color="text-weak">{s.expected}</Text> },
        ]
      : []),
    { property: 'primary', header: 'P after', render: (s: FailoverStepRecord) => <Text size="small">{sideText(s.primary)}</Text> },
    { property: 'peer', header: 'S after', render: (s: FailoverStepRecord) => <Text size="small">{sideText(s.peer)}</Text> },
    {
      property: 'seconds',
      header: 'Took',
      render: (s: FailoverStepRecord) => (
        <Text size="small">
          {s.seconds == null ? '--' : `${s.seconds} s`}
          {s.started_at ? ` · ${when(s.started_at)}` : ''}
        </Text>
      ),
    },
    { property: 'outcome', header: 'Outcome', render: (s: FailoverStepRecord) => <StatusIndicator state={OUTCOME[s.outcome].state} label={OUTCOME[s.outcome].label} /> },
  ];

  return (
    <StepShell
      title="Failover test"
      description="Proves the DR copy can take over and production can come back, on one Remote Copy group, using the array's own disaster-recovery actions. Both arrays are read after every step; roles and timings go into the as-built."
      stateDetail={
        testing
          ? 'test running'
          : shown
            ? shown.result === 'passed'
              ? 'passed'
              : shown.result === 'failed'
                ? `failed at step ${shown.failed_step}`
                : 'not started'
            : undefined
      }
      error={error}
      onDismissError={() => setError(null)}
      primary={primary}
      buttons={buttons}
      // Changes roles on both arrays: an explicit authorisation, not a click.
      confirmation={
        passed || testing
          ? undefined
          : {
              label: `I understand this stops ${group || 'the group'}, fails it over to ${bName}, recovers and restores it, and I authorise the test on ${aName} and ${bName}.`,
              checked: authorised,
              onChange: setAuthorised,
            }
      }
      guideOpen={!record}
      guidance={
        <Guidance
          items={[
            { title: 'The sequence', body: 'Stop the group, fail over to the peer, recover, wait for the sync back, restore the natural direction.' },
            { title: 'Hosts lose access', body: `For the duration of the test the chosen group is stopped and made primary on ${bName}. The tool's own 1 GiB test group ${TEST_GROUP} exists for exactly this.` },
            { title: 'If a step fails', body: 'The test stops, shows both arrays as read and the documented way back. It never changes roles further on its own.' },
            { title: 'Not part of this test', body: 'Switchover (Peer Persistence).' },
          ]}
        />
      }
    >
      {testing && (
        <StatusLine state="running" title="Failover test running">
          Each step appears in Activity, below, as it happens. The sync back can take up to 15 minutes.
        </StatusLine>
      )}
      {!running && !shown && (
        <StatusLine state="action_required" title="This test changes roles on both arrays">
          Choose the group, tick the authorisation and run the test. Nothing is changed until then.
        </StatusLine>
      )}
      {passed && shown && (
        <StatusLine state="complete" title={`Passed: ${shown.group} is back to Primary on ${shown.primary_array}, Secondary on ${shown.peer_array}`}>
          {`${shown.time_to_failover_s != null ? `The peer took over ${shown.time_to_failover_s} s after the failover was issued` : 'The peer took over'}${shown.time_to_synced_s != null ? `; every volume was Synced again ${shown.time_to_synced_s} s after the recover` : ''}.${shown.data_loss_bound ? ` Data-loss bound (async): ${shown.data_loss_bound}.` : ''}`}
        </StatusLine>
      )}
      {shown && shown.result !== 'passed' && (
        <StatusLine state="failed" title={shown.result === 'aborted' ? 'Not started: the group was not in its normal state' : `Failed at step ${shown.failed_step}`}>
          <Box gap="xsmall">
            <Text size="small">{shown.error}</Text>
            {shown.observed_state && <Text size="small">Observed: {shown.observed_state}</Text>}
          </Box>
        </StatusLine>
      )}
      {shown && shown.result !== 'passed' && shown.recovery_action && (
        <Panel title="The documented way back" description="The tool does not run this. Run it on the array named, then read both arrays again on the Replication step.">
          <CodeBlock label="The documented way back" lines={shown.recovery_action.split('\n')} />
        </Panel>
      )}

      {!passed && !testing && (
        <Panel
          title="Which group"
          description={`The test runs on one group. By default the tool's own test group ${TEST_GROUP}; groups this run created can be chosen. Any other group needs its name typed back.`}
        >
          <Box direction="row" gap="medium" wrap align="end" flex={false}>
            <FormField label="Remote Copy group" htmlFor="failover-group" margin="none">
              <Select id="failover-group" options={options} value={choice} onChange={({ option }) => setChoice(option)} disabled={running} />
            </FormField>
            {other && (
              <FormField label="Type the group's name to confirm" htmlFor="failover-typed" margin="none" help="Hosts on its primary volumes lose access for the duration of the test.">
                <TextInput id="failover-typed" value={typed} onChange={(e) => setTyped(e.target.value)} placeholder="group name" disabled={running} />
              </FormField>
            )}
          </Box>
          {knownMissing && (
            <InlineNotification
              tone="warning"
              title={`${group} was not on ${aName} when the arrays were last read`}
              message="Read both arrays again on the Replication step if it has been created since; otherwise the test stops at step 0 without changing anything."
            />
          )}
        </Panel>
      )}

      <Panel
        title={shown ? 'What each step did' : 'The sequence'}
        description="P = this array, S = the peer. Every role change is one disaster-recovery action over WSAPI, issued on the array named in On; the array mirrors it to its partner."
      >
        <DataTable
          columns={columns}
          data={rows}
          primaryKey="seq"
          a11yTitle="The failover test sequence: one row per step, with the expected state, what each array showed afterwards, the time it took and the outcome"
        />
        {shown?.steps.some((s) => s.detail) && (
          <Box gap="xxsmall" flex={false}>
            {shown.steps
              .filter((s) => s.detail)
              .map((s) => (
                <Text key={s.seq} size="xsmall" color="text-weak">
                  Step {s.seq}: {s.detail}
                </Text>
              ))}
          </Box>
        )}
      </Panel>
    </StepShell>
  );
}
