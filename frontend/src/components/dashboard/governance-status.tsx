import { ShieldCheck } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"
import { StatusIndicator } from "@/components/ui/status-indicator"
import { cn } from "@/lib/utils"

const PHASES = [
  { id: "plan", label: "Plan" },
  { id: "validate", label: "Validate" },
  { id: "allocate", label: "Allocate" },
  { id: "monitor", label: "Monitor" },
  { id: "decide", label: "Decide" },
] as const

/**
 * Governance Controller state machine.
 * Phase 3: driven by the execution-plan events (ExecutionPlanCreated,
 * budget allocation, watchdog signals).
 */
export function GovernanceStatus() {
  return (
    <Panel
      icon={ShieldCheck}
      title="Governance Controller"
      description="Execution plan lifecycle"
      className="xl:col-span-4"
      action={<StatusIndicator tone="muted" label="Standby" />}
    >
      <ol className="space-y-1">
        {PHASES.map((phase, index) => (
          <li key={phase.id} className="flex items-center gap-3">
            <span
              className={cn(
                "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border font-mono text-[10px]",
                "border-border bg-muted text-muted-foreground",
              )}
            >
              {index + 1}
            </span>
            <span className="flex-1 text-sm text-muted-foreground">{phase.label}</span>
            <Badge variant="outline">pending</Badge>
          </li>
        ))}
      </ol>
      <p className="text-xs leading-relaxed text-muted-foreground">
        The controller will create the execution plan, allocate budgets and
        supervise every agent the moment a review starts.
      </p>
    </Panel>
  )
}
