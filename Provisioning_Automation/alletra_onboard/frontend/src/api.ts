// Thin client for the FastAPI backend. In production the UI is served by the API itself
// (same origin); in vite dev it talks to the local API on 8765 (CORS is enabled there).
import type { components } from '../generated/api';

type S = components['schemas'];
/** What the server writes always carries every field; `?` in the schema only says a field has a default.
 *  Old stored events may still omit fields added in later releases, so guards (`?.`, `??`) on event data stay. */
type Wire<T> = T extends object ? { [K in keyof T]-?: Wire<T[K]> } : T;

export const API = import.meta.env.DEV ? 'http://127.0.0.1:8765' : '';

export type RunRecord = Wire<S['RunRecord']>;

export type RunEvent = Wire<S['RunEventList']['events'][number]>;
export type EventType = RunEvent['event_type'];
export type EventOf<T extends EventType> =
  T extends unknown
    ? (RunEvent extends infer E ? (E extends { event_type: infer U } ? (T extends U ? E : never) : never) : never)
    : never;

export type FieldCheck = Wire<S['FieldCheck']>;
export type HealthIssue = Wire<S['HealthIssue']>;
/** SPEC-024 R6: one row of the sheet's iSCSI network tab against the array's VLAN interfaces. */
export type IscsiVlanCheck = Wire<S['IscsiVlanCheck']>;

export type CheckReport = Wire<S['GreenLakeCheckReport']>;

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
export type FirewallRule = Wire<S['FirewallRule']>;
export const getFirewall = (region = 'jp1') =>
  request<{ region: string; rules: FirewallRule[] }>('GET', `/prereqs/firewall?region=${region}`);
// The downloadable .txt the customer forwards to their network team.
export const firewallTxtUrl = (region = 'jp1') => `${API}/prereqs/firewall.txt?region=${region}`;

export type ConnectivityResult = Wire<S['ConnectivityResultItem']>;
// Reachability to the key HPE endpoints via the SAME path the tool uses (through the effective proxy
// if there is one, else direct) — so a proxy-only network no longer shows everything as blocked.
export const checkConnectivity = (region = 'jp1') =>
  request<{ region: string; results: ConnectivityResult[]; all_reachable: boolean; proxy: string | null }>(
    'GET',
    `/prereqs/connectivity?region=${region}`,
  );

// Proxy: the tool auto-detects the system proxy (like the browser); a manual override can be saved.
export type ProxyStatus = Wire<S['ProxyStatusResponse']>;
// 'direct://' is the saved value that means "no proxy". It must be non-empty: an empty override
// means "auto-detect", so blanking the field can never express a decision to bypass the proxy.
export const PROXY_DIRECT = 'direct://';
export const getProxyStatus = () => request<ProxyStatus>('GET', '/prereqs/proxy');
export const saveProxy = (proxy: string | null) => request<ProxyStatus>('POST', '/prereqs/proxy', { proxy });

// Build profile — the UI brands itself + restricts the mode chooser from this. 'full' = the whole
// platform; init_only = the "Alletra MP Initialization" accelerator (Initialization only).
// It also carries the SERVED step registry + mode presets the wizard renders from (ADR 0011 Phase 2).
export type AppProfile = Wire<S['AppProfile']>;
export const getAppProfile = () => request<AppProfile>('GET', '/app/profile');

export const checkConfig = () => request<{ report: CheckReport }>('POST', '/config/check');

// Note: the CSV intake and direct run creation endpoints still exist for the CLI, but the UI mints
// every run from an uploaded workbook (createRunFromSheet), so it carries no client for them.

// Single-use hold token, parsed values for review (admin/device passwords never included),
// device endpoints without passwords (SPEC-006 R1), Replication network lines (SPEC-021),
// Snapshots tab lines (SPEC-023 R9), and problems in tabs onboarding does not use.
export type InitSheetUploadResult = Wire<S['InitSheetUploadResult']>;
// Upload the filled Initialisation_sheet.xlsx (base64). The server validates it is COMPLETE, writes
// the GreenLake API creds to .env, and HOLDS the parsed sheet server-side — returning a token. No run
// yet: the run is created later from this token + the chosen mode (createRunFromSheet), so device
// passwords never round-trip through the browser. See ADR 0005 (revision).
export const uploadInitSheet = (contentB64: string) =>
  request<InitSheetUploadResult>('POST', '/init-sheet/upload', { content_b64: contentB64 });

