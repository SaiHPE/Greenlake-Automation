import { Box, Button, CheckBox, Text } from 'grommet';
import { useState } from 'react';
import { ActionKey, MODE_PRESETS, RunMode, ServedStep, subtitleFor } from '../modes';
import { InlineNotification, Surface } from '../ui/primitives';
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
}

export function ModeStep({ mode, custom, setMode, setCustom, onConfirm, locked, initOnly, catalog }: Props) {
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

  const presets = initOnly ? MODE_PRESETS.filter((preset) => preset.mode === 'FULL_ONBOARDING') : MODE_PRESETS;
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
      state={locked ? 'complete' : 'action_required'}
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
          label={locked ? 'Continue' : 'Create run'}
          disabled={(mode === 'CUSTOM' && custom.length === 0) || missingDiscovery}
          onClick={confirm}
        />
      }
    >
      <Surface title={initOnly ? 'Initialization' : 'Mode'}>
        <Box gap="xsmall" flex={false}>
          {presets.map((preset) => {
            const selected = mode === preset.mode;
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
                onClick={locked ? undefined : () => setMode(preset.mode)}
                focusIndicator={!locked}
                flex={false}
                style={{ cursor: locked ? 'default' : 'pointer', opacity: locked && !selected ? 0.5 : 1 }}
              >
                <Box
                  width="18px"
                  height="18px"
                  round="full"
                  flex={false}
                  margin={{ top: 'xxsmall' }}
                  border={{ color: selected ? 'brand' : 'border', size: '2px' }}
                  align="center"
                  justify="center"
                >
                  {selected && <Box width="8px" height="8px" round="full" background="brand" />}
                </Box>
                <Box>
                  <Text weight={selected ? 'bold' : undefined} color={selected ? 'text-strong' : undefined}>
                    {labelFor(preset)}
                  </Text>
                  <Text size="small" color="text-weak">
                    {blurbFor(preset)}
                  </Text>
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
