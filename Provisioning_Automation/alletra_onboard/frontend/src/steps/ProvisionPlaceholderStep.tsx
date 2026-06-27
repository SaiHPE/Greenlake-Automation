import { Box, Button, Notification, Text } from 'grommet';
import { Section } from '../components';

// Phase-1 placeholder. The mode chooser + selection-aware run already route here; the real
// Discovery / SAN Zoning / Provision steps (WSAPI-driven, see docs/adr/0002-0004 + the runbook)
// replace this in the provisioning build (Phase 2).
export function ProvisionPlaceholderStep({ title, onDone }: { title: string; onDone: () => void }) {
  return (
    <Box gap="medium">
      <Section title={`${title}`}>
        <Notification
          status="unknown"
          title="Storage provisioning ships in the next build"
          message="Discovery, SAN zoning, and host + LUN provisioning are being built now. Decoupling is live, so this step is already part of the run you selected — the real screen lands shortly."
        />
        <Text size="small" color="text-weak">
          Every write here (zoning changes, host/volume/VLUN creation) will run behind a preview and an
          explicit confirmation.
        </Text>
      </Section>
      <Button primary alignSelf="start" label="Continue →" onClick={onDone} />
    </Box>
  );
}
