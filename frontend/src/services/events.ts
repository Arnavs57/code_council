/**
 * Event stream — architecture only.
 *
 * Phase 3: a typed stream abstraction over the WebSocket client. The
 * dashboard reducer consumes `subscribe()` to project run state, the
 * activity feed, the timeline and agent statuses from one source of truth.
 */
import type { TimelineEvent } from "@/types"

export interface EventStream {
  // TODO(phase-3): subscribeToRun(runId, handler), unsubscribe()
  onEvent(handler: (event: TimelineEvent) => void): void
}

export const eventStream: EventStream = {
  onEvent: () => {
    throw new Error("eventStream is a placeholder — implemented in Phase 3")
  },
}
