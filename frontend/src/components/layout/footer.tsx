import { useApp } from "@/contexts/app-context"

/** Subtle system status strip. */
export function Footer() {
  const { appName, version, environment } = useApp()
  return (
    <footer className="flex items-center justify-between gap-4 border-t border-border px-4 py-2.5 text-[11px] text-muted-foreground lg:px-6">
      <span>{appName} — Mission Control</span>
      <span className="font-mono uppercase tracking-widest">
        {environment} · v{version}
      </span>
    </footer>
  )
}
