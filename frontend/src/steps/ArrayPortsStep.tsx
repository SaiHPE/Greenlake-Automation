import { Box, Button, DataTable, Heading, Text } from 'grommet';
import { Network } from 'grommet-icons';
import { ReactNode, useEffect, useState } from 'react';
import {
  ArrayPorts,
  getArrayPorts,
  IscsiSection,
  IscsiVlanAction,
  IscsiVlanActionState,
  IscsiVlanRequest,
  PeerPortAction,
  PeerPortActionState,
  PeerPortIntent,
  PeerPortRequest,
  PeerSection,
  portsPreview,
  RunEvent,
  RunRecord,
} from '../api';
import { CodeBlock, EmptyState, Guidance, Section, mono } from '../ui/blocks';
import { InlineNotification, NotesList } from '../ui/primitives';
import { NoValue, RESULT, ResultWord, StatusIndicator } from '../ui/status';
import { useStepContext } from '../ui/StepContext';
import { FooterAction, StepShell, StepStatus } from '../ui/StepShell';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

// SPEC-024 R8 and SPEC-025 R8, the first slices (read, plan, the printed lines; no apply). One section per tab.
const PORTS_EVENTS = ['ports.previewed', 'ports.completed', 'ports.preview.failed'];
// A plan row's words are the shared ones (SPEC-030 R9): an address to add is Create, one on the array Already there.
const PLAN_STATE: Record<IscsiVlanActionState, ResultWord> = {
  create: RESULT.create,
  exists: RESULT.already_there,
  conflict: RESULT.conflict,
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);   // clipboard blocked: the text is on screen to select by hand
    }
  };
  return <Button size="small" label={copied ? 'Copied' : 'Copy'} onClick={copy} />;
}

function SheetRows({ rows }: { rows: IscsiVlanRequest[] }) {
  return (
    <Section title="What the sheet asks for" summary={`${rows.length} iSCSI address${rows.length === 1 ? '' : 'es'} on the iSCSI network tab`}>
      <DataTable
        columns={[
          { property: 'nsp', header: 'Port', render: (r: IscsiVlanRequest) => <Text size="small" style={mono}>{r.nsp}</Text> },
          { property: 'vlan_id', header: 'VLAN', render: (r: IscsiVlanRequest) => <Text size="small">{r.vlan_id}</Text> },
          { property: 'ip', header: 'Address', render: (r: IscsiVlanRequest) => <Text size="small" style={mono}>{r.ip} {r.netmask}</Text> },
          { property: 'gateway', header: 'Gateway', render: (r: IscsiVlanRequest) => (r.gateway ? <Text size="small" style={mono}>{r.gateway}</Text> : <NoValue />) },
        ]}
        data={rows}
        primaryKey={false}
        a11yTitle="The sheet's iSCSI network rows"
      />
    </Section>
  );
}

