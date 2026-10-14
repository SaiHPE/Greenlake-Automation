import { Box, Button, CheckBox, DataTable, Text } from 'grommet';
import { Connect } from 'grommet-icons';
import { useState } from 'react';
import {
  GroupVerdict,
  GroupVerification,
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
  RTT_LIMIT_MS,
  RunEvent,
  RunRecord,
} from '../api';
import { CodeBlock, EmptyState, Guidance, Panel, PartsBar, Section, StatusLine } from '../ui/blocks';
import { InlineNotification, NotesList } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

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
const OUTCOME_KIND: Record<ReplicationOutcome['kind'], string> = {
  ...KIND_LABEL,
  volume_admit: 'Volume admitted',
  start: 'Group started',
  policy: 'Policies and period',
};
const OUTCOME: Record<ReplicationOutcome['status'], { state: StepState; label: string }> = {
  created: { state: 'complete', label: 'Done' },
  exists: { state: 'not_started', label: 'Existed' },
  failed: { state: 'failed', label: 'Failed' },
  skipped: { state: 'not_started', label: 'Skipped' },
};
const VERDICT: Record<GroupVerdict, { state: StepState; label: string }> = {
  replicating: { state: 'complete', label: 'Replicating' },
  syncing: { state: 'running', label: 'Initial sync in progress' },
  not_replicating: { state: 'failed', label: 'Not replicating' },
};
const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;

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
 *  `removevvset` ("Set … is currently admitted to Remote Copy Group"); after A's dismiss/remove it goes. */
function RemovalSets({ result, runId, a, b }: { result: ReplicationResult; runId: string; a: string; b: string }) {
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
            Undoes exactly what this apply created, in dependency order: on A each group is stopped, its volumes dismissed
            (which removes the secondaries on B), then removed; then B’s peer volume sets — the array usually removes
            them with the group, so those lines may answer “does not exist”. Objects that already existed are not touched.
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
      {result.notes.length > 0 && <NotesList notes={result.notes} />}
    </Box>
  );
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
  const targets = partnership.targets ?? [];
  const byMode = partnership.target_by_mode ?? {};
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
  const limits = check.modes.map((m) => `${m} needs ${RTT_LIMIT_MS[m]} ms or less`).join(' · ');
  return (
    <Box gap="small" flex={false}>
      {check.error ? (
        <InlineNotification tone="critical" title="The link could not be measured" message={check.error} />
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
              <Text size="small" color={(r.pings_lost_pct ?? 0) > 0 ? 'status-warning' : 'text-weak'}>
                {r.pings_lost_pct === null ? '—' : `${r.pings_lost_pct} %`}
              </Text>
            ) },
            { property: 'detail', header: 'Detail', render: (r: LinkCheckResult) => <Text size="small" color="text-weak">{r.detail || '—'}</Text> },
          ]}
          data={check.results.map((r, i) => ({ ...r, key: i }))}
          primaryKey="key"
          a11yTitle="Link latency: one row per Remote Copy link, with the measured latency and pings lost"
        />
      )}
      {check.unchecked.length > 0 && <InlineNotification tone="info" title="Not checked" message={<NotesList notes={check.unchecked} />} />}
      <Text size="xsmall" color="text-weak">
        Measured {check.at.replace('T', ' ').slice(0, 19)} UTC with a {check.duration_s} s test, stopped after the latency phase. The full throughput test is
        the operator’s to run from Open terminal.
      </Text>
    </Box>
  );
}

