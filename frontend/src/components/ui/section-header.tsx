import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export interface SectionHeaderProps {
  icon?: LucideIcon
  title: string
  description?: string
  /** Right-aligned actions (badges, controls). */
  action?: ReactNode
  className?: string
}

/** Consistent header for every mission-control panel. */
export function SectionHeader({
  icon: Icon,
  title,
  description,
  action,
  className,
}: SectionHeaderProps) {
  return (
    <div className={cn("flex items-start justify-between gap-3", className)}>
      <div className="flex min-w-0 items-center gap-2.5">
        {Icon && (
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-border bg-muted text-muted-foreground">
            <Icon className="h-3.5 w-3.5" />
          </span>
        )}
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold tracking-tight">{title}</h3>
          {description && (
            <p className="truncate text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {action && <div className="flex shrink-0 items-center gap-2">{action}</div>}
    </div>
  )
}
