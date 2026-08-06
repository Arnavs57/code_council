import { ShieldAlert } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"
import { SEVERITY_BADGE_VARIANT, SEVERITY_META } from "@/constants"

const PREVIEW_SEVERITIES = ["critical", "high", "medium"] as const

/**
 * Findings feed — the security/quality signal stream.
 * Phase 3: FindingPublished events append rows here with severity badges,
 * evidence links and "contested" markers.
 */
export function FindingsFeed() {
  return (
    <Panel
      icon={ShieldAlert}
      title="Findings"
      description="Signals from every agent"
      className="xl:col-span-7"
      action={<Badge variant="secondary">0 open</Badge>}
    >
      <EmptyState
        icon={ShieldAlert}
        title="No findings yet"
        description="Security, architecture, QA and operations findings will stream in as agents complete their review passes."
      />
      <div className="mt-4 space-y-2">
        {PREVIEW_SEVERITIES.map((severity) => (
          <div
            key={severity}
            className="flex items-center gap-3 rounded-md border border-border/60 bg-muted/20 px-3 py-2.5"
          >
            <Badge variant={SEVERITY_BADGE_VARIANT[severity]}>
              {SEVERITY_META[severity].label.toUpperCase()}
            </Badge>
            <span className="h-2 flex-1 rounded bg-muted" />
          </div>
        ))}
      </div>
    </Panel>
  )
}
