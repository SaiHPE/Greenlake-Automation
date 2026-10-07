import { Text } from 'grommet';
import { ContinueButton, Surface } from '../ui/primitives';
import { StepShell } from '../ui/StepShell';

/** SPEC-017 — ships in v0.18. The step exists in the registry so the Replicate mode is complete;
 *  until the sequence is built it says so and lets the operator continue. */
export function FailoverTestStep({ onDone }: { onDone: () => void }) {
  return (
    <StepShell
      title="Failover test"
      description="Proves the DR copy can take over and production can come back: fail over to the peer, recover, restore — on the tool’s own 1 GiB test group by default — reading both arrays after every step and recording the roles and timings for the as-built."
      state="not_started"
      showActivity={false}
      footerNote="Specified in SPEC-017; arrives in v0.18, after the Replication step is live-verified."
      actions={<ContinueButton onClick={onDone} suffix="without the failover test" />}
    >
      <Surface title="Not in this build">
        <Text size="small" color="text-weak">
          The sequence (stop → failover → recover → restore, over the array’s own disaster-recovery actions) is specified
          but not yet built. Continue; the as-built will say the failover test was not run in this run.
        </Text>
      </Surface>
    </StepShell>
  );
}
