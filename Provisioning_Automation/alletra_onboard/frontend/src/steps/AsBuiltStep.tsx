import { Anchor, Box, Button, FormField, Notification, Spinner, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { AsBuiltResult, RunEvent, RunRecord, asbuiltDownloadUrl, startAsbuilt } from '../api';
import { EventLog, Section } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

export function AsBuiltStep({ runId, run, events, onDone }: Props) {
  const [username, setUsername] = useState('3paradm');
  const [password, setPassword] = useState('');
  const [customer, setCustomer] = useState('');
  const [site, setSite] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Like verify, _run_asbuilt never touches run.status — progress is derived from the events.
  const stepEvents = events.filter((e) => e.phase === 'ASBUILT_DOCUMENT');
  const last = stepEvents[stepEvents.length - 1];
  const running = submitting || last?.event_type === 'asbuilt.started';

  const terminal = [...stepEvents].reverse().find((e) => e.event_type === 'asbuilt.generated' || e.event_type === 'asbuilt.failed');
  const result = terminal?.event_type === 'asbuilt.generated' ? ((terminal.data as unknown as AsBuiltResult) ?? null) : null;
  const failure = terminal?.event_type === 'asbuilt.failed' ? terminal.message : null;

  const generate = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await startAsbuilt(runId, username.trim(), password, customer.trim(), site.trim());
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box gap="medium">
      <Notification
        status="normal"
        title="Generate the as-built document"
        message={`Reads array ${run?.serial_number ?? ''} over SSH (read-only: show* + checkhealth + showinventory) and produces the HPE-branded as-built .docx — Table 01 config, the full hardware inventory, and the checkhealth output. It changes nothing on the array.`}
      />

      <Section title="1 · Array admin credentials & cover details">
        <Text size="small">
          Use the array admin account (e.g. <b>3paradm</b>). The password is used only for this read-only SSH
          session — never stored. Customer name / site fill the cover page (defaulting to the sheet values).
        </Text>
        <Box direction="row" gap="medium" wrap>
          <FormField label="Username">
            <TextInput value={username} onChange={(e) => setUsername(e.target.value)} placeholder="3paradm" />
          </FormField>
          <FormField label="Password">
            <TextInput type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </FormField>
          <FormField label="Customer name (cover page)">
            <TextInput value={customer} onChange={(e) => setCustomer(e.target.value)} placeholder="from the sheet" />
          </FormField>
          <FormField label="Site / location (optional)">
            <TextInput value={site} onChange={(e) => setSite(e.target.value)} />
          </FormField>
        </Box>
        <Box direction="row" gap="small" align="center">
          <Button
            primary
            label={running ? 'Building…' : 'Generate as-built'}
            disabled={running || !username.trim() || !password}
            onClick={generate}
          />
          {running && <Spinner />}
        </Box>
      </Section>

      {error && <Notification status="critical" title="Request failed" message={error} onClose={() => setError(null)} />}
      {failure && <Notification status="warning" title="Could not build the as-built" message={failure} />}

      {result && (
        <Section title="As-built ready">
          <Notification
            status="normal"
            title={`As-built generated for ${result.name || result.serial}`}
            message={`${Math.max(1, Math.round((result.size ?? 0) / 1024))} KB${result.customer ? ` · cover: ${result.customer}` : ''}. Download the .docx below.`}
          />
          <Box direction="row" gap="small" align="center">
            <Anchor href={asbuiltDownloadUrl(runId)} download>
              <Button primary label="Download as-built (.docx)" />
            </Anchor>
            <Button label="Rebuild" onClick={generate} disabled={running} />
          </Box>
        </Section>
      )}

      <Section title="Progress">
        <EventLog events={stepEvents} emptyText="Enter the credentials and generate to see progress here." />
      </Section>

      <Button primary label="Finish →" onClick={onDone} alignSelf="start" />
    </Box>
  );
}
