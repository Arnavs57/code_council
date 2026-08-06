import { Activity } from "lucide-react"

import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

export function ActivityPage() {
  return (
    <ContentWrapper>
      <PageHeader
        title="Activity"
        description="Full audit trail across every review run."
      />
      <Panel icon={Activity} title="Event stream" description="Placeholder">
        <EmptyState
          icon={Activity}
          title="Stream is quiet"
          description="The complete event log — agent actions, findings, discussions and decisions — will render here."
        />
      </Panel>
    </ContentWrapper>
  )
}
