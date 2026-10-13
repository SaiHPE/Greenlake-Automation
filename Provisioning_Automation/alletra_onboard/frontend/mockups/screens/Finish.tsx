import { Box, Button, DataTable, Heading, Text } from 'grommet';
import { Archive, Document, Terminal } from 'grommet-icons';
import { StatusIndicator } from '../../src/ui/status';
import { RUN, rail } from '../data';
import { AppFrame, DocList, Guidance, Mark, Section, StatusLine, StepPage, mono } from '../kit';
import { Screen } from '../screen';

const CREATED = [
  { kind: 'Volume', name: 'zz_rc_vol01', detail: '10 GiB on SSD_r6' },
  { kind: 'Volume set', name: 'zz_rc_vvs', detail: 'holds zz_rc_vol01' },
  { kind: 'Host set', name: 'zz_rc_hs', detail: 'ESX1' },
  { kind: 'Export', name: 'zz_rc_vvs → zz_rc_hs', detail: 'LUN 1, 4 paths' },
  { kind: 'Remote Copy group', name: 'zz_rc_vvs_rcg', detail: 'sync → AlletraMP_E18U31, replicating' },
  { kind: 'Remote Copy group', name: 'zz_rc_test_rcg', detail: 'the failover test group, replicating' },
];

function Finish() {
  return (
    <AppFrame run={{ ...RUN, state: 'complete', stateLabel: 'Done' }} groups={rail('finish', 'complete')} current="finish">
      <StepPage
        title="Done"
        description="AlletraMP_D22U27 · Provision, then replicate · started 19:22, finished 20:05."
        state="complete"
        stateLabel="Run complete"
        secondary={[{ label: 'Start another run on this array' }]}
        primary={{ label: 'Back to your runs' }}
        done
        guideOpen={false}
        activity={{ last: '20:05:11  As-built generated (764 KB)', events: 48, commands: 112 }}
        guidance={
          <Guidance
            items={[
              { title: 'What to hand over', body: 'The as-built document is for the customer. The command log is the evidence of every command this run sent. The removal commands are for you, in case this work has to be undone.' },
              { title: 'The run stays', body: 'It stays in your runs with its documents. Nothing is deleted.' },
            ]}
          />
        }
      >
        <StatusLine state="complete" time="20:05">
          Everything this run set out to do is done: storage provisioned for ESX1, replication to AlletraMP_E18U31 running, failover test passed, configuration verified.<Mark n={1} />
        </StatusLine>
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Hand-over package<Mark n={2} /></Heading>
          <DocList
            head={<Button size="small" icon={<Archive size="small" />} label="Download everything as one zip" />}
            items={[
              { icon: <Document />, name: 'As-built document', detail: 'AlletraMP_D22U27_as-built_2026-10-13.docx · 764 KB · for the customer' },
              { icon: <Terminal />, name: 'Command log', detail: 'commands-e689758b.txt · 112 commands on 2 arrays · the evidence' },
              { icon: <Archive />, name: 'Removal commands', detail: 'A then B, 9 lines · for you, if this work has to be undone' },
            ]}
          />
        </Box>
        <Section title="Created by this run" summary="6 objects on 2 arrays" open>
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (r) => <Text size="small" color="text-weak">{r.kind}</Text> },
              { property: 'name', header: 'Name', render: (r) => <Text size="small" style={mono}>{r.name}</Text> },
              { property: 'detail', header: 'Detail', render: (r) => <Text size="small">{r.detail}</Text> },
            ]}
            data={CREATED}
            primaryKey="name"
          />
        </Section>
        <Section title="Checked" summary="12 of 12 configuration checks match the sheet · failover test passed in 1.3 s">
          <StatusIndicator state="complete" label="Verify configuration: 12 of 12 match" />
          <StatusIndicator state="complete" label="Failover test on zz_rc_test_rcg: failover 1.3 s, back in sync 1.4 s" />
        </Section>
        <Section title="Still to do by hand" summary="1 item" open>
          <Text size="small">The customer's monitoring: add AlletraMP_D22U27 to Data Ops Manager. The tool does not do this yet.<Mark n={3} /></Text>
        </Section>
      </StepPage>
    </AppFrame>
  );
}

export const finish: Screen = {
  id: 'M10',
  title: 'Done: the hand-over',
  notes: [
    'The end of the job reads like a hand-over, not like the end of a wizard: what was done, in one sentence.',
    'Everything the customer or the next engineer needs, as a list: one file per line with what it is for. "Download everything as one zip" is a proposal; the three single downloads exist today.',
    'What the tool did not do, said plainly, so nothing is assumed finished.',
  ],
  keeps: [
    ['Mark run complete', 'Happens when the last step finishes; this page is what you see'],
    ['Start a new deployment', 'Start another run on this array, or Back to your runs'],
    ['As-built download', 'Hand-over package'],
  ],
  render: () => <Finish />,
};