// Mint the run from a held sheet once the operator picks a mode.
export const createRunFromSheet = (token: string, mode = 'FULL_ONBOARDING', selectedSteps: string[] = []) =>
  request<{ run: RunRecord }>('POST', '/runs/from-sheet', { token, mode, selected_steps: selectedSteps });
// ADR 0013 / SPEC-008 R3: whether the run holds an array credential (from the sheet) and whose — never the password.
export type ArrayCredentialInfo = Wire<S['ArrayCredentialInfo']>;
export const getRun = (runId: string) => request<Wire<S['RunDetailResponse']>>('GET', `/runs/${runId}`);
export const listRuns = () => request<{ runs: RunRecord[] }>('GET', '/runs');

// ------------------------------------------------------------------ device trust (trusted on first contact)
/** One on-site device this run trusts: what it presented on first contact. Fingerprints only. */
export type TrustedDevice = Wire<S['DevicePinInfo']>;
export const getTrustedDevices = (runId: string) =>
  request<{ devices: TrustedDevice[]; device_ca_bundle: string | null }>('GET', `/runs/${runId}/trust`);
export const retrustDevice = (runId: string, device: TrustedDevice, fingerprint: string) =>
  request<{ device: TrustedDevice }>('POST', `/runs/${runId}/trust/retrust`, {
    kind: device.kind,
    host: device.host,
    port: device.port,
    fingerprint,
  });
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
// Post-init SSH verification. SPEC-008 R2: the run's own array credential is used unless a pair is given.
export type CredentialOverride = { username: string; password: string } | null;
export const startVerify = (runId: string, override: CredentialOverride = null) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/verify`, override ?? {});
export const markComplete = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/complete`);

// As-built document (the last step): read the array read-only and build the HPE .docx. The password is
// used only for the SSH session. Download the generated file from the URL below.
export type AsBuiltResult = Wire<S['AsBuiltResultData']>;
// SPEC-026 R10: from the same reads as the document's status section. A null figure
// is not known (its read failed, named in read_errors and in the warnings), never zero.
export type HandoverStatus = Wire<S['HandoverStatus']>;
export const startAsbuilt = (
  runId: string, override: CredentialOverride, customer = '', site = '',
  applicationWorkload = '', purpose = '',
) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/asbuilt`, {
    ...(override ?? {}), customer, site, application_workload: applicationWorkload, purpose,
  });
export const asbuiltDownloadUrl = (runId: string) => `${API}/runs/${runId}/asbuilt/download`;

// ------------------------------------------------------------------ console (SPEC-019)
export type CommandRecord = Wire<S['CommandRecord']>;
export const getConsoleLog = (runId: string, since = 0) =>
  request<Wire<S['ConsoleLogResponse']>>('GET', `/runs/${runId}/console/log?since=${since}`);
export const getConsoleTargets = (runId: string) =>
  request<Wire<S['ConsoleTargetsResponse']>>('GET', `/runs/${runId}/console/targets`);
export const runConsoleCommand = (runId: string, command: string, target: string) =>
  request<Wire<S['ConsoleCommandResponse']>>('POST', `/runs/${runId}/console`, { command, target });
export const openConsoleTerminal = (runId: string, target: string) =>
  request<Wire<S['ConsoleTerminalResponse']>>('POST', `/runs/${runId}/console/terminal`, { target });
export const consoleStreamUrl = (runId: string) => `${API}/runs/${runId}/console/stream`;
export const consoleLogTxtUrl = (runId: string) => `${API}/runs/${runId}/console/log?format=txt`;

// ------------------------------------------------------------------ storage provisioning (Phase 2)
export type ArrayPort = Wire<S['ArrayPort']>;
// A non-host-facing ethernet data port: file services or RCIP replication. Kept out of ArrayPort so
// these can never appear as zoning candidates.
export type EthernetPort = Wire<S['EthernetPort']>;
// One physical server, joined across vCenter, the array and the fabric name server on INITIATOR ID
// (never on name — those namespaces do not intersect). `os` is inferred from the IQN authority or
// the name server's OS string, and 'unknown' is a real answer rather than a failure.
export type DiscoveredHost = Wire<S['DiscoveredHost']>;
// The array's file side (Unified File), read over its file API. The File ports themselves stay in
// DiscoveryReport.file_ports (`showport -file`); nothing here repeats them.
export type FileNodeStatus = Wire<S['FileNodeStatus']>;
export type FileSystemRecord = Wire<S['FileSystemRecord']>;
// The array calls it a file share setting; on screen it is a client group.
export type ClientGroup = Wire<S['ClientGroup']>;
export type FileShareRecord = Wire<S['FileShareRecord']>;
// `service` is null when the file API was not read or refused; `notes` says why, one sentence each.
export type FileReport = Wire<S['FileReport']>;
// The read-only assisted zoning plan (ADR 0004): per-fabric SIST candidates the operator SELECTS
// from and names. already_zoned pairs render pre-selected + disabled; the preview only ever
// creates the operator-selected delta. Rendering itself lives in the backend (POST /zoning/render)
// so the command grammar has exactly one implementation.
export type AliasedWwpn = Wire<S['AliasedWwpn']>;
export type FabricZonePlan = Wire<S['FabricZonePlan']>;
export type ZoningPlan = Wire<S['ZoningPlan-Output']>;
export type ZoningRenderResult = Wire<S['ZoningRenderResponse']>;
export const renderZoningCommands = (
  plan: ZoningPlan, aliases: Record<string, string>, selectedPairs: [string, string][], runId?: string,
) => request<ZoningRenderResult>('POST', '/zoning/render', {
  plan, aliases, selected_pairs: selectedPairs, run_id: runId ?? null,
});
// stageZoning + the ZoningStageResult models were removed on 2026-09-02 (ADR 0012). They posted to
// /runs/{id}/zoning/stage, which wrote zones to the switch. renderZoning above is the whole zoning
// output now: the command set a consultant applies by hand.
// Opt-in Brocade FOS apply (ADR 0033) uses the separate approval-gated endpoint below.
export type FabricZoningApplyPlan = Wire<S['FabricZoningApplyPlan']>;
export type ZoningApplyResult = Wire<S['ZoningApplyResult']>;
export const applyZoning = (runId: string, approvedPlan: string | null) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/apply`, { approved_plan: approvedPlan });
export type PlannedAction = Wire<S['PlannedAction']>;
export type PlanState = PlannedAction['state'];
// plan_id: the apply quotes it back, and the server refuses any other (an older event may lack it).
export type ProvisioningPlan = Wire<S['ProvisioningPlan']>;
export type ActionOutcome = Wire<S['ActionOutcome']>;
export type RemovalItem = Wire<S['RemovalItem']>;        // SPEC-007
export type ProvisioningResult = Wire<S['ProvisioningResult']>;

