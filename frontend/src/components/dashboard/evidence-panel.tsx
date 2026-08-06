import { FileSearch } from "lucide-react"

import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

/**
 * Evidence panel — artifacts behind every finding.
 * Phase 3: scan outputs, tool reports and raw model responses render here,
 * linked from findings and discussions.
 */
export function EvidencePanel() {
  return (
    <Panel
      icon={FileSearch}
      title="Evidence"
      description="Artifacts behind findings"
      className="xl:col-span-4"
    >
      <EmptyState
        icon={FileSearch}
        title="No evidence captured"
        description="Semgrep output, Trivy reports, secret-scan results and agent reasoning traces will be attached here."
        className="py-8"
      />
    </Panel>
  )
}
