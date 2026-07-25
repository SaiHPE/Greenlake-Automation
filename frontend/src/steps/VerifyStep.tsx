import { Box, Button, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { useState } from 'react';
import { FieldCheck, RunEvent, RunRecord, VerificationReport, startVerify } from '../api';
import { CredentialsFields, InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const CHECK_STATE: Record<FieldCheck['status'], { state: StepState; label: string }> = {
  pass: { state: 'complete', label: 'Match' },
  mismatch: { state: 'action_required', label: 'Mismatch' },
  not_readable: { state: 'not_started', label: 'Not readable' },
};

export function VerifyStep({ runId, run, events, onDone }: Props) {
  const [username, setUsername] = useState('3paradm');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const mine = events.filter((event) => event.phase === 'CONFIG_VERIFY');
  const terminal = [...mine]
    .reverse()
    .find((event) => event.event_type === 'verify.completed' || event.event_type === 'verify.failed');
  const report =
    terminal?.event_type === 'verify.completed' ? ((terminal.data?.report as VerificationReport | undefined) ?? null) : null;
  const unreachable = terminal?.event_type === 'verify.failed' ? terminal.message : null;
  const running = submitting || mine[mine.length - 1]?.event_type === 'step.started';

  const mismatches = report ? report.checks.filter((check) => check.status !== 'pass').length : 0;
  const matches = report ? report.checks.filter((check) => check.status === 'pass').length : 0;

  const verify = async () => {
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
    <StepShell
      title="Verify configuration"
      description="Authenticates to the array over SSH and compares the running configuration against the workbook. Read-only."
      stateDetail={report ? (mismatches ? `${mismatches} discrepancy` : 'configuration matches') : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Enter the array credentials and run the verification."
      footerNote="A discrepancy never fails the run — disposition remains with the operator."
      actions={
        <>
          <Button
            busy={running}
            label={report ? 'Re-verify' : running ? 'Verifying' : 'Verify configuration'}
            disabled={!username.trim() || !password}
            onClick={verify}
          />
          <Button primary label="Continue" onClick={onDone} />
        </>
      }
    >
      <Surface
        title="Array credentials"
        description={`The array admin account registered in DSCC as the system credential for ${run?.serial_number ?? 'this array'}.`}
      >
        <CredentialsFields
          username={username}
          password={password}
          onUsername={setUsername}
          onPassword={setPassword}
          help="Used for this verification only; never stored."
        />
      </Surface>

      {unreachable && (
        <InlineNotification
          tone="warning"
          title="The array could not be reached over SSH"
          message={`${unreachable} Onboarding is unaffected — this verification is informational.`}
        />
      )}

      {report && (
        <>
          <Surface
            title="Configuration"
            description="Each setting from the workbook, compared against what the array reports."
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableCell scope="col">
                    <Text size="xsmall" weight={600} color="text-weak">
                      SETTING
                    </Text>
                  </TableCell>
                  <TableCell scope="col">
                    <Text size="xsmall" weight={600} color="text-weak">
                      EXPECTED
                    </Text>
                  </TableCell>
                  <TableCell scope="col">
                    <Text size="xsmall" weight={600} color="text-weak">
                      ON THE ARRAY
                    </Text>
                  </TableCell>
                  <TableCell scope="col">
                    <Text size="xsmall" weight={600} color="text-weak">
                      RESULT
                    </Text>
                  </TableCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.checks.map((check) => {
                  const meta = CHECK_STATE[check.status];
                  return (
                    <TableRow key={check.field}>
                      <TableCell>
                        <Text size="small">{check.field}</Text>
                      </TableCell>
                      <TableCell>
                        <Text size="small">{check.expected || '—'}</Text>
                      </TableCell>
                      <TableCell>
                        <Text size="small">{check.actual ?? '—'}</Text>
                      </TableCell>
                      <TableCell>
                        <StatusIndicator state={meta.state} label={meta.label} />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            <TableSummary>
              {matches} match · {mismatches} to review
            </TableSummary>
            <Text size="xsmall" color="text-weak">
              “Not readable” means the array did not report that value; check it by hand if it matters.
            </Text>
          </Surface>

          <Surface title="Array status" description="As reported by the array's own status check.">
            {report.health_issues.length === 0 ? (
              <InlineNotification tone="ok" title="No issues reported" />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableCell scope="col">
                      <Text size="xsmall" weight={600} color="text-weak">
                        COMPONENT
                      </Text>
                    </TableCell>
                    <TableCell scope="col">
                      <Text size="xsmall" weight={600} color="text-weak">
                        SUMMARY
                      </Text>
                    </TableCell>
                    <TableCell scope="col">
                      <Text size="xsmall" weight={600} color="text-weak">
                        COUNT
                      </Text>
                    </TableCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {report.health_issues.map((issue, index) => (
                    <TableRow key={`${issue.component}-${index}`}>
                      <TableCell>
                        <Text size="small">{issue.component}</Text>
                      </TableCell>
                      <TableCell>
                        <Text size="small">{issue.summary}</Text>
                      </TableCell>
                      <TableCell>
                        <Text size="small">{issue.qty}</Text>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            <Box flex={false}>
              <Text size="xsmall" color="text-weak">
                Each component listed requires manual attention — for example replication links, iLO, cage or security.
              </Text>
            </Box>
          </Surface>
        </>
      )}
    </StepShell>
  );
}
