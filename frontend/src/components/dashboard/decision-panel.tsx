import { Scale } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"
import { StatusIndicator } from "@/components/ui/status-indicator"
import { cn } from "@/lib/utils"

const OUTCOMES = [
  { label: "GO", tone: "text-success border-success/40" },
  { label: "NO-GO", tone: "text-destructive border-destructive/40" },
  { label: "GO w/ Conditions", tone: "text-warning border-warning/40" },
] as const

/**
 * Final decision panel — appears only after all deliberations complete.
 * Phase 3: driven by DecisionPending / DecisionMade events; becomes the
 * weighted verdict with score breakdown and dissent list.
 */
export function DecisionPanel() {
  return (
    <Panel
      icon={Scale}
      title="Release Decision"
      description="Release Manager verdict"
      className="xl:col-span-4"
      action={<StatusIndicator tone="muted" label="Pending" />}
    >
      <div className="flex flex-1 flex-col items-center justify-center gap-4 rounded-md border border-dashed border-border py-8 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-full border border-border bg-muted text-muted-foreground">
          <Scale className="h-5 w-5" />
        </span>
        <div>
          <p className="text-sm font-semibold">Decision pending</p>
          <p className="mt-1 max-w-xs text-xs leading-relaxed text-muted-foreground">
            The Release Manager delivers the final verdict only after every
            agent has finished and all discussions are resolved.
          </p>
        </div>
        <div className="flex gap-2">
          {OUTCOMES.map((outcome) => (
            <span
              key={outcome.label}
              className={cn(
                "rounded-md border px-3 py-1.5 text-xs font-semibold opacity-60",
                "border-border bg-muted/40",
                outcome.tone,
              )}
            >
              {outcome.label}
            </span>
          ))}
        </div>
        <Badge variant="outline">Awaiting review run</Badge>
      </div>
    </Panel>
  )
}
