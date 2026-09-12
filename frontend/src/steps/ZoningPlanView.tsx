import { Box, Button, CheckBox, DataTable, Text, TextInput } from 'grommet';
import { AddCircle, StatusGood, StatusUnknown, StatusWarning } from 'grommet-icons';
import { useMemo, useState } from 'react';
import { AliasedWwpn, FabricZonePlan, ZoningPlan, ZoningRenderResult, renderZoningCommands } from '../api';
import { InlineNotification, Surface, TableSummary } from '../ui/primitives';

// ADR 0004 + ADR 0012: the zoning screen, redesigned after the 2026-09-12 live test
// (docs/ux/ZONING-REDESIGN.md). Five panels, one step:
//   A  Fabrics          — what each declared switch is, and which array ports sit on it
//   B  Current zoning   — one row per host HBA port: what it can reach today, and by which zone
//   C  Design new zones — only HBA ports that need zones; array ports grouped by controller node
//   D  Names            — only the WWPNs that take part in a selected new zone
//   E  Command set      — the deliverable, per fabric; activation kept apart
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

const PAIR_STATE: Record<PairState, { label: string; color: string; Icon: typeof StatusGood }> = {
  zoned: { label: 'Zoned', color: 'status-ok', Icon: StatusGood },
  partial: { label: 'Partly zoned', color: 'status-warning', Icon: StatusWarning },
  unzoned: { label: 'Not zoned', color: 'status-warning', Icon: StatusWarning },
  offline: { label: 'Not on fabric', color: 'status-unknown', Icon: StatusUnknown },
  new: { label: 'New zone', color: 'brand', Icon: AddCircle },
};

function PairStatus({ state, detail }: { state: PairState; detail?: string }) {
  const { label, color, Icon } = PAIR_STATE[state];
  return (
    <Box direction="row" gap="xsmall" align="center" flex={false}>
      <Icon size="small" color={color} a11yTitle={label} />
      <Text size="small" weight={500}>{detail ? `${label} · ${detail}` : label}</Text>
    </Box>
  );
}

// ---------------------------------------------------------------- A. Fabrics

function FabricOverview({ plan }: { plan: ZoningPlan }) {
  return (
    <Surface title="Fabrics" description="The two switches named on the sheet, read read-only. Every array port is cabled to exactly one of them; a zone only works inside one fabric.">
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
        {plan.notes.length > 0 && (
          <InlineNotification tone="info" title="Cabling and fabric notes" message={plan.notes.join(' ')} />
        )}
      </Box>
    </Surface>
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
    r.zonedPorts.join(' ') || '-', r.zones.join(' ') || '-', PAIR_STATE[r.state].label,
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
    <Surface
      title="Current zoning"
      description="One row per host HBA port. “Zoned” is read from the array (a login is only possible through an effective zone) and the zone name from the switch's effective configuration."
      actions={<Button size="small" label="Export .txt" onClick={() => download('current-zoning.txt', exportText(plan, rows))} />}
    >
      {rows.length === 0 ? (
        <Text size="small" color="text-weak">No host HBA port is online on either fabric.</Text>
      ) : (
        <>
          <DataTable
            primaryKey="key"
            data={shown}
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
              { property: 'wwpn', header: 'HBA port (WWPN)', render: (r: HbaRow) => <Text size="small" style={mono}>{r.wwpn || '--'}</Text> },
              {
                property: 'fabric', header: 'Fabric',
                render: (r: HbaRow) => (
                  <Box>
                    <Text size="small">{r.fabric || '--'}</Text>
                    {r.placed && <Text size="xsmall" color="text-weak">on {r.placed} via ISL</Text>}
                  </Box>
                ),
              },
              {
                property: 'zonedPorts', header: 'Zoned to array ports',
                render: (r: HbaRow) => <Text size="small">{r.zonedPorts.length ? r.zonedPorts.join(', ') : '--'}</Text>,
              },
              { property: 'zones', header: 'Zone', render: (r: HbaRow) => <Text size="small" style={mono}>{r.zones.join(', ') || '--'}</Text> },
              {
                property: 'state', header: 'Status',
                render: (r: HbaRow) => (
                  <PairStatus
                    state={r.state}
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
    </Surface>
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
      description="Only HBA ports with an unzoned array port are listed. HPE's redundancy rule — one port on each controller node per fabric — is pre-selected; untick anything your SAN design does not want. Already-zoned pairs are shown, never recreated."
    >
      <Box gap="medium">
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
  plan, selectedPairs, aliases, setAlias,
}: {
  plan: ZoningPlan;
  selectedPairs: [string, string][];
  aliases: Record<string, string>;
  setAlias: (wwpn: string, v: string) => void;
}) {
  if (selectedPairs.length === 0) {
    return (
      <Surface title="Names for the new zones">
        <Text size="small" color="text-weak">Select a pair above. Only the WWPNs that take part in a new zone need a name.</Text>
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
                const check = reused ? { tone: 'ok' as const, text: 'Existing alias — reused' } : aliasProblem(value);
                const colour = check.tone === 'critical' ? 'status-critical' : check.tone === 'warning' ? 'status-warning' : 'status-ok';
                return (
                  <Box key={w.wwpn} direction="row" gap="small" align="center" wrap pad={{ vertical: 'xxsmall' }}>
                    <Box width="110px" flex={false}><Text size="xsmall" color="text-weak">{w.role === 'array' ? `Array port ${w.nsp}` : 'HBA port'}</Text></Box>
                    <Box width="170px" flex={false}><Text size="small" truncate>{w.role === 'array' ? (w.node != null ? `node ${w.node}` : '') : hostName(w)}</Text></Box>
                    <Box width="215px" flex={false}><Text size="small" style={mono} title={wwpnTitle(w)}>{w.display}</Text></Box>
                    <Box width="300px" flex={false}>
                      <TextInput size="small" value={value} placeholder="alias name" onChange={(e) => setAlias(w.wwpn, e.target.value)} />
                    </Box>
                    <Text size="xsmall" color={colour}>{check.text}</Text>
                    {w.existing_aliases.filter((a) => a !== value).length > 0 && (
                      <Text size="xsmall" color="text-weak">also on switch: {w.existing_aliases.filter((a) => a !== value).join(', ')}</Text>
                    )}
                  </Box>
                );
              })}
              <Text size="xsmall" color="text-weak">
                Zones to be created: {pairs.map(([h, a]) => `${nameOf(h) || '?'}_${nameOf(a) || '?'}`).join(' · ')}
              </Text>
            </Box>
          );
        })}
      </Box>
    </Surface>
  );
}

