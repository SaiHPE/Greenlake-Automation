import { DataTable, Text } from 'grommet';
import { Connect } from 'grommet-icons';
import { useEffect, useRef, useState } from 'react';
import {
  RunEvent, RunRecord, zoningPlan, zoningPreview, ZoningPlan, ZoningReport,
} from '../api';
import { DiscoveryFreshness } from '../ui/discoveryAge';
import { EmptyState, Guidance, Section, StatusLine } from '../ui/blocks';
import { InlineNotification, NotesList, TableSummary } from '../ui/primitives';
import { StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';
import { useStepState } from '../ui/useStepState';
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
  iscsi?: string[];   // iSCSI-only: the array ports its IQN is logged in on; no zone needed
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
    if (r.iscsi) {
      if (r.odd && !p.odd) gained.push(`${r.host} iSCSI now logged in`);
      if (!r.odd && p.odd) lost.push(`${r.host} iSCSI no longer logged in`);
      return;
    }
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
  const { step } = useStepContext();
  const { state } = useStepState(step, run, events);
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
  Object.entries(report?.iscsi_hosts ?? {}).forEach(([host, ports]) => {
    byHost[host] = { host, odd: ports.length > 0, even: ports.length > 0, iscsi: ports };
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

  const waiting = state === 'waiting';
  const renderedAt = [...events].reverse().find((event) => event.event_type === 'zoning.rendered')?.created_at;
  const hhmm = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '');
  const check: FooterAction = {
    label: running ? 'Checking' : report ? 'Check zoning again' : 'Check zoning on the array',
    busy: running,
    onClick: call(() => zoningPreview(runId)),
  };
  const build: FooterAction = { label: plan ? 'Rebuild plan' : 'Build zoning plan', busy: running, onClick: call(() => zoningPlan(runId)) };

  return (
    <StepShell
      title="SAN zoning"
      description="Which hosts can reach the array through the fabrics, and the command set for the zones still missing. This tool never writes to a switch."
      stateDetail={report ? (outstanding ? `${outstanding} host${outstanding === 1 ? '' : 's'} outstanding` : undefined) : undefined}
      stateLabel={waiting ? 'Waiting on the SAN team' : undefined}
      error={error}
      onDismissError={() => setError(null)}
      buttons={provisionable > 0 ? [check, build] : [build]}
      primary={
        provisionable > 0
          ? { label: `Continue with ${provisionable} zoned host${provisionable === 1 ? '' : 's'}`, onClick: onDone }
          : check
      }
      guideOpen={!report}
      guidance={
        <Guidance
          items={[
            {
              title: 'How zoning is checked',
              body: "From the array: a host adapter can log in to an array port only through a zone that is in effect, so the array's logins show the zoning in effect. No switch login is needed for the check.",
            },
            {
              title: 'The command set',
              body: 'Build zoning plan also reads both switches (read-only), shows the hosts not yet zoned and drafts the zones you select. Your SAN team pastes the commands; activating the configuration is their call. The tool never writes to a switch.',
            },
            {
              title: 'Per host',
              body: 'A host is provisioned once it is logged in on both fabrics. Hosts not ready are skipped by name and can join a later run. Brocade Fabric OS fabrics only.',
            },
          ]}
        />
      }
    >
      <DiscoveryFreshness events={events} action="drafting commands for the SAN team" />

      {!report && (
        <EmptyState icon={<Connect size="large" color="icon-weak" />} title="Zoning not checked yet">
          Check zoning reads the array only, with no switch login, and shows which hosts can be provisioned. Build zoning plan also reads both
          switches to show the hosts not yet zoned and draft new zones.
        </EmptyState>
      )}

      {report?.error && (
        <StatusLine state="failed" title="Zoning could not be checked">
          {report.error}
        </StatusLine>
      )}
      {report?.proper && (
        <StatusLine state="complete" title="Every expected host is zoned on both fabrics" time={hhmm(reportEvent?.created_at)}>
          Confirmed from the array&apos;s logins; no switch login was needed.
        </StatusLine>
      )}
      {report && !report.proper && !report.error && waiting && (
        <StatusLine state="waiting" title="Waiting on the SAN team" time={`since ${hhmm(renderedAt)}`}>
          The command set was generated at {hhmm(renderedAt)}. When the SAN team says it is applied, Check zoning again: the array shows each new
          login, and the hosts it confirms can be provisioned.
          {provisionable > 0 ? ` ${report.zoned_hosts.join(', ')} can go ahead now.` : ''}
        </StatusLine>
      )}
      {report && !report.proper && !report.error && !waiting && (
        <StatusLine
          state="action_required"
          title={
            provisionable
              ? `${provisionable} host${provisionable === 1 ? '' : 's'} can go ahead; the rest will be skipped`
              : 'No host is zoned on both fabrics yet'
          }
          time={hhmm(reportEvent?.created_at)}
        >
          {provisionable
            ? `Continue to provision ${report.zoned_hosts.join(', ')} now, or finish the missing zones and Check zoning again first. Hosts that are not ready are left out of this run by name.`
            : 'Build the plan, select the pairs, name the aliases and give the command set to your SAN team. After they apply and activate it, Check zoning again.'}
        </StatusLine>
      )}

      {change && <InlineNotification tone="info" title="Since the previous check" message={change} />}

      {rows.length > 0 && (
        <Section
          title={`${rows.length} host${rows.length === 1 ? '' : 's'} the array can reach`}
          summary={`${rows.length - outstanding} of ${rows.length} can be provisioned`}
          open
        >
          <Text size="small" color="text-weak">
            Read from the array&apos;s logins. A Fibre Channel host is provisioned in this run only when both fabric columns show Zoned; an
            iSCSI host needs no zone, only its IQN logged in on the array.
          </Text>
          <DataTable
            columns={[
              { property: 'host', header: 'Host', render: (row: HostRow) => <Text size="small">{row.host}</Text> },
              {
                property: 'odd',
                header: 'Fabric F1 (odd)',
                render: (row: HostRow) =>
                  row.iscsi ? (
                    <StatusIndicator
                      state={row.iscsi.length ? 'complete' : 'failed'}
                      label={row.iscsi.length ? 'iSCSI, no zoning needed' : 'iSCSI, IQN not logged in'}
                    />
                  ) : (
                    <StatusIndicator state={row.odd ? 'complete' : waiting ? 'waiting' : 'failed'} label={row.odd ? 'Zoned' : 'Not zoned'} />
                  ),
              },
              {
                property: 'even',
                header: 'Fabric F2 (even)',
                render: (row: HostRow) =>
                  row.iscsi ? (
                    <Text size="small" color="text-weak">
                      {row.iscsi.length ? `logged in on ${row.iscsi.join(', ')}` : '--'}
                    </Text>
                  ) : (
                    <StatusIndicator state={row.even ? 'complete' : waiting ? 'waiting' : 'failed'} label={row.even ? 'Zoned' : 'Not zoned'} />
                  ),
              },
            ]}
            data={rows}
            primaryKey="host"
            a11yTitle="Zoning check: one row per host with its state on each fabric, or its iSCSI login"
          />
          <TableSummary>
            {rows.length - outstanding} of {rows.length} hosts can be provisioned
          </TableSummary>
        </Section>
      )}

      {report && report.unverified_hosts.length > 0 && (
        <InlineNotification
          tone="warning"
          title={`${report.unverified_hosts.length} host${report.unverified_hosts.length === 1 ? '' : 's'} not seen by the array`}
          message={`The array has no login from ${report.unverified_hosts.join(', ')}. From the array alone this is either "not zoned" or "powered off"; the zoning plan (which reads the switches) tells them apart.`}
        />
      )}

      {report && report.notes.length > 0 && <InlineNotification tone="info" title="Check notes" message={<NotesList notes={report.notes} />} />}

      {/* Keyed on the plan event: the alias fields are seeded once from the plan, so rebuilding must
          mount a fresh view. Otherwise new WWPNs show an empty alias field while the generated
          commands carry the suggested one; the SAN team would receive names shown nowhere. */}
      {plan && <ZoningPlanView key={planEvent?.event_id} plan={plan} runId={runId} />}
    </StepShell>
  );
}
