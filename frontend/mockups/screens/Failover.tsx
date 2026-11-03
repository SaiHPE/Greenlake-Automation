import { Box, DataTable, FormField, ResponsiveContext, Select, Text, TextInput } from 'grommet';
import { useContext, useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, CodeBlock, Confirmation, Guidance, Mark, Panel, RunState, StateIcon, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const TEST_GROUP = 'zz_rc_test_rcg';
const OTHER = 'Another group…';
const A = 'AlletraMP_D22U27';
const B = 'AlletraMP_E18U31';

interface Row { seq: number; title: string; cli: string; where: string; expected: string; p: string; s: string; took: string; outcome: RunState; outcomeLabel: string }

const SEQUENCE: Omit<Row, 'p' | 's' | 'took' | 'outcome' | 'outcomeLabel'>[] = [
  { seq: 0, title: 'Read both arrays', cli: 'showrcopy groups', where: '-', expected: 'Primary/Started on P, Secondary/Started on S, every volume Synced' },
  { seq: 1, title: 'Stop the group', cli: 'stoprcopygroup', where: 'P', expected: 'Stopped on both arrays' },
  { seq: 2, title: 'Fail over to the peer', cli: 'setrcopygroup failover', where: 'S', expected: 'Primary-Rev on S; Primary/Stopped on P' },
  { seq: 3, title: "The peer's volumes are now read/write", cli: '', where: '-', expected: 'recorded, not written to' },
  { seq: 4, title: 'Recover', cli: 'setrcopygroup recover', where: 'S', expected: 'Primary-Rev/Started on S; Secondary-Rev on P; syncing back to P' },
  { seq: 5, title: 'Wait until Synced', cli: 'showrcopy groups', where: '-', expected: 'every volume Synced (up to 15 min)' },
  { seq: 6, title: 'Restore the natural direction', cli: 'setrcopygroup restore', where: 'S', expected: 'Primary/Started on P; Secondary/Started on S; Synced' },
];

const AFTER: { p: string; s: string; took: string }[] = [
  { p: 'Primary/Started · 1/1 Synced', s: 'Secondary/Started · 1/1 Synced', took: '2 s · 19:50:02' },
  { p: 'Primary/Stopped', s: 'Secondary/Stopped', took: '3 s · 19:50:04' },
  { p: 'Primary/Stopped', s: 'Primary-Rev/Stopped', took: '1.3 s · 19:50:07' },
  { p: '—', s: 'read/write', took: '0 s · 19:50:08' },
  { p: 'Secondary-Rev/Started', s: 'Primary-Rev/Started', took: '4 s · 19:50:08' },
  { p: 'Secondary-Rev/Started · 1/1 Synced', s: 'Primary-Rev/Started · 1/1 Synced', took: '84 s · 19:50:12' },
  { p: 'Primary/Started · 1/1 Synced', s: 'Secondary/Started · 1/1 Synced', took: '5 s · 19:51:36' },
];

function rows(state: string): Row[] {
  return SEQUENCE.map((s, i) => {
    const after = AFTER[i];
    const pending = { p: '—', s: '—', took: '—' };
    if (state === 'passed') return { ...s, ...after, outcome: 'complete', outcomeLabel: 'OK' };
    if (state === 'running') {
      if (i < 4) return { ...s, ...after, outcome: 'complete', outcomeLabel: 'OK' };
      if (i === 4) return { ...s, ...pending, outcome: 'running', outcomeLabel: 'Running' };
      return { ...s, ...pending, outcome: 'not_started', outcomeLabel: '—' };
    }
    if (state === 'failed') {
      if (i < 2) return { ...s, ...after, outcome: 'complete', outcomeLabel: 'OK' };
      if (i === 2) return { ...s, p: 'Primary/Stopped', s: 'Secondary/Stopped', took: '30 s · 19:50:07', outcome: 'failed', outcomeLabel: 'Failed' };
      return { ...s, ...pending, outcome: 'not_started', outcomeLabel: 'Skipped' };
    }
    return { ...s, ...pending, outcome: 'not_started', outcomeLabel: '—' };
  });
}

function Failover({ state, setState }: { state: string; setState: (s: string) => void }) {
  const size = useContext(ResponsiveContext);
  const wide = size === 'large' || size === 'xlarge';
  const [authorised, setAuthorised] = useState(false);
  const [choice, setChoice] = useState(TEST_GROUP);
  const [typed, setTyped] = useState('');
  const other = choice === OTHER;
  const group = other ? typed.trim() || 'the group' : choice;
  const running = state === 'running';
  const passed = state === 'passed';
  const failed = state === 'failed';
  const next = (s: string) => () => setState(s);

  const primary: Action | undefined = running
    ? undefined
    : passed
      ? { label: 'Continue to Verify configuration' }
      : { label: failed ? 'Run the failover test again' : 'Run failover test', onClick: next('running'), blocked: other && !typed.trim() ? 'Type the name of the group to confirm it.' : undefined };
  const actions: Action[] = running ? [] : passed ? [{ label: 'Run the failover test again', onClick: next('running') }] : [{ label: 'Continue without the failover test' }];
  const confirmation: Confirmation | undefined = running || passed
    ? undefined
    : { label: `I understand this stops ${group}, fails it over to ${B}, recovers and restores it, and I authorise the test on both arrays.`, checked: authorised, onChange: setAuthorised };

  return (
    <AppFrame run={RUN} groups={rail('failover', passed ? 'complete' : failed ? 'failed' : running ? 'running' : 'action_required')} current="failover">
      <StepPage
        stepLabel={stepLabel('failover')}
        title="Failover test"
        description="Proves the copy on the peer can take over and production can come back: stop, fail over, recover, wait for the sync back, restore. One Remote Copy group, the array's own disaster-recovery actions."
        state={passed ? 'complete' : failed ? 'failed' : running ? 'running' : 'action_required'}
        stateLabel={passed ? 'Passed' : failed ? 'Failed at step 2' : running ? 'Step 4 of 6' : 'Not started'}
        primary={primary}
        actions={actions}
        confirmation={confirmation}
        guideOpen={state === 'choose'}
        activity={{
          last: passed ? '19:51:41  Failover test passed: back to Primary on D22U27' : failed ? '19:50:37  Step 2 failed: failover did not complete in 30 s' : running ? '19:50:08  Step 4, recover, issued on E18U31' : '19:49:50  Replication verified: 2 groups replicating',
          events: 30,
          commands: 58,
        }}
        guidance={
          <Guidance
            items={[
              { title: 'What it changes', body: `For the length of the test the chosen group is stopped, made primary on ${B}, synced back and restored. Hosts running on its primary volumes lose access meanwhile. The tool's own 1 GiB group ${TEST_GROUP} exists for exactly this.` },
              { title: 'Both arrays after every step', body: 'Roles, status and sync state are read from both arrays after each step and go into the as-built with the timings.' },
              { title: 'If a step fails', body: 'The test stops, shows both arrays as read and the documented way back. It never changes roles further on its own. Switchover (Peer Persistence) is not part of this test.' },
            ]}
          />
        }
      >
        {state === 'choose' && (
          <StatusLine state="action_required">
            This test changes roles on both arrays. Choose the group, tick the box in the footer, then run it. Nothing is changed until then.<Mark n={1} />
          </StatusLine>
        )}
        {running && (
          <StatusLine state="running" time="19:50:08">
            Step 4 of 6, Recover, issued on {B}. Waiting for the sync back; up to 15 minutes.<Mark n={1} />
          </StatusLine>
        )}
        {passed && (
          <StatusLine state="complete" time="19:51">
            Passed. {TEST_GROUP} is back to Primary on {A}, Secondary on {B}. The peer took over 1.3 s after the failover; every volume was Synced again 84 s after the recover.<Mark n={1} />
          </StatusLine>
        )}
        {failed && (
          <Box gap="small" flex={false}>
            <StatusLine state="failed" time="19:50">
              Failed at step 2: {B} did not report Primary-Rev within 30 s. Observed: Primary/Stopped on {A}, Secondary/Stopped on {B}. Roles were not changed further.<Mark n={1} />
            </StatusLine>
            <Panel title="The documented way back (the tool does not run this)">
              <CodeBlock lines={[`# on ${A}`, `startrcopygroup ${TEST_GROUP}`, `showrcopy groups ${TEST_GROUP}`]} a11yTitle="The way back" />
              <Text size="small" color="text-weak">Starts the group again in its natural direction. Check both arrays, then run the test again or continue without it.</Text>
            </Panel>
          </Box>
        )}

        {!passed && !running && (
          <Panel title="Which group">
            <Box direction="row" gap="medium" wrap align="start">
              <FormField label="Remote Copy group" htmlFor="fo-group" margin="none" help={`By default the tool's own test group. Groups this run created can be chosen; any other group needs its name typed back.`}>
                <Select id="fo-group" options={[TEST_GROUP, 'zz_rc_vvs_rcg', OTHER]} value={choice} onChange={({ option }) => setChoice(option)} />
              </FormField>
              {other && (
                <FormField label="Type the group's name to confirm" htmlFor="fo-typed" margin="none" help="Hosts on its primary volumes lose access for the length of the test.">
                  <TextInput id="fo-typed" value={typed} onChange={(e) => setTyped(e.target.value)} placeholder="group name" />
                </FormField>
              )}
            </Box>
          </Panel>
        )}

        <Panel title={<>The sequence<Mark n={2} /></>} right={<Text size="small" color="text-weak">P = {A} · S = {B}</Text>}>
          {/* below the large breakpoint the two reference columns go; what each array showed and the outcome stay */}
          <DataTable
            columns={[
              { property: 'seq', header: '#', render: (r: Row) => <Text size="small">{r.seq}</Text> },
              {
                property: 'title',
                header: 'Step',
                render: (r: Row) => (
                  <Box>
                    <Text size="small">{r.title}</Text>
                    {r.cli && <Text size="xsmall" color="text-weak" style={mono}>{r.cli}</Text>}
                  </Box>
                ),
              },
              ...(wide ? [
                { property: 'where', header: 'On', render: (r: Row) => <Text size="small">{r.where}</Text> },
                { property: 'expected', header: 'Expected after', render: (r: Row) => <Text size="small" color="text-weak">{r.expected}</Text> },
              ] : []),
              { property: 'p', header: 'P after', render: (r: Row) => <Text size="small">{r.p}</Text> },
              { property: 's', header: 'S after', render: (r: Row) => <Text size="small">{r.s}</Text> },
              { property: 'took', header: 'Took', align: 'end', render: (r: Row) => <Text size="small" textAlign="end">{r.took}</Text> },
              {
                property: 'outcome',
                header: 'Outcome',
                render: (r: Row) => (
                  <Box direction="row" gap="xsmall" align="center">
                    <StateIcon state={r.outcome} />
                    <Text size="small" weight={500}>{r.outcomeLabel}</Text>
                  </Box>
                ),
              },
            ]}
            data={rows(state)}
            primaryKey="seq"
          />
          {passed && <StatusIndicator state="complete" label="Data-loss bound: none (sync)." />}
        </Panel>
      </StepPage>
    </AppFrame>
  );
}

export const failover: Screen = {
  id: 'M12',
  title: 'Failover test',
  states: [
    { key: 'choose', label: 'Before the test' },
    { key: 'running', label: 'Running (step 4 of 6)' },
    { key: 'passed', label: 'Passed' },
    { key: 'failed', label: 'Failed at step 2' },
  ],
  notes: [
    'One line says what state the test is in. Before it runs, the warning is the top line: this test changes roles on both arrays. While it runs, a spinner and the step it is on. Afterwards, Passed with the two numbers that matter, or Failed with what was observed and the way back as commands to copy.',
    'The sequence table is the same before, during and after: the seven steps, the expected state, what each array showed, how long it took, the outcome. Rows fill in as the test runs.',
  ],
  keeps: [
    ['Which group: the Select with the test group, the run\'s groups and Another group… (typed back)', 'Which group panel'],
    ['The role-change warning', 'The top line before the run'],
    ['Authorise tick', 'Footer, next to Run failover test'],
    ['Run failover test / Run the failover test again', 'Footer, right (green); afterwards beside Continue'],
    ['The sequence table (expected, P after, S after, took, outcome)', 'The sequence panel'],
    ['Passed / Failed result with observed state and the documented way back', 'Top line, plus a panel with the commands'],
    ['Continue without the failover test', 'Footer, beside the green button'],
  ],
  render: (state, setState) => <Failover state={state} setState={setState} />,
};
