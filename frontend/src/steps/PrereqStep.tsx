import { Anchor, Box, Button, Notification, Text } from 'grommet';
import { ReactNode } from 'react';
import { ClockSync } from '../ClockSync';
import { Instructions, Section } from '../components';

function Video({ src }: { src: string }) {
  return (
    <Box border round="xsmall" overflow="hidden" background="black" width={{ max: '560px' }} flex={false}>
      <video src={src} controls preload="metadata" style={{ width: '100%', display: 'block' }} />
    </Box>
  );
}

// A numbered sub-step: its instructions plus the matching HPE walkthrough clip.
function StepClip({ title, steps, src }: { title: string; steps: ReactNode[]; src: string }) {
  return (
    <Box gap="xsmall" pad={{ top: 'small' }} flex={false}>
      <Text weight="bold">{title}</Text>
      <Instructions items={steps} />
      <Video src={src} />
    </Box>
  );
}

// What the HPE engineer must do BEFORE running the automation — the manual steps from HPE's
// official onboarding checklist that this tool does not (and should not) perform.
export function PrereqStep({ onDone }: { onDone: () => void }) {
  return (
    <Box gap="medium">
      <Notification
        status="info"
        title="Do these first — the automation starts after they're done"
        message="This tool automates adding the device + subscription in GreenLake, the on-array Cloud Connectivity Wizard, and the DSCC Set Up System wizard. Everything below is manual setup HPE requires beforehand. The clips are HPE's own walkthroughs."
      />

      <Section title="1 · HPE GreenLake account & workspace">
        <Instructions
          items={[
            <>Activate your software subscriptions from the <b>Electronic Software Delivery (ESD) Receipt</b> email.</>,
            <>Create (or sign in to) your <Anchor href="https://console.greenlake.hpe.com" target="_blank" label="HPE GreenLake" /> account, then do the three steps below <b>in order</b>.</>,
          ]}
        />
        <StepClip
          title="1. Create the workspace"
          src="/prereq/videos/create-workspace.mp4"
          steps={[
            <>Click <b>Create Workspace</b> and provide the workspace name, country, street address, city/state, ZIP, phone and email.</>,
            <>Accept the legal terms and click <b>Create Workspace</b> — you become the workspace Administrator and your dashboard opens.</>,
          ]}
        />
        <StepClip
          title="2. Deploy Data Services Cloud Console"
          src="/prereq/videos/deploy-dscc.mp4"
          steps={[
            <>On the workspace <b>Home</b>, click <b>Find Services</b> → scroll to <b>Storage</b> → <b>Data Services</b> → <b>Provision</b>.</>,
            <>Select the <b>Deployment Region nearest the array</b>, accept the Terms of Service, and click <b>Deploy</b>.</>,
            <>At the top of the page, click <b>Launch</b> to open Data Services Cloud Console.</>,
          ]}
        />
        <StepClip
          title="3. Assign yourself the Data Services Administrator role"
          src="/prereq/videos/assign-admin.mp4"
          steps={[
            <><b>Manage Workspace → Identity &amp; Access → Assign Role</b>: select your user, set <b>Service Manager = Data Services</b> and <b>Role = Administrator</b>, leave <b>Limit Resource Access</b> off, and click <b>Assign Role</b>.</>,
            <>Launch Data Services and confirm the <b>Setup</b>, <b>Block Storage</b> and <b>Data Ops Manager</b> services appear.</>,
          ]}
        />
      </Section>

      <Section title="2 · Create the API client (for this tool)">
        <StepClip
          title="4. Create a personal API client"
          src="/prereq/videos/api-client-credentials.mp4"
          steps={[
            <>In GreenLake, go to <b>Manage Workspace → API</b> and click <b>Create personal API client</b>.</>,
            <>Give it a name and select the <b>HPE GreenLake Cloud Platform</b> service, then click <b>Create</b>.</>,
            <>Copy the <b>Client ID</b>, <b>Client Secret</b>, and the per-workspace <b>token URL</b> (…/authorization/v2/oauth2/&lt;tenant&gt;/token) — you only see the secret once.</>,
            <>Put those three into the <b>Initialisation sheet</b> (next step) — that's how this tool authenticates to GreenLake.</>,
          ]}
        />
        <Text size="xsmall" color="text-weak">The clip stops before the Client ID / secret are shown.</Text>
      </Section>

      <Section title="3 · Network & time prerequisites">
        <Instructions
          items={[
            <>Allow the firewall/proxy to reach: <b>console.greenlake.hpe.com</b>, <b>device.cloud.hpe.com</b>, <b>console-&lt;region&gt;.data.cloud.hpe.com</b>, <b>tunnel-&lt;region&gt;.data.cloud.hpe.com</b> (all TCP 443).</>,
            <>DNS on the array must resolve global names (e.g. <b>device.cloud.hpe.com</b>).</>,
            <><b>System time must be within 2 minutes</b> of correct, or the array can't connect to DSCC. Use NTP, or the <b>Sync system clock</b> control below.</>,
          ]}
        />
      </Section>

      <ClockSync title="System clock (must be within 2 minutes of correct)" />

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
