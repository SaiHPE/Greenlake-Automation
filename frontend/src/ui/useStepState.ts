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
  /** Report-only events that must not influence the step's state at all. */
  ignore?: string[];
}

// Event types that decide a step's state, per step. Anything matching FAILURE is a failure for any
// step. Events are scanned newest-first, so a retry always overrides an earlier verdict.
//
// Only events that genuinely END a step belong here. Report-only artifacts must NOT: the zoning plan
// and the tier-2 path verification are produced after their step's outcome is already decided, and
// listing them would make a finished step report Action required again. Path verification in
// particular never gates the run (ADR 0010).
const SIGNALS: Record<string, Signals> = {
  greenlake: { complete: ['step.completed'], gate: [] },
  cloudinit: { complete: ['step.completed'], gate: ['operator.review_ready'] },
  dscc: { complete: [], gate: ['operator.credentials_ready'] },
  discover: { complete: ['discover.completed'], gate: [] },
  zoning: { complete: ['zoning.proper'], gate: ['zoning.previewed'], ignore: ['zoning.plan'] },
  provision: {
    complete: ['storage.applied'],
    gate: ['storage.previewed'],
    // Tier-2 path verification reports; it never decides the provisioning step, not even when it
    // cannot run (ADR 0010). Its results are shown in their own panel.
    ignore: ['storage.paths.checking', 'storage.paths.verified', 'storage.paths.failed'],
  },
  verify: { complete: ['verify.completed'], gate: [] },
  asbuilt: { complete: ['asbuilt.generated'], gate: [] },
};
const DEFAULT_SIGNALS: Signals = { complete: ['step.completed'], gate: [] };

const FAILURE = /(failed|crashed|stalled)/;
const ACTIVE = /(started|progress|checking)/;

/**
 * The one mapping from a persisted run status to the shared vocabulary. Used for the run as a whole
 * and for the step the run is currently on. Note `ready` is the IDLE status — it is what a new run
 * gets and what every step returns to on success — so it is not "running".
 */
export function runStatusToState(status: string): StepState {
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
    const event = mine[i];
    const type = event.event_type;
    if (signals.ignore?.includes(type)) continue;
    if (FAILURE.test(type)) return 'failed';
    if (signals.complete.includes(type)) {
      // A GreenLake dry run reports step.completed too, but nothing was written, so the step is not
      // done. The live run emits from GL_VERIFY_DEVICE; the dry run stays on PREFLIGHT.
      if (step.key === 'greenlake' && event.phase === 'PREFLIGHT') return 'not_started';
      // Discovery and zoning report completion even when the read itself failed; the error is in the
      // payload, and the step component already surfaces it.
      if (event.data?.report?.error) return 'failed';
      return 'complete';
    }
    if (signals.gate.includes(type)) return 'action_required';
    if (ACTIVE.test(type)) return 'running';
  }

  if (run && owns(step, run.current_phase)) return runStatusToState(run.status);
  return 'not_started';
}

/**
 * A short result summary for the step rail, e.g. "4 ports · 6 adapters".
 *
 * Derived from the SAME newest state-deciding event as the state itself. Asking "did this event
 * ever happen" instead would let the rail say "verified on both fabrics" next to Action required
 * after a re-verify, or "document ready" next to Failed after a failed regeneration.
 */
export function deriveStepHint(step: ServedStep, run: RunRecord | null, events: RunEvent[]): string {
  const signals = SIGNALS[step.key] ?? DEFAULT_SIGNALS;
  const mine = events.filter((event) => owns(step, event.phase));

  const deciding = [...mine]
    .reverse()
    .find(
      (event) =>
        !signals.ignore?.includes(event.event_type) &&
        (FAILURE.test(event.event_type) ||
          signals.complete.includes(event.event_type) ||
          signals.gate.includes(event.event_type)),
    );
  if (!deciding) return '';

  const report = deciding.data?.report;
  const list = (value: unknown) => (Array.isArray(value) ? value : []);

  switch (deciding.event_type) {
    case 'discover.completed':
      if (report?.error) return 'read failed';
      return `${list(report?.array_ports).length} ports · ${list(report?.host_hbas).length} adapters`;
    case 'zoning.proper':
      return 'verified on both fabrics';
    case 'zoning.previewed': {
      const missing = list(report?.expected).filter((zone: { present: boolean }) => !zone.present).length;
      return missing ? `${missing} zone${missing === 1 ? '' : 's'} outstanding` : '';
    }
    case 'storage.applied':
      return 'objects created';
    case 'storage.previewed':
      return 'awaiting approval';
    case 'verify.completed': {
      const mismatches = list(report?.checks).filter((check: { status: string }) => check.status !== 'pass').length;
      return mismatches ? `${mismatches} to review` : 'configuration matches';
    }
    case 'asbuilt.generated':
      return 'document ready';
    default:
      return '';
  }
}

/** Live state for one step. */
export function useStepState(step: ServedStep | undefined, run: RunRecord | null, events: RunEvent[]) {
  return useMemo(() => {
    if (!step) return { state: 'not_started' as StepState, hint: '' };
    return { state: deriveStepState(step, run, events), hint: deriveStepHint(step, run, events) };
  }, [step, run, events]);
}
