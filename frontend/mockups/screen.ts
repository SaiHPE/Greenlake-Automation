import { ReactNode } from 'react';

/** One mockup screen in the gallery. `keeps` maps every control on today's page to its new place. */
export interface Screen {
  id: string;
  title: string;
  states?: { key: string; label: string }[];
  notes: string[];
  keeps?: [string, string][];
  render: (state: string, setState: (s: string) => void) => ReactNode;
}
