import type { LucideIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface MetricCardProps {
  icon?: LucideIcon
  label: string
  value: string
  /** e.g. "Healthy", "Idle", "0 active" — drives the tone badge. */
  status?: { label: string; variant: "success" | "warning" | "destructive" | "info" | "outline" }
  className?: string
}

/** Compact KPI tile used by System Health and summary sections. */
export function MetricCard({ icon: Icon, label, value, status, className }: MetricCardProps) {
  return (
    <Card className={cn("p-4", className)}>
      <div className="flex items-center justify-between gap-2">
        <span className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
          {Icon && <Icon className="h-3.5 w-3.5" />}
          {label}
        </span>
        {status && <Badge variant={status.variant}>{status.label}</Badge>}
      </div>
      <p className="mt-2 font-mono text-2xl font-semibold tabular-nums tracking-tight">
        {value}
      </p>
    </Card>
  )
}
