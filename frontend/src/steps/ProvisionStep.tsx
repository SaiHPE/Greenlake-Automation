import { Box, Button, DataTable, Text } from 'grommet';
import { Storage as StorageIcon } from 'grommet-icons';
import { ComponentProps, ReactNode, useState } from 'react';
import {
  ActionOutcome,
  HostPathStatus,
  PathVerdict,
  PathVerification,
  PlanState,
  PlannedAction,
  ProvisioningPlan,
  ProvisioningResult,
  RunEvent,
  RunRecord,
  storageApply,
  storagePreview,
  verifyPaths,
} from '../api';
import { isOf, latestOf } from '../events';
import { DoneList, EmptyState, Guidance, Panel, PartsBar, Section, StatusLine } from '../ui/blocks';
import { DiscoveryFreshness, discoveryReadAt, isDiscoveryStale } from '../ui/discoveryAge';
import { InlineNotification, NotesList } from '../ui/primitives';
import { NoValue, RESULT, ResultWord, StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';
import { ProvisioningBuilderView } from '../ui/ProvisioningBuilderView';
import { removalLines, RemovalSet } from '../ui/RemovalSets';

const VERDICT: Record<PathVerdict, ResultWord> = {
  live: RESULT.live,
  partial: RESULT.partial,
  no_path: RESULT.no_path,
};

// What apply will do to each object (SPEC-001 R10). Grey = not there yet; green = there and matches;
// amber = there, apply will add to it; red = there and differs in a way apply cannot fix.
const PLAN_STATE: Record<PlanState, ResultWord> = {
  create: RESULT.create,
  exists: RESULT.already_there,
  update: RESULT.update,
  conflict: RESULT.conflict,
};

const OUTCOME: Record<ActionOutcome['status'], ResultWord> = {
  created: RESULT.created,
  updated: RESULT.updated,
  exists: { ...RESULT.already_there, state: 'not_started' },
  failed: RESULT.failed,
};

/** The plan, one row per object (SPEC-001 R10); `previous` says what moved since the plan before it. */
function PlanTable({ plan, previous }: { plan: ProvisioningPlan; previous: Map<string, PlanState> }) {
  return (
    <DataTable
      columns={[
        { property: 'kind', header: 'Kind', render: (action: PlannedAction) => <Text size="small">{action.kind}</Text> },
        { property: 'name', header: 'Name', render: (action: PlannedAction) => <Text size="small">{action.name}</Text> },
        {
          property: 'state',
          header: 'Action',
          render: (action: PlannedAction) => {
            const was = previous.get(`${action.kind}|${action.name}`);
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
  );
}

/** What the array answered for each object, then the undo for everything this run created. */
function ResultTable({ result }: { result: ProvisioningResult }) {
  return (
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
          render: (outcome: ActionOutcome) =>
            outcome.detail ? (
              <Text size="small" color="text-weak">
                {outcome.detail}
              </Text>
            ) : (
              <NoValue />
            ),
        },
      ]}
      data={result.outcomes}
      primaryKey={false}
      a11yTitle="Provisioning result: one row per object, with what the array reported"
    />
  );
}

/** The path report: per host, the array's view and the ESXi host's own (SPEC-013), and its notes. */
function PathsReport({ paths }: { paths: PathVerification | null }) {
  return (
    <>
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
                  s === 'ok' ? 'Visible' : s === 'degraded' ? 'Degraded' : s === 'absent' ? 'Rescan needed' : s === 'not_read' ? 'Not read' : '';
                return (
                  <Box gap="xxsmall">
                    {label ? <StatusIndicator state={state} label={label} /> : <NoValue />}
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
    </>
  );
}

const pathsSummary = (paths: PathVerification | null) =>
  paths?.error
    ? 'Could not run'
    : paths
      ? `${paths.hosts.length} host${paths.hosts.length === 1 ? '' : 's'} read back`
      : 'Not run yet. A report only; it never gates the run.';

const PARTS = ['Compose', 'Review the plan', 'Create', 'Verify paths'];

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

// SPEC-007 R6: a failed apply carries a result too: what it made before it stopped, and the undo.
const APPLY_EVENTS = ['storage.applied', 'storage.apply.failed'] as const;

/** Index of the newest event of these types, or -1. Used to compare which of two outcomes is current. */
function latestIndex(events: RunEvent[], types: readonly string[]): number {
  for (let i = events.length - 1; i >= 0; i -= 1) if (types.includes(events[i].event_type)) return i;
  return -1;
}

export function ProvisionStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  // The tick belongs to one plan: a rebuilt plan has a new id, so it starts unticked (and the server
  // refuses an apply that does not carry the ticked plan's id).
  const [authorisedFor, setAuthorisedFor] = useState<string | null>(null);
  const running = run?.status === 'running';

  const plan = latestOf(events, 'storage.previewed')?.data?.plan ?? null;
  const planId = plan?.plan_id ?? '';
  const authorised = !!plan && authorisedFor === planId;
  const paths = latestOf(events, 'storage.paths.verified')?.data?.verification ?? null;
  // A result only reflects the plan on screen while it is newer than the newest preview. Rebuilding
  // the plan after a successful apply must offer Create again, not leave the operator with no action.
  const applied = latestIndex(events, APPLY_EVENTS);
  const previewed = latestIndex(events, ['storage.previewed']);
  const resultIsCurrent = applied > previewed;
  const result = resultIsCurrent ? (latestOf(events, ...APPLY_EVENTS)?.data?.result ?? null) : null;
  // An approval is for the plan on screen (LESSONS 6, 7). Derived, not reset after render, so a new
  // plan never shows a frame with the old tick; after an apply only a new plan offers the tick again.
  // Every apply's undo, kept past a rebuild: a retry calls a failed attempt's objects Exists, so its
  // own removal set never names them (SPEC-007 R6).
  const applyResults = events.flatMap((event) =>
    isOf(event, ...APPLY_EVENTS) && event.data?.result ? [event.data.result] : [],
  );
  const allRemovals = applyResults.flatMap((r) => r.removals ?? []);
  const allRemovalNotes = applyResults.flatMap((r) => r.removal_notes ?? []).filter((note, i, all) => all.indexOf(note) === i);

  // SPEC-012 R7 (X-7): the plan before this one, within the run, so a re-plan says what moved.
  const previews = events.filter((event) => isOf(event, 'storage.previewed'));
  const previousPlan = previews.length >= 2 ? (previews[previews.length - 2].data?.plan ?? null) : null;
  const previousState = new Map((previousPlan?.actions ?? []).map((a) => [`${a.kind}|${a.name}`, a.state]));
  // SPEC-012 R2 (P-10): has anything been created in this run at all?
  const everApplied = events.some((event) => event.event_type === 'storage.applied') || allRemovals.length > 0;

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
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  };

  const stopped = !!result?.error;
  const at = !plan || plan.error ? 0 : !result ? 1 : stopped ? 2 : 3;
  const allDone = !!result && !stopped && !!paths && !paths.error;
  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const rebuild = call(() => storagePreview(runId));
  const build: FooterAction = { label: plan ? 'Rebuild plan' : 'Build plan', busy: running, onClick: rebuild };
  const skip: FooterAction = { label: everApplied ? next : `${next} without provisioning`, onClick: onDone };
  const verify: FooterAction = { label: paths ? 'Verify paths again' : 'Verify paths', busy: running, onClick: call(() => verifyPaths(runId)) };
  // The server checks the tick too: it gets the plan's id only when this plan was ticked.
  const create: FooterAction = {
    label: 'Create storage objects',
    busy: running,
    onClick: call(() => storageApply(runId, authorised ? planId : null)),
  };
  // Rebuild plan sits on the plan's panel while that is the part at hand, and on its row once the plan
  // is created; it is in the footer only where it is the one way on: no plan yet, a plan that cannot be
  // applied, or a failed apply (SPEC-030 R4, R7a). One place at a time (R3).
  const reviewing = !!plan && !plan.error && !result && !blocked;

  let primary: FooterAction;
  let buttons: FooterAction[];
  if (stopped) {
    // A new plan reads the array again: what the failed attempt made shows as Already there, the rest as Create.
    primary = build;
    buttons = [skip];
  } else if (result) {
    primary = paths ? { label: next, onClick: onDone } : verify;
    buttons = paths ? [verify] : [skip];
  } else if (reviewing) {
    primary = create;
    buttons = [skip];
  } else {
    primary = build;
    buttons = [skip];
  }

  const hhmm = (types: readonly string[]) => {
    const when = [...events].reverse().find((event) => types.includes(event.event_type))?.created_at;
    return when ? new Date(when).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
  };

  // One status line (SPEC-030 R2): working, a plan that could not be built, what the create answered,
  // a plan that cannot be applied, a plan to approve. Before a plan, the empty state says it.
  let status: StepStatus | undefined;
  if (running) {
    status = { state: 'running', message: 'Working on the array. Each action appears in Activity, below.' };
  } else if (plan?.error) {
    status = { state: 'failed', title: 'The plan could not be built', message: plan.error };
  } else if (result) {
    status = {
      state: result.error || failed > 0 ? 'failed' : 'complete',
      title: result.error
        ? 'Creation reported an error'
        : failed > 0
          ? `${failed} export${failed === 1 ? '' : 's'} not found on read-back`
          : `${created} created${updated ? `, ${updated} updated` : ''}`,
      time: hhmm(APPLY_EVENTS),
      message: result.error
        ? `${result.error.replace(/\.$/, '')}. ${created ? `${created} object${created === 1 ? ' was' : 's were'} created before it stopped; the removal set below undoes them. ` : ''}Fix the cause on the array or in the plan, then rebuild the plan: objects already made will show as Already there.`
        : failed > 0
          ? "The array reported the export created, but it is not in the array's export list. Check `showvlun -t` on the array before continuing."
          : `${result.outcomes.length - created - updated} already existed and were left untouched.${paths ? '' : ' Verify the paths next.'}`,
    };
  } else if (plan && blocked) {
    status = {
      state: 'failed',
      title: conflictRows > 0 ? 'The plan has conflicts' : 'The plan cannot be applied yet',
      time: hhmm(['storage.previewed']),
      message:
        conflictRows > 0
          ? 'Something on the array has the same name as an object in this plan but different attributes. Resolve it on the array (or change the plan), then rebuild.'
          : plan.blockers.join(' '),
    };
  } else if (plan) {
    status = {
      state: 'action_required',
      title: 'Review the plan, then approve creation',
      time: hhmm(['storage.previewed']),
      message: `${toCreate} to create, ${toUpdate} to update, ${existing} already there. No changes have been made to the array. Tick the box next to the green button when you have reviewed it.`,
    };
  }

  // Every other notice is a note (R2); a stale discovery stays a visible warning here (LESSONS 8): the
  // hosts this step creates come from the discovery snapshot.
  const stale = isDiscoveryStale(events);
  const readAt = discoveryReadAt(events);
  const notes: ReactNode[] = [...(plan && !plan.error ? plan.notes : [])];
  if (readAt && !stale) notes.push(`Environment last read ${readAt.toLocaleString()}.`);

  // A create that stopped, or exports the read-back did not find, keep Create the open part (R6, R7a).
  const createOpen = !!result && (stopped || failed > 0);
  const counts = `${toCreate} to create · ${toUpdate} to update · ${existing} already there · ${conflicts} conflict${conflicts === 1 ? '' : 's'}`;

  // Finished parts, one row each (R7).
  const done: ComponentProps<typeof DoneList>['items'] = [];
  if (at >= 1) {
    done.push({
      text: result && !stopped ? 'Composition applied: host set members and exports' : 'Composition: host set members and exports',
      // editable until the objects are created, as before; read-only after (SPEC-004 R4)
      detail: <ProvisioningBuilderView runId={runId} disabled={running} readOnly={!!result && !stopped} bare />,
    });
  }
  if (plan && !plan.error && result) {
    done.push({
      text: `Plan built at ${hhmm(['storage.previewed'])}: ${toCreate} to create, ${toUpdate} to update, ${existing} already there`,
      detail: <PlanTable plan={plan} previous={previousState} />,
      again: stopped ? undefined : { label: 'Rebuild plan', busy: running, onClick: rebuild },
    });
  }
  if (result && !createOpen) {
    done.push({
      text: `What the array answered at ${hhmm(APPLY_EVENTS)}: ${created} created${updated ? `, ${updated} updated` : ''}, ${
        result.outcomes.length - created - updated - failed
      } already there`,
      detail: (
        <>
          <ResultTable result={result} />
          <RemovalSet removals={allRemovals} notes={allRemovalNotes} runId={runId} serial={run?.serial_number} />
        </>
      ),
    });
  }

  return (
    <StepShell
      title="Provision storage"
      description="Creates the hosts, host sets, volumes and exports on the array, only after you approve the plan."
      error={error}
      onDismissError={() => setError(null)}
      top={<PartsBar parts={PARTS} at={at} doneAll={allDone} failed={(blocked && !result) || stopped} />}
      status={status}
      notes={notes}
      staleNotice={stale ? <DiscoveryFreshness events={events} action="creating objects on the array" /> : undefined}
      primary={primary}
      buttons={buttons}
      // The only action in this tool that writes to a customer array, so it takes an explicit
      // authorisation rather than a single click (LESSONS 7).
      confirmation={
        plan && !plan.error && !blocked && !result
          ? {
              label: 'I have reviewed this plan and authorise creating these objects on the array.',
              checked: authorised,
              onChange: (on: boolean) => setAuthorisedFor(on ? planId : null),
            }
          : undefined
      }
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step writes',
              body: 'Only what the plan shows, and only after your tick. Objects marked Already there are left alone; Update adds to an existing object without removing anything.',
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
      {!running && !plan && (
        <EmptyState icon={<StorageIcon size="large" color="icon-weak" />} title="No plan yet">
          Compose the host set members and the exports below, then Build plan to see what will be created, what is already on the array and
          what conflicts. Nothing is created until you approve it.
        </EmptyState>
      )}

      {done.length > 0 && <DoneList items={done} />}

      {at === 0 && (
        <Panel title="Compose">
          <ProvisioningBuilderView runId={runId} disabled={running} bare />
        </Panel>
      )}

      {plan && !plan.error && !result && (
        <Panel
          title="Review the plan"
          right={
            <Box direction="row" gap="small" align="center" wrap>
              <Text size="small" color="text-weak">
                {counts}
              </Text>
              {reviewing && <Button size="small" label="Rebuild plan" busy={running} onClick={rebuild} />}
            </Box>
          }
        >
          {blocked && (
            <InlineNotification
              tone="critical"
              title={`${conflicts} conflict${conflicts === 1 ? '' : 's'}: the plan cannot be applied`}
              message={<NotesList notes={plan.blockers} />}
            />
          )}
          <PlanTable plan={plan} previous={previousState} />
        </Panel>
      )}

      {result && createOpen && (
        <Panel title="Create" description={`What the array answered: ${result.outcomes.length} objects, one row each, and the commands to remove what was created.`}>
          <ResultTable result={result} />
          <RemovalSet removals={allRemovals} notes={allRemovalNotes} runId={runId} serial={run?.serial_number} />
        </Panel>
      )}

      {result && !stopped && (
        <Panel title="Verify paths" right={<Text size="small" color="text-weak">{pathsSummary(paths)}</Text>}>
          <PathsReport paths={paths} />
        </Panel>
      )}

      {!result && allRemovals.length > 0 && (
        <Section title="Undo what this run created" summary={`${removalLines(allRemovals).length} removal command${removalLines(allRemovals).length === 1 ? '' : 's'} from earlier applies in this run`} open={false}>
          <RemovalSet removals={allRemovals} notes={allRemovalNotes} runId={runId} serial={run?.serial_number} />
        </Section>
      )}

      {/* Before a create the path check is a folded report with its own button, as before: it reads what
          is already exported and never gates the run. After a create it is the part at hand, above. */}
      {!(result && !stopped) && (
        <Section
          key={paths ? 'read' : 'not-read'}
          title="Path verification"
          summary={pathsSummary(paths)}
          open={!!paths}
          right={result ? undefined : <Button size="small" busy={running} label={paths ? 'Verify paths again' : 'Verify paths'} onClick={call(() => verifyPaths(runId))} />}
        >
          <PathsReport paths={paths} />
        </Section>
      )}
    </StepShell>
  );
}
