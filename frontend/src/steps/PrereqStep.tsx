import { Anchor, Box, Button, Notification, Spinner, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { StatusCritical, StatusGood } from 'grommet-icons';
import { ReactNode, useEffect, useState } from 'react';
import { API, ConnectivityResult, FirewallRule, checkConnectivity, firewallTxtUrl, getFirewall } from '../api';
import { ClockSync } from '../ClockSync';
import { Instructions, Section } from '../components';

function FirewallTable({ rules }: { rules: FirewallRule[] }) {
  if (!rules.length) {
    return (
      <Text size="small" color="text-weak">
        Loading firewall endpoints…
      </Text>
    );
  }
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {['Endpoint (FQDN)', 'Port', 'Initiator', 'Purpose'].map((h) => (
            <TableCell key={h} scope="col" border="bottom">
              <Text size="xsmall" weight="bold">
                {h}
              </Text>
            </TableCell>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rules.map((r) => (
          <TableRow key={r.fqdn}>
            <TableCell>
              <Text size="xsmall">{r.fqdn}</Text>
            </TableCell>
            <TableCell>
              <Text size="xsmall" color="text-weak">
                {r.port}
              </Text>
            </TableCell>
            <TableCell>
              <Text size="xsmall" color="text-weak">
                {r.initiator}
              </Text>
            </TableCell>
            <TableCell>
              <Text size="xsmall" color="text-weak">
                {r.purpose}
              </Text>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function Video({ src }: { src: string }) {
  return (
    <Box border round="xsmall" overflow="hidden" background="black" width={{ max: '560px' }} flex={false}>
      <video src={src} controls preload="metadata" style={{ width: '100%', display: 'block' }} />
    </Box>
  );
}

// A numbered sub-step: its instructions plus the matching HPE walkthrough clip.
function StepClip({ title, steps, src }: { title: string; steps: ReactNode[]; src: string }) {
  return (
    <Box gap="xsmall" pad={{ top: 'small' }} flex={false}>
      <Text weight="bold">{title}</Text>
      <Instructions items={steps} />
      <Video src={src} />
    </Box>
  );
}

// What the HPE engineer must do BEFORE running the automation — the manual steps from HPE's
// official onboarding checklist that this tool does not (and should not) perform.
export function PrereqStep({ onDone }: { onDone: () => void }) {
  const [rules, setRules] = useState<FirewallRule[]>([]);
  const [conn, setConn] = useState<ConnectivityResult[] | null>(null);
  const [allReachable, setAllReachable] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFirewall()
      .then((r) => setRules(r.rules))
      .catch(() => undefined);
  }, []);

  const runConnectivity = async () => {
    setBusy(true);
    setError(null);
    try {
      const r = await checkConnectivity();
      setConn(r.results);
      setAllReachable(r.all_reachable);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box gap="medium">
      <Notification
        status="info"
        title="Do these first — the automation starts after they're done"
        message="This tool automates adding the device + subscription in GreenLake, the on-array Cloud Connectivity Wizard, and the DSCC Set Up System wizard. Everything below is manual setup HPE requires beforehand. The clips are HPE's own walkthroughs."
      />

      <Section title="1 · HPE GreenLake account & workspace">
        <Instructions
          items={[
            <>Activate your software subscriptions from the <b>Electronic Software Delivery (ESD) Receipt</b> email.</>,
            <>Create (or sign in to) your <Anchor href="https://console.greenlake.hpe.com" target="_blank" label="HPE GreenLake" /> account, then do the three steps below <b>in order</b>.</>,
          ]}
        />
        <StepClip
          title="1. Create the workspace"
          src="/prereq/videos/create-workspace.mp4"
          steps={[
            <>Click <b>Create Workspace</b> and provide the workspace name, country, street address, city/state, ZIP, phone and email.</>,
            <>Accept the legal terms and click <b>Create Workspace</b> — you become the workspace Administrator and your dashboard opens.</>,
          ]}
        />
        <StepClip
          title="2. Deploy Data Services Cloud Console"
          src="/prereq/videos/deploy-dscc.mp4"
          steps={[
            <>On the workspace <b>Home</b>, click <b>Find Services</b> → scroll to <b>Storage</b> → <b>Data Services</b> → <b>Provision</b>.</>,
            <>Select the <b>Deployment Region nearest the array</b>, accept the Terms of Service, and click <b>Deploy</b>.</>,
            <>At the top of the page, click <b>Launch</b> to open Data Services Cloud Console.</>,
          ]}
        />
        <StepClip
          title="3. Assign yourself the Data Services Administrator role"
          src="/prereq/videos/assign-admin.mp4"
          steps={[
            <><b>Manage Workspace → Identity &amp; Access → Assign Role</b>: select your user, set <b>Service Manager = Data Services</b> and <b>Role = Administrator</b>, leave <b>Limit Resource Access</b> off, and click <b>Assign Role</b>.</>,
            <>Launch Data Services and confirm the <b>Setup</b>, <b>Block Storage</b> and <b>Data Ops Manager</b> services appear.</>,
          ]}
        />
      </Section>

      <Section title="2 · Create the API client (for this tool)">
        <StepClip
          title="4. Create a personal API client"
          src="/prereq/videos/api-client-credentials.mp4"
          steps={[
            <>In GreenLake, go to <b>Manage Workspace → API</b> and click <b>Create personal API client</b>.</>,
            <>Give it a name and select the <b>HPE GreenLake Cloud Platform</b> service, then click <b>Create</b>.</>,
            <>Copy the <b>Client ID</b>, <b>Client Secret</b>, and the per-workspace <b>token URL</b> (…/authorization/v2/oauth2/&lt;tenant&gt;/token) — you only see the secret once.</>,
            <>Put those three into the <b>Initialisation sheet</b> (section 6 below) — that's how this tool authenticates to GreenLake.</>,
          ]}
        />
        <Text size="xsmall" color="text-weak">The clip stops before the Client ID / secret are shown.</Text>
      </Section>

      <Section title="3 · Network, firewall & time">
        <Text size="small">
          The customer's network team must allow these HPE endpoints — all <b>TCP 443</b> outbound.
          <i> &lt;instance&gt;</i> is your DSCC region: <b>jp1</b> (Japan), or uk1, eu1, uae1, us1. Download the list to
          forward to them, then use <b>Test connectivity</b> once they confirm the ports are open.
        </Text>
        <Box direction="row" gap="medium" align="center" wrap>
          <Anchor href={firewallTxtUrl()} download="alletra-firewall-requirements.txt" label="Download firewall list (.txt)" />
          <Button
            label={busy ? 'Testing…' : 'Test connectivity (TCP 443)'}
            disabled={busy}
            onClick={runConnectivity}
          />
          {busy && <Spinner />}
        </Box>
        <FirewallTable rules={rules} />
        {error && <Notification status="critical" title="Connectivity test failed" message={error} onClose={() => setError(null)} />}
        {conn && (
          <Box gap="xsmall" pad={{ top: 'xsmall' }} flex={false}>
            <Notification
              status={allReachable ? 'normal' : 'warning'}
              title={allReachable ? 'All tested endpoints are reachable on TCP 443' : 'Some endpoints are not reachable'}
              message={
                allReachable
                  ? 'The jump box can reach the HPE endpoints directly.'
                  : 'Ask the network team to open the blocked destinations below (outbound TCP 443). A proxy-only path will also show as blocked here.'
              }
            />
            {conn.map((c) => (
              <Box key={c.host} direction="row" gap="small" align="center">
                {c.reachable ? (
                  <StatusGood color="status-ok" size="small" />
                ) : (
                  <StatusCritical color="status-critical" size="small" />
                )}
                <Text size="xsmall">{c.host}</Text>
                <Text size="xsmall" color="text-weak">
                  — {c.detail}
                </Text>
              </Box>
            ))}
          </Box>
        )}
        <Instructions
          items={[
            <>Local array discovery (HPE Discovery app) uses <b>mDNS on UDP 5353</b>.</>,
            <>The array's DNS must resolve these global names (e.g. <b>device.cloud.hpe.com</b>).</>,
            <>
              Reserved for array operations — <b>do not assign these</b>: 16.1.8.11/27/43/59 and
              16.1.9.11/27/43/59 (the CDM link-local range).
            </>,
            <><b>System time must be within 2 minutes</b> of correct, or the array can't connect to DSCC. Use NTP, or the <b>Sync system clock</b> control below.</>,
          ]}
        />
      </Section>

      <ClockSync title="System clock (must be within 2 minutes of correct)" />

      <Section title="4 · Management-network cabling (each controller → management switch)">
        <Notification
          status="warning"
          title="The array must be on the management network before onboarding"
          message="The Cloud Connectivity Wizard and DSCC reach the array over its management network. HPE shares one management IP across the controllers and fails over to a standby link, so EVERY controller must be cabled for redundancy. Connect all three port types below to the management switch."
        />
        <Instructions
          items={[
            <>
              <b>Admin port</b> — on <b>each controller</b>, run a CAT-5e / Cat 6 Ethernet cable from the Admin
              port to the <b>management LAN switch</b>. The controllers share one admin IP and only one link is
              active at a time (it fails over to the surviving link), so cable <b>all</b> controllers.
            </>,
            <>
              <b>iLO port</b> — on <b>each controller</b>, connect the iLO (out-of-band management) port to the{' '}
              <b>same management network</b>.
            </>,
            <>
              <b>CDM ports</b> — connect each controller chassis&apos;s <b>CDM Ethernet port</b> (using the supplied
              OCuLink-to-Ethernet dongle), plus at least one drive-chassis CDM per rack, to the <b>same network</b>{' '}
              as the management ports. CDMs auto-configure <b>link-local</b> addresses and need <b>no external IP</b>.
            </>,
          ]}
        />
        <Text size="xsmall" color="text-weak">
          Source: HPE&apos;s{' '}
          <Anchor
            href="https://infosight.hpe.com/welcomecenter/getting-started/checklist?connectopt=HPE%20Cloud%20Connectivity%20Wizard%2FDiscovery%20Tool&greenlakeplatform=HPE%20GreenLake%20Cloud%20Platform&model=B10140&opt=factory&product=alletraB10k"
            target="_blank"
            label="onboarding checklist"
          />{' '}
          and the <i>Installing and configuring factory-integrated system</i> guide (sd00002405).
        </Text>
      </Section>

      <Section title="5 · This jump box">
        <Instructions
          items={[
            <>The array is racked, cabled, and <b>powered on</b>.</>,
            <>This jump box is on the <b>same subnet</b> as the array (so it can reach the link-local <b>169.254.x</b> Cloud Connectivity URL).</>,
            <>Run this app <b>as Administrator</b> (so the clock-sync can set the system time).</>,
            <>Browser runtime: the packaged <b>.exe ships the VC++ runtime</b> Chromium needs; for a source/pip install, ensure the <b>Microsoft Visual C++ Redistributable (x64)</b> is installed.</>,
          ]}
        />
      </Section>

      <Section title="6 · Get the Initialisation sheet">
        <Text size="small">
          Download the workbook now, fill every required field (API credentials, serial, subscription key,
          network, DSCC details), and upload it on the next step. One workbook = one array. The workbook
          includes a <b>Prerequisites</b> tab with this firewall list and the cabling checklist.
        </Text>
        <Box direction="row" gap="small">
          <Anchor
            href={`${API}/init-sheet/template`}
            download="Initialisation_sheet.xlsx"
            label="Download Initialisation_sheet.xlsx"
          />
        </Box>
      </Section>

      <Button primary label="I've completed these → Initialisation sheet" onClick={onDone} alignSelf="start" />
    </Box>
  );
}
