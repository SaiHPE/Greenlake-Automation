import { Box, Button, CheckBox, DataTable, Tab, Tabs, Text, TextInput } from 'grommet';
import { Copy, Download, Terminal, Time } from 'grommet-icons';
import { useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { rail, stepLabel } from '../data';
import { AppFrame, CodeBlock, DoneList, Guidance, Mark, Panel, PartsBar, RunSummary, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// Draft 4 (SPEC-030): the SAN zoning step as one question at a time. Sample data only: no lab or
// customer names, documentation-range addresses.
const RUN: RunSummary = { array: 'DEMO-ARRAY-01', serial: 'DEMO000001', mode: 'Provision, then replicate', state: 'action_required', stateLabel: 'Waiting for you' };
const PARTS = ['Check the array', 'Draft zones', 'Hand off'];
const PART_OF: Record<string, number> = { pick: 1, names: 1, handoff: 2, log: 2 };

const HOSTS = [
  { host: 'esx-demo-01', f1: 'Zoned', f2: 'Zoned', ok: true },
  { host: 'esx-demo-02', f1: 'Zoned', f2: 'Not zoned', ok: false },
];

const PAIRS = [
  { port: '0:3:4', node: 0 },
  { port: '1:3:4', node: 1 },
];

const NAMES = [
  { what: 'HBA port', who: 'esx-demo-02', wwpn: '10:00:00:00:c9:00:00:02', alias: 'esx_demo_02_hba2', check: 'New alias' },
  { what: 'Array port 0:3:4', who: 'node 0', wwpn: '20:34:00:02:ac:00:00:01', alias: 'DEMO000001_N0S3P4', check: 'Existing alias, reused' },
  { what: 'Array port 1:3:4', who: 'node 1', wwpn: '21:34:00:02:ac:00:00:01', alias: 'DEMO000001_N1S3P4', check: 'Existing alias, reused' },
];

const PASTE = [
  'alicreate "esx_demo_02_hba2", "10:00:00:00:c9:00:00:02"',
  'zonecreate "esx_demo_02_hba2_DEMO000001_N0S3P4", "esx_demo_02_hba2; DEMO000001_N0S3P4"',
  'zonecreate "esx_demo_02_hba2_DEMO000001_N1S3P4", "esx_demo_02_hba2; DEMO000001_N1S3P4"',
  'cfgadd "demo_F2_cfg", "esx_demo_02_hba2_DEMO000001_N0S3P4; esx_demo_02_hba2_DEMO000001_N1S3P4"',
];

const LOG = [
  '19:38:02  DEMO-ARRAY-01 (ssh)  showhost -d  0.4s  ok',
  '19:38:05  SAN-DEMO-F1 (fos)  cfgshow  1.1s  ok',
  '19:38:07  SAN-DEMO-F2 (fos)  cfgshow  1.0s  ok',
  '19:38:08  SAN-DEMO-F2 (fos)  nsshow  0.6s  ok',
];

function HostTable() {
  return (
    <DataTable
      columns={[
        { property: 'host', header: 'Host', render: (h) => <Text size="small" weight={500}>{h.host}</Text> },
        { property: 'f1', header: 'Fabric F1', render: () => <StatusIndicator state="complete" label="Zoned" /> },
        { property: 'f2', header: 'Fabric F2', render: (h) => <StatusIndicator state={h.ok ? 'complete' : 'failed'} label={h.f2} /> },
      ]}
      data={HOSTS}
      primaryKey="host"
    />
  );
}

/**
 * The log panel as built (SPEC-030 R11): either bar button opens one panel on its own tab and closes it
 * when pressed again on that tab; the panel is 40% of the window high, 70% after Taller; the footer stays
 * on screen.
 */
function LogBar({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  const [tab, setTab] = useState(1);
  const [tall, setTall] = useState(false);
  const press = (which: number) => () => {
    if (open && tab === which) onToggle();
    else {
      setTab(which);
      if (!open) onToggle();
    }
  };
  const size = <Button size="small" label={tall ? 'Shorter' : 'Taller'} onClick={() => setTall((v) => !v)} />;
  return (
    <Box flex={false} background="background-contrast" border={{ side: 'top', color: 'border-weak' }}>
      <Box direction="row" justify="between" align="center" gap="small" pad={{ horizontal: 'large', vertical: 'xxsmall' }}>
        <Box direction="row" gap="xsmall" align="center">
          <Time size="small" color="icon-weak" aria-hidden />
          <Text size="small" color="text-weak">19:40  Command set generated for fabric F2 (4 lines)</Text>
        </Box>
        <Box direction="row" gap="small" flex={false}>
          <Button size="small" label="Activity (14)" onClick={press(0)} aria-expanded={open && tab === 0} active={open && tab === 0} />
          <Button
            size="small"
            icon={<Terminal size="small" />}
            label="Console (31 commands)"
            onClick={press(1)}
            aria-expanded={open && tab === 1}
            active={open && tab === 1}
          />
        </Box>
      </Box>
      {open && (
        <Box background="background-front" pad={{ horizontal: 'large', bottom: 'small' }} height={{ min: 'small', height: tall ? '70vh' : '40vh' }} overflow="auto">
          <Tabs activeIndex={tab} onActive={setTab} justify="start">
            <Tab title="Activity (14)">
              <Box gap="xsmall" pad={{ top: 'small' }}>
                <Box direction="row" justify="end">{size}</Box>
                <Text size="small">The step's events, newest last.</Text>
              </Box>
            </Tab>
            <Tab title="Commands (31)">
              <Box gap="xsmall" pad={{ top: 'small' }}>
                <Box direction="row" gap="small" justify="end">
                  <Button size="small" icon={<Copy size="small" />} label="Copy" />
                  <Button size="small" icon={<Download size="small" />} label="Download .txt" />
                  <Button size="small" icon={<Terminal size="small" />} label="Open terminal" />
                  {size}
                </Box>
                <CodeBlock lines={LOG} a11yTitle="Commands the tool sent in this run" />
              </Box>
            </Tab>
          </Tabs>
        </Box>
      )}
    </Box>
  );
}

function CalmZoning({ state, setState }: { state: string; setState: (s: string) => void }) {
  const [picked, setPicked] = useState<Record<string, boolean>>(state === 'pick' ? {} : { '0:3:4': true, '1:3:4': true });
  const [logOpen, setLogOpen] = useState(state === 'log');
  const [nothingPicked, setNothingPicked] = useState(false);
  const handedOff = state === 'handoff' || state === 'log';
  const count = Object.values(picked).filter(Boolean).length;
  const at = PART_OF[state] ?? 1;

  // Q3 (2026-11-17): Generate command set stays in the names panel, a default button that is never
  // disabled; with nothing ticked it says why. The footer is the step's own three, as in the app.
  const generate = () => {
    if (!count) {
      setNothingPicked(true);
      return;
    }
    setState('handoff');
  };

  return (
    <AppFrame run={RUN} groups={rail('zoning', handedOff ? 'waiting' : 'action_required')} current="zoning">
      <Box fill>
        <Box flex overflow="hidden">
          <StepPage
            stepLabel={stepLabel('zoning')}
            title="SAN zoning"
            state={handedOff ? 'waiting' : 'action_required'}
            stateLabel={handedOff ? 'Waiting on the SAN team' : 'Action required'}
            top={<PartsBar parts={PARTS} at={at} doneAll={false} />}
            actions={[{ label: 'Check zoning again' }, { label: 'Rebuild plan' }]}
            primary={{ label: 'Continue with esx-demo-01' }}
            guideOpen={false}
            guidance={
              <Guidance
                items={[
                  { title: 'What this step answers', body: 'Which hosts can reach the array through the fabrics, and which zones your SAN team still has to add. The tool never writes to a switch.' },
                  { title: 'How zoning is checked', body: "From the array's logins: a host adapter logs in to an array port only through a zone that is in effect." },
                ]}
              />
            }
          >
            {!handedOff && (
              <StatusLine state="action_required" time="19:38">
                esx-demo-02 is not zoned on fabric F2. Tick the pairs your SAN design wants; esx-demo-01 can go ahead now.<Mark n={1} />
              </StatusLine>
            )}
            {handedOff && (
              <StatusLine state="waiting" time="since 19:40" links={[{ label: 'See the commands', onClick: () => setLogOpen(true) }]}>
                Waiting on the SAN team: 2 zones for esx-demo-02 on fabric F2. When they say it is applied, check zoning again.<Mark n={1} />
              </StatusLine>
            )}

            <DoneList
              items={[
                // the check's "again" is in the footer, so the row has none (an action is drawn in one place)
                { text: 'Checked the array at 19:38: 2 hosts the array can reach, 1 of 2 can be provisioned', detail: <HostTable /> },
                ...(handedOff
                  ? [{
                      text: `Drafted ${count} new zones for the SAN team`,
                      again: 'Change',
                      detail: (
                        <Box gap="xxsmall">
                          <Text size="small">Fabric F2 (even): esx-demo-02 HBA 2 with 0:3:4 and 1:3:4</Text>
                          <Text size="small">1 new alias, esx_demo_02_hba2; 2 reused from the switch</Text>
                        </Box>
                      ),
                    }]
                  : []),
              ]}
            />

            {!handedOff && (
              <Panel title={<>Pick the pairs for fabric F2<Mark n={2} /></>}>
                <Text size="small" color="text-weak">Nothing is ticked for you. HPE's rule: at least one port on each controller node per fabric.</Text>
                <Box direction="row" gap="small" align="baseline">
                  <Text size="small" weight={500}>esx-demo-02</Text>
                  <Text size="small" style={mono}>10:00:00:00:c9:00:00:02</Text>
                </Box>
                <Box direction="row" gap="large">
                  {PAIRS.map((p) => (
                    <CheckBox
                      key={p.port}
                      label={<Text size="small">{p.port} (node {p.node})</Text>}
                      checked={!!picked[p.port]}
                      onChange={(e) => {
                        setPicked((m) => ({ ...m, [p.port]: e.target.checked }));
                        setNothingPicked(false);
                        if (state === 'pick' && e.target.checked) setState('names');
                      }}
                    />
                  ))}
                </Box>
              </Panel>
            )}

            {!handedOff && (
              <Panel title="Name the aliases">
                {count === 0 && <Text size="small" color="text-weak">Tick a pair above. Only the WWPNs that take part in a new zone need a name.</Text>}
                {count > 0 &&
                  NAMES.map((n) => (
                    <Box key={n.wwpn} direction="row" gap="small" align="center" wrap>
                      <Box basis="small" flex={false}><Text size="small">{n.what} · {n.who}</Text></Box>
                      <Box basis="small" flex={false}><Text size="small" style={mono}>{n.wwpn}</Text></Box>
                      <Box basis="medium" flex="shrink"><TextInput size="small" defaultValue={n.alias} aria-label={`Alias for ${n.wwpn}`} /></Box>
                      <StatusIndicator state="complete" label={n.check} />
                    </Box>
                  ))}
                <Box direction="row" gap="small" align="center" wrap>
                  <Button label={`Generate command set (${count} new zone${count === 1 ? '' : 's'})`} onClick={generate} />
                  {nothingPicked && <Text size="small" color="status-critical">Tick at least one pair above first.</Text>}
                </Box>
              </Panel>
            )}

            {handedOff && (
              <Panel
                title={<>Command set for the SAN team · fabric F2<Mark n={3} /></>}
                right={
                  <Box direction="row" gap="xsmall">
                    <Button size="small" icon={<Copy size="small" />} label="Copy paste block" />
                    <Button size="small" icon={<Download size="small" />} label="Download .txt" />
                  </Box>
                }
              >
                <Text size="small" weight={500}>1. Check, run alone first</Text>
                <CodeBlock lines={['cfgtransshow']} a11yTitle="Check command" />
                <Text size="small" weight={500}>2. Paste block, additive only</Text>
                <CodeBlock lines={PASTE} a11yTitle="Paste block for fabric F2" />
                <Box border={{ color: 'status-warning', side: 'left', size: 'medium' }} pad={{ left: 'small' }} gap="xxsmall">
                  <Text size="small" weight={500}>3. Save and activate: the SAN team, in a window</Text>
                  <Text size="small" style={mono}>cfgsave</Text>
                  <Text size="small" style={mono}>cfgenable "demo_F2_cfg"</Text>
                </Box>
                <Text size="small" color="text-weak">Fabric F1: nothing to add.</Text>
              </Panel>
            )}

            <Section title="What the switches hold" summary="F1: SAN-DEMO-F1, 14 zones · F2: SAN-DEMO-F2, 12 zones">
              <Text size="small" color="text-weak">Fabrics, current zoning per HBA port and Export .txt, as today.</Text>
            </Section>
          </StepPage>
        </Box>
        <LogBar open={logOpen} onToggle={() => setLogOpen((v) => !v)} />
      </Box>
    </AppFrame>
  );
}

export const calmZoning: Screen = {
  id: 'M16',
  title: 'Draft 4: SAN zoning, one question at a time',
  states: [
    { key: 'pick', label: 'Plan read: pick the pairs' },
    { key: 'names', label: 'Pairs picked: name the aliases' },
    { key: 'handoff', label: 'Command set handed off' },
    { key: 'log', label: 'Handed off, log open' },
  ],
  notes: [
    'One status line, one question. The words change with the part: draft (pick and name), hand off. Counts live here, not in the header (the header shows only the state).',
    'Q3 (2026-11-17): Generate command set stays in the names panel as a default button, never disabled; with nothing ticked, or a name the switch would refuse, it says why on click and sends nothing. The footer is the step\'s own: Check zoning again, Rebuild plan, and Continue with the zoned hosts as the primary.',
    'The current part is the only open panel. Finished parts are one line each in a list, with Show detail and their own "again" button, so the footer keeps at most three buttons.',
    'The command set keeps its three blocks; the activation block stays apart and marked, as the SAN team runs it in a window. Copy and Download sit on the panel header.',
    'The log is one panel with two tabs: Activity (14) opens it on Activity, Console (31 commands) on Commands, and pressed again on its own tab either closes it. It is 40% of the window high, 70% after Taller (Shorter puts it back, for the browser session); the footer stays on screen. The status line link "See the commands" opens it on Commands; it never opens by itself.',
    'As built (2026-11-17), as drawn here: the finished parts list sits above the part at hand on this step (Provision storage and Snapshots do the same); Replication puts it under (M6).',
  ],
  keeps: [
    ['Build zoning plan / Rebuild plan', 'Footer, as today'],
    ['Check zoning on the array / again', 'Footer, as today (so the Check row has no "again")'],
    ['Generate command set (green, in the page)', 'Names panel, a default button, never disabled (Q3)'],
    ['Pairs, names and the command set, all open at once', 'Pairs and names while drafting; once generated, one "Drafted" row (Change) and the command set'],
    ['Fabrics and Current zoning panels', 'Folded section "What the switches hold"'],
    ['Continue with N zoned hosts', 'Footer primary once a host is zoned, as today'],
    ['Activity and Console buttons', 'Same names, same bar; they open one panel with two tabs'],
  ],
  render: (state, setState) => <CalmZoning state={state} setState={setState} />,
};
