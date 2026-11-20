import { Box, Button, DataTable, Text } from 'grommet';
import { Clone } from 'grommet-icons';
import { ReactNode, useEffect, useState } from 'react';
import {
  ArraySchedule,
  getSnapshots,
  RemovalItem,
  RunEvent,
  RunRecord,
  SnapshotAction,
  SnapshotActionState,
  SnapshotOutcome,
  SnapshotPlan,
  SnapshotResult,
  SnapshotRowCheck,
  SnapshotsTab,
  SnapshotVerification,
  snapshotsApply,
  snapshotsPreview,
  snapshotsVerify,
} from '../api';
import { isOf, latestOf } from '../events';
import { CodeBlock, Disclosure, DoneList, EmptyState, Guidance, Panel, PartsBar, Section, mono } from '../ui/blocks';
import { NotesList } from '../ui/primitives';
import { NoValue, RESULT, ResultWord, StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';
import { stepEvents } from '../ui/useStepState';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

// SPEC-023 R10, built against mockup M21 (not reviewed before it was built). The page reads what the
// step's events carry; every name, sentence and command comes from the server.
const PARTS = ['Read the array', 'Review the plan', 'Create', 'Check snapshots'];
const PREVIEW = ['snapshots.previewed', 'snapshots.preview.failed'] as const;
const APPLY = ['snapshots.applied', 'snapshots.apply.failed'] as const;
const VERIFY = ['snapshots.verified', 'snapshots.verify.failed'] as const;
// What a running step is doing, by the event that started it.
const STARTED: Record<string, string> = {
  'step.started': 'Reading the array',
  'snapshots.apply.started': 'Creating the snapshots and schedules',
  'snapshots.verify.started': 'Checking the snapshots',
};

// The shared row words (SPEC-030 R9): a plan row, then a write.
const PLAN_WORD: Record<SnapshotActionState, ResultWord> = {
  create: RESULT.create,
  exists: RESULT.already_there,
  update: RESULT.update,
  conflict: RESULT.conflict,
};
const WRITE_WORD: Record<SnapshotOutcome['status'], ResultWord> = {
  created: RESULT.created,
  exists: { state: 'not_started', label: RESULT.already_there.label },
  skipped: RESULT.skipped,
  failed: RESULT.failed,
};
const WHAT: Record<SnapshotAction['kind'], string> = { snapshot: 'Snapshot now', schedule: 'Schedule' };
// The removal set's order (SPEC-023 R6): the schedule first, so it takes no more snapshots.
const REMOVAL_ORDER: Record<string, number> = { schedule: 0, snapshot: 1 };

function latestIndex(events: RunEvent[], types: readonly string[]): number {
  for (let i = events.length - 1; i >= 0; i -= 1) if (types.includes(events[i].event_type)) return i;
  return -1;
}

const hhmm = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '');
const plural = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;

