import { Anchor, Box, Button, FileInput, Notification, Spinner, Text } from 'grommet';
import { useState } from 'react';
import { API, CheckReport, checkConfig, InitSheetUploadResult, uploadInitSheet } from '../api';
import { Instructions, Section } from '../components';
import { actionKeysFor, ActionKey, RunMode } from '../modes';
import { fromParsedWorkItem, WorkItemForm } from '../workItem';

interface Props {
  setForm: (form: WorkItemForm) => void;
  onRunCreated: (runId: string) => void;
  mode: RunMode;
  selectedSteps: ActionKey[];
}

async function fileToBase64(file: File): Promise<string> {
  const bytes = new Uint8Array(await file.arrayBuffer());
  let binary = '';
  for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

export function InitSheetStep({ setForm, onRunCreated, mode, selectedSteps }: Props) {
  const [result, setResult] = useState<InitSheetUploadResult | null>(null);
  const [report, setReport] = useState<CheckReport | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onUpload = async (file: File) => {
    setBusy('upload');
    setError(null);
    setReport(null);
    try {
      const res = await uploadInitSheet(await fileToBase64(file), mode, selectedSteps);
      setResult(res);
      setForm(fromParsedWorkItem(res.work_item));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const test = async () => {
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

  const item = result?.work_item;
  const wantsGreenlake = actionKeysFor(mode, selectedSteps).includes('greenlake');

  return (
    <Box gap="medium">
      <Section title="1 · Download & fill the Initialisation sheet">
        <Instructions
          items={[
            <>
              <Anchor href={`${API}/init-sheet/template`} label="Download Initialisation_sheet.xlsx" download="Initialisation_sheet.xlsx" />
              {' '}— or use the copy the customer already filled.
            </>,
            <>Fill the <b>Value</b> column for every required field (marked <b>*</b>): GreenLake API credentials, serial, subscription key, network, and DSCC details (the admin <b>password</b> is entered later in the DSCC wizard, not here).</>,
            <>One workbook = one array. Don't rename the <b>Field</b> column.</>,
          ]}
        />
        <Text size="small" color="text-weak">
          On upload, the GreenLake API credentials in the sheet are saved to this machine&apos;s local
          .env. The array admin password is <b>not</b> in the sheet — you enter it in the DSCC wizard.
        </Text>
      </Section>

      <Section title="2 · Upload the filled sheet">
        <FileInput
          name="xlsx"
          accept=".xlsx"
          messages={{ dropPrompt: 'Drop the filled Initialisation_sheet.xlsx here', browse: 'browse' }}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void onUpload(file);
          }}
        />
        {busy === 'upload' && (
          <Box direction="row" gap="small" align="center">
            <Spinner />
            <Text size="small">Parsing the sheet and saving credentials…</Text>
          </Box>
        )}
      </Section>

      {error && <Notification status="critical" title="Could not read the sheet" message={error} onClose={() => setError(null)} />}

      {item && (
        <Section title="3 · Review & continue">
          <Notification status="normal" title={`Loaded ${item.serial_number} — GreenLake credentials saved to .env`} />
          <Box gap="xxsmall" pad={{ vertical: 'small' }}>
            <Text size="small"><b>Serial:</b> {item.serial_number} &nbsp; <b>SKU:</b> {item.part_number} &nbsp; <b>Region:</b> {item.service_catalog_region_id} / {item.dscc_region_code}</Text>
            <Text size="small"><b>Mgmt IP:</b> {item.network?.mgmt_ipv4} &nbsp; <b>Gateway:</b> {item.network?.gateway} &nbsp; <b>NTP:</b> {item.network?.ntp}</Text>
            <Text size="small"><b>DSCC system:</b> {item.dscc_setup?.system_name} ({item.dscc_setup?.country}) &nbsp; <b>Admin:</b> {item.dscc_setup?.username}</Text>
          </Box>
          <Box direction="row" gap="small" align="center">
            <Button primary label="Continue →" onClick={() => onRunCreated(result!.run.run_id)} />
            {wantsGreenlake && (
              <Button label={busy === 'check' ? 'Testing…' : 'Test GreenLake connection'} disabled={busy !== null} onClick={test} />
            )}
            {busy === 'check' && <Spinner />}
          </Box>
          {report && (
            <Notification
              status={report.ok && report.ready ? 'normal' : report.ok ? 'warning' : 'critical'}
              title={
                !report.ok
                  ? 'Connection failed'
                  : report.ready
                    ? 'Connected — Data Services is provisioned'
                    : 'Connected, but no PROVISIONED Data Services found'
              }
              message={report.ok ? (report.ready ? '' : 'Deploy Data Services to the workspace in the region nearest the array.') : (report.error ?? report.missing_credentials.join(', '))}
            />
          )}
        </Section>
      )}
    </Box>
  );
}
