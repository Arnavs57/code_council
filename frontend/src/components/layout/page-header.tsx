import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export interface PageHeaderProps {
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

/** Standard page title block used by every page. */
export function PageHeader({ title, description, action, className }: PageHeaderProps) {
  return (
    <div className={cn("flex flex-wrap items-end justify-between gap-3", className)}>
      <div>
        <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
        {description && (
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  )
}
