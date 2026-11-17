import { Box, Button, DataTable, Text } from 'grommet';
import { Network } from 'grommet-icons';
import { RESULT, ResultWord, StatusIndicator, StepState } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, CodeBlock, EmptyState, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// SPEC-024 R8, first slice (ADR 0017): read, plan, the printed CLI lines and the sentence for the
// network team. No tick and no apply button yet. Addresses are documentation-range (192.0.2.x).
// SPEC-030 (BL-59): the header says the state word only; one status line under it carries the counts,
// the plan's notes fold into "N notes", and a section opens by itself only when it holds work.
type Row = { nsp: string; vlan: number; ip: string; netmask: string; gateway: string };
type Plan = Row & { state: 'create' | 'exists' | 'conflict'; why: string; cli: string[] };

const ROWS: Row[] = [
  { nsp: '0:4:1', vlan: 120, ip: '192.0.2.11', netmask: '255.255.255.0', gateway: '192.0.2.1' },
  { nsp: '1:4:1', vlan: 120, ip: '192.0.2.12', netmask: '255.255.255.0', gateway: '192.0.2.1' },
  { nsp: '0:4:2', vlan: 130, ip: '198.51.100.11', netmask: '255.255.255.0', gateway: '' },
  { nsp: '0:4:3', vlan: 130, ip: '198.51.100.12', netmask: '255.255.255.0', gateway: '' },
];
const PLAN: Plan[] = [
  { ...ROWS[0], state: 'create', why: '192.0.2.11 255.255.255.0, gateway 192.0.2.1 on VLAN 120 (ready)',
    cli: ['controliscsiport addr 192.0.2.11 255.255.255.0 -vlan 120 -f 0:4:1', 'controliscsiport gw 192.0.2.1 -vlan 120 -f 0:4:1'] },
  { ...ROWS[1], state: 'create', why: '192.0.2.12 255.255.255.0, gateway 192.0.2.1 on VLAN 120 (ready)',
    cli: ['controliscsiport addr 192.0.2.12 255.255.255.0 -vlan 120 -f 1:4:1', 'controliscsiport gw 192.0.2.1 -vlan 120 -f 1:4:1'] },
  { ...ROWS[2], state: 'exists', why: '198.51.100.11 255.255.255.0 already set', cli: [] },
  { ...ROWS[3], state: 'conflict', cli: [],
    why: "DEMO-ARRAY-01 0:4:3 is not an iSCSI port: showport lists it as peer offline free IP. The tool never changes a port's role." },
];
const DONE: Plan[] = PLAN.slice(0, 3).map((p) => ({ ...p, state: 'exists', why: `${p.ip} ${p.netmask} already set`, cli: [] }));
const PLAN_STATE: Record<Plan['state'], ResultWord> = { create: RESULT.create, exists: RESULT.already_there, conflict: RESULT.conflict };
const SWITCH = [
  'Switch port cabled to DEMO-ARRAY-01 0:4:1: carry VLAN 120 tagged (802.1Q); keep the untagged (native) VLAN as it is.',
  'Switch port cabled to DEMO-ARRAY-01 0:4:2: carry VLAN 130 tagged (802.1Q); keep the untagged (native) VLAN as it is.',
  'Switch port cabled to DEMO-ARRAY-01 1:4:1: carry VLAN 120 tagged (802.1Q); keep the untagged (native) VLAN as it is.',
];
const NOTES = ['VLAN 130 is only on node 0. If that node stops, hosts on VLAN 130 lose every path.'];

function SheetRows({ rows }: { rows: Row[] }) {
  return (
    <Section title="What the sheet asks for" summary={`${rows.length} iSCSI address${rows.length === 1 ? '' : 'es'} on the iSCSI network tab`}>
      <DataTable
        columns={[
          { property: 'nsp', header: 'Port', render: (r: Row) => <Text size="small" style={mono}>{r.nsp}</Text> },
          { property: 'vlan', header: 'VLAN', render: (r: Row) => <Text size="small">{r.vlan}</Text> },
          { property: 'ip', header: 'Address', render: (r: Row) => <Text size="small" style={mono}>{r.ip} {r.netmask}</Text> },
          { property: 'gateway', header: 'Gateway', render: (r: Row) => <Text size="small" style={mono}>{r.gateway || '--'}</Text> },
        ]}
        data={rows}
        primaryKey={false}
      />
    </Section>
  );
}

function PlanTable({ plan }: { plan: Plan[] }) {
  const adds = plan.filter((p) => p.state === 'create');
  const conflicts = plan.filter((p) => p.state === 'conflict').length;
  return (
    <Box gap="medium" flex={false}>
      <Section title="The plan" summary={`${adds.length} to add · ${plan.filter((p) => p.state === 'exists').length} already there · ${conflicts} conflict`} open={adds.length + conflicts > 0}>
        <DataTable
          columns={[
            { property: 'nsp', header: 'Port', render: (p: Plan) => <Text size="small" style={mono}>{p.nsp}</Text> },
            { property: 'vlan', header: 'VLAN', render: (p: Plan) => <Text size="small">{p.vlan}</Text> },
            { property: 'ip', header: 'Address', render: (p: Plan) => <Text size="small" style={mono}>{p.ip}</Text> },
            { property: 'gateway', header: 'Gateway', render: (p: Plan) => <Text size="small" style={mono}>{p.gateway || '--'}</Text> },
            { property: 'state', header: 'Plan', render: (p: Plan) => <StatusIndicator state={PLAN_STATE[p.state].state} label={PLAN_STATE[p.state].label} /> },
            { property: 'why', header: 'Why', render: (p: Plan) => <Text size="small">{p.why}</Text> },
          ]}
          data={plan}
          primaryKey={false}
        />
      </Section>
      {adds.length > 0 && (
        <Section title="The array's command lines" summary={`${adds.length * 2} lines, each with -vlan`} right={<Button size="small" label="Copy" />}>
          <Text size="small" color="text-weak">
            The tool does not send these yet. Each line carries -vlan: without it the line would change the port&apos;s untagged address and cut
            off the hosts logged in on it.<Mark n={2} />
          </Text>
          <CodeBlock lines={adds.flatMap((p) => p.cli)} a11yTitle="CLI lines for the array" />
        </Section>
      )}
    </Box>
  );
}

