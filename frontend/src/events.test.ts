import { describe, expect, it } from 'vitest';
import type { EventOf, RunEvent } from './api';
import { isOf, latestOf } from './events';

const plain = (id: string, event_type: EventOf<'step.started' | 'step.completed'>['event_type'], message: string): RunEvent => ({
  event_id: id,
  run_id: 'run-1',
  phase: 'STORAGE_PROVISION',
  event_type,
  message,
  created_at: '2026-11-21T00:00:00Z',
  data: {},
});

const failoverStart = (id: string, group: string): RunEvent => ({
  event_id: id,
  run_id: 'run-1',
  phase: 'STORAGE_FAILOVER_TEST',
  event_type: 'failover.started',
  message: `starting ${group}`,
  created_at: '2026-11-21T00:00:00Z',
  data: { group },
});

describe('events narrowing helpers', () => {
  it('latestOf returns the newest matching event and skips non-matching types', () => {
    const list: RunEvent[] = [
      failoverStart('1', 'rc_first'),
      plain('2', 'step.started', 'other'),
      failoverStart('3', 'rc_second'),
      plain('4', 'step.completed', 'done'),
    ];
    const hit = latestOf(list, 'failover.started');
    expect(hit?.event_id).toBe('3');
    expect(hit?.data.group).toBe('rc_second');
    expect(latestOf(list, 'storage.previewed')).toBeUndefined();
  });

  it('isOf narrows matching types and returns false for another type', () => {
    const ev = failoverStart('1', 'rc_group');
    expect(isOf(ev, 'failover.started')).toBe(true);
    expect(isOf(ev, 'step.started', 'step.completed')).toBe(false);
    if (isOf(ev, 'failover.started')) {
      expect(ev.data.group).toBe('rc_group');
    }
  });
});
