import { Box, Button, CheckBox, Text } from 'grommet';
import { useState } from 'react';
import {
  applyZoning,
  FabricZoningApplyPlan,
  RunEvent,
  ZoningApplyResult,
} from '../api';
import { isOf } from '../events';
import { Section } from './blocks';
import { InlineNotification, Surface } from './primitives';
import { downloadText } from './RemovalSets';
import { StatusIndicator } from './status';
import { fabricLabel, zoningApprovalLabel, zoningRemovalBlocks, zoningRemovalText } from './zoningApplyHelpers';
import { mono } from './zoningHelpers';

/** Copy + download switch removal set body (rendered inside a Section on Zoning step and Finish page). */
export function SwitchRemovalBody({ results, runId }: { results: ZoningApplyResult[]; runId: string }) {
  const [copied, setCopied] = useState(false);
  const blocks = zoningRemovalBlocks(results);
  if (blocks.length === 0) return null;

  const text = zoningRemovalText(results, runId);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <Box gap="xsmall" flex={false}>
      <Text size="small" color="text-weak">
        Reverses what this run created on each switch, in order. Review before pasting; the tool never runs removal commands.
      </Text>
      <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
        {blocks.map((block, bi) => (
          <Box key={bi} margin={{ bottom: bi < blocks.length - 1 ? 'xsmall' : 'none' }}>
            <Text size="small" color="text-weak" style={mono}>{block.header}</Text>
            {block.lines.map((line, li) => (
              <Text key={li} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{line}</Text>
            ))}
          </Box>
        ))}
      </Box>
      <Box direction="row" gap="small" wrap>
        <Button size="small" label={copied ? 'Copied' : 'Copy removal set'} onClick={copy} />
        <Button size="small" label="Download .txt" onClick={() => downloadText(`zoning_removal_${runId.slice(0, 8)}.txt`, text)} />
      </Box>
    </Box>
  );
}

function SwitchRemovalSet({ results, runId }: { results: ZoningApplyResult[]; runId: string }) {
  const totalLines = zoningRemovalBlocks(results).reduce((sum, b) => sum + b.lines.length, 0);
  if (totalLines === 0) return null;
  return (
    <Section
      title="Switch removal command set"
      summary={`${totalLines} line${totalLines === 1 ? '' : 's'} to undo the aliases and zones created on the switches`}
    >
      <SwitchRemovalBody results={results} runId={runId} />
    </Section>
  );
}

function ApplyResultSummary({
  result,
  runId,
  onCheckAgain,
  running,
}: {
  result: ZoningApplyResult;
  runId: string;
  onCheckAgain?: () => void;
  running: boolean;
}) {
  const failed = Boolean(result.error);
  return (
    <Box gap="small" flex={false}>
      <InlineNotification
        tone={failed ? 'critical' : 'ok'}
        title={failed ? 'Switch zoning apply stopped with an error' : 'Switch zoning applied and verified'}
        message={
          result.error
            ?? 'Every planned zone was confirmed in the effective configuration on read-back. Check zoning again to confirm the host has logged into the array.'
        }
      />
      <Box gap="xsmall">
        {result.fabrics.map((fab) => (
          <Box key={`${fab.fabric}-${fab.switch_host}`} gap="xxsmall" pad={{ bottom: 'xsmall' }} border={{ side: 'bottom', color: 'border' }}>
            <Box direction="row" gap="small" align="center" wrap>
              <StatusIndicator
                state={fab.status === 'applied' ? 'complete' : fab.status === 'failed' ? 'failed' : 'not_started'}
                label={fab.status === 'applied' ? 'Applied and verified' : fab.status === 'failed' ? 'Failed' : 'Skipped'}
              />
              <Text size="small" weight={600}>{fabricLabel(fab.fabric)}</Text>
              <Text size="small" color="text-weak">
                switch <Text size="small" style={mono}>{fab.switch_host}</Text> · cfg <Text size="small" style={mono}>{fab.active_cfg}</Text>
              </Text>
            </Box>
            {fab.verified_zones.length > 0 && (
              <Text size="xsmall" color="text-weak">
                Verified in effective configuration: <Text size="xsmall" style={mono}>{fab.verified_zones.join(', ')}</Text>
              </Text>
            )}
            {fab.missing_zones.length > 0 && (
              <Text size="xsmall" color="status-critical">
                Missing on read-back: <Text size="xsmall" style={mono}>{fab.missing_zones.join(', ')}</Text>
              </Text>
            )}
            {fab.transaction_aborted && (
              <Text size="xsmall" color="text-weak">
                Uncommitted zoning transaction was aborted on the switch before exiting.
              </Text>
            )}
            {fab.error && <Text size="xsmall" color="status-critical">{fab.error}</Text>}
          </Box>
        ))}
      </Box>
      <SwitchRemovalSet results={[result]} runId={runId} />
      {onCheckAgain && (
        <Box direction="row" gap="small" align="center" wrap>
          <Button size="small" primary={!failed} busy={running} label="Check zoning again" onClick={onCheckAgain} />
          <Text size="small" color="text-weak">
            Confirm the host has logged into the array so provisioning can proceed.
          </Text>
        </Box>
      )}
    </Box>
  );
}

