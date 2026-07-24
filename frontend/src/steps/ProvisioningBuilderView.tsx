import { Box, Button, Notification, Select, Spinner, Text, TextInput } from 'grommet';
import { useState } from 'react';
import {
  ExportRequest,
  getStorageObjects,
  ProvisioningBuilder,
  ProvisioningObjects,
  saveStorageBuilder,
} from '../api';
import { Section } from '../components';

// The operator dropdown-builder (ADR 0010 Stage 2): compose host-set membership + the exports
// (source volume/VV-set → target host/host-set → LUN) over discovered + to-be-created objects, and
// save them onto the run's intent so the plan preview/apply act on them.

type Opt = { label: string; value: string };
// An export row's source/target are encoded "kind:name" so the Select value carries the kind.
interface ExportRow { source: string; target: string; lun: string }

function decode(v: string): [string, string] {
  const i = v.indexOf(':');
  return [v.slice(0, i), v.slice(i + 1)];
}

function rowToExport(r: ExportRow): ExportRequest | null {
  if (!r.source || !r.target) return null;
  const [sk, sn] = decode(r.source);
  const [tk, tn] = decode(r.target);
  const n = parseInt(r.lun.trim(), 10);
  return {
    source_kind: sk as 'volume' | 'vvset', source_name: sn,
    target_kind: tk as 'host' | 'hostset', target_name: tn,
    lun: r.lun.trim() === '' || Number.isNaN(n) ? null : n,
  };
}

function exportToRow(e: ExportRequest): ExportRow {
  return { source: `${e.source_kind}:${e.source_name}`, target: `${e.target_kind}:${e.target_name}`, lun: e.lun == null ? '' : String(e.lun) };
}

const sourceOptions = (o: ProvisioningObjects): Opt[] => [
  ...o.new_volumes.map((n) => ({ label: `${n} — new volume`, value: `volume:${n}` })),
  ...o.new_vvsets.map((n) => ({ label: `${n} — new VV-set`, value: `vvset:${n}` })),
  ...o.existing_volumes.map((n) => ({ label: `${n} — existing volume`, value: `volume:${n}` })),
  ...o.existing_volume_sets.map((n) => ({ label: `${n} — existing VV-set`, value: `vvset:${n}` })),
];

const targetOptions = (o: ProvisioningObjects): Opt[] => [
  ...o.new_host_sets.map((n) => ({ label: `${n} — new host-set`, value: `hostset:${n}` })),
  ...o.existing_host_sets.map((n) => ({ label: `${n} — existing host-set`, value: `hostset:${n}` })),
  ...o.existing_hosts.map((n) => ({ label: `${n} — existing host`, value: `host:${n}` })),
  ...o.discovered_hosts.map((h) => ({ label: `${h.name} — discovered host`, value: `host:${h.name}` })),
];

const memberOptions = (o: ProvisioningObjects): Opt[] => {
  const seen = new Set<string>();
  const opts: Opt[] = [];
  o.discovered_hosts.forEach((h) => { if (!seen.has(h.name)) { seen.add(h.name); opts.push({ label: `${h.name} — ${h.status}`, value: h.name }); } });
  o.existing_hosts.forEach((n) => { if (!seen.has(n)) { seen.add(n); opts.push({ label: `${n} — existing host`, value: n }); } });
  return opts;
};

function ExportRowView({ row, sourceOpts, targetOpts, disabled, onChange, onRemove }: {
  row: ExportRow; sourceOpts: Opt[]; targetOpts: Opt[]; disabled: boolean;
  onChange: (r: ExportRow) => void; onRemove: () => void;
}) {
  return (
    <Box direction="row" gap="small" align="center" pad={{ vertical: 'xxsmall' }}>
      <Box width="280px" flex={false}>
        <Select size="small" placeholder="source — volume / VV-set" options={sourceOpts} labelKey="label"
          valueKey={{ key: 'value', reduce: true }} value={row.source} disabled={disabled}
          onChange={({ value }) => onChange({ ...row, source: value })} />
      </Box>
      <Text size="small">→</Text>
      <Box width="280px" flex={false}>
        <Select size="small" placeholder="target — host / host-set" options={targetOpts} labelKey="label"
          valueKey={{ key: 'value', reduce: true }} value={row.target} disabled={disabled}
          onChange={({ value }) => onChange({ ...row, target: value })} />
      </Box>
      <Box width="95px" flex={false}>
        <TextInput size="small" placeholder="LUN auto" value={row.lun} disabled={disabled}
          onChange={(e) => onChange({ ...row, lun: e.target.value })} />
      </Box>
      <Button size="small" plain label="remove" disabled={disabled} onClick={onRemove} />
    </Box>
  );
}

