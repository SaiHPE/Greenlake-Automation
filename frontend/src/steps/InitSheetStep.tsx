import { Anchor, Box, Button, FileInput, NameValueList, NameValuePair, Text } from 'grommet';
import { useState } from 'react';
import { API, CheckReport, checkConfig, InitSheetUploadResult, uploadInitSheet } from '../api';
import { InlineNotification, Surface } from '../ui/primitives';
import { StepState } from '../ui/status';
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

export function InitSheetStep({ setForm, onUploaded, result, setResult, state }: Props) {
  const [report, setReport] = useState<CheckReport | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const item = result?.work_item;

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

  return (
    <StepShell
      title="Initialisation sheet"
      description="One workbook per array, completed in full. The selected mode determines which sections are applied."
      state={state}
      error={error}
      onDismissError={() => setError(null)}
      footerNote="The run is created on the next step."
      actions={
        <>
          <Button busy={busy === 'check'} label="Validate GreenLake credentials" disabled={!item} onClick={validate} />
          <Button primary label="Continue" disabled={!item} onClick={() => onUploaded(result!.token)} />
        </>
      }
    >
      <Surface
        title="Complete the workbook"
        description="One workbook is one array. Complete the value column for every required field and leave the field names unchanged."
        actions={
          <Anchor
            href={`${API}/init-sheet/template`}
            download="Initialisation_sheet.xlsx"
            label="Download blank template"
          />
        }
      >
        <Text size="small" color="text-weak">
          The array administrator password is deliberately absent from the workbook — it is entered directly in the
          DSCC wizard. On upload, the GreenLake API credentials it contains are stored in this workstation's local
          configuration.
        </Text>
      </Surface>

      <Surface title="Upload the completed workbook">
        <FileInput
          name="xlsx"
          accept=".xlsx"
          messages={{ dropPrompt: 'Drop the completed workbook here', browse: 'browse' }}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void upload(file);
          }}
        />
        {busy === 'upload' && (
          <Text size="small" color="text-weak">
            Reading the workbook and storing credentials.
          </Text>
        )}
        {item && (
          <InlineNotification
            tone="ok"
            title="Workbook validated"
            message="Device credentials remain on this workstation and are never transmitted to the browser."
          />
        )}
      </Surface>

      {item && (
        <Surface title="Review parsed values" description="Verify these against the workbook before creating the run.">
          <Box direction="row" gap="large" wrap>
            <NameValueList pairProps={{ direction: 'column' }}>
              <NameValuePair name="Serial number">
                <Text>{item.serial_number}</Text>
              </NameValuePair>
              <NameValuePair name="Product number">
                <Text>{item.part_number}</Text>
              </NameValuePair>
              <NameValuePair name="Management IP">
                <Text>{item.network?.mgmt_ipv4}</Text>
              </NameValuePair>
              <NameValuePair name="Gateway">
                <Text>{item.network?.gateway}</Text>
              </NameValuePair>
            </NameValueList>
            <NameValueList pairProps={{ direction: 'column' }}>
              <NameValuePair name="System name">
                <Text>{item.dscc_setup?.system_name}</Text>
              </NameValuePair>
              <NameValuePair name="Country">
                <Text>{item.dscc_setup?.country}</Text>
              </NameValuePair>
              <NameValuePair name="Regions">
                <Text>{`${item.service_catalog_region_id} · ${item.dscc_region_code}`}</Text>
              </NameValuePair>
              <NameValuePair name="NTP">
                <Text>{item.network?.ntp}</Text>
              </NameValuePair>
            </NameValueList>
          </Box>
        </Surface>
      )}

      {report && (
        <InlineNotification
          tone={report.ok && report.ready ? 'ok' : report.ok ? 'warning' : 'critical'}
          title={
            !report.ok
              ? 'GreenLake credentials were rejected'
              : report.ready
                ? 'GreenLake credentials accepted; Data Services is provisioned'
                : 'GreenLake credentials accepted, but no provisioned Data Services instance was found'
          }
          message={
            report.ok
              ? report.ready
                ? undefined
                : 'Deploy Data Services to the workspace in the region nearest the array before registering it.'
              : (report.error ?? report.missing_credentials.join(', '))
          }
        />
      )}
    </StepShell>
  );
}
