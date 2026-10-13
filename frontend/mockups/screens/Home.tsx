import { Box, Button, DataTable, Heading, Text } from 'grommet';
import { Document, Terminal } from 'grommet-icons';
import { HpeElement } from '../../src/ui/AppChrome';
import { Mark, RunState, StateLabel } from '../kit';
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

const RUNS: Run[] = [
  { array: 'AlletraMP_D22U27', serial: 'CZ2D320BT1', mode: 'Provision, then replicate', where: 'Replication · part 3 of 5', state: 'action_required', status: 'Waiting for you: approve the plan', last: 'today 19:31', group: 'you' },
  { array: 'CZ2D2K014S (rack13)', serial: 'CZ2D2K014S', mode: 'Full onboarding', where: 'Cloud Connectivity', state: 'failed', status: 'Stopped: the array says it is not registered in GreenLake', last: 'today 11:02', group: 'you' },
  { array: 'AlletraMP_D22U27', serial: 'CZ2D320BT1', mode: 'Provision storage only', where: 'SAN zoning', state: 'waiting', status: 'Waiting on the SAN team: 2 zones for ESX2 on F2, sent 19:40', last: 'today 19:40', group: 'others' },
  { array: 'AlletraMP_E18U31', serial: 'CZ2D3209YV', mode: 'Provision storage only', where: 'Done', state: 'complete', status: 'Done · as-built downloaded', last: '05/10/2026', group: 'done' },
  { array: 'AlletraMP_E18U31', serial: 'CZ2D3209YV', mode: 'Verify only', where: 'Done', state: 'complete', status: 'Done · 12 of 12 checks match', last: '05/10/2026', group: 'done' },
];

const GROUPS: { key: Run['group']; title: string; text: string }[] = [
  { key: 'you', title: 'Needs you', text: 'A decision or a fix is waiting.' },
  { key: 'others', title: 'Waiting on others', text: 'Nothing for you to do until they are done. Check again when they tell you.' },
  { key: 'done', title: 'Done', text: 'Documents stay available.' },
];

function Home() {
  return (
    <Box fill background="background-back">
      <Box
        direction="row"
        justify="between"
        align="center"
        pad={{ horizontal: 'medium', vertical: 'small' }}
        background="background-front"
        border={{ side: 'bottom', color: 'border-weak' }}
        flex={false}
      >
        <Box direction="row" gap="small" align="center">
          <HpeElement width={36} />
          <Text weight="bold" color="text-strong">Alletra MP Onboarding</Text>
        </Box>
        <Text size="small" color="text-weak">Jump box LABRAT · 5 runs</Text>
      </Box>
      <Box flex overflow="auto">
        <Box pad={{ horizontal: 'large', vertical: 'medium' }} flex={false} style={{ gap: '24px' }}>
          <Box direction="row" justify="between" align="end" flex={false}>
            <Box>
              <Text size="small" color="text-weak">Tuesday 13 October 2026</Text>
              <Heading level={1} size="small" margin="none">Your runs</Heading>
            </Box>
            <Button primary label="Start a new run" />
            <Mark n={1} />
          </Box>
          {GROUPS.map((g) => {
            const rows = RUNS.filter((r) => r.group === g.key);
            if (!rows.length) return null;
            return (
              <Box key={g.key} gap="xsmall" flex={false}>
                <Box direction="row" gap="small" align="baseline">
                  <Heading level={2} size="small" margin="none">{g.title} · {rows.length}</Heading>
                  <Text size="small" color="text-weak">{g.text}</Text>
                  {g.key === 'others' && <Mark n={2} />}
                </Box>
                <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
                  <DataTable
                    columns={[
                      { property: 'array', header: 'Array', render: (r: Run) => (
                        <Box><Text size="small" weight={600}>{r.array}</Text><Text size="xsmall" color="text-weak">{r.serial} · {r.mode}</Text></Box>
                      ) },
                      { property: 'status', header: 'Where it stands', render: (r: Run) => (
                        <Box><StateLabel state={r.state} label={r.status} /><Text size="xsmall" color="text-weak">{r.where}</Text></Box>
                      ) },
                      { property: 'last', header: 'Last activity', size: 'small', render: (r: Run) => <Text size="small" color="text-weak">{r.last}</Text> },
                      { property: 'open', header: '', size: 'xsmall', render: (r: Run) => (
                        <Button size="small" secondary={r.group === 'you'} label={r.group === 'done' ? 'Open' : 'Continue'} />
                      ) },
                    ]}
                    data={rows}
                    primaryKey={false}
                    pad={{ horizontal: 'medium', vertical: 'small' }}
                  />
                </Box>
              </Box>
            );
          })}
          <Box gap="small" flex={false}>
            <Heading level={2} size="small" margin="none">Recent documents<Mark n={3} /></Heading>
            <Box direction="row" gap="small" wrap>
              <Button secondary icon={<Document />} label="As-built · AlletraMP_E18U31 · 05/10" />
              <Button secondary icon={<Terminal />} label="Command log · AlletraMP_D22U27 · today" />
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
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
