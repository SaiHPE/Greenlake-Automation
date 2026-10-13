import { Box, Button, DataTable, Text } from 'grommet';
import { Copy, Download } from 'grommet-icons';
import { StatusIndicator } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { AppFrame, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const HOSTS = [
  { host: 'ESX1', f1: 'Zoned · logged in on 0:3:1, 1:3:1', f2: 'Zoned · logged in on 0:3:4, 1:3:4', ok: true },
  { host: 'ESX2', f1: 'Zoned · logged in on 0:3:1, 1:3:1', f2: 'Not zoned · 2 zones in the command set', ok: false },
];

const F2_COMMANDS = [
  'alicreate "ESX2_hba2", "10:00:00:90:fa:8b:2c:11"',
  'alicreate "CZ2D320BT1_N0S3P4", "20:34:00:02:ac:01:2d:ef"',
  'alicreate "CZ2D320BT1_N1S3P4", "21:34:00:02:ac:01:2d:ef"',
  'zonecreate "ESX2_hba2_CZ2D320BT1_N0S3P4", "ESX2_hba2; CZ2D320BT1_N0S3P4"',
  'zonecreate "ESX2_hba2_CZ2D320BT1_N1S3P4", "ESX2_hba2; CZ2D320BT1_N1S3P4"',
  'cfgadd "lab_F2_cfg", "ESX2_hba2_CZ2D320BT1_N0S3P4; ESX2_hba2_CZ2D320BT1_N1S3P4"',
  'cfgsave',
];

function Handoff({ state }: { state: string }) {
  const back = state === 'back';
  return (
    <AppFrame
      run={{ ...RUN, state: back ? 'complete' : 'waiting', stateLabel: back ? 'Zoned' : 'Waiting on the SAN team' }}
      groups={rail('zoning', back ? 'complete' : 'waiting')}
      current="zoning"
    >
      <StepPage
        stepLabel={stepLabel('zoning')}
        title="SAN zoning"
        description="Which hosts can reach the array through the fabrics, and the zones the SAN team still has to add. This tool never writes to a switch."
        state={back ? 'complete' : 'waiting'}
        stateLabel={back ? 'All hosts zoned' : 'Waiting on the SAN team'}
        secondary={back ? [{ label: 'Check zoning again' }] : [{ label: 'Continue with ESX1 only' }]}
        primary={back ? { label: 'Continue to Provision storage' } : { label: 'Check zoning again' }}
        guideOpen={false}
        activity={{ last: back ? '09:12:04  Zoning checked: ESX2 logged in on F2' : '19:40:12  Command set for F2 copied (7 lines)', events: 14, commands: 31 }}
        guidance={
          <Guidance
            items={[
              { title: 'How zoning is checked', body: "From the array: a host adapter can log in to an array port only through a working zone, so the array's logins show the zoning that is in effect. No switch login is needed for the check." },
              { title: 'The command set', body: 'Built from a read of both switches. Your SAN team pastes it; cfgenable is their call and is shown separately. The tool never writes to a switch.' },
              { title: 'Per host', body: 'Provisioning is allowed per host once it is zoned on both fabrics. Hosts not yet zoned are skipped by name and can join a later run.' },
            ]}
          />
        }
      >
        {back ? (
          <StatusLine state="complete" time="09:12">
            Both hosts are zoned on both fabrics. ESX2 logged in on F2 at 09:11, 13 hours after the command set was handed over.<Mark n={1} />
          </StatusLine>
        ) : (
          <StatusLine state="waiting" time="since 19:40">
            Waiting on the SAN team: 2 zones for ESX2 on fabric F2. The command set was copied at 19:40. When they say it is done, Check zoning again.<Mark n={1} />
          </StatusLine>
        )}
        <Section title="2 hosts" summary={back ? 'both zoned on F1 and F2' : 'ESX1 zoned on both · ESX2 zoned on F1, not on F2'} open>
          <DataTable
            columns={[
              { property: 'host', header: 'Host', render: (h) => <Text size="small" weight={600}>{h.host}</Text> },
              { property: 'f1', header: 'Fabric F1', render: (h) => <StatusIndicator state="complete" label={h.f1} /> },
              { property: 'f2', header: 'Fabric F2', render: (h) => <StatusIndicator state={back || h.ok ? 'complete' : 'action_required'} label={back && !h.ok ? 'Zoned · logged in on 0:3:4, 1:3:4' : h.f2} /> },
            ]}
            data={HOSTS}
            primaryKey="host"
          />
        </Section>
        {!back && (
          <Section
            title="Command set for the SAN team"
            summary="F2: 7 lines, Brocade FOS · F1: nothing to add"
            open
            right={
              <Box direction="row" gap="xsmall" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
                <Button size="small" icon={<Copy size="small" />} label="Copy F2" />
                <Button size="small" icon={<Download size="small" />} label="Download both" />
              </Box>
            }
          >
            <Box background="background-contrast" round="xsmall" pad="small" flex={false}>
              {F2_COMMANDS.map((c) => <Text key={c} size="small" style={mono}>{c}</Text>)}
            </Box>
            <Text size="small" color="text-weak">
              After the paste the SAN team runs <Text size="small" style={mono}>cfgenable "lab_F2_cfg"</Text> themselves. The zone names were checked against both switches: none clash.<Mark n={2} />
            </Text>
          </Section>
        )}
        <Section title="What the switches hold" summary="F1: SW3700B_D24U32_F1, cfg lab_F1_cfg, 14 zones · F2: SN3600B_D21U34_F2, cfg lab_F2_cfg, 12 zones">
          <Text size="small" color="text-weak">Read-only, 19:38. Aliases and zones per switch open here as today.</Text>
        </Section>
      </StepPage>
    </AppFrame>
  );
}

export const handoff: Screen = {
  id: 'M8',
  title: 'SAN zoning: the hand-off',
  states: [
    { key: 'waiting', label: 'Handed to the SAN team' },
    { key: 'back', label: 'Next morning: zoned' },
  ],
  notes: [
    'The one moment in the job that depends on another team. The step says so in plain words: who it waits on, what for, since when, and the one thing to do when they report back. The rail and the header show the same grey clock, so from any screen you know this run is parked, not broken.',
    'The command set is the hand-off itself: Copy and Download at the top of the section, the lines in full, and the one command the SAN team runs on their own.',
  ],
  keeps: [
    ['Check zoning on the array', 'Green button while waiting'],
    ['Build zoning plan, the pair picker, the Names panel', 'Opened from the hosts section before the hand-off (not mocked here)'],
    ['Command set with Copy and Download', 'Command set section'],
    ['Continue with the zoned hosts only', 'Footer, left'],
    ['Switch aliases and zones', 'Folded section at the bottom'],
  ],
  render: (state) => <Handoff state={state} />,
};
