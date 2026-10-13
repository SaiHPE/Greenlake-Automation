import { Anchor, Box, FileInput, Grid, Heading, RadioButton, Text } from 'grommet';
import { useState } from 'react';
import { StatusIcon, StepState } from '../../src/ui/status';
import { TOTAL, rail, stepNo } from '../data';
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
    <AppFrame groups={rail('sheet')} current="sheet">
      <StepPage
        stepNo={stepNo('sheet')}
        total={TOTAL}
        title="Initialisation sheet"
        description="One workbook per array. Upload it to start a run."
        state={read ? 'complete' : 'action_required'}
        stateLabel={read ? 'Workbook read' : 'Upload the workbook'}
        secondary={[{ label: 'Validate GreenLake credentials', disabled: !read }]}
        primary={{ label: 'Continue to Mode', disabled: !read }}
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
        <FileInput name="sheet" messages={{ dropPrompt: 'Drop the completed workbook here', browse: 'browse' }} />
        {read && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
            <Text weight={600}>What the workbook holds<Mark n={1} /></Text>
            {CONTENTS.map((c) => (
              <Box key={c.tab} direction="row" gap="small" align="center">
                <StatusIcon state={c.state} />
                <Box width="120px" flex={false}><Text size="small" weight={600}>{c.tab}</Text></Box>
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

const MODES: { key: string; title: string; text: string; steps: string[]; needs?: string }[] = [
  { key: 'full', title: 'Full onboarding', text: 'A brand-new array: GreenLake, Cloud Connectivity, DSCC, then verify.', steps: ['GreenLake registration', 'Cloud Connectivity', 'DSCC Setup', 'Verify', 'As-built'] },
  { key: 'prov', title: 'Provision storage only', text: 'An array that is already set up.', steps: ['Discovery', 'SAN zoning', 'Provision storage', 'Verify', 'As-built'] },
  { key: 'both', title: 'Onboard, then provision', text: 'Set up the array, then provision storage.', steps: ['GreenLake registration', 'Cloud Connectivity', 'DSCC Setup', 'Discovery', 'SAN zoning', 'Provision storage', 'Verify', 'As-built'] },
  { key: 'repl', title: 'Provision, then replicate', text: 'Provision, then Remote Copy to the peer array and a failover test.', steps: ['Discovery', 'SAN zoning', 'Provision storage', 'Replication', 'Failover test', 'Verify', 'As-built'] },
  { key: 'verify', title: 'Verify only', text: 'Read the array and compare it with the sheet. Changes nothing.', steps: ['Verify', 'As-built'] },
  { key: 'custom', title: 'Custom', text: 'Pick the steps yourself.', steps: [] },
];

function Mode() {
  const [mode, setMode] = useState('repl');
  const chosen = MODES.find((m) => m.key === mode)!;
  return (
    <AppFrame groups={rail('mode')} current="mode">
      <StepPage
        stepNo={stepNo('mode')}
        total={TOTAL}
        title="What do you want to do?"
        description="The run includes only the steps this choice needs."
        state="action_required"
        stateLabel="Choose a mode"
        primary={{ label: `Create run · ${chosen.steps.length || 'your'} steps` }}
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
        <Grid columns={['flex', 'flex']} gap="small">
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
        <Box background="background-contrast" round="small" pad="medium" gap="xsmall" flex={false}>
          <Heading level={3} size="small" margin="none">This run will do<Mark n={1} /></Heading>
          <Text size="small">{chosen.steps.length ? chosen.steps.join('  →  ') : 'The steps you tick on the next screen.'}</Text>
        </Box>
      </StepPage>
    </AppFrame>
  );
}

export const mode: Screen = {
  id: 'M3',
  title: 'Mode',
  notes: [
    'The steps of the chosen mode show before you create the run, so the step count does not jump from 9 to 11 afterwards. The button says how many steps it creates.',
  ],
  keeps: [
    ['The six mode cards', 'Same six, two per row'],
    ['Create run', 'Footer, right (green)'],
  ],
  render: () => <Mode />,
};
