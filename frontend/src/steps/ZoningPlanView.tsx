import { Box, Button, CheckBox, Text, TextInput } from 'grommet';
import { useMemo, useState } from 'react';
import {
  AliasedWwpn, FabricZonePlan, ZoningPlan, ZoningStageResult, renderZoningCommands, stageZoning,
} from '../api';
import { InlineNotification, Surface } from '../ui/primitives';

// ADR 0004 (refined; write path added 2026-08-15): the two-part zoning screen.
//   1. The current-connection map — pairs the fabric's effective config ALREADY covers, shown
//      pre-selected and disabled: nothing the tool proposes can recreate them.
//   2. The operator-selected builder — candidates are a MENU: the operator picks which array
//      ports serve each host, names the aliases, then either generates the command preview for
//      the SAN team or STAGES the zones (alicreate/zonecreate/cfgadd + cfgsave, DEFINED config
//      only). The backend's write surface has no delete verb and no cfgenable — existing zones
//      cannot be touched, and activation is always a manual SAN-team action (the hand-off).
// Commands are rendered by the BACKEND (POST /zoning/render) so the grammar has exactly one
// implementation.

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };

const pairKey = (host: string, arr: string) => `${host}|${arr}`;

function hostLabel(w: AliasedWwpn): string {
  // QLogic HBAs advertise no HN: on the fabric — fall back to the WWPN as the host's identity.
  return w.host_name || w.display;
}

function AliasRow({ w, value, onChange }: { w: AliasedWwpn; value: string; onChange: (v: string) => void }) {
  const label = w.role === 'array' ? `Array port ${w.nsp}` : hostLabel(w);
  const others = w.existing_aliases.filter((a) => a !== value);
  return (
    <Box direction="row" gap="small" align="center" pad={{ vertical: 'xxsmall' }} wrap>
      <Box width="190px" flex={false}>
        <Text size="small" truncate>{label}</Text>
      </Box>
      <Box width="215px" flex={false}><Text size="small" style={mono}>{w.display}</Text></Box>
      <Box width="300px" flex={false}>
        <TextInput size="small" value={value} placeholder="Enter an alias name" onChange={(e) => onChange(e.target.value)} />
      </Box>
      {others.length > 0 && <Text size="xsmall" color="text-weak">existing: {others.join(', ')}</Text>}
    </Box>
  );
}

function FabricBuilder({
  fab, aliases, setAlias, selected, toggle,
}: {
  fab: FabricZonePlan;
  aliases: Record<string, string>;
  setAlias: (wwpn: string, v: string) => void;
  selected: Record<string, boolean>;
  toggle: (key: string, on: boolean) => void;
}) {
  const zoned = useMemo(() => new Set(fab.already_zoned.map(([h, a]) => pairKey(h, a))), [fab]);
  const portByWwpn = useMemo(() => {
    const map: Record<string, AliasedWwpn> = {};
    fab.array_ports.forEach((p) => { map[p.wwpn] = p; });
    return map;
  }, [fab]);

  if (fab.hosts.length === 0 && fab.array_ports.length === 0) {
    return <Text size="small" color="text-weak">No host or array ports online on this fabric.</Text>;
  }
  return (
    <Box gap="small">
      {/* Part 1+2 combined per host: current connections are the disabled, pre-selected boxes. */}
      {fab.hosts.map((host) => (
        <Box key={host.wwpn} gap="xxsmall" pad={{ bottom: 'xsmall' }} border={{ side: 'bottom', color: 'border' }}>
          <Box direction="row" gap="small" align="center">
            <Text size="small" weight={600}>{hostLabel(host)}</Text>
            <Text size="small" color="text-weak" style={mono}>{host.display}</Text>
            {host.host_source === 'switch' && (
              <Text size="xsmall" color="text-weak">identified from the fabric name server</Text>
            )}
          </Box>
          <Box direction="row" gap="medium" wrap>
            {fab.array_ports.map((port) => {
              const key = pairKey(host.wwpn, port.wwpn);
              const isZoned = zoned.has(key);
              return (
                <CheckBox
                  key={key}
                  checked={isZoned || Boolean(selected[key])}
                  disabled={isZoned}
                  label={
                    <Text size="small" color={port.caution && !isZoned ? 'status-warning' : undefined}>
                      {port.nsp || portByWwpn[port.wwpn]?.display}
                      {isZoned && <Text size="xsmall" color="text-weak"> (zoned)</Text>}
                      {port.caution && !isZoned && (
                        <Text size="xsmall" color="status-warning"> ⚠ {port.caution}</Text>
                      )}
                    </Text>
                  }
                  onChange={(e) => toggle(key, e.target.checked)}
                />
              );
            })}
          </Box>
        </Box>
      ))}

      <Text size="small" weight={600}>Alias names</Text>
      {[...fab.hosts, ...fab.array_ports].map((w) => (
        <AliasRow key={w.wwpn} w={w} value={aliases[w.wwpn] ?? ''} onChange={(v) => setAlias(w.wwpn, v)} />
      ))}
    </Box>
  );
}

