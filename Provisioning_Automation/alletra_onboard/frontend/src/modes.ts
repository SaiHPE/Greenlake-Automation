// Decoupling (docs/adr/0005): the operator picks a MODE up front, and the wizard renders only the
// steps that mode needs — so verification or provisioning can run against an already-initialised
// array without walking the whole init chain. Mirrors the backend RunMode + step registry.

export type RunMode = 'FULL_ONBOARDING' | 'PROVISION_ONLY' | 'BOTH' | 'VERIFY_ONLY' | 'CUSTOM';

export type ActionKey =
  | 'greenlake'
  | 'cloudinit'
  | 'dscc'
  | 'discover'
  | 'zoning'
  | 'provision'
  | 'verify';

export interface ActionDef {
  key: ActionKey;
  title: string;
  subtitle: string;
  kind: 'init' | 'provision' | 'verify';
}

// Ordered catalog of the pickable action steps (the scaffolding steps — mode/prereq/sheet/done —
// are added by App). Order here is the order they appear in the wizard.
export const ACTION_CATALOG: ActionDef[] = [
  { key: 'greenlake', title: 'GreenLake registration', subtitle: 'register · assign · subscribe', kind: 'init' },
  { key: 'cloudinit', title: 'Cloud Connectivity', subtitle: 'on-array wizard', kind: 'init' },
  { key: 'dscc', title: 'DSCC Setup', subtitle: 'Set Up System wizard', kind: 'init' },
  { key: 'discover', title: 'Discovery', subtitle: 'array ports · ESXi HBAs · zoning', kind: 'provision' },
  { key: 'zoning', title: 'SAN Zoning', subtitle: 'verify · remediate (confirm)', kind: 'provision' },
  { key: 'provision', title: 'Provision storage', subtitle: 'host · volumes · LUNs', kind: 'provision' },
  { key: 'verify', title: 'Verify config & health', subtitle: 'SSH read-only check', kind: 'verify' },
];

// Preset modes -> their action keys (keep in lockstep with the backend _MODE_STEPS).
const MODE_STEPS: Record<Exclude<RunMode, 'CUSTOM'>, ActionKey[]> = {
  FULL_ONBOARDING: ['greenlake', 'cloudinit', 'dscc', 'verify'],
  PROVISION_ONLY: ['discover', 'zoning', 'provision', 'verify'],
  BOTH: ['greenlake', 'cloudinit', 'dscc', 'discover', 'zoning', 'provision', 'verify'],
  VERIFY_ONLY: ['verify'],
};

// The action steps to render for a mode, always in catalog order. CUSTOM uses the explicit set.
export function actionKeysFor(mode: RunMode, custom: ActionKey[]): ActionKey[] {
  const chosen = mode === 'CUSTOM' ? new Set(custom) : new Set<ActionKey>(MODE_STEPS[mode]);
  return ACTION_CATALOG.filter((a) => chosen.has(a.key)).map((a) => a.key);
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
  { mode: 'VERIFY_ONLY', label: 'Verify only', blurb: 'Read-only SSH config + health check against an initialised array.' },
  { mode: 'CUSTOM', label: 'Custom…', blurb: 'Pick exactly the steps to run.' },
];

// Map a persisted run phase back to the action step key, so a refresh resumes on the right step.
export function phaseToActionKey(phase: string): ActionKey {
  if (phase === 'CLOUDINIT_CONNECT') return 'cloudinit';
  if (phase === 'DSCC_SETUP_SYSTEM') return 'dscc';
  if (phase === 'STORAGE_DISCOVER') return 'discover';
  if (phase === 'STORAGE_ZONING') return 'zoning';
  if (phase === 'STORAGE_PROVISION') return 'provision';
  if (phase === 'CONFIG_VERIFY' || phase === 'COMPLETE') return 'verify';
  return 'greenlake'; // PREFLIGHT / GL_*
}
