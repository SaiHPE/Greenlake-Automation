import { Box, Button, Heading, Layer, Main, ResponsiveContext, Text } from 'grommet';
import { useContext, useEffect, useRef, useState } from 'react';
import { createRunFromSheet, getAppProfile, getRun, InitSheetUploadResult } from './api';
import { actionKeysFor, ActionKey, phaseToActionKey, RunMode, ServedStep, StepRegistry } from './modes';
import { useRunEvents } from './useRunEvents';
import { EMPTY_FORM, fromParsedWorkItem, WorkItemForm } from './workItem';
import { AppHeader, RailItem, StepRail, WizardBar } from './ui/AppChrome';
import { StepProvider } from './ui/StepContext';
import { ConsolePane } from './ui/ConsolePane';
import { Home, OverviewStep, RunOverview } from './ui/RunPages';
import { StepState } from './ui/status';
import { deriveStepHint, deriveStepState, runStatusToState, stepEvents } from './ui/useStepState';
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
import { ReplicationStep } from './steps/ReplicationStep';
import { FailoverTestStep } from './steps/FailoverTestStep';
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
const PREPARE_KEYS = ['prereq', 'sheet', 'mode'];
const RUN_ID_KEY = 'alletra.runId';

// Registry step kinds, mapped to the deployment stages the rail groups by.
const STAGE: Record<string, string> = { init: 'Initialize', provision: 'Provision', replicate: 'Replicate', verify: 'Document' };

// Prerequisites -> sheet -> mode -> the steps the mode selected -> finish. The middle comes from the
// served registry (GET /app/profile); the UI keeps no copy of the step list.
function buildSteps(registry: StepRegistry | null, mode: RunMode, custom: ActionKey[]): WizardStep[] {
  const keys = registry ? new Set(actionKeysFor(registry, mode, custom)) : new Set<ActionKey>();
  const actions = (registry?.steps ?? [])
    .filter((step) => keys.has(step.key))
    .map((step) => ({ key: step.key, label: step.label, group: STAGE[step.kind] ?? 'Provision', served: step }));
  return [PREREQ_STEP, SHEET_STEP, MODE_STEP, ...actions, DONE_STEP];
}

type View = 'wizard' | 'home' | 'overview';

