import { ThemeType } from 'grommet';
import { hpe } from 'grommet-theme-hpe';
import { dark, light } from 'hpe-design-tokens/grommet';
import { deepMerge } from 'grommet/utils';

// grommet-theme-hpe publishes status-ok / status-warning / status-critical / status-unknown as named
// colours, but not the information status. The five-state step vocabulary needs it, so surface it
// from the very same design token the theme uses for the others — no invented colour values.
// Heading level and size are independent in the Design System; the theme's smallest h2 (1.5rem) is
// too large for a section title inside a step, so h2/h3 get an xsmall size from the text scale.
const textSmall = (hpe as ThemeType).text?.small;

export const theme = deepMerge(hpe, {
  global: {
    colors: {
      'status-info': { light: light.hpe.color.icon.info, dark: dark.hpe.color.icon.info },
    },
  },
  heading: { level: { 2: { xsmall: textSmall }, 3: { xsmall: textSmall } } },
} as unknown as ThemeType);
