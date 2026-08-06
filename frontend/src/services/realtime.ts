/**
 * Realtime facade — the single entry point future live features use.
 *
 * Phase 3: composes the WebSocket client, event stream and notification
 * service into one `Realtime` API so components depend on an interface, not
 * on transport details.
 */
import { realtimeClient } from "@/services/ws/client"

export interface Realtime {
  // TODO(phase-3): connect(), disconnect(), subscribeToRun(runId, cb)
  connect(): Promise<void>
}

export const realtime: Realtime = {
  connect: () => {
    // Touch the client so the wiring is visible even as a placeholder.
    void realtimeClient
    throw new Error("Realtime is a placeholder — implemented in Phase 3")
  },
}
