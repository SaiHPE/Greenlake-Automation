import { Anchor, Box, Button, Notification, Spinner, Table, TableBody, TableCell, TableHeader, TableRow, Text, TextInput } from 'grommet';
import { useEffect, useState } from 'react';
import { CheckReport, checkConfig, getConfig, saveConfig } from '../api';
import { Instructions, Section } from '../components';

export function ConfigureStep({ onDone }: { onDone: () => void }) {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [tokenUrl, setTokenUrl] = useState('');
  const [workspaceId, setWorkspaceId] = useState('');
  const [configured, setConfigured] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<CheckReport | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getConfig()
      .then(({ configured, values }) => {
        setConfigured(configured);
        setClientId(values.GL_CLIENT_ID ?? '');
        setTokenUrl(values.GL_TOKEN_URL ?? '');
        setWorkspaceId(values.GL_MEMBER_WORKSPACE_ID ?? '');
      })
      .catch((exc) => setError(String(exc.message ?? exc)));
  }, []);

  const save = async () => {
    setBusy('save');
    setError(null);
    setSaved(false);
    try {
      const result = await saveConfig({
        gl_client_id: clientId || null,
        gl_client_secret: clientSecret || null,
        gl_token_url: tokenUrl || null,
        gl_member_workspace_id: workspaceId || null,
      });
      setConfigured(result.configured);
      setClientSecret('');
      setReport(null); // creds changed — old readiness result is stale
      setSaved(true);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(null);
    }
  };

  const check = async () => {
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
    <Box gap="medium">
      <Section title="Create the GreenLake API client">
        <Instructions
          items={[
            <>Sign in to <Anchor href="https://common.cloud.hpe.com" target="_blank" label="HPE GreenLake" /> and open (or create) your workspace.</>,
            <>Make sure the <b>Data Services</b> service is provisioned in your region (Services → Catalog).</>,
            <>Go to <b>Manage Workspace → API</b> and create a personal API client.</>,
            <>Copy the <b>Client ID</b>, <b>Client Secret</b>, and the per-workspace <b>token URL</b> (…/authorization/v2/oauth2/&lt;tenant&gt;/token) below.</>,
          ]}
        />
      </Section>

      <Section title="Credentials">
        <Box gap="small" width="large">
          <Text size="small">Client ID</Text>
          <TextInput value={clientId} onChange={(e) => setClientId(e.target.value)} placeholder="xxxxxxxx-xxxx-…" />
          <Text size="small">Client Secret {configured && !clientSecret ? '(already saved — leave blank to keep)' : ''}</Text>
          <TextInput type="password" value={clientSecret} onChange={(e) => setClientSecret(e.target.value)} />
          <Text size="small">Token URL</Text>
          <TextInput value={tokenUrl} onChange={(e) => setTokenUrl(e.target.value)} placeholder="https://global.api.greenlake.hpe.com/authorization/v2/oauth2/<tenant>/token" />
          <Text size="small">Workspace ID (optional)</Text>
          <TextInput value={workspaceId} onChange={(e) => setWorkspaceId(e.target.value)} />
          <Box direction="row" gap="small" margin={{ top: 'small' }}>
            <Button primary label={busy === 'save' ? 'Saving…' : 'Save'} disabled={busy !== null} onClick={save} />
            <Button label={busy === 'check' ? 'Checking…' : 'Test connection'} disabled={busy !== null || !configured} onClick={check} />
            {busy && <Spinner />}
          </Box>
        </Box>
      </Section>

      {error && <Notification status="critical" title="Request failed" message={error} onClose={() => setError(null)} />}
      {saved && !error && (
        <Notification
          status="normal"
          title="Credentials saved"
          message={configured ? 'Click Test connection, or continue to Array details.' : 'Client ID and Secret are required to proceed.'}
          onClose={() => setSaved(false)}
        />
      )}

      {report && (
        <Section title="GreenLake readiness">
          {!report.ok ? (
            <Notification status="critical" title="Check failed" message={report.error ?? report.missing_credentials.join(', ')} />
          ) : (
            <Box gap="small">
              <Notification
                status={report.ready ? 'normal' : 'warning'}
                title={report.ready ? 'Data Services is provisioned — you are good to go' : 'No PROVISIONED Data Services found'}
                message={report.ready ? '' : 'Add Data Services to the workspace (Manage Workspace → Services) before provisioning.'}
              />
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableCell scope="col"><b>Region</b></TableCell>
                    <TableCell scope="col"><b>Status</b></TableCell>
                    <TableCell scope="col"><b>Data Services?</b></TableCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {report.provisions.map((p, i) => (
                    <TableRow key={i}>
                      <TableCell>{p.region}</TableCell>
                      <TableCell>{p.status}</TableCell>
                      <TableCell>{p.is_data_services ? 'YES' : ''}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {report.ready && <Button primary label="Continue → Array details" onClick={onDone} alignSelf="start" />}
            </Box>
          )}
        </Section>
      )}
      {configured && !report && (
        <Box direction="row" gap="small">
          <Button label="Skip check → Array details" onClick={onDone} alignSelf="start" />
        </Box>
      )}
    </Box>
  );
}
