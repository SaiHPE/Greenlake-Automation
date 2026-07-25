import { Box, Button, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, launchBrowser, markComplete, startDscc } from '../api';
import { ClockSync } from '../ClockSync';
import { InlineNotification, Surface } from '../ui/primitives';
import { StatusIndicator } from '../ui/status';
import { StepShell } from '../ui/StepShell';

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

  const consoleUrl = `https://console-${dsccRegion || 'jp1'}.data.cloud.hpe.com`;
  const mine = events.filter((event) => event.phase === 'DSCC_SETUP_SYSTEM' || event.phase === 'COMPLETE');
  const running = run?.status === 'running' && run?.current_phase === 'DSCC_SETUP_SYSTEM';
  const credentialsReady = mine.some((event) => event.event_type === 'operator.credentials_ready');
  const completed = run?.status === 'succeeded';

  const call = async (key: string, action: () => Promise<unknown>) => {
    setBusy(key);
    setError(null);
    try {
      await action();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  return (
    <StepShell
      title="DSCC setup"
      description="Drives the Data Services Cloud Console Set Up System wizard as far as the credential step."
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Launch the browser and run the automation."
      footerNote="Mark complete only after DSCC reports the system as added."
      gate={
        credentialsReady && !completed
          ? {
              title: 'Enter the array credential in the browser, then complete the wizard',
              message:
                'All fields through the Credentials step are populated. Select or create the system credential with the array admin account, continue through Review, submit, then mark this step complete.',
            }
          : null
      }
      actions={
        <>
          <Button
            busy={busy === 'dscc' || running}
            label={running ? 'Filling' : 'Run DSCC automation'}
            disabled={!cdpUrl || completed}
            onClick={() => call('dscc', () => startDscc(runId, cdpUrl ?? 'http://localhost:9222'))}
          />
          <Button
            primary
            busy={busy === 'complete'}
            label={completed ? 'Continue' : 'Mark DSCC complete'}
            disabled={!credentialsReady && !completed}
            onClick={() => (completed ? onDone() : call('complete', () => markComplete(runId).then(onDone)))}
          />
        </>
      }
    >
      {/* DSCC sign-in fails on a skewed workstation clock, so it is re-checked here. */}
      <ClockSync consoleUrl={consoleUrl} title="Workstation clock" />

      <Surface
        title="Browser"
        description="DSCC requires an authenticated session, so the tool attaches to a browser under your control."
        actions={
          <Button
            busy={busy === 'browser'}
            label="Launch the DSCC browser"
            onClick={() =>
              call('browser', async () => {
                const info = await launchBrowser(consoleUrl);
                setCdpUrl(info.cdp_url);
              })
            }
          />
        }
      >
        <Box gap="xsmall" flex={false}>
          <Text size="small" color="text-weak">
            1. Sign in with your HPE GreenLake account. The automation never handles your sign-in.
          </Text>
          <Text size="small" color="text-weak">
            2. Open the Setup service, locate {run?.serial_number ?? 'the array'}, and select Set Up System.
          </Text>
          <Text size="small" color="text-weak">
            3. Leave the wizard on its Welcome screen and return here.
          </Text>
          {cdpUrl && (
            <Box pad={{ top: 'xsmall' }} flex={false}>
              <StatusIndicator state="complete" label={`Attached · ${cdpUrl}`} />
            </Box>
          )}
        </Box>
      </Surface>

      <Surface title="Populated fields" description="Everything the automation fills before it hands back to you.">
        <Text size="small" color="text-weak">
          Welcome, network domain, time, attributes (proxy and support contact), then the system name and country. It
          stops at System Credentials.
        </Text>
        <InlineNotification
          tone="info"
          title="Credential handling"
          message="The array password is entered by the operator only; this tool never submits credentials to a cloud console."
        />
      </Surface>

      {completed && (
        <InlineNotification
          tone="ok"
          title="DSCC setup is complete"
          message="The array is registered with Data Services Cloud Console."
        />
      )}
    </StepShell>
  );
}