function PlanTables({ section }: { section: IscsiSection }) {
  const plan = section.plan;
  if (!plan) return null;
  const rows = plan.actions.map((action: IscsiVlanAction, i: number) => ({ ...action, request: section.requests[i] }));
  const adds = plan.actions.filter((a) => a.state === 'create');
  const lines = adds.flatMap((a) => a.cli.split('\n'));
  const count = (state: IscsiVlanActionState) => plan.actions.filter((a) => a.state === state).length;
  // Section reads `open` once: keyed, so each opens by itself only while it holds something to act on
  const toAct = adds.length > 0 || count('conflict') > 0;
  return (
    <Box gap="medium" flex={false}>
      <Section
        key={toAct ? 'plan-act' : 'plan-done'}
        title="The plan"
        summary={`${count('create')} to add · ${count('exists')} already there · ${count('conflict')} conflict${count('conflict') === 1 ? '' : 's'}`}
        open={toAct}
      >
        <DataTable
          columns={[
            { property: 'nsp', header: 'Port', render: (r) => <Text size="small" style={mono}>{r.nsp}</Text> },
            { property: 'vlan_id', header: 'VLAN', render: (r) => <Text size="small">{r.vlan_id}</Text> },
            { property: 'ip', header: 'Address', render: (r) => (r.request ? <Text size="small" style={mono}>{r.request.ip}</Text> : <NoValue />) },
            { property: 'gateway', header: 'Gateway', render: (r) => (r.request?.gateway ? <Text size="small" style={mono}>{r.request.gateway}</Text> : <NoValue />) },
            { property: 'state', header: 'Plan', render: (r) => <StatusIndicator state={PLAN_STATE[r.state].state} label={PLAN_STATE[r.state].label} /> },
            { property: 'reason', header: 'Why', render: (r) => <Text size="small">{r.reason}</Text> },
          ]}
          data={rows}
          primaryKey={false}
          a11yTitle="The plan: one row per sheet row, with what the tool would do and why"
        />
      </Section>
      {lines.length > 0 && (
        <Section title="The array's command lines" summary={`${lines.length} line${lines.length === 1 ? '' : 's'}, each with -vlan`} right={<CopyButton text={lines.join('\n') + '\n'} />}>
          <Text size="small" color="text-weak">
            The tool does not send these yet. Pasted on the array&apos;s CLI they add the addresses above. Each line carries -vlan: without it
            the line would change the port&apos;s untagged address and cut off the hosts logged in on it.
          </Text>
          <CodeBlock lines={lines} label="Command lines for the array" />
        </Section>
      )}
      {plan.switch_handoff.length > 0 && (
        <Section
          key={adds.length ? 'handoff-act' : 'handoff-done'}
          title="For the network team"
          summary={`${plan.switch_handoff.length} switch port${plan.switch_handoff.length === 1 ? '' : 's'}`}
          right={<CopyButton text={plan.switch_handoff.join('\n') + '\n'} />}
          open={adds.length > 0}
        >
          <Text size="small" color="text-weak">The tool does not change any switch. Send these to the network team.</Text>
          <CodeBlock lines={plan.switch_handoff} label="Sentences for the network team" />
        </Section>
      )}
    </Box>
  );
}

