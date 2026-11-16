import { Box, Button, DataTable, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { Validate } from 'grommet-icons';
import { useState } from 'react';
import { CredentialOverride, FieldCheck, HealthIssue, RunEvent, RunRecord, VerificationReport, startVerify } from '../api';
import { ArrayCredentialCard, credentialReady, useArrayCredential } from '../ui/ArrayCredentialCard';
import { EmptyState, Guidance, Section, StatusLine, mono } from '../ui/blocks';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

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

const HEAD = (label: string) => (
  <TableCell scope="col">
    <Text size="small" weight={500}>{label}</Text>
  </TableCell>
);

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
        <TableCell align="right"><Text size="small">{issue.qty}</Text></TableCell>
        <TableCell>
          <Button size="small" label={open ? 'Hide detail' : details.length ? `Show ${details.length}` : 'Show detail'} onClick={() => setOpen((v) => !v)} aria-expanded={open} />
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
                    <Text size="small" style={mono}>{d.identifier}</Text>
                    <Text size="small">{d.description}</Text>
                    <Text size="small" color="text-weak">Resolution: {d.resolution}</Text>
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
  const { nextTitle } = useStepContext();
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
  const differ = report ? report.checks.filter((check) => check.status === 'mismatch') : [];
  // SPEC-011 R5 (X-7): the check before this one, within the run, for "new since" / "cleared".
  const completed = mine.filter((event) => event.event_type === 'verify.completed');
  const previousEvent = completed.length >= 2 ? completed[completed.length - 2] : null;
  const previous = (previousEvent?.data?.report as VerificationReport | undefined) ?? null;
  const previousKeys = new Set((previous?.health_issues ?? []).map(issueKey));
  const currentKeys = new Set((report?.health_issues ?? []).map(issueKey));
  const cleared = (previous?.health_issues ?? []).filter((i) => !currentKeys.has(issueKey(i)));
  const issues = report?.health_issues ?? [];
  // each line is one component and summary; qty is how many items the array counts on it
  const issueItems = issues.reduce((n, i) => n + (i.qty || 0), 0);
  const newIssues = previousEvent ? issues.filter((i) => !previousKeys.has(issueKey(i))).length : 0;

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

  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const verifyAction: FooterAction = {
    label: report ? 'Verify again' : 'Verify configuration',
    busy: running,
    onClick: verify,
    blocked: credentialReady(credential, override) ? undefined : 'Enter the array credentials first (Array credentials, at the top).',
  };
  const primary: FooterAction | undefined = running ? undefined : report ? { label: next, onClick: onDone } : verifyAction;
  // Continue was always available here: a discrepancy is the operator's to decide, never a stop.
  const buttons: FooterAction[] = running ? [] : report ? [verifyAction] : [{ label: `${next} without verifying`, onClick: onDone }];

  const summary = report
    ? [
        `${matches} of ${report.checks.length} settings match`,
        differ.length ? `${differ.map((c) => c.field).join(', ')} differ${differ.length === 1 ? 's' : ''}` : '',
        notReadable ? `${notReadable} not readable` : '',
        issues.length
          ? `The array's status check lists ${issueItems} item${issueItems === 1 ? '' : 's'} on ${issues.length} line${issues.length === 1 ? '' : 's'}${newIssues ? `, ${newIssues} line${newIssues === 1 ? '' : 's'} new since the last check` : ''}`
          : 'The array reports no status issues',
      ].filter(Boolean).join('. ') + '.'
    : '';

  return (
    <StepShell
      title="Verify configuration"
      description="Reads the array over SSH and compares what runs with what the workbook says. Changes nothing."
      stateDetail={report ? (mismatches ? `${mismatches} to review` : 'configuration matches') : undefined}
      error={error}
      onDismissError={() => setError(null)}
      primary={primary}
      buttons={buttons}
      guideOpen={!report}
      guidance={
        <Guidance
          items={[
            { title: 'What is compared', body: 'Every setting the workbook gives: network, time, DSCC region, and the objects this run created. The array’s own status check is read too.' },
            { title: 'A mismatch does not fail the run', body: 'It is reported for you to decide. "Not readable" means the array did not report that value; check it by hand if it matters.' },
            { title: 'Credentials', body: 'The array credential comes from the sheet and is held by this run only. Use a different one for this step if you need to.' },
          ]}
        />
      }
    >
      <ArrayCredentialCard info={credential} serial={run?.serial_number} override={override} onOverride={setOverride} />

      {running && (
        <StatusLine state="running" title="Reading the array">
          The configuration and the array’s status check, over SSH. About 20 seconds.
        </StatusLine>
      )}

      {!running && unreachable && (
        <StatusLine state="action_required" title="The array could not be reached over SSH">
          {unreachable} Onboarding is unaffected; this verification is a report.
        </StatusLine>
      )}

      {!running && !report && !unreachable && (
        <EmptyState icon={<Validate size="large" color="icon-weak" />} title="Not verified yet">
          Verify configuration reads every setting the workbook gives from the array, and the array’s own status check. It writes
          nothing.
        </EmptyState>
      )}

      {report && !running && (
        <StatusLine
          state={mismatches || issues.length ? 'action_required' : 'complete'}
          title={mismatches ? `${mismatches} to review` : 'Configuration matches the workbook'}
          time={terminal ? hhmm(terminal.created_at) : undefined}
        >
          {summary}
        </StatusLine>
      )}

      {report && (
        <Section
          title={`Configuration: ${report.checks.length} settings`}
          summary={`${matches} match · ${mismatches} to review`}
          open={mismatches > 0}
        >
          <DataTable
            columns={[
              { property: 'field', header: 'Setting', render: (c: FieldCheck) => <Text size="small">{c.field}</Text> },
              { property: 'expected', header: 'On the sheet', render: (c: FieldCheck) => <Text size="small">{c.expected || '--'}</Text> },
              { property: 'actual', header: 'On the array', render: (c: FieldCheck) => <Text size="small">{c.actual ?? '--'}</Text> },
              {
                property: 'status',
                header: 'Result',
                render: (c: FieldCheck) => (
                  <Box gap="xxsmall">
                    <StatusIndicator state={CHECK_STATE[c.status].state} label={CHECK_STATE[c.status].label} />
                    {c.status === 'pass' && c.match && MATCH_NOTE[c.match] && (
                      <Text size="xsmall" color="text-weak">{MATCH_NOTE[c.match]}</Text>
                    )}
                  </Box>
                ),
              },
            ]}
            data={report.checks}
            primaryKey="field"
            a11yTitle="Configuration: one row per setting, the workbook value, the array value and the result"
          />
          {notReadable > 0 && (
            <Text size="xsmall" color="text-weak">“Not readable” means the array did not report that value; check it by hand if it matters.</Text>
          )}
        </Section>
      )}

      {report && (
        <Section
          title="Array status"
          summary={`${issues.length ? `${issues.length} issue${issues.length === 1 ? '' : 's'}` : 'No issues reported'}${previousEvent ? ` · compared with the check at ${hhmm(previousEvent.created_at)}` : ''}`}
          open={issues.length > 0}
        >
          {issues.length === 0 ? (
            <StatusIndicator state="complete" label="No issues reported by the array’s status check." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  {HEAD('Component')}
                  {HEAD('Summary')}
                  {HEAD('Count')}
                  {HEAD('Detail')}
                </TableRow>
              </TableHeader>
              <TableBody>
                {issues.map((issue, index) => (
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
              Cleared since the last check: {cleared.map((i) => `${i.component}: ${i.summary}`).join(' · ')}
            </Text>
          )}
          {issues.length > 0 && (
            // SPEC-011 R2 (V-2): the guidance is the array's own detail rows, not our examples.
            <Text size="xsmall" color="text-weak">
              Each component here needs attention outside this tool. Show detail for the identifiers the array names and the
              resolution it states.
            </Text>
          )}
        </Section>
      )}
    </StepShell>
  );
}
