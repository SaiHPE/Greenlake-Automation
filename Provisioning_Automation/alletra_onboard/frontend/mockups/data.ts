/** Lab-like data for the mockups (names and numbers from the D22U27 / E18U31 captures). */
import { StepState } from '../src/ui/status';
import { RailGroup, RunSummary } from './kit';

export const STEPS: { key: string; label: string; stage: string }[] = [
  { key: 'prereq', label: 'Prerequisites', stage: 'Prepare' },
  { key: 'sheet', label: 'Initialisation sheet', stage: 'Prepare' },
  { key: 'mode', label: 'Mode', stage: 'Prepare' },
  { key: 'discover', label: 'Discovery', stage: 'Provision' },
  { key: 'zoning', label: 'SAN zoning', stage: 'Provision' },
  { key: 'provision', label: 'Provision storage', stage: 'Provision' },
  { key: 'replicate', label: 'Replication', stage: 'Replicate' },
  { key: 'failover', label: 'Failover test', stage: 'Replicate' },
  { key: 'verify', label: 'Verify configuration', stage: 'Document' },
  { key: 'asbuilt', label: 'As-built document', stage: 'Document' },
  { key: 'finish', label: 'Finish', stage: 'Document' },
];

export const RESULTS: Record<string, string> = {
  prereq: '3 checks passed',
  sheet: 'CZ2D320BT1 · 3 tabs',
  mode: 'Provision, then replicate',
  discover: '8 ports · 2 hosts · 2 fabrics',
  zoning: '2 hosts zoned on both fabrics',
  provision: '1 volume · 1 host set · 1 export',
  replicate: '1 group replicating',
  failover: 'Passed · 1.3 s',
  verify: '12 of 12 checks match',
  asbuilt: 'Generated · 764 KB',
};

/** The step rail with every step before `current` complete and `current` in `state`. Before a run
 * exists (`runSteps` false) only the Prepare group is listed; `preview` adds the chosen mode's steps
 * greyed, as the Mode screen does while you pick. */
export function rail(
  current: string,
  state: StepState = 'action_required',
  overrides: Record<string, StepState> = {},
  opts: { runSteps?: boolean; preview?: string[] } = {},
): RailGroup[] {
  const at = STEPS.findIndex((s) => s.key === current);
  const runSteps = opts.runSteps ?? at >= 3;
  const groups: RailGroup[] = [];
  STEPS.forEach((s, i) => {
    const prepare = s.stage === 'Prepare';
    if (!prepare && !runSteps && !(opts.preview ?? []).includes(s.key)) return;
    const st: StepState = overrides[s.key] ?? (i < at ? 'complete' : i === at ? state : 'not_started');
    const step = { key: s.key, label: s.label, state: st, result: st === 'complete' ? RESULTS[s.key] : undefined };
    const g = groups.find((x) => x.stage === s.stage);
    if (g) g.steps.push(step);
    else groups.push({ stage: s.stage, steps: [step] });
  });
  return groups;
}

const PREPARE = STEPS.filter((s) => s.stage === 'Prepare');
const RUN_STEPS = STEPS.filter((s) => s.stage !== 'Prepare' && s.key !== 'finish');

/** "Prepare · step 1 of 3" before the run exists; "Step 1 of 7" inside it (Finish is not a step). */
export function stepLabel(key: string): string {
  const p = PREPARE.findIndex((s) => s.key === key);
  if (p >= 0) return `Prepare · step ${p + 1} of ${PREPARE.length}`;
  const r = RUN_STEPS.findIndex((s) => s.key === key);
  return `Step ${r + 1} of ${RUN_STEPS.length}`;
}

export const stepNo = (key: string) => STEPS.findIndex((s) => s.key === key) + 1;

export const RUN: RunSummary = {
  array: 'AlletraMP_D22U27',
  serial: 'CZ2D320BT1',
  mode: 'Provision, then replicate',
  state: 'action_required',
  stateLabel: 'Waiting for you',
};