export function ReplicationStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  const [showCalls, setShowCalls] = useState(false);
  const [authorised, setAuthorised] = useState(false);
  const [acceptLatency, setAcceptLatency] = useState(false);
  const running = run?.status === 'running';

  const report = latest<ReplicationReport>(events, ['replication.previewed', 'replication.preview.failed'], 'report');
  const plan = latest<ReplicationPlan>(events, ['replication.previewed', 'replication.preview.failed'], 'plan');
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
  const everApplied = events.some((e) => e.event_type === 'replication.applied');
  const blocked = !!plan && plan.blockers.length > 0;
  const count = (state: ReplicationActionState) => (plan ? plan.actions.filter((a) => a.state === state).length : 0);
  const toCreate = count('create');
  const existing = count('exists');
  const conflicts = count('conflict');
  const calls = plan ? [...plan.actions.flatMap((a) => a.calls)].sort((x, y) => x.seq - y.seq) : [];
  const existingGroups: RcGroup[] = report ? report.primary.groups.filter((g) => plan?.existing_groups.includes(g.name)) : [];
  const aName = report?.primary.name || 'array A';
  const bName = report?.peer.name || 'array B';
  const rcip = !!report?.partnership;
  const measured = !!linkCheck && !linkCheck.error && linkCheck.results.some((r) => r.status === 'measured');
  const worstMs = measured ? Math.max(...linkCheck!.results.filter((r) => r.latency_ms !== null).map((r) => r.latency_ms as number)) : null;
  const overLimit = worstMs !== null && linkCheck ? linkCheck.modes.filter((m) => worstMs > (RTT_LIMIT_MS[m] ?? 0)) : [];
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
  const at = !report || plan?.error ? 0 : result ? 4 : rcip && !measured && canApply ? 1 : 2;
  const partFailed = !!plan?.error || (!!result?.error) || (blocked && !result);
  const linkIsPrimary = at === 1;

  const read: FooterAction = { label: report ? 'Read both arrays again' : 'Read both arrays', busy: running, onClick: call(() => replicationPreview(runId)) };
  const checkLink: FooterAction = { label: linkCheck ? 'Check the link again' : 'Check the link', busy: linkRunning, onClick: call(() => replicationLinkCheck(runId)) };
  const verify: FooterAction = { label: verification ? 'Verify again' : 'Verify replication', busy: running, onClick: call(() => replicationVerify(runId)) };
  const skip: FooterAction = { label: everApplied ? next : `${next} without configuring replication`, onClick: onDone };
  const configure: FooterAction = {
    label: 'Configure replication',
    busy: running,
    onClick: call(() => replicationApply(runId, acceptLatency)),
    blocked:
      rcip && !measured
        ? 'Check the link first: HPE asks for the latency between the arrays before Remote Copy over RCIP.'
        : rcip && overLimit.length > 0 && !acceptLatency
          ? `The measured latency is ${worstMs} ms, over HPE's limit for ${overLimit.join(' and ')}. Tick Continue anyway in the Link panel to accept it.`
          : undefined,
  };

  let primary: FooterAction;
  let buttons: FooterAction[];
  if (!report || plan?.error) {
    primary = read;
    buttons = [skip];
  } else if (result) {
    primary = verification ? { label: next, onClick: onDone } : verify;
    buttons = verification ? [verify, read] : [read, skip];
  } else if (linkIsPrimary) {
    primary = checkLink;
    buttons = [read, skip];
  } else if (canApply) {
    primary = configure;
    buttons = [read, ...(rcip ? [checkLink] : []), skip];
  } else if (blocked) {
    primary = read;
    buttons = [skip];
  } else {
    // nothing left to create: the plan's groups already exist
    primary = { label: next, onClick: onDone };
    buttons = [verify, read];
  }

  return (
    <StepShell
      title="Replication"
      description="Remote Copy of this run's volume sets to the peer array, over the partnership the two arrays already have. Nothing is written until you approve the plan."
      stateDetail={
        result
          ? result.error
            ? `stopped after ${result.outcomes.filter((o) => o.status === 'created').length} write(s)`
            : 'replication configured'
          : plan
            ? blocked
              ? `${plan.blockers.length} finding${plan.blockers.length === 1 ? '' : 's'} to resolve`
              : toCreate > 0
                ? 'awaiting approval'
                : 'nothing to create'
            : undefined
      }
      error={error}
      onDismissError={() => setError(null)}
      top={
        <PartsBar
          parts={['Read both arrays', 'Check the link', 'Review the plan', 'Configure', 'Verify']}
          at={at}
          doneAll={replicating}
          failed={partFailed}
          // a blocked plan is reviewed before the link is measured
          notDone={rcip && !measured && !result ? [1] : []}
        />
      }
      primary={primary}
      buttons={buttons}
      // The only replication action that writes to the arrays: an explicit authorisation, not a click.
      confirmation={
        canApply && !linkIsPrimary
          ? { label: `I have reviewed this plan and authorise configuring replication on ${aName} and ${bName}.`, checked: authorised, onChange: setAuthorised }
          : undefined
      }
      guideOpen={!report}
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step does',
              body: 'One Remote Copy group per volume set on the Replication tab, created over WSAPI on this array. The peer creates the secondary volumes on its own CPG.',
            },
            { title: 'Nothing is written until you approve', body: 'Reading, the link check and the plan change nothing. Only Configure replication writes, and only what the plan shows.' },
            { title: "HPE's limits over RCIP", body: 'Round-trip latency: sync 10 ms or less, async 200 ms or less (RCIP = Remote Copy over IP).' },
            {
              title: 'The partnership must exist',
              body: 'RCIP ports, targets and links are set up beforehand; this step reads and checks them. Groups this run did not create are listed and never touched.',
            },
          ]}
        />
      }
    >
      {linkRunning && (
        <StatusLine state="running" title="Checking the link">
          {linkProgress[linkProgress.length - 1] || 'Starting the link check.'}
        </StatusLine>
      )}
      {running && !linkRunning && <StatusLine state="running">Working on the arrays. Each action appears in Activity, below.</StatusLine>}
      {plan?.error && (
        <StatusLine state="failed" title="The arrays could not be read">
          {plan.error}
        </StatusLine>
      )}
      {!running && !report && !plan?.error && (
        <EmptyState icon={<Connect size="large" color="icon-weak" />} title="Not read yet">
          Read both arrays to see the partnership, the links and the groups already there, and what this run would configure. Reading
          changes nothing.
        </EmptyState>
      )}
      {!running && plan && !plan.error && !result && blocked && (
        <StatusLine state="failed" title="The plan cannot be applied yet">
          <NotesList notes={plan.blockers} />
        </StatusLine>
      )}
      {!running && plan && !plan.error && !result && !blocked && toCreate > 0 && (
        rcip && !measured ? (
          <StatusLine state="action_required" title="Check the link before configuring replication">
            HPE&apos;s procedure before Remote Copy over RCIP: measure the latency between the two arrays with checkrclink. The tool runs it
            (server on the peer, client on this array), shows the latency against the limit for the mode on the tab, and stops the test.
            Nothing is configured by the check.
          </StatusLine>
        ) : rcip && overLimit.length > 0 && !acceptLatency ? (
          <StatusLine state="action_required" title={`The measured latency is ${worstMs} ms, over HPE's limit for ${overLimit.join(' and ')}`}>
            {overLimit.map((m) => `${m} replication over RCIP needs ${RTT_LIMIT_MS[m]} ms or less`).join('; ')}. Replication can still be
            configured: tick Continue anyway in the Link panel to accept the measured latency.
          </StatusLine>
        ) : (
          <StatusLine state="action_required" title="Review the plan, then approve configuring replication">
            {toCreate} to create, {existing} already there. No changes have been made to either array. Tick the box next to the green button
            when you have reviewed it.
          </StatusLine>
        )
      )}
      {!running && plan && !plan.error && !result && !blocked && toCreate === 0 && (
        <StatusLine state="complete" title="Nothing to create">
          Every group in the plan is already on the arrays. Verify replication reads them back.
        </StatusLine>
      )}
      {!running && verification && !verification.error && (
        <StatusLine
          state={replicating ? 'complete' : 'action_required'}
          title={
            replicating
              ? 'Replication verified: every group is replicating'
              : `${verification.groups.filter((g) => g.verdict === 'replicating').length} of ${verification.groups.length} group${verification.groups.length === 1 ? '' : 's'} replicating`
          }
        >
          {replicating
            ? 'Both arrays report every group Started, with every volume Synced.'
            : 'An initial sync still running is normal; verify again later. The detail for each group is under Verify replication.'}
        </StatusLine>
      )}
      {!running && result && !(verification && !verification.error && !result.error) && (
        <StatusLine
          state={result.error ? 'failed' : 'complete'}
          title={
            result.error
              ? 'Configuring replication stopped'
              : result.groups_created.length
                ? `${result.groups_created.join(', ')} created and started`
                : 'Nothing new to create'
          }
        >
          {result.error
            ? `${result.error} The writes made before the stop, and the commands to undo them, are below.`
            : `${result.outcomes.filter((o) => o.status === 'exists').length} already existed and were left untouched.${verification ? '' : ' Verify replication reads both arrays back.'}`}
        </StatusLine>
      )}

      {report && !report.error && (
        <Section
          title="What the arrays say"
          summary={
            report.partnership
              ? `${aName} and ${bName} partnered · ${report.partnership.links_primary_up}/${report.partnership.links_primary_total} links up`
              : `No partnership between ${aName} and ${bName}`
          }
          open={!plan}
        >
          <Text size="small" color="text-weak">
            Read over SSH with the sheet&apos;s credentials; nothing was changed.
          </Text>
          <Box direction="row" gap="medium" flex={false} wrap>
            <ArrayCard label="A" view={report.primary} />
            <ArrayCard label="B" view={report.peer} />
          </Box>
          <PartnershipLine partnership={report.partnership} report={report} />
        </Section>
      )}

      {report && !report.error && rcip && result && (
        <Section
          title="Check the link"
          summary={linkCheck ? `Latency ${worstMs} ms${overLimit.length ? `, over the limit for ${overLimit.join(' and ')}` : ', within the limit'}` : 'Not measured'}
        >
          {linkCheck && <LinkLatency check={linkCheck} worstMs={worstMs} overLimit={overLimit} aName={aName} bName={bName} />}
        </Section>
      )}

      {report && !report.error && rcip && !result && (
        <Panel
          title="Check the link"
          description={`checkrclink between the arrays' Remote Copy ports: a test server on ${bName}, a test client on ${aName}, stopped as soon as the latency is printed. No configuration is changed.`}
          right={linkIsPrimary ? undefined : <Button size="small" busy={linkRunning} label={linkCheck ? 'Check again' : 'Check the link'} onClick={call(() => replicationLinkCheck(runId))} />}
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
          {linkCheck && !linkRunning && overLimit.length > 0 && canApply && (
            <CheckBox
              label={`Continue anyway: I accept the measured latency of ${worstMs} ms for ${overLimit.join(' and ')} replication.`}
              checked={acceptLatency}
              disabled={running}
              onChange={(event) => setAcceptLatency(event.target.checked)}
            />
          )}
        </Panel>
      )}

      {plan && !plan.error && (
        <Section
          title={result ? 'The plan that was applied' : 'Review the plan'}
          summary={`${toCreate} to create · ${existing} already there · ${conflicts} conflict${conflicts === 1 ? '' : 's'} · A = ${aName}, B = ${bName}`}
          open={!result}
        >
          {blocked && (
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
                render: (a: ReplicationAction) => (
                  <Text size="small" color={a.state === 'conflict' ? 'status-critical' : 'text-weak'}>
                    {a.reason || '--'}
                  </Text>
                ),
              },
            ]}
            data={plan.actions}
            primaryKey={false}
            a11yTitle="Replication plan: one row per object, with the action apply will take and on which array"
          />
          {plan.notes.length > 0 && <InlineNotification tone="info" title="Plan notes" message={<NotesList notes={plan.notes} />} />}
          {calls.length > 0 && (
            <Box gap="xsmall" flex={false}>
              <Box direction="row" gap="small" align="center">
                <Text size="small" weight={500}>
                  What will be run, in order
                </Text>
                <Button size="small" label={showCalls ? 'Hide the commands' : `Show ${calls.length} command${calls.length === 1 ? '' : 's'}`} onClick={() => setShowCalls((v) => !v)} aria-expanded={showCalls} />
              </Box>
              {showCalls && (
                <CodeBlock
                  label="The commands of the plan, in order"
                  lines={['# Each line is the WSAPI call the tool makes, shown as the array CLI command it is equivalent to.', ...calls.map((c) => `${c.where}  ${c.cli}`)]}
                />
              )}
            </Box>
          )}
        </Section>
      )}

      {result && (
        <Section title="What each array answered" summary={`${result.outcomes.length} writes, in the order they were made, and the commands to undo them`} open={!!result.error}>
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (o: ReplicationOutcome) => <Text size="small">{OUTCOME_KIND[o.kind]}</Text> },
              { property: 'name', header: 'Name', render: (o: ReplicationOutcome) => <Text size="small" style={mono}>{o.name}</Text> },
              { property: 'where', header: 'On', render: (o: ReplicationOutcome) => <Text size="small">{o.where}</Text> },
              { property: 'status', header: 'Result', render: (o: ReplicationOutcome) => <StatusIndicator state={OUTCOME[o.status].state} label={OUTCOME[o.status].label} /> },
              { property: 'detail', header: 'Detail', render: (o: ReplicationOutcome) => <Text size="small" color="text-weak">{o.detail || '--'}</Text> },
            ]}
            data={result.outcomes}
            primaryKey={false}
            a11yTitle="Replication result: one row per write, with what the array reported"
          />
          <RemovalSets result={result} runId={runId} a={aName} b={bName} />
        </Section>
      )}

      {plan && (
        <Section
          title="Verify replication"
          summary={
            verification?.error
              ? 'Could not read the arrays'
              : verification
                ? `${verification.groups.filter((g) => g.verdict === 'replicating').length} of ${verification.groups.length} group${verification.groups.length === 1 ? '' : 's'} replicating`
                : 'Not verified yet. Read-only; a report, never a gate.'
          }
          open={!!verification}
          right={result && !verification ? undefined : <Button size="small" busy={running} label={verification ? 'Verify again' : 'Verify replication'} onClick={call(() => replicationVerify(runId))} />}
        >
          <Text size="small" color="text-weak">
            Reads showrcopy on both arrays and judges each planned group: Started, Primary here and Secondary on the peer, every volume Synced.
            An initial sync still running is reported, not failed.
          </Text>
          {verification?.error && (
            <StatusLine state="failed" title="The arrays could not be read">
              {verification.error}
            </StatusLine>
          )}
          {verification && !verification.error && (
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
          )}
        </Section>
      )}

      {report && existingGroups.length > 0 && (
        <Section
          title={`Replication already on ${report.primary.name || 'array A'}`}
          summary={`${existingGroups.length} group${existingGroups.length === 1 ? '' : 's'} this run did not create; never changed, stopped or removed`}
        >
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
              { property: 'options', header: 'Policies', render: (g: RcGroup) => <Text size="small" color="text-weak">{g.options.length ? g.options.join(', ') : '--'}</Text> },
            ]}
            data={existingGroups}
            primaryKey="name"
            a11yTitle="Remote Copy groups already on the array, with mode, role, status and policies"
          />
        </Section>
      )}
    </StepShell>
  );
}
