import { Box, DataTable, Text } from 'grommet';
import { Connect } from 'grommet-icons';
import { ComponentProps, ReactNode, useEffect, useRef, useState } from 'react';
import {
  EventOf, RunEvent, RunRecord, zoningPlan, zoningPreview,
} from '../api';
import { latestOf } from '../events';
import { DiscoveryFreshness, discoveryReadAt, isDiscoveryStale } from '../ui/discoveryAge';
import { DoneList, EmptyState, Guidance, PartsBar } from '../ui/blocks';
import { TableSummary } from '../ui/primitives';
import { NoValue, RESULT, StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';
import { useStepState } from '../ui/useStepState';
import { ZoningPlanView } from '../ui/ZoningPlanView';

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

type ZoningReport = EventOf<'zoning.previewed'>['data']['report'];

/** The report carries one row per host and fabric; the operator thinks in hosts, so roll them up. */
function reportRows(report: ZoningReport | null): HostRow[] {
  const byHost: Record<string, HostRow> = {};
  report?.expected.forEach((zone) => {
    const host = zone.name.replace(/_(odd|even)$/, '');
    byHost[host] = byHost[host] ?? { host, odd: false, even: false };
    byHost[host][zone.fabric] = zone.present;
  });
  Object.entries(report?.iscsi_hosts ?? {}).forEach(([host, ports]) => {
    byHost[host] = { host, odd: ports.length > 0, even: ports.length > 0, iscsi: ports };
  });
  return Object.values(byHost);
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

// SPEC-030 R7: the parts of this step, in order. The step keeps its one registry entry.
const PARTS = ['Check the array', 'Draft zones', 'Hand off'];

/** The check's detail: one row per host, as the array's logins show it (R9 words). */
function HostTable({ rows, waiting }: { rows: HostRow[]; waiting: boolean }) {
  const outstanding = rows.filter((row) => !row.odd || !row.even).length;
  // while the command set is with the SAN team, a missing zone waits on them (grey), not on the operator
  const notZoned = waiting ? { ...RESULT.not_zoned, state: 'waiting' as const } : RESULT.not_zoned;
  const word = (on: boolean) => (on ? RESULT.zoned : notZoned);
  return (
    <Box gap="small" flex={false}>
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
                <StatusIndicator state={word(row.odd).state} label={word(row.odd).label} />
              ),
          },
          {
            property: 'even',
            header: 'Fabric F2 (even)',
            render: (row: HostRow) =>
              row.iscsi ? (
                row.iscsi.length ? (
                  <Text size="small" color="text-weak">
                    logged in on {row.iscsi.join(', ')}
                  </Text>
                ) : (
                  <NoValue />
                )
              ) : (
                <StatusIndicator state={word(row.even).state} label={word(row.even).label} />
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
    </Box>
  );
}

export function ZoningStep({ runId, run, events, onDone }: Props) {
  const { step, openLog } = useStepContext();
  const { state } = useStepState(step, run, events);
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';

  const reportEvent = latestOf(events, 'zoning.previewed', 'zoning.proper');
  const report = reportEvent?.data?.report ?? null;
  const planEvent = latestOf(events, 'zoning.plan');
  const plan = planEvent?.data?.plan ?? null;

  const rows = reportRows(report);
  const outstanding = rows.filter((row) => !row.odd || !row.even).length;
  const provisionable = report?.zoned_hosts?.length ?? 0;

  // Re-check diff: remember the rows of the previous report (keyed by its event) and say what moved.
  const lastSeen = useRef<{ id: string | undefined; rows: HostRow[] } | null>(null);
  const [change, setChange] = useState<string | null>(null);
  useEffect(() => {
    const current = reportEvent?.data?.report;
    if (!current) return;
    const id = reportEvent.event_id;
    if (lastSeen.current && lastSeen.current.id !== id) {
      const nextRows = reportRows(current);
      setChange(describeChange(lastSeen.current.rows, nextRows));
      lastSeen.current = { id, rows: nextRows };
    } else if (!lastSeen.current) {
      lastSeen.current = { id, rows: reportRows(current) };
    }
  }, [reportEvent]);

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  };

  const waiting = state === 'waiting';
  const renderedAt = [...events].reverse().find((event) => event.event_type === 'zoning.rendered')?.created_at;
  const applyEvent = latestOf(events, 'zoning.applied', 'zoning.apply.failed');
  const applyNewerThanReport =
    !!applyEvent && (!reportEvent || events.indexOf(applyEvent) > events.indexOf(reportEvent));
  const hhmm = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '');
  const check: FooterAction = {
    label: running ? 'Checking' : report ? 'Check zoning again' : 'Check zoning on the array',
    busy: running,
    onClick: call(() => zoningPreview(runId)),
  };
  const build: FooterAction = { label: plan ? 'Rebuild plan' : 'Build zoning plan', busy: running, onClick: call(() => zoningPlan(runId)) };

  // The parts (R7): checking, until a check answers; drafting, until a command set is with the SAN team.
  const at = !report || report.error ? 0 : waiting ? 2 : 1;
  const checkedAt = hhmm(reportEvent?.created_at);

  // One status line (R2): a check that failed, all zoned, waiting on the SAN team, or work to do.
  let status: StepStatus | undefined;
  if (report?.error) {
    status = { state: 'failed', title: 'Zoning could not be checked', message: report.error };
  } else if (applyNewerThanReport && applyEvent.event_type === 'zoning.apply.failed') {
    status = {
      state: 'failed',
      title: 'Switch zoning apply stopped with an error',
      time: hhmm(applyEvent.created_at),
      message: applyEvent.data?.result?.error ?? applyEvent.message,
    };
  } else if (applyNewerThanReport && applyEvent.event_type === 'zoning.applied' && !report?.proper) {
    status = {
      state: 'action_required',
      title: 'Switch zoning applied — check zoning again',
      time: hhmm(applyEvent.created_at),
      message: 'The approved Brocade zones are active on the switches. Click Check zoning again so the array confirms the new host logins.',
    };
  } else if (report?.proper) {
    status = {
      state: 'complete',
      title: 'Every expected host is zoned on both fabrics',
      time: checkedAt,
      message: 'Confirmed from the array\'s logins; no switch login was needed.',
    };
  } else if (report && waiting) {
    status = {
      state: 'waiting',
      title: 'Waiting on the SAN team',
      time: `since ${hhmm(renderedAt)}`,
      message: `The command set was generated at ${hhmm(renderedAt)}. When the SAN team says it is applied, check zoning again: the array shows each new login.${
        provisionable > 0 ? ` ${report.zoned_hosts.join(', ')} can go ahead now.` : ''
      }`,
      links: openLog ? [{ label: 'See the commands', onClick: () => openLog('commands') }] : undefined,
    };
  } else if (report) {
    status = {
      state: 'action_required',
      title: provisionable ? `${provisionable} host${provisionable === 1 ? '' : 's'} can go ahead now` : 'No host is zoned on both fabrics yet',
      time: checkedAt,
      message: provisionable
        ? `Provision ${report.zoned_hosts.join(', ')} now, or finish the missing zones and check zoning again; hosts that are not ready are left out of this run by name.`
        : 'Build the plan, select the pairs, name the aliases and give the command set to your SAN team; after they apply and activate it, check zoning again.',
    };
  }

  // Every other notice is a note (R2); a stale discovery stays a visible warning here (LESSONS 8).
  const stale = isDiscoveryStale(events);
  const readAt = discoveryReadAt(events);
  const notes: ReactNode[] = [];
  if (change) notes.push(`Since the previous check: ${change}`);
  if (report && report.unverified_hosts.length > 0) {
    notes.push(
      `${report.unverified_hosts.length} host${report.unverified_hosts.length === 1 ? '' : 's'} not seen by the array: the array has no login from ${report.unverified_hosts.join(', ')}. From the array alone this is either "not zoned" or "powered off"; the zoning plan (which reads the switches) tells them apart.`,
    );
  }
  if (report) notes.push(...report.notes);
  if (plan) notes.push(...plan.notes);
  if (readAt && !stale) notes.push(`Environment last read ${readAt.toLocaleString()}.`);

  // The finished check, one row (R7); its "again" is in the footer, so the row has none (R3).
  const done: ComponentProps<typeof DoneList>['items'] =
    report && !report.error
      ? [
          {
            text: `Checked the array at ${checkedAt}: ${rows.length} host${rows.length === 1 ? '' : 's'} the array can reach, ${
              rows.length - outstanding
            } of ${rows.length} can be provisioned`,
            detail: rows.length > 0 ? <HostTable rows={rows} waiting={waiting} /> : undefined,
          },
        ]
      : [];

  return (
    <StepShell
      title="SAN zoning"
      description="Which hosts can reach the array, and the commands your SAN team needs for the zones still missing."
      stateLabel={waiting ? 'Waiting on the SAN team' : undefined}
      error={error}
      onDismissError={() => setError(null)}
      top={<PartsBar parts={PARTS} at={report?.proper ? 2 : at} doneAll={!!report?.proper} failed={!!report?.error} />}
      status={status}
      notes={notes}
      staleNotice={stale ? <DiscoveryFreshness events={events} action="drafting commands for the SAN team" /> : undefined}
      buttons={provisionable > 0 ? [check, build] : [build]}
      primary={
        provisionable > 0
          ? { label: `Continue with ${provisionable} zoned host${provisionable === 1 ? '' : 's'}`, onClick: onDone }
          : check
      }
      guidance={
        <Guidance
          items={[
            {
              title: 'How zoning is checked',
              body: "From the array: a host adapter can log in to an array port only through a zone that is in effect, so the array's logins show the zoning in effect. No switch login is needed for the check.",
            },
            {
              title: 'The command set',
              body: 'Build zoning plan reads both switches (read-only), shows the hosts not yet zoned and drafts the zones you select. Copy-paste stays the default for your SAN team; when opted in and approved on screen, the tool can also apply and activate those exact Brocade commands directly.',
            },
            {
              title: 'Per host',
              body: 'A host is provisioned once it is logged in on both fabrics. Hosts not ready are skipped by name and can join a later run. Brocade Fabric OS fabrics only.',
            },
          ]}
        />
      }
    >
      {!report && (
        <EmptyState icon={<Connect size="large" color="icon-weak" />} title="Zoning not checked yet">
          Check zoning reads the array only, with no switch login, and shows which hosts can be provisioned. Build zoning plan also reads both
          switches to show the hosts not yet zoned and draft new zones.
        </EmptyState>
      )}

      {/* Keyed on the plan event: the alias fields are seeded once from the plan, so rebuilding must
          mount a fresh view. Otherwise new WWPNs show an empty alias field while the generated
          commands carry the suggested one; the SAN team would receive names shown nowhere. */}
      {plan ? (
        <ZoningPlanView
          key={planEvent?.event_id}
          plan={plan}
          runId={runId}
          done={done}
          events={events}
          running={running}
          onCheckAgain={call(() => zoningPreview(runId))}
        />
      ) : done.length > 0 && <DoneList items={done} />}
    </StepShell>
  );
}
