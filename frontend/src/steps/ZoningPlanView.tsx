import { Box, Button, CheckBox, DataTable, Heading, Text, TextInput } from 'grommet';
import { StatusGood } from 'grommet-icons';
import { ComponentProps, ReactNode, useMemo, useState } from 'react';
import { AliasedWwpn, FabricZonePlan, ZoningPlan, ZoningRenderResult, renderZoningCommands } from '../api';
import { DoneList, Section } from '../ui/blocks';
import { InlineNotification, NotesList, Surface, TableSummary } from '../ui/primitives';
import { NoValue, RESULT, ResultWord, StatusIndicator } from '../ui/status';

// ADR 0004 + ADR 0012: the zoning screen, redesigned after the 2026-09-12 live test
// (docs/ux/ZONING-REDESIGN.md), then calmed by SPEC-030 (BL-59 P8a). One step, in parts:
//   A  Fabrics          — what each declared switch is, and which array ports sit on it   } folded: What the
//   B  Current zoning   — one row per host HBA port: what it can reach today, and by which zone } switches hold
//   C  Design new zones — only HBA ports that need zones; array ports grouped by controller node  } Draft zones,
//   D  Names            — only the WWPNs that take part in a selected new zone             } until generated
//   E  Command set      — the deliverable, per fabric; activation kept apart               (Hand off)
// The data is exactly what the backend plan carries; commands are rendered by POST /zoning/render so
// the grammar has one implementation. The tool has no switch write path at any layer.

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };
const pairKey = (host: string, arr: string) => `${host}|${arr}`;

// ---------------------------------------------------------------- vocabulary (docs/ux/ZONING-REDESIGN §3)

const fabricTitle = (fab: FabricZonePlan) => `Fabric ${fab.fabric} (${fab.fabric === 'F1' ? 'odd' : 'even'})`;

const SOURCE_LABEL: Record<string, string> = {
  vcenter: 'from vCenter',
  sheet: 'from the sheet (Hosts tab)',
  array: 'array host object',
  switch: 'from the fabric name server',
};

function hostName(w: AliasedWwpn): string {
  // QLogic HBAs advertise no HN: on the fabric — the WWPN is the only identity we have.
  return w.host_name || w.display;
}

function hostSource(w: AliasedWwpn): string {
  if (w.host_source === 'array' && !w.host_name) return 'array login only — no host object yet';
  return SOURCE_LABEL[w.host_source] ?? '';
}

// Array target WWPNs on this family encode the port: 2N:SP:00:02:AC:<system> — node N, slot S, port P.
function wwpnTitle(w: AliasedWwpn): string {
  if (w.role === 'array') return `Array port ${w.nsp}${w.node != null ? ` on controller node ${w.node}` : ''} — WWPN ${w.display}`;
  return `HBA port WWPN ${w.display}`;
}

// Brocade FOS zone-object names (mirrors zoning_plan.fos_name_problem / fos_name_warning — the
// backend stays authoritative; this only lets the operator see a problem before clicking Generate).
const FOS_NAME = /^[A-Za-z0-9][A-Za-z0-9_\-$^]*$/;
const FOS_ENHANCED = /^[0-9]|[-$^]/;
function aliasProblem(name: string): { tone: 'critical' | 'warning' | 'ok'; text: string } {
  if (!name) return { tone: 'critical', text: 'Enter a name' };
  if (name.length > 64) return { tone: 'critical', text: `${name.length} characters — FOS allows 64` };
  if (!FOS_NAME.test(name)) return { tone: 'critical', text: 'Letters, digits and _ only' };
  if (FOS_ENHANCED.test(name)) return { tone: 'warning', text: 'Needs FOS 8.1.0+ on every switch (- $ ^ or leading digit)' };
  return { tone: 'ok', text: 'Valid' };
}

// SPEC-010 R3: mirrors zoning_plan.fos_name_suggestion — the closest name FOS accepts.
function aliasSuggestion(name: string): string {
  if (name && aliasProblem(name).tone !== 'critical') return name;
  let folded = (name || '').replace(/[^A-Za-z0-9_\-$^]+/g, '_').replace(/^[_\-$^]+|[_\-$^]+$/g, '');
  if (!folded || !/^[A-Za-z0-9]/.test(folded)) folded = `a${folded}`;
  return folded.slice(0, 64);
}

