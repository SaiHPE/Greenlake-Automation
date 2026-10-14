import { Anchor, Box, Button, CheckBox, FileInput, Grid, Notification, ResponsiveContext, Text } from 'grommet';
import { useContext, useState } from 'react';
import { StatusIcon, StepState } from '../../src/ui/status';
import { STEPS, rail, stepLabel } from '../data';
import { AppFrame, Guidance, Mark, Panel, SelectorCard, StatusLine, StepPage } from '../kit';
import { Screen } from '../screen';

const CONTENTS: { tab: string; state: StepState; text: string }[] = [
  { tab: 'Initialisation', state: 'complete', text: 'CZ2D320BT1 · AlletraMP_D22U27 · 10.64.122.99 · region jp1' },
  { tab: 'Provisioning', state: 'complete', text: 'Array, vCenter 10.54.154.226, 2 switches · 1 volume (10 GiB) · 1 host set' },
  { tab: 'Hosts', state: 'complete', text: '1 host by name: ESX1' },
  { tab: 'Replication', state: 'complete', text: 'Peer 10.64.154.190 · 1 volume set, sync · failover test on' },
];

function Sheet({ state }: { state: string }) {
  const read = state === 'read';
  return (
    <AppFrame groups={rail('sheet', read ? 'complete' : 'action_required')} current="sheet" railNote="The steps of your run appear here once you choose what to do (step 3).">
      <StepPage
        stepLabel={stepLabel('sheet')}
        runExists={false}
        title="Initialisation sheet"
        description="One workbook per array. Upload it to start a run."
        state={read ? 'complete' : 'action_required'}
        stateLabel={read ? 'Workbook read' : 'Upload the workbook'}
        actions={[{ label: 'Validate GreenLake credentials', blocked: read ? undefined : 'Upload the workbook first. The credentials are read from its Initialisation tab.' }]}
        primary={{ label: 'Continue to Mode', blocked: read ? undefined : 'Upload the completed workbook first.' }}
        activity={{ last: read ? '19:21:58  Workbook read: CZ2D320BT1, 4 tabs' : 'No activity yet', events: read ? 4 : 3, commands: 0 }}
        guidance={
          <Guidance
            items={[
              { title: 'The template', body: <><Anchor label="Download the blank template" href="#" />. Fill the value column for every required field. Leave the field names as they are.</> },
              { title: 'One workbook, one array', body: 'A workbook that names two arrays is refused.' },
              { title: 'Passwords', body: 'The workbook holds the array, vCenter and switch passwords for this run, and the GreenLake API credentials. They are stored on this workstation only.' },
            ]}
          />
        }
      >
        {read && (
          <StatusLine state="complete" time="19:21">
            Workbook read for CZ2D320BT1 (AlletraMP_D22U27). Nothing is sent to the array yet.
          </StatusLine>
        )}
        {read ? (
          <Box direction="row" justify="between" align="center" background="background-front" round="small" border={{ color: 'border-weak' }} pad={{ horizontal: 'medium', vertical: 'small' }} flex={false}>
            <Text size="small">Initialisation_sheet.xlsx · 48 KB</Text>
            <Box direction="row" gap="small">
              <Button size="small" label="Remove" />
              <Button size="small" label="Upload another" />
            </Box>
          </Box>
        ) : (
          <FileInput name="sheet" messages={{ dropPrompt: 'Drop the completed workbook here', browse: 'browse' }} />
        )}
        {read && (
          <Panel title={<>What the workbook holds<Mark n={1} /></>}>
            {CONTENTS.map((c) => (
              <Box key={c.tab} direction="row" gap="small" align="center">
                <StatusIcon state={c.state} />
                <Box width="xsmall" flex={false}><Text size="small" weight={500}>{c.tab}</Text></Box>
                <Text size="small">{c.text}</Text>
              </Box>
            ))}
          </Panel>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const sheet: Screen = {
  id: 'M2',
  title: 'Initialisation sheet',
  states: [
    { key: 'empty', label: 'Before upload' },
    { key: 'read', label: 'Workbook read' },
  ],
  notes: [
    'After upload you see what the workbook holds, tab by tab, so a missing tab shows before you pick a mode.',
  ],
  keeps: [
    ['Download blank template', 'Right panel'],
    ['Upload box', 'Same place'],
    ['Validate GreenLake credentials', 'Footer, beside the green button'],
    ['Continue to Mode', 'Footer, right (green). Active before the upload: pressing it says what is missing, as the Design System asks, instead of a greyed button'],
    ['Note about passwords', 'Right panel, corrected: the array password is in the Provisioning tab now'],
  ],
  render: (state) => <Sheet state={state} />,
};

// ------------------------------------------------------------------ mode

const MODES: { key: string; title: string; text: string; steps: string[] }[] = [
  { key: 'full', title: 'Full onboarding', text: 'A brand-new array: GreenLake, Cloud Connectivity, DSCC, then verify.', steps: ['greenlake', 'cloudinit', 'dscc', 'verify', 'asbuilt'] },
  { key: 'prov', title: 'Provision storage only', text: 'An array that is already set up.', steps: ['discover', 'zoning', 'provision', 'verify', 'asbuilt'] },
  { key: 'both', title: 'Onboard, then provision', text: 'Set up the array, then provision storage.', steps: ['greenlake', 'cloudinit', 'dscc', 'discover', 'zoning', 'provision', 'verify', 'asbuilt'] },
  { key: 'repl', title: 'Provision, then replicate', text: 'Provision, then Remote Copy to the peer array and a failover test.', steps: ['discover', 'zoning', 'provision', 'replicate', 'failover', 'verify', 'asbuilt'] },
  { key: 'verify', title: 'Verify only', text: 'Read the array and compare it with the sheet. Changes nothing.', steps: ['verify', 'asbuilt'] },
  { key: 'custom', title: 'Custom', text: 'Pick the steps yourself, below.', steps: [] },
];
const LABEL: Record<string, string> = Object.fromEntries(STEPS.map((s) => [s.key, s.label]));
LABEL.greenlake = 'GreenLake registration';
LABEL.cloudinit = 'Cloud Connectivity';
LABEL.dscc = 'DSCC Setup';

// The step catalogue the app serves, with its one-line subtitles, grouped by stage for the picker.
const CATALOG: { stage: string; steps: { key: string; label: string; subtitle: string }[] }[] = [
  { stage: 'Onboard', steps: [
    { key: 'greenlake', label: 'GreenLake registration', subtitle: 'Register, assign and subscribe' },
    { key: 'cloudinit', label: 'Cloud Connectivity', subtitle: 'Connect the array to HPE GreenLake' },
    { key: 'dscc', label: 'DSCC Setup', subtitle: 'Set Up System wizard' },
  ] },
  { stage: 'Provision', steps: [
    { key: 'discover', label: 'Discovery', subtitle: 'Array ports, host adapters, fabric logins' },
    { key: 'zoning', label: 'SAN zoning', subtitle: 'Check the zoning, draft the switch commands' },
    { key: 'provision', label: 'Provision storage', subtitle: 'Hosts, volumes and exports' },
  ] },
  { stage: 'Replicate', steps: [
    { key: 'replicate', label: 'Replication', subtitle: 'Remote Copy groups to the peer array' },
    { key: 'failover', label: 'Failover test', subtitle: 'Fail over, recover, restore' },
  ] },
  { stage: 'Document', steps: [
    { key: 'verify', label: 'Verify configuration', subtitle: 'Read-only configuration check' },
    { key: 'asbuilt', label: 'As-built document', subtitle: 'Hand-over document' },
  ] },
];
const ORDER = CATALOG.flatMap((g) => g.steps.map((s) => s.key));

function Mode({ state }: { state: string }) {
  const size = useContext(ResponsiveContext);
  const columns = size === 'xsmall' ? 1 : size === 'small' ? 2 : 3;
  const custom = state.startsWith('custom');
  const [mode, setMode] = useState(custom ? 'custom' : 'repl');
  const [picked, setPicked] = useState<string[]>(state === 'custom-missing' ? ['zoning', 'provision', 'verify'] : ['discover', 'zoning', 'provision', 'verify']);
  const preset = MODES.find((m) => m.key === mode)!;
  const steps = mode === 'custom' ? ORDER.filter((k) => picked.includes(k)) : preset.steps;
  const missingDiscovery = mode === 'custom' && (picked.includes('zoning') || picked.includes('provision')) && !picked.includes('discover');
  const blocked = mode === 'custom' && picked.length === 0 ? 'Tick at least one step.' : missingDiscovery ? 'Add Discovery: SAN zoning and Provision storage work from what it finds.' : undefined;
  const toggle = (key: string) => (on: boolean) => setPicked((p) => (on ? [...p, key] : p.filter((k) => k !== key)));
  return (
    <AppFrame
      groups={rail('mode', 'action_required', {}, { runSteps: false, preview: steps })}
      current="mode"
      railNote={steps.length ? `${steps.length} steps for ${preset.title}. Create the run to start.` : 'Tick the steps to see them here.'}
    >
      <StepPage
        stepLabel={stepLabel('mode')}
        runExists={false}
        title="What do you want to do?"
        description="The run includes only the steps this choice needs. Each run keeps its own steps; start another run from Runs, top right, to do something else with the same workbook."
        state="action_required"
        stateLabel={mode === 'custom' ? 'Pick the steps' : 'Choose a mode'}
        primary={{ label: `Create run · ${steps.length} step${steps.length === 1 ? '' : 's'}`, blocked }}
        guideOpen={false}
        activity={{ last: '19:21:58  Workbook read: CZ2D320BT1, 4 tabs', events: 4, commands: 0 }}
        guidance={
          <Guidance
            items={[
              { title: 'You can change your mind', body: 'Each run keeps its own steps. Start another run from Runs, top right, to do something else with the same workbook.' },
              { title: 'Replication needs its tab', body: 'Provision, then replicate, and the Replication and Failover test steps, are offered when the workbook has the Replication tab filled in.' },
              { title: 'Custom', body: 'SAN zoning and Provision storage work from what Discovery finds, so a custom run that has either of them needs Discovery too.' },
            ]}
          />
        }
      >
        <Grid columns={{ count: columns, size: 'auto' }} gap="small" role="radiogroup" aria-label="What do you want to do?">
          {MODES.map((m) => (
            <SelectorCard key={m.key} title={m.title} checked={m.key === mode} onSelect={() => setMode(m.key)}>
              <Text size="small" color="text-weak">{m.text}</Text>
            </SelectorCard>
          ))}
        </Grid>
        {mode === 'custom' && (
          <Panel title={<>Steps to run<Mark n={2} /></>} right={<Text size="small" color="text-weak">{picked.length} of {ORDER.length} ticked</Text>}>
            <Grid columns={{ count: 'fit', size: 'small' }} gap="medium">
              {CATALOG.map((g) => (
                <Box key={g.stage} gap="xsmall" flex={false}>
                  <Text size="small" weight={500} color="text-weak">{g.stage}</Text>
                  {g.steps.map((s) => (
                    <CheckBox
                      key={s.key}
                      checked={picked.includes(s.key)}
                      onChange={(e) => toggle(s.key)(e.target.checked)}
                      label={
                        <Box>
                          <Text size="small">{s.label}</Text>
                          <Text size="xsmall" color="text-weak">{s.subtitle}</Text>
                        </Box>
                      }
                    />
                  ))}
                </Box>
              ))}
            </Grid>
            {missingDiscovery && (
              <Notification status="warning" message="SAN zoning and Provision storage work from the discovery results. Tick Discovery as well." />
            )}
          </Panel>
        )}
        <Text size="small" color="text-weak">
          <Text size="small" weight={500} color="text-strong">This run will do: </Text>
          {steps.length ? steps.map((k) => LABEL[k] ?? k).join('  →  ') : 'the steps you tick above.'}
          <Mark n={1} />
        </Text>
      </StepPage>
    </AppFrame>
  );
}

export const mode: Screen = {
  id: 'M3',
  title: 'Mode',
  notes: [
    'The steps of the chosen mode show in the list on the left as you pick, so the count does not jump from 9 to 11 after the run is created. The button says how many steps it creates.',
  ],
  keeps: [
    ['The six mode cards', 'Same six, as Design System selector cards: the whole card is the choice, as many per row as fit'],
    ['Create run', 'Footer, right (green)'],
  ],
  render: () => <Mode state="preset" />,
};

export const custom: Screen = {
  id: 'M15',
  title: 'Custom: pick the steps',
  states: [
    { key: 'custom', label: 'A valid pick (4 steps)' },
    { key: 'custom-missing', label: 'Zoning without Discovery' },
  ],
  notes: [
    'Same screen as Mode. Choosing Custom opens the step list under the cards, in the order the run will take them, grouped by stage, each with the one line that says what it does. The list on the left fills in as you tick.',
    'A pick that cannot run (SAN zoning without Discovery) says so right under the list, and Create run says it again if pressed. The button is never greyed out.',
  ],
  keeps: [
    ['Custom mode card', 'Same card'],
    ['Steps to run checkboxes with their subtitles', 'Steps to run panel, grouped by stage'],
    ['"Discovery is required" warning', 'Under the list, and the Create run message'],
    ['"The Replication tab is required" warning', 'Same place when the workbook has no Replication tab (this workbook has one)'],
    ['Create run', 'Footer, right (green), with the step count'],
  ],
  render: (state) => <Mode state={state} />,
};
