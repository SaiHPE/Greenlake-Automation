// Thin client for the FastAPI backend. In production the UI is served by the API itself
// (same origin); in vite dev it talks to the local API on 8765 (CORS is enabled there).
export const API = import.meta.env.DEV ? 'http://127.0.0.1:8765' : '';

export interface RunRecord {
  run_id: string;
  serial_number: string;
  status: string; // ready | running | waiting_for_operator | retryable_failure | ...
  current_phase: string; // PREFLIGHT | GL_* | CLOUDINIT_CONNECT | DSCC_SETUP_SYSTEM | COMPLETE
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
export interface VerificationReport {
  reachable: boolean;
  error: string | null;
  checks: FieldCheck[];
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

export const getConfig = () => request<{ configured: boolean; values: Record<string, string> }>('GET', '/config');
export const saveConfig = (values: Record<string, string | null>) =>
  request<{ configured: boolean; values: Record<string, string> }>('POST', '/config', values);
export const checkConfig = () => request<{ report: CheckReport }>('POST', '/config/check');

export const parseCsv = (csvText: string) => request<{ work_items: any[] }>('POST', '/work-items/parse', { csv_text: csvText });
export const createRun = (workItem: any) => request<{ run: RunRecord }>('POST', '/runs', { work_item: workItem });

export interface InitSheetUploadResult {
  run: RunRecord;
  work_item: any; // parsed values for review (admin password never included)
  credentials_saved: boolean;
}
// Upload the filled Initialisation_sheet.xlsx (base64). The server parses it, writes the GreenLake
// API creds to .env, and creates the run — so the secret never round-trips through the browser.
export const uploadInitSheet = (contentB64: string) =>
  request<InitSheetUploadResult>('POST', '/init-sheet/upload', { content_b64: contentB64 });
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
