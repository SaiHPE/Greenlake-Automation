// The devices a run trusts: the key each on-site device presented the first time this run reached it,
// and the separate, deliberate action that trusts a new one. Never offered next to the error itself.
import { Box, Button, CheckBox, Heading, Paragraph, Text } from 'grommet';
import { useEffect, useState } from 'react';
import { getTrustedDevices, retrustDevice, RunEvent, TrustedDevice } from '../api';
import { mono } from './blocks';
import { InlineNotification } from './primitives';
import { StatusIcon } from './status';

const DEVICE_NAMES: Record<string, string> = { array: 'Array', switch: 'Switch', 'Linux host': 'Linux host', vCenter: 'vCenter' };
const deviceName = (d: TrustedDevice) => DEVICE_NAMES[d.device] ?? d.device;
const keyWord = (d: TrustedDevice) => (d.kind === 'ssh' ? 'SSH host key' : 'certificate');
const address = (d: TrustedDevice) => (d.port === (d.kind === 'ssh' ? 22 : 443) ? d.host : `${d.host}:${d.port}`);

function stamp(iso: string | null): string {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ''
    : d.toLocaleString([], { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function Fingerprint({ label, value, keyType }: { label: string; value: string; keyType?: string | null }) {
  return (
    <Box gap="xxsmall">
      <Text size="xsmall" color="text-weak">
        {label}
        {keyType ? ` (${keyType})` : ''}
      </Text>
      <Text size="small" style={{ ...mono, overflowWrap: 'anywhere' }}>
        {value}
      </Text>
    </Box>
  );
}

function Retrust({ runId, device, onDone }: { runId: string; device: TrustedDevice; onDone: () => void }) {
  const [checked, setChecked] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const what = keyWord(device);

  const trust = async () => {
    if (!checked) {
      setProblem(`Tick the box first: compare the new ${what} with the device's own console before you trust it.`);
      return;
    }
    setBusy(true);
    setProblem(null);
    try {
      await retrustDevice(runId, device, device.refused_fingerprint ?? '');
      onDone();
    } catch (err) {
      setProblem(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box gap="small" pad={{ top: 'xsmall' }}>
      <InlineNotification
        tone="critical"
        title={`Presented a different ${what}`}
        message={`On ${stamp(device.refused_at)} this device presented a ${what} that is not the one this run trusted, so the tool stopped and sent no password. If the device was replaced or reset on purpose, check the new fingerprint on the device's own console. If nobody changed it, stop and ask the customer's network team.`}
      />
      <Fingerprint label="Presented now" value={device.refused_fingerprint ?? ''} keyType={device.kind === 'ssh' ? device.refused_key_type : null} />
      {problem && <InlineNotification tone="warning" title="Not trusted yet" message={problem} onClose={() => setProblem(null)} />}
      <Box direction="row" gap="medium" align="center" wrap>
        <CheckBox
          checked={checked}
          onChange={(e) => setChecked(e.target.checked)}
          label={`I checked this fingerprint on the device's own console and it matches.`}
        />
        <Button label={`Trust the new ${what}`} busy={busy} onClick={trust} />
      </Box>
    </Box>
  );
}

/** Run overview: every on-site device this run trusts, with its fingerprint, and the re-trust action. */
export function TrustedDevices({ runId, events }: { runId: string; events: RunEvent[] }) {
  const [devices, setDevices] = useState<TrustedDevice[] | null>(null);
  const [bundle, setBundle] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [refresh, setRefresh] = useState(0);
  // a device trusted, refused or trusted again shows up as a run event: read the list again then
  const deviceEvents = events.filter((e) => e.event_type.startsWith('device.')).length;

  useEffect(() => {
    let live = true;
    getTrustedDevices(runId)
      .then((body) => {
        if (!live) return;
        setDevices(body.devices);
        setBundle(body.device_ca_bundle);
        setFailed(false);
      })
      .catch(() => live && setFailed(true));
    return () => {
      live = false;
    };
  }, [runId, deviceEvents, refresh]);

  return (
    <Box gap="small" flex={false}>
      <Heading level={2} size="small" margin="none">
        Trusted devices
      </Heading>
      <Paragraph size="small" margin="none" color="text-weak">
        The first time this run connects to the array, a switch, vCenter or a Linux host, the tool records the key
        the device presents. If the device later presents a different one, the tool stops before it sends a
        password. The customer can compare these fingerprints with each device's own console; the as-built lists
        them too.
        {bundle
          ? ` Array and vCenter certificates are checked against the customer's certificate authority file at ${bundle} instead; SSH keys are still recorded on first contact.`
          : ''}
      </Paragraph>
      {failed && <InlineNotification tone="warning" title="Could not read the trusted devices" message="Reload the page to try again." />}
      {devices !== null && devices.length === 0 && (
        <Text size="small" color="text-weak">
          No device reached yet.
        </Text>
      )}
      {devices !== null && devices.length > 0 && (
        <Box
          as="ul"
          aria-label={`Devices this run trusts: ${devices.length}`}
          margin="none"
          pad="none"
          background="background-front"
          round="small"
          border={{ color: 'border-weak' }}
          flex={false}
        >
          {devices.map((d, i) => (
            <Box
              as="li"
              key={`${d.kind}-${d.host}-${d.port}`}
              direction="row"
              gap="small"
              align="start"
              pad={{ horizontal: 'medium', vertical: 'small' }}
              border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined}
              style={{ listStyle: 'none' }}
            >
              <Box flex={false} pad={{ top: 'xxsmall' }}>
                <StatusIcon state={d.refused_fingerprint ? 'failed' : 'complete'} />
              </Box>
              <Box flex gap="xsmall">
                <Box direction="row" gap="small" align="baseline" wrap>
                  <Text size="small" weight={500} color="text-strong">
                    {deviceName(d)} {address(d)}
                  </Text>
                  <Text size="xsmall" color="text-weak">
                    {d.how === 'retrusted' ? `Trusted again by you, ${stamp(d.trusted_at)}` : `Trusted on first contact, ${stamp(d.trusted_at)}`}
                  </Text>
                </Box>
                <Fingerprint
                  label={d.kind === 'ssh' ? 'SSH host key, SHA-256' : 'Certificate, SHA-256'}
                  value={d.fingerprint}
                  keyType={d.kind === 'ssh' ? d.key_type : null}
                />
                {d.previous_fingerprint && (
                  <Text size="xsmall" color="text-weak" style={{ overflowWrap: 'anywhere' }}>
                    Replaced {d.previous_fingerprint}
                  </Text>
                )}
                {d.refused_fingerprint && <Retrust runId={runId} device={d} onDone={() => setRefresh((n) => n + 1)} />}
              </Box>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
}
