import { Box, Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import {
  Partnership,
  RcGroup,
  ReplicationAction,
  ReplicationActionState,
  ReplicationArrayView,
  ReplicationPlan,
  ReplicationReport,
  replicationPreview,
  RunEvent,
  RunRecord,
} from '../api';
import { ContinueButton, InlineNotification, NotesList, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const PLAN_STATE: Record<ReplicationActionState, { state: StepState; label: string }> = {
  create: { state: 'not_started', label: 'Create' },
  exists: { state: 'complete', label: 'Exists' },
  conflict: { state: 'failed', label: 'Conflict' },
};
const KIND_LABEL: Record<ReplicationAction['kind'], string> = {
  group: 'Remote Copy group',
  peer_vvset: 'Peer volume set',
  test_volume: 'Test volume',
  test_vvset: 'Test volume set',
};
const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;

function latest<T>(events: RunEvent[], types: string[], key: string): T | null {
  const event = [...events].reverse().find((item) => types.includes(item.event_type));
  return (event?.data?.[key] as T) ?? null;
}

/** One array as the step read it: identity, Remote Copy status, RCIP ports. */
function ArrayCard({ label, view }: { label: 'A' | 'B'; view: ReplicationArrayView }) {
  const rcState: StepState = view.read_error ? 'failed' : view.rc_status.toLowerCase() === 'started' ? 'complete' : 'action_required';
  return (
    <Box gap="xsmall" flex={false} basis="1/2">
      <Text size="small" weight={600}>
        {label === 'A' ? 'Array A — this run’s array' : 'Array B — the peer'} · {view.name || view.host}
      </Text>
      {view.read_error ? (
        <Text size="small" color="status-critical">{view.read_error}</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            {view.serial} · OS {view.os_version || '?'} · {view.host}
          </Text>
          <StatusIndicator state={rcState} label={`Remote Copy ${view.rc_status || 'unknown'}${view.rc_health ? `, ${view.rc_health}` : ''}`} />
          <Text size="small" color="text-weak">
            RCIP: {view.rcip_ports.length ? view.rcip_ports.map((p) => `${p.nsp} ${p.ip}`).join(' · ') : 'no configured ports'}
          </Text>
          <Text size="small" color="text-weak">
            {view.groups.length} Remote Copy group{view.groups.length === 1 ? '' : 's'} · {Object.keys(view.vvsets).length} volume set{Object.keys(view.vvsets).length === 1 ? '' : 's'}
          </Text>
        </>
      )}
    </Box>
  );
}

function PartnershipLine({ partnership, report }: { partnership: Partnership | null; report: ReplicationReport }) {
  const a = report.primary.name || 'A';
  const b = report.peer.name || 'B';
  if (!partnership) {
    return <StatusIndicator state="failed" label={`No partnership between ${a} and ${b}`} />;
  }
  const ok = partnership.links_primary_up >= 2 && partnership.links_peer_up >= 2;
  return (
    <Box gap="xxsmall" flex={false}>
      <StatusIndicator
        state={ok ? 'complete' : 'action_required'}
        label={`Partnered — ${a} → ${b} ${partnership.links_primary_up}/${partnership.links_primary_total} links Up · ${b} → ${a} ${partnership.links_peer_up}/${partnership.links_peer_total} links Up`}
      />
      <Text size="xsmall" color="text-weak">
        Target on {a}: “{partnership.target_on_primary}” · target on {b}: “{partnership.target_on_peer}” · policy {partnership.mirror_config ? 'mirror_config' : 'no_mirror_config'}.
        Found by link address; target names are not relied on.
      </Text>
    </Box>
  );
}

export function ReplicationStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [showCalls, setShowCalls] = useState(false);
  const running = run?.status === 'running';

  const report = latest<ReplicationReport>(events, ['replication.previewed', 'replication.preview.failed'], 'report');
  const plan = latest<ReplicationPlan>(events, ['replication.previewed', 'replication.preview.failed'], 'plan');
  const blocked = !!plan && plan.blockers.length > 0;
  const count = (state: ReplicationActionState) => (plan ? plan.actions.filter((a) => a.state === state).length : 0);
  const toCreate = count('create');
  const existing = count('exists');
  const conflicts = count('conflict');
  const calls = plan ? [...plan.actions.flatMap((a) => a.calls)].sort((x, y) => x.seq - y.seq) : [];
  const existingGroups: RcGroup[] = report ? report.primary.groups.filter((g) => plan?.existing_groups.includes(g.name)) : [];

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
      title="Replication"
      description="Reads both arrays (read-only), finds the Remote Copy partnership between them, and plans one Remote Copy group per volume set on the Replication tab: created over WSAPI on this array, with the secondary volumes auto-created on the peer’s CPG. Nothing is written until the plan is approved."
      stateDetail={plan ? (blocked ? `${plan.blockers.length} finding${plan.blockers.length === 1 ? '' : 's'} to resolve` : 'awaiting approval') : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Read both arrays to see the partnership and what this run would configure. Nothing is written by the read."
      footerNote="The partnership (RCIP ports, targets, links) has to exist already; this release reads and verifies it. Groups the run did not create are listed and never touched."
      gate={
        plan && !plan.error
          ? blocked
            ? {
                title: 'The plan cannot be applied yet',
                message: <NotesList notes={plan.blockers} />,
              }
            : {
                title: 'Review the plan',
                message:
                  'No changes have been made to either array. Configuring replication from this plan arrives in the next build of this release; the read and the plan are live now so the arrays can be checked.',
              }
          : null
      }
      actions={
        <>
          <Button busy={running} label={report ? 'Read both arrays again' : 'Read both arrays'} onClick={call(() => replicationPreview(runId))} />
          <ContinueButton onClick={onDone} suffix="without configuring replication" />
        </>
      }
    >
      {plan?.error && <InlineNotification tone="critical" title="The arrays could not be read" message={plan.error} />}

      {report && !report.error && (
        <Surface title="What the arrays say" description="Read over SSH with the sheet’s credentials; nothing was changed.">
          <Box direction="row" gap="medium" flex={false} wrap>
            <ArrayCard label="A" view={report.primary} />
            <ArrayCard label="B" view={report.peer} />
          </Box>
          <Box margin={{ top: 'small' }} flex={false}>
            <PartnershipLine partnership={report.partnership} report={report} />
          </Box>
        </Surface>
      )}

      {plan && !plan.error && (
        <Surface title="Plan" description="What approving this plan will do, object by object. A = this array, B = the peer.">
          {blocked && (
            <InlineNotification
              tone="critical"
              title={`${plan.blockers.length} finding${plan.blockers.length === 1 ? '' : 's'} — the plan cannot be applied`}
              message={<NotesList notes={plan.blockers} />}
            />
          )}
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (a: ReplicationAction) => <Text size="small">{KIND_LABEL[a.kind]}</Text> },
              { property: 'name', header: 'Name', render: (a: ReplicationAction) => <Text size="small" style={mono}>{a.name}</Text> },
              { property: 'where', header: 'On', render: (a: ReplicationAction) => <Text size="small">{a.where}</Text> },
              {
                property: 'state',
                header: 'Action',
                render: (a: ReplicationAction) => <StatusIndicator state={PLAN_STATE[a.state].state} label={PLAN_STATE[a.state].label} />,
              },
              {
                property: 'reason',
                header: 'Detail',
                render: (a: ReplicationAction) => (
                  <Text size="small" color={a.state === 'conflict' ? 'status-critical' : 'text-weak'}>{a.reason || '—'}</Text>
                ),
              },
            ]}
            data={plan.actions}
            primaryKey={false}
            a11yTitle="Replication plan: one row per object, with the action apply will take and on which array"
          />
          <TableSummary>
            {toCreate} to create · {existing} already exist · {conflicts} conflict{conflicts === 1 ? '' : 's'}
          </TableSummary>
          {plan.notes.length > 0 && <InlineNotification tone="info" title="Plan notes" message={<NotesList notes={plan.notes} />} />}
          {calls.length > 0 && (
            <Box gap="xsmall" margin={{ top: 'small' }} flex={false}>
              <Box direction="row" gap="small" align="center">
                <Text size="small" weight={600}>What will be run, in order</Text>
                <Button size="small" label={showCalls ? 'Hide' : `Show ${calls.length} command${calls.length === 1 ? '' : 's'}`} onClick={() => setShowCalls((v) => !v)} />
              </Box>
              {showCalls && (
                <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
                  <Text size="xsmall" color="text-weak" style={mono}>
                    # Each line is the WSAPI call the tool makes, shown as the array CLI command it is equivalent to.
                  </Text>
                  {calls.map((c, i) => (
                    <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>
                      {c.where}  {c.cli}
                    </Text>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Surface>
      )}

      {report && existingGroups.length > 0 && (
        <Surface
          title={`Replication already present on ${report.primary.name || 'array A'}`}
          description="Groups this run did not create. Shown so the partnership can be judged by what already works; never modified, stopped or removed."
        >
          <DataTable
            columns={[
              { property: 'name', header: 'Group', render: (g: RcGroup) => <Text size="small" style={mono}>{g.name}</Text> },
              { property: 'mode', header: 'Mode', render: (g: RcGroup) => <Text size="small">{g.mode}</Text> },
              { property: 'role', header: 'Role here', render: (g: RcGroup) => <Text size="small">{g.role}</Text> },
              {
                property: 'status',
                header: 'Status',
                render: (g: RcGroup) => {
                  const synced = g.volumes.filter((v) => v.sync_status === 'Synced').length;
                  const ok = g.status === 'Started' && synced === g.volumes.length;
                  return <StatusIndicator state={ok ? 'complete' : 'action_required'} label={`${g.status} · ${synced}/${g.volumes.length} synced`} />;
                },
              },
              {
                property: 'options',
                header: 'Policies',
                render: (g: RcGroup) => <Text size="small" color="text-weak">{g.options.length ? g.options.join(', ') : '—'}</Text>,
              },
            ]}
            data={existingGroups}
            primaryKey="name"
            a11yTitle="Remote Copy groups already on the array, with mode, role, status and policies"
          />
        </Surface>
      )}
    </StepShell>
  );
}