// ---------------------------------------------------------------- E. Command set

const ACTIVATION = ['cfgsave', 'cfgenable'];
const isActivation = (c: string) => ACTIVATION.some((verb) => c.startsWith(verb));

/** The command set for one fabric.
 *
 * Activation is separated from the additive commands on purpose. Until 2026-09-02 it was rendered
 * in the same block as commands the tool had just executed, so the screen drew no boundary between
 * "done" and "yours to do" — and an operator could reasonably select the whole block and paste it.
 * `cfgsave` commits the transaction; `cfgenable` replaces the effective config fabric-wide. Both
 * belong to the SAN team, in a window, deliberately. */
function CommandSet({ fab, commands }: { fab: FabricZonePlan; commands: string[] }) {
  const additive = commands.filter((c) => !isActivation(c));
  const activation = commands.filter(isActivation);
  const [copied, setCopied] = useState(false);
  if (commands.length === 0) {
    return <Text size="small" color="text-weak">{fabricTitle(fab)}: no commands — nothing selected here that does not already exist.</Text>;
  }
  const header = [
    `# ${fabricTitle(fab)} — switch ${fab.switch_host} ${fab.switch_name ?? ''} — active cfg ${fab.active_cfg}`,
    `# Generated ${new Date().toISOString()} by Alletra Onboard. Additive only: creates nothing that exists, removes nothing.`,
    '# Run cfgtransshow first — it must report no outstanding zoning transaction.',
  ];
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(additive.join('\n'));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);   // clipboard blocked; the text is on screen to select by hand
    }
  };
  const save = () => download(
    `zoning_${fab.fabric}_${fab.switch_host.replace(/[^0-9a-zA-Z]+/g, '-')}.txt`,
    [...header, '', '# --- paste block (additive) ---', ...additive, '', '# --- activation: SAN team, in a window ---', ...activation, ''].join('\n'),
  );
  return (
    <Box gap="xsmall">
      <Box direction="row" gap="small" align="baseline" wrap>
        <Text size="small" weight={600}>{fabricTitle(fab)}</Text>
        <Text size="small" color="text-weak">switch {fab.switch_host} {fab.switch_name ?? ''} · cfg <Text size="small" style={mono}>{fab.active_cfg}</Text></Text>
      </Box>
      <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
        {additive.map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
      </Box>
      <Box direction="row" gap="small" align="center" wrap>
        <Button size="small" label={copied ? 'Copied' : 'Copy paste block'} onClick={copy} />
        <Button size="small" label="Download .txt" onClick={save} />
        <Text size="small" color="text-weak">Run <Text size="small" style={mono}>cfgtransshow</Text> first: it must report no outstanding transaction.</Text>
      </Box>
      {activation.length > 0 && (
        <Box border={{ color: 'status-warning', side: 'left', size: '3px' }} pad={{ left: 'small', vertical: 'xsmall' }} gap="xxsmall">
          <Text size="small" weight={600}>Then, separately — save and activate (SAN team)</Text>
          <Text size="small" color="text-weak">
            Not part of the paste above. <Text size="small" style={mono}>cfgsave</Text> commits the defined
            configuration and closes the zoning transaction; <Text size="small" style={mono}>cfgenable</Text> replaces
            the effective configuration across the whole fabric, so the SAN team runs it in a maintenance window.
          </Text>
          {activation.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
        </Box>
      )}
    </Box>
  );
}

// ---------------------------------------------------------------- the step body

/** Pre-select HPE's redundancy rule for every HBA port that needs zones: the first unzoned,
 *  non-caution array port on each controller node of that fabric. */
function recommendedSelection(plan: ZoningPlan): Record<string, boolean> {
  const out: Record<string, boolean> = {};
  plan.fabrics.forEach((fab) => {
    const zoned = new Set(fab.already_zoned.map(([h, a]) => pairKey(h, a)));
    fab.hosts.forEach((h) => {
      const unzoned = fab.array_ports.filter((p) => !zoned.has(pairKey(h.wwpn, p.wwpn)) && !p.caution);
      if (unzoned.length === 0) return;
      const byNode = new Map<number, AliasedWwpn>();
      unzoned.forEach((p) => { const n = p.node ?? -1; if (!byNode.has(n)) byNode.set(n, p); });
      byNode.forEach((p) => { out[pairKey(h.wwpn, p.wwpn)] = true; });
    });
  });
  return out;
}

export function ZoningPlanView({ plan }: { plan: ZoningPlan }) {
  const [aliases, setAliases] = useState<Record<string, string>>(() => {
    const seed: Record<string, string> = {};
    plan.fabrics.forEach((f) => [...f.hosts, ...f.array_ports].forEach((w) => {
      seed[w.wwpn] = w.suggested_alias || w.proposed_alias || '';
    }));
    return seed;
  });
  const [selected, setSelected] = useState<Record<string, boolean>>(() => recommendedSelection(plan));
  const [result, setResult] = useState<ZoningRenderResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setAlias = (wwpn: string, v: string) => { setAliases((a) => ({ ...a, [wwpn]: v })); setResult(null); };
  const toggle = (key: string, on: boolean) => { setSelected((s) => ({ ...s, [key]: on })); setResult(null); };

  const selectedPairs: [string, string][] = plan.fabrics.flatMap((f) =>
    f.pairs.filter(([h, a]) => selected[pairKey(h, a)]),
  );
  const totalZoned = plan.fabrics.reduce((n, f) => n + f.already_zoned.length, 0);
  // Say it BEFORE the click: a selected pair whose member has no acceptable name cannot be zoned
  // (the rc.1 live test ticked an alias-less port and got an unchanged preview with no explanation).
  const blocked = selectedPairs.filter(([h, a]) =>
    aliasProblem(aliases[h] ?? '').tone === 'critical' || aliasProblem(aliases[a] ?? '').tone === 'critical').length;

  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      setResult(await renderZoningCommands(plan, aliases, selectedPairs));
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box gap="medium">
      {error && <InlineNotification tone="critical" title="The request failed" message={error} />}

      <FabricOverview plan={plan} />
      <CurrentZoningTable plan={plan} />
      <ZoneDesigner plan={plan} selected={selected} toggle={toggle} />
      <AliasReview plan={plan} selectedPairs={selectedPairs} aliases={aliases} setAlias={setAlias} />

      <Box direction="row" gap="small" align="center" wrap>
        <Button
          busy={busy}
          disabled={selectedPairs.length === 0 || blocked > 0}
          primary
          label={`Generate command set (${selectedPairs.length} new zone${selectedPairs.length === 1 ? '' : 's'})`}
          onClick={generate}
        />
        {totalZoned > 0 && <Text size="small" color="text-weak">{totalZoned} pair(s) already zoned — excluded automatically.</Text>}
        {blocked > 0 && <Text size="small" color="status-critical">{blocked} selected pair(s) have a missing or invalid alias name.</Text>}
      </Box>

      {result && (
        <Surface
          title="Command set — give this to your SAN team"
          description="This tool never writes to a switch. The SAN team reviews the paste block, applies it on the named switch, then saves and activates in a window. Re-check zoning afterwards: the array shows each new login."
        >
          <Box gap="medium">
            {plan.fabrics.map((fab) => (
              <Box key={fab.fabric} gap="xsmall">
                <CommandSet fab={fab} commands={result.commands[fab.fabric] ?? []} />
                {(result.skipped[fab.fabric] ?? []).length > 0 && (
                  <InlineNotification tone="warning" title="Not included" message={result.skipped[fab.fabric].join(' · ')} />
                )}
                {(result.warnings?.[fab.fabric] ?? []).length > 0 && (
                  <InlineNotification tone="info" title="Portability" message={result.warnings![fab.fabric].join(' · ')} />
                )}
              </Box>
            ))}
          </Box>
        </Surface>
      )}
    </Box>
  );
}
