import { Anchor, Box, Button, Grid, Heading, PageHeader, ResponsiveContext, Text } from 'grommet';
import { Document, Download, LinkPrevious, Storage, Terminal } from 'grommet-icons';
import { ReactNode, useContext, useEffect, useState } from 'react';
import { asbuiltDownloadUrl, consoleLogTxtUrl, listRuns, RunEvent, RunRecord } from '../api';
import { DocList, DocItem, EmptyState, StatusLine } from './blocks';
import { StatusIcon, StepState } from './status';
import { runStatusToState } from './useStepState';

/** "Today, 19:31", "Yesterday, 08:12" or "5 Oct 2026": relative while recent, the date once it is not. */
export function when(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return `Today, ${time}`;
  if (d.toDateString() === yesterday.toDateString()) return `Yesterday, ${time}`;
  return d.toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
}

function saveText(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/** A page that is not a step: the Design System PageHeader, a parent link on child pages only. */
export function PlainPage({
  title,
  subtitle,
  parent,
  actions,
  children,
}: {
  title: string;
  subtitle?: string;
  parent?: { label: string; onClick: () => void };
  actions?: JSX.Element;
  children: ReactNode;
}) {
  const size = useContext(ResponsiveContext);
  const pad = size === 'large' || size === 'xlarge' ? 'large' : 'medium';
  return (
    <Box pad={{ horizontal: pad, bottom: 'large' }} gap="medium" width={{ max: 'xxlarge' }} flex={false}>
      <PageHeader
        title={title}
        subtitle={subtitle}
        parent={parent ? <Anchor label={parent.label} icon={<LinkPrevious />} onClick={parent.onClick} /> : undefined}
        actions={actions}
        size="small"
        pad={{ vertical: 'medium' }}
      />
      {children}
    </Box>
  );
}

type Group = 'you' | 'running' | 'open' | 'done';
const GROUPS: { key: Group; title: string }[] = [
  { key: 'you', title: 'Needs you' },
  { key: 'running', title: 'Running' },
  { key: 'open', title: 'Open' },
  { key: 'done', title: 'Done' },
];
const groupOf = (state: StepState): Group =>
  state === 'action_required' || state === 'failed' ? 'you' : state === 'running' ? 'running' : state === 'complete' ? 'done' : 'open';
const STATUS_TEXT: Record<StepState, string> = {
  action_required: 'Waiting for you',
  failed: 'Stopped',
  running: 'Running',
  waiting: 'Waiting on others',
  complete: 'Done',
  not_started: 'Open',
};

/** Every run this tool holds, grouped by who has to act next (replaces the "Open another run" dialog). */
export function Home({
  currentRunId,
  modeLabel,
  phaseLabel,
  onOpen,
  onNewRun,
}: {
  currentRunId: string | null;
  modeLabel: (mode: string) => string;
  phaseLabel: (phase: string) => string;
  onOpen: (runId: string) => void;
  onNewRun: () => void;
}) {
  const [runs, setRuns] = useState<RunRecord[] | null>(null);
  useEffect(() => {
    listRuns()
      .then(({ runs: list }) => setRuns([...list].sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1))))
      .catch(() => setRuns([]));
  }, []);

  return (
    <Box flex overflow="auto">
      <PlainPage
        title="Your runs"
        subtitle={runs ? `${runs.length} run${runs.length === 1 ? '' : 's'} on this workstation, newest first` : undefined}
        actions={<Button primary label="Start a new run" onClick={onNewRun} />}
      >
        {runs === null && <Text color="text-weak">Reading runs.</Text>}
        {runs !== null && runs.length === 0 && (
          <EmptyState icon={<Storage size="large" color="icon-weak" />} title="No runs yet">
            Start a new run: check the prerequisites, upload the initialisation sheet, and choose what to do.
          </EmptyState>
        )}
        {runs !== null && runs.length > 0 && (
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
            {GROUPS.map((g) => {
              const rows = runs.filter((r) => groupOf(runStatusToState(r.status)) === g.key);
              if (!rows.length) return null;
              return (
                <Box key={g.key} flex={false} as="section" aria-label={`${g.title}: ${rows.length}`}>
                  <Box direction="row" gap="small" align="center" pad={{ horizontal: 'medium', vertical: 'xsmall' }} background="background-contrast">
                    <Heading level={2} size="xsmall" weight={500} margin="none">
                      {g.title}
                    </Heading>
                    <Text size="small" color="text-weak">
                      {rows.length}
                    </Text>
                  </Box>
                  {rows.map((r) => {
                    const state = runStatusToState(r.status);
                    const current = r.run_id === currentRunId;
                    return (
                      <Box
                        key={r.run_id}
                        direction="row"
                        gap="medium"
                        align="center"
                        pad={{ horizontal: 'medium', vertical: 'small' }}
                        border={{ side: 'top', color: 'border-weak' }}
                      >
                        <StatusIcon state={state} />
                        <Box basis="1/3" flex={false}>
                          <Text size="small" weight={500} color="text-strong">
                            {r.serial_number}
                            {current ? ' (open now)' : ''}
                          </Text>
                          <Text size="xsmall" color="text-weak">
                            {modeLabel(r.mode)} · run {r.run_id.slice(0, 8)}
                          </Text>
                        </Box>
                        <Box flex>
                          <Text size="small">{STATUS_TEXT[state]}</Text>
                          <Text size="xsmall" color="text-weak">
                            {phaseLabel(r.current_phase)}
                          </Text>
                        </Box>
                        <Box width="small" flex={false} align="end">
                          <Text size="small" color="text-weak" textAlign="end">
                            {when(r.updated_at)}
                          </Text>
                        </Box>
                        <Button
                          size="small"
                          label={state === 'complete' ? 'Open' : 'Continue'}
                          a11yTitle={`${state === 'complete' ? 'Open' : 'Continue'} the run for ${r.serial_number}`}
                          onClick={() => onOpen(r.run_id)}
                        />
                      </Box>
                    );
                  })}
                </Box>
              );
            })}
          </Box>
        )}
      </PlainPage>
    </Box>
  );
}

