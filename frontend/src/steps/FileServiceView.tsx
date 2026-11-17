import { Box, DataTable, Text } from 'grommet';
import { ClientGroup, EthernetPort, FileNodeStatus, FileReport, FileShareRecord, FileSystemRecord } from '../api';
import { Section } from '../ui/blocks';
import { InlineNotification, NotesList, TableSummary } from '../ui/primitives';
import { NoValue, StatusIndicator } from '../ui/status';

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };

const NODE_RUNNING = 'normal';

// Capacity on the file side is in MiB.
function size(mib: number): string {
  if (mib >= 1024 * 1024) return `${(mib / (1024 * 1024)).toFixed(1)} TiB`;
  return `${(mib / 1024).toFixed(mib % 1024 === 0 ? 0 : 1)} GiB`;
}

// "STATE_NORMAL" -> "normal".
function stateWord(state: string): string {
  return state.replace(/^STATE_/, '').replaceAll('_', ' ').toLowerCase();
}

function StateCell({ state }: { state: string }) {
  const word = stateWord(state);
  return <StatusIndicator state={word === 'normal' ? 'complete' : 'action_required'} label={word} />;
}

function clientText(group: ClientGroup | undefined): string[] {
  if (!group) return ['client group not read'];
  if (!group.clients.length) return ['no clients'];
  return group.clients.map((c) => {
    const who = c.address === '*' ? 'any host that can reach the File ports' : c.address;
    return [who, c.access, c.options].filter(Boolean).join(' · ');
  });
}

function PortsTable({ ports }: { ports: EthernetPort[] }) {
  return (
    <>
      <Text size="small" color="text-weak">
        These sit in the same slots as iSCSI ports, so the role comes from the array&apos;s own port type, never from the slot number.
      </Text>
      <DataTable
        columns={[
          { property: 'label', header: 'Port', render: (p: EthernetPort) => <Text size="small" style={mono}>{`${p.node}:${p.slot}:${p.card_port}`}</Text> },
          {
            property: 'address',
            header: 'IP address',
            render: (p: EthernetPort) => <Text size="small" style={mono}>{p.address ? `${p.address}/${p.prefix_len}` : <NoValue />}</Text>,
          },
          { property: 'gateway', header: 'Gateway', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.gateway || <NoValue />}</Text> },
          { property: 'vlan', header: 'VLAN', render: (p: EthernetPort) => <Text size="small">{p.vlan || <NoValue />}</Text> },
          { property: 'mtu', header: 'MTU', render: (p: EthernetPort) => <Text size="small">{p.mtu || <NoValue />}</Text> },
          { property: 'eth', header: 'Interface', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.eth || <NoValue />}</Text> },
          {
            property: 'link',
            header: 'Link',
            render: (p: EthernetPort) => (
              <Box gap="xxsmall">
                <StatusIndicator state={p.link === 'up' ? 'complete' : 'action_required'} label={p.link === 'up' ? `up · ${p.rate}` : p.link_state} />
                {/* A port whose address is carried by its partner is covered, not simply dead. */}
                {p.ip_disabled && <Text size="xsmall" color="text-weak">IP disabled</Text>}
              </Box>
            ),
          },
          {
            property: 'failover_ips',
            header: 'Failover for',
            render: (p: EthernetPort) => <Text size="small" style={mono} color="text-weak">{p.failover_ips.join(', ') || <NoValue />}</Text>,
          },
        ]}
        data={ports}
        primaryKey={false}
        a11yTitle="File ports with address, gateway, VLAN, MTU and link"
      />
    </>
  );
}

/**
 * The array's file side in Discovery: the file service, its File ports, file systems and shares
 * with their clients, each part folded. Shown when the array has File ports or a file service that
 * is on; on most block arrays there is neither, and nothing is shown.
 */
