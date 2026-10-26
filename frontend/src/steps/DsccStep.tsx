import { Box, Button, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, launchBrowser, markComplete, startDscc } from '../api';
import { ClockSync } from '../ClockSync';
import { Instructions } from '../components';
import { Guidance, Panel, StatusLine } from '../ui/blocks';
import { StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  dsccRegion: string;
  onDone: () => void;
}

export function DsccStep({ runId, run, events, dsccRegion, onDone }: Props) {
  const { nextTitle } = useStepContext();
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

  const runAutomation: FooterAction = {
    label: running ? 'Filling' : 'Run DSCC automation',
    busy: busy === 'dscc' || running,
    onClick: () => call('dscc', () => startDscc(runId, cdpUrl ?? 'http://localhost:9222')),
    blocked: cdpUrl ? undefined : 'Launch the DSCC browser first, sign in, and leave the Set Up System wizard on its Welcome screen.',
  };

  return (
    <StepShell
      title="DSCC setup"
      description="Fills the Data Services Cloud Console Set Up System wizard as far as the credential step. You finish it."
      error={error}
      onDismissError={() => setError(null)}
      gate={
        credentialsReady && !completed
          ? {
              title: 'Enter the array credential in the browser, then finish the wizard',
              message:
                'Every field up to System Credentials is filled. Select or create the system credential with the array admin account, continue through Review, submit, then mark this step complete.',
            }
          : null
      }
      buttons={completed ? [] : [runAutomation]}
      // Never gated on our own automation having run: the operator may have completed the Set Up
      // System wizard by hand, and only they can confirm DSCC accepted the system.
      primary={
        completed
          ? { label: `Continue to ${nextTitle ?? 'the next step'}`, onClick: onDone }
          : { label: 'Mark DSCC complete', busy: busy === 'complete', onClick: () => call('complete', () => markComplete(runId).then(onDone)) }
      }
      guidance={
        <Guidance
          items={[
            { title: 'What the automation fills', body: 'Welcome, network domain, time, attributes (proxy and support contact), then the system name and country. It stops at System Credentials.' },
            { title: 'Your sign-in and the password', body: 'The automation never handles your sign-in, and never submits the array password to a cloud console. You type it.' },
            { title: 'When to mark it complete', body: 'Only after DSCC reports the system as added. You can also do the whole wizard by hand and mark it complete.' },
          ]}
        />
      }
    >
      {completed && (
        <StatusLine state="complete" title="DSCC setup is complete">
          The array is registered with Data Services Cloud Console.
        </StatusLine>
      )}
      {running && <StatusLine state="running">Filling in the Set Up System wizard. Each screen appears in Activity, below.</StatusLine>}

      {/* DSCC sign-in fails on a skewed workstation clock, so it is checked again here. */}
      <ClockSync consoleUrl={consoleUrl} title="Workstation clock" />

      <Panel
        title="Browser"
        description="DSCC needs a signed-in session, so the tool attaches to a browser you control."
        right={
          <Button
            size="small"
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
        <Instructions
          items={[
            <>Sign in with your HPE GreenLake account.</>,
            <>Open the Setup service, find {run?.serial_number ?? 'the array'}, and select Set Up System.</>,
            <>Leave the wizard on its Welcome screen and come back here.</>,
          ]}
        />
        {cdpUrl && (
          <Box flex={false}>
            <StatusIndicator state="complete" label={`Attached · ${cdpUrl}`} />
          </Box>
        )}
        {!cdpUrl && (
          <Text size="small" color="text-weak">
            Not attached yet.
          </Text>
        )}
      </Panel>
    </StepShell>
  );
}