function download(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** Every apply's removal lines, each once, the schedules first (SPEC-007: a run may apply more than once). */
function removalLines(results: SnapshotResult[]): string[] {
  const items: RemovalItem[] = results.flatMap((r) => r.removals);
  const out: string[] = [];
  [...items]
    .sort((a, b) => (REMOVAL_ORDER[a.kind] ?? 9) - (REMOVAL_ORDER[b.kind] ?? 9))
    .forEach((item) => {
      if (!out.includes(item.command)) out.push(item.command);
    });
  return out;
}

function PlanTable({ plan }: { plan: SnapshotPlan }) {
  return (
    <DataTable
      columns={[
        { property: 'kind', header: 'Plan', render: (a: SnapshotAction) => <Text size="small">{WHAT[a.kind]}</Text> },
        { property: 'name', header: 'Name', render: (a: SnapshotAction) => <Text size="small" style={mono}>{a.kind === 'schedule' ? a.name : a.source}</Text> },
        { property: 'state', header: 'State', render: (a: SnapshotAction) => <StatusIndicator state={PLAN_WORD[a.state].state} label={PLAN_WORD[a.state].label} /> },
        { property: 'reason', header: 'What', render: (a: SnapshotAction) => (a.reason ? <Text size="small">{a.reason}</Text> : <NoValue />) },
      ]}
      data={plan.actions}
      primaryKey={false}
      a11yTitle="The plan: the snapshot now and the schedule of each row, with what the tool would do"
    />
  );
}

function OutcomeTable({ outcomes }: { outcomes: SnapshotOutcome[] }) {
  return (
    <DataTable
      columns={[
        { property: 'kind', header: 'Write', render: (o: SnapshotOutcome) => <Text size="small">{WHAT[o.kind]}</Text> },
        { property: 'name', header: 'Name', render: (o: SnapshotOutcome) => <Text size="small" style={mono}>{o.kind === 'schedule' ? o.name : o.source}</Text> },
        { property: 'status', header: 'Result', render: (o: SnapshotOutcome) => <StatusIndicator state={WRITE_WORD[o.status].state} label={WRITE_WORD[o.status].label} /> },
        { property: 'detail', header: 'What the array answered', render: (o: SnapshotOutcome) => (o.detail ? <Text size="small">{o.detail}</Text> : <NoValue />) },
      ]}
      data={outcomes}
      primaryKey={false}
      a11yTitle="What each write did"
    />
  );
}

function verdict(row: SnapshotRowCheck): ResultWord | null {
  if (row.verdict === 'scheduled') return { state: 'complete', label: `Scheduled, next run ${row.next_run}` };
  if (row.verdict === 'taking') return { state: 'complete', label: `Taking snapshots (${row.taken} so far)` };
  if (row.verdict === 'not_scheduled') return { state: 'failed', label: 'Not scheduled' };
  return null;
}

function CheckTable({ rows }: { rows: SnapshotRowCheck[] }) {
  return (
    <DataTable
      columns={[
        { property: 'source', header: 'Volume set or volume', render: (r: SnapshotRowCheck) => <Text size="small" style={mono}>{r.source}</Text> },
        {
          property: 'now_ok',
          header: 'Snapshot now',
          render: (r: SnapshotRowCheck) =>
            r.now_ok === null ? <NoValue /> : <StatusIndicator state={r.now_ok ? 'complete' : 'failed'} label={r.now_ok ? 'In place' : 'Not as asked'} />,
        },
        {
          property: 'verdict',
          header: 'Schedule',
          render: (r: SnapshotRowCheck) => {
            const word = verdict(r);
            return word ? <StatusIndicator state={word.state} label={word.label} /> : <NoValue />;
          },
        },
        {
          property: 'detail',
          header: 'What was read',
          render: (r: SnapshotRowCheck) => {
            const text = [r.now_detail, r.detail].filter(Boolean).join(' ');
            return text ? <Text size="small">{text}</Text> : <NoValue />;
          },
        },
      ]}
      data={rows}
      primaryKey={false}
      a11yTitle="Each row of the Snapshots tab, read back from the array"
    />
  );
}

function ScheduleTable({ schedules, mine }: { schedules: ArraySchedule[]; mine: string[] }) {
  return (
    <DataTable
      columns={[
        { property: 'name', header: 'Schedule', render: (s: ArraySchedule) => <Text size="small" style={mono}>{s.name}</Text> },
        { property: 'command', header: 'Runs', render: (s: ArraySchedule) => <Text size="small" style={mono}>{s.command}</Text> },
        { property: 'minute', header: 'Minute Hour Day Month Weekday', render: (s: ArraySchedule) => <Text size="small" style={mono}>{`${s.minute} ${s.hour} ${s.dom} ${s.month} ${s.dow}`}</Text> },
        { property: 'status', header: 'Status', render: (s: ArraySchedule) => <Text size="small">{s.status}</Text> },
        { property: 'next_run', header: 'Next run', render: (s: ArraySchedule) => (s.next_run && s.next_run !== '--' ? <Text size="small">{s.next_run}</Text> : <NoValue />) },
        { property: 'created_by', header: 'This run', render: (s: ArraySchedule) => <Text size="small">{mine.includes(s.name) ? 'Made by this run' : 'Not touched'}</Text> },
      ]}
      data={schedules}
      primaryKey={false}
      a11yTitle="The snapshot schedules on the array when it was read"
    />
  );
}

function RemovalSet({ lines, notes, runId, serial }: { lines: string[]; notes: string[]; runId: string; serial?: string }) {
  const [copied, setCopied] = useState(false);
  const header = [
    `# Removal of the snapshots and schedules run ${runId.slice(0, 8)} created on ${serial ?? 'the array'}`,
    '# Review before pasting. The tool never runs these. The schedule first, so it takes no more snapshots.',
  ];
  const text = [...header, ...lines, ''].join('\n');
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false); // clipboard blocked: the lines are on screen to select by hand
    }
  };
  return (
    <Box gap="small" flex={false}>
      {lines.length === 0 ? (
        <Text size="small" color="text-weak">Nothing to remove: this step has created nothing on the array.</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            Undoes exactly what this step created, including anything made before a failed attempt. Snapshots and schedules that were already
            there are not touched.
          </Text>
          <CodeBlock lines={[...header, ...lines]} label="The removal set" />
          <Box direction="row" gap="small">
            <Button size="small" label={copied ? 'Copied' : 'Copy'} onClick={copy} />
            <Button size="small" label="Download .txt" onClick={() => download(`snapshot_removal_${serial ?? 'array'}_${runId.slice(0, 8)}.txt`, text)} />
          </Box>
        </>
      )}
      {notes.length > 0 && <NotesList notes={notes} />}
    </Box>
  );
}

