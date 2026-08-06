import { History } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"
import { cn } from "@/lib/utils"

const STAGES = [
  { label: "Upload repository", time: "—", done: false },
  { label: "Governance plan", time: "—", done: false },
  { label: "Repository scan", time: "—", done: false },
  { label: "Agent deliberations", time: "—", done: false },
  { label: "Release decision", time: "—", done: false },
] as const

/**
 * Vertical review timeline.
 * Phase 3: rows light up as lifecycle events stream in; each row becomes a
 * jump target to the related evidence/finding.
 */
export function TimelinePanel() {
  return (
    <Panel
      icon={History}
      title="Timeline"
      description="Review phases"
      className="xl:col-span-7"
      action={<Badge variant="outline">0 of 5</Badge>}
    >
      <ol className="relative space-y-4 pl-5">
        <span className="absolute left-[5px] top-1 bottom-1 w-px bg-border" aria-hidden />
        {STAGES.map((stage) => (
          <li key={stage.label} className="relative">
            <span
              className={cn(
                "absolute -left-5 top-1 h-2.5 w-2.5 rounded-full border-2 border-background",
                stage.done ? "bg-success" : "bg-muted-foreground/40",
              )}
            />
            <div className="flex items-center justify-between gap-3">
              <span className="text-sm text-muted-foreground">{stage.label}</span>
              <span className="font-mono text-[11px] text-muted-foreground/70">
                {stage.time}
              </span>
            </div>
          </li>
        ))}
      </ol>
    </Panel>
  )
}
