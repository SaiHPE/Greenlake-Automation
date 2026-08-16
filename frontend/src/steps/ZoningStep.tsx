import { Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import {
  RunEvent, RunRecord, zoningPlan, zoningPreview, ZoningPlan, ZoningReport, ZoningStageResult,
} from '../api';
import { DiscoveryFreshness } from '../ui/discoveryAge';
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
  const planEvent = [...events].reverse().find((event) => event.event_type === 'zoning.plan');
  const plan = (planEvent?.data?.plan as ZoningPlan | undefined) ?? null;
  const stageEvent = [...events]
    .reverse()
    .find((event) => ['zoning.staged', 'zoning.stage.failed'].includes(event.event_type));
  const stageResult = (stageEvent?.data?.result as ZoningStageResult | undefined) ?? null;
  const staged = stageEvent?.event_type === 'zoning.staged';

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
      description="Verifies zoning as observed by the array, and stages operator-selected zones into the switches' defined configuration. Activation (cfgenable) is always a manual SAN-team action; existing zones are never modified."
      stateDetail={report ? (outstanding ? `${outstanding} host${outstanding === 1 ? '' : 's'} outstanding` : undefined) : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Verify zoning to see what the array can reach."
      footerNote="Zoning is a prerequisite: provisioning will not create exports until zoning is verified complete or the planned zones are staged."
      gate={
        report && !report.proper && !staged
          ? {
              title: 'Zoning is incomplete on at least one fabric',
              message:
                'Build the plan, select the pairs and stage them (defined configuration only), or hand the command preview to the SAN team — then re-verify. Provisioning stays locked until zoning is complete or staged.',
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
          {(report?.proper || staged) && <Button primary label="Continue" onClick={onDone} />}
        </>
      }
    >
      <DiscoveryFreshness events={events} action="drafting commands for the SAN team" />

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

      {/* Keyed on the plan event: the alias fields are seeded once from the plan, so rebuilding must
          mount a fresh view. Otherwise new WWPNs show an empty alias field while the generated
          commands carry the suggested one — the SAN team would receive names shown nowhere. */}
      {plan && (
        <ZoningPlanView
          key={planEvent?.event_id}
          plan={plan}
          runId={runId}
          running={running}
          stageResult={stageResult}
        />
      )}
    </StepShell>
  );
}
