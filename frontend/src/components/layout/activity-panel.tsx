import { Radio } from "lucide-react"

import { EmptyState } from "@/components/ui/empty-state"
import { StatusIndicator } from "@/components/ui/status-indicator"

/**
 * Right-hand live activity rail.
 *
 * Phase 3: this panel consumes the WebSocket event stream and renders agent
 * actions in real time (tool invocations, findings, questions). For the
 * foundation it renders placeholder feed rows so the slot's rhythm and
 * sizing are already correct.
 */
export function ActivityPanel() {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-l border-border bg-card/30 xl:flex">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          <Radio className="h-3.5 w-3.5 text-info" />
          Live Activity
        </span>
        <StatusIndicator tone="info" label="Standby" pulse />
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <div
            key={index}
            className="animate-fade-in-up rounded-md border border-border/60 bg-card p-3"
            style={{ animationDelay: `${index * 60}ms` }}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="h-2 w-16 rounded bg-muted" />
              <span className="h-2 w-8 rounded bg-muted" />
            </div>
            <div className="mt-2 h-2 w-11/12 rounded bg-muted" />
            <div className="mt-1.5 h-2 w-3/4 rounded bg-muted" />
          </div>
        ))}

        <EmptyState
          icon={Radio}
          title="Waiting for a review run"
          description="Agent actions, tool executions and findings will stream here the moment a repository review begins."
          className="py-8"
        />
      </div>
    </aside>
  )
}
