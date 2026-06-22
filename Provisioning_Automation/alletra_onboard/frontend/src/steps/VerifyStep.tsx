import { Box, Button, FormField, Notification, Spinner, Table, TableBody, TableCell, TableHeader, TableRow, Tag, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { FieldCheck, RunEvent, RunRecord, VerificationReport, startVerify } from '../api';
import { EventLog, Section } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const STATUS_META: Record<FieldCheck['status'], { label: string; color: string }> = {
  pass: { label: 'OK', color: 'status-ok' },
  mismatch: { label: 'Mismatch', color: 'status-critical' },
  not_readable: { label: 'Not readable', color: 'status-warning' },
};

export function VerifyStep({ runId, run, events, onDone }: Props) {
  const [username, setUsername] = useState('3paradm');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // _run_verify never touches run.status (the run stays SUCCEEDED/COMPLETE), so progress is
  // derived purely from the CONFIG_VERIFY events: step.started -> verify.completed | verify.failed.
  const verifyEvents = events.filter((e) => e.phase === 'CONFIG_VERIFY');
  const lastEvent = verifyEvents[verifyEvents.length - 1];
  const running = submitting || lastEvent?.event_type === 'step.started';

  const terminal = [...verifyEvents]
    .reverse()
    .find((e) => e.event_type === 'verify.completed' || e.event_type === 'verify.failed');
  const report =
    terminal?.event_type === 'verify.completed'
      ? ((terminal.data?.report as VerificationReport | undefined) ?? null)
      : null;
  const failureMessage = terminal?.event_type === 'verify.failed' ? terminal.message : null;

  const runVerify = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await startVerify(runId, username.trim(), password);
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
        title="Optional: verify the array configuration"
        message={`Array ${run?.serial_number ?? ''} is initialised. This logs into it over SSH (read-only) with the admin credentials and checks that the live settings match what you onboarded. It changes nothing and is safe to skip.`}
      />

      <Section title="1 · Array admin credentials">
        <Text size="small">
          Use the array admin account — the DSCC <b>System Credential</b> you set in the wizard (e.g. <b>3paradm</b>).
          The password is used only for this SSH session; it is never stored or written to disk.
        </Text>
        <Box direction="row" gap="medium" wrap>
          <FormField label="Username">
            <TextInput value={username} onChange={(e) => setUsername(e.target.value)} placeholder="3paradm" />
          </FormField>
          <FormField label="Password">
            <TextInput type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </FormField>
        </Box>
        <Box direction="row" gap="small" align="center">
          <Button
            primary
            label={running ? 'Checking…' : 'Verify configuration'}
            disabled={running || !username.trim() || !password}
            onClick={runVerify}
          />
          {running && <Spinner />}
        </Box>
      </Section>

      {error && <Notification status="critical" title="Request failed" message={error} onClose={() => setError(null)} />}

      {failureMessage && (
        <Notification
          status="warning"
          title="Could not reach the array over SSH"
          message={`${failureMessage} You can still finish onboarding — this check is informational.`}
        />
      )}

      {report && <ReportView report={report} />}

      <Section title="Progress">
        <EventLog events={verifyEvents} emptyText="Enter the credentials and run the check to see progress here." />
      </Section>

      <Button primary label="Continue to summary →" onClick={onDone} alignSelf="start" />
    </Box>
  );
}

function ReportView({ report }: { report: VerificationReport }) {
  const mismatch = report.checks.filter((c) => c.status === 'mismatch').length;
  const unreadable = report.checks.filter((c) => c.status === 'not_readable').length;
  const pass = report.checks.filter((c) => c.status === 'pass').length;
  const criticalMismatch = report.checks.some((c) => c.status === 'mismatch' && c.critical);

  return (
    <Section title="Verification report">
      <Notification
        status={mismatch ? (criticalMismatch ? 'critical' : 'warning') : 'normal'}
        title={mismatch ? `${mismatch} setting(s) do not match what you onboarded` : 'All readable settings match what you onboarded'}
        message={`${pass} OK · ${mismatch} mismatch · ${unreadable} not readable`}
      />
      <Table>
        <TableHeader>
          <TableRow>
            <TableCell scope="col" border="bottom"><Text size="small" weight="bold">Setting</Text></TableCell>
            <TableCell scope="col" border="bottom"><Text size="small" weight="bold">Expected</Text></TableCell>
            <TableCell scope="col" border="bottom"><Text size="small" weight="bold">On the array</Text></TableCell>
            <TableCell scope="col" border="bottom"><Text size="small" weight="bold">Result</Text></TableCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.checks.map((check) => {
            const meta = STATUS_META[check.status];
            return (
              <TableRow key={check.field}>
                <TableCell>
                  <Text size="small">{check.field}</Text>
                  {check.critical && (
                    <Text size="xsmall" color="text-weak">
                      {' '}· critical
                    </Text>
                  )}
                </TableCell>
                <TableCell><Text size="small">{check.expected || '—'}</Text></TableCell>
                <TableCell><Text size="small">{check.actual ?? '—'}</Text></TableCell>
                <TableCell><Tag size="small" value={meta.label} border={{ color: meta.color }} /></TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      <Text size="xsmall" color="text-weak">
        “Not readable” means the array didn’t expose that value in its CLI output (or the parser missed it) — check it
        by hand if it matters. Raw command output is recorded in the run timeline data.
      </Text>
    </Section>
  );
}
