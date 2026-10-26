import { Anchor, Box, Button, DataTable, Heading, Text, TextInput } from 'grommet';
import { ReactNode, useEffect, useState } from 'react';
import {
  API,
  ConnectivityResult,
  FirewallRule,
  PROXY_DIRECT,
  ProxyStatus,
  checkConnectivity,
  firewallTxtUrl,
  getFirewall,
  getProxyStatus,
  saveProxy,
} from '../api';
import { useClock } from '../ClockSync';
import { Instructions } from '../components';
import { Guidance, Section, StatusLine } from '../ui/blocks';
import { TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

/** A numbered task with its HPE walkthrough recording. */
function TaskClip({ title, steps, src }: { title: string; steps: ReactNode[]; src: string }) {
  return (
    <Box gap="xsmall" pad={{ top: 'small' }} flex={false}>
      <Text weight={500} color="text-strong">
        {title}
      </Text>
      <Instructions items={steps} />
      <Box round="xsmall" overflow="hidden" background="black" width={{ max: 'large' }} flex={false}>
        <video src={src} controls preload="metadata" style={{ width: '100%', display: 'block' }} />
      </Box>
    </Box>
  );
}

const CHECKLIST =
  'https://infosight.hpe.com/welcomecenter/getting-started/checklist?connectopt=HPE%20Cloud%20Connectivity%20Wizard%2FDiscovery%20Tool&greenlakeplatform=HPE%20GreenLake%20Cloud%20Platform&model=B10140&opt=factory&product=alletraB10k';

/**
 * The manual work HPE requires before any automation runs. This tool does not perform these, and
 * deliberately does not pretend to: it checks what it can (connection, proxy, clock) and lists the rest.
 */
export function PrereqStep({ onDone, state }: { onDone: () => void; state: StepState }) {
  const { nextTitle } = useStepContext();
  const [rules, setRules] = useState<FirewallRule[]>([]);
  const [connectivity, setConnectivity] = useState<ConnectivityResult[] | null>(null);
  const [allReachable, setAllReachable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [proxy, setProxy] = useState<ProxyStatus | null>(null);
  const [proxyInput, setProxyInput] = useState('');
  const [savingProxy, setSavingProxy] = useState(false);
  // The DSCC region is the <instance> in <instance>.data.cloud.hpe.com. HPE keeps adding regions, so
  // this is a suggestion list rather than a closed set.
  const [region, setRegion] = useState('jp1');
  const clockCheck = useClock();
  const { clock, skewOff } = clockCheck;

  useEffect(() => {
    getProxyStatus()
      .then((status) => {
        setProxy(status);
        // Never seed the box with the direct sentinel: it is a decision, not a proxy address.
        setProxyInput(status.forced_direct ? '' : status.manual ?? '');
      })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    getFirewall(region)
      .then((response) => setRules(response.rules))
      .catch(() => undefined);
  }, [region]);

  const test = async () => {
    setBusy(true);
    setError(null);
    try {
      const response = await checkConnectivity(region);
      setConnectivity(response.results);
      setAllReachable(response.all_reachable);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  const applyProxy = async (value: string | null) => {
    setSavingProxy(true);
    setError(null);
    try {
      const status = await saveProxy(value);
      setProxy(status);
      setProxyInput(status.forced_direct ? '' : status.manual ?? '');
      await test();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setSavingProxy(false);
    }
  };

  const reachable = connectivity?.filter((result) => result.reachable).length ?? 0;
  const blocked = (connectivity?.length ?? 0) - reachable;
  const skew = Math.abs(Math.round(clock?.skew_seconds ?? 0));

  const connState: StepState = !connectivity ? 'not_started' : allReachable ? 'complete' : 'action_required';
  const clockState: StepState = clock === null ? 'running' : skewOff ? 'action_required' : clock.skew_seconds == null ? 'not_started' : 'complete';
  const proxyText = !proxy
    ? 'Reading the system setting'
    : proxy.forced_direct
      ? 'In use: no proxy, connecting directly (detected value ignored)'
      : proxy.source === 'manual'
        ? `In use: manual proxy ${proxy.effective}`
        : proxy.source === 'system'
          ? `In use: detected system proxy ${proxy.detected}`
          : 'No proxy detected; connecting directly';

  const continueAction: FooterAction = { label: nextTitle ? `Continue to ${nextTitle}` : 'Continue', onClick: onDone };
  const download: FooterAction = {
    label: 'Download the initialisation sheet',
    href: `${API}/init-sheet/template`,
    download: 'Initialisation_sheet.xlsx',
  };

  return (
    <StepShell
      title="Prerequisites"
      description="What HPE requires before onboarding, and checks of this workstation."
      state={state}
      stateLabel={skewOff ? 'Clock needs a sync' : undefined}
      error={error}
      onDismissError={() => setError(null)}
      primary={skewOff ? { label: clockCheck.busy ? 'Syncing' : 'Sync system clock', busy: clockCheck.busy, onClick: clockCheck.sync } : continueAction}
      buttons={skewOff ? [download, { label: 'Continue without syncing', onClick: onDone }] : [download]}
      guidance={
        <Guidance
          items={[
            {
              title: 'What this step is for',
              body: "Everything here is preparation HPE requires before a B10000 is onboarded. The tool checks the connection, the proxy and the clock itself. You do the rest by hand; the recordings are HPE's own walkthroughs.",
            },
            { title: 'Nothing is changed', body: 'This step makes no changes to the array or to HPE GreenLake.' },
            {
              title: 'Where this comes from',
              body: (
                <>
                  HPE&apos;s <Anchor href={CHECKLIST} target="_blank" label="onboarding checklist" /> and the installation guide sd00002405.
                </>
              ),
            },
          ]}
        />
      }
    >
      {skewOff ? (
        <StatusLine state="action_required">
          The clock is {skew} seconds off. Sync it before you start: a clock that is off stops the array connecting to DSCC.
        </StatusLine>
      ) : connectivity && !allReachable ? (
        <StatusLine state="action_required">
          {blocked} of {connectivity.length} endpoints are blocked. Ask the network team to allow them on outbound TCP 443, or set the
          right proxy.
        </StatusLine>
      ) : connectivity ? (
        <StatusLine state="complete">
          Connection tested: {reachable} of {connectivity.length} endpoints reachable. Confirm the items you do by hand, then continue.
        </StatusLine>
      ) : (
        <StatusLine state="not_started">Connection not tested yet. Test it below, then confirm the items you do by hand.</StatusLine>
      )}

      <Box gap="small" flex={false}>
        <Heading level={2} size="small" margin="none">
          Checked by this tool
        </Heading>
        <Section
          level={3}
          title="Connection to HPE GreenLake"
          summary={connectivity ? `${reachable} of ${connectivity.length} endpoints reachable · region ${region}` : `Not tested · region ${region}`}
          open={Boolean(connectivity && !allReachable)}
          right={
            <Box direction="row" gap="small" align="center">
              <Button size="small" busy={busy} label={connectivity ? 'Retest' : 'Test connectivity'} onClick={test} />
              <StatusIndicator state={connState} label={!connectivity ? 'Not tested' : allReachable ? 'Passed' : 'Blocked'} />
            </Box>
          }
        >
          <Text size="small" color="text-weak">
            These endpoints must be reachable on outbound TCP 443. Request firewall exceptions from the network team for any shown as
            blocked.
          </Text>
          <Box direction="row" gap="small" align="center" wrap flex={false}>
            <Text size="small" color="text-weak">
              DSCC region
            </Text>
            <Box width="xsmall">
              <TextInput
                size="small"
                value={region}
                suggestions={['us1', 'eu1', 'jp1', 'uk1']}
                onChange={(event) => setRegion(event.target.value.trim())}
                onSelect={(event) => setRegion(String(event.suggestion))}
                aria-label="DSCC region"
              />
            </Box>
            <Anchor size="small" href={firewallTxtUrl(region)} download="alletra-firewall-requirements.txt" label="Download the list for the firewall team" />
          </Box>
          {connectivity ? (
            <Box flex={false}>
              <DataTable
                columns={[
                  { property: 'host', header: 'Endpoint', render: (result: ConnectivityResult) => <Text size="small">{result.host}</Text> },
                  {
                    property: 'reachable',
                    header: 'Result',
                    render: (result: ConnectivityResult) => (
                      <StatusIndicator state={result.reachable ? 'complete' : 'failed'} label={result.reachable ? 'Reachable' : 'Blocked'} />
                    ),
                  },
                  {
                    property: 'detail',
                    header: 'Detail',
                    render: (result: ConnectivityResult) => (
                      <Text size="small" color="text-weak">
                        {result.detail}
                        {result.via ? ` (via ${result.via})` : ''}
                      </Text>
                    ),
                  },
                ]}
                data={connectivity}
                primaryKey="host"
                a11yTitle="Connectivity checks: one row per endpoint the jump box must reach"
              />
              <TableSummary>
                {reachable} reachable · {blocked} blocked
              </TableSummary>
            </Box>
          ) : (
            rules.length > 0 && (
              <Box flex={false}>
                <DataTable
                  columns={[
                    { property: 'fqdn', header: 'Endpoint', render: (rule: FirewallRule) => <Text size="small">{rule.fqdn}</Text> },
                    { property: 'port', header: 'Port', render: (rule: FirewallRule) => <Text size="small">{rule.port}</Text> },
                    { property: 'initiator', header: 'Initiator', render: (rule: FirewallRule) => <Text size="small" color="text-weak">{rule.initiator}</Text> },
                    { property: 'purpose', header: 'Purpose', render: (rule: FirewallRule) => <Text size="small" color="text-weak">{rule.purpose}</Text> },
                  ]}
                  data={rules}
                  primaryKey="fqdn"
                  a11yTitle="Firewall and proxy rules: one row per destination"
                />
                <TableSummary>{rules.length} endpoints required</TableSummary>
              </Box>
            )
          )}
          <Instructions
            items={[
              <>Local array discovery uses mDNS on UDP 5353.</>,
              <>The array&apos;s DNS must resolve the HPE global names, for example device.cloud.hpe.com.</>,
              <>Reserved for array operations, do not assign: 16.1.8.11/27/43/59 and 16.1.9.11/27/43/59, the CDM link-local range.</>,
            ]}
          />
        </Section>

        <Section
          level={3}
          title="Proxy"
          summary={proxyText}
          right={<StatusIndicator state={proxy ? 'complete' : 'running'} label={proxy ? 'Detected' : 'Reading'} />}
        >
          <Text size="small" color="text-weak">
            Detected from the operating system, as a browser would resolve it. Enter an override if the detected value is wrong, or
            connect directly to ignore it.
          </Text>
          {proxy?.forced_direct && proxy.detected && (
            <Text size="xsmall" color="text-weak">
              The operating system reports {proxy.detected}; the tool is ignoring it by your choice.
            </Text>
          )}
          <Box direction="row" gap="small" align="center" wrap flex={false}>
            <Box width="medium">
              <TextInput
                size="small"
                placeholder="host:port"
                value={proxyInput}
                onChange={(event) => setProxyInput(event.target.value)}
                aria-label="Manual proxy override"
              />
            </Box>
            {proxyInput.trim() && (
              <Button size="small" busy={savingProxy} label="Save and retest" onClick={() => applyProxy(proxyInput.trim())} />
            )}
            {/* The only way to say "there is no proxy here": an empty field means auto-detect, so it
                can never express this. Saves the 'direct://' sentinel, which persists across restarts. */}
            {!proxy?.forced_direct && (
              <Button
                size="small"
                label="Connect directly (no proxy)"
                disabled={savingProxy}
                onClick={() => {
                  setProxyInput('');
                  applyProxy(PROXY_DIRECT);
                }}
              />
            )}
            {proxy?.manual && (
              <Button
                size="small"
                label="Use detected setting"
                disabled={savingProxy}
                onClick={() => {
                  setProxyInput('');
                  applyProxy(null);
                }}
              />
            )}
          </Box>
        </Section>

        <Section
          level={3}
          title="Workstation clock"
          summary={
            clock === null
              ? 'Checking'
              : skewOff
                ? `Off by about ${skew} seconds`
                : clock.skew_seconds == null
                  ? `Could not reach a time source (${clock.error ?? 'unknown'})`
                  : `In sync (±${skew} s against ${clock.source})`
          }
          open={skewOff}
          right={
            <StatusIndicator
              state={clockState}
              label={clock === null ? 'Checking' : skewOff ? 'Sync needed' : clock.skew_seconds == null ? 'Not checked' : 'Passed'}
            />
          }
        >
          <Text size="small">
            A clock that is off stops the array connecting to DSCC (the error says &quot;iat is in the future&quot;). Sync system clock
            sets it from an HTTPS time source, which works where NTP is blocked.
          </Text>
          {clock && !clock.is_admin && (
            <Text size="small" color="text-weak">
              Run the app as Administrator for the sync to set the clock.
            </Text>
          )}
          <Box direction="row" gap="small" align="center">
            <Button size="small" busy={clockCheck.busy} label="Sync system clock" onClick={clockCheck.sync} />
            {clockCheck.message && (
              <Text size="small" color="text-weak">
                {clockCheck.message}
              </Text>
            )}
          </Box>
          {clockCheck.error && (
            <StatusLine state="failed" title="Sync failed" onClose={() => clockCheck.setError(null)}>
              {clockCheck.error}
            </StatusLine>
          )}
        </Section>
      </Box>

      <Box gap="small" flex={false}>
        <Heading level={2} size="small" margin="none">
          Do these by hand before you start
        </Heading>
        <Section level={3} title="HPE GreenLake workspace and DSCC" summary="Activate the subscriptions, then 3 tasks in HPE GreenLake, with recordings">
          <Instructions
            items={[
              <>Activate the software subscriptions from the Electronic Software Delivery receipt email.</>,
              <>
                Create or sign in to your <Anchor href="https://console.greenlake.hpe.com" target="_blank" label="HPE GreenLake" /> account, then
                complete the three tasks below in order.
              </>,
            ]}
          />
          <TaskClip
            title="1. Create the workspace"
            src="/prereq/videos/create-workspace.mp4"
            steps={[
              <>Select Create Workspace and provide the name, country, address, phone and email.</>,
              <>Accept the legal terms and select Create Workspace. You become the workspace administrator.</>,
            ]}
          />
          <TaskClip
            title="2. Deploy Data Services Cloud Console"
            src="/prereq/videos/deploy-dscc.mp4"
            steps={[
              <>From the workspace home, select Find Services, then Storage, then Data Services, then Provision.</>,
              <>Select the deployment region nearest the array, accept the terms, and select Deploy.</>,
              <>Select Launch to open Data Services Cloud Console.</>,
            ]}
          />
          <TaskClip
            title="3. Assign the Data Services administrator role"
            src="/prereq/videos/assign-admin.mp4"
            steps={[
              <>
                In Manage Workspace, Identity and Access, Assign Role: select your user, set service manager to Data Services and role to
                Administrator, leave resource-access limits off, and assign.
              </>,
              <>Launch Data Services and confirm the Setup, Block Storage and Data Ops Manager services appear.</>,
            ]}
          />
        </Section>
        <Section level={3} title="API client" summary="A personal API client; its ID, secret and token URL go in the initialisation sheet">
          <TaskClip
            title="4. Create a personal API client"
            src="/prereq/videos/api-client-credentials.mp4"
            steps={[
              <>In Manage Workspace, API, select Create personal API client.</>,
              <>Name it, select the HPE GreenLake Cloud Platform service, and create it.</>,
              <>Record the client ID, client secret and the per-workspace token URL. The secret is displayed only once.</>,
              <>Enter all three in the initialisation sheet.</>,
            ]}
          />
          <Text size="xsmall" color="text-weak">
            The recording stops before the client ID and secret are displayed.
          </Text>
        </Section>
        <Section level={3} title="Management network cabling" summary="Admin, iLO and CDM ports on every controller">
          <Text size="small">
            The Cloud Connectivity wizard and DSCC reach the array over its management network. One management IP is shared across
            controllers with failover to a standby link, so every controller must be cabled.
          </Text>
          <Instructions
            items={[
              <>Admin port: on each controller, connect the admin port to the management LAN switch. Only one link is active at a time, so cable all controllers.</>,
              <>iLO port: on each controller, connect the out-of-band management port to the same network.</>,
              <>
                CDM ports: connect each controller chassis CDM Ethernet port using the supplied OCuLink adapter, plus at least one
                drive-chassis CDM per rack, to the same network. CDM ports self-assign link-local addresses and require no external IP.
              </>,
            ]}
          />
        </Section>
        <Section level={3} title="This workstation" summary="On the array's subnet, running as Administrator">
          <Instructions
            items={[
              <>The array is racked, cabled and powered on.</>,
              <>This workstation is on the same subnet as the array, so it can reach the link-local wizard address.</>,
              <>The application is running as administrator, so it can set the system clock.</>,
              <>
                The packaged executable ships the runtime the browser automation needs. For a source installation, ensure the Microsoft
                Visual C++ redistributable (x64) is present.
              </>,
            ]}
          />
        </Section>
      </Box>
    </StepShell>
  );
}
