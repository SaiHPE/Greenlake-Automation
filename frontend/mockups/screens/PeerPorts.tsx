import { Box, Button, DataTable, Heading, Text } from 'grommet';
import { RESULT, ResultWord, StatusIndicator, StepState } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, CodeBlock, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// SPEC-025 R8, first slice (ADR 0018): the Peer ports section of the Array ports step. The tool plans and
// prints the commands and their undo; a consultant pastes them; Read the array again judges the result.
// No tick and no apply button yet. Ports and WWNs as captured on a lab array (2026-11-16); the array's name is a sample one.
type Row = { nsp: string; now: string; after: string; state: 'create' | 'exists' | 'conflict'; why: string };
const PLAN: Row[] = [
  { nsp: '0:3:3', now: 'free · FC · ready', after: 'peer, point', state: 'create', why: 'free, nothing logged in, no exports' },
  { nsp: '1:3:4', now: 'free · FC · ready', after: 'peer, point', state: 'create', why: 'free, nothing logged in, no exports' },
];
const AFTER: Row[] = PLAN.map((r) => ({ ...r, now: 'peer · FC · ready', after: 'peer', state: 'exists', why: `${r.nsp} is already a peer port.` }));
const STATE: Record<Row['state'], ResultWord> = { create: RESULT.create, exists: RESULT.already_there, conflict: RESULT.conflict };
const COMMANDS = [
  '# 0:3:3', 'controlport offline 0:3:3', 'controlport config peer -ct point -f 0:3:3',
  '# 1:3:4', 'controlport offline 1:3:4', 'controlport config peer -ct point -f 1:3:4',
];
const REMOVALS = [
  'controlport offline 1:3:4', 'controlport config host -ct point -f 1:3:4', 'controlport rst 1:3:4',
  'controlport offline 0:3:3', 'controlport config host -ct point -f 0:3:3', 'controlport rst 0:3:3',
];
const NOTES = [
  "The zones on 0:3:3's WWPN were not checked (no switch read): ask the SAN team before setting it.",
  "The zones on 1:3:4's WWPN were not checked (no switch read): ask the SAN team before setting it.",
];

function PlanTable({ rows }: { rows: Row[] }) {
  return (
    <DataTable
      columns={[
        { property: 'nsp', header: 'Port', render: (r: Row) => <Text size="small" style={mono}>{r.nsp}</Text> },
        { property: 'now', header: 'Now', render: (r: Row) => <Text size="small">{r.now}</Text> },
        { property: 'after', header: 'After', render: (r: Row) => <Text size="small">{r.after}</Text> },
        { property: 'state', header: 'Plan', render: (r: Row) => <StatusIndicator state={STATE[r.state].state} label={STATE[r.state].label} /> },
        { property: 'why', header: 'Why', render: (r: Row) => <Text size="small">{r.why}</Text> },
      ]}
      data={rows}
      primaryKey="nsp"
    />
  );
}

