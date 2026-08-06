import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

/** Constrains page content width and applies vertical rhythm. */
export function PageContainer({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <main className={cn("container-page flex-1 px-4 py-6 lg:px-6", className)}>
      {children}
    </main>
  )
}
