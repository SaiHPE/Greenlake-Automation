import { Box, Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import { ArrayHost, ArrayPort, DiscoveryReport, HostHba, RunEvent, RunRecord, startDiscover } from '../api';
import { DiscoveryFreshness } from '../ui/discoveryAge';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator } from '../ui/status';
import { StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };

export function DiscoveryStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';

  const report =
    ([...events].reverse().find((event) => event.event_type === 'discover.completed')?.data?.report as
      | DiscoveryReport
      | undefined) ?? null;
  const fcPorts = (report?.array_ports ?? []).filter((port) => port.protocol === 'fc');
  const iscsiPorts = (report?.array_ports ?? []).filter((port) => port.protocol === 'iscsi');
  const readyPorts = fcPorts.filter((port) => port.link_state === 'ready').length;

  const discover = async () => {
    setError(null);
    try {
      await startDiscover(runId);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <StepShell
      title="Discovery"
      description="Reads the array target ports, the ESXi host adapters from vCenter, and their fabric logins. Read-only."
      stateDetail={report ? `${fcPorts.length} ports · ${report.host_hbas.length} adapters` : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Run discovery to read the environment."
      footerNote="Discovery results persist with the run and survive an application restart."
      actions={
        <>
          <Button
            busy={running}
            label={report ? 'Re-run discovery' : running ? 'Discovering' : 'Run discovery'}
            onClick={discover}
          />
          {report && <Button primary label="Continue" onClick={onDone} />}
        </>
      }
    >
      {!report && !running && (
        <Surface title="Nothing discovered yet">
          <Text size="small" color="text-weak">
            Discovery reads every array target port, the array's own host view, and each ESXi host's adapters from
            vCenter, then matches each adapter to the fabric it logs into. Nothing is modified.
          </Text>
        </Surface>
      )}

      <DiscoveryFreshness events={events} action="continuing" />

      {report?.error && <InlineNotification tone="critical" title="Discovery reported a problem" message={report.error} />}

      {report && (
        <Surface title="Array target ports" description="Fibre Channel ports the array presents to hosts.">
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (port: ArrayPort) => <Text size="small" style={mono}>{`${port.node}:${port.slot}:${port.card_port}`}</Text> },
              { property: 'wwpn', header: 'WWPN', render: (port: ArrayPort) => <Text size="small" style={mono}>{port.wwpn}</Text> },
              {
                property: 'fabric',
                header: 'Fabric',
                render: (port: ArrayPort) => (
                  <Text size="small">{port.fabric ? `${port.fabric}${port.fabric_switch ? ` (${port.fabric_switch})` : ''}` : '—'}</Text>
                ),
              },
              {
                property: 'link_state',
                header: 'Link',
                render: (port: ArrayPort) => (
                  <StatusIndicator
                    state={port.link_state === 'ready' ? 'complete' : 'action_required'}
                    label={port.link_state === 'ready' ? 'Ready' : port.link_state.replaceAll('_', ' ')}
                  />
                ),
              },
            ]}
            data={fcPorts}
            primaryKey={false}
          />
          <TableSummary>
            {readyPorts} ready · {fcPorts.length - readyPorts} require a cable or switch-port check
          </TableSummary>
        </Surface>
      )}

      {iscsiPorts.length > 0 && (
        <Surface title="Array iSCSI ports">
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (port: ArrayPort) => <Text size="small" style={mono}>{`${port.node}:${port.slot}:${port.card_port}`}</Text> },
              { property: 'address', header: 'IP address', render: (port: ArrayPort) => <Text size="small" style={mono}>{port.address || '—'}</Text> },
              {
                property: 'link_state',
                header: 'Link',
                render: (port: ArrayPort) => (
                  <StatusIndicator state={port.link_state === 'ready' ? 'complete' : 'action_required'} label={port.link_state} />
                ),
              },
            ]}
            data={iscsiPorts}
            primaryKey={false}
          />
        </Surface>
      )}

      {report && report.host_hbas.length > 0 && (
        <Surface
          title="ESXi hosts"
          description="Fabric logins indicate which hosts can be provisioned safely."
        >
          <DataTable
            columns={[
              { property: 'host_name', header: 'Host', render: (hba: HostHba) => <Text size="small">{hba.host_name}</Text> },
              { property: 'wwpn', header: 'Adapter WWPN', render: (hba: HostHba) => <Text size="small" style={mono}>{hba.wwpn}</Text> },
              {
                property: 'fabric',
                header: 'Fabric login',
                render: (hba: HostHba) =>
                  hba.fabric ? (
                    <StatusIndicator state="complete" label={`${hba.fabric} fabric`} />
                  ) : (
                    <StatusIndicator state="not_started" label="Not logged in" />
                  ),
              },
              { property: 'os', header: 'Operating system', render: (hba: HostHba) => <Text size="small">{hba.os ?? '—'}</Text> },
            ]}
            data={report.host_hbas}
            primaryKey={false}
          />
          <TableSummary>
            {new Set(report.host_hbas.map((hba) => hba.host_name)).size} hosts · {report.host_hbas.length} adapters ·{' '}
            {report.host_hbas.filter((hba) => hba.fabric).length} logged in
          </TableSummary>
        </Surface>
      )}

      {report && report.array_hosts.length > 0 && (
        <Surface
          title="Hosts known to the array"
          description="An adapter with no ports listed is configured on the array but not logged in — it is not zoned, or the host is offline."
        >
          <DataTable
            columns={[
              { property: 'name', header: 'Host', render: (host: ArrayHost) => <Text size="small">{host.name}</Text> },
              { property: 'persona', header: 'Persona', render: (host: ArrayHost) => <Text size="small">{host.persona || '—'}</Text> },
              {
                property: 'wwpns',
                header: 'Logged-in ports',
                render: (host: ArrayHost) => (
                  <Box gap="xxsmall">
                    {Object.entries(host.wwpns).map(([wwpn, ports]) => (
                      <Box key={wwpn} direction="row" gap="small" align="center" wrap>
                        <Text size="small" style={mono}>
                          {wwpn}
                        </Text>
                        {ports.length ? (
                          <Text size="small" color="text-weak" style={mono}>
                            {ports.join(', ')}
                          </Text>
                        ) : (
                          <StatusIndicator state="not_started" label="Not logged in" />
                        )}
                      </Box>
                    ))}
                  </Box>
                ),
              },
            ]}
            data={report.array_hosts}
            primaryKey={false}
          />
        </Surface>
      )}

      {report && report.notes.length > 0 && (
        <InlineNotification tone="info" title="Discovery notes" message={report.notes.join(' · ')} />
      )}
    </StepShell>
  );
}
