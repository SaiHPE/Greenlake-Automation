import { Box, DataTable, Text } from 'grommet';
import { useState } from 'react';
import { StatusIndicator } from '../../src/ui/status';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, Confirmation, Guidance, Mark, Panel, PartsBar, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

// A pair that replicates over Fibre Channel: the lab pair the live run needs (rack13-ARCUS and the Primera
// 630, two RCFC ports each). The WWNs are the ports' own, from the arrays' showport.
const A = 'rack13-ARCUS';
const B = 'PRIMERA630R11U22';
const FC_RUN = { ...RUN, array: A, serial: 'CZ2D2K014S' };
const PARTS = ['Read both arrays', 'Round-trip time', 'Review the plan', 'Configure', 'Verify'];
const PART_OF: Record<string, number> = { 'rtt-missing': 1, 'rtt-over': 1, plan: 2, mixed: 0 };
const A_LINKS = '0:3:3 → 20320002AC02AC38 · 1:3:4 → 21320002AC02AC38';
const B_LINKS = '0:3:2 → 20330002AC02D495 · 1:3:2 → 21340002AC02D495';
const RTT: Record<string, number | null> = { 'rtt-missing': null, 'rtt-over': 12, plan: 4, mixed: null };

function Arrays() {
  return (
    <Box direction="row" gap="medium" wrap flex={false}>
      {[
        ['Array A — this run’s array', A, 'CZ2D2K014S · OS 10.6.0', A_LINKS],
        ['Array B — the peer', B, 'SGH339NK4C · OS 4.6.20', B_LINKS],
      ].map(([label, name, id, links]) => (
        <Box key={name} gap="xsmall" basis="1/2" flex={false}>
          <Text size="small" weight={600}>{label} · {name}</Text>
          <Text size="small" color="text-weak">{id}</Text>
          <StatusIndicator state="complete" label="Remote Copy Started, Normal" />
          <Text size="small" color="text-weak">Fibre Channel: <span style={mono}>{links}</span><Mark n={2} /></Text>
        </Box>
      ))}
    </Box>
  );
}

