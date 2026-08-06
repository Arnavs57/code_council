import { cn } from "@/lib/utils"

export interface LogoProps {
  className?: string
}

/** Brand mark — the shield/circuit glyph over the product name. */
export function Logo({ className }: LogoProps) {
  return (
    <span className={cn("flex items-center gap-2.5", className)}>
      <span className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-card text-primary shadow-sm">
        <img src="/src/assets/logo.svg" alt="" className="h-5 w-5" />
      </span>
      <span className="flex flex-col leading-none">
        <span className="text-sm font-semibold tracking-tight">Code Council AI</span>
        <span className="mt-0.5 text-[10px] uppercase tracking-widest text-muted-foreground">
          Engineering Governance
        </span>
      </span>
    </span>
  )
}
