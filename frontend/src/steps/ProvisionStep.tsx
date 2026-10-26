import { Box, Button, DataTable, Text } from 'grommet';
import { Storage as StorageIcon } from 'grommet-icons';
import { useState } from 'react';
import {
  ActionOutcome,
  HostPathStatus,
  PathVerdict,
  PathVerification,
  PlanState,
  PlannedAction,
  ProvisioningPlan,
  ProvisioningResult,
  RemovalItem,
  RunEvent,
  RunRecord,
  storageApply,
  storagePreview,
  verifyPaths,
} from '../api';
import { EmptyState, Guidance, Panel, PartsBar, Section, StatusLine } from '../ui/blocks';
import { DiscoveryFreshness } from '../ui/discoveryAge';
import { InlineNotification, NotesList } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';
import { ProvisioningBuilderView } from './ProvisioningBuilderView';

const VERDICT: Record<PathVerdict, { state: StepState; label: string }> = {
  live: { state: 'complete', label: 'Live' },
  partial: { state: 'action_required', label: 'Partial' },
  no_path: { state: 'not_started', label: 'No path' },
};

// What apply will do to each object (SPEC-001 R10). Grey = not there yet; green = there and matches;
// amber = there, apply will add to it; red = there and differs in a way apply cannot fix.
const PLAN_STATE: Record<PlanState, { state: StepState; label: string }> = {
  create: { state: 'not_started', label: 'Create' },
  exists: { state: 'complete', label: 'Exists' },
  update: { state: 'action_required', label: 'Update' },
  conflict: { state: 'failed', label: 'Conflict' },
};

const OUTCOME: Record<ActionOutcome['status'], { state: StepState; label: string }> = {
  created: { state: 'complete', label: 'Created' },
  updated: { state: 'complete', label: 'Updated' },
  exists: { state: 'not_started', label: 'Existed' },
  failed: { state: 'failed', label: 'Failed' },
};

// SPEC-007 R3: exports, then sets, then their members — the order that pastes top to bottom.
const REMOVAL_ORDER: Record<string, number> = { vlun: 0, vvset: 1, volume: 2, hostset: 3, host: 4 };
const removalLines = (items: RemovalItem[]): string[] => {
  const out: string[] = [];
  [...items].sort((a, b) => (REMOVAL_ORDER[a.kind] ?? 9) - (REMOVAL_ORDER[b.kind] ?? 9))
    .forEach((i) => { if (!out.includes(i.command)) out.push(i.command); });
  return out;
};
const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;

