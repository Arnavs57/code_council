import { cn } from "@/lib/utils"

export interface LoaderProps {
  size?: "sm" | "md" | "lg"
  label?: string
  className?: string
}

const SIZE_CLASSES = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-9 w-9 border-[3px]",
}

/** Circular spinner + optional label. */
export function Loader({ size = "md", label, className }: LoaderProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn("flex items-center gap-2.5 text-sm text-muted-foreground", className)}
    >
      <span
        className={cn(
          "inline-block animate-spin rounded-full border-primary/25 border-t-primary",
          SIZE_CLASSES[size],
        )}
      />
      {label && <span>{label}</span>}
      <span className="sr-only">{label ?? "Loading"}</span>
    </div>
  )
}
