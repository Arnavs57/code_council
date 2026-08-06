import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

/** Vertical content wrapper — page header + body with consistent spacing. */
export function ContentWrapper({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return <div className={cn("flex flex-col gap-5", className)}>{children}</div>
}
