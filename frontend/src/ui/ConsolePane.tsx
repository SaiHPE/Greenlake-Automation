// SPEC-019 R4: the console. Every command the tool sent for this run, live, with the device's own
// output; a prompt that runs only the read-only allowlist with the run's credential (R3); and Open
// terminal for anything else (R5). The log comes from the run's store, so a refresh loses nothing.
import { Box, Button, Select, Text, TextInput } from 'grommet';
import { Copy, Download, Search, Terminal as TerminalIcon, Time } from 'grommet-icons';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { SearchAddon } from '@xterm/addon-search';
import '@xterm/xterm/css/xterm.css';
import { useEffect, useRef, useState } from 'react';
import {
  CommandRecord,
  consoleLogTxtUrl,
  consoleStreamUrl,
  getConsoleLog,
  getConsoleTargets,
  openConsoleTerminal,
  RunEvent,
  runConsoleCommand,
} from '../api';
import { ActivityTimeline } from './primitives';

const DIM = '\x1b[2m';
const GREY = '\x1b[90m';
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const RESET = '\x1b[0m';

export function recordLines(e: CommandRecord): string[] {
  const at = (e.at || '').slice(11, 19);
  const head = `${at}  ${e.target} (${e.transport})  ${e.command}  ${e.duration_s}s  ${e.result}`;
  const out = (e.output || '').replace(/\s+$/, '');
  return [head, ...(out ? out.split(/\r?\n/).map((line) => `    ${line}`) : [])];
}

function paint(term: Terminal, e: CommandRecord) {
  const at = (e.at || '').slice(11, 19);
  const colour = e.ok ? GREEN : RED;
  term.writeln(`${GREY}${at}${RESET}  ${e.target} (${e.transport})  ${e.command}  ${GREY}${e.duration_s}s${RESET}  ${colour}${e.result}${RESET}`);
  const out = (e.output || '').replace(/\s+$/, '');
  if (out) for (const line of out.split(/\r?\n/)) term.writeln(`${DIM}    ${line}${RESET}`);
}

/**
 * The bar under every step: the step's last event always visible, its full activity list and the
 * console one click away. `activity` is the current step's events (the whole run's on pages that are
 * not a step).
 */
