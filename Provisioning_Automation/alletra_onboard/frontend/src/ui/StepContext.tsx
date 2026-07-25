import { createContext, ReactNode, useContext } from 'react';
import { RunEvent, RunRecord } from '../api';
import { ServedStep } from '../modes';

/**
 * What every step needs to know about the run it belongs to.
 *
 * Supplied once by the shell rather than threaded through each step's props, so a step declares
 * only its own content and actions. StepShell reads its position, status and activity from here.
 */
export interface StepContextValue {
  runId: string | null;
  run: RunRecord | null;
  events: RunEvent[];
  /** The registry entry for this step; absent for the scaffolding steps that frame every run. */
  step?: ServedStep;
  position: { index: number; total: number };
  /** Advance to the next step in the wizard. */
  onDone: () => void;
}

const StepContext = createContext<StepContextValue | null>(null);

export function StepProvider({ value, children }: { value: StepContextValue; children: ReactNode }) {
  return <StepContext.Provider value={value}>{children}</StepContext.Provider>;
}

export function useStepContext(): StepContextValue {
  const value = useContext(StepContext);
  if (!value) throw new Error('useStepContext must be used inside a StepProvider');
  return value;
}
