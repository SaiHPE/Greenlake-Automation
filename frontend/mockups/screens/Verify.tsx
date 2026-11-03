import { Box, Button, DataTable, Text } from 'grommet';
import { Validate } from 'grommet-icons';
import { StatusIndicator, StepState } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, EmptyState, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

type Check = { field: string; expected: string; actual: string; status: 'pass' | 'mismatch' | 'not_readable'; note?: string };
const CHECK_STATE: Record<Check['status'], { state: StepState; label: string }> = {
  pass: { state: 'complete', label: 'Match' },
  mismatch: { state: 'action_required', label: 'Mismatch' },
  not_readable: { state: 'not_started', label: 'Not readable' },
};

const CHECKS: Check[] = [
  { field: 'System name', expected: 'AlletraMP_D22U27', actual: 'AlletraMP_D22U27', status: 'pass' },
  { field: 'Management IP', expected: '10.64.122.99', actual: '10.64.122.99', status: 'pass' },
  { field: 'Netmask', expected: '255.255.255.0', actual: '255.255.255.0', status: 'pass' },
  { field: 'Gateway', expected: '10.64.122.1', actual: '10.64.122.1', status: 'pass' },
  { field: 'DNS servers', expected: '10.64.1.5; 10.64.1.6', actual: '10.64.1.5, 10.64.1.6', status: 'pass', note: 'every expected value present' },
  { field: 'NTP server', expected: '10.64.1.10', actual: '10.64.1.10', status: 'pass' },
  { field: 'Time zone', expected: 'Asia/Tokyo', actual: 'Asia/Tokyo', status: 'pass' },
  { field: 'DSCC region', expected: 'jp1', actual: 'jp1', status: 'pass' },
  { field: 'Volume zz_rc_vol01', expected: '10 GiB on SSD_r6', actual: '10 GiB on SSD_r6', status: 'pass' },
  { field: 'Host set zz_rc_hs', expected: 'ESX1', actual: 'ESX1', status: 'pass' },
  { field: 'Export zz_rc_vvs → zz_rc_hs', expected: 'LUN 1', actual: 'LUN 1', status: 'pass' },
  { field: 'Remote Copy target', expected: 'AlletraMP_E18U31', actual: 'AlletraMP_E18U31', status: 'pass' },
];
const MISMATCH: Check[] = CHECKS.map((c) =>
  c.field === 'NTP server' ? { ...c, actual: '10.64.1.11', status: 'mismatch' as const }
    : c.field === 'Time zone' ? { ...c, actual: '', status: 'not_readable' as const } : c);

const ISSUES = [
  { component: 'Port', summary: 'Port 0:3:2 link down', qty: 1, details: [{ id: '0:3:2', text: 'FC port has no link', fix: 'Check the cable and the switch port, or mark the port offline if it is unused.' }], change: 'new since the last check' },
];

