import { cn } from "@/lib/utils"

type Tone = "muted" | "info" | "warning" | "destructive" | "success"

const DOT_TONES: Record<Tone, string> = {
  muted: "bg-muted-foreground/60",
  info: "bg-info",
  warning: "bg-warning",
  destructive: "bg-destructive",
  success: "bg-success",
}

const TEXT_TONES: Record<Tone, string> = {
  muted: "text-muted-foreground",
  info: "text-info",
  warning: "text-warning",
  destructive: "text-destructive",
  success: "text-success",
}

export interface StatusIndicatorProps {
  tone?: Tone
  label?: string
  /** Adds a radar-like pulse ring (use for live/active states). */
  pulse?: boolean
  className?: string
}

/**
 * Status dot with optional label. The `pulse` variant is reserved for
 * states that will be LIVE in later phases (agents working, scanning,
 * events streaming) — it animates a ping ring like a SOC console.
 */
export function StatusIndicator({
  tone = "muted",
  label,
  pulse = false,
  className,
}: StatusIndicatorProps) {
  return (
    <span className={cn("inline-flex items-center gap-1.5", className)}>
      <span className="relative flex h-2 w-2 shrink-0">
        {pulse && (
          <span
            className={cn(
              "absolute inline-flex h-full w-full animate-ping rounded-full opacity-60",
              DOT_TONES[tone],
            )}
          />
        )}
        <span className={cn("relative inline-flex h-2 w-2 rounded-full", DOT_TONES[tone])} />
      </span>
      {label && <span className={cn("text-xs font-medium", TEXT_TONES[tone])}>{label}</span>}
    </span>
  )
}