/** The files a run produces, for Run overview and the Done page. */
export function runDocuments(runId: string, run: RunRecord | null, events: RunEvent[]): DocItem[] {
  const zoning = [...events].reverse().find((e) => e.event_type === 'zoning.rendered');
  const zoningCommands = (zoning?.data?.commands ?? {}) as Record<string, string[]>;
  const zoningLines = Object.values(zoningCommands).reduce((n, c) => n + c.length, 0);
  const asbuilt = [...events].reverse().find((e) => e.event_type === 'asbuilt.generated');
  return [
    asbuilt
      ? {
          icon: <Document />,
          name: 'As-built document',
          detail: `Generated ${when(asbuilt.created_at)} · for the customer`,
          action: <Button size="small" label="Download" href={asbuiltDownloadUrl(runId)} />,
        }
      : { icon: <Document />, name: 'As-built document', detail: 'Generated at the As-built step', pending: 'Not yet' },
    {
      icon: <Terminal />,
      name: 'Command log',
      detail: 'Every command this run sent, with what each device answered',
      action: <Button size="small" label="Download" href={consoleLogTxtUrl(runId)} />,
    },
    zoning
      ? {
          icon: <Download />,
          name: 'Zoning command set',
          detail: `${zoningLines} line${zoningLines === 1 ? '' : 's'} for the SAN team · generated ${when(zoning.created_at)}`,
          action: (
            <Button
              size="small"
              label="Download"
              onClick={() =>
                saveText(
                  `zoning_${run?.serial_number ?? 'array'}_${runId.slice(0, 8)}.txt`,
                  Object.entries(zoningCommands)
                    .filter(([, lines]) => lines.length)
                    .flatMap(([fabric, lines]) => [`# ---- ${fabric}`, ...lines, ''])
                    .join('\n'),
                )
              }
            />
          ),
        }
      : { icon: <Download />, name: 'Zoning command set', detail: 'Generated at the SAN zoning step', pending: 'Not yet' },
  ];
}

