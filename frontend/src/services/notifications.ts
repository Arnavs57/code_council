/**
 * Notification service — architecture only.
 *
 * Phase 3: surfaces decision/finding/agent notifications (toast + inbox)
 * from the event stream. Injected as a dependency so the dashboard reducer
 * never touches the UI directly.
 */
export interface NotificationPayload {
  kind: "decision" | "finding" | "agent" | "system"
  title: string
  body?: string
}

export class NotificationService {
  // TODO(phase-3): wire to a toast/inbox store
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  notify(_payload: NotificationPayload): void {
    throw new Error("NotificationService is a placeholder")
  }
}

export const notificationService = new NotificationService()
