import { Box, Button, Layer, Text } from 'grommet';
import { useEffect, useRef, useState } from 'react';
import { createRunFromSheet, getAppProfile, getRun } from './api';
import { actionKeysFor, ActionKey, phaseToActionKey, RunMode, ServedStep, StepRegistry } from './modes';
import { useRunEvents } from './useRunEvents';
import { EMPTY_FORM, fromParsedWorkItem, WorkItemForm } from './workItem';
import { AppHeader, RailItem, StepRail, WizardBar } from './ui/AppChrome';
import { StepProvider } from './ui/StepContext';
import { StepState } from './ui/status';
import { deriveStepHint, deriveStepState } from './ui/useStepState';
import { AsBuiltStep } from './steps/AsBuiltStep';
import { CloudinitStep } from './steps/CloudinitStep';
import { DiscoveryStep } from './steps/DiscoveryStep';
import { DoneStep } from './steps/DoneStep';
import { DsccStep } from './steps/DsccStep';
import { GreenLakeStep } from './steps/GreenLakeStep';
import { InitSheetStep } from './steps/InitSheetStep';
import { ModeStep } from './steps/ModeStep';
import { PrereqStep } from './steps/PrereqStep';
import { ProvisionStep } from './steps/ProvisionStep';
import { VerifyStep } from './steps/VerifyStep';
import { ZoningStep } from './steps/ZoningStep';

interface WizardStep {
  key: string;
  label: string;
  group: string;
  /** The registry entry, for the steps a run actually executes. */
  served?: ServedStep;
}

// The steps that frame every run whatever the mode: intake before, summary after.
const PREREQ_STEP: WizardStep = { key: 'prereq', label: 'Prerequisites', group: 'Prepare' };
const SHEET_STEP: WizardStep = { key: 'sheet', label: 'Initialisation sheet', group: 'Prepare' };
const MODE_STEP: WizardStep = { key: 'mode', label: 'Mode', group: 'Prepare' };
const DONE_STEP: WizardStep = { key: 'done', label: 'Finish', group: 'Document' };
const RUN_ID_KEY = 'alletra.runId';

// Registry step kinds, mapped to the deployment stages the rail groups by.
const STAGE: Record<string, string> = { init: 'Initialize', provision: 'Provision', verify: 'Document' };

// Prerequisites -> sheet -> mode -> the steps the mode selected -> finish. The middle comes from the
// served registry (GET /app/profile); the UI keeps no copy of the step list.
function buildSteps(registry: StepRegistry | null, mode: RunMode, custom: ActionKey[]): WizardStep[] {
  const keys = registry ? new Set(actionKeysFor(registry, mode, custom)) : new Set<ActionKey>();
  const actions = (registry?.steps ?? [])
    .filter((step) => keys.has(step.key))
    .map((step) => ({ key: step.key, label: step.label, group: STAGE[step.kind] ?? 'Provision', served: step }));
  return [PREREQ_STEP, SHEET_STEP, MODE_STEP, ...actions, DONE_STEP];
}