function ReplicationFc({ state }: { state: string }) {
  const [accept, setAccept] = useState(false);
  const [authorised, setAuthorised] = useState(false);
  const rtt = RTT[state];
  const over = rtt !== null && rtt > 10;
  const mixed = state === 'mixed';

  const blocked = mixed
    ? 'The arrays show targets towards each other over IP and over Fibre Channel. Resolve that on the arrays first.'
    : rtt === null
      ? 'Type the round-trip time between the arrays on the Replication tab: the tool cannot measure Fibre Channel links yet.'
      : over && !accept
        ? `The typed round-trip time is ${rtt} ms, over HPE's limit for async over Fibre Channel. Tick Continue anyway to accept it.`
        : undefined;
  const primary: Action = mixed ? { label: 'Read both arrays again' } : { label: 'Configure replication', blocked };
  const confirmation: Confirmation | undefined = mixed || rtt === null
    ? undefined
    : over && !accept
      ? { label: `Continue anyway: I accept the typed round-trip time of ${rtt} ms for async replication over Fibre Channel.`, checked: accept, onChange: setAccept }
      : { label: `I have reviewed this plan and authorise configuring replication on ${A} and ${B}.`, checked: authorised, onChange: setAuthorised };

  return (
    <AppFrame run={FC_RUN} groups={rail('replicate', 'action_required')} current="replicate">
      <StepPage
        stepLabel={stepLabel('replicate')}
        title="Replication"
        description={`Remote Copy of this run's volume sets to the peer array ${B}.`}
        state="action_required"
        stateLabel={mixed ? '1 finding to resolve' : rtt === null ? 'Round-trip time needed' : 'Awaiting approval'}
        primary={primary}
        actions={[{ label: 'Read both arrays again' }, { label: 'Continue without configuring replication' }].filter((a) => !(mixed && a.label === primary.label))}
        confirmation={confirmation}
        guideOpen={false}
        top={
          <Box direction="row" align="center" flex={false}>
            <PartsBar parts={PARTS} at={PART_OF[state]} doneAll={false} />
          </Box>
        }
        activity={{ last: `10:02:11  Read ${A} and ${B}`, events: 9, commands: 22 }}
        guidance={
          <Guidance
            items={[
              { title: 'What this step does', body: 'One Remote Copy group per volume set on the Replication tab, over the partnership the two arrays already have.' },
              { title: "HPE's latency limits", body: 'Over RCIP: sync 10 ms or less, async 200 ms or less. Over Fibre Channel: 10 ms or less for both.' },
              { title: 'Fibre Channel', body: 'The tool uses a Fibre Channel partnership that exists; it does not set one up. It cannot measure the latency of Fibre Channel links yet, so it uses the round-trip time typed on the Replication tab.' },
            ]}
          />
        }
      >
        {mixed ? (
          <StatusLine state="failed">
            {A} and {B} show Remote Copy targets towards each other over IP and over Fibre Channel: {A} target ‘{B}’ (IP, status ready, 2 of 2
            links Up); {B} target ‘{A}’ (IP, status ready, 2 of 2 links Up); {B} target ‘rack13-ARCUS_PRIMERA’ (Fibre Channel, status failed, 0
            of 2 links Up). The arrays keep one partnership per pair, and a target in one transport stops one in the other from working, so the
            tool will not use either and plans nothing. Remove the failed one first: on {B}, removercopytarget -cleargroups -f
            rack13-ARCUS_PRIMERA (this also removes the groups on that target; their volumes stay). Save showrcopy -d groups before.
            <Mark n={5} />
          </StatusLine>
        ) : rtt === null ? (
          <StatusLine state="action_required">
            Type the round-trip time between the arrays on the Replication tab, then start a new run with the workbook. The tool cannot measure
            Fibre Channel links yet, so it holds the typed time to HPE’s limit instead.<Mark n={3} />
          </StatusLine>
        ) : over && !accept ? (
          <StatusLine state="action_required">
            The round-trip time typed on the Replication tab is {rtt} ms; async replication over Fibre Channel needs 10 ms or less. Replication can
            still be configured: tick Continue anyway to accept the typed time.<Mark n={4} />
          </StatusLine>
        ) : (
          <StatusLine state="action_required">2 to create, 0 already there. No changes have been made to either array. Tick the box next to the green button when you have reviewed it.</StatusLine>
        )}

        <Section title="What the arrays say" summary={mixed ? `No partnership the tool can use between ${A} and ${B}` : `${A} and ${B} partnered over Fibre Channel · 2/2 links up`} open>
          <Text size="small" color="text-weak">Read over SSH with the sheet&apos;s credentials; nothing was changed.</Text>
          <Arrays />
          {!mixed && (
            <Box gap="xxsmall" flex={false}>
              <StatusIndicator state="complete" label={`Partnered over Fibre Channel — ${A} → ${B} 2/2 links Up · ${B} → ${A} 2/2 links Up`} />
              <Text size="xsmall" color="text-weak">
                Target on {A}: “{B}” · target on {B}: “{A}” · policy mirror_config. Over Fibre Channel, found by port WWN; target names are not relied on.<Mark n={1} />
              </Text>
            </Box>
          )}
        </Section>

        {!mixed && (
          <Panel title="Round-trip time">
            <Text size="small">
              The link check measures RCIP links only, so it is not offered for a Fibre Channel pair. The tool uses the round-trip time typed on the
              Replication tab and says so in the result and the as-built document.
            </Text>
            {rtt === null ? (
              <StatusIndicator state="action_required" label="Not typed on the Replication tab" />
            ) : (
              <StatusIndicator
                state={over ? 'action_required' : 'complete'}
                label={`Typed ${rtt} ms · async over Fibre Channel needs 10 ms or less · ${over ? 'over the limit' : 'within the limit'}`}
              />
            )}
          </Panel>
        )}

        {state === 'plan' && (
          <Panel title="Review the plan" right={<Text size="small" color="text-weak">2 to create · 0 already there · 0 conflicts</Text>}>
            <DataTable
              columns={[
                { property: 'kind', header: 'Kind', render: (p) => <Text size="small">{p.kind}</Text> },
                { property: 'name', header: 'Name', render: (p) => <Text size="small" style={mono}>{p.name}</Text> },
                { property: 'on', header: 'On', render: (p) => <Text size="small">{p.on}</Text> },
                { property: 'detail', header: 'Detail', render: (p) => <Text size="small" color="text-weak">{p.detail}</Text> },
              ]}
              data={[
                { kind: 'Remote Copy group', name: 'zz_rc_vvs_rcg', on: 'A', detail: `async, RPO 10 min → ${B}, 1 volume from zz_rc_vvs` },
                { kind: 'Peer volume set', name: 'zz_rc_vvs_rc', on: 'B', detail: 'the secondary volumes on the peer' },
              ]}
              primaryKey="name"
            />
            <Text size="xsmall" color="text-weak">Plan note: Partnership over Fibre Channel: {A} → {B} via target ‘{B}’ (2/2 links Up), {B} → {A} via ‘{A}’ (2/2 Up), policy mirror_config.</Text>
          </Panel>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const replicationFc: Screen = {
  id: 'M6b',
  title: 'Replication over Fibre Channel',
  states: [
    { key: 'rtt-missing', label: '1. No round-trip time typed' },
    { key: 'rtt-over', label: '2. Typed time over the limit' },
    { key: 'plan', label: '3. Within the limit, plan to review' },
    { key: 'mixed', label: 'IP and Fibre Channel targets both' },
  ],
  notes: [
    'The partnership line names the transport: over Fibre Channel, found by port WWN. Target names are still never relied on.',
    'Each array card lists the Fibre Channel links its target uses (port → the other array’s port WWN) instead of “RCIP: no configured ports”.',
    'There is no Check the link over Fibre Channel: the array’s link test is known for RCIP only. The Round-trip time panel says why, and the green button explains what is missing: the time typed on the Replication tab.',
    'Over Fibre Channel the limit is 10 ms for sync and for async. A typed time over it needs the Continue anyway tick, as a measured one does over RCIP; the choice goes into the result and the as-built.',
    'Open with the owner: a typed time is required (built this way). The alternative is a tick to continue without one.',
    'A pair with targets in both transports is blocked with one finding that names every target and its state. A removal command is shown only for a failed target with no link Up and no started group.',
    'As built (2026-11-17): the same parts as over RCIP (M6), with Round-trip time in place of Check the link. The part at hand is the only open panel and the finished parts are one list under it, as on M6; this screen still draws What the arrays say open above the part. The typed-time tick is the first of the two footer ticks.',
  ],
  keeps: [
    ['Check the link / Check again', 'Not offered over Fibre Channel; the Round-trip time panel says why'],
    ['Continue anyway tick', 'Footer, when the typed time is over 10 ms'],
    ['Authorise tick, Configure replication', 'Footer, as over RCIP'],
    ['Partnership line', 'Names the transport and how the partnership was found'],
    ['RCIP ports on the array cards', 'The Fibre Channel links each target uses'],
  ],
  render: (state) => <ReplicationFc state={state} />,
};
