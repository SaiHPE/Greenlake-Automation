import { Box, Button, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { useState } from 'react';
import { CredentialOverride, FieldCheck, HealthIssue, RunEvent, RunRecord, VerificationReport, startVerify } from '../api';
import { ArrayCredentialCard, credentialReady, useArrayCredential } from '../ui/ArrayCredentialCard';
import { ContinueButton, InlineNotification, Surface, TableSummary } from '../ui/primitives';
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

// SPEC-011 R3 (V-4): a Match between two visibly different strings says why.
const MATCH_NOTE: Record<NonNullable<FieldCheck['match']>, string> = {
  exact: '',
  contains: 'contains the expected value',
  includes: 'every expected value present',
};

const issueKey = (i: HealthIssue) => `${i.component}|${i.summary}`;
const hhmm = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

/** One array-status row with the array's own Detail rows behind an expander (SPEC-011 R1). */
function StatusRow({ issue, change }: { issue: HealthIssue; change: 'new' | '' }) {
  const [open, setOpen] = useState(false);
  const details = issue.details ?? [];
  return (
    <>
      <TableRow>
        <TableCell><Text size="small">{issue.component}</Text></TableCell>
        <TableCell>
          <Box direction="row" gap="small" align="center" wrap>
            <Text size="small">{issue.summary}</Text>
            {change === 'new' && <StatusIndicator state="action_required" label="new since the last check" />}
          </Box>
        </TableCell>
        <TableCell><Text size="small">{issue.qty}</Text></TableCell>
        <TableCell>
          <Button size="small" label={open ? 'Hide' : details.length ? `Show ${details.length}` : 'Show'} onClick={() => setOpen((v) => !v)} />
        </TableCell>
      </TableRow>
      {open && (
        <TableRow>
          <TableCell colSpan={4}>
            {details.length === 0 ? (
              <Text size="small" color="text-weak">The array gave no detail row for this component.</Text>
            ) : (
              <Box gap="xxsmall" pad={{ left: 'small' }}>
                {details.map((d, i) => (
                  <Box key={`${d.identifier}-${i}`} direction="row" gap="small" wrap>
                    <Text size="small" style={{ fontFamily: 'ui-monospace, Consolas, monospace' }}>{d.identifier}</Text>
                    <Text size="small">{d.description}</Text>
                    <Text size="small" color="text-weak">resolution: {d.resolution}</Text>
                  </Box>
                ))}
              </Box>
            )}
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

export function VerifyStep({ runId, run, events, onDone }: Props) {
  const credential = useArrayCredential(runId);
  const [override, setOverride] = useState<CredentialOverride>(null);
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
  const notReadable = report ? report.checks.filter((check) => check.status === 'not_readable').length : 0;
  // SPEC-011 R5 (X-7): the check before this one, within the run, for "new since" / "cleared".
  const completed = mine.filter((event) => event.event_type === 'verify.completed');
  const previousEvent = completed.length >= 2 ? completed[completed.length - 2] : null;
  const previous = (previousEvent?.data?.report as VerificationReport | undefined) ?? null;
  const previousKeys = new Set((previous?.health_issues ?? []).map(issueKey));
  const currentKeys = new Set((report?.health_issues ?? []).map(issueKey));
  const cleared = (previous?.health_issues ?? []).filter((i) => !currentKeys.has(issueKey(i)));

  const verify = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await startVerify(runId, override);
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
      activityEmpty={credential?.available ? 'Run the verification.' : 'Enter the array credentials and run the verification.'}
      footerNote="A discrepancy never fails the run — disposition remains with the operator."
      actions={
        <>
          <Button
            busy={running}
            label={report ? 'Re-verify' : running ? 'Verifying' : 'Verify configuration'}
            disabled={!credentialReady(credential, override)}
            onClick={verify}
          />
          <ContinueButton onClick={onDone} />
        </>
      }
    >
      <ArrayCredentialCard info={credential} serial={run?.serial_number} override={override} onOverride={setOverride} />

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
                        <Box gap="xxsmall">
                          <StatusIndicator state={meta.state} label={meta.label} />
                          {check.status === 'pass' && check.match && MATCH_NOTE[check.match] && (
                            <Text size="xsmall" color="text-weak">{MATCH_NOTE[check.match]}</Text>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            <TableSummary>
              {matches} match · {mismatches} to review
            </TableSummary>
            {notReadable > 0 && (
              <Text size="xsmall" color="text-weak">
                “Not readable” means the array did not report that value; check it by hand if it matters.
              </Text>
            )}
          </Surface>

          <Surface
            title="Array status"
            description={
              previousEvent
                ? `As reported by the array's own status check — compared with the check at ${hhmm(previousEvent.created_at)}.`
                : "As reported by the array's own status check."
            }
          >
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
                    <TableCell scope="col">
                      <Text size="xsmall" weight={600} color="text-weak">
                        DETAIL
                      </Text>
                    </TableCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {report.health_issues.map((issue, index) => (
                    <StatusRow
                      key={`${issue.component}-${index}`}
                      issue={issue}
                      change={previousEvent && !previousKeys.has(issueKey(issue)) ? 'new' : ''}
                    />
                  ))}
                </TableBody>
              </Table>
            )}
            {cleared.length > 0 && (
              <Text size="xsmall" color="text-weak">
                Cleared since the last check: {cleared.map((i) => `${i.component} — ${i.summary}`).join(' · ')}
              </Text>
            )}
            {report.health_issues.length > 0 && (
              <Box flex={false}>
                {/* SPEC-011 R2 (V-2): the guidance is the array's own detail rows, not our examples. */}
                <Text size="xsmall" color="text-weak">
                  Each component here needs attention outside this tool. Expand a row for the identifiers the array names
                  and the resolution it states.
                </Text>
              </Box>
            )}
          </Surface>
        </>
      )}
    </StepShell>
  );
}
