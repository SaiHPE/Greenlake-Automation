// Decoupling (docs/adr/0005 + 0011): the operator picks a MODE up front, and the wizard renders only
// the steps that mode needs. The step registry (keys, labels, kinds, phases) and the mode→steps map
// are SERVED by the backend (GET /app/profile — single source of truth: domain/workflow.py). This
// module keeps only presentation extras (subtitles, mode labels/blurbs) and helpers over served data.

export type RunMode = 'FULL_ONBOARDING' | 'PROVISION_ONLY' | 'BOTH' | 'VERIFY_ONLY' | 'CUSTOM';

export type ActionKey =
  | 'greenlake'
  | 'cloudinit'
  | 'dscc'
  | 'discover'
  | 'zoning'
  | 'provision'
  | 'verify'
  | 'asbuilt';

// One step as served by GET /app/profile.
export interface ServedStep {
  key: ActionKey;
  label: string;
  kind: 'init' | 'provision' | 'verify';
  phase: string;
}

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
  zoning: 'Verify and draft switch commands',
  provision: 'Hosts, volumes and exports',
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
}

export const MODE_PRESETS: ModePreset[] = [
  { mode: 'FULL_ONBOARDING', label: 'Full onboarding', blurb: 'GreenLake → Cloud Connectivity → DSCC, then verify. For a brand-new array.' },
  { mode: 'PROVISION_ONLY', label: 'Provision storage only', blurb: 'Discovery, zoning, and host + LUN provisioning on an already-initialised array.' },
  { mode: 'BOTH', label: 'Onboard, then provision', blurb: 'The full chain end to end: initialise the array, then provision storage.' },
  { mode: 'VERIFY_ONLY', label: 'Verify only', blurb: 'A read-only verification of the array configuration and status.' },
  { mode: 'CUSTOM', label: 'Custom…', blurb: 'Pick exactly the steps to run.' },
];

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
