// Thin client for the FastAPI backend. In production the UI is served by the API itself
// (same origin); in vite dev it talks to the local API on 8765 (CORS is enabled there).
export const API = import.meta.env.DEV ? 'http://127.0.0.1:8765' : '';

export interface RunRecord {
  run_id: string;
  serial_number: string;
  status: string; // ready | running | waiting_for_operator | retryable_failure | ...
  current_phase: string; // PREFLIGHT | GL_* | CLOUDINIT_CONNECT | DSCC_SETUP_SYSTEM | STORAGE_* | COMPLETE
  mode: string; // FULL_ONBOARDING | PROVISION_ONLY | BOTH | VERIFY_ONLY | CUSTOM
  selected_steps: string[];
  warnings: string[];
  updated_at: string;
}

export interface RunEvent {
  event_id: string;
  run_id: string;
  phase: string;
  event_type: string;
  message: string;
  created_at: string;
  data?: Record<string, any>;
}

export interface FieldCheck {
  field: string;
  expected: string;
  actual: string | null;
  status: 'pass' | 'mismatch' | 'not_readable';
  critical: boolean;
}
export interface HealthIssue {
  component: string;
  summary: string;
  qty: number;
}
export interface VerificationReport {
  reachable: boolean;
  error: string | null;
  checks: FieldCheck[];
  health_issues: HealthIssue[];
  raw: Record<string, string>;
}

export interface CheckReport {
  ok: boolean;
  ready: boolean;
  error: string | null;
  missing_credentials: string[];
  provisions: { region: string; status: string; service_manager_id: string; is_data_services: boolean }[];
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    method,
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      if (payload.detail) detail = typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail);
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

// ------------------------------------------------------------------ prerequisites
export interface FirewallRule {
  fqdn: string;
  port: string;
  initiator: string;
  purpose: string;
}
export const getFirewall = (region = 'jp1') =>
  request<{ region: string; rules: FirewallRule[] }>('GET', `/prereqs/firewall?region=${region}`);
// The downloadable .txt the customer forwards to their network team.
export const firewallTxtUrl = (region = 'jp1') => `${API}/prereqs/firewall.txt?region=${region}`;

export interface ConnectivityResult {
  host: string;
  port: number;
  reachable: boolean;
  detail: string;
  via: string; // the proxy the test tunnelled through ('' = direct)
}
// Reachability to the key HPE endpoints via the SAME path the tool uses (through the effective proxy
// if there is one, else direct) — so a proxy-only network no longer shows everything as blocked.
export const checkConnectivity = (region = 'jp1') =>
  request<{ region: string; results: ConnectivityResult[]; all_reachable: boolean; proxy: string | null }>(
    'GET',
    `/prereqs/connectivity?region=${region}`,
  );

// Proxy: the tool auto-detects the system proxy (like the browser); a manual override can be saved.
export interface ProxyStatus {
  detected: string | null;
  manual: string | null;
  effective: string | null;
  source: 'manual' | 'system' | 'direct' | string;
}
export const getProxyStatus = () => request<ProxyStatus>('GET', '/prereqs/proxy');
export const saveProxy = (proxy: string | null) => request<ProxyStatus>('POST', '/prereqs/proxy', { proxy });

// Build profile — the UI brands itself + restricts the mode chooser from this. 'full' = the whole
// platform; init_only = the "Alletra MP Initialization" accelerator (Initialization only).
// It also carries the SERVED step registry + mode presets the wizard renders from (ADR 0011 Phase 2).
export interface AppProfile {
  profile: string;
  init_only: boolean;
  title: string;
  steps: import('./modes').ServedStep[];
  modes: Record<string, import('./modes').ActionKey[]>;
}
export const getAppProfile = () => request<AppProfile>('GET', '/app/profile');

export const getConfig = () => request<{ configured: boolean; values: Record<string, string> }>('GET', '/config');
export const saveConfig = (values: Record<string, string | null>) =>
  request<{ configured: boolean; values: Record<string, string> }>('POST', '/config', values);
export const checkConfig = () => request<{ report: CheckReport }>('POST', '/config/check');

// Note: the CSV intake and direct run creation endpoints still exist for the CLI, but the UI mints
// every run from an uploaded workbook (createRunFromSheet), so it carries no client for them.

export interface InitSheetUploadResult {
  token: string; // single-use hold for the parsed sheet; the run is minted from it + the chosen mode
  work_item: any; // parsed values for review (admin/device passwords never included)
  credentials_saved: boolean;
}
// Upload the filled Initialisation_sheet.xlsx (base64). The server validates it is COMPLETE, writes
// the GreenLake API creds to .env, and HOLDS the parsed sheet server-side — returning a token. No run
// yet: the run is created later from this token + the chosen mode (createRunFromSheet), so device
// passwords never round-trip through the browser. See ADR 0005 (revision).
export const uploadInitSheet = (contentB64: string) =>
  request<InitSheetUploadResult>('POST', '/init-sheet/upload', { content_b64: contentB64 });

