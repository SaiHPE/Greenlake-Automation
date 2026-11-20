import { Box, Button, Text } from 'grommet';
import { useState } from 'react';
import { RemovalItem, ReplicationResult } from '../api';
import { NotesList } from './primitives';

const mono = { fontFamily: 'Consolas, "Courier New", monospace' } as const;

export function downloadText(filename: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// SPEC-007 R3 (and SPEC-023 R6): schedules, snapshots, exports, then sets, then their members — the order
// that pastes top to bottom. The backend's REMOVAL_ORDER (domain/provisioning.py) is the same.
const REMOVAL_ORDER: Record<string, number> = { schedule: 0, snapshot: 1, vlun: 2, vvset: 3, volume: 4, hostset: 5, host: 6 };

export const removalLines = (items: RemovalItem[]): string[] => {
  const out: string[] = [];
  [...items].sort((a, b) => (REMOVAL_ORDER[a.kind] ?? 9) - (REMOVAL_ORDER[b.kind] ?? 9))
    .forEach((i) => { if (!out.includes(i.command)) out.push(i.command); });
  return out;
};

/** The undo for exactly what this run created, across every apply, failed ones included (SPEC-007 R4, R6).
 *  Text for the operator; the tool never runs it. */
export function RemovalSet({ removals, notes, runId, serial }: { removals: RemovalItem[]; notes: string[]; runId: string; serial?: string }) {
  const [copied, setCopied] = useState(false);
  const lines = removalLines(removals);
  const header = [
    `# Removal of what run ${runId.slice(0, 8)} created on ${serial ?? 'the array'} — ${new Date().toISOString()}`,
    '# Review before pasting. The tool never runs these. Order: exports, VV sets, volumes, host sets, hosts.',
  ];
  const text = [...header, ...lines, ''].join('\n');
  const copy = async () => {
    try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { setCopied(false); }
  };
  return (
    <Box gap="xsmall" margin={{ top: 'small' }}>
      <Text size="small" weight={500}>Removal command set</Text>
      {lines.length === 0 ? (
        <Text size="small" color="text-weak">Nothing to remove: this run has created nothing on the array.</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            Undoes exactly what this run created, in dependency order, including anything made before a failed attempt. Objects that already
            existed are not touched.
          </Text>
          <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
            {[...header, ...lines].map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
          </Box>
          <Box direction="row" gap="small">
            <Button size="small" label={copied ? 'Copied' : 'Copy removal set'} onClick={copy} />
            <Button size="small" label="Download .txt" onClick={() => downloadText(`removal_${serial ?? 'array'}_${runId.slice(0, 8)}.txt`, text)} />
          </Box>
        </>
      )}
      {notes.length > 0 && <NotesList notes={notes} />}
    </Box>
  );
}

/** SPEC-007 pattern, two blocks, A then B. Seen live 2026-10-09: while the group exists the peer refuses
 *  `removevvset` ("Set … is currently admitted to Remote Copy Group"); after A's dismiss/remove it goes.
 *  Live 2026-11-03: a Primera peer keeps secondaries in a set, so B also removes them by name. */
/** Every apply's removal lines, newest apply first: a second apply's groups go before the partnership the first
 *  set up (removercopytarget refuses while a group still uses the target). Each line once. */
export function mergedRemovals(results: ReplicationResult[]): { removals_a: string[]; removals_b: string[] } {
  const merge = (pick: (r: ReplicationResult) => string[]) =>
    [...results].reverse().flatMap(pick).filter((line, i, all) => all.indexOf(line) === i);
  return { removals_a: merge((r) => r.removals_a), removals_b: merge((r) => r.removals_b) };
}

export function RemovalSets({ result, runId, a, b }: { result: { removals_a: string[]; removals_b: string[] }; runId: string; a: string; b: string }) {
  const [copied, setCopied] = useState(false);
  const blocks: [string, string, string[]][] = [
    [a, 'A', result.removals_a],
    [b, 'B', result.removals_b],
  ];
  const text = [
    `# Removal of what run ${runId.slice(0, 8)} configured for replication — ${new Date().toISOString()}`,
    '# Review before pasting. The tool never runs these. Paste the A block on array A FIRST, then the B block on array B.',
    ...blocks.flatMap(([name, label, lines]) => (lines.length ? [``, `# ---- ${label}: ${name}`, ...lines] : [])),
    '',
  ].join('\n');
  const copy = async () => {
    try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch { setCopied(false); }
  };
  const total = result.removals_a.length + result.removals_b.length;
  return (
    <Box gap="xsmall" margin={{ top: 'small' }} flex={false}>
      <Text size="small" weight={500}>Removal command set</Text>
      {total === 0 ? (
        <Text size="small" color="text-weak">Nothing to remove — this apply created nothing.</Text>
      ) : (
        <>
          <Text size="small" color="text-weak">
            Undoes exactly what this run created, newest first: on A each group is stopped, its volumes dismissed, then
            removed; then the target, Remote Copy and the port addresses the run set up. On B the peer volume sets, the
            secondaries, then B’s target. A line may answer “does not exist” when the array already removed it. Objects that
            already existed are not touched.
          </Text>
          <Box background="background-contrast" round="xsmall" pad="small" tabIndex={0} style={{ overflowX: 'auto' }}>
            {blocks.map(([name, label, lines]) =>
              lines.length ? (
                <Box key={label} margin={{ bottom: 'xsmall' }}>
                  <Text size="small" color="text-weak" style={mono}># ---- {label}: {name}</Text>
                  {lines.map((c, i) => <Text key={i} size="small" style={{ ...mono, whiteSpace: 'pre-wrap' }}>{c}</Text>)}
                </Box>
              ) : null,
            )}
          </Box>
          <Box direction="row" gap="small">
            <Button size="small" label={copied ? 'Copied' : 'Copy removal set'} onClick={copy} />
            <Button size="small" label="Download .txt" onClick={() => downloadText(`removal_replication_${runId.slice(0, 8)}.txt`, text)} />
          </Box>
        </>
      )}
    </Box>
  );
}