export const ARRAY_PORTS = [
  { nsp: '0:3:1', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F1', logins: 'ESX1 HBA1' },
  { nsp: '1:3:1', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F1', logins: 'ESX1 HBA1' },
  { nsp: '0:3:4', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F2', logins: 'ESX1 HBA2' },
  { nsp: '1:3:4', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F2', logins: 'ESX1 HBA2' },
  { nsp: '0:3:2', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F1', logins: '—' },
  { nsp: '1:3:2', type: 'FC', state: 'ready', speed: '32 Gbps', fabric: 'F2', logins: '—' },
  { nsp: '0:4:3', type: 'RCIP', state: 'ready', speed: '10 Gbps', fabric: '—', logins: '10.54.122.92' },
  { nsp: '1:4:3', type: 'RCIP', state: 'ready', speed: '10 Gbps', fabric: '—', logins: '10.54.122.93' },
];

export const HOSTS = [
  { name: 'ESX1', os: 'ESXi 8.0', source: 'array, sheet', wwpns: '1000D0BF9CB7A3C9, 1000D0BF9CB7A3D1', fabrics: 'F1 and F2' },
  { name: 'ESX2', os: 'ESXi 8.0', source: 'vCenter', wwpns: '10000090FA8B2C10, 10000090FA8B2C11', fabrics: 'not logged in' },
];

export const EXISTING_GROUPS = ['300gb', 'APP_Test', 'Intern_Automation', 'Intern_Automation2', 'Test-RCG', 'Test-RCG2'];

export const PLAN = [
  { kind: 'Test volume', name: 'zz_rc_test_v01', on: 'A', action: 'Create', detail: '1 GiB on SSD_r6, for the failover test' },
  { kind: 'Test volume set', name: 'zz_rc_test', on: 'A', action: 'Create', detail: 'holds zz_rc_test_v01' },
  { kind: 'Remote Copy group', name: 'zz_rc_test_rcg', on: 'A', action: 'Create', detail: 'sync → AlletraMP_E18U31, 1 volume' },
  { kind: 'Peer volume set', name: 'zz_rc_test_rc', on: 'B', action: 'Create', detail: 'groups the secondary volume' },
  { kind: 'Remote Copy group', name: 'zz_rc_vvs_rcg', on: 'A', action: 'Create', detail: 'sync → AlletraMP_E18U31, 1 volume from zz_rc_vvs, secondaries on SSD_r6' },
  { kind: 'Peer volume set', name: 'zz_rc_vvs_rc', on: 'B', action: 'Create', detail: 'groups the secondary volume' },
];

export const COMMANDS = [
  'A  createvv -tpvv SSD_r6 zz_rc_test_v01 1g',
  'A  createvvset zz_rc_test zz_rc_test_v01',
  'A  creatercopygroup -usr_cpg SSD_r6 AlletraMP_E18U31:SSD_r6 zz_rc_test_rcg AlletraMP_E18U31:sync',
  'A  setrcopygroup pol auto_recover zz_rc_test_rcg ; setrcopygroup pol auto_synchronize zz_rc_test_rcg',
  'A  admitrcopyvv -createvv zz_rc_test_v01 zz_rc_test_rcg AlletraMP_E18U31:zz_rc_test_v01',
  'B  createvvset zz_rc_test_rc zz_rc_test_v01',
  'A  startrcopygroup zz_rc_test_rcg',
  'A  creatercopygroup -usr_cpg SSD_r6 AlletraMP_E18U31:SSD_r6 zz_rc_vvs_rcg AlletraMP_E18U31:sync',
  'A  setrcopygroup pol auto_recover zz_rc_vvs_rcg ; setrcopygroup pol auto_synchronize zz_rc_vvs_rcg',
  'A  admitrcopyvv -createvv zz_rc_vol01 zz_rc_vvs_rcg AlletraMP_E18U31:zz_rc_vol01',
  'B  createvvset zz_rc_vvs_rc zz_rc_vol01',
  'A  startrcopygroup zz_rc_vvs_rcg',
];
