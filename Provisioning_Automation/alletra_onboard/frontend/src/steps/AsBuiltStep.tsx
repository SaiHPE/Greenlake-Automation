import { Box, Button, FormField, Grid, NameValueList, NameValuePair, Text, TextInput } from 'grommet';
import { Document } from 'grommet-icons';
import { useState } from 'react';
import { AsBuiltResult, CredentialOverride, RunEvent, RunRecord, asbuiltDownloadUrl, startAsbuilt } from '../api';
import { ArrayCredentialCard, credentialReady, useArrayCredential } from '../ui/ArrayCredentialCard';
import { DocList, EmptyState, Guidance, Panel, StatusLine } from '../ui/blocks';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const hhmm = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

/** A value on the cover, or "--" read as "No value" (Design System name-value list). */
function CoverValue({ value }: { value?: string }) {
  return value ? <Text size="small">{value}</Text> : <Text size="small" color="text-weak" a11yTitle="No value">--</Text>;
}

export function AsBuiltStep({ runId, run, events, onDone }: Props) {
  const credential = useArrayCredential(runId);
  const { nextTitle } = useStepContext();
  const [override, setOverride] = useState<CredentialOverride>(null);
  const [customer, setCustomer] = useState('');
  const [site, setSite] = useState('');
  const [workload, setWorkload] = useState('');
  const [purpose, setPurpose] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const mine = events.filter((event) => event.phase === 'ASBUILT_DOCUMENT');
  const running = submitting || mine[mine.length - 1]?.event_type === 'asbuilt.started';
  const terminal = [...mine]
    .reverse()
    .find((event) => event.event_type === 'asbuilt.generated' || event.event_type === 'asbuilt.failed');
  const result =
    terminal?.event_type === 'asbuilt.generated' ? ((terminal.data as unknown as AsBuiltResult) ?? null) : null;
  const failure = terminal?.event_type === 'asbuilt.failed' ? terminal.message : null;
  const warnings = result?.warnings ?? [];
  const fileName = `as-built-${result?.serial || 'array'}.docx`;

  const generate = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await startAsbuilt(
        runId, override, customer.trim(), site.trim(),
        workload.trim(), purpose.trim(),
      );
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setSubmitting(false);
    }
  };

  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const generateAction: FooterAction = {
    label: result ? 'Generate again' : 'Generate document',
    busy: running,
    onClick: generate,
    blocked: credentialReady(credential, override) ? undefined : 'Enter the array credentials first (Array credentials, at the top).',
  };
  // Continue never depends on the document: this is the last action step, and the summary must stay reachable.
  const primary: FooterAction | undefined = running ? undefined : result ? { label: next, onClick: onDone } : generateAction;
  const buttons: FooterAction[] = running ? [] : result ? [generateAction] : [{ label: `${next} without the document`, onClick: onDone }];

  const field = (id: string, label: string, value: string, set: (v: string) => void, placeholder: string) => (
    <FormField key={id} label={label} htmlFor={`asbuilt-${id}`} name={id} margin="none">
      <TextInput id={`asbuilt-${id}`} name={id} value={value} onChange={(event) => set(event.target.value)} placeholder={placeholder} />
    </FormField>
  );

  return (
    <StepShell
      title="As-built document"
      description="Reads the array's final configuration and writes it into the HPE Word template: the hand-over document for the customer. Changes nothing."
      stateDetail={result ? (warnings.length ? `${warnings.length} item${warnings.length === 1 ? '' : 's'} to check` : 'document ready') : undefined}
      error={error}
      onDismissError={() => setError(null)}
      primary={primary}
      buttons={buttons}
      guideOpen={!result}
      guidance={
        <Guidance
          items={[
            { title: 'What goes in', body: 'System, network and time settings; the ports, hosts, volumes and exports; replication and the failover test with its timings; the verification result; the array status.' },
            { title: 'Cover details', body: 'Customer and site come from the workbook; type here to change them. Workload and purpose are yours to fill. None of it is stored on the array.' },
            { title: 'Check before sending', body: 'The document is always produced. Anything that did not fill is listed here so it cannot be missed; this is the last screen before the document goes to the customer.' },
          ]}
        />
      }
    >
      {running && (
        <StatusLine state="running" title="Writing the document">
          Reading the array once more and filling the HPE template. About 30 seconds.
        </StatusLine>
      )}

      {!running && failure && (
        <StatusLine state="action_required" title="The document could not be generated">
          {failure}
        </StatusLine>
      )}

      {result && !running && (
        <StatusLine
          state={warnings.length ? 'action_required' : 'complete'}
          title={warnings.length ? `${fileName} is ready. Check ${warnings.length} item${warnings.length === 1 ? '' : 's'} before you send it.` : `${fileName} is ready`}
          time={terminal ? hhmm(terminal.created_at) : undefined}
        >
          {`${Math.max(1, Math.round((result.size ?? 0) / 1024))} KB, formatted to the HPE template, with the inventory and status tables.`}
        </StatusLine>
      )}

      {result && warnings.length > 0 && (
        <Panel title="Check before sending">
          <Box as="ol" margin="none" pad={{ left: 'medium' }} gap="xsmall">
            {warnings.map((w) => (
              <Text as="li" key={w} size="small">{w}</Text>
            ))}
          </Box>
          <Text size="xsmall" color="text-weak">Fill the field or fix the cause, then Generate again. Or send it as it is; the document marks where a value is missing.</Text>
        </Panel>
      )}

      {result && (
        <DocList
          label="The generated document"
          items={[
            {
              icon: <Document />,
              name: fileName,
              detail: `${Math.max(1, Math.round((result.size ?? 0) / 1024))} KB${terminal ? ` · generated ${hhmm(terminal.created_at)}` : ''} · for the customer`,
              action: <Button size="small" as="a" href={asbuiltDownloadUrl(runId)} download label="Download" />,
            },
          ]}
        />
      )}

      <ArrayCredentialCard info={credential} serial={run?.serial_number} override={override} onOverride={setOverride} />

      <Panel title="Cover details" description="Not stored on the array. Customer and site default to the workbook when left empty.">
        <Grid columns={{ count: 'fit', size: 'medium' }} gap="small">
          {field('customer', 'Customer name', customer, setCustomer, 'Defaults to the workbook value')}
          {field('site', 'Site / location', site, setSite, 'Defaults to the workbook value')}
          {field('workload', 'Application / workload', workload, setWorkload, 'e.g. VMware vSphere cluster')}
          {field('purpose', 'Purpose of using Block storage', purpose, setPurpose, 'e.g. primary datastore for the vault zone')}
        </Grid>
      </Panel>

      {!running && !result && !failure && (
        <EmptyState icon={<Document size="large" color="icon-weak" />} title="Not generated yet">
          Generate document reads the array once more and fills the HPE template. Nothing is written to the array.
        </EmptyState>
      )}

      {result && (
        <Panel title="On the cover">
          <NameValueList pairProps={{ direction: 'column' }}>
            <NameValuePair name="System name">
              <CoverValue value={result.name} />
            </NameValuePair>
            <NameValuePair name="Serial number">
              <CoverValue value={result.serial} />
            </NameValuePair>
            <NameValuePair name="Customer">
              <CoverValue value={result.customer} />
            </NameValuePair>
          </NameValueList>
        </Panel>
      )}
    </StepShell>
  );
}
