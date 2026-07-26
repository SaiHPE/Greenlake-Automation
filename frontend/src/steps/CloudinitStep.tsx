import { Box, Button, FormField, NameValueList, NameValuePair, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { launchDiscoveryTool, RunEvent, RunRecord, startCloudinit } from '../api';
import { InlineNotification, Surface } from '../ui/primitives';
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

export function CloudinitStep({ runId, run, events, form, onDone }: Props) {
  // 169.254.0.0 is the placeholder the workbook carries when no per-boot address was recorded, so
  // the field starts empty and the operator must paste the current one.
  const [url, setUrl] = useState(form.cloudinit_url.includes('169.254.0.0') ? '' : form.cloudinit_url);
  const [error, setError] = useState<string | null>(null);
  const [discoveryBusy, setDiscoveryBusy] = useState(false);
  const [discovery, setDiscovery] = useState<{ ok: boolean; text: string } | null>(null);
  const { step } = useStepContext();

  const mine = events.filter((event) => event.phase === 'CLOUDINIT_CONNECT');
  const running = run?.status === 'running' && run?.current_phase === 'CLOUDINIT_CONNECT';
  // This step's own outcome, not the phase of whatever follows: a custom run may have no DSCC step.
  const { state } = useStepState(step, run, events);
  const connected = state === 'complete';
  const awaitingSubmit =
    run?.status === 'waiting_for_operator' &&
    run?.current_phase === 'CLOUDINIT_CONNECT' &&
    mine.some((event) => event.event_type === 'operator.review_ready');
  const valid = url.trim().startsWith('https://169.254.') && !url.trim().includes('169.254.0.0');

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
      description="Populates the array's on-box wizard with the network configuration from the workbook, then connects the array to HPE GreenLake."
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Paste the array wizard address and start the connection."
      footerNote="Values are verified against the array's own review screen immediately before submission."
      gate={
        awaitingSubmit
          ? {
              title: 'Submit the wizard in the array console',
              message:
                'The values are populated and verified. Select Submit in the browser window that is open on the array wizard; this step continues as soon as the array reports connected.',
            }
          : null
      }
      actions={
        connected ? (
          <Button primary label="Continue" onClick={onDone} />
        ) : (
          <Button
            primary
            busy={running}
            label={running ? 'Connecting' : 'Populate and connect'}
            disabled={!valid}
            onClick={start}
          />
        )
      }
    >
      <Surface
        title="Array wizard address"
        description="The link-local address changes on every boot; paste the current value."
        actions={
          <Button busy={discoveryBusy} label="Launch the HPE Discovery Tool" onClick={openDiscovery} />
        }
      >
        <Box width="large" flex={false}>
          <FormField
            label="Cloud Connectivity URL"
            htmlFor="cloudinit-url"
            help={`Search the Discovery Tool for ${run?.serial_number ?? 'the serial number'} and copy the wizard link.`}
            error={url.trim() && !valid ? 'Enter the link-local address, for example https://169.254.12.34/cloudinit' : undefined}
          >
            <TextInput
              id="cloudinit-url"
              placeholder="https://169.254.x.x/cloudinit"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
          </FormField>
        </Box>
        {discovery && (
          <Box pad={{ top: 'xsmall' }} flex={false}>
            <StatusIndicator state={discovery.ok ? 'complete' : 'failed'} label={discovery.text} />
          </Box>
        )}
      </Surface>

      <Surface
        title="Configuration to be applied"
        description="Review these here. To change any value, return to the initialisation sheet."
      >
        <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'medium' }}>
          <NameValuePair name="Management IP">
            <Text>{form.mgmt_ipv4 || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Subnet mask">
            <Text>{form.mask || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Gateway">
            <Text>{form.gateway || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="DNS">
            <Text>{dns || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="NTP">
            <Text>{form.ntp || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Time zone">
            <Text>{form.timezone || '—'}</Text>
          </NameValuePair>
          <NameValuePair name="Proxy">
            <Text>{proxy}</Text>
          </NameValuePair>
        </NameValueList>
        <InlineNotification
          tone="info"
          title="A wrong address cannot be applied"
          message="The array wizard discards typed values if it is left idle, so the tool re-reads the review screen immediately before submitting and refuses to proceed if the management IP does not match the values above."
        />
      </Surface>

      {connected && (
        <InlineNotification
          tone="ok"
          title="The array is connected to HPE GreenLake"
          message="Cloud connectivity is established. Continue to DSCC setup."
        />
      )}
    </StepShell>
  );
}
