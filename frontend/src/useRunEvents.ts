import { useCallback, useEffect, useRef, useState } from 'react';
import { API, getEvents, getRun, RunEvent, RunRecord } from './api';

/** Live view of one run: initial fetch + SSE stream; refetches the run record on every event. */
export function useRunEvents(runId: string | null) {
  const [run, setRun] = useState<RunRecord | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const seen = useRef<Set<string>>(new Set());

  const refresh = useCallback(() => {
    if (!runId) return;
    getRun(runId)
      .then((detail) => setRun(detail.run))
      .catch(() => undefined);
  }, [runId]);

  useEffect(() => {
    if (!runId) {
      setRun(null);
      setEvents([]);
      seen.current = new Set();
      return;
    }
    let source: EventSource | null = null;

    const append = (event: RunEvent) => {
      if (seen.current.has(event.event_id)) return;
      seen.current.add(event.event_id);
      setEvents((previous) => [...previous, event]);
    };

    refresh();
    getEvents(runId)
      .then((payload) => payload.events.forEach(append))
      .catch(() => undefined);

    source = new EventSource(`${API}/runs/${runId}/stream`);
    source.onmessage = (message) => {
      try {
        append(JSON.parse(message.data) as RunEvent);
      } catch {
        return;
      }
      refresh();
    };
    return () => source?.close();
  }, [runId, refresh]);

  return { run, events, refresh };
}
