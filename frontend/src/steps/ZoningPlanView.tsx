import { Box, Button, CheckBox, Text, TextInput } from 'grommet';
import { useMemo, useState } from 'react';
import { AliasedWwpn, FabricZonePlan, ZoningPlan, renderZoningCommands } from '../api';
import { InlineNotification, Surface } from '../ui/primitives';

// ADR 0004 + ADR 0012: the two-part zoning screen.
//   1. The current-connection map — pairs the fabric's effective config ALREADY covers, shown
//      pre-selected and disabled: nothing the tool proposes can recreate them.
//   2. The operator-selected builder — candidates are a MENU: the operator picks which array ports
//      serve each host, names the aliases, and generates the COMMAND SET. That set is the
//      deliverable; the tool cannot run it. It has no switch write path at any layer.
// Commands are rendered by the BACKEND (POST /zoning/render) so the grammar has exactly one
// implementation.

const mono = { fontFamily: 'ui-monospace, Consolas, monospace' };

const pairKey = (host: string, arr: string) => `${host}|${arr}`;

/** The command set for one fabric.
 *
 * `cfgenable` is separated from the additive commands on purpose. Until 2026-09-02 it was rendered
 * in the same block, weight and colour as commands the tool had just executed, so the screen drew no
 * boundary between "done" and "yours to do" — and an operator could reasonably select the whole
 * block and paste it, activating the configuration. Activation replaces the effective config
 * fabric-wide; it belongs to the SAN team, in a window, deliberately.
 */
function CommandSet({ commands }: { commands: string[] }) {
  const additive = commands.filter((c) => !c.startsWith('cfgenable'));
  const activation = commands.filter((c) => c.startsWith('cfgenable'));
  const [copied, setCopied] = useState(false);

  if (commands.length === 0) {
    return (
      <Box margin={{ top: 'small' }}>
        <Text size="small" color="text-weak">No commands — nothing selected that does not already exist.</Text>
      </Box>
    );
  }
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(additive.join('\n'));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);   // clipboard blocked; the text is on screen to select by hand
    }
  };
  return (
    <Box gap="xsmall" margin={{ top: 'small' }}>
      <Box background="background-contrast" round="xsmall" pad="small">
        {additive.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
      </Box>
      <Box direction="row" gap="small" align="center" wrap>
        <Button size="small" label={copied ? 'Copied' : 'Copy commands'} onClick={copy} />
        <Text size="small" color="text-weak">Additive only. Creates nothing that already exists, and removes nothing.</Text>
      </Box>
      {activation.length > 0 && (
        <Box
          border={{ color: 'status-warning', side: 'left', size: '3px' }}
          pad={{ left: 'small', vertical: 'xsmall' }}
        >
          <Text size="small" weight={600}>Then, separately — activation</Text>
          <Text size="small" color="text-weak">
            Not part of the paste above. This replaces the effective configuration across the whole
            fabric, so the SAN team runs it in a maintenance window once they are satisfied.
          </Text>
          {activation.map((c, i) => <Text key={i} size="small" style={mono}>{c}</Text>)}
        </Box>
      )}
    </Box>
  );
}

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

export function ZoningPlanView({ plan }: { plan: ZoningPlan }) {
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


  return (
    <Box gap="medium">
      <Text size="small" color="text-weak">
        Existing zones are pre-selected and cannot be recreated. Select the array ports that should
        serve each host and name the aliases, then generate the command set. <b>This tool never
        writes to a switch</b> — copy the commands to your SAN team, who review and apply them.
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
            <CommandSet commands={commands[fab.fabric]} />
          )}
        </Surface>
      ))}

      <Box direction="row" gap="small" align="center" wrap>
        <Button
          busy={busy}
          disabled={selectedPairs.length === 0}
          primary
          label={`Generate command set (${selectedPairs.length} new zone${selectedPairs.length === 1 ? '' : 's'})`}
          onClick={generate}
        />
        {totalZoned > 0 && (
          <Text size="small" color="text-weak">{totalZoned} pair(s) already zoned — excluded automatically.</Text>
        )}
        {unnamed > 0 && (
          <Text size="small" color="status-warning">
            {unnamed} selected pair(s) need an alias name before they can be zoned.
          </Text>
        )}
        {commands && (
          <Text size="small" color="text-weak">Give these to your SAN team to apply.</Text>
        )}
      </Box>


      {plan.offline_hosts.length > 0 && (
        <Surface title={`Offline — cable and power the host, then run the plan again (${plan.offline_hosts.length})`}>
          {plan.offline_hosts.map((h, i) => <Text key={i} size="small" color="status-warning">{h}</Text>)}
        </Surface>
      )}
      {plan.notes.map((n, i) => <Text key={i} size="small" color="text-weak">• {n}</Text>)}
    </Box>
  );
}
