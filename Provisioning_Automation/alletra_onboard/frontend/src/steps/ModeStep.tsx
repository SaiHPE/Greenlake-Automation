import { Box, Button, CheckBox, Notification, Text } from 'grommet';
import { useState } from 'react';
import { Section } from '../components';
import { ActionKey, MODE_PRESETS, RunMode, ServedStep, subtitleFor } from '../modes';

interface Props {
  mode: RunMode;
  custom: ActionKey[];
  setMode: (mode: RunMode) => void;
  setCustom: (keys: ActionKey[]) => void;
  onConfirm: () => Promise<void>; // mints the run from the uploaded sheet + this mode, then advances
  locked?: boolean; // once a run exists the mode is fixed (it shaped the run)
  initOnly?: boolean; // the Initialization accelerator: only the Initialization mode is offered
  catalog: ServedStep[]; // the SERVED step registry (GET /app/profile) — drives the CUSTOM picker
}

export function ModeStep({ mode, custom, setMode, setCustom, onConfirm, locked, initOnly, catalog }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toggle = (key: ActionKey, checked: boolean) =>
    setCustom(checked ? [...custom, key] : custom.filter((k) => k !== key));

  // SAN Zoning and Provision storage both COMPUTE over the Discovery results, so a custom run that
  // includes either without Discovery dead-ends (the step can't run, and Restart is only on Finish).
  // Require Discovery before the run is minted.
  const missingDiscovery =
    !locked && mode === 'CUSTOM' && (custom.includes('zoning') || custom.includes('provision')) && !custom.includes('discover');

  // The init-only accelerator offers just Initialization (Full onboarding), relabelled.
  const presets = initOnly ? MODE_PRESETS.filter((p) => p.mode === 'FULL_ONBOARDING') : MODE_PRESETS;
  const labelFor = (p: (typeof MODE_PRESETS)[number]) =>
    initOnly && p.mode === 'FULL_ONBOARDING' ? 'Initialization' : p.label;
  const blurbFor = (p: (typeof MODE_PRESETS)[number]) =>
    initOnly && p.mode === 'FULL_ONBOARDING'
      ? 'Register in GreenLake, run the Cloud Connectivity wizard, complete DSCC Set Up, then verify.'
      : p.blurb;

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
    <Box gap="medium">
      <Section title={initOnly ? 'Initialization' : 'What do you want to run?'}>
        <Text size="small" color="text-weak">
          {initOnly
            ? 'This accelerator runs array initialization only: GreenLake registration, Cloud Connectivity, and DSCC Set Up, then a read-only verify.'
            : 'Pick a mode. The wizard then shows only the steps that mode needs — so you can verify or provision an already-initialised array without re-running initialisation.'}
        </Text>
        <Box gap="small" pad={{ top: 'small' }}>
          {presets.map((preset) => {
            const selected = mode === preset.mode;
            return (
              <Box
                key={preset.mode}
                direction="row"
                gap="small"
                align="center"
                pad="small"
                round="small"
                border={{ color: selected ? 'brand' : 'border', size: selected ? '2px' : '1px' }}
                background={selected ? 'background-contrast' : undefined}
                onClick={locked ? undefined : () => setMode(preset.mode)}
                style={{ cursor: locked ? 'default' : 'pointer', opacity: locked && !selected ? 0.5 : 1 }}
              >
                <Box
                  width="18px"
                  height="18px"
                  round="full"
                  flex={false}
                  border={{ color: selected ? 'brand' : 'border', size: '2px' }}
                  align="center"
                  justify="center"
                >
                  {selected && <Box width="9px" height="9px" round="full" background="brand" />}
                </Box>
                <Box>
                  <Text weight={selected ? 'bold' : undefined}>{labelFor(preset)}</Text>
                  <Text size="small" color="text-weak">
                    {blurbFor(preset)}
                  </Text>
                </Box>
              </Box>
            );
          })}
        </Box>
      </Section>

      {mode === 'CUSTOM' && (
        <Section title="Pick the steps to run">
          <Box gap="xsmall">
            {catalog.map((action) => (
              <CheckBox
                key={action.key}
                label={`${action.label} — ${subtitleFor(action.key)}`}
                checked={custom.includes(action.key)}
                disabled={locked}
                onChange={(event) => toggle(action.key, event.target.checked)}
              />
            ))}
          </Box>
        </Section>
      )}

      {locked && (
        <Text size="small" color="text-weak">
          A run already exists for this session — the mode is locked. Use “Start over” (bottom of the
          left sidebar) to begin a new run with a different mode.
        </Text>
      )}

      {missingDiscovery && (
        <Notification
          status="warning"
          title="Add Discovery"
          message="SAN Zoning and Provision storage both work from the Discovery results — include “Discovery” in your selection."
        />
      )}

      {error && (
        <Notification status="critical" title="Could not create the run" message={error} onClose={() => setError(null)} />
      )}

      <Button
        primary
        alignSelf="start"
        label={busy ? 'Creating run…' : locked ? 'Continue →' : 'Create run & continue →'}
        disabled={busy || (mode === 'CUSTOM' && custom.length === 0) || missingDiscovery}
        onClick={confirm}
      />
    </Box>
  );
}