function download(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// A port to set to peer mode is Create, one already in peer mode Already there (SPEC-030 R9).
const PEER_STATE: Record<PeerPortActionState, ResultWord> = {
  create: RESULT.create,
  exists: RESULT.already_there,
  conflict: RESULT.conflict,
};

const lines = (text?: string) => (text ?? '').split('\n').filter((line) => line !== '');

/** A block of lines to paste, with Copy and Download .txt; the comment lines stay in the copy only. */
function PasteBlock({ title, text, file, open, children }: { title: string; text: string; file: string; open?: boolean; children?: ReactNode }) {
  const shown = lines(text).filter((line) => !line.startsWith('# Peer ports on') && !line.startsWith('# Undo') && !line.startsWith('# Review'));
  const count = shown.filter((line) => !line.startsWith('#')).length;
  return (
    <Section
      title={title}
      summary={`${count} line${count === 1 ? '' : 's'}`}
      right={<Box direction="row" gap="xsmall"><CopyButton text={text} /><Button size="small" label="Download .txt" onClick={() => download(file, text)} /></Box>}
      open={open}
    >
      {children}
      <CodeBlock lines={shown} label={title} />
    </Section>
  );
}

/** SPEC-025 R8, first slice: the peer-port section. The plan, the command set and its removal set for
 *  a consultant to paste, and after the paste the judgement of the next read (R4). No tick, no apply. */
function PeerPortsPanel({ intent, section, error }: { intent: PeerPortIntent | null; section: PeerSection | null; error: string | null }) {
  if (!intent) {
    return <Text size="small" color="text-weak">The sheet asks for no peer ports. Nothing to set up here.</Text>;
  }
  const plan = section?.plan;
  const result = section?.result ?? null;
  const sets = plan?.actions.filter((a) => a.state === 'create').length ?? 0;
  const ports = section?.view?.ports ?? {};
  return (
    <Box gap="small" flex={false}>
      <Section title="What the sheet asks for" summary={`${intent.ports.length} port${intent.ports.length === 1 ? '' : 's'} on the Peer ports tab`}>
        <DataTable
          columns={[
            { property: 'nsp', header: 'Port', render: (r: PeerPortRequest) => <Text size="small" style={mono}>{r.nsp}</Text> },
            {
              property: 'source_wwpns', header: 'Source array ports to zone',
              render: (r: PeerPortRequest) => (r.source_wwpns.length ? <Text size="small" style={mono}>{r.source_wwpns.join(', ')}</Text> : <NoValue />),
            },
          ]}
          data={intent.ports}
          primaryKey={false}
          a11yTitle="The sheet's Peer ports rows"
        />
      </Section>
      {error && <Text size="small" color="text-weak">Not read: nothing was planned for the peer ports.</Text>}
      {!error && !plan && <Text size="small" color="text-weak">Not read yet.</Text>}
      {result && (
        // the judgement of the read after the paste: a finding of this section, said next to its table
        <Box gap="xxsmall" flex={false}>
          <StatusIndicator
            state={result.error ? 'failed' : 'complete'}
            label={result.error ? 'The read after the paste does not match the plan' : 'The read after the paste'}
          />
          <Text size="small">
            <NotesList notes={result.sentences} />
          </Text>
        </Box>
      )}
      {plan && !error && plan.blockers.length > 0 && <InlineNotification tone="critical" title="Findings to resolve" message={<NotesList notes={plan.blockers} />} />}
      {plan && !error && (
        <DataTable
          columns={[
            { property: 'nsp', header: 'Port', render: (a: PeerPortAction) => <Text size="small" style={mono}>{a.nsp}</Text> },
            {
              property: 'now', header: 'Now',
              render: (a: PeerPortAction) => (ports[a.nsp] ? <Text size="small">{`${ports[a.nsp].type} · ${ports[a.nsp].protocol} · ${ports[a.nsp].state}`}</Text> : <NoValue />),
            },
            {
              property: 'after', header: 'After',
              render: (a: PeerPortAction) => (a.state === 'conflict' ? <NoValue /> : <Text size="small">{a.state === 'create' ? 'peer, point' : 'peer'}</Text>),
            },
            { property: 'state', header: 'Plan', render: (a: PeerPortAction) => <StatusIndicator state={PEER_STATE[a.state].state} label={PEER_STATE[a.state].label} /> },
            { property: 'reason', header: 'Why', render: (a: PeerPortAction) => <Text size="small">{a.reason}</Text> },
          ]}
          data={plan.actions}
          primaryKey={false}
          a11yTitle="The peer-port plan: one row per sheet row, the port now and after, and why"
        />
      )}
      {plan && !error && sets > 0 && !plan.blockers.length && (
        <Box gap="small" flex={false}>
          <PasteBlock title="Commands to paste on the array" text={section?.commands_text ?? ''} file="peer-ports-commands.txt" open>
            <Text size="small" color="text-weak">
              The tool does not send these. Each port goes offline first, then into peer mode; the plan offers only ports with no login and
              no export. Keep the removal set below before you paste.
            </Text>
          </PasteBlock>
          <PasteBlock title="Removal set, to keep before you paste" text={section?.removals_text ?? ''} file="peer-ports-removal.txt">
            <Text size="small" color="text-weak">
              Puts each port back in the mode it has now. Remove the SAN team&apos;s peer-port zones and any migration that uses these ports
              first. The tool never runs these.
            </Text>
          </PasteBlock>
        </Box>
      )}
      {result && result.removals.length > 0 && (
        <PasteBlock title="Removal set for what changed" text={section?.result_removals_text ?? ''} file="peer-ports-removal.txt">
          <Text size="small" color="text-weak">Only the ports the read shows changed, last first. The tool never runs these.</Text>
        </PasteBlock>
      )}
    </Box>
  );
}

export function ArrayPortsStep({ runId, run, events, onDone }: Props) {
  const { nextTitle } = useStepContext();
  const [ports, setPorts] = useState<ArrayPorts | null>(null);
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running' && run.current_phase === 'STORAGE_PORTS';

  const latest = [...events].reverse().find((event) => PORTS_EVENTS.includes(event.event_type));
  const failed = latest?.event_type === 'ports.preview.failed';
  const section = (latest?.data?.iscsi as IscsiSection | null | undefined) ?? null;
  const peer = (latest?.data?.peer as PeerSection | null | undefined) ?? null;
  const rows = ports?.iscsi_network ?? [];
  const peerIntent = ports?.peer_ports ?? null;
  // An event from before the peer section kept no `error`: a failed read then had no plan.
  const iscsiError = section?.error ?? (failed && section && !section.plan ? latest?.message ?? null : null);
  const peerError = peer?.error ?? null;

  // The rows, and whether each plan last shown is still the one the server holds: fetched again
  // after each read, because a read, a restart or a sheet change withdraws a plan (LESSONS 6).
  useEffect(() => {
    getArrayPorts(runId)
      .then(setPorts)
      .catch((exc: any) => setError(String(exc.message ?? exc)));
  }, [runId, latest?.event_id]);

  // R8: with nothing on either tab the step reads nothing and is complete; record that once.
  useEffect(() => {
    if (ports && ports.iscsi_network.length === 0 && !ports.peer_ports && !latest) {
      portsPreview(runId).catch((exc: any) => setError(String(exc.message ?? exc)));
    }
  }, [ports, latest, runId]);

  const read = async () => {
    setError(null);
    try {
      await portsPreview(runId);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };
  const plan = section?.plan;
  const adds = plan?.actions.filter((a) => a.state === 'create').length ?? 0;
  const conflicts = plan?.actions.filter((a) => a.state === 'conflict').length ?? 0;
  const peerPlan = peer?.plan;
  const sets = peerPlan?.actions.filter((a) => a.state === 'create').length ?? 0;
  const peerFindings = (peerPlan?.blockers.length ?? 0) + (peer?.result?.error ? 1 : 0);
  const nothing = ports !== null && rows.length === 0 && !peerIntent;
  const anyPlan = Boolean(plan || peerPlan);
  const stale = Boolean(plan) && ports !== null && !ports.iscsi_plan_held && rows.length > 0;
  const peerStale = Boolean(peerPlan) && ports !== null && !ports.peer_plan_held && Boolean(peerIntent);
  const hhmm = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '');

  const readAction: FooterAction = {
    label: running ? 'Reading' : anyPlan || failed ? 'Read the array again' : 'Read the array and plan',
    busy: running,
    onClick: read,
  };
  const next: FooterAction = { label: nextTitle ? `Continue to ${nextTitle}` : 'Continue', onClick: onDone };
  const open = [adds ? `${adds} to add` : '', sets ? `${sets} port${sets === 1 ? '' : 's'} to set` : ''].filter(Boolean);
  const findings = conflicts + peerFindings;
  const planTitle =
    open.length || findings ? `Plan ready: ${[...open, `${findings} conflict${findings === 1 ? '' : 's'}`].join(', ')}` : 'Set up: all in place';
  const time = hhmm(latest?.created_at);

  // One status line for both sections (SPEC-030 R2): a read that failed, then the plan, then all in place.
  const readErrors = [rows.length > 0 ? iscsiError : null, peerError].filter((e): e is string => Boolean(e));
  const inPlace = [
    plan && !iscsiError ? 'iSCSI address' : '',
    peerPlan && !peerError ? 'peer port' : '',
  ].filter(Boolean);
  let status: StepStatus | undefined;
  if (readErrors.length) {
    status = {
      state: 'failed',
      title: rows.length > 0 && iscsiError ? 'The array could not be read' : 'The peer ports could not be read',
      message: <NotesList notes={readErrors} />,
      time,
    };
  } else if (anyPlan && (open.length || findings)) {
    status = {
      state: 'action_required',
      title: planTitle,
      message: findings
        ? 'Resolve each conflict on the sheet or on the array, never with the tool, then read the array again.'
        : 'The tool does not set these up yet: paste the commands on the array\'s CLI, then read the array again.',
      time,
    };
  } else if (anyPlan) {
    status = {
      state: 'complete',
      title: planTitle,
      message: `Every ${inPlace.join(' and ')} the sheet asks for is in place on ${plan?.array || run?.serial_number || 'the array'}.`,
      time,
    };
  }
  const notes = [...(plan?.notes ?? []), ...(peerPlan && !peerError ? peerPlan.notes : [])];
  const stalePlans = [stale ? 'the iSCSI plan' : '', peerStale ? 'the peer-port plan' : ''].filter(Boolean);
  const staleNotice = stalePlans.length ? (
    <InlineNotification
      tone="warning"
      title="This plan is from an earlier read"
      message={`The app restarted or the sheet changed since ${stalePlans.join(' and ')} was made. Read the array again before you use its commands.`}
    />
  ) : undefined;

  return (
    <StepShell
      title="Array ports"
      description="What the sheet asks of this array's ports, planned against what the array has, without changing anything."
      error={error}
      onDismissError={() => setError(null)}
      status={status}
      notes={notes}
      staleNotice={staleNotice}
      buttons={nothing || (!anyPlan && !failed) ? [] : failed && !anyPlan ? [next] : [readAction]}
      primary={nothing || (anyPlan && !failed) ? next : readAction}
      guidance={
        <Guidance
          items={[
            {
              title: 'What is read',
              body: "The array's ports, the addresses on its iSCSI ports and their VLANs, its management, replication and file addresses, and for peer ports each port's connection mode, logins and exports. Read-only, over SSH: reading the array changes nothing.",
            },
            {
              title: 'Why before zoning',
              body: 'An iSCSI host on a VLAN logs in only once the array has an address on that VLAN, and a peer port has its own WWPN once it is set. The SAN zoning step works from both.',
            },
            {
              title: 'The switch',
              body: 'The tool never changes a switch. The network team gets one sentence per iSCSI port; the SAN team gets the peer-port zones as a command set in the SAN zoning step.',
            },
          ]}
        />
      }
    >
      {nothing && (
        <EmptyState icon={<Network size="large" color="icon-weak" />} title="Nothing to set up here">
          The sheet asks for no iSCSI VLANs and no peer ports. Nothing to set up here.
        </EmptyState>
      )}
      {!nothing && ports !== null && !anyPlan && !failed && (
        <EmptyState icon={<Network size="large" color="icon-weak" />} title="Not read yet">
          Read the array and plan reads the array over SSH, read-only, and compares it with what the sheet asks for below.
        </EmptyState>
      )}

      {!nothing && ports !== null && (
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">iSCSI addresses on VLANs</Heading>
          {rows.length === 0 && <Text size="small" color="text-weak">The sheet asks for no iSCSI VLANs. Nothing to set up here.</Text>}
          {rows.length > 0 && <SheetRows rows={rows} />}
          {rows.length > 0 && iscsiError && <Text size="small" color="text-weak">Not read: nothing was planned for the iSCSI addresses.</Text>}
          {section && !iscsiError && <PlanTables section={section} />}
        </Box>
      )}

      {!nothing && ports !== null && (
        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Peer ports</Heading>
          <PeerPortsPanel intent={peerIntent} section={peer} error={peerError} />
        </Box>
      )}
    </StepShell>
  );
}