export function FileServiceView({ ports, file }: { ports: EthernetPort[]; file: FileReport | null | undefined }) {
  const service = file?.service ?? null;
  const groups = new Map((file?.client_groups ?? []).map((g) => [g.name, g]));
  const portsUp = ports.filter((p) => p.link === 'up').length;
  const nodesRunning = service ? service.nodes.filter((n) => n.status === NODE_RUNNING).length : 0;
  const summary = [
    service ? (service.enabled ? `on · ${nodesRunning} of ${service.nodes.length} nodes running` : 'off') : 'service not read',
    `${portsUp} of ${ports.length} File port${ports.length === 1 ? '' : 's'} up`,
    service ? `${file?.file_systems.length ?? 0} file system${file?.file_systems.length === 1 ? '' : 's'}` : '',
    service ? `${file?.shares.length ?? 0} share${file?.shares.length === 1 ? '' : 's'}` : '',
  ].filter(Boolean);

  const notesToRead = Boolean(file?.notes.length);
  return (
    // keyed: Section reads `open` once, so it opens by itself only while the file side has notes to read
    <Section key={notesToRead ? 'notes' : 'quiet'} title="File service" summary={summary.join(' · ')} open={notesToRead}>
      <Text size="small" color="text-weak">
        The array&apos;s NFS file service, read from the array. This run changes nothing on the file side.
      </Text>
      {file && file.notes.length > 0 && (
        <InlineNotification tone="warning" title="File service notes" message={<NotesList notes={file.notes} />} />
      )}

      {service && (
        <Section
          level={3}
          title="Service"
          summary={service.enabled ? `on · ${nodesRunning} of ${service.nodes.length} nodes running` : 'off'}
        >
          <DataTable
            columns={[
              { property: 'node', header: 'Node', render: (n: FileNodeStatus) => <Text size="small">{n.node}</Text> },
              {
                property: 'status',
                header: 'File service',
                render: (n: FileNodeStatus) => (
                  <StatusIndicator
                    state={n.status === NODE_RUNNING ? 'complete' : 'action_required'}
                    label={n.status === NODE_RUNNING ? 'running' : n.status}
                  />
                ),
              },
              {
                property: 'ports',
                header: 'File ports online',
                render: (n: FileNodeStatus) => <Text size="small">{`${n.ports.filter((p) => p.online).length} of ${n.ports.length}`}</Text>,
              },
            ]}
            data={service.nodes}
            primaryKey={false}
            a11yTitle="File service state on each controller node"
          />
          {service.capacity && (
            <TableSummary>
              Capacity for file: {size(service.capacity.total)} · {size(service.capacity.used)} used · {size(service.capacity.available)}{' '}
              available
              {service.capacity.limit_percentage ? ` · limit ${service.capacity.limit_percentage}%` : ''}
            </TableSummary>
          )}
        </Section>
      )}

      {ports.length > 0 && (
        <Section level={3} title="File ports" summary={`${portsUp} of ${ports.length} up`}>
          <PortsTable ports={ports} />
        </Section>
      )}

      {service && (
        <Section
          level={3}
          title="File systems"
          summary={`${file?.file_systems.length ?? 0} file system${file?.file_systems.length === 1 ? '' : 's'}`}
        >
          {file && file.file_systems.length > 0 ? (
            <DataTable
              columns={[
                { property: 'name', header: 'File system', render: (fs: FileSystemRecord) => <Text size="small" style={mono}>{fs.name}</Text> },
                { property: 'size_mib', header: 'Size', align: 'end', render: (fs: FileSystemRecord) => <Text size="small">{size(fs.size_mib)}</Text> },
                { property: 'reduce', header: 'Data reduction', render: (fs: FileSystemRecord) => <Text size="small">{fs.reduce ? 'yes' : 'no'}</Text> },
                { property: 'share_count', header: 'Shares', align: 'end', render: (fs: FileSystemRecord) => <Text size="small">{fs.share_count}</Text> },
                { property: 'owner_node', header: 'Owner node', align: 'end', render: (fs: FileSystemRecord) => <Text size="small">{fs.owner_node}</Text> },
                { property: 'state', header: 'State', render: (fs: FileSystemRecord) => <StateCell state={fs.state} /> },
              ]}
              data={file.file_systems}
              primaryKey={false}
              a11yTitle="File systems with size, data reduction, share count and state"
            />
          ) : (
            <Text size="small" color="text-weak">The array has no file systems.</Text>
          )}
        </Section>
      )}

      {service && (
        <Section level={3} title="Shares" summary={`${file?.shares.length ?? 0} share${file?.shares.length === 1 ? '' : 's'}, with their clients`}>
          {file && file.shares.length > 0 ? (
            <DataTable
              columns={[
                { property: 'name', header: 'Share', render: (s: FileShareRecord) => <Text size="small" style={mono}>{s.name}</Text> },
                { property: 'file_system', header: 'File system', render: (s: FileShareRecord) => <Text size="small" style={mono}>{s.file_system}</Text> },
                {
                  property: 'client_group',
                  header: 'Client group and clients',
                  render: (s: FileShareRecord) => (
                    <Box gap="xxsmall">
                      <Text size="small" style={mono}>{s.client_group}</Text>
                      {clientText(groups.get(s.client_group)).map((line) => (
                        <Text key={line} size="xsmall" color="text-weak">{line}</Text>
                      ))}
                    </Box>
                  ),
                },
                {
                  property: 'mount_path',
                  header: 'Mount',
                  render: (s: FileShareRecord) => (
                    <Text size="small" style={mono}>{s.host_ip ? `${s.host_ip}:${s.mount_path}` : s.mount_path}</Text>
                  ),
                },
                { property: 'protocols', header: 'Protocol', render: (s: FileShareRecord) => <Text size="small">{s.protocols.join(', ') || <NoValue />}</Text> },
                { property: 'state', header: 'State', render: (s: FileShareRecord) => <StateCell state={s.state} /> },
              ]}
              data={file.shares}
              primaryKey={false}
              a11yTitle="File shares with file system, client group, clients, mount path and state"
            />
          ) : (
            <Text size="small" color="text-weak">The array has no shares.</Text>
          )}
        </Section>
      )}
    </Section>
  );
}
