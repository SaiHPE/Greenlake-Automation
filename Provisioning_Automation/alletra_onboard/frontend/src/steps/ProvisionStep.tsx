import { Box, Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import {
  ActionOutcome,
  HostPathStatus,
  PathVerdict,
  PathVerification,
  PlannedAction,
  ProvisioningPlan,
  ProvisioningResult,
  RunEvent,
  RunRecord,
  storageApply,
  storagePreview,
  verifyPaths,
} from '../api';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';
import { ProvisioningBuilderView } from './ProvisioningBuilderView';

const VERDICT: Record<PathVerdict, { state: StepState; label: string }> = {
  live: { state: 'complete', label: 'Live' },
  partial: { state: 'action_required', label: 'Partial' },
  no_path: { state: 'not_started', label: 'No path' },
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

export function ProvisionStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';

  const plan = latest<ProvisioningPlan>(events, 'storage.previewed', 'plan');
  const result = latest<ProvisioningResult>(events, 'storage.applied', 'result');
  const paths = latest<PathVerification>(events, 'storage.paths.verified', 'verification');

  const toCreate = plan ? plan.actions.filter((action) => !action.exists).length : 0;
  const existing = plan ? plan.actions.length - toCreate : 0;
  const created = result ? result.outcomes.filter((outcome) => outcome.status === 'created').length : 0;

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
      footerNote="Re-running skips existing objects."
      gate={
        plan && !plan.error && !result
          ? {
              title: 'Review the plan, then approve creation',
              message:
                'No changes have been made to the array. Creation is idempotent — existing objects are skipped.',
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
            <Button primary busy={running} label="Create storage objects" onClick={call(() => storageApply(runId))} />
          )}
          {result && <Button primary label="Continue" onClick={onDone} />}
        </>
      }
    >
      <ProvisioningBuilderView runId={runId} disabled={running} />

      {plan?.error && <InlineNotification tone="critical" title="The plan could not be built" message={plan.error} />}

      {plan && !plan.error && (
        <Surface title="Plan" description="Objects to be created on the array when you approve.">
          <DataTable
            columns={[
              { property: 'kind', header: 'Kind', render: (action: PlannedAction) => <Text size="small">{action.kind}</Text> },
              { property: 'name', header: 'Name', render: (action: PlannedAction) => <Text size="small">{action.name}</Text> },
              {
                property: 'exists',
                header: 'Action',
                render: (action: PlannedAction) => (
                  <StatusIndicator
                    state={action.exists ? 'not_started' : 'complete'}
                    label={action.exists ? 'Exists' : 'Create'}
                  />
                ),
              },
              {
                property: 'description',
                header: 'Detail',
                render: (action: PlannedAction) => (
                  <Text size="small" color="text-weak">
                    {action.description}
                  </Text>
                ),
              },
            ]}
            data={plan.actions}
            primaryKey={false}
          />
          <TableSummary>
            {toCreate} to create · {existing} already exist
          </TableSummary>
          {plan.notes.length > 0 && (
            <InlineNotification tone="info" title="Plan notes" message={plan.notes.join(' · ')} />
          )}
        </Surface>
      )}

      {result && (
        <Surface title="Result">
          {result.error ? (
            <InlineNotification tone="critical" title="Creation reported an error" message={result.error} />
          ) : (
            <InlineNotification
              tone="ok"
              title={`${created} object${created === 1 ? '' : 's'} created`}
              message={`${result.outcomes.length - created} already existed and were left untouched.`}
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
                  <StatusIndicator
                    state={outcome.status === 'created' ? 'complete' : outcome.status === 'failed' ? 'failed' : 'not_started'}
                    label={outcome.status === 'created' ? 'Created' : outcome.status === 'failed' ? 'Failed' : 'Existed'}
                  />
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
