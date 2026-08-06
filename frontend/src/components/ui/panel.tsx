import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"

import { Card, CardContent } from "@/components/ui/card"
import { SectionHeader } from "@/components/ui/section-header"
import { cn } from "@/lib/utils"

export interface PanelProps {
  icon?: LucideIcon
  title: string
  description?: string
  /** Right-aligned header actions. */
  action?: ReactNode
  children: ReactNode
  /** e.g. "xl:col-span-4" — the parent grid controls placement. */
  className?: string
  bodyClassName?: string
}

/**
 * The standard mission-control panel: header (icon + title + actions) over
 * a padded card body. Every dashboard section is built from this so the
 * visual language stays consistent as sections come alive.
 */
export function Panel({
  icon,
  title,
  description,
  action,
  children,
  className,
  bodyClassName,
}: PanelProps) {
  return (
    <Card className={cn("flex flex-col", className)}>
      <CardContent className="flex h-full flex-col gap-4 p-5">
        <SectionHeader icon={icon} title={title} description={description} action={action} />
        <div className={cn("min-h-0 flex-1", bodyClassName)}>{children}</div>
      </CardContent>
    </Card>
  )
}
