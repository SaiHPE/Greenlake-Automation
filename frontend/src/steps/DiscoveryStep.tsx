import { Box, Button, DataTable, Text } from 'grommet';
import { Search, StatusWarning } from 'grommet-icons';
import { ReactNode, useState } from 'react';
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
import { Disclosure, EmptyState, Guidance, Section } from '../ui/blocks';
import { discoveryReadAt, isDiscoveryStale } from '../ui/discoveryAge';
import { NotesList, TableSummary } from '../ui/primitives';
import { NoValue, RESULT, StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { StepShell, StepStatus } from '../ui/StepShell';
import { FileServiceView } from '../ui/FileServiceView';

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
// A Linux host's own multipath view that needs the operator: a failed, missing or single path, no
// multipath, a login that cannot read it, or a read that timed out. "none" (no Alletra devices yet) is
// normal before volumes are presented.
const MULTIPATH_WARN = new Set(['degraded', 'uneven', 'not_set_up', 'not_permitted', 'timed_out']);

// A host the operator should look at: not logged in to the array, or a multipath warning (BL-36).
const needsLook = (h: DiscoveredHost) => !h.logged_in || MULTIPATH_WARN.has(h.multipath_state ?? '');

const hhmm = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

// This step makes the snapshot, so its age is a note here; the steps that act on it warn (LESSONS 8).
function freshnessNote(events: RunEvent[]): string | null {
  const when = discoveryReadAt(events);
  if (!when) return null;
  return isDiscoveryStale(events)
    ? `The environment was last read ${when.toLocaleString()}, more than 12 hours ago. If hosts, cabling or zoning have changed since, run discovery again.`
    : `Environment last read ${when.toLocaleString()}.`;
}

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
        {h.lookup && (
          <Text size="xsmall" color={h.lookup.startsWith('not found') ? 'status-warning' : 'text-weak'}>sheet host {h.lookup}</Text>
        )}
        {h.host_read && (
          <Text size="xsmall" color={h.host_read.startsWith('read over') ? 'text-weak' : 'status-warning'}>{h.host_read}</Text>
        )}
      </Box>
    ),
  },
  {
    property: 'serial_number',
    header: 'Serial number',
    render: (h: DiscoveredHost) =>
      h.serial_number ? (
        <Text size="small" style={mono}>{h.serial_number}</Text>
      ) : (
        <Text size="small" color="text-weak">not reported</Text>
      ),
  },
  {
    property: 'os',
    header: 'OS',
    render: (h: DiscoveredHost) => (
      <Box gap="xxsmall">
        <Text size="small" color={h.os === 'unknown' && !h.os_text ? 'text-weak' : undefined}>{osLabel(h)}</Text>
        {h.persona && <Text size="xsmall" color="text-weak">persona {h.persona}</Text>}
        {h.multipath &&
          (MULTIPATH_WARN.has(h.multipath_state ?? '') ? (
            <Box direction="row" gap="xxsmall" align="start">
              <Box flex={false} pad={{ top: 'xxsmall' }}>
                <StatusWarning size="small" color="status-warning" a11yTitle="Warning" />
              </Box>
              <Text size="xsmall" color="status-warning">multipath: {h.multipath}</Text>
            </Box>
          ) : (
            <Text size="xsmall" color="text-weak">multipath: {h.multipath}</Text>
          ))}
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

function HostsTable({ title, description, rows, fold, open: openInitially }: { title: string; description: string; rows: DiscoveredHost[]; fold?: boolean; open?: boolean }) {
  const [open, setOpen] = useState(false);
  const folded = !!fold && !open && rows.length > OTHER_HOSTS_FOLD;
  const loggedIn = rows.filter((h) => h.logged_in).length;
  return (
    <Section title={`${title} (${rows.length})`} summary={`${loggedIn} logged in to the array`} open={openInitially}>
      <Text size="small" color="text-weak">
        {description}
      </Text>
      <DataTable columns={HOST_COLUMNS} data={folded ? rows.slice(0, OTHER_HOSTS_FOLD) : rows} primaryKey={false} a11yTitle={`${title}: one row per server`} />
      {folded && (
        <Box direction="row" align="center" gap="small">
          <Text size="small" color="text-weak">{rows.length - OTHER_HOSTS_FOLD} more not shown.</Text>
          <Button size="small" label={`Show all ${rows.length}`} onClick={() => setOpen(true)} />
        </Box>
      )}
      <Disclosure label="what the columns mean">
        <Text size="xsmall" color="text-weak">
          <b>Logged in (odd, even)</b>: the array sees the initiator on those fabrics. <b>Not logged in</b>: configured or expected but
          no login (not zoned, or the server is off). <b>none yet</b>: no host object on the array; provisioning creates one. <b>OS not
          reported</b>: no source states an operating system (the array&apos;s persona is shown when it has one).
        </Text>
      </Disclosure>
    </Section>
  );
}

export function DiscoveryStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const [error, setError] = useState<string | null>(null);
  const [preflight, setPreflight] = useState<PreflightReport | null>(null);
  const [checking, setChecking] = useState(false);
  const running = run?.status === 'running';

  const report =
    ([...events].reverse().find((event) => event.event_type === 'discover.completed')?.data?.report as
      | DiscoveryReport
      | undefined) ?? null;
  const reportAt = [...events].reverse().find((event) => event.event_type === 'discover.completed')?.created_at;
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

  // One status line: running, then a problem the read reported, then the counts (SPEC-030 R2).
  const status: StepStatus | undefined = running
    ? { state: 'running', message: 'Reading the array, vCenter and the hosts. Each part appears in Activity, below.' }
    : report?.error
      ? { state: 'failed', title: 'Discovery reported a problem', message: report.error }
      : report
        ? {
            state: 'complete',
            title: 'Discovery finished',
            time: reportAt ? hhmm(reportAt) : undefined,
            message: `${fcPorts.length} Fibre Channel port${fcPorts.length === 1 ? '' : 's'} (${readyPorts} ready), ${inRun.length} host${
              inRun.length === 1 ? '' : 's'
            } in this run, ${others.length} other host${others.length === 1 ? '' : 's'} on the array. Nothing was changed.`,
          }
        : undefined;
  const notes: ReactNode[] = [];
  if (report && previousDiscovery) {
    notes.push(
      changes.length ? (
        <>
          Since the discovery at {hhmm(previousDiscovery.created_at)}: <NotesList notes={changes} />
        </>
      ) : (
        `Since the discovery at ${hhmm(previousDiscovery.created_at)}: no change, the same hosts and every array port in the same link state.`
      ),
    );
  }
  if (report) notes.push(...report.notes);
  const freshness = freshnessNote(events);
  if (freshness) notes.push(freshness);

  const discover = async () => {
    setError(null);
    try {
      await startDiscover(runId);
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  };

  const checkReadiness = async () => {
    setError(null);
    setChecking(true);
    try {
      setPreflight(await getStoragePreflight(runId));
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setChecking(false);
    }
  };

  return (
    <StepShell
      title="Discovery"
      description="Reads the array's ports, the hosts and their fabric logins, and changes nothing."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      notes={notes}
      buttons={[
        { label: checking ? 'Checking' : 'Check readiness', busy: checking, onClick: checkReadiness },
        ...(report ? [{ label: running ? 'Discovering' : 'Run discovery again', busy: running, onClick: discover }] : []),
      ]}
      primary={
        report
          ? { label: nextTitle ? `Continue to ${nextTitle}` : 'Continue', onClick: onDone }
          : { label: running ? 'Discovering' : 'Run discovery', busy: running, onClick: discover }
      }
      guidance={
        <Guidance
          items={[
            {
              title: 'What it reads',
              body: "The array's target ports and host view over SSH, each ESXi host's adapters from vCenter, and the Windows and Linux hosts listed on the Hosts tab.",
            },
            { title: 'Read-only', body: 'Discovery changes nothing on the array, vCenter or the switches.' },
            { title: 'Kept with the run', body: 'The results stay with this run and survive a restart of the app. Run it again any time.' },
            { title: 'Not sure the array is reachable?', body: 'Check readiness tests the array and vCenter logins first, in a few seconds.' },
          ]}
        />
      }
    >
      {preflight && (
        // keyed: Section reads `open` once, so it opens by itself only while something is blocked
        <Section
          key={preflight.ready ? 'ready' : 'blocked'}
          title="Environment readiness"
          summary={preflight.ready ? 'Every prerequisite is met' : 'Something is blocked'}
          open={!preflight.ready}
          right={<StatusIndicator state={preflight.ready ? 'complete' : 'failed'} label={preflight.ready ? 'Ready' : 'Blocked'} />}
        >
          <Text size="small" color="text-weak">
            Read-only checks against the array and vCenter named in the sheet. Nothing is modified.
          </Text>
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
                render: (check: PreflightCheck) => {
                  const word = check.status === 'pass' ? RESULT.passed : check.status === 'warn' ? RESULT.review : RESULT.failed;
                  return <StatusIndicator state={word.state} label={word.label} />;
                },
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
              ? 'Every prerequisite is satisfied. Discovery can run.'
              : 'Resolve the blocked checks above; discovery cannot succeed until they pass.'}
          </TableSummary>
        </Section>
      )}

      {!report && !running && (
        <EmptyState icon={<Search size="large" color="icon-weak" />} title="Not run yet">
          {/* X-5: what's missing, why, the way forward. */}
          Run discovery to read the array&apos;s ports, the hosts and their fabric logins. SAN zoning and Provision storage need what it
          finds. It changes nothing. Not sure the array and vCenter are reachable? Check readiness first.
        </EmptyState>
      )}

      {report && (
        <Section
          title={`${fcPorts.length} array Fibre Channel port${fcPorts.length === 1 ? '' : 's'}`}
          summary={`${readyPorts} ready · ${fcPorts.length - readyPorts} need a cable or switch-port check`}
        >
          <Text size="small" color="text-weak">
            Fibre Channel ports the array presents to hosts.
          </Text>
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (port: ArrayPort) => <Text size="small" style={mono}>{`${port.node}:${port.slot}:${port.card_port}`}</Text> },
              { property: 'wwpn', header: 'WWPN', render: (port: ArrayPort) => <Text size="small" style={mono}>{port.wwpn}</Text> },
              {
                property: 'fabric',
                header: 'Fabric',
                render: (port: ArrayPort) => (
                  <Text size="small">{port.fabric ? `${port.fabric}${port.fabric_switch ? ` (${port.fabric_switch})` : ''}` : <NoValue />}</Text>
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
        </Section>
      )}

      {iscsiPorts.length > 0 && (
        <Section title={`${iscsiPorts.length} array iSCSI port${iscsiPorts.length === 1 ? '' : 's'}`} summary={`${iscsiPorts.filter((p) => p.link_state === 'ready').length} ready`}>
          <DataTable
            columns={[
              { property: 'label', header: 'Port', render: (port: ArrayPort) => <Text size="small" style={mono}>{`${port.node}:${port.slot}:${port.card_port}`}</Text> },
              { property: 'address', header: 'IP address', render: (port: ArrayPort) => <Text size="small" style={mono}>{port.address || <NoValue />}</Text> },
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
        </Section>
      )}

      {report && (report.file_ports.length > 0 || report.file) && <FileServiceView ports={report.file_ports} file={report.file} />}

      {report && report.replication_ports.length > 0 && (
        <Section
          title={`${report.replication_ports.length} replication port${report.replication_ports.length === 1 ? '' : 's'} (RCIP)`}
          summary={`${report.replication_ports.filter((p) => p.role === 'rcip').length} configured for Remote Copy over IP`}
        >
          <Text size="small" color="text-weak">
            Configured = carries a replication address; Available = link up, no replication configuration yet; Not cabled = no link. The
            array&apos;s node interconnect looks identical apart from its port type and is deliberately excluded.
          </Text>
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
              { property: 'address', header: 'IP address', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.address || <NoValue />}</Text> },
              { property: 'netmask', header: 'Netmask', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.netmask || <NoValue />}</Text> },
              { property: 'gateway', header: 'Gateway', render: (p: EthernetPort) => <Text size="small" style={mono}>{p.gateway || <NoValue />}</Text> },
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
        </Section>
      )}

      {report && hosts.length > 0 && (
        <Box gap="medium" flex={false}>
          {/* SPEC-014: the run's hosts, one table per OS. */}
          {(Object.keys(OS_LABEL) as DiscoveredHost['os'][])
            .filter((os) => inRun.some((h) => h.os === os))
            .map((os) => {
              const rows = inRun.filter((h) => h.os === os);
              const attention = rows.some(needsLook);
              return (
                // keyed: Section reads `open` once, so it opens by itself only while a host here needs a look
                <HostsTable
                  key={`${os}:${attention ? 'look' : 'fine'}`}
                  open={attention}
                  title={`Hosts in this run, ${os === 'unknown' ? 'OS not reported' : OS_LABEL[os]}`}
                  description="Servers the sheet's vCenter reports, the sheet declares, or a sheet host set names. A sheet host typed without a WWPN/IQN is looked up in vCenter and on the array; its serial number, WWPNs and IQN are filled in from what was found."
                  rows={rows}
                />
              );
            })}
          <HostsTable
            title="Other hosts on this array"
            description="Every other server the array can see: other tenants of a shared array. Listed so you know what not to touch; this run never changes them."
            rows={others}
            fold
          />
        </Box>
      )}
    </StepShell>
  );
}
