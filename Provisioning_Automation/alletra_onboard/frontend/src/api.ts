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
}
// Direct TCP-443 reachability from the jump box to the key HPE endpoints (are the firewall ports open?).
export const checkConnectivity = (region = 'jp1') =>
  request<{ region: string; results: ConnectivityResult[]; all_reachable: boolean }>(
    'GET',
    `/prereqs/connectivity?region=${region}`,
  );

export const getConfig = () => request<{ configured: boolean; values: Record<string, string> }>('GET', '/config');
export const saveConfig = (values: Record<string, string | null>) =>
  request<{ configured: boolean; values: Record<string, string> }>('POST', '/config', values);
export const checkConfig = () => request<{ report: CheckReport }>('POST', '/config/check');

export const parseCsv = (csvText: string) => request<{ work_items: any[] }>('POST', '/work-items/parse', { csv_text: csvText });
export const createRun = (workItem: any, mode = 'FULL_ONBOARDING', selectedSteps: string[] = []) =>
  request<{ run: RunRecord }>('POST', '/runs', { work_item: workItem, mode, selected_steps: selectedSteps });

export interface InitSheetUploadResult {
  run: RunRecord;
  work_item: any; // parsed values for review (admin password never included)
  credentials_saved: boolean;
}
// Upload the filled Initialisation_sheet.xlsx (base64). The server parses it, writes the GreenLake
// API creds to .env, and creates the run — so the secret never round-trips through the browser.
// `mode`/`selectedSteps` scope which sheet fields are required and which steps the run will render.
export const uploadInitSheet = (contentB64: string, mode = 'FULL_ONBOARDING', selectedSteps: string[] = []) =>
  request<InitSheetUploadResult>('POST', '/init-sheet/upload', {
    content_b64: contentB64,
    mode,
    selected_steps: selectedSteps,
  });
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

// ------------------------------------------------------------------ storage provisioning (Phase 2)
export interface ArrayPort {
  node: number; slot: number; card_port: number;
  wwpn: string; link_state: string; fabric: 'odd' | 'even';
}
export interface HostHba {
  host_name: string; wwpn: string; model: string | null; os: string | null;
  fabric: 'odd' | 'even' | null;
}
export interface DiscoveryReport {
  array_ports: ArrayPort[];
  host_hbas: HostHba[];
  nameserver: { fabric: string; switch_host: string; wwpn: string; is_array_port: boolean }[];
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
  proper: boolean; notes: string[]; error: string | null;
}
export interface PlannedAction {
  kind: string; name: string; description: string; exists: boolean; detail: Record<string, any>;
}
export interface ProvisioningPlan { actions: PlannedAction[]; notes: string[]; error: string | null; }
export interface ActionOutcome { kind: string; name: string; status: 'created' | 'exists' | 'failed'; detail: string; }
export interface ProvisioningResult { outcomes: ActionOutcome[]; error: string | null; }

export const startDiscover = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/discover`);
export const zoningPreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/preview`);
export const zoningApply = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/apply`);
export const storagePreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/preview`);
export const storageApply = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/apply`);

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
