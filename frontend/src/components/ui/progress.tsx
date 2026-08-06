import * as React from "react"

import { cn } from "@/lib/utils"

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  /** 0–100. Values are clamped defensively. */
  value: number
  /** Extra classes for the filled indicator (e.g. tone colors). */
  indicatorClassName?: string
}

/**
 * Accessible progress bar. Foundation version is intentionally dependency
 * free; the live dashboard will feed it aggregated event progress.
 */
export function Progress({
  value,
  className,
  indicatorClassName,
  ...props
}: ProgressProps) {
  const clamped = Number.isFinite(value)
    ? Math.min(100, Math.max(0, value))
    : 0
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(clamped)}
      data-slot="progress"
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-muted",
        className,
      )}
      {...props}
    >
      <div
        className={cn(
          "h-full rounded-full bg-primary transition-[width] duration-500 ease-out",
          indicatorClassName,
        )}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
