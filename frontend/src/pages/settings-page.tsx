import { Settings } from "lucide-react"

import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

export function SettingsPage() {
  return (
    <ContentWrapper>
      <PageHeader
        title="Settings"
        description="Platform configuration."
      />
      <Panel icon={Settings} title="Configuration" description="Placeholder">
        <EmptyState
          icon={Settings}
          title="Nothing to configure yet"
          description="Policies, agent model tiers, budgets and tool grants will be manageable here."
        />
      </Panel>
    </ContentWrapper>
  )
}