// Mint the run from a held sheet once the operator picks a mode.
export const createRunFromSheet = (token: string, mode = 'FULL_ONBOARDING', selectedSteps: string[] = []) =>
  request<{ run: RunRecord }>('POST', '/runs/from-sheet', { token, mode, selected_steps: selectedSteps });
export const getRun = (runId: string) => request<{ run: RunRecord; work_item: any }>('GET', `/runs/${runId}`);
export const getEvents = (runId: string) => request<{ events: RunEvent[] }>('GET', `/runs/${runId}/events`);

export const startProvision = (runId: string, dryRun: boolean) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/provision`, { dry_run: dryRun });
export const startCloudinit = (runId: string, cloudinitUrl: string, autoSubmit = true) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/cloudinit`, {
    cloudinit_url: cloudinitUrl,
    auto_submit: autoSubmit,
  });
export const startDscc = (runId: string, cdpUrl: string) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/dscc`, { cdp_url: cdpUrl });
// Post-init SSH verification — password is used for the SSH session only, never stored.
export const startVerify = (runId: string, username: string, password: string) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/verify`, { username, password });
export const markComplete = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/complete`);

// As-built document (the last step): read the array read-only and build the HPE .docx. The password is
// used only for the SSH session. Download the generated file from the URL below.
export interface AsBuiltResult { serial: string; name: string; customer: string; size: number }
export const startAsbuilt = (runId: string, username: string, password: string, customer = '', site = '') =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/asbuilt`, { username, password, customer, site });
export const asbuiltDownloadUrl = (runId: string) => `${API}/runs/${runId}/asbuilt/download`;