function ArrayPorts({ state, setState }: { state: string; setState: (s: string) => void }) {
  const none = state === 'none';
  const before = state === 'before';
  const plan = state === 'plan';
  const done = state === 'done';
  const stepState: StepState = none || done ? 'complete' : plan ? 'action_required' : 'not_started';
  const read: Action = { label: before ? 'Read the array and plan' : 'Read the array again', onClick: () => setState(plan ? 'done' : 'plan') };
  const primary: Action = none || done || plan ? { label: 'Continue to SAN zoning' } : read;
  return (
    <AppFrame run={RUN} groups={rail('ports', stepState)} current="ports">
      <StepPage
        stepLabel={stepLabel('ports')}
        title="Array ports"
        description="What the sheet asks of this array's ports, planned against what the array has, without changing anything."
        state={stepState}
        stateLabel={none || done ? 'Complete' : plan ? 'Action required' : 'Not started'}
        primary={primary}
        actions={none || before ? [] : [read]}
        guideOpen={false}
        activity={{ last: plan ? '10:12:04  Read DEMO-ARRAY-01: plan ready, 2 to add, 1 conflict' : '10:09:40  Discovery complete', events: 14, commands: 9 }}
        guidance={
          <Guidance
            items={[
              { title: 'What is read', body: "The array's ports, the addresses on its iSCSI ports and their VLANs, its management, replication and file addresses. Read-only: reading the array changes nothing." },
              { title: 'Why before zoning', body: 'An iSCSI host on a VLAN logs in only once the array has an address on that VLAN. The zoning check is what sees that login.' },
              { title: 'The switch', body: 'The tool never changes a switch. The network team gets one sentence per port: which VLANs to carry tagged, and to keep the native VLAN.' },
            ]}
          />
        }
      >
        {none && (
          <EmptyState icon={<Network size="large" color="icon-weak" />} title={<>Nothing to set up here<Mark n={1} /></>}>
            The sheet asks for no iSCSI VLANs. Nothing to set up here.
          </EmptyState>
        )}
        {plan && (
          <StatusLine state="action_required" time="10:12">
            Plan ready: 2 to add, 1 conflict. Resolve each conflict on the sheet or on the array, never with the tool, then read the array
            again.<Mark n={3} />
          </StatusLine>
        )}
        {done && <StatusLine state="complete" time="10:31">Set up: all in place. Every iSCSI address the sheet asks for is in place on DEMO-ARRAY-01.</StatusLine>}
        {plan && <Section title={`${NOTES.length} note`}><Text size="small">{NOTES[0]}</Text></Section>}
        {!none && <SheetRows rows={ROWS} />}
        {before && (
          <EmptyState icon={<Network size="large" color="icon-weak" />} title="Not read yet">
            Read the array and plan reads DEMO-ARRAY-01 over SSH (read-only) and compares it with the 4 rows above. It takes a few seconds.
          </EmptyState>
        )}
        {plan && (
          <Box gap="medium" flex={false}>
            <PlanTable plan={PLAN} />
            <Section title="For the network team" summary={`${SWITCH.length} switch ports`} right={<Button size="small" label="Copy" />} open>
              <Text size="small" color="text-weak">The tool does not change the switch. Send these to the network team.</Text>
              <CodeBlock lines={SWITCH} a11yTitle="Sentences for the network team" />
            </Section>
          </Box>
        )}
        {done && (
          <Box gap="medium" flex={false}>
            <PlanTable plan={DONE} />
            <Section title="For the network team" summary={`${SWITCH.length} switch ports`} right={<Button size="small" label="Copy" />}>
              <CodeBlock lines={SWITCH} a11yTitle="Sentences for the network team" />
            </Section>
          </Box>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const arrayPorts: Screen = {
  id: 'M17',
  title: 'Array ports (iSCSI VLANs, first slice)',
  states: [
    { key: 'none', label: 'Sheet asks for nothing' },
    { key: 'before', label: 'Not read yet' },
    { key: 'plan', label: 'Plan: 2 to add, 1 conflict' },
    { key: 'done', label: 'All in place' },
  ],
  notes: [
    'With no rows on the iSCSI network tab the step reads nothing and is complete (SPEC-024 R8).',
    'Every printed line carries -vlan (ADR 0017). The first slice has no tick and no apply button: the page says adding is not built yet.',
    'After the engineer pastes the lines, Read the array again turns each add into Already there.',
    'One status line under the header carries the counts (SPEC-030); the plan\'s notes fold into "N notes". The plan and the network team\'s sentences open by themselves only while there is something to add or a conflict.',
  ],
  render: (state, setState) => <ArrayPorts state={state} setState={setState} />,
};
