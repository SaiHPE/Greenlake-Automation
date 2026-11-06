import { Text } from 'grommet';
import { RunEvent } from '../api';
import { InlineNotification } from './primitives';

/**
 * How old the environment read is, and whether to say something about it.
 *
 * Discovery results persist with the run, which is what lets an interrupted engagement resume — but
 * it also means a run reopened days later will happily provision from adapters, cabling and zoning
 * as they were the first time. `apply_plan` builds the hosts it creates, names and FC WWPNs, straight
 * out of that snapshot. Nothing in the interface used to say how old it was.
 *
 * The timestamp comes from the step's own `discover.completed` event, which is persisted alongside
 * the result, so it is accurate across restarts without asking the backend for anything extra.
 */

/** Long enough not to nag during a normal deployment; short enough to catch a run resumed another day. */
const STALE_AFTER_MS = 12 * 60 * 60 * 1000;

export function discoveryReadAt(events: RunEvent[]): Date | null {
  const event = [...events].reverse().find((item) => item.event_type === 'discover.completed');
  if (!event) return null;
  const when = new Date(event.created_at);
  return Number.isNaN(when.getTime()) ? null : when;
}

export function isDiscoveryStale(events: RunEvent[], now: number = Date.now()): boolean {
  const when = discoveryReadAt(events);
  return when !== null && now - when.getTime() > STALE_AFTER_MS;
}

function describe(when: Date, now: number): string {
  const hours = Math.floor((now - when.getTime()) / (60 * 60 * 1000));
  if (hours < 1) return 'less than an hour ago';
  if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? '' : 's'} ago`;
}

/**
 * States when the environment was last read. Becomes a warning once the read is old enough that the
 * environment may have moved on — shown on the steps that act on it, not just where it was produced.
 */
export function DiscoveryFreshness({ events, action }: { events: RunEvent[]; action?: string }) {
  const when = discoveryReadAt(events);
  if (!when) return null;
  const now = Date.now();
  const stamp = when.toLocaleString();

  if (now - when.getTime() > STALE_AFTER_MS) {
    return (
      <InlineNotification
        tone="warning"
        title={`The environment was last read ${describe(when, now)}`}
        message={`Discovery ran at ${stamp}. If hosts, cabling or zoning have changed since, re-run discovery${
          action ? ` before ${action}` : ''
        } so it acts on the current environment.`}
      />
    );
  }
  return (
    <Text size="xsmall" color="text-weak">
      {`Environment last read ${stamp}.`}
    </Text>
  );
}
