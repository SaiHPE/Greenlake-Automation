import { Box, Button, DataTable, Text } from 'grommet';
import { useState } from 'react';
import {
  ArrayPort,
  DiscoveredHost,
  DiscoveryReport,
  EthernetPort,
  PreflightCheck,
  PreflightReport,
  RunEvent,
  RunRecord,
  getStoragePreflight,
  startDiscover,
} from '../api';
import { DiscoveryFreshness } from '../ui/discoveryAge';
import { ContinueButton, InlineNotification, NotesList, Surface, TableSummary } from '../ui/primitives';
import { StatusIndicator } from '../ui/status';
import { StepShell } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };

// SPEC-009: hosts are grouped by whose they are, not by OS. OS is a column; a host some source NAMED is
// identified even when nothing reports its OS (D-2: `vmenode`, Generic-ALUA, was filed as unidentified).
const OS_LABEL: Record<DiscoveredHost['os'], string> = {
  esxi: 'ESXi', windows: 'Windows', linux: 'Linux', vme: 'HPE VM Essentials', unknown: 'not reported',
};
const OTHER_HOSTS_FOLD = 10;

function osLabel(h: DiscoveredHost): string {
  if (h.os_text) return h.os_text;
  return OS_LABEL[h.os] ?? h.os;
}

// The RCIP state must agree with the row's own link (D-3): an unconfigured port with no link is not
// "available", it is not cabled.
function rcipState(p: EthernetPort): { state: 'complete' | 'not_started' | 'action_required'; label: string } {
  if (p.role === 'rcip') return { state: 'complete', label: 'Configured' };
  if (p.link_state === 'ready') return { state: 'not_started', label: 'Available' };
  return { state: 'action_required', label: 'Not cabled' };
}

const HOST_COLUMNS = [
  {
    property: 'name',
    header: 'Host',
    render: (h: DiscoveredHost) => (
      <Box gap="xxsmall">
        <Text size="small" weight={h.identified === false ? undefined : 500}>{h.name}</Text>
        {h.identified === false && <Text size="xsmall" color="text-weak">no source names this server</Text>}
        {/* The array's own name for the same server, when it differs — an operator cross-checking
            showhost needs to recognise the row. */}
        {h.array_host_name && h.array_host_name !== h.name && (
          <Text size="xsmall" color="text-weak">on the array: {h.array_host_name}</Text>
        )}
        {h.address && <Text size="xsmall" color="text-weak" style={mono}>{h.address}</Text>}
      </Box>
    ),
  },
  {
    property: 'os',
    header: 'OS',
    render: (h: DiscoveredHost) => (
      <Box gap="xxsmall">
        <Text size="small" color={h.os === 'unknown' && !h.os_text ? 'text-weak' : undefined}>{osLabel(h)}</Text>
        {h.persona && <Text size="xsmall" color="text-weak">persona {h.persona}</Text>}
      </Box>
    ),
  },
  {
    property: 'initiators',
    header: 'Initiators → array ports',
    render: (h: DiscoveredHost) => (
      <Box gap="xxsmall">
        {[...h.wwpns, ...h.iqns].length === 0 && <Text size="small" color="text-weak">none configured</Text>}
        {[...h.wwpns, ...h.iqns].map((id) => {
          const ports = h.ports?.[id] ?? [];
          return (
            <Box key={id} direction="row" gap="small" align="center" wrap>
              <Text size="small" style={mono}>{id}</Text>
              <Text size="xsmall" color="text-weak" style={mono}>{ports.length ? `→ ${ports.join(', ')}` : '→ not logged in'}</Text>
            </Box>
          );
        })}
      </Box>
    ),
  },
  {
    property: 'logged_in',
    header: 'Seen by the array',
    render: (h: DiscoveredHost) => (
      <StatusIndicator
        state={h.logged_in ? 'complete' : 'not_started'}
        label={h.logged_in ? (h.fabrics.length ? `Logged in (${h.fabrics.join(', ')})` : 'Logged in') : 'Not logged in'}
      />
    ),
  },
  {
    property: 'array_host_name',
    header: 'Array host object',
    render: (h: DiscoveredHost) =>
      h.array_host_name ? (
        <Text size="small" style={mono}>{h.array_host_name}</Text>
      ) : (
        <Text size="small" color="text-weak">{h.in_run ? 'none yet — provisioning creates one' : 'none yet'}</Text>
      ),
  },
];

