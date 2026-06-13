import { Box, Heading, Tag, Text } from 'grommet';
import { CircleInformation, StatusCritical, StatusGood, StatusWarning } from 'grommet-icons';
import { ReactNode } from 'react';
import { RunEvent } from './api';

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Box background="background-front" round="small" pad="medium" gap="small" border>
      <Heading level={3} margin="none">
        {title}
      </Heading>
      {children}
    </Box>
  );
}

const STATUS_COLORS: Record<string, string> = {
  ready: 'status-ok',
  succeeded: 'status-ok',
  running: 'status-unknown',
  waiting_for_operator: 'status-warning',
  retryable_failure: 'status-critical',
  terminal_failure: 'status-critical',
};

export function StatusTag({ status }: { status: string | undefined }) {
  if (!status) return null;
  return (
    <Tag
      size="small"
      value={status.replaceAll('_', ' ')}
      border={{ color: STATUS_COLORS[status] ?? 'border' }}
    />
  );
}

export function EventIcon({ type }: { type: string }) {
  if (type.includes('failed') || type.includes('crashed')) return <StatusCritical color="status-critical" size="small" />;
  if (type.includes('completed') || type === 'run.created') return <StatusGood color="status-ok" size="small" />;
  if (type.startsWith('operator.') || type.includes('stalled')) return <StatusWarning color="status-warning" size="small" />;
  return <CircleInformation size="small" />;
}

export function EventLog({ events, emptyText }: { events: RunEvent[]; emptyText?: string }) {
  if (!events.length) {
    return (
      <Text size="small" color="text-weak">
        {emptyText ?? 'No activity yet.'}
      </Text>
    );
  }
  return (
    <Box gap="xsmall" overflow="auto" height={{ max: 'medium' }}>
      {events.map((event) => (
        <Box key={event.event_id} direction="row" gap="small" align="start" flex={false}>
          <Box pad={{ top: 'xxsmall' }} flex={false}>
            <EventIcon type={event.event_type} />
          </Box>
          <Box>
            <Text size="small">{event.message}</Text>
            <Text size="xsmall" color="text-weak">
              {event.phase} · {new Date(event.created_at).toLocaleTimeString()}
            </Text>
          </Box>
        </Box>
      ))}
    </Box>
  );
}

export function Instructions({ items }: { items: ReactNode[] }) {
  return (
    <Box as="ol" margin={{ vertical: 'none', left: 'small' }} pad={{ left: 'medium' }} gap="xsmall">
      {items.map((item, index) => (
        <Text as="li" size="small" key={index}>
          {item}
        </Text>
      ))}
    </Box>
  );
}
