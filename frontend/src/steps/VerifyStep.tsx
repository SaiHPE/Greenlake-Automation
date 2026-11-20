import { Box, Button, DataTable, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { Validate } from 'grommet-icons';
import { useState } from 'react';
import { CredentialOverride, FieldCheck, HealthIssue, IscsiVlanCheck, RunEvent, RunRecord, startVerify } from '../api';
import { isOf, latestOf } from '../events';
import { ArrayCredentialCard, credentialReady, useArrayCredential } from '../ui/ArrayCredentialCard';
import { Disclosure, EmptyState, Guidance, Section, mono } from '../ui/blocks';
import { NoValue, RESULT, ResultWord, StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const CHECK_STATE: Record<FieldCheck['status'], ResultWord> = {
  pass: RESULT.matches,
  mismatch: RESULT.differs,
  not_readable: RESULT.not_readable,
};

// SPEC-011 R3 (V-4): a Match between two visibly different strings says why.
const MATCH_NOTE: Record<NonNullable<FieldCheck['match']>, string> = {
  exact: '',
  contains: 'contains the expected value',
  includes: 'every expected value present',
};

// An iSCSI VLAN address is a setting (SPEC-030 R9): Matches when present, Differs when missing or
// different; the Detail column says which.
const VLAN_STATE: Record<IscsiVlanCheck['status'], ResultWord> = {
  present: RESULT.matches,
  missing: RESULT.differs,
  different: RESULT.differs,
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

/** One row per setting: the workbook value, the array value and the result. */
function SettingsTable({ checks, label }: { checks: FieldCheck[]; label: string }) {
  return (
    <DataTable
      columns={[
        { property: 'field', header: 'Setting', render: (c: FieldCheck) => <Text size="small">{c.field}</Text> },
        { property: 'expected', header: 'On the sheet', render: (c: FieldCheck) => (c.expected ? <Text size="small">{c.expected}</Text> : <NoValue />) },
        { property: 'actual', header: 'On the array', render: (c: FieldCheck) => (c.actual != null ? <Text size="small">{c.actual}</Text> : <NoValue />) },
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
      data={checks}
      primaryKey="field"
      a11yTitle={label}
    />
  );
}

export function VerifyStep({ runId, run, events, onDone }: Props) {
  const credential = useArrayCredential(runId);
  const { nextTitle } = useStepContext();
  const [override, setOverride] = useState<CredentialOverride>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const mine = events.filter((event) => event.phase === 'CONFIG_VERIFY');
  const terminal = latestOf(mine, 'verify.completed', 'verify.failed');
  const report = terminal?.event_type === 'verify.completed' ? (terminal.data?.report ?? null) : null;
  const unreachable = terminal?.event_type === 'verify.failed' ? terminal.message : null;
  const running = submitting || mine[mine.length - 1]?.event_type === 'step.started';

  const vlanChecks = report?.iscsi_vlans ?? [];
  const vlansOff = vlanChecks.filter((check) => check.status !== 'present');
  // a VLAN read that failed is one thing to review, never "configuration matches"
  const peerChecks = report?.peer_ports ?? [];
  const peersOff = peerChecks.filter((check) => !check.ok);
  const mismatches = report
    ? report.checks.filter((check) => check.status !== 'pass').length + vlansOff.length + (report.iscsi_vlans_error ? 1 : 0)
      + peersOff.length + (report.peer_ports_error ? 1 : 0)
    : 0;
  const matches = report ? report.checks.filter((check) => check.status === 'pass').length : 0;
  const notReadable = report ? report.checks.filter((check) => check.status === 'not_readable').length : 0;
  const differ = report ? report.checks.filter((check) => check.status === 'mismatch') : [];
  const toReview = report ? report.checks.filter((check) => check.status !== 'pass') : [];
  // what differs from the workbook, in every part the report reads
  const differing = differ.length + vlansOff.length + peersOff.length;
  // SPEC-011 R5 (X-7): the check before this one, within the run, for "new since" / "cleared".
  const completed = mine.filter((event) => isOf(event, 'verify.completed'));
  const previousEvent = completed.length >= 2 ? completed[completed.length - 2] : null;
  const previous = previousEvent?.data?.report ?? null;
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
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
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
        vlanChecks.length ? `${vlanChecks.length - vlansOff.length} of ${vlanChecks.length} iSCSI VLAN addresses present` : '',
        report.iscsi_vlans_error ? 'the iSCSI VLAN addresses could not be read' : '',
        peerChecks.length ? `${peerChecks.length - peersOff.length} of ${peerChecks.length} peer ports ready` : '',
        report.peer_ports_error ? 'the peer ports could not be read' : '',
        issues.length
          ? `the array's status check lists ${issueItems} item${issueItems === 1 ? '' : 's'} on ${issues.length} line${issues.length === 1 ? '' : 's'}${newIssues ? `, ${newIssues} line${newIssues === 1 ? '' : 's'} new since the last check` : ''}`
          : 'the array reports no status issues',
      ].filter(Boolean).join('; ') + '.'
    : '';

  // one status line (SPEC-030 R2): reading, unreachable, or what the report found
  const status: StepStatus | undefined = running
    ? { state: 'running', title: 'Reading the array', message: 'The configuration and the array’s status check, over SSH; about 20 seconds.' }
    : unreachable
      ? { state: 'action_required', title: 'The array could not be reached over SSH', message: `${unreachable} Onboarding is unaffected; this verification is a report.` }
      : report
        ? {
            state: mismatches || issues.length ? 'action_required' : 'complete',
            title: differing
              ? `${differing} setting${differing === 1 ? ' differs' : 's differ'} from the workbook`
              : mismatches
                ? `${mismatches} to review`
                : 'Configuration matches the workbook',
            message: summary,
            time: terminal ? hhmm(terminal.created_at) : undefined,
          }
        : undefined;

  return (
    <StepShell
      title="Verify configuration"
      description="Reads the array over SSH and compares what runs with what the workbook says; it changes nothing."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      primary={primary}
      buttons={buttons}
      guidance={
        <Guidance
          items={[
            { title: 'What is compared', body: 'Every setting the workbook gives: network, time, DSCC region, and the objects this run created. The array’s own status check is read too.' },
            { title: 'A setting that differs does not fail the run', body: 'It is reported for you to decide. "Not readable" means the array did not report that value; check it by hand if it matters.' },
            { title: 'Credentials', body: 'The array credential comes from the sheet and is held by this run only. Use a different one for this step if you need to.' },
          ]}
        />
      }
    >
      <ArrayCredentialCard info={credential} serial={run?.serial_number} override={override} onOverride={setOverride} />

      {!running && !report && !unreachable && (
        <EmptyState icon={<Validate size="large" color="icon-weak" />} title="Not verified yet">
          Verify configuration reads every setting the workbook gives from the array, and the array’s own status check. It writes
          nothing.
        </EmptyState>
      )}

      {report && (
        <Section
          // Section reads `open` once: each report is a new section, open when a setting needs a look
          key={terminal?.event_id}
          title={`Configuration: ${report.checks.length} settings`}
          summary={`${matches} match · ${mismatches} to review`}
          open={toReview.length > 0}
        >
          {toReview.length > 0 ? (
            <SettingsTable checks={toReview} label="Settings to review: one row per setting that differs or could not be read, the workbook value, the array value and the result" />
          ) : (
            <Text size="small" color="text-weak">
              Every setting matches the workbook.
            </Text>
          )}
          <Disclosure label="all settings" count={report.checks.length}>
            <SettingsTable checks={report.checks} label="Configuration: one row per setting, the workbook value, the array value and the result" />
          </Disclosure>
          {notReadable > 0 && (
            <Text size="xsmall" color="text-weak">“Not readable” means the array did not report that value; check it by hand if it matters.</Text>
          )}
        </Section>
      )}

      {report && (vlanChecks.length > 0 || report.iscsi_vlans_error) && (
        <Section
          title={`iSCSI VLAN addresses: ${vlanChecks.length} on the sheet`}
          summary={report.iscsi_vlans_error ? 'could not be read' : `${vlanChecks.length - vlansOff.length} present · ${vlansOff.length} to review`}
          open={vlansOff.length > 0 || Boolean(report.iscsi_vlans_error)}
        >
          {report.iscsi_vlans_error ? (
            <Text size="small">{report.iscsi_vlans_error}</Text>
          ) : (
            <DataTable
              columns={[
                { property: 'nsp', header: 'Port', render: (c: IscsiVlanCheck) => <Text size="small" style={mono}>{c.nsp}</Text> },
                { property: 'vlan_id', header: 'VLAN', render: (c: IscsiVlanCheck) => <Text size="small">{c.vlan_id}</Text> },
                {
                  property: 'status',
                  header: 'Result',
                  render: (c: IscsiVlanCheck) => <StatusIndicator state={VLAN_STATE[c.status].state} label={VLAN_STATE[c.status].label} />,
                },
                {
                  property: 'differences',
                  header: 'Detail',
                  render: (c: IscsiVlanCheck) => (
                    c.status === 'missing' ? (
                      <Text size="small">Missing: not on the array.</Text>
                    ) : c.differences.length ? (
                      <Text size="small">{c.differences.join('; ')}</Text>
                    ) : c.note ? (
                      <Text size="small">{c.note}</Text>
                    ) : (
                      <NoValue />
                    )
                  ),
                },
              ]}
              data={vlanChecks}
              primaryKey={false}
              a11yTitle="iSCSI VLAN addresses: one row per sheet row, present, missing or different on the array"
            />
          )}
        </Section>
      )}

      {report && (peerChecks.length > 0 || report.peer_ports_error) && (
        <Section
          title={`Peer ports: ${peerChecks.length} on the sheet`}
          summary={report.peer_ports_error ? 'could not be read' : `${peerChecks.length - peersOff.length} ready · ${peersOff.length} to review`}
          open={peersOff.length > 0 || Boolean(report.peer_ports_error)}
        >
          {report.peer_ports_error ? (
            <Text size="small">{report.peer_ports_error}</Text>
          ) : (
            <Box gap="xxsmall">
              {peerChecks.map((c) => (
                <StatusIndicator key={c.nsp} state={c.ok ? 'complete' : 'action_required'} label={c.sentence} />
              ))}
            </Box>
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
