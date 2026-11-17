import { Box, Button, DataTable, Text } from 'grommet';
import { Connect } from 'grommet-icons';
import { ComponentProps, useEffect, useState } from 'react';
import {
  GroupVerdict,
  GroupVerification,
  isPartnershipResult,
  LinkCheck,
  LinkCheckResult,
  Partnership,
  RcGroup,
  ReplicationAction,
  ReplicationActionState,
  ReplicationArrayView,
  ReplicationOutcome,
  ReplicationPlan,
  ReplicationReport,
  ReplicationResult,
  ReplicationVerification,
  replicationApply,
  replicationLinkCheck,
  replicationPreview,
  replicationVerify,
  rttLimitMs,
  RunEvent,
  RunRecord,
  setsUpPartnership,
  Transport,
  TRANSPORT_WORDS,
} from '../api';
import { CodeBlock, Disclosure, DoneList, EmptyState, Guidance, Panel, PartsBar, Section } from '../ui/blocks';
import { InlineNotification, NotesList } from '../ui/primitives';
import { NoValue, RESULT, ResultWord, StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { Confirmation, FooterAction, StepShell, StepStatus } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const PLAN_STATE: Record<ReplicationActionState, ResultWord> = {
  create: RESULT.create,
  exists: RESULT.already_there,
  conflict: RESULT.conflict,
};
const KIND_LABEL: Record<ReplicationAction['kind'], string> = {
  group: 'Remote Copy group',
  peer_vvset: 'Peer volume set',
  test_volume: 'Test volume',
  test_vvset: 'Test volume set',
  rcip_port: 'Replication port',
  rc_service: 'Remote Copy service',
  target: 'Remote Copy target',
};
const OUTCOME_KIND: Record<ReplicationOutcome['kind'], string> = {
  ...KIND_LABEL,
  volume_admit: 'Volume admitted',
  start: 'Group started',
  policy: 'Policies and period',
  ping: 'Ping between the ports',
  links: 'Links Up',
};
const OUTCOME: Record<ReplicationOutcome['status'], ResultWord> = {
  created: RESULT.created,
  exists: { ...RESULT.already_there, state: 'not_started' },
  failed: RESULT.failed,
  skipped: RESULT.skipped,
};
const VERDICT: Record<GroupVerdict, ResultWord> = {
  replicating: RESULT.replicating,
  syncing: RESULT.syncing,
  not_replicating: RESULT.not_replicating,
};
const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;
const noValue = <NoValue />;
type DoneRow = ComponentProps<typeof DoneList>['items'][number];

function latest<T>(events: RunEvent[], types: string[], key: string): T | null {
  const event = [...events].reverse().find((item) => types.includes(item.event_type));
  return (event?.data?.[key] as T) ?? null;
}

/** Index of the newest event of one of these types, or -1 — to decide which of two artifacts is current. */
function latestIndex(events: RunEvent[], types: string[]): number {
  for (let i = events.length - 1; i >= 0; i -= 1) if (types.includes(events[i].event_type)) return i;
  return -1;
}

function download(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

/** SPEC-007 pattern, two blocks, A then B. Seen live 2026-10-09: while the group exists the peer refuses
 *  `removevvset` ("Set … is currently admitted to Remote Copy Group"); after A's dismiss/remove it goes.
 *  Live 2026-11-03: a Primera peer keeps secondaries in a set, so B also removes them by name. */
/** Every apply's removal lines, newest apply first: a second apply's groups go before the partnership the first
 *  set up (removercopytarget refuses while a group still uses the target). Each line once. */
export function mergedRemovals(results: ReplicationResult[]): { removals_a: string[]; removals_b: string[] } {
  const merge = (pick: (r: ReplicationResult) => string[]) =>
    [...results].reverse().flatMap(pick).filter((line, i, all) => all.indexOf(line) === i);
  return { removals_a: merge((r) => r.removals_a), removals_b: merge((r) => r.removals_b) };
}

function RemovalSets({ result, runId, a, b }: { result: { removals_a: string[]; removals_b: string[] }; runId: string; a: string; b: string }) {
  const [copied, setCopied] = useState(false);
  const blocks: [string, string, string[]][] = [
    [a, 'A', result.removals_a],
    [b, 'B', result.removals_b],
  ];
  const text = [
    `# Removal of what run ${runId.slice(0, 8)} configured for replication — ${new Date().toISOString()}`,
    '# Review before pasting. The tool never runs these. Paste the A block on array A FIRST, then the B block on array B.',
    ...blocks.flatMap(([name, label, lines]) => (lines.length ? [``, `# ---- ${label}: ${name}`, ...lines] : [])),
    '',
  ].join('\n');
  const copy = async () => {
    try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { setCopied(false); }
  };
  const total = result.removals_a.length + result.removals_b.length;
  return (
    <Box gap="xsmall" margin={{ top: 'small' }} flex={false}>
      <Text size="small" weight={500}>Removal command set</Text>
      {total === 0 ? (
        <Text size="small" color="text-weak">Nothing to remove — this apply created nothing.</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            Undoes exactly what this run created, newest first: on A each group is stopped, its volumes dismissed, then
            removed; then the target, Remote Copy and the port addresses the run set up. On B the peer volume sets, the
            secondaries, then B’s target. A line may answer “does not exist” when the array already removed it. Objects that
            already existed are not touched.
          </Text>
          <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
            {blocks.map(([name, label, lines]) =>
              lines.length ? (
                <Box key={label} margin={{ bottom: 'xsmall' }}>
                  <Text size="small" color="text-weak" style={mono}># ---- {label}: {name}</Text>
                  {lines.map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
                </Box>
              ) : null,
            )}
          </Box>
          <Box direction="row" gap="small">
            <Button size="small" label={copied ? 'Copied' : 'Copy removal set'} onClick={copy} />
            <Button size="small" label="Download .txt" onClick={() => download(`removal_replication_${runId.slice(0, 8)}.txt`, text)} />
          </Box>
        </>
      )}
    </Box>
  );
}

/** The outbound links of the array's Fibre Channel targets: its port → the other array's port WWN. */
function fcLinks(view: ReplicationArrayView): string[] {
  const fc = new Set(view.targets.filter((t) => t.type.toUpperCase() === 'FC').map((t) => t.name));
  return view.links.filter((l) => fc.has(l.target)).map((l) => `${l.nsp} → ${l.address}`);
}

/** One array as the step read it: identity, Remote Copy status, the replication ports (RCIP, or the FC links). */
function ArrayCard({ label, view }: { label: 'A' | 'B'; view: ReplicationArrayView }) {
  const rcState: StepState = view.read_error ? 'failed' : view.rc_status.toLowerCase() === 'started' ? 'complete' : 'action_required';
  const fc = fcLinks(view);
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
          {fc.length > 0 && (
            <Text size="small" color="text-weak">
              Fibre Channel: <span style={mono}>{fc.join(' · ')}</span>
            </Text>
          )}
          {(view.rcip_ports.length > 0 || fc.length === 0) && (
            <Text size="small" color="text-weak">
              RCIP: {view.rcip_ports.length ? view.rcip_ports.map((p) => `${p.nsp} ${p.ip}`).join(' · ') : 'no configured ports'}
            </Text>
          )}
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
    return (
      <StatusIndicator
        state="failed"
        label={report.mixed_transports ? `No partnership the tool can use between ${a} and ${b}: targets over IP and over Fibre Channel` : `No partnership between ${a} and ${b}`}
      />
    );
  }
  const ok = partnership.links_primary_up >= 2 && partnership.links_peer_up >= 2;
  const transport: Transport = partnership.transport ?? 'IP';
  const targets = partnership.targets ?? [];
  const byMode = partnership.target_by_mode ?? {};
  return (
    <Box gap="xxsmall" flex={false}>
      <StatusIndicator
        state={ok ? 'complete' : 'action_required'}
        label={`Partnered ${TRANSPORT_WORDS[transport]} — ${a} → ${b} ${partnership.links_primary_up}/${partnership.links_primary_total} links Up · ${b} → ${a} ${partnership.links_peer_up}/${partnership.links_peer_total} links Up`}
      />
      <Text size="xsmall" color="text-weak">
        Target on {a}: “{partnership.target_on_primary}” · target on {b}: “{partnership.target_on_peer}” · policy {partnership.mirror_config ? 'mirror_config' : 'no_mirror_config'}.
        {transport === 'FC' ? 'Over Fibre Channel, found by port WWN' : 'Over RCIP, found by link address'}; target names are not relied on.
      </Text>
      {targets.length > 1 && (
        <Text size="xsmall" color="text-weak">
          {targets.length} targets between the two arrays (one mode per target):{' '}
          {targets.map((t) => `“${t.name}” ${t.links_up}/${t.links_total} Up, ${t.modes.length ? `${t.groups} ${t.modes.join('/')} group(s)` : 'no groups'}`).join(' · ')}.
          {Object.keys(byMode).length > 0 && ` This run: ${Object.entries(byMode).map(([m, n]) => `${m} → “${n}”`).join(', ')}.`}
        </Text>
      )}
    </Box>
  );
}

function LinkLatency({ check, worstMs, overLimit, aName, bName }: {
  check: LinkCheck; worstMs: number | null; overLimit: string[]; aName: string; bName: string;
}) {
  const measured = check.results.filter((r) => r.status === 'measured');
  const limits = check.modes.map((m) => `${m} needs ${rttLimitMs('IP', m)} ms or less`).join(' · ');
  return (
    <Box gap="small" flex={false}>
      {check.error ? (
        <InlineNotification
          tone="critical"
          title={measured.length ? 'The Remote Copy links are down after the check' : 'The link could not be measured'}
          message={check.error}
        />
      ) : worstMs === null ? (
        <InlineNotification tone="critical" title="No link was measured" message={check.results.map((r) => r.detail).filter(Boolean).join(' ') || 'The client printed no latency.'} />
      ) : (
        <StatusIndicator
          state={overLimit.length ? 'action_required' : 'complete'}
          label={`Latency ${worstMs} ms on ${measured.length} link${measured.length === 1 ? '' : 's'} · ${limits} · ${overLimit.length ? `over the limit for ${overLimit.join(' and ')}` : 'within the limit'}`}
        />
      )}
      {check.results.length > 0 && (
        <DataTable
          columns={[
            { property: 'link', header: 'Link', render: (r: LinkCheckResult) => (
              <Text size="small" style={mono}>{aName} {r.pair.nsp_a} ({r.pair.ip_a}) → {bName} {r.pair.nsp_b} ({r.pair.ip_b})</Text>
            ) },
            { property: 'latency', header: 'Latency', render: (r: LinkCheckResult) => (
              r.status === 'measured'
                ? <Text size="small">{r.latency_ms} ms</Text>
                : <StatusIndicator state="failed" label="Not measured" />
            ) },
            { property: 'lost', header: 'Pings lost', render: (r: LinkCheckResult) => (
              r.pings_lost_pct === null ? noValue : (
                <Text size="small" color={r.pings_lost_pct > 0 ? 'status-warning' : 'text-weak'}>{r.pings_lost_pct} %</Text>
              )
            ) },
            { property: 'verdict', header: 'Against the limit', render: (r: LinkCheckResult) => {
              // A check that ended in an error (links Down afterwards) gates the apply whatever the latency.
              if (check.error || r.status !== 'measured' || r.latency_ms === null || !check.modes.length) return noValue;
              const over = check.modes.filter((m) => (r.latency_ms as number) > rttLimitMs('IP', m));
              const label = check.modes.map((m) => `${over.includes(m) ? 'over' : 'within'} ${m} (${rttLimitMs('IP', m)} ms)`).join(', ');
              return <StatusIndicator state={over.length ? 'action_required' : 'complete'} label={label.charAt(0).toUpperCase() + label.slice(1)} />;
            } },
            { property: 'detail', header: 'Detail', render: (r: LinkCheckResult) => (r.detail ? <Text size="small" color="text-weak">{r.detail}</Text> : noValue) },
          ]}
          data={check.results.map((r, i) => ({ ...r, key: i }))}
          primaryKey="key"
          a11yTitle="Link latency: one row per Remote Copy link, with the measured latency, the pings lost and whether the latency is within the limit for each mode"
        />
      )}
      {check.unchecked.length > 0 && <InlineNotification tone="info" title="Not checked" message={<NotesList notes={check.unchecked} />} />}
      {check.notes.length > 0 && <InlineNotification tone="warning" title="Gateway in the test path" message={<NotesList notes={check.notes} />} />}
      <Text size="xsmall" color="text-weak">
        Measured {check.at.replace('T', ' ').slice(0, 19)} UTC with a {check.duration_s} s test, stopped after the latency phase. The full throughput test is
        the operator’s to run from Open terminal.
      </Text>
    </Box>
  );
}

/** Both arrays as the read found them: the array cards and the partnership line. */
function ArraysRead({ report }: { report: ReplicationReport }) {
  return (
    <Box gap="small" flex={false}>
      <Text size="small" color="text-weak">
        Read over SSH with the sheet&apos;s credentials; nothing was changed.
      </Text>
      <Box direction="row" gap="medium" flex={false} wrap>
        <ArrayCard label="A" view={report.primary} />
        <ArrayCard label="B" view={report.peer} />
      </Box>
      <PartnershipLine partnership={report.partnership} report={report} />
    </Box>
  );
}

/** The plan: its findings, one row per object, and the commands it runs behind a toggle. */
function PlanDetail({ plan, notes = [] }: { plan: ReplicationPlan; notes?: string[] }) {
  const calls = [...plan.actions.flatMap((a) => a.calls)].sort((x, y) => x.seq - y.seq);
  return (
    <Box gap="small" flex={false}>
      {plan.blockers.length > 0 && (
        <InlineNotification
          tone="critical"
          title={`${plan.blockers.length} finding${plan.blockers.length === 1 ? '' : 's'}: the plan cannot be applied`}
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
            render: (a: ReplicationAction) =>
              a.state === 'create' ? (
                <Text size="small" weight={500}>Create</Text>
              ) : (
                <StatusIndicator state={PLAN_STATE[a.state].state} label={PLAN_STATE[a.state].label} />
              ),
          },
          {
            property: 'reason',
            header: 'Detail',
            render: (a: ReplicationAction) =>
              a.reason ? (
                <Text size="small" color={a.state === 'conflict' ? 'status-critical' : 'text-weak'}>
                  {a.reason}
                </Text>
              ) : (
                noValue
              ),
          },
        ]}
        data={plan.actions}
        primaryKey={false}
        a11yTitle="Replication plan: one row per object, with the action apply will take and on which array"
      />
      {notes.length > 0 && <InlineNotification tone="info" title="Plan notes" message={<NotesList notes={notes} />} />}
      {calls.length > 0 && (
        <Box gap="xsmall" flex={false}>
          <Text size="small" weight={500}>
            What will be run, in order
          </Text>
          <Disclosure label={`${calls.length} command${calls.length === 1 ? '' : 's'}`}>
            <CodeBlock
              label="The commands of the plan, in order"
              lines={['# Each line is a call the tool makes, shown as the array CLI command it is equivalent to.', ...calls.map((c) => `${c.where}  ${c.cli}`)]}
            />
          </Disclosure>
        </Box>
      )}
    </Box>
  );
}

/** What each array answered, one row per write, and the notes the apply left. */
function ResultTable({ result }: { result: ReplicationResult }) {
  return (
    <Box gap="small" flex={false}>
      <DataTable
        columns={[
          { property: 'kind', header: 'Kind', render: (o: ReplicationOutcome) => <Text size="small">{OUTCOME_KIND[o.kind]}</Text> },
          { property: 'name', header: 'Name', render: (o: ReplicationOutcome) => <Text size="small" style={mono}>{o.name}</Text> },
          { property: 'where', header: 'On', render: (o: ReplicationOutcome) => <Text size="small">{o.where}</Text> },
          { property: 'status', header: 'Result', render: (o: ReplicationOutcome) => <StatusIndicator state={OUTCOME[o.status].state} label={OUTCOME[o.status].label} /> },
          { property: 'detail', header: 'Detail', render: (o: ReplicationOutcome) => (o.detail ? <Text size="small" color="text-weak">{o.detail}</Text> : noValue) },
        ]}
        data={result.outcomes}
        primaryKey={false}
        a11yTitle="Replication result: one row per write, with what the array reported"
      />
      {result.notes.length > 0 && <NotesList notes={result.notes} />}
    </Box>
  );
}

/** The read-back of the planned groups: the links, then one row per group. */
function VerifyTable({ verification }: { verification: ReplicationVerification }) {
  return (
    <Box gap="small" flex={false}>
      <StatusIndicator state={verification.links_ok ? 'complete' : 'action_required'} label={verification.links_detail || 'links'} />
      {verification.groups.length === 0 ? (
        <Text size="small" color="text-weak">
          No group in the plan to verify.
        </Text>
      ) : (
        <DataTable
          columns={[
            {
              property: 'group',
              header: 'Group',
              render: (g: GroupVerification) => (
                <Box>
                  <Text size="small" style={mono}>{g.group}</Text>
                  {g.peer_group && <Text size="xsmall" color="text-weak" style={mono}>{g.peer_group} on the peer</Text>}
                </Box>
              ),
            },
            { property: 'verdict', header: 'Result', render: (g: GroupVerification) => <StatusIndicator state={VERDICT[g.verdict].state} label={VERDICT[g.verdict].label} /> },
            {
              property: 'detail',
              header: 'What the arrays say',
              render: (g: GroupVerification) => (
                <Box>
                  <Text size="small" color="text-weak">{g.detail}</Text>
                  {g.next_step && <Text size="xsmall" color="status-critical">{g.next_step}</Text>}
                </Box>
              ),
            },
          ]}
          data={verification.groups}
          primaryKey="group"
          a11yTitle="Replication verification: one row per group, the verdict and what both arrays report"
        />
      )}
      {verification.notes.length > 0 && <NotesList notes={verification.notes} />}
    </Box>
  );
}

const VERIFY_TEXT =
  'Reads Remote Copy back on both arrays and judges each planned group: Started, Primary here and Secondary on the peer, every volume Synced. An initial sync still running is reported, not failed.';

export function ReplicationStep({ runId, run, events, onDone }: Props) {
  const { nextTitle, openLog } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  // The tick belongs to one plan: a new read has a new id, so it starts unticked.
  const [authorisedFor, setAuthorisedFor] = useState<string | null>(null);
  const [acceptLatency, setAcceptLatency] = useState(false);
  const running = run?.status === 'running';

  const report = latest<ReplicationReport>(events, ['replication.previewed', 'replication.preview.failed'], 'report');
  const plan = latest<ReplicationPlan>(events, ['replication.previewed', 'replication.preview.failed'], 'plan');
  const planId = plan?.plan_id ?? '';
  const authorised = !!plan && authorisedFor === planId;
  // A result reflects the plan on screen only while it is newer than the newest preview: a re-read after
  // an apply must offer Configure again (if anything is left to create), not leave the operator stuck.
  const applied = latestIndex(events, ['replication.applied', 'replication.apply.failed']);
  const previewed = latestIndex(events, ['replication.previewed', 'replication.preview.failed']);
  const result = applied > previewed ? latest<ReplicationResult>(events, ['replication.applied', 'replication.apply.failed'], 'result') : null;
  const verification = latest<ReplicationVerification>(events, ['replication.verified', 'replication.verify.failed'], 'verification');
  // SPEC-020: the measured latency, and the progress lines while the check runs
  const linkCheck = latest<LinkCheck>(events, ['replication.link_checked', 'replication.link_check.failed'], 'link_check');
  const linkStarted = latestIndex(events, ['replication.link_check.started']);
  const linkDone = latestIndex(events, ['replication.link_checked', 'replication.link_check.failed']);
  const linkRunning = running && linkStarted > linkDone;
  const linkProgress = linkRunning ? events.slice(linkStarted + 1).filter((e) => e.event_type === 'phase.progress').map((e) => e.message) : [];
  // SPEC-021: the partnership apply is half the step; Continue only drops the word "without" once groups were configured
  const everApplied = events.some((e) => e.event_type === 'replication.applied' && !isPartnershipResult(e.data?.result as ReplicationResult));
  const partnershipPlan = setsUpPartnership(plan);
  const partnershipDone = !!result && !result.error && isPartnershipResult(result);
  // An approval is for the plan on screen: a new read or an apply spends it.
  useEffect(() => setAuthorisedFor(null), [previewed, applied]);
  const allRemovals = mergedRemovals(events
    .filter((e) => ['replication.applied', 'replication.apply.failed'].includes(e.event_type) && e.data?.result)
    .map((e) => e.data!.result as ReplicationResult));
  const hasRemovals = allRemovals.removals_a.length + allRemovals.removals_b.length > 0;
  const blocked = !!plan && plan.blockers.length > 0;
  const count = (state: ReplicationActionState) => (plan ? plan.actions.filter((a) => a.state === state).length : 0);
  const toCreate = count('create');
  const existing = count('exists');
  const conflicts = count('conflict');
  const existingGroups: RcGroup[] = report ? report.primary.groups.filter((g) => plan?.existing_groups.includes(g.name)) : [];
  const aName = report?.primary.name || 'array A';
  const bName = report?.peer.name || 'array B';
  // The partnership's transport decides how the latency is known: an RCIP pair is measured with the link check,
  // a Fibre Channel pair is held to the round-trip time typed on the Replication tab.
  const transport: Transport = report?.partnership?.transport ?? 'IP';
  const rcip = !!report?.partnership && transport === 'IP';
  const fc = !!report?.partnership && transport === 'FC';
  const measured = !!linkCheck && !linkCheck.error && linkCheck.results.some((r) => r.status === 'measured');
  const worstMs = measured ? Math.max(...linkCheck!.results.filter((r) => r.latency_ms !== null).map((r) => r.latency_ms as number)) : null;
  const overLimit = worstMs !== null && linkCheck ? linkCheck.modes.filter((m) => worstMs > rttLimitMs('IP', m)) : [];
  const typedRtt = report?.rtt_ms ?? null;
  const rttModes = report?.modes?.length ? report.modes : ['async'];
  const typedOver = fc && typedRtt !== null ? rttModes.filter((m) => typedRtt > rttLimitMs('FC', m)) : [];
  const canApply = !!plan && !plan.error && !blocked && toCreate > 0 && !result;

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const replicating = !!verification && !verification.error && verification.groups.length > 0 && verification.groups.every((g) => g.verdict === 'replicating');
  const latencyMissing = canApply && ((rcip && !measured) || (fc && typedRtt === null));
  const at = !report || plan?.error || partnershipDone ? 0 : result ? 4 : latencyMissing ? 1 : 2;
  const partFailed = !!plan?.error || (!!result?.error) || (blocked && !result);
  const linkIsPrimary = at === 1 && rcip;
  const goodRead = !!report && !report.error && !plan?.error;
  // The Verify part is open while it is the one left to act on: after a configure, or when nothing was left to create.
  const verifyActive = (!!result && !partnershipDone) || (!!plan && !plan.error && !blocked && toCreate === 0 && !result);
  const seeCommands = openLog ? [{ label: 'See the commands', onClick: () => openLog('commands') }] : undefined;

  const read: FooterAction = { label: report ? 'Read both arrays again' : 'Read both arrays', busy: running, onClick: call(() => replicationPreview(runId)) };
  const checkLink: FooterAction = { label: linkCheck ? 'Check the link again' : 'Check the link', busy: linkRunning, onClick: call(() => replicationLinkCheck(runId)) };
  const verify: FooterAction = { label: verification ? 'Verify again' : 'Verify replication', busy: running, onClick: call(() => replicationVerify(runId)) };
  const proceed: FooterAction = { label: next, onClick: onDone };
  const skip: FooterAction = { label: everApplied ? next : `${next} without replication`, onClick: onDone };
  const configure: FooterAction = {
    label: partnershipPlan ? 'Set up the partnership' : 'Configure replication',
    busy: running,
    // The server checks the tick too: it gets the plan's id only when this plan was ticked.
    onClick: call(() => replicationApply(runId, authorised ? planId : null, acceptLatency)),
    blocked:
      rcip && !measured
        ? 'Check the link first: HPE asks for the latency between the arrays before Remote Copy over RCIP.'
        : rcip && overLimit.length > 0 && !acceptLatency
          ? `The measured latency is ${worstMs} ms, over HPE's limit for ${overLimit.join(' and ')}. Tick Continue anyway first.`
          : fc && typedRtt === null
            ? 'Type the round-trip time between the arrays on the Replication tab: the tool cannot measure Fibre Channel links yet.'
            : fc && typedOver.length > 0 && !acceptLatency
              ? `The round-trip time typed on the Replication tab is ${typedRtt} ms, over HPE's limit for ${typedOver.join(' and ')} over Fibre Channel. Tick Continue anyway first.`
              : undefined,
  };

  // A finished part's "again" sits on its row, not in the footer (SPEC-030 R4).
  let primary: FooterAction;
  let buttons: FooterAction[];
  if (!report || plan?.error) {
    primary = read;
    buttons = [skip];
  } else if (partnershipDone) {
    primary = read;
    buttons = [skip];
  } else if (result) {
    primary = verification ? proceed : verify;
    buttons = verification ? [] : [skip];
  } else if (linkIsPrimary) {
    primary = checkLink;
    buttons = [skip];
  } else if (canApply) {
    primary = configure;
    buttons = [skip];
  } else if (blocked) {
    primary = read;
    buttons = [skip];
  } else {
    // nothing left to create: the plan's groups already exist
    primary = proceed;
    buttons = verification ? [] : [verify];
  }
  const readInFooter = primary === read;

  // Both ticks sit in the footer: the latency first, then the plan (the only replication action that writes).
  const latencyTick: Confirmation | undefined =
    canApply && rcip && !!linkCheck && !linkRunning && overLimit.length > 0
      ? {
          label: `Continue anyway: I accept the measured latency of ${worstMs} ms for ${overLimit.join(' and ')} replication.`,
          checked: acceptLatency,
          onChange: setAcceptLatency,
        }
      : canApply && fc && typedOver.length > 0
        ? {
            label: `Continue anyway: I accept the typed round-trip time of ${typedRtt} ms for ${typedOver.join(' and ')} replication over Fibre Channel.`,
            checked: acceptLatency,
            onChange: setAcceptLatency,
          }
        : undefined;
  const planTick: Confirmation | undefined =
    canApply && !latencyMissing
      ? {
          label: partnershipPlan
            ? `I have reviewed this plan and authorise setting up the replication ports and the partnership on ${aName} and ${bName}.`
            : `I have reviewed this plan and authorise configuring replication on ${aName} and ${bName}.`,
          checked: authorised,
          onChange: (on: boolean) => setAuthorisedFor(on ? planId : null),
        }
      : undefined;
  const confirmations = [latencyTick, planTick].filter((tick): tick is Confirmation => !!tick);

  // One status line (SPEC-030 R2), the first of these that holds; the others become notes.
  const writes = (status: ReplicationOutcome['status']) => (result ? result.outcomes.filter((o) => o.status === status).length : 0);
  const candidates: (StepStatus | null)[] = running
    ? [
        linkRunning
          ? { state: 'running', title: 'Checking the link', message: linkProgress[linkProgress.length - 1] || 'Starting the link check.' }
          : { state: 'running', message: 'Working on the arrays. Each action appears in Activity, below.' },
        plan?.error ? { state: 'failed', title: 'The arrays could not be read', message: plan.error } : null,
      ]
    : [
        plan?.error ? { state: 'failed', title: 'The arrays could not be read', message: plan.error, links: seeCommands } : null,
        result?.error && !partnershipDone
          ? {
              state: 'failed',
              title: 'Configuring replication stopped',
              message: `${result.error} The writes made before the stop, and the commands to undo them, are below.`,
              links: seeCommands,
            }
          : null,
        verification?.error && verifyActive ? { state: 'failed', title: 'Replication could not be verified', message: verification.error } : null,
        plan && !plan.error && !result && blocked
          ? {
              state: 'failed',
              title: 'The plan cannot be applied yet',
              message: `${plan.blockers.length} finding${plan.blockers.length === 1 ? '' : 's'} to resolve, listed with the plan; then read both arrays again.`,
            }
          : null,
        plan && !plan.error && !result && !blocked && toCreate > 0
          ? rcip && !measured
            ? {
                state: 'action_required',
                title: 'Check the link before configuring replication',
                message: "HPE's procedure before Remote Copy over RCIP is to measure the latency between the two arrays; the check changes nothing.",
              }
            : rcip && overLimit.length > 0 && !acceptLatency
              ? {
                  state: 'action_required',
                  title: `The measured latency is ${worstMs} ms, over HPE's limit for ${overLimit.join(' and ')}`,
                  message: `${overLimit.map((m) => `${m} over RCIP needs ${rttLimitMs('IP', m)} ms or less`).join('; ')}; tick Continue anyway to configure it regardless.`,
                }
              : fc && typedRtt === null
                ? {
                    state: 'action_required',
                    title: 'Type the round-trip time on the Replication tab',
                    message:
                      'The arrays replicate over Fibre Channel, which the tool cannot measure yet: type the round-trip time between the arrays on the Replication tab of the workbook, then start a new run with it.',
                  }
                : fc && typedOver.length > 0 && !acceptLatency
                  ? {
                      state: 'action_required',
                      title: `The typed round-trip time is ${typedRtt} ms, over HPE's limit for ${typedOver.join(' and ')}`,
                      message: `${typedOver.map((m) => `${m} over Fibre Channel needs ${rttLimitMs('FC', m)} ms or less`).join('; ')}; tick Continue anyway to configure it regardless.`,
                    }
                  : {
                      state: 'action_required',
                      title: partnershipPlan ? 'Review the plan, then approve setting up the partnership' : 'Review the plan, then approve configuring replication',
                      message: `${toCreate} to create and ${existing} already there; nothing is changed on either array until you tick the box next to the green button.`,
                    }
          : null,
        partnershipDone
          ? {
              state: 'action_required',
              title: 'Ports and partnership set up',
              message: `${writes('created')} step(s) done and every link is Up, but nothing is replicated yet: read both arrays again to plan the groups, check the link, then configure them.`,
            }
          : null,
        verification && !verification.error
          ? {
              state: replicating ? 'complete' : 'action_required',
              title: replicating
                ? 'Replication verified: every group is replicating'
                : `${verification.groups.filter((g) => g.verdict === 'replicating').length} of ${verification.groups.length} group${verification.groups.length === 1 ? '' : 's'} replicating`,
              message: replicating
                ? 'Both arrays report every group Started, with every volume Synced.'
                : 'An initial sync still running is normal, so verify again later; the detail for each group is under Verify.',
            }
          : null,
        result && !result.error && !partnershipDone && !(verification && !verification.error)
          ? {
              state: 'complete',
              title: result.groups_created.length ? `${result.groups_created.join(', ')} created and started` : 'Nothing new to create',
              message: `${writes('exists')} already existed and were left untouched${verification ? '' : '; Verify replication reads both arrays back'}.`,
            }
          : null,
        plan && !plan.error && !result && !blocked && toCreate === 0
          ? { state: 'complete', title: 'Nothing to create', message: 'Every group in the plan is already on the arrays; Verify replication reads them back.' }
          : null,
      ];
  const [status, ...others] = candidates.filter((line): line is StepStatus => !!line);
  const planCurrent = !!plan && !plan.error && !result && !latencyMissing;
  const notes = [
    ...others.map((line) => [line.title, typeof line.message === 'string' ? line.message : ''].filter(Boolean).join('. ')),
    ...(planCurrent ? plan!.notes : []),
  ];

  // Finished parts, one row each, with the part's own "again" (SPEC-030 R7).
  const rows: DoneRow[] = [];
  if (goodRead) {
    rows.push({
      text: report!.partnership
        ? `Read both arrays: ${aName} and ${bName} partnered ${TRANSPORT_WORDS[transport]} · ${report!.partnership.links_primary_up}/${report!.partnership.links_primary_total} links up`
        : `Read both arrays: no partnership between ${aName} and ${bName}`,
      again: readInFooter ? undefined : { label: read.label, busy: read.busy, onClick: read.onClick! },
      detail: <ArraysRead report={report!} />,
    });
  }
  if (rcip && measured && linkCheck) {
    rows.push({
      text: `Check the link: latency ${worstMs} ms, ${overLimit.length ? `over the limit for ${overLimit.join(' and ')}` : 'within the limit'}`,
      state: overLimit.length ? 'action_required' : 'complete',
      // after a configure the link is not tested again from here, as before
      again: result ? undefined : { label: 'Check the link again', busy: linkRunning, onClick: checkLink.onClick! },
      detail: <LinkLatency check={linkCheck} worstMs={worstMs} overLimit={overLimit} aName={aName} bName={bName} />,
    });
  }
  const rttLabel =
    typedRtt === null
      ? ''
      : `Typed ${typedRtt} ms · ${rttModes.map((m) => `${m} over Fibre Channel needs ${rttLimitMs('FC', m)} ms or less`).join(' · ')} · ${typedOver.length ? `over the limit for ${typedOver.join(' and ')}` : 'within the limit'}`;
  const rttDescription =
    'The link check measures RCIP links only, so it is not offered for a Fibre Channel pair. The tool uses the round-trip time typed on the Replication tab, and the result and the as-built say it was typed, not measured.';
  if (fc && typedRtt !== null) {
    rows.push({
      text: `Round-trip time: typed ${typedRtt} ms, ${typedOver.length ? `over the limit for ${typedOver.join(' and ')}` : 'within the limit'}`,
      state: typedOver.length ? 'action_required' : 'complete',
      detail: (
        <Box gap="small" flex={false}>
          <Text size="small" color="text-weak">
            {rttDescription}
          </Text>
          <StatusIndicator state={typedOver.length ? 'action_required' : 'complete'} label={rttLabel} />
        </Box>
      ),
    });
  }
  if (plan && !plan.error && result) {
    rows.push({
      text: `The plan that was applied: ${toCreate} to create · ${existing} already there · ${conflicts} conflict${conflicts === 1 ? '' : 's'}`,
      detail: <PlanDetail plan={plan} notes={plan.notes} />,
    });
  }
  if (result && !result.error) {
    rows.push({
      text: `${partnershipDone ? 'Ports and partnership set up' : result.groups_created.length ? `${result.groups_created.join(', ')} created and started` : 'Nothing new to create'}: ${result.outcomes.length} write${result.outcomes.length === 1 ? '' : 's'}`,
      detail: (
        <Box gap="small" flex={false}>
          <ResultTable result={result} />
          {hasRemovals && <RemovalSets result={allRemovals} runId={runId} a={aName} b={bName} />}
        </Box>
      ),
    });
  }
  const verifyAgain = { label: verify.label, busy: verify.busy, onClick: verify.onClick! };
  // open while there is something to act on: nothing read back yet after a configure, or a group not replicating
  const verifyOpen = verifyActive && (verification ? !replicating : !!result && !result.error);
  if (verification && !verifyOpen) {
    rows.push({
      text: replicating
        ? 'Replication verified: every group is replicating'
        : verification.error
          ? 'Replication could not be verified'
          : `${verification.groups.filter((g) => g.verdict === 'replicating').length} of ${verification.groups.length} group${verification.groups.length === 1 ? '' : 's'} replicating`,
      state: replicating ? 'complete' : verification.error ? 'failed' : 'action_required',
      again: verifyAgain,
      detail: verification.error ? <Text size="small">{verification.error}</Text> : <VerifyTable verification={verification} />,
    });
  }

  return (
    <StepShell
      title="Replication"
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      notes={notes}
      top={
        <PartsBar
          parts={['Read both arrays', fc ? 'Round-trip time' : 'Check the link', 'Review the plan', 'Configure', 'Verify']}
          at={at}
          doneAll={replicating}
          failed={partFailed}
          // a blocked plan is reviewed before the link is measured; a partnership is planned before there is a link
          notDone={(rcip && !measured && !result) || (fc && typedRtt === null && !result) || (partnershipPlan && !result) ? [1] : []}
        />
      }
      primary={primary}
      buttons={buttons}
      confirmations={confirmations}
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step does',
              body: "Remote Copy of this run's volume sets to the peer array: one Remote Copy group per volume set on the Replication tab, created on this array. The peer creates the secondary volumes on its own CPG.",
            },
            {
              title: 'Nothing is written until you approve',
              body: 'Reading, the link check and the plan change nothing. Only the green button under an approved plan writes, and only what the plan shows.',
            },
            {
              title: "HPE's latency limits",
              body: 'Round-trip latency over RCIP (Remote Copy over IP): sync 10 ms or less, async 200 ms or less. Over Fibre Channel: 10 ms or less for both. The tool measures RCIP links with checkrclink (a test server on the peer, a test client on this array); for a Fibre Channel pair it uses the round-trip time typed on the Replication tab and holds it to the limit.',
            },
            {
              title: 'The partnership',
              body: "When the workbook's Replication network tab names the ports, the ports and the partnership are set up first, as their own plan: the RCIP addresses, Remote Copy started and a target on each array. Then read both arrays again, check the link and configure the groups. Without that tab the partnership must exist, and this step reads and checks it. Groups this run did not create are listed and never touched.",
            },
            { title: 'Verify replication', body: 'Reads showrcopy on both arrays and judges each planned group. It is read-only: a report, never a gate.' },
          ]}
        />
      }
    >
      {!running && !report && !plan?.error && (
        <EmptyState icon={<Connect size="large" color="icon-weak" />} title="Not read yet">
          Read both arrays to see the partnership, the links and the groups already there, and what this run would configure. Reading
          changes nothing.
        </EmptyState>
      )}

      {plan?.error && report && !report.error && (
        <Panel title="Read both arrays">
          <ArraysRead report={report} />
        </Panel>
      )}

      {at === 1 && rcip && (
        <Panel
          title="Check the link"
          description={`Measures the latency between the arrays' Remote Copy ports: a test server on ${bName}, a test client on ${aName}, stopped as soon as the latency is printed. No configuration is changed.`}
        >
          {linkRunning && (
            <Box gap="xxsmall" flex={false}>
              <StatusIndicator state="running" label={linkProgress[linkProgress.length - 1] || 'Starting the link check'} />
              {linkProgress.slice(0, -1).map((line, i) => (
                <Text key={i} size="xsmall" color="text-weak">
                  {line}
                </Text>
              ))}
            </Box>
          )}
          {!linkCheck && !linkRunning && (
            <Text size="small" color="text-weak">
              Not measured yet. About 10 seconds per link.
            </Text>
          )}
          {linkCheck && !linkRunning && <LinkLatency check={linkCheck} worstMs={worstMs} overLimit={overLimit} aName={aName} bName={bName} />}
        </Panel>
      )}

      {at === 1 && fc && (
        <Panel title="Round-trip time" description={rttDescription}>
          <StatusIndicator state="action_required" label="Not typed on the Replication tab" />
        </Panel>
      )}

      {planCurrent && (
        <Panel
          title="Review the plan"
          right={
            <Text size="small" color="text-weak">
              {toCreate} to create · {existing} already there · {conflicts} conflict{conflicts === 1 ? '' : 's'}
            </Text>
          }
          description={`A = ${aName}, B = ${bName}`}
        >
          <PlanDetail plan={plan!} />
        </Panel>
      )}

      {result?.error && !partnershipDone && (
        <Panel title="Configure" description="What each array answered, in the order the writes were made, and the commands to undo them.">
          <ResultTable result={result} />
          {hasRemovals && <RemovalSets result={allRemovals} runId={runId} a={aName} b={bName} />}
        </Panel>
      )}

      {verifyOpen && (
        <Panel title="Verify" right={verification ? <Button size="small" label="Verify again" busy={running} onClick={verify.onClick} /> : undefined}>
          <Text size="small" color="text-weak">
            {VERIFY_TEXT}
          </Text>
          {verification && !verification.error && <VerifyTable verification={verification} />}
        </Panel>
      )}

      {/* finished parts sit under the current part, so its start stays above the fold (SPEC-030 R13) */}
      {rows.length > 0 && <DoneList items={rows} />}

      {rcip && !measured && !linkIsPrimary && (
        <Section
          title="Check the link"
          summary="Not measured"
          right={result ? undefined : <Button size="small" busy={linkRunning} label={linkCheck ? 'Check again' : 'Check the link'} onClick={checkLink.onClick} />}
        >
          {linkCheck ? (
            <LinkLatency check={linkCheck} worstMs={worstMs} overLimit={overLimit} aName={aName} bName={bName} />
          ) : (
            <Text size="small" color="text-weak">
              Not measured yet. About 10 seconds per link.
            </Text>
          )}
        </Section>
      )}

      {fc && typedRtt === null && at !== 1 && (
        <Section title="Round-trip time" summary="Not typed on the Replication tab">
          <Text size="small" color="text-weak">
            {rttDescription}
          </Text>
        </Section>
      )}

      {hasRemovals && !result && (
        <Section title="Removal command set" summary="Every line that undoes what this run configured for replication">
          <RemovalSets result={allRemovals} runId={runId} a={aName} b={bName} />
        </Section>
      )}

      {report && existingGroups.length > 0 && (
        <Section title={`Other groups on ${report.primary.name || 'array A'} (${existingGroups.length}), never touched`}>
          <DataTable
            columns={[
              { property: 'name', header: 'Group', render: (g: RcGroup) => <Text size="small" style={mono}>{g.name}</Text> },
              { property: 'mode', header: 'Mode', render: (g: RcGroup) => <Text size="small">{g.mode}{g.period ? ` · every ${g.period}` : ''}</Text> },
              { property: 'role', header: 'Role here', render: (g: RcGroup) => <Text size="small">{g.role}</Text> },
              {
                property: 'status',
                header: 'Status',
                render: (g: RcGroup) => {
                  const synced = g.volumes.filter((v) => v.sync_status === 'Synced').length;
                  const ok = g.status === 'Started' && synced === g.volumes.length;
                  return <StatusIndicator state={ok ? 'complete' : 'action_required'} label={`${g.status} · ${synced}/${g.volumes.length} synced${g.last_sync ? ` · last sync ${g.last_sync}` : ''}`} />;
                },
              },
              { property: 'options', header: 'Policies', render: (g: RcGroup) => (g.options.length ? <Text size="small" color="text-weak">{g.options.join(', ')}</Text> : noValue) },
            ]}
            data={existingGroups}
            primaryKey="name"
            a11yTitle="Remote Copy groups already on the array, with mode, role, status and policies; this run never changes, stops or removes them"
          />
        </Section>
      )}
    </StepShell>
  );
}
