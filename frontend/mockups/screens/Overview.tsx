import { Anchor, Box, Button, Grid, Heading, Text } from 'grommet';
import { Document, Download, Terminal } from 'grommet-icons';
import { StepState } from '../../src/ui/status';
import { RESULTS, RUN, STEPS, rail } from '../data';
import { AppFrame, DocList, Mark, PlainPage, StatusLine, StepIcon } from '../kit';
import { Screen } from '../screen';

const STATE_AT_ZONING: Record<string, StepState> = { prereq: 'complete', sheet: 'complete', mode: 'complete', discover: 'complete', zoning: 'action_required' };
const WHEN: Record<string, string> = { discover: '19:22 · 21 s', zoning: 'since 19:23' };

function Overview() {
  const steps = STEPS.filter((s) => !['prereq', 'sheet', 'mode', 'finish'].includes(s.key));
  const begun = steps.filter((s) => STATE_AT_ZONING[s.key]);
  const todo = steps.filter((s) => !STATE_AT_ZONING[s.key]);
  return (
    <AppFrame run={RUN} groups={rail('zoning')} current="overview">
      <PlainPage
        title="AlletraMP_D22U27"
        subtitle="Provision, then replicate · started 13 Oct 2026, 19:22 · 7 steps"
        parent={{ label: 'Your runs' }}
        actions={<Button primary label="Continue at SAN zoning" />}
      >
        <StatusLine state="action_required">
          Waiting for you at SAN zoning: ESX2 is not zoned on fabric F2. Send the command set to your SAN team, then check again.
          <Mark n={1} />
        </StatusLine>
        <Grid columns={{ count: 'fit', size: 'small' }} gap="small" as="ul" style={{ margin: 0, padding: 0 }}>
          {begun.map((s) => {
            const state = STATE_AT_ZONING[s.key];
            const here = s.key === 'zoning';
            return (
              <Box
                as="li"
                key={s.key}
                background="background-front"
                round="small"
                border={{ color: here ? 'border-selected' : 'border-weak', size: here ? 'medium' : 'xsmall' }}
                pad="medium"
                gap="xsmall"
                style={{ listStyle: 'none' }}
              >
                <Box direction="row" justify="between" align="center" gap="small">
                  <Box direction="row" gap="small" align="center">
                    <StepIcon state={state} />
                    <Heading level={2} size="xsmall" weight={500} margin="none">{s.label}</Heading>
                  </Box>
                  <Text size="xsmall" color="text-weak" textAlign="end">{WHEN[s.key]}</Text>
                </Box>
                <Text size="small" color={here ? 'text-strong' : 'text-weak'}>
                  {state === 'complete' ? RESULTS[s.key] : '1 of 2 hosts zoned on both fabrics'}
                </Text>
                <Anchor size="small" label={here ? 'Open the current step' : `Open ${s.label}`} href="#" />
              </Box>
            );
          })}
        </Grid>
        <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad={{ horizontal: 'medium', vertical: 'small' }} flex={false} gap="xxsmall">
          <Heading level={2} size="xsmall" weight={500} margin="none">Still to do<Mark n={3} /></Heading>
          <Text size="small" color="text-weak">{todo.map((s) => s.label).join('  →  ')}</Text>
        </Box>
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Documents and logs<Mark n={2} /></Heading>
          <DocList
            items={[
              { icon: <Terminal />, name: 'Command log', detail: '64 commands so far · grows as the run goes on' },
              { icon: <Download />, name: 'Zoning command set', detail: 'F2: 7 lines · F1: nothing to add · handed to the SAN team 19:40' },
              { icon: <Document />, name: 'As-built document', detail: 'Generated at the As-built step', pending: 'Not yet' },
            ]}
          />
        </Box>
      </PlainPage>
    </AppFrame>
  );
}

export const overview: Screen = {
  id: 'M4',
  title: 'Run overview (new page)',
  notes: [
    'A new page. The steps that have run or are running, each with its result, when it ran and how long it took. You open any of them from here. Nothing in the steps changes.',
    'The files a run produces in one place: the command log, the zoning command set, the as-built document.',
    'Steps not started yet are one line, not five empty cards. The green button, top right in the page header as the Design System places page actions, takes you to the current step. "Your runs" above the title is the way back.',
  ],
  keeps: [
    ['Nothing removed', 'This page is added; each card opens the step as it is'],
  ],
  render: () => <Overview />,
};
