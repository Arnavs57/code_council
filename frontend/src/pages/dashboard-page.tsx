import { AgentStatus } from "@/components/dashboard/agent-status"
import { DecisionPanel } from "@/components/dashboard/decision-panel"
import { DiscussionPanel } from "@/components/dashboard/discussion-panel"
import { EvidencePanel } from "@/components/dashboard/evidence-panel"
import { FindingsFeed } from "@/components/dashboard/findings-feed"
import { GovernanceStatus } from "@/components/dashboard/governance-status"
import { RepoExplorer } from "@/components/dashboard/repo-explorer"
import { RepositorySummary } from "@/components/dashboard/repository-summary"
import { SystemHealth } from "@/components/dashboard/system-health"
import { TimelinePanel } from "@/components/dashboard/timeline-panel"
import { DashboardGrid } from "@/components/layout/dashboard-grid"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { StatusIndicator } from "@/components/ui/status-indicator"

/**
 * Mission Control — the product's live war room.
 * Every section is a placeholder wired for the real-time phase. The grid is
 * a deliberate SOC layout: summary/health across the top, the agent board
 * and timeline in the center, evidence and decision to the right.
 */
export function DashboardPage() {
  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        title="Mission Control"
        description="Live engineering review board — agents collaborate, disagree and decide in real time."
        action={
          <>
            <StatusIndicator tone="muted" label="No active run" pulse={false} />
            <Button variant="outline" disabled>
              Upload repository
            </Button>
            <Badge variant="secondary" className="hidden md:inline-flex">
              Preview
            </Badge>
          </>
        }
      />

      {/* Column math: every row sums to 12 on the xl grid (4+4+4, 5+7,
          7+5, 4+4+4) so no row leaves ragged gaps. */}
      <DashboardGrid>
        <RepositorySummary />
        <GovernanceStatus />
        <SystemHealth />

        <AgentStatus />
        <TimelinePanel />

        <FindingsFeed />
        <DiscussionPanel />

        <RepoExplorer />
        <EvidencePanel />
        <DecisionPanel />
      </DashboardGrid>
    </div>
  )
}
