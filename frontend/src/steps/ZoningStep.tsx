import { Button, DataTable, Text } from 'grommet';
import { useEffect, useRef, useState } from 'react';
import {
  RunEvent, RunRecord, zoningPlan, zoningPreview, ZoningPlan, ZoningReport,
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

/** What a re-check changed, in the operator's words: the loop is design → SAN team applies →
 *  re-check → the array shows the new login. Without this the second check looks like the first. */
function describeChange(before: HostRow[], after: HostRow[]): string | null {
  const prev = new Map(before.map((r) => [r.host, r]));
  const gained: string[] = [];
  const lost: string[] = [];
  after.forEach((r) => {
    const p = prev.get(r.host);
    if (!p) { if (r.odd || r.even) gained.push(`${r.host} (new)`); return; }
    const fabrics: string[] = [];
    if (r.odd && !p.odd) fabrics.push('F1');
    if (r.even && !p.even) fabrics.push('F2');
    if (fabrics.length) gained.push(`${r.host} now zoned on ${fabrics.join(' and ')}`);
    const dropped: string[] = [];
    if (!r.odd && p.odd) dropped.push('F1');
    if (!r.even && p.even) dropped.push('F2');
    if (dropped.length) lost.push(`${r.host} no longer seen on ${dropped.join(' and ')}`);
  });
  if (!gained.length && !lost.length) return null;
  return [...gained, ...lost].join(' · ');
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

  // The report carries one row per host and fabric; the operator thinks in hosts, so roll them up.
  const byHost: Record<string, HostRow> = {};
  report?.expected.forEach((zone) => {
    const host = zone.name.replace(/_(odd|even)$/, '');
    byHost[host] = byHost[host] ?? { host, odd: false, even: false };
    byHost[host][zone.fabric] = zone.present;
  });
  const rows = Object.values(byHost);
  const outstanding = rows.filter((row) => !row.odd || !row.even).length;
  const provisionable = report?.zoned_hosts?.length ?? 0;

  // Re-check diff: remember the rows of the previous report (keyed by its event) and say what moved.
  const reportEvent = [...events].reverse().find((event) => ['zoning.previewed', 'zoning.proper'].includes(event.event_type));
  const lastSeen = useRef<{ id: string | undefined; rows: HostRow[] } | null>(null);
  const [change, setChange] = useState<string | null>(null);
  useEffect(() => {
    if (!report) return;
    const id = reportEvent?.event_id;
    if (lastSeen.current && lastSeen.current.id !== id) {
      setChange(describeChange(lastSeen.current.rows, rows));
    }
    if (!lastSeen.current || lastSeen.current.id !== id) lastSeen.current = { id, rows };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportEvent?.event_id]);

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
      description="Reads the array and both Brocade switches (read-only), shows what every host HBA port can reach today, and builds the command set for the zones you select. This tool never writes to a switch: your SAN team applies the commands, then Re-check zoning here — the array shows each new login, and provisioning unlocks per host."
      stateDetail={report ? (outstanding ? `${outstanding} host${outstanding === 1 ? '' : 's'} outstanding` : undefined) : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Check zoning to see what the array can reach, or build the plan to read the switches."
      footerNote="Zoning is a prerequisite, enforced per host: a host is provisioned once this step confirms it logged in on both fabrics. Others are skipped by name and join a later run. Brocade Fabric OS fabrics only."
      gate={
        report && !report.proper
          ? {
              title: provisionable
                ? `${provisionable} host${provisionable === 1 ? '' : 's'} can proceed; the rest will be skipped`
                : 'No host is zoned on both fabrics yet',
              message: provisionable
                ? `Continue to provision ${report.zoned_hosts.join(', ')} now, or complete the missing zones and Re-check zoning first. Hosts that are not ready are excluded from this run by name.`
                : 'Build the plan, select the pairs, name the aliases and give the command set to your SAN team. After they apply and activate it, Re-check zoning.',
            }
          : null
      }
      actions={
        <>
          <Button
            busy={running}
            label={report ? 'Re-check zoning' : 'Check zoning'}
            onClick={call(() => zoningPreview(runId))}
          />
          <Button busy={running} label={plan ? 'Rebuild plan' : 'Build zoning plan'} onClick={call(() => zoningPlan(runId))} />
          {provisionable > 0 && (
            <Button
              primary
              label={`Continue with ${provisionable} zoned host${provisionable === 1 ? '' : 's'}`}
              onClick={onDone}
            />
          )}
        </>
      }
    >
      <DiscoveryFreshness events={events} action="drafting commands for the SAN team" />

      {!report && (
        <Surface title="Zoning has not been checked yet">
          <Text size="small" color="text-weak">
            Check zoning reads the array only — no switch sign-in. A host adapter can log into an array port only
            through an effective zone, so the array's logins are its effective zoning. Build zoning plan additionally
            reads both switches (read-only) to show unzoned hosts and design new zones.
          </Text>
        </Surface>
      )}

      {report?.proper && (
        <InlineNotification
          tone="ok"
          title="Every expected host is zoned on both fabrics"
          message="Confirmed from the array's logins; no switch sign-in was required."
        />
      )}

      {change && (
        <InlineNotification tone="info" title="Since the previous check" message={change} />
      )}

      {rows.length > 0 && (
        <Surface
          title="Provisioning gate — hosts zoned on both fabrics (array view)"
          description="Read from the array's logins. A host is provisioned in this run only when both columns show Zoned."
        >
          <DataTable
            columns={[
              { property: 'host', header: 'Host', render: (row: HostRow) => <Text size="small">{row.host}</Text> },
              {
                property: 'odd',
                header: 'Fabric F1 (odd)',
                render: (row: HostRow) => (
                  <StatusIndicator state={row.odd ? 'complete' : 'failed'} label={row.odd ? 'Zoned' : 'Not zoned'} />
                ),
              },
              {
                property: 'even',
                header: 'Fabric F2 (even)',
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
          title={`${report.unverified_hosts.length} host${report.unverified_hosts.length === 1 ? '' : 's'} not seen by the array`}
          message={`The array has no login from ${report.unverified_hosts.join(', ')}. From the array alone this is either "not zoned" or "powered off" — the zoning plan (which reads the switches) tells them apart.`}
        />
      )}

      {report && report.notes.length > 0 && (
        <InlineNotification tone="info" title="Check notes" message={report.notes.join(' · ')} />
      )}

      {/* Keyed on the plan event: the alias fields are seeded once from the plan, so rebuilding must
          mount a fresh view. Otherwise new WWPNs show an empty alias field while the generated
          commands carry the suggested one — the SAN team would receive names shown nowhere. */}
      {plan && (
        <ZoningPlanView key={planEvent?.event_id} plan={plan} />
      )}
    </StepShell>
  );
}
