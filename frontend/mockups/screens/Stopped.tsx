import { Box, Button, Text } from 'grommet';
import { Copy } from 'grommet-icons';
import { StatusIndicator } from '../../src/ui/status';
import { COMMANDS, RUN, rail, stepLabel } from '../data';
import { AppFrame, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// The real 2026-10-09 event: write 4 of 12 refused with HTTP 400 code 44.
const DONE = COMMANDS.slice(0, 3);
const FAILED = COMMANDS[3];
const REMOVE_A = ['removercopygroup -f zz_rc_test_rcg', 'removevvset -f zz_rc_test', 'removevv -f zz_rc_test_v01'];

function Stopped() {
  return (
    <AppFrame run={{ ...RUN, state: 'failed', stateLabel: 'Stopped' }} groups={rail('replicate', 'failed')} current="replicate">
      <StepPage
        stepLabel={stepLabel('replicate')}
        title="Replication"
        description="Remote Copy of this run's volume sets to the peer array AlletraMP_E18U31."
        state="failed"
        stateLabel="Stopped at write 4 of 12"
        secondary={[{ label: 'Copy the removal commands' }, { label: 'Continue without replication' }]}
        primary={{ label: 'Read both arrays again' }}
        guideOpen={false}
        activity={{ last: '19:32:40  Write 4 refused by AlletraMP_D22U27 (HTTP 400, code 44)', events: 19, commands: 41 }}
        guidance={
          <Guidance
            items={[
              { title: 'Why it stops', body: 'The apply stops at the first write the array refuses. Nothing after it is attempted, so the array is never half-configured without you knowing exactly where it stands.' },
              { title: 'Undo', body: 'The removal commands undo only what this run created, in the right order. Paste them on the array yourself; the tool never deletes.' },
              { title: 'Try again', body: 'Read both arrays again to build a new plan. Objects already created show as Exists and are not created twice.' },
            ]}
          />
        }
      >
        <StatusLine state="failed" time="19:32">
          Configuring replication stopped at write 4 of 12. AlletraMP_D22U27 refused the policies for zz_rc_test_rcg: HTTP 400, code 44, "period and policies cannot be set in one call".<Mark n={1} />
        </StatusLine>
        <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad="medium" gap="small" flex={false}>
          <Text weight={600}>What to do<Mark n={2} /></Text>
          <Text size="small">1. This is a fault in the tool, not in your arrays: it sent the period and the policies together. It is fixed in v0.17.1. Update the app, then Read both arrays again and configure; the 3 objects already created are reused.</Text>
          <Text size="small">2. Or undo the 3 writes with the removal commands below and continue without replication.</Text>
        </Box>
        <Section title="What was done before the stop" summary="3 of 12 writes, all on AlletraMP_D22U27" open>
          {DONE.map((c) => (
            <Box key={c} direction="row" gap="small" align="center">
              <StatusIndicator state="complete" label="Done" />
              <Text size="small" style={mono}>{c}</Text>
            </Box>
          ))}
          <Box direction="row" gap="small" align="center">
            <StatusIndicator state="failed" label="Refused" />
            <Text size="small" style={mono}>{FAILED}</Text>
          </Box>
          <Text size="small" color="text-weak">8 writes not attempted.</Text>
        </Section>
        <Section
          title="To undo what was done"
          summary="3 commands on AlletraMP_D22U27, nothing on the peer"
          right={<Button size="small" icon={<Copy size="small" />} label="Copy" onClick={(e: React.MouseEvent) => e.stopPropagation()} />}
        >
          <Box background="background-contrast" round="xsmall" pad="small" flex={false}>
            {REMOVE_A.map((c) => <Text key={c} size="small" style={mono}>{c}</Text>)}
          </Box>
        </Section>
        <Section title="The array's full answer" summary="HTTP 400 · code 44 · 19:32:40">
          <Text size="small" style={mono}>{'{"code": 44, "desc": "invalid input: parameters cannot be present at the same time - policies, syncPeriod"}'}</Text>
          <Text size="small" color="text-weak">Also in the Console, bottom right, with every other command of this run.</Text>
        </Section>
      </StepPage>
    </AppFrame>
  );
}

export const stopped: Screen = {
  id: 'M9',
  title: 'A step that stopped (the failure template)',
  notes: [
    'Every failure reads the same way: what stopped, where, and what the device said, in one sentence. Red, because it needs you.',
    'Then what to do, as numbered options, before any table. Today the failure text is in a red box and the way out is scattered across the page and the activity list.',
  ],
  keeps: [
    ['Result table with Done / Failed per write', 'What was done before the stop'],
    ['Removal sets with Copy', 'To undo what was done'],
    ['Read both arrays again', 'Footer, right (green)'],
    ['Continue without configuring replication', 'Footer, left'],
  ],
  render: () => <Stopped />,
};
