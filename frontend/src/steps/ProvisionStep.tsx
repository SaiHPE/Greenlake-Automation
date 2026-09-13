import { Box, Button, CheckBox, DataTable, Text } from 'grommet';
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
  RunEvent,
  RunRecord,
  storageApply,
  storagePreview,
  verifyPaths,
} from '../api';
import { DiscoveryFreshness } from '../ui/discoveryAge';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';
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

  const count = (state: PlanState) => (plan ? plan.actions.filter((action) => action.state === state).length : 0);
  const toCreate = count('create');
  const toUpdate = count('update');
  const existing = count('exists');
  const conflicts = count('conflict');
  const blocked = !!plan && plan.blockers.length > 0;
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

  return (
    <StepShell
      title="Provision storage"
      description="Creates the hosts, host sets, volumes and exports on the array. No writes occur until the plan is approved."
      stateDetail={result ? 'objects created' : plan ? 'awaiting approval' : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Compose the objects below, then build the plan."
      footerNote="Re-running skips objects that already match the plan; an object that exists but differs blocks until it is resolved on the array."
      gate={
        plan && !plan.error && !result
          ? blocked
            ? {
                title: 'The plan has conflicts',
                message:
                  'Something on the array has the same name as an object in this plan but different attributes. Resolve it on the array (or change the plan), then rebuild.',
              }
            : {
                title: 'Review the plan, then approve creation',
                message:
                  'No changes have been made to the array. Objects marked Exists are left alone; Update adds to an existing object without removing anything.',
              }
          : null
      }
      actions={
        <>
          <Button
            busy={running}
            label={plan ? 'Rebuild plan' : 'Build plan'}
            onClick={call(() => storagePreview(runId))}
          />
          {plan && !plan.error && !result && (
            <Button
              busy={running}
              label="Create storage objects"
              disabled={!authorised || blocked}
              onClick={call(() => storageApply(runId))}
            />
          )}
          {/* Continue is always available: an operator may legitimately pass through this step
              without creating anything. */}
          <Button primary label="Continue" onClick={onDone} />
        </>
      }
    >
      {/* The hosts this step creates come from the discovery snapshot, so its age matters here most. */}
      <DiscoveryFreshness events={events} action="creating objects on the array" />

      <ProvisioningBuilderView runId={runId} disabled={running} />

      {plan?.error && <InlineNotification tone="critical" title="The plan could not be built" message={plan.error} />}

      {plan && !plan.error && (
        <Surface title="Plan" description="What approving this plan will do on the array, object by object.">
          {blocked && (
            <InlineNotification
              tone="critical"
              title={`${conflicts} conflict${conflicts === 1 ? '' : 's'} — the plan cannot be applied`}
              message={plan.blockers.join(' · ')}
            />
          )}
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (action: PlannedAction) => <Text size="small">{action.kind}</Text> },
              { property: 'name', header: 'Name', render: (action: PlannedAction) => <Text size="small">{action.name}</Text> },
              {
                property: 'state',
                header: 'Action',
                render: (action: PlannedAction) => (
                  <StatusIndicator state={PLAN_STATE[action.state].state} label={PLAN_STATE[action.state].label} />
                ),
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
          />
          <TableSummary>
            {toCreate} to create · {toUpdate} to update · {existing} already exist · {conflicts} conflict{conflicts === 1 ? '' : 's'}
          </TableSummary>
          {plan.notes.length > 0 && (
            <InlineNotification tone="info" title="Plan notes" message={plan.notes.join(' · ')} />
          )}
          {/* The only action in this tool that writes to a customer array, so it takes an explicit
              authorisation rather than a single click. */}
          {!result && (
            <CheckBox
              label="I have reviewed this plan and authorise creating these objects on the array."
              checked={authorised}
              disabled={running || blocked}
              onChange={(event) => setAuthorised(event.target.checked)}
            />
          )}
        </Surface>
      )}

      {result && (
        <Surface title="Result">
          {result.error ? (
            <InlineNotification tone="critical" title="Creation reported an error" message={result.error} />
          ) : failed > 0 ? (
            <InlineNotification
              tone="critical"
              title={`${failed} export${failed === 1 ? '' : 's'} not found on read-back`}
              message="The array reported the export created, but it is not in the array's export list. Check `showvlun -t` on the array before continuing."
            />
          ) : (
            <InlineNotification
              tone="ok"
              title={`${created} created${updated ? ` · ${updated} updated` : ''}`}
              message={`${result.outcomes.length - created - updated} already existed and were left untouched.`}
            />
          )}
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (outcome: ActionOutcome) => <Text size="small">{outcome.kind}</Text> },
              { property: 'name', header: 'Name', render: (outcome: ActionOutcome) => <Text size="small">{outcome.name}</Text> },
              {
                property: 'status',
                header: 'Result',
                render: (outcome: ActionOutcome) => (
                  <StatusIndicator state={OUTCOME[outcome.status].state} label={OUTCOME[outcome.status].label} />
                ),
              },
              {
                property: 'detail',
                header: 'Detail',
                render: (outcome: ActionOutcome) => (
                  <Text size="small" color="text-weak">
                    {outcome.detail || '—'}
                  </Text>
                ),
              },
            ]}
            data={result.outcomes}
            primaryKey={false}
          />
        </Surface>
      )}

      <Surface
        title="Path verification"
        description="Reads the array back and reports whether each exported LUN is live, and over how many fabrics. Report only — it never gates the run."
        actions={<Button busy={running} label="Verify paths" onClick={call(() => verifyPaths(runId))} />}
      >
        {paths?.error && <InlineNotification tone="critical" title="Path verification failed" message={paths.error} />}
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
                render: (host: HostPathStatus) => (
                  <StatusIndicator state={VERDICT[host.verdict].state} label={VERDICT[host.verdict].label} />
                ),
              },
              {
                property: 'detail',
                header: 'Detail',
                render: (host: HostPathStatus) => (
                  <Text size="small" color="text-weak">
                    {host.detail}
                  </Text>
                ),
              },
            ]}
            data={paths.hosts}
            primaryKey="host"
          />
        )}
        {paths?.notes.length ? (
          <Box flex={false}>
            <Text size="xsmall" color="text-weak">
              {paths.notes.join(' · ')}
            </Text>
          </Box>
        ) : null}
      </Surface>
    </StepShell>
  );
}