interface ZoningApplyViewProps {
  runId: string;
  applyPlanId: string | null;
  applyFabrics: FabricZoningApplyPlan[];
  events: RunEvent[];
  running: boolean;
  onCheckAgain?: () => void;
}

/** Opt-in Brocade switch zoning apply panel rendered beneath the default copy-paste command set. */
export function ZoningApplyView({
  runId,
  applyPlanId,
  applyFabrics,
  events,
  running,
  onCheckAgain,
}: ZoningApplyViewProps) {
  const [approvedForPlan, setApprovedForPlan] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const applyEvents = events.filter((e) => isOf(e, 'zoning.applied', 'zoning.apply.failed'));
  const matchingResult = applyPlanId
    ? [...applyEvents].reverse().find((e) => e.data?.result?.plan_id === applyPlanId)?.data?.result ?? null
    : null;
  const latestResult = matchingResult ?? applyEvents[applyEvents.length - 1]?.data?.result ?? null;

  const lastStartIdx = events.map((e) => e.event_type).lastIndexOf('zoning.apply.started');
  const progressLines = running && lastStartIdx >= 0
    ? events.slice(lastStartIdx + 1).filter((e) => e.event_type === 'phase.progress').map((e) => e.message)
    : [];

  const canApply = Boolean(applyPlanId && applyFabrics.length > 0 && !matchingResult);
  const ticked = Boolean(applyPlanId && approvedForPlan === applyPlanId);

  if (!canApply && !latestResult && progressLines.length === 0) return null;

  const submit = async () => {
    if (!applyPlanId || !ticked) return;
    setSubmitting(true);
    setError(null);
    try {
      await applyZoning(runId, applyPlanId);
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Surface
      title="Apply directly to Brocade switches (optional)"
      description="Applies the aliases and zones above and activates the configuration on the listed Brocade switches without copy-paste. Refuses if another zoning transaction is open, records the removal command set before changing anything, and reads the effective configuration back to verify."
    >
      <Box gap="small">
        {canApply && (
          <>
            <Box gap="xxsmall">
              {applyFabrics.map((fab) => (
                <Text key={`${fab.fabric}-${fab.switch_host}`} size="small">
                  {fabricLabel(fab.fabric)}: switch <Text size="small" style={mono}>{fab.switch_host}</Text> · activate{' '}
                  <Text size="small" style={mono}>{fab.active_cfg}</Text> ({Object.keys(fab.zones).length} zone
                  {Object.keys(fab.zones).length === 1 ? '' : 's'})
                </Text>
              ))}
            </Box>
            <CheckBox
              checked={ticked}
              disabled={running || submitting}
              label={<Text size="small">{zoningApprovalLabel(applyFabrics)}</Text>}
              onChange={(e) => setApprovedForPlan(e.target.checked ? applyPlanId : null)}
            />
            {error && <InlineNotification tone="critical" title="Could not start switch apply" message={error} />}
            <Box direction="row" gap="small" align="center" wrap>
              <Button
                primary
                label={running || submitting ? 'Applying to switches' : 'Apply to switches'}
                busy={running || submitting}
                disabled={!ticked || running || submitting}
                onClick={submit}
              />
              {!ticked && (
                <Text size="small" color="text-weak">
                  Tick the authorisation box above to enable direct switch apply, or hand the copy-paste block above to your SAN team instead.
                </Text>
              )}
            </Box>
          </>
        )}

        {progressLines.length > 0 && (
          <Box gap="xxsmall" background="background-contrast" round="xsmall" pad="small">
            {progressLines.map((line, i) => (
              <Text key={i} size="small">{line}</Text>
            ))}
          </Box>
        )}

        {latestResult && (
          <ApplyResultSummary result={latestResult} runId={runId} onCheckAgain={onCheckAgain} running={running} />
        )}
      </Box>
    </Surface>
  );
}
