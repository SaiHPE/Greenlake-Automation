import { Box, Button, CheckBox, DataTable, FormField, Select, Text, TextInput } from 'grommet';
import { useState } from 'react';
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
import { ContinueButton, InlineNotification, Surface } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';

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
  pending: { state: 'not_started', label: '—' },
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
  if (!side) return '—';
  if (!side.present) return 'not on the array';
  const bits = [`${side.role}/${side.status}`, `${side.synced}/${side.volumes} Synced`];
  if (side.last_sync && side.last_sync !== 'NA') bits.push(`last sync ${side.last_sync}`);
  return bits.join(' · ');
}
type FailoverSideLike = { present: boolean; role: string; status: string; synced: number; volumes: number; last_sync: string };

function when(iso: string): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleTimeString();
}

export function FailoverTestStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [authorised, setAuthorised] = useState(false);
  const [choice, setChoice] = useState<string>(TEST_GROUP);
  const [typed, setTyped] = useState('');
  const running = run?.status === 'running';

  const report = latest<ReplicationReport>(events, ['replication.previewed'], 'report');
  const result = latest<ReplicationResult>(events, ['replication.applied', 'replication.apply.failed'], 'result');
  const record = latest<FailoverRecord>(events, ['failover.completed', 'failover.failed'], 'record');
  const started = events.some((e) => e.event_type === 'failover.started');
  const aName = report?.primary.name || 'this array';
  const bName = report?.peer.name || 'the peer';

  // R1: offered by default — the tool's test group and the groups this run created. Anything else is typed.
  const created = result?.groups_created ?? [];
  const onArray = new Set((report?.primary.groups ?? []).map((g) => g.name));
  const offered = [TEST_GROUP, ...created.filter((g) => g !== TEST_GROUP)];
  const options = [...offered, OTHER];
  const other = choice === OTHER;
  const group = other ? typed.trim() : choice;
  const knownMissing = group && onArray.size > 0 && !onArray.has(group);
  const canRun = !!group && authorised && !running && (!other || typed.trim().length > 0);

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const rows: FailoverStepRecord[] = record
    ? record.steps
    : SEQUENCE.map((s) => ({ ...s, action: '', cli: '', started_at: '', ended_at: '', seconds: null, primary: null, peer: null, outcome: 'pending', detail: '' }));

  return (
    <StepShell
      title="Failover test"
      description="Proves the DR copy can take over and production can come back: stop → fail over to the peer → recover → wait for the sync back → restore, on one Remote Copy group, over the array’s own disaster-recovery actions. Both arrays are read after every step; roles and timings go into the as-built."
      stateDetail={record ? (record.result === 'passed' ? 'passed' : record.result === 'failed' ? `failed at step ${record.failed_step}` : 'not started') : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Choose the group, tick the authorisation and run the test. Nothing is changed until then."
      footerNote="Switchover (Peer Persistence) is not part of this test. If a step fails, the test stops, shows both arrays as read and the documented way back; it never changes roles further on its own."
      gate={
        !record && !running
          ? {
              title: 'This test changes roles on both arrays',
              message: `For the duration of the test the chosen group is stopped, made primary on ${bName}, synced back and restored. Hosts running on its primary volumes lose access. The tool’s own 1 GiB test group exists for exactly this.`,
            }
          : null
      }
      actions={
        <>
          <Button busy={running} label={record ? 'Run the failover test again' : 'Run failover test'} disabled={!canRun} onClick={call(() => failoverTest(runId, group, other ? typed.trim() : null))} />
          <ContinueButton onClick={onDone} suffix={record?.result === 'passed' ? '' : 'without the failover test'} />
        </>
      }
    >
      <Surface title="Which group" description={`The test runs on one group. By default the tool’s own test group ${TEST_GROUP}; groups this run created can be chosen. Any other group needs its name typed back.`}>
        <Box direction="row" gap="medium" wrap align="end">
          <FormField label="Remote Copy group" margin="none">
            <Select options={options} value={choice} onChange={({ option }) => setChoice(option)} disabled={running} />
          </FormField>
          {other && (
            <FormField label="Type the group’s name to confirm" margin="none" help="Hosts on its primary volumes lose access for the duration of the test.">
              <TextInput value={typed} onChange={(e) => setTyped(e.target.value)} placeholder="group name" disabled={running} />
            </FormField>
          )}
        </Box>
        {knownMissing && (
          <InlineNotification tone="warning" title={`${group} was not on ${aName} when the arrays were last read`} message="Read both arrays again on the Replication step if it has been created since; otherwise the test stops at step 0 without changing anything." />
        )}
        <CheckBox
          label={`I understand this stops ${group || 'the group'}, fails it over to ${bName}, recovers and restores it, and I authorise the test on ${aName} and ${bName}.`}
          checked={authorised}
          disabled={running}
          onChange={(event) => setAuthorised(event.target.checked)}
        />
      </Surface>

      <Surface title="The sequence" description="P = this array, S = the peer. Every role change is one disaster-recovery action over WSAPI, issued on the array named in On; the array mirrors it to its partner.">
        {record?.result === 'passed' && (
          <InlineNotification
            tone="ok"
            title={`Passed — ${record.group} is back to Primary on ${record.primary_array}, Secondary on ${record.peer_array}`}
            message={`${record.time_to_failover_s != null ? `The peer took over ${record.time_to_failover_s} s after the failover was issued` : ''}${record.time_to_synced_s != null ? `; every volume was Synced again ${record.time_to_synced_s} s after the recover` : ''}.${record.data_loss_bound ? ` Data-loss bound (async): ${record.data_loss_bound}.` : ''}`}
          />
        )}
        {record && record.result !== 'passed' && (
          <InlineNotification
            tone="critical"
            title={record.result === 'aborted' ? 'Not started — the group was not in its normal state' : `Failed at step ${record.failed_step}`}
            message={
              <Box gap="xsmall">
                <Text size="small">{record.error}</Text>
                {record.observed_state && <Text size="small">Observed: {record.observed_state}</Text>}
                {record.recovery_action && (
                  <Box gap="xxsmall">
                    <Text size="small" weight={600}>The documented way back (the tool does not run this):</Text>
                    <Text size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{record.recovery_action}</Text>
                  </Box>
                )}
              </Box>
            }
          />
        )}
        {running && started && !record && <StatusIndicator state="running" label="Running — the activity log below shows each step as it happens." />}
        <DataTable
          columns={[
            { property: 'seq', header: '#', render: (s: FailoverStepRecord) => <Text size="small">{s.seq}</Text> },
            { property: 'title', header: 'Step', render: (s: FailoverStepRecord) => (
              <Box>
                <Text size="small">{s.title}</Text>
                {s.cli && <Text size="xsmall" color="text-weak" style={mono}>{s.cli}</Text>}
              </Box>
            ) },
            { property: 'where', header: 'On', render: (s: FailoverStepRecord) => <Text size="small">{s.where}</Text> },
            { property: 'expected', header: 'Expected after', render: (s: FailoverStepRecord) => <Text size="small" color="text-weak">{s.expected}</Text> },
            { property: 'primary', header: 'P after', render: (s: FailoverStepRecord) => <Text size="small">{sideText(s.primary)}</Text> },
            { property: 'peer', header: 'S after', render: (s: FailoverStepRecord) => <Text size="small">{sideText(s.peer)}</Text> },
            { property: 'seconds', header: 'Took', render: (s: FailoverStepRecord) => <Text size="small">{s.seconds == null ? '—' : `${s.seconds} s`}{s.started_at ? ` · ${when(s.started_at)}` : ''}</Text> },
            { property: 'outcome', header: 'Outcome', render: (s: FailoverStepRecord) => <StatusIndicator state={OUTCOME[s.outcome].state} label={OUTCOME[s.outcome].label} /> },
          ]}
          data={rows}
          primaryKey="seq"
          a11yTitle="The failover test sequence: one row per step, with the expected state, what each array showed afterwards, the time it took and the outcome"
        />
        {record?.steps.some((s) => s.detail) && (
          <Box gap="xxsmall">
            {record.steps.filter((s) => s.detail).map((s) => (
              <Text key={s.seq} size="xsmall" color="text-weak">Step {s.seq}: {s.detail}</Text>
            ))}
          </Box>
        )}
      </Surface>
    </StepShell>
  );
}
