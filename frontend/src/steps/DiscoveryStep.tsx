import { Box, Button, Notification, Spinner, Table, TableBody, TableCell, TableHeader, TableRow, Text } from 'grommet';
import { useState } from 'react';
import { DiscoveryReport, RunEvent, RunRecord, startDiscover } from '../api';
import { EventLog, Section } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

function latestReport(events: RunEvent[]): DiscoveryReport | null {
  const event = [...events].reverse().find((e) => e.event_type === 'discover.completed');
  return (event?.data?.report as DiscoveryReport) ?? null;
}

export function DiscoveryStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';
  const report = latestReport(events);
  const fcPorts = (report?.array_ports ?? []).filter((p) => p.protocol === 'fc');
  const iscsiPorts = (report?.array_ports ?? []).filter((p) => p.protocol === 'iscsi');

  const run_ = async () => {
    setError(null);
    try {
      await startDiscover(runId);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <Box gap="medium">
      <Section title="Discover the environment (read-only)">
        <Text size="small" color="text-weak">
          Reads <b>all</b> of the array&apos;s FC and iSCSI target ports, the array&apos;s own host view
          (<b>showhost</b>), and each ESXi host&apos;s FC HBA WWPNs + OS (vCenter). Each HBA is matched to
          the fabric it logs into on the array. Read-only — nothing is changed.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button primary label={running ? 'Discovering…' : report ? 'Re-run discovery' : 'Run discovery'} disabled={running} onClick={run_} />
          {running && <Spinner />}
        </Box>
        {error && <Notification status="critical" title="Discovery failed to start" message={error} onClose={() => setError(null)} />}
      </Section>

      {report && (
        <>
          <Section title={`Array FC ports (${fcPorts.length})`}>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableCell><Text size="small" weight="bold">Port (n:s:p)</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">WWPN</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">Fabric</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">State</Text></TableCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fcPorts.map((p) => (
                  <TableRow key={`${p.node}:${p.slot}:${p.card_port}`}>
                    <TableCell><Text size="small">{p.node}:{p.slot}:{p.card_port}</Text></TableCell>
                    <TableCell><Text size="small">{p.wwpn}</Text></TableCell>
                    <TableCell><Text size="small">{p.fabric ?? '—'}</Text></TableCell>
                    <TableCell><Text size="small" color={p.link_state === 'ready' ? 'status-ok' : 'status-warning'}>{p.link_state}</Text></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Section>

          {iscsiPorts.length > 0 && (
            <Section title={`Array iSCSI ports (${iscsiPorts.length})`}>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableCell><Text size="small" weight="bold">Port (n:s:p)</Text></TableCell>
                    <TableCell><Text size="small" weight="bold">IP address</Text></TableCell>
                    <TableCell><Text size="small" weight="bold">State</Text></TableCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {iscsiPorts.map((p) => (
                    <TableRow key={`${p.node}:${p.slot}:${p.card_port}`}>
                      <TableCell><Text size="small">{p.node}:{p.slot}:{p.card_port}</Text></TableCell>
                      <TableCell><Text size="small">{p.address || '—'}</Text></TableCell>
                      <TableCell><Text size="small" color={p.link_state === 'ready' ? 'status-ok' : 'status-warning'}>{p.link_state}</Text></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Section>
          )}

          {report.array_hosts.length > 0 && (
            <Section title={`Array hosts — showhost (${report.array_hosts.length})`}>
              <Text size="small" color="text-weak">
                The array&apos;s own host view. A WWPN with array ports listed is <b>logged in (zoned)</b> there;
                &ldquo;not logged in&rdquo; means configured but not connected.
              </Text>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableCell><Text size="small" weight="bold">Host</Text></TableCell>
                    <TableCell><Text size="small" weight="bold">Persona</Text></TableCell>
                    <TableCell><Text size="small" weight="bold">WWPN</Text></TableCell>
                    <TableCell><Text size="small" weight="bold">Logged-in ports</Text></TableCell>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {report.array_hosts.flatMap((h) =>
                    Object.entries(h.wwpns).map(([wwpn, ports]) => (
                      <TableRow key={h.name + wwpn}>
                        <TableCell><Text size="small">{h.name}</Text></TableCell>
                        <TableCell><Text size="small">{h.persona}</Text></TableCell>
                        <TableCell><Text size="small">{wwpn}</Text></TableCell>
                        <TableCell><Text size="small" color={ports.length ? 'status-ok' : 'status-warning'}>{ports.length ? ports.join(', ') : 'not logged in'}</Text></TableCell>
                      </TableRow>
                    )),
                  )}
                </TableBody>
              </Table>
            </Section>
          )}

          <Section title={`ESXi host HBAs (${report.host_hbas.length})`}>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableCell><Text size="small" weight="bold">Host</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">WWPN</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">Fabric</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">OS</Text></TableCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.host_hbas.map((h) => (
                  <TableRow key={h.host_name + h.wwpn}>
                    <TableCell><Text size="small">{h.host_name}</Text></TableCell>
                    <TableCell><Text size="small">{h.wwpn}</Text></TableCell>
                    <TableCell><Text size="small" color={h.fabric ? undefined : 'status-warning'}>{h.fabric ?? 'not logged in'}</Text></TableCell>
                    <TableCell><Text size="small">{h.os ?? '—'}</Text></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Section>

          {report.notes.length > 0 && (
            <Section title="Notes">
              {report.notes.map((n, i) => (
                <Text key={i} size="small" color="status-warning">• {n}</Text>
              ))}
            </Section>
          )}

          <Button primary label="Continue →" onClick={onDone} alignSelf="start" />
        </>
      )}

      <Section title="Activity"><EventLog events={events.filter((e) => e.phase === 'STORAGE_DISCOVER')} /></Section>
    </Box>
  );
}
