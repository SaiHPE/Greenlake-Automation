import { Box, Heading, Text } from 'grommet';
import { Checkmark } from 'grommet-icons';
import { useEffect, useRef, useState } from 'react';
import { createRunFromSheet, getRun } from './api';
import { actionKeysFor, ACTION_CATALOG, ActionKey, phaseToActionKey, RunMode } from './modes';
import { useRunEvents } from './useRunEvents';
import { EMPTY_FORM, fromParsedWorkItem, WorkItemForm } from './workItem';
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

interface StepDef {
  key: string;
  title: string;
  subtitle: string;
}

// The scaffolding steps that frame every run, regardless of mode.
const MODE_STEP: StepDef = { key: 'mode', title: 'Choose what to run', subtitle: 'pick a mode' };
const PREREQ_STEP: StepDef = { key: 'prereq', title: 'Prerequisites', subtitle: 'what to do first' };
const SHEET_STEP: StepDef = { key: 'sheet', title: 'Initialisation sheet', subtitle: 'download · fill · upload' };
const DONE_STEP: StepDef = { key: 'done', title: 'Finish', subtitle: 'summary' };
const RUN_ID_KEY = 'alletra.runId';

// The wizard steps: the sheet is COMPLETE intake and comes BEFORE the mode (ADR 0005 revision), so
// the order is Prereq -> Sheet -> Mode -> the mode's action steps -> Finish. Still 3 scaffolding
// steps before the actions, so the resume math (3 + indexInActions) is unchanged.
function buildSteps(mode: RunMode, custom: ActionKey[]): StepDef[] {
  const keys = actionKeysFor(mode, custom);
  const actions = ACTION_CATALOG.filter((a) => keys.includes(a.key)).map((a) => ({
    key: a.key,
    title: a.title,
    subtitle: a.subtitle,
  }));
  return [PREREQ_STEP, SHEET_STEP, MODE_STEP, ...actions, DONE_STEP];
}

const ACTION_KEY_SET = new Set<string>(ACTION_CATALOG.map((a) => a.key));