function download(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

/** The undo for exactly what this apply created (SPEC-007). Text for the operator; the tool never runs it. */
function RemovalSet({ result, runId, serial }: { result: ProvisioningResult; runId: string; serial?: string }) {
  const [copied, setCopied] = useState(false);
  const lines = removalLines(result.removals ?? []);
  const header = [
    `# Removal of what run ${runId.slice(0, 8)} created on ${serial ?? 'the array'} — ${new Date().toISOString()}`,
    '# Review before pasting. The tool never runs these. Order: exports, VV sets, volumes, host sets, hosts.',
  ];
  const text = [...header, ...lines, ''].join('\n');
  const copy = async () => {
    try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { setCopied(false); }
  };
  return (
    <Box gap="xsmall" margin={{ top: 'small' }}>
      <Text size="small" weight={500}>Removal command set</Text>
      {lines.length === 0 ? (
        <Text size="small" color="text-weak">Nothing to remove: this apply created nothing.</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            Undoes exactly what this apply created, in dependency order. Objects that already existed are not touched.
          </Text>
          <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
            {[...header, ...lines].map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
          </Box>
          <Box direction="row" gap="small">
            <Button size="small" label={copied ? 'Copied' : 'Copy removal set'} onClick={copy} />
            <Button size="small" label="Download .txt" onClick={() => download(`removal_${serial ?? 'array'}_${runId.slice(0, 8)}.txt`, text)} />
          </Box>
        </>
      )}
      {(result.removal_notes ?? []).length > 0 && <NotesList notes={result.removal_notes} />}
    </Box>
  );
}

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

function latest<T>(events: RunEvent[], type: string, key: string): T | null {
  const event = [...events].reverse().find((item) => item.event_type === type);
  return (event?.data?.[key] as T) ?? null;
}

/** Index of the newest event of this type, or -1. Used to compare which of two outcomes is current. */
function latestIndex(events: RunEvent[], type: string): number {
  for (let i = events.length - 1; i >= 0; i -= 1) if (events[i].event_type === type) return i;
  return -1;
}

export function ProvisionStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  const [authorised, setAuthorised] = useState(false);
  const running = run?.status === 'running';

  const plan = latest<ProvisioningPlan>(events, 'storage.previewed', 'plan');
  const paths = latest<PathVerification>(events, 'storage.paths.verified', 'verification');
  // A result only reflects the plan on screen while it is newer than the newest preview. Rebuilding
  // the plan after a successful apply must offer Create again, not leave the operator with no action.
  const applied = latestIndex(events, 'storage.applied');
  const previewed = latestIndex(events, 'storage.previewed');
  const resultIsCurrent = applied > previewed;
  const result = resultIsCurrent ? latest<ProvisioningResult>(events, 'storage.applied', 'result') : null;

  // SPEC-012 R7 (X-7): the plan before this one, within the run, so a re-plan says what moved.
  const previews = events.filter((event) => event.event_type === 'storage.previewed');
  const previousPlan = previews.length >= 2 ? ((previews[previews.length - 2].data?.plan as ProvisioningPlan | undefined) ?? null) : null;
  const previousState = new Map((previousPlan?.actions ?? []).map((a) => [`${a.kind}|${a.name}`, a.state]));
  // SPEC-012 R2 (P-10): has anything been created in this run at all?
  const everApplied = events.some((event) => event.event_type === 'storage.applied');

  const count = (state: PlanState) => (plan ? plan.actions.filter((action) => action.state === state).length : 0);
  const toCreate = count('create');
  const toUpdate = count('update');
  const existing = count('exists');
  const conflicts = count('conflict');
  const blocked = !!plan && plan.blockers.length > 0;
  // P-22 (2026-09-17): an empty host set is a blocker but not a conflict; the banner used to say
  // "same name, different attributes" for it. Conflicts are the rows the plan marked so.
  const conflictRows = plan ? plan.actions.filter((a) => a.state === 'conflict').length : 0;
  const created = result ? result.outcomes.filter((outcome) => outcome.status === 'created').length : 0;
  const updated = result ? result.outcomes.filter((outcome) => outcome.status === 'updated').length : 0;
  const failed = result ? result.outcomes.filter((outcome) => outcome.status === 'failed').length : 0;

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const at = !plan || plan.error ? 0 : !result ? 1 : 3;
  const allDone = !!result && !!paths && !paths.error;
  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const build: FooterAction = { label: plan ? 'Rebuild plan' : 'Build plan', busy: running, onClick: call(() => storagePreview(runId)) };
  const skip: FooterAction = { label: everApplied ? next : `${next} without provisioning`, onClick: onDone };
  const verify: FooterAction = { label: paths ? 'Verify paths again' : 'Verify paths', busy: running, onClick: call(() => verifyPaths(runId)) };
  const create: FooterAction = { label: 'Create storage objects', busy: running, onClick: call(() => storageApply(runId)) };

  let primary: FooterAction;
  let buttons: FooterAction[];
  if (result) {
    primary = paths ? { label: next, onClick: onDone } : verify;
    buttons = paths ? [verify, build] : [build, skip];
  } else if (plan && !plan.error && !blocked) {
    primary = create;
    buttons = [build, skip];
  } else {
    primary = build;
    buttons = [skip];
  }

  return (
    <StepShell
      title="Provision storage"
      description="Creates the hosts, host sets, volumes and exports on the array. Nothing is written until you approve the plan."
      stateDetail={
        result
          ? 'objects created'
          : blocked
            ? `${plan!.blockers.length} blocker${plan!.blockers.length === 1 ? '' : 's'} to resolve`
            : plan
              ? 'awaiting approval'
              : undefined
      }
      error={error}
      onDismissError={() => setError(null)}
      top={<PartsBar parts={['Compose', 'Review the plan', 'Create', 'Verify paths']} at={at} doneAll={allDone} failed={blocked && !result} />}
      primary={primary}
      buttons={buttons}
      // The only action in this tool that writes to a customer array, so it takes an explicit
      // authorisation rather than a single click (LESSONS 7).
      confirmation={
        plan && !plan.error && !blocked && !result
          ? { label: 'I have reviewed this plan and authorise creating these objects on the array.', checked: authorised, onChange: setAuthorised }
          : undefined
      }
      guideOpen={false}
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step writes',
              body: 'Only what the plan shows, and only after your tick. Objects marked Exists are left alone; Update adds to an existing object without removing anything.',
            },
            { title: 'Discovery feeds it', body: 'The hosts it creates come from Discovery. Run Discovery again if hosts, cabling or zoning have changed since.' },
            {
              title: 'If something has the same name',
              body: 'An object on the array with the same name but different attributes is a conflict. The plan cannot be applied until it is resolved on the array or the plan is changed.',
            },
            {
              title: 'Path verification',
              body: "Reads the array back per host: LUNs, HBAs, paths and fabrics. For ESXi hosts also the host's own view from vCenter (a new LUN needs a storage rescan). A report, never a gate.",
            },
          ]}
        />
      }
    >
      {/* The hosts this step creates come from the discovery snapshot, so its age matters here most. */}
      <DiscoveryFreshness events={events} action="creating objects on the array" />

      {running && <StatusLine state="running">Working on the array. Each action appears in Activity, below.</StatusLine>}
      {!running && !plan && (
        <EmptyState icon={<StorageIcon size="large" color="icon-weak" />} title="No plan yet">
          Compose the host set members and the exports below, then Build plan to see what will be created, what is already on the array and
          what conflicts. Nothing is created until you approve it.
        </EmptyState>
      )}
      {plan?.error && (
        <StatusLine state="failed" title="The plan could not be built">
          {plan.error}
        </StatusLine>
      )}
      {!running && plan && !plan.error && !result && blocked && (
        <StatusLine state="failed" title={conflictRows > 0 ? 'The plan has conflicts' : 'The plan cannot be applied yet'}>
          {conflictRows > 0
            ? 'Something on the array has the same name as an object in this plan but different attributes. Resolve it on the array (or change the plan), then rebuild.'
            : plan.blockers.join(' ')}
        </StatusLine>
      )}
      {!running && plan && !plan.error && !result && !blocked && (
        <StatusLine state="action_required" title="Review the plan, then approve creation">
          {toCreate} to create, {toUpdate} to update, {existing} already there. No changes have been made to the array. Tick the box next to the
          green button when you have reviewed it.
        </StatusLine>
      )}
      {!running && result && (
        <StatusLine
          state={result.error || failed > 0 ? 'failed' : 'complete'}
          title={
            result.error
              ? 'Creation reported an error'
              : failed > 0
                ? `${failed} export${failed === 1 ? '' : 's'} not found on read-back`
                : `${created} created${updated ? `, ${updated} updated` : ''}`
          }
        >
          {result.error
            ? result.error
            : failed > 0
              ? "The array reported the export created, but it is not in the array's export list. Check `showvlun -t` on the array before continuing."
              : `${result.outcomes.length - created - updated} already existed and were left untouched.${paths ? '' : ' Verify the paths next.'}`}
        </StatusLine>
      )}

      {/* keyed: Section reads `open` once, so it folds when the plan arrives */}
      <Section key={plan ? 'planned' : 'compose'} title={result ? 'Composition applied' : 'Compose'} summary="Host set members and exports" open={!plan}>
        <ProvisioningBuilderView runId={runId} disabled={running} readOnly={!!result} />
      </Section>

      {plan && !plan.error && !result && (
        <Panel title="Review the plan" right={<Text size="small" color="text-weak">{toCreate} to create · {toUpdate} to update · {existing} already there · {conflicts} conflict{conflicts === 1 ? '' : 's'}</Text>}>
          {blocked && (
            <InlineNotification
              tone="critical"
              title={`${conflicts} conflict${conflicts === 1 ? '' : 's'}: the plan cannot be applied`}
              message={<NotesList notes={plan.blockers} />}
            />
          )}
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (action: PlannedAction) => <Text size="small">{action.kind}</Text> },
              { property: 'name', header: 'Name', render: (action: PlannedAction) => <Text size="small">{action.name}</Text> },
              {
                property: 'state',
                header: 'Action',
                render: (action: PlannedAction) => {
                  const was = previousState.get(`${action.kind}|${action.name}`);
                  return (
                    <Box gap="xxsmall">
                      {action.state === 'create' ? (
                        <Text size="small" weight={500}>Create</Text>
                      ) : (
                        <StatusIndicator state={PLAN_STATE[action.state].state} label={PLAN_STATE[action.state].label} />
                      )}
                      {was && was !== action.state && <Text size="xsmall" color="text-weak">was {PLAN_STATE[was].label.toLowerCase()}</Text>}
                    </Box>
                  );
                },
              },
              {
                property: 'description',
                header: 'Detail',
                render: (action: PlannedAction) => (
                  <Box>
                    <Text size="small" color="text-weak">
                      {action.description}
                    </Text>
                    {action.reason && (
                      <Text size="xsmall" color={action.state === 'conflict' ? 'status-critical' : 'text-weak'}>
                        {action.reason}
                      </Text>
                    )}
                  </Box>
                ),
              },
            ]}
            data={plan.actions}
            primaryKey={false}
            a11yTitle="Provisioning plan: one row per object, with the action apply will take"
          />
          {plan.notes.length > 0 && <InlineNotification tone="info" title="Plan notes" message={<NotesList notes={plan.notes} />} />}
        </Panel>
      )}

      {result && (
        <Section title="What the array answered" summary={`${result.outcomes.length} objects, one row each, and the commands to remove what was created`} open={!!result.error || failed > 0}>
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (outcome: ActionOutcome) => <Text size="small">{outcome.kind}</Text> },
              { property: 'name', header: 'Name', render: (outcome: ActionOutcome) => <Text size="small">{outcome.name}</Text> },
              {
                property: 'status',
                header: 'Result',
                render: (outcome: ActionOutcome) => <StatusIndicator state={OUTCOME[outcome.status].state} label={OUTCOME[outcome.status].label} />,
              },
              {
                property: 'detail',
                header: 'Detail',
                render: (outcome: ActionOutcome) => (
                  <Text size="small" color="text-weak">
                    {outcome.detail || '--'}
                  </Text>
                ),
              },
            ]}
            data={result.outcomes}
            primaryKey={false}
            a11yTitle="Provisioning result: one row per object, with what the array reported"
          />
          <RemovalSet result={result} runId={runId} serial={run?.serial_number} />
        </Section>
      )}

      <Section
        key={paths ? 'read' : 'not-read'}
        title="Path verification"
        summary={
          paths?.error
            ? 'Could not run'
            : paths
              ? `${paths.hosts.length} host${paths.hosts.length === 1 ? '' : 's'} read back`
              : 'Not run yet. A report only; it never gates the run.'
        }
        open={!!paths}
        right={result ? undefined : <Button size="small" busy={running} label={paths ? 'Verify paths again' : 'Verify paths'} onClick={call(() => verifyPaths(runId))} />}
      >
        <Text size="small" color="text-weak">
          Reads the array back and reports, per host: how many LUNs are live, over how many HBAs, how many paths each LUN has, and on which
          fabrics. For ESXi hosts it also reads the host&apos;s own multipath view through vCenter (a new LUN needs a storage rescan before
          ESXi sees it).
        </Text>
        {paths?.error && (
          <StatusLine state="failed" title="Path verification failed">
            {paths.error}
          </StatusLine>
        )}
        {paths && !paths.error && paths.hosts.length === 0 && (
          <Text size="small" color="text-weak">
            No target hosts to verify.
          </Text>
        )}
        {paths && !paths.error && paths.hosts.length > 0 && (
          <DataTable
            columns={[
              { property: 'host', header: 'Host', render: (host: HostPathStatus) => <Text size="small">{host.host}</Text> },
              {
                property: 'verdict',
                header: 'Result',
                render: (host: HostPathStatus) => <StatusIndicator state={VERDICT[host.verdict].state} label={VERDICT[host.verdict].label} />,
              },
              {
                property: 'detail',
                header: 'Array view',
                render: (host: HostPathStatus) => (
                  <Text size="small" color="text-weak">
                    {host.detail}
                  </Text>
                ),
              },
              {
                property: 'esxi_note',
                header: 'ESXi view',
                render: (host: HostPathStatus) => {
                  // SPEC-013: the host's own multipath view; a second opinion, never the verdict.
                  const s = host.esxi_state ?? 'not_checked';
                  const state: StepState =
                    s === 'ok' ? 'complete' : s === 'degraded' || s === 'absent' ? 'action_required' : s === 'not_read' ? 'failed' : 'not_started';
                  const label =
                    s === 'ok' ? 'Visible' : s === 'degraded' ? 'Degraded' : s === 'absent' ? 'Rescan needed' : s === 'not_read' ? 'Not read' : s === 'not_in_vcenter' ? 'n/a' : '--';
                  return (
                    <Box gap="xxsmall">
                      <StatusIndicator state={state} label={label} />
                      {host.esxi_note && (
                        <Text size="xsmall" color="text-weak">
                          {host.esxi_note}
                        </Text>
                      )}
                    </Box>
                  );
                },
              },
            ]}
            data={paths.hosts}
            primaryKey="host"
            a11yTitle="Path verification: one row per host, the array's view and the ESXi host's view"
          />
        )}
        {paths?.notes.length ? (
          <Box flex={false}>
            <Text size="xsmall" color="text-weak">
              <NotesList notes={paths.notes} />
            </Text>
          </Box>
        ) : null}
      </Section>
    </StepShell>
  );
}