export function ProvisioningBuilderView({ runId, disabled = false }: { runId: string; disabled?: boolean }) {
  const [objects, setObjects] = useState<ProvisioningObjects | null>(null);
  const [members, setMembers] = useState<Record<string, string[]>>({});
  const [rows, setRows] = useState<ExportRow[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);

  const load = async () => {
    setError(null); setSaved(null); setBusy(true);
    try {
      const o = await getStorageObjects(runId);
      setObjects(o);
      const seed: Record<string, string[]> = {};
      o.host_sets.forEach((hs) => { seed[hs.name] = hs.members; });
      setMembers(seed);
      setRows(o.exports.length ? o.exports.map(exportToRow) : []);
    } catch (e: any) {
      setError(String(e.message ?? e));
    } finally {
      setBusy(false);
    }
  };

  const save = async () => {
    if (!objects) return;
    setError(null); setSaved(null); setBusy(true);
    try {
      const builder: ProvisioningBuilder = {
        host_sets: objects.host_sets.map((hs) => ({ name: hs.name, members: members[hs.name] ?? [] })),
        exports: rows.map(rowToExport).filter((x): x is ExportRequest => x !== null),
        vvsets: {}, // VV-set membership stays as the sheet defined it (empty => keep)
      };
      const comp = await saveStorageBuilder(runId, builder);
      const assigned = comp.host_sets.reduce((n, h) => n + h.members.length, 0);
      setSaved(`Saved — ${comp.exports.length} export(s), ${assigned} host-set member(s). Build the plan below to preview.`);
    } catch (e: any) {
      setError(String(e.message ?? e));
    } finally {
      setBusy(false);
    }
  };

  if (!objects) {
    return (
      <Section title="Compose the provisioning (dropdowns)">
        <Text size="small" color="text-weak">
          Pick host-set members and the exports (which volume / VV-set is presented to which host /
          host-set, at which LUN) from the discovered + to-be-created objects. Leave it untouched to use
          the default (every volume → every host-set, auto LUN).
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button primary size="small" label={busy ? 'Loading…' : 'Load objects'} disabled={disabled || busy} onClick={load} />
          {busy && <Spinner />}
        </Box>
        {error && <Notification status="critical" title="Could not load objects" message={error} onClose={() => setError(null)} />}
      </Section>
    );
  }

  const srcOpts = sourceOptions(objects);
  const tgtOpts = targetOptions(objects);
  const memOpts = memberOptions(objects);
  const busyOrDisabled = disabled || busy;

  return (
    <Section title="Compose the provisioning (dropdowns)">
      {objects.array_error && (
        <Notification status="warning" title="Array objects unavailable"
          message={`Couldn't read existing objects from the array (${objects.array_error}). You can still compose over the to-be-created + discovered objects.`} />
      )}

      <Text size="small" weight="bold">Host-set membership</Text>
      <Text size="xsmall" color="text-weak">Empty = all discovered hosts. Status shows fabric-login so a half-zoned host isn't picked blind.</Text>
      {objects.host_sets.length === 0 && <Text size="small" color="text-weak">No host sets in the sheet.</Text>}
      {objects.host_sets.map((hs) => (
        <Box key={hs.name} direction="row" gap="small" align="center" pad={{ vertical: 'xxsmall' }}>
          <Box width="200px" flex={false}><Text size="small">{hs.name}</Text></Box>
          <Box width="540px" flex={false}>
            <Select size="small" multiple closeOnChange={false} placeholder="all discovered hosts"
              options={memOpts} labelKey="label" valueKey={{ key: 'value', reduce: true }}
              value={members[hs.name] ?? []} disabled={busyOrDisabled}
              onChange={({ value }) => setMembers((m) => ({ ...m, [hs.name]: value }))} />
          </Box>
        </Box>
      ))}

      <Box margin={{ top: 'small' }}>
        <Text size="small" weight="bold">Exports (presentation)</Text>
        <Text size="xsmall" color="text-weak">LUN blank = auto-assign. No rows = the default (every volume → every host-set).</Text>
      </Box>
      {rows.map((row, i) => (
        <ExportRowView key={i} row={row} sourceOpts={srcOpts} targetOpts={tgtOpts} disabled={busyOrDisabled}
          onChange={(r) => setRows((rs) => rs.map((x, j) => (j === i ? r : x)))}
          onRemove={() => setRows((rs) => rs.filter((_, j) => j !== i))} />
      ))}
      <Button size="small" label="+ Add export row" disabled={busyOrDisabled} alignSelf="start"
        onClick={() => setRows((rs) => [...rs, { source: '', target: '', lun: '' }])} />

      <Box direction="row" gap="small" align="center" margin={{ top: 'small' }}>
        <Button primary size="small" label={busy ? 'Saving…' : 'Save composition'} disabled={busyOrDisabled} onClick={save} />
        <Button size="small" label="Reload" disabled={busyOrDisabled} onClick={load} />
        {busy && <Spinner />}
      </Box>
      {saved && <Notification status="normal" title="Composition saved" message={saved} onClose={() => setSaved(null)} />}
      {error && <Notification status="critical" title="Save failed" message={error} onClose={() => setError(null)} />}
    </Section>
  );
}
