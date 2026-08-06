import { FileBarChart } from "lucide-react"

import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

export function ReportsPage() {
  return (
    <ContentWrapper>
      <PageHeader
        title="Reports"
        description="Summaries and exportable evidence packs."
      />
      <Panel icon={FileBarChart} title="Generated reports" description="Placeholder">
        <EmptyState
          icon={FileBarChart}
          title="No reports yet"
          description="Decision summaries with score breakdowns and evidence links will be generated after each review."
        />
      </Panel>
    </ContentWrapper>
  )
}