// ------------------------------------------------------------------ storage provisioning (Phase 2)
export interface ArrayPort {
  node: number; slot: number; card_port: number;
  protocol: 'fc' | 'iscsi';
  wwpn: string; address: string; link_state: string;
  fabric: 'odd' | 'even' | null;
  fabric_switch: string; // switch the port attaches to (showportdev fcfabric); '' if by parity
}
export interface HostHba {
  host_name: string; wwpn: string; model: string | null; os: string | null;
  fabric: 'odd' | 'even' | null;
}
// From `showhost -d` — the array's curated host view: each FC WWPN -> the n:s:p ports it's logged
// into (empty = configured but not logged in / not zoned).
export interface ArrayHost {
  name: string; persona: string; wwpns: Record<string, string[]>;
}
export interface DiscoveryReport {
  array_ports: ArrayPort[];
  host_hbas: HostHba[];
  array_hosts: ArrayHost[];
  notes: string[];
  error: string | null;
}
export interface ExpectedZone {
  fabric: 'odd' | 'even'; switch_host: string; name: string;
  host_wwpn: string; array_wwpn: string; present: boolean;
}
export interface ZoneRemediation {
  fabric: 'odd' | 'even'; switch_host: string; cfg_name: string; commands: string[];
}
export interface ZoningReport {
  expected: ExpectedZone[]; remediations: ZoneRemediation[];
  proper: boolean;
  unverified_hosts: string[]; // expected hosts seen on neither fabric — not zoned OR offline
  source: string;             // 'array' — verified from showportdev ns, no switch
  notes: string[]; error: string | null;
}
// The read-only assisted zoning plan (ADR 0004): per-fabric SIST candidates the operator SELECTS
// from and names. already_zoned pairs render pre-selected + disabled; the preview only ever
// creates the operator-selected delta. Rendering itself lives in the backend (POST /zoning/render)
// so the command grammar has exactly one implementation.
export interface AliasedWwpn {
  wwpn: string; display: string; role: 'host' | 'array'; fabric: string; nsp: string;
  host_name: string; host_source: string; existing_aliases: string[]; suggested_alias: string;
  caution: string;  // non-empty = select knowingly (RCFC/Peer-labelled port)
}
export interface FabricZonePlan {
  fabric: string; switch_host: string; active_cfg: string;
  hosts: AliasedWwpn[]; array_ports: AliasedWwpn[];
  pairs: [string, string][]; already_zoned: [string, string][];
}
export interface ZoningPlan {
  fabrics: FabricZonePlan[]; offline_hosts: string[]; notes: string[]; error: string | null;
}
export const renderZoningCommands = (
  plan: ZoningPlan, aliases: Record<string, string>, selectedPairs: [string, string][],
) => request<{ commands: Record<string, string[]>; skipped: Record<string, string[]> }>('POST', '/zoning/render', {
  plan, aliases, selected_pairs: selectedPairs,
});
// Staged write: alicreate/zonecreate/cfgadd + cfgsave into the DEFINED config only. The backend's
// write patterns contain no delete verb and no cfgenable — existing zones cannot be touched and
// activation is always a manual SAN-team action (the per-fabric `handoff` command).
export interface FabricStageResult {
  fabric: string; switch_host: string; staged: string[]; skipped: string[];
  verified: boolean; handoff: string; error: string | null;
}
export interface ZoningStageResult { fabrics: FabricStageResult[]; warning: string; }
export const stageZoning = (
  runId: string, plan: ZoningPlan, aliases: Record<string, string>, selectedPairs: [string, string][],
) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/stage`, {
  plan, aliases, selected_pairs: selectedPairs,
});
export interface PlannedAction {
  kind: string; name: string; description: string; exists: boolean; detail: Record<string, any>;
}
export interface ProvisioningPlan { actions: PlannedAction[]; notes: string[]; error: string | null; }
export interface ActionOutcome { kind: string; name: string; status: 'created' | 'exists' | 'failed'; detail: string; }
export interface ProvisioningResult { outcomes: ActionOutcome[]; error: string | null; }

// The plural provisioning intent pieces + the operator dropdown-builder (ADR 0010 Stage 2).
export interface VolumeRequest { name: string; size_gib: number; provisioning_type: 'tpvv' | 'reduce'; cpg: string; vvset: string | null; }
export interface HostSetRequest { name: string; members: string[]; }
export interface ExportRequest { source_kind: 'volume' | 'vvset'; source_name: string; target_kind: 'host' | 'hostset'; target_name: string; lun: number | null; }
export interface DiscoveredHostBrief { name: string; status: string; wwpns: string[]; }
// The dropdown "palette": existing array objects + to-be-created (from the sheet) + discovered hosts.
export interface ProvisioningObjects {
  existing_cpgs: string[]; existing_hosts: string[]; existing_host_sets: string[];
  existing_volumes: string[]; existing_volume_sets: string[]; array_error: string | null;
  new_volumes: string[]; new_host_sets: string[]; new_vvsets: string[];
  discovered_hosts: DiscoveredHostBrief[];
  host_sets: HostSetRequest[]; exports: ExportRequest[]; // currently composed (resume)
}
export interface ProvisioningBuilder { host_sets: HostSetRequest[]; exports: ExportRequest[]; vvsets: Record<string, string[]>; }
export interface ProvisioningComposition { host_sets: HostSetRequest[]; exports: ExportRequest[]; volumes: VolumeRequest[]; }

// Read-only readiness of the array + vCenter, checked BEFORE discovery so a missing prerequisite is
// named rather than surfacing as a failed step. Never writes to the array.
export interface PreflightCheck { key: string; label: string; status: 'pass' | 'warn' | 'fail'; detail: string; }
export interface PreflightReport { checks: PreflightCheck[]; ready: boolean; }
export const getStoragePreflight = (runId: string) => request<PreflightReport>('GET', `/runs/${runId}/storage/preflight`);

export const startDiscover = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/discover`);
export const zoningPreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/preview`);
export const zoningPlan = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/plan`);
export const getStorageObjects = (runId: string) => request<ProvisioningObjects>('GET', `/runs/${runId}/storage/objects`);
export const saveStorageBuilder = (runId: string, builder: ProvisioningBuilder) =>
  request<ProvisioningComposition>('POST', `/runs/${runId}/storage/builder`, builder);
export const storagePreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/preview`);
export const storageApply = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/apply`);

// Tier-2 path verification (ADR 0010): read `showvlun -a` back and report, per host, whether the
// exported LUN is actually live and over how many fabrics. Read-only; report-only (never gates).
export type PathVerdict = 'live' | 'partial' | 'no_path';
export interface HostPathStatus {
  host: string; verdict: PathVerdict;
  hbas_with_paths: number; fabrics: string[];
  live_volumes: string[]; dead_volumes: string[]; detail: string;
}
export interface PathVerification { hosts: HostPathStatus[]; notes: string[]; error: string | null; }
export const verifyPaths = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/verify-paths`);

export const launchBrowser = (url?: string) =>
  request<{ cdp_url: string; profile_dir: string; executable: string }>('POST', '/browser/launch', { port: 9222, url });

export interface DiscoveryToolResult {
  launched: boolean;
  path: string | null;
  searched: string[];
  error: string | null;
}
export const launchDiscoveryTool = () => request<DiscoveryToolResult>('POST', '/tools/discovery/launch');

export interface ClockStatus {
  in_sync: boolean;
  skew_seconds: number | null;
  local_utc: string;
  server_utc: string | null;
  is_admin: boolean;
  source: string;
  error: string | null;
}

const clockQuery = (url?: string) => (url ? `?url=${encodeURIComponent(url)}` : '');
export const getClock = (url?: string) => request<ClockStatus>('GET', `/system/clock${clockQuery(url)}`);
export const syncClock = (url?: string) =>
  request<{ changed: boolean; skew_seconds_before: number; local_utc_after: string }>('POST', `/system/clock/sync${clockQuery(url)}`);
