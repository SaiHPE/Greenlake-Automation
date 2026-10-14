import { Box, Button, FormField, NameValueList, NameValuePair, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { launchDiscoveryTool, RunEvent, RunRecord, startCloudinit } from '../api';
import { Guidance, Panel, StatusLine } from '../ui/blocks';
import { StatusIndicator } from '../ui/status';
import { StepShell } from '../ui/StepShell';
import { useStepContext } from '../ui/StepContext';
import { useStepState } from '../ui/useStepState';
import { WorkItemForm } from '../workItem';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  form: WorkItemForm;
  onDone: () => void;
}

/** IPv4 169.254.x.x (not the 169.254.0.0 placeholder) or bracketed IPv6 fe80::, zone optional. */
export function isLinkLocalWizardUrl(raw: string): boolean {
  const value = (raw ?? '').trim();
  if (!/^https:\/\//i.test(value)) return false;
  const ipv4 = /^https:\/\/169\.254\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/.*)?$/i;
  const ipv6 = /^https:\/\/\[fe80:[0-9a-f:]*(?:%25?[A-Za-z0-9._-]+)?\](?::\d+)?(?:\/.*)?$/i;
  if (ipv4.test(value)) return !/\/\/169\.254\.0\.0(?:[:/]|$)/.test(value);
  return ipv6.test(value);
}

function Value({ children }: { children: string }) {
  return children ? <Text size="small">{children}</Text> : <Text size="small" color="text-weak" a11yTitle="No value">--</Text>;
}

export function CloudinitStep({ runId, run, events, form, onDone }: Props) {
  // 169.254.0.0 is the placeholder the workbook carries when no per-boot address was recorded, so
  // the field starts empty and the operator must paste the current one.
  const [url, setUrl] = useState(form.cloudinit_url.includes('169.254.0.0') ? '' : form.cloudinit_url);
  const [error, setError] = useState<string | null>(null);
  const [discoveryBusy, setDiscoveryBusy] = useState(false);
  const [discovery, setDiscovery] = useState<{ ok: boolean; text: string } | null>(null);
  const { step, nextTitle } = useStepContext();

  const mine = events.filter((event) => event.phase === 'CLOUDINIT_CONNECT');
  const running = run?.status === 'running' && run?.current_phase === 'CLOUDINIT_CONNECT';
  // This step's own outcome, not the phase of whatever follows: a custom run may have no DSCC step.
  const { state } = useStepState(step, run, events);
  const connected = state === 'complete';
  const awaitingSubmit =
    run?.status === 'waiting_for_operator' &&
    run?.current_phase === 'CLOUDINIT_CONNECT' &&
    mine.some((event) => event.event_type === 'operator.review_ready');
  // Accepts BOTH link-local families: the Discovery Tool reports whichever it found the array on,
  // and an IPv6-only result is normal (reported live: serial CZ2D2K014S returned only
  // https://[fe80::6095:14a0:b25d:fcb0], and this gate rejected it so the step could not start).
  // The path is optional here because the tool's Launch field gives a bare origin; the backend
  // normalises and is authoritative; see domain/cloudinit_url.py.
  const valid = isLinkLocalWizardUrl(url);

  const dns = form.dns
    .split(';')
    .map((value) => value.trim())
    .filter(Boolean)
    .join(', ');
  const proxy = form.proxy_host ? `${form.proxy_host}:${form.proxy_port || '8080'}` : 'None';

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
      setDiscovery(
        result.launched
          ? { ok: true, text: `Opened ${result.path?.split('\\').pop() ?? 'the Discovery Tool'}` }
          : { ok: false, text: result.error ?? 'The Discovery Tool could not be opened' },
      );
    } catch (exc: any) {
      setDiscovery({ ok: false, text: String(exc.message ?? exc) });
    } finally {
      setDiscoveryBusy(false);
    }
  };

  return (
    <StepShell
      title="Cloud Connectivity"
      description="Fills the array's own setup wizard with the network values from the workbook, then connects the array to HPE GreenLake."
      error={error}
      onDismissError={() => setError(null)}
      gate={
        awaitingSubmit
          ? {
              title: 'Submit the wizard in the array console',
              message:
                'The values are filled in and checked. Select Submit in the browser window open on the array wizard; this step carries on as soon as the array reports connected.',
            }
          : null
      }
      primary={
        connected
          ? { label: nextTitle ? `Continue to ${nextTitle}` : 'Continue', onClick: onDone }
          : {
              label: running ? 'Connecting' : 'Fill in and connect',
              busy: running,
              onClick: start,
              blocked: valid ? undefined : "Paste the array's wizard address first: https://169.254.x.x/cloudinit or https://[fe80::…]/cloudinit.",
            }
      }
      guidance={
        <Guidance
          items={[
            { title: 'The address changes on every boot', body: 'Search the HPE Discovery Tool for the serial number and copy the wizard link. IPv4 or IPv6, whichever it reports.' },
            {
              title: 'A wrong address cannot be applied',
              body: 'The array wizard forgets typed values if it is left idle, so the tool reads its review screen again just before submitting and refuses if the management IP does not match the workbook.',
            },
            { title: 'To change a value', body: 'Go back to the initialisation sheet, correct the workbook and upload it again.' },
          ]}
        />
      }
    >
      {connected && (
        <StatusLine state="complete" title="The array is connected to HPE GreenLake">
          Cloud connectivity is established.
        </StatusLine>
      )}
      {running && !awaitingSubmit && <StatusLine state="running">Filling in the array wizard. Each screen appears in Activity, below.</StatusLine>}

      <Panel
        title="Array wizard address"
        description="The link-local address changes on every boot; paste the current one."
        right={<Button size="small" busy={discoveryBusy} label="Launch the HPE Discovery Tool" onClick={openDiscovery} />}
      >
        <Box width={{ max: 'large' }} flex={false}>
          <FormField
            label="Cloud Connectivity URL"
            htmlFor="cloudinit-url"
            name="cloudinit-url"
            help={`Search the Discovery Tool for ${run?.serial_number ?? 'the serial number'} and copy the wizard link.`}
            error={
              url.trim() && !valid
                ? 'Enter the array’s link-local address: https://169.254.12.34/cloudinit or https://[fe80::1]/cloudinit'
                : undefined
            }
          >
            <TextInput
              id="cloudinit-url"
              name="cloudinit-url"
              placeholder="https://169.254.x.x/cloudinit or https://[fe80::…]/cloudinit"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
          </FormField>
        </Box>
        {discovery && <StatusIndicator state={discovery.ok ? 'complete' : 'failed'} label={discovery.text} />}
      </Panel>

      <Panel title="Values the wizard gets" description="From the workbook. To change one, correct the workbook and upload it again.">
        <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'medium' }}>
          <NameValuePair name="Management IP">
            <Value>{form.mgmt_ipv4}</Value>
          </NameValuePair>
          <NameValuePair name="Subnet mask">
            <Value>{form.mask}</Value>
          </NameValuePair>
          <NameValuePair name="Gateway">
            <Value>{form.gateway}</Value>
          </NameValuePair>
          <NameValuePair name="DNS">
            <Value>{dns}</Value>
          </NameValuePair>
          <NameValuePair name="NTP">
            <Value>{form.ntp}</Value>
          </NameValuePair>
          <NameValuePair name="Time zone">
            <Value>{form.timezone}</Value>
          </NameValuePair>
          <NameValuePair name="Proxy">
            <Value>{proxy}</Value>
          </NameValuePair>
        </NameValueList>
      </Panel>
    </StepShell>
  );
}
