import { Anchor, Box, Button, FormField, NameValueList, NameValuePair, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { AsBuiltResult, RunEvent, RunRecord, asbuiltDownloadUrl, startAsbuilt } from '../api';
import { CredentialsFields, InlineNotification, Surface } from '../ui/primitives';
import { StepShell } from '../ui/StepShell';

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

  const mine = events.filter((event) => event.phase === 'ASBUILT_DOCUMENT');
  const running = submitting || mine[mine.length - 1]?.event_type === 'asbuilt.started';
  const terminal = [...mine]
    .reverse()
    .find((event) => event.event_type === 'asbuilt.generated' || event.event_type === 'asbuilt.failed');
  const result =
    terminal?.event_type === 'asbuilt.generated' ? ((terminal.data as unknown as AsBuiltResult) ?? null) : null;
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
    <StepShell
      title="As-built document"
      description="Reads the array's final configuration and renders it into the HPE Word template as the handover deliverable."
      stateDetail={result ? 'document ready' : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Enter the array credentials and generate the document."
      footerNote="Read-only — generation makes no changes to the array."
      actions={
        <>
          <Button
            busy={running}
            label={result ? 'Regenerate' : running ? 'Generating' : 'Generate document'}
            disabled={!username.trim() || !password}
            onClick={generate}
          />
          {result ? (
            <Anchor href={asbuiltDownloadUrl(runId)} download>
              <Button primary label="Download document" />
            </Anchor>
          ) : (
            <Button primary label="Continue" onClick={onDone} />
          )}
        </>
      }
    >
      <Surface
        title="Array credentials"
        description={`Read-only access to ${run?.serial_number ?? 'the array'} to collect its configuration, inventory and status.`}
      >
        <CredentialsFields
          username={username}
          password={password}
          onUsername={setUsername}
          onPassword={setPassword}
          help="Used for this read-only session only; never stored."
        />
      </Surface>

      <Surface title="Cover details" description="Operator-supplied fields; not stored on the array.">
        <Box direction="row" gap="medium" wrap>
          <Box width="medium">
            <FormField label="Customer name" htmlFor="asbuilt-customer">
              <TextInput
                id="asbuilt-customer"
                value={customer}
                onChange={(event) => setCustomer(event.target.value)}
                placeholder="Defaults to the workbook value"
              />
            </FormField>
          </Box>
          <Box width="medium">
            <FormField label="Site" htmlFor="asbuilt-site">
              <TextInput
                id="asbuilt-site"
                value={site}
                onChange={(event) => setSite(event.target.value)}
                placeholder="Defaults to the workbook value"
              />
            </FormField>
          </Box>
        </Box>
      </Surface>

      {failure && (
        <InlineNotification tone="warning" title="The document could not be generated" message={failure} />
      )}

      {result && (
        <Surface title="Document contents">
          <InlineNotification
            tone="ok"
            title={`as-built-${result.serial || 'array'}.docx is ready`}
            message={`${Math.max(1, Math.round((result.size ?? 0) / 1024))} KB. Inventory and status tables are included, formatted to the HPE template.`}
          />
          <NameValueList pairProps={{ direction: 'column' }}>
            <NameValuePair name="System name">
              <Text>{result.name || '—'}</Text>
            </NameValuePair>
            <NameValuePair name="Serial number">
              <Text>{result.serial || '—'}</Text>
            </NameValuePair>
            <NameValuePair name="Customer">
              <Text>{result.customer || '—'}</Text>
            </NameValuePair>
          </NameValueList>
        </Surface>
      )}
    </StepShell>
  );
}
