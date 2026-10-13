import { Anchor, Box, Button, FileInput, Grid, RadioButton, Text } from 'grommet';
import { useState } from 'react';
import { StatusIcon, StepState } from '../../src/ui/status';
import { STEPS, rail, stepLabel } from '../data';
import { AppFrame, Guidance, Mark, StatusLine, StepPage } from '../kit';
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
        secondary={[{ label: 'Validate GreenLake credentials', disabled: !read }]}
        primary={{ label: 'Continue to Mode', disabled: !read, hint: 'Upload the workbook first' }}
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
              <Button size="small" secondary label="Upload another" />
            </Box>
          </Box>
        ) : (
          <FileInput name="sheet" messages={{ dropPrompt: 'Drop the completed workbook here', browse: 'browse' }} />
        )}
        {read && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
            <Text weight={600}>What the workbook holds<Mark n={1} /></Text>
            {CONTENTS.map((c) => (
              <Box key={c.tab} direction="row" gap="small" align="center">
                <StatusIcon state={c.state} />
                <Box width="xsmall" flex={false}><Text size="small" weight={600}>{c.tab}</Text></Box>
                <Text size="small">{c.text}</Text>
              </Box>
            ))}
          </Box>
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
    ['Validate GreenLake credentials', 'Footer, left'],
    ['Continue to Mode', 'Footer, right (green)'],
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
  { key: 'custom', title: 'Custom', text: 'Pick the steps yourself.', steps: [] },
];
const LABEL: Record<string, string> = Object.fromEntries(STEPS.map((s) => [s.key, s.label]));
LABEL.greenlake = 'GreenLake registration';
LABEL.cloudinit = 'Cloud Connectivity';
LABEL.dscc = 'DSCC Setup';

function Mode() {
  const [mode, setMode] = useState('repl');
  const chosen = MODES.find((m) => m.key === mode)!;
  return (
    <AppFrame
      groups={rail('mode', 'action_required', {}, { runSteps: false, preview: chosen.steps })}
      current="mode"
      railNote={chosen.steps.length ? `${chosen.steps.length} steps for ${chosen.title}. Create the run to start.` : 'Pick the steps on the next screen.'}
    >
      <StepPage
        stepLabel={stepLabel('mode')}
        runExists={false}
        title="What do you want to do?"
        description="The run includes only the steps this choice needs. Each run keeps its own steps; start another run from Runs, top right, to do something else with the same workbook."
        state="action_required"
        stateLabel="Choose a mode"
        primary={{ label: `Create run · ${chosen.steps.length || 'your'} steps` }}
        guideOpen={false}
        activity={{ last: '19:21:58  Workbook read: CZ2D320BT1, 4 tabs', events: 4, commands: 0 }}
        guidance={
          <Guidance
            items={[
              { title: 'You can change your mind', body: 'Each run keeps its own steps. Start another run from Runs, top right, to do something else with the same workbook.' },
              { title: 'Replication needs its tab', body: 'Provision, then replicate is offered when the workbook has the Replication tab filled in.' },
            ]}
          />
        }
      >
        <Grid columns={['flex', 'flex', 'flex']} gap="small">
          {MODES.map((m) => (
            <Box
              key={m.key}
              pad="medium"
              round="small"
              background="background-front"
              border={{ color: m.key === mode ? 'border-selected' : 'border-weak', size: m.key === mode ? 'medium' : 'xsmall' }}
              onClick={() => setMode(m.key)}
              gap="xsmall"
            >
              <Box direction="row" gap="small" align="center">
                <RadioButton name="mode" checked={m.key === mode} onChange={() => setMode(m.key)} label={<Text weight={600}>{m.title}</Text>} />
              </Box>
              <Text size="small" color="text-weak">{m.text}</Text>
            </Box>
          ))}
        </Grid>
        <Text size="small" color="text-weak">
          <Text size="small" weight={600} color="text-strong">This run will do: </Text>
          {chosen.steps.length ? chosen.steps.map((k) => LABEL[k] ?? k).join('  →  ') : 'the steps you tick on the next screen.'}
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
    ['The six mode cards', 'Same six, three per row'],
    ['Create run', 'Footer, right (green)'],
  ],
  render: () => <Mode />,
};