// The plural provisioning intent pieces + the operator dropdown-builder (ADR 0010 Stage 2).
export type ExportRequest = Wire<S['ExportRequest']>;
export type DiscoveredHostBrief = Wire<S['DiscoveredHostBrief']>;
// The dropdown "palette": existing array objects + to-be-created (from the sheet) + discovered hosts.
export type ProvisioningObjects = Wire<S['ProvisioningObjects']>;
export type ProvisioningBuilder = Wire<S['ProvisioningBuilder']>;
export type ProvisioningComposition = Wire<S['ProvisioningComposition']>;

// Read-only readiness of the array + vCenter, checked BEFORE discovery so a missing prerequisite is
// named rather than surfacing as a failed step. Never writes to the array.
export type PreflightCheck = Wire<S['alletra_onboard__domain__provisioning__PreflightCheck']>;
export type PreflightReport = Wire<S['alletra_onboard__domain__provisioning__PreflightReport']>;
export const getStoragePreflight = (runId: string) => request<PreflightReport>('GET', `/runs/${runId}/storage/preflight`);

export const startDiscover = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/discover`);
export const zoningPreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/preview`);
export const zoningPlan = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/zoning/plan`);
export const getStorageObjects = (runId: string) => request<ProvisioningObjects>('GET', `/runs/${runId}/storage/objects`);
export const saveStorageBuilder = (runId: string, builder: ProvisioningBuilder) =>
  request<ProvisioningComposition>('POST', `/runs/${runId}/storage/builder`, builder);
export const storagePreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/preview`);
// approvedPlan: the plan_id of the plan the operator ticked; null when nothing is ticked (the server refuses).
export const storageApply = (runId: string, approvedPlan: string | null) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/apply`, { approved_plan: approvedPlan });

// Tier-2 path verification (ADR 0010): read `showvlun -a` back and report, per host, whether the
// exported LUN is actually live and over how many fabrics. Read-only; report-only (never gates).
export type HostPathStatus = Wire<S['HostPathStatus']>;
export type PathVerdict = HostPathStatus['verdict'];
export type PathVerification = Wire<S['PathVerification']>;
export const verifyPaths = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/storage/verify-paths`);

