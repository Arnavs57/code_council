import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

export interface DashboardGridProps {
  children: ReactNode
  className?: string
}

/**
 * The mission-control grid. Panels place themselves via col-span classes:
 * 1 col on mobile → 2 on tablet → 12-col layout on xl screens.
 */
export function DashboardGrid({ children, className }: DashboardGridProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-12",
        className,
      )}
    >
      {children}
    </div>
  )
}
