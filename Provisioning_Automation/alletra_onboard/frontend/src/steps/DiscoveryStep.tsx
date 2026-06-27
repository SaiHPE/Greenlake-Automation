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
          Reads the array FC target ports (WSAPI), each ESXi host&apos;s FC HBA WWPNs and OS (vCenter),
          and which fabric each HBA logs into (both switches&apos; nameserver). Nothing is changed.
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button primary label={running ? 'Discovering…' : report ? 'Re-run discovery' : 'Run discovery'} disabled={running} onClick={run_} />
          {running && <Spinner />}
        </Box>
        {error && <Notification status="critical" title="Discovery failed to start" message={error} onClose={() => setError(null)} />}
      </Section>

      {report && (
        <>
          <Section title={`Array FC ports (${report.array_ports.length})`}>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableCell><Text size="small" weight="bold">Port (n:s:p)</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">WWPN</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">Fabric</Text></TableCell>
                  <TableCell><Text size="small" weight="bold">Link</Text></TableCell>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report.array_ports.map((p) => (
                  <TableRow key={p.wwpn}>
                    <TableCell><Text size="small">{p.node}:{p.slot}:{p.card_port}</Text></TableCell>
                    <TableCell><Text size="small">{p.wwpn}</Text></TableCell>
                    <TableCell><Text size="small">{p.fabric}</Text></TableCell>
                    <TableCell><Text size="small">{p.link_state}</Text></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Section>

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