// BL-09: the name clashes zoning_plan.render_commands skips a pair for, said before Generate.
function nameClashes(plan: ZoningPlan, selectedPairs: [string, string][], aliases: Record<string, string>) {
  const port: Record<string, string> = {};   // wwpn -> why its new alias cannot be created
  const zone: Record<string, string> = {};   // pairKey -> why its zone cannot be created
  const chosen = new Set(selectedPairs.map(([h, a]) => pairKey(h, a)));
  plan.fabrics.forEach((fab) => {
    const defined = new Set(fab.defined_names ?? []);
    const entry = new Map([...fab.hosts, ...fab.array_ports].map((w) => [w.wwpn, w]));
    const label = (wwpn: string) => { const w = entry.get(wwpn); return w?.role === 'array' ? `array port ${w.nsp}` : (w ? hostName(w) : wwpn); };
    const pairs = fab.pairs.filter(([h, a]) => chosen.has(pairKey(h, a)));
    const typedFor = new Map<string, string[]>();
    new Set(pairs.flat()).forEach((wwpn) => {
      const name = aliases[wwpn] ?? '';
      if (!name || entry.get(wwpn)?.existing_aliases.includes(name)) return;
      if (defined.has(name)) port[wwpn] = 'Already on the switch for another device';
      else typedFor.set(name, [...(typedFor.get(name) ?? []), wwpn]);
    });
    typedFor.forEach((wwpns) => {
      if (wwpns.length > 1) wwpns.forEach((w) => { port[w] = `Same name as ${wwpns.filter((o) => o !== w).map(label).join(', ')}`; });
    });
    pairs.forEach(([h, a]) => {
      const name = `${aliases[h] ?? ''}_${aliases[a] ?? ''}`;
      if (defined.has(name)) zone[pairKey(h, a)] = `zone ${name} already exists on the switch`;
      else if (name.length > 64) zone[pairKey(h, a)] = `zone ${name} is ${name.length} characters — FOS allows 64; shorten an alias`;
    });
  });
  return { port, zone };
}

