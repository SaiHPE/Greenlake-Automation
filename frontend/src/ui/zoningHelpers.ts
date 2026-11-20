import { AliasedWwpn, FabricZonePlan, ZoningPlan } from '../api';
import { RESULT, ResultWord } from './status';

export const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };
export const pairKey = (host: string, arr: string) => `${host}|${arr}`;

export const fabricTitle = (fab: FabricZonePlan) => `Fabric ${fab.fabric} (${fab.fabric === 'F1' ? 'odd' : 'even'})`;

const SOURCE_LABEL: Record<string, string> = {
  vcenter: 'from vCenter',
  sheet: 'from the sheet (Hosts tab)',
  array: 'array host object',
  switch: 'from the fabric name server',
};

export function hostName(w: AliasedWwpn): string {
  // QLogic HBAs advertise no HN: on the fabric — the WWPN is the only identity we have.
  return w.host_name || w.display;
}

export function hostSource(w: AliasedWwpn): string {
  if (w.host_source === 'array' && !w.host_name) return 'array login only — no host object yet';
  return SOURCE_LABEL[w.host_source] ?? '';
}

// Array target WWPNs on this family encode the port: 2N:SP:00:02:AC:<system> — node N, slot S, port P.
export function wwpnTitle(w: AliasedWwpn): string {
  if (w.role === 'array') return `Array port ${w.nsp}${w.node != null ? ` on controller node ${w.node}` : ''} — WWPN ${w.display}`;
  return `HBA port WWPN ${w.display}`;
}

// Brocade FOS zone-object names (mirrors zoning_plan.fos_name_problem / fos_name_warning — the
// backend stays authoritative; this only lets the operator see a problem before clicking Generate).
const FOS_NAME = /^[A-Za-z0-9][A-Za-z0-9_\-$^]*$/;
const FOS_ENHANCED = /^[0-9]|[-$^]/;
export function aliasProblem(name: string): { tone: 'critical' | 'warning' | 'ok'; text: string } {
  if (!name) return { tone: 'critical', text: 'Enter a name' };
  if (name.length > 64) return { tone: 'critical', text: `${name.length} characters — FOS allows 64` };
  if (!FOS_NAME.test(name)) return { tone: 'critical', text: 'Letters, digits and _ only' };
  if (FOS_ENHANCED.test(name)) return { tone: 'warning', text: 'Needs FOS 8.1.0+ on every switch (- $ ^ or leading digit)' };
  return { tone: 'ok', text: 'Valid' };
}

// SPEC-010 R3: mirrors zoning_plan.fos_name_suggestion — the closest name FOS accepts.
export function aliasSuggestion(name: string): string {
  if (name && aliasProblem(name).tone !== 'critical') return name;
  let folded = (name || '').replace(/[^A-Za-z0-9_\-$^]+/g, '_').replace(/^[_\-$^]+|[_\-$^]+$/g, '');
  if (!folded || !/^[A-Za-z0-9]/.test(folded)) folded = `a${folded}`;
  return folded.slice(0, 64);
}

// BL-09: the name clashes zoning_plan.render_commands skips a pair for, said before Generate.
export function nameClashes(plan: ZoningPlan, selectedPairs: [string, string][], aliases: Record<string, string>) {
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

type PairState = 'zoned' | 'partial' | 'unzoned' | 'offline' | 'new';

export const PAIR: Record<PairState, ResultWord> = {
  zoned: RESULT.zoned,
  partial: RESULT.partly_zoned,
  unzoned: RESULT.not_zoned,
  offline: RESULT.not_on_fabric,
  new: { state: 'not_started', label: 'New zone' },
};

export interface HbaRow {
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

export function hbaRows(plan: ZoningPlan): HbaRow[] {
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

export function exportText(plan: ZoningPlan, rows: HbaRow[]): string {
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
