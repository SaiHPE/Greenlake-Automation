import type { EventOf, EventType, RunEvent } from './api';

/** True when `event` has one of `types`, narrowing its `data` to that payload. */
export const isOf = <T extends EventType>(event: RunEvent, ...types: T[]): event is EventOf<T> =>
  (types as EventType[]).includes(event.event_type);

/** The newest event of one of `types`, narrowed to its payload. */
export function latestOf<T extends EventType>(events: RunEvent[], ...types: T[]): EventOf<T> | undefined {
  for (let i = events.length - 1; i >= 0; i -= 1) {
    const event = events[i];
    if (isOf(event, ...types)) return event;
  }
  return undefined;
}