export default function App() {
  const storedRunId = localStorage.getItem(RUN_ID_KEY);
  const [mode, setMode] = useState<RunMode>('FULL_ONBOARDING');
  const [customSteps, setCustomSteps] = useState<ActionKey[]>([]);
  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [form, setForm] = useState<WorkItemForm>(EMPTY_FORM);
  const [runId, setRunId] = useState<string | null>(storedRunId);
  // The held-sheet token from the upload step; the Mode step mints the run from it. In memory only —
  // refreshing before a mode is chosen means re-uploading, which costs nothing because no run exists.
  const [sheetToken, setSheetToken] = useState<string | null>(null);
  const [initOnly, setInitOnly] = useState(false);
  const [appTitle, setAppTitle] = useState('Alletra MP B10000 Onboarding');
  const [registry, setRegistry] = useState<StepRegistry | null>(null);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const { run, events } = useRunEvents(runId);

  const steps = buildSteps(registry, mode, customSteps);
  const lastStep = steps.length - 1;
  const stepIndex = Math.min(step, lastStep);
  const current = steps[stepIndex];

  useEffect(() => {
    if (runId) localStorage.setItem(RUN_ID_KEY, runId);
    else localStorage.removeItem(RUN_ID_KEY);
  }, [runId]);

  // Build profile: brand the app, take the served registry, and lock the accelerator to Initialization.
  useEffect(() => {
    getAppProfile()
      .then((profile) => {
        setInitOnly(profile.init_only);
        setAppTitle(profile.title);
        setRegistry({ steps: profile.steps, modes: profile.modes });
        if (profile.init_only) setMode('FULL_ONBOARDING');
      })
      .catch(() => undefined);
  }, []);

  // Once the registry has arrived: restore a persisted run, its mode and its position. Indexes come
  // from the built step list, so nothing depends on how many steps frame the run.
  const restored = useRef(false);
  useEffect(() => {
    if (!registry || restored.current) return;
    restored.current = true;
    const stored = localStorage.getItem(RUN_ID_KEY);
    if (!stored) return;
    getRun(stored)
      .then((detail) => {
        const runMode = (detail.run.mode as RunMode) || 'FULL_ONBOARDING';
        const selected = (detail.run.selected_steps as ActionKey[]) || [];
        setMode(runMode);
        setCustomSteps(selected);
        if (detail.work_item) setForm(fromParsedWorkItem(detail.work_item));

        const restoredSteps = buildSteps(registry, runMode, selected);
        const actionKey = phaseToActionKey(registry, detail.run.current_phase);
        const found = restoredSteps.findIndex((item) => item.key === actionKey);
        const afterMode = restoredSteps.findIndex((item) => item.key === 'mode') + 1;
        setStep((currentStep) => (currentStep === 0 ? (found >= 0 ? found : afterMode) : currentStep));
        setMaxStep(restoredSteps.length - 1); // the run exists, so every step is navigable
      })
      .catch(() => {
        localStorage.removeItem(RUN_ID_KEY);
        setRunId(null);
      });
  }, [registry]);

  const advance = (to: number) => {
    setStep(to);
    setMaxStep((previous) => Math.max(previous, to));
  };
  const next = () => advance(Math.min(stepIndex + 1, lastStep));
  const previous = () => setStep(Math.max(stepIndex - 1, 0));

  const discardRun = () => {
    setRunId(null);
    setSheetToken(null);
    setForm(EMPTY_FORM);
    setCustomSteps([]);
    setMode('FULL_ONBOARDING');
    setStep(0);
    setMaxStep(0);
    setConfirmCancel(false);
  };

  // Choosing a mode is what mints the run from the held sheet. If a run already exists the operator
  // has navigated back, and the mode is fixed for its lifetime.
  const confirmMode = async () => {
    if (runId) {
      next();
      return;
    }
    if (!sheetToken) throw new Error('Upload the initialisation sheet first.');
    const { run: created } = await createRunFromSheet(sheetToken, mode, customSteps);
    setSheetToken(null);
    setRunId(created.run_id);
    next();
  };

  // The rail: one entry per step, each showing how far it has got and what it found.
  const scaffoldState = (key: string): StepState => {
    if (key === 'prereq') return stepIndex > 0 ? 'complete' : 'action_required';
    if (key === 'sheet') return sheetToken || runId ? 'complete' : stepIndex === 1 ? 'action_required' : 'not_started';
    if (key === 'mode') return runId ? 'complete' : stepIndex === 2 ? 'action_required' : 'not_started';
    return run?.status === 'succeeded' ? 'complete' : 'not_started';
  };
  const railItems: RailItem[] = steps.map((item, index) => ({
    key: item.key,
    label: item.label,
    group: item.group,
    state: item.served ? deriveStepState(item.served, run, events) : scaffoldState(item.key),
    hint: item.served ? deriveStepHint(item.served, run, events) : undefined,
    reachable: index <= maxStep,
  }));

  const runState: StepState | undefined = run
    ? run.status === 'succeeded'
      ? 'complete'
      : run.status === 'retryable_failure' || run.status === 'terminal_failure'
        ? 'failed'
        : run.status === 'waiting_for_operator'
          ? 'action_required'
          : 'running'
    : undefined;
  const runLabel = run
    ? run.status === 'succeeded'
      ? 'Run complete'
      : runState === 'failed'
        ? 'Run needs attention'
        : runState === 'action_required'
          ? 'Action required'
          : 'Run in progress'
    : undefined;

  const needsRun = Boolean(current.served) && !runId;
  const stepValue = {
    runId,
    run,
    events,
    step: current.served,
    position: { index: stepIndex + 1, total: steps.length },
    onDone: next,
  };

  return (
    <Box fill background="background-back">
      <AppHeader
        title={appTitle}
        serial={run?.serial_number}
        mode={runId ? modeLabel(mode, initOnly) : undefined}
        runState={runState}
        runLabel={runLabel}
      />
      <Box direction="row" flex overflow="hidden">
        <StepRail items={railItems} activeKey={current.key} onSelect={(key) => advance(steps.findIndex((s) => s.key === key))} />
        <Box flex overflow="auto">
          <WizardBar
            onPrevious={previous}
            canGoPrevious={stepIndex > 0}
            onCancel={() => setConfirmCancel(true)}
            canCancel={Boolean(runId)}
          />
          <Box pad="medium" width={{ max: 'xlarge' }} flex={false}>
            <StepProvider value={stepValue}>
              {current.key === 'prereq' && <PrereqStep onDone={next} />}
              {current.key === 'sheet' && (
                <InitSheetStep
                  setForm={setForm}
                  onUploaded={(token) => {
                    setSheetToken(token);
                    next();
                  }}
                />
              )}
              {current.key === 'mode' && (
                <ModeStep
                  mode={mode}
                  custom={customSteps}
                  setMode={setMode}
                  setCustom={setCustomSteps}
                  onConfirm={confirmMode}
                  locked={Boolean(runId)}
                  initOnly={initOnly}
                  catalog={registry?.steps ?? []}
                />
              )}
              {current.key === 'greenlake' && runId && <GreenLakeStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'cloudinit' && runId && (
                <CloudinitStep runId={runId} run={run} events={events} form={form} onDone={next} />
              )}
              {current.key === 'dscc' && runId && (
                <DsccStep runId={runId} run={run} events={events} dsccRegion={form.dscc_region_code} onDone={next} />
              )}
              {current.key === 'discover' && runId && <DiscoveryStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'zoning' && runId && <ZoningStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'provision' && runId && <ProvisionStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'verify' && runId && <VerifyStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'asbuilt' && runId && <AsBuiltStep runId={runId} run={run} events={events} onDone={next} />}
              {current.key === 'done' && <DoneStep run={run} events={events} onRestart={() => setConfirmCancel(true)} />}
              {needsRun && <Text color="text-weak">Select a mode first — that creates the run.</Text>}
            </StepProvider>
          </Box>
        </Box>
      </Box>

      {/* Discarding a run cannot be undone, so it is confirmed twice. */}
      {confirmCancel && (
        <Layer
          position="center"
          onEsc={() => setConfirmCancel(false)}
          onClickOutside={() => setConfirmCancel(false)}
          modal
        >
          <Box pad="medium" gap="medium" width="medium">
            <Box gap="xsmall">
              <Text size="xlarge" weight="bold" color="text-strong">
                Discard this run?
              </Text>
              <Text>
                Objects already created on the array are retained. This removes the run from this tool only.
              </Text>
            </Box>
            <Box direction="row" gap="small" justify="end">
              <Button label="Keep run" onClick={() => setConfirmCancel(false)} />
              <Button primary label="Discard run" onClick={discardRun} />
            </Box>
          </Box>
        </Layer>
      )}
    </Box>
  );
}

function modeLabel(mode: RunMode, initOnly: boolean): string {
  if (initOnly) return 'Initialization';
  return {
    FULL_ONBOARDING: 'Full onboarding',
    PROVISION_ONLY: 'Provision storage only',
    BOTH: 'Onboard, then provision',
    VERIFY_ONLY: 'Verify only',
    CUSTOM: 'Custom',
  }[mode];
}
