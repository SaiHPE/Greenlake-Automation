import { Box, Button, DataTable, Select, Text, TextInput } from 'grommet';
import { Add, Storage, Trash } from 'grommet-icons';
import { useState } from 'react';
import { StatusIndicator, StepState } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, CodeBlock, Confirmation, DoneList, EmptyState, Guidance, Mark, Panel, PartsBar, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const PARTS = ['Compose', 'Review the plan', 'Create', 'Verify paths'];
const PART_OF: Record<string, number> = { compose: 0, plan: 1, conflict: 1, created: 3, verified: 3 };

type PlanState = 'create' | 'exists' | 'update' | 'conflict';
// Exists, Update and Conflict are statuses of what is on the array; Create is an action, so it is words alone.
const PLAN_STATE: Record<Exclude<PlanState, 'create'>, { state: StepState; label: string }> = {
  exists: { state: 'complete', label: 'Exists' },
  update: { state: 'action_required', label: 'Update' },
  conflict: { state: 'failed', label: 'Conflict' },
};
const PlanAction = ({ state }: { state: PlanState }) =>
  state === 'create' ? <Text size="small" weight={500}>Create</Text> : <StatusIndicator state={PLAN_STATE[state].state} label={PLAN_STATE[state].label} />;

const PLAN = [
  { kind: 'Host', name: 'ESX1', state: 'exists' as PlanState, detail: 'On the array with the same 2 WWPNs. Left alone.', reason: '' },
  { kind: 'Volume', name: 'zz_rc_vol01', state: 'create' as PlanState, detail: '10 GiB, thin, on SSD_r6', reason: '' },
  { kind: 'Volume set', name: 'zz_rc_vvs', state: 'create' as PlanState, detail: 'holds zz_rc_vol01', reason: '' },
  { kind: 'Host set', name: 'zz_rc_hs', state: 'create' as PlanState, detail: 'members: ESX1', reason: '' },
  { kind: 'Export', name: 'zz_rc_vvs → zz_rc_hs', state: 'create' as PlanState, detail: 'LUN auto (the array picks the next free number)', reason: '' },
];
const CONFLICT = PLAN.map((p) => (p.kind === 'Host set'
  ? { ...p, state: 'conflict' as PlanState, detail: 'On the array with members ESX3, ESX4', reason: 'Same name, different members. The plan would not add ESX1 silently.' }
  : p));

const RESULT = [
  { kind: 'Host', name: 'ESX1', result: 'Exists', detail: 'left untouched' },
  { kind: 'Volume', name: 'zz_rc_vol01', result: 'Created', detail: 'WWN 60002AC0000000000000001B0002D5EF' },
  { kind: 'Volume set', name: 'zz_rc_vvs', result: 'Created', detail: '1 member' },
  { kind: 'Host set', name: 'zz_rc_hs', result: 'Created', detail: '1 member' },
  { kind: 'Export', name: 'zz_rc_vvs → zz_rc_hs', result: 'Created', detail: 'LUN 1 · read back from showvlun -t' },
];
const REMOVAL = ['removevlun -f set:zz_rc_vvs 1 set:zz_rc_hs', 'removehostset -f zz_rc_hs', 'removevvset -f zz_rc_vvs', 'removevv -f zz_rc_vol01'];

const MEMBERS = ['ESX1 · logged in on F1 and F2 · from the sheet', 'ESX2 · not logged in · from vCenter'];

