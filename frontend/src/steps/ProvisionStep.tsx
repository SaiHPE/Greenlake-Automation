import { Box, Button, CheckBox, Notification, Spinner, Table, TableBody, TableCell, TableHeader, TableRow, Tag, Text } from 'grommet';
import { useState } from 'react';
import { PathVerdict, PathVerification, ProvisioningPlan, ProvisioningResult, RunEvent, RunRecord, storageApply, storagePreview, verifyPaths } from '../api';
import { EventLog, Section } from '../components';
import { ProvisioningBuilderView } from './ProvisioningBuilderView';

const VERDICT_COLOR: Record<PathVerdict, string> = { live: 'status-ok', partial: 'status-warning', no_path: 'status-unknown' };

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

function latest<T>(events: RunEvent[], type: string, key: string): T | null {
  const event = [...events].reverse().find((e) => e.event_type === type);
  return (event?.data?.[key] as T) ?? null;
}

export function ProvisionStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const running = run?.status === 'running';
  const plan = latest<ProvisioningPlan>(events, 'storage.previewed', 'plan');
  const result = latest<ProvisioningResult>(events, 'storage.applied', 'result');
  const paths = latest<PathVerification>(events, 'storage.paths.verified', 'verification');

  const call = (fn: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await fn();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <Box gap="medium">
      <ProvisioningBuilderView runId={runId} disabled={running} />

      <Section title="Provision storage (host · volumes · LUN export)">
        <Text size="small" color="text-weak">
          Creates one host definition per ESXi server (all FC WWNs, at the discovered persona — VMware =
          WSAPI 8), groups them in the host set, creates the volumes in the CPG, and exports them per the
          composition above (or the default). Idempotent — a re-run reports what already exists.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button primary label={running ? 'Working…' : plan ? 'Rebuild plan' : 'Build plan'} disabled={running} onClick={call(() => storagePreview(runId))} />
          {running && <Spinner />}
        </Box>
        {error && <Notification status="critical" title="Provisioning step failed" message={error} onClose={() => setError(null)} />}
      </Section>

      {plan?.error && <Notification status="critical" title="Plan could not be built" message={plan.error} />}

      {plan && !plan.error && (
        <Section title={`Plan — ${plan.actions.length} action(s)`}>
          <Table>
            <TableHeader>
              <TableRow>
                <TableCell><Text size="small" weight="bold">Kind</Text></TableCell>
                <TableCell><Text size="small" weight="bold">Name</Text></TableCell>
                <TableCell><Text size="small" weight="bold">What</Text></TableCell>
                <TableCell><Text size="small" weight="bold">State</Text></TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {plan.actions.map((a, i) => (
                <TableRow key={i}>
                  <TableCell><Text size="small">{a.kind}</Text></TableCell>
                  <TableCell><Text size="small">{a.name}</Text></TableCell>
                  <TableCell><Text size="small">{a.description}</Text></TableCell>
                  <TableCell><Tag size="small" value={a.exists ? 'exists' : 'create'} border={{ color: a.exists ? 'border' : 'brand' }} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {plan.notes.map((n, i) => <Text key={i} size="small" color="status-warning">• {n}</Text>)}
          <CheckBox
            label="I reviewed this plan and authorise creating these objects on the array."
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          <Button label={running ? 'Creating…' : 'Apply — create on array'} primary disabled={!confirmed || running} onClick={call(() => storageApply(runId))} alignSelf="start" />
        </Section>
      )}

      {result && (
        <Section title="Result">
          {result.error && <Notification status="critical" title="Provisioning reported an error" message={result.error} />}
          {result.outcomes.map((o, i) => (
            <Text key={i} size="small">
              <b>{o.kind}</b> {o.name} — {o.status}{o.detail ? ` (${o.detail})` : ''}
            </Text>
          ))}
          <Button label="Continue →" primary onClick={onDone} alignSelf="start" />
        </Section>
      )}

      <Section title="Path verification (tier-2) — is the exported LUN actually live?">
        <Text size="small" color="text-weak">
          Reads showvlun -a (read-only) and reports, per host, whether the LUN is live and over how many
          fabrics. Report-only — a "no path" host is fine (the export activates once the host is on +
          zoned); it never blocks provisioning.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button label={running ? 'Working…' : 'Check paths'} disabled={running} onClick={call(() => verifyPaths(runId))} />
          {running && <Spinner />}
        </Box>
        {paths?.error && <Notification status="critical" title="Path check failed" message={paths.error} />}
        {paths && !paths.error && paths.hosts.map((h) => (
          <Box key={h.host} direction="row" gap="small" align="center" pad={{ vertical: 'xxsmall' }}>
            <Box width="240px" flex={false}><Text size="small">{h.host}</Text></Box>
            <Box width="90px" flex={false}><Tag size="small" value={h.verdict} border={{ color: VERDICT_COLOR[h.verdict] }} /></Box>
            <Text size="small" color="text-weak">{h.detail}</Text>
          </Box>
        ))}
        {paths && !paths.error && paths.hosts.length === 0 && <Text size="small" color="text-weak">No target hosts to verify.</Text>}
        {paths?.notes.map((n, i) => <Text key={i} size="small" color="text-weak">• {n}</Text>)}
      </Section>

      <Section title="Activity"><EventLog events={events.filter((e) => e.phase === 'STORAGE_PROVISION')} /></Section>
    </Box>
  );
}
