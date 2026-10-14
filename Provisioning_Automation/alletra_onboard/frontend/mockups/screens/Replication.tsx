import { Box, Button, DataTable, Text } from 'grommet';
import { Connect } from 'grommet-icons';
import { useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { COMMANDS, EXISTING_GROUPS, PLAN, RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, CodeBlock, Confirmation, DoneList, EmptyState, Guidance, Mark, Panel, PartsBar, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const PARTS = ['Read both arrays', 'Check the link', 'Review the plan', 'Configure', 'Verify'];
const PART_OF: Record<string, number> = { read: 0, link: 1, 'link-over': 1, plan: 2, configured: 3, verified: 4 };

function LinkTable({ ms }: { ms: string }) {
  const rows = [
    { a: '0:4:3 · 10.54.122.92', b: '0:4:3 · 10.54.154.192', ms, lost: '0 %' },
    { a: '1:4:3 · 10.54.122.93', b: '1:4:3 · 10.54.154.193', ms, lost: '0 %' },
  ];
  return (
    <DataTable
      columns={[
        { property: 'a', header: 'From D22U27', render: (r) => <Text size="small" style={mono}>{r.a}</Text> },
        { property: 'b', header: 'To E18U31', render: (r) => <Text size="small" style={mono}>{r.b}</Text> },
        { property: 'ms', header: 'Latency', render: (r) => <Text size="small" weight={600}>{r.ms} ms</Text> },
        { property: 'lost', header: 'Pings lost', render: (r) => <Text size="small" color="text-weak">{r.lost}</Text> },
      ]}
      data={rows}
      primaryKey="a"
    />
  );
}

function Replication({ state, setState }: { state: string; setState: (s: string) => void }) {
  const [accept, setAccept] = useState(false);
  const [authorised, setAuthorised] = useState(false);
  const [showCalls, setShowCalls] = useState(false);
  const at = PART_OF[state];
  const verified = state === 'verified';
  const over = state === 'link-over';
  const next = (s: string) => () => setState(s);

  const primary: Action = {
    read: { label: 'Read both arrays', onClick: next('link') },
    link: { label: 'Check the link', onClick: next('plan') },
    'link-over': { label: 'Continue to the plan', onClick: next('plan') },
    plan: { label: 'Configure replication', onClick: next('configured') },
    configured: { label: 'Verify replication', onClick: next('verified') },
    verified: { label: 'Continue to Failover test' },
  }[state] as Action;
  const confirmation: Confirmation | undefined = {
    'link-over': { label: 'Continue anyway: I accept the measured latency of 12 ms for sync replication.', checked: accept, onChange: setAccept },
    plan: { label: 'I have reviewed the plan and authorise these changes on both arrays.', checked: authorised, onChange: setAuthorised },
  }[state as 'link-over' | 'plan'];
  const actions: Action[] = !verified && state !== 'configured' ? [{ label: 'Continue without replication' }] : [];

  const done: { text: string; again?: string; detail?: React.ReactNode }[] = [];
  if (at > 0) done.push({ text: 'Read both arrays: partnered over 2 of 2 links each way.', again: 'Read again',
    detail: <Text size="small">Target AlletraMP_E18U31 on both arrays, policy mirror_config, found by link address. Remote Copy started on both.</Text> });
  if (at > 1) done.push({ text: over || accept ? 'Link: 12 ms, over the 10 ms sync limit. You chose to continue.' : 'Link: 0.4 ms on 2 links. Sync allows 10 ms.',
    again: 'Check again', detail: <LinkTable ms={over || accept ? '12' : '0.4'} /> });
  if (at > 2) done.push({ text: 'Plan approved at 19:31: 6 objects, 12 commands.', detail: <Text size="small" style={mono}>{PLAN.map((p) => p.name).join(' · ')}</Text> });
  if (at > 3) done.push({ text: 'Configured at 19:32: 12 writes done, both groups started.',
    detail: <Box direction="row" gap="small"><Button size="small" label="Copy the removal commands for A" /><Button size="small" label="Copy the removal commands for B" /></Box> });

  return (
    <AppFrame run={RUN} groups={rail('replicate', verified ? 'complete' : 'action_required')} current="replicate">
      <StepPage
        stepLabel={stepLabel('replicate')}
        title="Replication"
        description="Remote Copy of this run's volume sets to the peer array AlletraMP_E18U31."
        state={verified ? 'complete' : 'action_required'}
        stateLabel={verified ? 'Replicating' : `Part ${at + 1} of 5`}
        primary={primary}
        actions={actions}
        confirmation={confirmation}
        guideOpen={state === 'read'}
        top={
          <Box direction="row" align="center" flex={false}>
            <PartsBar parts={PARTS} at={at} doneAll={verified} />
            <Mark n={1} />
          </Box>
        }
        activity={{ last: verified ? '19:33:10  Verified: 2 groups replicating, links up' : '19:30:02  Read AlletraMP_D22U27 and AlletraMP_E18U31', events: 11 + at * 3, commands: 22 + at * 10 }}
        guidance={
          <Guidance
            items={[
              { title: 'What this step does', body: 'One Remote Copy group per volume set on the Replication tab, over the partnership the two arrays already have. The peer creates the secondary volumes itself.' },
              { title: 'Nothing is written until you approve', body: 'Reading, the link check and the plan change nothing. Only Configure replication writes, and only what the plan shows.' },
              { title: "HPE's limits over RCIP", body: 'Round-trip latency: sync 10 ms or less, async 200 ms or less (RCIP = Remote Copy over IP).' },
              { title: 'Groups already there', body: 'Groups this run did not create are listed and never changed, stopped or removed.' },
            ]}
          />
        }
      >
        {done.length > 0 && (
          <Box flex={false}>
            <DoneList items={done} />
            <Mark n={2} />
          </Box>
        )}

        {state === 'read' && (
          <EmptyState icon={<Connect size="large" color="icon-weak" />} title="Not read yet">
            Read both arrays to see the partnership, the links and the groups already there. Reading changes nothing.
          </EmptyState>
        )}

        {(state === 'link' || over) && (
          <Panel title="Check the link">
            {state === 'link' ? (
              <Text size="small">
                checkrclink measures the latency between the two arrays' replication ports: a test server on AlletraMP_E18U31, a test client here,
                stopped as soon as the latency is printed. About 10 seconds per link.
              </Text>
            ) : (
              <Box gap="small" flex={false}>
                <StatusLine state="action_required" time="19:30">Latency 12 ms on 2 links: over the 10 ms limit for sync.<Mark n={5} /></StatusLine>
                <LinkTable ms="12" />
                <Text size="small" color="text-weak">To continue regardless, tick the box next to the green button. Your choice is written in the result and the as-built document.</Text>
              </Box>
            )}
          </Panel>
        )}

        {state === 'plan' && (
          <Panel title="Review the plan" right={<Text size="small" color="text-weak">6 to create · 0 already there · 0 conflicts</Text>}>
            <DataTable
              columns={[
                { property: 'kind', header: 'Kind', render: (p) => <Text size="small">{p.kind}</Text> },
                { property: 'name', header: 'Name', render: (p) => <Text size="small" style={mono}>{p.name}</Text> },
                { property: 'on', header: 'On', render: (p) => <Text size="small">{p.on}</Text> },
                { property: 'action', header: 'Action', render: () => <Text size="small" weight={500}>Create</Text> },
                { property: 'detail', header: 'Detail', render: (p) => <Text size="small" color="text-weak">{p.detail}</Text> },
              ]}
              data={PLAN}
              primaryKey="name"
            />
            <Text size="xsmall" color="text-weak">A = AlletraMP_D22U27 (this array), B = AlletraMP_E18U31 (the peer).</Text>
            <Box direction="row" gap="small" align="center">
              <Button size="small" label={showCalls ? 'Hide the commands' : 'Show the 12 commands'} onClick={() => setShowCalls((v) => !v)} aria-expanded={showCalls} />
            </Box>
            {showCalls && <CodeBlock lines={COMMANDS} a11yTitle="The 12 commands of the plan" />}
            <Text size="small" color="text-weak">When you have reviewed the plan, tick the box next to the green button.<Mark n={4} /></Text>
          </Panel>
        )}

        {state === 'configured' && (
          <Panel>
            <StatusLine state="complete" time="19:32">zz_rc_vvs_rcg and zz_rc_test_rcg created and started. 12 writes, none failed.</StatusLine>
            <Section title="What each array answered" summary="12 writes, in the order they were made">
              {COMMANDS.slice(0, 6).map((c) => (
                <Box key={c} direction="row" gap="small" align="center">
                  <StatusIndicator state="complete" label="Done" />
                  <Text size="small" style={mono}>{c}</Text>
                </Box>
              ))}
              <Text size="small" color="text-weak">6 more, all done.</Text>
            </Section>
            <Section title="To remove what this run created" summary="Paste on A first, then on B">
              <Box direction="row" gap="small">
                <Button size="small" label="Copy the commands for A" />
                <Button size="small" label="Copy the commands for B" />
                <Button size="small" label="Download both" />
              </Box>
            </Section>
          </Panel>
        )}

        {verified && (
          <Panel>
            <StatusLine state="complete" time="19:33">2 groups replicating. Links up 2 of 2 each way.</StatusLine>
            {['zz_rc_vvs_rcg', 'zz_rc_test_rcg'].map((g) => (
              <Box key={g} direction="row" gap="medium" align="center">
                <Box width="small" flex={false}><Text size="small" style={mono}>{g}</Text></Box>
                <StatusIndicator state="complete" label="Replicating" />
                <Text size="small" color="text-weak">Started · Primary here, Secondary on the peer · 1 of 1 volume synced</Text>
              </Box>
            ))}
          </Panel>
        )}

        {at > 0 && (
          <Section title={<>Replication already on AlletraMP_D22U27<Mark n={3} /></>} summary={`${EXISTING_GROUPS.length} groups, not touched by this run`}>
            <Text size="small" style={mono}>{EXISTING_GROUPS.join(' · ')}</Text>
            <Text size="small" color="text-weak">All sync, Started, Synced.</Text>
          </Section>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const replication: Screen = {
  id: 'M6',
  title: 'Replication (the busiest step)',
  states: [
    { key: 'read', label: '1. Not read yet' },
    { key: 'link', label: '2. Link not checked' },
    { key: 'link-over', label: '2. Latency over the limit' },
    { key: 'plan', label: '3. Plan to review' },
    { key: 'configured', label: '4. Configured' },
    { key: 'verified', label: '5. Verified' },
  ],
  notes: [
    'The step is split into five parts done in order. The bar shows where you are, and the green button is always the next part: Read, Check the link, Configure, Verify. Today this page has 9 buttons at once.',
    'Finished parts fold to one line each, with Show for the detail and the part\'s own Read again or Check again. The footer keeps only Continue without replication and the green button.',
    'Groups already on the array fold into one line at the bottom.',
    'The authorisation tick sits in the footer, right next to the button it unlocks, so it is always on screen. The button stays active: press it before the tick and it tells you what is missing, as the Design System asks, instead of a greyed button that says nothing.',
    'Latency over the limit: same rule as today. The Continue anyway tick is in the footer next to the green button, and the choice goes into the result and the as-built.',
  ],
  keeps: [
    ['Read both arrays / Read both arrays again', 'Footer (green) first, then Read again on the finished line'],
    ['Check the link / Check again', 'Part 2, then Check again on the finished line'],
    ['Continue anyway tick', 'Footer, next to the green button, when the latency is over the limit'],
    ['Plan table, Show N commands', 'Part 3'],
    ['Authorise tick', 'Footer, next to Configure replication'],
    ['Configure replication', 'Footer, right (green) in part 3'],
    ['Result table, removal sets with Copy and Download', 'Part 4'],
    ['Verify replication and its table', 'Part 5'],
    ['Replication already present table', 'Folded section at the bottom'],
    ['Continue without configuring replication', 'Footer, beside the green button'],
  ],
  render: (state, setState) => <Replication state={state} setState={setState} />,
};
