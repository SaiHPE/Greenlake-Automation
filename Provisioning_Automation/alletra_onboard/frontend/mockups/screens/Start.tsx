import { Box, Heading, Text } from 'grommet';
import { Screen } from '../screen';

function Rule({ n, title, text }: { n: number; title: string; text: string }) {
  return (
    <Box direction="row" gap="small" flex={false}>
      <Text weight="bold" color="text-strong">{n}.</Text>
      <Box>
        <Text weight={600} color="text-strong">{title}</Text>
        <Text size="small">{text}</Text>
      </Box>
    </Box>
  );
}

function Start({ screens, go }: { screens: Screen[]; go: (id: string) => void }) {
  return (
    <Box fill overflow="auto" background="background-back">
      <Box pad="large" gap="medium" width={{ max: '900px' }} flex={false}>
        <Box>
          <Text size="small" color="text-weak">Redesign mockups · draft 2 · 13/10/2026</Text>
          <Heading level={1} size="small" margin="none">Alletra MP Onboarding: a calmer screen per step</Heading>
        </Box>
        <Text>
          These are mockups, not the app. They use the same HPE Design System parts the app uses (Grommet with the HPE theme
          and design tokens), so what you see is what we can build. The data is made up from the lab arrays.
        </Text>

        <Box background="background-front" round="small" pad="medium" gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">What does not change</Heading>
          <Text size="small">Every step, every check and every button keeps working the way it does today. All the prerequisites stay.</Text>
          <Text size="small">Only the layout, the wording and the order on each page change. The backend is not touched.</Text>
          <Text size="small">Each screen lists where every control from today now lives (Kept from today, in the notes panel).</Text>
        </Box>

        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">The rules every screen follows</Heading>
          <Rule n={1} title="One line says what happened" text="At the top of each step: one sentence and the time. Coloured only when something needs you." />
          <Rule n={2} title="One green button, always bottom right" text="It is the next thing to do. Other actions are outlined buttons on the left. When a tick is needed first (authorise, accept), the tick sits in the footer next to the button." />
          <Rule n={3} title="Details fold away" text="Tables and long lists sit in sections you open. Counts show in the section titles." />
          <Rule n={4} title="Explanations go to the right" text="What the step does, what it reads, what it changes: in a panel beside the work, not between you and the button. Hide it when you know the step." />
          <Rule n={5} title="Status means status" text="A grey circle for not started, never a question mark. Orange only when you must act." />
          <Rule n={6} title="Activity and console fold into the bottom line" text="The last event is always visible. Open the full list or the console when you need it." />
          <Rule n={7} title="Prepare first, then the run" text="The three preparation steps count as Prepare 1 to 3. The list of run steps appears when you choose the mode, so the step count never jumps." />
        </Box>

        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Screens</Heading>
          {screens.map((s) => (
            <Box key={s.id} direction="row" gap="small" align="center" onClick={() => go(s.id)} hoverIndicator="background-hover" pad="xsmall" round="xsmall">
              <Box width="40px" flex={false}><Text weight="bold" color="text-strong">{s.id}</Text></Box>
              <Text>{s.title}</Text>
              {s.states && <Text size="small" color="text-weak">· {s.states.length} states</Text>}
            </Box>
          ))}
        </Box>

        <Box background="background-contrast" round="small" pad="medium" gap="xsmall" flex={false}>
          <Heading level={2} size="small" margin="none">How to give feedback</Heading>
          <Text size="small">Turn on Notes (top right) to see numbered markers on each screen and what each one changes.</Text>
          <Text size="small">Tell me in plain words, with the screen and note number. For example: "M6 note 4: keep the tick at the top" or "M1: the Done ticks are not needed".</Text>
          <Text size="small">Use the State list to see a screen at different moments, and Width to see it at the jump box size (1366 pixels) or a large monitor.</Text>
        </Box>
      </Box>
    </Box>
  );
}

export function startScreen(screens: Screen[], go: (id: string) => void): Screen {
  return {
    id: 'M0',
    title: 'Start here',
    notes: [],
    render: () => <Start screens={screens} go={go} />,
  };
}
