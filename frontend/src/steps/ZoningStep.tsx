import { Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, zoningPlan, zoningPreview, ZoningPlan, ZoningReport } from '../api';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator } from '../ui/status';
import { StepShell } from '../ui/StepShell';
import { ZoningPlanView } from './ZoningPlanView';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

interface HostRow {
  host: string;
  odd: boolean;
  even: boolean;
}

export function ZoningStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';

  const report =
    ([...events]
      .reverse()
      .find((event) => ['zoning.previewed', 'zoning.proper'].includes(event.event_type))?.data?.report as
      | ZoningReport
      | undefined) ?? null;
  const plan =
    ([...events].reverse().find((event) => event.event_type === 'zoning.plan')?.data?.plan as ZoningPlan | undefined) ??
    null;

  // The report carries one row per host and fabric; the operator thinks in hosts, so roll them up.
  const byHost: Record<string, HostRow> = {};
  report?.expected.forEach((zone) => {
    const host = zone.name.replace(/_(odd|even)$/, '');
    byHost[host] = byHost[host] ?? { host, odd: false, even: false };
    byHost[host][zone.fabric] = zone.present;
  });
  const rows = Object.values(byHost);
  const outstanding = rows.filter((row) => !row.odd || !row.even).length;

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <StepShell
      title="SAN zoning"
      description="Verifies zoning as observed by the array and drafts switch commands for the SAN team. This tool never writes to a switch."
      stateDetail={report ? (outstanding ? `${outstanding} host${outstanding === 1 ? '' : 's'} outstanding` : undefined) : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Verify zoning to see what the array can reach."
      footerNote="Provisioning may proceed — exports become active once zoning is applied."
      gate={
        report && !report.proper
          ? {
              title: 'Zoning is incomplete on at least one fabric',
              message:
                'Provide the proposed commands below to the SAN team and re-verify once they have been applied during a maintenance window.',
            }
          : null
      }
      actions={
        <>
          <Button
            busy={running}
            label={report ? 'Re-verify' : 'Verify zoning'}
            onClick={call(() => zoningPreview(runId))}
          />
          <Button busy={running} label={plan ? 'Rebuild plan' : 'Build zoning plan'} onClick={call(() => zoningPlan(runId))} />
          {report && <Button primary label={report.proper ? 'Continue' : 'Proceed anyway'} onClick={onDone} />}
        </>
      }
    >
      {!report && (
        <Surface title="Zoning has not been verified yet">
          <Text size="small" color="text-weak">
            Verification reads the array only — no switch sign-in. A fabric name server is zoning-filtered, so what
            each array port can see is its effective zoning. Every host should be zoned on both fabrics.
          </Text>
        </Surface>
      )}

      {report?.proper && (
        <InlineNotification
          tone="ok"
          title="Zoning is correct on both fabrics"
          message="Verified from the array; no switch sign-in was required."
        />
      )}

      {rows.length > 0 && (
        <Surface title="Zoning observed by the array" description="Each host should be zoned on both fabrics.">
          <DataTable
            columns={[
              { property: 'host', header: 'Host', render: (row: HostRow) => <Text size="small">{row.host}</Text> },
              {
                property: 'odd',
                header: 'Odd fabric (F1)',
                render: (row: HostRow) => (
                  <StatusIndicator state={row.odd ? 'complete' : 'failed'} label={row.odd ? 'Zoned' : 'Not zoned'} />
                ),
              },
              {
                property: 'even',
                header: 'Even fabric (F2)',
                render: (row: HostRow) => (
                  <StatusIndicator state={row.even ? 'complete' : 'failed'} label={row.even ? 'Zoned' : 'Not zoned'} />
                ),
              },
            ]}
            data={rows}
            primaryKey="host"
          />
          <TableSummary>
            {rows.length - outstanding} of {rows.length} hosts zoned on both fabrics
          </TableSummary>
        </Surface>
      )}

      {report && report.unverified_hosts.length > 0 && (
        <InlineNotification
          tone="warning"
          title={`${report.unverified_hosts.length} host${report.unverified_hosts.length === 1 ? '' : 's'} could not be confirmed`}
          message={`The array sees no login for ${report.unverified_hosts.join(', ')}. It cannot distinguish an unzoned host from one that is powered off — confirm the host is online; if it is, this is a genuine zoning gap.`}
        />
      )}

      {report && report.notes.length > 0 && (
        <InlineNotification tone="info" title="Verification notes" message={report.notes.join(' · ')} />
      )}

      {plan && <ZoningPlanView plan={plan} />}
    </StepShell>
  );
}
