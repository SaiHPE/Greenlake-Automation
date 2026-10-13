import { Box, Button, CheckBox, Grommet, Select, Text } from 'grommet';
import { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { theme } from '../src/theme';
import { NotesContext } from './kit';
import { Screen } from './screen';
import { discovery } from './screens/Discovery';
import { overview } from './screens/Overview';
import { prerequisites } from './screens/Prerequisites';
import { replication } from './screens/Replication';
import { mode, sheet } from './screens/SheetMode';
import { startScreen } from './screens/Start';

const SCREENS: Screen[] = [prerequisites, sheet, mode, overview, discovery, replication];
const WIDTHS = [
  { label: 'Jump box 1366 × 768', w: 1366, h: 768 },
  { label: 'Large monitor 1920 × 1080', w: 1920, h: 1080 },
  { label: 'Fit this window', w: 0, h: 0 },
];

const parseHash = () => {
  const [id, state] = window.location.hash.slice(1).split('/');
  return { id: id || 'M0', state };
};

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
          <Text size="small" weight="bold" color="text-strong">Redesign draft 1</Text>
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
            key={screen.id + state}
            background="background-front"
            elevation={width.w ? 'medium' : undefined}
            flex={false}
            style={width.w ? { width: width.w, height: width.h, maxWidth: '100%', maxHeight: '100%' } : { width: '100%', height: '100%' }}
            overflow="hidden"
          >
            <NotesContext.Provider value={notes}>{screen.render(state, setState)}</NotesContext.Provider>
          </Box>
        </Box>
        {notes && screen.notes.length > 0 && (
          <Box width="380px" flex={false} background="background-front" border={{ side: 'left', color: 'border-weak' }} pad="medium" gap="medium" overflow="auto">
            <Box>
              <Text size="small" color="text-weak">{screen.id}</Text>
              <Text weight="bold" color="text-strong">{screen.title}</Text>
            </Box>
            <Box gap="small" flex={false}>
              {screen.notes.map((n, i) => (
                <Box key={i} direction="row" gap="small" flex={false}>
                  <Box round="full" background="decorative-purple" width="22px" height="22px" align="center" justify="center" flex={false}>
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

createRoot(document.getElementById('root')!).render(
  <Grommet theme={theme} full>
    <Gallery />
  </Grommet>,
);