export function ZoningPlanView({ plan, runId, running, stageResult }: {
  plan: ZoningPlan;
  runId: string;
  running: boolean;
  stageResult: ZoningStageResult | null;
}) {
  const [aliases, setAliases] = useState<Record<string, string>>(() => {
    const seed: Record<string, string> = {};
    plan.fabrics.forEach((f) => [...f.hosts, ...f.array_ports].forEach((w) => { seed[w.wwpn] = w.suggested_alias; }));
    return seed;
  });
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [commands, setCommands] = useState<Record<string, string[]> | null>(null);
  const [skipped, setSkipped] = useState<Record<string, string[]> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setAlias = (wwpn: string, v: string) => { setAliases((a) => ({ ...a, [wwpn]: v })); setCommands(null); };
  const toggle = (key: string, on: boolean) => { setSelected((s) => ({ ...s, [key]: on })); setCommands(null); };

  const selectedPairs: [string, string][] = plan.fabrics.flatMap((f) =>
    f.pairs.filter(([h, a]) => selected[pairKey(h, a)]),
  );
  const totalZoned = plan.fabrics.reduce((n, f) => n + f.already_zoned.length, 0);
  // A selected pair whose member has no alias name cannot be zoned — say so BEFORE the operator
  // clicks (the live rc.1 test ticked the alias-less 0:3:4 and got an unchanged preview with no
  // explanation). The backend reports the same condition authoritatively after rendering.
  const unnamed = selectedPairs.filter(([h, a]) => !(aliases[h] ?? '').trim() || !(aliases[a] ?? '').trim()).length;

  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await renderZoningCommands(plan, aliases, selectedPairs);
      setCommands(res.commands);
      setSkipped(res.skipped);
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  const stage = async () => {
    setBusy(true);
    setError(null);
    try {
      await stageZoning(runId, plan, aliases, selectedPairs);  // result arrives via run events
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Box gap="medium">
      <Text size="small" color="text-weak">
        Existing zones are pre-selected and cannot be recreated. Select the array ports that should
        serve each host, name the aliases, then preview the commands and <b>stage the zones</b> —
        written to the switch&apos;s <b>defined configuration only</b> (cfgsave). The tool cannot
        delete zones and never runs cfgenable: <b>activation is always a manual SAN-team action</b>.
      </Text>
      {error && <InlineNotification tone="critical" title="The request failed" message={error} />}

      {plan.fabrics.map((fab) => (
        <Surface key={fab.fabric} title={`${fab.fabric} — ${fab.switch_host} (cfg ${fab.active_cfg || 'not read'})`}>
          <FabricBuilder fab={fab} aliases={aliases} setAlias={setAlias} selected={selected} toggle={toggle} />
          {skipped && (skipped[fab.fabric] ?? []).length > 0 && (
            <Box margin={{ top: 'small' }}>
              <InlineNotification
                tone="warning"
                title="Not included in the preview"
                message={skipped[fab.fabric].join(' · ')}
              />
            </Box>
          )}
          {commands && commands[fab.fabric] && (
            <Box background="background-contrast" round="xsmall" pad="small" margin={{ top: 'small' }}>
              {commands[fab.fabric].length === 0
                ? <Text size="small" color="text-weak">No commands — nothing selected that does not already exist.</Text>
                : commands[fab.fabric].map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
            </Box>
          )}
        </Surface>
      ))}

      <Box direction="row" gap="small" align="center" wrap>
        <Button
          busy={busy}
          disabled={selectedPairs.length === 0}
          label={`Generate command preview (${selectedPairs.length} new zone${selectedPairs.length === 1 ? '' : 's'})`}
          onClick={generate}
        />
        <Button
          primary
          busy={busy || running}
          disabled={selectedPairs.length === 0 || unnamed > 0 || !commands}
          label={`Stage ${selectedPairs.length} zone${selectedPairs.length === 1 ? '' : 's'} on the switches`}
          onClick={stage}
        />
        {totalZoned > 0 && (
          <Text size="small" color="text-weak">{totalZoned} pair(s) already zoned — excluded automatically.</Text>
        )}
        {unnamed > 0 && (
          <Text size="small" color="status-warning">
            {unnamed} selected pair(s) need an alias name before they can be zoned.
          </Text>
        )}
        {!commands && selectedPairs.length > 0 && (
          <Text size="small" color="text-weak">Preview first — staging runs exactly the commands shown.</Text>
        )}
      </Box>

      {stageResult && (
        <Surface title="Staged to the defined configuration">
          {stageResult.fabrics.map((fr) => (
            <Box key={fr.fabric} gap="xxsmall" margin={{ bottom: 'small' }}>
              <Text size="small" weight={600}>{fr.fabric} — {fr.switch_host}</Text>
              {fr.error && <InlineNotification tone="critical" title={`${fr.fabric}: staging failed`} message={fr.error} />}
              {!fr.error && fr.staged.length === 0 && (
                <Text size="small" color="text-weak">Nothing to stage on this fabric.</Text>
              )}
              {fr.staged.length > 0 && (
                <Box background="background-contrast" round="xsmall" pad="small">
                  {fr.staged.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
                  <Text size="small" style={mono}>cfgsave  (committed — defined configuration only)</Text>
                </Box>
              )}
              {fr.verified && (
                <Text size="small" color="status-ok">
                  Verified on read-back: zones present in the defined configuration; effective configuration unchanged.
                </Text>
              )}
              {fr.handoff && (
                <Text size="small">
                  Manual activation (SAN team, maintenance window): <Text size="small" style={mono} weight={600}>{fr.handoff}</Text>
                </Text>
              )}
            </Box>
          ))}
          {stageResult.warning && (
            <InlineNotification tone="warning" title="Activation pending" message={stageResult.warning} />
          )}
        </Surface>
      )}

      {plan.offline_hosts.length > 0 && (
        <Surface title={`Offline — cable and power the host, then run the plan again (${plan.offline_hosts.length})`}>
          {plan.offline_hosts.map((h, i) => <Text key={i} size="small" color="status-warning">{h}</Text>)}
        </Surface>
      )}
      {plan.notes.map((n, i) => <Text key={i} size="small" color="text-weak">• {n}</Text>)}
    </Box>
  );
}
