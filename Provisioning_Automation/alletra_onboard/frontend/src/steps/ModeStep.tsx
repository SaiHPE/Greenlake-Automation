import { Box, Button, CheckBox, Text } from 'grommet';
import { Radial, RadialSelected } from 'grommet-icons';
import { useState } from 'react';
import { ActionKey, MODE_PRESETS, RunMode, ServedStep, subtitleFor } from '../modes';
import { InlineNotification, Surface } from '../ui/primitives';
import { StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { StepShell } from '../ui/StepShell';

interface Props {
  mode: RunMode;
  custom: ActionKey[];
  setMode: (mode: RunMode) => void;
  setCustom: (keys: ActionKey[]) => void;
  onConfirm: () => Promise<void>;
  locked?: boolean;
  initOnly?: boolean;
  catalog: ServedStep[];
  state: StepState;
  /** The uploaded workbook carries a filled Replication tab (SPEC-015 R4); the Replicate mode needs it. */
  hasReplicationTab?: boolean;
}

export function ModeStep({ mode, custom, setMode, setCustom, onConfirm, locked, initOnly, catalog, state, hasReplicationTab }: Props) {
  const { nextTitle } = useStepContext();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (key: ActionKey, checked: boolean) =>
    setCustom(checked ? [...custom, key] : custom.filter((item) => item !== key));

  // Zoning and provisioning both compute over the discovery results, so a custom selection without
  // discovery would dead-end at the first of them.
  const missingDiscovery =
    !locked &&
    mode === 'CUSTOM' &&
    (custom.includes('zoning') || custom.includes('provision')) &&
    !custom.includes('discover');
  // The replication steps read the Replication tab; a workbook without one refuses them (422).
  const replicationPicked = custom.includes('replicate') || custom.includes('failover_test');
  const missingReplicationTab = !locked && !hasReplicationTab && (mode === 'REPLICATE' || (mode === 'CUSTOM' && replicationPicked));

  const presets = initOnly ? MODE_PRESETS.filter((preset) => preset.mode === 'FULL_ONBOARDING') : MODE_PRESETS;
  const unavailable = (preset: (typeof MODE_PRESETS)[number]) => !locked && preset.needs === 'replication' && !hasReplicationTab;
  const labelFor = (preset: (typeof MODE_PRESETS)[number]) =>
    initOnly && preset.mode === 'FULL_ONBOARDING' ? 'Initialization' : preset.label;
  const blurbFor = (preset: (typeof MODE_PRESETS)[number]) =>
    initOnly && preset.mode === 'FULL_ONBOARDING'
      ? 'Registers the array in HPE GreenLake, connects it, completes DSCC setup, then verifies the configuration.'
      : preset.blurb;

  const confirm = async () => {
    setBusy(true);
    setError(null);
    try {
      await onConfirm();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <StepShell
      title="Select mode"
      description="The wizard presents only the steps the selected mode requires, enabling provisioning or verification of an array that is already initialised."
      state={state}
      error={error}
      onDismissError={() => setError(null)}
      footerNote={
        locked
          ? 'The mode is fixed for the lifetime of the run.'
          : 'Creating the run associates this workbook with the array.'
      }
      actions={
        <Button
          primary
          busy={busy}
          label={locked ? `Continue to ${nextTitle ?? 'the next step'}` : 'Create run'}
          disabled={(mode === 'CUSTOM' && custom.length === 0) || missingDiscovery || missingReplicationTab}
          onClick={confirm}
        />
      }
    >
      <Surface title={initOnly ? 'Initialization' : 'Mode'}>
        <Box gap="xsmall" flex={false}>
          {presets.map((preset) => {
            const selected = mode === preset.mode;
            const off = unavailable(preset);
            return (
              <Box
                key={preset.mode}
                direction="row"
                gap="small"
                align="start"
                pad="small"
                round="small"
                background={selected ? 'background-contrast' : undefined}
                border={{ color: selected ? 'brand' : 'transparent', size: '2px' }}
                onClick={locked || off ? undefined : () => setMode(preset.mode)}
                focusIndicator={!locked && !off}
                flex={false}
                style={{ cursor: locked || off ? 'default' : 'pointer', opacity: (locked && !selected) || off ? 0.5 : 1 }}
                a11yTitle={off ? `${preset.label} — needs the workbook's Replication tab` : undefined}
              >
                {/* X-1: the DS glyph, not a hand-drawn 18px/8px radio. */}
                <Box flex={false} margin={{ top: 'xxsmall' }}>
                  {selected ? <RadialSelected color="brand" a11yTitle="selected" /> : <Radial color="border" a11yTitle="not selected" />}
                </Box>
                <Box>
                  <Text weight={selected ? 'bold' : undefined} color={selected ? 'text-strong' : undefined}>
                    {labelFor(preset)}
                  </Text>
                  <Text size="small" color="text-weak">
                    {blurbFor(preset)}
                  </Text>
                  {off && (
                    <Text size="xsmall" color="text-weak">
                      Not available: the uploaded workbook has no filled Replication tab.
                    </Text>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      </Surface>

      {mode === 'CUSTOM' && (
        <Surface title="Steps to run" description="Choose exactly the steps this run should include.">
          <Box gap="xsmall" flex={false}>
            {catalog.map((step) => (
              <CheckBox
                key={step.key}
                label={`${step.label} — ${subtitleFor(step.key)}`}
                checked={custom.includes(step.key)}
                disabled={locked}
                onChange={(event) => toggle(step.key, event.target.checked)}
              />
            ))}
          </Box>
        </Surface>
      )}

      {missingDiscovery && (
        <InlineNotification
          tone="warning"
          title="Discovery is required"
          message="SAN zoning and Provision storage both work from the discovery results — include Discovery in the selection."
        />
      )}

      {missingReplicationTab && (
        <InlineNotification
          tone="warning"
          title="The Replication tab is required"
          message="Replication and Failover test read the peer array and the volume sets to protect from the workbook's Replication tab. Fill it in (download the template for the layout) and upload the workbook again."
        />
      )}

      {locked && (
        <InlineNotification
          tone="info"
          title="The mode is fixed for this run"
          message="Cancel the run from the wizard bar to start again with a different mode."
        />
      )}
    </StepShell>
  );
}
