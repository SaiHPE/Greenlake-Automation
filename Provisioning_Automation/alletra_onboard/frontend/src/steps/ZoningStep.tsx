import { Box, Button, Notification, Spinner, Text } from 'grommet';
import { useState } from 'react';
import { RunEvent, RunRecord, zoningPreview, ZoningReport } from '../api';
import { EventLog, Section } from '../components';

interface Props {
  runId: string;
  run: RunRecord | null;
  events: RunEvent[];
  onDone: () => void;
}

function latestReport(events: RunEvent[]): ZoningReport | null {
  const event = [...events].reverse().find((e) =>
    ['zoning.previewed', 'zoning.proper', 'zoning.applied'].includes(e.event_type),
  );
  return (event?.data?.report as ZoningReport) ?? null;
}

export function ZoningStep({ runId, run, events, onDone }: Props) {
  const [error, setError] = useState<string | null>(null);
  const running = run?.status === 'running';
  const report = latestReport(events);
  const missing = report ? report.expected.filter((z) => !z.present) : [];

  // Roll the per-(host,fabric) rows up to one line per host: odd ✓/✗, even ✓/✗.
  const byHost: Record<string, { odd: boolean; even: boolean }> = {};
  report?.expected.forEach((z) => {
    const host = z.name.replace(/_(odd|even)$/, '');
    byHost[host] = byHost[host] || { odd: false, even: false };
    byHost[host][z.fabric] = z.present;
  });

  const call = (fn: () => Promise<unknown>) => async () => {
    setError(null);
    try {
      await fn();
    } catch (exc: any) {
      setError(String(exc.message ?? exc));
    }
  };

  return (
    <Box gap="medium">
      <Section title="Verify SAN zoning (both fabrics)">
        <Text size="small" color="text-weak">
          Read-only, <b>from the array</b> (no switch login): the fabric name server is zoning-filtered,
          so what each array FC port can see is its effective zoning. Each host should be zoned on
          BOTH fabrics (odd/F1 and even/F2).
        </Text>
        <Box direction="row" gap="small" align="center">
          <Button primary label={running ? 'Working…' : report ? 'Re-verify' : 'Verify zoning'} disabled={running} onClick={call(() => zoningPreview(runId))} />
          {running && <Spinner />}
        </Box>
        {error && <Notification status="critical" title="Zoning step failed" message={error} onClose={() => setError(null)} />}
      </Section>

      {report?.proper && (
        <Notification status="normal" title="Zoning is correct on both fabrics — verified from the array, no switch" />
      )}

      {report && Object.keys(byHost).length > 0 && (
        <Section title="Per-host zoning (from showportdev ns)">
          {Object.entries(byHost).map(([host, f]) => (
            <Text key={host} size="small" color={f.odd && f.even ? undefined : 'status-warning'}>
              <b>{host}</b> — odd/F1: {f.odd ? 'zoned' : 'MISSING'} · even/F2: {f.even ? 'zoned' : 'MISSING'}
            </Text>
          ))}
        </Section>
      )}

      {report && report.unverified_hosts.length > 0 && (
        <Notification
          status="warning"
          title={`Could not confirm ${report.unverified_hosts.length} host(s) — not zoned OR offline`}
          message={`The array sees no login for: ${report.unverified_hosts.join(', ')}. The array can't tell "no zone" from "host powered off" — confirm the host is up; if it is, it's a real zoning gap.`}
        />
      )}

      {report && report.notes.length > 0 && (
        <Section title="Notes">
          {report.notes.map((n, i) => <Text key={i} size="small" color="text-weak">• {n}</Text>)}
        </Section>
      )}

      {report && !report.proper && missing.length > 0 && (
        <Section title={`Zoning plan — ${missing.length} zone(s) to add`}>
          <Text size="small">
            The tool does <b>not</b> write to the switch. Hand these <b>additive</b> commands to the SAN
            team to run on each fabric — they activate with <b>cfgenable</b> (never cfgsave-alone) and
            leave existing zones untouched — then click <b>Re-verify</b> above.
          </Text>
          {report.remediations.map((rem) => (
            <Box key={rem.switch_host} gap="xsmall" pad={{ vertical: 'small' }}>
              <Text size="small" weight="bold">{rem.fabric} fabric — {rem.switch_host} (cfg {rem.cfg_name})</Text>
              <Box background="background-contrast" round="xsmall" pad="small">
                {rem.commands.map((c, i) => (
                  <Text key={i} size="small" style={{ fontFamily: 'monospace' }}>{c}</Text>
                ))}
              </Box>
            </Box>
          ))}
        </Section>
      )}

      {report && (
        <Button label="Continue →" primary={report.proper} onClick={onDone} alignSelf="start" />
      )}

      <Section title="Activity"><EventLog events={events.filter((e) => e.phase === 'STORAGE_ZONING')} /></Section>
    </Box>
  );
}
