import { Box, Text, TextInput } from 'grommet';
import { useState } from 'react';
import { AliasedWwpn, FabricZonePlan, ZoningPlan } from '../api';
import { Section } from '../components';

// Assemble the read-only command preview for one fabric from the plan + the operator's chosen aliases.
// Mirrors zoning_plan.render_commands (ADR 0004); the tool never RUNS these.
function renderCommands(fab: FabricZonePlan, aliases: Record<string, string>): string[] {
  const byWwpn: Record<string, AliasedWwpn> = {};
  [...fab.hosts, ...fab.array_ports].forEach((w) => { byWwpn[w.wwpn] = w; });
  const aliasFor = (wwpn: string) => (aliases[wwpn] ?? byWwpn[wwpn]?.suggested_alias ?? '').trim();

  const cmds: string[] = [];
  const emitted = new Set<string>();
  [...fab.hosts, ...fab.array_ports].forEach((w) => {
    const name = aliasFor(w.wwpn);
    if (name && !w.existing_aliases.includes(name) && !emitted.has(name)) {
      cmds.push(`alicreate "${name}","${w.display}"`);
      emitted.add(name);
    }
  });
  const zones: string[] = [];
  fab.pairs.forEach(([host, arr]) => {
    const ha = aliasFor(host);
    const aa = aliasFor(arr);
    if (!ha || !aa) return;
    const zone = `${ha}_${aa}`;
    if (zones.includes(zone)) return; // dedupe: colliding aliases must not double a zone
    zones.push(zone);
    cmds.push(`zonecreate "${zone}","${ha};${aa}"`);
  });
  if (zones.length > 0 && fab.active_cfg) {
    cmds.push(`cfgadd "${fab.active_cfg}","${zones.join(';')}"`);
    cmds.push(`cfgenable ${fab.active_cfg}`);
  }
  return cmds;
}

function AliasRow({ w, value, onChange }: { w: AliasedWwpn; value: string; onChange: (v: string) => void }) {
  const label = w.role === 'array' ? `array ${w.nsp}` : `host ${w.host_name}`;
  const others = w.existing_aliases.filter((a) => a !== value);
  return (
    <Box direction="row" gap="small" align="center" pad={{ vertical: 'xxsmall' }}>
      <Box width="140px" flex={false}><Text size="small">{label}</Text></Box>
      <Box width="215px" flex={false}><Text size="small" style={{ fontFamily: 'monospace' }}>{w.display}</Text></Box>
      <Box width="330px" flex={false}>
        <TextInput size="small" value={value} placeholder="type an alias name…" onChange={(e) => onChange(e.target.value)} />
      </Box>
      {others.length > 0 && <Text size="xsmall" color="text-weak">other aliases: {others.join(', ')}</Text>}
    </Box>
  );
}

export function ZoningPlanView({ plan }: { plan: ZoningPlan }) {
  // Seed the editable aliases from each WWPN's suggested (convention-matching) alias.
  const [aliases, setAliases] = useState<Record<string, string>>(() => {
    const seed: Record<string, string> = {};
    plan.fabrics.forEach((f) => [...f.hosts, ...f.array_ports].forEach((w) => { seed[w.wwpn] = w.suggested_alias; }));
    return seed;
  });
  const set = (wwpn: string, v: string) => setAliases((a) => ({ ...a, [wwpn]: v }));

  return (
    <Box gap="medium">
      <Text size="small" color="text-weak">
        The tool found the WWPNs, their fabric, and the single-initiator-single-target pairing. Name each
        alias — existing aliases are pre-filled and reused, never re-created. The commands are a{' '}
        <b>read-only preview</b> for the SAN team; the tool never writes to the switch.
      </Text>
      {plan.fabrics.map((fab) => {
        const rows = [...fab.hosts, ...fab.array_ports];
        const cmds = renderCommands(fab, aliases);
        return (
          <Section key={fab.fabric} title={`${fab.fabric} — ${fab.switch_host} (cfg ${fab.active_cfg || '—'})`}>
            {rows.length === 0
              ? <Text size="small" color="text-weak">No host or array ports online on this fabric.</Text>
              : rows.map((w) => <AliasRow key={w.wwpn} w={w} value={aliases[w.wwpn] ?? ''} onChange={(v) => set(w.wwpn, v)} />)}
            {cmds.length > 0 && (
              <Box background="background-contrast" round="xsmall" pad="small" margin={{ top: 'small' }}>
                {cmds.map((c, i) => <Text key={i} size="small" style={{ fontFamily: 'monospace' }}>{c}</Text>)}
              </Box>
            )}
          </Section>
        );
      })}
      {plan.offline_hosts.length > 0 && (
        <Section title={`Offline — cable + power the host, then re-run (${plan.offline_hosts.length})`}>
          {plan.offline_hosts.map((h, i) => <Text key={i} size="small" color="status-warning">{h}</Text>)}
        </Section>
      )}
      {plan.notes.map((n, i) => <Text key={i} size="small" color="text-weak">• {n}</Text>)}
    </Box>
  );
}
