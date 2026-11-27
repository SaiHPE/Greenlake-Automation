import { Box, Button, CheckBox, Text, TextInput } from 'grommet';
import { StatusGood } from 'grommet-icons';
import { ComponentProps, ReactNode, useState } from 'react';
import { RunEvent, ZoningPlan, ZoningRenderResult, renderZoningCommands } from '../api';
import { DoneList, Section } from './blocks';
import { InlineNotification, NotesList, Surface } from './primitives';
import { ZoningApplyView } from './ZoningApplyView';
import {
  aliasProblem,
  aliasSuggestion,
  fabricTitle,
  hostName,
  hostSource,
  mono,
  nameClashes,
  pairKey,
  wwpnTitle,
} from './zoningHelpers';
import { CommandSet, CurrentZoningTable, FabricOverview } from './ZoningSwitchView';

// ADR 0004 + ADR 0012: the zoning screen, redesigned after the 2026-09-12 live test
// (docs/ux/ZONING-REDESIGN.md), then calmed by SPEC-030 (BL-59 P8a). One step, in parts:
//   A  Fabrics          — what each declared switch is, and which array ports sit on it   } folded: What the
//   B  Current zoning   — one row per host HBA port: what it can reach today, and by which zone } switches hold
//   C  Design new zones — only HBA ports that need zones; array ports grouped by controller node  } Draft zones,
//   D  Names            — only the WWPNs that take part in a selected new zone             } until generated
//   E  Command set      — the deliverable, per fabric; activation kept apart               (Hand off)
// The data is exactly what the backend plan carries; commands are rendered by POST /zoning/render so
// the grammar has one implementation. The tool has no switch write path at any layer.

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
export function ZoningPlanView({
  plan, runId, done = [], events = [], running = false, onCheckAgain,
}: {
  plan: ZoningPlan;
  runId?: string;
  done?: DoneItem[];
  events?: RunEvent[];
  running?: boolean;
  onCheckAgain?: () => void;
}) {
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
    } catch (exc: unknown) {
      setError(exc instanceof Error ? exc.message : String(exc));
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
          description="Copy-paste stays the default deliverable: the SAN team reviews the paste block, applies it on the named switch, then saves and activates in a window. You can also opt in to direct Brocade apply below. Re-check zoning afterwards: the array shows each new login."
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

      {result && (result.warnings?.apply ?? []).length > 0 && (
        <InlineNotification
          tone="warning"
          title="Direct switch apply unavailable"
          message={<NotesList notes={result.warnings!.apply} />}
        />
      )}

      {runId && (
        <ZoningApplyView
          runId={runId}
          applyPlanId={result?.apply_plan_id ?? null}
          applyFabrics={result?.apply_fabrics ?? []}
          events={events}
          running={running}
          onCheckAgain={onCheckAgain}
        />
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
