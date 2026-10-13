import { Box, Heading, Text } from 'grommet';
import { RunState, StateIcon } from '../kit';
import { Screen } from '../screen';

const DAY: { moment: string; what: string; screen: string }[] = [
  { moment: 'Arrive', what: 'Open the app on the jump box. See every run on this box, who each one waits on, and pick up where you left off.', screen: 'M7' },
  { moment: 'Prepare', what: 'Check the workstation and the HPE side (connection, proxy, clock, workspace, API client, cabling). Upload the sheet. Say what you want to do.', screen: 'M1 M2 M3' },
  { moment: 'Work', what: 'One step at a time: one line of status, one green button, details folded. Nothing is written without your tick.', screen: 'M5 M6' },
  { moment: 'Hand off', what: 'Zoning goes to the SAN team as a command set. The run says who it waits on and since when. You go and do something else.', screen: 'M8' },
  { moment: 'Come back', what: 'Next morning, on Home the run shows what changed. Check zoning again and carry on.', screen: 'M7 M8 M4' },
  { moment: 'Something stops', what: 'One sentence on what the device refused, then numbered options: fix and retry, or undo with the removal commands.', screen: 'M9' },
  { moment: 'Finish', what: 'The hand-over package: as-built, command log, removal commands, and what still has to be done by hand.', screen: 'M10' },
];

const VOCAB: { state: RunState; word: string; means: string; colour: string }[] = [
  { state: 'not_started', word: 'Not started', means: 'Nothing has run yet.', colour: 'grey circle' },
  { state: 'running', word: 'Running', means: 'The tool is working. Wait.', colour: 'blue' },
  { state: 'action_required', word: 'Waiting for you', means: 'A decision, a tick or an input is needed from you.', colour: 'orange' },
  { state: 'waiting', word: 'Waiting on others', means: 'The SAN team, the network team, the lab. Nothing for you until they report back.', colour: 'grey clock (new)' },
  { state: 'failed', word: 'Stopped', means: 'A device refused something. The step says what, and what to do.', colour: 'red' },
  { state: 'complete', word: 'Done', means: 'Finished, with a one-line result.', colour: 'green' },
];

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
          <Heading level={2} size="small" margin="none">The operator's day, and which screen serves each moment</Heading>
          <Text size="small" color="text-weak">The big picture. A field engineer runs several arrays over several days, hands work to other teams, and comes back. The app has to make sense at every one of these moments, not only inside a step.</Text>
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
            {DAY.map((d, i) => (
              <Box key={d.moment} direction="row" gap="medium" pad={{ horizontal: 'medium', vertical: 'small' }} border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined} align="start">
                <Box width="130px" flex={false}><Text size="small" weight="bold" color="text-strong">{d.moment}</Text></Box>
                <Box flex><Text size="small">{d.what}</Text></Box>
                <Box width="90px" flex={false}><Text size="small" color="text-weak">{d.screen}</Text></Box>
              </Box>
            ))}
          </Box>
        </Box>

        <Box gap="small" flex={false}>
          <Heading level={2} size="small" margin="none">Six words for status, the same everywhere</Heading>
          <Text size="small" color="text-weak">Rail, header, step, overview and Home all use these and nothing else. Today the app has five; "Waiting on others" is new, so a parked run no longer looks like a problem.</Text>
          <Box background="background-front" round="small" border={{ color: 'border-weak' }} flex={false}>
            {VOCAB.map((v, i) => (
              <Box key={v.word} direction="row" gap="medium" pad={{ horizontal: 'medium', vertical: 'xsmall' }} border={i > 0 ? { side: 'top', color: 'border-weak' } : undefined} align="center">
                <Box width="190px" flex={false} direction="row" gap="xsmall" align="center"><StateIcon state={v.state} /><Text size="small" weight={600}>{v.word}</Text></Box>
                <Box flex><Text size="small">{v.means}</Text></Box>
                <Box width="130px" flex={false}><Text size="small" color="text-weak">{v.colour}</Text></Box>
              </Box>
            ))}
          </Box>
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
          <Rule n={8} title="A hand-off is a state, not a dead end" text="When the run waits on another team, it says who, what for and since when, and the one thing to do when they report back." />
          <Rule n={9} title="A failure says what to do" text="What stopped and what the device said, then numbered options. The removal commands are always one click away." />
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