export function ConsolePane({ runId, activity }: { runId: string; activity: RunEvent[] }) {
  const [panel, setPanel] = useState<'none' | 'activity' | 'console'>('none');
  const open = panel === 'console';
  const toggle = (which: 'activity' | 'console') => setPanel((p) => (p === which ? 'none' : which));
  const [count, setCount] = useState(0);
  const [targets, setTargets] = useState<Record<string, string>>({});
  const [target, setTarget] = useState('array');
  const [command, setCommand] = useState('');
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState('');
  const [find, setFind] = useState('');
  const history = useRef<string[]>([]);
  const cursor = useRef(-1);
  const records = useRef<CommandRecord[]>([]);
  const host = useRef<HTMLDivElement>(null);
  const term = useRef<Terminal | null>(null);
  const fit = useRef<FitAddon | null>(null);
  const search = useRef<SearchAddon | null>(null);
  const lastSeq = useRef(0);

  // The log and the live stream run whether or not the pane is open, so the count stays true.
  useEffect(() => {
    let closed = false;
    records.current = [];
    lastSeq.current = 0;
    setCount(0);
    const add = (e: CommandRecord) => {
      if (e.seq <= lastSeq.current) return;
      lastSeq.current = e.seq;
      records.current.push(e);
      setCount(records.current.length);
      if (term.current) paint(term.current, e);
    };
    getConsoleTargets(runId).then((t) => !closed && setTargets(t.targets)).catch(() => undefined);
    const source = new EventSource(consoleStreamUrl(runId));
    source.onmessage = (message) => {
      try {
        add(JSON.parse(message.data) as CommandRecord);
      } catch {
        /* heartbeat or partial frame */
      }
    };
    getConsoleLog(runId)
      .then((log) => {
        if (closed) return;
        log.commands.sort((a, b) => a.seq - b.seq).forEach(add);
      })
      .catch(() => undefined);
    return () => {
      closed = true;
      source.close();
    };
  }, [runId]);

  useEffect(() => {
    if (!open || !host.current || term.current) return;
    const t = new Terminal({ convertEol: true, disableStdin: true, fontSize: 12, scrollback: 20000, theme: { background: '#1b1b1b' } });
    const f = new FitAddon();
    const s = new SearchAddon();
    t.loadAddon(f);
    t.loadAddon(s);
    t.open(host.current);
    f.fit();
    records.current.forEach((e) => paint(t, e));
    term.current = t;
    fit.current = f;
    search.current = s;
    const onResize = () => f.fit();
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      t.dispose();
      term.current = null;
    };
  }, [open]);

  const run = async () => {
    const text = command.trim();
    if (!text || busy) return;
    history.current = [text, ...history.current.filter((h) => h !== text)].slice(0, 50);
    cursor.current = -1;
    setBusy(true);
    setNote('');
    try {
      const out = await runConsoleCommand(runId, text, target);
      if (out.refused) setNote(out.output);
      else setCommand('');
    } catch (err) {
      setNote(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  const onKey = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') run();
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
      event.preventDefault();
      const next = Math.max(-1, Math.min(history.current.length - 1, cursor.current + (event.key === 'ArrowUp' ? 1 : -1)));
      cursor.current = next;
      setCommand(next < 0 ? '' : history.current[next]);
    }
  };

  const copy = () => {
    const text = records.current.flatMap(recordLines).join('\n');
    navigator.clipboard?.writeText(text).then(() => setNote('Copied the whole log.')).catch(() => setNote('The browser refused the clipboard; use Download .txt.'));
  };

  const terminal = async () => {
    try {
      const out = await openConsoleTerminal(runId, target);
      setNote(out.launched ? `Opened a terminal: ${out.command} (type the password there).` : out.error || `Run: ${out.command}`);
    } catch (err) {
      setNote(err instanceof Error ? err.message : String(err));
    }
  };

  const targetOptions = Object.entries(targets).map(([key, who]) => ({ key, label: `${key === 'peer' ? 'Peer' : 'Array'} · ${who}` }));
  const last = activity[activity.length - 1];

  return (
    <Box flex={false} border={{ side: 'top', color: 'border-weak' }} background="background-contrast">
      <Box direction="row" align="center" justify="between" gap="small" pad={{ horizontal: 'medium', vertical: 'xsmall' }}>
        <Box direction="row" gap="xsmall" align="center" flex style={{ minWidth: 0 }}>
          <Time size="small" color="icon-weak" aria-hidden />
          <Text size="small" color="text-weak" truncate>
            {last ? `${new Date(last.created_at).toLocaleTimeString()}  ${last.message}` : 'No activity yet'}
          </Text>
        </Box>
        <Box direction="row" gap="small" flex={false}>
          <Button
            size="small"
            label={`Activity (${activity.length})`}
            onClick={() => toggle('activity')}
            aria-expanded={panel === 'activity'}
            primary={panel === 'activity'}
          />
          <Button
            size="small"
            icon={<TerminalIcon size="small" />}
            label={`Console (${count} command${count === 1 ? '' : 's'})`}
            onClick={() => toggle('console')}
            aria-expanded={open}
            primary={open}
          />
        </Box>
      </Box>
      {panel === 'activity' && (
        <Box pad={{ horizontal: 'medium', bottom: 'small' }} background="background-front" border={{ side: 'top', color: 'border-weak' }}>
          <Box pad={{ top: 'small' }}>
            <ActivityTimeline events={activity} />
          </Box>
        </Box>
      )}
      {open && (
        <Box pad={{ horizontal: 'medium', bottom: 'small' }} gap="xsmall" background="background-front" border={{ side: 'top', color: 'border-weak' }}>
          <Box direction="row" gap="small" align="center" justify="end" pad={{ top: 'xsmall' }} wrap>
            <Box width="small">
              <TextInput
                size="xsmall"
                icon={<Search size="small" />}
                placeholder="Find"
                value={find}
                onChange={(event) => setFind(event.target.value)}
                onKeyDown={(event) => event.key === 'Enter' && search.current?.findNext(find)}
                aria-label="Find in the console"
              />
            </Box>
            <Button size="small" icon={<Copy size="small" />} label="Copy" onClick={copy} />
            <Button size="small" icon={<Download size="small" />} label="Download .txt" href={consoleLogTxtUrl(runId)} />
            <Button size="small" icon={<TerminalIcon size="small" />} label="Open terminal" onClick={terminal} disabled={!targets[target]} />
          </Box>
          <div ref={host} style={{ height: 220, width: '100%' }} />
          <Box direction="row" gap="small" align="center">
            {targetOptions.length > 1 && (
              <Box width="small">
                <Select
                  size="small"
                  options={targetOptions}
                  labelKey="label"
                  valueKey={{ key: 'key', reduce: true }}
                  value={target}
                  onChange={({ value }) => setTarget(value)}
                  a11yTitle="Which array the command runs on"
                />
              </Box>
            )}
            <Box flex>
              <TextInput
                size="small"
                placeholder={targets[target] ? 'showvlun -a -host ESX1   (read-only show… commands, checkhealth)' : 'This run holds no array credential'}
                value={command}
                disabled={!targets[target] || busy}
                onChange={(event) => setCommand(event.target.value)}
                onKeyDown={onKey}
                a11yTitle="Read-only command"
              />
            </Box>
            <Button size="small" primary label={busy ? 'Running…' : 'Run'} onClick={run} disabled={!command.trim() || busy || !targets[target]} />
          </Box>
          {note && <Text size="small" color="text-weak">{note}</Text>}
        </Box>
      )}
    </Box>
  );
}
