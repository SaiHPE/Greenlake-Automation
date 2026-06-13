import { Box, Heading, Text } from 'grommet';
import { Checkmark } from 'grommet-icons';
import { useState } from 'react';
import { useRunEvents } from './useRunEvents';
import { EMPTY_FORM, WorkItemForm } from './workItem';
import { ArrayStep } from './steps/ArrayStep';
import { CloudinitStep } from './steps/CloudinitStep';
import { ConfigureStep } from './steps/ConfigureStep';
import { DoneStep } from './steps/DoneStep';
import { DsccStep } from './steps/DsccStep';
import { GreenLakeStep } from './steps/GreenLakeStep';

const STEPS = [
  { title: 'Configure GreenLake', subtitle: 'API client credentials' },
  { title: 'Array details', subtitle: 'CSV template or form' },
  { title: 'GreenLake registration', subtitle: 'register · assign · subscribe' },
  { title: 'Cloud Connectivity', subtitle: 'on-array wizard' },
  { title: 'DSCC Setup', subtitle: 'Set Up System wizard' },
  { title: 'Finish', subtitle: 'summary' },
];

export default function App() {
  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [form, setForm] = useState<WorkItemForm>(EMPTY_FORM);
  const [runId, setRunId] = useState<string | null>(null);
  const { run, events } = useRunEvents(runId);

  const advance = (to: number) => {
    setStep(to);
    setMaxStep((previous) => Math.max(previous, to));
  };

  const restart = () => {
    setRunId(null);
    setForm(EMPTY_FORM);
    setStep(1);
    setMaxStep(1);
  };

  return (
    <Box fill direction="row" background="background-back">
      <Box width="320px" background="background-front" border={{ side: 'right' }} pad="medium" gap="medium" flex={false}>
        <Box gap="xxsmall">
          <Box direction="row" gap="small" align="center">
            <Box background="brand" width="14px" height="14px" round="xsmall" />
            <Text weight="bold">HPE GreenLake</Text>
          </Box>
          <Heading level={4} margin="none">
            Alletra MP B10000 Onboarding
          </Heading>
          <Text size="small" color="text-weak">
            {run ? `${run.serial_number} · ${run.status.replaceAll('_', ' ')}` : 'No active run'}
          </Text>
        </Box>
        <Box gap="xsmall">
          {STEPS.map((item, index) => {
            const isCurrent = index === step;
            const isDone = index < step || (index === 5 && run?.status === 'succeeded');
            const reachable = index <= maxStep;
            return (
              <Box
                key={item.title}
                direction="row"
                gap="small"
                align="center"
                pad={{ vertical: 'xsmall', horizontal: 'small' }}
                round="xsmall"
                background={isCurrent ? 'background-contrast' : undefined}
                onClick={reachable ? () => setStep(index) : undefined}
                style={{ cursor: reachable ? 'pointer' : 'default', opacity: reachable ? 1 : 0.5 }}
              >
                <Box
                  width="26px"
                  height="26px"
                  round="full"
                  align="center"
                  justify="center"
                  background={isDone ? 'brand' : isCurrent ? 'background-contrast' : 'background-back'}
                  border={isDone ? undefined : { color: isCurrent ? 'brand' : 'border' }}
                  flex={false}
                >
                  {isDone ? <Checkmark size="small" color="white" /> : <Text size="small">{index + 1}</Text>}
                </Box>
                <Box>
                  <Text size="small" weight={isCurrent ? 'bold' : undefined}>
                    {item.title}
                  </Text>
                  <Text size="xsmall" color="text-weak">
                    {item.subtitle}
                  </Text>
                </Box>
              </Box>
            );
          })}
        </Box>
        <Box flex />
        <Text size="xsmall" color="text-weak">
          Provisioning automation · localhost only
        </Text>
      </Box>

      <Box flex overflow="auto">
        {/* flex={false}: keep natural height inside the scroll container — otherwise flexbox
            shrinks every section to fit the viewport and their contents overlap. */}
        <Box pad="large" gap="medium" width={{ max: '1100px' }} flex={false}>
          <Heading level={2} margin="none">
            {STEPS[step].title}
          </Heading>
          {step === 0 && <ConfigureStep onDone={() => advance(1)} />}
          {step === 1 && (
            <ArrayStep
              form={form}
              setForm={setForm}
              onRunCreated={(id) => {
                setRunId(id);
                advance(2);
              }}
            />
          )}
          {step === 2 && runId && <GreenLakeStep runId={runId} run={run} events={events} onDone={() => advance(3)} />}
          {step === 3 && runId && (
            <CloudinitStep runId={runId} run={run} events={events} defaultUrl={form.cloudinit_url} onDone={() => advance(4)} />
          )}
          {step === 4 && runId && (
            <DsccStep runId={runId} run={run} events={events} dsccRegion={form.dscc_region_code} onDone={() => advance(5)} />
          )}
          {step === 5 && <DoneStep run={run} events={events} onRestart={restart} />}
          {step >= 2 && !runId && (
            <Text color="text-weak">Create a run on the Array details step first.</Text>
          )}
        </Box>
      </Box>
    </Box>
  );
}
