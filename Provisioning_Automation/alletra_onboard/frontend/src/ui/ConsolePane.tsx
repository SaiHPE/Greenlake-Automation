// SPEC-019 R4: the console. Every command the tool sent for this run, live, with the device's own
// output; a prompt that runs only the read-only allowlist with the run's credential (R3); and Open
// terminal for anything else (R5). The log comes from the run's store, so a refresh loses nothing.
import { Box, Button, Select, Tab, Tabs, Text, TextInput } from 'grommet';
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
import { LogTab } from './StepContext';

// SPEC-030 R11: the panel is 40% of the window high, or 70% after Taller; the choice lasts the session.
const PANEL_CAP = '40vh';
const PANEL_TALL = '70vh';
const SIZE_KEY = 'alletra.log';
function wasMadeTaller(): boolean {
  try {
    return sessionStorage.getItem(SIZE_KEY) === 'tall';
  } catch {
    return false;
  }
}

/** Whether the log panel is open, and on which tab; App keeps it so a status line's link can open it. */
export interface LogPanel {
  open: boolean;
  tab: LogTab;
}

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
 * console one click away, as the two tabs of one panel. `activity` is the current step's events (the
 * whole run's on pages that are not a step).
 */
export function ConsolePane({
  runId,
  activity,
  log,
  onLog,
}: {
  runId: string;
  activity: RunEvent[];
  log: LogPanel;
  onLog: (next: LogPanel) => void;
}) {
  const shows = (tab: LogTab) => log.open && log.tab === tab;
  // either button opens the panel on its own tab; pressed again on that tab, it closes the panel
  const toggle = (tab: LogTab) => onLog(shows(tab) ? { ...log, open: false } : { open: true, tab });
  const [tall, setTall] = useState(wasMadeTaller);
  const cap = tall ? PANEL_TALL : PANEL_CAP;
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
  // the terminal's box: the room the panel leaves under the toolbar, above the prompt. Held in state, so
  // the terminal is made (and fitted) whenever the Commands tab draws it.
  const [host, setHost] = useState<HTMLDivElement | null>(null);
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
    if (!host) return;
    const t = new Terminal({ convertEol: true, disableStdin: true, fontSize: 12, scrollback: 20000, theme: { background: '#1b1b1b' } });
    const f = new FitAddon();
    const s = new SearchAddon();
    t.loadAddon(f);
    t.loadAddon(s);
    t.open(host);
    f.fit();
    records.current.forEach((e) => paint(t, e));
    term.current = t;
    fit.current = f;
    search.current = s;
    const onResize = () => f.fit();
    window.addEventListener('resize', onResize);
    // the box also changes without a window resize: the target list arriving, a note under the prompt
    const watch = new ResizeObserver(onResize);
    watch.observe(host);
    return () => {
      window.removeEventListener('resize', onResize);
      watch.disconnect();
      t.dispose();
      term.current = null;
      fit.current = null;
    };
  }, [host]);

  const resize = () => {
    const next = !tall;
    setTall(next);
    try {
      if (next) sessionStorage.setItem(SIZE_KEY, 'tall');
      else sessionStorage.removeItem(SIZE_KEY);
    } catch {
      // storage refused: the size lasts until the page reloads
    }
    requestAnimationFrame(() => fit.current?.fit());
  };
  const sizeButton = <Button size="small" label={tall ? 'Shorter' : 'Taller'} onClick={resize} />;
  // Grommet's tabs take Tab and Enter; the arrow keys also move between them (SPEC-030 R12), on a tab only
  const arrowsBetweenTabs = (event: React.KeyboardEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (target.getAttribute('role') !== 'tab' || (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight')) return;
    event.preventDefault();
    const index = event.key === 'ArrowLeft' ? 0 : 1;
    onLog({ open: true, tab: index === 0 ? 'activity' : 'commands' });
    event.currentTarget.querySelectorAll<HTMLElement>('[role="tab"]')[index]?.focus();
  };

  const run = async () => {
    if (busy) return;
    const text = command.trim();
    if (!targets[target]) {
      setNote('Nothing was sent: this run holds no credential for this array.');
      return;
    }
    if (!text) {
      setNote('Nothing was sent: type a read-only command first.');
      return;
    }
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
    if (!targets[target]) {
      setNote('No terminal was opened: this run holds no credential for this array.');
      return;
    }
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
    // it may shrink, down to the panel's minimum, so a tall panel never pushes the step's footer away
    <Box flex={{ grow: 0, shrink: 1 }} basis="auto" border={{ side: 'top', color: 'border-weak' }} background="background-contrast">
      <Box direction="row" align="center" justify="between" gap="small" pad={{ horizontal: 'medium', vertical: 'xsmall' }} flex={false}>
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
            aria-expanded={shows('activity')}
            active={shows('activity')}
          />
          <Button
            size="small"
            icon={<TerminalIcon size="small" />}
            label={`Console (${count} command${count === 1 ? '' : 's'})`}
            onClick={() => toggle('commands')}
            aria-expanded={shows('commands')}
            active={shows('commands')}
          />
        </Box>
      </Box>
      {/* One panel, as high as its cap (40% of the window, 70% after Taller), so a tab change does not move
          the step above; the list and the terminal fill it and scroll inside. */}
      {log.open && (
        <Box height={{ min: 'small', height: cap }} background="background-front" border={{ side: 'top', color: 'border-weak' }}>
          <Tabs
            flex
            activeIndex={log.tab === 'activity' ? 0 : 1}
            onActive={(i) => onLog({ open: true, tab: i === 0 ? 'activity' : 'commands' })}
            onKeyDown={arrowsBetweenTabs}
          >
            <Tab title={`Activity (${activity.length})`}>
              <Box height="100%" pad={{ horizontal: 'medium', vertical: 'small' }} gap="xsmall">
                <Box direction="row" justify="end" flex={false}>
                  {sizeButton}
                </Box>
                <ActivityTimeline events={activity} />
              </Box>
            </Tab>
            <Tab title={`Commands (${count})`}>
              <Box height="100%" pad={{ horizontal: 'medium', bottom: 'small' }} gap="xsmall">
                <Box direction="row" gap="small" align="center" justify="end" pad={{ top: 'xsmall' }} wrap flex={false}>
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
                  <Button size="small" icon={<TerminalIcon size="small" />} label="Open terminal" onClick={terminal} />
                  {sizeButton}
                </Box>
                {/* what the toolbar and the prompt leave, never below xsmall */}
                <Box ref={setHost} flex height={{ min: 'xsmall' }} overflow="hidden" />
                <Box direction="row" gap="small" align="center" flex={false}>
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
                  <Button size="small" label={busy ? 'Running…' : 'Run'} onClick={run} />
                </Box>
                {note && <Text size="small" color="text-weak">{note}</Text>}
              </Box>
            </Tab>
          </Tabs>
        </Box>
      )}
    </Box>
  );
}
