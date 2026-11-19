import { describe, expect, it } from 'vitest';
import { actionKeysFor, MODE_PRESETS, phaseToActionKey, StepRegistry, unavailableReasons } from './modes';

// What GET /app/profile serves today (domain/workflow.py), steps and modes only.
const REGISTRY: StepRegistry = {
  steps: [
    { key: 'greenlake', label: 'GreenLake registration', kind: 'init', phase: 'PREFLIGHT', unavailable: '' },
    { key: 'cloudinit', label: 'Cloud Connectivity', kind: 'init', phase: 'CLOUDINIT_CONNECT', unavailable: '' },
    { key: 'dscc', label: 'DSCC Setup', kind: 'init', phase: 'DSCC_SETUP_SYSTEM', unavailable: '' },
    { key: 'discover', label: 'Discovery', kind: 'provision', phase: 'STORAGE_DISCOVER', unavailable: '' },
    { key: 'ports', label: 'Array ports', kind: 'provision', phase: 'STORAGE_PORTS', unavailable: '' },
    { key: 'zoning', label: 'SAN Zoning', kind: 'provision', phase: 'STORAGE_ZONING', unavailable: '' },
    { key: 'migrate', label: 'Migration', kind: 'migrate', phase: 'STORAGE_MIGRATE', unavailable: 'The Migration step is not built yet.' },
    { key: 'provision', label: 'Provision storage', kind: 'provision', phase: 'STORAGE_PROVISION', unavailable: '' },
    { key: 'replicate', label: 'Replication', kind: 'replicate', phase: 'STORAGE_REPLICATE', unavailable: '' },
    { key: 'failover_test', label: 'Failover test', kind: 'replicate', phase: 'STORAGE_FAILOVER_TEST', unavailable: '' },
    { key: 'snapshots', label: 'Snapshots', kind: 'snapshot', phase: 'STORAGE_SNAPSHOT', unavailable: '' },
    { key: 'verify', label: 'Verify configuration', kind: 'verify', phase: 'CONFIG_VERIFY', unavailable: '' },
    { key: 'asbuilt', label: 'As-built document', kind: 'verify', phase: 'ASBUILT_DOCUMENT', unavailable: '' },
  ],
  modes: {
    FULL_ONBOARDING: ['greenlake', 'cloudinit', 'dscc', 'verify', 'asbuilt'],
    PROVISION_ONLY: ['discover', 'ports', 'zoning', 'provision', 'verify', 'asbuilt'],
    BOTH: ['greenlake', 'cloudinit', 'dscc', 'discover', 'ports', 'zoning', 'provision', 'verify', 'asbuilt'],
    REPLICATE: ['discover', 'ports', 'zoning', 'provision', 'replicate', 'failover_test', 'verify', 'asbuilt'],
    MIGRATE: ['discover', 'zoning', 'migrate', 'verify', 'asbuilt'],
    VERIFY_ONLY: ['verify', 'asbuilt'],
  },
};

describe('actionKeysFor', () => {
  it('gives a preset the steps the registry serves for it', () => {
    expect(actionKeysFor(REGISTRY, 'FULL_ONBOARDING', [])).toEqual(['greenlake', 'cloudinit', 'dscc', 'verify', 'asbuilt']);
    expect(actionKeysFor(REGISTRY, 'VERIFY_ONLY', ['greenlake'])).toEqual(['verify', 'asbuilt']);
  });

  it('keeps registry order whatever order the mode lists its steps in', () => {
    const shuffled = { ...REGISTRY, modes: { ...REGISTRY.modes, PROVISION_ONLY: ['asbuilt', 'provision', 'discover'] as StepRegistry['modes'][string] } };
    expect(actionKeysFor(shuffled, 'PROVISION_ONLY', [])).toEqual(['discover', 'provision', 'asbuilt']);
  });

  it('uses the picked steps for Custom, in registry order', () => {
    expect(actionKeysFor(REGISTRY, 'CUSTOM', ['asbuilt', 'snapshots', 'greenlake'])).toEqual(['greenlake', 'snapshots', 'asbuilt']);
  });

  it('gives no steps for a mode the server does not serve', () => {
    const { MIGRATE: _dropped, ...modes } = REGISTRY.modes;
    expect(actionKeysFor({ ...REGISTRY, modes }, 'MIGRATE', [])).toEqual([]);
  });
});

describe('unavailableReasons', () => {
  it('names the not-built step of a mode that includes it', () => {
    expect(unavailableReasons(REGISTRY.steps, actionKeysFor(REGISTRY, 'MIGRATE', []))).toEqual(['The Migration step is not built yet.']);
  });

  it('leaves every built preset available, initialisation first', () => {
    for (const preset of MODE_PRESETS.filter((p) => p.mode !== 'CUSTOM' && p.mode !== 'MIGRATE')) {
      expect(unavailableReasons(REGISTRY.steps, actionKeysFor(REGISTRY, preset.mode, [])), preset.mode).toEqual([]);
    }
  });

  it('offers only presets the server serves', () => {
    const offered = MODE_PRESETS.map((p) => p.mode).filter((m) => m !== 'CUSTOM');
    expect(offered.filter((m) => !(m in REGISTRY.modes))).toEqual([]);
  });
});

describe('phaseToActionKey', () => {
  it('maps a step phase back to its step', () => {
    expect(phaseToActionKey(REGISTRY, 'STORAGE_ZONING')).toBe('zoning');
    expect(phaseToActionKey(REGISTRY, 'DSCC_SETUP_SYSTEM')).toBe('dscc');
  });

  it('resumes a GreenLake sub-phase on the GreenLake step', () => {
    expect(phaseToActionKey(REGISTRY, 'GL_ASSIGN_APPLICATION')).toBe('greenlake');
    expect(phaseToActionKey(REGISTRY, 'PREFLIGHT')).toBe('greenlake');
  });

  it('does not move the operator on a complete run or an unknown phase', () => {
    expect(phaseToActionKey(REGISTRY, 'COMPLETE')).toBeNull();
    expect(phaseToActionKey(REGISTRY, 'NOT_STARTED')).toBeNull();
  });
});
