import { hpe } from 'grommet-theme-hpe';
import { dark, light } from 'hpe-design-tokens/grommet';
import { deepMerge } from 'grommet/utils';

// grommet-theme-hpe publishes status-ok / status-warning / status-critical / status-unknown as named
// colours, but not the information status. The five-state step vocabulary needs it, so surface it
// from the very same design token the theme uses for the others — no invented colour values.
export const theme = deepMerge(hpe, {
  global: {
    colors: {
      'status-info': { light: light.hpe.color.icon.info, dark: dark.hpe.color.icon.info },
    },
  },
});