function Verify({ state, setState }: { state: string; setState: (s: string) => void }) {
  const done = state !== 'before';
  const mismatch = state === 'mismatch';
  const checks = mismatch ? MISMATCH : CHECKS;
  const matches = checks.filter((c) => c.status === 'pass').length;
  const review = checks.length - matches;
  const primary: Action = done ? { label: 'Continue to As-built document' } : { label: 'Verify configuration', onClick: () => setState('match') };
  const actions: Action[] = done ? [{ label: 'Verify again', onClick: () => setState('match') }] : [];
  return (
    <AppFrame run={RUN} groups={rail('verify', done ? 'complete' : 'not_started')} current="verify">
      <StepPage
        stepLabel={stepLabel('verify')}
        title="Verify configuration"
        description="Reads the array over SSH and compares what runs with what the workbook says. Changes nothing."
        state={done ? (mismatch ? 'action_required' : 'complete') : 'not_started'}
        stateLabel={done ? (mismatch ? `${review} to review` : 'Configuration matches') : 'Not verified'}
        primary={primary}
        actions={actions}
        guideOpen={!done}
        activity={{ last: done ? `19:53:20  Verified: ${matches} of ${checks.length} match` : '19:51:41  Failover test passed', events: done ? 36 : 31, commands: done ? 71 : 58 }}
        guidance={
          <Guidance
            items={[
              { title: 'What is compared', body: 'Every setting the workbook gives: network, time, DSCC region, and the objects this run created. The array status check is read too.' },
              { title: 'A mismatch does not fail the run', body: 'It is reported for you to decide. "Not readable" means the array did not report that value; check it by hand if it matters.' },
              { title: 'Credentials', body: 'The array credential comes from the sheet and is held by this run only. Use a different one for this step if you need to.' },
            ]}
          />
        }
      >
        <Section title="Array credentials" summary="From the sheet: 3paradm @ 10.64.122.99 · held by this run only" level={2}>
          <Text size="small" color="text-weak">Typed once, on the sheet. A different credential here is used for this step only and is not stored.</Text>
          <Box direction="row"><Button size="small" label="Use a different credential" /></Box>
        </Section>

        {!done && (
          <EmptyState icon={<Validate size="large" color="icon-weak" />} title={<>Not verified yet<Mark n={1} /></>}>
            Verify configuration reads 12 settings from the array and the array's own status check. It takes about 20 seconds and writes nothing.
          </EmptyState>
        )}

        {done && (
          <Box gap="medium" flex={false}>
            {mismatch ? (
              <StatusLine state="action_required" time="19:53">
                {matches} of {checks.length} settings match. NTP server differs (10.64.1.11 on the array, 10.64.1.10 on the sheet). Time zone could not be read. 1 array status issue, new since the last check.<Mark n={1} />
              </StatusLine>
            ) : (
              <StatusLine state="complete" time="19:53">All {checks.length} settings match the workbook. The array reports no status issues.<Mark n={1} /></StatusLine>
            )}
            <Section title={`Configuration: ${checks.length} settings`} summary={`${matches} match · ${review} to review`} open={mismatch}>
              <DataTable
                columns={[
                  { property: 'field', header: 'Setting', render: (c: Check) => <Text size="small">{c.field}</Text> },
                  { property: 'expected', header: 'On the sheet', render: (c: Check) => <Text size="small" style={mono}>{c.expected}</Text> },
                  { property: 'actual', header: 'On the array', render: (c: Check) => <Text size="small" style={mono}>{c.actual || '--'}</Text> },
                  {
                    property: 'status',
                    header: 'Result',
                    render: (c: Check) => (
                      <Box gap="xxsmall">
                        <StatusIndicator state={CHECK_STATE[c.status].state} label={CHECK_STATE[c.status].label} />
                        {c.note && <Text size="xsmall" color="text-weak">{c.note}</Text>}
                      </Box>
                    ),
                  },
                ]}
                data={checks}
                primaryKey="field"
              />
            </Section>
            <Section title="Array status" summary={mismatch ? '1 issue · compared with the check at 19:22' : 'No issues reported · compared with the check at 19:22'} open={mismatch}>
              {mismatch ? (
                <Box gap="small" flex={false}>
                  <DataTable
                    columns={[
                      { property: 'component', header: 'Component', render: (i) => <Text size="small">{i.component}</Text> },
                      { property: 'summary', header: 'Summary', render: (i) => <Box direction="row" gap="small" align="center" wrap><Text size="small">{i.summary}</Text><StatusIndicator state="action_required" label={i.change} /></Box> },
                      { property: 'qty', header: 'Count', align: 'end', render: (i) => <Text size="small" textAlign="end">{i.qty}</Text> },
                    ]}
                    data={ISSUES}
                    primaryKey="summary"
                  />
                  {ISSUES[0].details.map((d) => (
                    <Box key={d.id} direction="row" gap="small" wrap pad={{ left: 'small' }}>
                      <Text size="small" style={mono}>{d.id}</Text>
                      <Text size="small">{d.text}</Text>
                      <Text size="small" color="text-weak">Resolution: {d.fix}</Text>
                    </Box>
                  ))}
                  <Text size="xsmall" color="text-weak">Each component here needs attention outside this tool. The identifiers and the resolution are the array's own words.<Mark n={2} /></Text>
                </Box>
              ) : (
                <StatusIndicator state="complete" label="No issues reported by the array's status check." />
              )}
            </Section>
          </Box>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const verify: Screen = {
  id: 'M13',
  title: 'Verify configuration',
  states: [
    { key: 'before', label: 'Not verified' },
    { key: 'match', label: 'Everything matches' },
    { key: 'mismatch', label: '2 to review, 1 status issue' },
  ],
  notes: [
    'One line with the verdict: all match, or exactly which settings differ and whether the array reports an issue. The two tables fold; the one with something to review opens by itself.',
    'The array status table says what changed since the last check (new, cleared) and shows the array\'s own identifiers and resolution text, not ours.',
  ],
  keeps: [
    ['Array credentials card (sheet credential, Use a different credential)', 'Folded section at the top'],
    ['Verify configuration / Re-verify', 'Footer, right (green); then Verify again beside Continue'],
    ['Configuration table (setting, expected, on the array, result, match note)', 'Configuration section'],
    ['Array status table with Show detail rows, new since / cleared', 'Array status section'],
    ['"Not readable" footnote', 'Right panel and the result column'],
    ['Continue', 'Footer, right (green) once verified'],
  ],
  render: (state, setState) => <Verify state={state} setState={setState} />,
};