function Compose({ readOnly }: { readOnly: boolean }) {
  return (
    <Panel title={readOnly ? 'Composition used' : 'Compose'}>
      <Text size="small" color="text-weak">Which hosts go in each host set, and which volume or volume set is presented to which host or host set, at which LUN. Nothing is written here.</Text>
      <Box gap="xsmall" flex={false}>
        <Text size="small" weight={500}>Host set members</Text>
        <Box direction="row" gap="small" align="center" wrap>
          <Box width="small" flex={false}><Text size="small" style={mono}>zz_rc_hs</Text></Box>
          <Box width="medium">
            <Select size="small" multiple options={MEMBERS} value={[MEMBERS[0]]} valueLabel="ESX1" disabled={readOnly} aria-label="Members of zz_rc_hs" onChange={() => undefined} />
          </Box>
        </Box>
      </Box>
      <Box gap="xsmall" flex={false}>
        <Text size="small" weight={500}>Exports</Text>
        <Box direction="row" gap="small" align="center" wrap>
          <Box flex width={{ min: 'small' }}><Select size="small" options={['zz_rc_vvs · new volume set', 'zz_rc_vol01 · new volume']} value="zz_rc_vvs · new volume set" disabled={readOnly} aria-label="Source" onChange={() => undefined} /></Box>
          <Text size="small">→</Text>
          <Box flex width={{ min: 'small' }}><Select size="small" options={['zz_rc_hs · new host set', 'ESX1 · logged in on F1 and F2']} value="zz_rc_hs · new host set" disabled={readOnly} aria-label="Target" onChange={() => undefined} /></Box>
          <Box width="xsmall" flex={false}><TextInput size="small" placeholder="LUN auto" aria-label="LUN" disabled={readOnly} /></Box>
          {!readOnly && <Button size="small" icon={<Trash size="small" />} a11yTitle="Remove this export row" />}
        </Box>
        <Text size="xsmall" color="text-weak">LUN blank = the array picks. With no export rows and one host set, every volume goes to that set.</Text>
      </Box>
      {!readOnly && (
        <Box direction="row" gap="small" align="center">
          <Button size="small" icon={<Add size="small" />} label="Add export row" />
          <Button size="small" label="Save composition" />
          <Button size="small" label="Reload" />
        </Box>
      )}
    </Panel>
  );
}

function PlanTable({ rows }: { rows: typeof PLAN }) {
  return (
    <DataTable
      columns={[
        { property: 'kind', header: 'Kind', render: (p) => <Text size="small">{p.kind}</Text> },
        { property: 'name', header: 'Name', render: (p) => <Text size="small" style={mono}>{p.name}</Text> },
        { property: 'state', header: 'Action', render: (p) => <PlanAction state={p.state} /> },
        {
          property: 'detail',
          header: 'Detail',
          render: (p) => (
            <Box>
              <Text size="small" color="text-weak">{p.detail}</Text>
              {p.reason && <Text size="xsmall" color="text-critical">{p.reason}</Text>}
            </Box>
          ),
        },
      ]}
      data={rows}
      primaryKey="name"
    />
  );
}