export interface OverviewStep {
  key: string;
  label: string;
  state: StepState;
  hint?: string;
  lastAt?: string;
}

const NEXT_SENTENCE: Record<StepState, (label: string) => string> = {
  action_required: (l) => `Waiting for you at ${l}.`,
  failed: (l) => `${l} stopped. Open it to see what the device said and what to do.`,
  running: (l) => `${l} is running.`,
  waiting: (l) => `${l} is waiting on another team.`,
  not_started: (l) => `Next: ${l}.`,
  complete: () => 'Every step of this run is done.',
};

/** One page with every step of the run: what has run, what is next, and the files it produced. */
export function RunOverview({
  runId,
  run,
  events,
  steps,
  modeLabel,
  onOpenStep,
  onHome,
}: {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  steps: OverviewStep[];
  modeLabel: string;
  onOpenStep: (key: string) => void;
  onHome: () => void;
}) {
  const size = useContext(ResponsiveContext);
  const columns = size === 'xsmall' ? 1 : size === 'small' ? 2 : 3;
  const begun = steps.filter((s) => s.state !== 'not_started');
  const todo = steps.filter((s) => s.state === 'not_started');
  const next = steps.find((s) => s.state !== 'complete');
  const created = events.find((e) => e.event_type === 'run.created');
  const docs = runDocuments(runId, run, events);

  return (
    <PlainPage
      title={run?.serial_number ?? 'This run'}
      subtitle={`${modeLabel}${created ? ` · started ${when(created.created_at)}` : ''} · ${steps.length} steps`}
      parent={{ label: 'Your runs', onClick: onHome }}
      actions={next ? <Button primary label={`Continue at ${next.label}`} onClick={() => onOpenStep(next.key)} /> : undefined}
    >
      <StatusLine state={next ? (next.state === 'not_started' ? 'not_started' : next.state) : 'complete'}>
        {next ? NEXT_SENTENCE[next.state](next.label) : NEXT_SENTENCE.complete('')}
      </StatusLine>
      {begun.length > 0 && (
        <Grid columns={{ count: columns, size: 'auto' }} gap="small" as="ul" style={{ margin: 0, padding: 0 }}>
          {begun.map((s) => (
            <Box
              as="li"
              key={s.key}
              background="background-front"
              round="small"
              border={{ color: s.key === next?.key ? 'border-selected' : 'border-weak', size: s.key === next?.key ? 'medium' : 'xsmall' }}
              pad="medium"
              gap="xsmall"
              style={{ listStyle: 'none' }}
            >
              <Box direction="row" justify="between" align="center" gap="small">
                <Box direction="row" gap="small" align="center">
                  <StatusIcon state={s.state} />
                  <Heading level={2} size="xsmall" weight={500} margin="none">
                    {s.label}
                  </Heading>
                </Box>
                {s.lastAt && (
                  <Text size="xsmall" color="text-weak" textAlign="end">
                    {when(s.lastAt)}
                  </Text>
                )}
              </Box>
              {s.hint && (
                <Text size="small" color="text-weak">
                  {s.hint}
                </Text>
              )}
              <Anchor size="small" label={`Open ${s.label}`} onClick={() => onOpenStep(s.key)} />
            </Box>
          ))}
        </Grid>
      )}
      {todo.length > 0 && (
        <Box background="background-front" round="small" border={{ color: 'border-weak' }} pad={{ horizontal: 'medium', vertical: 'small' }} flex={false} gap="xxsmall">
          <Heading level={2} size="xsmall" weight={500} margin="none">
            Still to do
          </Heading>
          <Text size="small" color="text-weak">
            {todo.map((s) => s.label).join('  →  ')}
          </Text>
        </Box>
      )}
      <Box gap="small" flex={false}>
        <Heading level={2} size="small" margin="none">
          Documents and logs
        </Heading>
        <DocList items={docs} label="Documents and logs of this run" />
      </Box>
    </PlainPage>
  );
}