// SPEC-024: the Array ports step. VLAN-tagged iSCSI addresses from the sheet's iSCSI network tab, planned
// against what the array has. The first slice prints the array's own CLI lines; the tool sends none.
export type IscsiVlanRequest = Wire<S['IscsiVlanRequest']>;
// `cli` is the addr line only; a gateway goes in the separate change-window set (`gateway_window`), never sent.
export type IscsiVlanAction = Wire<S['IscsiVlanAction']>;
export type IscsiVlanActionState = IscsiVlanAction['state'];
/** The iSCSI section of a ports.* event: the rows read, and (after a read) the view and the plan. */
export type IscsiSection = Wire<S['IscsiSection']>;
// SPEC-025: peer ports for a migration, the second section of the Array ports step. The first slice prints
// the commands and their undo for a consultant to paste; the tool sends none.
export type PeerPortRequest = Wire<S['PeerPortRequest']>;
export type PeerPortIntent = Wire<S['PeerPortIntent']>;
export type PeerPortAction = Wire<S['PeerPortAction']>;
export type PeerPortActionState = PeerPortAction['state'];
/** The peer section of a ports.* event: the rows, and after a read the view, the plan, the command set and
 *  its removal set, and the judgement of a read after the paste. */
export type PeerSection = Wire<S['PeerSection']>;
export type ArrayPorts = Wire<S['ArrayPortsResponse']>;
export const getArrayPorts = (runId: string) => request<ArrayPorts>('GET', `/runs/${runId}/ports`);
export const portsPreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/ports/preview`);

// SPEC-016: replication to a peer array. Release (a) is read-only: both arrays read, the
// partnership found by link address, the findings, and the exists/create/conflict plan.
// SPEC-031: a partnership is over RCIP ('IP', found by address) or Fibre Channel ('FC', found by port WWN).
export type RcGroup = Wire<S['RcGroup']>;
export type ReplicationArrayView = Wire<S['ReplicationArrayView']>;
export type Partnership = Wire<S['Partnership']>;
export type Transport = Partnership['transport'];
export type ReplicationReport = Wire<S['ReplicationReport']>;
export type ReplicationAction = Wire<S['ReplicationAction']>;
export type ReplicationActionState = ReplicationAction['state'];
export type ReplicationPlan = Wire<S['ReplicationPlan']>;
const runPost = (runId: string, tail: string, body?: unknown) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/${tail}`, body);

export const replicationPreview = (runId: string) => runPost(runId, 'replication/preview');
// R4/R7: what the arrays said per write, and the removal lines per array (the operator pastes; the tool never runs them).
export type ReplicationOutcome = Wire<S['ReplicationOutcome']>;
export type ReplicationResult = Wire<S['ReplicationResult']>;
// SPEC-021: a plan that sets up the ports and the partnership holds only these kinds (its apply adds the pings
// and the links). That apply is half the step: the groups are planned after it, from a fresh read.
const PARTNERSHIP_KINDS: string[] = ['rcip_port', 'rc_service', 'target', 'ping', 'links'];
export const setsUpPartnership = (plan: ReplicationPlan | null | undefined) =>
  !!plan && plan.actions.some((a) => a.state === 'create' && PARTNERSHIP_KINDS.includes(a.kind));
export const isPartnershipResult = (result: ReplicationResult | null | undefined) =>
  !!result && result.outcomes.length > 0 && result.outcomes.every((o) => PARTNERSHIP_KINDS.includes(o.kind));
export const replicationApply = (runId: string, approvedPlan: string | null, acceptLatency = false) =>
  runPost(runId, 'replication/apply', { approved_plan: approvedPlan, accept_latency: acceptLatency });