function Provision({ state, setState }: { state: string; setState: (s: string) => void }) {
  const [authorised, setAuthorised] = useState(false);
  const at = PART_OF[state] ?? 0;
  const next = (s: string) => () => setState(s);
  const conflict = state === 'conflict';
  const created = state === 'created' || state === 'verified';
  const verified = state === 'verified';

  const primary: Action = {
    compose: { label: 'Build plan', onClick: next('plan') },
    plan: { label: 'Create storage objects', onClick: next('created') },
    conflict: { label: 'Rebuild plan', onClick: next('plan') },
    created: { label: 'Verify paths', onClick: next('verified') },
    verified: { label: 'Continue to Replication' },
  }[state] as Action;
  const actions: Action[] = {
    compose: [{ label: 'Continue without provisioning' }],
    plan: [{ label: 'Rebuild plan' }, { label: 'Continue without provisioning' }],
    conflict: [{ label: 'Continue without provisioning' }],
    created: [{ label: 'Rebuild plan' }],
    verified: [{ label: 'Verify paths again' }, { label: 'Rebuild plan' }],
  }[state] as Action[];
  const confirmation: Confirmation | undefined = state === 'plan'
    ? { label: 'I have reviewed this plan and authorise creating these objects on the array.', checked: authorised, onChange: setAuthorised }
    : undefined;

  const done: { text: string; again?: string; detail?: React.ReactNode }[] = [];
  if (at >= 1) done.push({ text: 'Composition saved: zz_rc_hs with ESX1 · 1 export, zz_rc_vvs → zz_rc_hs, LUN auto.', again: created ? undefined : 'Edit', detail: <Compose readOnly /> });
  if (created) done.push({ text: 'Plan approved at 19:44: 4 to create, 1 already there.', detail: <PlanTable rows={PLAN} /> });
  if (created) done.push({
    text: 'Created at 19:45: 4 created, 1 left untouched, none failed.',
    detail: (
      <Box gap="small" flex={false}>
        <DataTable
          columns={[
            { property: 'kind', header: 'Kind', render: (r) => <Text size="small">{r.kind}</Text> },
            { property: 'name', header: 'Name', render: (r) => <Text size="small" style={mono}>{r.name}</Text> },
            { property: 'result', header: 'Result', render: (r) => <StatusIndicator state="complete" label={r.result} /> },
            { property: 'detail', header: 'Detail', render: (r) => <Text size="small" color="text-weak">{r.detail}</Text> },
          ]}
          data={RESULT}
          primaryKey="name"
        />
        <Section title="To remove what this run created" summary="4 commands, in the right order" level={3}>
          <CodeBlock lines={REMOVAL} a11yTitle="Removal commands" />
          <Box direction="row" gap="small"><Button size="small" label="Copy" /><Button size="small" label="Download .txt" /></Box>
        </Section>
      </Box>
    ),
  });

  return (
    <AppFrame run={RUN} groups={rail('provision', verified ? 'complete' : 'action_required')} current="provision">
      <StepPage
        stepLabel={stepLabel('provision')}
        title="Provision storage"
        description="Creates the hosts, host sets, volumes and exports on the array. Nothing is written until you approve the plan."
        state={verified ? 'complete' : conflict ? 'failed' : 'action_required'}
        stateLabel={verified ? 'Provisioned' : conflict ? 'Plan blocked' : `Part ${at + 1} of 4`}
        primary={primary}
        actions={actions}
        confirmation={confirmation}
        guideOpen={false}
        top={<PartsBar parts={PARTS} at={at} doneAll={verified} />}
        activity={{
          last: verified ? '19:47:02  Paths verified: ESX1 1 LUN over 2 HBAs, 4 paths' : created ? '19:45:31  Export created and read back: LUN 1' : at >= 1 ? '19:44:10  Plan built: 4 to create, 1 exists' : '19:41:55  Composition loaded from the run',
          events: 20 + at * 4,
          commands: 31 + at * 6,
        }}
        guidance={
          <Guidance
            items={[
              { title: 'What this step writes', body: 'Only what the plan shows, and only after your tick. Objects marked Exists are left alone; Update adds to an existing object without removing anything.' },
              { title: 'Discovery feeds it', body: 'The hosts come from Discovery, read at 19:22. Run Discovery again if the hosts have changed since.' },
              { title: 'If something has the same name', body: 'An object on the array with the same name but different attributes is a conflict. The plan cannot be applied until it is resolved on the array or the plan is changed.' },
              { title: 'Path verification', body: "After creating, the array is read back per host: LUNs, HBAs, paths and fabrics. For ESXi hosts the host's own view from vCenter too (a new LUN needs a storage rescan). A report, never a gate." },
            ]}
          />
        }
      >
        {done.length > 0 && <DoneList items={done} />}

        {state === 'compose' && (
          <Box gap="medium" flex={false}>
            <Compose readOnly={false} />
            <EmptyState icon={<Storage size="large" color="icon-weak" />} title={<>No plan yet<Mark n={1} /></>}>
              Build the plan to see what will be created, what is already on the array and what conflicts. Nothing is created until you approve it.
            </EmptyState>
          </Box>
        )}

        {(state === 'plan' || conflict) && (
          <Box gap="small" flex={false}>
            {conflict ? (
              <StatusLine state="failed" time="19:44">
                1 conflict: the host set zz_rc_hs is on the array with other members. Change the name on the sheet or resolve it on the array, then rebuild the plan.<Mark n={2} />
              </StatusLine>
            ) : (
              <StatusLine state="action_required" time="19:44">
                Plan built: 4 to create, 1 already there, 0 conflicts. Review it, tick the box, then create.<Mark n={2} />
              </StatusLine>
            )}
            <Panel title="Review the plan" right={<Text size="small" color="text-weak">{conflict ? '3 to create · 1 already there · 1 conflict' : '4 to create · 0 to update · 1 already there · 0 conflicts'}</Text>}>
              <PlanTable rows={conflict ? CONFLICT : PLAN} />
              <Text size="xsmall" color="text-weak">Plan note: the export LUN is chosen by the array at create time and read back afterwards.</Text>
            </Panel>
          </Box>
        )}

        {created && !verified && (
          <Box gap="small" flex={false}>
            <StatusLine state="complete" time="19:45">4 objects created on AlletraMP_D22U27, 1 left untouched. Verify the paths before you continue.<Mark n={3} /></StatusLine>
            <EmptyState title="Paths not verified yet">
              Verify paths reads the array back per host: how many LUNs are live, over how many HBAs, with how many paths, on which fabrics. For ESX1 it also asks vCenter what the host sees.
            </EmptyState>
          </Box>
        )}

        {verified && (
          <Box gap="small" flex={false}>
            <StatusLine state="complete" time="19:47">
              ESX1 sees zz_rc_vol01 over 2 HBAs and 4 paths on both fabrics. The ESXi host needs a storage rescan to show it.<Mark n={3} />
            </StatusLine>
            <Panel title="Paths per host" level={2}>
              <DataTable
                columns={[
                  { property: 'host', header: 'Host', render: (h) => <Text size="small" weight={500}>{h.host}</Text> },
                  { property: 'verdict', header: 'Result', render: (h) => <StatusIndicator state={h.ok ? 'complete' : 'action_required'} label={h.verdict} /> },
                  { property: 'array', header: 'Array view', render: (h) => <Text size="small" color="text-weak">{h.array}</Text> },
                  { property: 'esxi', header: 'ESXi view', render: (h) => <StatusIndicator state={h.esxiOk ? 'complete' : 'action_required'} label={h.esxi} /> },
                ]}
                data={[{ host: 'ESX1', ok: true, verdict: 'OK', array: '1 LUN · 2 HBAs · 4 paths · F1 and F2', esxiOk: false, esxi: 'Rescan needed' }]}
                primaryKey="host"
              />
              <Text size="xsmall" color="text-weak">ESXi view is the host's own multipath view through vCenter: a second opinion, never the verdict. After the rescan it reads Visible.</Text>
            </Panel>
          </Box>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const provision: Screen = {
  id: 'M11',
  title: 'Provision storage (the only step that writes)',
  states: [
    { key: 'compose', label: '1. Compose, no plan yet' },
    { key: 'plan', label: '2. Plan to review' },
    { key: 'conflict', label: '2. Plan blocked by a conflict' },
    { key: 'created', label: '3. Created, paths not verified' },
    { key: 'verified', label: '4. Paths verified' },
  ],
  notes: [
    'Four parts in order: compose, review the plan, create, verify paths. The compose form is a form, so its buttons sit bottom left as the Design System places form actions; the step\'s own actions stay in the footer. Below the form, an empty state says there is no plan yet instead of a long paragraph.',
    'The plan: one line with the counts, then the table. Objects already there are green Exists; a conflict is red with the reason under it, and the green button becomes Rebuild plan because Create cannot apply. The authorisation tick is in the footer next to Create storage objects.',
    'After creating: the result folds to one line with Show detail (the result table and the removal commands). Path verification is its own part with its own empty state, then a table per host with the array\'s view and the ESXi view side by side.',
  ],
  keeps: [
    ['Compose card (host-set members, export rows, LUN, Add export row, Save composition, Reload)', 'Part 1, Compose'],
    ['Discovery freshness note', 'Right panel, Discovery feeds it'],
    ['Build plan / Rebuild plan', 'Footer (green) in part 1; Rebuild plan beside the green button afterwards'],
    ['Plan table with Create / Exists / Update / Conflict, counts, plan notes, "was …"', 'Part 2, Review the plan'],
    ['Authorise tick', 'Footer, next to Create storage objects'],
    ['Create storage objects', 'Footer, right (green) in part 2'],
    ['Result table, removal set with Copy and Download .txt', 'Finished line, Show detail'],
    ['Verify paths and its table (array view, ESXi view)', 'Part 4'],
    ['Continue without provisioning', 'Footer, beside the green button, until something is created'],
  ],
  render: (state, setState) => <Provision state={state} setState={setState} />,
};
