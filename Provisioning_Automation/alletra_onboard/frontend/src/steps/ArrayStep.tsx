import { Anchor, Box, Button, FileInput, Grid, Notification, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { API, createRun, parseCsv } from '../api';
import { Instructions, Section } from '../components';
import { fromParsedWorkItem, toWorkItemPayload, WorkItemForm } from '../workItem';

interface Props {
  form: WorkItemForm;
  setForm: (form: WorkItemForm) => void;
  onRunCreated: (runId: string) => void;
}

function Field({
  label,
  value,
  onChange,
  hint,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  hint?: string;
  placeholder?: string;
}) {
  return (
    <Box gap="xxsmall">
      <Text size="small">{label}</Text>
      <TextInput size="small" value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
      {hint && (
        <Text size="xsmall" color="text-weak">
          {hint}
        </Text>
      )}
    </Box>
  );
}

export function ArrayStep({ form, setForm, onRunCreated }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const set = (key: keyof WorkItemForm) => (value: string) => setForm({ ...form, [key]: value });

  const onUpload = async (file: File) => {
    setError(null);
    try {
      const text = await file.text();
      const { work_items } = await parseCsv(text);
      if (!work_items.length) throw new Error('The CSV has no data rows.');
      setForm(fromParsedWorkItem(work_items[0]));
      setNotice(`Loaded ${work_items[0].serial_number} from the CSV — review and edit below.`);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const { run } = await createRun(toWorkItemPayload(form));
      onRunCreated(run.run_id);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box gap="medium">
      <Section title="Fill the array details">
        <Instructions
          items={[
            <>
              <Anchor href={`${API}/work-items/template`} label="Download the CSV template" download="arrays.csv" />, fill it
              with this array&apos;s values, and upload it back — or type directly into the form below.
            </>,
            <>Every field stays editable after upload, so you can fix anything before creating the run.</>,
          ]}
        />
        <FileInput
          name="csv"
          accept=".csv"
          messages={{ dropPrompt: 'Drop the filled arrays.csv here', browse: 'browse' }}
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void onUpload(file);
          }}
        />
      </Section>

      {notice && <Notification status="normal" title={notice} onClose={() => setNotice(null)} />}
      {error && <Notification status="critical" title="Problem with the work item" message={error} onClose={() => setError(null)} />}

      <Section title="Identity & subscription">
        <Grid columns={{ count: 3, size: 'auto' }} gap="small">
          <Field label="Serial number" value={form.serial_number} onChange={set('serial_number')} placeholder="SGHDxxxxxxxx" />
          <Field
            label="Part number (product SKU)"
            value={form.part_number}
            onChange={set('part_number')}
            hint="Use the product SKU (e.g. S0B84A) — NOT the box FRU number (R7C75-…), which GreenLake rejects."
          />
          <Field
            label="Subscription key"
            value={form.subscription_key}
            onChange={set('subscription_key')}
            hint="From the activation email's attachment — a GreenLake key, not the EON or AutoPass keys."
          />
          <Field label="GreenLake region" value={form.service_catalog_region_id} onChange={set('service_catalog_region_id')} />
          <Field label="DSCC region code" value={form.dscc_region_code} onChange={set('dscc_region_code')} />
        </Grid>
      </Section>

      <Section title="Management network (applied by the Cloud Connectivity Wizard)">
        <Grid columns={{ count: 3, size: 'auto' }} gap="small">
          <Field label="Management IPv4" value={form.mgmt_ipv4} onChange={set('mgmt_ipv4')} />
          <Field label="Netmask" value={form.mask} onChange={set('mask')} />
          <Field label="Gateway" value={form.gateway} onChange={set('gateway')} />
          <Field label="DNS servers" value={form.dns} onChange={set('dns')} hint="Separate multiple with ; (semicolon)" />
          <Field label="NTP server" value={form.ntp} onChange={set('ntp')} />
          <Field label="Timezone" value={form.timezone} onChange={set('timezone')} placeholder="Asia/Kolkata" />
          <Field label="Proxy host (optional)" value={form.proxy_host} onChange={set('proxy_host')} />
          <Field label="Proxy port" value={form.proxy_port} onChange={set('proxy_port')} />
        </Grid>
      </Section>

      <Section title="DSCC setup">
        <Grid columns={{ count: 3, size: 'auto' }} gap="small">
          <Field label="System name" value={form.dscc_system_name} onChange={set('dscc_system_name')} />
          <Field label="System country" value={form.dscc_country} onChange={set('dscc_country')} />
          <Field label="Support contact first name" value={form.contact_first_name} onChange={set('contact_first_name')} />
          <Field label="Support contact last name" value={form.contact_last_name} onChange={set('contact_last_name')} />
          <Field label="Preferred language" value={form.contact_language} onChange={set('contact_language')} />
          <Field label="Company (optional)" value={form.contact_company} onChange={set('contact_company')} />
          <Field label="Phone (optional)" value={form.contact_phone} onChange={set('contact_phone')} />
          <Field label="Email (optional)" value={form.contact_email} onChange={set('contact_email')} />
          <Field
            label="Credential (secret) name"
            value={form.secret_name}
            onChange={set('secret_name')}
            hint="You will create/select this secret yourself in the DSCC wizard — the password is never stored here."
          />
        </Grid>
      </Section>

      <Box direction="row" gap="small">
        <Button
          primary
          disabled={busy || !form.serial_number.trim() || !form.subscription_key.trim()}
          label={busy ? 'Creating run…' : 'Create run → GreenLake'}
          onClick={submit}
        />
        {!form.serial_number.trim() && (
          <Text size="small" color="text-weak" alignSelf="center">
            Serial number and subscription key are required.
          </Text>
        )}
      </Box>
    </Box>
  );
}