function PeerPorts({ state, setState }: { state: string; setState: (s: string) => void }) {
  const none = state === 'none';
  const plan = state === 'plan';
  const after = state === 'after';
  const stepState: StepState = plan ? 'action_required' : 'complete';
  const read: Action = { label: 'Read the array again', onClick: () => setState(plan ? 'after' : 'plan') };
  return (
    <AppFrame run={RUN} groups={rail('ports', stepState)} current="ports">
      <StepPage
        stepLabel={stepLabel('ports')}
        title="Array ports"
        description="What the sheet asks of this array's ports, planned against what the array has, without changing anything."
        state={stepState}
        stateLabel={plan ? 'Action required' : 'Complete'}
        primary={{ label: 'Continue to SAN zoning' }}
        actions={none ? [] : [read]}
        guideOpen={false}
        activity={{ last: plan ? '10:12:04  Read DEMO-ARRAY-01: plan ready, peer ports: 2 to set' : '10:31:40  Read DEMO-ARRAY-01: all 2 peer ports in peer mode', events: 16, commands: 15 }}
        guidance={
          <Guidance
            items={[
              { title: 'Peer ports', body: 'Free Fibre Channel ports set to peer mode, so a data migration can read the source array through them. The tool only offers ports with no login and no export.' },
              { title: 'The command set', body: 'Each port is taken offline, then set to peer. Keep the removal set before you paste: it puts each port back as it was.' },
            ]}
          />
        }
      >
        {plan && (
          <StatusLine state="action_required" time="10:12">
            Plan ready: 2 ports to set. The tool does not set these up yet: paste the commands on the array&apos;s CLI, then read the array
            again.<Mark n={2} />
          </StatusLine>
        )}
        {after && <StatusLine state="complete" time="10:31">Set up: all in place. Every peer port the sheet asks for is in place on DEMO-ARRAY-01.</StatusLine>}
        {plan && <Section title={`${NOTES.length} notes`}>{NOTES.map((n) => <Text key={n} size="small">{n}</Text>)}</Section>}
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">iSCSI addresses on VLANs</Heading>
          <Text size="small" color="text-weak">The sheet asks for no iSCSI VLANs. Nothing to set up here.</Text>
        </Box>
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Peer ports<Mark n={1} /></Heading>
          {none && <Text size="small" color="text-weak">The sheet asks for no peer ports. Nothing to set up here.</Text>}
          {!none && (
            <Section title="What the sheet asks for" summary="2 ports · 2 source array ports to zone">
              <Text size="small" style={mono}>0:3:3 → 20:31:00:02:ac:02:ac:38</Text>
              <Text size="small" style={mono}>1:3:4 → 21:31:00:02:ac:02:ac:38</Text>
            </Section>
          )}
          {plan && (
            <Box gap="small" flex={false}>
              <PlanTable rows={PLAN} />
              <Section title="Commands to paste on DEMO-ARRAY-01" summary="4 lines" right={<Box direction="row" gap="xsmall"><Button size="small" label="Copy" /><Button size="small" label="Download .txt" /></Box>} open>
                <Text size="small" color="text-weak">Each port goes offline first; it carries no login and no export. The tool does not send these.</Text>
                <CodeBlock lines={COMMANDS} a11yTitle="Commands to paste" />
              </Section>
              <Section title="Removal set, to keep before you paste" summary="6 lines" right={<Box direction="row" gap="xsmall"><Button size="small" label="Copy" /><Button size="small" label="Download .txt" /></Box>}>
                <CodeBlock lines={REMOVALS} a11yTitle="Removal set" />
              </Section>
            </Box>
          )}
          {after && (
            <Box gap="small" flex={false}>
              <Box gap="xxsmall" flex={false}>
                <StatusIndicator state="complete" label="The read after the paste" />
                <Text size="small">0:3:3 is now a peer port (port WWPN 20330202AC02D495).</Text>
                <Text size="small">1:3:4 is now a peer port (port WWPN 21340202AC02D495).<Mark n={3} /></Text>
              </Box>
              <PlanTable rows={AFTER} />
              <Section title="Removal set for what changed" summary="6 lines" right={<Box direction="row" gap="xsmall"><Button size="small" label="Copy" /><Button size="small" label="Download .txt" /></Box>}>
                <CodeBlock lines={REMOVALS} a11yTitle="Removal set" />
              </Section>
            </Box>
          )}
        </Box>
      </StepPage>
    </AppFrame>
  );
}

export const peerPorts: Screen = {
  id: 'M18',
  title: 'Array ports (peer ports, first slice)',
  states: [
    { key: 'none', label: 'Sheet asks for nothing' },
    { key: 'plan', label: 'Plan: 2 ports to set' },
    { key: 'after', label: 'Read after the paste' },
  ],
  notes: [
    'One section per tab of the sheet; a tab that is empty says so and reads nothing (SPEC-024 and SPEC-025 R8).',
    'First slice (ADR 0018): the commands and their removal set are printed; there is no tick and no Set button yet.',
    'Read the array again judges the read after the paste: each port peer, point; every other port unchanged.',
    'One status line under the header for the whole step (SPEC-030); the read after the paste stays in the Peer ports section as its finding; the notes fold into "N notes".',
  ],
  render: (state, setState) => <PeerPorts state={state} setState={setState} />,
};
