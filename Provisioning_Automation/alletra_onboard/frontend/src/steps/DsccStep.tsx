import { Box, Button, Notification, Spinner, Text } from 'grommet';
import { useEffect, useState } from 'react';
import { ClockStatus, RunEvent, RunRecord, getClock, launchBrowser, markComplete, startDscc, syncClock } from '../api';
import { EventLog, Instructions, Section, StatusTag } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  dsccRegion: string;
  onDone: () => void;
}

export function DsccStep({ runId, run, events, dsccRegion, onDone }: Props) {
  const [cdpUrl, setCdpUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [clock, setClock] = useState<ClockStatus | null>(null);
  const [clockMsg, setClockMsg] = useState<string | null>(null);

  const consoleUrl = `https://console-${dsccRegion || 'jp1'}.data.cloud.hpe.com`;

  useEffect(() => {
    getClock(consoleUrl).then(setClock).catch(() => undefined);
  }, [consoleUrl]);

  const fixClock = async () => {
    setBusy('clock');
    setError(null);
    setClockMsg(null);
    try {
      const r = await syncClock(consoleUrl);
      setClockMsg(r.changed ? `Clock corrected (was off by ${Math.round(r.skew_seconds_before)}s).` : 'Clock already in sync.');
      setClock(await getClock(consoleUrl));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };
  const stepEvents = events.filter((e) => e.phase === 'DSCC_SETUP_SYSTEM' || e.phase === 'COMPLETE');
  const running = run?.status === 'running' && run?.current_phase === 'DSCC_SETUP_SYSTEM';
  const credentialsReady = stepEvents.some((e) => e.event_type === 'operator.credentials_ready');
  const failed = run?.current_phase === 'DSCC_SETUP_SYSTEM' && run?.status === 'retryable_failure';
  const completed = run?.status === 'succeeded';

  const openBrowser = async () => {
    setBusy('browser');
    setError(null);
    try {
      const info = await launchBrowser(consoleUrl);
      setCdpUrl(info.cdp_url);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const runAutomation = async () => {
    setBusy('dscc');
    setError(null);
    try {
      await startDscc(runId, cdpUrl ?? 'http://localhost:9222');
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const finish = async () => {
    setBusy('complete');
    setError(null);
    try {
      await markComplete(runId);
      onDone();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const skewOff = clock?.skew_seconds != null && !clock.in_sync;

  return (
    <Box gap="medium">
      {/* Always shown — a skewed clock fails DSCC sign-in, so the sync control must be findable
          even when the clock currently looks fine. */}
      <Section title="System clock (required for DSCC sign-in)">
        {clock === null ? (
          <Text size="small" color="text-weak">Checking the clock…</Text>
        ) : skewOff ? (
          <Notification
            status="warning"
            title={`Clock is off by ~${Math.abs(Math.round(clock.skew_seconds as number))}s — DSCC sign-in will fail`}
            message='DSCC rejects a skewed clock ("iat is in the future"). Sync it before opening the DSCC browser.'
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
          <Button
            primary={skewOff}
            label={busy === 'clock' ? 'Syncing…' : 'Sync system clock'}
            disabled={busy !== null}
            onClick={fixClock}
          />
          <Text size="small" color="text-weak">Uses an HTTPS time source — works where NTP is blocked.</Text>
        </Box>
        {clock && !clock.is_admin && (
          <Text size="small" color="text-weak">Run the app as Administrator for the sync to set the clock.</Text>
        )}
        {clockMsg && (
          <Text size="small" color="status-ok">
            {clockMsg}
          </Text>
        )}
      </Section>

      <Section title="1 · Open DSCC and start the Set Up System wizard">
        <Instructions
          items={[
            <>Click <b>Open DSCC browser</b> — a Chrome window opens at {consoleUrl}.</>,
            <>Sign in with your HPE GreenLake account (SSO). The automation never touches your login.</>,
            <>Open the <b>Setup</b> service, find <b>{run?.serial_number ?? 'your array'}</b>, and click <b>Set Up System</b>.</>,
            <>Stay on the wizard&apos;s <b>Welcome</b> screen, then come back here.</>,
          ]}
        />
        <Box direction="row" gap="small" align="center">
          <Button primary label={busy === 'browser' ? 'Launching…' : 'Open DSCC browser'} disabled={busy !== null} onClick={openBrowser} />
          {cdpUrl && (
            <Text size="small" color="status-ok">
              Browser launched (attach: {cdpUrl})
            </Text>
          )}
        </Box>
      </Section>

      <Section title="2 · Run the automation">
        <Text size="small">
          Fills Welcome → Network Domain → Time → Attributes (Proxy, Support Contact) → System name &amp; country,
          then stops at <b>System Credentials</b> for you.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button
            primary
            label={running || busy === 'dscc' ? 'Filling…' : 'Run DSCC automation'}
            disabled={busy !== null || running || !cdpUrl}
            onClick={runAutomation}
          />
          {running && <Spinner />}
          <StatusTag status={run?.current_phase === 'DSCC_SETUP_SYSTEM' ? run?.status : undefined} />
        </Box>
        {!cdpUrl && (
          <Text size="small" color="text-weak">
            Open the DSCC browser first (step 1).
          </Text>
        )}
      </Section>

      {error && <Notification status="critical" title="Request failed" message={error} onClose={() => setError(null)} />}

      {credentialsReady && !completed && (
        <Notification
          status="warning"
          title="Action needed: finish in the DSCC browser"
          message="In the wizard: select or Create New under System Credentials (your array admin username/password), click Continue, review everything, and click Submit. Then mark the run complete below."
        />
      )}
      {failed && (
        <Notification
          status="critical"
          title="Could not drive the DSCC wizard"
          message="Make sure the debug Chrome is open on the Set Up System wizard (Welcome screen), then run the automation again."
        />
      )}

      <Section title="Progress">
        <EventLog events={stepEvents} emptyText="Run the automation to see progress here." />
      </Section>

      <Button
        primary
        label={busy === 'complete' ? 'Saving…' : 'I submitted in DSCC — mark complete'}
        disabled={!credentialsReady || completed || busy !== null}
        onClick={finish}
        alignSelf="start"
      />
    </Box>
  );
}
