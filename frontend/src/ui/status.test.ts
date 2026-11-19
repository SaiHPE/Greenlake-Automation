import { describe, expect, it } from 'vitest';
import { RESULT, stateLabel, StepState } from './status';

const STATES: StepState[] = ['not_started', 'running', 'action_required', 'waiting', 'complete', 'failed'];

describe('the status vocabulary', () => {
  it('has one word per state', () => {
    expect(STATES.map(stateLabel)).toEqual(['Not started', 'Running', 'Action required', 'Waiting on others', 'Complete', 'Failed']);
  });

  it('never draws one result word with two different states', () => {
    const seen = new Map<string, StepState>(STATES.map((state) => [stateLabel(state), state]));
    for (const [key, word] of Object.entries(RESULT)) {
      const earlier = seen.get(word.label);
      expect(earlier === undefined || earlier === word.state, `${key}: "${word.label}"`).toBe(true);
      seen.set(word.label, word.state);
    }
  });

  it('shows a report as amber or grey, never red', () => {
    // No path is a report, never a gate; Already there and Not on fabric are left alone.
    expect(RESULT.no_path.state).toBe('action_required');
    expect(RESULT.partial.state).toBe('action_required');
    expect(RESULT.not_on_fabric.state).toBe('not_started');
    expect(RESULT.not_checked.state).toBe('not_started');
  });

  it('draws a problem the operator must fix in red', () => {
    for (const word of [RESULT.failed, RESULT.blocked, RESULT.not_zoned, RESULT.conflict, RESULT.not_replicating]) {
      expect(word.state, word.label).toBe('failed');
    }
  });
});
