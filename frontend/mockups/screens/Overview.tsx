import { Anchor, Box, Button, Grid, Heading, Text } from 'grommet';
import { Document, Download, Terminal } from 'grommet-icons';
import { StepState } from '../../src/ui/status';
import { RESULTS, RUN, STEPS, rail } from '../data';
import { AppFrame, Mark, StatusLine, StepIcon } from '../kit';
import { Screen } from '../screen';

const STATE_AT_ZONING: Record<string, StepState> = { prereq: 'complete', sheet: 'complete', mode: 'complete', discover: 'complete', zoning: 'action_required' };

function Overview() {
  const steps = STEPS.filter((s) => !['prereq', 'sheet', 'mode', 'finish'].includes(s.key));
  return (
    <AppFrame run={RUN} groups={rail('zoning')} current="overview">
      <Box fill overflow="auto">
        <Box pad={{ horizontal: 'large', vertical: 'medium' }} gap="medium" flex={false}>
          <Box>
            <Text size="small" color="text-weak">Run started 13/10/2026 19:22 · Provision, then replicate</Text>
            <Heading level={1} size="small" margin="none">AlletraMP_D22U27</Heading>
          </Box>
          <StatusLine state="action_required">
            Waiting for you at SAN zoning: ESX2 is not zoned on fabric F2. Send the command set to your SAN team, then check again.
            <Mark n={1} />
          </StatusLine>
          <Grid columns={['flex', 'flex', 'flex']} gap="small">
            {steps.map((s) => {
              const state: StepState = STATE_AT_ZONING[s.key] ?? 'not_started';
              const here = s.key === 'zoning';
              return (
                <Box
                  key={s.key}
                  background="background-front"
                  round="small"
                  border={{ color: here ? 'border-selected' : 'border-weak', size: here ? 'medium' : 'xsmall' }}
                  pad="medium"
                  gap="xsmall"
                >
                  <Box direction="row" justify="between" align="center">
                    <Box direction="row" gap="small" align="center">
                      <StepIcon state={state} />
                      <Text weight={600}>{s.label}</Text>
                    </Box>
                    {here && <Text size="xsmall" weight="bold" color="text-strong">YOU ARE HERE</Text>}
                  </Box>
                  <Text size="small" color="text-weak">
                    {state === 'complete' ? RESULTS[s.key] : here ? '1 of 2 hosts zoned on both fabrics' : 'Not started'}
                  </Text>
                  <Anchor size="small" label={state === 'not_started' ? 'Preview this step' : 'Open'} href="#" />
                </Box>
              );
            })}
          </Grid>
          <Box gap="small" flex={false}>
            <Heading level={2} size="small" margin="none">Documents and logs<Mark n={2} /></Heading>
            <Box direction="row" gap="small" wrap>
              <Button secondary icon={<Terminal />} label="Command log · 64 commands" />
              <Button secondary icon={<Download />} label="Zoning command set (F1, F2)" />
              <Button secondary icon={<Document />} label="As-built document" disabled />
            </Box>
          </Box>
        </Box>
      </Box>
    </AppFrame>
  );
}

export const overview: Screen = {
  id: 'M4',
  title: 'Run overview (new page)',
  notes: [
    'A new page. Every step of the run on one screen: its status, its result and where you are. You open any step from here. Nothing in the steps changes.',
    'The files a run produces in one place: the command log, the zoning command set, the as-built document.',
  ],
  keeps: [
    ['Nothing removed', 'This page is added; each card opens the step as it is'],
  ],
  render: () => <Overview />,
};
