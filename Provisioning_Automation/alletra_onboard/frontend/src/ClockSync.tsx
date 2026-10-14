import { Box, Button, Text } from 'grommet';
import { useEffect, useState } from 'react';
import { ClockStatus, getClock, syncClock } from './api';
import { Panel, StatusLine } from './ui/blocks';
import { StatusIndicator } from './ui/status';

interface Props {
  // When set, the skew is measured against this host's HTTPS Date header (the DSCC console);
  // omit on the prerequisites step to use the default public time sources.
  consoleUrl?: string;
  title?: string;
  note?: string;
}

// Shared "System clock" check + sync. A drifted clock (>2 min) blocks the array from connecting
// to DSCC, so the operator can correct it both up front (prerequisites) and at the DSCC step.
export function useClock(consoleUrl?: string) {
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

  return { clock, message, busy, error, setError, skewOff, sync };
}

export function ClockSync({ consoleUrl, title = 'System clock', note }: Props) {
  const { clock, message, busy, error, setError, skewOff, sync } = useClock(consoleUrl);
  const skew = Math.abs(Math.round(clock?.skew_seconds ?? 0));

  return (
    <Panel
      title={title}
      right={
        <StatusIndicator
          state={clock === null ? 'running' : skewOff ? 'action_required' : clock.skew_seconds == null ? 'not_started' : 'complete'}
          label={clock === null ? 'Checking' : skewOff ? `Off by about ${skew} s` : clock.skew_seconds == null ? 'Not checked' : `In sync (±${skew} s)`}
        />
      }
    >
      {skewOff ? (
        <StatusLine state="action_required" title={`The clock is off by about ${skew} seconds`}>
          A clock that is off stops the array connecting to DSCC (&quot;iat is in the future&quot;). Sync it now.
        </StatusLine>
      ) : clock && clock.skew_seconds == null ? (
        <Text size="small" color="text-weak">
          Could not reach a time source to check ({clock.error ?? 'unknown'}). You can still sync.
        </Text>
      ) : clock ? (
        <Text size="small" color="text-weak">
          Compared with {clock.source}.
        </Text>
      ) : null}
      <Box direction="row" gap="small" align="center" wrap>
        <Button size="small" primary={skewOff} busy={busy} label="Sync system clock" onClick={sync} />
        <Text size="small" color="text-weak">
          {note ?? 'Uses an HTTPS time source, which works where NTP is blocked.'}
        </Text>
      </Box>
      {clock && !clock.is_admin && (
        <Text size="small" color="text-weak">
          Run the app as Administrator for the sync to set the clock.
        </Text>
      )}
      {message && (
        <Text size="small" color="text-weak">
          {message}
        </Text>
      )}
      {error && (
        <StatusLine state="failed" title="Sync failed" onClose={() => setError(null)}>
          {error}
        </StatusLine>
      )}
    </Panel>
  );
}
