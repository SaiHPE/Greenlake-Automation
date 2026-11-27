import type { FabricZoningApplyPlan, ZoningApplyResult } from '../api';

export const fabricLabel = (fabric: 'odd' | 'even') => (fabric === 'odd' ? 'Fabric F1 (odd)' : 'Fabric F2 (even)');

/** Format the opt-in approval sentence naming the exact configurations and switches. */
export function zoningApprovalLabel(fabrics: FabricZoningApplyPlan[]): string {
  const cfgs = [...new Set(fabrics.map((f) => f.active_cfg).filter(Boolean))].join(', ');
  const switches = [...new Set(fabrics.map((f) => f.switch_host).filter(Boolean))].join(', ');
  return `I have reviewed these Brocade commands and authorise creating these aliases and zones and activating ${cfgs} on ${switches}.`;
}

/** Merge every switch removal line from one or more zoning apply results into one valid Brocade
 *  sequence per switch: newest-first cfgremove, deduplicated zonedelete, deduplicated alidelete,
 *  and one closing `cfgenable "<cfg>" -f` at the very end (never leaving an open transaction). */
export function zoningRemovalBlocks(results: ZoningApplyResult[]): { header: string; lines: string[] }[] {
  interface SwitchBucket {
    header: string;
    cfgremove: string[];
    zonedelete: string[];
    alidelete: string[];
    other: string[];
    cfgenable: string | null;
  }
  const bySwitch = new Map<string, SwitchBucket>();
  const pushUnique = (list: string[], line: string) => {
    if (!list.includes(line)) list.push(line);
  };
  [...results].reverse().forEach((res) => {
    (res.fabrics ?? []).forEach((fab) => {
      const removals = fab.removals ?? [];
      if (removals.length === 0) return;
      const key = `${fab.fabric}::${fab.switch_host}::${fab.active_cfg}`;
      const bucket = bySwitch.get(key) ?? {
        header: `# ${fabricLabel(fab.fabric)} — switch ${fab.switch_host} — cfg ${fab.active_cfg}`,
        cfgremove: [],
        zonedelete: [],
        alidelete: [],
        other: [],
        cfgenable: null,
      };
      removals.forEach((line) => {
        if (line.startsWith('cfgremove ')) pushUnique(bucket.cfgremove, line);
        else if (line.startsWith('zonedelete ')) pushUnique(bucket.zonedelete, line);
        else if (line.startsWith('alidelete ')) pushUnique(bucket.alidelete, line);
        else if (line.startsWith('cfgenable ')) bucket.cfgenable = bucket.cfgenable ?? line;
        else pushUnique(bucket.other, line);
      });
      bySwitch.set(key, bucket);
    });
  });
  return [...bySwitch.values()].map((b) => ({
    header: b.header,
    lines: [
      ...b.cfgremove,
      ...b.zonedelete,
      ...b.alidelete,
      ...b.other,
      ...(b.cfgenable ? [b.cfgenable] : []),
    ],
  }));
}

/** Plain-text downloadable switch removal command set. */
export function zoningRemovalText(results: ZoningApplyResult[], runId: string): string {
  const blocks = zoningRemovalBlocks(results);
  return [
    `# Switch removal command set for run ${runId.slice(0, 8)} — ${new Date().toISOString()}`,
    '# Review before pasting. The tool never runs removal commands.',
    ...blocks.flatMap((b) => ['', b.header, ...b.lines]),
    '',
  ].join('\n');
}
