import { Box, Button, CheckBox, Text } from 'grommet';
import { Section } from '../components';
import { ACTION_CATALOG, ActionKey, MODE_PRESETS, RunMode } from '../modes';

interface Props {
  mode: RunMode;
  custom: ActionKey[];
  setMode: (mode: RunMode) => void;
  setCustom: (keys: ActionKey[]) => void;
  onDone: () => void;
  locked?: boolean; // once a run exists the mode is fixed (it shaped the run + the sheet validation)
}

export function ModeStep({ mode, custom, setMode, setCustom, onDone, locked }: Props) {
  const toggle = (key: ActionKey, checked: boolean) =>
    setCustom(checked ? [...custom, key] : custom.filter((k) => k !== key));

  return (
    <Box gap="medium">
      <Section title="What do you want to run?">
        <Text size="small" color="text-weak">
          Pick a mode. The wizard then shows only the steps that mode needs — so you can verify or
          provision an already-initialised array without re-running initialisation.
        </Text>
        <Box gap="small" pad={{ top: 'small' }}>
          {MODE_PRESETS.map((preset) => {
            const selected = mode === preset.mode;
            return (
              <Box
                key={preset.mode}
                direction="row"
                gap="small"
                align="center"
                pad="small"
                round="small"
                border={{ color: selected ? 'brand' : 'border', size: selected ? '2px' : '1px' }}
                background={selected ? 'background-contrast' : undefined}
                onClick={locked ? undefined : () => setMode(preset.mode)}
                style={{ cursor: locked ? 'default' : 'pointer', opacity: locked && !selected ? 0.5 : 1 }}
              >
                <Box
                  width="18px"
                  height="18px"
                  round="full"
                  flex={false}
                  border={{ color: selected ? 'brand' : 'border', size: '2px' }}
                  align="center"
                  justify="center"
                >
                  {selected && <Box width="9px" height="9px" round="full" background="brand" />}
                </Box>
                <Box>
                  <Text weight={selected ? 'bold' : undefined}>{preset.label}</Text>
                  <Text size="small" color="text-weak">
                    {preset.blurb}
                  </Text>
                </Box>
              </Box>
            );
          })}
        </Box>
      </Section>

      {mode === 'CUSTOM' && (
        <Section title="Pick the steps to run">
          <Box gap="xsmall">
            {ACTION_CATALOG.map((action) => (
              <CheckBox
                key={action.key}
                label={`${action.title} — ${action.subtitle}`}
                checked={custom.includes(action.key)}
                disabled={locked}
                onChange={(event) => toggle(action.key, event.target.checked)}
              />
            ))}
          </Box>
        </Section>
      )}

      {locked && (
        <Text size="small" color="text-weak">
          A run already exists for this session — the mode is locked. Use “Restart” on the Finish step
          to start a new run with a different mode.
        </Text>
      )}

      <Button
        primary
        alignSelf="start"
        label="Continue → Prerequisites"
        disabled={mode === 'CUSTOM' && custom.length === 0}
        onClick={onDone}
      />
    </Box>
  );
}
