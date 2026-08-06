/**
 * WebSocket client — architecture only. No implementation in this phase.
 *
 * Phase 3: manages the live event stream from the backend gateway:
 *   - subscribe to run channels
 *   - cursor-based resume (last_event_id) after reconnect
 *   - exponential backoff, heartbeats, event dedupe
 * Consumed by the dashboard reducer; never by components directly.
 */

export interface WsSubscription {
  runId: string
  /** TODO(phase-3): called with each decoded event envelope. */
  onEvent: (event: unknown) => void
}

export class RealtimeClient {
  constructor(private readonly url: string) {}

  // TODO(phase-3): open(), close(), subscribe(), resubscribe()
  subscribe(subscription: WsSubscription): void {
    // Reference the wiring so the URL and channel contract stay visible.
    void subscription
    throw new Error(
      `RealtimeClient is a placeholder (WS URL: ${this.url}) — implemented in Phase 3`,
    )
  }

  /** Expose the configured endpoint for debug/diagnostics. */
  get endpoint(): string {
    return this.url
  }
}

/** Shared instance — WS URL from env once the gateway exists. */
export const realtimeClient = new RealtimeClient(
  import.meta.env.VITE_WS_URL ?? "ws://127.0.0.1:8000/ws/v1/events",
)
