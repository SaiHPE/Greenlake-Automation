// Decoupling (docs/adr/0005 + 0011): the operator picks a MODE up front, and the wizard renders only
// the steps that mode needs. The step registry (keys, labels, kinds, phases) and the mode→steps map
// are SERVED by the backend (GET /app/profile — single source of truth: domain/workflow.py). This
// module keeps only presentation extras (subtitles, mode labels/blurbs) and helpers over served data.

import type { AppProfile, RunRecord } from './api';

export type RunMode = RunRecord['mode'];
// One step as served by GET /app/profile (unavailable is '' when the step can run).
export type ServedStep = AppProfile['steps'][number];
export type ActionKey = ServedStep['key'];

/** Registry step kinds, mapped to the deployment stages the rail groups the steps by. */
export const STAGE: Record<ServedStep['kind'], string> = {
  init: 'Initialize', provision: 'Provision', replicate: 'Replicate', migrate: 'Migrate', snapshot: 'Protect', verify: 'Document',
};

export interface StepRegistry {
  steps: ServedStep[];
  modes: Record<string, ActionKey[]>;
}

// Presentation only — the one per-step thing the backend doesn't own.
const STEP_SUBTITLES: Record<ActionKey, string> = {
  greenlake: 'Register, assign and subscribe',
  cloudinit: 'Connect the array to HPE GreenLake',
  dscc: 'Set Up System wizard',
  discover: 'Array ports, host adapters, fabric logins',
  ports: 'iSCSI VLAN addresses from the sheet',
  zoning: 'Verify and draft switch commands',
  migrate: 'Read the source array and check it is ready',
  provision: 'Hosts, volumes and exports',
  replicate: 'Remote Copy groups to the peer array',
  failover_test: 'Fail over, recover, restore',
  snapshots: 'A snapshot now and a schedule',
  verify: 'Read-only configuration check',
  asbuilt: 'Handover document',
};

export function subtitleFor(key: string): string {
  return STEP_SUBTITLES[key as ActionKey] ?? '';
}

// The action steps to render for a mode, always in registry order. CUSTOM uses the explicit set.
export function actionKeysFor(registry: StepRegistry, mode: RunMode, custom: ActionKey[]): ActionKey[] {
  const chosen = mode === 'CUSTOM' ? new Set(custom) : new Set(registry.modes[mode] ?? []);
  return registry.steps.filter((s) => chosen.has(s.key)).map((s) => s.key);
}

export interface ModePreset {
  mode: RunMode;
  label: string;
  blurb: string;
  /** The workbook tab this mode cannot run without (SPEC-015 R4). */
  needs?: 'replication';
}

export const MODE_PRESETS: ModePreset[] = [
  { mode: 'FULL_ONBOARDING', label: 'Full onboarding', blurb: 'GreenLake → Cloud Connectivity → DSCC, then verify. For a brand-new array.' },
  { mode: 'PROVISION_ONLY', label: 'Provision storage only', blurb: 'Discovery, zoning, and host + LUN provisioning on an already-initialised array.' },
  { mode: 'BOTH', label: 'Onboard, then provision', blurb: 'The full chain end to end: initialise the array, then provision storage.' },
  {
    mode: 'REPLICATE', label: 'Provision, then replicate', needs: 'replication',
    blurb: 'Discovery, zoning and provisioning, then Remote Copy of the new volume sets to a peer array and a failover test. Needs the workbook’s Replication tab.',
  },
  {
    mode: 'MIGRATE', label: 'Migrate from another array',
    blurb: 'Discovery and zoning, then read the array the data moves from and check it is ready for Peer Motion. Needs the workbook’s Migration tab.',
  },
  { mode: 'VERIFY_ONLY', label: 'Verify only', blurb: 'A read-only verification of the array configuration and status.' },
  { mode: 'CUSTOM', label: 'Custom…', blurb: 'Pick exactly the steps to run.' },
];

// The served reasons a set of steps cannot run yet: one per step whose work is not built.
export function unavailableReasons(catalog: ServedStep[], keys: ActionKey[]): string[] {
  const chosen = new Set(keys);
  return catalog.filter((s) => chosen.has(s.key) && s.unavailable).map((s) => s.unavailable);
}

// Map a persisted run phase back to the action step key, so a refresh resumes on the right step.
// A GL_* mid-phase resolves to the step that owns it (GreenLake).
//
// COMPLETE deliberately resolves to nothing. The backend marks the whole run complete when the
// operator confirms DSCC, which in most modes happens with several steps still to go; resuming on
// "the last step" would silently carry the operator past discovery, zoning, provisioning and
// verification. Returning null lets the caller leave the operator where they were.
export function phaseToActionKey(registry: StepRegistry, phase: string): ActionKey | null {
  const match = registry.steps.find((s) => s.phase === phase);
  if (match) return match.key;
  if (phase.startsWith('GL_') || phase === 'PREFLIGHT') {
    return registry.steps.find((s) => s.phase === 'PREFLIGHT')?.key ?? null;
  }
  return null;
}
