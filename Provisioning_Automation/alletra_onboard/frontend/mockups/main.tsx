import { Box, Button, CheckBox, Grommet, Select, Text } from 'grommet';
import { hpe } from 'grommet-theme-hpe';
import { deepMerge } from 'grommet/utils';
import { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { theme } from '../src/theme';
import { NotesContext } from './kit';
import { Screen } from './screen';
import { discovery } from './screens/Discovery';
import { finish } from './screens/Finish';
import { handoff } from './screens/Handoff';
import { home } from './screens/Home';
import { overview } from './screens/Overview';
import { prerequisites } from './screens/Prerequisites';
import { replication } from './screens/Replication';
import { mode, sheet } from './screens/SheetMode';
import { startScreen } from './screens/Start';
import { stopped } from './screens/Stopped';

const SCREENS: Screen[] = [home, prerequisites, sheet, mode, overview, discovery, replication, handoff, stopped, finish];
const WIDTHS = [
  { label: 'Jump box 1366 × 768', w: 1366, h: 768 },
  { label: 'Small laptop 1080 × 720', w: 1080, h: 720 },
  { label: 'Large monitor 1920 × 1080', w: 1920, h: 1080 },
  { label: 'Fit this window', w: 0, h: 0 },
];

const parseHash = () => {
  const [id, state] = window.location.hash.slice(1).split('/');
  return { id: id || 'M0', state };
};

/**
 * Frame mode (`?frame=1`): one screen, nothing else, inside the gallery's iframe. The iframe is the
 * size of the chosen device, so Grommet's breakpoints see that width and the layout responds for
 * real (the step rail hides, the guidance stacks) instead of the page being clipped.
 */
function Frame() {
  const [h, setH] = useState(parseHash);
  const notes = new URLSearchParams(window.location.search).get('notes') === '1';
  useEffect(() => {
    const onHash = () => setH(parseHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const all = useMemo(() => [startScreen(SCREENS, (id) => { window.location.hash = id; }), ...SCREENS], []);
  const screen = all.find((s) => s.id === h.id) ?? all[0];
  const state = h.state ?? screen.states?.[0]?.key ?? '';
  const setState = (s: string) => {
    window.location.hash = `${screen.id}/${s}`;
    window.parent.postMessage({ mockupState: s, id: screen.id }, '*');
  };
  return <NotesContext.Provider value={notes}>{screen.render(state, setState)}</NotesContext.Provider>;
}

function Gallery() {
  const [id, setId] = useState(() => parseHash().id);
  const [states, setStates] = useState<Record<string, string>>(() => {
    const h = parseHash();
    return h.state ? { [h.id]: h.state } : {};
  });
  const [notes, setNotes] = useState(false);
  const [width, setWidth] = useState(WIDTHS[0]);
  const go = (next: string) => {
    window.location.hash = next;
    setId(next);
  };
  useEffect(() => {
    const onHash = () => {
      const h = parseHash();
      setId(h.id);
      if (h.state) setStates((m) => ({ ...m, [h.id]: h.state }));
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const all = useMemo(() => [startScreen(SCREENS, go), ...SCREENS], []);
  const screen = all.find((s) => s.id === id) ?? all[0];
  const state = states[screen.id] ?? screen.states?.[0]?.key ?? '';
  const setState = (s: string) => {
    setStates((m) => ({ ...m, [screen.id]: s }));
    window.history.replaceState(null, '', `#${screen.id}/${s}`);
  };
  // the frame reports state changes made inside it (clicking through the Replication parts)
  useEffect(() => {
    const onMessage = (e: MessageEvent) => {
      if (e.data && e.data.mockupState && e.data.id) setStates((m) => ({ ...m, [e.data.id]: e.data.mockupState }));
    };
    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);
  const frameSrc = `${window.location.pathname}?frame=1&notes=${notes ? 1 : 0}#${screen.id}${state ? '/' + state : ''}`;

  return (
    <Box fill>
      <Box
        direction="row"
        align="center"
        justify="between"
        gap="small"
        pad={{ horizontal: 'medium', vertical: 'xsmall' }}
        background="background-front"
        border={{ side: 'bottom', color: 'border-default' }}
        flex={false}
        wrap
      >
        <Box direction="row" align="center" gap="small" wrap>
          <Box background="decorative-purple" round="xsmall" pad={{ horizontal: 'small', vertical: 'xxsmall' }}>
            <Text size="xsmall" weight="bold" color="text-onStrong">MOCKUP</Text>
          </Box>
          <Text size="small" weight="bold" color="text-strong">Redesign draft 3</Text>
          {all.map((s) => (
            <Button key={s.id} size="small" primary={s.id === screen.id} label={s.id} tip={s.title} onClick={() => go(s.id)} />
          ))}
        </Box>
        <Box direction="row" align="center" gap="small">
          {screen.states && (
            <Select
              size="small"
              aria-label="State"
              options={screen.states}
              labelKey="label"
              valueKey={{ key: 'key', reduce: true }}
              value={state}
              onChange={({ value }) => setState(value)}
            />
          )}
          <Select
            size="small"
            aria-label="Width"
            options={WIDTHS}
            labelKey="label"
            value={width}
            onChange={({ option }) => setWidth(option)}
          />
          <CheckBox toggle label={<Text size="small">Notes</Text>} checked={notes} onChange={(e) => setNotes(e.target.checked)} />
        </Box>
      </Box>
      <Box direction="row" flex overflow="hidden" background="background-contrast">
        <Box flex overflow="auto" align="center" pad={width.w ? 'small' : 'none'}>
          <Box
            background="background-front"
            elevation={width.w ? 'medium' : undefined}
            flex={false}
            style={width.w ? { width: width.w, height: width.h, maxWidth: '100%' } : { width: '100%', height: '100%' }}
            overflow="hidden"
          >
            <iframe
              key={frameSrc}
              title={`${screen.id} ${screen.title}`}
              src={frameSrc}
              style={{ border: 0, width: '100%', height: '100%', display: 'block' }}
            />
          </Box>
        </Box>
        {notes && screen.notes.length > 0 && (
          <Box width="medium" flex={false} background="background-front" border={{ side: 'left', color: 'border-weak' }} pad="medium" gap="medium" overflow="auto">
            <Box>
              <Text size="small" color="text-weak">{screen.id}</Text>
              <Text weight="bold" color="text-strong">{screen.title}</Text>
            </Box>
            <Box gap="small" flex={false}>
              {screen.notes.map((n, i) => (
                <Box key={i} direction="row" gap="small" flex={false}>
                  <Box round="full" background="decorative-purple" pad={{ horizontal: 'xsmall' }} align="center" justify="center" flex={false} style={{ minWidth: '1.6em', height: '1.6em' }}>
                    <Text size="xsmall" weight="bold" color="text-onStrong">{i + 1}</Text>
                  </Box>
                  <Text size="small">{n}</Text>
                </Box>
              ))}
            </Box>
            {screen.keeps && (
              <Box gap="xsmall" flex={false}>
                <Text size="small" weight="bold" color="text-strong">Kept from today</Text>
                {screen.keeps.map(([was, now]) => (
                  <Box key={was} border={{ side: 'top', color: 'border-weak' }} pad={{ top: 'xsmall' }}>
                    <Text size="small">{was}</Text>
                    <Text size="small" color="text-weak">→ {now}</Text>
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
}

const isFrame = new URLSearchParams(window.location.search).get('frame') === '1';

/**
 * The Design System keeps heading level and heading size independent. The HPE theme stops at 1.5rem
 * for an h2, which is too much for a section title inside a step, so h2 and h3 get an `xsmall` size
 * taken from the theme's own small text token. The app theme would get the same two lines.
 */
const mockTheme = deepMerge(theme, { heading: { level: { 2: { xsmall: hpe.text.small }, 3: { xsmall: hpe.text.small } } } });

createRoot(document.getElementById('root')!).render(
  <Grommet theme={mockTheme} full>
    {isFrame ? <Frame /> : <Gallery />}
  </Grommet>,
);
