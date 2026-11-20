import { Box, Button, CheckBox, DataTable, Heading, Text } from 'grommet';
import { ReactNode, useMemo, useState } from 'react';
import { FabricZonePlan, ZoningPlan } from '../api';
import { TableSummary } from './primitives';
import { downloadText } from './RemovalSets';
import { NoValue, StatusIndicator } from './status';
import { exportText, fabricTitle, HbaRow, hbaRows, mono, PAIR } from './zoningHelpers';

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

export function FabricOverview({ plan }: { plan: ZoningPlan }) {
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

export function CurrentZoningTable({ plan }: { plan: ZoningPlan }) {
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
      right={<Button size="small" label="Export .txt" onClick={() => downloadText('current-zoning.txt', exportText(plan, rows))} />}
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
export function CommandSet({ fab, commands }: { fab: FabricZonePlan; commands: string[] }) {
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
  const save = () => downloadText(
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
