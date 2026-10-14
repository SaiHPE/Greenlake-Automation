import { Anchor, Box, FileInput, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { API, CheckReport, checkConfig, InitSheetUploadResult, uploadInitSheet } from '../api';
import { Guidance, Panel, StatusLine } from '../ui/blocks';
import { StepState } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { StepShell } from '../ui/StepShell';
import { fromParsedWorkItem, WorkItemForm } from '../workItem';

interface Props {
  setForm: (form: WorkItemForm) => void;
  onUploaded: (token: string) => void;
  /** Held by the shell, so navigating away and back does not lose the upload. */
  result: InitSheetUploadResult | null;
  setResult: (result: InitSheetUploadResult | null) => void;
  state: StepState;
}

async function fileToBase64(file: File): Promise<string> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  let binary = '';
  for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

const TARGETS: [string, string][] = [
  ['array', 'Array'],
  ['vcenter', 'vCenter'],
  ['switch_f1', 'Switch, fabric F1'],
  ['switch_f2', 'Switch, fabric F2'],
  ['peer', 'Peer array (replication)'],
];

function Value({ children }: { children?: string | null }) {
  return children ? <Text size="small">{children}</Text> : <Text size="small" color="text-weak" a11yTitle="No value">--</Text>;
}

export function InitSheetStep({ setForm, onUploaded, result, setResult, state }: Props) {
  const { nextTitle } = useStepContext();
  const [report, setReport] = useState<CheckReport | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const item = result?.work_item;
  const targets = result?.targets ?? {};

  const upload = async (file: File) => {
    setBusy('upload');
    setError(null);
    setReport(null);
    try {
      const uploaded = await uploadInitSheet(await fileToBase64(file));
      setResult(uploaded);
      setForm(fromParsedWorkItem(uploaded.work_item));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const validate = async () => {
    setBusy('check');
    setError(null);
    try {
      setReport((await checkConfig()).report);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const reportState: StepState = !report ? 'not_started' : report.ok && report.ready ? 'complete' : report.ok ? 'action_required' : 'failed';
  const reportTitle = !report
    ? ''
    : !report.ok
      ? report.tls_trust_failure
        ? // The credentials were never sent; say so, or the operator re-checks a secret for an hour.
          'Could not verify the HPE certificate. The credentials were not checked.'
        : report.missing_credentials.length > 0
          ? 'GreenLake credentials are not configured'
          : 'GreenLake credentials were rejected'
      : report.ready
        ? 'GreenLake credentials accepted; Data Services is provisioned'
        : 'GreenLake credentials accepted, but no provisioned Data Services instance was found';
  const reportMessage = !report
    ? undefined
    : report.ok
      ? report.ready
        ? undefined
        : 'Deploy Data Services to the workspace in the region nearest the array before registering it.'
      : (report.error ?? report.missing_credentials.join(', '));

  return (
    <StepShell
      title="Initialisation sheet"
      description="One workbook per array, completed in full. Upload it to start a run."
      state={state}
      stateLabel={item ? 'Workbook read' : busy === 'upload' ? 'Reading' : 'Upload the workbook'}
      error={error}
      onDismissError={() => setError(null)}
      buttons={[
        {
          label: 'Validate GreenLake credentials',
          busy: busy === 'check',
          onClick: validate,
          blocked: item ? undefined : 'Upload the workbook first. The credentials are read from it.',
        },
      ]}
      primary={{
        label: nextTitle ? `Continue to ${nextTitle}` : 'Continue',
        onClick: () => result && onUploaded(result.token),
        blocked: item ? undefined : 'Upload the completed workbook first.',
      }}
      guidance={
        <Guidance
          items={[
            {
              title: 'The template',
              body: (
                <>
                  <Anchor href={`${API}/init-sheet/template`} download="Initialisation_sheet.xlsx" label="Download the blank template" />. Fill the
                  value column for every required field and leave the field names as they are.
                </>
              ),
            },
            { title: 'One workbook, one array', body: 'A workbook that names two arrays is refused. The mode you choose next decides which parts are used.' },
            {
              title: 'Passwords',
              body: 'The DSCC administrator password is not in the workbook: you type it in the DSCC wizard. The array, vCenter and switch passwords on the Provisioning tab, and the GreenLake API credentials, stay on this workstation and are never sent to the browser.',
            },
          ]}
        />
      }
    >
      {busy === 'upload' && <StatusLine state="running">Reading the workbook and storing the credentials.</StatusLine>}
      {item && busy !== 'upload' && (
        <StatusLine state="complete">
          Workbook read for {item.serial_number}
          {item.dscc_setup?.system_name ? ` (${item.dscc_setup.system_name})` : ''}. Nothing is sent to the array yet; the run is created on
          the next step.
        </StatusLine>
      )}
      {report && (
        <StatusLine state={reportState} title={reportTitle}>
          {reportMessage}
        </StatusLine>
      )}

      <Box flex={false}>
        <FileInput
          name="xlsx"
          accept=".xlsx"
          messages={{ dropPrompt: item ? 'Drop another workbook here to replace it' : 'Drop the completed workbook here', browse: 'browse' }}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void upload(file);
          }}
        />
      </Box>

      {item && (
        <Panel title="What the workbook holds" description="Check these against the workbook before you create the run.">
          <Box direction="row" gap="large" wrap>
            <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'small' }}>
              <NameValuePair name="Serial number">
                <Value>{item.serial_number}</Value>
              </NameValuePair>
              <NameValuePair name="Product number">
                <Value>{item.part_number}</Value>
              </NameValuePair>
              <NameValuePair name="Management IP">
                <Value>{item.network?.mgmt_ipv4}</Value>
              </NameValuePair>
              <NameValuePair name="Gateway">
                <Value>{item.network?.gateway}</Value>
              </NameValuePair>
            </NameValueList>
            <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'small' }}>
              <NameValuePair name="System name">
                <Value>{item.dscc_setup?.system_name}</Value>
              </NameValuePair>
              <NameValuePair name="Country">
                <Value>{item.dscc_setup?.country}</Value>
              </NameValuePair>
              <NameValuePair name="Regions">
                <Value>{`${item.service_catalog_region_id} · ${item.dscc_region_code}`}</Value>
              </NameValuePair>
              <NameValuePair name="NTP">
                <Value>{item.network?.ntp}</Value>
              </NameValuePair>
            </NameValueList>
            <NameValueList pairProps={{ direction: 'column' }} valueProps={{ width: 'small' }}>
              {TARGETS.map(([key, label]) => (
                <NameValuePair key={key} name={label}>
                  <Value>{targets[`${key}_host`] ? `${targets[`${key}_user`] ?? ''}@${targets[`${key}_host`]}` : null}</Value>
                </NameValuePair>
              ))}
            </NameValueList>
          </Box>
        </Panel>
      )}
    </StepShell>
  );
}
