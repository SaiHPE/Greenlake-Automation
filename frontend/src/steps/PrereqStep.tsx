import { Anchor, Box, Button, DataTable, Text, TextInput } from 'grommet';
import { ReactNode, useEffect, useState } from 'react';
import {
  API,
  ConnectivityResult,
  FirewallRule,
  ProxyStatus,
  checkConnectivity,
  firewallTxtUrl,
  getFirewall,
  getProxyStatus,
  saveProxy,
} from '../api';
import { ClockSync } from '../ClockSync';
import { Instructions } from '../components';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator, StepState } from '../ui/status';
import { StepShell } from '../ui/StepShell';

/** A numbered task with its HPE walkthrough recording. */
function TaskClip({ title, steps, src }: { title: string; steps: ReactNode[]; src: string }) {
  return (
    <Box gap="xsmall" pad={{ top: 'small' }} flex={false}>
      <Text weight="bold" color="text-strong">
        {title}
      </Text>
      <Instructions items={steps} />
      <Box round="xsmall" overflow="hidden" background="black" width={{ max: 'large' }} flex={false}>
        <video src={src} controls preload="metadata" style={{ width: '100%', display: 'block' }} />
      </Box>
    </Box>
  );
}

/**
 * The manual work HPE requires before any automation runs. This tool does not perform these, and
 * deliberately does not pretend to — it verifies what it can and hands over the rest.
 */
