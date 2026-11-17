import { Box, CheckBox, Grid, ResponsiveContext, Text } from 'grommet';
import { useContext, useState } from 'react';
import { ActionKey, MODE_PRESETS, RunMode, ServedStep, subtitleFor, unavailableReasons } from '../modes';
import { Guidance, Panel, SelectorCard } from '../ui/blocks';
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
  /** The served preset mode -> step keys map. */
  modeSteps: Record<string, ActionKey[]>;
  state: StepState;
  /** The uploaded workbook carries a filled Replication tab (SPEC-015 R4); the Replicate mode needs it. */
  hasReplicationTab?: boolean;
  /** The steps the chosen mode (or custom pick) puts in the run, in order: the list the rail shows. */
  runSteps: string[];
  /** SPEC-023 R9: the workbook fills the Snapshots tab but the chosen steps leave out Snapshots. */
  snapshotsReminder?: string | null;
}

const STAGE: Record<string, string> = {
  init: 'Onboard', provision: 'Provision', replicate: 'Replicate', migrate: 'Migrate', snapshot: 'Protect', verify: 'Document',
};

export function ModeStep({ mode, custom, setMode, setCustom, onConfirm, locked, initOnly, catalog, modeSteps, state, hasReplicationTab, runSteps, snapshotsReminder }: Props) {
  const stepCount = runSteps.length;
  const { nextTitle } = useStepContext();
  const size = useContext(ResponsiveContext);
  const columns = size === 'xsmall' ? 1 : size === 'small' ? 2 : 3;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (key: ActionKey, checked: boolean) => setCustom(checked ? [...custom, key] : custom.filter((item) => item !== key));

  // Zoning and provisioning both compute over the discovery results, so a custom selection without
  // discovery would dead-end at the first of them.
  const missingDiscovery =
    !locked && mode === 'CUSTOM' && (custom.includes('zoning') || custom.includes('provision')) && !custom.includes('discover');
  // The replication steps read the Replication tab; a workbook without one refuses them (422).
  const replicationPicked = custom.includes('replicate') || custom.includes('failover_test');
  const missingReplicationTab = !locked && !hasReplicationTab && (mode === 'REPLICATE' || (mode === 'CUSTOM' && replicationPicked));

  // A step whose work is not built yet is served with the reason; a run cannot include it (the server refuses it too).
  const notBuilt = (keys: ActionKey[]) => (locked ? [] : unavailableReasons(catalog, keys));
  const notBuiltPicked = notBuilt(mode === 'CUSTOM' ? custom : (modeSteps[mode] ?? []));

  const presets = initOnly ? MODE_PRESETS.filter((preset) => preset.mode === 'FULL_ONBOARDING') : MODE_PRESETS;
  const presetNotBuilt = (preset: (typeof MODE_PRESETS)[number]) => (preset.mode === 'CUSTOM' ? [] : notBuilt(modeSteps[preset.mode] ?? []));
  const unavailable = (preset: (typeof MODE_PRESETS)[number]) =>
    !locked && ((preset.needs === 'replication' && !hasReplicationTab) || presetNotBuilt(preset).length > 0);
  const labelFor = (preset: (typeof MODE_PRESETS)[number]) =>
    initOnly && preset.mode === 'FULL_ONBOARDING' ? 'Initialization' : preset.label.replace('…', '');
  const blurbFor = (preset: (typeof MODE_PRESETS)[number]) =>
    initOnly && preset.mode === 'FULL_ONBOARDING'
      ? 'Registers the array in HPE GreenLake, connects it, completes DSCC setup, then verifies the configuration.'
      : preset.mode === 'CUSTOM'
        ? 'Pick exactly the steps to run, below.'
        : preset.blurb;

  const blocked =
    mode === 'CUSTOM' && custom.length === 0
      ? 'Tick at least one step.'
      : missingDiscovery
        ? 'Add Discovery: SAN zoning and Provision storage work from what it finds.'
        : missingReplicationTab
          ? "The workbook has no filled Replication tab. Fill it in and upload the workbook again, or choose another mode."
          : notBuiltPicked.length
            ? notBuiltPicked.join(' ')
            : undefined;

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

  const stages = Object.entries(STAGE)
    .map(([kind, title]) => ({ title, steps: catalog.filter((s) => s.kind === kind) }))
    .filter((g) => g.steps.length);

  return (
    <StepShell
      title="What do you want to do?"
      description="The run includes only the steps this choice needs."
      state={state}
      stateLabel={locked ? 'Mode chosen' : mode === 'CUSTOM' ? 'Pick the steps' : 'Choose a mode'}
      error={error}
      onDismissError={() => setError(null)}
      status={
        locked
          ? {
              state: 'complete',
              title: 'The mode is fixed for this run',
              message: 'To use a different mode, cancel the run from the bar above and start again.',
            }
          : snapshotsReminder
            ? { state: 'action_required', title: 'Snapshots are not in this run', message: snapshotsReminder }
            : undefined
      }
      primary={
        locked
          ? { label: `Continue to ${nextTitle ?? 'the next step'}`, busy, onClick: confirm }
          : { label: `Create run · ${stepCount} step${stepCount === 1 ? '' : 's'}`, busy, onClick: confirm, blocked }
      }
      guidance={
        <Guidance
          items={[
            { title: 'You can change your mind', body: 'The mode is fixed for the life of a run. To do something else with the same workbook, start another run from Runs, top right.' },
            { title: 'Replication needs its tab', body: 'Provision, then replicate, and the Replication and Failover test steps, need the workbook’s Replication tab filled in.' },
            { title: 'Custom', body: 'SAN zoning and Provision storage work from what Discovery finds, so a custom run with either of them needs Discovery too.' },
          ]}
        />
      }
    >
      <Grid columns={{ count: columns, size: 'auto' }} gap="small" role="radiogroup" aria-label="What do you want to do?">
        {presets.map((preset) => {
          const off = unavailable(preset);
          return (
            <SelectorCard
              key={preset.mode}
              title={labelFor(preset)}
              checked={mode === preset.mode}
              disabled={locked || off}
              onSelect={() => setMode(preset.mode)}
            >
              <Text size="small" color="text-weak">
                {blurbFor(preset)}
              </Text>
              {off && (
                <Text size="xsmall" color="text-weak">
                  {presetNotBuilt(preset).length
                    ? presetNotBuilt(preset).join(' ')
                    : 'Not available: the uploaded workbook has no filled Replication tab.'}
                </Text>
              )}
            </SelectorCard>
          );
        })}
      </Grid>

      {mode === 'CUSTOM' && (
        <Panel title="Steps to run" right={<Text size="small" color="text-weak">{custom.length} of {catalog.length} ticked</Text>}>
          <Grid columns={{ count: columns, size: 'auto' }} gap="medium">
            {stages.map((g) => (
              <Box key={g.title} gap="xsmall" flex={false}>
                <Text size="small" weight={500} color="text-weak">
                  {g.title}
                </Text>
                {g.steps.map((step) => (
                  <CheckBox
                    key={step.key}
                    checked={custom.includes(step.key)}
                    disabled={locked || Boolean(step.unavailable)}
                    onChange={(event) => toggle(step.key, event.target.checked)}
                    label={
                      <Box>
                        <Text size="small">{step.label}</Text>
                        <Text size="xsmall" color="text-weak">
                          {step.unavailable || subtitleFor(step.key)}
                        </Text>
                      </Box>
                    }
                  />
                ))}
              </Box>
            ))}
          </Grid>
        </Panel>
      )}

      {!locked && (
        <Text size="small" color="text-weak">
          <Text size="small" weight={500} color="text-strong">
            This run will do:{' '}
          </Text>
          {runSteps.length ? runSteps.join('  →  ') : 'the steps you tick above.'}
        </Text>
      )}
    </StepShell>
  );
}