// SPEC-020: the latency between the arrays measured with checkrclink (server on B, client on A, read until
// the latency is printed, stop both). RTT_LIMIT_MS mirrors the domain's HPE limits per transport and mode
// (SPEC-031 R6: 10 ms for both modes over Fibre Channel); read it through rttLimitMs, which names the transport.
const RTT_LIMIT_MS: Record<Transport, Record<string, number>> = {
  IP: { sync: 10, async: 200 },
  FC: { sync: 10, async: 10 },
};
export const rttLimitMs = (transport: Transport, mode: string): number => RTT_LIMIT_MS[transport][mode] ?? 0;
export const TRANSPORT_WORDS: Record<Transport, string> = { IP: 'over RCIP', FC: 'over Fibre Channel' };
export type LinkCheckResult = Wire<S['LinkCheckResult']>;
export type LinkCheck = Wire<S['LinkCheck']>;
export const replicationLinkCheck = (runId: string, durationS = 600) =>
  runPost(runId, 'replication/link-check', { duration_s: durationS });
// R6: read-only verdict per planned group from `showrcopy` on both arrays.
// `showrcopy -d groups <group>` on this array (BL-64): every column as the array printed it ("NA", "none", "").
export type RcVolumeDetail = Wire<S['RcVolumeDetail']>;
export type RcGroupDetail = Wire<S['RcGroupDetail']>;
export type GroupVerification = Wire<S['GroupVerification']>;
export type GroupVerdict = GroupVerification['verdict'];
export type ReplicationVerification = Wire<S['ReplicationVerification']>;
export const replicationVerify = (runId: string) => runPost(runId, 'replication/verify');

// SPEC-017: the failover test record. P = this run's array, S = the peer.
export type FailoverStepRecord = Wire<S['FailoverStepRecord']>;
export type FailoverOutcome = FailoverStepRecord['outcome'];
export const failoverTest = (runId: string, group: string | null, confirm: string | null, authorised: boolean) =>
  runPost(runId, 'replication/failover-test', { group, confirm, authorised });

export const launchBrowser = (url?: string) =>
  request<{ cdp_url: string; profile_dir: string; executable: string }>('POST', '/browser/launch', { port: 9222, url });

export type DiscoveryToolResult = Wire<S['DiscoveryToolResponse']>;
export const launchDiscoveryTool = () => request<DiscoveryToolResult>('POST', '/tools/discovery/launch');

export type ClockStatus = Wire<S['ClockStatus']>;

const clockQuery = (url?: string) => (url ? `?url=${encodeURIComponent(url)}` : '');
export const getClock = (url?: string) => request<ClockStatus>('GET', `/system/clock${clockQuery(url)}`);
export const syncClock = (url?: string) =>
  request<{ changed: boolean; skew_seconds_before: number; local_utc_after: string }>('POST', `/system/clock/sync${clockQuery(url)}`);

// SPEC-023: a snapshot now of each volume set or volume on the Snapshots tab, and a schedule on the array.
export type SnapshotAction = Wire<S['SnapshotAction']>;
export type SnapshotActionState = SnapshotAction['state'];
export type SnapshotPlan = Wire<S['SnapshotPlan']>;
export type ArraySchedule = Wire<S['ArraySchedule']>;
export type SnapshotOutcome = Wire<S['SnapshotOutcome']>;
export type SnapshotResult = Wire<S['SnapshotResult']>;
export type SnapshotRowCheck = Wire<S['SnapshotRowCheck']>;
export type SnapshotVerification = Wire<S['SnapshotVerification']>;
// The tab's rows in words, and the id of the plan the server still holds ('' when none: it was used, or the app restarted).
export type SnapshotsTab = Wire<S['SnapshotsResponse']>;
export const getSnapshots = (runId: string) => request<SnapshotsTab>('GET', `/runs/${runId}/snapshots`);
export const snapshotsPreview = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/snapshots/preview`);
// The server checks the tick too: it gets the plan's id only when this plan was ticked (BL-52).
export const snapshotsApply = (runId: string, approvedPlan: string | null) =>
  request<{ run: RunRecord }>('POST', `/runs/${runId}/snapshots/apply`, { approved_plan: approvedPlan });
export const snapshotsVerify = (runId: string) => request<{ run: RunRecord }>('POST', `/runs/${runId}/snapshots/verify`);

/**
 * SPEC-023 R9: what the sheet review says when the Snapshots tab is filled and the chosen steps lack the
 * Snapshots step; null otherwise. `steps` are the run's step keys, from the served registry.
 */
export function snapshotsTabNotPicked(sheet: InitSheetUploadResult | null | undefined, steps: string[]): string | null {
  return sheet?.snapshot_rows?.length && !steps.includes('snapshots')
    ? 'The Snapshots tab is filled in; pick the Snapshots step to apply it.'
    : null;
}
