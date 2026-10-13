import { Anchor, Box, Button, Grid, Heading, Text } from 'grommet';
import { Document, Download, Terminal } from 'grommet-icons';
import { StepState } from '../../src/ui/status';
import { RESULTS, RUN, STEPS, rail } from '../data';
import { AppFrame, DocList, Mark, StatusLine, StepIcon } from '../kit';
import { Screen } from '../screen';

const STATE_AT_ZONING: Record<string, StepState> = { prereq: 'complete', sheet: 'complete', mode: 'complete', discover: 'complete', zoning: 'action_required' };
const WHEN: Record<string, string> = { discover: '19:22 · 21 s', zoning: 'since 19:23' };

function Overview() {
  const steps = STEPS.filter((s) => !['prereq', 'sheet', 'mode', 'finish'].includes(s.key));
  const begun = steps.filter((s) => STATE_AT_ZONING[s.key]);
  const todo = steps.filter((s) => !STATE_AT_ZONING[s.key]);
  return (
    <AppFrame run={RUN} groups={rail('zoning')} current="overview">
      <Box fill>
        <Box flex overflow="auto">
          <Box pad={{ horizontal: 'large', vertical: 'medium' }} flex={false} gap="medium">
            <Box>
              <Text size="small" color="text-weak">Run started 13/10/2026 19:22 · Provision, then replicate · 7 steps</Text>
              <Heading level={1} size="small" margin="none">AlletraMP_D22U27</Heading>
            </Box>
            <StatusLine state="action_required">
              Waiting for you at SAN zoning: ESX2 is not zoned on fabric F2. Send the command set to your SAN team, then check again.
              <Mark n={1} />
            </StatusLine>
            <Grid columns={['flex', 'flex', 'flex']} gap="small">
              {begun.map((s) => {
                const state = STATE_AT_ZONING[s.key];
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
                      <Text size="xsmall" color="text-weak">{WHEN[s.key]}</Text>
                    </Box>
                    <Text size="small" color={here ? 'text-strong' : 'text-weak'}>
                      {state === 'complete' ? RESULTS[s.key] : '1 of 2 hosts zoned on both fabrics'}
                    </Text>
                    <Anchor size="small" label={here ? 'Open the current step' : 'Open'} href="#" />
                  </Box>
                );
              })}
            </Grid>
            <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad={{ horizontal: 'medium', vertical: 'small' }} flex={false}>
              <Text size="small" color="text-strong" weight={600}>Still to do<Mark n={3} /></Text>
              <Text size="small" color="text-weak">{todo.map((s) => s.label).join('  →  ')}</Text>
            </Box>
            <Box gap="small" flex={false}>
              <Heading level={2} size="small" margin="none">Documents and logs<Mark n={2} /></Heading>
              <DocList
                items={[
                  { icon: <Terminal />, name: 'Command log', detail: '64 commands so far · grows as the run goes on' },
                  { icon: <Download />, name: 'Zoning command set', detail: 'F2: 7 lines · F1: nothing to add · handed to the SAN team 19:40' },
                  { icon: <Document />, name: 'As-built document', detail: 'Generated at the As-built step', disabled: true, action: 'Not yet' },
                ]}
              />
            </Box>
          </Box>
        </Box>
        <Box direction="row" justify="end" pad={{ horizontal: 'large', vertical: 'small' }} background="background-front" border={{ side: 'top', color: 'border-weak' }} flex={false}>
          <Button primary label="Continue at SAN zoning" />
        </Box>
      </Box>
    </AppFrame>
  );
}

export const overview: Screen = {
  id: 'M4',
  title: 'Run overview (new page)',
  notes: [
    'A new page. The steps that have run or are running, each with its result, when it ran and how long it took. You open any of them from here. Nothing in the steps changes.',
    'The files a run produces in one place: the command log, the zoning command set, the as-built document.',
    'Steps not started yet are one line, not five empty cards. The green button takes you to the current step.',
  ],
  keeps: [
    ['Nothing removed', 'This page is added; each card opens the step as it is'],
  ],
  render: () => <Overview />,
};
