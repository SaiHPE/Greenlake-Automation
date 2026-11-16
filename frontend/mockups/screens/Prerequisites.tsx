import { Anchor, Box, Button, CheckBox, DataTable, Heading, Text, TextInput } from 'grommet';
import { PlayFill } from 'grommet-icons';
import { useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { stepLabel, rail } from '../data';
import { AppFrame, Guidance, Mark, Section, StatusLine, StepPage } from '../kit';
import { Screen } from '../screen';

const ENDPOINTS = [
  { fqdn: 'global.api.greenlake.hpe.com', result: 'Reachable', detail: 'via proxy, 210 ms' },
  { fqdn: 'sso.common.cloud.hpe.com', result: 'Reachable', detail: 'via proxy, 190 ms' },
  { fqdn: 'console-jp1.data.cloud.hpe.com', result: 'Reachable', detail: 'via proxy, 240 ms' },
  { fqdn: 'device.cloud.hpe.com', result: 'Reachable', detail: 'via proxy, 220 ms' },
];

function Recording({ title, steps }: { title: string; steps: string[] }) {
  return (
    <Box direction="row" gap="medium" align="start" flex={false}>
      <Box width="small" height="xsmall" background="background-contrast" round="xsmall" align="center" justify="center" flex={false}>
        <Button icon={<PlayFill />} a11yTitle={`Play the recording: ${title}`} />
      </Box>
      <Box gap="xxsmall">
        <Text size="small" weight={600}>{title}</Text>
        {steps.map((s, i) => <Text key={i} size="small">{i + 1}. {s}</Text>)}
      </Box>
    </Box>
  );
}

function Confirm({ done, set }: { done: boolean; set: (v: boolean) => void }) {
  return (
    <Box direction="row" gap="xsmall" align="center" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
      <CheckBox label="Done" checked={done} onChange={(e) => set(e.target.checked)} />
    </Box>
  );
}

function Prerequisites({ state }: { state: string }) {
  const clockOk = state === 'all-passed';
  const [done, setDone] = useState<Record<string, boolean>>({});
  const tick = (k: string) => (v: boolean) => setDone((d) => ({ ...d, [k]: v }));
  return (
    <AppFrame groups={rail('prereq')} current="prereq" railNote="The steps of your run appear here once you choose what to do (step 3).">
      <StepPage
        stepLabel={stepLabel('prereq')}
        first
        runExists={false}
        title="Prerequisites"
        description="What HPE requires before onboarding, and checks of this workstation."
        state={clockOk ? 'complete' : 'action_required'}
        stateLabel={clockOk ? 'Checks passed' : 'Action required'}
        actions={clockOk
          ? [{ label: 'Download the initialisation sheet' }]
          : [{ label: 'Download the initialisation sheet' }, { label: 'Continue without syncing' }]}
        primary={clockOk ? { label: 'Continue to Initialisation sheet' } : { label: 'Sync system clock' }}
        activity={{ last: '19:20:41  Connectivity test: 12 of 12 endpoints reachable', events: 3, commands: 0 }}
        guidance={
          <Guidance
            items={[
              { title: 'What this step is for', body: 'Everything here is preparation HPE requires before a B10000 is onboarded. The tool checks the connection, the proxy and the clock itself. You confirm the rest.' },
              { title: 'Nothing is changed', body: 'This step makes no changes to the array or to HPE GreenLake.' },
              { title: 'Where this comes from', body: <>HPE's <Anchor label="onboarding checklist" href="#" /> and the installation guide sd00002405. The recordings are HPE's own walkthroughs.</> },
            ]}
          />
        }
      >
        <StatusLine state={clockOk ? 'complete' : 'action_required'} time="checked 19:20">
          {clockOk
            ? '3 of 3 checks passed. Confirm the 4 items below, then continue.'
            : '2 of 3 checks passed. The clock is 11 seconds off: sync it before you start.'}
          <Mark n={1} />
        </StatusLine>

        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Checked by this tool<Mark n={2} /></Heading>
          <Section
            level={3}
            title="Connection to HPE GreenLake"
            summary="12 of 12 endpoints reachable · region jp1"
            right={<StatusIndicator state="complete" label="Passed" />}
          >
            <Box direction="row" gap="small" align="center">
              <Text size="small" color="text-weak">DSCC region</Text>
              <Box width="xsmall"><TextInput size="small" value="jp1" readOnly aria-label="DSCC region" /></Box>
              <Button size="small" label="Retest" />
              <Anchor size="small" label="Download the list for the firewall team" href="#" />
            </Box>
            <DataTable
              columns={[
                { property: 'fqdn', header: 'Endpoint', render: (r) => <Text size="small">{r.fqdn}</Text> },
                { property: 'result', header: 'Result', render: () => <StatusIndicator state="complete" label="Reachable" /> },
                { property: 'detail', header: 'Detail', render: (r) => <Text size="small" color="text-weak">{r.detail}</Text> },
              ]}
              data={ENDPOINTS}
              primaryKey="fqdn"
            />
            <Text size="small" color="text-weak">8 more endpoints, all reachable.</Text>
            <Text size="small">Also needed: mDNS on UDP 5353 for local discovery; the array's DNS resolves HPE's global names; 16.1.8.x and 16.1.9.x stay unassigned (reserved for the array).</Text>
          </Section>
          <Section
            level={3}
            title="Proxy"
            summary="In use: system proxy web-proxy.corp.hpe.com:8080"
            right={<StatusIndicator state="complete" label="Detected" />}
          >
            <Box direction="row" gap="small" align="center" wrap>
              <Box width="medium"><TextInput size="small" placeholder="host:port" aria-label="Manual proxy override" /></Box>
              <Button size="small" label="Save and retest" />
              <Button size="small" label="Connect directly (no proxy)" />
            </Box>
          </Section>
          <Section
            level={3}
            title="Workstation clock"
            summary={clockOk ? 'In sync' : 'Off by 11 seconds'}
            open={!clockOk}
            right={<StatusIndicator state={clockOk ? 'complete' : 'action_required'} label={clockOk ? 'Passed' : 'Sync needed'} />}
          >
            <Text size="small">A clock that is off stops the array connecting to DSCC (the error says "iat is in the future"). Sync system clock, bottom right, sets it; the app must run as Administrator for that.<Mark n={5} /></Text>
          </Section>
        </Box>

        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Confirm before you start<Mark n={3} /></Heading>
          <Section
            level={3}
            title="HPE GreenLake workspace and DSCC"
            summary="Activate the subscriptions, then 3 tasks in HPE GreenLake · recordings"
            right={<Confirm done={!!done.ws} set={tick('ws')} />}
          >
            <Text size="small">Activate the software subscriptions from the Electronic Software Delivery receipt email. Then sign in to <Anchor label="HPE GreenLake" href="#" /> and do these in order.</Text>
            <Recording title="1. Create the workspace" steps={['Select Create Workspace and give the name, country, address, phone and email.', 'Accept the terms and select Create Workspace. You become the workspace administrator.']} />
            <Recording title="2. Deploy Data Services Cloud Console" steps={['Find Services, Storage, Data Services, Provision.', 'Pick the region nearest the array, accept the terms, Deploy.', 'Select Launch to open DSCC.']} />
            <Recording title="3. Assign the Data Services administrator role" steps={['Manage Workspace, Identity and Access, Assign Role: your user, Data Services, Administrator.', 'Launch Data Services and check Setup, Block Storage and Data Ops Manager appear.']} />
          </Section>
          <Section
            level={3}
            title="API client"
            summary="Create a personal API client; its ID, secret and token URL go in the sheet"
            right={<Confirm done={!!done.api} set={tick('api')} />}
          >
            <Recording title="4. Create a personal API client" steps={['Manage Workspace, API, Create personal API client.', 'Name it and pick the HPE GreenLake Cloud Platform service.', 'Write down the client ID, secret and token URL. The secret is shown once.', 'Enter all three in the initialisation sheet.']} />
          </Section>
          <Section
            level={3}
            title="Management network cabling"
            summary="Admin, iLO and CDM ports on every controller"
            right={<Confirm done={!!done.cab} set={tick('cab')} />}
          >
            <Text size="small">Admin port: each controller to the management LAN. Only one link is active at a time, so cable all of them.</Text>
            <Text size="small">iLO port: each controller's out-of-band port to the same network.</Text>
            <Text size="small">CDM ports: each controller chassis CDM port (OCuLink adapter) and at least one drive-chassis CDM per rack. They pick their own link-local addresses.</Text>
          </Section>
          <Section
            level={3}
            title="This workstation"
            summary="Same subnet as the array, run as Administrator"
            right={<Confirm done={!!done.ws2} set={tick('ws2')} />}
          >
            <Text size="small">The array is racked, cabled and powered on. This workstation is on the array's subnet, so it reaches the wizard's link-local address. The app runs as Administrator. A source install needs the Microsoft Visual C++ redistributable (x64).</Text>
          </Section>
        </Box>
        <Text size="small" color="text-weak">The Done ticks are for you. They do not stop you continuing.<Mark n={4} /></Text>
      </StepPage>
    </AppFrame>
  );
}

export const prerequisites: Screen = {
  id: 'M1',
  title: 'Prerequisites',
  states: [
    { key: 'clock-off', label: 'Clock is off (needs action)' },
    { key: 'all-passed', label: 'All checks passed' },
  ],
  notes: [
    'One line at the top says where you stand: how many checks passed and the one thing to fix.',
    'Every prerequisite from today stays. The three the tool checks for you come first, with their result next to the title.',
    'The four you do by hand come next. Each is one row; open it for the steps and the recording.',
    'Optional idea: a Done tick on each manual row, for your own tracking. It does not block Continue. Say if you want it.',
    'One green button per page, far right, as the Design System places a wizard\'s next action. While the clock is off the green button is Sync system clock; Continue without syncing stays available beside it. Once the clock is in sync the green button is Continue.',
  ],
  keeps: [
    ['Test connectivity, Retest', 'Connection row, Retest'],
    ['DSCC region field, Download list, endpoint table, network notes', 'Connection row'],
    ['Proxy field, Save and retest, Connect directly, Use detected', 'Proxy row'],
    ['Sync system clock', 'Footer, right (green) while the clock is off'],
    ['4 recordings and their steps', 'GreenLake workspace row and API client row'],
    ['Cabling and This workstation text', 'Their own rows'],
    ['Download the initialisation sheet', 'Footer, beside the green button'],
    ['Continue', 'Footer, right (green)'],
  ],
  render: (state) => <Prerequisites state={state} />,
};