export default function App() {
  const storedRunId = localStorage.getItem(RUN_ID_KEY);
  const [mode, setMode] = useState<RunMode>('FULL_ONBOARDING');
  const [customSteps, setCustomSteps] = useState<ActionKey[]>([]);
  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [form, setForm] = useState<WorkItemForm>(EMPTY_FORM);
  const [runId, setRunId] = useState<string | null>(storedRunId);
  // The held-sheet token from the upload step; the Mode step mints the run from it. In-memory only —
  // a browser refresh before choosing a mode means re-uploading the sheet (cheap; the run isn't lost
  // because it doesn't exist yet).
  const [sheetToken, setSheetToken] = useState<string | null>(null);
  const { run, events } = useRunEvents(runId);

  const steps = buildSteps(mode, customSteps);
  const lastStep = steps.length - 1;
  const current = steps[Math.min(step, lastStep)];

  // Persist the active run so a browser refresh / reopen doesn't lose it.
  useEffect(() => {
    if (runId) localStorage.setItem(RUN_ID_KEY, runId);
    else localStorage.removeItem(RUN_ID_KEY);
  }, [runId]);

  // On first load, if a run was persisted, restore its mode + work-item form and jump to the right
  // step. If it no longer exists in the backend, drop it.
  const restored = useRef(false);
  useEffect(() => {
    if (restored.current) return;
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

        // Resume on the action step matching the run's phase (within this mode's step list).
        const keys = actionKeysFor(runMode, selected);
        const actionKey = phaseToActionKey(detail.run.current_phase);
        const indexInActions = keys.indexOf(actionKey);
        const resumeAt = indexInActions >= 0 ? 3 + indexInActions : keys.length ? 3 : 2;
        const total = 3 + keys.length + 1;
        setStep((cur) => (cur === 0 ? resumeAt : cur));
        setMaxStep(total - 1); // the run exists — let every step be navigable
      })
      .catch(() => {
        localStorage.removeItem(RUN_ID_KEY);
        setRunId(null);
      });
  }, []);

  const advance = (to: number) => {
    setStep(to);
    setMaxStep((previous) => Math.max(previous, to));
  };
  const next = () => advance(step + 1);

  const restart = () => {
    setRunId(null);
    setSheetToken(null);
    setForm(EMPTY_FORM);
    setCustomSteps([]);
    setMode('FULL_ONBOARDING');
    setStep(0);
    setMaxStep(0);
  };

  // Picking a mode is what MINTS the run (from the held sheet). If a run already exists (the operator
  // navigated back to this step), just move on — the mode is locked.
  const confirmMode = async () => {
    if (runId) {
      next();
      return;
    }
    if (!sheetToken) throw new Error('Upload the Initialisation sheet first.');
    const { run: created } = await createRunFromSheet(sheetToken, mode, customSteps);
    setSheetToken(null);
    setRunId(created.run_id);
    next();
  };

  const needsRun = ACTION_KEY_SET.has(current.key) && !runId;

  return (
    <Box fill direction="row" background="background-back">
      <Box width="320px" background="background-front" border={{ side: 'right' }} pad="medium" gap="medium" flex={false}>
        <Box gap="xxsmall">
          <Box direction="row" gap="small" align="center">
            <Box background="brand" width="14px" height="14px" round="xsmall" />
            <Text weight="bold">HPE GreenLake</Text>
          </Box>
          <Heading level={4} margin="none">
            Alletra MP B10000 Onboarding
          </Heading>
          <Text size="small" color="text-weak">
            {run ? `${run.serial_number} · ${run.status.replaceAll('_', ' ')}` : 'No active run'}
          </Text>
        </Box>
        <Box gap="xsmall">
          {steps.map((item, index) => {
            const isCurrent = index === step;
            const isDone = index < step || (index === lastStep && run?.status === 'succeeded');
            const reachable = index <= maxStep;
            return (
              <Box
                key={item.key}
                direction="row"
                gap="small"
                align="center"
                pad={{ vertical: 'xsmall', horizontal: 'small' }}
                round="xsmall"
                background={isCurrent ? 'background-contrast' : undefined}
                onClick={reachable ? () => setStep(index) : undefined}
                style={{ cursor: reachable ? 'pointer' : 'default', opacity: reachable ? 1 : 0.5 }}
              >
                <Box
                  width="26px"
                  height="26px"
                  round="full"
                  align="center"
                  justify="center"
                  background={isDone ? 'brand' : isCurrent ? 'background-contrast' : 'background-back'}
                  border={isDone ? undefined : { color: isCurrent ? 'brand' : 'border' }}
                  flex={false}
                >
                  {isDone ? <Checkmark size="small" color="white" /> : <Text size="small">{index + 1}</Text>}
                </Box>
                <Box>
                  <Text size="small" weight={isCurrent ? 'bold' : undefined}>
                    {item.title}
                  </Text>
                  <Text size="xsmall" color="text-weak">
                    {item.subtitle}
                  </Text>
                </Box>
              </Box>
            );
          })}
        </Box>
        <Box flex />
        <Text size="xsmall" color="text-weak">
          Provisioning automation · localhost only
        </Text>
      </Box>

      <Box flex overflow="auto">
        {/* flex={false}: keep natural height inside the scroll container — otherwise flexbox
            shrinks every section to fit the viewport and their contents overlap. */}
        <Box pad="large" gap="medium" width={{ max: '1100px' }} flex={false}>
          <Heading level={2} margin="none">
            {current.title}
          </Heading>

          {current.key === 'mode' && (
            <ModeStep
              mode={mode}
              custom={customSteps}
              setMode={setMode}
              setCustom={setCustomSteps}
              onConfirm={confirmMode}
              locked={!!runId}
            />
          )}
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
          {current.key === 'greenlake' && runId && (
            <GreenLakeStep runId={runId} run={run} events={events} onDone={next} />
          )}
          {current.key === 'cloudinit' && runId && (
            <CloudinitStep runId={runId} run={run} events={events} form={form} onDone={next} />
          )}
          {current.key === 'dscc' && runId && (
            <DsccStep runId={runId} run={run} events={events} dsccRegion={form.dscc_region_code} onDone={next} />
          )}
          {current.key === 'discover' && runId && (
            <DiscoveryStep runId={runId} run={run} events={events} onDone={next} />
          )}
          {current.key === 'zoning' && runId && (
            <ZoningStep runId={runId} run={run} events={events} onDone={next} />
          )}
          {current.key === 'provision' && runId && (
            <ProvisionStep runId={runId} run={run} events={events} onDone={next} />
          )}
          {current.key === 'verify' && runId && (
            <VerifyStep runId={runId} run={run} events={events} onDone={next} />
          )}
          {current.key === 'done' && <DoneStep run={run} events={events} onRestart={restart} />}
          {needsRun && <Text color="text-weak">Choose a mode first — that creates the run.</Text>}
        </Box>
      </Box>
    </Box>
  );
}
