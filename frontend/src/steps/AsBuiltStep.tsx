import { Box, Button, FormField, Grid, Text, TextInput } from 'grommet';
import { Document } from 'grommet-icons';
import { useState } from 'react';
import { AsBuiltResult, CredentialOverride, HandoverStatus, RunEvent, RunRecord, asbuiltDownloadUrl, startAsbuilt } from '../api';
import { ArrayCredentialCard, credentialReady, useArrayCredential } from '../ui/ArrayCredentialCard';
import { DocList, EmptyState, Guidance, Panel, Section } from '../ui/blocks';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const hhmm = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

/** The alert verdict as a status: words from the same reads as the document's section. */
function alertStatus(status: HandoverStatus): { state: StepState; label: string } {
  const count = status.alerts_new;
  if (count === null) return { state: 'action_required', label: 'The alerts could not be read.' };
  if (count === 0) return { state: 'complete', label: 'No new alerts.' };
  const major = status.alerts_major ? ` (${status.alerts_major} Major or worse)` : '';
  const oldest = status.oldest_alert ? `; the oldest first occurred on ${status.oldest_alert}` : '';
  return { state: 'action_required', label: `${count} new alert${count === 1 ? '' : 's'}${major}${oldest}.` };
}

/** What the array said about itself when the document was made: its new alerts. */
function HandoverBlock({ status }: { status: HandoverStatus }) {
  const verdict = alertStatus(status);
  const failed = Object.keys(status.read_errors ?? {}).length;
  const summary = status.alerts_new === null ? 'alerts not read' : `${status.alerts_new} new alert${status.alerts_new === 1 ? '' : 's'}`;
  return (
    <Section title="Status at handover" summary={summary} open>
      <StatusIndicator state={verdict.state} label={verdict.label} />
      {status.cloud_alert !== null && (
        <Text size="small">The array reports it is disconnected from Data Services Cloud Console (alert {status.cloud_alert}).</Text>
      )}
      {!!status.alerts_new && (
        <Text size="small" color="text-weak">
          Alerts record an event, not the current state: compare each with the array’s status check before acting. The document lists them.
        </Text>
      )}
      {failed > 0 && (
        <Text size="xsmall" color="text-weak">
          {failed === 1 ? '1 read' : `${failed} reads`} could not be made. The document names each one, and so does Check before sending.
        </Text>
      )}
    </Section>
  );
}

function asBuiltFromEvent(data: Partial<AsBuiltResult> | undefined): AsBuiltResult | null {
  if (!data || typeof data.size !== 'number' || !Array.isArray(data.warnings)) return null;
  return {
    serial: typeof data.serial === 'string' ? data.serial : '',
    name: typeof data.name === 'string' ? data.name : '',
    customer: typeof data.customer === 'string' ? data.customer : '',
    size: data.size,
    warnings: data.warnings.map(String),
    handover: data.handover ?? null,
  };
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
  const result = terminal?.event_type === 'asbuilt.generated' ? asBuiltFromEvent(terminal.data) : null;
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
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
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

  const size = `${Math.max(1, Math.round((result?.size ?? 0) / 1024))} KB`;
  // one status line (SPEC-030 R2): writing, could not, or the document and what to check
  const status: StepStatus | undefined = running
    ? { state: 'running', title: 'Writing the document', message: 'Reading the array once more and filling the HPE template; about 30 seconds.' }
    : failure
      ? { state: 'action_required', title: 'The document could not be generated', message: failure }
      : result
        ? {
            state: warnings.length ? 'action_required' : 'complete',
            title: warnings.length ? `${fileName} is ready; check ${warnings.length} item${warnings.length === 1 ? '' : 's'} first` : `${fileName} is ready`,
            message: `${size}, formatted to the HPE template, with the inventory and status tables.`,
            time: terminal ? hhmm(terminal.created_at) : undefined,
          }
        : undefined;

  const field = (id: string, label: string, value: string, set: (v: string) => void, placeholder: string) => (
    <FormField key={id} label={label} htmlFor={`asbuilt-${id}`} name={id} margin="none">
      <TextInput id={`asbuilt-${id}`} name={id} value={value} onChange={(event) => set(event.target.value)} placeholder={placeholder} />
    </FormField>
  );

  const coverForm = (
    <Grid columns={{ count: 'fit', size: 'medium' }} gap="small">
      {field('customer', 'Customer name', customer, setCustomer, 'Defaults to the workbook value')}
      {field('site', 'Site / location', site, setSite, 'Defaults to the workbook value')}
      {field('workload', 'Application / workload', workload, setWorkload, 'e.g. VMware vSphere cluster')}
      {field('purpose', 'Purpose of using Block storage', purpose, setPurpose, 'e.g. primary datastore for the vault zone')}
    </Grid>
  );

  return (
    <StepShell
      title="As-built document"
      description="Reads the array's final configuration and writes it into the HPE Word template: the hand-over document for the customer."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      primary={primary}
      buttons={buttons}
      guidance={
        <Guidance
          items={[
            { title: 'What goes in', body: 'System, network and time settings; the ports, hosts, volumes and exports; replication and the failover test with its timings; the verification result; the array status: its new alerts and capacity in use. Making it changes nothing on the array.' },
            { title: 'Cover details', body: 'Customer and site come from the workbook; type here to change them. Workload and purpose are yours to fill. None of it is stored on the array.' },
            { title: 'Check before sending', body: 'The document is always produced. Anything that did not fill is listed here so it cannot be missed; this is the last screen before the document goes to the customer.' },
          ]}
        />
      }
    >
      {!running && !result && !failure && (
        <EmptyState icon={<Document size="large" color="icon-weak" />} title="Not generated yet">
          Generate document reads the array once more and fills the HPE template. Nothing is written to the array.
        </EmptyState>
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
              detail: `${size}${terminal ? ` · generated ${hhmm(terminal.created_at)}` : ''} · for the customer`,
              action: <Button size="small" as="a" href={asbuiltDownloadUrl(runId)} download label="Download" />,
            },
          ]}
        />
      )}

      {result?.handover && <HandoverBlock status={result.handover} />}

      <ArrayCredentialCard info={credential} serial={run?.serial_number} override={override} onOverride={setOverride} />

      {/* a field to fill before the document; once it is made, the form folds under the same title (the lab reads it) */}
      {result ? (
        <Section title="Cover details" summary="Not stored on the array. Customer and site default to the workbook when left empty.">
          {coverForm}
        </Section>
      ) : (
        <Panel title="Cover details" description="Not stored on the array. Customer and site default to the workbook when left empty.">
          {coverForm}
        </Panel>
      )}
    </StepShell>
  );
}
