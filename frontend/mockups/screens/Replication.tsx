import { Box, Button, CheckBox, DataTable, Text } from 'grommet';
import { Radial } from 'grommet-icons';
import { Fragment, useState } from 'react';
import { StatusIcon, StatusIndicator, StepState } from '../../src/ui/status';
import { COMMANDS, EXISTING_GROUPS, PLAN, RUN, TOTAL, rail, stepNo } from '../data';
import { Action, AppFrame, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const PARTS = ['Read both arrays', 'Check the link', 'Review the plan', 'Configure', 'Verify'];
const ORDER = ['read', 'link', 'link-over', 'plan', 'configured', 'verified'];
const PART_OF: Record<string, number> = { read: 0, link: 1, 'link-over': 1, plan: 2, configured: 3, verified: 4 };

function PartsBar({ at, doneAll }: { at: number; doneAll: boolean }) {
  return (
    <Box direction="row" align="center" gap="xsmall" wrap flex={false}>
      {PARTS.map((p, i) => {
        const state: StepState = doneAll || i < at ? 'complete' : i === at ? 'action_required' : 'not_started';
        return (
          <Fragment key={p}>
            {i > 0 && <Box width="24px" border={{ side: 'top', color: i <= at ? 'border-strong' : 'border-weak' }} />}
            <Box direction="row" gap="xsmall" align="center" pad={{ horizontal: 'small', vertical: 'xsmall' }} round="large" background={i === at && !doneAll ? 'background-selected-primary' : undefined}>
              {state === 'not_started' ? <Radial size="small" color="text-weak" /> : <StatusIcon state={state} />}
              <Text size="small" weight={i === at ? 'bold' : 500} color={state === 'not_started' ? 'text-weak' : 'text-strong'}>{i + 1}. {p}</Text>
            </Box>
          </Fragment>
        );
      })}
    </Box>
  );
}

function Done({ children, detail, mark }: { children: string; detail?: React.ReactNode; mark?: number }) {
  return (
    <Section title={<Box direction="row" gap="small" align="center"><StatusIcon state="complete" /><Text>{children}</Text>{mark && <Mark n={mark} />}</Box>}>
      {detail ?? null}
    </Section>
  );
}

function LinkTable({ ms }: { ms: string }) {
  const rows = [
    { link: 'D22U27 0:4:3 (10.54.122.92) → E18U31 0:4:3 (10.54.154.192)', ms, lost: '0 %' },
    { link: 'D22U27 1:4:3 (10.54.122.93) → E18U31 1:4:3 (10.54.154.193)', ms, lost: '0 %' },
  ];
  return (
    <DataTable
      columns={[
        { property: 'link', header: 'Link', render: (r) => <Text size="small" style={mono}>{r.link}</Text> },
        { property: 'ms', header: 'Latency', render: (r) => <Text size="small">{r.ms} ms</Text> },
        { property: 'lost', header: 'Pings lost', render: (r) => <Text size="small" color="text-weak">{r.lost}</Text> },
      ]}
      data={rows}
      primaryKey="link"
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
    'link-over': { label: 'Continue to the plan', disabled: !accept, onClick: next('plan'), hint: 'Tick Continue anyway first' },
    plan: { label: 'Configure replication', disabled: !authorised, onClick: next('configured'), hint: 'Tick the authorisation first' },
    configured: { label: 'Verify replication', onClick: next('verified') },
    verified: { label: 'Continue to Failover test' },
  }[state] as Action;
  const secondary: Action[] = [];
  if (ORDER.indexOf(state) > 0) secondary.push({ label: 'Read both arrays again', onClick: next('link') });
  if (ORDER.indexOf(state) > 1 && state !== 'verified') secondary.push({ label: 'Check the link again' });
  if (!verified && state !== 'configured') secondary.push({ label: 'Continue without replication' });

  return (
    <AppFrame run={RUN} groups={rail('replicate', verified ? 'complete' : 'action_required')} current="replicate">
      <StepPage
        stepNo={stepNo('replicate')}
        total={TOTAL}
        title="Replication"
        description="Remote Copy of this run's volume sets to the peer array AlletraMP_E18U31."
        state={verified ? 'complete' : 'action_required'}
        stateLabel={verified ? 'Replicating' : `Part ${at + 1} of 5`}
        primary={primary}
        secondary={secondary}
        guideOpen={state !== 'plan' && state !== 'configured'}
        top={
          <Box direction="row" align="center" flex={false}>
            <PartsBar at={at} doneAll={verified} />
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
        {at > 0 && (
          <Done mark={2} detail={<Text size="small">Target AlletraMP_E18U31 on both arrays, policy mirror_config, found by link address. Remote Copy started on both.</Text>}>
            Read both arrays: partnered over 2 of 2 links each way.
          </Done>
        )}
        {at > 1 && (
          <Done detail={<LinkTable ms={over || accept ? '12' : '0.4'} />}>
            {over || accept ? 'Link: 12 ms, over the 10 ms sync limit. You chose to continue.' : 'Link: 0.4 ms on 2 links. Sync allows 10 ms.'}
          </Done>
        )}
        {at > 2 && (
          <Done detail={<Text size="small" style={mono}>{PLAN.map((p) => p.name).join(' · ')}</Text>}>
            Plan approved at 19:31: 6 objects, 12 commands.
          </Done>
        )}
        {at > 3 && (
          <Done detail={<Box direction="row" gap="small"><Button size="small" secondary label="Copy the removal commands for A" /><Button size="small" secondary label="Copy the removal commands for B" /></Box>}>
            Configured: 12 writes done, both groups started.
          </Done>
        )}

        {state === 'read' && (
          <StatusLine state="not_started">Not read yet. Reading both arrays changes nothing.</StatusLine>
        )}

        {(state === 'link' || over) && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
            <Text weight={600}>Check the link</Text>
            {state === 'link' ? (
              <Text size="small">
                checkrclink measures the latency between the two arrays' replication ports: a test server on AlletraMP_E18U31, a test client here,
                stopped as soon as the latency is printed. About 10 seconds per link.
              </Text>
            ) : (
              <>
                <StatusLine state="action_required" time="19:30">Latency 12 ms on 2 links: over the 10 ms limit for sync.</StatusLine>
                <LinkTable ms="12" />
                <CheckBox
                  checked={accept}
                  onChange={(e) => setAccept(e.target.checked)}
                  label="Continue anyway: I accept the measured latency of 12 ms for sync replication."
                />
                <Text size="small" color="text-weak">Your choice is written in the result and the as-built document.<Mark n={5} /></Text>
              </>
            )}
          </Box>
        )}

        {state === 'plan' && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
            <Box direction="row" justify="between" align="center">
              <Text weight={600}>Review the plan</Text>
              <Text size="small" color="text-weak">6 to create · 0 already there · 0 conflicts</Text>
            </Box>
            <DataTable
              columns={[
                { property: 'kind', header: 'Kind', render: (p) => <Text size="small">{p.kind}</Text> },
                { property: 'name', header: 'Name', render: (p) => <Text size="small" style={mono}>{p.name}</Text> },
                { property: 'on', header: 'On', render: (p) => <Text size="small">{p.on}</Text> },
                { property: 'action', header: 'Action', render: () => <Text size="small" weight={600}>Create</Text> },
                { property: 'detail', header: 'Detail', render: (p) => <Text size="small" color="text-weak">{p.detail}</Text> },
              ]}
              data={PLAN}
              primaryKey="name"
            />
            <Text size="xsmall" color="text-weak">A = AlletraMP_D22U27 (this array), B = AlletraMP_E18U31 (the peer).</Text>
            <Box direction="row" gap="small" align="center">
              <Button size="small" label={showCalls ? 'Hide the commands' : 'Show the 12 commands'} onClick={() => setShowCalls((v) => !v)} />
            </Box>
            {showCalls && (
              <Box background="background-contrast" round="xsmall" pad="small" flex={false}>
                {COMMANDS.map((c) => <Text key={c} size="small" style={mono}>{c}</Text>)}
              </Box>
            )}
            <Box border={{ side: 'top', color: 'border-weak' }} pad={{ top: 'small' }} direction="row" align="center">
              <CheckBox
                checked={authorised}
                onChange={(e) => setAuthorised(e.target.checked)}
                label="I have reviewed this plan and authorise configuring replication on AlletraMP_D22U27 and AlletraMP_E18U31."
              />
              <Mark n={4} />
            </Box>
          </Box>
        )}

        {state === 'configured' && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
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
                <Button size="small" secondary label="Copy the commands for A" />
                <Button size="small" secondary label="Copy the commands for B" />
                <Button size="small" label="Download both" />
              </Box>
            </Section>
          </Box>
        )}

        {verified && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
            <StatusLine state="complete" time="19:33">2 groups replicating. Links up 2 of 2 each way.</StatusLine>
            {['zz_rc_vvs_rcg', 'zz_rc_test_rcg'].map((g) => (
              <Box key={g} direction="row" gap="medium" align="center">
                <Box width="180px" flex={false}><Text size="small" style={mono}>{g}</Text></Box>
                <StatusIndicator state="complete" label="Replicating" />
                <Text size="small" color="text-weak">Started · Primary here, Secondary on the peer · 1 of 1 volume synced</Text>
              </Box>
            ))}
          </Box>
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
    'Finished parts fold to one line each, so the page tells the story of the step without scrolling.',
    'Groups already on the array fold into one line at the bottom.',
    'The authorisation tick sits right above the green button it unlocks. Today the tick is mid-page and the button at the bottom.',
    'Latency over the limit: same rule as today. You tick Continue anyway, and the choice goes into the result and the as-built.',
  ],
  keeps: [
    ['Read both arrays / Read both arrays again', 'Footer: green first, then on the left'],
    ['Check the link / Check again', 'Part 2, then on the left'],
    ['Continue anyway tick', 'Part 2, when the latency is over the limit'],
    ['Plan table, Show N commands, authorise tick', 'Part 3'],
    ['Configure replication', 'Footer, right (green) in part 3'],
    ['Result table, removal sets with Copy and Download', 'Part 4'],
    ['Verify replication and its table', 'Part 5'],
    ['Replication already present table', 'Folded section at the bottom'],
    ['Continue without configuring replication', 'Footer, left'],
  ],
  render: (state, setState) => <Replication state={state} setState={setState} />,
};
