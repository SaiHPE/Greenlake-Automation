import { Box, Button, Notification, Spinner, Text } from 'grommet';
import { useEffect, useState } from 'react';
import { ClockStatus, getClock, syncClock } from './api';
import { Section } from './components';

interface Props {
  // When set, the skew is measured against this host's HTTPS Date header (the DSCC console);
  // omit on the prerequisites step to use the default public time sources.
  consoleUrl?: string;
  title?: string;
  note?: string;
}

// Shared "System clock" check + sync. A drifted clock (>2 min) blocks the array from connecting
// to DSCC, so the operator can correct it both up front (prerequisites) and at the DSCC step.
export function ClockSync({ consoleUrl, title = 'System clock', note }: Props) {
  const [clock, setClock] = useState<ClockStatus | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getClock(consoleUrl).then(setClock).catch(() => undefined);
  }, [consoleUrl]);

  const skewOff = clock?.skew_seconds != null && !clock.in_sync;

  const sync = async () => {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const result = await syncClock(consoleUrl);
      setMessage(
        result.changed
          ? `Clock corrected (was off by ${Math.round(result.skew_seconds_before)}s).`
          : 'Clock already in sync.',
      );
      setClock(await getClock(consoleUrl));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Section title={title}>
      {clock === null ? (
        <Box direction="row" gap="small" align="center">
          <Spinner size="small" />
          <Text size="small" color="text-weak">Checking the clock…</Text>
        </Box>
      ) : skewOff ? (
        <Notification
          status="warning"
          title={`Clock is off by ~${Math.abs(Math.round(clock.skew_seconds as number))}s`}
          message='A skewed clock stops the array connecting to DSCC ("iat is in the future"). Sync it now.'
        />
      ) : clock.skew_seconds == null ? (
        <Text size="small" color="text-weak">
          Couldn&apos;t reach a time source to check ({clock.error ?? 'unknown'}). You can still sync below.
        </Text>
      ) : (
        <Text size="small" color="status-ok">
          ✓ Clock is in sync (±{Math.abs(Math.round(clock.skew_seconds))}s vs {clock.source}).
        </Text>
      )}
      <Box direction="row" gap="small" align="center">
        <Button primary={skewOff} label={busy ? 'Syncing…' : 'Sync system clock'} disabled={busy} onClick={sync} />
        <Text size="small" color="text-weak">{note ?? 'Uses an HTTPS time source — works where NTP is blocked.'}</Text>
      </Box>
      {clock && !clock.is_admin && (
        <Text size="small" color="text-weak">Run the app as Administrator for the sync to set the clock.</Text>
      )}
      {message && <Text size="small" color="status-ok">{message}</Text>}
      {error && <Notification status="critical" title="Sync failed" message={error} onClose={() => setError(null)} />}
    </Section>
  );
}
