import { useMemo } from 'react';
import { RunEvent, RunRecord } from '../api';
import { ServedStep } from '../modes';
import { StepState } from './status';

/**
 * The single progress model.
 *
 * Before this, six step components each derived "is it running / done / failed" from their own
 * reading of `run.status`, while Verify and As-built derived it from event types instead (their
 * backend steps deliberately never touch run status). Two models disagreed at the edges. This is
 * the one place that answers the question, for every step.
 *
 * A step's own events are the primary evidence — they record what actually happened. The run record
 * is consulted only for the step the run is currently on, to catch "running" before its first event
 * lands.
 */

/** Which workflow phases belong to a step. GreenLake spans the whole GL_* chain from PREFLIGHT. */
export function owns(step: ServedStep, phase: string): boolean {
  if (phase === step.phase) return true;
  return step.phase === 'PREFLIGHT' && phase.startsWith('GL_');
}

/** The events a step produced — the activity timeline and every derivation read through this. */
export function stepEvents(step: ServedStep | undefined, events: RunEvent[]): RunEvent[] {
  if (!step) return [];
  return events.filter((event) => owns(step, event.phase));
}

interface Signals {
  complete: string[];
  gate: string[];
}

// Event types that end a step, per step. Anything matching FAILURE below is a failure for any step.
const SIGNALS: Record<string, Signals> = {
  greenlake: { complete: ['step.completed'], gate: [] },
  cloudinit: { complete: ['step.completed'], gate: ['operator.review_ready'] },
  dscc: { complete: [], gate: ['operator.credentials_ready'] },
  discover: { complete: ['discover.completed'], gate: [] },
  zoning: { complete: ['zoning.proper'], gate: ['zoning.previewed', 'zoning.plan'] },
  provision: { complete: ['storage.applied'], gate: ['storage.previewed', 'storage.paths.verified'] },
  verify: { complete: ['verify.completed'], gate: [] },
  asbuilt: { complete: ['asbuilt.generated'], gate: [] },
};
const DEFAULT_SIGNALS: Signals = { complete: ['step.completed'], gate: [] };

const FAILURE = /(failed|crashed|stalled)/;
const ACTIVE = /(started|progress|checking)/;

function fromRunStatus(status: string): StepState {
  if (status === 'running') return 'running';
  if (status === 'waiting_for_operator') return 'action_required';
  if (status === 'retryable_failure' || status === 'terminal_failure') return 'failed';
  if (status === 'succeeded') return 'complete';
  return 'not_started';
}

export function deriveStepState(step: ServedStep, run: RunRecord | null, events: RunEvent[]): StepState {
  // DSCC hands off to the operator inside the cloud console; the run is marked complete afterwards,
  // and that confirmation is the only signal that the step finished.
  if (step.key === 'dscc' && run && (run.status === 'succeeded' || run.current_phase === 'COMPLETE')) {
    return 'complete';
  }

  const signals = SIGNALS[step.key] ?? DEFAULT_SIGNALS;
  const mine = events.filter((event) => owns(step, event.phase));

  for (let i = mine.length - 1; i >= 0; i -= 1) {
    const type = mine[i].event_type;
    if (FAILURE.test(type)) return 'failed';
    if (signals.complete.includes(type)) return 'complete';
    if (signals.gate.includes(type)) return 'action_required';
    if (ACTIVE.test(type)) return 'running';
  }

  if (run && owns(step, run.current_phase)) return fromRunStatus(run.status);
  return 'not_started';
}

/** A short result summary for the step rail, e.g. "4 ports · 6 adapters". Empty when there is none. */
export function deriveStepHint(step: ServedStep, run: RunRecord | null, events: RunEvent[]): string {
  const mine = events.filter((event) => owns(step, event.phase));
  const latest = (type: string) => [...mine].reverse().find((event) => event.event_type === type);

  if (step.key === 'discover') {
    const report = latest('discover.completed')?.data?.report;
    if (report) return `${report.array_ports?.length ?? 0} ports · ${report.host_hbas?.length ?? 0} adapters`;
  }
  if (step.key === 'zoning') {
    if (latest('zoning.proper')) return 'verified on both fabrics';
    const report = latest('zoning.previewed')?.data?.report;
    if (report) {
      const missing = (report.expected ?? []).filter((zone: { present: boolean }) => !zone.present).length;
      return missing ? `${missing} zone${missing === 1 ? '' : 's'} outstanding` : '';
    }
  }
  if (step.key === 'provision') {
    if (latest('storage.applied')) return 'objects created';
    if (latest('storage.previewed')) return 'awaiting approval';
  }
  if (step.key === 'verify') {
    const report = latest('verify.completed')?.data?.report;
    if (report) {
      const mismatches = (report.checks ?? []).filter((check: { status: string }) => check.status !== 'pass').length;
      return mismatches ? `${mismatches} discrepancy` : 'configuration matches';
    }
  }
  if (step.key === 'asbuilt' && latest('asbuilt.generated')) return 'document ready';
  return '';
}

/** Live state for one step. */
export function useStepState(step: ServedStep | undefined, run: RunRecord | null, events: RunEvent[]) {
  return useMemo(() => {
    if (!step) return { state: 'not_started' as StepState, hint: '' };
    return { state: deriveStepState(step, run, events), hint: deriveStepHint(step, run, events) };
  }, [step, run, events]);
}