export function SnapshotsStep({ runId, run, events, onDone }: Props) {
  const { nextTitle, step } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<SnapshotsTab | null>(null);
  // The tick belongs to one plan: a new read has a new id, so it starts unticked (BL-52).
  const [authorisedFor, setAuthorisedFor] = useState<string | null>(null);

  const mine = stepEvents(step, events);
  const previewed = latestIndex(mine, PREVIEW);
  const appliedAt = latestIndex(mine, APPLY);
  const verifiedAt = latestIndex(mine, VERIFY);
  const preview = previewed >= 0 ? latestOf(mine, ...PREVIEW) : undefined;
  const plan = preview?.data?.plan ?? null;
  const array = preview?.data?.array ?? null;
  const planId = plan?.plan_id ?? '';
  const authorised = !!plan && authorisedFor === planId;
  // A result belongs to the plan on screen only while it is newer than the newest read.
  const result = appliedAt > previewed ? (latestOf(mine, ...APPLY)?.data?.result ?? null) : null;
  const verification = verifiedAt > previewed ? (latestOf(mine, ...VERIFY)?.data?.verification ?? null) : null;
  const results = mine.flatMap((e) => (isOf(e, ...APPLY) && e.data?.result ? [e.data.result] : []));
  const lines = removalLines(results);
  const removalNotes = [...new Set(results.flatMap((r) => r.removal_notes))];
  const madeHere = [...new Set(results.flatMap((r) => r.schedules_created))];

  // running here: the run is busy on this step, and its newest start has no answer yet
  const running = run?.status === 'running' && run.current_phase === step?.phase;
  const startedIndex = latestIndex(mine, Object.keys(STARTED));
  const open = startedIndex > Math.max(previewed, appliedAt, verifiedAt);
  const doing = running && open ? STARTED[mine[startedIndex].event_type] : null;
  const progress = doing ? [...mine.slice(startedIndex + 1)].reverse().find((e) => e.event_type === 'phase.progress')?.message : undefined;

  // what the server still holds: a restart or an apply withdraws the plan (LESSONS 6)
  useEffect(() => {
    let live = true;
    getSnapshots(runId)
      .then((t) => live && setTab(t))
      .catch(() => live && setTab(null));
    return () => {
      live = false;
    };
  }, [runId, previewed, appliedAt]);
  // an approval is for the plan on screen: a new read or an apply spends it
  useEffect(() => setAuthorisedFor(null), [previewed, appliedAt]);

  const call = (action: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await action();
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  };

  const count = (state: SnapshotActionState) => (plan ? plan.actions.filter((a) => a.state === state).length : 0);
  const toCreate = count('create');
  const blocked = !!plan && (!!plan.error || plan.blockers.length > 0);
  const held = !!tab && !!planId && tab.held_plan_id === planId;
  const canCreate = !!plan && !blocked && toCreate > 0 && !result;
  const arrayName = array?.name || array?.host || 'the array';
  const created = result ? result.outcomes.filter((o) => o.status === 'created').length : 0;
  const existed = result ? result.outcomes.filter((o) => o.status === 'exists').length : 0;
  const checkFailed = !!verification && (!!verification.error || verification.rows.some((r) => r.verdict === 'not_scheduled' || r.now_ok === false));

  // the parts, in order: read, plan, create, check
  const at = !plan || plan.error ? 0 : !result && !(verification && toCreate === 0) ? 1 : verification ? 3 : 2;
  const doneAll = !!verification && !checkFailed && (!result || !result.error);
  const partFailed = !!plan?.error || (blocked && !result) || !!result?.error || checkFailed;

  const next = nextTitle ? `Continue to ${nextTitle}` : 'Continue';
  const read: FooterAction = { label: plan ? 'Read the array again' : 'Read the array', busy: running && doing === STARTED['step.started'], onClick: call(() => snapshotsPreview(runId)) };
  const check: FooterAction = { label: 'Check snapshots', busy: running && doing === STARTED['snapshots.verify.started'], onClick: call(() => snapshotsVerify(runId)) };
  const proceed: FooterAction = { label: next, onClick: onDone };
  const skip: FooterAction = { label: `${next} without snapshots`, onClick: onDone };
  const create: FooterAction = {
    label: 'Create snapshots and schedules',
    busy: running && doing === STARTED['snapshots.apply.started'],
    onClick: call(() => snapshotsApply(runId, authorised ? planId : null)),
    blocked: held ? undefined : 'Read the array again: the app no longer holds this plan (it was used, or the app restarted).',
  };

  let primary: FooterAction;
  let buttons: FooterAction[];
  let readAgainInList = false;
  if (!plan || blocked || result?.error) {
    primary = read;
    buttons = [skip];
  } else if (canCreate) {
    primary = create;
    buttons = [skip];
    readAgainInList = true;
  } else {
    // created, or nothing left to create: check, then move on
    primary = verification ? proceed : check;
    buttons = verification ? [check] : [proceed];
    readAgainInList = true;
  }

  const time = (types: readonly string[]) => hhmm(mine[latestIndex(mine, types)]?.created_at);
  let status: StepStatus | undefined;
  if (doing) {
    status = { state: 'running', title: doing, message: progress };
  } else if (plan?.error) {
    status = { state: 'failed', title: 'The array could not be read', message: plan.error, time: time(PREVIEW) };
  } else if (result?.error) {
    status = { state: 'failed', title: 'Creation stopped', message: result.error, time: time(APPLY) };
  } else if (verification) {
    status = verification.error
      ? { state: 'failed', title: 'The snapshots could not be read back', message: verification.error, time: time(VERIFY) }
      : checkFailed
        ? { state: 'action_required', title: 'Not everything is as planned', message: 'The rows below say what differs. Read the array again to plan the rest.', time: time(VERIFY) }
        : {
            state: 'complete',
            title: 'Snapshots in place',
            message: verification.rows.map((r) => verdict(r)?.label).filter(Boolean).join(' · ') || 'Every snapshot now is in place.',
            time: time(VERIFY),
          };
  } else if (result) {
    status = {
      state: 'complete',
      title: `${created} created`,
      message: `${existed ? `${existed} already there. ` : ''}Check snapshots reads them back.`,
      time: time(APPLY),
    };
  } else if (blocked) {
    status = {
      state: 'failed',
      title: `${plural(plan!.blockers.length, 'finding')} to resolve`,
      message: 'Nothing can be created until they are resolved: change the Snapshots tab or the array, then read the array again.',
      time: time(PREVIEW),
    };
  } else if (plan && toCreate > 0) {
    status = { state: 'action_required', title: `Plan ready: ${toCreate} to create`, message: 'Review the plan, then tick the box next to the button.', time: time(PREVIEW) };
  } else if (plan) {
    status = { state: 'complete', title: 'Already in place', message: 'Every snapshot and schedule on the Snapshots tab is already on the array.', time: time(PREVIEW) };
  }

  const done: { text: string; state?: 'complete' | 'failed'; again?: { label: string; onClick: () => void; busy?: boolean }; detail?: ReactNode }[] = [];
  if (at > 0 && plan) {
    done.push({
      text: `Read ${arrayName} at ${time(PREVIEW)}: OS ${array?.os_version || 'not read'}, ${plural(array?.schedules.length ?? 0, 'schedule')} on it.`,
      again: readAgainInList ? { label: 'Read the array again', onClick: read.onClick!, busy: read.busy } : undefined,
    });
  }
  if (at > 1 && plan && result) {
    const calls = plan.actions.filter((a) => a.state === 'create').flatMap((a) => [a.call, `   = ${a.cli}`]);
    done.push({ text: `Plan approved: ${plural(toCreate, 'write')}.`, detail: <CodeBlock lines={calls} label="The calls of the approved plan" /> });
  }
  if (at > 2 && result) {
    done.push({ text: `Created at ${time(APPLY)}: ${created} created, ${existed} already there.`, detail: <OutcomeTable outcomes={result.outcomes} /> });
  }

  const zone = array?.time_zone ? `Times are the array's own: ${array.time_zone}.` : '';

  return (
    <StepShell
      title="Snapshots"
      description="A snapshot now of each volume set on the Snapshots tab, and a schedule the array keeps running."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      top={<PartsBar parts={PARTS} at={at} doneAll={doneAll} failed={partFailed} />}
      primary={primary}
      buttons={buttons}
      // The step's only write to the array: an explicit authorisation, not a click (LESSONS 7).
      confirmation={
        canCreate
          ? {
              label: `I have reviewed this plan and authorise creating these snapshots and schedules on ${arrayName}. The schedules keep running after this run ends.`,
              checked: authorised,
              onChange: (on: boolean) => setAuthorisedFor(on ? planId : null),
            }
          : undefined
      }
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step does',
              body: 'Takes one read-only snapshot of each volume now, named <volume>.initial, and sets up a schedule on the array that takes more and lets each expire after Keep for.',
            },
            {
              title: 'The schedule keeps running',
              body: 'After this run ends the array keeps taking snapshots until someone removes the schedule. The removal set starts with that line.',
            },
            {
              title: 'Nothing is written until you approve',
              body: 'Reading and the plan change nothing. Only Create snapshots and schedules writes, and only what the plan shows.',
            },
            {
              title: 'Schedules already there',
              body: 'Schedules this run did not make are listed and never changed, suspended or removed. A same-named one is a conflict.',
            },
          ]}
        />
      }
    >
      {!plan && !doing && (
        <Box flex={false}>
          <EmptyState icon={<Clone size="large" color="icon-weak" />} title="Not read yet">
            Read the array to see its volume sets, the snapshots they already have and the schedules on it. Reading changes nothing.
          </EmptyState>
        </Box>
      )}

      {done.length > 0 && (
        <Box flex={false}>
          <DoneList items={done} />
        </Box>
      )}

      {at === 1 && plan && (
        <Panel title="Review the plan" right={<Text size="small" color="text-weak">{`${toCreate} to create · ${count('exists')} already there · ${count('conflict')} conflict${count('conflict') === 1 ? '' : 's'}`}</Text>} description={zone || undefined}>
          {plan.actions.length > 0 && <PlanTable plan={plan} />}
          {plan.blockers.length > 0 && <NotesList notes={plan.blockers} />}
          {/* above the tick: what the array would have asked, and that the schedule keeps writing (SPEC-023 R4) */}
          {plan.notes.length > 0 && <NotesList notes={plan.notes} />}
          {toCreate > 0 && (
            <Disclosure label="the calls" count={toCreate}>
              <CodeBlock lines={plan.actions.filter((a) => a.state === 'create').flatMap((a) => [a.call, `   = ${a.cli}`])} label="The calls of the plan" />
            </Disclosure>
          )}
        </Panel>
      )}

      {at === 2 && result && (
        <Panel title="Create">
          <OutcomeTable outcomes={result.outcomes} />
          {result.notes.length > 0 && <NotesList notes={result.notes} />}
        </Panel>
      )}

      {at === 3 && verification && !verification.error && (
        <Panel title="Check snapshots">
          <CheckTable rows={verification.rows} />
          {verification.notes.length > 0 && <NotesList notes={verification.notes} />}
        </Panel>
      )}

      {results.length > 0 && (
        // open by itself only after a failed create: then it is what to act on (SPEC-030 R6)
        <Box flex={false} key={result?.error ? `open-${appliedAt}` : 'folded'}>
          <Section title="To remove what this step created" summary="The schedule first, so it takes no more snapshots" open={!!result?.error}>
            <RemovalSet lines={lines} notes={removalNotes} runId={runId} serial={run?.serial_number} />
          </Section>
        </Box>
      )}

      {tab && tab.rows.length > 0 && (
        <Box flex={false}>
          <Section title="What the workbook asks for" summary={[plural(tab.rows.length, 'row'), zone].filter(Boolean).join(' · ')}>
            <DataTable
              columns={[
                { property: 'source', header: 'Volume set or volume', render: (r) => <Text size="small" style={mono}>{r.source}</Text> },
                { property: 'kind', header: 'Kind', render: (r) => <Text size="small">{r.kind}</Text> },
                { property: 'summary', header: 'Asks for', render: (r) => <Text size="small">{r.summary}</Text> },
                { property: 'schedule', header: 'Schedule name', render: (r) => (r.schedule ? <Text size="small" style={mono}>{r.schedule}</Text> : <NoValue />) },
              ]}
              data={tab.rows}
              primaryKey={false}
              a11yTitle="The rows of the Snapshots tab"
            />
          </Section>
        </Box>
      )}

      {array && array.schedules.length > 0 && (
        <Box flex={false}>
          <Section title={`Schedules on ${arrayName}`} summary={`${plural(array.schedules.length, 'schedule')} when it was read`}>
            <ScheduleTable schedules={array.schedules} mine={madeHere} />
          </Section>
        </Box>
      )}
    </StepShell>
  );
}