export default function App() {
  const storedRunId = localStorage.getItem(RUN_ID_KEY);
  const [mode, setMode] = useState<RunMode>('FULL_ONBOARDING');
  const [customSteps, setCustomSteps] = useState<ActionKey[]>([]);
  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [form, setForm] = useState<WorkItemForm>(EMPTY_FORM);
  const [runId, setRunId] = useState<string | null>(storedRunId);
  // The held-sheet token from the upload step; the Mode step mints the run from it. In memory only:
  // refreshing before a mode is chosen means re-uploading, which costs nothing because no run exists.
  const [sheetToken, setSheetToken] = useState<string | null>(null);
  // The parsed workbook lives here, not inside the sheet step: returning to that step must not lose
  // the upload and disable its own Continue button.
  const [sheetResult, setSheetResult] = useState<InitSheetUploadResult | null>(null);
  const [initOnly, setInitOnly] = useState(false);
  const [registry, setRegistry] = useState<StepRegistry | null>(null);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [footerHost, setFooterHost] = useState<HTMLDivElement | null>(null);
  const [view, setView] = useState<View>('wizard');
  const size = useContext(ResponsiveContext);
  const pad = size === 'large' || size === 'xlarge' ? 'large' : 'medium';

  const switchRun = (id: string) => {
    if (id === runId) {
      setView('wizard');
      return;
    }
    // The restore-on-load path already rebuilds mode, steps and position from the stored id; reuse it.
    localStorage.setItem(RUN_ID_KEY, id);
    window.location.reload();
  };
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
        document.title = profile.title;
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
        const found = actionKey ? restoredSteps.findIndex((item) => item.key === actionKey) : -1;
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
    setView('wizard');
  };
  const next = () => advance(Math.min(stepIndex + 1, lastStep));
  const previous = () => setStep(Math.max(stepIndex - 1, 0));
  const openStep = (key: string) => {
    const index = steps.findIndex((item) => item.key === key);
    if (index >= 0) advance(index);
  };

  const discardRun = () => {
    setRunId(null);
    setSheetToken(null);
    setSheetResult(null);
    setForm(EMPTY_FORM);
    setCustomSteps([]);
    setMode('FULL_ONBOARDING');
    setStep(0);
    setMaxStep(0);
    setConfirmCancel(false);
    setView('wizard');
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

  // The state of the steps that frame a run. One definition, used by the rail AND by the step
  // itself: deriving it in both places is how a rail entry ends up disagreeing with its own header.
  const scaffoldState = (key: string): StepState => {
    if (key === 'prereq') return maxStep > 0 ? 'complete' : 'action_required';
    if (key === 'sheet') return sheetToken || runId || sheetResult ? 'complete' : maxStep >= 1 ? 'action_required' : 'not_started';
    if (key === 'mode') return runId ? 'complete' : maxStep >= 2 ? 'action_required' : 'not_started';
    return run?.status === 'succeeded' ? 'complete' : runId ? 'action_required' : 'not_started';
  };
  const railItems: RailItem[] = steps.map((item, index) => ({
    key: item.key,
    label: item.label,
    group: item.group,
    state: item.served ? deriveStepState(item.served, run, events) : scaffoldState(item.key),
    hint: item.served ? deriveStepHint(item.served, run, events) : undefined,
    reachable: index <= maxStep,
  }));
  // Before a run exists the rail lists only Prepare; on the Mode step it previews the chosen mode's
  // steps, so the count does not jump when the run is created.
  const shownRail = runId
    ? railItems
    : railItems.filter((item) => PREPARE_KEYS.includes(item.key) || (current.key === 'mode' && item.key !== 'done'));

  // "Prepare · step 2 of 3" before the run; "Step 3 of 7" for the run's own steps; nothing on Finish.
  const runSteps = steps.filter((item) => item.served);
  const stepLabel = (key: string): string => {
    const p = PREPARE_KEYS.indexOf(key);
    if (p >= 0) return `Prepare · step ${p + 1} of ${PREPARE_KEYS.length}`;
    const r = runSteps.findIndex((item) => item.key === key);
    return r >= 0 ? `Step ${r + 1} of ${runSteps.length}` : '';
  };

  // One mapper for run status, shared with the step model: 'ready' is idle, not running, so the
  // header does not claim work is happening while the tool waits for the operator.
  const runState: StepState | undefined = run ? runStatusToState(run.status) : undefined;
  const runLabel = run
    ? {
        complete: 'Run complete',
        failed: 'Run needs attention',
        action_required: 'Waiting for you',
        waiting: 'Waiting on others',
        running: 'Run in progress',
        not_started: 'Run open',
      }[runState ?? 'not_started']
    : undefined;
  const currentModeLabel = modeLabel(mode, initOnly);
  const phaseLabel = (phase: string) => {
    const key = registry ? phaseToActionKey(registry, phase) : null;
    const served = registry?.steps.find((s) => s.key === key);
    if (served) return served.label;
    return phase === 'COMPLETE' ? 'Complete' : phase.replaceAll('_', ' ').toLowerCase();
  };

  const overviewSteps: OverviewStep[] = steps
    .map((item, index) => ({ item, rail: railItems[index] }))
    .filter(({ item }) => item.served)
    .map(({ item, rail }) => {
      const mine = stepEvents(item.served, events);
      return { key: item.key, label: item.label, state: rail.state, hint: rail.hint, lastAt: mine[mine.length - 1]?.created_at };
    });

  const needsRun = Boolean(current.served) && !runId;
  const stepValue = {
    runId,
    run,
    events,
    step: current.served,
    position: { index: stepIndex + 1, total: steps.length, label: stepLabel(current.key) },
    nextTitle: steps[stepIndex + 1]?.label,
    onDone: next,
    footerHost,
  };

  const finished = current.key === 'done';
  const cancelControl =
    finished || (!runId && maxStep === 0)
      ? undefined
      : { label: runId ? 'Cancel run' : 'Start over', onClick: () => setConfirmCancel(true) };

  return (
    <Box fill background="background-back">
      <AppHeader
        appName={initOnly ? 'initialization' : 'onboarding'}
        serial={run?.serial_number}
        mode={runId ? currentModeLabel : undefined}
        runState={runState}
        runLabel={runLabel}
        onHome={() => setView('home')}
        onNewRun={discardRun}
      />
      {view === 'home' ? (
        <Home
          currentRunId={runId}
          modeLabel={(m) => modeLabel(m as RunMode, initOnly)}
          phaseLabel={phaseLabel}
          onOpen={switchRun}
          onNewRun={discardRun}
        />
      ) : (
        <Box direction="row" flex overflow="hidden">
          <StepRail
            items={shownRail}
            activeKey={view === 'wizard' ? current.key : ''}
            onSelect={openStep}
            overview={runId ? { current: view === 'overview', onSelect: () => setView('overview') } : undefined}
            note={!runId && current.key !== 'mode' ? 'The steps of your run appear here once you choose what to do (step 3).' : undefined}
          />
          <Box flex direction="column" overflow="hidden">
            {view === 'wizard' && !finished && (
              <WizardBar
                flow={runId ? `${currentModeLabel} on ${run?.serial_number ?? 'this array'}` : 'Prepare a run'}
                previous={stepIndex > 0 ? { label: steps[stepIndex - 1].label, onClick: previous } : undefined}
                cancel={cancelControl}
              />
            )}
            {/* A real <main> landmark: assistive technology needs to skip the rail to the step content. */}
            <Main flex overflow="auto" background="background-back">
              {view === 'overview' && runId ? (
                <RunOverview
                  runId={runId}
                  run={run}
                  events={events}
                  steps={overviewSteps}
                  modeLabel={currentModeLabel}
                  onOpenStep={openStep}
                  onHome={() => setView('home')}
                />
              ) : finished ? (
                <DoneStep
                  runId={runId}
                  run={run}
                  events={events}
                  modeLabel={runId ? currentModeLabel : ''}
                  onRestart={() => setConfirmCancel(true)}
                  onHome={() => setView('home')}
                />
              ) : (
                <Box pad={{ horizontal: pad, vertical: 'medium' }} width={{ max: 'xxlarge' }} flex={false}>
                  <StepProvider value={stepValue}>
                    {current.key === 'prereq' && <PrereqStep onDone={next} state={scaffoldState('prereq')} />}
                    {current.key === 'sheet' && (
                      <InitSheetStep
                        setForm={setForm}
                        result={sheetResult}
                        setResult={setSheetResult}
                        state={scaffoldState('sheet')}
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
                        state={scaffoldState('mode')}
                        hasReplicationTab={Boolean(sheetResult?.targets?.peer_host) || Boolean(runId)}
                        runSteps={runSteps.map((item) => item.label)}
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
                    {current.key === 'replicate' && runId && <ReplicationStep runId={runId} run={run} events={events} onDone={next} />}
                    {current.key === 'failover_test' && runId && <FailoverTestStep runId={runId} run={run} events={events} onDone={next} />}
                    {current.key === 'verify' && runId && <VerifyStep runId={runId} run={run} events={events} onDone={next} />}
                    {current.key === 'asbuilt' && runId && <AsBuiltStep runId={runId} run={run} events={events} onDone={next} />}
                    {needsRun && <Text color="text-weak">Choose a mode first. That creates the run.</Text>}
                  </StepProvider>
                </Box>
              )}
            </Main>
            {/* the current step's footer is drawn here (StepShell portals into it) */}
            <Box ref={setFooterHost} flex={false} />
            {runId && <ConsolePane runId={runId} activity={current.served && view === 'wizard' ? stepEvents(current.served, events) : events} />}
          </Box>
        </Box>
      )}

      {/* Design System double confirmation: nothing is deleted, so say what does and does not happen. */}
      {confirmCancel && (
        <Layer position="center" onEsc={() => setConfirmCancel(false)} onClickOutside={() => setConfirmCancel(false)} modal>
          <Box pad="large" gap="medium" width="large">
            <Box gap="xxsmall">
              <Heading level={2} size="small" margin="none">
                {finished ? 'Start a new run?' : runId ? 'Cancel this run?' : 'Start over?'}
              </Heading>
              <Text color="text-strong">{runId ? `${currentModeLabel} on ${run?.serial_number ?? 'this array'}` : 'Prepare a run'}</Text>
            </Box>
            <Text>
              {runId
                ? 'You go back to the Prerequisites. This run stays in Your runs with everything it did, and you can open it again. Nothing on the array, vCenter or the switches changes.'
                : 'The uploaded workbook and your choices on these screens are forgotten.'}
            </Text>
            <Box as="footer" direction="row" gap="small" justify="end">
              <Button label="No, stay" secondary onClick={() => setConfirmCancel(false)} />
              <Button
                primary
                label={finished ? 'Yes, start a new run' : runId ? 'Yes, cancel the run' : 'Yes, start over'}
                onClick={discardRun}
              />
            </Box>
          </Box>
        </Layer>
      )}
    </Box>
  );
}

function modeLabel(mode: RunMode, initOnly: boolean): string {
  if (initOnly) return 'Initialization';
  return (
    {
      FULL_ONBOARDING: 'Full onboarding',
      PROVISION_ONLY: 'Provision storage only',
      BOTH: 'Onboard, then provision',
      REPLICATE: 'Provision, then replicate',
      VERIFY_ONLY: 'Verify only',
      CUSTOM: 'Custom',
    }[mode] ?? mode
  );
}
