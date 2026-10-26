import { Box, Button, Heading, Text } from 'grommet';
import { Document, Terminal } from 'grommet-icons';
import { AppFrame, DocList, Mark, PlainPage, RunState, StateIcon } from '../kit';
import { Screen } from '../screen';

interface Run {
  array: string;
  serial: string;
  mode: string;
  where: string;
  state: RunState;
  status: string;
  last: string;
  group: 'you' | 'others' | 'running' | 'done';
}

// Times as the Design System asks: relative while recent, the date once it is not; right-aligned in the column.
const RUNS: Run[] = [
  { array: 'AlletraMP_D22U27', serial: 'CZ2D320BT1', mode: 'Provision, then replicate', where: 'Replication, part 3 of 5', state: 'action_required', status: 'Approve the replication plan', last: 'Today, 19:31', group: 'you' },
  { array: 'CZ2D2K014S (rack13)', serial: 'CZ2D2K014S', mode: 'Full onboarding', where: 'Cloud Connectivity', state: 'failed', status: 'Stopped: the array is not registered in GreenLake', last: 'Today, 11:02', group: 'you' },
  { array: 'AlletraMP_D22U27', serial: 'CZ2D320BT1', mode: 'Provision storage only', where: 'SAN zoning', state: 'waiting', status: 'SAN team: 2 zones for ESX2 on F2', last: 'Sent today, 19:40', group: 'others' },
  { array: 'AlletraMP_E18U31', serial: 'CZ2D3209YV', mode: 'Provision storage only', where: 'As-built downloaded', state: 'complete', status: 'Done', last: '5 Oct 2026', group: 'done' },
  { array: 'AlletraMP_E18U31', serial: 'CZ2D3209YV', mode: 'Verify only', where: '12 of 12 checks match', state: 'complete', status: 'Done', last: '5 Oct 2026', group: 'done' },
];

const GROUPS: { key: Run['group']; title: string }[] = [
  { key: 'you', title: 'Needs you' },
  { key: 'others', title: 'Waiting on others' },
  { key: 'done', title: 'Done' },
];

function Home() {
  return (
    <AppFrame right={<Text size="small" color="text-weak">Jump box LABRAT</Text>}>
      <PlainPage
        title="Your runs"
        subtitle="Tuesday 13 October 2026 · 5 runs on this jump box"
        actions={<Box direction="row" align="center"><Button primary label="Start a new run" /><Mark n={1} /></Box>}
      >
        <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false} aria-label="Runs, grouped by who they wait on">
          {GROUPS.map((g) => {
            const rows = RUNS.filter((r) => r.group === g.key);
            if (!rows.length) return null;
            return (
              <Box key={g.key} flex={false}>
                <Box direction="row" gap="small" align="center" pad={{ horizontal: 'medium', vertical: 'xsmall' }} background="background-contrast">
                  <Heading level={2} size="xsmall" weight={500} margin="none">{g.title}</Heading>
                  <Text size="small" color="text-weak">{rows.length}</Text>
                  {g.key === 'others' && <Mark n={2} />}
                </Box>
                {rows.map((r) => (
                  <Box
                    key={r.array + r.mode}
                    direction="row"
                    gap="medium"
                    align="center"
                    pad={{ horizontal: 'medium', vertical: 'small' }}
                    border={{ side: 'top', color: 'border-weak' }}
                    hoverIndicator="background-hover"
                    onClick={() => undefined}
                  >
                    <StateIcon state={r.state} />
                    <Box basis="1/3" flex={false}>
                      <Text size="small" weight={500} color="text-strong">{r.array}</Text>
                      <Text size="xsmall" color="text-weak">{r.mode}</Text>
                    </Box>
                    <Box flex>
                      <Text size="small">{r.status}</Text>
                      <Text size="xsmall" color="text-weak">{r.where}</Text>
                    </Box>
                    <Box width="small" flex={false} align="end">
                      <Text size="small" color="text-weak" textAlign="end">{r.last}</Text>
                    </Box>
                    <Button size="small" label={r.group === 'done' ? 'Open' : 'Continue'} />
                  </Box>
                ))}
              </Box>
            );
          })}
        </Box>
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Recent documents<Mark n={3} /></Heading>
          <DocList
            items={[
              { icon: <Document />, name: 'As-built document · AlletraMP_E18U31', detail: '5 Oct 2026 · Provision storage only · 712 KB' },
              { icon: <Terminal />, name: 'Command log · AlletraMP_D22U27', detail: 'Today, 19:31 · Provision, then replicate · 41 commands so far' },
            ]}
          />
        </Box>
      </PlainPage>
    </AppFrame>
  );
}

export const home: Screen = {
  id: 'M7',
  title: 'Home: your runs (new page)',
  notes: [
    'The page the app opens on when you come back. Today it drops you into whatever run was open last, and other runs hide behind "Open another run". A field engineer juggles several arrays and several days; this page shows all of them, grouped by who is waiting on whom.',
    'A new word in the status vocabulary: "Waiting on others", grey with a clock. Zoning handed to the SAN team is not your problem until they are done. Today both this and "approve the plan" are the same orange "Action required".',
    'The documents a customer asks for later, without opening the run.',
  ],
  keeps: [
    ['Open another run (dialog)', 'This page, with status and grouping'],
    ['Start a new deployment', 'Start a new run, top right (green)'],
  ],
  render: () => <Home />,
};
