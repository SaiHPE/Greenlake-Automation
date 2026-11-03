import { Box, FormField, Heading, Notification, Text, TextInput } from 'grommet';
import { ReactNode } from 'react';
import { RunEvent } from '../api';
import { Panel } from './blocks';
import { StatusIcon, StepState } from './status';

/**
 * Many notes, one per line (SPEC-004 R3). A single note renders as plain text; the " · "-joined
 * paragraph the register called X-6 is what this replaces.
 */
export function NotesList({ notes }: { notes: string[] }) {
  if (notes.length <= 1) return <>{notes[0] ?? ''}</>;
  return (
    <Box as="ul" margin="none" pad={{ left: 'medium' }} gap="xxsmall">
      {notes.map((note, i) => (
        <Text as="li" size="small" key={i}>
          {note}
        </Text>
      ))}
    </Box>
  );
}

/** A content surface with a heading: the redesign's Panel, kept under this name for the views that use it. */
export function Surface({
  title,
  description,
  actions,
  children,
}: {
  title?: string;
  description?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <Panel title={title} description={description} right={actions ? <Box direction="row" gap="xsmall" flex={false}>{actions}</Box> : undefined}>
      {children}
    </Panel>
  );
}

export type Tone = 'ok' | 'info' | 'warning' | 'critical';

const TONE_STATUS: Record<Tone, 'normal' | 'info' | 'warning' | 'critical'> = {
  ok: 'normal',
  info: 'info',
  warning: 'warning',
  critical: 'critical',
};

/** Feedback placed next to the content it concerns — the Design System's inline notification. */
export function InlineNotification({
  tone,
  title,
  message,
  onClose,
}: {
  tone: Tone;
  title: string;
  message?: ReactNode;
  onClose?: () => void;
}) {
  return <Notification status={TONE_STATUS[tone]} title={title} message={message} onClose={onClose} />;
}

/** A step's event stream, newest last, with status-coloured markers and tabular timestamps. */
export function ActivityTimeline({ events, empty }: { events: RunEvent[]; empty?: string }) {
  if (!events.length) {
    return (
      <Text size="small" color="text-weak">
        {empty ?? 'No activity recorded yet.'}
      </Text>
    );
  }
  const toneOf = (type: string): StepState => {
    if (/(failed|crashed|stalled)/.test(type)) return 'failed';
    if (type.startsWith('operator.')) return 'action_required';
    if (/(completed|applied|generated|proper|\.plan$|rendered|verified)/.test(type)) return 'complete';
    if (/previewed/.test(type)) return 'action_required';
    return 'running';
  };
  return (
    <Box gap="xsmall" overflow="auto" height={{ max: 'medium' }}>
      {events.map((event) => (
        <Box key={event.event_id} direction="row" gap="small" align="start" flex={false}>
          <Box pad={{ top: 'xxsmall' }} flex={false}>
            <StatusIcon state={toneOf(event.event_type)} />
          </Box>
          <Box direction="row" gap="small" align="baseline" wrap>
            <Text size="xsmall" color="text-weak">
              {new Date(event.created_at).toLocaleTimeString()}
            </Text>
            <Text size="small">{event.message}</Text>
          </Box>
        </Box>
      ))}
    </Box>
  );
}

/** The summary line under a table — the Design System puts aggregate counts in a table footer. */
export function TableSummary({ children }: { children: ReactNode }) {
  // role="status": a screen reader hears the count when it changes (SPEC-012 R6, X-3).
  return (
    <Box pad={{ top: 'xsmall' }} border={{ side: 'top', color: 'border-weak' }} flex={false} role="status">
      <Text size="small" color="text-weak">
        {children}
      </Text>
    </Box>
  );
}

/**
 * Array sign-in fields, shared by the two steps that read the array over SSH. The password is used
 * for that operation only and is never stored — the help text says so where the operator types it.
 */
export function CredentialsFields({
  username,
  password,
  onUsername,
  onPassword,
  help = 'Used for this operation only; never stored.',
}: {
  username: string;
  password: string;
  onUsername: (value: string) => void;
  onPassword: (value: string) => void;
  help?: string;
}) {
  return (
    <Box direction="row" gap="medium" wrap>
      <Box width="medium">
        <FormField label="User name" name="username" htmlFor="array-username">
          <TextInput
            id="array-username"
            name="username"
            value={username}
            onChange={(event) => onUsername(event.target.value)}
          />
        </FormField>
      </Box>
      <Box width="medium">
        <FormField label="Password" name="password" htmlFor="array-password" help={help}>
          <TextInput
            id="array-password"
            name="password"
            type="password"
            value={password}
            onChange={(event) => onPassword(event.target.value)}
          />
        </FormField>
      </Box>
    </Box>
  );
}
