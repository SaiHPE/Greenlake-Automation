import { describe, expect, it } from 'vitest';
import type { FabricZoningApplyPlan, RunEvent, ZoningApplyResult } from '../api';
import type { ServedStep } from '../modes';
import { deriveStepHint, deriveStepState } from './useStepState';
import { zoningApprovalLabel, zoningRemovalBlocks, zoningRemovalText } from './zoningApplyHelpers';

const ZONING_STEP: ServedStep = {
  key: 'zoning',
  label: 'SAN Zoning',
  kind: 'provision',
  phase: 'STORAGE_ZONING',
  unavailable: '',
};

const EMPTY_RESULT: ZoningApplyResult = { plan_id: 'p1', error: null, fabrics: [] };

const mkEvent = (event_type: 'zoning.apply.started' | 'zoning.applied' | 'zoning.apply.failed'): RunEvent => {
  const base = {
    event_id: `ev-${event_type}`,
    run_id: 'r1',
    phase: 'STORAGE_ZONING' as const,
    message: event_type,
    created_at: '2026-11-27T10:00:00Z',
  };
  if (event_type === 'zoning.apply.started') {
    return { ...base, event_type, data: {} };
  }
  return { ...base, event_type, data: { result: EMPTY_RESULT } };
};

describe('zoningApplyHelpers', () => {
  it('formats the opt-in approval label naming configs and switches', () => {
    const fabrics: FabricZoningApplyPlan[] = [
      {
        fabric: 'odd',
        switch_host: '10.132.30.111',
        active_cfg: 'F1_CFG',
        aliases: { h1: '10:00:00:00:00:00:00:01' },
        zones: { z1: ['h1', 'a1'] },
        commands: [],
        removals: [],
      },
      {
        fabric: 'even',
        switch_host: '10.132.30.112',
        active_cfg: 'F2_CFG',
        aliases: {},
        zones: { z2: ['h2', 'a2'] },
        commands: [],
        removals: [],
      },
    ];
    expect(zoningApprovalLabel(fabrics)).toBe(
      'I have reviewed these Brocade commands and authorise creating these aliases and zones and activating F1_CFG, F2_CFG on 10.132.30.111, 10.132.30.112.',
    );
  });

  it('merges removal commands into one valid sequence per switch with one closing cfgenable at the end', () => {
    const res1: ZoningApplyResult = {
      plan_id: 'p1',
      error: null,
      fabrics: [
        {
          fabric: 'even',
          switch_host: '10.132.30.112',
          active_cfg: 'F2_CFG',
          status: 'applied',
          error: null,
          outcomes: [],
          verified_zones: ['z1'],
          missing_zones: [],
          transaction_aborted: false,
          removals: ['cfgremove "F2_CFG","z1"', 'zonedelete "z1"', 'alidelete "a1"', 'cfgenable "F2_CFG" -f'],
        },
        {
          fabric: 'odd',
          switch_host: '10.132.30.111',
          active_cfg: 'F1_CFG',
          status: 'applied',
          error: null,
          outcomes: [],
          verified_zones: ['z_f1'],
          missing_zones: [],
          transaction_aborted: false,
          removals: ['cfgremove "F1_CFG","z_f1"', 'zonedelete "z_f1"', 'cfgenable "F1_CFG" -f'],
        },
      ],
    };
    const res2: ZoningApplyResult = {
      plan_id: 'p2',
      error: null,
      fabrics: [
        {
          fabric: 'even',
          switch_host: '10.132.30.112',
          active_cfg: 'F2_CFG',
          status: 'applied',
          error: null,
          outcomes: [],
          verified_zones: ['z2'],
          missing_zones: [],
          transaction_aborted: false,
          removals: ['cfgremove "F2_CFG","z2"', 'zonedelete "z2"', 'alidelete "a1"', 'cfgenable "F2_CFG" -f'],
        },
      ],
    };
    const blocks = zoningRemovalBlocks([res1, res2]);
    expect(blocks).toHaveLength(2);
    expect(blocks[0].lines).toEqual([
      'cfgremove "F2_CFG","z2"',
      'cfgremove "F2_CFG","z1"',
      'zonedelete "z2"',
      'zonedelete "z1"',
      'alidelete "a1"',
      'cfgenable "F2_CFG" -f',
    ]);
    expect(blocks[1].lines).toEqual([
      'cfgremove "F1_CFG","z_f1"',
      'zonedelete "z_f1"',
      'cfgenable "F1_CFG" -f',
    ]);
    const txt = zoningRemovalText([res1, res2], '12345678abcd');
    expect(txt).toContain('# Fabric F2 (even) — switch 10.132.30.112 — cfg F2_CFG');
    expect(txt.trimEnd().endsWith('cfgenable "F1_CFG" -f')).toBe(true);
  });
});

describe('useStepState zoning apply transitions', () => {
  it('treats zoning.apply.started as running, zoning.applied as action_required, and zoning.apply.failed as failed', () => {
    expect(deriveStepState(ZONING_STEP, null, [mkEvent('zoning.apply.started')])).toBe('running');
    expect(deriveStepState(ZONING_STEP, null, [mkEvent('zoning.apply.started'), mkEvent('zoning.applied')])).toBe(
      'action_required',
    );
    expect(deriveStepHint(ZONING_STEP, null, [mkEvent('zoning.applied')])).toBe('applied on switches · re-check');
    expect(deriveStepState(ZONING_STEP, null, [mkEvent('zoning.apply.failed')])).toBe('failed');
    expect(deriveStepHint(ZONING_STEP, null, [mkEvent('zoning.apply.failed')])).toBe('stopped during switch apply');
  });
});
