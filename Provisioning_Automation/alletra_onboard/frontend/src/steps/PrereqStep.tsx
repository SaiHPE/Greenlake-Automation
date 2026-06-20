import { Anchor, Box, Button, Notification, Text } from 'grommet';
import { Instructions, Section } from '../components';

// What the HPE engineer must do BEFORE running the automation — the manual steps from HPE's
// official onboarding checklist that this tool does not (and should not) perform.
export function PrereqStep({ onDone }: { onDone: () => void }) {
  return (
    <Box gap="medium">
      <Notification
        status="info"
        title="Do these first — the automation starts after they're done"
        message="This tool automates adding the device + subscription in GreenLake, the on-array Cloud Connectivity Wizard, and the DSCC Set Up System wizard. Everything below is manual setup HPE requires beforehand."
      />

      <Section title="1 · HPE GreenLake account & workspace">
        <Instructions
          items={[
            <>Activate your software subscriptions from the <b>Electronic Software Delivery (ESD) Receipt</b> email.</>,
            <>Create (or sign in to) your <Anchor href="https://console.greenlake.hpe.com" target="_blank" label="HPE GreenLake" /> account and <b>create a workspace</b>.</>,
            <>Deploy <b>Data Services Cloud Console</b> to the workspace (Find Services → Data Services → Provision), picking the <b>region closest to the array</b>.</>,
            <>Assign yourself the <b>Data Services Administrator</b> role (Manage Workspace → Identity &amp; Access → Assign Role), and verify the Setup / Block Storage / Data Ops Manager services appear.</>,
          ]}
        />
      </Section>

      <Section title="2 · Create the API client (for this tool)">
        <Instructions
          items={[
            <>In GreenLake, go to <b>Manage Workspace → API</b> and create a personal API client.</>,
            <>Copy the <b>Client ID</b>, <b>Client Secret</b>, and the per-workspace <b>token URL</b> (…/authorization/v2/oauth2/&lt;tenant&gt;/token).</>,
            <>Put those three into the <b>Initialisation sheet</b> (next step) — that's how this tool authenticates to GreenLake.</>,
          ]}
        />
      </Section>

      <Section title="3 · Network & time prerequisites">
        <Instructions
          items={[
            <>Allow the firewall/proxy to reach: <b>console.greenlake.hpe.com</b>, <b>device.cloud.hpe.com</b>, <b>console-&lt;region&gt;.data.cloud.hpe.com</b>, <b>tunnel-&lt;region&gt;.data.cloud.hpe.com</b> (all TCP 443).</>,
            <>DNS on the array must resolve global names (e.g. <b>device.cloud.hpe.com</b>).</>,
            <><b>System time must be within 2 minutes</b> of correct, or the array can't connect to DSCC — use NTP (this app also has a clock-sync button on the DSCC step).</>,
          ]}
        />
      </Section>

      <Section title="4 · Physical install & this jump box">
        <Instructions
          items={[
            <>The array is racked, cabled, <b>powered on</b>, and its admin ports are on the management network.</>,
            <>This jump box is on the <b>same subnet</b> as the array (so it can reach the link-local <b>169.254.x</b> Cloud Connectivity URL).</>,
            <>Run this app <b>as Administrator</b> (so the clock-sync can set the system time).</>,
          ]}
        />
      </Section>

      <Section title="5 · Fill the Initialisation sheet">
        <Text size="small">
          On the next step, download the <b>Initialisation_sheet.xlsx</b>, fill every required field
          (API credentials, serial, subscription key, network, DSCC details, admin credential), and
          upload it. One workbook = one array.
        </Text>
      </Section>

      <Button primary label="I've completed these → Initialisation sheet" onClick={onDone} alignSelf="start" />
    </Box>
  );
}