function download(filename: string, text: string) {
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ---------------------------------------------------------------- status (colour + icon + shape + text)

type PairState = 'zoned' | 'partial' | 'unzoned' | 'offline' | 'new';

const PAIR: Record<PairState, ResultWord> = {
  zoned: RESULT.zoned,
  partial: RESULT.partly_zoned,
  unzoned: RESULT.not_zoned,
  offline: RESULT.not_on_fabric,
  new: { state: 'not_started', label: 'New zone' },
};

/** A block inside the folded section: its heading is an h3 under the section's h2. */
function SubPanel({ title, description, right, children }: { title: string; description: ReactNode; right?: ReactNode; children: ReactNode }) {
  return (
    <Box gap="small" flex={false}>
      <Box direction="row" justify="between" align="center" gap="small" wrap>
        <Heading level={3} size="xsmall" weight={500} margin="none">
          {title}
        </Heading>
        {right}
      </Box>
      <Text size="small" color="text-weak">
        {description}
      </Text>
      {children}
    </Box>
  );
}

// ---------------------------------------------------------------- A. Fabrics

function FabricOverview({ plan }: { plan: ZoningPlan }) {
  return (
    <SubPanel title="Fabrics" description="The two switches named on the sheet, read read-only. Every array port is cabled to exactly one of them; a zone only works inside one fabric.">
      <Box gap="small">
        {plan.fabrics.map((fab) => (
          <Box key={fab.fabric} gap="xxsmall" pad={{ bottom: 'xsmall' }} border={{ side: 'bottom', color: 'border' }}>
            <Box direction="row" gap="small" align="baseline" wrap>
              <Text size="medium" weight={600}>{fabricTitle(fab)}</Text>
              <Text size="small">switch <Text size="small" style={mono}>{fab.switch_host}</Text>{fab.switch_name ? ` ${fab.switch_name}` : ''}</Text>
              {fab.fabric_name && (
                <Text size="small" color="text-weak">
                  fabric {fab.fabric_name}{fab.switch_count ? ` · ${fab.switch_count} switch${fab.switch_count === 1 ? '' : 'es'}` : ''}
                </Text>
              )}
              <Text size="small">active cfg <Text size="small" weight={600} style={mono}>{fab.active_cfg || 'not read'}</Text></Text>
            </Box>
            <Text size="small" color="text-weak">
              {fab.array_ports.length === 0
                ? 'No array port is online on this fabric.'
                : 'Array ports here: ' + fab.array_ports.map((p) => `${p.nsp}${p.node != null ? ` (node ${p.node})` : ''}`).join(' · ')}
            </Text>
          </Box>
        ))}
      </Box>
    </SubPanel>
  );
}

// ---------------------------------------------------------------- B. Current zoning

interface HbaRow {
  key: string;
  host: string;
  meta: string;              // "ESXi 8.0.2 · from vCenter"
  wwpn: string;
  fabric: string;            // "F1" | "F2" | ""
  placed: string;            // remote switch name or ""
  zonedPorts: string[];      // n:s:p already zoned to this HBA on this fabric
  totalPorts: number;
  zones: string[];
  state: PairState;
}

function hbaRows(plan: ZoningPlan): HbaRow[] {
  const rows: HbaRow[] = [];
  plan.fabrics.forEach((fab) => {
    const zoned = new Set(fab.already_zoned.map(([h, a]) => pairKey(h, a)));
    fab.hosts.forEach((h) => {
      const zonedPorts: string[] = [];
      const zones = new Set<string>();
      fab.array_ports.forEach((p) => {
        if (zoned.has(pairKey(h.wwpn, p.wwpn))) {
          zonedPorts.push(p.nsp || p.display);
          (fab.zone_names?.[pairKey(h.wwpn, p.wwpn)] ?? []).forEach((z) => zones.add(z));
        }
      });
      const total = fab.array_ports.length;
      const state: PairState = zonedPorts.length === 0 ? 'unzoned' : zonedPorts.length < total ? 'partial' : 'zoned';
      rows.push({
        key: `${fab.fabric}|${h.wwpn}`, host: hostName(h),
        meta: [h.os, hostSource(h)].filter(Boolean).join(' · '),
        wwpn: h.display, fabric: fab.fabric, placed: h.placed_on_switch ?? '',
        zonedPorts, totalPorts: total, zones: [...zones], state,
      });
    });
  });
  plan.offline_hosts.forEach((entry) => {
    const m = /^(.*) \(([0-9a-f:]+)\)$/i.exec(entry);
    rows.push({
      key: `off|${entry}`, host: m ? m[1] : entry, meta: '', wwpn: m ? m[2] : '', fabric: '', placed: '',
      zonedPorts: [], totalPorts: 0, zones: [], state: 'offline',
    });
  });
  rows.sort((a, b) => a.host.localeCompare(b.host) || a.fabric.localeCompare(b.fabric) || a.wwpn.localeCompare(b.wwpn));
  return rows;
}

function exportText(plan: ZoningPlan, rows: HbaRow[]): string {
  const lines = ['Current zoning — as observed from the array and both fabric switches (read-only)', ''];
  plan.fabrics.forEach((fab) => {
    lines.push(`${fabricTitle(fab)}: switch ${fab.switch_host} ${fab.switch_name ?? ''} · fabric ${fab.fabric_name || '-'} · active cfg ${fab.active_cfg || '-'}`);
    lines.push('  array ports: ' + fab.array_ports.map((p) => `${p.nsp} ${p.display}`).join(', '));
  });
  lines.push('', 'Host | HBA port | Fabric | Zoned to array ports | Zone(s) | Status');
  rows.forEach((r) => lines.push([
    r.host, r.wwpn, r.fabric ? `${r.fabric}${r.placed ? ` (on ${r.placed})` : ''}` : '-',
    r.zonedPorts.join(' ') || '-', r.zones.join(' ') || '-', PAIR[r.state].label,
  ].join(' | ')));
  return lines.join('\n') + '\n';
}

function CurrentZoningTable({ plan }: { plan: ZoningPlan }) {
  const rows = useMemo(() => hbaRows(plan), [plan]);
  const needWork = rows.filter((r) => r.state !== 'zoned');
  const [onlyNeeding, setOnlyNeeding] = useState(needWork.length > 0 && needWork.length < rows.length);
  const shown = onlyNeeding ? needWork : rows;
  const hosts = new Set(rows.map((r) => r.host));
  const fullyZonedHosts = [...hosts].filter((h) => rows.filter((r) => r.host === h).every((r) => r.state === 'zoned'));

  return (
    <SubPanel
      title="Current zoning"
      description="One row per host HBA port. “Zoned” is read from the array (a login is only possible through an effective zone) and the zone name from the switch's effective configuration."
      right={<Button size="small" label="Export .txt" onClick={() => download('current-zoning.txt', exportText(plan, rows))} />}
    >
      {rows.length === 0 ? (
        <Text size="small" color="text-weak">No host HBA port is online on either fabric.</Text>
      ) : (
        <>
          <DataTable
            primaryKey="key"
            data={shown}
            a11yTitle="Current zoning: one row per host HBA port with the array ports it is zoned to"
            columns={[
              {
                property: 'host', header: 'Host', pin: true,
                render: (r: HbaRow) => (
                  <Box>
                    <Text size="small" weight={600}>{r.host}</Text>
                    {r.meta && <Text size="xsmall" color="text-weak">{r.meta}</Text>}
                  </Box>
                ),
              },
              { property: 'wwpn', header: 'HBA port (WWPN)', render: (r: HbaRow) => (r.wwpn ? <Text size="small" style={mono}>{r.wwpn}</Text> : <NoValue />) },
              {
                property: 'fabric', header: 'Fabric',
                render: (r: HbaRow) => (
                  <Box>
                    {r.fabric ? <Text size="small">{r.fabric}</Text> : <NoValue />}
                    {r.placed && <Text size="xsmall" color="text-weak">on {r.placed} via ISL</Text>}
                  </Box>
                ),
              },
              {
                property: 'zonedPorts', header: 'Zoned to array ports',
                render: (r: HbaRow) => (r.zonedPorts.length ? <Text size="small">{r.zonedPorts.join(', ')}</Text> : <NoValue />),
              },
              { property: 'zones', header: 'Zone', render: (r: HbaRow) => (r.zones.length ? <Text size="small" style={mono}>{r.zones.join(', ')}</Text> : <NoValue />) },
              {
                property: 'state', header: 'Status',
                render: (r: HbaRow) => (
                  <StatusIndicator
                    state={PAIR[r.state].state}
                    label={PAIR[r.state].label}
                    detail={r.state === 'partial' ? `${r.zonedPorts.length} of ${r.totalPorts} ports` : undefined}
                  />
                ),
              },
            ]}
          />
          <Box direction="row" justify="between" align="center" wrap gap="small">
            <TableSummary>
              {fullyZonedHosts.length} of {hosts.size} hosts zoned on every fabric they are cabled to ·{' '}
              {needWork.filter((r) => r.state !== 'offline').length} HBA port(s) need zones ·{' '}
              {needWork.filter((r) => r.state === 'offline').length} not on any fabric
            </TableSummary>
            {needWork.length > 0 && needWork.length < rows.length && (
              <CheckBox label="Show only HBA ports that need zones" checked={onlyNeeding} onChange={(e) => setOnlyNeeding(e.target.checked)} />
            )}
          </Box>
        </>
      )}
    </SubPanel>
  );
}

// ---------------------------------------------------------------- C. Design new zones

function ZoneDesigner({
  plan, selected, toggle,
}: {
  plan: ZoningPlan;
  selected: Record<string, boolean>;
  toggle: (key: string, on: boolean) => void;
}) {
  const fabricsWithWork = plan.fabrics.filter((fab) => {
    const zoned = new Set(fab.already_zoned.map(([h, a]) => pairKey(h, a)));
    return fab.pairs.some(([h, a]) => !zoned.has(pairKey(h, a)));
  });
  if (fabricsWithWork.length === 0) {
    return (
      <Surface title="Design new zones">
        <Text size="small" color="text-weak">Every host HBA port online on a fabric is already zoned to every array port there. Nothing to design.</Text>
      </Surface>
    );
  }
  return (
    <Surface
      title="Design new zones"
      description="Only HBA ports with an unzoned array port are listed. Nothing is ticked for you: tick each pair your SAN design wants. HPE's redundancy rule is at least one port on each controller node per fabric. Already-zoned pairs are shown, never recreated."
    >
      <Box gap="medium">
        {/* SPEC-010 R4 (Z-1): the glyphs the rows use, said once. */}
        <Box direction="row" gap="medium" wrap align="center">
          <Box direction="row" gap="xsmall" align="center"><StatusGood size="small" color="status-ok" a11yTitle="Zoned" /><Text size="xsmall" color="text-weak">already zoned (read from the array; never recreated)</Text></Box>
          <Box direction="row" gap="xsmall" align="center"><CheckBox checked readOnly tabIndex={-1} a11yTitle="selected" /><Text size="xsmall" color="text-weak">selected — a new zone will be created</Text></Box>
          <Box direction="row" gap="xsmall" align="center"><CheckBox checked={false} readOnly tabIndex={-1} a11yTitle="not selected" /><Text size="xsmall" color="text-weak">available, not selected</Text></Box>
          <Text size="xsmall" color="status-warning">⚠ caution — see the port's note</Text>
        </Box>
        {fabricsWithWork.map((fab) => {
          const zoned = new Set(fab.already_zoned.map(([h, a]) => pairKey(h, a)));
          const nodes = [...new Set(fab.array_ports.map((p) => p.node ?? -1))].sort((a, b) => a - b);
          const hosts = fab.hosts.filter((h) => fab.array_ports.some((p) => !zoned.has(pairKey(h.wwpn, p.wwpn))));
          return (
            <Box key={fab.fabric} gap="small">
              <Text size="small" weight={600}>
                {fabricTitle(fab)} · cfg <Text size="small" style={mono}>{fab.active_cfg || 'not read'}</Text>
              </Text>
              {hosts.map((h) => {
                const zonedHere = fab.array_ports.filter((p) => zoned.has(pairKey(h.wwpn, p.wwpn)));
                return (
                  <Box key={h.wwpn} gap="xsmall" pad={{ left: 'small', bottom: 'small' }} border={{ side: 'bottom', color: 'border' }}>
                    <Box direction="row" gap="small" align="baseline" wrap>
                      <Text size="small" weight={600}>{hostName(h)}</Text>
                      <Text size="small" color="text-weak">HBA port</Text>
                      <Text size="small" style={mono} title={wwpnTitle(h)}>{h.display}</Text>
                      {h.os && <Text size="xsmall" color="text-weak">{h.os}</Text>}
                      {hostSource(h) && <Text size="xsmall" color="text-weak">{hostSource(h)}</Text>}
                      {h.placed_on_switch && <Text size="xsmall" color="text-weak">on {h.placed_on_switch} via ISL</Text>}
                    </Box>
                    <Box direction="row" gap="large" wrap>
                      {nodes.map((node) => (
                        <Box key={node} direction="row" gap="small" align="center">
                          <Text size="xsmall" color="text-weak">{node >= 0 ? `node ${node}:` : 'ports:'}</Text>
                          {fab.array_ports.filter((p) => (p.node ?? -1) === node).map((p) => {
                            const key = pairKey(h.wwpn, p.wwpn);
                            if (zoned.has(key)) {
                              return (
                                <Box key={key} direction="row" gap="xsmall" align="center" title={`Already zoned: ${(fab.zone_names?.[key] ?? []).join(', ')}`}>
                                  <StatusGood size="small" color="status-ok" a11yTitle="Zoned" />
                                  <Text size="small">{p.nsp}</Text>
                                </Box>
                              );
                            }
                            return (
                              <CheckBox
                                key={key}
                                checked={Boolean(selected[key])}
                                label={
                                  <Text size="small" color={p.caution ? 'status-warning' : undefined}>
                                    {p.nsp}
                                    {p.caution && <Text size="xsmall" color="status-warning"> ⚠ {p.caution}</Text>}
                                  </Text>
                                }
                                onChange={(e) => toggle(key, e.target.checked)}
                              />
                            );
                          })}
                        </Box>
                      ))}
                    </Box>
                    {zonedHere.length > 0 && (
                      <Text size="xsmall" color="text-weak">
                        Already zoned here: {zonedHere.map((p) => `${p.nsp} (${(fab.zone_names?.[pairKey(h.wwpn, p.wwpn)] ?? ['?']).join(', ')})`).join(' · ')}
                      </Text>
                    )}
                  </Box>
                );
              })}
            </Box>
          );
        })}
      </Box>
    </Surface>
  );
}

// ---------------------------------------------------------------- D. Names

function AliasReview({
  plan, selectedPairs, aliases, setAlias, clashes, children,
}: {
  plan: ZoningPlan;
  selectedPairs: [string, string][];
  aliases: Record<string, string>;
  setAlias: (wwpn: string, v: string) => void;
  clashes: ReturnType<typeof nameClashes>;
  /** Generate command set, at the foot of the panel (Q3: in the page, not the footer). */
  children: ReactNode;
}) {
  if (selectedPairs.length === 0) {
    return (
      <Surface title="Names for the new zones">
        <Text size="small" color="text-weak">Select a pair above. Only the WWPNs that take part in a new zone need a name.</Text>
        {children}
      </Surface>
    );
  }
  const selectedSet = new Set(selectedPairs.map(([h, a]) => pairKey(h, a)));
  return (
    <Surface
      title="Names for the new zones"
      description="An alias is the switch's readable name for a WWPN; zones are written with alias names. Where the switch already has one it is reused (no alicreate). Otherwise a name from the HPE convention is proposed — edit it to your site's standard."
    >
      <Box gap="medium">
        {plan.fabrics.map((fab) => {
          const pairs = fab.pairs.filter(([h, a]) => selectedSet.has(pairKey(h, a)));
          if (pairs.length === 0) return null;
          const participants = new Set(pairs.flatMap((p) => p));
          const entries = [...fab.hosts, ...fab.array_ports].filter((w) => participants.has(w.wwpn));
          const nameOf = (wwpn: string) => aliases[wwpn] ?? '';
          return (
            <Box key={fab.fabric} gap="xsmall">
              <Text size="small" weight={600}>{fabricTitle(fab)}</Text>
              {entries.map((w) => {
                const value = nameOf(w.wwpn);
                const reused = value !== '' && w.existing_aliases.includes(value);
                const check = reused ? { tone: 'ok' as const, text: 'Existing alias — reused' }
                  : clashes.port[w.wwpn] ? { tone: 'critical' as const, text: clashes.port[w.wwpn] } : aliasProblem(value);
                const colour = check.tone === 'critical' ? 'status-critical' : check.tone === 'warning' ? 'status-warning' : 'status-ok';
                const suggestion = check.tone === 'critical' ? aliasSuggestion(value) : '';
                const offer = suggestion && suggestion !== value && aliasProblem(suggestion).tone !== 'critical';
                return (
                  <Box key={w.wwpn} direction="row" gap="small" align="center" wrap pad={{ vertical: 'xxsmall' }}>
                    <Box basis="xsmall" flex={false}><Text size="xsmall" color="text-weak">{w.role === 'array' ? `Array port ${w.nsp}` : 'HBA port'}</Text></Box>
                    <Box basis="small" flex={false}><Text size="small" truncate>{w.role === 'array' ? (w.node != null ? `node ${w.node}` : '') : hostName(w)}</Text></Box>
                    <Box basis="small" flex={false}><Text size="small" style={mono} title={wwpnTitle(w)}>{w.display}</Text></Box>
                    <Box basis="medium" flex="shrink">
                      <TextInput size="small" value={value} placeholder="alias name" onChange={(e) => setAlias(w.wwpn, e.target.value)} />
                    </Box>
                    <Text size="xsmall" color={colour}>{check.text}</Text>
                    {/* SPEC-010 R3 (Z-3): the validator offers the fix, not only the verdict. */}
                    {offer && <Button size="small" label={`Use ${suggestion}`} onClick={() => setAlias(w.wwpn, suggestion)} />}
                    {w.existing_aliases.filter((a) => a !== value).length > 0 && (
                      <Text size="xsmall" color="text-weak">also on switch: {w.existing_aliases.filter((a) => a !== value).join(', ')}</Text>
                    )}
                  </Box>
                );
              })}
              <Text size="xsmall" color="text-weak">
                Zones to be created: {pairs.map(([h, a]) => `${nameOf(h) || '?'}_${nameOf(a) || '?'}`).join(' · ')}
              </Text>
              {pairs.filter(([h, a]) => clashes.zone[pairKey(h, a)]).map(([h, a]) => (
                <Text key={pairKey(h, a)} size="xsmall" color="status-critical">{clashes.zone[pairKey(h, a)]}</Text>
              ))}
            </Box>
          );
        })}
        {children}
      </Box>
    </Surface>
  );
}

// ---------------------------------------------------------------- E. Command set

const ACTIVATION = ['cfgsave', 'cfgenable'];
const isActivation = (c: string) => ACTIVATION.some((verb) => c.startsWith(verb));
const isPrecheck = (c: string) => c.startsWith('cfgtransshow');
const PRECHECK_EXPECT = 'There is no outstanding zoning transaction';

/** The command set for one fabric, in FOS order (SPEC-010): 1. check, 2. paste block, 3. activate.
 *
 * Activation is separated from the additive commands on purpose. Until 2026-09-02 it was rendered
 * in the same block as commands the tool had just executed, so the screen drew no boundary between
 * "done" and "yours to do" — and an operator could reasonably select the whole block and paste it.
 * `cfgsave` commits the transaction; `cfgenable` replaces the effective config fabric-wide. Both
 * belong to the SAN team, in a window, deliberately. The check is its own block for the same reason:
 * pasted with the rest it would be a line of output nobody reads before the alicreates land. */
function CommandSet({ fab, commands }: { fab: FabricZonePlan; commands: string[] }) {
  const precheck = commands.filter(isPrecheck);
  const additive = commands.filter((c) => !isActivation(c) && !isPrecheck(c));
  const activation = commands.filter(isActivation);
  const [copied, setCopied] = useState<'' | 'check' | 'paste'>('');
  if (commands.length === 0) {
    return <Text size="small" color="text-weak">{fabricTitle(fab)}: no commands — nothing selected here that does not already exist.</Text>;
  }
  const header = [
    `# ${fabricTitle(fab)} — switch ${fab.switch_host} ${fab.switch_name ?? ''} — active cfg ${fab.active_cfg || 'NOT READ'}`,
    `# Generated ${new Date().toISOString()} by Alletra Onboard. Additive only: creates nothing that exists, removes nothing.`,
    `# Paste only after cfgtransshow reported "${PRECHECK_EXPECT}".`,
  ];
  const copyText = async (text: string, which: 'check' | 'paste') => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(which);
      setTimeout(() => setCopied(''), 2000);
    } catch {
      setCopied('');   // clipboard blocked; the text is on screen to select by hand
    }
  };
  const save = () => download(
    `zoning_${fab.fabric}_${fab.switch_host.replace(/[^0-9a-zA-Z]+/g, '-')}.txt`,
    [
      ...header, '',
      `# --- 1. check: must reply "${PRECHECK_EXPECT}" — stop if it does not ---`, ...precheck, '',
      '# --- 2. paste block (additive) ---', ...additive, '',
      '# --- 3. save and activate: SAN team, in a window ---',
      ...(activation.length ? activation : ['# none: no effective zoning configuration was read on this switch - see the plan notes']), '',
    ].join('\n'),
  );
  return (
    <Box gap="xsmall">
      <Box direction="row" gap="small" align="baseline" wrap>
        <Text size="small" weight={600}>{fabricTitle(fab)}</Text>
        <Text size="small" color="text-weak">switch {fab.switch_host} {fab.switch_name ?? ''} · cfg <Text size="small" style={mono}>{fab.active_cfg || 'not read'}</Text></Text>
      </Box>
      {precheck.length > 0 && (
        <Box gap="xxsmall">
          <Text size="small" weight={600}>1. Check — run alone first</Text>
          <Box direction="row" gap="small" align="center" wrap>
            <Box background="background-contrast" round="xsmall" pad={{ horizontal: 'small', vertical: 'xsmall' }}>
              {precheck.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
            </Box>
            <Button size="small" label={copied === 'check' ? 'Copied' : 'Copy'} onClick={() => copyText(precheck.join('\n'), 'check')} />
            <Text size="small" color="text-weak">Expected reply: <i>{PRECHECK_EXPECT}</i>. Anything else: stop and ask the SAN team.</Text>
          </Box>
        </Box>
      )}
      <Text size="small" weight={600}>2. Paste block — additive only</Text>
      <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
        {additive.map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
      </Box>
      <Box direction="row" gap="small" align="center" wrap>
        <Button size="small" label={copied === 'paste' ? 'Copied' : 'Copy paste block'} onClick={() => copyText([...header, ...additive].join('\n'), 'paste')} />
        <Button size="small" label="Download .txt (all three steps)" onClick={save} />
      </Box>
      {activation.length > 0 && (
        <Box border={{ color: 'status-warning', side: 'left', size: 'medium' }} pad={{ left: 'small', vertical: 'xsmall' }} gap="xxsmall">
          <Text size="small" weight={600}>3. Save and activate — SAN team, in a window</Text>
          <Text size="small" color="text-weak">
            Not part of the paste above. <Text size="small" style={mono}>cfgsave</Text> commits the defined
            configuration and closes the zoning transaction; <Text size="small" style={mono}>cfgenable</Text> replaces
            the effective configuration across the whole fabric, so the SAN team runs it in a maintenance window.
          </Text>
          {activation.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
        </Box>
      )}
      {activation.length === 0 && additive.length > 0 && (
        <Box border={{ color: 'status-critical', side: 'left', size: 'medium' }} pad={{ left: 'small', vertical: 'xsmall' }} gap="xxsmall">
          <Text size="small" weight={600}>3. Save and activate — cannot be generated for this switch</Text>
          <Text size="small">
            No effective zoning configuration was read on {fab.switch_host}, so there is no <Text size="small" style={mono}>cfgadd</Text> or{' '}
            <Text size="small" style={mono}>cfgenable</Text>. The zones in the paste block take no effect until they are in an enabled
            configuration. Run <Text size="small" style={mono}>cfgactvshow</Text> on the switch and ask the SAN owner before pasting.
          </Text>
        </Box>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------- F. Peer ports (SPEC-025 R7)

/** The pairs the sheet's Peer ports tab asks for, on the fabric where both ports are, with their names.
 *  Every pair is drafted (the sheet chose them); a pair the fabric already zones is left out. */
function PeerZones({ plan, aliases, setAlias }: {
  plan: ZoningPlan; aliases: Record<string, string>; setAlias: (wwpn: string, v: string) => void;
}) {
  const fabrics = plan.fabrics.filter((f) => (f.peer_pairs ?? []).length > 0);
  if (fabrics.length === 0) return null;
  return (
    <Surface
      title="Peer ports for the migration"
      description="From the sheet's Peer ports tab: each peer port of this array zoned to the source array's ports, using the peer port's WWPN read after it was set. The zones go in a command set of their own."
    >
      <Box gap="medium">
        {fabrics.map((fab) => {
          const zoned = new Set((fab.peer_already_zoned ?? []).map(([p, s]) => pairKey(p, s)));
          const entries = [...(fab.peer_ports ?? []), ...(fab.sources ?? [])];
          return (
            <Box key={fab.fabric} gap="xsmall">
              <Text size="small" weight={600}>{fabricTitle(fab)}</Text>
              {entries.map((w) => {
                const value = aliases[w.wwpn] ?? '';
                const reused = value !== '' && w.existing_aliases.includes(value);
                const check = reused ? { tone: 'ok' as const, text: 'Existing alias, reused' } : aliasProblem(value);
                const colour = check.tone === 'critical' ? 'status-critical' : check.tone === 'warning' ? 'status-warning' : 'status-ok';
                const peer = (fab.peer_ports ?? []).includes(w);
                return (
                  <Box key={w.wwpn} direction="row" gap="small" align="center" wrap pad={{ vertical: 'xxsmall' }}>
                    <Box basis="small" flex={false}>
                      <Text size="xsmall" color="text-weak">{peer ? `Peer port ${w.nsp}` : `Source port ${w.nsp || ''}`.trim()}</Text>
                    </Box>
                    <Box basis="small" flex={false}><Text size="small" style={mono}>{w.display}</Text></Box>
                    <Box basis="medium" flex="shrink">
                      <TextInput size="small" value={value} placeholder="alias name" onChange={(e) => setAlias(w.wwpn, e.target.value)} />
                    </Box>
                    <Text size="xsmall" color={colour}>{check.text}</Text>
                  </Box>
                );
              })}
              <Text size="xsmall" color="text-weak">
                Zones: {(fab.peer_pairs ?? []).map(([p, s]) =>
                  `${aliases[p] || '?'}_${aliases[s] || '?'}${zoned.has(pairKey(p, s)) ? ' (already zoned)' : ''}`).join(' · ')}
              </Text>
            </Box>
          );
        })}
      </Box>
    </Surface>
  );
}

// ---------------------------------------------------------------- the step body

type DoneItem = ComponentProps<typeof DoneList>['items'][number];

/** What was drafted, for the finished part's detail: the zones per fabric with the names they carry. */
function Drafted({ plan, selectedPairs, aliases }: { plan: ZoningPlan; selectedPairs: [string, string][]; aliases: Record<string, string> }) {
  const chosen = new Set(selectedPairs.map(([h, a]) => pairKey(h, a)));
  const zone = ([h, a]: [string, string]) => `${aliases[h] || '?'}_${aliases[a] || '?'}`;
  return (
    <Box gap="xxsmall">
      {plan.fabrics.map((fab) => {
        const pairs = fab.pairs.filter(([h, a]) => chosen.has(pairKey(h, a)));
        return pairs.length ? (
          <Text key={fab.fabric} size="small">
            {fabricTitle(fab)}: <Text size="small" style={mono}>{pairs.map(zone).join(' · ')}</Text>
          </Text>
        ) : null;
      })}
      {plan.fabrics.map((fab) => {
        // a peer pair the fabric already zones is not in the command set (the backend leaves it out)
        const zoned = new Set((fab.peer_already_zoned ?? []).map(([p, src]) => pairKey(p, src)));
        const pairs = (fab.peer_pairs ?? []).filter(([p, src]) => !zoned.has(pairKey(p, src)));
        return pairs.length ? (
          <Text key={`peer-${fab.fabric}`} size="small">
            Peer ports, {fabricTitle(fab)}: <Text size="small" style={mono}>{pairs.map(zone).join(' · ')}</Text>
          </Text>
        ) : null;
      })}
    </Box>
  );
}

/**
 * The plan's parts of SAN zoning (SPEC-030 R7): the finished parts in one list (the step's check row,
 * handed in as `done`, and the drafting row once a command set exists), then the part at hand (the
 * pairs and the names, or the command set), then what the switches hold, folded. The view keeps its
 * own state: it is keyed on the plan event, so the alias fields are seeded once per plan.
 */
export function ZoningPlanView({ plan, runId, done = [] }: { plan: ZoningPlan; runId?: string; done?: DoneItem[] }) {
  const [aliases, setAliases] = useState<Record<string, string>>(() => {
    const seed: Record<string, string> = {};
    plan.fabrics.forEach((f) => [...f.hosts, ...f.array_ports, ...(f.peer_ports ?? []), ...(f.sources ?? [])].forEach((w) => {
      seed[w.wwpn] = w.suggested_alias || w.proposed_alias || '';
    }));
    return seed;
  });
  // Field decision 2026-09-29 (BL-01): the operator ticks every pair; nothing is chosen for them.
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [result, setResult] = useState<ZoningRenderResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nothingSelected, setNothingSelected] = useState(false);

  const setAlias = (wwpn: string, v: string) => { setAliases((a) => ({ ...a, [wwpn]: v })); setResult(null); };
  const toggle = (key: string, on: boolean) => { setSelected((s) => ({ ...s, [key]: on })); setResult(null); setNothingSelected(false); };

  const selectedPairs: [string, string][] = plan.fabrics.flatMap((f) =>
    f.pairs.filter(([h, a]) => selected[pairKey(h, a)]),
  );
  const totalZoned = plan.fabrics.reduce((n, f) => n + f.already_zoned.length, 0);
  const peerToZone = plan.fabrics.reduce((n, f) => n + (f.peer_pairs ?? []).length - (f.peer_already_zoned ?? []).length, 0);
  const newZones = selectedPairs.length + peerToZone;
  // Say it BEFORE the click: a selected pair whose member has no acceptable name cannot be zoned
  // (the rc.1 live test ticked an alias-less port and got an unchanged preview with no explanation).
  const clashes = nameClashes(plan, selectedPairs, aliases);
  const blocked = selectedPairs.filter(([h, a]) =>
    aliasProblem(aliases[h] ?? '').tone === 'critical' || aliasProblem(aliases[a] ?? '').tone === 'critical'
    || clashes.port[h] || clashes.port[a] || clashes.zone[pairKey(h, a)]).length;

  // Q3: never disabled. With nothing to zone, or a name the switch would refuse, the click says why
  // (the sentence beside the button) and sends nothing.
  const generate = async () => {
    if (newZones === 0) {
      setNothingSelected(true);
      return;
    }
    if (blocked > 0) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await renderZoningCommands(plan, aliases, selectedPairs, runId));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  const items: DoneItem[] = [
    ...done,
    ...(result
      ? [{
          text: `Drafted ${newZones} new zone${newZones === 1 ? '' : 's'} for the SAN team`,
          detail: <Drafted plan={plan} selectedPairs={selectedPairs} aliases={aliases} />,
          // back to the pairs and names, as they were; generating again makes a new command set
          again: { label: 'Change', onClick: () => setResult(null) },
        }]
      : []),
  ];

  return (
    <Box gap="medium">
      {items.length > 0 && <DoneList items={items} />}

      {!result && <ZoneDesigner plan={plan} selected={selected} toggle={toggle} />}
      {!result && <PeerZones plan={plan} aliases={aliases} setAlias={setAlias} />}
      {!result && (
        <AliasReview plan={plan} selectedPairs={selectedPairs} aliases={aliases} setAlias={setAlias} clashes={clashes}>
          {error && <InlineNotification tone="critical" title="The request failed" message={error} />}
          <Box direction="row" gap="small" align="center" wrap>
            <Button
              busy={busy}
              label={`Generate command set (${newZones} new zone${newZones === 1 ? '' : 's'})`}
              onClick={generate}
            />
            {totalZoned > 0 && <Text size="small" color="text-weak">{totalZoned} pair(s) already zoned — excluded automatically.</Text>}
            {blocked > 0 && <Text size="small" color="status-critical">{blocked} selected pair(s) have a missing, invalid or clashing name.</Text>}
            {nothingSelected && newZones === 0 && (
              <Text size="small" color="status-critical">Nothing is selected: tick a pair above first.</Text>
            )}
          </Box>
        </AliasReview>
      )}

      {result && (
        <Surface
          title="Command set — give this to your SAN team"
          description="This tool never writes to a switch. The SAN team reviews the paste block, applies it on the named switch, then saves and activates in a window. Re-check zoning afterwards: the array shows each new login."
        >
          <Box gap="medium">
            {plan.fabrics.filter((fab) => selectedPairs.length > 0 || (result.commands[fab.fabric] ?? []).length > 0).map((fab) => (
              <Box key={fab.fabric} gap="xsmall">
                <CommandSet fab={fab} commands={result.commands[fab.fabric] ?? []} />
                {(result.skipped[fab.fabric] ?? []).length > 0 && (
                  <InlineNotification tone="warning" title="Not included" message={<NotesList notes={result.skipped[fab.fabric]} />} />
                )}
                {(result.warnings?.[fab.fabric] ?? []).length > 0 && (
                  <InlineNotification tone="info" title="Portability" message={<NotesList notes={result.warnings![fab.fabric]} />} />
                )}
              </Box>
            ))}
            {Object.keys(result.peer_commands ?? {}).length > 0 && (
              <Box gap="small">
                <Text weight={600}>Peer ports for the migration</Text>
                {plan.fabrics.filter((fab) => fab.fabric in (result.peer_commands ?? {})).map((fab) => (
                  <Box key={`peer-${fab.fabric}`} gap="xsmall">
                    <CommandSet fab={fab} commands={result.peer_commands?.[fab.fabric] ?? []} />
                    {(result.peer_skipped?.[fab.fabric] ?? []).length > 0 && (
                      <InlineNotification tone="warning" title="Not included" message={<NotesList notes={result.peer_skipped![fab.fabric]} />} />
                    )}
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </Surface>
      )}

      <Section
        title="What the switches hold"
        summary={plan.fabrics.map((fab) => `${fabricTitle(fab)} on ${fab.switch_name || fab.switch_host}`).join(' · ')}
      >
        <FabricOverview plan={plan} />
        <CurrentZoningTable plan={plan} />
      </Section>
    </Box>
  );
}
