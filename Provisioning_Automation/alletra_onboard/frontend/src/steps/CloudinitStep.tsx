import { Box, Button, Notification, Spinner, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { launchDiscoveryTool, RunEvent, RunRecord, startCloudinit } from '../api';
import { EventLog, Instructions, Section, StatusTag } from '../components';
import { WorkItemForm } from '../workItem';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  form: WorkItemForm;
  onDone: () => void;
}

function ReviewRow({ label, value }: { label: string; value: string }) {
  return (
    <Box direction="row" gap="small">
      <Box width="180px" flex={false}>
        <Text size="small" color="text-weak">
          {label}
        </Text>
      </Box>
      <Text size="small" weight="bold">
        {value || '—'}
      </Text>
    </Box>
  );
}

export function CloudinitStep({ runId, run, events, form, onDone }: Props) {
  // 169.254.0.0 is the placeholder the work item carries when no per-boot URL was set — start
  // with an empty box so the operator must paste the real one from the Discovery Tool.
  const [url, setUrl] = useState(form.cloudinit_url.includes('169.254.0.0') ? '' : form.cloudinit_url);
  const [error, setError] = useState<string | null>(null);
  const [discoveryBusy, setDiscoveryBusy] = useState(false);
  const [discovery, setDiscovery] = useState<{ ok: boolean; text: string } | null>(null);

  const stepEvents = events.filter((e) => e.phase === 'CLOUDINIT_CONNECT');
  const running = run?.status === 'running' && run?.current_phase === 'CLOUDINIT_CONNECT';
  const connected = run?.current_phase === 'DSCC_SETUP_SYSTEM' && run?.status === 'ready';
  const failed =
    run?.current_phase === 'CLOUDINIT_CONNECT' &&
    (run?.status === 'retryable_failure' || run?.status === 'terminal_failure');
  // Must be a real link-local URL — reject the 169.254.0.0 placeholder (it's not a host).
  const validUrl = url.trim().startsWith('https://169.254.') && !url.trim().includes('169.254.0.0');

  const dns = form.dns
    .split(';')
    .map((value) => value.trim())
    .filter(Boolean)
    .join(', ');
  const proxy = form.proxy_host ? `${form.proxy_host}:${form.proxy_port || '8080'}` : 'none';

  const start = async () => {
    setError(null);
    try {
      await startCloudinit(runId, url.trim(), true);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const openDiscovery = async () => {
    setDiscoveryBusy(true);
    setDiscovery(null);
    try {
      const result = await launchDiscoveryTool();
      if (result.launched) {
        setDiscovery({ ok: true, text: `Opened ${result.path?.split('\\').pop() ?? 'Discovery Tool'}` });
      } else {
        setDiscovery({ ok: false, text: result.error ?? 'Could not open the Discovery Tool' });
      }
    } catch (exc: any) {
      setDiscovery({ ok: false, text: String(exc.message ?? exc) });
    } finally {
      setDiscoveryBusy(false);
    }
  };

  return (
    <Box gap="medium">
      <Section title="1 · Get the wizard URL from the Discovery Tool">
        <Instructions
          items={[
            <>Click <b>Open Discovery Tool</b> below (it launches the app from this jump box&apos;s Desktop).</>,
            <>Search for the array&apos;s serial number ({run?.serial_number ?? '…'}).</>,
            <>Copy the wizard link — it looks like <b>https://169.254.x.x/cloudinit</b> (it changes every boot).</>,
            <>Paste it into the box below.</>,
          ]}
        />
        <Box direction="row" gap="small" align="center">
          <Button
            label={discoveryBusy ? 'Opening…' : 'Open Discovery Tool'}
            disabled={discoveryBusy}
            onClick={openDiscovery}
          />
          {discovery && (
            <Text size="small" color={discovery.ok ? 'status-ok' : 'status-critical'}>
              {discovery.text}
            </Text>
          )}
        </Box>
        <Box direction="row" gap="small" align="center" width="large">
          <TextInput placeholder="https://169.254.x.x/cloudinit" value={url} onChange={(e) => setUrl(e.target.value)} />
        </Box>
        {url.trim() === '' ? (
          <Text size="small" color="text-weak">
            Paste the array&apos;s <b>https://169.254.x.x/cloudinit</b> URL from the Discovery Tool (it changes every boot).
          </Text>
        ) : !validUrl ? (
          <Text size="small" color="status-critical">
            That isn&apos;t a usable array URL — paste the link-local <b>https://169.254.x.x/cloudinit</b> from the Discovery Tool (not 169.254.0.0).
          </Text>
        ) : null}
      </Section>

      <Section title="2 · Review the values that will be applied">
        <Text size="small">
          The automation fills these and Submits in one motion — review them <b>here</b>, not in the
          wizard. (The on-array wizard discards typed Network values if it sits idle on its Review
          screen, so we don&apos;t pause there.)
        </Text>
        <Box gap="xsmall" pad={{ vertical: 'small' }}>
          <ReviewRow label="Management IP" value={form.mgmt_ipv4} />
          <ReviewRow label="Netmask" value={form.mask} />
          <ReviewRow label="Gateway" value={form.gateway} />
          <ReviewRow label="DNS" value={dns} />
          <ReviewRow label="NTP" value={form.ntp} />
          <ReviewRow label="Timezone" value={form.timezone} />
          <ReviewRow label="Proxy" value={proxy} />
        </Box>
        <Notification
          status="info"
          message="A safety check re-reads the wizard's Review screen right before Submit and refuses to apply if the Network IP doesn't match these values — so a wrong (link-local) IP can never be applied. To change anything, go back to Array details."
        />
      </Section>

      <Section title="3 · Fill & connect">
        <Text size="small">
          A browser opens at the URL above, fills the wizard, and connects the array. This page
          updates live and continues automatically once the array reports connected.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button
            primary
            disabled={!validUrl || running || connected}
            label={running ? 'Filling & connecting…' : 'Fill & connect'}
            onClick={start}
          />
          {running && <Spinner />}
          <StatusTag status={run?.current_phase === 'CLOUDINIT_CONNECT' ? run?.status : undefined} />
        </Box>
      </Section>

      {error && <Notification status="critical" title="Could not start" message={error} onClose={() => setError(null)} />}
      {failed && (
        <Notification
          status="critical"
          title="The wizard run did not complete"
          message="Nothing was applied. Check the message in Progress (and the screenshot in .alletra_onboard/artifacts), then click Fill & connect again."
        />
      )}
      {connected && (
        <Notification status="normal" title="Array connected to HPE GreenLake" message="Cloud connectivity is done — continue to DSCC Setup." />
      )}

      <Section title="Progress">
        <EventLog events={stepEvents} emptyText="Paste the URL and click Fill & connect to start." />
      </Section>

      <Button primary label="Continue → DSCC Setup" disabled={!connected} onClick={onDone} alignSelf="start" />
    </Box>
  );
}
