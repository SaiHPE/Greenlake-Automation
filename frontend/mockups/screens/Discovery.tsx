import { Box, DataTable, Text } from 'grommet';
import { InlineNotification } from '../../src/ui/primitives';
import { StatusIndicator } from '../../src/ui/status';
import { ARRAY_PORTS, HOSTS, RUN, rail, stepLabel } from '../data';
import { AppFrame, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

function Discovery({ state, setState }: { state: string; setState: (s: string) => void }) {
  const done = state === 'done';
  const running = state === 'running';
  return (
    <AppFrame run={RUN} groups={rail('discover', done ? 'complete' : running ? 'running' : 'not_started')} current="discover">
      <StepPage
        stepLabel={stepLabel('discover')}
        title="Discovery"
        description="Reads the array's ports, the hosts and their fabric logins. Changes nothing."
        state={done ? 'complete' : running ? 'running' : 'not_started'}
        stateLabel={done ? 'Complete' : running ? 'Reading' : 'Not started'}
        secondary={done ? [{ label: 'Check readiness' }, { label: 'Run discovery again', onClick: () => setState('running') }] : [{ label: 'Check readiness' }]}
        primary={done ? { label: 'Continue to SAN zoning' } : { label: 'Run discovery', busy: running, onClick: () => setState('running') }}
        activity={{ last: done ? '19:22:43  Discovery finished: 8 ports, 2 hosts, 2 fabrics' : running ? '19:22:31  Reading the array ports' : '19:22:22  Run created', events: done ? 9 : 1, commands: done ? 14 : running ? 3 : 0 }}
        guidance={
          <Guidance
            items={[
              { title: 'What it reads', body: "The array's target ports and host view over SSH and the array API, each ESXi host's adapters from vCenter, and the Windows and Linux hosts listed on the Hosts tab." },
              { title: 'Read-only', body: 'Discovery changes nothing on the array, vCenter or the switches.' },
              { title: 'Kept with the run', body: 'The results stay with this run and survive a restart of the app. Run it again any time.' },
              { title: 'Not sure the array is reachable?', body: 'Check readiness tests the array and vCenter logins first, in a few seconds.' },
            ]}
          />
        }
      >
        {state === 'not-run' && (
          <StatusLine state="not_started">Not run yet. Zoning and provisioning need what discovery finds.<Mark n={1} /></StatusLine>
        )}
        {running && (
          <Box gap="xsmall" flex={false}>
            <StatusLine state="running" time="19:22:31">Reading AlletraMP_D22U27…<Mark n={1} /></StatusLine>
            <Text size="small" color="text-weak">Array ports read · reading the host view · vCenter next</Text>
          </Box>
        )}
        {done && (
          <>
            <StatusLine state="complete" time="19:22">
              Discovery finished: 8 array ports, 2 hosts, 2 fabrics. Nothing was changed.<Mark n={1} />
            </StatusLine>
            <Box flex={false}>
              <InlineNotification
                tone="info"
                title="ESX1 was found from the array, not from vCenter"
                message="vCenter 10.54.154.226 does not manage ESX1. Its two adapters are logged in to the array, and the Hosts tab names it, so it is in this run."
              />
            </Box>
            <Section title={<>8 array ports<Mark n={2} /></>} summary="6 FC ready on 2 fabrics (F1, F2) · 2 RCIP for replication">
              <DataTable
                columns={[
                  { property: 'nsp', header: 'Port', render: (p) => <Text size="small" style={mono}>{p.nsp}</Text> },
                  { property: 'type', header: 'Type', render: (p) => <Text size="small">{p.type}</Text> },
                  { property: 'state', header: 'State', render: () => <StatusIndicator state="complete" label="Ready" /> },
                  { property: 'speed', header: 'Speed', render: (p) => <Text size="small">{p.speed}</Text> },
                  { property: 'fabric', header: 'Fabric', render: (p) => <Text size="small">{p.fabric}</Text> },
                  { property: 'logins', header: 'Logged in', render: (p) => <Text size="small" color="text-weak">{p.logins}</Text> },
                ]}
                data={ARRAY_PORTS}
                primaryKey="nsp"
              />
            </Section>
            <Section title="2 hosts in this run" summary="ESX1 logged in on both fabrics · ESX2 not logged in">
              <DataTable
                columns={[
                  { property: 'name', header: 'Host', render: (h) => <Text size="small" weight={600}>{h.name}</Text> },
                  { property: 'os', header: 'OS', render: (h) => <Text size="small">{h.os}</Text> },
                  { property: 'source', header: 'Found by', render: (h) => <Text size="small">{h.source}</Text> },
                  { property: 'wwpns', header: 'WWPNs (adapter IDs)', render: (h) => <Text size="small" style={mono}>{h.wwpns}</Text> },
                  { property: 'fabrics', header: 'Logged in', render: (h) => <Text size="small" color="text-weak">{h.fabrics}</Text> },
                ]}
                data={HOSTS}
                primaryKey="name"
              />
            </Section>
            <Section title="3 hosts not in this run" summary="in vCenter, not named on the sheet">
              <Text size="small" color="text-weak">esx-lab-03, esx-lab-04, esx-lab-07. Add them to the Hosts tab to include them.</Text>
            </Section>
          </>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const discovery: Screen = {
  id: 'M5',
  title: 'Discovery (the step template)',
  states: [
    { key: 'not-run', label: 'Not run' },
    { key: 'running', label: 'Running' },
    { key: 'done', label: 'Finished' },
  ],
  notes: [
    'Every step follows this template. One line at the top: what happened, in one sentence, with the time. A coloured note only when there is something to know.',
    'Results are sections with the count in the title. They stay folded until you open them, so the page fits on one screen.',
  ],
  keeps: [
    ['Check readiness', 'Footer, left'],
    ['Run discovery / Re-run discovery', 'Footer, right (green) until it has run; then Run discovery again on the left'],
    ['Port, host and fabric tables', 'In their own sections, folded'],
    ['Activity list', 'Bottom line; opens on click'],
    ['Explanations', 'Right panel'],
  ],
  render: (state, setState) => <Discovery state={state} setState={setState} />,
};
