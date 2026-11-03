import { Box, Button, FormField, Grid, NameValueList, NameValuePair, Text, TextInput } from 'grommet';
import { Document } from 'grommet-icons';
import { RUN, rail, stepLabel } from '../data';
import { Action, AppFrame, DocList, EmptyState, Guidance, Mark, Panel, Section, StatusLine, StepPage } from '../kit';
import { Screen } from '../screen';

const FIELDS: { id: string; label: string; value: string; placeholder: string }[] = [
  { id: 'customer', label: 'Customer name', value: 'Contoso Bank', placeholder: 'Defaults to the workbook value' },
  { id: 'site', label: 'Site / location', value: 'Tokyo DC2, rack 13', placeholder: 'Defaults to the workbook value' },
  { id: 'workload', label: 'Application / workload', value: '', placeholder: 'e.g. VMware vSphere cluster' },
  { id: 'purpose', label: 'Purpose of using Block storage', value: '', placeholder: 'e.g. primary datastore for the vault zone' },
];

const WARNINGS = [
  'Application / workload is empty on the cover page.',
  'The switch F2 zone list could not be read (login refused); the SAN zoning section shows the command set only.',
];

function AsBuilt({ state, setState }: { state: string; setState: (s: string) => void }) {
  const ready = state !== 'before';
  const warn = state === 'warnings';
  const primary: Action = ready ? { label: 'Finish run' } : { label: 'Generate document', onClick: () => setState('ready') };
  const actions: Action[] = ready ? [{ label: 'Generate again', onClick: () => setState('ready') }] : [];
  return (
    <AppFrame run={RUN} groups={rail('asbuilt', ready ? 'complete' : 'not_started')} current="asbuilt">
      <StepPage
        stepLabel={stepLabel('asbuilt')}
        title="As-built document"
        description="Reads the array's final configuration and writes it into the HPE Word template: the hand-over document for the customer."
        state={ready ? (warn ? 'action_required' : 'complete') : 'not_started'}
        stateLabel={ready ? (warn ? '2 items to check' : 'Document ready') : 'Not generated'}
        primary={primary}
        actions={actions}
        guideOpen={!ready}
        activity={{ last: ready ? '20:05:11  As-built generated (764 KB)' : '19:53:20  Verified: 12 of 12 match', events: ready ? 40 : 36, commands: ready ? 84 : 71 }}
        guidance={
          <Guidance
            items={[
              { title: 'What goes in', body: 'System, network and time settings; the ports, hosts, volumes and exports; replication and the failover test with its timings; the verification result; the array status.' },
              { title: 'Cover details', body: 'Customer and site come from the workbook; you can change them here. Workload and purpose are yours to fill. None of it is stored on the array.' },
              { title: 'Check before sending', body: 'The document is always produced. Anything that did not fill is listed here so it cannot be missed; it is the last screen before the document goes to the customer.' },
            ]}
          />
        }
      >
        {ready && (warn ? (
          <StatusLine state="action_required" time="20:05">
            as-built-CZ2D320BT1.docx is ready (764 KB). Check 2 items before you send it.<Mark n={2} />
          </StatusLine>
        ) : (
          <StatusLine state="complete" time="20:05">as-built-CZ2D320BT1.docx is ready (764 KB), formatted to the HPE template.<Mark n={2} /></StatusLine>
        ))}
        {warn && (
          <Panel title="Check before sending">
            <Box as="ol" margin="none" pad={{ left: 'medium' }} gap="xsmall">
              {WARNINGS.map((w) => <Text as="li" key={w} size="small">{w}</Text>)}
            </Box>
            <Text size="xsmall" color="text-weak">Fill the field or fix the cause, then Generate again. Or send it as it is; the document says where a value is missing.</Text>
          </Panel>
        )}
        {ready && <DocList items={[{ icon: <Document />, name: 'as-built-CZ2D320BT1.docx', detail: '764 KB · generated 20:05 · for the customer', action: 'Download' }]} />}

        <Section title="Array credentials" summary="From the sheet: 3paradm @ 10.64.122.99 · held by this run only" level={2}>
          <Text size="small" color="text-weak">Typed once, on the sheet. A different credential here is used for this step only and is not stored.</Text>
          <Box direction="row"><Button size="small" label="Use a different credential" /></Box>
        </Section>

        <Panel title={<>Cover details<Mark n={1} /></>}>
          <Grid columns={{ count: 'fit', size: 'medium' }} gap="small">
            {FIELDS.map((f) => (
              <FormField key={f.id} label={f.label} htmlFor={`ab-${f.id}`} name={f.id} margin="none">
                <TextInput id={`ab-${f.id}`} name={f.id} defaultValue={f.value} placeholder={f.placeholder} />
              </FormField>
            ))}
          </Grid>
          <Text size="xsmall" color="text-weak">Not stored on the array. Customer and site default to the workbook.</Text>
        </Panel>

        {!ready && (
          <EmptyState icon={<Document size="large" color="icon-weak" />} title="Not generated yet">
            Generate document reads the array once more and fills the HPE template. About 30 seconds. Nothing is written to the array.
          </EmptyState>
        )}

        {ready && (
          <Panel title="On the cover">
            <NameValueList pairProps={{ direction: 'column' }}>
              <NameValuePair name="System name"><Text size="small">AlletraMP_D22U27</Text></NameValuePair>
              <NameValuePair name="Serial number"><Text size="small">CZ2D320BT1</Text></NameValuePair>
              <NameValuePair name="Customer"><Text size="small">Contoso Bank</Text></NameValuePair>
              <NameValuePair name="Site"><Text size="small">Tokyo DC2, rack 13</Text></NameValuePair>
              <NameValuePair name="Application / workload"><Text size="small" color={warn ? 'text-weak' : undefined} a11yTitle={warn ? 'No value' : undefined}>{warn ? '--' : 'VMware vSphere cluster'}</Text></NameValuePair>
            </NameValueList>
          </Panel>
        )}
      </StepPage>
    </AppFrame>
  );
}

export const asbuilt: Screen = {
  id: 'M14',
  title: 'As-built document',
  states: [
    { key: 'before', label: 'Not generated' },
    { key: 'ready', label: 'Document ready' },
    { key: 'warnings', label: 'Ready, 2 items to check' },
  ],
  notes: [
    'The cover fields are a Design System form: label above each field, two per row when there is room, defaults from the workbook. Nothing else to read before the green button.',
    'When the document is ready: one line with the file name and size, the file as a list row with Download, and what is on the cover as a name-value list (an empty value shows as "--", as the Design System asks). Anything that did not fill is a numbered list you cannot miss.',
  ],
  keeps: [
    ['Array credentials card', 'Folded section at the top'],
    ['Cover details (customer, site, workload, purpose)', 'Cover details panel'],
    ['Generate document / Regenerate', 'Footer, right (green); then Generate again beside Finish run'],
    ['Warnings list', 'Check before sending panel'],
    ['Document ready note, System name / Serial / Customer', 'Top line and On the cover'],
    ['Download document', 'The file row'],
    ['Continue (Finish)', 'Footer, right (green): Finish run opens the Done page'],
  ],
  render: (state, setState) => <AsBuilt state={state} setState={setState} />,
};