export function PrereqStep({ onDone, state }: { onDone: () => void; state: StepState }) {
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

  useEffect(() => {
    getProxyStatus()
      .then((status) => {
        setProxy(status);
        setProxyInput(status.manual ?? '');
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
      setProxyInput(status.manual ?? '');
      await test();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setSavingProxy(false);
    }
  };

  const reachable = connectivity?.filter((result) => result.reachable).length ?? 0;

  return (
    <StepShell
      title="Prerequisites"
      description="Validate connectivity from this workstation to HPE GreenLake and the array before proceeding."
      state={state}
      error={error}
      onDismissError={() => setError(null)}
      footerNote="This step makes no changes to the array."
      actions={
        <>
          <Button
            as="a"
            href={`${API}/init-sheet/template`}
            download="Initialisation_sheet.xlsx"
            label="Download the initialisation sheet"
          />
          <Button primary label="Continue" onClick={onDone} />
        </>
      }
    >
      <InlineNotification
        tone="info"
        title="Complete these before starting"
        message="This tool automates device and subscription registration in HPE GreenLake, the on-array Cloud Connectivity wizard, and DSCC setup. Everything on this page is preparation HPE requires beforehand; the recordings are HPE's own walkthroughs."
      />

      <Surface title="HPE GreenLake account and workspace">
        <Instructions
          items={[
            <>Activate the software subscriptions from the Electronic Software Delivery receipt email.</>,
            <>
              Create or sign in to your{' '}
              <Anchor href="https://console.greenlake.hpe.com" target="_blank" label="HPE GreenLake" /> account, then
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
              In Manage Workspace, Identity and Access, Assign Role: select your user, set service manager to Data
              Services and role to Administrator, leave resource-access limits off, and assign.
            </>,
            <>Launch Data Services and confirm the Setup, Block Storage and Data Ops Manager services appear.</>,
          ]}
        />
      </Surface>

      <Surface title="API client" description="How this tool authenticates to HPE GreenLake.">
        <TaskClip
          title="4. Create a personal API client"
          src="/prereq/videos/api-client-credentials.mp4"
          steps={[
            <>In Manage Workspace, API, select Create personal API client.</>,
            <>Name it, select the HPE GreenLake Cloud Platform service, and create it.</>,
            <>
              Record the client ID, client secret and the per-workspace token URL. The secret is displayed only once.
            </>,
            <>Enter all three in the initialisation sheet.</>,
          ]}
        />
        <Text size="xsmall" color="text-weak">
          The recording stops before the client ID and secret are displayed.
        </Text>
      </Surface>

      <Surface
        title="Connectivity"
        description="These endpoints must be reachable on outbound TCP 443. Request firewall exceptions from the network team for any shown as blocked."
        actions={
          <>
            <Anchor href={firewallTxtUrl(region)} download="alletra-firewall-requirements.txt" label="Download list" />
            <Button busy={busy} label={connectivity ? 'Retest' : 'Test connectivity'} onClick={test} />
          </>
        }
      >
        <Box direction="row" gap="small" align="center" flex={false}>
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
        </Box>

        {connectivity && (
          <>
            <DataTable
              columns={[
                {
                  property: 'host',
                  header: 'Endpoint',
                  render: (result: ConnectivityResult) => <Text size="small">{result.host}</Text>,
                },
                {
                  property: 'reachable',
                  header: 'Result',
                  render: (result: ConnectivityResult) => (
                    <StatusIndicator
                      state={result.reachable ? 'complete' : 'failed'}
                      label={result.reachable ? 'Reachable' : 'Blocked'}
                    />
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
            />
            <TableSummary>
              {reachable} reachable · {connectivity.length - reachable} blocked
            </TableSummary>
          </>
        )}

        {connectivity && !allReachable && (
          <InlineNotification
            tone="warning"
            title="Some endpoints are not reachable"
            message="Ask the network team to permit the blocked destinations on outbound TCP 443, or set the correct proxy below."
          />
        )}

        {!connectivity && rules.length > 0 && (
          <>
            <DataTable
              columns={[
                { property: 'fqdn', header: 'Endpoint', render: (rule: FirewallRule) => <Text size="small">{rule.fqdn}</Text> },
                { property: 'port', header: 'Port', render: (rule: FirewallRule) => <Text size="small">{rule.port}</Text> },
                {
                  property: 'initiator',
                  header: 'Initiator',
                  render: (rule: FirewallRule) => (
                    <Text size="small" color="text-weak">
                      {rule.initiator}
                    </Text>
                  ),
                },
                {
                  property: 'purpose',
                  header: 'Purpose',
                  render: (rule: FirewallRule) => (
                    <Text size="small" color="text-weak">
                      {rule.purpose}
                    </Text>
                  ),
                },
              ]}
              data={rules}
              primaryKey="fqdn"
            />
            <TableSummary>{rules.length} endpoints required</TableSummary>
          </>
        )}

        <Instructions
          items={[
            <>Local array discovery uses mDNS on UDP 5353.</>,
            <>The array's DNS must resolve the HPE global names, for example device.cloud.hpe.com.</>,
            <>
              Reserved for array operations, do not assign: 16.1.8.11/27/43/59 and 16.1.9.11/27/43/59, the CDM
              link-local range.
            </>,
          ]}
        />
      </Surface>

      <Surface
        title="Proxy"
        description="Detected from the operating system, as a browser would resolve it. Provide an override only if the detected value is incorrect."
      >
        {proxy && (
          <Text size="small">
            {proxy.source === 'manual' && `In use: manual proxy ${proxy.effective}`}
            {proxy.source === 'system' && `In use: detected system proxy ${proxy.detected}`}
            {proxy.source === 'direct' && 'No proxy detected; connecting directly.'}
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
          <Button
            size="small"
            busy={savingProxy}
            label="Save and retest"
            onClick={() => applyProxy(proxyInput.trim() || null)}
          />
          {proxy?.manual && (
            <Button size="small" label="Clear override" disabled={savingProxy} onClick={() => applyProxy(null)} />
          )}
        </Box>
      </Surface>

      {/* HPE GreenLake rejects authentication when the workstation clock has drifted. */}
      <ClockSync title="Workstation clock" />

      <Surface title="Management network cabling">
        <InlineNotification
          tone="warning"
          title="The array must be on the management network before onboarding"
          message="The Cloud Connectivity wizard and DSCC reach the array over its management network. One management IP is shared across controllers with failover to a standby link, so every controller must be cabled."
        />
        <Instructions
          items={[
            <>
              Admin port: on each controller, connect the admin port to the management LAN switch. Only one link is
              active at a time, so cable all controllers.
            </>,
            <>iLO port: on each controller, connect the out-of-band management port to the same network.</>,
            <>
              CDM ports: connect each controller chassis CDM Ethernet port using the supplied OCuLink adapter, plus at
              least one drive-chassis CDM per rack, to the same network. CDM ports self-assign link-local addresses and
              require no external IP.
            </>,
          ]}
        />
        <Text size="xsmall" color="text-weak">
          Source: HPE's{' '}
          <Anchor
            href="https://infosight.hpe.com/welcomecenter/getting-started/checklist?connectopt=HPE%20Cloud%20Connectivity%20Wizard%2FDiscovery%20Tool&greenlakeplatform=HPE%20GreenLake%20Cloud%20Platform&model=B10140&opt=factory&product=alletraB10k"
            target="_blank"
            label="onboarding checklist"
          />{' '}
          and the installation guide sd00002405.
        </Text>
      </Surface>

      <Surface title="This workstation">
        <Instructions
          items={[
            <>The array is racked, cabled and powered on.</>,
            <>This workstation is on the same subnet as the array, so it can reach the link-local wizard address.</>,
            <>The application is running as administrator, so it can set the system clock.</>,
            <>
              The packaged executable ships the runtime the browser automation needs. For a source installation, ensure
              the Microsoft Visual C++ redistributable (x64) is present.
            </>,
          ]}
        />
      </Surface>
    </StepShell>
  );
}