function HostsTable({ title, description, rows, fold }: { title: string; description: string; rows: DiscoveredHost[]; fold?: boolean }) {
  const [open, setOpen] = useState(false);
  const folded = !!fold && !open && rows.length > OTHER_HOSTS_FOLD;
  return (
    <Surface title={`${title} (${rows.length})`} description={description}>
      <DataTable columns={HOST_COLUMNS} data={folded ? rows.slice(0, OTHER_HOSTS_FOLD) : rows} primaryKey={false} a11yTitle={`${title}: one row per server`} />
      {folded && (
        <Box direction="row" align="center" gap="small">
          <Text size="small" color="text-weak">{rows.length - OTHER_HOSTS_FOLD} more not shown.</Text>
          <Button size="small" label={`Show all ${rows.length}`} onClick={() => setOpen(true)} />
        </Box>
      )}
    </Surface>
  );
}

export function DiscoveryStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [preflight, setPreflight] = useState<PreflightReport | null>(null);
  const [checking, setChecking] = useState(false);
  const running = run?.status === 'running';

  const report =
    ([...events].reverse().find((event) => event.event_type === 'discover.completed')?.data?.report as
      | DiscoveryReport
      | undefined) ?? null;
  const fcPorts = (report?.array_ports ?? []).filter((port) => port.protocol === 'fc');
  const iscsiPorts = (report?.array_ports ?? []).filter((port) => port.protocol === 'iscsi');
  const readyPorts = fcPorts.filter((port) => port.link_state === 'ready').length;
  const hosts = report?.hosts ?? [];
  // SPEC-012 R7 (X-7): the discovery before this one, within the run.
  const completedDiscoveries = events.filter((event) => event.event_type === 'discover.completed');
  const previousDiscovery = completedDiscoveries.length >= 2 ? completedDiscoveries[completedDiscoveries.length - 2] : null;
  const previousReport = (previousDiscovery?.data?.report as DiscoveryReport | undefined) ?? null;
  const changes: string[] = [];
  if (report && previousReport) {
    const before = new Set((previousReport.hosts ?? []).map((h) => h.name));
    const after = new Set(hosts.map((h) => h.name));
    const appeared = [...after].filter((n) => !before.has(n));
    const gone = [...before].filter((n) => !after.has(n));
    if (appeared.length) changes.push(`${appeared.length} host${appeared.length === 1 ? '' : 's'} appeared: ${appeared.join(', ')}`);
    if (gone.length) changes.push(`${gone.length} host${gone.length === 1 ? '' : 's'} no longer seen: ${gone.join(', ')}`);
    const linkBefore = new Map(previousReport.array_ports.map((p) => [`${p.node}:${p.slot}:${p.card_port}`, p.link_state]));
    (report.array_ports ?? []).forEach((p) => {
      const key = `${p.node}:${p.slot}:${p.card_port}`;
      const was = linkBefore.get(key);
      if (was && was !== p.link_state) changes.push(`port ${key}: ${was} → ${p.link_state}`);
    });
  }
  // Older runs (before SPEC-009) have no in_run flag; a vCenter/sheet source is the same rule.
  const inRun = hosts.filter((h) => h.in_run ?? (h.sources.includes('vcenter') || h.sources.includes('sheet')));
  const others = hosts.filter((h) => !inRun.includes(h));

  const discover = async () => {
    setError(null);
    try {
      await startDiscover(runId);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  const checkReadiness = async () => {
    setError(null);
    setChecking(true);
    try {
      setPreflight(await getStoragePreflight(runId));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setChecking(false);
    }
  };

  return (
    <StepShell
      title="Discovery"
      description="Reads the array target ports, the ESXi host adapters from vCenter, and their fabric logins. Read-only."
      stateDetail={report ? `${fcPorts.length} ports · ${inRun.length} host${inRun.length === 1 ? '' : 's'} in this run` : undefined}
      error={error}
      onDismissError={() => setError(null)}
      activityEmpty="Run discovery to read the environment."
      footerNote="Discovery results persist with the run and survive an application restart."
      actions={
        <>
          <Button busy={checking} label={checking ? 'Checking' : 'Check readiness'} onClick={checkReadiness} />
          <Button
            busy={running}
            label={report ? 'Re-run discovery' : running ? 'Discovering' : 'Run discovery'}
            onClick={discover}
          />
          {report && <ContinueButton onClick={onDone} />}
        </>
      }
    >
      {preflight && (
        <Surface
          title="Environment readiness"
          description="Read-only checks against the array and vCenter named in the sheet. Nothing is modified."
        >
          <DataTable
            columns={[
              {
                property: 'label',
                header: 'Check',
                render: (check: PreflightCheck) => <Text size="small">{check.label}</Text>,
              },
              {
                property: 'status',
                header: 'Result',
                render: (check: PreflightCheck) => (
                  <StatusIndicator
                    state={check.status === 'pass' ? 'complete' : check.status === 'warn' ? 'action_required' : 'failed'}
                    label={check.status === 'pass' ? 'Ready' : check.status === 'warn' ? 'Review' : 'Blocked'}
                  />
                ),
              },
              {
                property: 'detail',
                header: 'Detail',
                render: (check: PreflightCheck) => (
                  <Text size="small" color="text-weak">
                    {check.detail}
                  </Text>
                ),
              },
            ]}
            data={preflight.checks}
            primaryKey={false}
            a11yTitle="Environment readiness: one row per prerequisite check"
          />
          <TableSummary>
            {preflight.ready
              ? 'Every prerequisite is satisfied — discovery can run.'
              : 'Resolve the blocked checks above; discovery cannot succeed until they pass.'}
          </TableSummary>
        </Surface>
      )}

      {!report && !running && (
        <Surface title="Nothing discovered yet">
          <Text size="small" color="text-weak">
            {/* X-5: what's missing, why, the way forward. */}
            No array ports, hosts or fabric logins are known for this run yet. Zoning and provisioning need them
            to decide which hosts can be presented to. Run discovery (read-only: the array's ports and host view,
            plus each ESXi host's adapters from vCenter) — or run <i>Check readiness</i> first if you are unsure the
            array and vCenter are reachable.
          </Text>
        </Surface>
      )}

      <DiscoveryFreshness events={events} action="continuing" />

      {report?.error && <InlineNotification tone="critical" title="Discovery reported a problem" message={report.error} />}

      {report && previousDiscovery && (
        <InlineNotification
          tone="info"
          title={`Since the discovery at ${new Date(previousDiscovery.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
          message={changes.length ? <NotesList notes={changes} /> : 'No change: the same hosts, and every array port in the same link state.'}
        />
      )}

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
            a11yTitle="Array Fibre Channel target ports with fabric and link state"
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
            a11yTitle="Array iSCSI ports with address and link state"
          />
        </Surface>
      )}

      {report && report.file_ports.length > 0 && (
        <Surface
          title="File service ports"
          description="Ethernet ports serving file protocols. These occupy the same n:s:p as iSCSI ports, so the role comes from the array's own port type, never from the slot number."
        >
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (p: EthernetPort) => <Text size="small" style={mono}>{`${p.node}:${p.slot}:${p.card_port}`}</Text> },
              {
                property: 'address',
                header: 'IP address',
                render: (p: EthernetPort) => (
                  <Text size="small" style={mono}>{p.address ? `${p.address}/${p.prefix_len}` : '—'}</Text>
                ),
              },
              { property: 'vlan', header: 'VLAN', render: (p: EthernetPort) => <Text size="small">{p.vlan || '—'}</Text> },
              { property: 'mtu', header: 'MTU', render: (p: EthernetPort) => <Text size="small">{p.mtu || '—'}</Text> },
              { property: 'eth', header: 'Interface', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.eth || '—'}</Text> },
              {
                property: 'link',
                header: 'Link',
                render: (p: EthernetPort) => (
                  <Box gap="xxsmall">
                    <StatusIndicator
                      state={p.link === 'up' ? 'complete' : 'action_required'}
                      label={p.link === 'up' ? `up · ${p.rate}` : p.link_state}
                    />
                    {/* A port whose address is carried by its partner is covered, not simply dead. */}
                    {p.ip_disabled && <Text size="xsmall" color="text-weak">IP disabled</Text>}
                  </Box>
                ),
              },
              {
                property: 'failover_ips',
                header: 'Failover for',
                render: (p: EthernetPort) => (
                  <Text size="small" style={mono} color="text-weak">{p.failover_ips.join(', ') || '—'}</Text>
                ),
              },
            ]}
            data={report.file_ports}
            primaryKey={false}
            a11yTitle="File service ports with address, VLAN, MTU and link"
          />
        </Surface>
      )}

      {report && report.replication_ports.length > 0 && (
        <Surface
          title="Replication ports (RCIP)"
          description="IP replication ports. Configured = carries a replication address; Available = link up, no replication configuration yet; Not cabled = no link. The array's node interconnect looks identical apart from its port type and is deliberately excluded."
        >
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (p: EthernetPort) => <Text size="small" style={mono}>{`${p.node}:${p.slot}:${p.card_port}`}</Text> },
              {
                property: 'role',
                header: 'State',
                render: (p: EthernetPort) => {
                  const s = rcipState(p);
                  return <StatusIndicator state={s.state} label={s.label} />;
                },
              },
              { property: 'address', header: 'IP address', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.address || '—'}</Text> },
              { property: 'netmask', header: 'Netmask', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.netmask || '—'}</Text> },
              { property: 'gateway', header: 'Gateway', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.gateway || '—'}</Text> },
              {
                property: 'link_state',
                header: 'Link',
                render: (p: EthernetPort) => (
                  <StatusIndicator
                    state={p.link_state === 'ready' ? 'complete' : 'action_required'}
                    label={p.link_state === 'ready' && p.rate ? `${p.link_state} · ${p.rate}` : p.link_state}
                  />
                ),
              },
            ]}
            data={report.replication_ports}
            primaryKey={false}
            a11yTitle="Replication (RCIP) ports with configuration state and link"
          />
          <TableSummary>
            {report.replication_ports.filter((p) => p.role === 'rcip').length} of{' '}
            {report.replication_ports.length} replication-capable ports configured
          </TableSummary>
        </Surface>
      )}

      {report && hosts.length > 0 && (
        <>
          <HostsTable
            title="Hosts in this run"
            description="Servers the sheet's vCenter reports, the sheet declares, or a sheet host set names. These are the hosts provisioning may create or present to."
            rows={inRun}
          />
          <HostsTable
            title="Other hosts on this array"
            description="Every other server the array can see — other tenants of a shared array. Listed so you know what not to touch; this run never changes them."
            rows={others}
            fold
          />
          <Text size="xsmall" color="text-weak">
            Legend — <b>Logged in (odd, even)</b>: the array sees the initiator on those fabrics · <b>Not logged in</b>: configured
            or expected but no login (not zoned, or the server is off) · <b>none yet</b>: no host object on the array; provisioning
            creates one · <b>OS not reported</b>: no source states an operating system (the array's persona is shown when it has one).
          </Text>
        </>
      )}

      {report && report.notes.length > 0 && (
        <InlineNotification tone="info" title="Discovery notes" message={<NotesList notes={report.notes} />} />
      )}
    </StepShell>
  );
}
