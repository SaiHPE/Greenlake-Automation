import { Box, Button, DataTable, Text } from 'grommet';
import { Clone } from 'grommet-icons';
import { useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { RUN } from '../data';
import { Action, AppFrame, CodeBlock, Confirmation, DoneList, EmptyState, Guidance, Mark, Panel, PartsBar, RailGroup, RunState, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// SPEC-023 R10. Data from the D22U27 capture of 2026-11-17 (OS 10.5.0): its seven schedules, five of
// which start at 00:00 on Sundays, and the live run's own row (SPEC-023 section 6).
const PARTS = ['Read the array', 'Review the plan', 'Create', 'Check snapshots'];
const PART_OF: Record<string, number> = { read: 0, plan: 1, conflict: 1, created: 2, checked: 3 };

const ASK = 'zz_sn_vvs (set, 2 volumes) · Snapshot now · every 15 minutes · kept 2 hours · read-only';

const PLAN = [
  { what: 'Snapshot now', name: 'zz_sn_vvs', state: 'Create', detail: 'zz_sn_vol01.initial, zz_sn_vol02.initial (read-only, expires after 2 hours)' },
  { what: 'Schedule', name: 'zz_sn_vvs_snap', state: 'Create', detail: 'every 15 minutes, every day, kept 2 hours, read-only' },
];
const CONFLICT = [
  PLAN[0],
  { what: 'Schedule', name: 'zz_sn_vvs_snap', state: 'Conflict', detail: "already runs 'createsv -f -ro -exp 3h …' at '0,15,30,45 * * * *'" },
];
const COMMANDS = [
  'POST /volumesets/zz_sn_vvs {"action": "createSnapshot", "parameters": {"name": "@vvname@.initial", "readOnly": true, "expirationHours": 2}}',
  '   = createsv -ro -exp 2h @vvname@.initial set:zz_sn_vvs',
  'createsched -f "createsv -f -ro -exp 2h @vvname@.@y@@m@@d@@H@@M@@S@ set:zz_sn_vvs" "0,15,30,45 * * * *" zz_sn_vvs_snap',
];
const REMOVAL = ['removesched -f zz_sn_vvs_snap', 'removevv -f zz_sn_vol01.initial', 'removevv -f zz_sn_vol02.initial'];
const ON_ARRAY = [
  { name: 'test_CRV_snapschedule', runs: 'createsv … set:test_CRV_set', when: '00 0,4,8,12,16,20 * * *', status: 'Active' },
  { name: 'compactcpg_SSD_r6_sun', runs: 'compactcpg -f SSD_r6', when: '0 0 * * 0', status: 'Active' },
  { name: 'Pol-999', runs: 'createsv … set:set-test999', when: '0,15,30,45 8-20 * * *', status: 'Active' },
  { name: 'Compact-Task', runs: 'compactcpg SSD_r6', when: '0 0,5,10,15,20 * * *', status: 'Active' },
  { name: 'Compact-Task1', runs: 'compactcpg SSD_r6', when: '0 0,5,10,15,17,20 * * *', status: 'Active' },
  { name: 'Compact-Task2', runs: 'compactcpg -f SSD_r6', when: '0 0,5,10,15,17,20 * * *', status: 'Active' },
  { name: 'Test', runs: 'createsv … set:300gb', when: '0 7 9 * *', status: 'Active' },
];

/** The live run's mode: Custom, Provision storage → Snapshots → Verify → As-built. */
function rail(state: RunState): RailGroup[] {
  return [
    { stage: 'Prepare', steps: [
      { key: 'prereq', label: 'Prerequisites', state: 'complete', result: '3 checks passed' },
      { key: 'sheet', label: 'Initialisation sheet', state: 'complete', result: 'CZ2D320BT1 · 4 tabs' },
      { key: 'mode', label: 'Mode', state: 'complete', result: 'Custom' },
    ] },
    { stage: 'Provision', steps: [{ key: 'provision', label: 'Provision storage', state: 'complete', result: '2 volumes · 1 volume set' }] },
    { stage: 'Protect', steps: [{ key: 'snapshots', label: 'Snapshots', state }] },
    { stage: 'Document', steps: [
      { key: 'verify', label: 'Verify configuration', state: 'not_started' },
      { key: 'asbuilt', label: 'As-built document', state: 'not_started' },
    ] },
  ];
}

function PlanTable({ rows }: { rows: typeof PLAN }) {
  return (
    <DataTable
      columns={[
        { property: 'what', header: 'Plan', render: (p) => <Text size="small">{p.what}</Text> },
        { property: 'name', header: 'Name', render: (p) => <Text size="small" style={mono}>{p.name}</Text> },
        { property: 'state', header: 'State', render: (p) => (
          p.state === 'Conflict' ? <StatusIndicator state="failed" label="Conflict" /> : <Text size="small" weight={500}>{p.state}</Text>
        ) },
        { property: 'detail', header: 'What', render: (p) => <Text size="small" color="text-weak">{p.detail}</Text> },
      ]}
      data={rows}
      primaryKey="what"
    />
  );
}

function Snapshots({ state, setState }: { state: string; setState: (s: string) => void }) {
  const [authorised, setAuthorised] = useState(false);
  const [showCalls, setShowCalls] = useState(false);
  const at = PART_OF[state];
  const checked = state === 'checked';
  const conflict = state === 'conflict';
  const next = (s: string) => () => setState(s);

  const primary: Action = {
    read: { label: 'Read the array', onClick: next('plan') },
    plan: { label: 'Create snapshots and schedules', onClick: next('created') },
    conflict: { label: 'Create snapshots and schedules', blocked: 'Resolve the conflict first: the plan has 1 finding.' },
    created: { label: 'Check snapshots', onClick: next('checked') },
    checked: { label: 'Continue to Verify configuration' },
  }[state] as Action;
  const confirmation: Confirmation | undefined = state === 'plan'
    ? {
      label: 'I have reviewed this plan and authorise creating these snapshots and schedules on AlletraMP_D22U27. The schedules keep running after this run ends.',
      checked: authorised, onChange: setAuthorised,
    }
    : undefined;
  const actions: Action[] = at > 0 && !checked ? [{ label: 'Read the array again', onClick: next('plan') }] : [];

  const done: { text: string; again?: string; detail?: React.ReactNode }[] = [];
  if (at > 0) done.push({ text: 'Read AlletraMP_D22U27 at 14:02: OS 10.5.0, 7 schedules, 2 volumes in zz_sn_vvs.', again: 'Read again' });
  if (at > 1) done.push({ text: 'Plan approved at 14:03: a snapshot now and a schedule.', detail: <CodeBlock lines={COMMANDS} a11yTitle="The calls of the plan" /> });
  if (at > 2) done.push({ text: 'Created at 14:03: 2 snapshots taken and read back; zz_sn_vvs_snap active, next run 14:15.' });

  return (
    <AppFrame run={{ ...RUN, mode: 'Custom' }} groups={rail(checked ? 'complete' : conflict ? 'failed' : 'action_required')} current="snapshots">
      <StepPage
        stepLabel="Step 2 of 4"
        title="Snapshots"
        description="A snapshot now of each volume set on the Snapshots tab, and a schedule the array keeps running."
        state={checked ? 'complete' : conflict ? 'failed' : 'action_required'}
        stateLabel={checked ? 'Taking snapshots' : conflict ? '1 finding to resolve' : state === 'plan' ? 'Plan ready · 2 to create' : `Part ${at + 1} of 4`}
        primary={primary}
        actions={actions}
        confirmation={confirmation}
        guideOpen={state === 'read'}
        top={
          <Box direction="row" align="center" flex={false}>
            <PartsBar parts={PARTS} at={at} doneAll={checked} />
            <Mark n={1} />
          </Box>
        }
        activity={{ last: checked ? '14:19:40  Check: zz_sn_vvs_snap taking snapshots (2 so far)' : '14:02:11  Read AlletraMP_D22U27', events: 6 + at * 3, commands: 9 + at * 4 }}
        guidance={
          <Guidance
            items={[
              { title: 'What this step does', body: 'Takes one read-only snapshot of each volume now, named <volume>.initial, and sets up a schedule on the array that takes more and lets each expire after Keep for.' },
              { title: 'The schedule keeps running', body: 'After this run ends the array keeps taking snapshots until someone removes the schedule. The removal set starts with that line.' },
              { title: 'Nothing is written until you approve', body: 'Reading and the plan change nothing. Only Create snapshots and schedules writes, and only what the plan shows.' },
              { title: 'Schedules already there', body: 'Schedules this run did not make are listed and never changed, suspended or removed.' },
            ]}
          />
        }
      >
        <Panel title="What the workbook asks for">
          <Text size="small" style={mono}>{ASK}</Text>
          <Text size="small" color="text-weak">Array time: IST (Asia/Calcutta), as the array prints it. Start hours and days on the tab are in this time.<Mark n={2} /></Text>
        </Panel>

        {done.length > 0 && (
          <Box flex={false}>
            <DoneList items={done} />
          </Box>
        )}

        {state === 'read' && (
          <EmptyState icon={<Clone size="large" color="icon-weak" />} title="Not read yet">
            Read the array to see the volume sets, the snapshots they already have and the schedules on it. Reading changes nothing.
          </EmptyState>
        )}

        {(state === 'plan' || conflict) && (
          <Panel title="Review the plan" right={<Text size="small" color="text-weak">{conflict ? '1 to create · 1 conflict' : '2 to create · 0 already there'}</Text>}>
            <PlanTable rows={conflict ? CONFLICT : PLAN} />
            {conflict ? (
              <StatusLine state="failed">
                A schedule named zz_sn_vvs_snap already runs 'createsv -f -ro -exp 3h @vvname@.@y@@m@@d@@H@@M@@S@ set:zz_sn_vvs' at '0,15,30,45 * * * *'. The tool never changes a schedule it did not make: name another on the Snapshots tab, or remove that one first.
              </StatusLine>
            ) : (
              <Box gap="xsmall" flex={false}>
                <Text size="small">SSD_r6 has 393.8 GiB free; snapshots use the volume's own CPG.</Text>
                <Text size="small">The array already starts 5 schedules at 00:00 on Sunday; zz_sn_vvs_snap adds one. The array advises spreading schedule start times.<Mark n={3} /></Text>
                <Text size="small">Once created, the array takes a snapshot of zz_sn_vvs every 15 minutes until someone removes the schedule zz_sn_vvs_snap.</Text>
              </Box>
            )}
            <Box direction="row" gap="small" align="center">
              <Button size="small" label={showCalls ? 'Hide the calls' : 'Show the 2 calls'} onClick={() => setShowCalls((v) => !v)} aria-expanded={showCalls} />
            </Box>
            {showCalls && <CodeBlock lines={COMMANDS} a11yTitle="The calls of the plan" />}
            {!conflict && <Text size="small" color="text-weak">When you have reviewed the plan, tick the box next to the green button.<Mark n={4} /></Text>}
          </Panel>
        )}

        {(state === 'created' || checked) && (
          <Panel>
            {checked ? (
              <Box gap="xsmall" flex={false}>
                <StatusLine state="complete" time="14:19">zz_sn_vvs: taking snapshots (2 so far), next run 14:30.</StatusLine>
                <Box direction="row" gap="medium" align="center">
                  <StatusIndicator state="complete" label="In place" />
                  <Text size="small" color="text-weak">zz_sn_vol01.initial, zz_sn_vol02.initial: read-only, expiring 16:03</Text>
                </Box>
              </Box>
            ) : (
              <StatusLine state="complete" time="14:03">2 snapshots taken and read back. zz_sn_vvs_snap is active; the array takes the next at 14:15.</StatusLine>
            )}
            <Section title="To remove what this step created" summary="The schedule first, so it takes no more snapshots" open={state === 'created'}>
              <CodeBlock lines={REMOVAL} a11yTitle="The removal set" />
              <Text size="small" color="text-weak">Snapshots the schedule takes expire on their own after 2 hours. To remove them sooner, remove each with removevv -f.</Text>
              <Box direction="row" gap="small">
                <Button size="small" label="Copy" />
                <Button size="small" label="Download .txt" />
              </Box>
            </Section>
          </Panel>
        )}

        {at > 0 && (
          <Section title={<>Schedules already on AlletraMP_D22U27<Mark n={5} /></>} summary={`${ON_ARRAY.length} schedules, not touched by this run`}>
            <DataTable
              columns={[
                { property: 'name', header: 'Schedule', render: (r) => <Text size="small" style={mono}>{r.name}</Text> },
                { property: 'runs', header: 'Runs', render: (r) => <Text size="small" style={mono}>{r.runs}</Text> },
                { property: 'when', header: 'When', render: (r) => <Text size="small" style={mono}>{r.when}</Text> },
                { property: 'status', header: 'Status', render: (r) => <Text size="small">{r.status}</Text> },
              ]}
              data={ON_ARRAY}
              primaryKey="name"
            />
          </Section>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const snapshots: Screen = {
  id: 'M21',
  title: 'Snapshots',
  states: [
    { key: 'read', label: '1. Not read yet' },
    { key: 'plan', label: '2. Plan to review' },
    { key: 'conflict', label: '2. A schedule of that name' },
    { key: 'created', label: '3. Created' },
    { key: 'checked', label: '4. Checked' },
  ],
  notes: [
    'Four parts in order, as on Replication: read, review the plan, create, check. The green button is always the next part.',
    "The array's own time zone is shown as the array prints it (Asia/Calcutta and Asia/Kolkata both occur on the lab). Start hours on the tab are in that time.",
    'The plan says, above the tick, what the array would have asked: when other schedules already start in the same minute. It is a note, not a blocker.',
    'The tick names the array and says the schedules keep running after the run. Create snapshots and schedules stays active; pressed before the tick, it says what is missing.',
    'Schedules already on the array fold into one line at the bottom, each not touched by this run.',
    'As built (2026-11-17), as drawn here: the finished parts are one list above the part at hand, as on SAN zoning and Provision storage; Replication puts it under (M6).',
  ],
  keeps: [
    ['Read the array / Read the array again', 'Footer (green) first, then Read again on the finished line and in the footer'],
    ['Plan table, Show the calls', 'Part 2'],
    ['Authorise tick', 'Footer, next to Create snapshots and schedules'],
    ['Create snapshots and schedules', 'Footer, right (green) in part 2'],
    ['Result, removal set with Copy and Download .txt', 'Part 3'],
    ['Check snapshots and its verdicts', 'Part 4'],
    ['Schedules already on the array', 'Folded section at the bottom'],
  ],
  render: (state, setState) => <Snapshots state={state} setState={setState} />,
};
